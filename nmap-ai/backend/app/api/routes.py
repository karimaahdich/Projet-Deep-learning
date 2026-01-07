from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from app.models.schemas import UserQuery, FinalDecision

router = APIRouter()


@router.post("/command/generate", response_model=FinalDecision)
async def generate_command(request: Request, q: UserQuery):
    """Endpoint principal: reçoit une requête utilisateur et appelle l'orchestrateur"""

    logger.info("🔁 /command/generate appelé")

    orchestrator = getattr(request.app.state, "orchestrator", None)
    if orchestrator is None:
        logger.error("❌ orchestrator introuvable dans request.app.state")
        raise HTTPException(status_code=500, detail="orchestrator missing from app state")

    try:
        result = await orchestrator.handle(q)
        logger.info(f"🎉 Commande finale générée: {result.command}")
        return result

    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération de commande: {e}")
        raise HTTPException(status_code=400, detail=str(e))
