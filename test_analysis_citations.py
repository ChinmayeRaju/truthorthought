#!/usr/bin/env python3
"""
Test the full analysis pipeline to see citations
"""

import requests
import json

def test_analysis_with_citations():
    """Test the analysis endpoint to see if citations are included"""
    
    print("🔍 Testing Analysis Pipeline...")
    
    # Test data
    test_urls = ["https://www.bbc.co.uk/news/business-67896659"]
    
    try:
        # Make request to analyze_multiple endpoint
        response = requests.post('http://localhost:5000/analyze_multiple', 
                               json={
                                   'urls': test_urls,
                                   'analysis_mode': 'individual',
                                   'max_sentences': 5
                               })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis completed successfully")
            
            # Check for facts with citations
            if 'facts' in data and data['facts']:
                print(f"\n📊 Found {len(data['facts'])} facts:")
                
                for i, fact in enumerate(data['facts'], 1):
                    print(f"\n{i}. Fact: {fact.get('sentence', 'No sentence')[:100]}...")
                    
                    # Check for citations
                    citations = fact.get('citations', [])
                    if citations:
                        print(f"   ✅ Has {len(citations)} citations:")
                        for j, citation in enumerate(citations, 1):
                            print(f"      {j}. {citation.get('title', 'No title')}")
                            print(f"         URL: {citation.get('url', 'No URL')}")
                            print(f"         Score: {citation.get('verification_score', 'No score')}")
                    else:
                        print("   ❌ No citations found")
            else:
                print("❌ No facts found in response")
                
            # Print full response structure for debugging
            print(f"\n🔧 Response keys: {list(data.keys())}")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis_with_citations()
