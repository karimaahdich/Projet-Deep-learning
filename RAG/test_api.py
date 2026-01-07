import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test de l'endpoint health"""
    print("\n🔍 Test health endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health: {data['status']}")
        print(f"   Neo4j: {'✅' if data['neo4j_connected'] else '❌'}")
        print(f"   Uptime: {data['uptime_seconds']:.2f}s")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_generate_command():
    """Test de génération de commande"""
    print("\n🔍 Test génération de commande...")
    
    test_cases = [
        {
            "query": "scan UDP sur 192.168.1.1 avec scripts",
            "description": "Scan UDP avec scripts"
        },
        {
            "query": "scan SYN sur google.com",
            "description": "Scan SYN simple"
        },
        {
            "query": "scan avec détection de version et OS",
            "description": "Détection version + OS"
        },
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['description']}")
        print(f"   Query: '{test['query']}'")
        
        payload = {
            "query": test["query"],
            "complexity": "easy"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Command: {data['command']}")
            print(f"   🎯 Confidence: {data['confidence']:.2%}")
            print(f"   ⏱️  Time: {elapsed*1000:.2f}ms")
            
            if data["warnings"]:
                for warning in data["warnings"]:
                    print(f"   ⚠️  Warning: {warning}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")

def test_quick_test():
    """Test de l'endpoint quick-test"""
    print("\n🔍 Test quick-test endpoint...")
    
    query = "scan%20UDP%20sur%20192.168.1.1"
    response = requests.get(f"{BASE_URL}/api/v1/quick-test/{query}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query: {data['query']}")
        print(f"✅ Command: {data['result']['command']}")
        return True
    else:
        print(f"❌ Quick test failed: {response.status_code}")
        return False

def test_examples():
    """Test des exemples"""
    print("\n🔍 Test des exemples...")
    response = requests.get(f"{BASE_URL}/api/v1/test-examples")
    
    if response.status_code == 200:
        examples = response.json()
        print(f"✅ {len(examples)} examples loaded")
        
        for i, example in enumerate(examples, 1):
            print(f"\n   Example {i}:")
            print(f"     Command: {example['command']}")
            print(f"     Confidence: {example['confidence']:.2%}")
        
        return True
    else:
        print(f"❌ Examples failed: {response.status_code}")
        return False

def test_swagger():
    """Vérifie que Swagger est accessible"""
    print("\n🔍 Test Swagger UI...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200 and "swagger-ui" in response.text.lower():
            print(f"✅ Swagger UI accessible")
            print(f"   URL: {BASE_URL}/docs")
            return True
        else:
            print(f"❌ Swagger UI not accessible")
            return False
    except Exception as e:
        print(f"❌ Error accessing Swagger: {e}")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print("="*60)
    print("🧪 TEST COMPLET DE L'API NMAP-AI RAG")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Swagger UI", test_swagger),
        ("Generate Command", test_generate_command),
        ("Quick Test", test_quick_test),
        ("Examples", test_examples),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Running: {test_name}")
        print('='*40)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✨ TOUS LES TESTS ONT RÉUSSI!")
        print(f"📚 Swagger: {BASE_URL}/docs")
        print(f"🚀 API prête à être utilisée!")
    else:
        print(f"\n⚠️  Certains tests ont échoué")

if __name__ == "__main__":
    run_all_tests()