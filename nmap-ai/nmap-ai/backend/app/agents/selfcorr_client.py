# app/agents/selfcorr_client.py
import httpx
from loguru import logger
from app.models.schemas import CommandCandidate, ValidationResult
from app.core.config import VALIDATION_BASE_URL


class SelfCorrectionClient:
    async def repair(self, cand: CommandCandidate, v: ValidationResult) -> CommandCandidate:
        logger.info("→ Appel vers le Self-Correction réel")

        full_url = f"{VALIDATION_BASE_URL.rstrip('/')}/api/v1/repair"
        logger.info(f"   URL cible : {full_url}")
        logger.info(f"   Commande à réparer : {cand.command}")
        logger.info(f"   Issues : {v.issues}")

        # Construction du payload complexe attendu
        payload = {
            "query": {
                "user_id": "orchestrator_user",
                "query": cand.rationale or "Réparer la commande Nmap",  # Ou q.text si tu gardes la query originale
                "metadata": {}
            },
            "candidate": {
                "command": cand.command,
                "user_id": "orchestrator_user",
                "context": {},
                "rationale": cand.rationale or "",
                "source_agent": cand.source_agent or "unknown",
                "suggested_generation": "",
                "generation_metadata": {}
            },
            "result": {
                "status": v.status,
                "command": cand.command,
                "valid": v.status == "valid",
                "risk_score": 1.0 - v.score,  # Inversion si nécessaire
                "risk_level": "high" if v.score < 0.5 else "low",
                "issues": [
                    {
                        "type": "syntax" if "syntax" in issue.lower() else "semantic",
                        "severity": "high" if "incompatible" in issue.lower() else "medium",
                        "message": issue,
                        "suggestion": "Corriger manuellement"
                    } for issue in v.issues
                ],
                "warnings": [],
                "recommendation": "Réparer les problèmes détectés",
                "timestamp": "2025-12-24T00:00:00Z"  # Date actuelle approximative
            }
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(full_url, json=payload)
                logger.info(f"   Réponse HTTP : {response.status_code}")

                response.raise_for_status()

                data = response.json()
                logger.info(f"   Réponse du Self-Correction : {data}")

                new_command = data.get("command") or data.get("repaired_command") or cand.command
                rationale = data.get("rationale", "Corrigé par agent Self-Correction réel")

                logger.success(f"✅ Self-Correction réel a répondu : {new_command}")

                return CommandCandidate(
                    command=new_command.strip(),
                    rationale=rationale,
                    source_agent="SelfCorrection"
                )

        except Exception as e:
            logger.error(f"Self-Correction réel inaccessible ou erreur ({full_url}) : {e}")
            # Fallback : retourne la commande originale
            return cand