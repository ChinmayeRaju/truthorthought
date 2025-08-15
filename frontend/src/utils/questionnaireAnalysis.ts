// Utility functions for analyzing questionnaire data

export interface PreQuestionnaireData {
  // News Familiarity
  newsFamiliarity: number; // 1-5 Likert scale
  newsFrequency: string; // daily/weekly/monthly/rarely
  factOpinionConfidence: number; // 1-5 Likert scale
  
  // Trust & Bias
  trustedOutlets: string[]; // BBC/CNN/Guardian/Other
  outletsBiased: string; // yes/no
  biasedOutletsSpecify?: string; // text
  aiFamiliarityTools: number; // 1-5 Likert scale
  
  // Reading Habits
  headlineReliance: number; // 1-5 Likert scale
  crossCheckFrequency: number; // 1-5 Likert scale
  
  // Demographics
  techExperience: string; // beginner/intermediate/advanced/expert
  age: string;
  profession: string;
}

export interface PostQuestionnaireData {
  // Task Difficulty (NASA-TLX)
  mentalDemand: number; // 0-100 slider
  effortRequired: number; // 0-100 slider
  frustrationLevel: number; // 0-100 slider
  
  // System Clarity
  factOpinionClarity: number; // 1-5 Likert scale
  controlLevel: number; // 1-5 Likert scale
  sourceInfluence: number; // 1-5 Likert scale
  explanationHelpfulness: number; // 1-5 Likert scale
  
  // Features & Issues
  mostHelpfulFeature: string[]; // checkboxes
  otherHelpfulFeature?: string; // text
  issuesEncountered: string; // text
  missedFacts: number; // 1-5 Likert scale
  missedFactsSpecify?: string; // text
  
  // Final Comments
  additionalComments: string; // text
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

// Research Analysis Functions

export class QuestionnaireAnalyzer {
  
  /**
   * NASA-TLX Analysis: Mental demand, effort, and frustration
   */
  static analyzeTaskLoad(sessions: SessionData[]) {
    const analysis = {
      mentalDemandScores: [] as number[],
      effortScores: [] as number[],
      frustrationScores: [] as number[],
      averageTLX: 0,
      taskLoadByUser: [] as { sessionId: string; mentalDemand: number; effort: number; frustration: number; average: number }[]
    };

    sessions.forEach(session => {
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        
        analysis.mentalDemandScores.push(post.mentalDemand);
        analysis.effortScores.push(post.effortRequired);
        analysis.frustrationScores.push(post.frustrationLevel);
        
        const avgTLX = (post.mentalDemand + post.effortRequired + post.frustrationLevel) / 3;
        analysis.taskLoadByUser.push({
          sessionId: session.sessionId,
          mentalDemand: post.mentalDemand,
          effort: post.effortRequired,
          frustration: post.frustrationLevel,
          average: avgTLX
        });
      }
    });

    if (analysis.mentalDemandScores.length > 0) {
      const totalTLX = analysis.taskLoadByUser.reduce((sum, user) => sum + user.average, 0);
      analysis.averageTLX = totalTLX / analysis.taskLoadByUser.length;
    }

    return analysis;
  }

  /**
   * System Clarity Analysis: Fact-opinion clarity across UI designs and outlets
   */
  static analyzeSystemClarity(sessions: SessionData[]) {
    const analysis = {
      clarityScores: [] as number[],
      controlScores: [] as number[],
      sourceInfluenceScores: [] as number[],
      explanationHelpfulnessScores: [] as number[],
      averageClarity: 0,
      clarityDistribution: {} as Record<number, number>
    };

    sessions.forEach(session => {
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        
        analysis.clarityScores.push(post.factOpinionClarity);
        analysis.controlScores.push(post.controlLevel);
        analysis.sourceInfluenceScores.push(post.sourceInfluence);
        analysis.explanationHelpfulnessScores.push(post.explanationHelpfulness);
        
        // Count clarity distribution
        analysis.clarityDistribution[post.factOpinionClarity] = 
          (analysis.clarityDistribution[post.factOpinionClarity] || 0) + 1;
      }
    });

    if (analysis.clarityScores.length > 0) {
      analysis.averageClarity = analysis.clarityScores.reduce((a, b) => a + b, 0) / analysis.clarityScores.length;
    }

    return analysis;
  }

  /**
   * Trust Analysis: How source labels influence trust
   */
  static analyzeTrustFactors(sessions: SessionData[]) {
    const analysis = {
      trustedOutlets: {} as Record<string, number>,
      biasPerceptions: { yes: 0, no: 0 },
      sourceInfluenceOnTrust: [] as number[],
      trustVsInfluence: [] as { trusted: string[]; influence: number }[]
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire) {
        const pre = session.preQuestionnaire;
        
        // Count trusted outlets
        if (pre.trustedOutlets && Array.isArray(pre.trustedOutlets)) {
          pre.trustedOutlets.forEach(outlet => {
            analysis.trustedOutlets[outlet] = (analysis.trustedOutlets[outlet] || 0) + 1;
          });
        }
        
        // Count bias perceptions
        if (pre.outletsBiased === 'yes') {
          analysis.biasPerceptions.yes++;
        } else {
          analysis.biasPerceptions.no++;
        }
      }
      
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        analysis.sourceInfluenceOnTrust.push(post.sourceInfluence);
        
        if (session.preQuestionnaire) {
          analysis.trustVsInfluence.push({
            trusted: session.preQuestionnaire.trustedOutlets || [],
            influence: post.sourceInfluence
          });
        }
      }
    });

    return analysis;
  }

  /**
   * Feature Effectiveness Analysis: Most helpful features
   */
  static analyzeFeatureEffectiveness(sessions: SessionData[]) {
    const analysis = {
      featureFrequency: {} as Record<string, number>,
      explanationHelpfulness: [] as number[],
      featureVsClarity: [] as { features: string[]; clarity: number }[]
    };

    sessions.forEach(session => {
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        
        // Count feature frequency
        if (post.mostHelpfulFeature && Array.isArray(post.mostHelpfulFeature)) {
          post.mostHelpfulFeature.forEach(feature => {
            analysis.featureFrequency[feature] = (analysis.featureFrequency[feature] || 0) + 1;
          });
        }
        
        analysis.explanationHelpfulness.push(post.explanationHelpfulness);
        
        analysis.featureVsClarity.push({
          features: post.mostHelpfulFeature || [],
          clarity: post.factOpinionClarity
        });
      }
    });

    return analysis;
  }

  /**
   * User Experience Analysis: Pre vs post confidence changes
   */
  static analyzeUserExperience(sessions: SessionData[]) {
    const analysis = {
      preConfidence: [] as number[],
      postClarity: [] as number[],
      confidenceChanges: [] as { pre: number; post: number; change: number }[],
      newsFamiliarity: [] as number[],
      aiFamiliarity: [] as number[],
      experienceByTech: {} as Record<string, { clarity: number[]; control: number[] }>
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire && session.postQuestionnaire) {
        const pre = session.preQuestionnaire;
        const post = session.postQuestionnaire;
        
        analysis.preConfidence.push(pre.factOpinionConfidence);
        analysis.postClarity.push(post.factOpinionClarity);
        analysis.newsFamiliarity.push(pre.newsFamiliarity);
        analysis.aiFamiliarity.push(pre.aiFamiliarityTools);
        
        const change = post.factOpinionClarity - pre.factOpinionConfidence;
        analysis.confidenceChanges.push({
          pre: pre.factOpinionConfidence,
          post: post.factOpinionClarity,
          change: change
        });
        
        // Group by tech experience
        if (!analysis.experienceByTech[pre.techExperience]) {
          analysis.experienceByTech[pre.techExperience] = { clarity: [], control: [] };
        }
        analysis.experienceByTech[pre.techExperience].clarity.push(post.factOpinionClarity);
        analysis.experienceByTech[pre.techExperience].control.push(post.controlLevel);
      }
    });

    return analysis;
  }

  /**
   * Content Gap Analysis: Missed facts and information
   */
  static analyzeContentGaps(sessions: SessionData[]) {
    const analysis = {
      missedFactsScores: [] as number[],
      averageMissedFacts: 0,
      issuesReported: [] as string[],
      gapsByOutlet: {} as Record<string, number[]>,
      qualitativeGaps: [] as string[]
    };

    sessions.forEach(session => {
      if (session.postQuestionnaire) {
        const post = session.postQuestionnaire;
        
        analysis.missedFactsScores.push(post.missedFacts);
        
        if (post.issuesEncountered && post.issuesEncountered.toLowerCase() !== 'none') {
          analysis.issuesReported.push(post.issuesEncountered);
        }
        
        if (post.missedFactsSpecify) {
          analysis.qualitativeGaps.push(post.missedFactsSpecify);
        }
      }
    });

    if (analysis.missedFactsScores.length > 0) {
      analysis.averageMissedFacts = analysis.missedFactsScores.reduce((a, b) => a + b, 0) / analysis.missedFactsScores.length;
    }

    return analysis;
  }

  /**
   * Demographics Analysis: Performance by user characteristics
   */
  static analyzeDemographics(sessions: SessionData[]) {
    const analysis = {
      ageDistribution: {} as Record<string, number>,
      professionDistribution: {} as Record<string, number>,
      techExperienceDistribution: {} as Record<string, number>,
      newsFrequencyDistribution: {} as Record<string, number>,
      performanceByAge: {} as Record<string, { clarity: number[]; control: number[] }>,
      performanceByTech: {} as Record<string, { clarity: number[]; control: number[] }>
    };

    sessions.forEach(session => {
      if (session.preQuestionnaire) {
        const pre = session.preQuestionnaire;
        
        // Count distributions
        analysis.ageDistribution[pre.age] = (analysis.ageDistribution[pre.age] || 0) + 1;
        analysis.professionDistribution[pre.profession] = (analysis.professionDistribution[pre.profession] || 0) + 1;
        analysis.techExperienceDistribution[pre.techExperience] = (analysis.techExperienceDistribution[pre.techExperience] || 0) + 1;
        analysis.newsFrequencyDistribution[pre.newsFrequency] = (analysis.newsFrequencyDistribution[pre.newsFrequency] || 0) + 1;
        
        if (session.postQuestionnaire) {
          const post = session.postQuestionnaire;
          
          // Performance by age groups
          const ageGroup = this.getAgeGroup(pre.age);
          if (!analysis.performanceByAge[ageGroup]) {
            analysis.performanceByAge[ageGroup] = { clarity: [], control: [] };
          }
          analysis.performanceByAge[ageGroup].clarity.push(post.factOpinionClarity);
          analysis.performanceByAge[ageGroup].control.push(post.controlLevel);
          
          // Performance by tech experience
          if (!analysis.performanceByTech[pre.techExperience]) {
            analysis.performanceByTech[pre.techExperience] = { clarity: [], control: [] };
          }
          analysis.performanceByTech[pre.techExperience].clarity.push(post.factOpinionClarity);
          analysis.performanceByTech[pre.techExperience].control.push(post.controlLevel);
        }
      }
    });

    return analysis;
  }

  // Helper functions
  private static getAgeGroup(age: string): string {
    const ageNum = parseInt(age);
    if (ageNum < 25) return '18-24';
    if (ageNum < 35) return '25-34';
    if (ageNum < 45) return '35-44';
    if (ageNum < 55) return '45-54';
    if (ageNum < 65) return '55-64';
    return '65+';
  }

  // Data export functions
  static exportToCSV(sessions: SessionData[]): string {
    const headers = [
      'sessionId', 'newsFamiliarity', 'newsFrequency', 'factOpinionConfidence', 'trustedOutlets',
      'outletsBiased', 'aiFamiliarityTools', 'headlineReliance', 'crossCheckFrequency',
      'techExperience', 'age', 'profession', 'mentalDemand', 'effortRequired', 'frustrationLevel',
      'factOpinionClarity', 'controlLevel', 'sourceInfluence', 'explanationHelpfulness',
      'mostHelpfulFeature', 'issuesEncountered', 'missedFacts', 'additionalComments'
    ];

    const rows = sessions.map(session => {
      const pre = session.preQuestionnaire;
      const post = session.postQuestionnaire;
      
      return [
        session.sessionId,
        pre?.newsFamiliarity || '',
        pre?.newsFrequency || '',
        pre?.factOpinionConfidence || '',
        Array.isArray(pre?.trustedOutlets) ? pre.trustedOutlets.join(';') : (pre?.trustedOutlets || ''),
        pre?.outletsBiased || '',
        pre?.aiFamiliarityTools || '',
        pre?.headlineReliance || '',
        pre?.crossCheckFrequency || '',
        pre?.techExperience || '',
        pre?.age || '',
        pre?.profession || '',
        post?.mentalDemand || '',
        post?.effortRequired || '',
        post?.frustrationLevel || '',
        post?.factOpinionClarity || '',
        post?.controlLevel || '',
        post?.sourceInfluence || '',
        post?.explanationHelpfulness || '',
        Array.isArray(post?.mostHelpfulFeature) ? post.mostHelpfulFeature.join(';') : (post?.mostHelpfulFeature || ''),
        post?.issuesEncountered || '',
        post?.missedFacts || '',
        post?.additionalComments || ''
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