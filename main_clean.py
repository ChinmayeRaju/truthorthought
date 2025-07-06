"""
Main script for Clean Fact vs Opinion Analysis System
Simple CLI interface using Gemini 2.5 Flash
"""

import sys
import json
from clean_agents import CleanAnalysisSystem
from scraper import NewsContentScraper

def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("🤖 CLEAN FACT vs OPINION ANALYSIS")
    print("🔬 Powered by Gemini 2.5 Flash")
    print("👥 4 AI Agents: Journalist | Professor | Linguist | Social Media")
    print("=" * 60)

def analyze_url(url: str):
    """Analyze content from URL"""
    print(f"\n🌐 Scraping: {url}")
    
    scraper = NewsContentScraper()
    scraped_data = scraper.scrape_url(url)
    
    if not scraped_data or not scraped_data.get('content'):
        print("❌ Failed to scrape content")
        return None
    
    print(f"✅ Scraped {len(scraped_data['content'])} characters")
    print(f"📰 Title: {scraped_data.get('title', 'N/A')}")
    
    try:
        system = CleanAnalysisSystem()
        result = system.analyze_content(scraped_data['content'])
        return result, scraped_data
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def analyze_text(text: str):
    """Analyze provided text"""
    print(f"\n📝 Analyzing text ({len(text)} characters)")
    
    try:
        system = CleanAnalysisSystem()
        result = system.analyze_content(text)
        return result, {'content': text, 'title': 'User Text'}
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def print_results(result, data):
    """Print analysis results"""
    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"📰 Title: {data.get('title', 'N/A')}")
    print(f"📊 Length: {len(data['content'])} characters")
    
    print(f"\n🎯 CLASSIFICATION: {result.final_classification}")
    print(f"🔍 CONFIDENCE: {result.confidence:.2f}")
    print(f"💭 REASONING: {result.consensus_reasoning}")
    
    if result.evidence_summary:
        print(f"\n📚 EVIDENCE:")
        for i, evidence in enumerate(result.evidence_summary, 1):
            print(f"   {i}. {evidence}")
    
    print(f"\n🤖 AGENT RESULTS:")
    for agent in result.agent_results:
        print(f"  • {agent.agent_name}: {agent.classification} ({agent.confidence:.2f})")
    
    print("=" * 60)

def save_results(result, data, filename="clean_results.json"):
    """Save results to JSON"""
    try:
        output = {
            'content_info': {
                'title': data.get('title', 'N/A'),
                'length': len(data['content']),
                'preview': data['content'][:200] + "..."
            },
            'analysis': result.to_dict()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to {filename}")
    except Exception as e:
        print(f"❌ Save failed: {e}")

def main():
    """Main function"""
    print_banner()
    
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print("\n📖 USAGE:")
        print("  python main_clean.py <URL>")
        print("  python main_clean.py --text <TEXT>")
        print("\n📝 EXAMPLES:")
        print("  python main_clean.py https://www.bbc.com/news/article")
        print('  python main_clean.py --text "The economy is improving."')
        print("\n🔧 OPTIONS:")
        print("  --help, -h    Show this help message")
        print("  --text        Analyze provided text instead of URL")
        return
    
    # Parse arguments
    if sys.argv[1] == "--text":
        if len(sys.argv) < 3:
            print("❌ Please provide text")
            return
        text = " ".join(sys.argv[2:])
        result_data = analyze_text(text)
    else:
        url = sys.argv[1]
        result_data = analyze_url(url)
    
    # Process results
    if result_data:
        result, data = result_data
        print_results(result, data)
        save_results(result, data)
        print(f"\n✅ Complete! Classification: {result.final_classification} ({result.confidence:.2f})")
    else:
        print("\n❌ Analysis failed")

if __name__ == "__main__":
    main()