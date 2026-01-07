import asyncio
from agents.hard_agent_final import HardAgent, UserQuery  # ← Changé ici

async def test():
    print("🔥 Test Hard Agent...")
    
    agent = HardAgent(dataset_path="data/nmap_dataset_enriched.json")
    
    query = UserQuery("Scan all ports on 192.168.1.1")
    result = await agent.generate(query)
    
    print(f"\n✅ Query: {query.query}")
    print(f"   Command: {result.command}")
    print(f"   Rationale: {result.rationale}")
    print(f"   Source: {result.source_agent}")
    
    assert result.command.startswith("nmap"), "❌ ERREUR"
    assert result.source_agent == "DIFFUSION", "❌ ERREUR"
    print("\n✅ Hard Agent fonctionne!")

if __name__ == "__main__":
    asyncio.run(test())