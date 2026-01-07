from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes.rag import router as rag_router
from app.agents.rag_agent_api import NmapRAGAPIAgent
from app.core.config import settings

# Variable globale pour l'agent
rag_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global rag_agent
    
    # Démarrage
    print("🚀 Démarrage de l'API NMAP-AI RAG...")
    
    # Initialisation de l'agent RAG
    rag_agent = NmapRAGAPIAgent(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password
    )
    
    print(f"✅ Agent RAG initialisé")
    print(f"📡 API disponible sur: http://{settings.host}:{settings.port}")
    print(f"📚 Documentation: http://{settings.host}:{settings.port}/docs")
    
    yield
    
    # Arrêt
    print("\n🛑 Arrêt de l'API NMAP-AI RAG...")
    if rag_agent:
        await rag_agent.close()
        print("✅ Agent RAG fermé")

# Création de l'application FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(rag_router)

# Route racine
@app.get("/")
async def root():
    """Route racine avec informations sur l'API"""
    return {
        "message": "Bienvenue sur l'API NMAP-AI RAG",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "generate": "/api/v1/generate",
            "test_examples": "/api/v1/test-examples",
            "quick_test": "/api/v1/quick-test/{query}"
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Éviter les erreurs favicon"""
    return {"message": "No favicon"}