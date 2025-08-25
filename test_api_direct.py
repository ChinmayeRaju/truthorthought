#!/usr/bin/env python3
"""
Test API endpoints directly
"""

import requests
import json

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    # Test get_study_data first
    try:
        print("Testing /api/get_study_data...")
        response = requests.get(f"{base_url}/api/get_study_data", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ get_study_data failed: {e}")
    
    # Test each export type
    export_types = ['pre_questionnaires', 'post_questionnaires', 'post_questionnaire2', 'exit_questionnaires', 'sessions', 'all']
    
    for export_type in export_types:
        try:
            print(f"\nTesting export: {export_type}")
            response = requests.post(
                f"{base_url}/api/export_study_data",
                headers={"Content-Type": "application/json"},
                json={"export_type": export_type},
                timeout=10
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            if result.get('files'):
                print(f"Files: {list(result['files'].keys())}")
        except Exception as e:
            print(f"❌ {export_type} failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()