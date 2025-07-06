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
                confidence=0.3,
                reasoning=f"Analysis failed: {str(e)[:100]}",
                evidence=[],
                key_phrases=[]
            )
    
    def _parse_response(self, response: str) -> AnalysisResult:
        """Parse JSON response"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found")
            
            json_str = response[start:end]
            data = json.loads(json_str)
            
            return AnalysisResult(
                agent_name=self.agent_name,
                classification=data.get('classification', 'MIXED'),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', 'Analysis completed'),
                evidence=data.get('evidence', []),
                key_phrases=data.get('key_phrases', [])
            )
        except Exception as e:
            print(f"Parse error in {self.agent_name}: {e}")
            return AnalysisResult(
                agent_name=self.agent_name,
                classification="MIXED",
                confidence=0.3,
                reasoning="Failed to parse response",
                evidence=[],
                key_phrases=[]
            )

class CleanAnalysisSystem:
    """Main analysis system with 4 agents"""
    
    def __init__(self):
        self.client = CleanGeminiClient()
        self.agents = [
            Agent(self.client, "Journalist", "experienced journalist focused on factual accuracy"),
            Agent(self.client, "Professor", "media studies professor applying academic standards"),
            Agent(self.client, "Linguist", "linguist analyzing language patterns"),
            Agent(self.client, "Social Media Expert", "social media expert identifying viral vs factual content")
        ]
        
        # Weights for consensus
        self.weights = [0.3, 0.3, 0.2, 0.2]
    
    def analyze_content(self, content: str) -> ConsensusResult:
        """Run analysis with all agents"""
        print(f"🤖 Starting analysis with {len(self.agents)} agents...")
        
        agent_results = []
        
        for i, agent in enumerate(self.agents):
            print(f"   Agent {i+1}/4: {agent.agent_name} analyzing...")
            result = agent.analyze(content)
            agent_results.append(result)
            print(f"   ✓ {agent.agent_name}: {result.classification} ({result.confidence:.2f})")
            time.sleep(1)  # Rate limiting
        
        # Build consensus
        consensus = self._build_consensus(agent_results)
        print(f"🎯 Final: {consensus.final_classification} ({consensus.confidence:.2f})")
        
        return consensus
    
    def _build_consensus(self, results: List[AnalysisResult]) -> ConsensusResult:
        """Build weighted consensus"""
        scores = {"FACT": 0.0, "OPINION": 0.0, "MIXED": 0.0}
        
        for result, weight in zip(results, self.weights):
            scores[result.classification] += weight * result.confidence
        
        final_classification = max(scores.keys(), key=lambda k: scores[k])
        final_confidence = scores[final_classification]
        
        # Build reasoning
        agreeing_agents = [r for r in results if r.classification == final_classification]
        reasoning = f"Consensus from {len(agreeing_agents)} agents: " + \
                   " | ".join([f"{r.agent_name}: {r.reasoning[:50]}..." for r in agreeing_agents[:2]])
        
        # Collect evidence
        all_evidence = []
        for result in results:
            all_evidence.extend(result.evidence)
        unique_evidence = list(dict.fromkeys(all_evidence))[:5]
        
        return ConsensusResult(
            final_classification=final_classification,
            confidence=min(final_confidence, 1.0),
            agent_results=results,
            consensus_reasoning=reasoning,
            evidence_summary=unique_evidence
        )

def main():
    """Test the clean system"""
    test_content = """
    The Federal Reserve announced today that it will raise interest rates by 0.25 percentage points, 
    bringing the federal funds rate to 5.25%. This decision was made during the Federal Open Market 
    Committee meeting held on March 15-16, 2024.
    """
    
    try:
        system = CleanAnalysisSystem()
        result = system.analyze_content(test_content)
        
        print("\n" + "="*50)
        print("📋 ANALYSIS RESULTS")
        print("="*50)
        print(f"Classification: {result.final_classification}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reasoning: {result.consensus_reasoning}")
        print(f"Evidence: {', '.join(result.evidence_summary)}")
        
        print("\n🤖 Agent Results:")
        for agent_result in result.agent_results:
            print(f"  • {agent_result.agent_name}: {agent_result.classification} ({agent_result.confidence:.2f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()