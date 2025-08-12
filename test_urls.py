#!/usr/bin/env python3
"""
Test script to directly check URL processing
"""
import requests
import json

def test_multiple_urls():
    urls = [
        'https://www.theguardian.com/world/2025/aug/09/thousands-in-tel-aviv-protest-against-netanyahus-plan-to-escalate-gaza-war',
        'https://www.theguardian.com/world/2025/aug/10/netanyahu-defends-gaza-city-plan-as-un-warns-of-calamity-and-starvation',
        'https://www.theguardian.com/world/2025/aug/12/ukraine-war-briefing-russia-preparing-for-fresh-offensives-not-a-ceasefire-zelenskyy-says'
    ]
    
    print(f"Testing {len(urls)} URLs...")
    
    payload = {
        'urls': urls,
        'max_sentences': 15,
        'analysis_mode': 'individual',
        'participant_id': 'test_participant',
        'study_mode': 'research'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/analyze_multiple',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Response received.")
            print(f"Analysis mode: {data.get('analysis_mode', 'Unknown')}")
            print(f"URLs analyzed: {data.get('urls_analyzed', 'Unknown')}")
            
            # Check individual_results
            individual_results = data.get('individual_results', [])
            print(f"\nIndividual results count: {len(individual_results)}")
            
            for i, result in enumerate(individual_results):
                print(f"\nResult {i+1}:")
                print(f"  URL: {result.get('url', 'No URL')[:80]}...")
                print(f"  Title: {result.get('title', 'No Title')}")
                print(f"  Domain: {result.get('domain', 'No Domain')}")
                print(f"  Facts: {result.get('facts_count', 0)}")
                print(f"  Opinions: {result.get('opinions_count', 0)}")
                print(f"  Has URL: {bool(result.get('url'))}")
                print(f"  Has Title: {bool(result.get('title'))}")
                
                # Check content fields
                formatted_content = result.get('formatted_content', '')
                summary = result.get('summary', '')
                print(f"  Has formatted_content: {bool(formatted_content)}")
                print(f"  Has summary: {bool(summary)}")
                print(f"  Formatted content length: {len(formatted_content)}")
                print(f"  Summary length: {len(summary)}")
                
                # Show first 100 chars of content to check for duplication
                content_preview = (formatted_content or summary or 'No content')[:100].replace('\n', ' ')
                print(f"  Content preview: {content_preview}...")
                
                # Check if content is suspiciously similar to previous results
                if i > 0:
                    prev_content = individual_results[i-1].get('formatted_content', '') or individual_results[i-1].get('summary', '')
                    current_content = formatted_content or summary
                    if prev_content and current_content:
                        similarity = len(set(prev_content.split()) & set(current_content.split())) / max(len(prev_content.split()), len(current_content.split()))
                        print(f"  Content similarity with previous: {similarity:.2%}")
                        if similarity > 0.5:
                            print(f"  ⚠️  WARNING: High content similarity detected!")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == '__main__':
    test_multiple_urls()
