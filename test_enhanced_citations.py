#!/usr/bin/env python3
"""Test script to verify enhanced citation system with politics/conflict domains"""

import json
from app import app

def test_enhanced_citations():
    """Test enhanced citations for different domains"""
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test politics/conflict domain for multiple sources
        test_cases = [
            {
                'name': 'BBC Politics Test',
                'urls': ['https://www.bbc.co.uk/news/articles/cy98jqr4p0xo'],
                'expected_citations': 1  # Should have citations
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"TESTING: {test_case['name']}")
            print(f"URL: {test_case['urls'][0]}")
            print(f"{'='*60}")
            
            test_data = {
                'urls': test_case['urls'],
                'max_sentences': 10,
                'analysis_mode': 'individual'
            }
            
            response = client.post('/analyze_multiple', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                
                print(f"✅ Domain: {data.get('domain', 'Unknown')}")
                print(f"✅ Specialists: {data.get('specialists', [])}")
                
                if 'facts' in data and data['facts']:
                    print(f"✅ Found {len(data['facts'])} facts with citations:")
                    
                    for i, fact in enumerate(data['facts'], 1):
                        print(f"\n   📋 FACT {i}:")
                        print(f"      Text: {fact['sentence'][:100]}...")
                        
                        # Check multiple citations
                        if 'citations' in fact and fact['citations']:
                            print(f"      🔗 {len(fact['citations'])} VERIFIED SOURCES:")
                            for j, citation in enumerate(fact['citations'], 1):
                                if citation and citation.get('title') and citation.get('url'):
                                    print(f"         {j}. {citation['title']}")
                                    print(f"            URL: {citation['url']}")
                        
                        # Check primary citation
                        elif 'citation' in fact and fact['citation']:
                            citation = fact['citation']
                            print(f"      🔗 PRIMARY SOURCE:")
                            print(f"         Title: {citation.get('title', 'N/A')}")
                            print(f"         URL: {citation.get('url', 'N/A')}")
                        else:
                            print(f"      ❌ NO CITATIONS FOUND!")
                            
                else:
                    print("❌ No facts found!")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.data}")
            
            print(f"{'='*60}")

if __name__ == "__main__":
    test_enhanced_citations()
