"""
Comprehensive Domain Detection Test Suite
"""

from clean_agents import CleanAnalysisSystem, DomainDetector, CleanGeminiClient

def test_domain_detection():
    """Comprehensive test cases for domain detection"""
    
    test_cases = [
        # LIFESTYLE - Food, brands, consumer products
        {
            "url": "https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/",
            "title": "KFC and Greggs teaming up for crossover of the century – and it's not chicken",
            "content": "Fast food chains KFC and Greggs are collaborating on a new menu item that combines their signature products. The partnership brings together Greggs' famous sausage rolls with KFC's chicken flavoring in an unprecedented brand collaboration. This marks the first time the two British food giants have worked together on a joint product offering consumers a unique dining experience.",
            "expected": "LIFESTYLE"
        },
        
        # ENVIRONMENT - Climate, conservation
        {
            "url": "https://www.bbc.co.uk/news/articles/cy98jqr4p0xo",
            "title": "Amazon deforestation law puts Brazil's environment at risk",
            "content": "New legislation in Brazil could accelerate deforestation in the Amazon rainforest, environmental scientists warn. The law reduces protection for indigenous lands and opens more areas to agricultural development. Climate experts say this could have devastating effects on global carbon emissions and biodiversity conservation efforts.",
            "expected": "ENVIRONMENT"
        },
        
        # CONFLICT - War, military operations
        {
            "url": "https://www.cnn.com/2025/01/15/europe/ukraine-russia-conflict",
            "title": "Ukraine reports missile strikes on eastern cities",
            "content": "Ukrainian officials reported multiple missile strikes on eastern cities overnight, with military installations targeted. The attacks represent an escalation in the ongoing conflict between Russia and Ukraine. Defense officials confirmed several casualties among military personnel and damage to critical infrastructure.",
            "expected": "CONFLICT"
        },
        
        # TECHNOLOGY - Tech companies, innovation
        {
            "url": "https://techcrunch.com/2025/01/10/apple-ai-features",
            "title": "Apple announces new AI features for iPhone",
            "content": "Apple unveiled advanced artificial intelligence capabilities for its latest iPhone models, including enhanced Siri functionality and machine learning-powered photography features. The tech company demonstrated how AI integration will improve user experience across iOS applications and services.",
            "expected": "TECHNOLOGY"
        },
        
        # SPORTS - Athletic events, competitions
        {
            "url": "https://espn.com/nfl/story/2025/playoffs-results",
            "title": "NFL playoff results: Chiefs advance to championship",
            "content": "The Kansas City Chiefs defeated the Buffalo Bills 31-24 in yesterday's playoff game, advancing to the AFC Championship. Patrick Mahomes threw three touchdown passes in the victory, leading his team to another Super Bowl appearance. The game featured intense competition between two top NFL teams.",
            "expected": "SPORTS"
        },
        
        # POLITICS - Elections, government
        {
            "url": "https://www.politico.com/news/2025/election-update",
            "title": "Presidential campaign heats up as primaries approach",
            "content": "Democratic and Republican candidates are ramping up their campaign efforts as primary elections draw near. Policy debates focus on healthcare, economy, and foreign policy issues. Political analysts predict a competitive election season with high voter turnout expected.",
            "expected": "POLITICS"
        },
        
        # HEALTH - Medical topics
        {
            "url": "https://www.webmd.com/news/flu-season-2025",
            "title": "Flu season reaches peak levels across the country",
            "content": "Health officials report that influenza cases have reached peak levels nationwide, with hospitals seeing increased patient volumes. The CDC recommends vaccination and preventive measures to reduce transmission. Medical experts urge people to seek treatment early if symptoms develop.",
            "expected": "HEALTH"
        },
        
        # FINANCE - Markets, economy
        {
            "url": "https://www.bloomberg.com/markets/stocks-rise",
            "title": "Stock market rallies on strong earnings reports",
            "content": "Major stock indices rose sharply following better-than-expected quarterly earnings from technology companies. The S&P 500 gained 2.5% while the Nasdaq climbed 3.1%. Financial analysts attribute the rally to strong corporate performance and investor optimism about economic growth.",
            "expected": "FINANCE"
        },
        
        # ENTERTAINMENT - Movies, celebrities
        {
            "url": "https://variety.com/film/news/oscar-nominations-2025",
            "title": "Oscar nominations announced for 2025 ceremony",
            "content": "The Academy of Motion Picture Arts and Sciences revealed this year's Oscar nominations, with several blockbuster films and indie darlings receiving multiple nods across major categories. Celebrity reactions and industry analysis follow the announcement.",
            "expected": "ENTERTAINMENT"
        },
        
        # Edge cases - Should NOT be classified as CONFLICT
        {
            "url": "https://www.bbc.co.uk/sport/football/match-report",
            "title": "Manchester United defeats Arsenal in Premier League clash",
            "content": "Manchester United secured a 3-1 victory over Arsenal at Old Trafford in a heated Premier League match. The game featured several controversial decisions and intense competition between rivals. Both teams fought hard for three points in this crucial league fixture.",
            "expected": "SPORTS"  # Not CONFLICT despite "clash" and "heated"
        },
        
        {
            "url": "https://fortune.com/business/trade-war-impact",
            "title": "Trade war between tech giants escalates",
            "content": "The ongoing business rivalry between Apple and Samsung has intensified with new patent lawsuits and competing product launches in the smartphone market. Industry analysts describe this as a 'trade war' for market dominance in mobile technology.",
            "expected": "TECHNOLOGY"  # Not CONFLICT despite "war" (metaphorical use)
        }
    ]
    
    return test_cases

def run_domain_tests():
    """Run comprehensive domain detection tests"""
    
    print("🧪 INITIALIZING DOMAIN DETECTION TEST SUITE")
    print("=" * 60)
    
    try:
        # Initialize system with LLM-powered domain detection
        system = CleanAnalysisSystem()
        test_cases = test_domain_detection()
        
        print(f"✅ System initialized successfully")
        print(f"🔧 LLM Client: {'Available' if system.domain_detector.client else 'Not Available'}")
        print(f"📋 Test Cases: {len(test_cases)}")
        print("=" * 60)
        
        passed = 0
        failed = 0
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['title'][:50]}...")
            
            try:
                # Test domain detection
                detected = system.domain_detector.detect_domain(
                    test_case['url'],
                    test_case['title'], 
                    test_case['content']
                )
                
                expected = test_case['expected']
                
                if detected == expected:
                    print(f"✅ PASS: {detected}")
                    passed += 1
                    status = "PASS"
                else:
                    print(f"❌ FAIL: Expected {expected}, got {detected}")
                    failed += 1
                    status = "FAIL"
                
                results.append({
                    'test': f"Test {i}",
                    'title': test_case['title'][:40],
                    'expected': expected,
                    'detected': detected,
                    'status': status
                })
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                failed += 1
                results.append({
                    'test': f"Test {i}",
                    'title': test_case['title'][:40],
                    'expected': test_case['expected'],
                    'detected': f"ERROR: {e}",
                    'status': "ERROR"
                })
        
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        
        # Print detailed results table
        print(f"{'Test':<8} {'Expected':<12} {'Detected':<12} {'Status':<8} {'Title':<40}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['test']:<8} {result['expected']:<12} {result['detected']:<12} {result['status']:<8} {result['title']:<40}")
        
        print(f"\n{'='*80}")
        print(f"FINAL RESULTS: {passed} passed, {failed} failed")
        success_rate = passed/(passed+failed)*100 if (passed+failed) > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        # Test specific problematic URLs with live scraping
        print(f"\n🔍 TESTING SPECIFIC PROBLEMATIC URLS:")
        problematic_urls = [
            "https://metro.co.uk/2025/08/05/kfc-greggs-teaming-crossover-century-not-chicken-23836504/",
            "https://www.bbc.co.uk/news/articles/cy98jqr4p0xo",
            "https://www.bbc.co.uk/news/articles/c9w15nggj58o"
        ]
        
        for url in problematic_urls:
            print(f"\n🌐 Testing: {url}")
            try:
                # Try to scrape and detect
                scraped_data = system.scraper.scrape_url(url)
                if scraped_data and scraped_data.get('content'):
                    detected_domain = system.domain_detector.detect_domain(
                        url, 
                        scraped_data.get('title', ''), 
                        scraped_data.get('content', '')
                    )
                    print(f"📰 Title: {scraped_data.get('title', 'N/A')}")
                    print(f"📄 Content preview: {scraped_data.get('content', '')[:200]}...")
                    print(f"🎯 Detected domain: {detected_domain}")
                else:
                    print("❌ Failed to scrape content")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return passed, failed
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to initialize system: {e}")
        return 0, 1

def test_simple_cases():
    """Test simple cases without web scraping"""
    
    print("\n🧪 TESTING SIMPLE DOMAIN DETECTION")
    print("=" * 60)
    
    try:
        # Initialize just the domain detector
        client = CleanGeminiClient()
        detector = DomainDetector(client)
        
        simple_cases = [
            ("", "KFC and Greggs collaboration", "Fast food chains working together", "LIFESTYLE"),
            ("", "Amazon rainforest deforestation", "Environmental protection concerns", "ENVIRONMENT"),
            ("", "Ukraine missile attack", "Military conflict escalation", "CONFLICT"),
            ("", "Apple iPhone AI features", "New technology announced", "TECHNOLOGY"),
            ("", "NFL playoff game", "Sports championship match", "SPORTS"),
        ]
        
        for url, title, content, expected in simple_cases:
            detected = detector.detect_domain(url, title, content)
            status = "✅ PASS" if detected == expected else "❌ FAIL"
            print(f"{status}: '{title}' → {detected} (expected {expected})")
        
    except Exception as e:
        print(f"❌ Error in simple tests: {e}")

if __name__ == "__main__":
    # Run comprehensive tests
    passed, failed = run_domain_tests()
    
    # Run simple tests
    test_simple_cases()
    
    print(f"\n{'='*80}")
    print(f"🎯 OVERALL TEST COMPLETION")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100 if passed+failed > 0 else 0:.1f}%")
    print(f"{'='*80}")
