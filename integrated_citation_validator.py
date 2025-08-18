"""
Integrated Citation Validator
Combines comprehensive URL validation with citation generation for Facts section
"""

import time
from typing import List, Dict
from gemini_citation_service import GeminiCitationService
from comprehensive_url_validator import ComprehensiveURLValidator

class IntegratedCitationValidator:
    """Complete citation system with comprehensive URL validation for Facts section"""
    
    def __init__(self):
        """Initialize citation and validation services"""
        self.gemini_service = GeminiCitationService()
        self.url_validator = ComprehensiveURLValidator()
    
    def get_verified_facts_with_working_sources(self, analysis_data: Dict) -> Dict:
        """Get facts with comprehensively verified working sources only"""
        print("🔧 Processing facts with comprehensive URL validation...")
        
        if not analysis_data or 'results' not in analysis_data:
            return analysis_data
        
        enhanced_results = []
        facts_processed = 0
        facts_with_verified_sources = 0
        
        for result in analysis_data['results']:
            enhanced_result = result.copy()
            
            if result.get('final_classification') == 'FACT':
                facts_processed += 1
                print(f"   Processing fact {facts_processed}...")
                
                sentence = result.get('original_sentence', result.get('sentence', ''))
                domain = analysis_data.get('domain', 'GENERAL')
                
                # Step 1: Get initial citations from Gemini
                print(f"     Getting citations for: {sentence[:80]}...")
                verified_citations = self.gemini_service.get_citations_for_sentence(sentence, domain)
                
                if verified_citations:
                    # Step 2: Convert to dictionary format for comprehensive validation
                    citation_dicts = []
                    for vc in verified_citations:
                        citation_dict = {
                            'title': vc.title,
                            'url': vc.url,
                            'domain': vc.domain,
                            'snippet': vc.snippet,
                            'verification_score': vc.verification_score,
                            'reasoning': vc.reasoning,
                            'publication_date': vc.publication_date,
                            'supports_claim': vc.supports_claim
                        }
                        citation_dicts.append(citation_dict)
                    
                    # Step 3: Comprehensive URL validation
                    print(f"     Performing comprehensive URL validation...")
                    validated_citations = self.url_validator.validate_citation_urls_comprehensive(citation_dicts)
                    
                    if validated_citations:
                        # Only include facts with verified working sources
                        enhanced_result['citations'] = validated_citations
                        enhanced_result['citation'] = validated_citations[0]  # Primary citation
                        enhanced_result['citation_quality_score'] = max([c['verification_score'] for c in validated_citations])
                        enhanced_result['total_supporting_sources'] = len(validated_citations)
                        enhanced_result['all_urls_comprehensively_verified'] = True
                        enhanced_result['validation_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Create source-attributed sentence
                        primary_source = validated_citations[0]
                        source_name = self._extract_clean_source_name(primary_source['domain'])
                        enhanced_result['attributed_sentence'] = f"{source_name} reported {sentence}"
                        
                        facts_with_verified_sources += 1
                        print(f"     ✅ Fact verified with {len(validated_citations)} working sources")
                    else:
                        # No working sources found - exclude from Facts section
                        print(f"     ❌ No working sources found - excluding from Facts section")
                        enhanced_result['excluded_reason'] = "No comprehensively verified working sources found"
                        enhanced_result['original_classification'] = 'FACT'
                        enhanced_result['final_classification'] = 'EXCLUDED_FACT'  # Mark as excluded
                        enhanced_result['all_urls_comprehensively_verified'] = False
                else:
                    # No citations found - exclude from Facts section
                    print(f"     ❌ No citations found - excluding from Facts section")
                    enhanced_result['excluded_reason'] = "No citations found"
                    enhanced_result['original_classification'] = 'FACT'
                    enhanced_result['final_classification'] = 'EXCLUDED_FACT'
                    enhanced_result['all_urls_comprehensively_verified'] = False
            
            enhanced_results.append(enhanced_result)
        
        # Update analysis data
        enhanced_analysis_data = analysis_data.copy()
        enhanced_analysis_data['results'] = enhanced_results
        enhanced_analysis_data['comprehensive_validation_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate statistics
        verified_facts = [r for r in enhanced_results if r.get('final_classification') == 'FACT' and r.get('all_urls_comprehensively_verified')]
        excluded_facts = [r for r in enhanced_results if r.get('final_classification') == 'EXCLUDED_FACT']
        
        enhanced_analysis_data['facts_validation_summary'] = {
            'total_facts_processed': facts_processed,
            'facts_with_verified_sources': len(verified_facts),
            'facts_excluded_no_sources': len(excluded_facts),
            'verification_success_rate': (len(verified_facts) / facts_processed * 100) if facts_processed > 0 else 0,
            'only_verified_sources_included': True
        }
        
        print(f"✅ Facts processing complete!")
        print(f"   📊 {len(verified_facts)}/{facts_processed} facts have comprehensively verified sources")
        print(f"   🚫 {len(excluded_facts)} facts excluded due to no working sources")
        
        return enhanced_analysis_data
    
    def _extract_clean_source_name(self, domain: str) -> str:
        """Extract clean source name from domain"""
        source_mapping = {
            'ipcc.ch': 'IPCC',
            'nasa.gov': 'NASA',
            'climate.nasa.gov': 'NASA',
            'science.nasa.gov': 'NASA',
            'noaa.gov': 'NOAA',
            'bbc.co.uk': 'BBC',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'coindesk.com': 'CoinDesk',
            'investopedia.com': 'Investopedia',
            'bankrate.com': 'Bankrate',
            'metoffice.gov.uk': 'Met Office',
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'Wall Street Journal',
            'nytimes.com': 'New York Times',
            'washingtonpost.com': 'Washington Post',
            'theguardian.com': 'The Guardian',
            'guardian.com': 'The Guardian'
        }
        
        domain_lower = domain.lower()
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain_lower:
                return source_name
        
        # Fallback
        if '.' in domain:
            return domain.split('.')[0].title()
        return "News Source"
    
    def generate_facts_section_with_verified_sources(self, enhanced_analysis_data: Dict) -> str:
        """Generate Facts section with only comprehensively verified sources"""
        print("📝 Generating Facts section with comprehensively verified sources...")
        
        if not enhanced_analysis_data or 'results' not in enhanced_analysis_data:
            return "No analysis data available."
        
        # Get only facts with verified sources
        verified_facts = [r for r in enhanced_analysis_data['results'] 
                         if r.get('final_classification') == 'FACT' and r.get('all_urls_comprehensively_verified')]
        
        excluded_facts = [r for r in enhanced_analysis_data['results'] 
                         if r.get('final_classification') == 'EXCLUDED_FACT']
        
        if not verified_facts:
            return """# Facts Section

*No facts with comprehensively verified working sources found.*

All potential facts were excluded due to:
- No working source URLs found
- URLs failed comprehensive validation (404, 500, SSL errors, etc.)
- Content not accessible or readable
- Sources not meeting verification criteria

Only facts with fully verified, accessible sources are included in this section.
"""
        
        # Generate Facts section
        facts_section = f"""# Facts Section - Comprehensively Verified Sources

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
*All sources comprehensively validated for accessibility and content*

## Summary
- **Total Facts with Verified Sources:** {len(verified_facts)}
- **Facts Excluded (No Working Sources):** {len(excluded_facts)}
- **Verification Success Rate:** {enhanced_analysis_data.get('facts_validation_summary', {}).get('verification_success_rate', 0):.1f}%
- **All URLs Comprehensively Tested:** ✅ Yes

## ✅ Verified Facts with Working Sources

"""
        
        for i, fact in enumerate(verified_facts, 1):
            sentence = fact.get('attributed_sentence', fact.get('sentence', ''))
            citations = fact.get('citations', [])
            
            facts_section += f"**{i}.** {sentence}\n\n"
            
            # Add source information
            if citations:
                facts_section += f"   **Sources ({len(citations)} verified):**\n"
                for j, citation in enumerate(citations, 1):
                    url = citation.get('url', '')
                    title = citation.get('title', 'Unknown Title')
                    domain = citation.get('domain', '')
                    response_time = citation.get('response_time', 0)
                    content_length = citation.get('content_length', 0)
                    
                    facts_section += f"   {j}. [{title}]({url})\n"
                    facts_section += f"      - Domain: {domain}\n"
                    facts_section += f"      - Status: ✅ Verified Working\n"
                    facts_section += f"      - Response Time: {response_time:.2f}s\n"
                    facts_section += f"      - Content Size: {content_length:,} bytes\n"
                    
                    if citation.get('snippet'):
                        facts_section += f"      - Excerpt: \"{citation['snippet'][:100]}...\"\n"
                    
                    facts_section += "\n"
            
            facts_section += "\n"
        
        # Add validation summary
        validation_summary = enhanced_analysis_data.get('facts_validation_summary', {})
        if validation_summary:
            facts_section += f"""## Validation Summary

- **Total Facts Processed:** {validation_summary.get('total_facts_processed', 0)}
- **Facts with Verified Sources:** {validation_summary.get('facts_with_verified_sources', 0)}
- **Facts Excluded:** {validation_summary.get('facts_excluded_no_sources', 0)}
- **Success Rate:** {validation_summary.get('verification_success_rate', 0):.1f}%

"""
        
        if excluded_facts:
            facts_section += f"""## ⚠️ Excluded Facts (No Working Sources)

The following {len(excluded_facts)} facts were excluded from the Facts section due to no comprehensively verified working sources:

"""
            for i, excluded_fact in enumerate(excluded_facts, 1):
                sentence = excluded_fact.get('sentence', '')
                reason = excluded_fact.get('excluded_reason', 'Unknown reason')
                facts_section += f"{i}. \"{sentence[:100]}...\"\n"
                facts_section += f"   - Reason: {reason}\n\n"
        
        facts_section += """## Comprehensive Validation Process

Each fact in this section has undergone the following validation:

1. **Citation Generation**: Facts verified using Gemini with Google Search grounding
2. **URL Format Validation**: Proper URL structure confirmed
3. **DNS Resolution**: Domain existence and reachability verified
4. **SSL Certificate Check**: HTTPS certificates validated
5. **HTTP Status Verification**: 200 OK response confirmed
6. **Connection Testing**: Successful connection establishment verified
7. **Content Accessibility**: Page content successfully fetched
8. **Content Readability**: Text content confirmed readable
9. **Error Page Detection**: Filtered out error and maintenance pages
10. **Performance Testing**: Response time and content size measured

---
**Guarantee:** Every fact and source in this section has passed comprehensive validation. All URLs are confirmed working, accessible, and contain relevant content at the time of validation.
"""
        
        return facts_section
    
    def save_facts_section_to_file(self, enhanced_analysis_data: Dict, filename: str = None) -> str:
        """Save Facts section with verified sources to file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"verified_facts_section_{timestamp}.md"
        
        facts_content = self.generate_facts_section_with_verified_sources(enhanced_analysis_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(facts_content)
        
        print(f"📄 Facts section with verified sources saved to: {filename}")
        return filename

# Example usage and testing
if __name__ == "__main__":
    print("🔍 Testing Integrated Citation Validator for Facts Section")
    print("=" * 70)
    
    # Test the complete system
    integrated_validator = IntegratedCitationValidator()
    
    # Mock analysis data with facts
    test_analysis_data = {
        'results': [
            {
                'sentence': 'The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.',
                'original_sentence': 'The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.',
                'final_classification': 'FACT',
                'consensus_confidence': 0.95
            },
            {
                'sentence': 'Bitcoin reached an all-time high of over $60,000 in 2021.',
                'original_sentence': 'Bitcoin reached an all-time high of over $60,000 in 2021.',
                'final_classification': 'FACT',
                'consensus_confidence': 0.92
            },
            {
                'sentence': 'This policy is the best approach for the country.',
                'final_classification': 'OPINION',
                'consensus_confidence': 0.88
            }
        ],
        'domain': 'SCIENCE',
        'title': 'Test Article',
        'url': 'https://example.com/test'
    }
    
    # Process facts with comprehensive validation
    enhanced_data = integrated_validator.get_verified_facts_with_working_sources(test_analysis_data)
    
    # Generate Facts section
    facts_file = integrated_validator.save_facts_section_to_file(enhanced_data)
    
    print(f"\n✅ Integrated citation validation test complete!")
    print(f"📄 Facts section file: {facts_file}")
    
    # Print summary
    validation_summary = enhanced_data.get('facts_validation_summary', {})
    print(f"📊 Facts with verified sources: {validation_summary.get('facts_with_verified_sources', 0)}")
    print(f"🚫 Facts excluded: {validation_summary.get('facts_excluded_no_sources', 0)}")
    print(f"✅ Success rate: {validation_summary.get('verification_success_rate', 0):.1f}%")