from typing import Iterable
from app.models.schemas import ClassificationResult, ComplexityResult

# === Mots-clés de base pour détecter si la requête concerne Nmap ===
NMAP_HINTS: Iterable[str] = (
    "nmap", "-sS", "-sU", "-A", "-p", "--open", "udp", "tcp", "scan", "port", "os detect"
)

def is_nmap_related(text: str) -> ClassificationResult:
    """
    Vérifie si la requête utilisateur est liée à Nmap
    en cherchant des mots-clés connus.
    """
    t = text.lower()
    hit = any(h in t for h in NMAP_HINTS)
    reason = "Contient des mots-clés Nmap" if hit else "Aucun mot-clé détecté"
    return ClassificationResult(is_nmap_related=hit, reason=reason)

def baseline_complexity(text: str) -> ComplexityResult:
    """
    Estime la complexité d'une requête Nmap :
    - easy : basique (scan simple)
    - medium : options supplémentaires
    - hard : scan complet, évasion, UDP, etc.
    """
    t = text.lower()

    if any(k in t for k in ["udp", "all ports", "os detect", "fragment", "bypass", "evasion"]):
        return ComplexityResult(level="hard", confidence=0.7)

    if any(k in t for k in ["version", "scripts", "timing", "exclude", "-sV"]):
        return ComplexityResult(level="medium", confidence=0.6)

    return ComplexityResult(level="easy", confidence=0.8)
