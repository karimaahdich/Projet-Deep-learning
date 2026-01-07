# app/core/mcp.py
import json
from datetime import datetime
from loguru import logger
from typing import Any, Dict
import os

class MCPLogger:
    """
    Model Context Protocol Logger
    Enregistre les étapes clés du pipeline pour testing et validation.
    """
    
    def __init__(self, log_file: str = "mcp_context_logs.jsonl"):
        self.log_file = log_file
        # Crée le fichier s'il n'existe pas
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                pass  # Crée un fichier vide

    def log(self, stage: str, data: Dict[str, Any]):
        """
        Enregistre une étape avec timestamp et données structurées.
        Format JSONL (une ligne = un événement).
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            **data
        }
        
        logger.debug(f"MCP → {stage}: {data.get('level', '')} | {data.get('status', '')}")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")