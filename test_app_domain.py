#!/usr/bin/env python3
"""Test script to verify app.py returns domain information correctly"""

import json
import requests
import time

def test_domain_response():
    """Test that the Flask app returns domain information"""
    
    # Start the app in a separate thread for testing
    import threading
    from app import app
    
    # Run app in test mode
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test with a known URL that should be classified as LIFESTYLE
        test_data = {
            'urls': ['https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/'],
            'max_sentences': 10,
            'analysis_mode': 'individual'
        }
        
        print("Testing domain response...")
        print(f"Request data: {test_data}")
        
        response = client.post('/analyze_multiple', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'domain' in data:
                print(f"Domain detected: {data['domain']}")
            else:
                print("NO DOMAIN FIELD in response!")
                
            if 'specialists' in data:
                print(f"Specialists: {data['specialists']}")
            else:
                print("NO SPECIALISTS FIELD in response!")
                
            # Print full response for debugging
            print(f"Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.data}")

if __name__ == "__main__":
    test_domain_response()
