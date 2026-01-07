#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 API pour Backend - Agents Hard & Medium
Deux endpoints séparés : /hard et /medium
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Importer les agents
from agents.hard_agent_final import HardAgent, UserQuery, CommandCandidate as HardCommandCandidate
from agents.medium_agent_final import MediumAgent, CommandCandidate as MediumCommandCandidate

# ============================================
# MODÈLES PYDANTIC POUR L'API
# ============================================

class UserQueryRequest(BaseModel):
    """Requête du backend"""
    query: str

class CommandCandidateResponse(BaseModel):
    """Réponse au backend"""
    command: str
    rationale: str
    source_agent: str

# ============================================
# INITIALISATION FASTAPI
# ============================================

app = FastAPI(
    title="Nmap Agents API",
    description="API avec 2 endpoints : /hard et /medium",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agents globaux
hard_agent = None
medium_agent = None

# ============================================
# STARTUP - CHARGER LES AGENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Charge les agents au démarrage"""
    global hard_agent, medium_agent
    
    print("=" * 70)
    print("🔄 CHARGEMENT DES AGENTS")
    print("=" * 70)
    
    # Chemins
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "nmap_dataset_enriched.json")
    
    try:
        # Hard Agent
        print("\n1️⃣ Chargement Hard Agent...")
        hard_agent = HardAgent(dataset_path=dataset_path if os.path.exists(dataset_path) else None)
        
        # Medium Agent
        print("\n2️⃣ Chargement Medium Agent...")
        medium_agent = MediumAgent(dataset_path=dataset_path if os.path.exists(dataset_path) else None)
        
        print("\n" + "=" * 70)
        print("✅ AGENTS CHARGÉS AVEC SUCCÈS!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("\n💡 Vérifiez:")
        print("   - Le modèle T5 est dans: models/t5_nmap_final/")
        print("   - Le dataset est dans: data/nmap_dataset_enriched.json")
        print("   - Les dépendances sont installées\n")

# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "name": "Nmap Agents API",
        "version": "1.0.0",
        "endpoints": {
            "POST /hard": "Hard Agent (Diffusion)",
            "POST /medium": "Medium Agent (T5-LoRA)"
        },
        "format": "UserQuery -> CommandCandidate"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "agents": {
            "HARD": hard_agent is not None,
            "MEDIUM": medium_agent is not None
        }
    }

# ============================================
# ENDPOINT 1 : HARD AGENT
# ============================================

@app.post("/hard", response_model=CommandCandidateResponse)
async def generate_hard(request: UserQueryRequest) -> CommandCandidateResponse:
    """
    Génère une commande Nmap via Hard Agent (Diffusion)
    
    Body:
    {
        "query": "Stealth scan with 10 decoys on target.com"
    }
    
    Returns:
    {
        "command": "nmap -sS -T2 -D RND:10 target.com",
        "rationale": "Diffusion-based synthesis: SYN stealth scan, polite timing, 10 random decoys...",
        "source_agent": "DIFFUSION"
    }
    """
    # Valider
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Vérifier que l'agent est chargé
    if hard_agent is None:
        raise HTTPException(status_code=503, detail="Hard agent not loaded")
    
    # Appeler Hard Agent
    try:
        user_query = UserQuery(request.query)
        result = await hard_agent.generate(user_query)
        
        return CommandCandidateResponse(
            command=result.command,
            rationale=result.rationale,
            source_agent=result.source_agent
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hard agent error: {str(e)}")

# ============================================
# ENDPOINT 2 : MEDIUM AGENT
# ============================================

@app.post("/medium", response_model=CommandCandidateResponse)
async def generate_medium(request: UserQueryRequest) -> CommandCandidateResponse:
    """
    Génère une commande Nmap via Medium Agent (T5-LoRA)
    
    Body:
    {
        "query": "Scan all ports on 192.168.1.1"
    }
    
    Returns:
    {
        "command": "nmap -p- 192.168.1.1",
        "rationale": "T5-LoRA generation: all 65535 ports, target 192.168.1.1",
        "source_agent": "MEDIUM"
    }
    """
    # Valider
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Vérifier que l'agent est chargé
    if medium_agent is None:
        raise HTTPException(status_code=503, detail="Medium agent not loaded")
    
    # Appeler Medium Agent
    try:
        user_query = UserQuery(request.query)
        result = await medium_agent.generate(user_query)
        
        return CommandCandidateResponse(
            command=result.command,
            rationale=result.rationale,
            source_agent=result.source_agent
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medium agent error: {str(e)}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 API NMAP AGENTS - 2 ENDPOINTS")
    print("=" * 70)
    print("\n📍 Endpoints:")
    print("   GET  /              - Info")
    print("   GET  /health        - Health check")
    print("   POST /hard          - Hard Agent (Diffusion)")
    print("   POST /medium        - Medium Agent (T5-LoRA)")
    print("\n🌐 URL: http://localhost:8002")
    print("📚 Docs: http://localhost:8002/docs")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )