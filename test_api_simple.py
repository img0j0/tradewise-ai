#!/usr/bin/env python3

import requests
import json

def test_api():
    try:
        # Test the stock search API
        response = requests.post('http://localhost:5000/api/stock-search', 
                               json={'query': 'AAPL'})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Working!")
            print(f"Symbol: {data.get('symbol', 'N/A')}")
            print(f"Name: {data.get('name', 'N/A')}")
            print(f"Price: ${data.get('price', 'N/A')}")
            print(f"Change: {data.get('change_percent', 'N/A')}%")
            print(f"Recommendation: {data.get('ai_recommendation', 'N/A')}")
            print(f"Confidence: {data.get('confidence', 'N/A')}%")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_api()