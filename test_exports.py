#!/usr/bin/env python3
"""
Test script to verify export functionality
"""

import requests
import json

def test_export_endpoint(export_type):
    """Test a specific export endpoint"""
    url = "http://127.0.0.1:5000/api/export_study_data"
    headers = {"Content-Type": "application/json"}
    data = {"export_type": export_type}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\n=== Testing {export_type} export ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {export_type} export successful!")
                if 'files' in result:
                    print(f"Files created: {list(result['files'].keys())}")
            else:
                print(f"❌ {export_type} export failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server. Make sure Flask is running on port 5000")
    except Exception as e:
        print(f"❌ Error testing {export_type}: {e}")

def test_get_study_data():
    """Test the get study data endpoint"""
    url = "http://127.0.0.1:5000/api/get_study_data"
    
    try:
        response = requests.get(url)
        print(f"\n=== Testing get_study_data ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Study data retrieved successfully!")
            print(f"Participants: {len(result.get('participants', []))}")
            print(f"Statistics: {result.get('statistics', {})}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server. Make sure Flask is running on port 5000")
    except Exception as e:
        print(f"❌ Error testing get_study_data: {e}")

if __name__ == "__main__":
    print("Testing Export Functionality")
    print("=" * 50)
    
    # Test get study data first
    test_get_study_data()
    
    # Test all export types
    export_types = [
        'pre_questionnaires',
        'post_questionnaires', 
        'post_questionnaire2',
        'exit_questionnaires',
        'sessions',
        'interactions',
        'all'
    ]
    
    for export_type in export_types:
        test_export_endpoint(export_type)
    
    print("\n" + "=" * 50)
    print("Export testing completed!")