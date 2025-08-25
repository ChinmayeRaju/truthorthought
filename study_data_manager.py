"""
Comprehensive Study Data Manager
Handles storage, retrieval, and export of all study data including:
- Pre-questionnaires (comprehensive and research-aligned)
- Post-questionnaires (research-aligned)
- Exit questionnaires
- Analyzed URLs and sessions
- User interactions and timestamps
"""

import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field

@dataclass
class StudyParticipant:
    """Complete participant data structure"""
    session_id: str
    participant_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    # Pre-questionnaire data
    comprehensive_pre: Optional[Dict[str, Any]] = None
    research_pre: Optional[Dict[str, Any]] = None
    
    # Post-questionnaire data
    research_post: Optional[Dict[str, Any]] = None
    
    # Bias analysis questionnaire data
    bias_analysis: Optional[Dict[str, Any]] = None
    
    # Exit questionnaire data
    exit_questionnaire: Optional[Dict[str, Any]] = None
    
    # Analysis sessions
    analysis_sessions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Interaction data
    interactions: List[Dict[str, Any]] = field(default_factory=list)

class StudyDataManager:
    """Manages all study data with file persistence and CSV export capabilities"""
    
    def __init__(self, data_dir: str = "research_data"):
        self.data_dir = data_dir
        self.participants_file = os.path.join(data_dir, "participants.json")
        self.sessions_file = os.path.join(data_dir, "analysis_sessions.json")
        self.interactions_file = os.path.join(data_dir, "interactions.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.participants = self._load_participants()
        self.analysis_sessions = self._load_analysis_sessions()
        self.interactions = self._load_interactions()
    
    def _load_participants(self) -> Dict[str, StudyParticipant]:
        """Load participants from disk"""
        if os.path.exists(self.participants_file):
            try:
                with open(self.participants_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    participants = {}
                    for session_id, participant_data in data.items():
                        participants[session_id] = StudyParticipant(**participant_data)
                    return participants
            except Exception as e:
                print(f"Error loading participants: {e}")
        return {}
    
    def _load_analysis_sessions(self) -> Dict[str, Any]:
        """Load analysis sessions from disk"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading analysis sessions: {e}")
        return {}
    
    def _load_interactions(self) -> List[Dict[str, Any]]:
        """Load interaction logs from disk"""
        if os.path.exists(self.interactions_file):
            try:
                with open(self.interactions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading interactions: {e}")
        return []
    
    def _save_participants(self):
        """Save participants to disk"""
        try:
            data = {}
            for session_id, participant in self.participants.items():
                data[session_id] = asdict(participant)
            
            with open(self.participants_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving participants: {e}")
    
    def _save_analysis_sessions(self):
        """Save analysis sessions to disk"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving analysis sessions: {e}")
    
    def _save_interactions(self):
        """Save interactions to disk"""
        try:
            with open(self.interactions_file, 'w', encoding='utf-8') as f:
                json.dump(self.interactions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving interactions: {e}")
    
    def get_or_create_participant(self, session_id: str) -> StudyParticipant:
        """Get existing participant or create new one"""
        if session_id not in self.participants:
            self.participants[session_id] = StudyParticipant(
                session_id=session_id,
                start_time=datetime.now().isoformat()
            )
            self._save_participants()
        return self.participants[session_id]
    
    def save_questionnaire_data(self, session_id: str, questionnaire_type: str, data: Dict[str, Any]) -> bool:
        """Save questionnaire data for a participant"""
        try:
            participant = self.get_or_create_participant(session_id)
            
            # Add metadata
            data_with_metadata = {
                **data,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'type': questionnaire_type
            }
            
            # Store based on questionnaire type
            if questionnaire_type == 'comprehensive_pre':
                participant.comprehensive_pre = data_with_metadata
            elif questionnaire_type == 'research_pre':
                participant.research_pre = data_with_metadata
            elif questionnaire_type == 'research_post':
                participant.research_post = data_with_metadata
            elif questionnaire_type == 'bias_analysis':
                participant.bias_analysis = data_with_metadata
            elif questionnaire_type == 'exit':
                participant.exit_questionnaire = data_with_metadata
                participant.end_time = datetime.now().isoformat()
            
            self._save_participants()
            return True
            
        except Exception as e:
            print(f"Error saving questionnaire data: {e}")
            return False
    
    def save_analysis_session(self, session_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Save analysis session data"""
        try:
            # Store in analysis sessions
            self.analysis_sessions[session_id] = {
                'timestamp': datetime.now().isoformat(),
                'analysis_data': analysis_data
            }
            self._save_analysis_sessions()
            
            # Also link to participant
            participant = self.get_or_create_participant(session_id)
            participant.analysis_sessions.append({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'url': analysis_data.get('url', ''),
                'urls': analysis_data.get('urls', []),
                'title': analysis_data.get('title', ''),
                'domain': analysis_data.get('domain', ''),
                'total_facts': analysis_data.get('total_facts', 0),
                'total_opinions': analysis_data.get('total_opinions', 0),
                'is_multiple': 'multiple_results' in analysis_data or len(analysis_data.get('urls', [])) > 1
            })
            self._save_participants()
            
            return True
            
        except Exception as e:
            print(f"Error saving analysis session: {e}")
            return False
    
    def log_interaction(self, session_id: str, interaction_type: str, data: Dict[str, Any]) -> bool:
        """Log user interaction"""
        try:
            interaction = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'type': interaction_type,
                'data': data
            }
            
            self.interactions.append(interaction)
            self._save_interactions()
            
            # Also add to participant
            participant = self.get_or_create_participant(session_id)
            participant.interactions.append(interaction)
            self._save_participants()
            
            return True
            
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return False
    
    def get_all_participants(self) -> List[StudyParticipant]:
        """Get all participants"""
        return list(self.participants.values())
    
    def get_participant(self, session_id: str) -> Optional[StudyParticipant]:
        """Get specific participant"""
        return self.participants.get(session_id)
    
    def get_analysis_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis session"""
        return self.analysis_sessions.get(session_id)
    
    def export_to_csv(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export all data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export comprehensive study data
            self._export_comprehensive_data(output_dir, timestamp, exported_files)
            
            # Export questionnaire-specific data
            self._export_questionnaire_data(output_dir, timestamp, exported_files)
            
            # Export analysis sessions
            self._export_analysis_sessions(output_dir, timestamp, exported_files)
            
            # Export interactions
            self._export_interactions(output_dir, timestamp, exported_files)
            
            return exported_files
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return {}
    
    def export_questionnaires_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only questionnaire data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export only questionnaire-specific data
            self._export_questionnaire_data(output_dir, timestamp, exported_files)
            return exported_files
            
        except Exception as e:
            print(f"Error exporting questionnaire data: {e}")
            return {}
    
    def export_sessions_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only analysis session data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export only analysis sessions
            self._export_analysis_sessions(output_dir, timestamp, exported_files)
            return exported_files
            
        except Exception as e:
            print(f"Error exporting session data: {e}")
            return {}
    
    def export_interactions_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only interaction data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export only interactions
            self._export_interactions(output_dir, timestamp, exported_files)
            return exported_files
            
        except Exception as e:
            print(f"Error exporting interaction data: {e}")
            return {}
    
    def export_pre_questionnaires_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only pre-questionnaire data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export comprehensive pre-questionnaire
            filename = f"comprehensive_pre_questionnaire_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            rows = []
            for participant in self.participants.values():
                if participant.comprehensive_pre:
                    rows.append(participant.comprehensive_pre)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files['comprehensive_pre_questionnaire'] = filepath
            
            # Export research pre-questionnaire
            filename = f"research_pre_questionnaire_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            rows = []
            for participant in self.participants.values():
                if participant.research_pre:
                    rows.append(participant.research_pre)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files['research_pre_questionnaire'] = filepath
            
            return exported_files
            
        except Exception as e:
            print(f"Error exporting pre-questionnaire data: {e}")
            return {}
    
    def export_post_questionnaires_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only post-questionnaire data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export research post-questionnaire
            filename = f"research_post_questionnaire_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            rows = []
            for participant in self.participants.values():
                if participant.research_post:
                    rows.append(participant.research_post)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files['research_post_questionnaire'] = filepath
            else:
                # Create an empty file to indicate no data available
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('No post-questionnaire data available\n')
                exported_files['research_post_questionnaire'] = filepath
            
            return exported_files
            
        except Exception as e:
            print(f"Error exporting post-questionnaire data: {e}")
            return {}
    
    def export_bias_analysis_questionnaires_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only bias analysis questionnaire data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export bias analysis questionnaire (post_experiment_questionnaire2 type)
            filename = f"bias_analysis_questionnaire_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            rows = []
            for participant in self.participants.values():
                if participant.bias_analysis:
                    # Extract only the questionnaire responses, exclude biasSessionData and other analysis data
                    questionnaire_data = participant.bias_analysis.copy()
                    
                    # Remove analysis-related data, keep only questionnaire responses
                    fields_to_remove = ['biasSessionData', 'content', 'domain', 'facts', 'opinions', 'url', 'urls', 'title']
                    for field in fields_to_remove:
                        questionnaire_data.pop(field, None)
                    
                    rows.append(questionnaire_data)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files['bias_analysis_questionnaire'] = filepath
            else:
                # Create an empty file to indicate no data available
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('No bias analysis questionnaire data available\n')
                exported_files['bias_analysis_questionnaire'] = filepath
            
            return exported_files
            
        except Exception as e:
            print(f"Error exporting bias analysis questionnaire data: {e}")
            return {}

    def export_exit_questionnaires_only(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export only exit questionnaire data to CSV files"""
        if output_dir is None:
            output_dir = self.data_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        try:
            # Export exit questionnaire
            filename = f"exit_questionnaire_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            rows = []
            for participant in self.participants.values():
                if participant.exit_questionnaire:
                    rows.append(participant.exit_questionnaire)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files['exit_questionnaire'] = filepath
            
            return exported_files
            
        except Exception as e:
            print(f"Error exporting exit questionnaire data: {e}")
            return {}
    
    def _export_comprehensive_data(self, output_dir: str, timestamp: str, exported_files: Dict[str, str]):
        """Export comprehensive participant data"""
        filename = f"comprehensive_study_data_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        rows = []
        for participant in self.participants.values():
            row = {
                'session_id': participant.session_id,
                'participant_id': participant.participant_id,
                'start_time': participant.start_time,
                'end_time': participant.end_time,
                'has_comprehensive_pre': participant.comprehensive_pre is not None,
                'has_research_pre': participant.research_pre is not None,
                'has_research_post': participant.research_post is not None,
                'has_exit_questionnaire': participant.exit_questionnaire is not None,
                'num_analysis_sessions': len(participant.analysis_sessions),
                'num_interactions': len(participant.interactions)
            }
            
            # Add pre-questionnaire data
            if participant.comprehensive_pre:
                for key, value in participant.comprehensive_pre.items():
                    if key not in ['timestamp', 'session_id', 'type']:
                        row[f'comp_pre_{key}'] = value
            
            if participant.research_pre:
                for key, value in participant.research_pre.items():
                    if key not in ['timestamp', 'session_id', 'type']:
                        row[f'res_pre_{key}'] = value
            
            # Add post-questionnaire data
            if participant.research_post:
                for key, value in participant.research_post.items():
                    if key not in ['timestamp', 'session_id', 'type']:
                        row[f'res_post_{key}'] = value
            
            # Add exit questionnaire data
            if participant.exit_questionnaire:
                for key, value in participant.exit_questionnaire.items():
                    if key not in ['timestamp', 'session_id', 'type']:
                        row[f'exit_{key}'] = value
            
            rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False, encoding='utf-8')
            exported_files['comprehensive_data'] = filepath
    
    def _export_questionnaire_data(self, output_dir: str, timestamp: str, exported_files: Dict[str, str]):
        """Export questionnaire-specific data"""
        questionnaire_types = [
            ('comprehensive_pre', 'comprehensive_pre_questionnaire'),
            ('research_pre', 'research_pre_questionnaire'),
            ('research_post', 'research_post_questionnaire'),
            ('exit_questionnaire', 'exit_questionnaire')
        ]
        
        for attr_name, file_prefix in questionnaire_types:
            filename = f"{file_prefix}_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            
            rows = []
            for participant in self.participants.values():
                questionnaire_data = getattr(participant, attr_name)
                if questionnaire_data:
                    rows.append(questionnaire_data)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')
                exported_files[file_prefix] = filepath
    
    def _export_analysis_sessions(self, output_dir: str, timestamp: str, exported_files: Dict[str, str]):
        """Export analysis session data"""
        filename = f"analysis_sessions_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        rows = []
        for session_id, session_data in self.analysis_sessions.items():
            analysis_data = session_data.get('analysis_data', {})
            
            row = {
                'session_id': session_id,
                'timestamp': session_data.get('timestamp'),
                'url': analysis_data.get('url', ''),
                'urls': json.dumps(analysis_data.get('urls', [])),
                'title': analysis_data.get('title', ''),
                'domain': analysis_data.get('domain', ''),
                'total_facts': analysis_data.get('total_facts', 0),
                'total_opinions': analysis_data.get('total_opinions', 0),
                'total_sentences': analysis_data.get('total_sentences', 0),
                'is_multiple': 'multiple_results' in analysis_data,
                'confidence': analysis_data.get('confidence', 0),
                'specialists': json.dumps(analysis_data.get('specialists', [])),
                'content_length': len(analysis_data.get('content', '')),
                'has_multiple_results': 'multiple_results' in analysis_data,
                'num_results': len(analysis_data.get('results', []))
            }
            
            rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False, encoding='utf-8')
            exported_files['analysis_sessions'] = filepath
    
    def _export_interactions(self, output_dir: str, timestamp: str, exported_files: Dict[str, str]):
        """Export interaction data"""
        filename = f"interactions_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        if self.interactions:
            df = pd.DataFrame(self.interactions)
            df.to_csv(filepath, index=False, encoding='utf-8')
            exported_files['interactions'] = filepath
    
    def get_study_statistics(self) -> Dict[str, Any]:
        """Get comprehensive study statistics"""
        stats = {
            'total_participants': len(self.participants),
            'completed_comprehensive_pre': 0,
            'completed_research_pre': 0,
            'completed_research_post': 0,
            'completed_exit': 0,
            'completed_full_study': 0,
            'total_analysis_sessions': len(self.analysis_sessions),
            'total_interactions': len(self.interactions),
            'avg_analysis_sessions_per_participant': 0.0,
            'avg_interactions_per_participant': 0.0
        }
        
        for participant in self.participants.values():
            if participant.comprehensive_pre:
                stats['completed_comprehensive_pre'] += 1
            if participant.research_pre:
                stats['completed_research_pre'] += 1
            if participant.research_post:
                stats['completed_research_post'] += 1
            if participant.exit_questionnaire:
                stats['completed_exit'] += 1
            
            # Full study completion (has pre and post questionnaires)
            if ((participant.comprehensive_pre or participant.research_pre) and 
                participant.research_post):
                stats['completed_full_study'] += 1
        
        if stats['total_participants'] > 0:
            stats['avg_analysis_sessions_per_participant'] = stats['total_analysis_sessions'] / stats['total_participants']
            stats['avg_interactions_per_participant'] = stats['total_interactions'] / stats['total_participants']
        
        return stats

# Global instance
study_data_manager = StudyDataManager()