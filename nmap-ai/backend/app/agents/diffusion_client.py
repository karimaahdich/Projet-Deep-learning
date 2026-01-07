# app/agents/diffusion_client.py
import httpx
from loguru import logger
from app.models.schemas import UserQuery, CommandCandidate
from app.core.config import GENERATION_BASE_URL  # Même URL que LLM


class DiffusionClient:
    async def generate(self, q: UserQuery) -> CommandCandidate:
        logger.info("→ Appel vers l'agent Diffusion réel (hard)")

        full_url = f"{GENERATION_BASE_URL.rstrip('/')}/hard"
        logger.info(f"   URL cible : {full_url}")
        logger.info(f"   Intention utilisateur : \"{q.text}\"")

        payload = {
            "query": q.text  # ← Même champ "query"
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:  # Diffusion peut être plus lent
                logger.info("   Envoi de la requête POST...")
                response = await client.post(full_url, json=payload)

                logger.info(f"   Réponse HTTP reçue : {response.status_code}")

                response.raise_for_status()

                data = response.json()
                logger.info(f"   Réponse brute de Diffusion : {data}")

                command = data.get("command")
                if not command:
                    raise ValueError("Diffusion n'a pas retourné de commande valide")

                rationale = data.get("rationale", "Généré par modèle Diffusion-based")
                source_agent = data.get("source_agent", "DIFFUSION")

                logger.success(f"✅ Diffusion réel a répondu avec succès : {command}")

                return CommandCandidate(
                    command=command.strip(),
                    rationale=rationale,
                    source_agent=source_agent
                )

        except Exception as e:
            logger.error(f"Erreur avec Diffusion réel ({full_url}) : {e}")
            raise HTTPException(status_code=503, detail="Tous les agents de génération ont échoué")