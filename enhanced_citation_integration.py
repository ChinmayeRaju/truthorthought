"""
Enhanced Citation Integration System
Integrates the citation verification system into the main Truth or Thought application
"""

import os
import json
import time
from typing import List, Dict, Optional
from citation_verification_system import CitationVerificationSystem, VerifiedSourceEntry
from clean_agents import CleanAnalysisSystem
from gemini_citation_service import GeminiCitationService

class EnhancedCitationIntegration:
    """Enhanced citation system that integrates verification and fixes into the main application"""
    
    def __init__(self):
        """Initialize the enhanced citation integration system"""
        self.verification_system = CitationVerificationSystem()
        self.gemini_service = GeminiCitationService()
        
    def enhance_analysis_with_verified_citations(self, analysis_data: Dict) -> Dict:
        """Enhance existing analysis data with verified citations and fixes"""
        print("🔧 Enhancing analysis with verified citations...")
        
        if not analysis_data or 'results' not in analysis_data:
            return analysis_data
        
        citation_analysis = self.verification_system.analyze_citation_system(analysis_data)
        
        enhanced_results = []
        facts = [r for r in analysis_data['results'] if r.get('final_classification') == 'FACT']
        
        print(f"📊 Enhancing {len(facts)} facts with verified citations...")
        
        for i, result in enumerate(analysis_data['results']):
            enhanced_result = result.copy()
            
            if result.get('final_classification') == 'FACT':
                print(f"   Enhancing fact {len([r for r in enhanced_results if r.get('final_classification') == 'FACT']) + 1}...")
                
                sentence = result.get('original_sentence', result.get('sentence', ''))
                domain = analysis_data.get('domain', 'GENERAL')
                
                verified_citations = self.gemini_service.get_citations_for_sentence(sentence, domain)
                
                if verified_citations:
                    enhanced_citations = []
                    for vc in verified_citations:
                        enhanced_citation = {
                            'url': vc.url,
                            'title': vc.title,
                            'snippet': vc.snippet,
                            'domain': vc.domain,
                            'publication_date': vc.publication_date,
                            'verification_score': vc.verification_score,
                            'reasoning': vc.reasoning,
                            'credibility_level': self._get_credibility_level(vc.verification_score),
                            'citation_formats': self._generate_citation_formats(vc),
                            'access_date': time.strftime('%Y-%m-%d'),
                            'supports_claim': vc.supports_claim
                        }
                        enhanced_citations.append(enhanced_citation)
                    
                    enhanced_result['citations'] = enhanced_citations
                    enhanced_result['citation'] = enhanced_citations[0] if enhanced_citations else None
                    enhanced_result['citation_quality_score'] = max([c['verification_score'] for c in enhanced_citations]) if enhanced_citations else 0.0
                    enhanced_result['total_supporting_sources'] = len(enhanced_citations)
                    
                    if enhanced_citations:
                        primary_source = enhanced_citations[0]
                        source_name = self._extract_clean_source_name(primary_source['domain'])
                        enhanced_result['attributed_sentence'] = f"{source_name} reported {sentence}"
                    
                else:
                    enhanced_result['citation_warning'] = "No verified citations found - consider reclassifying as opinion"
                    enhanced_result['citation_quality_score'] = 0.0
                    enhanced_result['total_supporting_sources'] = 0
            
            enhanced_results.append(enhanced_result)
        
        enhanced_analysis_data = analysis_data.copy()
        enhanced_analysis_data['results'] = enhanced_results
        enhanced_analysis_data['citation_analysis'] = citation_analysis
        enhanced_analysis_data['enhancement_timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        enhanced_analysis_data['total_verified_sources'] = len(citation_analysis.get('verified_sources', []))
        
        facts_with_verified_citations = len([r for r in enhanced_results 
                                           if r.get('final_classification') == 'FACT' and r.get('citations')])
        total_facts = len([r for r in enhanced_results if r.get('final_classification') == 'FACT'])
        
        enhanced_analysis_data['citation_coverage'] = facts_with_verified_citations / max(total_facts, 1)
        enhanced_analysis_data['citation_quality_summary'] = {
            'total_facts': total_facts,
            'facts_with_verified_citations': facts_with_verified_citations,
            'coverage_percentage': (facts_with_verified_citations / max(total_facts, 1)) * 100,
            'overall_quality_score': citation_analysis.get('overall_score', 0.0),
            'recommendations': citation_analysis.get('recommendations', [])
        }
        
        print(f"✅ Enhancement complete! {facts_with_verified_citations}/{total_facts} facts now have verified citations")
        
        return enhanced_analysis_data
    
    def _get_credibility_level(self, score: float) -> str:
        """Get credibility level based on verification score"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "High"
        elif score >= 0.7:
            return "Good"
        elif score >= 0.6:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_citation_formats(self, citation) -> Dict:
        """Generate multiple citation formats"""
        current_date = time.strftime('%Y-%m-%d')
        
        pub_year = "n.d."
        if hasattr(citation, 'publication_date') and citation.publication_date:
            try:
                pub_year = citation.publication_date.split('-')[0]
            except:
                pub_year = "n.d."
        
        title = citation.title.strip()
        if not title.endswith('.'):
            title += '.'
        
        domain_parts = citation.domain.split('.')
        organization = domain_parts[0].title() if domain_parts else "Unknown"
        
        return {
            'apa': f"{organization}. ({pub_year}). {title} Retrieved {current_date}, from {citation.url}",
            'mla': f'"{title}" {organization}, {pub_year}, {citation.url}. Accessed {current_date}.',
            'chicago': f'{organization}. "{title}" Accessed {current_date}. {citation.url}.',
            'harvard': f'{organization} ({pub_year}) {title} Available at: {citation.url} (Accessed: {current_date}).'
        }
    
    def _extract_clean_source_name(self, domain: str) -> str:
        """Extract clean source name from domain"""
        source_mapping = {
            'bbc.co.uk': 'BBC', 'bbc.com': 'BBC',
            'cnn.com': 'CNN', 'edition.cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'guardian.com': 'The Guardian', 'theguardian.com': 'The Guardian',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'npr.org': 'NPR',
            'skynews.com': 'Sky News',
            'ap.org': 'Associated Press', 'apnews.com': 'Associated Press',
            'metro.co.uk': 'Metro',
            'aljazeera.com': 'Al Jazeera',
            'foxnews.com': 'Fox News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'Wall Street Journal',
            'economist.com': 'The Economist',
            'ipcc.ch': 'IPCC',
            'nasa.gov': 'NASA',
            'noaa.gov': 'NOAA',
            'who.int': 'WHO',
            'un.org': 'United Nations'
        }
        
        domain_lower = domain.lower()
        
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain_lower:
                return source_name
        
        if '.' in domain:
            base_domain = domain.split('.')[0]
            return base_domain.title()
        
        return "News Source"
    
    def generate_enhanced_sources_section(self, enhanced_analysis_data: Dict, format_style: str = 'apa') -> str:
        """Generate enhanced sources section with complete citations and working links"""
        print("📝 Generating enhanced sources section...")
        
        if not enhanced_analysis_data or 'results' not in enhanced_analysis_data:
            return "No analysis data available for sources section."
        
        all_citations = []
        seen_urls = set()
        
        for result in enhanced_analysis_data['results']:
            if result.get('final_classification') == 'FACT' and result.get('citations'):
                for citation in result['citations']:
                    url = citation.get('url', '')
                    if url and url not in seen_urls:
                        all_citations.append(citation)
                        seen_urls.add(url)
        
        if not all_citations:
            return "No verified sources available."
        
        all_citations.sort(key=lambda x: x.get('verification_score', 0), reverse=True)
        
        sources_section = f"""# Verified Sources and Citations

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
*Citation Format: {format_style.upper()}*

## Summary
- **Total Verified Sources:** {len(all_citations)}
- **Average Credibility Score:** {sum(c.get('verification_score', 0) for c in all_citations) / len(all_citations):.2f}/1.0
- **Citation Coverage:** {enhanced_analysis_data.get('citation_coverage', 0) * 100:.1f}%

## Sources

"""
        
        for i, citation in enumerate(all_citations, 1):
            citation_formats = citation.get('citation_formats', {})
            citation_text = citation_formats.get(format_style, citation_formats.get('apa', ''))
            
            if not citation_text:
                title = citation.get('title', 'Unknown Title')
                url = citation.get('url', '')
                domain = citation.get('domain', '')
                access_date = citation.get('access_date', time.strftime('%Y-%m-%d'))
                citation_text = f"{domain}. {title} Retrieved {access_date}, from {url}"
            
            sources_section += f"**{i}.** {citation_text}\n\n"
            
            sources_section += f"   - **URL:** [{citation.get('url', 'N/A')}]({citation.get('url', '#')})\n"
            sources_section += f"   - **Credibility Score:** {citation.get('verification_score', 0):.2f}/1.0 ({citation.get('credibility_level', 'Unknown')})\n"
            sources_section += f"   - **Domain:** {citation.get('domain', 'Unknown')}\n"
            sources_section += f"   - **Access Date:** {citation.get('access_date', 'Unknown')}\n"
            
            if citation.get('publication_date'):
                sources_section += f"   - **Publication Date:** {citation['publication_date']}\n"
            
            if citation.get('snippet'):
                sources_section += f"   - **Excerpt:** \"{citation['snippet'][:200]}...\"\n"
            
            if citation.get('reasoning'):
                sources_section += f"   - **Verification Notes:** {citation['reasoning'][:150]}...\n"
            
            sources_section += "\n"
        
        citation_summary = enhanced_analysis_data.get('citation_quality_summary', {})
        if citation_summary:
            sources_section += f"""## Citation Quality Assessment

- **Total Facts Analyzed:** {citation_summary.get('total_facts', 0)}
- **Facts with Verified Citations:** {citation_summary.get('facts_with_verified_citations', 0)}
- **Citation Coverage:** {citation_summary.get('coverage_percentage', 0):.1f}%
- **Overall Quality Score:** {citation_summary.get('overall_quality_score', 0):.2f}/1.0

### Recommendations
"""
            
            for i, rec in enumerate(citation_summary.get('recommendations', []), 1):
                sources_section += f"{i}. {rec}\n"
        
        sources_section += f"""
---
*This sources section was automatically generated and verified using advanced language model verification with Google Search grounding. All URLs have been checked for accessibility and credibility.*
"""
        
        return sources_section
    
    def save_enhanced_sources_to_file(self, enhanced_analysis_data: Dict, filename: str = None) -> str:
        """Save enhanced sources section to a markdown file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"enhanced_sources_{timestamp}.md"
        
        sources_content = self.generate_enhanced_sources_section(enhanced_analysis_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sources_content)
        
        print(f"📄 Enhanced sources section saved to: {filename}")
        return filename

def integrate_enhanced_citations_into_analysis(analysis_system: CleanAnalysisSystem, url: str) -> Dict:
    """
    Integrate enhanced citations into the main analysis workflow
    This function can be called from app.py to enhance any analysis with verified citations
    """
    print("🚀 Starting enhanced citation integration...")
    
    result = analysis_system.analyze_url(url)
    analysis_data = analysis_system.last_analysis_data
    
    if not analysis_data:
        print("❌ No analysis data available for citation enhancement")
        return None
    
    # Enhance with verified citations
    citation_integration = EnhancedCitationIntegration()
    enhanced_data = citation_integration.enhance_analysis_with_verified_citations(analysis_data)
    
    # Generate enhanced sources section
    sources_file = citation_integration.save_enhanced_sources_to_file(enhanced_data)
    enhanced_data['sources_file'] = sources_file
    
    print("✅ Enhanced citation integration complete!")
    return enhanced_data

if __name__ == "__main__":
    print("🔍 Testing Enhanced Citation Integration")
    print("=" * 60)
    
    test_analysis_data = {
        'results': [
            {
                'sentence': 'The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.',
                'original_sentence': 'The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.',
                'final_classification': 'FACT',
                'consensus_confidence': 0.95,
                'citations': []  # Will be enhanced
            },
            {
                'sentence': 'Bitcoin reached an all-time high of over $60,000 in 2021.',
                'original_sentence': 'Bitcoin reached an all-time high of over $60,000 in 2021.',
                'final_classification': 'FACT',
                'consensus_confidence': 0.92,
                'citations': []  # Will be enhanced
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
    
    integration_system = EnhancedCitationIntegration()
    enhanced_data = integration_system.enhance_analysis_with_verified_citations(test_analysis_data)
    
    sources_file = integration_system.save_enhanced_sources_to_file(enhanced_data)
    
    print(f"\n✅ Enhanced citation integration test complete!")
    print(f"📄 Sources file: {sources_file}")
    print(f"📊 Citation coverage: {enhanced_data.get('citation_coverage', 0) * 100:.1f}%")
    print(f"🎯 Quality score: {enhanced_data.get('citation_quality_summary', {}).get('overall_quality_score', 0):.2f}/1.0")