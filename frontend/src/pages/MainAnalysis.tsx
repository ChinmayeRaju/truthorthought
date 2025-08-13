import React, { useState } from 'react';
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
  ExclamationCircleOutlined
} from '@ant-design/icons';
import AppLayout from '../components/AppLayout';
import ChatComponent from '../components/ChatComponent';
import { apiService } from '../services/api';
import type { AnalysisResult, Statement } from '../types';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const MainAnalysis: React.FC = () => {
  const [urls, setUrls] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [showChat, setShowChat] = useState(false);

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

  const getDomainColor = (domain: string) => {
    const domainColors: Record<string, string> = {
      'NEWS': 'green',
      'POLITICS': 'blue',
      'CONFLICT': 'red',
      'FINANCE': 'orange',
      'HEALTH': 'pink',
      'TECHNOLOGY': 'cyan',
      'SPORTS': 'purple',
      'MULTI-SOURCE': 'magenta',
      'GENERAL': 'default',
    };
    return domainColors[domain] || 'default';
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
          {statement.sentence}
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
                
                {/* Analysis Header */}
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

                  {results.domain && (
                    <div style={{ marginTop: 16 }}>
                      <Space>
                        <Text strong>Domain:</Text>
                        <Tag color={getDomainColor(results.domain)}>
                          {results.domain}
                        </Tag>
                        {results.specialists && results.specialists.length > 0 && (
                          <>
                            <Text strong>AI Specialists:</Text>
                            <Text type="secondary">{results.specialists.join(', ')}</Text>
                          </>
                        )}
                      </Space>
                    </div>
                  )}
                </Card>

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
