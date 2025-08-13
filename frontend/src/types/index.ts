export interface Citation {
  url: string;
  title: string;
  snippet?: string;
  domain?: string;
  verification_score?: number;
  reasoning?: string;
}

export interface Statement {
  sentence: string;
  confidence?: number;
  reasoning?: string;
  citations?: Citation[];
  citation?: Citation;
  source_url?: string;
  source_title?: string;
}

export interface AnalysisResult {
  success: boolean;
  facts: Statement[];
  opinions: Statement[];
  domain: string;
  title: string;
  content?: string;
  specialists: string[];
  confidence: number;
  session_id: string;
  url?: string;
  final_classification?: string;
  total_facts?: number;
  total_opinions?: number;
  total_sentences?: number;
  results?: string;
  multiple_results?: IndividualResult[];
  bias_metrics?: BiasMetrics;
}

export interface IndividualResult {
  url: string;
  title: string;
  domain: string;
  summary: string;
  analysis: string;
  formatted_content: string;
  raw_content: string;
  facts_count: number;
  opinions_count: number;
  sentences_count: number;
  facts: Statement[];
  opinions: Statement[];
  full_content?: string;
  scraped_title?: string;
}

export interface BiasMetrics {
  fact_percentage: number;
  opinion_percentage: number;
  bias_level: string;
  total_statements: number;
  analysis_quality: string;
}

export interface SessionInfo {
  session_id: string;
  timestamp: string;
  title: string;
  domain: string;
  total_facts: number;
  total_opinions: number;
  total_sentences: number;
  url: string;
  is_multiple: boolean;
}

export interface BiasAnalysisSession {
  success: boolean;
  session_id: string;
  title: string;
  domain: string;
  content: string;
  url: string;
  timestamp: string;
  facts: Statement[];
  opinions: Statement[];
  total_facts: number;
  total_opinions: number;
  specialists: string[];
  is_multiple?: boolean;
  multiple_results?: IndividualResult[];
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}
