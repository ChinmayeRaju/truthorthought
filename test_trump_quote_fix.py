#!/usr/bin/env python3
"""
Test script to verify that direct quotes from political figures like Donald Trump
are properly classified as facts when attributed to credible sources.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_agents import CleanAnalysisSystem

def test_trump_quote_classification():
    """Test that Donald Trump quotes are properly classified as facts"""
    
    print("🔍 Testing Donald Trump Quote Classification")
    print("=" * 60)
    
    # Initialize the system
    try:
        system = CleanAnalysisSystem()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False
    
    # Test content with Donald Trump quote
    test_content = """
    Writing on Truth Social after leaving a meeting with Russian leader Vladimir Putin in Alaska 
    without reaching any deal, the US president said that ceasefires "often times do not hold up".
    
    Donald Trump stated: "very well" when asked about the negotiations.
    
    The former president also mentioned that he believes the talks were productive despite 
    the lack of immediate agreement.
    """
    
    print(f"📝 Analyzing test content with Trump quote...")
    
    try:
        # Analyze the content
        formatted_output = system.analyze_text(test_content)
        
        print(f"✅ Analysis completed successfully")
        
        # Access the stored analysis data
        analysis_data = system.last_analysis_data
        if not analysis_data:
            print(f"❌ No analysis data found")
            return False
        
        # Get the results from the stored data
        results = analysis_data.get('results', [])
        
        # Check if the Trump quote was classified as a fact
        facts_found = []
        opinions_found = []
        
        for result in results:
            sentence = result.get('sentence', '')
            original_sentence = result.get('original_sentence', '')
            classification = result.get('final_classification', '')
            
            # Check both sentence and original_sentence for Trump quote
            if ('Donald Trump stated' in sentence and 'very well' in sentence) or \
               ('Donald Trump stated' in original_sentence and 'very well' in original_sentence):
                if classification == 'FACT':
                    facts_found.append(result)
                    print(f"✅ Found Trump quote in FACTS: {sentence}")
                elif classification == 'OPINION':
                    opinions_found.append(result)
                    print(f"❌ Found Trump quote in OPINIONS (should be FACT): {sentence}")
            elif 'Trump' in sentence or 'Trump' in original_sentence:
                if classification == 'FACT':
                    facts_found.append(result)
                    print(f"📝 Found Trump-related fact: {sentence}")
                elif classification == 'OPINION':
                    opinions_found.append(result)
                    print(f"📝 Found Trump-related opinion: {sentence}")
        
        # Verify the fix worked
        trump_quote_in_facts = any(
            ('Donald Trump stated' in result.get('sentence', '') and 'very well' in result.get('sentence', '')) or
            ('Donald Trump stated' in result.get('original_sentence', '') and 'very well' in result.get('original_sentence', ''))
            for result in facts_found
        )
        trump_quote_in_opinions = any(
            ('Donald Trump stated' in result.get('sentence', '') and 'very well' in result.get('sentence', '')) or
            ('Donald Trump stated' in result.get('original_sentence', '') and 'very well' in result.get('original_sentence', ''))
            for result in opinions_found
        )
        
        print(f"\n🎯 Test Results:")
        print(f"   - Trump quote found in Facts: {trump_quote_in_facts}")
        print(f"   - Trump quote found in Opinions: {trump_quote_in_opinions}")
        
        if trump_quote_in_facts and not trump_quote_in_opinions:
            print(f"✅ SUCCESS: Donald Trump quote properly classified as FACT!")
            return True
        elif trump_quote_in_opinions:
            print(f"❌ ISSUE: Donald Trump quote still in opinions section")
            return False
        else:
            print(f"⚠️  WARNING: Donald Trump quote not found in either section")
            print(f"   This might be due to sentence filtering or processing")
            
            # Print all results for debugging
            print(f"\n📊 All Results found:")
            for i, result in enumerate(results, 1):
                classification = result.get('final_classification', 'UNKNOWN')
                sentence = result.get('sentence', '')
                original = result.get('original_sentence', '')
                print(f"   {i}. [{classification}] {sentence}")
                if original != sentence:
                    print(f"      Original: {original}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    success = test_trump_quote_classification()
    if success:
        print(f"\n🎉 Test completed successfully!")
    else:
        print(f"\n💥 Test failed - fix may need adjustment")
    
    sys.exit(0 if success else 1)