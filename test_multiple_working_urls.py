#!/usr/bin/env python3
"""
Test script with multiple working URLs to verify 5 sentences per URL
"""

import requests
from scraper import NewsContentScraper, route_through_proxy
from clean_agents import CleanAnalysisSystem
import time

def test_multiple_working_urls():
    """Test with multiple working URLs to verify 5 sentences per URL"""
    
    # Use multiple URLs that should work (all BBC articles)
    test_urls = [
        'https://www.bbc.co.uk/news/articles/ce93y2dxlg4o',
        'https://www.bbc.com/news/world-europe-67845123',  # Different BBC format
        'https://www.bbc.co.uk/news/world-europe-67845123'  # Another BBC format
    ]
    
    print("🧪 Multiple Working URLs Test (5 sentences per URL)")
    print("=" * 60)
    print(f"📡 Testing {len(test_urls)} URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"   {i}. {url}")
    print()
    
    # Initialize components
    scraper = NewsContentScraper()
    analysis_system = CleanAnalysisSystem()
    
    total_sentences = 0
    successful_urls = 0
    results = []
    
    # Test each URL
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Testing URL {i}/{len(test_urls)}")
        print(f"📡 URL: {url}")
        
        try:
            # Scrape content
            scraped_data = scraper.scrape_url(url)
            
            if not scraped_data:
                print("❌ Failed to scrape content")
                results.append({'url': url, 'success': False, 'sentences': 0})
                continue
            
            print(f"✅ Content scraped successfully")
            print(f"📄 Title: {scraped_data.get('title', 'N/A')[:60]}...")
            
            # Extract sentences
            content = scraped_data.get('content', '')
            sentences = analysis_system._split_sentences(content)
            
            print(f"🤖 Extracted {len(sentences)} sentences from this URL")
            
            # Show sentences
            for j, sentence in enumerate(sentences, 1):
                print(f"   {j}. {sentence[:80]}...")
            
            successful_urls += 1
            total_sentences += len(sentences)
            
            results.append({
                'url': url,
                'success': True,
                'sentences': len(sentences),
                'title': scraped_data.get('title', 'N/A')
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({'url': url, 'success': False, 'sentences': 0})
        
        print("-" * 60)
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MULTIPLE URLS TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Successful URLs: {successful_urls}/{len(test_urls)}")
    print(f"📝 Total sentences extracted: {total_sentences}")
    
    if successful_urls > 0:
        avg_per_url = total_sentences / successful_urls
        print(f"📊 Average sentences per URL: {avg_per_url:.1f}")
        
        # Check if we're getting 5 sentences per URL
        expected_total = successful_urls * 5
        print(f"🎯 Expected (5 × {successful_urls} URLs): {expected_total} sentences")
        
        if total_sentences == expected_total:
            print("🎉 ✅ PERFECT! Exactly 5 sentences per URL")
        elif total_sentences <= expected_total:
            print("✅ GOOD! Up to 5 sentences per URL (some URLs may have fewer)")
        else:
            print("❌ ISSUE! More than 5 sentences per URL detected")
    
    print("\n📋 Detailed Results:")
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"   URL {i}: ✅ {result['sentences']} sentences")
        else:
            print(f"   URL {i}: ❌ Failed")
    
    return successful_urls > 0 and total_sentences <= successful_urls * 5

def main():
    """Run the test"""
    print("🚀 Testing Multiple URLs for 5 Sentences Per URL")
    print("=" * 60)
    
    success = test_multiple_working_urls()
    
    print(f"\n🎯 FINAL RESULT: {'PASSED' if success else 'FAILED'}")

if __name__ == "__main__":
    main()
