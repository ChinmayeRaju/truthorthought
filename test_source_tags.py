#!/usr/bin/env python3
"""
Test script to verify source tag formatting functionality
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_source_tag_creation():
    """Test that source tags are properly created with metadata"""
    
    # Initialize the system
    system = CleanAnalysisSystem()
    
    # Test URLs from different outlets
    test_urls = [
        "https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html",
        "https://economictimes.indiatimes.com/news/defence/us-approves-ukraine-long-range-missiles/articleshow/115123456.cms",
        "https://www.bbc.com/news/world-europe-67890123",
        "https://www.nytimes.com/2024/11/17/world/europe/biden-ukraine-atacms-missiles.html",
        "https://www.hindustantimes.com/world-news/ukraine-us-missiles-approval-101731876543210.html",
        "https://techcrunch.com/2024/11/17/tech-news-example/",
        "https://bloomberg.com/news/articles/2024-11-17/financial-news-example"
    ]
    
    print("🏷️  Testing source tag creation with metadata:")
    print("=" * 70)
    
    for url in test_urls:
        source_tag = system._create_source_tag(url)
        
        print(f"URL: {url}")
        print(f"Tag Data:")
        print(f"  📛 Name: {source_tag['name']}")
        print(f"  🎨 Display Name: {source_tag['display_name']}")
        print(f"  🎯 Short Name: {source_tag['short_name']}")
        print(f"  🌈 Tag Color: {source_tag['tag_color']}")
        print(f"  📊 Tag Style: {source_tag['tag_style']}")
        print(f"  🌐 Domain: {source_tag['domain']}")
        print("-" * 50)
    
    print("\n✅ All source tags created successfully!")
    
    # Test specific outlets for proper formatting
    print("\n🎯 Testing specific outlet tag formatting:")
    print("=" * 60)
    
    test_cases = [
        {
            'url': 'https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html',
            'expected_name': 'The Independent',
            'expected_short': 'Independent',
            'expected_style': 'primary'
        },
        {
            'url': 'https://economictimes.indiatimes.com/news/defence/us-approves-ukraine-long-range-missiles/articleshow/115123456.cms',
            'expected_name': 'Economic Times',
            'expected_short': 'ET',
            'expected_style': 'warning'
        },
        {
            'url': 'https://www.nytimes.com/2024/11/17/world/europe/biden-ukraine-atacms-missiles.html',
            'expected_name': 'The New York Times',
            'expected_short': 'NYT',
            'expected_style': 'primary'
        }
    ]
    
    for test_case in test_cases:
        source_tag = system._create_source_tag(test_case['url'])
        
        print(f"Testing: {test_case['expected_name']}")
        print(f"  ✅ Name: {source_tag['name']} (Expected: {test_case['expected_name']})")
        print(f"  ✅ Short: {source_tag['short_name']} (Expected: {test_case['expected_short']})")
        print(f"  ✅ Style: {source_tag['tag_style']} (Expected: {test_case['expected_style']})")
        
        # Verify the values match expectations
        assert source_tag['name'] == test_case['expected_name'], f"Name mismatch: {source_tag['name']} != {test_case['expected_name']}"
        assert source_tag['short_name'] == test_case['expected_short'], f"Short name mismatch: {source_tag['short_name']} != {test_case['expected_short']}"
        assert source_tag['tag_style'] == test_case['expected_style'], f"Style mismatch: {source_tag['tag_style']} != {test_case['expected_style']}"
        
        print(f"  ✅ All assertions passed!")
        print()
    
    print("🎉 All source tag tests passed successfully!")
    
    # Test JSON serialization for frontend compatibility
    print("\n📤 Testing JSON serialization for frontend:")
    print("=" * 50)
    
    sample_tag = system._create_source_tag('https://www.independent.co.uk/news/test')
    json_output = json.dumps(sample_tag, indent=2)
    print("Sample tag JSON output:")
    print(json_output)
    
    # Verify it can be parsed back
    parsed_tag = json.loads(json_output)
    assert parsed_tag['name'] == sample_tag['name']
    print("✅ JSON serialization/deserialization works correctly!")

def test_tag_integration_in_results():
    """Test that source tags are properly integrated into analysis results"""
    
    print("\n🔗 Testing source tag integration in analysis results:")
    print("=" * 60)
    
    # Create a mock data structure similar to what would come from scraping
    mock_data = {
        'url': 'https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html',
        'title': 'US approves Ukraine long-range missiles',
        'content': 'The United States has approved the use of long-range missiles by Ukraine. This decision comes after months of deliberation. The missiles have a range of approximately 190 miles. Defense officials confirmed the policy change. The approval allows Ukraine to strike targets deep inside enemy territory.'
    }
    
    system = CleanAnalysisSystem()
    
    # Test that source tag is created correctly
    source_tag = system._create_source_tag(mock_data['url'])
    
    print(f"Source URL: {mock_data['url']}")
    print(f"Generated Tag:")
    print(f"  📛 Name: {source_tag['name']}")
    print(f"  🎨 Color: {source_tag['tag_color']}")
    print(f"  📊 Style: {source_tag['tag_style']}")
    print(f"  🎯 Short: {source_tag['short_name']}")
    
    # Verify the tag has all required fields for UI rendering
    required_fields = ['name', 'display_name', 'tag_color', 'tag_style', 'domain', 'url', 'short_name']
    for field in required_fields:
        assert field in source_tag, f"Missing required field: {field}"
        assert source_tag[field] is not None, f"Field {field} is None"
    
    print("✅ Source tag has all required fields for UI rendering!")
    
    print("\n🎯 Tag ready for frontend integration:")
    print(f"  • Display as: [{source_tag['short_name']}] with {source_tag['tag_style']} style")
    print(f"  • Color: {source_tag['tag_color']}")
    print(f"  • Full name: {source_tag['name']}")

if __name__ == "__main__":
    test_source_tag_creation()
    test_tag_integration_in_results()