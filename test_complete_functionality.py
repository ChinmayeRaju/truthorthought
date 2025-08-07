#!/usr/bin/env python3
"""Test script to verify complete functionality including domain detection and fact citations"""

import json
import requests
import time

def test_complete_functionality():
    """Test that the Flask app returns domain information and fact citations"""
    
    # Start the app in a separate thread for testing
    import threading
    from app import app
    
    # Run app in test mode
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test with multiple URLs from different domains to test domain detection and citations
        test_cases = [
            {
                'name': 'LIFESTYLE Domain Test (KFC/Greggs)',
                'urls': ['https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/'],
                'expected_domain': 'LIFESTYLE'
            },
            {
                'name': 'BBC News Test',
                'urls': ['https://www.bbc.co.uk/news/articles/cy98jqr4p0xo'],
                'expected_domain': 'NEWS'  # Could be NEWS, POLITICS, etc.
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*50}")
            print(f"TESTING: {test_case['name']}")
            print(f"{'='*50}")
            
            test_data = {
                'urls': test_case['urls'],
                'max_sentences': 10,
                'analysis_mode': 'individual'
            }
            
            print(f"Request: {test_data['urls'][0]}")
            
            response = client.post('/analyze_multiple', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                
                # Test domain detection
                if 'domain' in data:
                    print(f"✅ Domain detected: {data['domain']}")
                    if test_case['expected_domain'] and data['domain'] == test_case['expected_domain']:
                        print(f"✅ Domain matches expected: {test_case['expected_domain']}")
                    else:
                        print(f"ℹ️  Domain differs from expected: got {data['domain']}, expected {test_case['expected_domain']}")
                else:
                    print("❌ NO DOMAIN FIELD in response!")
                
                # Test specialists
                if 'specialists' in data:
                    print(f"✅ Specialists: {data['specialists']}")
                else:
                    print("❌ NO SPECIALISTS FIELD in response!")
                
                # Test fact citations
                if 'facts' in data and len(data['facts']) > 0:
                    print(f"✅ Found {len(data['facts'])} facts")
                    for i, fact in enumerate(data['facts'], 1):
                        print(f"   Fact {i}: {fact['sentence'][:100]}...")
                        if 'citation' in fact and fact['citation']:
                            citation = fact['citation']
                            if citation.get('title') and citation.get('url'):
                                print(f"   ✅ Citation: {citation['title']} ({citation['url']})")
                            else:
                                print(f"   ⚠️  Incomplete citation: {citation}")
                        else:
                            print(f"   ❌ No citation for this fact!")
                else:
                    print("❌ No facts found in response!")
                
                # Test overall structure
                expected_keys = ['success', 'domain', 'specialists', 'facts', 'opinions', 'analysis_mode']
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    print(f"❌ Missing keys: {missing_keys}")
                else:
                    print("✅ All expected keys present in response")
                    
            else:
                print(f"❌ Error response: {response.data}")
            
            print(f"{'='*50}")

if __name__ == "__main__":
    test_complete_functionality()
