"""
Test script for integrated pronoun resolution system
"""

from clean_agents import CleanAnalysisSystem
import sys

def test_integrated_pronoun_resolution():
    print('🔍 Testing Integrated Pronoun Resolution System')
    print('=' * 60)

    try:
        # Initialize the system
        analyzer = CleanAnalysisSystem()
        print('✅ System initialized successfully')
        
        # Test with sample text containing facts and pronouns
        test_text = """
        Dr. Sarah Johnson, the lead climate scientist at MIT, announced groundbreaking research findings yesterday. 
        She stated that "global temperatures have risen faster than previously predicted." Johnson explained that 
        her team's data shows unprecedented warming patterns. "We are seeing changes that we didn't expect for 
        another decade," she said during the press conference.
        
        Professor Michael Chen from Stanford University disagreed with some of Johnson's conclusions. He argued 
        that the methodology needs further review. "While the data is concerning, we must be cautious about 
        drawing premature conclusions," Chen told reporters.
        """
        
        print(f'📝 Analyzing test content with pronoun resolution...')
        result = analyzer.analyze_text(test_text)
        
        print(f'✅ Analysis completed')
        
        # Check if pronoun analysis was included
        if analyzer.last_analysis_data and 'pronoun_analysis' in analyzer.last_analysis_data:
            pronoun_data = analyzer.last_analysis_data['pronoun_analysis']
            print(f'🎯 Pronoun Resolution Results:')
            print(f'   - Entities found: {pronoun_data["summary"]["total_entities"]}')
            print(f'   - Pronouns resolved: {pronoun_data["summary"]["resolved_pronouns"]}')
            print(f'   - Attribution statements: {pronoun_data["summary"]["total_statements"]}')
            print(f'   - High credibility facts: {pronoun_data["summary"]["high_credibility_facts"]}')
            
            # Show some entities
            if pronoun_data['entities']:
                print(f'\n👥 Key Personnel:')
                for entity in pronoun_data['entities'][:3]:
                    print(f'   - {entity["name"]} ({entity["full_name"]})')
                    print(f'     Credibility: {entity["credibility_score"]:.2f}')
                    print(f'     Pronouns: {entity["pronouns_used"]}')
            
            # Show attributed statements
            if pronoun_data['attributed_statements']:
                print(f'\n💬 Attributed Statements:')
                for stmt in pronoun_data['attributed_statements'][:3]:
                    print(f'   - {stmt["attributed_to"]}: "{stmt["statement"][:60]}..."')
                    print(f'     Type: {stmt["statement_type"]}, Factual: {stmt["is_factual_claim"]}')
            
            # Check enhanced results
            enhanced_facts = [r for r in analyzer.last_analysis_data['results'] if r.get('attribution')]
            if enhanced_facts:
                print(f'\n🔗 Enhanced Facts with Attribution:')
                for fact in enhanced_facts[:2]:
                    print(f'   - "{fact["sentence"][:80]}..."')
                    print(f'     Attribution: {fact["attribution"]["attributed_to"]} ({fact["attribution"]["statement_type"]})')
                    print(f'     Credibility: {fact["attribution"]["credibility_status"]}')
        else:
            print('⚠️ Pronoun analysis not found in results')
        
        print('\n✅ Integrated pronoun resolution test completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integrated_pronoun_resolution()
    sys.exit(0 if success else 1)