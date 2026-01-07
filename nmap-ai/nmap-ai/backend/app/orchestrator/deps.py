# app/orchestrator/deps.py

from app.agents.rag_client import RAGClient
from app.agents.llm_client import LLMClient
from app.agents.diffusion_client import DiffusionClient
from app.agents.validator_client import ValidatorClient
from app.agents.selfcorr_client import SelfCorrectionClient

from app.core.comprehension import ComprehensionService
from app.core.classifier import ComplexityClassifier


class Deps:
    """
    Conteneur des dépendances injectées dans l'OrchestratorEngine.
    """
    def __init__(self):
        # Agents génératifs
        self.rag = RAGClient()
        self.llm = LLMClient()
        self.diffusion = DiffusionClient()

        # Validator & self-correction
        self.validator = ValidatorClient()
        self.selfcorr = SelfCorrectionClient()

        # Services NLP
        self.comprehension = ComprehensionService()
        self.classifier = ComplexityClassifier()
