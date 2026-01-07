#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST MEDIUM AGENT
Test simple du Medium Agent
"""

import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.medium_agent_final import MediumAgent


def test_medium_agent():
    """Test du Medium Agent"""
    print("=" * 70)
    print("🧪 TEST MEDIUM AGENT (T5-small + LoRA)")
    print("=" * 70)
    
    # Initialiser l'agent
    try:
        agent = MediumAgent()
    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        print("\n💡 Solution: Vérifiez que le modèle t5_nmap_final existe")
        return
    
    # Tests
    test_queries = [
        "Scan all ports on 192.168.1.1",
        "Check if port 80 is open on example.com",
        "Detect operating system on 10.0.0.1",
        "Perform SYN scan with version detection on target.com",
        "Scan TCP ports 20 to 100 on 192.168.1.100"
    ]
    
    print("\n" + "=" * 70)
    print("📝 TESTS")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query:")
        print(f"    {query}")
        
        try:
            # Générer la commande
            command = agent.generate_nmap_command(query)
            print(f"    ✅ Nmap: {command}")
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Tests terminés!")
    print("=" * 70)


def test_with_orchestrator_format():
    """Test avec le format orchestrator (process)"""
    print("\n" + "=" * 70)
    print("🧪 TEST FORMAT ORCHESTRATOR")
    print("=" * 70)
    
    try:
        agent = MediumAgent()
    except FileNotFoundError as e:
        print(f"\n❌ Erreur: {e}")
        return
    
    # Simuler le format du classifier
    classification = {
        'original_query': 'Scan ports 80,443 with SYN on 192.168.1.1',
        'score': 28,
        'reasoning': 'Standard complexity',
        'complexity_level': 'medium'
    }
    
    print("\n📥 Input (classification):")
    print(f"    Query: {classification['original_query']}")
    print(f"    Score: {classification['score']}")
    
    # Appeler process
    result = agent.process(classification)
    
    print("\n📤 Output (agent result):")
    print(f"    Agent: {result.get('agent')}")
    print(f"    Command: {result.get('nmap_command')}")
    print(f"    Model: {result.get('model')}")
    
    print("\n✅ Test orchestrator OK!")


if __name__ == "__main__":
    # Test 1: Génération simple
    test_medium_agent()
    
    # Test 2: Format orchestrator
    test_with_orchestrator_format()