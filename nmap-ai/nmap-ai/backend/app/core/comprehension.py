from app.models.schemas import ComprehensionResult


class ComprehensionService:
    def analyze(self, text: str) -> ComprehensionResult:
        """
        Analyse simple : détecte si la requête parle de Nmap.
        """
        text_lower = text.lower()

        if "nmap" in text_lower:
            return ComprehensionResult(
                is_nmap_related=True,
                reason="Mot-clé 'nmap' détecté dans la requête"
            )

        return ComprehensionResult(
            is_nmap_related=False,
            reason="Aucun mot-clé lié à Nmap détecté"
        )
