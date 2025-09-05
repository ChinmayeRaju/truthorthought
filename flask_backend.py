#!/usr/bin/env python3
"""
Simple Flask Backend for Truth or Thought Questionnaire Submission
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from study_data_manager import StudyDataManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

study_data_manager = StudyDataManager()

@app.route('/api/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    """Submit questionnaire data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        logger.info(f"Received questionnaire submission: {data.get('type', 'unknown')}")
        
        # Save questionnaire data
        success = study_data_manager.save_questionnaire_data(data)
        
        if success:
            logger.info("Questionnaire saved successfully")
            return jsonify({
                'success': True, 
                'message': 'Questionnaire saved successfully',
                'session_id': data.get('sessionId', data.get('session_id', 'unknown'))
            })
        else:
            logger.error("Failed to save questionnaire")
            return jsonify({'success': False, 'message': 'Failed to save questionnaire'}), 500
            
    except Exception as e:
        logger.error(f"Error submitting questionnaire: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get_study_data')
def get_study_data():
    """Get all study data for the research dashboard"""
    try:
        participants = study_data_manager.get_all_participants()
        stats = study_data_manager.get_study_statistics()
        
        participant_data = []
        for participant in participants:
            participant_data.append({
                'session_id': participant.session_id,
                'participant_id': participant.participant_id,
                'start_time': participant.start_time,
                'end_time': participant.end_time,
                'has_comprehensive_pre': participant.comprehensive_pre is not None,
                'has_research_pre': participant.research_pre is not None,
                'has_research_post': participant.research_post is not None,
                'has_post_experiment_questionnaire2': participant.post_experiment_questionnaire2 is not None,
                'has_exit_questionnaire': participant.exit_questionnaire is not None,
                'num_analysis_sessions': len(participant.analysis_sessions),
                'num_interactions': len(participant.interactions)
            })
        
        return jsonify({
            'success': True,
            'participants': participant_data,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting study data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export_study_data', methods=['POST'])
def export_study_data():
    """Export study data based on type"""
    try:
        data = request.get_json()
        export_type = data.get('export_type', 'all')
        
        exported_files = {}
        
        if export_type == 'all':
            exported_files = study_data_manager.export_to_csv()
        elif export_type == 'pre_questionnaires':
            exported_files = study_data_manager.export_pre_questionnaires_only()
        elif export_type == 'post_questionnaires':
            exported_files = study_data_manager.export_post_questionnaires_only()
        elif export_type == 'post_questionnaire2':
            exported_files = study_data_manager.export_post_questionnaire2_only()
        elif export_type == 'exit_questionnaires':
            exported_files = study_data_manager.export_exit_questionnaires_only()
        elif export_type == 'sessions':
            exported_files = study_data_manager.export_analysis_sessions_only()
        elif export_type == 'interactions':
            exported_files = study_data_manager.export_interactions_only()
        else:
            return jsonify({'success': False, 'message': f'Unknown export type: {export_type}'}), 400
        
        if exported_files:
            return jsonify({
                'success': True,
                'message': f'{export_type.replace("_", " ").title()} data exported successfully',
                'files': exported_files
            })
        else:
            return jsonify({
                'success': False,
                'message': f'No data found for {export_type.replace("_", " ")}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error exporting study data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download_export/<filename>')
def download_export(filename):
    """Download exported file"""
    try:
        data_dir = study_data_manager.data_dir
        return send_from_directory(data_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_participant_data/<session_id>')
def get_participant_data(session_id):
    """Get specific participant data"""
    try:
        participant = study_data_manager.get_participant(session_id)
        
        if participant:
            return jsonify({
                'success': True,
                'participant': {
                    'session_id': participant.session_id,
                    'participant_id': participant.participant_id,
                    'start_time': participant.start_time,
                    'end_time': participant.end_time,
                    'comprehensive_pre': participant.comprehensive_pre,
                    'research_pre': participant.research_pre,
                    'research_post': participant.research_post,
                    'post_experiment_questionnaire2': participant.post_experiment_questionnaire2,
                    'exit_questionnaire': participant.exit_questionnaire,
                    'analysis_sessions': participant.analysis_sessions,
                    'interactions': participant.interactions
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Participant not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting participant data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/log_interaction', methods=['POST'])
def log_interaction():
    """Log user interaction"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        interaction_type = data.get('type')
        interaction_data = data.get('data', {})
        
        if not session_id or not interaction_type:
            return jsonify({'success': False, 'message': 'Missing session_id or type'}), 400
        
        success = study_data_manager.log_interaction(session_id, interaction_type, interaction_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Interaction logged successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to log interaction'}), 500
            
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running'
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Truth or Thought Flask Backend',
        'status': 'running',
        'endpoints': [
            '/api/submit_questionnaire',
            '/api/get_study_data',
            '/api/export_study_data',
            '/api/download_export/<filename>',
            '/api/get_participant_data/<session_id>',
            '/api/log_interaction',
            '/api/health'
        ]
    })

if __name__ == '__main__':
    print("Starting Flask Backend for Truth or Thought...")
    print("Questionnaire submission endpoint: http://localhost:5000/api/submit_questionnaire")
    print("Health check: http://localhost:5000/api/health")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)