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
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from study_data_manager import study_data_manager

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global storage for analysis sessions with file persistence
analysis_sessions = {}

def load_analysis_sessions():
    """Load analysis sessions from disk"""
    global analysis_sessions
    try:
        if os.path.exists('analysis_sessions.json'):
            with open('analysis_sessions.json', 'r') as f:
                analysis_sessions = json.load(f)
                print(f"Loaded {len(analysis_sessions)} analysis sessions from disk")
        else:
            analysis_sessions = {}
            print("No existing analysis sessions file found, starting fresh")
    except Exception as e:
        print(f"Error loading analysis sessions: {e}")
        analysis_sessions = {}

def save_analysis_sessions():
    """Save analysis sessions to disk"""
    try:
        with open('analysis_sessions.json', 'w') as f:
            json.dump(analysis_sessions, f, indent=2)
        print(f"Saved {len(analysis_sessions)} analysis sessions to disk")
    except Exception as e:
        print(f"Error saving analysis sessions: {e}")

# Load existing sessions on startup
load_analysis_sessions()

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
        # Force reload sessions from disk to ensure we have the latest data
        load_analysis_sessions()
        
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
                    'is_multiple': 'multiple_results' in analysis_data or ('urls' in analysis_data and len(analysis_data.get('urls', [])) > 1)
                }
                
                # Calculate metrics - check for multi-source sessions first
                if 'multiple_results' in analysis_data:
                    # Handle multiple URL results
                    total_facts = 0
                    total_opinions = 0
                    total_sentences = 0
                    urls = []
                    
                    # First, try to get URLs from the direct 'urls' field (saved by analyze_multiple)
                    if 'urls' in analysis_data and analysis_data['urls']:
                        urls = analysis_data['urls']
                    
                    # Process individual results for metrics
                    for i, result in enumerate(analysis_data['multiple_results']):
                        facts_count = result.get('facts_count', 0)
                        opinions_count = result.get('opinions_count', 0)
                        sentences_count = result.get('sentences_count', 0)
                        url = result.get('url', '')
                        total_facts += facts_count
                        total_opinions += opinions_count
                        total_sentences += sentences_count
                        
                        # If we didn't get URLs from the direct field, collect them from individual results
                        if not urls and url:
                            urls.append(url)
                    
                    session_info['total_facts'] = total_facts
                    session_info['total_opinions'] = total_opinions
                    session_info['total_sentences'] = total_sentences
                    session_info['title'] = f"Multi-Source Analysis ({len(urls)} URLs)" if urls else f"Multi-Source Analysis ({len(analysis_data['multiple_results'])} URLs)"
                    # For multi-source, include the URLs as a comma-separated string or array
                    session_info['url'] = urls[0] if len(urls) == 1 else ', '.join(urls) if urls else ''
                    session_info['urls'] = urls  # Also include as array for frontend
                elif 'urls' in analysis_data and len(analysis_data.get('urls', [])) > 1:
                    # Handle sessions with multiple URLs but no multiple_results (individual analysis mode)
                    urls = analysis_data['urls']
                    
                    # Use the regular results array for metrics since there's no multiple_results
                    if 'results' in analysis_data and len(analysis_data['results']) > 0:
                        results = analysis_data['results']
                        session_info['total_facts'] = len([r for r in results if r.get('final_classification') == 'FACT'])
                        session_info['total_opinions'] = len([r for r in results if r.get('final_classification') == 'OPINION'])
                        session_info['total_sentences'] = len(results)
                    
                    session_info['title'] = f"Multi-Source Analysis ({len(urls)} URLs)"
                    session_info['url'] = ', '.join(urls) if isinstance(urls, list) else str(urls)
                    session_info['urls'] = urls  # Also include as array for frontend
                elif 'results' in analysis_data and len(analysis_data['results']) > 0:
                    results = analysis_data['results']
                    session_info['total_facts'] = len([r for r in results if r.get('final_classification') == 'FACT'])
                    session_info['total_opinions'] = len([r for r in results if r.get('final_classification') == 'OPINION'])
                    session_info['total_sentences'] = len(results)
                
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
        # Force reload sessions from disk to ensure we have the latest data
        load_analysis_sessions()
        
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
        
        # Handle multiple URL analysis (with multiple_results)
        if 'multiple_results' in analysis_data:
            response_data['is_multiple'] = True
            response_data['multiple_results'] = analysis_data['multiple_results']
            
            # Extract URLs from the direct 'urls' field if available
            if 'urls' in analysis_data:
                response_data['urls'] = analysis_data['urls']
            
            # For bias research, we need the full article content from each URL
            from scraper import NewsContentScraper
            scraper = NewsContentScraper()
            
            # Fetch full content for each URL and enhance multiple_results
            enhanced_results = []
            for i, url_result in enumerate(analysis_data['multiple_results']):
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
        
        # Handle sessions with multiple URLs but no multiple_results (individual analysis mode)
        elif 'urls' in analysis_data and len(analysis_data.get('urls', [])) > 1:
            print(f"DEBUG: Loading multi-URL session without multiple_results")
            print(f"DEBUG: Found URLs: {analysis_data['urls']}")
            
            response_data['is_multiple'] = True
            response_data['urls'] = analysis_data['urls']
            response_data['title'] = f"Multi-Source Analysis ({len(analysis_data['urls'])} URLs)"
            
            # For this type of session, the results are in the regular 'results' array
            # but they represent analysis from multiple sources
            if 'results' in analysis_data and len(analysis_data['results']) > 0:
                results = analysis_data['results']
                
                # Extract facts and opinions with detailed information
                for result in results:
                    sentence_data = {
                        'sentence': result.get('sentence', ''),
                        'confidence': result.get('consensus_confidence', 0),
                        'reasoning': result.get('consensus_reasoning', ''),
                        'citations': result.get('citations', []),
                        'citation': result.get('citation', {}),
                        'source_url': result.get('source_url', ''),
                        'source_name': result.get('source_name', '')
                    }
                    
                    if result.get('final_classification') == 'FACT':
                        response_data['facts'].append(sentence_data)
                    elif result.get('final_classification') == 'OPINION':
                        response_data['opinions'].append(sentence_data)
                
                response_data['total_facts'] = len(response_data['facts'])
                response_data['total_opinions'] = len(response_data['opinions'])
        
        # Handle single URL analysis
        elif 'results' in analysis_data and len(analysis_data['results']) > 0:
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
        
        # Handle multiple URL analysis (with multiple_results)
        elif 'multiple_results' in analysis_data:
            print(f"DEBUG: Loading multiple results session")
            print(f"DEBUG: Found {len(analysis_data['multiple_results'])} results in session")
            
            response_data['is_multiple'] = True
            response_data['multiple_results'] = analysis_data['multiple_results']
            
            # Extract URLs from the direct 'urls' field if available
            if 'urls' in analysis_data:
                response_data['urls'] = analysis_data['urls']
                print(f"DEBUG: Found URLs in analysis_data: {analysis_data['urls']}")
            
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
        
        # Handle sessions with multiple URLs but no multiple_results (individual analysis mode)
        elif 'urls' in analysis_data and len(analysis_data.get('urls', [])) > 1:
            print(f"DEBUG: Loading multi-URL session without multiple_results")
            print(f"DEBUG: Found URLs: {analysis_data['urls']}")
            
            response_data['is_multiple'] = True
            response_data['urls'] = analysis_data['urls']
            response_data['title'] = f"Multi-Source Analysis ({len(analysis_data['urls'])} URLs)"
            
            # For this type of session, the results are in the regular 'results' array
            # but they represent analysis from multiple sources
            if 'results' in analysis_data and len(analysis_data['results']) > 0:
                results = analysis_data['results']
                
                # Extract facts and opinions with detailed information
                for result in results:
                    sentence_data = {
                        'sentence': result.get('sentence', ''),
                        'confidence': result.get('consensus_confidence', 0),
                        'reasoning': result.get('consensus_reasoning', ''),
                        'citations': result.get('citations', []),
                        'citation': result.get('citation', {}),
                        'source_url': result.get('source_url', ''),
                        'source_name': result.get('source_name', '')
                    }
                    
                    if result.get('final_classification') == 'FACT':
                        response_data['facts'].append(sentence_data)
                    elif result.get('final_classification') == 'OPINION':
                        response_data['opinions'].append(sentence_data)
                
                response_data['total_facts'] = len(response_data['facts'])
                response_data['total_opinions'] = len(response_data['opinions'])
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug_session/<session_id>', methods=['GET'])
def debug_session(session_id):
    """Debug endpoint to see raw session data"""
    try:
        # Force reload sessions from disk
        load_analysis_sessions()
        
        if session_id not in analysis_sessions:
            return jsonify({'error': 'Session not found', 'available_sessions': list(analysis_sessions.keys())}), 404
        
        session_data = analysis_sessions[session_id]
        return jsonify({
            'session_id': session_id,
            'session_data': session_data,
            'analysis_data_keys': list(session_data.get('analysis_data', {}).keys()) if 'analysis_data' in session_data else [],
            'has_multiple_results': 'multiple_results' in session_data.get('analysis_data', {}),
            'multiple_results_count': len(session_data.get('analysis_data', {}).get('multiple_results', [])),
            'multiple_results_sample': session_data.get('analysis_data', {}).get('multiple_results', [])[:1] if session_data.get('analysis_data', {}).get('multiple_results') else []
        })
        
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
        save_analysis_sessions()  # Persist to disk
        
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
            save_analysis_sessions()  # Persist to disk
            
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
                    save_analysis_sessions()  # Persist to disk
                else:
                    # Handle case where all URLs failed
                    analysis_sessions[session_id] = {
                        'analysis_data': { 'multiple_results': individual_results, 'urls': urls },
                        'timestamp': datetime.now().isoformat()
                    }
                    save_analysis_sessions()  # Persist to disk
            else:
                # Fallback if no results at all
                analysis_sessions[session_id] = {
                    'analysis_data': { 'urls': urls },
                    'timestamp': datetime.now().isoformat()
                }
                save_analysis_sessions()  # Persist to disk

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
    """Handle chat questions about analysis using intelligent assistant"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question = data.get('question')
        
        if not session_id or session_id not in analysis_sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if not question or not question.strip():
            return jsonify({'error': 'No question provided'}), 400
        
        # Get analysis data from session
        analysis_data = analysis_sessions[session_id]['analysis_data']
        
        # Debug: Print session data info
        print(f"🤖 Chat request for session: {session_id}")
        print(f"📝 Question: {question}")
        print(f"📊 Analysis data available: {bool(analysis_data)}")
        
        # Create intelligent chat assistant
        from intelligent_chat_assistant import IntelligentChatAssistant
        assistant = IntelligentChatAssistant()
        
        # Create chat context from analysis data
        context = assistant.create_chat_context(analysis_data, session_id)
        
        # Get intelligent response
        answer = assistant.answer_question(question, context)
        
        # Get suggested follow-up questions
        suggestions = assistant.get_suggested_questions(context)
        
        print(f"✅ Generated response length: {len(answer)} characters")
        
        return jsonify({
            'success': True,
            'answer': answer,
            'suggested_questions': suggestions[:4],  # Limit to 4 suggestions
            'context_info': {
                'facts_count': len(context.facts),
                'opinions_count': len(context.opinions),
                'domain': context.domain,
                'has_verified_sources': context.analysis_summary.get('has_verified_sources', False)
            }
        })
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return helpful error message
        return jsonify({
            'success': False,
            'error': 'I apologize, but I encountered an issue processing your question. Please try rephrasing your question or ask about a different aspect of the analysis.',
            'suggested_questions': [
                'What are the main facts in this article?',
                'Can you summarize the key points?',
                'What sources support the claims made?',
                'Are there any potential biases in this content?'
            ]
        }), 500

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

def save_questionnaire_to_excel(questionnaire_data, questionnaire_type):
    """Save questionnaire data to Excel file"""
    try:
        # Create questionnaires directory if it doesn't exist
        os.makedirs('questionnaire_data', exist_ok=True)
        
        # Define Excel file path
        excel_file = 'questionnaire_data/truth_or_thought_research_data.xlsx'
        
        # Load existing workbook or create new one
        try:
            wb = load_workbook(excel_file)
        except FileNotFoundError:
            wb = Workbook()
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
        
        # Create or get worksheet for this questionnaire type
        sheet_name = f"{questionnaire_type.title()}_Questionnaire"
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.create_sheet(sheet_name)
            
            # Create headers based on questionnaire type - OPTIMIZED FOR RESEARCH VALUE
            if questionnaire_type == 'pre':
                headers = [
                    'Session_ID', 'Timestamp', 'User_ID',
                    'News_Frequency', 'Fact_Opinion_Confidence_Baseline', 'AI_Familiarity_Tools',
                    'Age', 'Profession', 'Tech_Experience'
                ]
            elif questionnaire_type == 'post':
                headers = [
                    'Session_ID', 'Timestamp', 'User_ID',
                    # Truth or Thought Effectiveness Metrics
                    'Perspective_Awareness_Improvement', 'Bias_Detection_Improvement', 'Objective_Subjective_Clarity',
                    # Usability & Efficiency Metrics
                    'Quick_Evaluation', 'Effort_vs_Expected', 'Time_Efficiency', 'Clarity_Rating',
                    # Trust & Adoption Metrics
                    'Future_Usage_Intent', 'Recommendation_Likelihood', 'Trust_In_Analysis', 'Vs_Traditional_Methods',
                    # Feature Value Assessment
                    'Most_Helpful_Feature', 'Tool_Effectiveness_Rating',
                    # Article Familiarity Assessment
                    'Article_Familiarity', 'Familiarity_Bias_Impact', 'Model_Effectiveness_New_Content'
                ]
            else:  # exit questionnaire
                headers = [
                    'Session_ID', 'Timestamp', 'User_ID',
                    'Task_Preference', 'Bias_Detection_Task_Difference', 'Personnel_Influence_Rating',
                    'Overall_Tool_Value', 'Research_Feedback'
                ]
            
            # Add headers with styling
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
        
        # Find next empty row
        next_row = ws.max_row + 1
        
        # Extract data based on questionnaire type
        session_id = questionnaire_data.get('sessionId', f"session_{int(time.time())}")
        timestamp = questionnaire_data.get('timestamp', datetime.now().isoformat())
        q_type = questionnaire_data.get('type', questionnaire_type)
        
        # Extract user ID from session for tracking
        user_id = session_id.split('_')[0] if '_' in session_id else session_id
        
        if questionnaire_type == 'pre':
            row_data = [
                session_id, timestamp, user_id,
                questionnaire_data.get('newsFrequency', ''),
                questionnaire_data.get('factOpinionConfidence', ''),
                questionnaire_data.get('aiFamiliarityTools', ''),
                questionnaire_data.get('age', ''),
                questionnaire_data.get('profession', ''),
                questionnaire_data.get('techExperience', '')
            ]
        elif questionnaire_type == 'post':
            row_data = [
                session_id, timestamp, user_id,
                # Truth or Thought Effectiveness Metrics
                questionnaire_data.get('perspectiveAwareness', ''),
                questionnaire_data.get('biasDetectionImprovement', ''),
                questionnaire_data.get('objectiveSubjectiveClarity', ''),
                # Usability & Efficiency Metrics
                questionnaire_data.get('quickEvaluation', ''),
                questionnaire_data.get('lessEffortThanExpected', ''),
                questionnaire_data.get('timeConsumingQuick', ''),
                questionnaire_data.get('confusingClear', ''),
                # Trust & Adoption Metrics
                questionnaire_data.get('futureUsage', ''),
                questionnaire_data.get('recommendToOthers', ''),
                questionnaire_data.get('trustInAnalysis', ''),
                questionnaire_data.get('comparedToTraditional', ''),
                # Feature Value Assessment
                ', '.join(questionnaire_data.get('mostHelpfulFeature', [])) if isinstance(questionnaire_data.get('mostHelpfulFeature'), list) else questionnaire_data.get('mostHelpfulFeature', ''),
                questionnaire_data.get('factOpinionClarity', ''),  # Overall effectiveness rating
                # Article Familiarity Assessment
                questionnaire_data.get('articleFamiliarity', ''),
                questionnaire_data.get('familiarityBiasImpact', ''),
                questionnaire_data.get('modelEffectivenessNewContent', '')
            ]
        else:  # exit questionnaire
            row_data = [
                session_id, timestamp, user_id,
                questionnaire_data.get('taskPreference', ''),
                questionnaire_data.get('biasDetectionDifference', ''),
                questionnaire_data.get('personnelInfluence', ''),
                questionnaire_data.get('overallToolValue', ''),
                questionnaire_data.get('additionalComments', '')
            ]
        
        # Add data to worksheet
        for col, value in enumerate(row_data, 1):
            ws.cell(row=next_row, column=col, value=value)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save workbook
        wb.save(excel_file)
        return True, excel_file
        
    except Exception as e:
        return False, str(e)

@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    """Enhanced questionnaire submission endpoint using study data manager"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        questionnaire_type = data.get('type')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required'
            }), 400
        
        if not questionnaire_type:
            return jsonify({
                'success': False,
                'error': 'Questionnaire type is required'
            }), 400
        
        # Save using study data manager
        success = study_data_manager.save_questionnaire_data(session_id, questionnaire_type, data)
        
        if success:
            # Also save to Excel for backward compatibility
            try:
                save_questionnaire_to_excel(data, questionnaire_type)
            except Exception as e:
                print(f"Warning: Failed to save to Excel: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Questionnaire data saved successfully',
                'session_id': session_id,
                'file_path': f'research_data/participants.json'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save questionnaire data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit questionnaire: {str(e)}'
        }), 500

@app.route('/api/submit_questionnaire', methods=['POST'])
def api_submit_questionnaire():
    """API version of questionnaire submission endpoint"""
    return submit_questionnaire()

@app.route('/api/analyze_multiple', methods=['POST'])
def api_analyze_multiple():
    """API version of analyze_multiple endpoint"""
    return analyze_multiple()

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API version of analyze endpoint"""
    return analyze()

@app.route('/api/analyze_for_bias', methods=['POST'])
def api_analyze_for_bias():
    """API version of analyze_for_bias endpoint"""
    return analyze_for_bias()

@app.route('/api/get_analyzed_sessions', methods=['GET'])
def api_get_analyzed_sessions():
    """API version of get_analyzed_sessions endpoint"""
    return get_analyzed_sessions()

@app.route('/api/load_session_for_bias/<session_id>', methods=['GET'])
def api_load_session_for_bias(session_id):
    """API version of load_session_for_bias endpoint"""
    return load_session_for_bias(session_id)

@app.route('/api/submit_research_data', methods=['POST'])
def api_submit_research_data():
    """API version of submit_research_data endpoint"""
    return submit_research_data()

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API version of chat endpoint"""
    return chat()

@app.route('/api/summarize_content', methods=['POST'])
def api_summarize_content():
    """API version of summarize_content endpoint"""
    return summarize_content()

@app.route('/api/summarize_session/<session_id>', methods=['POST'])
def api_summarize_session(session_id):
    """API version of summarize_session endpoint"""
    return summarize_session(session_id)

@app.route('/api/health', methods=['GET'])
def api_health():
    """API version of health endpoint"""
    return health()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Study data manager imported at top of file

@app.route('/api/get_study_data', methods=['GET'])
def get_study_data():
    """Get all study data for research dashboard"""
    try:
        participants = study_data_manager.get_all_participants()
        stats = study_data_manager.get_study_statistics()
        
        # Convert participants to serializable format
        participants_data = []
        for participant in participants:
            participant_dict = {
                'session_id': participant.session_id,
                'participant_id': participant.participant_id,
                'start_time': participant.start_time,
                'end_time': participant.end_time,
                'has_comprehensive_pre': participant.comprehensive_pre is not None,
                'has_research_pre': participant.research_pre is not None,
                'has_research_post': participant.research_post is not None,
                'has_exit_questionnaire': participant.exit_questionnaire is not None,
                'comprehensive_pre': participant.comprehensive_pre,
                'research_pre': participant.research_pre,
                'research_post': participant.research_post,
                'exit_questionnaire': participant.exit_questionnaire,
                'analysis_sessions': participant.analysis_sessions,
                'num_interactions': len(participant.interactions)
            }
            participants_data.append(participant_dict)
        
        return jsonify({
            'success': True,
            'participants': participants_data,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get study data: {str(e)}'
        }), 500

@app.route('/api/export_study_data', methods=['POST'])
def export_study_data():
    """Export study data to CSV files based on export type"""
    try:
        data = request.get_json()
        export_type = data.get('export_type', 'all')  # 'all', 'pre_questionnaires', 'post_questionnaires', 'exit_questionnaires', 'sessions', 'interactions'
        
        # Choose the appropriate export method based on type
        if export_type == 'pre_questionnaires':
            exported_files = study_data_manager.export_pre_questionnaires_only()
        elif export_type == 'post_questionnaires':
            exported_files = study_data_manager.export_post_questionnaires_only()
        elif export_type == 'exit_questionnaires':
            exported_files = study_data_manager.export_exit_questionnaires_only()
        elif export_type == 'sessions':
            exported_files = study_data_manager.export_sessions_only()
        elif export_type == 'interactions':
            exported_files = study_data_manager.export_interactions_only()
        else:  # 'all' or any other value
            exported_files = study_data_manager.export_to_csv()
        
        if exported_files:
            return jsonify({
                'success': True,
                'message': f'{export_type.replace("_", " ").title()} data exported successfully',
                'files': exported_files
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No {export_type.replace("_", " ")} data to export'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to export {export_type.replace("_", " ")} data: {str(e)}'
        }), 500

@app.route('/api/download_export/<filename>', methods=['GET'])
def download_export(filename):
    """Download exported CSV file"""
    try:
        # Security: Only allow downloading from the research_data directory
        safe_filename = os.path.basename(filename)  # Remove any path traversal attempts
        file_path = os.path.join('research_data', safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file as attachment
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

@app.route('/api/log_interaction', methods=['POST'])
def log_interaction():
    """Log user interaction for research purposes"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        interaction_type = data.get('type')
        interaction_data = data.get('data', {})
        
        if not session_id or not interaction_type:
            return jsonify({
                'success': False,
                'error': 'Session ID and interaction type are required'
            }), 400
        
        success = study_data_manager.log_interaction(session_id, interaction_type, interaction_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Interaction logged successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to log interaction'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to log interaction: {str(e)}'
        }), 500

@app.route('/api/get_participant_data/<session_id>', methods=['GET'])
def get_participant_data(session_id):
    """Get specific participant data"""
    try:
        participant = study_data_manager.get_participant(session_id)
        
        if not participant:
            return jsonify({
                'success': False,
                'error': 'Participant not found'
            }), 404
        
        participant_data = {
            'session_id': participant.session_id,
            'participant_id': participant.participant_id,
            'start_time': participant.start_time,
            'end_time': participant.end_time,
            'comprehensive_pre': participant.comprehensive_pre,
            'research_pre': participant.research_pre,
            'research_post': participant.research_post,
            'exit_questionnaire': participant.exit_questionnaire,
            'analysis_sessions': participant.analysis_sessions,
            'interactions': participant.interactions
        }
        
        return jsonify({
            'success': True,
            'participant': participant_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get participant data: {str(e)}'
        }), 500

# Enhanced analysis endpoint that integrates with study data manager
@app.route('/api/analyze_with_tracking', methods=['POST'])
def analyze_with_tracking():
    """Analyze content and track in study data manager"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        content = data.get('content')
        content_type = data.get('type', 'url')
        
        if not session_id or not content:
            return jsonify({
                'success': False,
                'error': 'Session ID and content are required'
            }), 400
        
        system = get_system()
        
        # Perform analysis
        if content_type == 'url':
            result = system.analyze_url(content)
        else:
            result = system.analyze_text(content)
        
        analysis_data = system.last_analysis_data
        
        if analysis_data:
            # Save analysis session to study data manager
            study_data_manager.save_analysis_session(session_id, analysis_data)
            
            # Log the analysis interaction
            study_data_manager.log_interaction(session_id, 'analysis', {
                'content_type': content_type,
                'content': content[:200] + '...' if len(content) > 200 else content,
                'analysis_result': {
                    'total_facts': len([r for r in analysis_data.get('results', []) if r.get('final_classification') == 'FACT']),
                    'total_opinions': len([r for r in analysis_data.get('results', []) if r.get('final_classification') == 'OPINION']),
                    'domain': analysis_data.get('domain'),
                    'title': analysis_data.get('title')
                }
            })
            
            # Format response similar to existing analyze endpoint
            facts = [{'sentence': r['sentence'], 'citation': r.get('citation', {}), 'citations': r.get('citations', [])}
                    for r in analysis_data['results'] if r['final_classification'] == 'FACT']
            opinions = [{'sentence': r['sentence']}
                       for r in analysis_data['results'] if r['final_classification'] == 'OPINION']
            
            return jsonify({
                'success': True,
                'facts': facts,
                'opinions': opinions,
                'domain': analysis_data['domain'],
                'title': analysis_data['title'],
                'content': analysis_data['content'],
                'specialists': [agent.agent_name for agent in system.agents],
                'confidence': analysis_data.get('confidence', 0),
                'session_id': session_id,
                'total_facts': len(facts),
                'total_opinions': len(opinions),
                'total_sentences': len(analysis_data['results'])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze content'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to analyze content: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)