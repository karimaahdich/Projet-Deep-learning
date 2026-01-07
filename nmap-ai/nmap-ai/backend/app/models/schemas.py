from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ============================
# 🏷 ENUMS
# ============================

class Complexity(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ValidationStatus(str, Enum):
    valid = "valid"
    repairable = "repairable"
    invalid = "invalid"


# ============================
# 🧠 MODELS
# ============================

class UserQuery(BaseModel):
    text: str
    context: Optional[Dict] = Field(default_factory=dict)


class ClassificationResult(BaseModel):
    is_nmap_related: bool
    reason: Optional[str] = None
    features: Dict[str, float] = Field(default_factory=dict)


class ComplexityResult(BaseModel):
    level: Complexity
    confidence: float = 0.5


class CommandCandidate(BaseModel):
    command: str
    rationale: Optional[str] = None
    source_agent: str = "unknown"


class ValidationResult(BaseModel):
    status: ValidationStatus
    issues: List[str] = Field(default_factory=list)
    score: float = 0.0
    simulation_notes: Optional[str] = None


class SelfCorrectionResult(BaseModel):
    repaired: bool
    new_command: Optional[str] = None
    notes: Optional[str] = None


class FinalDecision(BaseModel):
    command: str
    confidence: float
    flags_explanation: Dict[str, str] = Field(default_factory=dict)
