#!/usr/bin/env python3
"""Test script to verify citation verification system"""

import json
from app import app

def test_citation_verification():
    """Test that citations are verified before being included with facts"""
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        print("🧪 TESTING CITATION VERIFICATION SYSTEM")
        print("=" * 60)
        
        # Test with a URL that should have facts with verified citations
        test_data = {
            'urls': ['https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/'],
            'max_sentences': 10,
            'analysis_mode': 'individual'
        }
        
        print(f"🔍 Testing URL: {test_data['urls'][0]}")
        print("📋 Looking for citation verification in the process...")
        
        response = client.post('/analyze_multiple', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            
            print(f"\n✅ Analysis completed successfully")
            print(f"📊 Domain: {data.get('domain', 'Unknown')}")
            print(f"🎯 Specialists: {data.get('specialists', [])}")
            
            if 'facts' in data and data['facts']:
                print(f"\n📚 FACTS ANALYSIS:")
                print(f"   Found {len(data['facts'])} facts")
                
                for i, fact in enumerate(data['facts'], 1):
                    print(f"\n   📋 FACT {i}:")
                    print(f"      Text: {fact['sentence'][:100]}...")
                    
                    # Check for verified citations
                    if 'citations' in fact and fact['citations']:
                        print(f"      ✅ VERIFIED CITATIONS ({len(fact['citations'])}):")
                        for j, citation in enumerate(fact['citations'], 1):
                            if citation and citation.get('title') and citation.get('url'):
                                print(f"         {j}. {citation['title']}")
                                print(f"            🔗 {citation['url']}")
                            else:
                                print(f"         {j}. ❌ Invalid citation structure")
                    
                    elif 'citation' in fact and fact['citation']:
                        citation = fact['citation']
                        print(f"      ✅ VERIFIED PRIMARY CITATION:")
                        print(f"         Title: {citation.get('title', 'N/A')}")
                        print(f"         🔗 URL: {citation.get('url', 'N/A')}")
                    
                    else:
                        print(f"      ❌ NO VERIFIED CITATIONS - This should not happen for facts!")
                        
            else:
                print("❌ No facts found in response!")
            
            # Check if any facts were downgraded due to lack of verified citations
            if 'results' in data and data['results']:
                for result in data['results']:
                    if 'analysis' in result:
                        analysis_text = result['analysis']
                        if 'MIXED' in analysis_text and 'No verified citations' in analysis_text:
                            print(f"⚠️  Found fact downgraded to MIXED due to unverified citations")
                            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.data}")
        
        print("=" * 60)

if __name__ == "__main__":
    test_citation_verification()
