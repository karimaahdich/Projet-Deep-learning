from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui ajoute un identifiant unique (X-Request-ID)
    à chaque requête HTTP, pour faciliter le suivi et les logs.
    """

    async def dispatch(self, request, call_next):
        # Génère un identifiant unique pour chaque requête
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = req_id

        # Lie cet ID aux logs
        logger.bind(request_id=req_id)
        logger.info(f"📩 Nouvelle requête reçue: {request.url.path} (ID: {req_id})")

        # Exécute la requête suivante dans la pile
        response = await call_next(request)

        # Ajoute l'ID dans la réponse HTTP
        response.headers["X-Request-ID"] = req_id
        logger.info(f"✅ Réponse envoyée pour {request.url.path} (ID: {req_id})")
        return response
