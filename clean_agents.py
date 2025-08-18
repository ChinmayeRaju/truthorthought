"""
Clean Fact vs Opinion Analysis System using Google Generative AI SDK
Simple 4-agent system with Gemini-based citation verification
"""

import os
import json
import time
import re
from dataclasses import dataclass, asdict
from typing import List, Dict
from urllib.parse import urlparse
from dotenv import load_dotenv
import google.generativeai as genai
from scraper import NewsContentScraper
from gemini_citation_service import GeminiCitationService, VerifiedCitation
from integrated_citation_validator import IntegratedCitationValidator

# Load environment variables
load_dotenv()

# Domain-specific role configurations
DOMAIN_ROLES = {
    'NEWS': [
        ("Investigative Journalist", "investigative journalist with expertise in fact-checking news sources and verifying claims"),
        ("Media Analyst", "media analyst specialized in identifying bias, opinion, and factual reporting in news"),
        ("Political Reporter", "political reporter with deep knowledge of current events and political fact-checking")
    ],
    'CONFLICT': [
        ("War Correspondent", "experienced war correspondent with expertise in conflict reporting and military affairs"),
        ("Security Analyst", "security and defense analyst specialized in geopolitical conflicts and military operations"),
        ("International Relations Expert", "international relations expert focused on conflict analysis and diplomatic affairs")
    ],
    'POLITICS': [
        ("Political Journalist", "seasoned political journalist with expertise in governmental affairs and policy analysis"),
        ("Policy Analyst", "policy analyst specialized in political systems and governmental decision-making"),
        ("Electoral Expert", "electoral systems expert focused on political processes and democratic institutions")
    ],
    'FINANCE': [
        ("Financial Analyst", "certified financial analyst with expertise in market data and economic indicators"),
        ("Investment Advisor", "investment advisor specialized in distinguishing financial facts from market opinions"),
        ("Economic Researcher", "economic researcher with focus on financial data verification and market analysis")
    ],
    'HEALTH': [
        ("Medical Professional", "medical doctor with expertise in evaluating health claims and medical evidence"),
        ("Research Scientist", "biomedical research scientist specialized in clinical data and health studies"),
        ("Health Policy Expert", "health policy expert focused on distinguishing medical facts from health opinions")
    ],
    'TECHNOLOGY': [
        ("Tech Journalist", "technology journalist with deep knowledge of tech industry and innovation trends"),
        ("Software Engineer", "senior software engineer with expertise in technical specifications and industry facts"),
        ("Tech Analyst", "technology analyst specialized in evaluating tech claims and product information")
    ],
    'SPORTS': [
        ("Sports Journalist", "sports journalist with extensive knowledge of athletic performance and statistics"),
        ("Sports Analyst", "sports analyst specialized in game statistics and player performance data"),
        ("Athletic Expert", "athletic performance expert focused on sports facts versus commentary")
    ],
    'ENTERTAINMENT': [
        ("Entertainment Reporter", "entertainment industry reporter with knowledge of celebrity facts and industry news"),
        ("Media Critic", "media critic specialized in distinguishing entertainment facts from opinions"),
        ("Industry Analyst", "entertainment industry analyst focused on box office data and industry trends")
    ],
    'SCIENCE': [
        ("Research Scientist", "research scientist with expertise in peer-reviewed studies and scientific methodology"),
        ("Science Journalist", "science journalist specialized in fact-checking scientific claims and research"),
        ("Academic Researcher", "academic researcher focused on evidence-based analysis and scientific data")
    ],
    'ENVIRONMENT': [
        ("Environmental Scientist", "environmental scientist with expertise in climate data and ecological studies"),
        ("Climate Researcher", "climate researcher specialized in environmental facts and scientific evidence"),
        ("Sustainability Expert", "sustainability expert focused on environmental policy and conservation facts")
    ],
    'LEGAL': [
        ("Legal Analyst", "legal analyst with expertise in law, court proceedings, and judicial systems"),
        ("Constitutional Expert", "constitutional law expert specialized in legal precedents and judicial decisions"),
        ("Court Reporter", "experienced court reporter focused on legal facts versus legal opinions")
    ],
    'LIFESTYLE': [
        ("Consumer Reporter", "consumer lifestyle reporter with expertise in product reviews and brand analysis"),
        ("Food & Lifestyle Critic", "food and lifestyle critic specialized in distinguishing factual information from personal preferences"),
        ("Brand Analyst", "brand and consumer market analyst focused on product facts versus marketing opinions")
    ],
    'GENERAL': [
        ("News Journalist", "experienced news journalist focused on factual accuracy and source verification"),
        ("Academic Professor", "university professor specializing in critical analysis and evidence evaluation"),
        ("Research Analyst", "research analyst expert in distinguishing factual information from subjective opinions")
    ]
}

class DomainDetector:
    """Detect domain type using LLM context analysis"""
    
    def __init__(self, client=None):
        self.client = client
    
    def detect_domain(self, url: str, title: str = "", content: str = "") -> str:
        """Detect domain using LLM context analysis with fallback"""
        if not self.client:
            print("❌ No LLM client available, using keyword fallback")
            return self._keyword_fallback(url, title, content)
        
        if not (title or content):
            return 'GENERAL'
        
        return self._llm_context_analysis(url, title, content)
    
    def _llm_context_analysis(self, url: str, title: str, content: str) -> str:
        """Use LLM to analyze content context and determine domain"""
        try:
            # Use substantial content for better context (up to 1500 chars)
            content_sample = content[:1500] if content else ""
            
            prompt = f"""Analyze this article's content and context to determine which domain/sector it belongs to. Focus on the MAIN TOPIC and PRIMARY SUBJECT MATTER.

URL: {url}
Title: {title}
Content: {content_sample}

Available domains:
1. LIFESTYLE - Food, restaurants, brands, consumer products, fashion, travel, shopping, daily life, product collaborations
2. CONFLICT - War, military operations, armed conflicts, terrorism, violence, battles (NOT metaphorical uses like "trade war")
3. POLITICS - Elections, government affairs, political campaigns, policy-making, governance, political parties
4. ENVIRONMENT - Climate change, pollution, conservation, environmental protection, sustainability, deforestation
5. HEALTH - Medical topics, diseases, healthcare systems, treatments, public health, medicine
6. TECHNOLOGY - Tech industry, software, AI, gadgets, innovation, tech companies, computing
7. FINANCE - Financial markets, economy, banking, investments, business economics, stocks
8. SPORTS - Athletic events, sports competitions, teams, games, tournaments, athletes
9. ENTERTAINMENT - Movies, TV shows, celebrities, music, Hollywood, entertainment industry
10. SCIENCE - Scientific research, studies, discoveries, academic research, experiments
11. LEGAL - Court cases, lawsuits, legal proceedings, judicial matters, law enforcement
12. NEWS - General breaking news that doesn't fit other specific categories
13. GENERAL - Other topics not fitting any specific domain

CRITICAL RULES:
- Food/restaurant collaborations (like KFC + Greggs) = LIFESTYLE
- Amazon deforestation = ENVIRONMENT (not NEWS)
- Sports rivalries/competitions = SPORTS (not CONFLICT)
- Business competition/"trade wars" = FINANCE or TECHNOLOGY (not CONFLICT)
- Product launches = TECHNOLOGY (tech) or LIFESTYLE (consumer goods)
- Celebrity news = ENTERTAINMENT
- Political scandals = POLITICS
- Court rulings = LEGAL

EXAMPLES:
- "KFC and Greggs collaboration" → LIFESTYLE
- "Amazon deforestation threatens wildlife" → ENVIRONMENT  
- "Manchester United vs Arsenal clash" → SPORTS
- "Apple vs Samsung patent war" → TECHNOLOGY
- "Ukraine missile strikes" → CONFLICT
- "Presidential election campaign" → POLITICS

Read the ENTIRE content carefully. Respond with ONLY the domain name:"""

            response = self.client.generate_content(prompt)
            detected_domain = response.strip().upper()
            
            # Validate the response
            valid_domains = ['LIFESTYLE', 'CONFLICT', 'POLITICS', 'ENVIRONMENT', 'HEALTH', 
                           'TECHNOLOGY', 'FINANCE', 'SPORTS', 'ENTERTAINMENT', 'SCIENCE', 
                           'LEGAL', 'NEWS', 'GENERAL']
            
            if detected_domain in valid_domains:
                print(f"🤖 LLM context analysis detected: {detected_domain}")
                return detected_domain
            else:
                print(f"❌ LLM returned invalid domain '{detected_domain}', using fallback")
                return self._keyword_fallback(url, title, content)
                
        except Exception as e:
            print(f"❌ LLM context analysis failed: {e}, using fallback")
            return self._keyword_fallback(url, title, content)
    
    def _keyword_fallback(self, url: str, title: str, content: str) -> str:
        """Simple keyword-based fallback when LLM fails"""
        if not (title or content):
            return 'GENERAL'
            
        text = (title + " " + content).lower()
        
        # Parse URL for domain indicators
        parsed_url = urlparse(url.lower()) if url else None
        domain = parsed_url.netloc.lower() if parsed_url else ""
        path = parsed_url.path.lower() if parsed_url else ""
        # Basic keyword detection for fallback
        if any(word in text for word in ['food', 'restaurant', 'brand', 'kfc', 'greggs', 'menu', 'collaboration']):
            return 'LIFESTYLE'
        elif any(word in text for word in ['deforestation', 'climate', 'environment', 'amazon rainforest', 'pollution']):
            return 'ENVIRONMENT'
        elif any(word in text for word in ['missile', 'attack', 'war', 'military', 'conflict']) and not any(word in text for word in ['trade war', 'price war', 'sports']):
            return 'CONFLICT'
        elif any(word in text for word in ['iphone', 'tech', 'software', 'ai', 'apple', 'google', 'technology']):
            return 'TECHNOLOGY'
        elif any(word in text for word in ['election', 'government', 'political', 'president', 'politics']):
            return 'POLITICS'
        elif any(word in text for word in ['football', 'basketball', 'sports', 'team', 'game', 'match']):
            return 'SPORTS'
        
        # News domain fallback
        if any(keyword in domain for keyword in ['bbc', 'cnn', 'npr', 'nytimes', 'washingtonpost', 'guardian']):
            return 'NEWS'
        
        return 'GENERAL'

@dataclass
class AnalysisResult:
    agent_name: str
    classification: str  # FACT, OPINION, or MIXED
    confidence: float    # 0.0 to 1.0
    reasoning: str
    evidence: List[str]
    key_phrases: List[str]
    sources: List[Dict[str, str]]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ConsensusResult:
    final_classification: str
    confidence: float
    agent_results: List[AnalysisResult]
    consensus_reasoning: str
    evidence_summary: List[str]
    sources_summary: List[Dict[str, str]]
    
    def to_dict(self):
        return {
            'final_classification': self.final_classification,
            'confidence': self.confidence,
            'agent_results': [agent.to_dict() for agent in self.agent_results],
            'consensus_reasoning': self.consensus_reasoning,
            'evidence_summary': self.evidence_summary,
            'sources_summary': self.sources_summary
        }

class CleanGeminiClient:
    """Simple Gemini client using official SDK"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Model equipped for search
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            tools=['google_search_retrieval']
        )
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else ""
        except Exception as e:
            raise Exception(f"API Error: {e}")

class CitationVerifier:
    """Verify citation validity and relevance using LLM"""
    
    def __init__(self, client: CleanGeminiClient):
        self.client = client
    
    def verify_citations(self, fact_text: str, citations: List[Dict[str, str]], domain: str = "GENERAL") -> List[Dict[str, str]]:
        """Verify if citations are valid and relevant to the fact"""
        if not citations:
            return []
        
        verified_citations = []
        
        for citation in citations:
            if self._verify_single_citation(fact_text, citation, domain):
                verified_citations.append(citation)
            else:
                print(f"❌ Citation verification failed for: {citation.get('title', 'Unknown title')}")
        
        return verified_citations
    
    def _verify_single_citation(self, fact_text: str, citation: Dict[str, str], domain: str) -> bool:
        """Verify a single citation using LLM and URL accessibility check"""
        try:
            title = citation.get('title', '')
            url = citation.get('url', '')
            
            if not title or not url:
                return False
            
            # First, check URL accessibility
            if not self._check_url_accessibility(url):
                print(f"❌ Citation rejected: {title} (Reason: URL_NOT_ACCESSIBLE)")
                return False
            
            # Enhanced verification prompt with URL accessibility confirmation
            prompt = f"""Verify if this citation is valid and relevant for the given fact claim.

FACT CLAIM: {fact_text[:300]}

CITATION TO VERIFY:
Title: {title}
URL: {url}

VERIFICATION CRITERIA:
1. URL VALIDITY: Does the URL look like a real, specific news article URL?
   - Valid examples: "https://www.bbc.co.uk/news/world-europe-67845123", "https://www.reuters.com/world/europe/ukraine-reports-2024/"
   - Invalid examples: "bbc.com", "example.com", generic domains without specific article paths
   - NOTE: URL accessibility has been pre-verified

2. TITLE RELEVANCE: Does the article title directly relate to the fact claim?
   - The title should contain keywords or concepts that match the fact
   - Should be about the same topic, event, or subject matter

3. SOURCE CREDIBILITY: Is this from a credible news source?
   - Credible: BBC, Reuters, CNN, Guardian, Associated Press, NPR, Washington Post, NYT, Sky News, Al Jazeera, official government sites
   - Check if the domain matches known credible sources

4. CONTEXT ALIGNMENT: For domain {domain}, does this source make sense?
   - POLITICS/CONFLICT: Should be from major news outlets or government sources
   - HEALTH: Should be from medical journals, health organizations, or health reporters
   - TECHNOLOGY: Should be from tech publications or major news tech sections
   - LIFESTYLE: Should be from lifestyle publications or major news lifestyle sections

5. URL REALISM: Does the URL structure look realistic for the claimed source?
   - Check if the domain matches the source name
   - Verify the URL path looks like a real article path

RESPOND WITH ONLY ONE WORD:
- "VALID" if the citation passes all criteria
- "INVALID" if it fails any criteria

Response:"""

            response = self.client.generate_content(prompt)
            result = response.strip().upper()
            
            is_valid = result == "VALID"
            
            if is_valid:
                print(f"✅ Citation verified: {title}")
            else:
                print(f"❌ Citation rejected: {title} (Reason: {result})")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ Citation verification error: {e}")
            return False

    def _check_url_accessibility(self, url: str) -> bool:
        """Check if URL is accessible with both HEAD and GET requests"""
        try:
            import requests
            from urllib.parse import urlparse
            
            # Basic URL format validation
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                print(f"🔍 URL format invalid: {url}")
                return False
            
            # Try HEAD request first (faster)
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                # Only accept 200 as truly accessible for HEAD requests
                if response.status_code == 200:
                    return True
                elif response.status_code == 405:  # Method not allowed, try GET
                    pass  # Continue to GET request
                else:
                    print(f"🔍 URL check failed: {url} (HEAD Status: {response.status_code})")
                    return False
            except requests.RequestException:
                pass  # Continue to GET request if HEAD fails
            
            # Try GET request as fallback or if HEAD returned 405
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                # Be more strict - only 200 is acceptable
                if response.status_code == 200:
                    # Additional check: ensure we got actual content, not just a redirect page
                    if len(response.content) > 1000:  # Must have substantial content
                        # Extra validation: check if it's not an error page
                        content_text = response.text.lower()
                        error_indicators = ['404', 'not found', 'page not found', 'error', 'access denied', 
                                          'forbidden', 'unauthorized', 'temporarily unavailable',
                                          'this page does not exist', 'page cannot be found']
                        
                        # If content contains error indicators, reject it
                        if any(indicator in content_text for indicator in error_indicators):
                            print(f"🔍 URL check failed: {url} (Content indicates error page)")
                            return False
                        
                        return True
                    else:
                        print(f"🔍 URL check failed: {url} (Content too short, likely error page)")
                        return False
                else:
                    print(f"🔍 URL check failed: {url} (GET Status: {response.status_code})")
                    return False
            except requests.RequestException as e:
                print(f"🔍 URL accessibility check failed for {url}: {e}")
                return False
            
        except Exception as e:
            print(f"🔍 URL accessibility check failed for {url}: {e}")
            return False  # If we can't check, assume it's not accessible

class Agent:
    """Base agent class"""
    
    def __init__(self, client: CleanGeminiClient, name: str, role: str):
        self.client = client
        self.agent_name = name
        self.role = role
    
    def analyze(self, content: str) -> AnalysisResult:
        """Analyze content with web grounding"""
        prompt = f"""As a {self.role}, analyze this text and classify it as either FACT or OPINION.

Use web search to verify any factual claims and provide SPECIFIC, DIRECT source citations.

Text: {content[:500]}

CLASSIFICATION RULES:
- FACT: Verifiable information that can be confirmed through web search, documented data, or objective evidence. Examples: dates, names, locations, statistics, documented events, scientific measurements.
- OPINION: Subjective statements, personal views, interpretations, predictions, evaluations, or value judgments. Examples: "good", "bad", "should", "might", personal beliefs, preferences.

CRITICAL RULE: If you cannot find right/verifiable citations for a claim, it should AUTOMATICALLY be classified as OPINION, regardless of how factual it appears.

IMPORTANT: You must choose either FACT or OPINION. Do not use MIXED. If a statement contains both, classify based on the primary intent.

FOR FACTS: You MUST provide SPECIFIC, DIRECT source URLs that verify the factual claims. If you cannot find proper citations, classify as OPINION instead. 

SOURCE REQUIREMENTS:
- Use COMPLETE, SPECIFIC URLs that link directly to the actual article/page (not just domain names)
- For POLITICS, CONFLICT, WAR topics: Provide 3-4 different credible sources
- For other topics: Provide 1-3 relevant sources
- URLs must be real, specific links like: "https://www.bbc.co.uk/news/world-europe-67845123", "https://www.reuters.com/world/europe/ukraine-reports-russian-attacks-2024-01-15/", "https://edition.cnn.com/2024/01/15/politics/ukraine-aid-package/index.html"

CREDIBLE SOURCES: BBC News, Reuters, Associated Press, CNN, Guardian, Washington Post, New York Times, Sky News, Al Jazeera, NPR, official government websites, academic institutions

Respond with ONLY valid JSON. No other text before or after:

{{
    "classification": "FACT",
    "confidence": 0.9,
    "reasoning": "Brief explanation with web verification from multiple sources",
    "evidence": ["key evidence verified across sources"],
    "key_phrases": ["important phrases from the text"],
    "sources": [
        {{"title": "BBC News - Full Specific Article Title", "url": "https://www.bbc.co.uk/news/world-europe-67845123"}}, 
        {{"title": "Reuters - Complete Article Headline", "url": "https://www.reuters.com/world/europe/specific-story-2024-01-15/"}},
        {{"title": "Associated Press - Detailed Coverage", "url": "https://apnews.com/article/specific-article-id-12345"}}
    ]
}}

Make sure all strings are properly quoted and there are no trailing commas. For FACTS, sources array must contain COMPLETE, SPECIFIC URLs to actual articles."""

        try:
            response = self.client.generate_content(prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"Error in {self.agent_name}: {e}")
            return AnalysisResult(
                agent_name=self.agent_name,
                classification="MIXED",
                confidence=0.5,
                reasoning=f"Error occurred: {e}",
                evidence=[],
                key_phrases=[],
                sources=[]
            )
    
    def _parse_response(self, response: str) -> AnalysisResult:
        """Parse JSON response from agent"""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Try to find JSON block within the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                
                # Clean up common JSON formatting issues
                json_str = json_str.replace('\n', ' ')  # Remove newlines
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                
                data = json.loads(json_str)
            else:
                # If no valid JSON structure found, create a default structure
                print(f"No valid JSON found in response: {response[:100]}...")
                data = {
                    'classification': 'MIXED',
                    'confidence': 0.5,
                    'reasoning': 'Could not parse response',
                    'evidence': [],
                    'key_phrases': [],
                    'sources': []
                }
            
            return AnalysisResult(
                agent_name=self.agent_name,
                classification=data.get('classification', 'MIXED'),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                evidence=data.get('evidence', []),
                key_phrases=data.get('key_phrases', []),
                sources=data.get('sources', [])
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Parse error in {self.agent_name}: {e}")
            print(f"Response content: {response[:200]}...")
            return AnalysisResult(
                agent_name=self.agent_name,
                classification="MIXED",
                confidence=0.5,
                reasoning=f"Parse error: {e}",
                evidence=[],
                key_phrases=[],
                sources=[]
            )

class ConsensusBuilder:
    """Build consensus from multiple agent results"""
    
    def build_consensus(self, results: List[AnalysisResult]) -> ConsensusResult:
        """Build consensus from agent results with proper classification logic"""
        if not results:
            return ConsensusResult(
                final_classification="INCONCLUSIVE",
                confidence=0.0,
                agent_results=[],
                consensus_reasoning="No results to analyze",
                evidence_summary=[],
                sources_summary=[]
            )
        
        # Count classifications
        classifications = [r.classification for r in results]
        fact_count = classifications.count('FACT')
        opinion_count = classifications.count('OPINION')
        mixed_count = classifications.count('MIXED')
        
        total_agents = len(results)
        
        # Determine final classification based on majority
        if fact_count > opinion_count and fact_count > mixed_count:
            final_classification = 'FACT'
            agreeing_results = [r for r in results if r.classification == 'FACT']
        elif opinion_count > fact_count and opinion_count > mixed_count:
            final_classification = 'OPINION'
            agreeing_results = [r for r in results if r.classification == 'OPINION']
        elif fact_count == opinion_count and fact_count > mixed_count:
            # Equal facts and opinions - tie situation
            final_classification = 'CONTESTED'  # Neither clearly fact nor opinion
            agreeing_results = results  # Use all results for confidence calculation
        elif mixed_count >= fact_count and mixed_count >= opinion_count:
            final_classification = 'MIXED'
            agreeing_results = [r for r in results if r.classification == 'MIXED']
        else:
            final_classification = 'INCONCLUSIVE'
            agreeing_results = results
        
        # Calculate confidence score
        if final_classification == 'CONTESTED':
            # For contested results, average all confidences but reduce overall confidence
            all_confidences = [r.confidence for r in results]
            base_confidence = sum(all_confidences) / len(all_confidences)
            confidence = base_confidence * 0.7  # Reduce confidence for contested results
        elif agreeing_results:
            # Average confidence of agreeing agents
            confidence = sum(r.confidence for r in agreeing_results) / len(agreeing_results)
            # Boost confidence based on consensus strength
            consensus_ratio = len(agreeing_results) / total_agents
            confidence = confidence * (0.5 + 0.5 * consensus_ratio)  # Scale between 50-100% of original
        else:
            confidence = 0.5
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        # Build consensus reasoning with vote breakdown
        reasoning_parts = []
        reasoning_parts.append(f"Vote breakdown: {fact_count} FACT, {opinion_count} OPINION, {mixed_count} MIXED out of {total_agents} agents")
        
        for result in results:
            reasoning_parts.append(f"{result.agent_name} ({result.classification}, {result.confidence:.2f}): {result.reasoning[:80]}...")
        
        consensus_reasoning = f"Final classification: {final_classification} | " + " | ".join(reasoning_parts)
        
        # Aggregate evidence
        evidence_summary = []
        for result in results:
            evidence_summary.extend(result.evidence)

        # Aggregate sources
        sources_summary = []
        seen_urls = set()
        for result in results:
            if hasattr(result, 'sources') and result.sources:
                for source in result.sources:
                    if source.get('url') and source['url'] not in seen_urls:
                        sources_summary.append(source)
                        seen_urls.add(source['url'])
        
        return ConsensusResult(
            final_classification=final_classification,
            confidence=confidence,
            agent_results=results,
            consensus_reasoning=consensus_reasoning,
            evidence_summary=list(set(evidence_summary)),  # Remove duplicates
            sources_summary=sources_summary
        )

class SimpleFormatter:
    """Simple formatter for clean analysis results"""
    
    def format_results(self, results, title="", domain=""):
        """Format results in a simple way - DISABLED for bias research interface"""
        return ""

class CleanAnalysisSystem:
    """Main analysis system with domain-specific agents"""
    
    def __init__(self):
        self.client = CleanGeminiClient()
        self.consensus_builder = ConsensusBuilder()
        self.scraper = NewsContentScraper()
        # Pass the LLM client to the domain detector for intelligent detection
        self.domain_detector = DomainDetector(self.client)
        # Add Gemini citation service with Google Search grounding
        self.citation_service = GeminiCitationService()
        # Add integrated citation validator for comprehensive URL validation
        self.citation_validator = IntegratedCitationValidator()
        self.last_analysis_data = None
        self.formatter = SimpleFormatter()
        self.current_domain = 'GENERAL'
        
        # Initialize with default GENERAL agents
        self.agents = self._create_agents_for_domain('GENERAL')
    
    def _extract_source_name_from_url(self, url: str) -> str:
        """Extract source name from URL for sentence attribution"""
        if not url:
            return "Unknown Source"
        
        from urllib.parse import urlparse
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Map common domains to readable source names
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
            'cbsnews.com': 'CBS News',
            'independent.co.uk': 'The Independent',
            'dailymail.co.uk': 'Daily Mail',
            'telegraph.co.uk': 'The Telegraph',
            'usatoday.com': 'USA Today',
            'wsj.com': 'The Wall Street Journal',
            'bloomberg.com': 'Bloomberg',
            'politico.com': 'Politico',
            'huffpost.com': 'HuffPost'
        }
        
        # Check for exact domain matches
        if domain in source_mapping:
            return source_mapping[domain]
        
        # Fallback: capitalize domain name and remove TLD
        if '.' in domain:
            base_domain = domain.split('.')[0]
            return base_domain.capitalize()
        
        return "News Source"
    
    def _create_agents_for_domain(self, domain: str) -> List[Agent]:
        """Create specialized agents based on domain"""
        roles = DOMAIN_ROLES.get(domain, DOMAIN_ROLES['GENERAL'])
        agents = []
        
        for name, role_description in roles:
            agent = Agent(self.client, name, role_description)
            agents.append(agent)
        
        return agents
    
    def _update_agents_for_domain(self, domain: str):
        """Update agents based on detected domain"""
        if domain != self.current_domain:
            print(f"Switching from {self.current_domain} to {domain} domain specialists...")
            self.current_domain = domain
            self.agents = self._create_agents_for_domain(domain)
            print(f"Loaded {len(self.agents)} {domain} specialists: {[agent.agent_name for agent in self.agents]}")
    
    def analyze_single_content(self, content: str, domain: str = 'GENERAL') -> ConsensusResult:
        """Analyze content with domain-specific agents"""
        self._update_agents_for_domain(domain)
        
        print(f"Analyzing content with {len(self.agents)} {domain} specialists...")
        
        results = []
        for i, agent in enumerate(self.agents, 1):
            print(f"  Agent {i}/{len(self.agents)}: {agent.agent_name}...")
            result = agent.analyze(content)
            results.append(result)
            time.sleep(1)  # Rate limiting
        
        consensus = self.consensus_builder.build_consensus(results)
        return consensus
    
    def analyze_url(self, url: str) -> str:
        """Analyze URL with scraping, domain detection, and consensus"""
        print(f"Scraping content from: {url}")
        
        scraped_data = self.scraper.scrape_url(url)
        if not scraped_data or not scraped_data.get('content'):
            return "ERROR: Failed to scrape content from URL"
        
        print(f"Scraped {len(scraped_data['content'])} characters")
        print(f"Title: {scraped_data.get('title', 'N/A')}")
        
        # Add URL to scraped data for source tracking
        scraped_data['url'] = url
        
        # Detect domain and update agents
        detected_domain = self.domain_detector.detect_domain(
            url,
            scraped_data.get('title', ''),
            scraped_data.get('content', '')
        )
        print(f"Detected domain: {detected_domain}")
        
        return self._analyze_content(scraped_data, detected_domain)
    
    def analyze_text(self, text: str) -> str:
        """Analyze text content with GENERAL domain"""
        print(f"Analyzing provided text ({len(text)} characters)")
        
        data = {'content': text, 'title': 'User Provided Text'}
        return self._analyze_content(data, 'GENERAL')
    
    def generate_summary(self, content: str, title: str) -> str:
        """Generate a concise summary of the article content"""
        try:
            prompt = f"""
            Please provide a concise, objective summary of this news article in 2-3 sentences.
            Focus on the key facts and main points without adding opinions or interpretations.
            
            Title: {title}
            
            Content: {content[:2000]}...
            
            Summary:
            """
            
            response = self.client.generate_content(prompt)
            return response.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def format_content_to_markdown(self, content: str, title: str) -> str:
        """Format article content to clean, readable markdown"""
        try:
            prompt = f"""
            Convert the following article content into clean, well-formatted markdown.
            Follow these guidelines STRICTLY:
            1. COMPLETELY REMOVE any photo/image/video descriptions, captions, or credits
            2. REMOVE any lines mentioning "Photograph:", "Image:", "Video:", "Getty Images", "AFP", "Reuters", etc.
            3. REMOVE navigation text, social media links, footer content, ads, or promotional material
            4. REMOVE any audio/video/multimedia references
            5. Keep ONLY the main article text content that contains actual news information
            6. Format with proper markdown headers, paragraphs, and structure
            7. Make it easy to read and well-organized
            8. Remove promotional language and keep factual information
            
            Title: {title}
            
            Raw Content:
            {content}
            
            Clean Markdown Version (NO IMAGE/VIDEO/PHOTO references):
            """
            
            response = self.client.generate_content(prompt)
            formatted_content = response.strip()
            
            # Additional post-processing to ensure no media references
            lines = formatted_content.split('\n')
            clean_lines = []
            
            for line in lines:
                line_lower = line.lower()
                # Skip lines that contain media references
                if any(word in line_lower for word in [
                    'photograph:', 'image:', 'video:', 'getty images', 'afp', 'reuters',
                    'view image', 'fullscreen', 'screenshot', 'photo by', 'credit:',
                    'shutterstock', 'associated press', 'ap photo', 'picture:'
                ]):
                    continue
                # Skip very short lines that might be captions
                if len(line.strip()) < 20 and any(word in line_lower for word in ['photo', 'image', 'video']):
                    continue
                clean_lines.append(line)
            
            formatted_content = '\n'.join(clean_lines)
            
            # Ensure we have a proper title
            if not formatted_content.startswith('#'):
                formatted_content = f"# {title}\n\n{formatted_content}"
            
            return formatted_content
        except Exception as e:
            return f"# {title}\n\n{content[:1000]}...\n\n*Error formatting content: {str(e)}*"
    
    def _analyze_content(self, data: Dict, domain: str = 'GENERAL') -> str:
        """Analyze content and store data for later access"""
        sentences = self._split_sentences(data['content'])
        print(f"Found {len(sentences)} sentences to analyze")
        
        if not sentences:
            return "ERROR: No sentences found to analyze"
        
        consensus_results = []
        analysis_limit = min(len(sentences), 5)  # Analyze up to 5 sentences for research
        
        for i, sentence in enumerate(sentences[:analysis_limit], 1):
            print(f"   Analyzing sentence {i}/{analysis_limit}...")
            consensus = self.analyze_single_content(sentence, domain)
            consensus_results.append(consensus)
            time.sleep(1)  # Rate limiting between sentences
        
        # Store analysis data for later access
        # Convert ConsensusResult objects to dictionaries for compatibility
        formatted_results = []
        for i, consensus in enumerate(consensus_results):
            sentence_text = sentences[i] if i < len(sentences) else f"Result {i+1}"
            
            # Extract citation information from sources if this is a FACT
            citations = []
            attributed_sentence = sentence_text  # Default to original sentence
            
            # Create source-attributed sentence based on the original URL
            source_url = data.get('url', '')
            if source_url:
                source_name = self._extract_source_name_from_url(source_url)
                attributed_sentence = f"{source_name} reported {sentence_text}"
                print(f"📝 Source-attributed sentence: {attributed_sentence[:100]}...")
            
            if hasattr(consensus, 'final_classification') and consensus.final_classification == 'FACT':
                print(f"🔍 Getting verified citations for FACT using Gemini with Google Search...")
                
                # Use Gemini citation service to find and verify citations
                verified_citations = self.citation_service.get_citations_for_sentence(
                    sentence_text, domain
                )
                
                if verified_citations:
                    print(f"✅ Found {len(verified_citations)} verified citations with Google Search")
                    
                    # Convert VerifiedCitation objects to dictionary format for compatibility
                    citations = []
                    for vc in verified_citations:
                        citations.append({
                            'url': vc.url,
                            'title': vc.title,
                            'snippet': vc.snippet,
                            'domain': vc.domain,
                            'verification_score': vc.verification_score,
                            'reasoning': vc.reasoning
                        })
                    
                    # For critical domains (POLITICS, CONFLICT), show multiple sources
                    # For other domains, show primary source but keep others available
                    critical_domains = ['POLITICS', 'CONFLICT', 'WAR', 'LEGAL']
                    if domain in critical_domains:
                        # Show up to 4 verified sources for critical domains
                        citations = citations[:4]
                    else:
                        # Show up to 2 verified sources for other domains
                        citations = citations[:2]
                        
                else:
                    print(f"⚠️  No verified citations found for fact using Gemini, automatically reclassifying as OPINION")
                    # If no valid citations, automatically classify as OPINION instead of FACT
                    consensus.final_classification = 'OPINION'
                    consensus.confidence = min(consensus.confidence * 0.8, 0.9)  # Slightly reduce confidence but keep reasonable
                    consensus.consensus_reasoning = f"{consensus.consensus_reasoning} However, no verifiable citations were found using Google Search grounding, so this is reclassified as OPINION per verification standards."
            
            # Create a result object that matches what the frontend expects
            formatted_result = {
                'sentence': attributed_sentence,  # Use source-attributed sentence for facts
                'original_sentence': sentence_text,  # Keep original for reference
                'source_url': source_url,  # Add source URL for reference
                'source_name': self._extract_source_name_from_url(source_url) if source_url else 'Unknown Source',  # Add source name
                'final_classification': consensus.final_classification if hasattr(consensus, 'final_classification') else 'MIXED',
                'consensus_confidence': consensus.confidence if hasattr(consensus, 'confidence') else 0.5,
                'citation': citations[0] if citations else None,  # Primary citation for backward compatibility
                'citations': citations,  # Multiple citations for enhanced display
                'consensus_reasoning': consensus.consensus_reasoning if hasattr(consensus, 'consensus_reasoning') else 'Analysis completed'
            }
            formatted_results.append(formatted_result)
        
        # Store initial analysis data
        initial_analysis_data = {
            'content': data['content'],
            'results': formatted_results,  # Use formatted results
            'consensus_result': {
                'sources_summary': self._extract_sources_from_results(consensus_results)
            },
            'domain': domain,  # Store the detected domain
            'title': data.get('title', ''),
            'url': data.get('url', '')
        }
        
        # Apply comprehensive URL validation to filter facts with working sources
        print(f"🔧 Applying comprehensive URL validation to filter facts...")
        self.last_analysis_data = self.citation_validator.get_verified_facts_with_working_sources(initial_analysis_data)
        
        # Format output similar to the MultiRolePromptingSystem
        return self._format_results(consensus_results, data.get('title', ''), domain)
    
    def _extract_sources_from_results(self, consensus_results):
        """Extract sources from consensus results"""
        sources = []
        seen_urls = set()
        
        for result in consensus_results:
            # Access sources_summary attribute correctly from ConsensusResult
            if hasattr(result, 'sources_summary') and result.sources_summary:
                for source in result.sources_summary:
                    if isinstance(source, dict) and source.get('url') and source['url'] not in seen_urls:
                        sources.append(source)
                        seen_urls.add(source['url'])
            # Also check agent_results for individual agent sources
            elif hasattr(result, 'agent_results'):
                for agent_result in result.agent_results:
                    if hasattr(agent_result, 'sources') and agent_result.sources:
                        for source in agent_result.sources:
                            if isinstance(source, dict) and source.get('url') and source['url'] not in seen_urls:
                                sources.append(source)
                                seen_urls.add(source['url'])
        
        return sources
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences and filter out media references and metadata"""
        sentences = re.split(r'[.!?]+', text)
        
        # Filter sentences
        filtered_sentences = []
        for s in sentences:
            s = s.strip()
            if len(s) <= 10:  # Too short
                continue
                
            s_lower = s.lower()
            
            # Skip sentences with media references
            if any(word in s_lower for word in [
                'photograph:', 'image:', 'video:', 'getty images', 'afp', 'reuters',
                'view image', 'fullscreen', 'screenshot', 'photo by', 'credit:',
                'shutterstock', 'associated press', 'ap photo', 'picture:',
                'images/view image', 'photograph', 'photo credit'
            ]):
                print(f"🚫 Filtered media reference: {s[:100]}...")
                continue
            
            # Skip timestamp and metadata sentences
            if any(pattern in s_lower for pattern in [
                'bst', 'gmt', 'published on', 'last modified', 'first published',
                'updated on', 'posted on', 'edited on', ':30', ':45', ':00', ':15',
                'am', 'pm', 'sharelikecomment', 'share', 'like', 'comment',
                'follow us', 'subscribe', 'newsletter', 'email alerts'
            ]):
                print(f"🚫 Filtered timestamp/metadata: {s[:100]}...")
                continue
                
            # Skip sentences that are mostly numbers/dates/times
            if re.match(r'^[\d\s:/-]+$', s) or len(re.findall(r'\d', s)) > len(s) * 0.5:
                print(f"🚫 Filtered numeric/date content: {s[:100]}...")
                continue
                
            # Skip very short sentences that might be captions or metadata
            if len(s) < 30 and any(word in s_lower for word in [
                'photo', 'image', 'video', 'source:', 'by:', 'via:', 'read more',
                'click here', 'see also', 'related:', 'tags:', 'category:'
            ]):
                print(f"🚫 Filtered short metadata: {s}")
                continue
                
            # Skip navigation and social media text
            if any(phrase in s_lower for phrase in [
                'explore more', 'reuse this content', 'share on', 'follow on',
                'sign up', 'log in', 'register', 'terms of service', 'privacy policy'
            ]):
                print(f"🚫 Filtered navigation/social: {s[:100]}...")
                continue
                
            filtered_sentences.append(s)
        
        print(f"Debug: Original sentences: {len(sentences)}, Filtered: {len(filtered_sentences)}")
        print(f"Debug: First 3 filtered sentences: {filtered_sentences[:3] if filtered_sentences else 'None'}")
        return filtered_sentences
    
    def _format_results(self, consensus_results: List[ConsensusResult], title: str = "", domain: str = "GENERAL") -> str:
        """Format analysis results - return empty for bias research to avoid cluttering interface"""
        # Return empty string to completely remove consensus summary from display
        return ""
        
        return "\n".join(output)
    
    def _format_items(self, items: List[ConsensusResult]) -> List[str]:
        """Format consensus items"""
        lines = []
        for i, item in enumerate(items, 1):
            confidence = item.confidence
            conf_indicator = "[HIGH]" if confidence > 0.8 else "[MED]" if confidence > 0.6 else "[LOW]"
            
            # Get the actual sentence content from consensus reasoning or first agent result
            sentence = "No content"
            if hasattr(item, 'agent_results') and item.agent_results:
                # Try to get content from the first agent result
                sentence = f"{item.final_classification} - {item.consensus_reasoning[:50]}..."
            elif hasattr(item, 'consensus_reasoning'):
                sentence = item.consensus_reasoning[:50] + "..."
            
            lines.append(f"{i}. {conf_indicator} {sentence}")
            lines.append("")
        
        return lines
    
    def get_facts_section_with_verified_sources(self) -> str:
        """Generate Facts section with only comprehensively verified sources"""
        if not self.last_analysis_data:
            return "No analysis data available. Please run an analysis first."
        
        return self.citation_validator.generate_facts_section_with_verified_sources(self.last_analysis_data)
    
    def get_verification_summary(self) -> dict:
        """Get summary of URL verification results"""
        if not self.last_analysis_data:
            return {"error": "No analysis data available"}
        
        return self.last_analysis_data.get('verification_summary', {})