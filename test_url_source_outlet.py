#!/usr/bin/env python3
"""
Test URL source outlet extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_url_source_outlet():
    """Test source outlet extraction from URLs"""
    print("Testing URL Source Outlet Extraction")
    print("=" * 50)
    
    system = CleanAnalysisSystem()
    
    test_urls = [
        'https://www.bbc.co.uk/news/world-middle-east-67840123',
        'https://edition.cnn.com/2024/01/15/politics/ukraine-aid-package/index.html',
        'https://www.reuters.com/world/europe/ukraine-reports-2024-01-15/',
        'https://www.theguardian.com/world/2024/jan/15/ukraine-war-latest',
        'https://www.metro.co.uk/2024/01/15/ukraine-conflict-19837462/',
        'https://apnews.com/article/ukraine-war-russia-attack-12345678',
        'https://www.nytimes.com/2024/01/15/world/europe/ukraine.html',
        'https://news.sky.com/story/ukraine-war-latest-12345678'
    ]
    
    for url in test_urls:
        result = system._extract_source_outlet_from_url(url)
        print(f"URL: {url}")
        print(f"Source Outlet: {result}")
        print("-" * 30)

if __name__ == "__main__":
    test_url_source_outlet()
