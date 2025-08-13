#!/usr/bin/env python3
"""
Test script to verify citation service is working
"""

from gemini_citation_service import GeminiCitationService

def test_citation_service():
    """Test the citation service with a simple fact"""
    
    print("🔍 Testing Citation Service...")
    
    try:
        # Initialize citation service
        citation_service = GeminiCitationService()
        print("✅ Citation service initialized successfully")
        
        # Test with a simple factual statement
        test_sentence = "The current population of the United States is approximately 330 million people."
        print(f"\n📝 Testing sentence: {test_sentence}")
        
        # Get citations
        citations = citation_service.get_citations_for_sentence(test_sentence, "NEWS")
        
        print(f"\n📊 Results:")
        print(f"Number of citations found: {len(citations)}")
        
        if citations:
            for i, citation in enumerate(citations, 1):
                print(f"\n{i}. {citation.title}")
                print(f"   URL: {citation.url}")
                print(f"   Domain: {citation.domain}")
                print(f"   Score: {citation.verification_score:.2f}")
                print(f"   Snippet: {citation.snippet[:100]}...")
                print(f"   Reasoning: {citation.reasoning[:100]}...")
        else:
            print("❌ No citations found")
            
    except Exception as e:
        print(f"❌ Error testing citation service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_citation_service()
