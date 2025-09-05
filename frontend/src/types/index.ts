export interface Citation {
  url: string;
  title: string;
  snippet?: string;
  domain?: string;
  verification_score?: number;
  reasoning?: string;
}

export interface SourceTag {
  name: string;
  display_name: string;
  tag_color: string;
  tag_style: string;
  domain: string;
  url: string;
  short_name: string;
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
  source_tag?: SourceTag;
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

export interface ExitQuestionnaireData {
  easierTask: string;
  betterUnderstanding: string;
  moreControl: string;
  timeSaving: string;
  lessMentalDemand: string;
  moreTrust: string;
  biasNoticed: string;
  biasDescription?: string;
  personnelInfluence: number;
  personnelInfluenceDifference: string;
  personnelInfluenceDescription?: string;
  futurePreference: string;
  additionalComments?: string;
  sessionId: string;
  timestamp: string;
}

export interface ComprehensivePreQuestionnaireData {
  // Media Trust Foundation
  mediaTrustGeneral: number;
  mediaCredibilityFactors: string[];
  informationVerificationHabits: string;
  
  // Outlet Assessment
  outletTrustRankingBBC?: number;
  outletTrustRankingCNN?: number;
  outletTrustRankingGuardian?: number;
  outletTrustRankingReuters?: number;
  outletTrustRankingAP?: number;
  perceivedBiasTopics: string[];
  biasDetectionConfidence: number;
  
  // Psychological Impact
  newsEmotionalDraining: number;
  newsMoodImpact: string;
  newsAnxietyRelationship: string;
  stressfulNewsTopics: string[];
  
  // News Behaviors
  newsAvoidanceBehaviors: string;
  newsCheckingFrequency: string;
  newsCheckingTriggers: string[];
  preferredNewsFormat: string;
  
  // Crisis Information
  crisisInformationSources: string[];
  crisisInformationSpeed: number;
  informationOverloadCoping: string;
  misinformationConcern: number;
  
  // Demographics & Background
  age: number;
  education: string;
  profession: string;
  politicalInterest: number;
  techComfort: number;
  additionalComments?: string;
  
  sessionId: string;
  timestamp: string;
  type: 'comprehensive_pre';
}

export interface ResearchAlignedPreQuestionnaireData {
  // Demographics & Individual Differences (RQ6)
  age: string;
  education: string;
  profession: string;
  technologyComfort: number;
  learningStyle: string;
  cognitiveStyle: string;
  
  // Fact/Opinion Detection Baseline (RQ1)
  factOpinionConfidence: number;
  factOpinionMethods: string[];
  factOpinionAccuracy: number;
  factOpinionChallenges: string;
  
  // Bias Detection & Media Literacy (RQ3, RQ4)
  biasDetectionConfidence: number;
  biasDetectionMethods: string[];
  mediaLiteracyTraining: string;
  newsEvaluationProcess: string;
  informationVerificationFrequency: string;
  
  // Automation & AI Preferences (RQ5)
  automationOversightPreference: string;
  aiTrustLevel: number;
  aiExperienceLevel: string;
  automationConcerns: string[];
  
  // Cognitive Processing & Interface Preferences (RQ2)
  informationProcessingStyle: string;
  cognitiveLoadFactors: string[];
  preferredInformationPresentation: string[];
  mentalEffortNews: number;
  learningMechanismsPreference: string[];
  
  // News Consumption Patterns
  generalMediaTrust: number;
  mostTrustworthy: string;
  secondTrustworthy: string;
  thirdTrustworthy: string;
  fourthTrustworthy: string;
  leastTrustworthy: string;
  newsEmotionalImpact: number;
  newsConsumptionFrequency: string;
  newsSourceTypes: string[];
  aiExpectations: string;
  successMetrics: string[];
  additionalComments?: string;
  
  sessionId: string;
  timestamp: string;
  type: 'research_pre';
}

export interface ResearchAlignedPostQuestionnaireData {
  // AI Accuracy Perception (RQ1)
  aiAccuracyPerception: number;
  aiVsHumanAccuracy: string;
  aiTrustChange: string;
  aiClassificationAgreement: number;
  aiAccuracyExpectationComparison: string;
  aiErrorTypes: string[];
  
  // Cognitive Load & Interface (RQ2)
  mentalDemand: number;
  effortRequired: number;
  frustrationLevel: number;
  interfaceUsability: number;
  learningSupport: number;
  cognitiveLoadComparison: string;
  interfaceFeatureHelpfulness: string[];
  
  // Skill Development & Learning (RQ3)
  biasDetectionConfidenceChange: string;
  skillDevelopmentPerception: number;
  learningMechanisms: string[];
  skillTransferConfidence: number;
  independentAnalysisImprovement: string;
  newSkillsLearned: string;
  
  // Behavioral Changes & Comparison (RQ4)
  approachChange: string;
  aiVsTraditionalPreference: string;
  effectivenessComparison: number;
  behavioralChanges: string[];
  traditionalMethodsStillUseful: string[];
  
  // Automation Balance Preferences (RQ5)
  optimalAutomationLevel: string;
  trustBalancePreference: number;
  controlSatisfaction: number;
  automationImprovements: string;
  overrideFrequency: number;
  agencyFeeling: number;
  
  // Decision-Making Clarity & Understanding
  decisionMakingConfidence: number;
  informationInfluence: number;
  claritySemanticDifferential: number;
  factOpinionDistinction: number;
  objectiveSubjectiveUnderstanding: number;
  
  // Efficiency & Cognitive Load Assessment
  evaluationSpeed: number;
  effortRequiredSanitized: number;
  judgmentSpeed: number;
  focusEfficiency: number;
  timeSemanticDifferential: number;
  effortSemanticDifferential: number;
  judgmentSpeedSemanticDifferential: number;
  
  // Perception of Balance
  informationBalance: number;
  perspectiveAwareness: number;
  
  // Adoption & Individual Factors (RQ6)
  agencyAndInfluence: number;
  citationEffectiveness: number;
  mostValuableInterfaceElement: string;
  comprehensiveCoverage: number;
  timeEfficiencyImprovement: string;
  emotionalBurdenReduction: string;
  systematicBiasDetection: string;
  
  // TAM-style Adoption Questions
  futureUseConsideration: number;
  likelyToUse: number;
  recommendToOthers: number;
  toolUsefulness: number;
  useLikelihoodSemanticDifferential: number;
  interestSemanticDifferential: number;
  recommendationSemanticDifferential: number;
  
  continuedUseIntention: number;
  perceivedUtility: number;
  recommendationLikelihood: number;
  individualFactorsInfluence: string[];
  adoptionBarriers: string[];
  overallSatisfaction: number;
  finalComments?: string;
  
  // AI Feature Evaluation
  personnelRelevanceAccuracy: number;
  personnelHelpfulness: number;
  quotesRelevanceAccuracy: number;
  quotesHelpfulness: number;
  featureUsagePreference: string[];
  featureImprovementSuggestions?: string;
  
  sessionId: string;
  timestamp: string;
  type: 'research_post';
}
