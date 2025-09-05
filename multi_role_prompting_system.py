import sys
import re
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from clean_agents import CleanGeminiClient
from scraper import NewsContentScraper

@dataclass
class ExpertAnalysis:
    expert_role: str
    classification: str
    confidence: float
    reasoning: str
    domain_expertise: str
    verification_method: str

@dataclass
class ConsensusResult:
    sentence: str
    final_classification: str
    consensus_confidence: float
    expert_analyses: List[ExpertAnalysis]
    consensus_reasoning: str
    agreement_level: str
    domain: str
    citation: Optional[Dict[str, str]] = None

class MultiRoleAnalyzer:
    def __init__(self):
        self.client = CleanGeminiClient()
        self.domain_experts = {
            'health': [
                {
                    'role': 'Medical Doctor and Clinical Researcher',
                    'expertise': 'MD with 20+ years clinical practice and medical research',
                    'focus': 'Clinical evidence, peer-reviewed studies, medical guidelines, FDA approvals'
                },
                {
                    'role': 'Healthcare Journalist and Medical Writer',
                    'expertise': 'Medical journalism with 15+ years covering health news',
                    'focus': 'Source verification, medical reporting standards, health communication'
                },
                {
                    'role': 'Public Health Expert and Epidemiologist',
                    'expertise': 'PhD in Public Health with epidemiological research background',
                    'focus': 'Population health data, disease surveillance, health statistics'
                }
            ],
            'politics': [
                {
                    'role': 'Social Media Domain Expert',
                    'expertise': '15+ years analyzing political discourse on social media platforms and digital communication',
                    'focus': 'Social media verification, viral content analysis, digital political communication patterns'
                },
                {
                    'role': 'Professor in Media Studies',
                    'expertise': 'PhD in Media Studies with 20+ years researching political media and communication',
                    'focus': 'Media literacy, political communication theory, news framing analysis'
                },
                {
                    'role': 'Political Journalist',
                    'expertise': '25+ years covering politics for major news organizations with fact-checking expertise',
                    'focus': 'Political reporting standards, source verification, government accountability'
                }
            ],
            'conflict': [
                {
                    'role': 'Social Media Analyst',
                    'expertise': '12+ years analyzing conflict-related social media content, disinformation, and war reporting',
                    'focus': 'Social media verification in conflict zones, propaganda detection, digital warfare analysis'
                },
                {
                    'role': 'News Journalist',
                    'expertise': '20+ years covering international conflicts, war zones, and crisis reporting',
                    'focus': 'Conflict journalism standards, war reporting ethics, crisis fact-checking'
                },
                {
                    'role': 'Linguist',
                    'expertise': 'PhD in Linguistics with specialization in conflict discourse analysis and propaganda language',
                    'focus': 'Language patterns in conflict reporting, propaganda linguistics, discourse analysis'
                }
            ],
            'sports': [
                {
                    'role': 'Former Professional Athlete and Sports Analyst',
                    'expertise': 'Former professional athlete with sports broadcasting experience',
                    'focus': 'Game statistics, performance data, athletic achievements, official records'
                },
                {
                    'role': 'Sports Journalist and Beat Reporter',
                    'expertise': '15+ years covering professional sports for major publications',
                    'focus': 'Sports reporting standards, statistical verification, league information'
                },
                {
                    'role': 'Sports Statistician and Performance Analyst',
                    'expertise': 'Sports analytics with statistical analysis and data science background',
                    'focus': 'Performance metrics, statistical analysis, data verification'
                }
            ],
            'economics': [
                {
                    'role': 'Senior Economic Analyst and Market Researcher',
                    'expertise': 'PhD in Economics with Wall Street and research experience',
                    'focus': 'Economic data, market analysis, financial reports, statistical indicators'
                },
                {
                    'role': 'Financial Journalist and Business Reporter',
                    'expertise': '20+ years covering financial markets and business news',
                    'focus': 'Financial reporting standards, market verification, business analysis'
                },
                {
                    'role': 'Central Bank Policy Expert and Monetary Analyst',
                    'expertise': 'Former Federal Reserve analyst with monetary policy expertise',
                    'focus': 'Monetary policy, central bank communications, economic indicators'
                }
            ],
            'technology': [
                {
                    'role': 'Technology Industry Veteran and CTO',
                    'expertise': 'Computer Science PhD with 20+ years in tech industry leadership',
                    'focus': 'Technical specifications, industry trends, product development'
                },
                {
                    'role': 'Technology Journalist and Industry Analyst',
                    'expertise': '15+ years covering technology sector for major tech publications',
                    'focus': 'Tech reporting standards, industry verification, product analysis'
                },
                {
                    'role': 'Cybersecurity Expert and Research Scientist',
                    'expertise': 'Cybersecurity research with academic and industry experience',
                    'focus': 'Security analysis, technical verification, research validation'
                }
            ],
            'environment': [
                {
                    'role': 'Climate Scientist and Environmental Researcher',
                    'expertise': 'PhD in Climate Science with IPCC report contribution experience',
                    'focus': 'Climate data, environmental measurements, peer-reviewed research'
                },
                {
                    'role': 'Environmental Journalist and Science Writer',
                    'expertise': '15+ years covering environmental issues and climate science',
                    'focus': 'Environmental reporting, scientific source verification, climate communication'
                },
                {
                    'role': 'Environmental Policy Expert and Sustainability Analyst',
                    'expertise': 'Environmental policy analysis with government and NGO experience',
                    'focus': 'Policy analysis, regulatory frameworks, sustainability metrics'
                }
            ],
            'entertainment': [
                {
                    'role': 'Entertainment Industry Insider and Critic',
                    'expertise': '20+ years covering Hollywood, film industry, and celebrity culture',
                    'focus': 'Industry facts, box office data, production information, celebrity verification'
                },
                {
                    'role': 'Media Studies Professor specializing in Popular Culture',
                    'expertise': 'PhD in Media Studies with focus on entertainment media and cultural analysis',
                    'focus': 'Entertainment media analysis, cultural context, industry trends'
                },
                {
                    'role': 'Entertainment Journalist and Awards Reporter',
                    'expertise': '15+ years reporting on entertainment news, awards, and industry events',
                    'focus': 'Entertainment reporting standards, industry source verification, event coverage'
                }
            ],
            'general': [
                {
                    'role': 'Investigative Journalist and Fact-Checker',
                    'expertise': '25+ years investigative journalism with fact-checking specialization',
                    'focus': 'Source verification, evidence analysis, investigative standards'
                },
                {
                    'role': 'Media Literacy Expert and Communication Professor',
                    'expertise': 'PhD in Communications with media literacy research focus',
                    'focus': 'Media analysis, information verification, critical thinking'
                },
                {
                    'role': 'Information Scientist and Research Methodologist',
                    'expertise': 'Information science with research methodology and data analysis expertise',
                    'focus': 'Information verification, research standards, data validation'
                }
            ]
        }
    
    def analyze_sentence_multi_role(self, sentence: str, domain: str) -> ConsensusResult:
        experts = self.domain_experts.get(domain, self.domain_experts['general'])
        expert_analyses = []
        
        print(f"      Multi-role analysis with {len(experts)} experts...", flush=True)
        
        for i, expert in enumerate(experts, 1):
            print(f"         Expert {i}/{len(experts)}: {expert['role'][:30]}...", flush=True)
            analysis = self._get_expert_analysis(sentence, expert, domain)
            expert_analyses.append(analysis)
            time.sleep(0.3)
        
        consensus = self._build_consensus(sentence, expert_analyses, domain)
        print(f"      Consensus: {consensus.final_classification} ({consensus.consensus_confidence:.2f}) - {consensus.agreement_level}", flush=True)
        print(f"      Sentence: \"{sentence[:50]}{'...' if len(sentence) > 50 else ''}\"", flush=True)
        
        return consensus
    
    def _get_expert_analysis(self, sentence: str, expert: Dict[str, str], domain: str) -> ExpertAnalysis:
        prompt = f"""You are a {expert['role']} with {expert['expertise']}.

Your specialized focus: {expert['focus']}.

Analyze this sentence from a {domain} context and classify it as either FACT or OPINION:

Sentence: "{sentence}"

CRITICAL CLASSIFICATION RULES:

FACT - Choose FACT if the sentence contains:
- Verifiable information: {self._get_domain_fact_criteria(domain)}
- Specific data, numbers, dates, names, locations
- Statements that can be independently verified
- Direct quotes from official sources
- Documented events or actions

OPINION - Choose OPINION if the sentence contains:
- Subjective content: {self._get_domain_opinion_criteria(domain)}
- Evaluative language (good, bad, should, might, could)
- Predictions about the future
- Personal interpretations or assessments
- Emotional language or value judgments
- Speculation or analysis

IMPORTANT: Be strict in classification. Prioritize FACT for verifiable events, actions, and documented occurrences. Only classify as OPINION if the statement contains clear subjective language, predictions, or value judgments.

SPECIAL ATTENTION FOR CONFLICT/HUMANITARIAN CONTENT:
- Deaths, injuries, casualties = FACT (if reported by credible sources)
- Military actions, attacks, bombings = FACT (if documented)
- Humanitarian conditions, starvation, displacement = FACT (if reported by organizations)
- Quotes from officials or witnesses = FACT (if attributed)

Respond ONLY with this exact JSON format:
{{
    "classification": "FACT",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this is a fact or opinion",
    "domain_expertise": "How your expertise influenced this decision",
    "verification_method": "How this could be verified"
}}

OR

{{
    "classification": "OPINION",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this is a fact or opinion",
    "domain_expertise": "How your expertise influenced this decision",
    "verification_method": "How this could be verified"
}}"""

        try:
            response = self.client.generate_content(prompt)
            return self._parse_expert_response(response, expert['role'])
        except Exception as e:
            return ExpertAnalysis(
                expert_role=expert['role'],
                classification="OPINION",
                confidence=0.3,
                reasoning=f"Analysis failed: {str(e)[:50]}",
                domain_expertise="Analysis failed",
                verification_method="Unable to determine"
            )
    
    def _parse_expert_response(self, response: str, expert_role: str) -> ExpertAnalysis:
        """Parse expert response into structured analysis"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try to find JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                # If no JSON, try to extract classification from text
                if 'FACT' in response.upper() and 'OPINION' not in response.upper():
                    classification = 'FACT'
                elif 'OPINION' in response.upper():
                    classification = 'OPINION'
                else:
                    classification = 'OPINION'  # Default to opinion when unclear
                
                return ExpertAnalysis(
                    expert_role=expert_role,
                    classification=classification,
                    confidence=0.6,
                    reasoning="Extracted from text response",
                    domain_expertise="Text-based classification",
                    verification_method="Manual extraction"
                )
            
            json_str = response[start:end]
            data = json.loads(json_str)
            
            # Ensure classification is valid
            classification = data.get('classification', 'FACT').upper()
            if classification not in ['FACT', 'OPINION']:
                classification = 'FACT'
            
            return ExpertAnalysis(
                expert_role=expert_role,
                classification=classification,
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', 'Analysis completed'),
                domain_expertise=data.get('domain_expertise', 'Expert analysis applied'),
                verification_method=data.get('verification_method', 'Standard verification')
            )
        except Exception as e:
            # Default to FACT when parsing fails (conservative approach for factual content)
            return ExpertAnalysis(
                expert_role=expert_role,
                classification="FACT",
                confidence=0.3,
                reasoning=f"Parse error: {str(e)[:50]} - defaulting to FACT for safety",
                domain_expertise="Parse error occurred",
                verification_method="Unable to determine"
            )
    
    def _build_consensus(self, sentence: str, analyses: List[ExpertAnalysis], domain: str) -> ConsensusResult:
        """Build consensus from multiple expert analyses"""
        # Count classifications
        fact_votes = [a for a in analyses if a.classification == 'FACT']
        opinion_votes = [a for a in analyses if a.classification == 'OPINION']
        
        # Determine final classification
        if len(fact_votes) > len(opinion_votes):
            final_classification = 'FACT'
            supporting_analyses = fact_votes
        elif len(opinion_votes) > len(fact_votes):
            final_classification = 'OPINION'
            supporting_analyses = opinion_votes
        else:
            # In case of tie, prefer FACT for verifiable content
            final_classification = 'FACT'
            supporting_analyses = fact_votes
        
        # Find citation if it's a fact
        citation = None
        if final_classification == 'FACT':
            citation = None

        # Calculate consensus confidence (weighted average of supporting experts)
        if supporting_analyses:
            consensus_confidence = sum(a.confidence for a in supporting_analyses) / len(supporting_analyses)
        else:
            consensus_confidence = 0.5
        
        # Determine agreement level
        total_experts = len(analyses)
        majority_count = len(supporting_analyses)
        
        if majority_count == total_experts:
            agreement_level = "UNANIMOUS"
        elif majority_count > total_experts / 2:
            agreement_level = "MAJORITY"
        else:
            agreement_level = "SPLIT"
        
        # Build consensus reasoning
        consensus_reasoning = self._build_consensus_reasoning(supporting_analyses, agreement_level)
        
        return ConsensusResult(
            sentence=sentence,
            final_classification=final_classification,
            consensus_confidence=consensus_confidence,
            expert_analyses=analyses,
            consensus_reasoning=consensus_reasoning,
            agreement_level=agreement_level,
            domain=domain,
            citation=citation
        )
    
    def _build_consensus_reasoning(self, supporting_analyses: List[ExpertAnalysis], agreement_level: str) -> str:
        """Build consensus reasoning from supporting expert analyses"""
        if agreement_level == "UNANIMOUS":
            prefix = "All experts unanimously agree:"
        elif agreement_level == "MAJORITY":
            prefix = f"Majority of experts ({len(supporting_analyses)}) agree:"
        else:
            prefix = "Split decision with slight majority:"
        
        # Combine key reasoning points
        key_points = []
        for analysis in supporting_analyses[:2]:  # Top 2 supporting experts
            expert_name = analysis.expert_role.split(' and ')[0]  # Shorten name
            key_points.append(f"{expert_name}: {analysis.reasoning[:60]}...")
        
        return f"{prefix} {' | '.join(key_points)}"
    
    def _get_domain_fact_criteria(self, domain: str) -> str:
        """Get domain-specific criteria for facts"""
        criteria = {
            'conflict': 'Official casualty reports, verified military actions, confirmed diplomatic statements, documented humanitarian data, international organization reports',
            'health': 'Clinical trial data, FDA approvals, medical guidelines, peer-reviewed studies, official health statistics',
            'politics': 'Voting records, official statements, legislation text, election results, government data, court decisions',
            'sports': 'Game scores, official statistics, records, tournament results, verified performance data, league announcements',
            'economics': 'Market data, financial reports, economic indicators, official statistics, company filings, central bank data',
            'technology': 'Technical specifications, research papers, product documentation, industry reports, patent filings, official releases',
            'environment': 'Scientific measurements, research data, climate records, environmental studies, official reports, peer-reviewed findings',
            'general': 'Documented evidence, official sources, verifiable data, credible reporting, factual documentation'
        }
        return criteria.get(domain, criteria['general'])
    
    def _get_domain_opinion_criteria(self, domain: str) -> str:
        """Get domain-specific criteria for opinions"""
        criteria = {
            'conflict': 'Strategic assessments, conflict predictions, subjective interpretations of events, editorial commentary on war, personal testimonies without verification',
            'health': 'Treatment recommendations without guidelines, personal health experiences, subjective symptom descriptions, medical predictions',
            'politics': 'Policy interpretations, political predictions, subjective candidate assessments, editorial commentary, political speculation',
            'sports': 'Performance predictions, subjective player evaluations, game outcome speculation, coaching opinions, fan perspectives',
            'economics': 'Market predictions, investment advice, economic forecasts, subjective business evaluations, analyst opinions',
            'technology': 'Product reviews, future tech predictions, subjective usability assessments, industry speculation, personal preferences',
            'environment': 'Environmental predictions, policy recommendations, subjective impact assessments, advocacy positions, future scenarios',
            'general': 'Personal views, interpretations, predictions, subjective assessments, editorial commentary, value judgments'
        }
        return criteria.get(domain, criteria['general'])

class DomainDetector:
    """Enhanced domain detector for multi-role system"""
    
    def __init__(self):
        self.client = CleanGeminiClient()
        
        self.domain_keywords = {
            'conflict': ['war', 'conflict', 'gaza', 'israel', 'palestine', 'ukraine', 'russia', 'military', 'attack', 'bombing', 'ceasefire', 'casualties', 'refugees', 'humanitarian', 'crisis', 'violence', 'armed', 'battle', 'invasion', 'occupation', 'crash', 'accident', 'disaster', 'emergency', 'incident', 'tragedy', 'fatal', 'death', 'killed', 'injured', 'victims'],
            'health': ['health', 'medical', 'disease', 'treatment', 'doctor', 'hospital', 'medicine', 'patient', 'drug', 'vaccine', 'symptoms', 'diagnosis', 'therapy', 'clinical'],
            'politics': ['politics', 'government', 'election', 'vote', 'policy', 'congress', 'senate', 'president', 'minister', 'parliament', 'law', 'legislation', 'campaign', 'political'],
            'sports': ['sports', 'game', 'team', 'player', 'match', 'score', 'championship', 'league', 'coach', 'athlete', 'tournament', 'season', 'football', 'basketball', 'soccer'],
            'economics': ['economy', 'economic', 'market', 'stock', 'financial', 'business', 'trade', 'investment', 'inflation', 'gdp', 'unemployment', 'banking', 'corporate'],
            'technology': ['technology', 'tech', 'software', 'hardware', 'digital', 'internet', 'ai', 'artificial intelligence', 'computer', 'data', 'cyber', 'innovation'],
            'environment': ['environment', 'climate', 'weather', 'pollution', 'carbon', 'renewable', 'sustainability', 'ecosystem', 'conservation', 'global warming'],
            'entertainment': ['entertainment', 'movie', 'film', 'actor', 'actress', 'celebrity', 'hollywood', 'music', 'album', 'concert', 'tv', 'television', 'show', 'series', 'awards', 'oscar', 'grammy']
        }
    
    def detect_domain(self, content: str, title: str = "") -> str:
        """Detect domain with enhanced accuracy"""
        print(f"🔍 Domain Detection Process:", flush=True)
        full_text = f"{title} {content}".lower()
        
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            domain_scores[domain] = score
            if score > 0:
                print(f"   {domain.upper()}: {score} keyword matches", flush=True)
        
        if max(domain_scores.values()) > 2:
            detected = max(domain_scores.keys(), key=lambda k: domain_scores[k])
            print(f"✅ Domain detected via keywords: {detected.upper()}", flush=True)
            return detected
        
        print("🤖 Using AI-based domain detection...")
        return self._ai_domain_detection(content[:500])
    
    def _ai_domain_detection(self, content: str) -> str:
        """AI-based domain detection"""
        prompt = f"""Analyze this content and identify its primary domain.

Content: "{content}"

Choose from: health, politics, sports, economics, technology, environment, general

Respond with JSON: {{"domain": "domain_name"}}"""

        try:
            response = self.client.generate_content(prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                data = json.loads(response[start:end])
                return data.get('domain', 'general')
        except:
            pass
        
        return 'general'

class MultiRoleFormatter:
    """Enhanced formatter for multi-role analysis results"""
    
    def format_results(self, consensus_results: List[ConsensusResult], title: str = "", domain: str = "general") -> str:
        """Format multi-role analysis results"""
        output = []
        
        # Header
        output.append("=" * 140)
        output.append(f"MULTI-ROLE PROMPTING SYSTEM - RESEARCH ANALYSIS")
        output.append(f"DOMAIN: {domain.upper()} | EXPERTS: 3 per sentence | CONSENSUS-BASED CLASSIFICATION")
        if title:
            output.append(f"Title: {title}")
        output.append("=" * 140)
        
        # Separate facts and opinions
        facts = [r for r in consensus_results if r.final_classification == 'FACT']
        opinions = [r for r in consensus_results if r.final_classification == 'OPINION']
        
        # Research metrics
        total_sentences = len(consensus_results)
        unanimous_decisions = len([r for r in consensus_results if r.agreement_level == 'UNANIMOUS'])
        majority_decisions = len([r for r in consensus_results if r.agreement_level == 'MAJORITY'])
        
        output.append(f"MULTI-ROLE ANALYSIS METRICS:")
        output.append(f"   Total Sentences: {total_sentences} | Facts: {len(facts)} | Opinions: {len(opinions)}")
        output.append(f"   Unanimous Decisions: {unanimous_decisions} ({unanimous_decisions/total_sentences*100:.1f}%)")
        output.append(f"   Majority Decisions: {majority_decisions} ({majority_decisions/total_sentences*100:.1f}%)")
        output.append(f"   Expert Agreement Rate: {(unanimous_decisions + majority_decisions)/total_sentences*100:.1f}%")
        output.append("")
        
        # Column headers
        output.append(f"{'FACTS (Multi-Expert Verified)':<68} | {'OPINIONS (Multi-Expert Identified)':<68}")
        output.append("-" * 69 + "|" + "-" * 69)
        
        # Format items
        fact_lines = self._format_consensus_items(facts)
        opinion_lines = self._format_consensus_items(opinions)
        
        # Balance columns
        max_lines = max(len(fact_lines), len(opinion_lines))
        while len(fact_lines) < max_lines:
            fact_lines.append("")
        while len(opinion_lines) < max_lines:
            opinion_lines.append("")
        
        # Combine columns
        for fact_line, opinion_line in zip(fact_lines, opinion_lines):
            fact_part = fact_line[:68].ljust(68)
            opinion_part = opinion_line[:68].ljust(68)
            output.append(f"{fact_part} | {opinion_part}")
        
        # Research summary
        output.append("=" * 140)
        output.append(f"MULTI-ROLE RESEARCH SUMMARY")
        output.append("=" * 140)
        
        # Confidence analysis
        fact_avg_conf = sum(f.consensus_confidence for f in facts) / len(facts) if facts else 0
        opinion_avg_conf = sum(o.consensus_confidence for o in opinions) / len(opinions) if opinions else 0
        overall_conf = sum(r.consensus_confidence for r in consensus_results) / len(consensus_results)
        
        output.append(f"CONSENSUS CONFIDENCE METRICS:")
        output.append(f"   Facts Average: {fact_avg_conf:.3f} | Opinions Average: {opinion_avg_conf:.3f}")
        output.append(f"   Overall System Confidence: {overall_conf:.3f}")
        
        # Expert agreement analysis
        high_agreement = len([r for r in consensus_results if r.consensus_confidence > 0.8])
        output.append(f"\nEXPERT AGREEMENT ANALYSIS:")
        output.append(f"   High-Confidence Consensus (>0.8): {high_agreement}/{total_sentences} ({high_agreement/total_sentences*100:.1f}%)")
        output.append(f"   Multi-Role Validation: {len(consensus_results[0].expert_analyses) if consensus_results else 0} experts per sentence")
        output.append(f"   Domain Expertise: {domain.title()} specialists applied")
        
        output.append("=" * 140)
        
        return "\n".join(output)
    
    def _format_consensus_items(self, items: List[ConsensusResult]) -> List[str]:
        """Format consensus items with multi-expert information"""
        lines = []
        for i, item in enumerate(items, 1):
            confidence = item.consensus_confidence
            conf_indicator = "[HIGH]" if confidence > 0.8 else "[MED]" if confidence > 0.6 else "[LOW]"
            agreement_indicator = "[UNA]" if item.agreement_level == "UNANIMOUS" else "[MAJ]" if item.agreement_level == "MAJORITY" else "[SPL]"
            
            # Main sentence
            sentence = item.sentence[:50] + "..." if len(item.sentence) > 50 else item.sentence
            lines.append(f"{i}. {conf_indicator}{agreement_indicator} {sentence}")
            
            # Add citation if available
            if item.citation:
                lines.append(f"   Source: {item.citation['title']} ({item.citation['url']})")

            # Consensus info
            lines.append(f"   Consensus: {confidence:.2f} | {item.agreement_level}")
            
            # Expert breakdown
            fact_experts = len([a for a in item.expert_analyses if a.classification == 'FACT'])
            opinion_experts = len([a for a in item.expert_analyses if a.classification == 'OPINION'])
            lines.append(f"   Experts: {fact_experts}F/{opinion_experts}O | {item.domain.title()}")
            
            lines.append("")
        
        return lines

class ChatInterface:
    """Interactive chat interface for post-analysis questions"""
    
    def __init__(self, original_content: str, analysis_results: List[ConsensusResult], domain: str, title: str = ""):
        self.client = CleanGeminiClient()
        self.original_content = original_content
        self.analysis_results = analysis_results
        self.domain = domain
        self.title = title
        self.facts = [r for r in analysis_results if r.final_classification == 'FACT']
        self.opinions = [r for r in analysis_results if r.final_classification == 'OPINION']
    
    def start_chat(self):
        """Start interactive chat session"""
        print("\n" + "=" * 80)
        print("INTERACTIVE Q&A SESSION")
        print("Ask questions about the analyzed content")
        print("Type 'quit', 'exit', or 'q' to end the session")
        print("=" * 80)
        
        print(f"\nContent Summary:")
        print(f"- Title: {self.title}")
        print(f"- Domain: {self.domain.upper()}")
        print(f"- Facts identified: {len(self.facts)}")
        print(f"- Opinions identified: {len(self.opinions)}")
        print(f"- Total sentences analyzed: {len(self.analysis_results)}")
        
        print("\nSample questions you can ask:")
        print("- What are the main facts in this article?")
        print("- What opinions were identified?")
        print("- What is the expert consensus on [specific topic]?")
        print("- Summarize the key points")
        print("- What controversies are mentioned?")
        
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q', '']:
                    print("Chat session ended.")
                    break
                
                answer = self._answer_question(question)
                print(f"\nAnswer: {answer}")
                
            except KeyboardInterrupt:
                print("\nChat session ended.")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _answer_question(self, question: str) -> str:
        """Generate answer based on analysis results"""
        # Debug: Print analysis results info
        print(f"DEBUG: Total analysis results: {len(self.analysis_results)}")
        print(f"DEBUG: Facts found: {len(self.facts)}")
        print(f"DEBUG: Opinions found: {len(self.opinions)}")
        
        # Prepare context from analysis
        if self.facts:
            facts_text = "\n".join([f"- {fact.sentence}" for fact in self.facts[:10]])
        else:
            facts_text = "No facts identified in the analysis."
            
        if self.opinions:
            opinions_text = "\n".join([f"- {opinion.sentence}" for opinion in self.opinions[:10]])
        else:
            opinions_text = "No opinions identified in the analysis."
        
        # Add more detailed analysis info
        analysis_summary = f"Total sentences analyzed: {len(self.analysis_results)}\n"
        analysis_summary += f"Facts identified: {len(self.facts)}\n"
        analysis_summary += f"Opinions identified: {len(self.opinions)}\n"
        
        context = f"""
ANALYZED CONTENT SUMMARY:
Title: {self.title}
Domain: {self.domain}
{analysis_summary}

IDENTIFIED FACTS:
{facts_text}

IDENTIFIED OPINIONS:
{opinions_text}

ORIGINAL CONTENT SNIPPET:
{self.original_content[:1000]}...
"""
        
        prompt = f"""You are an expert analyst answering questions about analyzed news content.

{context}

User Question: {question}

Provide a clear, informative answer based on the analysis results. Reference specific facts or opinions when relevant. If the question cannot be answered from the available information, say so clearly.

Answer:"""
        
        try:
            response = self.client.generate_content(prompt)
            return response.strip()
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {e}"

class MultiRolePromptingSystem:
    """Main system with multi-role prompting"""
    
    def __init__(self):
        self.scraper = NewsContentScraper()
        self.domain_detector = DomainDetector()
        self.multi_analyzer = MultiRoleAnalyzer()
        self.formatter = MultiRoleFormatter()
        self.last_analysis_data = None  # Store for chat interface
    
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
            
            response = self.multi_analyzer.client.generate_content(prompt)
            return response.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def analyze_url(self, url: str) -> str:
        """Analyze URL with multi-role prompting"""
        print(f"Scraping content from: {url}")
        
        scraped_data = self.scraper.scrape_url(url)
        if not scraped_data or not scraped_data.get('content'):
            return "ERROR: Failed to scrape content from URL"
        
        print(f"Scraped {len(scraped_data['content'])} characters")
        print(f"Title: {scraped_data.get('title', 'N/A')}")
        
        domain = self.domain_detector.detect_domain(
            scraped_data['content'],
            scraped_data.get('title', '')
        )
        
        print(f"Detected Domain: {domain.upper()}")
        print(f"Multi-Role Analysis: 3 experts per sentence")
        
        return self._analyze_content(scraped_data, domain)
    
    def analyze_text(self, text: str) -> str:
        """Analyze text with multi-role prompting"""
        print(f"Analyzing provided text ({len(text)} characters)")
        
        domain = self.domain_detector.detect_domain(text)
        print(f"Detected Domain: {domain.upper()}")
        print(f"Multi-Role Analysis: 3 experts per sentence")
        
        data = {'content': text, 'title': 'User Provided Text'}
        return self._analyze_content(data, domain)
    
    def get_chat_interface(self) -> ChatInterface:
        """Get chat interface for last analysis"""
        if not self.last_analysis_data:
            raise ValueError("No analysis data available. Run analysis first.")
        
        return ChatInterface(
            self.last_analysis_data['content'],
            self.last_analysis_data['results'],
            self.last_analysis_data['domain'],
            self.last_analysis_data['title']
        )
    
    def _analyze_content(self, data: Dict[str, Any], domain: str) -> str:
        """Analyze content with multi-role experts"""
        sentences = self._split_sentences(data['content'])
        print(f"Found {len(sentences)} sentences to analyze")
        
        if not sentences:
            return "ERROR: No sentences found to analyze"
        
        consensus_results = []
        analysis_limit = min(len(sentences), 1) 

        for i, sentence in enumerate(sentences[:analysis_limit], 1):
            print(f"   Multi-role analyzing sentence {i}/{analysis_limit}...")
            consensus = self.multi_analyzer.analyze_sentence_multi_role(sentence, domain)
            consensus_results.append(consensus)
            time.sleep(1)  
        
        self.last_analysis_data = {
            'content': data['content'],
            'results': consensus_results,
            'domain': domain,
            'title': data.get('title', '')
        }
        
        formatted_output = self.formatter.format_results(
            consensus_results,
            data.get('title', ''),
            domain
        )
        
        return formatted_output
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
        return sentences

def main():
    print("=" * 120)
    print("MULTI-ROLE PROMPTING SYSTEM")
    print("3 Expert Roles Per Sentence | Consensus-Based Classification")
    print("Enhanced Accuracy Through Multi-Expert Analysis")
    print("=" * 120)
    
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h", "help"]:
        print("\nUSAGE:")
        print("  python multi_role_prompting_system.py <URL>")
        print("  python multi_role_prompting_system.py --text <TEXT>")
        print("\nEXAMPLES:")
        print("  python multi_role_prompting_system.py https://edition.cnn.com/politics")
        print('  python multi_role_prompting_system.py --text "Political analysis text..."')
        print("\nFEATURES:")
        print("  - 3 expert roles analyze each sentence simultaneously")
        print("  - Consensus-based classification with agreement levels")
        print("  - Domain-specific expert teams (health, politics, sports, etc.)")
        print("  - Enhanced accuracy through multi-expert validation")
        return
    
    system = MultiRolePromptingSystem()
    
    try:
        if sys.argv[1] == "--text":
            if len(sys.argv) < 3:
                print("ERROR: Please provide text")
                return
            text = " ".join(sys.argv[2:])
            result = system.analyze_text(text)
        else:
            url = sys.argv[1]
            result = system.analyze_url(url)
        
        print("\n" + result)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"multi_role_analysis_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nMulti-role analysis saved to {filename}")
        
        try:
            chat = system.get_chat_interface()
            chat.start_chat()
        except Exception as chat_error:
            print(f"\nChat interface error: {chat_error}")
        
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    main()