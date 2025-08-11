#!/usr/bin/env python3
"""
Test improved URL validation and BBC URL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_bbc_url_citations():
    """Test the BBC URL with improved citation verification"""
    print("🧪 TESTING BBC URL WITH IMPROVED CITATION VERIFICATION")
    print("=" * 70)
    
    try:
        # Initialize the analysis system
        system = CleanAnalysisSystem()
        
        # Test the BBC URL
        bbc_url = "https://www.bbc.co.uk/news/articles/c0e9py7e28xo"
        print(f"🔍 Testing URL: {bbc_url}")
        print()
        
        # First, let's test the URL accessibility directly
        print("📋 Direct URL accessibility test:")
        is_accessible = system.citation_verifier._check_url_accessibility(bbc_url)
        print(f"   BBC URL accessible: {'✅ YES' if is_accessible else '❌ NO'}")
        print()
        
        # Now run full analysis
        print("📊 Running full fact-checking analysis...")
        result = system.analyze_url(bbc_url)
        print("✅ Analysis completed")
        
        # Check the stored analysis data for citation quality
        if system.last_analysis_data:
            results = system.last_analysis_data.get('results', [])
            print(f"\n📚 CITATION QUALITY ANALYSIS:")
            print(f"   Found {len(results)} analyzed statements")
            
            for i, result in enumerate(results, 1):
                classification = result.get('final_classification', 'UNKNOWN')
                citations = result.get('citations', [])
                
                print(f"\n   📋 Statement {i}: {classification}")
                if citations:
                    print(f"      ✅ Verified Citations ({len(citations)}):")
                    for j, citation in enumerate(citations, 1):
                        title = citation.get('title', 'No title')
                        url = citation.get('url', 'No URL')
                        print(f"         {j}. {title}")
                        print(f"            🔗 {url}")
                else:
                    print(f"      ❌ No verified citations")
        
        print("\n" + "=" * 70)
        print("✅ BBC URL citation test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bbc_url_citations()
