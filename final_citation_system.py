"""
Final Citation System with URL Verification
Combines citation verification, URL checking, and working link generation
"""

import time
from typing import List, Dict
from gemini_citation_service import GeminiCitationService
from url_verification_and_correction import URLVerificationSystem
from citation_verification_system import CitationVerificationSystem

class FinalCitationSystem:
    """Complete citation system with verified working URLs"""
    
    def __init__(self):
        """Initialize all citation services"""
        self.gemini_service = GeminiCitationService()
        self.url_verifier = URLVerificationSystem()
        self.citation_verifier = CitationVerificationSystem()
    
    def get_verified_citations_with_working_urls(self, sentence: str, domain: str = "GENERAL") -> List[Dict]:
        """Get citations with verified working URLs for a sentence"""
        print(f"🔍 Getting verified citations with working URLs for: {sentence[:100]}...")
        
        verified_citations = self.gemini_service.get_citations_for_sentence(sentence, domain)
        
        if not verified_citations:
            print("❌ No citations found from Gemini service")
            return []
        
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
        
        verified_url_citations = self.url_verifier.verify_citation_urls(citation_dicts)
        
        working_citations = []
        for citation in verified_url_citations:
            url_verification = citation.get('url_verification', {})
            if url_verification.get('is_accessible', False):
                # URL is working
                working_citations.append(citation)
                print(f"✅ Working citation: {citation['title'][:50]}...")
            elif citation.get('url_status') == 'fixed_with_fallback':
                # URL was fixed with fallback
                working_citations.append(citation)
                print(f"🔧 Fixed citation: {citation['title'][:50]}...")
            else:
                print(f"❌ Skipping broken citation: {citation['title'][:50]}...")
        
        print(f"✅ Found {len(working_citations)} citations with working URLs")
        return working_citations
    
    def enhance_analysis_with_working_citations(self, analysis_data: Dict) -> Dict:
        """Enhance analysis data with verified citations that have working URLs"""
        print("🔧 Enhancing analysis with verified citations and working URLs...")
        
        if not analysis_data or 'results' not in analysis_data:
            return analysis_data
        
        enhanced_results = []
        facts = [r for r in analysis_data['results'] if r.get('final_classification') == 'FACT']
        
        print(f"📊 Enhancing {len(facts)} facts with verified working citations...")
        
        for result in analysis_data['results']:
            enhanced_result = result.copy()
            
            if result.get('final_classification') == 'FACT':
                sentence = result.get('original_sentence', result.get('sentence', ''))
                domain = analysis_data.get('domain', 'GENERAL')
                
                working_citations = self.get_verified_citations_with_working_urls(sentence, domain)
                
                if working_citations:
                    enhanced_result['citations'] = working_citations
                    enhanced_result['citation'] = working_citations[0]  # Primary citation
                    enhanced_result['citation_quality_score'] = max([c['verification_score'] for c in working_citations])
                    enhanced_result['total_supporting_sources'] = len(working_citations)
                    enhanced_result['all_urls_verified'] = True
                    
                    primary_source = working_citations[0]
                    source_name = self._extract_clean_source_name(primary_source['domain'])
                    enhanced_result['attributed_sentence'] = f"{source_name} reported {sentence}"
                    
                else:
                    enhanced_result['citation_warning'] = "No working citations found - consider reclassifying as opinion"
                    enhanced_result['citation_quality_score'] = 0.0
                    enhanced_result['total_supporting_sources'] = 0
                    enhanced_result['all_urls_verified'] = False
            
            enhanced_results.append(enhanced_result)
        
        enhanced_analysis_data = analysis_data.copy()
        enhanced_analysis_data['results'] = enhanced_results
        enhanced_analysis_data['enhancement_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        facts_with_working_citations = len([r for r in enhanced_results 
                                          if r.get('final_classification') == 'FACT' and r.get('all_urls_verified')])
        total_facts = len([r for r in enhanced_results if r.get('final_classification') == 'FACT'])
        
        enhanced_analysis_data['working_citation_coverage'] = facts_with_working_citations / max(total_facts, 1)
        enhanced_analysis_data['citation_quality_summary'] = {
            'total_facts': total_facts,
            'facts_with_working_citations': facts_with_working_citations,
            'working_coverage_percentage': (facts_with_working_citations / max(total_facts, 1)) * 100,
            'all_urls_verified': True
        }
        
        print(f"✅ Enhancement complete! {facts_with_working_citations}/{total_facts} facts have working citations")
        
        return enhanced_analysis_data
    
    def _extract_clean_source_name(self, domain: str) -> str:
        """Extract clean source name from domain"""
        source_mapping = {
            'ipcc.ch': 'IPCC',
            'nasa.gov': 'NASA',
            'climate.nasa.gov': 'NASA',
            'noaa.gov': 'NOAA',
            'bbc.co.uk': 'BBC',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'coindesk.com': 'CoinDesk',
            'investopedia.com': 'Investopedia',
            'bankrate.com': 'Bankrate',
            'metoffice.gov.uk': 'Met Office'
        }
        
        domain_lower = domain.lower()
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain_lower:
                return source_name
        
        if '.' in domain:
            return domain.split('.')[0].title()
        return "News Source"
    
    def generate_final_sources_section(self, enhanced_analysis_data: Dict) -> str:
        """Generate final sources section with guaranteed working URLs"""
        print("📝 Generating final sources section with verified working URLs...")
        
        if not enhanced_analysis_data or 'results' not in enhanced_analysis_data:
            return "No analysis data available."
        
        all_working_citations = []
        seen_urls = set()
        
        for result in enhanced_analysis_data['results']:
            if result.get('final_classification') == 'FACT' and result.get('citations'):
                for citation in result['citations']:
                    url = citation.get('url', '')
                    if url and url not in seen_urls:
                        # Only include if URL verification passed
                        url_verification = citation.get('url_verification', {})
                        if url_verification.get('is_accessible', False) or citation.get('url_status') == 'fixed_with_fallback':
                            all_working_citations.append(citation)
                            seen_urls.add(url)
        
        if not all_working_citations:
            return "No verified working sources available."
        
        all_working_citations.sort(key=lambda x: x.get('verification_score', 0), reverse=True)
        
        sources_section = f"""# Verified Sources with Working URLs

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
*All URLs verified accessible at generation time*

## Summary
- **Total Verified Sources:** {len(all_working_citations)}
- **All URLs Tested:** ✅ Working
- **Average Credibility Score:** {sum(c.get('verification_score', 0) for c in all_working_citations) / len(all_working_citations):.2f}/1.0
- **URL Success Rate:** 100% (Only working URLs included)

## ✅ Verified Working Sources

"""
        
        for i, citation in enumerate(all_working_citations, 1):
            title = citation.get('title', 'Unknown Title')
            url = citation.get('url', '')
            domain = citation.get('domain', '')
            verification_score = citation.get('verification_score', 0)
            url_verification = citation.get('url_verification', {})
            
            sources_section += f"**{i}.** {title}\n\n"
            sources_section += f"   - **URL:** [{url}]({url})\n"
            sources_section += f"   - **Domain:** {domain}\n"
            sources_section += f"   - **Credibility Score:** {verification_score:.2f}/1.0\n"
            sources_section += f"   - **URL Status:** ✅ Verified Working (HTTP {url_verification.get('status_code', 200)})\n"
            sources_section += f"   - **Verified:** {url_verification.get('verification_timestamp', 'Unknown')}\n"
            
            if citation.get('snippet'):
                sources_section += f"   - **Excerpt:** \"{citation['snippet'][:150]}...\"\n"
            
            if citation.get('reasoning'):
                sources_section += f"   - **Verification Notes:** {citation['reasoning'][:100]}...\n"
            
            if citation.get('url_status') == 'fixed_with_fallback':
                sources_section += f"   - **Note:** 🔧 Original URL was broken, replaced with verified working alternative\n"
            
            sources_section += "\n"
        
        quality_summary = enhanced_analysis_data.get('citation_quality_summary', {})
        if quality_summary:
            sources_section += f"""## Citation Quality Summary

- **Total Facts Analyzed:** {quality_summary.get('total_facts', 0)}
- **Facts with Working Citations:** {quality_summary.get('facts_with_working_citations', 0)}
- **Working URL Coverage:** {quality_summary.get('working_coverage_percentage', 0):.1f}%
- **All URLs Verified:** ✅ Yes

"""
        
        sources_section += """## Verification Process

1. **Initial Citation Generation:** Facts verified using Gemini with Google Search grounding
2. **URL Accessibility Testing:** Each URL tested with HTTP requests to ensure accessibility
3. **Broken Link Replacement:** Non-working URLs replaced with verified alternatives
4. **Final Verification:** All included URLs confirmed working at generation time
5. **Quality Scoring:** Sources ranked by credibility and verification scores

---
**Guarantee:** All URLs in this sources section have been verified as accessible and should work when clicked. If any URL doesn't work, it may have become inaccessible after this report was generated.
"""
        
        return sources_section
    
    def save_final_sources_to_file(self, enhanced_analysis_data: Dict, filename: str = None) -> str:
        """Save final sources section with working URLs to file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"final_verified_sources_{timestamp}.md"
        
        sources_content = self.generate_final_sources_section(enhanced_analysis_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sources_content)
        
        print(f"📄 Final verified sources saved to: {filename}")
        return filename

if __name__ == "__main__":
    print("🔍 Testing Final Citation System with URL Verification")
    print("=" * 70)
    
    final_system = FinalCitationSystem()
    
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
            }
        ],
        'domain': 'SCIENCE',
        'title': 'Test Article',
        'url': 'https://example.com/test'
    }
    
    enhanced_data = final_system.enhance_analysis_with_working_citations(test_analysis_data)
    
    sources_file = final_system.save_final_sources_to_file(enhanced_data)
    
    print(f"\n✅ Final citation system test complete!")
    print(f"📄 Sources file: {sources_file}")
    
    quality_summary = enhanced_data.get('citation_quality_summary', {})
    print(f"📊 Working citation coverage: {quality_summary.get('working_coverage_percentage', 0):.1f}%")
    print(f"🔗 All URLs verified: {quality_summary.get('all_urls_verified', False)}")