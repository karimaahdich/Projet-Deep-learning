# NMAP-AI: Autonomous Nmap Command Generator

**Knowledge Graph RAG • Fine-Tuning • MCP (Model Context Protocol)**

**NMAP-AI** est un système agentique intelligent qui transforme une intention de scan réseau exprimée en langage naturel en une commande Nmap **sûre, valide, optimisée et exécutable**.

## Fonctionnalités clés

- Génération progressive par niveaux de complexité (easy → medium → hard)
- **Escalade automatique** en cas d’échec ou d’indisponibilité d’un agent
- **Self-correction** intelligente grâce à un validator dédié
- **Traçabilité complète** via le **MCP (Model Context Protocol)**
- Architecture **microservices distribuée** sur plusieurs machines
- Tests unitaires à 100 % avec pytest

## Pipeline du système

Le système suit un pipeline résilient orchestré par un backend FastAPI :
comprehension ->complexity ->AGENT -> commande candidate ->validator ->escalade si commande non valide ->commande final

![Pipeline ](./images/pipeline.png)

1. **Requête utilisateur** en langage naturel
2. **Compréhension & classification** de la complexité (easy / medium / hard)
3. **Génération progressive** :
   - Easy → Agent KG-RAG (Knowledge Graph Neo4j)
   - Medium → LLM fine-tuné (LoRA)
   - Hard → Agent Diffusion-based
4. **Validation** par un agent dédié
5. **Self-correction** si la commande est réparable
6. **Escalade automatique** vers un agent plus puissant si nécessaire
7. **Réponse finale** avec commande validée et confidence

### Escalade automatique en cas de panne

Si un agent est indisponible ou retourne une commande invalide, l’orchestrateur escalade automatiquement :

![Escalade automatique en cas de panne](./images/Escalade automatique en cas de panne.png)

### Model Context Protocol (MCP)

Toutes les étapes sont tracées dans un fichier JSONL structuré pour le debugging et l’audit :

![Exemple de logs MCP](./images/MCP.png)

### Tests unitaires (pytest)

L’orchestrateur est couvert à 100 % par des tests automatisés :

![Pytest 100% passed](./images/pytest.png)

## Architecture microservices distribuée

Le système est déployé sur plusieurs machines indépendantes :

| Agent                     | Port  | Endpoint principal               | 
|---------------------------|-------|----------------------------------|
| Orchestrateur (backend)   | 8000  | `POST /api/v1/command/generate`  |         
| KG-RAG (Neo4j)            | 8001  | `POST /api/v1/generate`          | 
| LLM (medium) + Diffusion (hard) | 8002  | `/medium` et `/hard`                 |
| Validator + Self-Correction | 8004  | `/api/v1/validate` et `/api/v1/repair` | 

Configuration via `.env` avec les URLs de base → résilience et déploiement distribué.

## Arborescence du projet backend
NMAP-AI/
└── backend/
├── .venv/
├── pycache/
├── app/
│   ├── agents/
│   │   ├── rag_client.py
│   │   ├── llm_client.py
│   │   ├── diffusion_client.py
│   │   ├── validator_client.py
│   │   └── selfcorr_client.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── mcp.py
│   ├── models/
│   │   └── schemas.py
│   ├── orchestrator/
│   │   ├── engine.py
│   │   └── classify.py
│   └── main.py
├── tests/
│   └── test_orchestrator.py
├── .env
├── mcp_context_logs.jsonl
├── pyproject.toml
└── requirements.txt
## Comment lancer le projet

### 1. Lancer l’orchestrateur (backend central)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

API disponible sur : http://localhost:8000/docs
2. Lancer les agents externes 
KG-RAG : uvicorn RAG_agent:app --port 8001 --host 0.0.0.0 --reload
LLM & Diffusion : uvicorn generation_api:app --port 8002 --host 0.0.0.0 --reload
Validator & Self-Correction : uvicorn validation_api:app --port 8004 --host 0.0.0.0 --reload

Mettre à jour le .env avec les IPs réelles des machines.

**Agent** **RAG** **-** 
> **Technique**
>
> **Vue** **d'ensemble**
>
> L'**Agent** **RAG** **Retrieval-Augmented** **Generation)** est un
> composant spécialisé du système NMAPAI, conçu pour traiter les
> requêtes utilisateur de **complexité** **faible** Easy) et générer
> des commandes Nmap valides, sûres et optimisées. Cet agent exploite
> une base de connaissances structurée sous forme de graphe Neo4j pour
> la validation sémantique et syntaxique des commandes.
>
> **Architecture** **du** **projet**
>
> TEST_PROJECT_NMAP/ │
>
> ├── app/ \# Code principal de l'application │ ├── agents/ \# Code des
> agents spécialisés
>
> │ │ └── rag_agent_api.py \# Implémentation principale de l'Agent RAG │
> ├── api/ \# Points d'entrée API
>
> │ │ ├── routes/ \# Définition des routes API
>
> │ │ │ ├── rag.py
>
> │ │ │ ├── main.py

\# Route dédiée à l'Agent RAG

> \# Logique API principale
>
> │ │ │ └── models.py \# Modèles de données Pydantic │ │ └──
> \_\_init\_\_.py \# Initialisation du package API
>
> │ └── \_\_pycache\_\_/ \# Fichiers Python compilés │
>
> ├── core/ \# Configuration et services centraux
>
> │ ├── \_\_pycache\_\_/ │ └── config.py
>
> │
>
> \# Fichiers Python compilés

\# Configuration globale Neo4j, logging, etc.)

> ├── venv/
>
> ├── requirements.txt

\# Environnement virtuel Python

> \# Dépendances du projet

ReadMe 1

> ├── run.py
>
> └── test_api.py

\# Script de lancement de l'application

> \# Tests de l'API
>
> **Prérequis** **&** **Installation**
>
> **1.Environnement** **logiciel** **requis**
>
> **Python** **3.10**
>
> **Neo4j** **5.x** avec la base de connaissances NMAP préchargée 458
> nœuds, 11551 relations)
>
> **FastAPI** pour le serveur API
>
> **Uvicorn** pour l'exécution asynchrone
>
> **2.Installation** **des** **dépendances**
>
> bash
>
> \# Création de l'environnement virtuel python -m venv venv
>
> \# Activation venv\Scripts\activate
>
> \# Installation des packages pip install -r requirements.txt
>
> **3.Configuration** **de** **la** **base** **Neo4j**
>
> Éditez core/config.py avec vos paramètres de connexion :
>
> python
>
> NEO4J_URI  "bolt://localhost:7687" NEO4J_USER  "neo4j"
> NEO4J_PASSWORD  Wissal123 NEO4J_DATABASE  neo4j
>
> \# Configuration de l'Agent RAG

ReadMe 2

> RAG_TIMEOUT  30 \# secondes MAX_COMMAND_LENGTH  2000 \# caractères
>
> **Démarrage** **rapide**
>
> **1.Lancer** **le** **serveur** **API**
>
> python run.py
>
> Le serveur démarre sur http://localhost:8001
>
> **2.Vérifier** **l'état** **du** **service**
>
> bash
>
> curl http://localhost:8001/health
>
> **3.Tester** **l'Agent** **RAG**
>
> bash
>
> curl X POST http://localhost:8000/api/rag/generate \\ H
> "Content-Type: application/json" \\
>
> -d '{"query": "scan SYN sur google.com port 80"}'
>
> **Architecture** **technique** **de** **l'Agent** **RAG**
>
> **Composants** **principaux** **:**
>
> **1.** **app/agents/rag_agent_api.py** **-** **Cœur** **de**
> **l'Agent** **RAG**
>
> **Classe** **RAGClient**  Orchestrateur principal
>
> **Méthode** **generate()**  Point d'entrée pour la génération de
> commandes
>
> **Intégration** **Neo4j**  Client pour interroger le graphe de
> connaissances
>
> **Validation** **en** **temps** **réel**  Vérification des conflits
> et dépendances

ReadMe 3

> **2.** **app/api/routes/rag.py** **-** **Interface** **REST**
>
> **Endpoint** **/api/rag/generate**  Accepte les requêtes en langage
> naturel
>
> **Validation** **des** **entrées**  Via les modèles Pydantic
>
> **Gestion** **des** **erreurs**  Retours d'erreur structurés
>
> **Logging** **complet**  Traçabilité de chaque requête
>
> **3.** **app/api/models.py** **-** **Modèles** **de** **données**
>
> python
>
> class UserQuery:
>
> """Représente une requête utilisateur pour l'API""" text: str
>
> complexity: str = "easy" confidence: float  0.0 target:
> Optional\[str\]  None
>
> class CommandCandidate(BaseModel):
>
> """Réponse avec la commande Nmap générée"""
>
> command: str  Field(..., description="Commande Nmap générée")
> confidence: float  Field(..., description="Score de confiance 0.0 à
> 1.0",
>
> ge=0.0, le=1.0
>
> validation_passed: bool  Field(..., description="Si la validation a
> réussi") source_agent: str  Field(..., description="Nom de l'agent
> qui a généré la
>
> commande")
>
> warnings: List\[str\]  Field(default=\[\],
> description="Avertissements") errors: List\[str\] 
> Field(default=\[\], description="Erreurs")
>
> rationale: str  Field(..., description="Explication de la
> génération") processing_time_ms: Optional\[float\] 
> Field(default=None, description
>
> ="Temps de traitement en ms")
>
> **4.** **core/config.py** **-** **Configuration** **centralisée**
>
> Gestion des connexions Neo4j
>
> Paramètres de performance
>
> Niveaux de logging

ReadMe 4

> Constantes métier
>
> 🔄 **Flux** **de** **traitement** **d'une** **requête** text
>
> ┌─────────────────┐ │ Requête │
>
> │ Utilisateur │ └────────┬────────┘
>
> │ POST /api/rag/generate) ▼
>
> ┌─────────────────┐ │ FastAPI Route │
>
> │ (rag.py) │ └────────┬────────┘
>
> │ (validation, parsing) ▼
>
> ┌─────────────────┐ │ RAGClient │
>
> │ (rag_agent_api) │ └────────┬────────┘
>
> │ 1. Analyse sémantique │ 2. Traversal du graphe
>
> │ 3. Construction commande │ 4. Validation interne
>
> ▼ ┌─────────────────┐ │ Neo4j Graph │
>
> │ 458 nœuds) │ │ 11551 rel.) │
>
> └────────┬────────┘
>
> │ (retour des options validées) ▼
>
> ┌─────────────────┐ │ Génération │
>
> │ Commande │ └────────┬────────┘
>
> │

ReadMe 5

> ▼ ┌─────────────────┐ │ Réponse API │
>
> │ CommandCandidate │ └─────────────────┘
>
> **Entités** **Neo4j** **exploitées**
>
> L'Agent RAG utilise activement les entités du graphe de connaissances
> :
>
> **Nœuds** **principaux** **utilisés** **:**
>
> **NmapOption**  Options de ligne de commande (-sS, O, A, etc.)
>
> **NseScript**  Scripts du Nmap Scripting Engine
>
> **OptionCategory**  Catégorisation fonctionnelle
>
> **Privilege**  Niveaux de droits requis (root/user)
>
> **ScanTechnique**  Techniques de scan réseau
>
> **Relations** **clés** **vérifiées** **:**
>
> **REQUIRES**  Vérification des prérequis
>
> **CONFLICTS_WITH**  Détection d'incompatibilités
>
> **DEPENDS_ON**  Gestion des dépendances
>
> **APPLIES_TO**  Association option → contexte
>
> **BELONGS_TO**  Hiérarchisation des options
>
> **Points** **d'API** **disponibles**
>
> **1.** **Génération** **de** **commande**
>
> http
>
> POST /api/rag/generate Content-Type: application/json
>
> {
>
> "query": "scan UDP sur 192.168.1.1 avec scripts",

ReadMe 6

> "complexity": "easy", "target": "192.168.1.1"
>
> }
>
> **Réponse** **réussie** **:**
>
> json
>
> {
>
> "command": "nmap -sU -sC T3 --script
> \\default,ssl-cert,malware,vuln,a uth\\ 192.168.1.1",
>
> "confidence" 0.9500000000000001, "validation_passed": true,
> "source_agent": "KGRAGAPI", "warnings": \[
>
> "Scan UDP sans ports spécifiés → très long", "Nécessite les privilèges
> root (sudo)", "Privilèges root requis"
>
> \],
>
> "errors": \[\],
>
> "rationale": "## 📊 Commande Nmap générée\n\n\*\*Scan:\*\*
> -sU\n\*\*Cible: \*\* 192.168.1.1\n\*\*Options:\*\*
> -sC\n\*\*Scripts:\*\* default, ssl-cert, malware, vu ln,
> auth\n\*\*Confiance:\*\* 95.00%\n\n\*\*Source:\*\* Knowledge Graph
> Neo4j",
>
> "processing_time_ms" 2227.69 }
>
> **2.** **Vérification** **de** **santé**
>
> http
>
> GET /health
>
> **3.** **Informations** **sur** **l'agent**
>
> http
>
> GET /api/rag/info

ReadMe 7

> **Tests** **et** **validation**
>
> **Exécution** **des** **tests**
>
> bash
>
> python test_api.py
>
> **Tests** **couverts** **:**
>
> ✅ Connexion à l'API
>
> ✅ Génération de commandes simples
>
> ✅ Gestion des erreurs
>
> ✅ Validation des entrées
>
> ✅ Performance des requêtes
>
> **Exemple** **de** **test** **manuel** **:**
>
> python
>
> import requests
>
> response = requests.post( "http://localhost:8000/api/rag/generate",
> json={
>
> "query": "détection OS et version sur scanme.nmap.org",
> "complexity_level": "easy"
>
> } )
>
> print(response.json())
>
> **2.** **Optimisations** **Neo4j**
>
> Indexation automatique sur les propriétés fréquemment interrogées
>
> Requêtes Cypher optimisées avec EXPLAIN
>
> Pool de connexions pour les performances

ReadMe 8

> **3.** **Sécurité**
>
> Validation stricte des entrées utilisateur
>
> Sanitization des commandes générées
>
> Limitation de la longueur des requêtes
>
> Logging d'audit complet
>
> 📈 **Métriques** **de** **performance**
>
> L'Agent RAG expose des métriques via l'endpoint /api/rag/metrics :
>
> **Temps** **moyen** **de** **réponse** :  1.5 secondes
>
> **Taux** **de** **succès** :  95%
>
> **Utilisation** **mémoire** :  100 MB
>
> **Connexions** **Neo4j** **actives** : surveillées en temps réel
>
> **Intégration** **avec** **le** **système** **NMAP-AI**
>
> **Flux** **complet** **NMAP-AI** **avec** **RAG** **:**
>
> text
>
> Utilisateur\] → \[Agent Compréhension\] → \[Vérification Pertinence\]
> ↓ (si pertinent & complexité  Easy)
>
> Agent RAG  Base Neo4j\] ↓
>
> Commande générée\] → \[Validation MCP ↓
>
> Retour utilisateur\]
>
> **Points** **d'intégration** **:**
>
>  **Entrée**  Reçoit les requêtes prétraitées de l'Agent de
> Compréhension
>
>  **Sortie**  Fournit des CommandCandidate aux modules de validation
>
>  **Fallback**  Peut être contourné par les agents Medium/Hard si
> nécessaire

# NMAP-AI MEdium + Hard

## 🧠 Technologies

* Python
* FastAPI
* PyTorch
* Transformers (T5 + LoRA)
* Rule-based system


## 📌 Description du projet

Ce projet propose une API REST qui traduit des requêtes en langage naturel en commandes **nmap** valides grâce à deux agents distincts :

### 🔹 Medium Agent

* Modèle **T5-small** fine-tuné avec **LoRA**
* Entraîné sur 1 637 exemples
* Idéal pour les requêtes de complexité moyenne à élevée

### 🔹 Hard Agent

* Approche **rule-based + diffusion-inspired**
* Sans modèle ML
* Conçu pour gérer les requêtes très complexes :

  * Évasion IDS
  * Decoys
  * Spoofing
  * Timing personnalisé
  * Scripts NSE
  * Fragmentation, etc.

L’API expose deux endpoints indépendants :

* `/medium`
* `/hard`

Chaque endpoint retourne une réponse standardisée :

```json
{
  "command": "...",
  "rationale": "...",
  "source_agent": "..."
}
```

---

## ⚙️ Fonctionnalités

✅ Génération de commandes Nmap depuis des phrases naturelles
✅ Scans classiques (SYN, TCP, UDP, version detection, OS detection…)
✅ Techniques avancées d’évasion (decoys, fragmentation, MAC spoofing…)
✅ Timing personnalisé (`-T0` à `-T5`)
✅ Scripts NSE (`vuln`, `auth`, `default`…)
✅ Réponse structurée avec explication
✅ Health check
✅ Documentation Swagger & ReDoc intégrée

---

## 📁 Structure du projet

```
textnmap-agents-api/
├── agents/
│   ├── medium_agent_final.py
│   ├── hard_agent_final.py
│   └── __init__.py
├── data/
│   └── nmap_dataset_enriched.json
├── models/
│   └── t5_nmap_final/
├── api_final.py
├── requirements_final.txt
├── test_medium.py
├── test_hard.py
└── README.md
```

---

## 🚀 Installation

### 1️⃣ Cloner le repository

```bash
git clone https://github.com/votre-nom/nmap-agents-api.git
cd nmap-agents-api
```

---

### 2️⃣ Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\\Scripts\\activate       # Windows
```

---

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements_final.txt
```

⚠️ **Note** : PyTorch est lourd.
Si vous avez un GPU CUDA :

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### 4️⃣ Placer le modèle LoRA (Medium Agent)

Le dossier suivant doit contenir les fichiers du modèle LoRA fine-tuné :

```
models/t5_nmap_final/
```

Exemples de fichiers attendus :

* `adapter_model.bin`
* `adapter_config.json`

⚠️ Sans ce modèle, le **Medium Agent** plantera au démarrage.

---

## ▶️ Lancement de l'API

```bash
uvicorn api_final.py:app --host 0.0.0.0 --port 8002
```

---

## 🌐 Accès

* API : [http://localhost:8002](http://localhost:8002)
* Swagger UI : [http://localhost:8002/docs](http://localhost:8002/docs)
* ReDoc : [http://localhost:8002/redoc](http://localhost:8002/redoc)

---

## 📡 Utilisation de l'API

### Endpoint `/medium` (T5-LoRA)

```bash
curl -X POST http://localhost:8002/medium \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Scan all ports on 192.168.1.1 with version detection"}'
```

#### Réponse attendue

```json
{
  "command": "nmap -p- -sV 192.168.1.1",
  "rationale": "T5-LoRA generation: all 65535 ports, version detection, target 192.168.1.1",
  "source_agent": "MEDIUM"
}
```

---

### Endpoint `/hard` (Diffusion-based)

```bash
curl -X POST http://localhost:8002/hard \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Stealth scan with 15 random decoys, packet fragmentation and paranoid timing on example.com"}'
```

#### Réponse attendue

```json
{
  "command": "nmap -sS -T0 -f -D RND:15 example.com",
  "rationale": "Diffusion-based synthesis: SYN stealth scan, paranoid timing, packet fragmentation, 15 random decoys for IDS evasion, targeting example.com",
  "source_agent": "DIFFUSION"
}
```

---

## 🩺 Health Check

```bash
curl http://localhost:8002/health
```

---

## 🧪 Tests unitaires

```bash
python test_medium.py
python test_hard.py
```

Les deux scripts affichent plusieurs exemples de génération et valident le fonctionnement des agents.



# NMAP-AI Security Validation System

## Executive Summary

This document presents the **Validation & Security Layer**  for the **NMAP-AI project**, focusing on a command validation pipeline with Docker-based sandbox execution, security policy enforcement, and autonomous error correction.

### Key Achievements

* **3 Core Agents**: Validation Agent, Self-Correction Agent, Autonomous Repair System
* **Docker Sandbox**: Secure command testing
* **Security Policy Engine**: Flags, unsafe targets, risk scoring
* **Autonomous Repair**: 60-70% error correction without M3 involvement
* **Performance**: 2-3x faster corrections, 40-50% fewer M3 calls

---

## System Architecture

### High-Level Pipeline

* **M3**: Command Generation (1000-2000ms)
* **M4**: Validation Agent (100-200ms)

  * Syntax Checking
  * Security Policy Check
  * Sandbox Execution
  * Risk Scoring
* **M5**: Self-Correction Agent

  * **Auto Repair** (100-150ms): 60-70% success
  * **Iterative Repair** (600-900ms): 20-30% success
  * **M3 Regeneration** (2000ms): As a fallback

---

## Core Components

### Validation Agent (M4)

**File**: `validation/validation_v2.py`

Validates NMAP commands:

* **Syntax Validation**
* **Security Policy Enforcement**
* **Risk Scoring**

Example:

```python
class ValidationV2:
    def validate_single(command: str) -> Dict:
        # Returns command validation status, risk, and errors
```

### Self-Correction Agent (M5)

**Files**: `self_correction_agent.py`, `error_mapping_logic.py`

Automatically fixes commands:

* **Autonomous Fixes**: Known fixes (e.g., permission errors, syntax)
* **Iterative Loop**: Attempts up to 3 corrections

Example:

```python
class SelfCorrectionAgent:
    def attempt_autonomous_repair(command: str) -> Optional[Dict]:
        # Applies known fixes for errors
```

### Security Rules Engine

**File**: `validation/security_rules.py`

Enforces security policies:

* Forbidden flags (e.g., `-sN`, `--script exploit`)
* Unsafe targets (e.g., `192.168.0.0/16`)

---


### Component Interaction Map

```
┌──────────────────────────────────────────────────────────────────┐
│                     VALIDATION LAYER                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT: CommandCandidate (from M3)                               │
│    ↓                                                              │
│  ┌──────────────────────────────────────────┐                   │
│  │ VALIDATION AGENT (M4)                    │                   │
│  ├──────────────────────────────────────────┤                   │
│  │                                          │                   │
│  │  1. Syntax Validation                    │                   │
│  │     └─ validation_v2.py                  │                   │
│  │                                          │                   │
│  │  2. Security Policy Enforcement          │                   │
│  │     └─ security_rules.py                 │                   │
│  │        • Forbidden flags detector        │                   │
│  │        • Unsafe target identifier        │                   │
│  │        • Risk scorer                     │                   │
│  │                                          │                   │
│  │  3. Docker Sandbox Execution             │                   │
│  │     └─ execution_simulator.py            │                   │
│  │        • Execute in isolated container   │                   │
│  │        • Capture output/errors           │                   │
│  │        • Parse execution results         │                   │
│  │                                          │                   │
│  │  OUTPUT: ValidationResult                │                   │
│  │    {status: "Valid/Repairable/Invalid",  │                   │
│  │     risk_level: "low/medium/high",       │                   │
│  │     issues: [...]}                       │                   │
│  │                                          │                   │
│  └──────────────────────────────────────────┘                   │
│                    ↓                                              │
│       ┌────────────┴─────────────┐                              │
│       │                          │                              │
│    VALID              REPAIRABLE/INVALID                        │
│       │                          │                              │
│       ▼                          ▼                              │
│  ┌─────────┐          ┌──────────────────────┐                │
│  │ Execute │          │ SELF-CORRECTION (M5) │                │
│  └─────────┘          ├──────────────────────┤                │
│                       │                      │                │
│                       │ 5A: Autonomous Repair                │
│                       │  (if Repairable)     │                │
│                       │                      │                │
│                       │ • Known fix mapping  │                │
│                       │ • Pattern matching   │                │
│                       │ • Test repair       │                │
│                       │                      │                │
│                       │ Success?            │                │
│                       │  YES ─→ Return      │                │
│                       │  NO ─→ Iterative    │                │
│                       │                      │                │
│                       │ 5B: Iterative Loop   │                │
│                       │ (if Auto fails)      │                │
│                       │                      │                │
│                       │ • Error analysis     │                │
│                       │ • Generic fixes      │                │
│                       │ • Retry up to 3x     │                │
│                       │                      │                │
│                       │ Success?            │                │
│                       │  YES ─→ Return      │                │
│                       │  NO ─→ Feedback     │                │
│                       │        to M3        │                │
│                       └──────────────────────┘                │
│                                                                  │
│  OUTPUT: RepairResponse                                        │
│    {success: bool,                                             │
│     source_agent: "SELF-CORR-AUTO/ITER/FAILED",              │
│     repaired_command: str,                                    │
│     feedback_for_m3: {...}}                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Delivered Artifacts

### Core Files

* **Validation Agent**: `validation/validation_v2.py`
* **Self-Correction Agent**: `self_correction_agent.py`
* **Security Rules**: `validation/security_rules.py`
* **Docker Sandbox**: `docker/Dockerfile`

### API Integration

* **Endpoints**: `/validate`, `/repair`, `/repair/session/{id}`

---

## Performance Metrics

* **Validation Time**: 150-200ms (Target: <200ms)
* **Autonomous Repair**: 100-150ms (Target: <200ms)
* **Success Rate**: 90%+ for autonomous repair

---

## Installation & Deployment

### Prerequisites

```bash
pip install fastapi uvicorn pydantic docker
```

### Setup

```bash
git clone https://github.com/yourusername/NMAP-AI-Security-Validation.git
cd NMAP-AI-Security-Validation
pip install -r requirements.txt
```

### Start API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8004
```

---

## Usage Examples

### Example 1: Simple Validation

```bash
curl -X POST "http://127.0.0.1:8000/validate" -d '{"command": "nmap -sV scanme.nmap.org"}'
```

### Example 2: Permission Error Detection & Repair

```bash
curl -X POST "http://127.0.0.1:8000/validate" -d '{"command": "nmap -sS -p 80 target.com"}'
curl -X POST "http://127.0.0.1:8000/repair" -d '{"command": "nmap -sS -p 80 target.com", "validation_status": "Repairable"}'
```

---

## Key Achievements

* **100% Security Enforcement**: No forbidden flags bypassed.
* **98%+ Reliability**: Low false positive and negative rates.
* **Performance**: 40-50% reduction in M3 invocations.

---

## Future Improvements

### Phase 2: Advanced Features

* ML-based repair strategies
* Performance optimizations

### Phase 3: Enterprise Features

* Multi-user support
* Custom repair rules
* Analytics dashboard

# Nmap IA- Frontend avec React et vite


## 📁 Project Structure

```
nmap-command-generator-frontend/
├── public/
│   └── terminal-icon.svg
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── QueryInput.jsx
│   │   ├── ErrorDisplay.jsx
│   │   ├── ResultTabs.jsx
│   │   ├── ResultTab.jsx
│   │   ├── ValidationTab.jsx
│   │   ├── DetailsTab.jsx
│   │   └── ArchitectureCards.jsx
│   ├── services/
│   │   └── api.js
│   ├── utils/
│   │   └── helpers.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd nmap-command-generator-frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure API endpoint**

Edit `src/services/api.js` and update the API_BASE_URL:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

4. **Start development server**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🔌 Backend Integration

### Backend API Schema

Your FastAPI backend expects this request format:

**Endpoint:** `POST /api/v1/command/generate`

**Request Body:**
```json
{
  "text": "Scan all ports on 192.168.1.1",
  "context": {
    "timestamp": "2025-01-04T12:00:00Z",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response Format (FinalDecision):**
```json
{
  "command": "nmap -p- 192.168.1.1",
  "confidence": 0.95,
  "flags_explanation": {
    "-p-": "Scan all 65535 ports",
    "192.168.1.1": "Target IP address"
  }
}
```

### CORS Configuration (Backend)

Make sure your FastAPI backend has CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Proxy Configuration (Frontend)

The `vite.config.js` already includes a proxy for local development:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 🧪 Testing the Connection

### Method 1: Browser Console

```javascript
// Test the API connection
fetch('http://localhost:8000/api/v1/command/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Scan port 80 on 192.168.1.1',
    context: {}
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

### Method 2: cURL

```bash
curl -X POST http://localhost:8000/api/v1/command/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Scan port 80 on 192.168.1.1",
    "context": {}
  }'
```

### Method 3: Using the Test Script

```javascript
import { runAllTests } from './api.test.js';
runAllTests();
```

## 🐛 Troubleshooting

### Error: 422 Unprocessable Entity

**Cause:** The request body doesn't match the backend schema.

**Solution:** Check that you're sending:
```json
{
  "text": "your query here",
  "context": {}
}
```

NOT:
```json
{
  "query": "your query here"  // ❌ Wrong field name
}
```

### Error: CORS Policy

**Cause:** Backend not configured for CORS.

**Solution:** Add CORS middleware to your FastAPI app (see Backend Integration section).

### Error: Connection Refused

**Cause:** Backend not running or wrong URL.

**Solution:** 
1. Start your FastAPI backend: `uvicorn main:app --reload`
2. Verify URL in `src/services/api.js`
3. Check backend is running: `curl http://localhost:8000/health`

### Error: Network Error

**Cause:** Backend URL incorrect or firewall blocking.

**Solution:**
1. Verify backend URL: `const API_BASE_URL = 'http://localhost:8000/api/v1';`
2. Check if backend is accessible: Open `http://localhost:8000/docs` in browser

## 🎨 Customization

### Colors & Theme

Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      purple: {
        // Your custom colors
      },
    },
  },
}
```

### API Response Transformation

The frontend automatically transforms the backend response. To modify this, edit the `transformBackendResponse` function in `src/services/api.js`:

```javascript
const transformBackendResponse = (backendData) => {
  // Your custom transformation logic
  return {
    query: { ... },
    candidate: { ... },
    result: { ... }
  };
};
```

## 📦 Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

## 🚢 Deployment

### With Docker (Frontend + Backend)

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
```

### Environment Variables

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000
```

Update `api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

## 📚 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **Fetch API** - HTTP requests

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/command/generate` | POST | Generate Nmap command |





