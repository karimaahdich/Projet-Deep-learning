#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 MEDIUM AGENT - T5-small + LoRA Fine-tuned
Adapté pour retourner CommandCandidate
"""

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel
import os
import re
from typing import Dict, Optional


# ============================================
# CLASSES POUR L'API
# ============================================

class CommandCandidate:
    """Format de sortie standardisé"""
    def __init__(self, command: str, rationale: str, source_agent: str):
        self.command = command
        self.rationale = rationale
        self.source_agent = source_agent
    
    def to_dict(self):
        return {
            "command": self.command,
            "rationale": self.rationale,
            "source_agent": self.source_agent
        }


class UserQuery:
    """Format d'entrée standardisé"""
    def __init__(self, query: str):
        self.query = query


# ============================================
# AGENT MEDIUM
# ============================================

class MediumAgent:
    """
    Agent Medium : T5-small fine-tuné avec LoRA
    Fine-tuné sur 1,637 paires NL→Nmap
    """
    
    def __init__(self, model_path: str = None, dataset_path: Optional[str] = None):
        """
        Initialise l'agent avec le modèle fine-tuné
        
        Args:
            model_path: Chemin vers le modèle LoRA (par défaut: models/t5_nmap_final)
            dataset_path: Chemin vers le dataset (optionnel)
        """
        # Chemin par défaut
        if model_path is None:
            # Chercher dans le dossier courant d'abord
            if os.path.exists("./models/t5_nmap_final"):
                model_path = "./models/t5_nmap_final"
            else:
                # Sinon, calculer depuis le fichier (remonter au parent)
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                model_path = os.path.join(base_dir, "models", "t5_nmap_final")
        
        print(f"🟡 Initialisation de l'Agent MEDIUM (T5-small + LoRA)...")
        print(f"📂 Chemin du modèle: {model_path}")
        
        # Dataset (optionnel)
        if dataset_path and os.path.exists(dataset_path):
            import json
            with open(dataset_path, 'r', encoding='utf-8') as f:
                self.dataset = json.load(f)
            print(f"📊 Dataset chargé: {len(self.dataset)} exemples")
        else:
            self.dataset = []
        
        # Vérifier que le modèle existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"❌ Modèle non trouvé dans: {model_path}\n"
                f"Veuillez placer t5_nmap_final dans models/"
            )
        
        # Charger tokenizer depuis t5-small
        print("   └─ Chargement du tokenizer...")
        self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
        
        # Charger le modèle de base T5-small
        print("   └─ Chargement du modèle de base...")
        base_model = T5ForConditionalGeneration.from_pretrained(
            "t5-small",
            torch_dtype=torch.float32
        )
        
        # Charger les adaptateurs LoRA
        print("   └─ Chargement des adaptateurs LoRA...")
        self.model = PeftModel.from_pretrained(base_model, model_path)
        
        # Device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Agent MEDIUM prêt sur {self.device.upper()}")
        
        # Stats
        trainable = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.model.parameters())
        print(f"📊 Paramètres: {trainable/1e6:.2f}M entraînables / {total/1e6:.2f}M total\n")
    
    def generate_nmap_command(
        self, 
        query: str,
        max_length: int = 128,
        num_beams: int = 4
    ) -> str:
        """
        Génère une commande Nmap à partir d'une requête NL
        
        Args:
            query: Requête en langage naturel
            max_length: Longueur max de génération
            num_beams: Nombre de beams (beam search)
            
        Returns:
            Commande Nmap générée
        """
        # Format d'entraînement : "translate NL to Nmap: {query}"
        input_text = f"translate NL to Nmap: {query}"
        
        # Tokenization
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Génération
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                do_sample=False  # Beam search déterministe
            )
        
        # Décodage
        command = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return command.strip()
    
    def _generate_rationale(self, query: str, command: str) -> str:
        """Génère l'explication (rationale) de la commande"""
        parts = []
        
        # Type de scan
        if '-sS' in command:
            parts.append("SYN scan")
        elif '-sT' in command:
            parts.append("TCP connect scan")
        elif '-sU' in command:
            parts.append("UDP scan")
        elif '-sV' in command:
            parts.append("version detection")
        elif '-sn' in command:
            parts.append("ping sweep")
        
        # Ports
        if '-p-' in command:
            parts.append("all 65535 ports")
        elif '-p ' in command:
            port_match = re.search(r'-p (\S+)', command)
            if port_match:
                parts.append(f"ports {port_match.group(1)}")
        
        # OS detection
        if '-O' in command:
            parts.append("OS detection")
        
        # Timing
        timing_match = re.search(r'-T(\d)', command)
        if timing_match:
            parts.append(f"T{timing_match.group(1)} timing")
        
        # Scripts
        if '--script' in command:
            script_match = re.search(r'--script (\S+)', command)
            if script_match:
                parts.append(f"{script_match.group(1)} scripts")
        
        # Cible
        target_match = re.search(r'([0-9a-zA-Z.-:/]+)$', command)
        if target_match:
            parts.append(f"target {target_match.group(1)}")
        
        if parts:
            return "T5-LoRA generation: " + ", ".join(parts)
        else:
            return f"T5-LoRA generated command for: {query}"
    
    async def generate(self, q: UserQuery) -> CommandCandidate:
        """
        Génère une commande Nmap via T5-LoRA (pour l'API)
        
        Args:
            q: UserQuery contenant la requête
            
        Returns:
            CommandCandidate: Format standardisé avec command, rationale, source_agent
        """
        # Générer la commande
        command = self.generate_nmap_command(q.query)
        
        # Générer l'explication
        rationale = self._generate_rationale(q.query, command)
        
        return CommandCandidate(
            command=command,
            rationale=rationale,
            source_agent="MEDIUM"
        )
    
    def process(self, classification_result: Dict) -> Dict:
        """
        Point d'entrée pour l'orchestrateur
        
        Args:
            classification_result: Résultat du classifier
            
        Returns:
            dict avec agent, model, query, nmap_command
        """
        query = classification_result.get('original_query', '')
        
        if not query:
            return {
                'error': 'No query provided',
                'agent': 'medium',
                'nmap_command': None
            }
        
        try:
            nmap_cmd = self.generate_nmap_command(query)
        except Exception as e:
            return {
                'error': str(e),
                'agent': 'medium',
                'nmap_command': None,
                'query': query
            }
        
        return {
            'agent': 'medium',
            'model': 'T5-small fine-tuned with LoRA',
            'query': query,
            'nmap_command': nmap_cmd,
            'complexity_score': classification_result.get('score', 0),
            'reasoning': classification_result.get('reasoning', '')
        }
    
    def __call__(self, query: str) -> str:
        """Permet d'utiliser l'agent comme une fonction"""
        return self.generate_nmap_command(query)


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST MEDIUM AGENT (T5-small + LoRA)")
    print("=" * 70)
    
    try:
        agent = MediumAgent()
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\n💡 Solution: Placez t5_nmap_final dans models/")
        exit(1)
    
    # Test simple
    test_queries = [
        "Scan all ports on 192.168.1.1",
        "Check if port 80 is open on example.com",
        "Detect operating system on 10.0.0.1"
    ]
    
    print("\n📝 TESTS SIMPLES:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] Query : {query}")
        result = agent(query)
        print(f"    Nmap  : {result}")
    
    # Test avec CommandCandidate (async)
    import asyncio
    
    async def test_async():
        print("\n📝 TEST API (CommandCandidate):")
        query = UserQuery("Scan port 443 on example.com")
        result = await agent.generate(query)
        print(f"\n✅ Command: {result.command}")
        print(f"   Rationale: {result.rationale}")
        print(f"   Source: {result.source_agent}")
    
    asyncio.run(test_async())
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés!")
    print("=" * 70 + "\n")