# app/agents/llm_client.py
import httpx
from loguru import logger
from app.models.schemas import UserQuery, CommandCandidate
from app.core.config import GENERATION_BASE_URL  # http://IP:8002


class LLMClient:
    async def generate(self, q: UserQuery) -> CommandCandidate:
        logger.info("→ Appel vers l'agent LLM réel (fine-tuné LoRA)")

        full_url = f"{GENERATION_BASE_URL.rstrip('/')}/medium"
        logger.info(f"   URL cible : {full_url}")
        logger.info(f"   Intention utilisateur : \"{q.text}\"")

        payload = {
            "query": q.text  # ← Champ attendu par l'API
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info("   Envoi de la requête POST...")
                response = await client.post(full_url, json=payload)

                logger.info(f"   Réponse HTTP reçue : {response.status_code}")

                response.raise_for_status()

                data = response.json()
                logger.info(f"   Réponse brute du LLM : {data}")

                command = data.get("command")
                if not command:
                    raise ValueError("LLM n'a pas retourné de commande valide")

                rationale = data.get("rationale", "Généré par LLM fine-tuné LoRA")
                source_agent = data.get("source_agent", "LLM")

                logger.success(f"✅ LLM réel a répondu avec succès : {command}")

                return CommandCandidate(
                    command=command.strip(),
                    rationale=rationale,
                    source_agent=source_agent
                )

        except Exception as e:
            logger.error(f"Erreur avec LLM réel ({full_url}) : {e} – escalade vers Diffusion")
            raise  # Escalade automatique vers hard