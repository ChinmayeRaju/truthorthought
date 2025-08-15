// Utility functions for analyzing questionnaire data

export interface PreQuestionnaireData {
  // Demographics
  age: string;
  education: string;
  techExperience: string;
  aiExperience: string;
  
  // Media Habits
  mediaConsumption: string[];
  newsFrequency: string;
  sourceVerification: string;
  factChecking: string;
  
  // Bias Detection Skills
  factOpinionConfidence: string;
  biasAwareness: string;
  biasTypes: string[];
  mediaSkepticism: string;
  
  // AI Perceptions
  aiTrust: string;
  aiAccuracyExpectation: string;
  automationPreference: string;
  learningExpectation: string;
}

export interface PostQuestionnaireData {
  // System Evaluation
  systemAccuracy: number;
  systemHelpfulness: number;
  interfaceUsability: number;
  userAgency: string;
  automationBalance: string;
  
  // Learning & Skills
  skillImprovement: string;
  confidenceChange: string;
  independentDetection: string;
  learningMechanisms: string[];
  
  // Behavioral Changes
  futureVerification: string;
  mediaApproach: string;
  toolAdoption: string;
  recommendToOthers: string;
  
  // Final Feedback
  overallSatisfaction: number;
  mostValuableFeature: string;
  improvements: string;
  concerns: string;
  additionalComments?: string;
}

export interface SessionData {
  sessionId: string;
  preQuestionnaire?: PreQuestionnaireData & {
    timestamp: string;
    type: string;
  };
  postQuestionnaire?: PostQuestionnaireData & {
    timestamp: string;
    type: string;
  };
  systemUsage?: {
    duration: number;
    interactions: number;
    startTime: string;
    endTime: string;
  };
}

// Research Question Analysis Functions

export class QuestionnaireAnalyzer {
  
  /**
   * Research Question 1: How accurately can NLP techniques distinguish factual from opinion statements?
   */
  static analyzeNLPAccuracy(sessions: SessionData[]) {
    const analysis = {
      expectedAccuracy: [] as string[],
      perceivedAccuracy: [] as number[],
      accuracyGap: [] as number[],
      confidenceCorrelation: [] as { confidence: number; perceived: number }[]
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        analysis.expectedAccuracy.push(pre.aiAccuracyExpectation);
        analysis.perceivedAccuracy.push(post.systemAccuracy);
        
        // Calculate accuracy gap (expected vs perceived)
        const expectedMidpoint = this.getAccuracyMidpoint(pre.aiAccuracyExpectation);
        analysis.accuracyGap.push(post.systemAccuracy - expectedMidpoint);
        
        // Confidence correlation
        const confidence = parseInt(pre.factOpinionConfidence);
        analysis.confidenceCorrelation.push({
          confidence,
          perceived: post.systemAccuracy
        });
      }
    });

    return analysis;
  }

  /**
   * Research Question 2: What interface strategies best preserve user agency and support learning?
   */
  static analyzeInterfaceStrategies(sessions: SessionData[]) {
    const analysis = {
      userAgencyRatings: [] as string[],
      automationBalance: [] as string[],
      usabilityScores: [] as number[],
      learningMechanisms: {} as Record<string, number>,
      agencyVsUsability: [] as { agency: number; usability: number }[]
    };

    sessions.forEach(session => {
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        
        analysis.userAgencyRatings.push(post.userAgency);
        analysis.automationBalance.push(post.automationBalance);
        analysis.usabilityScores.push(post.interfaceUsability);
        
        // Count learning mechanisms
        if (post.learningMechanisms && Array.isArray(post.learningMechanisms)) {
          post.learningMechanisms.forEach(mechanism => {
            analysis.learningMechanisms[mechanism] = (analysis.learningMechanisms[mechanism] || 0) + 1;
          });
        }
        
        // Agency vs Usability correlation
        const agencyScore = this.convertAgencyToScore(post.userAgency);
        analysis.agencyVsUsability.push({
          agency: agencyScore,
          usability: post.interfaceUsability
        });
      }
    });

    return analysis;
  }

  /**
   * Research Question 3: Does AI assistance improve independent bias detection over time?
   */
  static analyzeBiasDetectionImprovement(sessions: SessionData[]) {
    const analysis = {
      skillImprovementRatings: [] as string[],
      confidenceChanges: [] as string[],
      independentDetectionChanges: [] as string[],
      prePostConfidenceComparison: [] as { pre: number; post: string }[],
      improvementByExperience: {} as Record<string, string[]>
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        analysis.skillImprovementRatings.push(post.skillImprovement);
        analysis.confidenceChanges.push(post.confidenceChange);
        analysis.independentDetectionChanges.push(post.independentDetection);
        
        // Pre-post confidence comparison
        const preConfidence = parseInt(pre.factOpinionConfidence);
        analysis.prePostConfidenceComparison.push({
          pre: preConfidence,
          post: post.confidenceChange
        });
        
        // Improvement by AI experience
        const aiExp = pre.aiExperience;
        if (!analysis.improvementByExperience[aiExp]) {
          analysis.improvementByExperience[aiExp] = [];
        }
        analysis.improvementByExperience[aiExp].push(post.skillImprovement);
      }
    });

    return analysis;
  }

  /**
   * Research Question 4: How does the model affect user behavior compared to traditional media literacy?
   */
  static analyzeBehavioralChanges(sessions: SessionData[]) {
    const analysis = {
      verificationChanges: [] as string[],
      mediaApproachChanges: [] as string[],
      toolAdoptionIntention: [] as string[],
      traditionalVsAI: [] as { traditional: string; aiAdoption: string }[]
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        analysis.verificationChanges.push(post.futureVerification);
        analysis.mediaApproachChanges.push(post.mediaApproach);
        analysis.toolAdoptionIntention.push(post.toolAdoption);
        
        // Traditional vs AI comparison
        analysis.traditionalVsAI.push({
          traditional: pre.factChecking,
          aiAdoption: post.toolAdoption
        });
      }
    });

    return analysis;
  }

  /**
   * Research Question 5: What balance of automation and human judgment is optimal?
   */
  static analyzeAutomationBalance(sessions: SessionData[]) {
    const analysis = {
      preferredAutomation: [] as string[],
      experiencedBalance: [] as string[],
      satisfactionByBalance: {} as Record<string, number[]>,
      optimalBalanceIndicators: [] as { preferred: string; experienced: string; satisfaction: number }[]
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        analysis.preferredAutomation.push(pre.automationPreference);
        analysis.experiencedBalance.push(post.automationBalance);
        
        // Satisfaction by balance
        const balance = post.automationBalance;
        if (!analysis.satisfactionByBalance[balance]) {
          analysis.satisfactionByBalance[balance] = [];
        }
        analysis.satisfactionByBalance[balance].push(post.overallSatisfaction);
        
        // Optimal balance indicators
        analysis.optimalBalanceIndicators.push({
          preferred: pre.automationPreference,
          experienced: post.automationBalance,
          satisfaction: post.overallSatisfaction
        });
      }
    });

    return analysis;
  }

  /**
   * Research Question 6: How do individual differences affect utility and adoption?
   */
  static analyzeIndividualDifferences(sessions: SessionData[]) {
    const analysis = {
      demographicSegments: {} as Record<string, any>,
      adoptionByDemographics: {} as Record<string, string[]>,
      satisfactionByExperience: {} as Record<string, number[]>,
      utilityFactors: [] as { age: string; education: string; techExp: string; satisfaction: number; adoption: string }[]
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        // Demographic segments
        const segment = `${pre.age}_${pre.education}_${pre.techExperience}`;
        if (!analysis.demographicSegments[segment]) {
          analysis.demographicSegments[segment] = {
            count: 0,
            satisfaction: [],
            adoption: []
          };
        }
        analysis.demographicSegments[segment].count++;
        analysis.demographicSegments[segment].satisfaction.push(post.overallSatisfaction);
        analysis.demographicSegments[segment].adoption.push(post.toolAdoption);
        
        // Adoption by demographics
        ['age', 'education', 'techExperience', 'aiExperience'].forEach(demo => {
          const key = pre[demo as keyof PreQuestionnaireData] as string;
          if (!analysis.adoptionByDemographics[key]) {
            analysis.adoptionByDemographics[key] = [];
          }
          analysis.adoptionByDemographics[key].push(post.toolAdoption);
        });
        
        // Satisfaction by experience
        const techExp = pre.techExperience;
        if (!analysis.satisfactionByExperience[techExp]) {
          analysis.satisfactionByExperience[techExp] = [];
        }
        analysis.satisfactionByExperience[techExp].push(post.overallSatisfaction);
        
        // Utility factors
        analysis.utilityFactors.push({
          age: pre.age,
          education: pre.education,
          techExp: pre.techExperience,
          satisfaction: post.overallSatisfaction,
          adoption: post.toolAdoption
        });
      }
    });

    return analysis;
  }

  // Helper functions
  private static getAccuracyMidpoint(range: string): number {
    const midpoints: Record<string, number> = {
      '90-100': 95,
      '70-89': 79.5,
      '50-69': 59.5,
      '30-49': 39.5,
      'below-30': 15
    };
    return midpoints[range] || 50;
  }

  private static convertAgencyToScore(agency: string): number {
    const scores: Record<string, number> = {
      'complete-control': 10,
      'mostly-control': 8,
      'some-control': 6,
      'little-control': 4,
      'no-control': 2
    };
    return scores[agency] || 5;
  }

  // Data export functions
  static exportToCSV(sessions: SessionData[]): string {
    const headers = [
      'sessionId', 'age', 'education', 'techExperience', 'aiExperience',
      'factOpinionConfidence', 'biasAwareness', 'aiTrust', 'aiAccuracyExpectation',
      'systemAccuracy', 'systemHelpfulness', 'skillImprovement', 'toolAdoption',
      'overallSatisfaction'
    ];

    const rows = sessions.map(session => {
      const pre = session.preQuestionnaire;
      const post = session.postQuestionnaire;
      
      return [
        session.sessionId,
        pre?.age || '',
        pre?.education || '',
        pre?.techExperience || '',
        pre?.aiExperience || '',
        pre?.factOpinionConfidence || '',
        pre?.biasAwareness || '',
        pre?.aiTrust || '',
        pre?.aiAccuracyExpectation || '',
        post?.systemAccuracy || '',
        post?.systemHelpfulness || '',
        post?.skillImprovement || '',
        post?.toolAdoption || '',
        post?.overallSatisfaction || ''
      ].join(',');
    });

    return [headers.join(','), ...rows].join('\n');
  }

  static getAllSessionData(): SessionData[] {
    const sessions: SessionData[] = [];
    
    // Get all localStorage keys
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith('pre_questionnaire_') || key?.startsWith('post_questionnaire_')) {
        const sessionId = key.split('_').slice(2).join('_');
        
        let session = sessions.find(s => s.sessionId === sessionId);
        if (!session) {
          session = { sessionId };
          sessions.push(session);
        }
        
        const data = JSON.parse(localStorage.getItem(key) || '{}');
        
        if (key.startsWith('pre_questionnaire_')) {
          session.preQuestionnaire = data;
        } else if (key.startsWith('post_questionnaire_')) {
          session.postQuestionnaire = data;
        }
      }
    }
    
    return sessions;
  }
}