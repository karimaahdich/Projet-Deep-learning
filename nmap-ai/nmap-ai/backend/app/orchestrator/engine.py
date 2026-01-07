from fastapi import HTTPException
from loguru import logger
import os

from app.models.schemas import (
    UserQuery,
    CommandCandidate,
    ValidationResult,
    FinalDecision,
)

from app.orchestrator.classify import (
    is_nmap_related,
    baseline_complexity
)

from app.core.mcp import MCPLogger  # <-- Import ajouté pour MCP

MAX_CORRECTIONS = int(os.getenv("MAX_CORRECTIONS", "3"))


class Deps:
    """Regroupe les dépendances/agents utilisés par l'orchestrateur."""

    def __init__(self, rag, llm, diffusion, validator, selfcorr):
        self.rag = rag
        self.llm = llm
        self.diffusion = diffusion
        self.validator = validator
        self.selfcorr = selfcorr


class Orchestrator:
    """
    Orchestrateur OPTION 2 :
    - Escalade automatique entre les agents
    - Boucle de self-correction
    - Validation multi-étapes
    - MCP (Model Context Protocol) pour traçabilité et testing
    """

    def __init__(self, deps: Deps):
        self.deps = deps
        self.mcp = MCPLogger()  # <-- Initialisation du MCP Logger

    # ============================================================
    #                    PIPELINE PRINCIPAL
    # ============================================================
    async def handle(self, q: UserQuery) -> FinalDecision:

        logger.info(f"🟢 Nouvelle requête utilisateur: {q.text}")

        # ---------- 1) COMPRÉHENSION ----------
        comp = is_nmap_related(q.text)
        logger.info(f"🔎 Compréhension → {comp.is_nmap_related}, reason={comp.reason}")

        self.mcp.log("comprehension", {
            "is_nmap_related": comp.is_nmap_related,
            "reason": comp.reason,
            "user_query": q.text
        })

        if not comp.is_nmap_related:
            raise HTTPException(400, "Requête non liée à Nmap")

        # ---------- 2) COMPLEXITÉ INITIALE ----------
        cx = baseline_complexity(q.text)
        logger.info(f"📊 Complexité → {cx.level}, confidence={cx.confidence}")

        self.mcp.log("complexity_classification", {
            "level": cx.level,
            "confidence": cx.confidence,
            "user_query": q.text
        })

        chain = ["easy", "medium", "hard"]
        start_index = chain.index(cx.level)

        # ============================================================
        #         ESCALADE ENTRE RAG → LLM → DIFFUSION
        # ============================================================
        for level_index in range(start_index, len(chain)):
            level = chain[level_index]

            logger.info(f"🎯 Escalade : niveau {level.upper()}")

            self.mcp.log("generation_start", {
                "level": level,
                "is_initial_level": level == chain[start_index]
            })

            # ---------- 3) GÉNÉRATION ----------
            cand = await self._generate(q, level)
            logger.info(f"🧠 Commande générée : {cand.command}")

            self.mcp.log("generation_success", {
                "level": level,
                "command": cand.command,
                "source_agent": getattr(cand, "source_agent", "unknown"),
                "rationale": getattr(cand, "rationale", None)
            })

            # ========================================================
            #           SELF-CORRECTION + VALIDATION EN BOUCLE
            # ========================================================
            for attempt in range(1, MAX_CORRECTIONS + 2):
                logger.info(f"🧪 Validation tentative {attempt}/{MAX_CORRECTIONS + 1}")

                try:
                    v = await self.deps.validator.validate(cand)
                except Exception as e:
                    logger.error(f"❌ Erreur validation: {str(e)}")
                    v = ValidationResult(status="invalid", score=0.0, issues=["Erreur interne lors de la validation"])

                logger.info(f"🔍 Validator → status={v.status}, score={v.score}")

                self.mcp.log("validation_attempt", {
                    "attempt": attempt,
                    "level": level,
                    "status": v.status,
                    "score": v.score,
                    "issues": v.issues,
                    "command": cand.command
                })

                if v.status == "valid":
                    logger.info("🏁 Commande validée !")

                    self.mcp.log("pipeline_success", {
                        "final_command": cand.command,
                        "final_confidence": v.score,
                        "final_level": level,
                        "total_attempts": attempt
                    })

                    return self._finalize(cand, v)

                if v.status == "repairable":
                    logger.info("🛠 Self-correction…")
                    try:
                        cand = await self.deps.selfcorr.repair(cand, v)
                    except Exception as e:
                        logger.error(f"❌ Erreur self-correction: {str(e)}")
                        self.mcp.log("self_correction_failure", {
                            "level": level,
                            "attempt": attempt,
                            "error": str(e)
                        })
                        break

                    logger.info(f"🔁 Commande corrigée : {cand.command}")

                    self.mcp.log("self_correction_success", {
                        "attempt": attempt,
                        "new_command": cand.command,
                        "issues_fixed": v.issues
                    })
                    continue

                # status == invalid
                logger.warning("❌ Commande totalement invalide")
                self.mcp.log("validation_failure", {
                    "attempt": attempt,
                    "level": level,
                    "issues": v.issues
                })
                break  # escalade vers agent suivant

        # Si aucune stratégie n'a fonctionné
        self.mcp.log("pipeline_failure", {
            "user_query": q.text,
            "reason": "Aucun agent n'a produit une commande valide après escalade et corrections"
        })

        raise HTTPException(500, "Impossible de générer une commande valide")

    # ============================================================
    #               ROUTAGE VERS LE BON AGENT
    # ============================================================
    async def _generate(self, q: UserQuery, level: str) -> CommandCandidate:
        chain = ["easy", "medium", "hard"]
        current_index = chain.index(level)
        
        try:
            logger.info(f"→ Appel agent au niveau {level.upper()}")
            if level == "easy":
                return await self.deps.rag.generate(q)
            elif level == "medium":
                return await self.deps.llm.generate(q)
            elif level == "hard":
                return await self.deps.diffusion.generate(q)
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération au niveau {level}: {str(e)}")

            self.mcp.log("generation_failure", {
                "level": level,
                "error": str(e),
                "user_query": q.text
            })

            # Fallback : escalade vers le niveau supérieur si possible
            if current_index < len(chain) - 1:
                next_level = chain[current_index + 1]
                logger.warning(f"⚠️ Escalade automatique vers {next_level.upper()} en raison d'erreur")
                return await self._generate(q, next_level)  # Appel récursif pour escalade
            else:
                logger.critical("🚨 Tous les niveaux d'agents ont échoué")
                raise HTTPException(status_code=503, detail="Service indisponible : échec de génération de commande")

    # ============================================================
    #                   DÉCISION FINALE
    # ============================================================
    def _finalize(self, cand: CommandCandidate, v: ValidationResult) -> FinalDecision:

        logger.info("📤 Construction de la décision finale")

        return FinalDecision(
            command=cand.command,
            confidence=v.score,
            flags_explanation={},  # rempli plus tard
        )