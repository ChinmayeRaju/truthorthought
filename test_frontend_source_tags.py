#!/usr/bin/env python3
"""
Test script to verify frontend source tag integration
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_frontend_integration():
    """Test that source tags are properly formatted for frontend consumption"""
    
    print("🔗 Testing Frontend Source Tag Integration")
    print("=" * 60)
    
    # Initialize the system
    system = CleanAnalysisSystem()
    
    # Test URLs that should generate source tags
    test_cases = [
        {
            'url': 'https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html',
            'expected_name': 'The Independent',
            'expected_short': 'Independent',
            'expected_style': 'primary',
            'expected_color': '#DC143C'
        },
        {
            'url': 'https://economictimes.indiatimes.com/news/defence/us-approves-ukraine-long-range-missiles/articleshow/115123456.cms',
            'expected_name': 'Economic Times',
            'expected_short': 'ET',
            'expected_style': 'warning',
            'expected_color': '#FF8C00'
        },
        {
            'url': 'https://www.hindustantimes.com/world-news/ukraine-us-missiles-approval-101731876543210.html',
            'expected_name': 'Hindustan Times',
            'expected_short': 'HT',
            'expected_style': 'info',
            'expected_color': '#0066CC'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['expected_name']}")
        print("-" * 40)
        
        # Create source tag
        source_tag = system._create_source_tag(test_case['url'])
        
        # Simulate what would be sent to frontend
        mock_statement = {
            'sentence': f"{test_case['expected_name']} reported The Pentagon has been quietly blocking Ukraine from using U.S.-made long-range missiles.",
            'source_tag': source_tag,
            'source_name': source_tag['name'],
            'source_url': test_case['url'],
            'final_classification': 'FACT',
            'consensus_confidence': 0.85
        }
        
        print(f"📤 Frontend Data Structure:")
        print(f"  Sentence: {mock_statement['sentence'][:80]}...")
        print(f"  Source Tag:")
        print(f"    📛 Name: {source_tag['name']}")
        print(f"    🎯 Short: {source_tag['short_name']}")
        print(f"    🎨 Color: {source_tag['tag_color']}")
        print(f"    📊 Style: {source_tag['tag_style']}")
        
        # Verify expected values
        assert source_tag['name'] == test_case['expected_name']
        assert source_tag['short_name'] == test_case['expected_short']
        assert source_tag['tag_style'] == test_case['expected_style']
        assert source_tag['tag_color'] == test_case['expected_color']
        
        print(f"  ✅ All assertions passed!")
        
        # Show how it would render in frontend
        print(f"  🎭 Frontend Rendering:")
        print(f"    Tag: [{source_tag['short_name']}] with {source_tag['tag_style']} style")
        print(f"    Color: {source_tag['tag_color']}")
        print(f"    Text: {mock_statement['sentence'].split(' reported ')[1] if ' reported ' in mock_statement['sentence'] else mock_statement['sentence']}")
    
    print(f"\n🎉 All {len(test_cases)} frontend integration tests passed!")
    
    # Test JSON serialization for API response
    print(f"\n📡 Testing API Response Format:")
    print("=" * 40)
    
    sample_response = {
        'success': True,
        'facts': [
            {
                'sentence': 'Economic Times reported Defense Secretary Pete Hegseth has final say over use of the long-range weapons.',
                'source_tag': system._create_source_tag('https://economictimes.indiatimes.com/news/test'),
                'source_name': 'Economic Times',
                'final_classification': 'FACT',
                'consensus_confidence': 0.79
            }
        ],
        'opinions': [],
        'domain': 'POLITICS'
    }
    
    # Serialize to JSON (as would happen in API response)
    json_response = json.dumps(sample_response, indent=2)
    print("Sample API Response with Source Tags:")
    print(json_response[:500] + "..." if len(json_response) > 500 else json_response)
    
    # Verify it can be parsed back
    parsed_response = json.loads(json_response)
    fact = parsed_response['facts'][0]
    
    print(f"\n✅ JSON Response Verification:")
    print(f"  Source Tag Name: {fact['source_tag']['name']}")
    print(f"  Source Tag Short: {fact['source_tag']['short_name']}")
    print(f"  Source Tag Color: {fact['source_tag']['tag_color']}")
    print(f"  Source Tag Style: {fact['source_tag']['tag_style']}")
    
    assert fact['source_tag']['name'] == 'Economic Times'
    assert fact['source_tag']['short_name'] == 'ET'
    print(f"  ✅ JSON serialization/parsing works correctly!")

if __name__ == "__main__":
    test_frontend_integration()