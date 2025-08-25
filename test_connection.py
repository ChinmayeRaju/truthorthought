#!/usr/bin/env python3
"""
Test connection to Flask server
"""

import requests
import json

def test_connection():
    """Test if Flask server is responding"""
    try:
        # Test basic health check
        response = requests.get("http://127.0.0.1:5000/api/get_study_data", timeout=5)
        print(f"✅ Flask server is responding!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        # Test export endpoint
        response = requests.post(
            "http://127.0.0.1:5000/api/export_study_data",
            headers={"Content-Type": "application/json"},
            json={"export_type": "pre_questionnaires"},
            timeout=10
        )
        print(f"\n✅ Export endpoint responding!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server on port 5000")
        print("Make sure Flask is running with: python app.py")
    except requests.exceptions.Timeout:
        print("❌ Request timed out - Flask server might be slow")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()