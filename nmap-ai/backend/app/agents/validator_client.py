# app/agents/validator_client.py
import httpx
from loguru import logger
from app.models.schemas import CommandCandidate, ValidationResult
from app.core.config import VALIDATION_BASE_URL


class ValidatorClient:
    async def validate(self, cand: CommandCandidate) -> ValidationResult:
        logger.info("→ Appel vers le Validator réel")

        full_url = f"{VALIDATION_BASE_URL.rstrip('/')}/api/v1/validate"
        logger.info(f"   URL cible : {full_url}")
        logger.info(f"   Commande à valider : {cand.command}")

        # Payload exact attendu par l'API
        payload = {
            "command": cand.command,
            "user_id": "orchestrator_user",  # Valeur fixe ou dynamique si besoin
            "context": {},
            "rationale": cand.rationale or "",
            "source_agent": cand.source_agent or "unknown",
            "suggested_generation": "",
            "generation_metadata": {}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(full_url, json=payload)
                logger.info(f"   Réponse HTTP : {response.status_code}")

                response.raise_for_status()

                data = response.json()
                logger.info(f"   Réponse complète du Validator : {data}")

                # Extraction des champs clés
                status = data.get("status", "invalid")
                score = data.get("risk_score", 0.1)  # risk_score semble être le score
                issues = []
                for issue in data.get("issues", []):
                    issues.append(issue.get("message", "Issue inconnue"))

                warnings = data.get("warnings", [])

                logger.info(f"   Validator → status={status}, score={score}, issues={issues[:3]}...")

                return ValidationResult(
                    status=status.lower(),  # "valid", "invalid", "repairable" ?
                    score=1.0 - score if score else 0.85,  # Inversion si risk_score (0 = safe, 1 = risky)
                    issues=issues + warnings
                )

        except Exception as e:
            logger.error(f"Validator réel inaccessible ou erreur ({full_url}) : {e}")
            # Fallback sécurisé : traite comme invalide
            return ValidationResult(
                status="invalid",
                score=0.0,
                issues=["Validator indisponible ou erreur"]
            )