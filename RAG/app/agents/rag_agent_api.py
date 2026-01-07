import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from neo4j import AsyncGraphDatabase
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class UserQuery:
    """Représente une requête utilisateur pour l'API"""
    text: str
    complexity: str = "easy"
    confidence: float = 0.0
    target: Optional[str] = None

class NmapRAGAPIAgent:
    """
    Agent RAG adapté pour l'API REST
    Version simplifiée et optimisée
    """
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = AsyncGraphDatabase.driver(
            neo4j_uri, 
            auth=(neo4j_user, neo4j_password)
        )
        self.start_time = time.time()
        logger.info("✅ Agent RAG API initialisé")
    
    async def _query_kg(self, cypher_query: str, params: Dict = None) -> List[Dict]:
        """Exécute une requête Cypher"""
        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, params or {})
                return await result.data()
        except Exception as e:
            logger.error(f"Erreur Neo4j: {e}")
            return []
    
    async def check_connection(self) -> bool:
        """Vérifie la connexion à Neo4j"""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.consume()
            return True
        except Exception as e:
            logger.error(f"Connexion Neo4j échouée: {e}")
            return False
    
    async def generate_command(self, user_query: UserQuery) -> Dict[str, Any]:
        """
        Génère une commande Nmap - version API optimisée
        """
        start_time = time.time()
        query_text = user_query.text
        query_lower = query_text.lower()
        
        try:
            # 1. Détection du type de scan
            scan_type = await self._detect_scan_type(query_lower)
            
            # 2. Extraction de la cible
            target = user_query.target or self._extract_target(query_text)
            
            # 3. Extraction des ports (seulement si explicite)
            ports = self._extract_ports_explicit(query_lower)
            
            # 4. Options additionnelles
            options = await self._extract_options(query_lower, scan_type)
            
            # 5. Scripts
            scripts = await self._extract_scripts(query_lower) if "script" in query_lower else []
            
            # 6. Construction de la commande
            command = self._build_final_command(
                scan_type=scan_type,
                target=target,
                ports=ports,
                options=options,
                scripts=scripts,
                query_lower=query_lower
            )
            
            # 7. Calcul de la confiance
            confidence = self._calculate_confidence(
                scan_type=scan_type,
                target=target,
                ports=ports,
                options=options,
                scripts=scripts
            )
            
            # 8. Génération des avertissements
            warnings = self._generate_warnings(
                scan_type=scan_type,
                ports=ports,
                scripts=scripts
            )
            
            # 9. Rationale
            rationale = self._generate_rationale(
                scan_type=scan_type,
                target=target,
                ports=ports,
                options=options,
                scripts=scripts,
                confidence=confidence,
                warnings=warnings
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "command": command,
                "confidence": confidence,
                "validation_passed": True,
                "source_agent": "KG-RAG-API",
                "warnings": warnings,
                "errors": [],
                "rationale": rationale,
                "processing_time_ms": round(processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Erreur génération: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "command": "nmap -sS -T3 scanme.nmap.org",
                "confidence": 0.5,
                "validation_passed": False,
                "source_agent": "KG-RAG-API-Error",
                "warnings": [],
                "errors": [f"Erreur: {str(e)}"],
                "rationale": f"Erreur lors de la génération: {str(e)}",
                "processing_time_ms": round(processing_time, 2)
            }
    
    async def _detect_scan_type(self, query_lower: str) -> str:
        """Détecte le type de scan"""
        scan_patterns = [
            (["udp"], "-sU"),
            (["syn", "stealth", "furtif"], "-sS"),
            (["tcp", "connect"], "-sT"),
            (["version", "service", "détection de service"], "-sV"),
            (["os", "operating system", "système d'exploitation"], "-O"),
            (["aggressif", "aggressive", "complet"], "-A"),
            (["ping", "host discovery"], "-sn"),
            (["null"], "-sN"),
            (["fin"], "-sF"),
            (["xmas", "christmas"], "-sX"),
            (["ack"], "-sA"),
        ]
        
        for keywords, scan_flag in scan_patterns:
            if any(keyword in query_lower for keyword in keywords):
                return scan_flag
        
        return "-sS"  # Par défaut
    
    def _extract_target(self, query_text: str) -> str:
        """Extrait la cible"""
        # IP
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}(?:\/\d{1,2})?(?:-\d{1,3})?\b'
        ip_match = re.search(ip_pattern, query_text)
        if ip_match:
            return ip_match.group(0)
        
        # Domaine
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        domain_match = re.search(domain_pattern, query_text, re.IGNORECASE)
        if domain_match:
            return domain_match.group(0)
        
        return "scanme.nmap.org"
    
    def _extract_ports_explicit(self, query_lower: str) -> Optional[str]:
        """Extrait les ports seulement si explicitement demandés"""
        patterns = [
            (r'port\s+(\d+)', lambda m: f"-p {m.group(1)}"),
            (r'ports?\s+(\d+\s*-\s*\d+)', lambda m: f"-p {re.sub(r'\s+', '', m.group(1))}"),
            (r'ports?\s+(\d+(?:[,\s]+\d+)+)', lambda m: f"-p {re.sub(r'\s+', '', m.group(1))}"),
            (r'de\s*(\d+)\s*à\s*(\d+)', lambda m: f"-p {m.group(1)}-{m.group(2)}"),
        ]
        
        for pattern, formatter in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return formatter(match)
        
        # Options spéciales
        if "common" in query_lower or "top" in query_lower:
            return "--top-ports 100"
        
        if "all" in query_lower or "tous" in query_lower:
            return "-p-"
        
        if "fast" in query_lower or "rapide" in query_lower:
            return "-F"
        
        return None
    
    async def _extract_options(self, query_lower: str, scan_type: str) -> List[str]:
        """Extrait les options additionnelles"""
        options = []
        option_map = {
            "-sV": ["version", "service"],
            "-O": ["os", "operating system"],
            "--traceroute": ["traceroute", "tracert"],
            "-F": ["fast", "rapide", "quick"],
            "-6": ["ipv6", "v6"],
            "-Pn": ["no ping", "skip ping"],
            "-n": ["no dns", "skip dns"],
            "-v": ["verbose"],
            "-vv": ["very verbose", "debug"],
            "-sC": ["script", "scripts"],
        }
        
        for option, keywords in option_map.items():
            if any(keyword in query_lower for keyword in keywords):
                # Éviter redondances
                if scan_type != "-A" or option not in ["-sV", "-O", "-sC"]:
                    options.append(option)
        
        return list(set(options))
    
    async def _extract_scripts(self, query_lower: str) -> List[str]:
        """Extrait les scripts"""
        scripts = []
        
        # Chercher les scripts populaires
        result = await self._query_kg("""
            MATCH (s:NseScript)
            RETURN s.name as name, s.count as count
            ORDER BY s.count DESC
            LIMIT 5
        """)
        
        for record in result:
            script_name = record.get("name")
            if script_name and script_name not in scripts:
                scripts.append(script_name)
        
        return scripts
    
    def _build_final_command(self, **kwargs) -> str:
        """Construit la commande finale"""
        parts = ["nmap"]
        
        # Scan type
        parts.append(kwargs["scan_type"])
        
        # Options
        for opt in kwargs.get("options", []):
            if opt not in parts:
                parts.append(opt)
        
        # Timing
        timing = "-T3"
        if "aggressif" in kwargs["query_lower"] or kwargs["scan_type"] == "-A":
            timing = "-T4"
        elif "furtif" in kwargs["query_lower"] or kwargs["scan_type"] in ["-sN", "-sF", "-sX"]:
            timing = "-T1"
        
        parts.append(timing)
        
        # Ports
        if kwargs.get("ports"):
            parts.append(kwargs["ports"])
        
        # Scripts
        if kwargs.get("scripts") and kwargs["scan_type"] != "-A":
            scripts = kwargs["scripts"]
            if len(scripts) == 1:
                parts.append(f"--script {scripts[0]}")
            else:
                parts.append(f"--script \"{','.join(scripts)}\"")
        
        # Target
        parts.append(kwargs["target"])
        
        return " ".join(parts)
    
    def _calculate_confidence(self, **kwargs) -> float:
        """Calcule la confiance"""
        score = 0.8
        
        # Bonus pour spécificité
        if kwargs["target"] != "scanme.nmap.org":
            score += 0.1
        
        if kwargs.get("ports"):
            score += 0.05
        
        if kwargs.get("scripts"):
            score += 0.03
        
        if kwargs.get("options"):
            score += 0.02
        
        return min(0.98, max(0.6, score))
    
    def _generate_warnings(self, **kwargs) -> List[str]:
        """Génère les avertissements"""
        warnings = []
        
        # Warnings pour scan UDP
        if kwargs["scan_type"] == "-sU" and not kwargs.get("ports"):
            warnings.append("Scan UDP sans ports spécifiés → très long")
            warnings.append("Nécessite les privilèges root (sudo)")
        
        # Warnings pour root
        if kwargs["scan_type"] in ["-sU", "-sS", "-O"]:
            warnings.append("Privilèges root requis")
        
        # Warnings pour timing
        if "aggressif" in kwargs.get("query_lower", ""):
            warnings.append("Timing agressif (-T4)")
        
        return warnings
    
    def _generate_rationale(self, **kwargs) -> str:
        """Génère l'explication"""
        lines = []
        lines.append("## 📊 Commande Nmap générée")
        lines.append("")
        lines.append(f"**Scan:** {kwargs['scan_type']}")
        lines.append(f"**Cible:** {kwargs['target']}")
        
        if kwargs.get("ports"):
            lines.append(f"**Ports:** {kwargs['ports']}")
        
        if kwargs.get("options"):
            lines.append(f"**Options:** {', '.join(kwargs['options'])}")
        
        if kwargs.get("scripts"):
            lines.append(f"**Scripts:** {', '.join(kwargs['scripts'])}")
        
        lines.append(f"**Confiance:** {kwargs['confidence']:.2%}")
        lines.append("")
        lines.append("**Source:** Knowledge Graph Neo4j")
        
        return "\n".join(lines)
    
    def get_uptime(self) -> float:
        """Retourne le temps de fonctionnement"""
        return time.time() - self.start_time
    
    async def close(self):
        """Ferme la connexion"""
        await self.driver.close()
        logger.info("Connexion Neo4j fermée")