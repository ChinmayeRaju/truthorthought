"""
Content Summarizer Service using Gemini
Extracts key personnel, important quotes, and key insights from analyzed content
"""

import os
import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class KeyPersonnel:
    """Represents a key person mentioned in the content"""
    name: str
    title: str
    organization: str
    role_in_story: str
    quotes: List[str]
    relevance_score: float

@dataclass
class ImportantQuote:
    """Represents an important quote from the content"""
    quote: str
    speaker: str
    speaker_title: str
    context: str
    significance: str
    impact_score: float

@dataclass
class KeyInsight:
    """Represents a key insight or important bit from the content"""
    insight: str
    category: str  # e.g., "main_point", "consequence", "background", "statistic"
    supporting_evidence: str
    importance_score: float

@dataclass
class ContentSummary:
    """Complete summary of content with all extracted elements"""
    key_personnel: List[KeyPersonnel]
    important_quotes: List[ImportantQuote]
    key_insights: List[KeyInsight]
    main_themes: List[str]
    executive_summary: str
    content_type: str  # e.g., "news", "analysis", "opinion"
    credibility_indicators: List[str]

class ContentSummarizer:
    """Advanced content summarizer using Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini client for content summarization"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
    
    def summarize_content(self, content: str, title: str = "", domain: str = "GENERAL") -> ContentSummary:
        """
        Generate comprehensive summary of content with key personnel, quotes, and insights
        
        Args:
            content: The full text content to summarize
            title: Title of the content (optional)
            domain: Content domain for context (NEWS, POLITICS, etc.)
            
        Returns:
            ContentSummary with all extracted elements
        """
        print(f"🔍 Summarizing content: {title[:100]}...")
        
        try:
            # Create comprehensive summarization prompt
            prompt = self._create_summarization_prompt(content, title, domain)
            
            # Generate summary using Gemini
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            
            # Parse the structured response
            summary = self._parse_summary_response(response.text)
            
            print(f"✅ Content summarization completed")
            return summary
            
        except Exception as e:
            print(f"❌ Error in content summarization: {str(e)}")
            # Return empty summary on error
            return ContentSummary(
                key_personnel=[],
                important_quotes=[],
                key_insights=[],
                main_themes=[],
                executive_summary="Summary generation failed",
                content_type="unknown",
                credibility_indicators=[]
            )
    
    def _create_summarization_prompt(self, content: str, title: str, domain: str) -> str:
        """Create a comprehensive prompt for content summarization"""
        
        domain_context = {
            'NEWS': 'news article with focus on current events and factual reporting',
            'POLITICS': 'political content with focus on government, policy, and political figures',
            'HEALTH': 'health-related content with focus on medical information and health policies',
            'FINANCE': 'financial content with focus on economic data and market information',
            'TECHNOLOGY': 'technology content with focus on innovations and tech industry',
            'SCIENCE': 'scientific content with focus on research and discoveries',
            'SPORTS': 'sports content with focus on athletic performance and competitions',
            'ENTERTAINMENT': 'entertainment content with focus on media and celebrity news',
            'LEGAL': 'legal content with focus on court cases and legal proceedings',
            'ENVIRONMENT': 'environmental content with focus on climate and sustainability'
        }.get(domain, 'general content')
        
        return f"""
You are an expert content analyst specializing in extracting key information from {domain_context}.

Analyze the following content and extract structured information in JSON format:

TITLE: {title}
CONTENT: {content}

Please provide a comprehensive analysis in the following JSON structure:

{{
    "key_personnel": [
        {{
            "name": "Full name of the person",
            "title": "Their official title or position",
            "organization": "Organization they represent",
            "role_in_story": "Their role/relevance in this content",
            "quotes": ["Direct quotes from this person"],
            "relevance_score": 0.0-1.0
        }}
    ],
    "important_quotes": [
        {{
            "quote": "The exact quote text",
            "speaker": "Who said it",
            "speaker_title": "Speaker's title/position",
            "context": "Context around the quote",
            "significance": "Why this quote is important",
            "impact_score": 0.0-1.0
        }}
    ],
    "key_insights": [
        {{
            "insight": "Key point or important information",
            "category": "main_point|consequence|background|statistic|prediction|analysis",
            "supporting_evidence": "Evidence supporting this insight",
            "importance_score": 0.0-1.0
        }}
    ],
    "main_themes": ["Theme 1", "Theme 2", "Theme 3"],
    "executive_summary": "2-3 sentence summary of the main points",
    "content_type": "news|analysis|opinion|report|interview|announcement",
    "credibility_indicators": ["Indicator 1", "Indicator 2"]
}}

EXTRACTION GUIDELINES:
1. KEY PERSONNEL: Focus on people who are central to the story, have authority, or provide expert opinions
2. IMPORTANT QUOTES: Select quotes that reveal key information, opinions, or decisions
3. KEY INSIGHTS: Extract the most important facts, statistics, consequences, and analysis points
4. MAIN THEMES: Identify 3-5 overarching themes or topics
5. EXECUTIVE SUMMARY: Provide a concise overview of the main story
6. CONTENT TYPE: Classify the type of content
7. CREDIBILITY INDICATORS: Note elements that indicate reliability (sources, data, expert opinions)

Ensure all scores are between 0.0 and 1.0, with 1.0 being most important/relevant.
Return only valid JSON without any additional text or formatting.
"""
    
    def _parse_summary_response(self, response_text: str) -> ContentSummary:
        """Parse Gemini's JSON response into ContentSummary object"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove any markdown formatting
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Convert to dataclass objects
            key_personnel = [
                KeyPersonnel(
                    name=p.get('name', ''),
                    title=p.get('title', ''),
                    organization=p.get('organization', ''),
                    role_in_story=p.get('role_in_story', ''),
                    quotes=p.get('quotes', []),
                    relevance_score=float(p.get('relevance_score', 0.0))
                ) for p in data.get('key_personnel', [])
            ]
            
            important_quotes = [
                ImportantQuote(
                    quote=q.get('quote', ''),
                    speaker=q.get('speaker', ''),
                    speaker_title=q.get('speaker_title', ''),
                    context=q.get('context', ''),
                    significance=q.get('significance', ''),
                    impact_score=float(q.get('impact_score', 0.0))
                ) for q in data.get('important_quotes', [])
            ]
            
            key_insights = [
                KeyInsight(
                    insight=i.get('insight', ''),
                    category=i.get('category', 'main_point'),
                    supporting_evidence=i.get('supporting_evidence', ''),
                    importance_score=float(i.get('importance_score', 0.0))
                ) for i in data.get('key_insights', [])
            ]
            
            return ContentSummary(
                key_personnel=key_personnel,
                important_quotes=important_quotes,
                key_insights=key_insights,
                main_themes=data.get('main_themes', []),
                executive_summary=data.get('executive_summary', ''),
                content_type=data.get('content_type', 'unknown'),
                credibility_indicators=data.get('credibility_indicators', [])
            )
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}...")
            return self._create_fallback_summary(response_text)
        except Exception as e:
            print(f"❌ Error parsing summary response: {str(e)}")
            return self._create_fallback_summary(response_text)
    
    def _create_fallback_summary(self, response_text: str) -> ContentSummary:
        """Create a basic summary when JSON parsing fails"""
        # Try to extract some basic information using regex
        quotes = re.findall(r'"([^"]+)"', response_text)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', response_text)
        
        return ContentSummary(
            key_personnel=[],
            important_quotes=[
                ImportantQuote(
                    quote=quote,
                    speaker="Unknown",
                    speaker_title="",
                    context="",
                    significance="",
                    impact_score=0.5
                ) for quote in quotes[:3]  # Take first 3 quotes
            ],
            key_insights=[
                KeyInsight(
                    insight="Summary generation encountered parsing issues",
                    category="technical_note",
                    supporting_evidence="",
                    importance_score=0.3
                )
            ],
            main_themes=["Content analysis"],
            executive_summary="Content summary could not be fully generated due to parsing issues.",
            content_type="unknown",
            credibility_indicators=[]
        )
    
    def summarize_multiple_sources(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize multiple sources and provide cross-source analysis
        
        Args:
            sources: List of source dictionaries with content, title, url, etc.
            
        Returns:
            Combined summary with cross-source insights
        """
        print(f"🔍 Summarizing {len(sources)} sources...")
        
        individual_summaries = []
        all_personnel = []
        all_quotes = []
        all_insights = []
        all_themes = []
        
        # Summarize each source individually
        for source in sources:
            content = source.get('content', source.get('formatted_content', ''))
            title = source.get('title', '')
            domain = source.get('domain', 'GENERAL')
            
            summary = self.summarize_content(content, title, domain)
            individual_summaries.append({
                'url': source.get('url', ''),
                'title': title,
                'summary': summary
            })
            
            # Aggregate data
            all_personnel.extend(summary.key_personnel)
            all_quotes.extend(summary.important_quotes)
            all_insights.extend(summary.key_insights)
            all_themes.extend(summary.main_themes)
        
        # Generate cross-source analysis
        cross_analysis = self._generate_cross_source_analysis(individual_summaries)
        
        return {
            'individual_summaries': [
                {
                    'url': s['url'],
                    'title': s['title'],
                    'key_personnel': [asdict(p) for p in s['summary'].key_personnel],
                    'important_quotes': [asdict(q) for q in s['summary'].important_quotes],
                    'key_insights': [asdict(i) for i in s['summary'].key_insights],
                    'main_themes': s['summary'].main_themes,
                    'executive_summary': s['summary'].executive_summary,
                    'content_type': s['summary'].content_type
                } for s in individual_summaries
            ],
            'cross_source_analysis': cross_analysis,
            'aggregated_data': {
                'total_personnel': len(set(p.name for p in all_personnel)),
                'total_quotes': len(all_quotes),
                'total_insights': len(all_insights),
                'common_themes': self._find_common_themes(all_themes),
                'top_personnel': self._rank_personnel(all_personnel),
                'most_impactful_quotes': self._rank_quotes(all_quotes),
                'key_insights_summary': self._rank_insights(all_insights)
            }
        }
    
    def _generate_cross_source_analysis(self, summaries: List[Dict]) -> Dict[str, Any]:
        """Generate analysis across multiple sources"""
        # This could be enhanced with another Gemini call for cross-source analysis
        return {
            'consistency_analysis': 'Cross-source analysis would be implemented here',
            'conflicting_information': [],
            'corroborating_evidence': [],
            'source_reliability_comparison': []
        }
    
    def _find_common_themes(self, all_themes: List[str]) -> List[str]:
        """Find themes that appear across multiple sources"""
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Return themes that appear more than once
        return [theme for theme, count in theme_counts.items() if count > 1]
    
    def _rank_personnel(self, personnel: List[KeyPersonnel]) -> List[Dict]:
        """Rank personnel by relevance score"""
        sorted_personnel = sorted(personnel, key=lambda p: p.relevance_score, reverse=True)
        return [asdict(p) for p in sorted_personnel[:10]]  # Top 10
    
    def _rank_quotes(self, quotes: List[ImportantQuote]) -> List[Dict]:
        """Rank quotes by impact score"""
        sorted_quotes = sorted(quotes, key=lambda q: q.impact_score, reverse=True)
        return [asdict(q) for q in sorted_quotes[:10]]  # Top 10
    
    def _rank_insights(self, insights: List[KeyInsight]) -> List[Dict]:
        """Rank insights by importance score"""
        sorted_insights = sorted(insights, key=lambda i: i.importance_score, reverse=True)
        return [asdict(i) for i in sorted_insights[:15]]  # Top 15