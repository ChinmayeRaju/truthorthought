"""
Test source attribution functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_media_outlet

def test_source_attribution():
    """Test the source attribution function"""
    
    # Test various URLs
    test_cases = [
        ("https://www.bbc.co.uk/news/world-europe-67845123", "BBC"),
        ("https://edition.cnn.com/2024/01/15/politics/ukraine-aid-package/index.html", "CNN"),
        ("https://www.reuters.com/world/europe/ukraine-reports-2024/", "Reuters"),
        ("https://www.theguardian.com/world/2024/article", "The Guardian"),
        ("https://www.metro.co.uk/news/article", "Metro"),
        ("https://apnews.com/article/12345", "Associated Press"),
        ("https://www.nytimes.com/article", "New York Times"),
        ("https://www.skynews.com/news/article", "Sky News"),
    ]
    
    print("Testing Source Attribution Function")
    print("=" * 50)
    
    for url, expected_outlet in test_cases:
        result = extract_media_outlet(url)
        status = "✅ PASS" if result == expected_outlet else "❌ FAIL"
        print(f"{status} | URL: {url[:40]}... | Expected: {expected_outlet} | Got: {result}")
    
    print("\n" + "=" * 50)
    print("Source Attribution Test Complete")

if __name__ == "__main__":
    test_source_attribution()
