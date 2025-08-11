#!/usr/bin/env python3
"""
Test URL validation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanGeminiClient, CitationVerifier

def test_url_validation():
    """Test URL validation with real URLs"""
    print("🧪 TESTING URL VALIDATION SYSTEM")
    print("=" * 60)
    
    # Initialize the system
    try:
        client = CleanGeminiClient()
        verifier = CitationVerifier(client)
        
        # Test URLs - including the problematic Washington Post URL
        test_citations = [
            {
                "title": "Ukraine and Russia Peace Talks Update",
                "url": "https://www.washingtonpost.com/politics/2025/08/10/ukraine-russia-peace-talks/"
            },
            {
                "title": "BBC News - Valid URL",
                "url": "https://www.bbc.co.uk/news/world-europe-67845123"
            },
            {
                "title": "Reuters - Valid URL", 
                "url": "https://www.reuters.com/world/europe/ukraine-reports-2024/"
            },
            {
                "title": "Invalid URL Example",
                "url": "https://example.com/fake-news-article"
            },
            {
                "title": "Generic Domain",
                "url": "bbc.com"
            }
        ]
        
        fact_text = "Ukraine and Russia are engaged in peace talks."
        
        print(f"🔍 Testing {len(test_citations)} citations for URL accessibility and validity")
        print()
        
        for i, citation in enumerate(test_citations, 1):
            print(f"📋 Citation {i}: {citation['title']}")
            print(f"🔗 URL: {citation['url']}")
            
            # Test URL accessibility first
            is_accessible = verifier._check_url_accessibility(citation['url'])
            print(f"   Accessibility: {'✅ ACCESSIBLE' if is_accessible else '❌ NOT ACCESSIBLE'}")
            
            # Test full verification
            is_valid = verifier._verify_single_citation(fact_text, citation, "POLITICS")
            print(f"   Overall Validity: {'✅ VALID' if is_valid else '❌ INVALID'}")
            print()
        
        print("=" * 60)
        print("✅ URL validation test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_url_validation()
