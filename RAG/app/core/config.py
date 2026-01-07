from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API
    api_title: str = "NMAP-AI RAG API"
    api_version: str = "1.0.0"
    api_description: str = "API REST pour l'agent RAG Nmap avec Knowledge Graph"
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "Wissal@123"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()