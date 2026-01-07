from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ComplexityLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class NmapRequest(BaseModel):
    """Requête pour générer une commande Nmap"""
    query: str = Field(
        ...,
        description="Requête en langage naturel (ex: 'scan UDP sur 192.168.1.1 avec scripts')",
        example="scan UDP sur 192.168.1.1 avec scripts"
    )
    complexity: ComplexityLevel = Field(
        default=ComplexityLevel.EASY,
        description="Niveau de complexité de la requête"
    )
    target: Optional[str] = Field(
        default=None,
        description="Cible spécifique (optionnel, sera extrait de la requête si non fourni)",
        example="192.168.1.1"
    )

class CommandCandidate(BaseModel):
    """Réponse avec la commande Nmap générée"""
    command: str = Field(..., description="Commande Nmap générée")
    confidence: float = Field(..., description="Score de confiance (0.0 à 1.0)", ge=0.0, le=1.0)
    validation_passed: bool = Field(..., description="Si la validation a réussi")
    source_agent: str = Field(..., description="Nom de l'agent qui a généré la commande")
    warnings: List[str] = Field(default=[], description="Avertissements")
    errors: List[str] = Field(default=[], description="Erreurs")
    rationale: str = Field(..., description="Explication de la génération")
    processing_time_ms: Optional[float] = Field(default=None, description="Temps de traitement en ms")

class HealthCheck(BaseModel):
    """Statut de santé de l'API"""
    status: str = Field(..., description="Statut du service")
    neo4j_connected: bool = Field(..., description="Connexion à Neo4j active")
    api_version: str = Field(..., description="Version de l'API")
    uptime_seconds: Optional[float] = Field(default=None, description="Temps de fonctionnement en secondes")