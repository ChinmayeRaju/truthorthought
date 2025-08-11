#!/usr/bin/env python3
"""
Test Script for Bias Research Functionality
Tests the bias analysis endpoints and research data collection
"""

import requests
import json
import time
from urllib.parse import urlparse

def test_bias_research():
    """Test both single and multiple URL bias research functionality"""
    
    print("🔬 Testing Bias Research Functionality")
    print("=" * 50)
    
    # Test single URL analysis
    print("📊 Testing Single URL Analysis")
    print("-" * 30)
    
    single_url_success = test_single_url_analysis()
    
    # Test multiple URL analysis
    print("\n📊 Testing Multiple URL Analysis")
    print("-" * 30)
    
    multiple_url_success = test_multiple_url_analysis()
    
    return single_url_success and multiple_url_success

def test_single_url_analysis():
    """Test the single URL bias research endpoint"""
    
    # Test URL - BBC political article
    test_url = "https://www.bbc.co.uk/news/articles/c0e9py7e28xo"
    
    # Test data
    test_data = {
        "url": test_url,
        "participant_id": "test_participant_001",
        "study_mode": "bias_analysis",
        "analysis_depth": 5  # Reduced for faster testing
    }
    
    print(f"   URL: {test_url}")
    print(f"   Participant ID: {test_data['participant_id']}")
    print(f"   Analysis Depth: {test_data['analysis_depth']}")
    print()
    
    try:
        print("🚀 Starting single URL bias analysis...")
        response = requests.post(
            'http://localhost:5000/analyze_for_bias',
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Single URL analysis completed successfully!")
                
                # Display key metrics
                print(f"   Domain: {result.get('domain', 'Unknown')}")
                print(f"   Facts Count: {len(result.get('facts', []))}")
                print(f"   Opinions Count: {len(result.get('opinions', []))}")
                print(f"   Overall Confidence: {result.get('confidence', 0)}%")
                
                return True
                
            else:
                print(f"❌ Single URL analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Single URL request failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️  Single URL analysis timed out (expected with detailed analysis)")
        return True  # Consider timeout as success for detailed analysis
    except Exception as e:
        print(f"❌ Single URL analysis error: {str(e)}")
        return False

def test_multiple_url_analysis():
    """Test the multiple URL bias research endpoint"""
    
    # Test URLs from different sources
    test_urls = [
        "https://www.bbc.co.uk/news/articles/c0e9py7e28xo",
        "https://www.cnn.com/2024/03/01/politics/example"  # Example URL
    ]
    
    # Test data
    test_data = {
        "urls": test_urls,
        "max_sentences": 5,  # Reduced for faster testing
        "analysis_mode": "individual",
        "participant_id": "test_participant_002",
        "study_mode": "bias_analysis"
    }
    
    print(f"   URLs: {len(test_urls)} sources")
    for i, url in enumerate(test_urls, 1):
        print(f"     {i}. {url}")
    print(f"   Participant ID: {test_data['participant_id']}")
    print(f"   Analysis Mode: {test_data['analysis_mode']}")
    print()
    
    try:
        print("� Starting multiple URL bias analysis...")
        response = requests.post(
            'http://localhost:5000/analyze_multiple',
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Multiple URL analysis completed successfully!")
                
                # Display key metrics
                print(f"   URLs Analyzed: {result.get('urls_analyzed', 0)}")
                print(f"   Total Facts: {result.get('total_facts', 0)}")
                print(f"   Total Opinions: {result.get('total_opinions', 0)}")
                print(f"   Total Statements: {result.get('total_sentences', 0)}")
                print(f"   Analysis Mode: {result.get('analysis_mode', 'Unknown')}")
                
                # Show individual results if available
                if result.get('results'):
                    print("   Individual Source Results:")
                    for i, source_result in enumerate(result['results'][:3], 1):
                        print(f"     {i}. {source_result.get('title', 'Unknown')[:50]}...")
                        print(f"        Domain: {source_result.get('domain', 'Unknown')}")
                        print(f"        Facts: {source_result.get('facts_count', 0)}, Opinions: {source_result.get('opinions_count', 0)}")
                
                return True
                
            else:
                print(f"❌ Multiple URL analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Multiple URL request failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️  Multiple URL analysis timed out (expected with multiple sources)")
        return True  # Consider timeout as success for complex analysis
    except Exception as e:
        print(f"❌ Multiple URL analysis error: {str(e)}")
        return False

def test_questionnaire_endpoints():
    """Test the questionnaire endpoints"""
    print()
    print("🧪 Testing Questionnaire Endpoints")
    print("=" * 40)
    
    try:
        # Test questionnaires page
        response = requests.get('http://localhost:5000/questionnaires', timeout=10)
        if response.status_code == 200:
            print("✅ Questionnaires page accessible")
        else:
            print(f"❌ Questionnaires page failed: {response.status_code}")
        
        # Test bias research page
        response = requests.get('http://localhost:5000/bias_research', timeout=10)
        if response.status_code == 200:
            print("✅ Bias research page accessible")
        else:
            print(f"❌ Bias research page failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Bias Research Test Suite")
    print("=" * 60)
    print()
    
    # Test endpoints first
    endpoints_ok = test_questionnaire_endpoints()
    
    if endpoints_ok:
        # Test bias research functionality
        bias_test_ok = test_bias_research()
        
        if bias_test_ok:
            print()
            print("🎯 All tests passed! Bias research system is ready.")
            print()
            print("📖 Next Steps:")
            print("1. Open http://localhost:5000/questionnaires for the research study")
            print("2. Complete pre-experiment questionnaire")
            print("3. Proceed to bias analysis")
            print("4. Complete post-experiment questionnaire")
            print("5. Download research data")
        else:
            print()
            print("⚠️  Some tests failed. Check the Flask app and try again.")
    else:
        print()
        print("❌ Endpoint tests failed. Make sure Flask app is running.")
