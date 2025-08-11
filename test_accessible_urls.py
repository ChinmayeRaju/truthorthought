#!/usr/bin/env python3
"""
Test with accessible real URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanGeminiClient, CitationVerifier

def test_accessible_urls():
    """Test URL validation with real, accessible URLs"""
    print("🧪 TESTING WITH ACCESSIBLE URLS")
    print("=" * 60)
    
    # Initialize the system
    try:
        client = CleanGeminiClient()
        verifier = CitationVerifier(client)
        
        # Test with real, accessible URLs
        test_citations = [
            {
                "title": "BBC News Homepage",
                "url": "https://www.bbc.com/news"
            },
            {
                "title": "CNN World News",
                "url": "https://edition.cnn.com/world"
            },
            {
                "title": "Reuters Homepage",
                "url": "https://www.reuters.com/"
            },
            {
                "title": "Google News",
                "url": "https://news.google.com"
            }
        ]
        
        fact_text = "Major news organizations provide current affairs coverage."
        
        print(f"🔍 Testing {len(test_citations)} citations for URL accessibility")
        print()
        
        for i, citation in enumerate(test_citations, 1):
            print(f"📋 Citation {i}: {citation['title']}")
            print(f"🔗 URL: {citation['url']}")
            
            # Test URL accessibility
            is_accessible = verifier._check_url_accessibility(citation['url'])
            print(f"   Accessibility: {'✅ ACCESSIBLE' if is_accessible else '❌ NOT ACCESSIBLE'}")
            print()
        
        print("=" * 60)
        print("✅ Real URL accessibility test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_accessible_urls()
