"""
Flask Web Application for Multi-Role Prompting System
Provides a user-friendly web interface for fact vs opinion analysis
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import time
from datetime import datetime
from clean_agents import CleanAnalysisSystem
from content_summarizer import ContentSummarizer
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global storage for analysis sessions (in-memory for demo purposes)
# In production, you'd want to use a database or persistent storage
analysis_sessions = {}

# Global system instances
analysis_system = None
content_summarizer = None

def get_system():
    """Get or create analysis system instance"""
    global analysis_system
    if analysis_system is None:
        # API key validation removed - system will handle API errors gracefully
        pass
        analysis_system = CleanAnalysisSystem()
    return analysis_system

def get_summarizer():
    """Get or create content summarizer instance"""
    global content_summarizer
    if content_summarizer is None:
        content_summarizer = ContentSummarizer()
    return content_summarizer

@app.route('/')
def index():
    """Main page - redirect to questionnaires for study flow"""
    # Check if coming from questionnaire with session data
    session_id = request.args.get('sessionId')
    from_questionnaire = request.args.get('fromQuestionnaire')
    
    if session_id and from_questionnaire:
        # Coming from pre-questionnaire, show Truth or Thought analysis
        return render_template('index.html')
    else:
        # Default: redirect to pre-questionnaire to start study
        return render_template('questionnaires.html')

@app.route('/questionnaires')
def questionnaires():
    """Research questionnaires page"""
    return render_template('questionnaires.html')

@app.route('/bias_research')
def bias_research():
    """Bias research interface"""
    return render_template('bias_research.html')

@app.route('/get_analyzed_sessions', methods=['GET'])
def get_analyzed_sessions():
    """Get all previously analyzed sessions for bias research"""
    try:
        # Get all stored sessions with analysis data
        analyzed_sessions_list = []
        
        for session_id, session_data in analysis_sessions.items():
            if 'analysis_data' in session_data:
                analysis_data = session_data['analysis_data']
                
                # Extract basic info for display
                session_info = {
                    'session_id': session_id,
                    'timestamp': session_data.get('timestamp', ''),
                    'title': analysis_data.get('title', 'Unknown Article'),
                    'domain': analysis_data.get('domain', 'Unknown'),
                    'total_facts': 0,
                    'total_opinions': 0,
                    'total_sentences': 0,
                    'url': analysis_data.get('url', ''),
                    'is_multiple': 'multiple_results' in analysis_data
                }
                
                # Calculate metrics
                if 'results' in analysis_data:
                    results = analysis_data['results']
                    session_info['total_facts'] = len([r for r in results if r.get('final_classification') == 'FACT'])
                    session_info['total_opinions'] = len([r for r in results if r.get('final_classification') == 'OPINION'])
                    session_info['total_sentences'] = len(results)
                elif 'multiple_results' in analysis_data:
                    # Handle multiple URL results
                    total_facts = 0
                    total_opinions = 0
                    total_sentences = 0
                    for result in analysis_data['multiple_results']:
                        total_facts += result.get('facts_count', 0)
                        total_opinions += result.get('opinions_count', 0)
                        total_sentences += result.get('sentences_count', 0)
                    session_info['total_facts'] = total_facts
                    session_info['total_opinions'] = total_opinions
                    session_info['total_sentences'] = total_sentences
                    session_info['title'] = f"Multi-Source Analysis ({len(analysis_data['multiple_results'])} URLs)"
                
                analyzed_sessions_list.append(session_info)
        
        # Sort by timestamp (most recent first)
        analyzed_sessions_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'sessions': analyzed_sessions_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_session_for_bias/<session_id>', methods=['GET'])
def load_session_for_bias(session_id):
    """Load a specific session's data for bias research analysis"""
    try:
        if session_id not in analysis_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = analysis_sessions[session_id]
        if 'analysis_data' not in session_data:
            return jsonify({'error': 'No analysis data in session'}), 404
        
        analysis_data = session_data['analysis_data']
        
        # Format for bias research display
        response_data = {
            'success': True,
            'session_id': session_id,
            'title': analysis_data.get('title', 'Unknown Article'),
            'domain': analysis_data.get('domain', 'Unknown'),
            'content': analysis_data.get('content', ''),
            'url': analysis_data.get('url', ''),
            'timestamp': session_data.get('timestamp', ''),
            'facts': [],
            'opinions': [],
            'total_facts': 0,
            'total_opinions': 0,
            'specialists': []
        }
        
        # Handle single URL analysis
        if 'results' in analysis_data:
            results = analysis_data['results']
            
            # Extract facts and opinions with detailed information
            for result in results:
                sentence_data = {
                    'sentence': result.get('sentence', ''),
                    'confidence': result.get('consensus_confidence', 0),
                    'reasoning': result.get('consensus_reasoning', ''),
                    'citations': result.get('citations', []),
                    'citation': result.get('citation', {})
                }
                
                if result.get('final_classification') == 'FACT':
                    response_data['facts'].append(sentence_data)
                elif result.get('final_classification') == 'OPINION':
                    response_data['opinions'].append(sentence_data)
            
            response_data['total_facts'] = len(response_data['facts'])
            response_data['total_opinions'] = len(response_data['opinions'])
        
        # Handle multiple URL analysis
        elif 'multiple_results' in analysis_data:
            print(f"DEBUG: Loading multiple results session")
            print(f"DEBUG: Found {len(analysis_data['multiple_results'])} results in session")
            
            response_data['is_multiple'] = True
            response_data['multiple_results'] = analysis_data['multiple_results']
            
            # For bias research, we need the full article content from each URL
            from scraper import NewsContentScraper
            scraper = NewsContentScraper()
            
            # Fetch full content for each URL and enhance multiple_results
            enhanced_results = []
            for i, url_result in enumerate(analysis_data['multiple_results']):
                print(f"DEBUG: Processing result {i+1}: {url_result.get('title', 'No title')} - {url_result.get('url', 'No URL')}")
                enhanced_result = url_result.copy()
                
                # Try to get full article content
                if 'url' in url_result:
                    try:
                        scraped_data = scraper.scrape_url(url_result['url'])
                        if scraped_data and scraped_data.get('content'):
                            enhanced_result['full_content'] = scraped_data['content']
                            enhanced_result['scraped_title'] = scraped_data.get('title', url_result.get('title', 'Unknown'))
                        else:
                            enhanced_result['full_content'] = url_result.get('summary', 'Content not available')
                            enhanced_result['scraped_title'] = url_result.get('title', 'Unknown')
                    except Exception as e:
                        print(f"Error scraping content for {url_result['url']}: {e}")
                        enhanced_result['full_content'] = url_result.get('summary', 'Content not available')
                        enhanced_result['scraped_title'] = url_result.get('title', 'Unknown')
                else:
                    enhanced_result['full_content'] = url_result.get('summary', 'Content not available')
                    enhanced_result['scraped_title'] = url_result.get('title', 'Unknown')
                
                enhanced_results.append(enhanced_result)
            
            response_data['multiple_results'] = enhanced_results
            
            # Aggregate facts and opinions from all sources
            all_facts = []
            all_opinions = []
            
            for url_result in enhanced_results:
                if 'facts' in url_result:
                    for fact in url_result['facts']:
                        fact['source_url'] = url_result['url']
                        fact['source_title'] = url_result['title']
                        all_facts.append(fact)
                
                if 'opinions' in url_result:
                    for opinion in url_result['opinions']:
                        opinion['source_url'] = url_result['url']
                        opinion['source_title'] = url_result['title']
                        all_opinions.append(opinion)
            
            response_data['facts'] = all_facts
            response_data['opinions'] = all_opinions
            response_data['total_facts'] = len(all_facts)
            response_data['total_opinions'] = len(all_opinions)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_for_bias', methods=['POST'])
def analyze_for_bias():
    """Enhanced analysis endpoint for bias research study"""
    try:
        data = request.get_json()
        url = data.get('url')
        participant_id = data.get('participant_id', '')
        study_mode = data.get('study_mode', 'bias_analysis')
        analysis_depth = data.get('analysis_depth', 10)
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        system = get_system()
        
        # Perform analysis with enhanced research features
        result = system.analyze_url(url)
        analysis_data = system.last_analysis_data
        
        if analysis_data:
            # Create enhanced response for research
            facts = [{'sentence': r['sentence'], 'citation': r['citation'], 'citations': r.get('citations', [])} 
                    for r in analysis_data['results'] if r['final_classification'] == 'FACT']
            opinions = [{'sentence': r['sentence']} 
                       for r in analysis_data['results'] if r['final_classification'] == 'OPINION']
            
            # Calculate research metrics
            total_statements = len(analysis_data['results'])
            fact_count = len(facts)
            opinion_count = len(opinions)
            
            confidence = 0
            if analysis_data['results']:
                total_confidence = sum(r['consensus_confidence'] for r in analysis_data['results'])
                confidence = round((total_confidence / len(analysis_data['results'])) * 100)
            
            # Enhanced bias metrics for research
            bias_metrics = {
                'fact_percentage': round((fact_count / total_statements) * 100, 2) if total_statements > 0 else 0,
                'opinion_percentage': round((opinion_count / total_statements) * 100, 2) if total_statements > 0 else 0,
                'bias_level': 'Low' if (opinion_count / total_statements if total_statements > 0 else 0) < 0.3 else 'Medium' if (opinion_count / total_statements if total_statements > 0 else 0) < 0.6 else 'High',
                'total_statements': total_statements,
                'analysis_quality': 'High' if total_statements >= analysis_depth * 0.8 else 'Medium'
            }
            
            return jsonify({
                'success': True,
                'facts': facts,
                'opinions': opinions,
                'domain': analysis_data['domain'],
                'title': analysis_data['title'],
                'content': analysis_data['content'],
                'specialists': [agent.agent_name for agent in system.agents],
                'confidence': confidence,
                'bias_metrics': bias_metrics,
                'session_id': f"research_{int(time.time())}_{participant_id}",
                'study_mode': study_mode,
                'analysis_depth': analysis_depth,
                'participant_id': participant_id,
                'analyzed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'url': url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze content'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/submit_research_data', methods=['POST'])
def submit_research_data():
    """Endpoint to receive and store research study data"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required'
            }), 400
        
        # Store research data (in a real study, this would go to a database)
        research_file = f"research_data_{session_id}.json"
        
        # Create research_data directory if it doesn't exist
        import os
        os.makedirs('research_data', exist_ok=True)
        
        # Save the complete research data
        with open(f"research_data/{research_file}", 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Research data submitted successfully',
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit research data: {str(e)}'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze URL or text content"""
    try:
        data = request.get_json()
        input_type = data.get('type')  # 'url' or 'text'
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        system = get_system()
        
        # Perform analysis
        if input_type == 'url':
            result = system.analyze_url(content)
        else:
            result = system.analyze_text(content)
        
        # Get analysis data for interactive features
        analysis_data = system.last_analysis_data
        
        # Store in session for chat
        session_id = str(uuid.uuid4())
        analysis_sessions[session_id] = {
            'analysis_data': analysis_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate confidence for single URL analysis
        confidence = 0
        if analysis_data and analysis_data.get('results'):
            total_confidence = sum(r.consensus_confidence for r in analysis_data['results'])
            confidence = round((total_confidence / len(analysis_data['results'])) * 100)
        
            return jsonify({
                'success': True,
                'result': result,
                'session_id': session_id,
                'analysis_data': {
                    'domain': analysis_data['domain'] if analysis_data else 'unknown',
                    'title': analysis_data['title'] if analysis_data else 'Unknown',
                    'facts_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'FACT']) if analysis_data else 0,
                    'opinions_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'OPINION']) if analysis_data else 0,
                'total_sentences': len(analysis_data['results']) if analysis_data else 0,
                'confidence': confidence
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_multiple', methods=['POST'])
def analyze_multiple():
    """Analyze multiple URLs with maximum information extraction"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        max_sentences = data.get('max_sentences', 15)
        analysis_mode = data.get('analysis_mode', 'combined')
        
        print(f"\n🔍 DEBUG: Received {len(urls)} URLs for analysis:")
        for i, url in enumerate(urls):
            print(f"   {i+1}. {url}")
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        if len(urls) > 10:  # Limit to prevent overload
            return jsonify({'error': 'Maximum 10 URLs allowed'}), 400
        
        system = get_system()
        
        # Store results for each URL
        individual_results = []
        all_content = []
        all_results = []
        total_facts = 0
        total_opinions = 0
        total_sentences = 0
        
        # Analyze each URL
        for i, url in enumerate(urls):
            try:
                # Analyze individual URL with max sentences limit
                print(f"\n🔍 Starting analysis for URL {i+1}/{len(urls)}: {url}", flush=True)
                print(f"📊 Analysis mode: {analysis_mode}", flush=True)
                result = system.analyze_url(url)
                analysis_data = system.last_analysis_data
                print(f"✅ Analysis completed for URL {i+1}: {url}", flush=True)
                print(f"📋 Analysis data available: {analysis_data is not None}", flush=True)
                
                if analysis_data:
                    print(f"📄 Title: {analysis_data.get('title', 'No title')}", flush=True)
                    print(f"🌐 Domain: {analysis_data.get('domain', 'No domain')}", flush=True)
                    print(f"📊 Results count: {len(analysis_data.get('results', []))}", flush=True)
                    # Generate summary for this article
                    summary = system.generate_summary(analysis_data['content'], analysis_data['title'])
                    
                    # Format content to clean markdown
                    formatted_content = system.format_content_to_markdown(analysis_data['content'], analysis_data['title'])
                    
                    print(f"🔍 DEBUG: Formatted content for URL {i+1} (first 200 chars): {formatted_content[:200]}...")
                    print(f"📏 DEBUG: Formatted content length for URL {i+1}: {len(formatted_content)} characters")
                    
                    individual_results.append({
                        'url': url,
                        'title': analysis_data['title'],
                        'domain': analysis_data['domain'],
                        'specialists': [agent.agent_name for agent in system.agents],
                        'summary': summary,
                        'analysis': result,
                        'results': analysis_data['results'],
                        'formatted_content': formatted_content,  # Add formatted markdown content
                        'raw_content': analysis_data['content'],  # Keep raw content for backup
                        'facts_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'FACT']),
                        'opinions_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'OPINION']),
                        'sentences_count': len(analysis_data['results']),
                        'facts': [{'sentence': r['sentence'], 'citation': r['citation'], 'citations': r.get('citations', []), 'source_url': r.get('source_url', url), 'source_name': r.get('source_name', 'Unknown Source')} for r in analysis_data['results'] if r['final_classification'] == 'FACT'],
                        'opinions': [{'sentence': r['sentence'], 'source_url': r.get('source_url', url), 'source_name': r.get('source_name', 'Unknown Source')} for r in analysis_data['results'] if r['final_classification'] == 'OPINION']
                    })
                    
                    # Debug: Print what we're sending
                    print(f"DEBUG: Facts count: {len([r for r in analysis_data['results'] if r['final_classification'] == 'FACT'])}")
                    print(f"DEBUG: Opinions count: {len([r for r in analysis_data['results'] if r['final_classification'] == 'OPINION'])}")
                    print(f"DEBUG: Facts: {[r['sentence'] for r in analysis_data['results'] if r['final_classification'] == 'FACT']}")
                    print(f"DEBUG: Opinions: {[r['sentence'] for r in analysis_data['results'] if r['final_classification'] == 'OPINION']}")
                    print(f"DEBUG: Domain: {analysis_data['domain']}")
                    print(f"DEBUG: Specialists: {[agent.agent_name for agent in system.agents]}")
                    
                    # Accumulate for combined analysis
                    if analysis_mode == 'combined':
                        all_content.append(analysis_data['content'])
                        all_results.extend(analysis_data['results'])
                    
                    # Update totals
                    total_facts += len([r for r in analysis_data['results'] if r['final_classification'] == 'FACT'])
                    total_opinions += len([r for r in analysis_data['results'] if r['final_classification'] == 'OPINION'])
                    total_sentences += len(analysis_data['results'])
                    
            except Exception as e:
                print(f"Error analyzing URL {url}: {str(e)}")
                individual_results.append({
                    'url': url,
                    'title': f'Error: {str(e)}',
                    'domain': 'error',
                    'specialists': [],
                    'analysis': f'Failed to analyze: {str(e)}',
                    'facts_count': 0,
                    'opinions_count': 0,
                    'sentences_count': 0,
                    'formatted_content': f'# Error\n\nFailed to analyze URL: {url}\n\nError: {str(e)}',
                    'raw_content': ''
                })
        
        print(f"DEBUG: Total individual results: {len(individual_results)}")
        for i, result in enumerate(individual_results):
            print(f"DEBUG: Result {i+1}: Title='{result.get('title', 'No Title')}' URL='{result.get('url', 'No URL')}' Domain='{result.get('domain', 'No Domain')}'")
            print(f"  Facts: {result.get('facts_count', 0)}, Opinions: {result.get('opinions_count', 0)}")
        
        print(f"DEBUG: individual_results structure before response:")
        for i, result in enumerate(individual_results):
            print(f"  Result {i+1} keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Prepare response based on analysis mode
        if analysis_mode == 'combined' and all_results:
            # Create combined analysis
            combined_content = '\n\n'.join(all_content)
            combined_result = system.formatter.format_results(all_results, 'Multi-Source Analysis', 'MULTI-SOURCE')
            
            # Store combined session data
            session_id = str(uuid.uuid4())
            analysis_sessions[session_id] = {
                'analysis_data': {
                    'content': combined_content,
                    'results': all_results,
                    'domain': 'MULTI-SOURCE',
                    'title': 'Multi-Source Analysis',
                    'multiple_results': individual_results,  # Store individual results for bias research
                    'urls': urls  # Store the original URLs
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate average confidence
            confidence = 0
            if all_results:
                total_confidence = sum(r['consensus_confidence'] for r in all_results)
                confidence = round((total_confidence / len(all_results)) * 100, 1)
            
            # Determine overall classification based on facts vs opinions count
            if total_facts > total_opinions:
                overall_classification = "FACT-DOMINANT"
            elif total_opinions > total_facts:
                overall_classification = "OPINION-DOMINANT"  
            elif total_facts == total_opinions and total_facts > 0:
                overall_classification = "BALANCED"
            else:
                overall_classification = "INCONCLUSIVE"
            
            return jsonify({
                'success': True,
                'analysis_mode': 'combined',
                'urls_analyzed': len(urls),
                'results': combined_result,
                'individual_results': individual_results,  # Add individual results for bias analysis
                'final_classification': overall_classification,
                'total_facts': total_facts,
                'total_opinions': total_opinions,
                'total_sentences': total_sentences,
                'confidence': confidence,
                'facts': [{'sentence': r['sentence'], 'citation': r['citation'], 'citations': r.get('citations', [])} for r in all_results if r['final_classification'] == 'FACT'],
                'opinions': [{'sentence': r['sentence']} for r in all_results if r['final_classification'] == 'OPINION'],
                'domain': 'MULTI-SOURCE',
                'specialists': ['Cross-Domain Analyst', 'Multi-Source Verifier', 'Consensus Expert'],
                'session_id': session_id
            })
        else:
            # Individual analysis mode - aggregate results from all successful analyses
            session_id = str(uuid.uuid4())
            
            # Use the analysis data from all successful results
            if individual_results:
                # Filter out errored results
                successful_results = [r for r in individual_results if r.get('domain') != 'error']
                
                if successful_results:
                    # Combine content and results from all successful analyses
                    combined_content = "\n\n---\n\n".join([res.get('raw_content', '') for res in successful_results])
                    combined_raw_results = []
                    for res in successful_results:
                        # The 'results' key holds the detailed results objects
                        if 'results' in res:
                            combined_raw_results.extend(res['results'])

                    analysis_sessions[session_id] = {
                        'analysis_data': {
                            'content': combined_content,
                            'results': combined_raw_results,
                            'domain': 'MULTI-SOURCE-INDIVIDUAL',
                            'title': f'Individual Analysis of {len(successful_results)} Sources',
                            'multiple_results': individual_results,
                            'urls': urls
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # Handle case where all URLs failed
                    analysis_sessions[session_id] = {
                        'analysis_data': { 'multiple_results': individual_results, 'urls': urls },
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                # Fallback if no results at all
                analysis_sessions[session_id] = {
                    'analysis_data': { 'urls': urls },
                    'timestamp': datetime.now().isoformat()
                }

            # Get the domain and specialists from the first successful result
            first_successful_result = next((r for r in individual_results if r.get('domain') != 'error'), None)
            detected_domain = first_successful_result.get('domain', 'GENERAL') if first_successful_result else 'GENERAL'
            detected_specialists = first_successful_result.get('specialists', ['General Analyst']) if first_successful_result else ['General Analyst']
            
            # Collect all facts and opinions from individual results for display
            all_facts = []
            all_opinions = []
            for result in individual_results:
                if result.get('facts'):
                    all_facts.extend(result['facts'])
                if result.get('opinions'):
                    all_opinions.extend(result['opinions'])
            
            return jsonify({
                'success': True,
                'analysis_mode': 'individual',
                'urls_analyzed': len(urls),
                'results': individual_results,
                'individual_results': individual_results,
                'multiple_results': individual_results,
                'facts': all_facts,
                'opinions': all_opinions,
                'total_facts': total_facts,
                'total_opinions': total_opinions,
                'total_sentences': total_sentences,
                'domain': detected_domain,
                'specialists': detected_specialists,
                'session_id': session_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat questions about analysis"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question = data.get('question')
        
        if not session_id or session_id not in session:
            return jsonify({'error': 'Invalid session'}), 400
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get analysis data from session
        analysis_data = analysis_sessions[session_id]['analysis_data']
        
        # Debug: Print session data info
        print(f"DEBUG: Session analysis data keys: {analysis_data.keys()}")
        print(f"DEBUG: Results type: {type(analysis_data['results'])}")
        print(f"DEBUG: Results length: {len(analysis_data['results']) if analysis_data['results'] else 0}")
        print(f"DEBUG: Domain: {analysis_data['domain']}")
        print(f"DEBUG: Title: {analysis_data['title']}")
        
        # Create chat interface
        from multi_role_prompting_system import ChatInterface
        chat_interface = ChatInterface(
            analysis_data['content'],
            analysis_data['results'],
            analysis_data['domain'],
            analysis_data['title']
        )
        
        # Get answer
        answer = chat_interface._answer_question(question)
        
        return jsonify({
            'success': True,
            'answer': answer
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize_content', methods=['POST'])
def summarize_content():
    """Summarize content to extract key personnel, quotes, and insights"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', '')
        domain = data.get('domain', 'GENERAL')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        summarizer = get_summarizer()
        summary = summarizer.summarize_content(content, title, domain)
        
        # Convert dataclass objects to dictionaries for JSON serialization
        summary_dict = {
            'key_personnel': [
                {
                    'name': p.name,
                    'title': p.title,
                    'organization': p.organization,
                    'role_in_story': p.role_in_story,
                    'quotes': p.quotes,
                    'relevance_score': p.relevance_score
                } for p in summary.key_personnel
            ],
            'important_quotes': [
                {
                    'quote': q.quote,
                    'speaker': q.speaker,
                    'speaker_title': q.speaker_title,
                    'context': q.context,
                    'significance': q.significance,
                    'impact_score': q.impact_score
                } for q in summary.important_quotes
            ],
            'key_insights': [
                {
                    'insight': i.insight,
                    'category': i.category,
                    'supporting_evidence': i.supporting_evidence,
                    'importance_score': i.importance_score
                } for i in summary.key_insights
            ],
            'main_themes': summary.main_themes,
            'executive_summary': summary.executive_summary,
            'content_type': summary.content_type,
            'credibility_indicators': summary.credibility_indicators
        }
        
        return jsonify({
            'success': True,
            'summary': summary_dict
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize_session/<session_id>', methods=['POST'])
def summarize_session(session_id):
    """Summarize content from an existing analysis session"""
    try:
        if session_id not in analysis_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = analysis_sessions[session_id]
        if 'analysis_data' not in session_data:
            return jsonify({'error': 'No analysis data in session'}), 404
        
        analysis_data = session_data['analysis_data']
        summarizer = get_summarizer()
        
        # Handle single URL analysis
        if 'content' in analysis_data and 'multiple_results' not in analysis_data:
            content = analysis_data.get('content', '')
            title = analysis_data.get('title', '')
            domain = analysis_data.get('domain', 'GENERAL')
            
            summary = summarizer.summarize_content(content, title, domain)
            
            # Convert to dictionary
            summary_dict = {
                'key_personnel': [
                    {
                        'name': p.name,
                        'title': p.title,
                        'organization': p.organization,
                        'role_in_story': p.role_in_story,
                        'quotes': p.quotes,
                        'relevance_score': p.relevance_score
                    } for p in summary.key_personnel
                ],
                'important_quotes': [
                    {
                        'quote': q.quote,
                        'speaker': q.speaker,
                        'speaker_title': q.speaker_title,
                        'context': q.context,
                        'significance': q.significance,
                        'impact_score': q.impact_score
                    } for q in summary.important_quotes
                ],
                'key_insights': [
                    {
                        'insight': i.insight,
                        'category': i.category,
                        'supporting_evidence': i.supporting_evidence,
                        'importance_score': i.importance_score
                    } for i in summary.key_insights
                ],
                'main_themes': summary.main_themes,
                'executive_summary': summary.executive_summary,
                'content_type': summary.content_type,
                'credibility_indicators': summary.credibility_indicators
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'summary_type': 'single_source',
                'summary': summary_dict
            })
        
        # Handle multiple URL analysis
        elif 'multiple_results' in analysis_data:
            multiple_results = analysis_data['multiple_results']
            
            # Prepare sources for multi-source summarization
            sources = []
            for result in multiple_results:
                if result.get('domain') != 'error':  # Skip failed analyses
                    sources.append({
                        'content': result.get('formatted_content', result.get('raw_content', '')),
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'domain': result.get('domain', 'GENERAL')
                    })
            
            if not sources:
                return jsonify({'error': 'No valid sources found for summarization'}), 400
            
            # Generate multi-source summary
            multi_summary = summarizer.summarize_multiple_sources(sources)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'summary_type': 'multi_source',
                'summary': multi_summary
            })
        
        else:
            return jsonify({'error': 'No content available for summarization'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)