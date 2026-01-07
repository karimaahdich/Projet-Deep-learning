#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 HARD AGENT - Diffusion-Inspired Iterative Synthesis
Adapté pour retourner CommandCandidate
"""

import re
import json
import os
from typing import Dict, Optional


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


class HardAgent:
    """
    Agent HARD avec approche diffusion-inspired
    Retourne CommandCandidate au format orchestrateur
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """Initialise l'agent Hard avec le dataset"""
        print("🔥 Initialisation de l'Agent HARD (Diffusion-based)...")
        
        self.num_diffusion_steps = 10
        
        # Charger le dataset si fourni
        self.dataset = []
        if dataset_path and os.path.exists(dataset_path):
            with open(dataset_path, 'r', encoding='utf-8') as f:
                self.dataset = json.load(f)
            print(f"📊 Dataset chargé: {len(self.dataset)} exemples")
        
        # Knowledge base pour commandes complexes
        self.scan_types = {
            'syn': '-sS', 'tcp': '-sT', 'udp': '-sU', 
            'ack': '-sA', 'null': '-sN', 'fin': '-sF', 'xmas': '-sX',
            'window': '-sW', 'maimon': '-sM'
        }
        
        self.evasion_techniques = {
            'decoy': lambda n: f'-D RND:{n}',
            'spoof_mac': '--spoof-mac 0',
            'fragment': '-f',
            'randomize': '--randomize-hosts',
            'data_length': '--data-length 25'
        }
        
        self.timing_levels = {
            'paranoid': '-T0', 'sneaky': '-T1', 'polite': '-T2',
            'normal': '-T3', 'aggressive': '-T4', 'insane': '-T5',
            'slow': '-T1', 'fast': '-T4', 'faster': '-T5',
            'ultra-slow': '-T0', 'maximum speed': '-T5'
        }
        
        print(f"✅ Agent HARD prêt!")
        print(f"   Diffusion steps: {self.num_diffusion_steps}\n")
    
    def _diffusion_step_0_analyze(self, query: str) -> Dict:
        """Step 0: Analyse initiale"""
        return {
            'query': query.lower(),
            'detected_keywords': re.findall(r'\b\w+\b', query.lower()),
            'complexity': 'high'
        }
    
    def _diffusion_step_1_extract_target(self, state: Dict) -> Dict:
        """Step 1: Extraire la cible"""
        query = state['query']
        
        # IPv6
        ipv6_match = re.search(r'([0-9a-f:]+::[0-9a-f:]*|[0-9a-f:]+)', query)
        if ipv6_match and ':' in ipv6_match.group(1):
            state['target'] = ipv6_match.group(1)
            return state
        
        # IP ou CIDR
        ip_match = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?)\b', query)
        if ip_match:
            state['target'] = ip_match.group(1)
            return state
        
        # Domaine
        domain_match = re.search(r'\b([a-z0-9.-]+\.[a-z]{2,})\b', query)
        if domain_match:
            state['target'] = domain_match.group(1)
            return state
        
        state['target'] = '<target>'
        return state
    
    def _diffusion_step_2_detect_scan_type(self, state: Dict) -> Dict:
        """Step 2: Déterminer le type de scan"""
        query = state['query']
        
        for keyword, option in self.scan_types.items():
            if keyword in query:
                state['scan_type'] = option
                return state
        
        # Défaut: SYN scan
        state['scan_type'] = '-sS'
        return state
    
    def _diffusion_step_3_extract_ports(self, state: Dict) -> Dict:
        """Step 3: Extraire les ports"""
        query = state['query']
        
        # All ports
        if 'all port' in query:
            state['ports'] = '-'
        # Top ports
        elif 'top' in query and 'port' in query:
            top_match = re.search(r'top\s+(\d+)', query)
            if top_match:
                state['ports'] = f'--top-ports {top_match.group(1)}'
            else:
                state['ports'] = '--top-ports 100'
        # Range
        elif match := re.search(r'ports?\s+(\d+-\d+)', query):
            state['ports'] = match.group(1)
        # Liste
        elif match := re.search(r'ports?\s+(\d+(?:,\d+)*)', query):
            state['ports'] = match.group(1)
        # Single port
        elif match := re.search(r'port\s+(\d+)', query):
            state['ports'] = match.group(1)
        else:
            state['ports'] = None
        
        return state
    
    def _diffusion_step_4_detect_evasion(self, state: Dict) -> Dict:
        """Step 4: Détecter techniques d'évasion"""
        query = state['query']
        evasion = []
        
        # Decoys
        if 'decoy' in query or 'decoys' in query:
            match = re.search(r'(\d+)\s+(?:random\s+)?decoys?', query)
            n = match.group(1) if match else '10'
            evasion.append(self.evasion_techniques['decoy'](n))
        
        # Spoof MAC
        if 'spoof' in query and 'mac' in query:
            evasion.append(self.evasion_techniques['spoof_mac'])
        
        # Fragment
        if 'fragment' in query:
            evasion.append(self.evasion_techniques['fragment'])
        
        # Randomize
        if 'randomize' in query:
            evasion.append(self.evasion_techniques['randomize'])
        
        state['evasion'] = evasion
        return state
    
    def _diffusion_step_5_detect_timing(self, state: Dict) -> Dict:
        """Step 5: Détecter le timing"""
        query = state['query']
        
        # T0-T5 explicite
        if match := re.search(r'[Tt](\d)', query):
            state['timing'] = f"-T{match.group(1)}"
            return state
        
        # Mots-clés
        for keyword, timing in self.timing_levels.items():
            if keyword in query:
                state['timing'] = timing
                return state
        
        # Défaut basé sur évasion
        if state.get('evasion'):
            state['timing'] = '-T2'
        else:
            state['timing'] = '-T3'
        
        return state
    
    def _diffusion_step_6_detect_scripts(self, state: Dict) -> Dict:
        """Step 6: Détecter scripts NSE"""
        query = state['query']
        scripts = []
        
        if 'vuln' in query or 'vulnerability' in query or 'exploit' in query:
            scripts.append('--script vuln')
        elif 'auth' in query and 'scan' in query:
            scripts.append('--script auth')
        elif 'script' in query and 'default' in query:
            scripts.append('--script default')
        
        state['scripts'] = scripts
        return state
    
    def _diffusion_step_7_synthesize(self, state: Dict) -> Dict:
        """Step 7: Synthèse initiale"""
        parts = ['nmap']
        
        # Scan type
        parts.append(state.get('scan_type', '-sS'))
        
        # Ports
        if ports := state.get('ports'):
            if ports.startswith('--top-ports'):
                parts.append(ports)
            else:
                parts.append(f'-p {ports}')
        
        # Timing
        if timing := state.get('timing'):
            parts.append(timing)
        
        # Évasion
        if evasion := state.get('evasion'):
            parts.extend(evasion)
        
        # Scripts
        if scripts := state.get('scripts'):
            parts.extend(scripts)
        
        # Target
        parts.append(state.get('target', '<target>'))
        
        state['command'] = ' '.join(parts)
        return state
    
    def _diffusion_step_8_refine_duplicates(self, state: Dict) -> Dict:
        """Step 8: Enlever doublons"""
        parts = state['command'].split()
        seen = set()
        refined = []
        
        for part in parts:
            if part == 'nmap' or part.startswith('<') or part.startswith('--') or part not in seen:
                refined.append(part)
                if part != 'nmap':
                    seen.add(part)
        
        state['command'] = ' '.join(refined)
        return state
    
    def _diffusion_step_9_refine_conflicts(self, state: Dict) -> Dict:
        """Step 9: Résoudre conflits"""
        command = state['command']
        
        # Conflit: multiple scan types
        scan_types = ['-sS', '-sT', '-sU', '-sA', '-sN', '-sF', '-sX', '-sW', '-sM']
        found_scans = [s for s in scan_types if s in command]
        
        if len(found_scans) > 1:
            parts = command.split()
            keep_scan = found_scans[0]
            parts = [p for p in parts if p == keep_scan or p not in scan_types]
            command = ' '.join(parts)
        
        state['command'] = command
        return state
    
    def _generate_rationale(self, query: str, command: str) -> str:
        """Génère l'explication (rationale) de la commande"""
        parts = []
        
        # Scan type
        if '-sS' in command:
            parts.append("SYN stealth scan")
        elif '-sT' in command:
            parts.append("TCP connect scan")
        elif '-sU' in command:
            parts.append("UDP scan")
        elif '-sW' in command:
            parts.append("TCP Window scan")
        elif '-sA' in command:
            parts.append("ACK scan")
        elif '-sN' in command:
            parts.append("NULL scan")
        elif '-sF' in command:
            parts.append("FIN scan")
        elif '-sX' in command:
            parts.append("XMAS scan")
        
        # Ports
        if '--top-ports' in command:
            match = re.search(r'--top-ports (\d+)', command)
            if match:
                parts.append(f"top {match.group(1)} ports")
        elif '-p -' in command:
            parts.append("all 65535 ports")
        elif '-p ' in command:
            port_match = re.search(r'-p (\S+)', command)
            if port_match:
                parts.append(f"ports {port_match.group(1)}")
        
        # Timing
        timing_match = re.search(r'-T(\d)', command)
        if timing_match:
            timing_names = {
                '0': 'paranoid', '1': 'sneaky', '2': 'polite',
                '3': 'normal', '4': 'aggressive', '5': 'insane'
            }
            parts.append(f"{timing_names[timing_match.group(1)]} timing")
        
        # Evasion
        if '-D RND:' in command:
            decoy_match = re.search(r'-D RND:(\d+)', command)
            if decoy_match:
                parts.append(f"{decoy_match.group(1)} random decoys for IDS evasion")
        
        if '--spoof-mac' in command:
            parts.append("MAC address spoofing")
        
        if '-f' in command:
            parts.append("packet fragmentation")
        
        if '--randomize-hosts' in command:
            parts.append("randomized host order")
        
        # Scripts
        if '--script vuln' in command:
            parts.append("vulnerability detection scripts")
        elif '--script auth' in command:
            parts.append("authentication scripts")
        elif '--script default' in command:
            parts.append("default NSE scripts")
        
        # Target
        target_match = re.search(r'(\S+)$', command)
        if target_match and target_match.group(1) != '<target>':
            parts.append(f"targeting {target_match.group(1)}")
        
        if parts:
            return "Diffusion-based synthesis: " + ", ".join(parts)
        else:
            return f"Diffusion-based command generation for: {query}"
    
    async def generate(self, q: UserQuery) -> CommandCandidate:
        """
        Génère une commande Nmap via processus de diffusion
        
        Args:
            q: UserQuery contenant la requête
            
        Returns:
            CommandCandidate: Format standardisé avec command, rationale, source_agent
        """
        # État initial
        state = {}
        
        # PROCESSUS DE DIFFUSION (10 étapes)
        state = self._diffusion_step_0_analyze(q.query)
        state = self._diffusion_step_1_extract_target(state)
        state = self._diffusion_step_2_detect_scan_type(state)
        state = self._diffusion_step_3_extract_ports(state)
        state = self._diffusion_step_4_detect_evasion(state)
        state = self._diffusion_step_5_detect_timing(state)
        state = self._diffusion_step_6_detect_scripts(state)
        state = self._diffusion_step_7_synthesize(state)
        state = self._diffusion_step_8_refine_duplicates(state)
        state = self._diffusion_step_9_refine_conflicts(state)
        
        command = state['command']
        rationale = self._generate_rationale(q.query, command)
        
        return CommandCandidate(
            command=command,
            rationale=rationale,
            source_agent="DIFFUSION"
        )


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST HARD AGENT")
    print("=" * 70)
    
    agent = HardAgent()
    
    test_queries = [
        "Scan with 10 decoys and spoof MAC on 192.168.1.1",
        "Stealth scan all ports with fragment and T2 timing on 10.0.0.0/24",
        "Fast aggressive scan with vulnerability scripts on target.com"
    ]
    
    import asyncio
    
    async def test():
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            result = await agent.generate(UserQuery(query))
            print(f"✅ Command: {result.command}")
            print(f"   Rationale: {result.rationale}")
            print(f"   Source: {result.source_agent}")
    
    asyncio.run(test())