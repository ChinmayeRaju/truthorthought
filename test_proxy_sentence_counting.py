#!/usr/bin/env python3
"""
Test script to scrape a URL through the yazzy.carter.works proxy
and count the number of valid sentences extracted.
"""

from scraper import NewsContentScraper, route_through_proxy
from clean_agents import CleanAnalysisSystem
import time

def test_url_scraping_and_sentence_counting(url):
    """
    Test URL scraping through proxy and count valid sentences
    
    Args:
        url: The URL to test
    """
    print(f"🔍 Testing URL: {url}")
    print("=" * 80)
    
    # Initialize scraper and analysis system
    scraper = NewsContentScraper()
    analysis_system = CleanAnalysisSystem()
    
    # Show proxy routing
    proxied_url = route_through_proxy(url)
    print(f"📡 Original URL: {url}")
    print(f"🔄 Proxied URL: {proxied_url}")
    print()
    
    # Scrape the content
    print("📥 Scraping content...")
    start_time = time.time()
    
    try:
        scraped_data = scraper.scrape_url(url)
        scrape_time = time.time() - start_time
        
        if not scraped_data:
            print("❌ Failed to scrape content")
            return
        
        print(f"✅ Content scraped successfully in {scrape_time:.2f} seconds")
        print(f"📄 Title: {scraped_data.get('title', 'N/A')}")
        print(f"📝 Content length: {len(scraped_data.get('content', ''))} characters")
        print()
        
        # Extract and count sentences
        print("🔤 Extracting and counting sentences...")
        content = scraped_data.get('content', '')
        
        if not content:
            print("❌ No content found to analyze")
            return
        
        # Use the analysis system's sentence splitting method
        sentences = analysis_system._split_sentences(content)
        
        print(f"📊 Sentence Analysis Results:")
        print(f"   • Total valid sentences: {len(sentences)}")
        print(f"   • Average sentence length: {sum(len(s) for s in sentences) / len(sentences):.1f} characters" if sentences else "   • No sentences found")
        print()
        
        # Show first few sentences as examples
        print("📋 Sample sentences (first 5):")
        for i, sentence in enumerate(sentences[:5], 1):
            print(f"   {i}. {sentence[:100]}{'...' if len(sentence) > 100 else ''}")
        
        if len(sentences) > 5:
            print(f"   ... and {len(sentences) - 5} more sentences")
        
        print()
        
        # Test sentence grouping functionality
        print("🔗 Testing sentence grouping for multi-sentence fact checking...")
        grouped_sentences = analysis_system._group_related_sentences(sentences)
        
        print(f"📊 Grouping Results:")
        print(f"   • Original sentences: {len(sentences)}")
        print(f"   • After grouping: {len(grouped_sentences)}")
        print(f"   • Sentences combined: {len(sentences) - len(grouped_sentences)}")
        
        if len(grouped_sentences) != len(sentences):
            print("\n📋 Sample grouped sentences:")
            for i, grouped in enumerate(grouped_sentences[:3], 1):
                if len(grouped) > 150:  # Likely a combined sentence
                    print(f"   {i}. [COMBINED] {grouped[:150]}...")
        
        return {
            'url': url,
            'title': scraped_data.get('title', 'N/A'),
            'content_length': len(content),
            'total_sentences': len(sentences),
            'grouped_sentences': len(grouped_sentences),
            'scrape_time': scrape_time,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return {
            'url': url,
            'success': False,
            'error': str(e)
        }

def main():
    """Run tests with multiple URLs"""
    test_urls = [
        'https://www.bbc.co.uk/news/articles/ce93y2dxlg4o',
        'https://www.reuters.com/world/',
        'https://www.cnn.com/2024/01/15/politics/ukraine-aid-package/index.html'
    ]
    
    print("🧪 Proxy Sentence Counting Test Suite")
    print("=" * 80)
    print()
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}/{len(test_urls)}")
        result = test_url_scraping_and_sentence_counting(url)
        results.append(result)
        
        if i < len(test_urls):
            print("\n" + "─" * 80 + "\n")
            time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r.get('success', False)]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    
    if successful_tests:
        total_sentences = sum(r['total_sentences'] for r in successful_tests)
        total_grouped = sum(r['grouped_sentences'] for r in successful_tests)
        avg_scrape_time = sum(r['scrape_time'] for r in successful_tests) / len(successful_tests)
        
        print(f"📝 Total sentences extracted: {total_sentences}")
        print(f"🔗 Total after grouping: {total_grouped}")
        print(f"⏱️  Average scrape time: {avg_scrape_time:.2f} seconds")
        print(f"🔄 Sentences combined: {total_sentences - total_grouped}")
    
    failed_tests = [r for r in results if not r.get('success', False)]
    if failed_tests:
        print(f"\n❌ Failed tests: {len(failed_tests)}")
        for failed in failed_tests:
            print(f"   • {failed['url']}: {failed.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()