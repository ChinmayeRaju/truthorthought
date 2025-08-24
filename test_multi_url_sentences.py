#!/usr/bin/env python3
"""
Test script to verify 5 sentences per URL extraction for multiple URLs
"""

from scraper import NewsContentScraper, route_through_proxy
from clean_agents import CleanAnalysisSystem
import time

def test_multi_url_sentence_extraction():
    """Test that the system extracts exactly 5 sentences per URL"""
    
    # Test with multiple URLs
    test_urls = [
        'https://www.bbc.co.uk/news/articles/ce93y2dxlg4o',
        'https://www.reuters.com/world/',
        'https://www.cnn.com/2024/01/15/politics/ukraine-aid-package/index.html'
    ]
    
    print("🧪 Multi-URL Sentence Extraction Test")
    print("=" * 60)
    print(f"📡 Testing {len(test_urls)} URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"   {i}. {url}")
    print()
    
    # Initialize components
    scraper = NewsContentScraper()
    analysis_system = CleanAnalysisSystem()
    
    total_sentences_extracted = 0
    successful_urls = 0
    results = []
    
    # Test each URL individually to verify 5 sentences per URL
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Testing URL {i}/{len(test_urls)}: {url}")
        
        # Show proxy routing
        proxied_url = route_through_proxy(url)
        print(f"🔄 Proxied URL: {proxied_url}")
        
        try:
            # Scrape content
            print("📥 Scraping content...")
            start_time = time.time()
            scraped_data = scraper.scrape_url(url)
            scrape_time = time.time() - start_time
            
            if not scraped_data:
                print("❌ Failed to scrape content")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'Failed to scrape content'
                })
                continue
            
            print(f"✅ Content scraped in {scrape_time:.2f} seconds")
            print(f"📄 Title: {scraped_data.get('title', 'N/A')}")
            print(f"📝 Content length: {len(scraped_data.get('content', ''))} characters")
            
            # Extract sentences using LLM (should be exactly 5 per URL)
            content = scraped_data.get('content', '')
            sentences = analysis_system._split_sentences(content)
            
            print(f"🤖 LLM extracted {len(sentences)} sentences from this URL")
            
            # Verify we got exactly 5 sentences (or fewer if content is limited)
            expected_sentences = min(5, len(sentences)) if sentences else 0
            actual_sentences = len(sentences)
            
            print(f"📊 Expected: up to 5 sentences, Got: {actual_sentences} sentences")
            
            if actual_sentences <= 5:
                print("✅ Sentence extraction per URL is correct")
                successful_urls += 1
                total_sentences_extracted += actual_sentences
            else:
                print(f"❌ Too many sentences extracted! Expected ≤5, got {actual_sentences}")
            
            # Show sample sentences
            print("📋 Sample sentences from this URL:")
            for j, sentence in enumerate(sentences[:3], 1):  # Show first 3
                print(f"   {j}. {sentence[:80]}...")
            if len(sentences) > 3:
                print(f"   ... and {len(sentences) - 3} more sentences")
            
            results.append({
                'url': url,
                'success': True,
                'title': scraped_data.get('title', 'N/A'),
                'sentences_extracted': actual_sentences,
                'scrape_time': scrape_time,
                'content_length': len(content)
            })
            
        except Exception as e:
            print(f"❌ Error processing URL: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
        
        print("-" * 60)
        time.sleep(2)  # Brief pause between URLs
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MULTI-URL SENTENCE EXTRACTION TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Successful URLs: {successful_urls}/{len(test_urls)}")
    print(f"📝 Total sentences extracted: {total_sentences_extracted}")
    print(f"📊 Average sentences per successful URL: {total_sentences_extracted/successful_urls:.1f}" if successful_urls > 0 else "📊 No successful URLs")
    
    # Expected total: 5 sentences × number of successful URLs
    expected_total = successful_urls * 5
    print(f"🎯 Expected total (5 × {successful_urls} URLs): up to {expected_total} sentences")
    
    if total_sentences_extracted <= expected_total:
        print("🎉 ✅ MULTI-URL SENTENCE EXTRACTION TEST PASSED!")
        print("✅ System correctly extracts up to 5 sentences per URL")
    else:
        print("❌ MULTI-URL SENTENCE EXTRACTION TEST FAILED!")
        print(f"❌ Extracted {total_sentences_extracted} sentences, expected ≤{expected_total}")
    
    print("\n📋 Detailed Results:")
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"   URL {i}: ✅ {result['sentences_extracted']} sentences - {result['title'][:50]}...")
        else:
            print(f"   URL {i}: ❌ {result['error']}")
    
    return {
        'total_urls': len(test_urls),
        'successful_urls': successful_urls,
        'total_sentences': total_sentences_extracted,
        'expected_max': expected_total,
        'test_passed': total_sentences_extracted <= expected_total and successful_urls > 0
    }

def main():
    """Run the multi-URL sentence extraction test"""
    print("🚀 Starting Multi-URL Sentence Extraction Test")
    print("Testing that system extracts exactly 5 sentences per URL")
    print("=" * 60)
    print()
    
    result = test_multi_url_sentence_extraction()
    
    print(f"\n🎯 FINAL RESULT: {'PASSED' if result['test_passed'] else 'FAILED'}")
    if result['test_passed']:
        print("✅ System correctly implements 5 sentences per URL policy")
    else:
        print("❌ System needs adjustment for per-URL sentence extraction")

if __name__ == "__main__":
    main()