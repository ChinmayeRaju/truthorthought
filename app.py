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
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global system instance
analysis_system = None

def get_system():
    """Get or create analysis system instance"""
    global analysis_system
    if analysis_system is None:
        # API key validation removed - system will handle API errors gracefully
        pass
        analysis_system = CleanAnalysisSystem()
    return analysis_system

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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
        session[session_id] = {
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
                print(f"\n🔍 Starting analysis for: {url}", flush=True)
                print(f"📊 Analysis mode: {analysis_mode}", flush=True)
                result = system.analyze_url(url)
                analysis_data = system.last_analysis_data
                print(f"✅ Analysis completed for: {url}", flush=True)
                
                if analysis_data:
                    # Generate summary for this article
                    summary = system.generate_summary(analysis_data['content'], analysis_data['title'])
                    
                    individual_results.append({
                        'url': url,
                        'title': analysis_data['title'],
                        'domain': analysis_data['domain'],
                        'specialists': [agent.agent_name for agent in system.agents],
                        'summary': summary,
                        'analysis': result,
                        'facts_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'FACT']),
                        'opinions_count': len([r for r in analysis_data['results'] if r['final_classification'] == 'OPINION']),
                        'sentences_count': len(analysis_data['results']),
                        'facts': [{'sentence': r['sentence'], 'citation': r['citation']} for r in analysis_data['results'] if r['final_classification'] == 'FACT'],
                        'opinions': [{'sentence': r['sentence']} for r in analysis_data['results'] if r['final_classification'] == 'OPINION']
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
                    'sentences_count': 0
                })
        
        # Prepare response based on analysis mode
        if analysis_mode == 'combined' and all_results:
            # Create combined analysis
            combined_content = '\n\n'.join(all_content)
            combined_result = system.formatter.format_results(all_results, 'Combined Multi-Source Analysis', 'MULTI-SOURCE')
            
            # Store combined session data
            session_id = str(uuid.uuid4())
            session[session_id] = {
                'analysis_data': {
                    'content': combined_content,
                    'results': all_results,
                    'domain': 'MULTI-SOURCE',
                    'title': 'Combined Multi-Source Analysis'
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
                'final_classification': overall_classification,
                'total_facts': total_facts,
                'total_opinions': total_opinions,
                'total_sentences': total_sentences,
                'confidence': confidence,
                'facts': [{'sentence': r['sentence'], 'citation': r['citation']} for r in all_results if r['final_classification'] == 'FACT'],
                'opinions': [{'sentence': r['sentence']} for r in all_results if r['final_classification'] == 'OPINION'],
                'domain': 'MULTI-SOURCE',
                'specialists': ['Cross-Domain Analyst', 'Multi-Source Verifier', 'Consensus Expert'],
                'session_id': session_id
            })
        else:
            # Individual analysis mode - use the actual analysis data from the single URL
            session_id = str(uuid.uuid4())
            if individual_results:
                # Use the analysis data from the first (and only) result
                first_result = individual_results[0]
                # Get the original analysis data for this URL
                last_analysis = system.last_analysis_data
                
                session[session_id] = {
                    'analysis_data': {
                        'content': last_analysis['content'] if last_analysis else first_result.get('title', ''),
                        'results': last_analysis['results'] if last_analysis else [],
                        'domain': last_analysis['domain'] if last_analysis else first_result.get('domain', 'UNKNOWN'),
                        'title': last_analysis['title'] if last_analysis else first_result.get('title', 'Individual Analysis')
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback if no results
                session[session_id] = {
                    'analysis_data': {
                        'content': '',
                        'results': [],
                        'domain': 'UNKNOWN',
                        'title': 'Individual Analysis'
                    },
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
                'facts': all_facts,  # Add facts array for frontend
                'opinions': all_opinions,  # Add opinions array for frontend
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
        analysis_data = session[session_id]['analysis_data']
        
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

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)