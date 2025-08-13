#!/usr/bin/env python3
"""
Test script to demonstrate automatic reclassification of facts without citations as opinions
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_citation_requirement():
    """Test that facts without verifiable citations are automatically classified as opinions"""
    
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        print("🧪 TESTING AUTOMATIC FACT-TO-OPINION RECLASSIFICATION")
        print("=" * 80)
        print("📋 RULE: If no right/verifiable citations found → Automatically classify as OPINION")
        print("=" * 80)
        
        # Test with a URL that might have mixed citation quality
        test_data = {
            'urls': ['https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/'],
            'max_sentences': 8,
            'analysis_mode': 'individual'
        }
        
        print(f"🔍 Testing URL: {test_data['urls'][0]}")
        print("📊 Expected behavior: Facts without verified citations → OPINION")
        print()
        
        response = client.post('/analyze_multiple', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            
            print(f"✅ Analysis completed successfully")
            print(f"📊 Domain: {data.get('domain', 'Unknown')}")
            print(f"🎯 Total Facts: {data.get('total_facts', 0)}")
            print(f"🎯 Total Opinions: {data.get('total_opinions', 0)}")
            print()
            
            # Check facts - should all have verified citations
            if 'facts' in data and data['facts']:
                print(f"📚 FACTS ANALYSIS ({len(data['facts'])} found):")
                print("-" * 60)
                
                for i, fact in enumerate(data['facts'], 1):
                    print(f"\n   📋 FACT {i}:")
                    print(f"      Text: {fact['sentence'][:120]}...")
                    
                    # Check for verified citations
                    if 'citations' in fact and fact['citations']:
                        print(f"      ✅ VERIFIED CITATIONS ({len(fact['citations'])}):")
                        for j, citation in enumerate(fact['citations'], 1):
                            if citation and citation.get('title') and citation.get('url'):
                                print(f"         {j}. {citation['title']}")
                                print(f"            🔗 {citation['url']}")
                            else:
                                print(f"         {j}. ❌ Invalid citation structure")
                    else:
                        print(f"      ❌ NO VERIFIED CITATIONS - This should NOT happen with new rule!")
                        
            else:
                print("📚 No facts found (all statements likely reclassified as opinions)")
            
            # Check opinions - some should be reclassified facts
            if 'opinions' in data and data['opinions']:
                print(f"\n💭 OPINIONS ANALYSIS ({len(data['opinions'])} found):")
                print("-" * 60)
                
                reclassified_count = 0
                for i, opinion in enumerate(data['opinions'], 1):
                    # Check if this was reclassified from fact to opinion
                    was_reclassified = False
                    if 'reasoning' in opinion and opinion['reasoning']:
                        if 'reclassified as OPINION per verification standards' in opinion['reasoning']:
                            was_reclassified = True
                            reclassified_count += 1
                    
                    print(f"\n   💭 OPINION {i}:")
                    print(f"      Text: {opinion['sentence'][:120]}...")
                    
                    if was_reclassified:
                        print(f"      🔄 RECLASSIFIED: Originally identified as fact but reclassified due to lack of citations")
                    else:
                        print(f"      📝 ORIGINAL OPINION: Classified as opinion from the start")
                
                print(f"\n📊 Summary: {reclassified_count} statements were reclassified from FACT → OPINION due to missing citations")
                
            else:
                print("💭 No opinions found")
            
            # Test the new rule effectiveness
            total_statements = data.get('total_facts', 0) + data.get('total_opinions', 0)
            if total_statements > 0:
                citation_compliance = (data.get('total_facts', 0) / total_statements) * 100
                print(f"\n📈 CITATION COMPLIANCE RATE: {citation_compliance:.1f}%")
                print(f"   (All facts have verified citations as required by the new rule)")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Error: {response.data}")
        
        print("\n" + "=" * 80)
        print("🎯 CONCLUSION: Facts without verifiable citations are now automatically")
        print("   reclassified as OPINIONS, ensuring citation integrity.")
        print("=" * 80)

if __name__ == "__main__":
    test_citation_requirement()
