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
  source_name?: string;
  original_sentence?: string;
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

export interface KeyPersonnel {
  name: string;
  title: string;
  organization: string;
  role_in_story: string;
  quotes: string[];
  relevance_score: number;
}

export interface ImportantQuote {
  quote: string;
  speaker: string;
  speaker_title: string;
  context: string;
  significance: string;
  impact_score: number;
}

export interface KeyInsight {
  insight: string;
  category: string;
  supporting_evidence: string;
  importance_score: number;
}

export interface ContentSummary {
  key_personnel: KeyPersonnel[];
  important_quotes: ImportantQuote[];
  key_insights: KeyInsight[];
  main_themes: string[];
  executive_summary: string;
  content_type: string;
  credibility_indicators: string[];
}

export interface MultiSourceSummary {
  individual_summaries: {
    url: string;
    title: string;
    key_personnel: KeyPersonnel[];
    important_quotes: ImportantQuote[];
    key_insights: KeyInsight[];
    main_themes: string[];
    executive_summary: string;
    content_type: string;
  }[];
  cross_source_analysis: {
    consistency_analysis: string;
    conflicting_information: any[];
    corroborating_evidence: any[];
    source_reliability_comparison: any[];
  };
  aggregated_data: {
    total_personnel: number;
    total_quotes: number;
    total_insights: number;
    common_themes: string[];
    top_personnel: KeyPersonnel[];
    most_impactful_quotes: ImportantQuote[];
    key_insights_summary: KeyInsight[];
  };
}

export interface SummaryResponse {
  success: boolean;
  session_id?: string;
  summary_type?: 'single_source' | 'multi_source';
  summary: ContentSummary | MultiSourceSummary;
}

export interface KeyFigure {
  full_name: string;
  title?: string;
  organization?: string;
  role_in_story?: string;
  significance?: string;
  category?: string;
  source_url?: string;
}

export interface KeyFiguresData {
  total_figures: number;
  categories?: {
    primary_actors?: { figures: KeyFigure[] };
    secondary_participants?: { figures: KeyFigure[] };
    quoted_sources?: { figures: KeyFigure[] };
    other?: { figures: KeyFigure[] };
  };
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}
