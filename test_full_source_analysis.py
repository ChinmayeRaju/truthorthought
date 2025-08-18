#!/usr/bin/env python3
"""
Test full analysis with source outlet attribution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_full_analysis_with_source():
    """Test full analysis including source outlet attribution"""
    print("Testing Full Analysis with Source Outlet Attribution")
    print("=" * 60)
    
    system = CleanAnalysisSystem()
    
    # Mock scraped data with URL to test source outlet extraction
    test_data = {
        'content': 'The government announced new policies today. This is a significant development for the country.',
        'title': 'Government Policy Update',
        'url': 'https://www.bbc.co.uk/news/politics-67840123'
    }
    
    print(f"Testing with URL: {test_data['url']}")
    print(f"Content: {test_data['content']}")
    print("-" * 60)
    
    # Call the internal analysis method
    result = system._analyze_content(test_data, 'POLITICS')
    
    # Check the stored analysis data
    if system.last_analysis_data:
        print("✅ Analysis completed successfully!")
        print(f"Domain: {system.last_analysis_data.get('domain', 'N/A')}")
        print(f"URL: {system.last_analysis_data.get('url', 'N/A')}")
        
        results = system.last_analysis_data.get('results', [])
        print(f"Number of analyzed sentences: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\nSentence {i}:")
            print(f"  Text: {result['sentence'][:100]}...")
            print(f"  Classification: {result['final_classification']}")
            print(f"  Source Outlet: {result.get('source_outlet', 'MISSING!')}")
            print(f"  Confidence: {result['consensus_confidence']:.2f}")
    else:
        print("❌ No analysis data stored!")

if __name__ == "__main__":
    test_full_analysis_with_source()
