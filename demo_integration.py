#!/usr/bin/env python3
"""
Demo script showcasing the Truth or Thought ↔ Bias Research Integration
This demonstrates the complete workflow from analysis to research.
"""

import requests
import json
import time
import webbrowser
from datetime import datetime

def demo_integration():
    """Demonstrate the complete integration workflow"""
    base_url = "http://localhost:5000"
    
    print("🎬 TRUTH OR THOUGHT ↔ BIAS RESEARCH INTEGRATION DEMO")
    print("=" * 60)
    
    # Demo URLs - different sources covering similar topics
    demo_urls = [
        "https://www.bbc.co.uk/news/articles/c0e9py7e28xo",
        "https://edition.cnn.com/2024/12/10/politics/trump-biden-transition/index.html"
    ]
    
    print(f"\n📰 Demo Articles:")
    for i, url in enumerate(demo_urls, 1):
        print(f"   {i}. {url}")
    
    print(f"\n🔍 STEP 1: Analyzing articles on Truth or Thought...")
    print("-" * 40)
    
    try:
        # Simulate multiple URL analysis
        analysis_response = requests.post(f"{base_url}/analyze_multiple", 
            json={
                "urls": demo_urls,
                "max_sentences": 10,
                "analysis_mode": "combined"
            },
            timeout=120
        )
        
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            if analysis_data.get('success'):
                session_id = analysis_data.get('session_id')
                
                print(f"✅ Analysis completed successfully!")
                print(f"   📊 URLs analyzed: {analysis_data.get('urls_analyzed', 0)}")
                print(f"   ✅ Facts found: {analysis_data.get('total_facts', 0)}")
                print(f"   💭 Opinions found: {analysis_data.get('total_opinions', 0)}")
                print(f"   🔑 Session ID: {session_id}")
                print(f"   🏷️ Domain: {analysis_data.get('domain', 'Unknown')}")
                
                # Show sample results
                facts = analysis_data.get('facts', [])
                if facts:
                    print(f"\n   📝 Sample fact: \"{facts[0].get('sentence', 'N/A')[:100]}...\"")
                
                time.sleep(2)
                
                print(f"\n🔬 STEP 2: Loading analysis in Bias Research...")
                print("-" * 40)
                
                # Get all sessions to show the research interface
                sessions_response = requests.get(f"{base_url}/get_analyzed_sessions")
                
                if sessions_response.status_code == 200:
                    sessions_data = sessions_response.json()
                    if sessions_data.get('success'):
                        sessions = sessions_data.get('sessions', [])
                        
                        print(f"✅ Found {len(sessions)} analysis sessions available for research")
                        
                        if sessions:
                            latest_session = sessions[0]
                            print(f"   📋 Latest: {latest_session.get('title', 'Unknown')}")
                            print(f"   📅 Analyzed: {format_timestamp(latest_session.get('timestamp', ''))}")
                            print(f"   📊 Facts: {latest_session.get('total_facts', 0)} | Opinions: {latest_session.get('total_opinions', 0)}")
                            
                            time.sleep(2)
                            
                            print(f"\n🎯 STEP 3: Demonstrating research capabilities...")
                            print("-" * 40)
                            
                            # Load the session for bias research
                            load_response = requests.get(f"{base_url}/load_session_for_bias/{latest_session.get('session_id')}")
                            
                            if load_response.status_code == 200:
                                load_data = load_response.json()
                                if load_data.get('success'):
                                    print(f"✅ Session loaded for bias research!")
                                    print(f"   📰 Article: {load_data.get('title', 'Unknown')}")
                                    print(f"   🏷️ Domain: {load_data.get('domain', 'Unknown')}")
                                    print(f"   📊 Research Data Available:")
                                    print(f"      - {load_data.get('total_facts', 0)} verified facts")
                                    print(f"      - {load_data.get('total_opinions', 0)} identified opinions")
                                    print(f"      - Original content for comparison")
                                    print(f"      - Detailed sentence analysis")
                                    
                                    # Show research capabilities
                                    print(f"\n   🔬 Research Features Available:")
                                    print(f"      ✅ Split-screen analysis interface")
                                    print(f"      ✅ User interaction tracking")
                                    print(f"      ✅ Data export for academic use")
                                    print(f"      ✅ Cross-source bias comparison")
                                    
                                    time.sleep(2)
                                    
                                    print(f"\n🎉 INTEGRATION DEMO COMPLETE!")
                                    print("=" * 60)
                                    print(f"🚀 Ready to explore? Here's what you can do:")
                                    print(f"")
                                    print(f"1. 🌐 Open Truth or Thought: {base_url}")
                                    print(f"   - Analyze news articles for facts vs opinions")
                                    print(f"   - Try multiple sources for comparison")
                                    print(f"")
                                    print(f"2. 🔬 Open Bias Research: {base_url}/bias_research")
                                    print(f"   - Select 'Load Previous Analysis' mode")
                                    print(f"   - Choose from your analyzed articles")
                                    print(f"   - Conduct academic research studies")
                                    print(f"")
                                    print(f"3. 📝 Complete Research: {base_url}/questionnaires")
                                    print(f"   - Start with pre-experiment questionnaires")
                                    print(f"   - Use bias analysis tools")
                                    print(f"   - Export data for academic use")
                                    
                                    # Offer to open browser
                                    user_input = input(f"\n🌐 Would you like to open the interfaces in your browser? (y/n): ")
                                    if user_input.lower() in ['y', 'yes']:
                                        print(f"🚀 Opening interfaces...")
                                        webbrowser.open(base_url)
                                        time.sleep(2)
                                        webbrowser.open(f"{base_url}/bias_research")
                                    
                                    return True
                                    
                print(f"❌ Demo failed at some step. Please check the console output above.")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print(f"💡 Make sure the Flask app is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def show_research_benefits():
    """Display the benefits of this integration"""
    print(f"\n🎯 RESEARCH BENEFITS")
    print("=" * 30)
    print(f"✅ **Time Efficiency**: No need to re-analyze articles")
    print(f"✅ **Consistency**: Same AI analysis across research sessions")
    print(f"✅ **Comparison**: Study bias patterns across multiple sources")
    print(f"✅ **Academic Rigor**: Complete questionnaire-based studies")
    print(f"✅ **Data Export**: Download findings for academic papers")
    print(f"✅ **Reproducibility**: Consistent results for peer review")

if __name__ == "__main__":
    print("🎬 Starting Truth or Thought ↔ Bias Research Integration Demo")
    print("📋 This demo shows how to analyze articles and use them for bias research")
    print("")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Flask server is running")
    except:
        print("❌ Flask server not running!")
        print("🚀 Please start it first: python app.py")
        exit(1)
    
    input("Press Enter to start the demo...")
    
    success = demo_integration()
    
    if success:
        show_research_benefits()
        print(f"\n🎉 Demo completed successfully!")
        print(f"📚 Check BIAS_RESEARCH_INTEGRATION_GUIDE.md for more details")
    else:
        print(f"\n❌ Demo encountered issues")
        print(f"🔧 Please check the error messages above")
