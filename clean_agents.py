"""
Clean Fact vs Opinion Analysis System using Google Generative AI SDK
Simple 4-agent system without unnecessary complexity
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

class Agent:
    """Base agent class"""
    
    def __init__(self, client: CleanGeminiClient, name: str, role: str):
        self.client = client
        self.agent_name = name
        self.role = role
    
    def analyze(self, content: str) -> AnalysisResult:
        """Analyze content with web grounding"""
        prompt = f"""As a {self.role}, analyze this text and classify it as either FACT or OPINION.

Use web search to verify any factual claims and provide citations when possible.

Text: {content[:500]}

CLASSIFICATION RULES:
- FACT: Verifiable information that can be confirmed through web search, documented data, or objective evidence. Examples: dates, names, locations, statistics, documented events, scientific measurements.
- OPINION: Subjective statements, personal views, interpretations, predictions, evaluations, or value judgments. Examples: "good", "bad", "should", "might", personal beliefs, preferences.

IMPORTANT: You must choose either FACT or OPINION. Do not use MIXED. If a statement contains both, classify based on the primary intent.

Respond with ONLY valid JSON. No other text before or after:

{{
    "classification": "FACT",
    "confidence": 0.9,
    "reasoning": "Brief explanation with web verification if applicable",
    "evidence": ["key evidence with sources if available"],
    "key_phrases": ["important phrases from the text"],
    "sources": [{{"title": "Source Name", "url": "https://example.com"}}]
}}

Make sure all strings are properly quoted and there are no trailing commas."""

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
        """Format results in a simple way"""
        if not results:
            return "No results to format"
        
        output = []
        output.append(f"Analysis Results for: {title}")
        output.append(f"Domain: {domain}")
        output.append(f"Total items: {len(results)}")
        
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {str(result)[:100]}...")
        
        return "\n".join(output)

class CleanAnalysisSystem:
    """Main analysis system with domain-specific agents"""
    
    def __init__(self):
        self.client = CleanGeminiClient()
        self.consensus_builder = ConsensusBuilder()
        self.scraper = NewsContentScraper()
        # Pass the LLM client to the domain detector for intelligent detection
        self.domain_detector = DomainDetector(self.client)
        self.last_analysis_data = None
        self.formatter = SimpleFormatter()
        self.current_domain = 'GENERAL'
        
        # Initialize with default GENERAL agents
        self.agents = self._create_agents_for_domain('GENERAL')
    
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
    
    def _analyze_content(self, data: Dict, domain: str = 'GENERAL') -> str:
        """Analyze content and store data for later access"""
        sentences = self._split_sentences(data['content'])
        print(f"Found {len(sentences)} sentences to analyze")
        
        if not sentences:
            return "ERROR: No sentences found to analyze"
        
        consensus_results = []
        analysis_limit = min(len(sentences), 2)  # Limit for API costs
        
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
            # Create a result object that matches what the frontend expects
            formatted_result = {
                'sentence': sentence_text,
                'final_classification': consensus.final_classification if hasattr(consensus, 'final_classification') else 'MIXED',
                'consensus_confidence': consensus.confidence if hasattr(consensus, 'confidence') else 0.5,
                'citation': None,  # Can be added later when we have source tracking
                'consensus_reasoning': consensus.consensus_reasoning if hasattr(consensus, 'consensus_reasoning') else 'Analysis completed'
            }
            formatted_results.append(formatted_result)
        
        self.last_analysis_data = {
            'content': data['content'],
            'results': formatted_results,  # Use formatted results
            'consensus_result': {
                'sources_summary': self._extract_sources_from_results(consensus_results)
            },
            'domain': domain,  # Store the detected domain
            'title': data.get('title', ''),
            'url': data.get('url', '')
        }
        
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
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]  # Reduced from 15 to 5
        print(f"Debug: Split sentences: {sentences}")  # Debug output
        return sentences
    
    def _format_results(self, consensus_results: List[ConsensusResult], title: str = "", domain: str = "GENERAL") -> str:
        """Format analysis results with domain information"""
        output = []
        
        # Header with domain information
        output.append("=" * 80)
        output.append(f"DOMAIN-SPECIFIC FACT-CHECKING ANALYSIS")
        output.append(f"Domain: {domain}")
        if title:
            output.append(f"Title: {title}")
        output.append(f"Specialists: {[agent.agent_name for agent in self.agents]}")
        output.append("=" * 80)
        
        # Separate facts and opinions - these are ConsensusResult objects
        facts = [r for r in consensus_results if r.final_classification == 'FACT']
        opinions = [r for r in consensus_results if r.final_classification == 'OPINION']
        mixed = [r for r in consensus_results if r.final_classification == 'MIXED']
        
        # Metrics
        total_sentences = len(consensus_results)
        output.append(f"ANALYSIS METRICS:")
        output.append(f"   Total Sentences: {total_sentences} | Facts: {len(facts)} | Opinions: {len(opinions)} | Mixed: {len(mixed)}")
        output.append("")
        
        # Show actual content for debugging
        for i, result in enumerate(consensus_results):
            output.append(f"   Sentence {i+1}: {result.final_classification} (confidence: {result.confidence:.2f})")
        output.append("")
        
        # Column headers
        output.append(f"{'FACTS':<38} | {'OPINIONS':<38}")
        output.append("-" * 39 + "|" + "-" * 39)
        
        # Format items
        fact_lines = self._format_items(facts)
        opinion_lines = self._format_items(opinions)
        
        # Balance columns
        max_lines = max(len(fact_lines), len(opinion_lines))
        while len(fact_lines) < max_lines:
            fact_lines.append("")
        while len(opinion_lines) < max_lines:
            opinion_lines.append("")
        
        # Combine columns
        for fact_line, opinion_line in zip(fact_lines, opinion_lines):
            fact_part = fact_line[:38].ljust(38)
            opinion_part = opinion_line[:38].ljust(38)
            output.append(f"{fact_part} | {opinion_part}")
        
        output.append("=" * 80)
        
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