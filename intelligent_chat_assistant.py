import os
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ChatContext:
    """Context information for chat conversations"""
    content: str
    title: str
    url: str
    domain: str
    facts: List[Dict[str, Any]]
    opinions: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    session_id: str
    timestamp: datetime
    multiple_urls: Optional[List[str]] = None
    individual_results: Optional[List[Dict[str, Any]]] = None
    is_multi_url_analysis: bool = False

class IntelligentChatAssistant:
    """
    Sophisticated AI assistant for analyzing and discussing article content.
    Provides intelligent responses with context awareness and analytical capabilities.
    """
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("No Google API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
    def create_chat_context(self, analysis_data: Dict[str, Any], session_id: str) -> ChatContext:
        """Create chat context from analysis data - supports both single and multiple URL analysis"""
        
        is_multi_url = 'multiple_results' in analysis_data or 'urls' in analysis_data
        multiple_urls = analysis_data.get('urls', [])
        individual_results = analysis_data.get('multiple_results', [])
        
        facts = []
        opinions = []
        
        if 'results' in analysis_data and analysis_data['results']:
            for result in analysis_data['results']:
                if result.get('final_classification') == 'FACT':
                    facts.append(result)
                elif result.get('final_classification') == 'OPINION':
                    opinions.append(result)
        
        if is_multi_url and individual_results:
            for url_result in individual_results:
                if 'facts' in url_result:
                    for fact in url_result['facts']:
                        fact_with_source = fact.copy()
                        fact_with_source['source_url'] = url_result.get('url', '')
                        fact_with_source['source_title'] = url_result.get('title', 'Unknown Source')
                        facts.append(fact_with_source)
                
                if 'opinions' in url_result:
                    for opinion in url_result['opinions']:
                        opinion_with_source = opinion.copy()
                        opinion_with_source['source_url'] = url_result.get('url', '')
                        opinion_with_source['source_title'] = url_result.get('title', 'Unknown Source')
                        opinions.append(opinion_with_source)
        
        analysis_summary = {
            'total_sentences': len(analysis_data.get('results', [])),
            'facts_count': len(facts),
            'opinions_count': len(opinions),
            'domain': analysis_data.get('domain', 'GENERAL'),
            'verification_summary': analysis_data.get('verification_summary', {}),
            'has_verified_sources': any(fact.get('all_urls_comprehensively_verified', False) for fact in facts),
            'is_multi_url_analysis': is_multi_url,
            'urls_analyzed': len(multiple_urls) if multiple_urls else 1,
            'individual_results_count': len(individual_results) if individual_results else 0
        }
        
        if is_multi_url:
            title = f"Multi-Source Analysis ({len(multiple_urls)} URLs)" if multiple_urls else "Multi-Source Analysis"
            if 'content' in analysis_data:
                content = analysis_data['content']
            else:
                content_parts = []
                for url_result in individual_results:
                    if 'raw_content' in url_result and url_result['raw_content']:
                        content_parts.append(f"Source: {url_result.get('title', 'Unknown')}\n{url_result['raw_content']}")
                content = "\n\n---\n\n".join(content_parts)
        else:
            title = analysis_data.get('title', 'Analyzed Content')
            content = analysis_data.get('content', '')
        
        return ChatContext(
            content=content,
            title=title,
            url=analysis_data.get('url', multiple_urls[0] if multiple_urls else ''),
            domain=analysis_data.get('domain', 'GENERAL'),
            facts=facts,
            opinions=opinions,
            analysis_summary=analysis_summary,
            session_id=session_id,
            timestamp=datetime.now(),
            multiple_urls=multiple_urls if is_multi_url else None,
            individual_results=individual_results if is_multi_url else None,
            is_multi_url_analysis=is_multi_url
        )
    
    def answer_question(self, question: str, context: ChatContext) -> str:
        """
        Generate intelligent response to user question about the analyzed content.
        Maintains conversation context and provides analytical insights.
        """
        
        if context.session_id not in self.conversation_history:
            self.conversation_history[context.session_id] = []
        
        question_type = self._classify_question(question)
        
        context_prompt = self._build_context_prompt(context, question_type)
        
        conversation_context = self._build_conversation_context(context.session_id)
        
        if context.is_multi_url_analysis:
            main_prompt = f"""You are an expert AI assistant specializing in multi-source content analysis and critical thinking. You have analyzed multiple sources ({context.analysis_summary.get('urls_analyzed', 0)} URLs) and can provide sophisticated comparative insights about their content, themes, arguments, and implications.

{context_prompt}

{conversation_context}

CURRENT USER QUESTION: {question}

MULTI-SOURCE ANALYSIS GUIDELINES:
1. Provide comprehensive responses that synthesize information across all analyzed sources
2. Compare and contrast different sources when relevant to the question
3. Identify agreements, contradictions, and unique perspectives between sources
4. Reference specific facts, opinions, or passages with their source attribution
5. Highlight which sources provide the strongest evidence for claims
6. Maintain conversational flow and context from previous exchanges
7. Offer analytical insights that draw connections between different sources
8. If the question is unclear, ask clarifying questions
9. If information is not available across the sources, state this clearly
10. Provide additional context that helps understand the topic from multiple angles
11. Handle follow-up questions naturally, considering all sources
12. Identify potential biases or limitations across different sources
13. Explain how different sources frame the same topics or events
14. Help users understand the value of cross-source verification

RESPONSE:"""
        else:
            main_prompt = f"""You are an expert AI assistant specializing in content analysis and critical thinking. You have analyzed an article and can provide sophisticated insights about its content, themes, arguments, and implications.

{context_prompt}

{conversation_context}

CURRENT USER QUESTION: {question}

RESPONSE GUIDELINES:
1. Provide accurate, relevant responses based on the analyzed content
2. Reference specific facts, opinions, or passages when relevant
3. Maintain conversational flow and context from previous exchanges
4. Offer analytical insights and draw connections between ideas
5. If the question is unclear, ask clarifying questions
6. If information is not available in the analysis, state this clearly
7. Provide additional context or related information when appropriate
8. Handle follow-up questions naturally
9. Identify potential biases or limitations in the content when relevant
10. Explain complex concepts mentioned in the article clearly

RESPONSE:"""

        try:
            response = self.model.generate_content(main_prompt)
            answer = response.text.strip()
            
            self.conversation_history[context.session_id].append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat(),
                'question_type': question_type
            })
            
            if len(self.conversation_history[context.session_id]) > 10:
                self.conversation_history[context.session_id] = self.conversation_history[context.session_id][-10:]
            
            return answer
            
        except Exception as e:
            error_response = self._handle_error(question, str(e))
            return error_response
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question to provide better context"""
        question_lower = question.lower()
        
        # Question type patterns
        if any(word in question_lower for word in ['summarize', 'summary', 'main points', 'key points']):
            return 'summary'
        elif any(word in question_lower for word in ['fact', 'facts', 'factual', 'true', 'verified']):
            return 'facts'
        elif any(word in question_lower for word in ['opinion', 'opinions', 'view', 'perspective', 'think']):
            return 'opinions'
        elif any(word in question_lower for word in ['bias', 'biased', 'slanted', 'prejudice']):
            return 'bias'
        elif any(word in question_lower for word in ['source', 'sources', 'citation', 'reference']):
            return 'sources'
        elif any(word in question_lower for word in ['theme', 'themes', 'topic', 'subject']):
            return 'themes'
        elif any(word in question_lower for word in ['argument', 'arguments', 'claim', 'claims']):
            return 'arguments'
        elif any(word in question_lower for word in ['implication', 'implications', 'consequence', 'impact']):
            return 'implications'
        elif any(word in question_lower for word in ['controversy', 'controversial', 'debate', 'dispute']):
            return 'controversy'
        elif any(word in question_lower for word in ['explain', 'what is', 'what does', 'how does']):
            return 'explanation'
        else:
            return 'general'
    
    def _build_context_prompt(self, context: ChatContext, question_type: str) -> str:
        """Build comprehensive context prompt based on analysis data - supports multiple URLs"""
        
        if context.is_multi_url_analysis:
            context_sections = [
                f"MULTI-SOURCE ANALYSIS INFORMATION:",
                f"Analysis Type: {context.title}",
                f"Domain: {context.domain.upper()}",
                f"URLs Analyzed: {context.analysis_summary.get('urls_analyzed', 0)}",
                f"Individual Results: {context.analysis_summary.get('individual_results_count', 0)}",
                f"Analysis Date: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ]
            
            # Add individual URL information
            if context.multiple_urls:
                context_sections.append("ANALYZED URLS:")
                for i, url in enumerate(context.multiple_urls, 1):
                    context_sections.append(f"{i}. {url}")
                context_sections.append("")
            
            # Add individual source summaries
            if context.individual_results:
                context_sections.append("SOURCE SUMMARIES:")
                for i, result in enumerate(context.individual_results[:5], 1):  # Limit to 5 sources
                    title = result.get('title', 'Unknown Title')
                    domain = result.get('domain', 'Unknown')
                    facts_count = result.get('facts_count', 0)
                    opinions_count = result.get('opinions_count', 0)
                    context_sections.append(f"{i}. {title} ({domain})")
                    context_sections.append(f"   Facts: {facts_count}, Opinions: {opinions_count}")
                context_sections.append("")
        else:
            context_sections = [
                f"ARTICLE INFORMATION:",
                f"Title: {context.title}",
                f"Domain: {context.domain.upper()}",
                f"URL: {context.url}" if context.url else "Source: User-provided text",
                f"Analysis Date: {context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ]
        
        if context.is_multi_url_analysis:
            context_sections.extend([
                f"COMPREHENSIVE ANALYSIS SUMMARY:",
                f"- URLs analyzed: {context.analysis_summary.get('urls_analyzed', 0)}",
                f"- Total sentences analyzed: {context.analysis_summary['total_sentences']}",
                f"- Facts identified across all sources: {context.analysis_summary['facts_count']}",
                f"- Opinions identified across all sources: {context.analysis_summary['opinions_count']}",
                f"- Primary domain classification: {context.analysis_summary['domain']}",
                f"- Has verified sources: {'Yes' if context.analysis_summary.get('has_verified_sources') else 'No'}",
                f"- Cross-source analysis: Available",
                ""
            ])
        else:
            context_sections.extend([
                f"ANALYSIS SUMMARY:",
                f"- Total sentences analyzed: {context.analysis_summary['total_sentences']}",
                f"- Facts identified: {context.analysis_summary['facts_count']}",
                f"- Opinions identified: {context.analysis_summary['opinions_count']}",
                f"- Domain classification: {context.analysis_summary['domain']}",
                f"- Has verified sources: {'Yes' if context.analysis_summary.get('has_verified_sources') else 'No'}",
                ""
            ])
        
        if question_type in ['facts', 'summary', 'general', 'sources'] and context.facts:
            if context.is_multi_url_analysis:
                context_sections.append("IDENTIFIED FACTS (ACROSS ALL SOURCES):")
                for i, fact in enumerate(context.facts[:10], 1):  # More facts for multi-URL
                    sentence = fact.get('sentence', fact.get('original_sentence', ''))
                    source_title = fact.get('source_title', 'Unknown Source')
                    source_url = fact.get('source_url', '')
                    
                    context_sections.append(f"{i}. {sentence}")
                    context_sections.append(f"   Source: {source_title}")
                    if source_url:
                        context_sections.append(f"   URL: {source_url}")
                    
                    if fact.get('citations') and len(fact['citations']) > 0:
                        citation = fact['citations'][0]  # Primary citation
                        context_sections.append(f"   Citation: {citation.get('title', 'Unknown')} ({citation.get('domain', 'Unknown domain')})")
                        if citation.get('verification_score'):
                            context_sections.append(f"   Quality Score: {int(citation['verification_score'] * 100)}%")
                context_sections.append("")
            else:
                context_sections.append("IDENTIFIED FACTS:")
                for i, fact in enumerate(context.facts[:8], 1):  # Limit to 8 facts
                    sentence = fact.get('sentence', fact.get('original_sentence', ''))
                    context_sections.append(f"{i}. {sentence}")
                    
                    if fact.get('citations') and len(fact['citations']) > 0:
                        citation = fact['citations'][0]  # Primary citation
                        context_sections.append(f"   Source: {citation.get('title', 'Unknown')} ({citation.get('domain', 'Unknown domain')})")
                        if citation.get('verification_score'):
                            context_sections.append(f"   Quality Score: {int(citation['verification_score'] * 100)}%")
                context_sections.append("")
        
        if question_type in ['opinions', 'summary', 'general', 'bias'] and context.opinions:
            if context.is_multi_url_analysis:
                context_sections.append("IDENTIFIED OPINIONS (ACROSS ALL SOURCES):")
                for i, opinion in enumerate(context.opinions[:8], 1):  # More opinions for multi-URL
                    sentence = opinion.get('sentence', opinion.get('original_sentence', ''))
                    source_title = opinion.get('source_title', 'Unknown Source')
                    source_url = opinion.get('source_url', '')
                    
                    context_sections.append(f"{i}. {sentence}")
                    context_sections.append(f"   Source: {source_title}")
                    if source_url:
                        context_sections.append(f"   URL: {source_url}")
                context_sections.append("")
            else:
                context_sections.append("IDENTIFIED OPINIONS:")
                for i, opinion in enumerate(context.opinions[:6], 1):  # Limit to 6 opinions
                    sentence = opinion.get('sentence', opinion.get('original_sentence', ''))
                    context_sections.append(f"{i}. {sentence}")
                context_sections.append("")
        
        if context.content:
            content_snippet = context.content[:1500] + "..." if len(context.content) > 1500 else context.content
            context_sections.extend([
                "ORIGINAL CONTENT (EXCERPT):",
                content_snippet,
                ""
            ])
        
        if context.analysis_summary.get('verification_summary'):
            verification = context.analysis_summary['verification_summary']
            context_sections.extend([
                "SOURCE VERIFICATION SUMMARY:",
                f"- Facts with verified sources: {verification.get('facts_with_verified_sources', 0)}",
                f"- Facts excluded (no sources): {verification.get('facts_excluded_no_sources', 0)}",
                f"- Verification success rate: {verification.get('verification_success_rate', 0):.1f}%",
                ""
            ])
        
        return "\n".join(context_sections)
    
    def _build_conversation_context(self, session_id: str) -> str:
        """Build conversation history context"""
        if session_id not in self.conversation_history or not self.conversation_history[session_id]:
            return "CONVERSATION HISTORY: This is the start of our conversation."
        
        history_lines = ["RECENT CONVERSATION HISTORY:"]
        for exchange in self.conversation_history[session_id][-3:]:  # Last 3 exchanges
            history_lines.append(f"User: {exchange['question']}")
            history_lines.append(f"Assistant: {exchange['answer'][:200]}{'...' if len(exchange['answer']) > 200 else ''}")
            history_lines.append("")
        
        return "\n".join(history_lines)
    
    def _handle_error(self, question: str, error_message: str) -> str:
        """Handle errors gracefully with helpful responses"""
        
        if "quota" in error_message.lower() or "limit" in error_message.lower():
            return "I apologize, but I'm currently experiencing high demand. Please try your question again in a moment."
        
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            return "I'm having trouble connecting to my analysis systems. Please check your connection and try again."
        
        elif "invalid" in error_message.lower() or "malformed" in error_message.lower():
            return "I'm having trouble understanding your question. Could you please rephrase it or provide more specific details about what you'd like to know?"
        
        else:
            return f"""I apologize, but I encountered an issue while processing your question. Here are some things you can try:

1. **Rephrase your question** - Try asking in a different way
2. **Be more specific** - Add details about what aspect you're interested in
3. **Try these example questions:**
   - "What are the main facts in this article?"
   - "What opinions or viewpoints are presented?"
   - "Can you summarize the key points?"
   - "What sources support the claims made?"
   - "Are there any potential biases in this content?"

Please try again with a rephrased question."""
    
    def get_suggested_questions(self, context: ChatContext) -> List[str]:
        """Generate contextually relevant suggested questions - enhanced for multiple URLs"""
        suggestions = []
        
        if context.is_multi_url_analysis:
            suggestions.extend([
                "How do the different sources compare in their coverage of this topic?",
                "What are the main points of agreement across all sources?",
                "Are there any contradictions between the different sources?",
                "Which source provides the most reliable information?",
                "What unique perspectives does each source offer?"
            ])
            
            if context.facts:
                suggestions.extend([
                    "Which facts are supported by multiple sources?",
                    "What facts are unique to specific sources?",
                    "How do the sources differ in their factual claims?"
                ])
            
            if context.opinions:
                suggestions.extend([
                    "What range of opinions is represented across all sources?",
                    "Do the sources show bias toward particular viewpoints?",
                    "How do editorial perspectives differ between sources?"
                ])
        else:
            if context.facts:
                suggestions.append("What are the main facts presented in this article?")
                suggestions.append("Which facts have the strongest source verification?")
            
            if context.opinions:
                suggestions.append("What opinions or viewpoints are expressed?")
                suggestions.append("How can I distinguish between facts and opinions here?")
        
        if context.domain.upper() == 'POLITICS':
            if context.is_multi_url_analysis:
                suggestions.extend([
                    "How do different sources frame this political issue?",
                    "What political biases can you identify across sources?",
                    "Are there partisan differences in coverage?"
                ])
            else:
                suggestions.extend([
                    "What political perspectives are represented?",
                    "Are there any potential biases in the political coverage?",
                    "What are the key political arguments made?"
                ])
        elif context.domain.upper() == 'HEALTH':
            if context.is_multi_url_analysis:
                suggestions.extend([
                    "How consistent are health claims across sources?",
                    "Which sources provide the most credible medical evidence?",
                    "Are there conflicting health recommendations?"
                ])
            else:
                suggestions.extend([
                    "What health claims are made and are they supported?",
                    "What medical evidence is cited?",
                    "Are there any health recommendations mentioned?"
                ])
        elif context.domain.upper() == 'CONFLICT':
            if context.is_multi_url_analysis:
                suggestions.extend([
                    "How do different sources report on this conflict?",
                    "What perspectives from different sides are represented?",
                    "Are there discrepancies in reported events?"
                ])
            else:
                suggestions.extend([
                    "What are the different sides of this conflict?",
                    "How reliable are the sources for conflict information?",
                    "What are the key events or developments mentioned?"
                ])
        
        if context.is_multi_url_analysis:
            suggestions.extend([
                "Can you provide a comprehensive summary across all sources?",
                "What are the strongest arguments when considering all sources?",
                "How can I synthesize information from multiple perspectives?",
                "What gaps exist in the overall coverage?"
            ])
        else:
            suggestions.extend([
                "Can you summarize the main themes of this article?",
                "What are the strongest and weakest arguments presented?",
                "Are there any logical fallacies or questionable claims?",
                "What additional context would help understand this topic better?"
            ])
        
        max_suggestions = 8 if context.is_multi_url_analysis else 6
        return suggestions[:max_suggestions]
    
    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

def test_chat_assistant():
    """Test the intelligent chat assistant with single URL"""
    print("🤖 Testing Intelligent Chat Assistant (Single URL)")
    print("=" * 60)
    
    try:
        assistant = IntelligentChatAssistant()
        
        sample_data = {
            'content': 'Climate scientists report that global temperatures have risen by 1.1 degrees Celsius since pre-industrial times. Many experts believe this trend will continue without intervention.',
            'title': 'Climate Change Analysis',
            'url': 'https://example.com/climate-article',
            'domain': 'CLIMATE',
            'results': [
                {
                    'sentence': 'Climate scientists report that global temperatures have risen by 1.1 degrees Celsius since pre-industrial times.',
                    'final_classification': 'FACT',
                    'citations': [{'title': 'IPCC Report', 'domain': 'ipcc.ch', 'verification_score': 0.95}],
                    'all_urls_comprehensively_verified': True
                },
                {
                    'sentence': 'Many experts believe this trend will continue without intervention.',
                    'final_classification': 'OPINION',
                    'citations': []
                }
            ]
        }
        
        context = assistant.create_chat_context(sample_data, 'test_session')
        
        test_questions = [
            "What are the main facts in this article?",
            "What sources support the climate claims?",
            "Can you explain the significance of the 1.1 degree increase?"
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            answer = assistant.answer_question(question, context)
            print(f"A: {answer[:200]}...")
        
        print("\n✅ Single URL chat assistant test completed successfully!")
        
    except Exception as e:
        print(f"❌ Single URL test failed: {e}")

def test_multi_url_chat_assistant():
    """Test the intelligent chat assistant with multiple URLs"""
    print("\n🤖 Testing Intelligent Chat Assistant (Multiple URLs)")
    print("=" * 60)
    
    try:
        assistant = IntelligentChatAssistant()
        
        multi_url_data = {
            'content': 'Combined content from multiple sources about climate change and renewable energy.',
            'title': 'Multi-Source Analysis (3 URLs)',
            'domain': 'MULTI-SOURCE',
            'urls': [
                'https://example.com/climate-article',
                'https://example.com/renewable-energy',
                'https://example.com/policy-analysis'
            ],
            'multiple_results': [
                {
                    'url': 'https://example.com/climate-article',
                    'title': 'Climate Change Report',
                    'domain': 'CLIMATE',
                    'facts_count': 5,
                    'opinions_count': 2,
                    'facts': [
                        {
                            'sentence': 'Global temperatures have risen by 1.1°C since pre-industrial times.',
                            'source_url': 'https://example.com/climate-article',
                            'source_title': 'Climate Change Report'
                        }
                    ],
                    'opinions': [
                        {
                            'sentence': 'Immediate action is necessary to prevent catastrophic warming.',
                            'source_url': 'https://example.com/climate-article',
                            'source_title': 'Climate Change Report'
                        }
                    ],
                    'raw_content': 'Climate scientists report significant warming trends...'
                },
                {
                    'url': 'https://example.com/renewable-energy',
                    'title': 'Renewable Energy Progress',
                    'domain': 'ENERGY',
                    'facts_count': 3,
                    'opinions_count': 4,
                    'facts': [
                        {
                            'sentence': 'Solar energy costs have decreased by 70% in the last decade.',
                            'source_url': 'https://example.com/renewable-energy',
                            'source_title': 'Renewable Energy Progress'
                        }
                    ],
                    'opinions': [
                        {
                            'sentence': 'Renewable energy is the future of power generation.',
                            'source_url': 'https://example.com/renewable-energy',
                            'source_title': 'Renewable Energy Progress'
                        }
                    ],
                    'raw_content': 'Renewable energy technologies have made remarkable progress...'
                },
                {
                    'url': 'https://example.com/policy-analysis',
                    'title': 'Climate Policy Analysis',
                    'domain': 'POLITICS',
                    'facts_count': 2,
                    'opinions_count': 6,
                    'facts': [
                        {
                            'sentence': 'The Paris Agreement has 195 signatory countries.',
                            'source_url': 'https://example.com/policy-analysis',
                            'source_title': 'Climate Policy Analysis'
                        }
                    ],
                    'opinions': [
                        {
                            'sentence': 'Current climate policies are insufficient to meet targets.',
                            'source_url': 'https://example.com/policy-analysis',
                            'source_title': 'Climate Policy Analysis'
                        }
                    ],
                    'raw_content': 'Climate policy frameworks around the world vary significantly...'
                }
            ],
            'results': []  
        }
        
        context = assistant.create_chat_context(multi_url_data, 'test_multi_session')
        
        print(f"✅ Multi-URL context created:")
        print(f"   - Is multi-URL analysis: {context.is_multi_url_analysis}")
        print(f"   - URLs analyzed: {len(context.multiple_urls) if context.multiple_urls else 0}")
        print(f"   - Individual results: {len(context.individual_results) if context.individual_results else 0}")
        print(f"   - Facts count: {len(context.facts)}")
        print(f"   - Opinions count: {len(context.opinions)}")
        
        multi_url_questions = [
            "How do the different sources compare in their coverage?",
            "What are the main points of agreement across all sources?",
            "Are there any contradictions between the sources?",
            "Which source provides the most reliable information?",
            "Can you provide a comprehensive summary across all sources?"
        ]
        
        for question in multi_url_questions:
            print(f"\nQ: {question}")
            answer = assistant.answer_question(question, context)
            print(f"A: {answer[:200]}...")
        
        suggestions = assistant.get_suggested_questions(context)
        print(f"\n📝 Suggested questions for multi-URL analysis:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        print("\n✅ Multi-URL chat assistant test completed successfully!")
        
    except Exception as e:
        print(f"❌ Multi-URL test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_assistant()
    test_multi_url_chat_assistant()