"""Test registration endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    payload = {
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✓ Registration successful!")
            return True
        else:
            print(f"✗ Registration failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_agents():
    """Test agents endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/agents/list",
            timeout=10
        )
        
        print(f"\nAgents Status: {response.status_code}")
        if response.status_code == 200:
            agents = response.json()
            print(f"✓ Agents loaded: {len(agents) if isinstance(agents, list) else 'object'}")
            return True
        else:
            print(f"✗ Agents error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Sentinel-Net API...")
    print("-" * 50)
    
    test_agents()
    print("-" * 50)
    test_registration()
