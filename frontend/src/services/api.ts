import axios from 'axios';
import type { AnalysisResult, SessionInfo, BiasAnalysisSession, SummaryResponse } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Analyze multiple URLs
  analyzeMultipleUrls: async (urls: string[], maxSentences: number = 15, analysisMode: string = 'combined'): Promise<AnalysisResult> => {
    const response = await api.post('/analyze_multiple', {
      urls,
      max_sentences: maxSentences,
      analysis_mode: analysisMode,
    });
    return response.data;
  },

  // Analyze single URL or text
  analyzeSingle: async (content: string, type: 'url' | 'text'): Promise<AnalysisResult> => {
    const response = await api.post('/analyze', {
      content,
      type,
    });
    return response.data;
  },

  // Analyze for bias research
  analyzeForBias: async (
    url: string, 
    participantId: string = '', 
    studyMode: string = 'bias_analysis', 
    analysisDepth: number = 10
  ): Promise<AnalysisResult> => {
    const response = await api.post('/analyze_for_bias', {
      url,
      participant_id: participantId,
      study_mode: studyMode,
      analysis_depth: analysisDepth,
    });
    return response.data;
  },

  // Get analyzed sessions for bias research
  getAnalyzedSessions: async (): Promise<{ success: boolean; sessions: SessionInfo[] }> => {
    const response = await api.get('/get_analyzed_sessions');
    return response.data;
  },

  // Load specific session for bias research
  loadSessionForBias: async (sessionId: string): Promise<BiasAnalysisSession> => {
    const response = await api.get(`/load_session_for_bias/${sessionId}`);
    return response.data;
  },

  // Submit research data
  submitResearchData: async (data: any): Promise<{ success: boolean; message: string; session_id: string }> => {
    const response = await api.post('/submit_research_data', data);
    return response.data;
  },

  // Chat with AI
  chat: async (sessionId: string, question: string): Promise<{
    success: boolean;
    answer: string;
    suggested_questions?: string[];
    context_info?: {
      facts_count: number;
      opinions_count: number;
      domain: string;
      has_verified_sources: boolean;
    };
    error?: string;
  }> => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      question,
    });
    return response.data;
  },

  // Summarize content directly
  summarizeContent: async (content: string, title: string = '', domain: string = 'GENERAL'): Promise<SummaryResponse> => {
    const response = await api.post('/summarize_content', {
      content,
      title,
      domain,
    });
    return response.data;
  },

  // Summarize content from an existing session
  summarizeSession: async (sessionId: string): Promise<SummaryResponse> => {
    const response = await api.post(`/summarize_session/${sessionId}`);
    return response.data;
  },

  // Submit questionnaire data
  submitQuestionnaire: async (questionnaireData: any): Promise<{ success: boolean; message: string; session_id: string; file_path?: string }> => {
    const response = await api.post('/submit_questionnaire', questionnaireData);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default apiService;
