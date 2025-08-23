#!/usr/bin/env python3
"""
Test script to verify session storage and retrieval
"""

import json
import uuid
from datetime import datetime

# Simulate the session storage functions
def save_analysis_sessions(sessions):
    """Save analysis sessions to disk"""
    try:
        with open('analysis_sessions.json', 'w') as f:
            json.dump(sessions, f, indent=2)
        print(f"Saved {len(sessions)} analysis sessions to disk")
        return True
    except Exception as e:
        print(f"Error saving analysis sessions: {e}")
        return False

def load_analysis_sessions():
    """Load analysis sessions from disk"""
    try:
        with open('analysis_sessions.json', 'r') as f:
            sessions = json.load(f)
            print(f"Loaded {len(sessions)} analysis sessions from disk")
            return sessions
    except FileNotFoundError:
        print("No existing analysis sessions file found")
        return {}
    except Exception as e:
        print(f"Error loading analysis sessions: {e}")
        return {}

# Test creating a multi-source session
def test_multi_source_session():
    print("=== Testing Multi-Source Session Creation ===")
    
    # Create test session data
    session_id = str(uuid.uuid4())
    test_urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ]
    
    individual_results = []
    for i, url in enumerate(test_urls):
        individual_results.append({
            'url': url,
            'title': f'Test Article {i+1}',
            'domain': 'example.com',
            'summary': f'Summary for article {i+1}',
            'analysis': f'Analysis for article {i+1}',
            'formatted_content': f'# Test Article {i+1}\n\nContent for article {i+1}',
            'raw_content': f'Raw content for article {i+1}',
            'facts_count': 5,
            'opinions_count': 3,
            'sentences_count': 8,
            'facts': [
                {'sentence': f'Fact 1 from article {i+1}', 'citation': {}, 'citations': []},
                {'sentence': f'Fact 2 from article {i+1}', 'citation': {}, 'citations': []}
            ],
            'opinions': [
                {'sentence': f'Opinion 1 from article {i+1}'},
                {'sentence': f'Opinion 2 from article {i+1}'}
            ]
        })
    
    # Create session data structure
    session_data = {
        'analysis_data': {
            'content': 'Combined content from all articles',
            'results': [],
            'domain': 'MULTI-SOURCE',
            'title': 'Multi-Source Analysis',
            'multiple_results': individual_results,
            'urls': test_urls
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Save session
    sessions = {session_id: session_data}
    success = save_analysis_sessions(sessions)
    
    if success:
        print(f"✅ Successfully created test session: {session_id}")
        print(f"   URLs: {len(test_urls)}")
        print(f"   Individual results: {len(individual_results)}")
        
        # Test loading
        loaded_sessions = load_analysis_sessions()
        if session_id in loaded_sessions:
            loaded_session = loaded_sessions[session_id]
            analysis_data = loaded_session['analysis_data']
            
            print(f"✅ Successfully loaded session")
            print(f"   Title: {analysis_data.get('title')}")
            print(f"   Domain: {analysis_data.get('domain')}")
            print(f"   Multiple results: {'multiple_results' in analysis_data}")
            
            if 'multiple_results' in analysis_data:
                multiple_results = analysis_data['multiple_results']
                print(f"   Number of results: {len(multiple_results)}")
                for i, result in enumerate(multiple_results):
                    print(f"     Result {i+1}: {result.get('title')} - {result.get('url')}")
            
            return True
        else:
            print("❌ Failed to load session")
            return False
    else:
        print("❌ Failed to save session")
        return False

if __name__ == "__main__":
    success = test_multi_source_session()
    if success:
        print("\n🎉 Session storage test passed!")
    else:
        print("\n💥 Session storage test failed!")