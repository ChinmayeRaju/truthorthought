#!/usr/bin/env python3
"""
Test script for the bias research integration functionality
Tests the connection between Truth or Thought analysis and Bias Research
"""

import sys
import os
import requests
import json
import time

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_integration():
    """Test the complete integration workflow"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Bias Research Integration")
    print("=" * 50)
    
    # Test 1: Analyze a URL on Truth or Thought
    print("\n1. Testing URL analysis on Truth or Thought...")
    test_urls = [
        "https://www.bbc.co.uk/news/articles/c0e9py7e28xo",
        "https://edition.cnn.com/2024/12/10/politics/trump-biden-transition/index.html"
    ]
    
    try:
        # Test multiple URL analysis
        analysis_response = requests.post(f"{base_url}/analyze_multiple", 
            json={
                "urls": test_urls,
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
                print(f"   Session ID: {session_id}")
                print(f"   URLs analyzed: {analysis_data.get('urls_analyzed', 0)}")
                print(f"   Total facts: {analysis_data.get('total_facts', 0)}")
                print(f"   Total opinions: {analysis_data.get('total_opinions', 0)}")
                
                # Test 2: Get analyzed sessions for bias research
                print("\n2. Testing session retrieval for bias research...")
                sessions_response = requests.get(f"{base_url}/get_analyzed_sessions")
                
                if sessions_response.status_code == 200:
                    sessions_data = sessions_response.json()
                    if sessions_data.get('success'):
                        sessions = sessions_data.get('sessions', [])
                        print(f"✅ Retrieved {len(sessions)} previous sessions")
                        
                        if sessions:
                            latest_session = sessions[0]
                            print(f"   Latest session: {latest_session.get('title', 'Unknown')}")
                            print(f"   Timestamp: {latest_session.get('timestamp', 'Unknown')}")
                            print(f"   Domain: {latest_session.get('domain', 'Unknown')}")
                            
                            # Test 3: Load specific session for bias research
                            print("\n3. Testing session loading for bias research...")
                            session_id_to_load = latest_session.get('session_id')
                            
                            load_response = requests.get(f"{base_url}/load_session_for_bias/{session_id_to_load}")
                            
                            if load_response.status_code == 200:
                                load_data = load_response.json()
                                if load_data.get('success'):
                                    print(f"✅ Session loaded successfully for bias research!")
                                    print(f"   Title: {load_data.get('title', 'Unknown')}")
                                    print(f"   Domain: {load_data.get('domain', 'Unknown')}")
                                    print(f"   Facts available: {load_data.get('total_facts', 0)}")
                                    print(f"   Opinions available: {load_data.get('total_opinions', 0)}")
                                    print(f"   Multiple URLs: {load_data.get('is_multiple', False)}")
                                    
                                    # Check if we have proper data structure
                                    facts = load_data.get('facts', [])
                                    opinions = load_data.get('opinions', [])
                                    
                                    if facts:
                                        print(f"   Sample fact: {facts[0].get('sentence', 'No sentence')[:100]}...")
                                    if opinions:
                                        print(f"   Sample opinion: {opinions[0].get('sentence', 'No sentence')[:100]}...")
                                    
                                    print("\n🎉 Integration test completed successfully!")
                                    print("✅ Truth or Thought → Bias Research integration is working!")
                                    return True
                                else:
                                    print(f"❌ Failed to load session: {load_data.get('error', 'Unknown error')}")
                            else:
                                print(f"❌ HTTP error loading session: {load_response.status_code}")
                        else:
                            print("⚠️ No sessions found - this might be expected if this is the first run")
                            print("✅ Session retrieval endpoint is working")
                            return True
                    else:
                        print(f"❌ Failed to get sessions: {sessions_data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP error getting sessions: {sessions_response.status_code}")
            else:
                print(f"❌ Analysis failed: {analysis_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error during analysis: {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("Make sure the Flask app is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return False

def print_usage_instructions():
    """Print usage instructions for users"""
    print("\n" + "=" * 60)
    print("📋 HOW TO USE THE BIAS RESEARCH INTEGRATION")
    print("=" * 60)
    print("""
1. 🔍 ANALYZE ARTICLES ON TRUTH OR THOUGHT:
   - Go to http://localhost:5000 (main Truth or Thought page)
   - Enter one or more news article URLs
   - Click "Analyze Multiple Sources" or use single URL analysis
   - Wait for the analysis to complete

2. 🔬 ACCESS BIAS RESEARCH:
   - Go to http://localhost:5000/bias_research
   - In the "Analysis Mode" dropdown, select "Load Previous Analysis"
   - You'll see a list of previously analyzed articles
   - Click "Load" on any session to use it for bias research

3. 📊 CONDUCT BIAS RESEARCH:
   - The loaded analysis will appear in the split-screen interface
   - Original article content on the left
   - Facts vs Opinions analysis on the right
   - Use the research tools to study bias patterns
   - Export data for academic research

4. 📝 COMPLETE RESEARCH STUDY:
   - Start with questionnaires: http://localhost:5000/questionnaires
   - Follow the complete research workflow
   - Use the bias analysis tools
   - Complete post-experiment questionnaires

🎯 This integration allows you to:
   ✅ Reuse analysis from Truth or Thought in bias research
   ✅ Study bias patterns across multiple sources
   ✅ Conduct academic research with pre-analyzed data
   ✅ Save time by not re-analyzing the same content
    """)

if __name__ == "__main__":
    print("🚀 Starting Bias Research Integration Test")
    print("Make sure your Flask app is running first!")
    print("Start it with: python app.py")
    
    input("\nPress Enter to continue with the test...")
    
    success = test_integration()
    
    if success:
        print_usage_instructions()
    else:
        print("\n❌ Integration test failed!")
        print("Please check the error messages above and ensure:")
        print("1. Flask app is running (python app.py)")
        print("2. All dependencies are installed")
        print("3. Network connectivity is working")
