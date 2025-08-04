"""
Clean Fact vs Opinion Analysis System using Google Generative AI SDK
Simple 4-agent system without unnecessary complexity
"""

import os
import json
import time
from dataclasses import dataclass, asdict
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

@dataclass
class AnalysisResult:
    agent_name: str
    classification: str  # FACT, OPINION, or MIXED
    confidence: float    # 0.0 to 1.0
    reasoning: str
    evidence: List[str]
    key_phrases: List[str]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ConsensusResult:
    final_classification: str
    confidence: float
    agent_results: List[AnalysisResult]
    consensus_reasoning: str
    evidence_summary: List[str]
    
    def to_dict(self):
        return {
            'final_classification': self.final_classification,
            'confidence': self.confidence,
            'agent_results': [agent.to_dict() for agent in self.agent_results],
            'consensus_reasoning': self.consensus_reasoning,
            'evidence_summary': self.evidence_summary
        }

class CleanGeminiClient:
    """Simple Gemini client using official SDK"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
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
        prompt = f"""As a {self.role}, analyze this text and classify it as FACT, OPINION, or MIXED.

Use web search to verify any factual claims and provide citations.

Text: {content[:500]}

For FACTS: Look for verifiable information that can be confirmed through web search.
For OPINIONS: Identify subjective statements, personal views, or interpretations.
For MIXED: Content containing both factual and opinion elements.

Respond with JSON only:
{{
    "classification": "FACT/OPINION/MIXED",
    "confidence": 0.8,
    "reasoning": "Brief explanation with web verification",
    "evidence": ["key evidence with sources"],
    "key_phrases": ["important phrases"]
}}"""

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
                key_phrases=[]
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
            
            data = json.loads(response)
            
            return AnalysisResult(
                agent_name=self.agent_name,
                classification=data.get('classification', 'MIXED'),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                evidence=data.get('evidence', []),
                key_phrases=data.get('key_phrases', [])
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Parse error in {self.agent_name}: {e}")
            return AnalysisResult(
                agent_name=self.agent_name,
                classification="MIXED",
                confidence=0.5,
                reasoning=f"Parse error: {e}",
                evidence=[],
                key_phrases=[]
            )

class ConsensusBuilder:
    """Build consensus from multiple agent results"""
    
    def build_consensus(self, results: List[AnalysisResult]) -> ConsensusResult:
        """Build consensus from agent results"""
        if not results:
            return ConsensusResult(
                final_classification="MIXED",
                confidence=0.0,
                agent_results=[],
                consensus_reasoning="No results to analyze",
                evidence_summary=[]
            )
        
        # Count classifications
        classifications = [r.classification for r in results]
        fact_count = classifications.count('FACT')
        opinion_count = classifications.count('OPINION')
        mixed_count = classifications.count('MIXED')
        
        # Determine final classification
        if fact_count > opinion_count and fact_count > mixed_count:
            final_classification = 'FACT'
        elif opinion_count > fact_count and opinion_count > mixed_count:
            final_classification = 'OPINION'
        else:
            final_classification = 'MIXED'
        
        # Calculate confidence (average of agreeing agents)
        agreeing_results = [r for r in results if r.classification == final_classification]
        if agreeing_results:
            confidence = sum(r.confidence for r in agreeing_results) / len(agreeing_results)
        else:
            confidence = 0.5
        
        # Build consensus reasoning
        reasoning_parts = []
        for result in results:
            reasoning_parts.append(f"{result.agent_name}: {result.reasoning[:100]}...")
        
        consensus_reasoning = f"Final classification: {final_classification} based on {len(agreeing_results)}/{len(results)} agents. " + " | ".join(reasoning_parts)
        
        # Aggregate evidence
        evidence_summary = []
        for result in results:
            evidence_summary.extend(result.evidence)
        
        return ConsensusResult(
            final_classification=final_classification,
            confidence=confidence,
            agent_results=results,
            consensus_reasoning=consensus_reasoning,
            evidence_summary=list(set(evidence_summary))  # Remove duplicates
        )

class CleanAnalysisSystem:
    """Main analysis system with 4 agents"""
    
    def __init__(self):
        self.client = CleanGeminiClient()
        self.consensus_builder = ConsensusBuilder()
        
        # Initialize 4 agents with different roles
        self.agents = [
            Agent(self.client, "News Journalist", "experienced news journalist focused on factual accuracy"),
            Agent(self.client, "Academic Professor", "university professor specializing in critical analysis"),
            Agent(self.client, "Social Media Analyst", "social media analyst expert in identifying opinions and bias"),
            Agent(self.client, "Linguist", "linguist expert in language patterns and semantic analysis")
        ]
    
    def analyze_content(self, content: str) -> ConsensusResult:
        """Analyze content with all agents and build consensus"""
        print(f"Analyzing content with {len(self.agents)} agents...")
        
        results = []
        for i, agent in enumerate(self.agents, 1):
            print(f"  Agent {i}/{len(self.agents)}: {agent.agent_name}...")
            result = agent.analyze(content)
            results.append(result)
            time.sleep(1)  # Rate limiting
        
        consensus = self.consensus_builder.build_consensus(results)
        return consensus