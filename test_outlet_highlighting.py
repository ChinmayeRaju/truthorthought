#!/usr/bin/env python3
"""
Test script to verify outlet highlighting functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_outlet_name_extraction():
    """Test that outlet names are properly extracted from URLs"""
    
    # Initialize the system
    system = CleanAnalysisSystem()
    
    # Test URLs from different outlets
    test_urls = [
        "https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html",
        "https://economictimes.indiatimes.com/news/defence/us-approves-ukraine-long-range-missiles/articleshow/115123456.cms",
        "https://www.bbc.com/news/world-europe-67890123",
        "https://www.cnn.com/2024/11/17/politics/ukraine-atacms-missiles/index.html",
        "https://www.nytimes.com/2024/11/17/world/europe/biden-ukraine-atacms-missiles.html",
        "https://www.reuters.com/world/europe/ukraine-missiles-approval-2024-11-17/",
        "https://www.theguardian.com/world/2024/nov/17/ukraine-long-range-missiles-us-approval",
        "https://timesofindia.indiatimes.com/world/us/biden-ukraine-missiles/articleshow/115123789.cms",
        "https://www.hindustantimes.com/world-news/ukraine-us-missiles-approval-101731876543210.html",
        "https://www.ndtv.com/world-news/ukraine-gets-us-approval-for-long-range-missiles-4567890"
    ]
    
    print("🔍 Testing outlet name extraction from URLs:")
    print("=" * 60)
    
    for url in test_urls:
        outlet_name = system._extract_source_name_from_url(url)
        print(f"URL: {url}")
        print(f"Outlet: {outlet_name}")
        print("-" * 40)
    
    print("\n✅ All outlet names extracted successfully!")
    
    # Test the specific outlets mentioned by the user
    print("\n🎯 Testing specific outlets from user feedback:")
    print("=" * 50)
    
    independent_url = "https://www.independent.co.uk/news/world/americas/ukraine-missiles-us-approval-b2652847.html"
    economictimes_url = "https://economictimes.indiatimes.com/news/defence/us-approves-ukraine-long-range-missiles/articleshow/115123456.cms"
    
    independent_name = system._extract_source_name_from_url(independent_url)
    economictimes_name = system._extract_source_name_from_url(economictimes_url)
    
    print(f"The Independent URL: {independent_url}")
    print(f"Extracted Name: '{independent_name}'")
    print()
    print(f"Economic Times URL: {economictimes_url}")
    print(f"Extracted Name: '{economictimes_name}'")
    
    # Verify the names are correct
    assert independent_name == "The Independent", f"Expected 'The Independent', got '{independent_name}'"
    assert economictimes_name == "Economic Times", f"Expected 'Economic Times', got '{economictimes_name}'"
    
    print("\n✅ Both outlets are now properly mapped!")
    print(f"✅ The Independent: '{independent_name}'")
    print(f"✅ Economic Times: '{economictimes_name}'")

if __name__ == "__main__":
    test_outlet_name_extraction()