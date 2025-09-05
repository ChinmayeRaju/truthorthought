"""
Enhanced Citation Verification and Source Management System
Analyzes, verifies, and improves source citations for factual accuracy and completeness
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin
from datetime import datetime
import re
from gemini_citation_service import GeminiCitationService, VerifiedCitation
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CitationIssue:
    """Represents an issue found with a citation"""
    issue_type: str  
    severity: str   
    description: str
    suggested_fix: str
    original_citation: Dict
    
@dataclass
class VerifiedSourceEntry:
    """Represents a fully verified and formatted source entry"""
    id: str
    title: str
    url: str
    domain: str
    publication_date: Optional[str]
    access_date: str
    snippet: str
    credibility_score: float
    verification_status: str  
    citation_format: Dict  
    supporting_facts: List[str]
    
class CitationVerificationSystem:
    """Comprehensive citation verification and enhancement system"""
    
    def __init__(self):
        """Initialize the citation verification system"""
        self.gemini_service = GeminiCitationService()
        self.verified_sources = {}
        self.citation_issues = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.domain_credibility = {
            'bbc.co.uk': 0.95, 'bbc.com': 0.95,
            'reuters.com': 0.98,
            'ap.org': 0.97, 'apnews.com': 0.97,
            'npr.org': 0.92,
            'pbs.org': 0.90,
            
            'cnn.com': 0.85, 'edition.cnn.com': 0.85,
            'theguardian.com': 0.88, 'guardian.com': 0.88,
            'nytimes.com': 0.87,
            'washingtonpost.com': 0.86,
            'wsj.com': 0.89,
            'economist.com': 0.88,
            
            'skynews.com': 0.75,
            'aljazeera.com': 0.78,
            'cbsnews.com': 0.76,
            'nbcnews.com': 0.76,
            'abcnews.go.com': 0.75,
            
            '.gov': 0.92,
            '.edu': 0.88,
            '.ac.uk': 0.88,
            'who.int': 0.94,
            'un.org': 0.90,
            'europa.eu': 0.89,
            
            'nature.com': 0.96,
            'science.org': 0.96,
            'cell.com': 0.95,
            'nejm.org': 0.97,
            'bmj.com': 0.94,
            'lancet.com': 0.96,
            'pubmed.ncbi.nlm.nih.gov': 0.93,
            'scholar.google.com': 0.85,
            'arxiv.org': 0.82,
        }
    
    def analyze_citation_system(self, analysis_data: Dict) -> Dict:
        """Analyze the current citation system for issues and improvements"""
        print("🔍 Analyzing citation system for factual accuracy and completeness...")
        
        analysis_results = {
            'total_facts': 0,
            'facts_with_citations': 0,
            'citation_issues': [],
            'broken_links': [],
            'incomplete_citations': [],
            'low_credibility_sources': [],
            'verified_sources': [],
            'recommendations': [],
            'overall_score': 0.0
        }
        
        if not analysis_data or 'results' not in analysis_data:
            return analysis_results
        
        results = analysis_data['results']
        facts = [r for r in results if r.get('final_classification') == 'FACT']
        analysis_results['total_facts'] = len(facts)
        
        print(f"📊 Found {len(facts)} facts to analyze for citation quality...")
        
        for i, fact in enumerate(facts, 1):
            print(f"   Analyzing fact {i}/{len(facts)}...")
            
            citations = fact.get('citations', [])
            if citations:
                analysis_results['facts_with_citations'] += 1
                
                for citation in citations:
                    issues = self._analyze_single_citation(citation)
                    analysis_results['citation_issues'].extend(issues)
                    
                    for issue in issues:
                        if issue.issue_type == 'broken_link':
                            analysis_results['broken_links'].append(issue)
                        elif issue.issue_type == 'incomplete_info':
                            analysis_results['incomplete_citations'].append(issue)
                        elif issue.issue_type == 'low_credibility':
                            analysis_results['low_credibility_sources'].append(issue)
            
            enhanced_citations = self._verify_and_enhance_citations(fact, analysis_data.get('domain', 'GENERAL'))
            if enhanced_citations:
                analysis_results['verified_sources'].extend(enhanced_citations)
        
        analysis_results['overall_score'] = self._calculate_citation_quality_score(analysis_results)
        
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
        
        return analysis_results
    
    def _analyze_single_citation(self, citation: Dict) -> List[CitationIssue]:
        """Analyze a single citation for issues"""
        issues = []
        
        if not citation:
            return issues
        
        url = citation.get('url', '')
        title = citation.get('title', '')
        domain = citation.get('domain', '')
        
        # Check for broken or inaccessible links
        if url:
            if not self._check_url_accessibility(url):
                issues.append(CitationIssue(
                    issue_type='broken_link',
                    severity='critical',
                    description=f"URL is not accessible: {url}",
                    suggested_fix="Find alternative working URL or replace with accessible source",
                    original_citation=citation
                ))
        else:
            issues.append(CitationIssue(
                issue_type='incomplete_info',
                severity='high',
                description="Missing URL in citation",
                suggested_fix="Add complete, working URL to the citation",
                original_citation=citation
            ))
        
        # Check for incomplete information
        if not title or len(title.strip()) < 10:
            issues.append(CitationIssue(
                issue_type='incomplete_info',
                severity='medium',
                description="Missing or inadequate title information",
                suggested_fix="Add complete, descriptive title for the source",
                original_citation=citation
            ))
        
        credibility = self._calculate_domain_credibility(domain or url)
        if credibility < 0.7:
            issues.append(CitationIssue(
                issue_type='low_credibility',
                severity='medium' if credibility > 0.5 else 'high',
                description=f"Low credibility source (score: {credibility:.2f})",
                suggested_fix="Replace with more authoritative source or add additional supporting sources",
                original_citation=citation
            ))
        
        if not citation.get('publication_date'):
            issues.append(CitationIssue(
                issue_type='missing_date',
                severity='low',
                description="Missing publication date",
                suggested_fix="Add publication date if available",
                original_citation=citation
            ))
        
        return issues
    
    def _check_url_accessibility(self, url: str) -> bool:
        """Check if a URL is accessible"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400
        except:
            try:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                return response.status_code < 400
            except:
                return False
    
    def _calculate_domain_credibility(self, domain_or_url: str) -> float:
        """Calculate credibility score for a domain"""
        if not domain_or_url:
            return 0.5
        
        if domain_or_url.startswith('http'):
            domain = urlparse(domain_or_url).netloc.lower()
        else:
            domain = domain_or_url.lower()
        
        if domain in self.domain_credibility:
            return self.domain_credibility[domain]
        
        for pattern, score in self.domain_credibility.items():
            if pattern.startswith('.') and domain.endswith(pattern):
                return score
            elif pattern in domain:
                return score
        
        return 0.6
    
    def _verify_and_enhance_citations(self, fact: Dict, domain: str) -> List[VerifiedSourceEntry]:
        """Verify and enhance citations for a fact using Gemini service"""
        sentence = fact.get('original_sentence', fact.get('sentence', ''))
        
        if not sentence:
            return []
        
        print(f"🔍 Verifying citations for: {sentence[:100]}...")
        
        try:
            verified_citations = self.gemini_service.get_citations_for_sentence(sentence, domain)
            
            enhanced_sources = []
            for i, vc in enumerate(verified_citations):
                source_entry = VerifiedSourceEntry(
                    id=f"source_{int(time.time())}_{i}",
                    title=vc.title,
                    url=vc.url,
                    domain=vc.domain,
                    publication_date=vc.publication_date,
                    access_date=datetime.now().strftime('%Y-%m-%d'),
                    snippet=vc.snippet,
                    credibility_score=vc.verification_score,
                    verification_status='verified' if vc.verification_score > 0.8 else 'partially_verified',
                    citation_format=self._generate_citation_formats(vc),
                    supporting_facts=[sentence]
                )
                enhanced_sources.append(source_entry)
            
            return enhanced_sources
            
        except Exception as e:
            print(f"❌ Error verifying citations: {e}")
            return []
    
    def _generate_citation_formats(self, citation: VerifiedCitation) -> Dict:
        """Generate multiple citation formats (APA, MLA, Chicago)"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        pub_year = "n.d."
        if citation.publication_date:
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
    
    def _calculate_citation_quality_score(self, analysis_results: Dict) -> float:
        """Calculate overall citation quality score"""
        total_facts = analysis_results['total_facts']
        if total_facts == 0:
            return 0.0
        
        coverage_score = (analysis_results['facts_with_citations'] / total_facts) * 0.4
        
        total_issues = len(analysis_results['citation_issues'])
        critical_issues = len([i for i in analysis_results['citation_issues'] if i.severity == 'critical'])
        high_issues = len([i for i in analysis_results['citation_issues'] if i.severity == 'high'])
        
        issue_penalty = (critical_issues * 0.2 + high_issues * 0.1) / max(total_facts, 1)
        
        verified_bonus = min(len(analysis_results['verified_sources']) / total_facts, 0.3)
        
        final_score = max(0.0, min(1.0, coverage_score - issue_penalty + verified_bonus))
        return final_score
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate recommendations for improving citation quality"""
        recommendations = []
        
        total_facts = analysis_results['total_facts']
        facts_with_citations = analysis_results['facts_with_citations']
        
        if total_facts == 0:
            return ["No facts found to analyze."]
        
        coverage_rate = facts_with_citations / total_facts
        if coverage_rate < 0.8:
            recommendations.append(f"Improve citation coverage: Only {coverage_rate:.1%} of facts have citations. Target: 90%+")
        
        if analysis_results['broken_links']:
            recommendations.append(f"Fix {len(analysis_results['broken_links'])} broken links - these are critical issues")
        
        if analysis_results['low_credibility_sources']:
            recommendations.append(f"Replace {len(analysis_results['low_credibility_sources'])} low-credibility sources with more authoritative ones")
        
        if analysis_results['incomplete_citations']:
            recommendations.append(f"Complete {len(analysis_results['incomplete_citations'])} incomplete citations with missing information")
        
        overall_score = analysis_results['overall_score']
        if overall_score < 0.7:
            recommendations.append("Overall citation quality is below acceptable standards. Focus on high-credibility sources and complete information.")
        elif overall_score < 0.9:
            recommendations.append("Citation quality is good but can be improved. Focus on source diversity and completeness.")
        else:
            recommendations.append("Excellent citation quality! Maintain current standards.")
        
        return recommendations
    
    def generate_sources_section(self, verified_sources: List[VerifiedSourceEntry], format_style: str = 'apa') -> str:
        """Generate a properly formatted sources section"""
        if not verified_sources:
            return "No verified sources available."
        
        sorted_sources = sorted(verified_sources, key=lambda x: x.credibility_score, reverse=True)
        
        sources_section = f"## Sources ({format_style.upper()} Format)\n\n"
        
        for i, source in enumerate(sorted_sources, 1):
            citation_text = source.citation_format.get(format_style, source.citation_format.get('apa', ''))
            
            sources_section += f"{i}. {citation_text}\n"
            sources_section += f"   - **Credibility Score:** {source.credibility_score:.2f}/1.0\n"
            sources_section += f"   - **Verification Status:** {source.verification_status.title()}\n"
            sources_section += f"   - **Access Date:** {source.access_date}\n"
            if source.snippet:
                sources_section += f"   - **Excerpt:** \"{source.snippet[:150]}...\"\n"
            sources_section += "\n"
        
        return sources_section
    
    def export_citation_report(self, analysis_results: Dict, output_file: str = None) -> str:
        """Export comprehensive citation analysis report"""
        if not output_file:
            output_file = f"citation_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report = f"""# Citation Verification and Source Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Facts Analyzed:** {analysis_results['total_facts']}
- **Facts with Citations:** {analysis_results['facts_with_citations']} ({analysis_results['facts_with_citations']/max(analysis_results['total_facts'], 1):.1%})
- **Overall Citation Quality Score:** {analysis_results['overall_score']:.2f}/1.0
- **Total Issues Found:** {len(analysis_results['citation_issues'])}

## Issue Breakdown
- **Critical Issues:** {len([i for i in analysis_results['citation_issues'] if i.severity == 'critical'])}
- **High Priority Issues:** {len([i for i in analysis_results['citation_issues'] if i.severity == 'high'])}
- **Medium Priority Issues:** {len([i for i in analysis_results['citation_issues'] if i.severity == 'medium'])}
- **Low Priority Issues:** {len([i for i in analysis_results['citation_issues'] if i.severity == 'low'])}

## Specific Issues Found

### Broken Links ({len(analysis_results['broken_links'])})
"""
        
        for issue in analysis_results['broken_links']:
            report += f"- **{issue.description}**\n  - Fix: {issue.suggested_fix}\n"
        
        report += f"""
### Incomplete Citations ({len(analysis_results['incomplete_citations'])})
"""
        
        for issue in analysis_results['incomplete_citations']:
            report += f"- **{issue.description}**\n  - Fix: {issue.suggested_fix}\n"
        
        report += f"""
### Low Credibility Sources ({len(analysis_results['low_credibility_sources'])})
"""
        
        for issue in analysis_results['low_credibility_sources']:
            report += f"- **{issue.description}**\n  - Fix: {issue.suggested_fix}\n"
        
        report += """
## Recommendations
"""
        
        for i, rec in enumerate(analysis_results['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        if analysis_results['verified_sources']:
            report += "\n" + self.generate_sources_section(analysis_results['verified_sources'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Citation analysis report saved to: {output_file}")
        return output_file

if __name__ == "__main__":
    verification_system = CitationVerificationSystem()
    
    test_analysis_data = {
        'results': [
            {
                'sentence': 'The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.',
                'final_classification': 'FACT',
                'citations': [
                    {
                        'url': 'https://www.ipcc.ch/report/ar6/syr/',
                        'title': 'IPCC Sixth Assessment Report',
                        'domain': 'ipcc.ch'
                    }
                ]
            },
            {
                'sentence': 'Bitcoin reached an all-time high of over $60,000 in 2021.',
                'final_classification': 'FACT',
                'citations': []  
            }
        ],
        'domain': 'SCIENCE'
    }
    
    print("🔍 Testing Citation Verification System")
    print("=" * 60)
    
    analysis_results = verification_system.analyze_citation_system(test_analysis_data)
    
    report_file = verification_system.export_citation_report(analysis_results)
    
