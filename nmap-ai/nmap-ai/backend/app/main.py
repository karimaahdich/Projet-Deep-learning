from fastapi import FastAPI
from app.api.routes import router
from app.core.logging import RequestIdMiddleware

from app.orchestrator.engine import Orchestrator, Deps
from app.agents.rag_client import RAGClient
from app.agents.llm_client import LLMClient
from app.agents.diffusion_client import DiffusionClient
from app.agents.validator_client import ValidatorClient
from app.agents.selfcorr_client import SelfCorrectionClient

def create_app() -> FastAPI:
    app = FastAPI(title="NMAP-AI Orchestrator (M1)")
    app.add_middleware(RequestIdMiddleware)

    deps = Deps(
        rag=RAGClient(),
        llm=LLMClient(),
        diffusion=DiffusionClient(),
        validator=ValidatorClient(),
        selfcorr=SelfCorrectionClient(),
    )

    # IMPORTANT : enregistrer l'orchestrateur dans l'état FastAPI
    app.state.orchestrator = Orchestrator(deps)
    print(">>>>> ORCHESTRATOR INIT:", app.state.orchestrator)


    # Router
    app.include_router(router, prefix="/api/v1")

    return app


# L'application finale
app = create_app()
