import os
from dotenv import load_dotenv

# === Charger le fichier .env au démarrage ===
# .env (ou .env.example) doit être dans ton dossier backend/
load_dotenv()

# === Variables principales des services ===
RAG_BASE_URL = os.getenv("RAG_BASE_URL", "http://localhost:8001")
GENERATION_BASE_URL = os.getenv("GENERATION_BASE_URL")
VALIDATION_BASE_URL = os.getenv("VALIDATION_BASE_URL")
# === Paramètres de pipeline ===
MAX_CORRECTIONS = int(os.getenv("MAX_CORRECTIONS", "3"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# === Pour ton orchestrateur ou les logs ===
APP_NAME = "NMAP-AI Orchestrator"
VERSION = "1.0.0"
