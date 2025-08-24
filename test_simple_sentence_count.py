#!/usr/bin/env python3
"""
Simple test to demonstrate proxy scraping and sentence counting
"""

from scraper import NewsContentScraper, route_through_proxy
from clean_agents import CleanAnalysisSystem

def test_sentence_counting():
    """Test URL scraping through proxy and count valid sentences"""
    
    # Use the BBC URL that we know works
    url = 'https://www.bbc.co.uk/news/articles/ce93y2dxlg4o'
    
    print("🧪 Proxy Sentence Counting Test")
    print("=" * 50)
    print(f"📡 Testing URL: {url}")
    
    # Show proxy routing
    proxied_url = route_through_proxy(url)
    print(f"🔄 Proxied URL: {proxied_url}")
    print()
    
    # Initialize components
    scraper = NewsContentScraper()
    analysis_system = CleanAnalysisSystem()
    
    # Scrape content
    print("📥 Scraping content...")
    scraped_data = scraper.scrape_url(url)
    
    if not scraped_data:
        print("❌ Failed to scrape content")
        return
    
    print(f"✅ Content scraped successfully")
    print(f"📄 Title: {scraped_data.get('title', 'N/A')}")
    print(f"📝 Content length: {len(scraped_data.get('content', ''))} characters")
    print()
    
    # Extract sentences
    content = scraped_data.get('content', '')
    sentences = analysis_system._split_sentences(content)
    
    print("📊 Sentence Analysis Results:")
    print(f"   • Total valid sentences: {len(sentences)}")
    print(f"   • Average sentence length: {sum(len(s) for s in sentences) / len(sentences):.1f} characters" if sentences else "   • No sentences found")
    print()
    
    # Show sentences
    print("📋 Extracted sentences:")
    for i, sentence in enumerate(sentences, 1):
        print(f"   {i}. {sentence}")
    print()
    
    # Test grouping
    grouped_sentences = analysis_system._group_related_sentences(sentences)
    print(f"🔗 After grouping: {len(grouped_sentences)} sentences")
    
    if len(grouped_sentences) != len(sentences):
        print("📋 Grouped sentences:")
        for i, grouped in enumerate(grouped_sentences, 1):
            print(f"   {i}. {grouped}")
    
    return len(sentences)

if __name__ == "__main__":
    sentence_count = test_sentence_counting()
    print(f"\n🎯 Final result: {sentence_count} valid sentences extracted")