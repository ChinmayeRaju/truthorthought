import React, { useState, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Row,
  Col,
  Statistic,
  Typography,
  message,
  Spin,
  Tag,
  Divider,
  Badge,
  Space,
  Alert
} from 'antd';
import {
  BarChartOutlined,
  CheckCircleOutlined,
  CommentOutlined,
  LinkOutlined,
  RocketOutlined,
  TrophyOutlined,
  ExclamationCircleOutlined,
  UserOutlined,
  TeamOutlined,
  SoundOutlined,
  ContactsOutlined,
  FormOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import ChatComponent from '../components/ChatComponent';
import { apiService } from '../services/api';
import type { AnalysisResult, Statement, KeyFigure, KeyFiguresData, SummaryResponse, ContentSummary, MultiSourceSummary, KeyPersonnel, ImportantQuote, KeyInsight } from '../types';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const MainAnalysis: React.FC = () => {
  const [urls, setUrls] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [showPostQuestionnaire, setShowPostQuestionnaire] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const sessionId = searchParams.get('sessionId');
  const fromQuestionnaire = searchParams.get('fromQuestionnaire') === 'true';

  useEffect(() => {
    // Show post-questionnaire option after user has interacted with results
    if (results && fromQuestionnaire) {
      const timer = setTimeout(() => {
        setShowPostQuestionnaire(true);
      }, 30000); // Show after 30 seconds of analysis interaction
      
      return () => clearTimeout(timer);
    }
  }, [results, fromQuestionnaire]);

  const handleAnalyze = async () => {
    if (!urls.trim()) {
      message.error('Please enter at least one URL');
      return;
    }

    const urlList = urls
      .split('\n')
      .map(url => url.trim())
      .filter(url => url.length > 0);

    if (urlList.length === 0) {
      message.error('Please enter valid URLs');
      return;
    }

    const invalidUrls = urlList.filter(url => !url.match(/^https?:\/\/.+/));
    if (invalidUrls.length > 0) {
      message.error(`Invalid URLs detected: ${invalidUrls.join(', ')}`);
      return;
    }

    setLoading(true);
    try {
      const result = await apiService.analyzeMultipleUrls(urlList, 15, 'combined');
      if (result.success) {
        console.log('Analysis result received:', {
          factsCount: result.facts?.length || 0,
          opinionsCount: result.opinions?.length || 0,
          facts: result.facts,
          sampleFact: result.facts?.[0]
        });
        setResults(result);
        setShowChat(true);
        
        // Log the analysis interaction
        if (sessionId && result.session_id) {
          try {
            await fetch('/api/log_interaction', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: sessionId,
                type: 'analysis_completion',
                data: {
                  analysis_session_id: result.session_id,
                  urls_analyzed: urlList,
                  facts_count: result.facts?.length || 0,
                  opinions_count: result.opinions?.length || 0,
                  total_sentences: result.total_sentences || 0,
                  completion_time: new Date().toISOString()
                }
              })
            });
          } catch (error) {
            console.warn('Failed to log analysis interaction:', error);
          }
        }
        
        // Generate summary after successful analysis
        if (result.session_id) {
          handleGenerateSummary(result.session_id);
        }
        
        message.success('Analysis completed successfully!');
      } else {
        message.error('Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      message.error('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSummary = async (sessionId: string) => {
    setLoadingSummary(true);
    try {
      const summaryResult = await apiService.summarizeSession(sessionId);
      if (summaryResult.success) {
        setSummary(summaryResult);
        console.log('Summary generated:', summaryResult);
      } else {
        message.error('Failed to generate summary');
      }
    } catch (error) {
      console.error('Summary generation error:', error);
      message.error('Failed to generate summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const StatementCard: React.FC<{ statement: Statement; type: 'fact' | 'opinion' }> = ({ statement, type }) => {
    // Check if this was reclassified from fact to opinion due to missing citations
    const wasReclassified = statement.reasoning?.includes('reclassified as OPINION per verification standards');
    
    // Debug logging
    console.log('StatementCard rendering:', {
      sentence: statement.sentence?.substring(0, 50) + '...',
      type,
      hasCitations: statement.citations && statement.citations.length > 0,
      citationsCount: statement.citations?.length || 0,
      citations: statement.citations
    });
    
    return (
      <Card 
        size="small" 
        style={{ 
          marginBottom: 12,
          border: `1px solid ${type === 'fact' ? '#52c41a' : '#faad14'}`,
          borderLeft: `4px solid ${type === 'fact' ? '#52c41a' : '#faad14'}`
        }}
      >
        <Paragraph style={{ margin: 0, marginBottom: 8 }}>
          {/* Extract and highlight source attribution */}
          {(() => {
            const sentence = statement.sentence || '';
            
            // Check if we have source_tag metadata from backend
            if (statement.source_tag) {
              const sourceTag = statement.source_tag;
              // Extract the sentence content after "SourceName reported"
              const reportedMatch = sentence.match(/^(.+?) reported (.+)$/);
              
              if (reportedMatch) {
                const [, sourceName, restOfSentence] = reportedMatch;
                return (
                  <>
                    <Tag
                      color={sourceTag.tag_style === 'primary' ? 'blue' :
                             sourceTag.tag_style === 'warning' ? 'orange' :
                             sourceTag.tag_style === 'info' ? 'cyan' :
                             sourceTag.tag_style === 'success' ? 'green' :
                             sourceTag.tag_style === 'dark' ? 'default' : 'blue'}
                      style={{
                        marginRight: 8,
                        marginBottom: 4,
                        fontWeight: 'bold',
                        fontSize: '12px',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        backgroundColor: sourceTag.tag_color,
                        borderColor: sourceTag.tag_color,
                        color: sourceTag.tag_style === 'dark' || sourceTag.tag_color === '#000000' ? 'white' : undefined
                      }}
                    >
                      📰 {sourceTag.short_name}
                    </Tag>
                    <span>{restOfSentence}</span>
                  </>
                );
              }
            }
            
            // Fallback: try to match with expanded regex for outlets not yet using source_tag
            const sourceMatch = sentence.match(/^(BBC|CNN|Reuters|Guardian|The Guardian|The New York Times|Washington Post|NPR|Sky News|Associated Press|Metro|Al Jazeera|Fox News|NBC News|ABC News|CBS News|The Independent|Daily Mail|The Telegraph|USA Today|The Wall Street Journal|Bloomberg|Politico|HuffPost|Economic Times|Times of India|Hindustan Times|The Indian Express|NDTV|News18|Zee News|Firstpost|Mint|Business Standard|The Financial Express|Moneycontrol|CNBC|MarketWatch|Fortune|Forbes|TechCrunch|The Verge|Engadget|Wired|Ars Technica) reported (.+)$/);
            
            if (sourceMatch) {
              const [, sourceName, restOfSentence] = sourceMatch;
              return (
                <>
                  <Tag
                    color="blue"
                    style={{
                      marginRight: 8,
                      marginBottom: 4,
                      fontWeight: 'bold',
                      fontSize: '12px',
                      padding: '2px 8px',
                      borderRadius: '4px'
                    }}
                  >
                    📰 {sourceName}
                  </Tag>
                  <span>{restOfSentence}</span>
                </>
              );
            }
            
            return sentence;
          })()}
        </Paragraph>
        
        {wasReclassified && (
          <Alert
            message="Auto-reclassified as Opinion"
            description="Originally classified as fact but reclassified as opinion due to lack of verifiable citations"
            type="warning"
            showIcon
            style={{ marginBottom: 8, fontSize: '12px' }}
          />
        )}
        
        {statement.citations && statement.citations.length > 0 && (
          <div style={{ marginTop: 8, padding: 12, backgroundColor: '#f8f9fa', borderRadius: 6, border: '1px solid #e9ecef' }}>
            <Text strong style={{ fontSize: '12px', color: '#1890ff', display: 'block', marginBottom: 8 }}>
              <LinkOutlined /> Verified Sources ({statement.citations.length}):
            </Text>
            {statement.citations.map((citation, index) => (
              <div key={index} style={{ 
                marginBottom: 8, 
                padding: 8, 
                backgroundColor: 'white', 
                borderRadius: 4,
                border: '1px solid #f0f0f0'
              }}>
                <div style={{ marginBottom: 4 }}>
                  <a 
                    href={citation.url.startsWith('http') ? citation.url : `https://${citation.url}`}
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ fontSize: '13px', fontWeight: 500, color: '#1890ff' }}
                  >
                    {citation.title}
                  </a>
                </div>
                
                {citation.domain && (
                  <div style={{ fontSize: '11px', color: '#666', marginBottom: 2 }}>
                    🏛️ {citation.domain}
                  </div>
                )}
                
                {citation.verification_score && (
                  <div style={{ fontSize: '11px', marginBottom: 2 }}>
                    <span style={{ 
                      color: citation.verification_score >= 0.8 ? '#52c41a' : 
                             citation.verification_score >= 0.6 ? '#faad14' : '#ff4d4f',
                      fontWeight: 500
                    }}>
                      📊 Quality Score: {(citation.verification_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                
                {citation.snippet && (
                  <div style={{ 
                    fontSize: '11px', 
                    color: '#666', 
                    fontStyle: 'italic',
                    marginTop: 4,
                    padding: 4,
                    backgroundColor: '#fafafa',
                    borderRadius: 3
                  }}>
                    "{citation.snippet.length > 120 ? citation.snippet.substring(0, 120) + '...' : citation.snippet}"
                  </div>
                )}
                
                {citation.reasoning && (
                  <div style={{ 
                    fontSize: '10px', 
                    color: '#999',
                    marginTop: 4
                  }}>
                    💭 {citation.reasoning.length > 80 ? citation.reasoning.substring(0, 80) + '...' : citation.reasoning}
                  </div>
                )}
              </div>
            ))}
            <div style={{ fontSize: '10px', color: '#999', marginTop: 4, textAlign: 'center' }}>
              🔍 Verified using Gemini with Google Search grounding
            </div>
          </div>
        )}
        
        {statement.source_title && (
          <div style={{ marginTop: 8 }}>
            <Tag color="blue">
              {statement.source_title}
            </Tag>
          </div>
        )}
      </Card>
    );
  };

  const KeyFiguresCard: React.FC<{ keyFigures: KeyFiguresData }> = ({ keyFigures }) => {
    // Group figures by source URL
    const figuresBySource: { [url: string]: KeyFigure[] } = {};
    
    // Collect all figures from all categories
    const allFigures: KeyFigure[] = [];
    if (keyFigures.categories?.primary_actors?.figures) allFigures.push(...keyFigures.categories.primary_actors.figures);
    if (keyFigures.categories?.secondary_participants?.figures) allFigures.push(...keyFigures.categories.secondary_participants.figures);
    if (keyFigures.categories?.quoted_sources?.figures) allFigures.push(...keyFigures.categories.quoted_sources.figures);
    if (keyFigures.categories?.other?.figures) allFigures.push(...keyFigures.categories.other.figures);
    
    // Group by source URL
    allFigures.forEach(figure => {
      const sourceUrl = figure.source_url || 'Unknown Source';
      if (!figuresBySource[sourceUrl]) {
        figuresBySource[sourceUrl] = [];
      }
      figuresBySource[sourceUrl].push(figure);
    });

    const getSourceName = (url: string) => {
      if (url === 'Unknown Source') return url;
      try {
        const domain = new URL(url).hostname.replace('www.', '');
        return domain.charAt(0).toUpperCase() + domain.slice(1);
      } catch {
        return url;
      }
    };

    return (
      <Card
        title={
          <Space>
            <UserOutlined style={{ color: '#3498db' }} />
            Key Figures Identified
            <Badge count={keyFigures.total_figures} style={{ backgroundColor: '#3498db' }} />
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        {keyFigures.total_figures > 0 ? (
          <div>
            {Object.entries(figuresBySource).map(([sourceUrl, figures]) => (
              <Card
                key={sourceUrl}
                size="small"
                title={
                  <Space>
                    <LinkOutlined style={{ color: '#1890ff' }} />
                    <Text strong>{getSourceName(sourceUrl)}</Text>
                    <Badge count={figures.length} size="small" style={{ backgroundColor: '#52c41a' }} />
                  </Space>
                }
                style={{ marginBottom: 16 }}
              >
                <div style={{ marginBottom: 12 }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Source: {sourceUrl}
                  </Text>
                </div>
                
                <Row gutter={[8, 8]}>
                  {figures.map((figure, index) => (
                    <Col span={12} key={index}>
                      <Card size="small" style={{ height: '100%' }}>
                        <div style={{ marginBottom: 8 }}>
                          <Text strong style={{ fontSize: '14px', color: '#1890ff' }}>
                            {figure.full_name}
                          </Text>
                          {figure.title && (
                            <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                              <strong>Title:</strong> {figure.title}
                            </div>
                          )}
                          {figure.organization && (
                            <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                              <strong>Organization:</strong> {figure.organization}
                            </div>
                          )}
                        </div>
                        
                        {figure.role_in_story && (
                          <div style={{ fontSize: '12px', marginBottom: 4 }}>
                            <strong>Role:</strong> {figure.role_in_story}
                          </div>
                        )}
                        
                        {figure.significance && (
                          <div style={{ fontSize: '12px', marginBottom: 4 }}>
                            <strong>Significance:</strong> {figure.significance}
                          </div>
                        )}
                        
                        {figure.category && (
                          <div style={{ marginTop: 8 }}>
                            <Tag color={
                              figure.category === 'primary_actor' ? 'blue' :
                              figure.category === 'secondary_participant' ? 'green' :
                              figure.category === 'quoted_source' ? 'orange' : 'purple'
                            }>
                              {figure.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Tag>
                          </div>
                        )}
                      </Card>
                    </Col>
                  ))}
                </Row>
              </Card>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <ExclamationCircleOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">No key figures identified</Text>
            </div>
          </div>
        )}
      </Card>
    );
  };

  const SummaryCard: React.FC<{ summary: ContentSummary | MultiSourceSummary; summaryType?: string }> = ({ summary, summaryType }) => {
    const isSingleSource = 'key_personnel' in summary;
    
    if (isSingleSource) {
      const singleSummary = summary as ContentSummary;
      return (
        <Card
          title={
            <Space>
              <SoundOutlined style={{ color: '#722ed1' }} />
              Content Summary
              <Tag color="purple">{singleSummary.content_type}</Tag>
            </Space>
          }
          style={{ marginBottom: 24 }}
        >
          {/* Executive Summary */}
          <Card size="small" title="Executive Summary" style={{ marginBottom: 16 }}>
            <Paragraph>{singleSummary.executive_summary}</Paragraph>
          </Card>

          {/* Main Themes */}
          {singleSummary.main_themes.length > 0 && (
            <Card size="small" title="Main Themes" style={{ marginBottom: 16 }}>
              <Space wrap>
                {singleSummary.main_themes.map((theme, index) => (
                  <Tag key={index} color="blue">{theme}</Tag>
                ))}
              </Space>
            </Card>
          )}

          {/* Key Personnel */}
          {singleSummary.key_personnel.length > 0 && (
            <Card size="small" title={
              <Space>
                <ContactsOutlined style={{ color: '#1890ff' }} />
                Key Personnel ({singleSummary.key_personnel.length})
              </Space>
            } style={{ marginBottom: 16 }}>
              <Row gutter={[16, 16]}>
                {singleSummary.key_personnel.map((person, index) => (
                  <Col span={12} key={index}>
                    <Card size="small" style={{ height: '100%' }}>
                      <div style={{ marginBottom: 8 }}>
                        <Text strong style={{ fontSize: '14px', color: '#1890ff' }}>
                          {person.name}
                        </Text>
                        {person.title && (
                          <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                            <strong>Title:</strong> {person.title}
                          </div>
                        )}
                        {person.organization && (
                          <div style={{ fontSize: '12px', color: '#666', marginTop: 2 }}>
                            <strong>Organization:</strong> {person.organization}
                          </div>
                        )}
                        {person.role_in_story && (
                          <div style={{ fontSize: '12px', marginTop: 4 }}>
                            <strong>Role:</strong> {person.role_in_story}
                          </div>
                        )}
                        <div style={{ fontSize: '11px', color: '#999', marginTop: 4 }}>
                          Relevance: {(person.relevance_score * 100).toFixed(0)}%
                        </div>
                      </div>
                      {person.quotes.length > 0 && (
                        <div style={{ marginTop: 8 }}>
                          <Text strong style={{ fontSize: '11px' }}>Quotes:</Text>
                          {person.quotes.slice(0, 2).map((quote, qIndex) => (
                            <div key={qIndex} style={{
                              fontSize: '10px',
                              fontStyle: 'italic',
                              marginTop: 2,
                              padding: 4,
                              backgroundColor: '#f5f5f5',
                              borderRadius: 3
                            }}>
                              "{quote.length > 80 ? quote.substring(0, 80) + '...' : quote}"
                            </div>
                          ))}
                        </div>
                      )}
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          )}

          {/* Important Quotes */}
          {singleSummary.important_quotes.length > 0 && (
            <Card size="small" title={
              <Space>
                <CommentOutlined style={{ color: '#faad14' }} />
                Important Quotes ({singleSummary.important_quotes.length})
              </Space>
            } style={{ marginBottom: 16 }}>
              {singleSummary.important_quotes.slice(0, 5).map((quote, index) => (
                <Card key={index} size="small" style={{ marginBottom: 12 }}>
                  <div style={{ marginBottom: 8 }}>
                    <Text style={{ fontSize: '13px', fontStyle: 'italic' }}>
                      "{quote.quote}"
                    </Text>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
                    <strong>Speaker:</strong> {quote.speaker} {quote.speaker_title && `(${quote.speaker_title})`}
                  </div>
                  {quote.context && (
                    <div style={{ fontSize: '11px', color: '#999', marginBottom: 4 }}>
                      <strong>Context:</strong> {quote.context}
                    </div>
                  )}
                  {quote.significance && (
                    <div style={{ fontSize: '11px', color: '#666' }}>
                      <strong>Significance:</strong> {quote.significance}
                    </div>
                  )}
                  <div style={{ fontSize: '10px', color: '#999', marginTop: 4 }}>
                    Impact Score: {(quote.impact_score * 100).toFixed(0)}%
                  </div>
                </Card>
              ))}
            </Card>
          )}

          {/* Key Insights */}
          {singleSummary.key_insights.length > 0 && (
            <Card size="small" title={
              <Space>
                <BarChartOutlined style={{ color: '#52c41a' }} />
                Key Insights ({singleSummary.key_insights.length})
              </Space>
            } style={{ marginBottom: 16 }}>
              {singleSummary.key_insights.slice(0, 8).map((insight, index) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <div style={{ marginBottom: 4 }}>
                    <Tag color={
                      insight.category === 'main_point' ? 'blue' :
                      insight.category === 'consequence' ? 'red' :
                      insight.category === 'statistic' ? 'green' :
                      insight.category === 'prediction' ? 'purple' : 'orange'
                    }>
                      {insight.category.replace('_', ' ').toUpperCase()}
                    </Tag>
                    <span style={{ fontSize: '12px', marginLeft: 8 }}>
                      Importance: {(insight.importance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', marginBottom: 4 }}>
                    {insight.insight}
                  </div>
                  {insight.supporting_evidence && (
                    <div style={{ fontSize: '11px', color: '#666', fontStyle: 'italic' }}>
                      Evidence: {insight.supporting_evidence}
                    </div>
                  )}
                </Card>
              ))}
            </Card>
          )}

          {/* Credibility Indicators */}
          {singleSummary.credibility_indicators.length > 0 && (
            <Card size="small" title="Credibility Indicators">
              <Space wrap>
                {singleSummary.credibility_indicators.map((indicator, index) => (
                  <Tag key={index} color="green">{indicator}</Tag>
                ))}
              </Space>
            </Card>
          )}
        </Card>
      );
    } else {
      // Multi-source summary display
      const multiSummary = summary as MultiSourceSummary;
      return (
        <Card
          title={
            <Space>
              <TeamOutlined style={{ color: '#722ed1' }} />
              Multi-Source Summary
              <Badge count={multiSummary.individual_summaries.length} style={{ backgroundColor: '#722ed1' }} />
            </Space>
          }
          style={{ marginBottom: 24 }}
        >
          {/* Aggregated Data Overview */}
          <Card size="small" title="Overview" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="Total Personnel"
                  value={multiSummary.aggregated_data.total_personnel}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Total Quotes"
                  value={multiSummary.aggregated_data.total_quotes}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Total Insights"
                  value={multiSummary.aggregated_data.total_insights}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Sources"
                  value={multiSummary.individual_summaries.length}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>
          </Card>

          {/* Common Themes */}
          {multiSummary.aggregated_data.common_themes.length > 0 && (
            <Card size="small" title="Common Themes Across Sources" style={{ marginBottom: 16 }}>
              <Space wrap>
                {multiSummary.aggregated_data.common_themes.map((theme, index) => (
                  <Tag key={index} color="blue">{theme}</Tag>
                ))}
              </Space>
            </Card>
          )}

          {/* Top Personnel */}
          {multiSummary.aggregated_data.top_personnel.length > 0 && (
            <Card size="small" title="Most Relevant Personnel" style={{ marginBottom: 16 }}>
              <Row gutter={[8, 8]}>
                {multiSummary.aggregated_data.top_personnel.slice(0, 6).map((person, index) => (
                  <Col span={8} key={index}>
                    <Card size="small">
                      <Text strong style={{ fontSize: '12px' }}>{person.name}</Text>
                      <div style={{ fontSize: '10px', color: '#666' }}>
                        {person.title} {person.organization && `at ${person.organization}`}
                      </div>
                      <div style={{ fontSize: '10px', color: '#999' }}>
                        Relevance: {(person.relevance_score * 100).toFixed(0)}%
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          )}

          {/* Most Impactful Quotes */}
          {multiSummary.aggregated_data.most_impactful_quotes.length > 0 && (
            <Card size="small" title="Most Impactful Quotes">
              {multiSummary.aggregated_data.most_impactful_quotes.slice(0, 3).map((quote, index) => (
                <Card key={index} size="small" style={{ marginBottom: 8 }}>
                  <Text style={{ fontSize: '12px', fontStyle: 'italic' }}>
                    "{quote.quote.length > 120 ? quote.quote.substring(0, 120) + '...' : quote.quote}"
                  </Text>
                  <div style={{ fontSize: '11px', color: '#666', marginTop: 4 }}>
                    — {quote.speaker} {quote.speaker_title && `(${quote.speaker_title})`}
                  </div>
                  <div style={{ fontSize: '10px', color: '#999' }}>
                    Impact: {(quote.impact_score * 100).toFixed(0)}%
                  </div>
                </Card>
              ))}
            </Card>
          )}
        </Card>
      );
    }
  };

  return (
    <AppLayout>
      <Row gutter={[24, 24]} style={{ height: '100%' }}>
        <Col span={24}>
          <Card
            style={{ 
              borderRadius: 15, 
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              background: 'white'
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Title level={2} style={{ marginBottom: 8 }}>
                <RocketOutlined style={{ color: '#3498db', marginRight: 8 }} />
                Truth or Thought Analysis
              </Title>
              <Text type="secondary" style={{ fontSize: 16 }}>
                AI-Powered Fact vs Opinion Analysis for Modern Media
              </Text>
            </div>

            <Row gutter={[24, 24]}>
              <Col span={24}>
                <Card title="Multiple URL Analysis" size="small">
                  <TextArea
                    rows={6}
                    placeholder={`https://www.bbc.co.uk/news/article1
https://edition.cnn.com/article2
https://metro.co.uk/article3

Add multiple URLs to analyze and compare facts vs opinions across sources...`}
                    value={urls}
                    onChange={(e) => setUrls(e.target.value)}
                    style={{ marginBottom: 16 }}
                  />
                  <Alert
                    message="Supported sources: BBC, CNN, Metro, Reuters, Guardian, and other major news sites"
                    description="Tip: Add URLs covering the same story from different sources for comprehensive analysis"
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                  />
                  <div style={{ textAlign: 'center' }}>
                    <Button
                      type="primary"
                      size="large"
                      onClick={handleAnalyze}
                      loading={loading}
                      icon={<BarChartOutlined />}
                      style={{
                        background: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
                        border: 'none',
                        borderRadius: 8,
                        height: 48,
                        fontSize: 16,
                        fontWeight: 600,
                      }}
                    >
                      Analyze Multiple Sources
                    </Button>
                  </div>
                </Card>
              </Col>
            </Row>

            {loading && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>Analyzing... this may take a moment.</Text>
                </div>
              </div>
            )}

            {results && (
              <>
                <Divider />
                
                {/* Analysis Header - Removed Domain and Specialists */}
                <Card 
                  title={
                    <Space>
                      <TrophyOutlined style={{ color: '#3498db' }} />
                      Analysis Results
                    </Space>
                  }
                  style={{ marginBottom: 24 }}
                >
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="Final Classification"
                        value={results.final_classification || 'N/A'}
                        valueStyle={{ 
                          color: results.final_classification === 'FACT-DOMINANT' ? '#3f8600' : 
                                results.final_classification === 'OPINION-DOMINANT' ? '#cf1322' : '#722ed1'
                        }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Confidence Score"
                        value={results.confidence || 0}
                        suffix="%"
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Total Facts"
                        value={results.total_facts || results.facts?.length || 0}
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Total Opinions"
                        value={results.total_opinions || results.opinions?.length || 0}
                        valueStyle={{ color: '#cf1322' }}
                      />
                    </Col>
                  </Row>
                </Card>

                {/* Content Summary */}
                {summary && (
                  <SummaryCard
                    summary={summary.summary}
                    summaryType={summary.summary_type}
                  />
                )}

                {loadingSummary && (
                  <Card style={{ marginBottom: 24, textAlign: 'center' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: 16 }}>
                      <Text>Generating content summary...</Text>
                    </div>
                  </Card>
                )}

                {/* Consensus Summary */}
                {results.results && (
                  <Card
                    title="Consensus Summary"
                    style={{ marginBottom: 24 }}
                  >
                    <Paragraph>{results.results}</Paragraph>
                  </Card>
                )}

                {/* Facts and Opinions */}
                <Row gutter={24}>
                  <Col span={12}>
                    <Card
                      title={
                        <Space>
                          <CheckCircleOutlined style={{ color: '#52c41a' }} />
                          Verified Facts
                          <Badge count={results.facts?.length || 0} style={{ backgroundColor: '#52c41a' }} />
                        </Space>
                      }
                      style={{ height: '600px', overflow: 'auto' }}
                    >
                      {results.facts && results.facts.length > 0 ? (
                        results.facts.map((fact, index) => {
                          console.log(`Rendering fact ${index}:`, {
                            sentence: fact.sentence?.substring(0, 50),
                            citations: fact.citations,
                            citation: fact.citation,
                            fullFact: fact
                          });
                          return (
                            <StatementCard
                              key={index}
                              statement={fact}
                              type="fact"
                            />
                          );
                        })
                      ) : (
                        <div style={{ textAlign: 'center', padding: 40 }}>
                          <ExclamationCircleOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                          <div style={{ marginTop: 16 }}>
                            <Text type="secondary">No facts identified</Text>
                          </div>
                        </div>
                      )}
                    </Card>
                  </Col>
                  
                  <Col span={12}>
                    <Card
                      title={
                        <Space>
                          <CommentOutlined style={{ color: '#faad14' }} />
                          Identified Opinions
                          <Badge count={results.opinions?.length || 0} style={{ backgroundColor: '#faad14' }} />
                        </Space>
                      }
                      style={{ height: '600px', overflow: 'auto' }}
                    >
                      {results.opinions && results.opinions.length > 0 ? (
                        results.opinions.map((opinion, index) => (
                          <StatementCard
                            key={index}
                            statement={opinion}
                            type="opinion"
                          />
                        ))
                      ) : (
                        <div style={{ textAlign: 'center', padding: 40 }}>
                          <ExclamationCircleOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                          <div style={{ marginTop: 16 }}>
                            <Text type="secondary">No opinions identified</Text>
                          </div>
                        </div>
                      )}
                    </Card>
                  </Col>
                </Row>

                {/* Post-Questionnaire Option */}
                {showPostQuestionnaire && sessionId && (
                  <Card
                    title={
                      <Space>
                        <FormOutlined style={{ color: '#52c41a' }} />
                        Complete Your Research Participation
                      </Space>
                    }
                    style={{
                      marginTop: 24,
                      border: '2px solid #52c41a',
                      borderRadius: 12
                    }}
                  >
                    <div style={{ textAlign: 'center', padding: '20px 0' }}>
                      <Typography.Title level={4} style={{ color: '#52c41a', marginBottom: 16 }}>
                        Thank you for using our AI bias detection system!
                      </Typography.Title>
                      <Typography.Paragraph style={{ fontSize: 16, marginBottom: 24 }}>
                        Help us improve by sharing your experience in our post-study questionnaire.
                        Your feedback is valuable for advancing AI-assisted media literacy research.
                      </Typography.Paragraph>
                      <Space size="large">
                        <Button
                          type="primary"
                          size="large"
                          icon={<FormOutlined />}
                          onClick={() => navigate(`/post-questionnaire?type=post&sessionId=${sessionId}`)}
                          style={{
                            background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                            border: 'none',
                            borderRadius: 8,
                            height: 48,
                            fontSize: 16,
                            fontWeight: 600,
                          }}
                        >
                          Complete Post-Study Questionnaire
                        </Button>
                        <Button
                          size="large"
                          onClick={() => setShowPostQuestionnaire(false)}
                          style={{ height: 48 }}
                        >
                          Maybe Later
                        </Button>
                      </Space>
                    </div>
                  </Card>
                )}

                {/* Chat Component */}
                {showChat && results.session_id && (
                  <Card title="Chat with AI" style={{ marginTop: 24 }}>
                    <ChatComponent sessionId={results.session_id} />
                  </Card>
                )}
              </>
            )}
          </Card>
        </Col>
      </Row>
    </AppLayout>
  );
};

export default MainAnalysis;