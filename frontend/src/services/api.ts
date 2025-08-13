import axios from 'axios';
import type { AnalysisResult, SessionInfo, BiasAnalysisSession } from '../types';

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
  chat: async (sessionId: string, question: string): Promise<{ success: boolean; answer: string }> => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      question,
    });
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default apiService;
