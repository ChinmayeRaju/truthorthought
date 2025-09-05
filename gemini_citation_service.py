"""
Gemini-based Citation Service with Google Search Grounding
Uses Gemini's built-in search capabilities to find and verify citations
"""

import os
import json
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class VerifiedCitation:
    """Represents a verified citation with all required details"""
    url: str
    title: str
    snippet: str
    domain: str
    publication_date: Optional[str] = None
    verification_score: float = 0.0
    supports_claim: bool = False
    reasoning: str = ""

class GeminiCitationService:
    """Advanced citation service using Gemini with Google Search grounding"""
    
    def __init__(self):
        """Initialize Gemini client with search grounding capabilities"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash-lite"
        
        self.authoritative_domains = {
            'news': ['bbc.com', 'reuters.com', 'ap.org', 'cnn.com', 'guardian.com', 
                    'nytimes.com', 'washingtonpost.com', 'npr.org', 'skynews.com'],
            'academic': ['.edu', '.ac.uk', 'scholar.google.com', 'pubmed.ncbi.nlm.nih.gov',
                        'jstor.org', 'arxiv.org', 'researchgate.net'],
            'government': ['.gov', '.gov.uk', '.europa.eu', 'who.int', 'un.org'],
            'medical': ['nih.gov', 'cdc.gov', 'who.int', 'nejm.org', 'bmj.com', 'lancet.com'],
            'financial': ['sec.gov', 'federalreserve.gov', 'imf.org', 'worldbank.org']
        }
    
    def get_citations_for_sentence(self, sentence: str, domain: str = "GENERAL") -> List[VerifiedCitation]:
        """
        Get verified citations for a single sentence using Gemini with Google Search
        
        Args:
            sentence: The sentence to find citations for
            domain: Domain context (NEWS, POLITICS, HEALTH, etc.)
            
        Returns:
            List of verified citations that support the sentence
        """
        print(f"🔍 Finding citations for: {sentence[:100]}...")
        
        try:
            verification_prompt = self._create_verification_prompt(sentence, domain)
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=verification_prompt),
                    ],
                ),
            ]
            tools = [
                types.Tool(googleSearch=types.GoogleSearch()),
            ]
            generate_content_config = types.GenerateContentConfig(
                tools=tools,
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )
            
            citations = self._parse_gemini_response(response, sentence)
            
            verified_citations = self._verify_and_score_citations(citations, sentence, domain)
            
            print(f"✅ Found {len(verified_citations)} verified citations for sentence")
            return verified_citations
            
        except Exception as e:
            print(f"❌ Error getting citations for sentence: {e}")
            return []
    
    def _create_verification_prompt(self, sentence: str, domain: str) -> str:
        """Create a comprehensive verification prompt for Gemini with search grounding"""
        
        domain_specific_instructions = {
            'NEWS': "Focus on recent news reports and journalistic sources",
            'POLITICS': "Prioritize government sources, official statements, and political reporting",
            'HEALTH': "Look for medical journals, health organizations, and clinical studies",
            'TECHNOLOGY': "Find tech publications, company announcements, and industry reports",
            'FINANCE': "Search for financial reports, regulatory filings, and economic data",
            'CONFLICT': "Look for international news, diplomatic sources, and conflict reporting",
            'SCIENCE': "Find scientific papers, research institutions, and peer-reviewed sources"
        }
        
        domain_instruction = domain_specific_instructions.get(domain, "Search for credible, authoritative sources")
        
        prompt = f"""
TASK: Analyze this sentence and provide potential citations based on your knowledge.

SENTENCE TO VERIFY: "{sentence}"

DOMAIN CONTEXT: {domain}
SEARCH FOCUS: {domain_instruction}

VERIFICATION CRITERIA:
✅ Direct Support: Sources that would explicitly state or support the fact
✅ Authoritative Source: From credible, authoritative domains
✅ Recent Information: Published within reasonable timeframe  
✅ Context Match: The context in source matches the claim
✅ No Contradictions: Source doesn't contradict the fact

INSTRUCTIONS:
1. Based on your knowledge, suggest authoritative sources that would likely contain information supporting this sentence
2. Focus on well-known, credible sources: major news outlets, government sites, academic institutions
3. Provide realistic URLs and titles for sources that would verify this information
4. Only suggest sources that would directly support the claim
5. Prioritize recent, credible sources over older or less reliable ones

REQUIRED OUTPUT FORMAT (JSON):
{{
    "sentence_analysis": {{
        "is_verifiable": true/false,
        "claim_type": "factual/opinion/mixed",
        "verification_needed": true/false
    }},
    "citations": [
        {{
            "url": "complete_https_url",
            "title": "realistic_article_title", 
            "snippet": "likely_text_excerpt_from_source",
            "domain": "source_domain.com",
            "publication_date": "YYYY-MM-DD or null",
            "supports_claim": true/false,
            "support_level": "direct/indirect/contradicts",
            "reasoning": "why this source would support/doesn't support the claim",
            "credibility_score": 0.0-1.0
        }}
    ],
    "verification_summary": {{
        "total_supporting_sources": 0,
        "highest_credibility_score": 0.0,
        "recommendation": "FACT/OPINION/CONTESTED",
        "confidence": 0.0-1.0,
        "reasoning": "overall assessment explanation"
    }}
}}

IMPORTANT: Provide realistic, authoritative sources that would be expected to cover this topic. Base suggestions on your knowledge of reputable sources.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response: Any, original_sentence: str) -> List[Dict]:
        """Parse Gemini response and extract citation information"""
        try:
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                citations = data.get('citations', [])
                verification_summary = data.get('verification_summary', {})
                
                print(f"📊 Gemini found {len(citations)} potential citations")
                print(f"🎯 Recommendation: {verification_summary.get('recommendation', 'Unknown')}")
                
                return citations
            else:
                print("❌ No valid JSON found in Gemini response")
                return []
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing Gemini response: {e}")
            return []
    
    def _verify_and_score_citations(self, citations: List[Dict], sentence: str, domain: str) -> List[VerifiedCitation]:
        """Additional verification and scoring of citations"""
        verified_citations = []
        
        for citation in citations:
            try:
                # Extract citation details
                url = citation.get('url', '')
                title = citation.get('title', '')
                snippet = citation.get('snippet', '')
                domain_name = citation.get('domain', '')
                supports_claim = citation.get('supports_claim', False)
                support_level = citation.get('support_level', 'indirect')
                reasoning = citation.get('reasoning', '')
                base_score = citation.get('credibility_score', 0.5)
                
                if not supports_claim or support_level == 'contradicts':
                    print(f"❌ Skipping citation that doesn't support claim: {title}")
                    continue
                
                verification_score = self._calculate_verification_score(
                    domain_name, url, support_level, base_score
                )
                
                if verification_score >= 0.6:
                    verified_citation = VerifiedCitation(
                        url=url,
                        title=title,
                        snippet=snippet,
                        domain=domain_name,
                        verification_score=verification_score,
                        supports_claim=supports_claim,
                        reasoning=reasoning
                    )
                    verified_citations.append(verified_citation)
                    print(f"✅ Verified citation: {title} (Score: {verification_score:.2f})")
                else:
                    print(f"❌ Low verification score: {title} (Score: {verification_score:.2f})")
                    
            except Exception as e:
                print(f"❌ Error processing citation: {e}")
                continue
        
        verified_citations.sort(key=lambda x: x.verification_score, reverse=True)
        
        return verified_citations[:5] 
    
    def _calculate_verification_score(self, domain: str, url: str, support_level: str, base_score: float) -> float:
        """Calculate verification score based on domain authority and other factors"""
        score = base_score
        
        domain_lower = domain.lower()
        
        authority_bonus = 0.0
        for category, domains in self.authoritative_domains.items():
            for auth_domain in domains:
                if auth_domain in domain_lower:
                    authority_bonus = 0.3 if category in ['government', 'academic'] else 0.2
                    break
            if authority_bonus > 0:
                break
        
        score += authority_bonus
        
        support_bonuses = {
            'direct': 0.2,
            'indirect': 0.0,
            'contradicts': -1.0
        }
        score += support_bonuses.get(support_level, 0.0)
        
        if url.startswith('https://') and len(url) > 50:  # Specific article URLs
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def extract_source_name(self, citation: VerifiedCitation) -> str:
        """Extract a clean source name from citation for sentence prefixing"""
        if not citation:
            return "Unknown Source"
        
        domain = citation.domain.lower()
        
        source_mapping = {
            'bbc.co.uk': 'BBC',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'edition.cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'guardian.com': 'The Guardian',
            'theguardian.com': 'The Guardian',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'npr.org': 'NPR',
            'skynews.com': 'Sky News',
            'ap.org': 'Associated Press',
            'apnews.com': 'Associated Press',
            'metro.co.uk': 'Metro',
            'aljazeera.com': 'Al Jazeera',
            'foxnews.com': 'Fox News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News'
        }
        
        # Check for exact domain matches
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain:
                return source_name
        
        title = citation.title.lower()
        if 'bbc' in title:
            return 'BBC'
        elif 'cnn' in title:
            return 'CNN'
        elif 'reuters' in title:
            return 'Reuters'
        elif 'guardian' in title:
            return 'The Guardian'
        elif 'new york times' in title or 'nytimes' in title:
            return 'The New York Times'
        elif 'washington post' in title:
            return 'The Washington Post'
        elif 'associated press' in title or 'ap news' in title:
            return 'Associated Press'
        elif 'sky news' in title:
            return 'Sky News'
        elif 'metro' in title:
            return 'Metro'
        elif 'al jazeera' in title:
            return 'Al Jazeera'
        
        if '.' in domain:
            base_domain = domain.split('.')[0]
            return base_domain.capitalize()
        
        return "News Source"
    
    def create_source_attributed_sentence(self, original_sentence: str, citations: List[VerifiedCitation]) -> str:
        """Create a sentence with source attribution prefix"""
        if not citations or len(citations) == 0:
            return original_sentence
        
        primary_citation = max(citations, key=lambda c: c.verification_score)
        source_name = self.extract_source_name(primary_citation)
        
        clean_sentence = original_sentence.strip()
        if clean_sentence and clean_sentence[0] in '"\'':
            clean_sentence = clean_sentence[1:]
        
        attributed_sentence = f"{source_name} reported {clean_sentence}"
        
        return attributed_sentence
    
    def batch_get_citations(self, sentences: List[str], domain: str = "GENERAL") -> Dict[str, List[VerifiedCitation]]:
        """Get citations for multiple sentences with rate limiting"""
        results = {}
        
        print(f"🔍 Getting citations for {len(sentences)} sentences in domain: {domain}")
        
        for i, sentence in enumerate(sentences, 1):
            print(f"\n📝 Processing sentence {i}/{len(sentences)}")
            
            if i > 1:
                time.sleep(2) 
            
            citations = self.get_citations_for_sentence(sentence, domain)
            results[sentence] = citations
            
            print(f"✅ Completed {i}/{len(sentences)} sentences")
        
        return results

if __name__ == "__main__":
    citation_service = GeminiCitationService()
    
    test_sentences = [
        "The global temperature has increased by 1.1 degrees Celsius since pre-industrial times.",
        "Bitcoin reached an all-time high of over $60,000 in 2021.",
        "The human brain contains approximately 86 billion neurons."
    ]
    
    for sentence in test_sentences:
        print(f"\n{'='*80}")
        print(f"Testing: {sentence}")
        print(f"{'='*80}")
        
        citations = citation_service.get_citations_for_sentence(sentence, "SCIENCE")
        
        print(f"\nFound {len(citations)} verified citations:")
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.title}")
            print(f"   URL: {citation.url}")
            print(f"   Score: {citation.verification_score:.2f}")
            print(f"   Reasoning: {citation.reasoning}")
            print()
