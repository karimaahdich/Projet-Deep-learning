import pytest
from app.orchestrator.engine import Orchestrator, Deps
from app.models.schemas import UserQuery, CommandCandidate, ValidationResult


# === Mocks simples pour les agents ===

class MockRAGClient:
    async def generate(self, q):
        return CommandCandidate(command="nmap -sS 192.168.1.10", source_agent="RAG", rationale="mock")


class MockLLMClient:
    async def generate(self, q):
        return CommandCandidate(command="nmap -sS -sV 192.168.1.10", source_agent="LLM", rationale="mock")


class MockDiffusionClient:
    async def generate(self, q):
        return CommandCandidate(command="nmap -A -p- 192.168.1.0/24", source_agent="DIFFUSION", rationale="mock")


class MockValidatorClient:
    async def validate(self, cand):
        # Refuse toutes les commandes contenant 192.168.1.10 (RAG et LLM)
        if "192.168.1.10" in cand.command:
            return ValidationResult(status="invalid", score=0.1, issues=["Mock refuse RAG/LLM pour test escalade"])

        # Accepte Diffusion
        if "192.168.1.0/24" in cand.command or "-A -p-" in cand.command:
            return ValidationResult(status="valid", score=0.9, issues=[])

        return ValidationResult(status="invalid", score=0.1, issues=["Mock invalid"])


class MockSelfCorrClient:
    async def repair(self, cand, v):
        return CommandCandidate(command=cand.command + " -sS", source_agent="SelfCorr", rationale="mock")


# === Fixture ===
@pytest.fixture
def orchestrator():
    deps = Deps(
        rag=MockRAGClient(),
        llm=MockLLMClient(),
        diffusion=MockDiffusionClient(),
        validator=MockValidatorClient(),
        selfcorr=MockSelfCorrClient(),
    )
    return Orchestrator(deps)


# === Tests ===

@pytest.mark.asyncio
async def test_simple_easy_scan_success(orchestrator):
    query = UserQuery(text="Scan nmap simple")
    result = await orchestrator.handle(query)
    # Note : avec ce validator, easy sera refusé → escalade → mais on garde le test pour vérifier que ça passe quand même
    assert "nmap" in result.command
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_escalation_on_validation_failure(orchestrator):
    query = UserQuery(text="Scan complexe avec tout")
    result = await orchestrator.handle(query)
    assert "192.168.1.0/24" in result.command  # Obligatoire : preuve d'escalade jusqu'à hard
    assert result.confidence > 0.8


@pytest.mark.asyncio
async def test_mcp_logs_generated(orchestrator, tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator.mcp, "log_file", str(tmp_path / "test_mcp.jsonl"))
    query = UserQuery(text="Scan nmap simple")
    await orchestrator.handle(query)
    log_content = (tmp_path / "test_mcp.jsonl").read_text(encoding="utf-8")
    assert "pipeline_success" in log_content
    assert "generation_success" in log_content
    assert "validation_attempt" in log_content