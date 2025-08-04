#!/usr/bin/env python3
"""
Test script to verify confidence score calculation
"""

from multi_role_prompting_system import MultiRolePromptingSystem

def test_confidence_calculation():
    print("Testing confidence score calculation...")
    
    # Create system instance
    system = MultiRolePromptingSystem()
    
    # Test with simple text
    test_text = "The president announced new policies today. This is a great decision."
    
    try:
        print(f"Analyzing text: {test_text}")
        result = system.analyze_text(test_text)
        
        # Check if analysis data is available
        if system.last_analysis_data:
            results = system.last_analysis_data.get('results', [])
            print(f"Found {len(results)} analysis results")
            
            if results:
                # Calculate confidence manually to verify
                total_confidence = sum(r.consensus_confidence for r in results)
                confidence_percentage = round((total_confidence / len(results)) * 100)
                
                print(f"Individual confidences: {[r.consensus_confidence for r in results]}")
                print(f"Average confidence: {total_confidence / len(results):.3f}")
                print(f"Confidence percentage: {confidence_percentage}%")
                
                # Test Flask response format
                flask_confidence = 0
                if results:
                    flask_total = sum(r.consensus_confidence for r in results)
                    flask_confidence = round((flask_total / len(results)) * 100)
                
                print(f"Flask format confidence: {flask_confidence}%")
                
                return flask_confidence
            else:
                print("No results found in analysis data")
                return 0
        else:
            print("No analysis data available")
            return 0
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 0

if __name__ == "__main__":
    confidence = test_confidence_calculation()
    print(f"\nFinal confidence result: {confidence}%")