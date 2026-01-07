from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import asyncio
import time

from app.api.models import NmapRequest, CommandCandidate, HealthCheck
from app.agents.rag_agent_api import NmapRAGAPIAgent, UserQuery
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1",
    tags=["rag"],
    responses={404: {"description": "Not found"}}
)

# Variable globale pour l'agent
_rag_agent = None

async def get_rag_agent() -> NmapRAGAPIAgent:
    """Dependency pour obtenir l'agent RAG"""
    global _rag_agent
    
    if _rag_agent is None:
        _rag_agent = NmapRAGAPIAgent(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password
        )
    
    return _rag_agent

@router.get("/health", response_model=HealthCheck)
async def health_check(agent: NmapRAGAPIAgent = Depends(get_rag_agent)):
    """Vérifie la santé de l'API et de Neo4j"""
    neo4j_connected = await agent.check_connection()
    
    return {
        "status": "healthy" if neo4j_connected else "degraded",
        "neo4j_connected": neo4j_connected,
        "api_version": settings.api_version,
        "uptime_seconds": agent.get_uptime()
    }

@router.post("/generate", response_model=CommandCandidate)
async def generate_nmap_command(
    request: NmapRequest,
    background_tasks: BackgroundTasks,
    agent: NmapRAGAPIAgent = Depends(get_rag_agent)
):
    """
    Génère une commande Nmap à partir d'une requête en langage naturel
    
    - **query**: Requête en langage naturel (ex: "scan UDP sur 192.168.1.1 avec scripts")
    - **complexity**: Niveau de complexité (easy, medium, hard)
    - **target**: Cible spécifique (optionnel)
    """
    try:
        # Création de la requête utilisateur
        user_query = UserQuery(
            text=request.query,
            complexity=request.complexity,
            target=request.target
        )
        
        # Génération de la commande
        result = await agent.generate_command(user_query)
        
        return CommandCandidate(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération: {str(e)}")

@router.get("/test-examples", response_model=List[CommandCandidate])
async def test_examples(agent: NmapRAGAPIAgent = Depends(get_rag_agent)):
    """Retourne des exemples de génération pour tester l'API"""
    examples = [
        NmapRequest(query="scan UDP sur 192.168.1.1 avec scripts"),
        NmapRequest(query="scan SYN sur google.com"),
        NmapRequest(query="scan avec détection de version"),
        NmapRequest(query="scan agressif avec OS detection"),
        NmapRequest(query="scan TCP sur les ports 80,443"),
    ]
    
    results = []
    for example in examples:
        user_query = UserQuery(
            text=example.query,
            complexity=example.complexity,
            target=example.target
        )
        
        result = await agent.generate_command(user_query)
        results.append(CommandCandidate(**result))
    
    return results

@router.get("/quick-test/{query:path}")
async def quick_test(query: str, agent: NmapRAGAPIAgent = Depends(get_rag_agent)):
    """
    Test rapide avec une requête dans l'URL
    
    Exemple: /api/v1/quick-test/scan%20UDP%20sur%20192.168.1.1
    """
    try:
        user_query = UserQuery(text=query)
        result = await agent.generate_command(user_query)
        
        return {
            "query": query,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))