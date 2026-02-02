#!/usr/bin/env python3
"""
Test the SMS classification API endpoint
Run this in a separate terminal while backend is running
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_classify_text():
    """Test the /classify/text endpoint"""
    
    test_cases = [
        {
            "text": "Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121.",
            "expected": "SPAM",
            "label": "Spam SMS"
        },
        {
            "text": "Hello how are you doing today?",
            "expected": "HAM",
            "label": "Normal SMS"
        },
        {
            "text": "Congratulations! You have won a free iPhone. Click here to claim!",
            "expected": "SPAM",
            "label": "Spam Claim"
        },
    ]
    
    print("=" * 80)
    print("TESTING SMS CLASSIFICATION API")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['label']}")
        print(f"Text: {test['text'][:60]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/classify/text",
                json={"text": test["text"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: 200 OK")
                print(f"  Classification: {data.get('classification')}")
                print(f"  Confidence: {data.get('confidence'):.2%}")
                print(f"  Agent votes:")
                for agent, vote in data.get('agent_votes', {}).items():
                    pred = vote.get('prediction')
                    conf = vote.get('confidence')
                    print(f"    - {agent}: {pred} ({conf:.2%})")
            else:
                print(f"✗ Status: {response.status_code} {response.reason}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error - is backend running on {BASE_URL}?")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_classify_text()
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)
