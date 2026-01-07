# app/agents/rag_client.py
import httpx
from loguru import logger
from app.models.schemas import UserQuery, CommandCandidate
from app.core.config import RAG_BASE_URL


class RAGClient:
    async def generate(self, q: UserQuery) -> CommandCandidate:
        logger.info("→ Tentative d'appel vers l'agent RAG réel (Knowledge Graph - Neo4j)")

        full_url = f"{RAG_BASE_URL.rstrip('/')}/api/v1/generate"
        logger.info(f"   URL cible : {full_url}")
        logger.info(f"   Intention utilisateur : \"{q.text}\"")

        payload = {
            "query": q.text,  # ← Ici : "query" au lieu de "text"
            "context": q.context or {}
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info("   Envoi de la requête POST...")
                response = await client.post(full_url, json=payload)

                logger.info(f"   Réponse HTTP reçue : {response.status_code}")

                response.raise_for_status()

                data = response.json()
                logger.info(f"   Réponse brute du RAG : {data}")

                command = data.get("command") or data.get("cmd") or data.get("nmap_command")
                if not command:
                    raise ValueError("Le RAG réel n'a pas retourné de commande valide")

                rationale = data.get("rationale", "Généré par Knowledge Graph RAG (Neo4j)")

                logger.success(f"✅ RAG réel a répondu avec succès : {command}")

                return CommandCandidate(
                    command=command.strip(),
                    rationale=rationale,
                    source_agent="RAG"
                )

        except Exception as e:
            logger.error(f"Erreur avec le RAG réel : {e} – escalade automatique")
            raise