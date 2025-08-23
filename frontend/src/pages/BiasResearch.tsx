import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Row, 
  Col, 
  Typography, 
  message, 
  Spin, 
  List,
  Tag,
  Space,
  Statistic,
  Alert,
  Select
} from 'antd';
import { 
  ExperimentOutlined, 
  BarChartOutlined, 
  FileTextOutlined,
  LinkOutlined,
  SearchOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import AppLayout from '../components/AppLayout';
import { apiService } from '../services/api';
import type { SessionInfo, BiasAnalysisSession, IndividualResult } from '../types';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

const BiasResearch: React.FC = () => {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [selectedSession, setSelectedSession] = useState<BiasAnalysisSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoadingSessions(true);
    try {
      const response = await apiService.getAnalyzedSessions();
      if (response.success) {
        setSessions(response.sessions);
      } else {
        message.error('Failed to load sessions');
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
      message.error('Network error occurred');
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadSessionDetails = async (sessionId: string) => {
    setLoading(true);
    try {
      const response = await apiService.loadSessionForBias(sessionId);
      if (response.success) {
        setSelectedSession(response);
        message.success('Session loaded successfully');
      } else {
        message.error('Failed to load session details');
      }
    } catch (error) {
      console.error('Error loading session details:', error);
      message.error('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSourceContent = (result: IndividualResult) => {
    return result.formatted_content || result.full_content || result.raw_content || 'Content not available';
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
                <ExperimentOutlined style={{ color: '#3498db', marginRight: 8 }} />
                Bias Analysis Research
              </Title>
              <Text type="secondary" style={{ fontSize: 16 }}>
                Analyze previous sessions for media bias patterns and research insights
              </Text>
            </div>

            {/* Session Selection */}
            <Card title="Load Previous Analysis Session" style={{ marginBottom: 24 }}>
              <Space style={{ width: '100%', marginBottom: 16 }} direction="vertical">
                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                  <Select
                    style={{ flex: 1 }}
                    placeholder="Select a session to analyze"
                    loading={loadingSessions}
                    onChange={(sessionId) => loadSessionDetails(sessionId)}
                    optionFilterProp="children"
                    showSearch
                  >
                    {sessions.map(session => (
                      <Option key={session.session_id} value={session.session_id}>
                        <div>
                          <Text strong>{session.title}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {session.domain} • {session.total_facts} facts, {session.total_opinions} opinions • {session.timestamp}
                          </Text>
                        </div>
                      </Option>
                    ))}
                  </Select>
                  <Button 
                    icon={<ReloadOutlined />} 
                    onClick={loadSessions}
                    loading={loadingSessions}
                  >
                    Refresh
                  </Button>
                </div>
                <Alert
                  message="Select a session to view detailed bias analysis and source comparisons"
                  type="info"
                  showIcon
                />
              </Space>
            </Card>

            {loading && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>Loading session details...</Text>
                </div>
              </div>
            )}

            {selectedSession && !loading && (
              <>
                {/* Session Overview */}
                <Card 
                  title={
                    <Space>
                      <BarChartOutlined style={{ color: '#3498db' }} />
                      Session Analysis: {selectedSession.title}
                    </Space>
                  }
                  style={{ marginBottom: 24 }}
                >
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="Domain"
                        value={selectedSession.domain}
                        valueStyle={{ fontSize: '16px' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Total Facts"
                        value={selectedSession.total_facts}
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Total Opinions"
                        value={selectedSession.total_opinions}
                        valueStyle={{ color: '#cf1322' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="Analysis Date"
                        value={new Date(selectedSession.timestamp).toLocaleDateString()}
                        valueStyle={{ fontSize: '16px' }}
                      />
                    </Col>
                  </Row>

                  {selectedSession.url && (
                    <div style={{ marginTop: 16 }}>
                      <Space>
                        <Text strong>Source URL:</Text>
                        <a href={selectedSession.url} target="_blank" rel="noopener noreferrer">
                          <LinkOutlined /> {selectedSession.url}
                        </a>
                      </Space>
                    </div>
                  )}
                </Card>

                {/* Multi-Source Analysis */}
                {selectedSession.is_multiple && selectedSession.multiple_results && (
                  <div style={{ display: 'flex', height: 'calc(100vh - 400px)', gap: 24 }}>
                    {/* Source URLs Panel */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                      <Card
                        title={
                          <Space>
                            <LinkOutlined />
                            Source URLs ({selectedSession.multiple_results.length})
                          </Space>
                        }
                        style={{ height: '100%' }}
                        bodyStyle={{ padding: 16, height: 'calc(100% - 57px)', overflow: 'auto' }}
                      >
                        {selectedSession.multiple_results && selectedSession.multiple_results.length > 0 ? (
                          <List
                            dataSource={selectedSession.multiple_results}
                            renderItem={(result, index) => (
                              <List.Item style={{ padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                                <div style={{ width: '100%' }}>
                                  <div style={{ marginBottom: 8 }}>
                                    <Text strong style={{ fontSize: '14px', color: '#1890ff', display: 'block', marginBottom: 4 }}>
                                      Source {index + 1}
                                    </Text>
                                    <Text style={{ fontSize: '13px', color: '#333', display: 'block', marginBottom: 8, lineHeight: 1.4 }}>
                                      {result.title || result.scraped_title || 'Unknown Title'}
                                    </Text>
                                  </div>
                                  
                                  <a
                                    href={result.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      fontSize: '13px',
                                      wordBreak: 'break-all',
                                      display: 'block',
                                      padding: '12px 16px',
                                      background: '#f8f9fa',
                                      border: '1px solid #dee2e6',
                                      borderRadius: '6px',
                                      textDecoration: 'none',
                                      color: '#0066cc',
                                      width: '100%',
                                      transition: 'all 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = '#e9ecef';
                                      e.currentTarget.style.borderColor = '#adb5bd';
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = '#f8f9fa';
                                      e.currentTarget.style.borderColor = '#dee2e6';
                                    }}
                                  >
                                    <LinkOutlined style={{ marginRight: 8 }} />
                                    {result.url}
                                  </a>
                                </div>
                              </List.Item>
                            )}
                          />
                        ) : (
                          <div style={{
                            padding: 20,
                            textAlign: 'center',
                            color: '#999',
                            fontStyle: 'italic'
                          }}>
                            <Text>No source URLs found in this session.</Text>
                          </div>
                        )}
                      </Card>
                    </div>

                    {/* Analysis Panel */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                      <Card 
                        title={
                          <Space>
                            <SearchOutlined />
                            Bias Analysis Results
                          </Space>
                        }
                        style={{ height: '100%' }}
                        bodyStyle={{ padding: 0, height: 'calc(100% - 57px)', overflow: 'auto' }}
                      >
                        <div style={{ padding: 16 }}>
                          <Row gutter={[16, 16]}>
                            <Col span={12}>
                              <Card 
                                title={
                                  <Space>
                                    <Text style={{ color: '#52c41a' }}>✓ Facts</Text>
                                    <Tag color="green">{selectedSession.facts.length}</Tag>
                                  </Space>
                                }
                                size="small"
                                style={{ height: '400px', overflow: 'auto' }}
                              >
                                <List
                                  dataSource={selectedSession.facts}
                                  renderItem={(fact) => (
                                    <List.Item style={{ padding: '8px 0' }}>
                                      <div style={{ width: '100%' }}>
                                        <Paragraph style={{ margin: 0, fontSize: '13px' }}>
                                          {fact.sentence}
                                        </Paragraph>
                                        {fact.source_title && (
                                          <Tag color="blue" style={{ marginTop: 4, fontSize: '11px' }}>
                                            {fact.source_title}
                                          </Tag>
                                        )}
                                        {fact.citations && fact.citations.length > 0 && (
                                          <div style={{ marginTop: 4 }}>
                                            <Text type="secondary" style={{ fontSize: '11px' }}>
                                              <LinkOutlined /> {fact.citations.length} source(s)
                                            </Text>
                                          </div>
                                        )}
                                      </div>
                                    </List.Item>
                                  )}
                                />
                              </Card>
                            </Col>

                            <Col span={12}>
                              <Card 
                                title={
                                  <Space>
                                    <Text style={{ color: '#faad14' }}>💭 Opinions</Text>
                                    <Tag color="orange">{selectedSession.opinions.length}</Tag>
                                  </Space>
                                }
                                size="small"
                                style={{ height: '400px', overflow: 'auto' }}
                              >
                                <List
                                  dataSource={selectedSession.opinions}
                                  renderItem={(opinion) => (
                                    <List.Item style={{ padding: '8px 0' }}>
                                      <div style={{ width: '100%' }}>
                                        <Paragraph style={{ margin: 0, fontSize: '13px' }}>
                                          {opinion.sentence}
                                        </Paragraph>
                                        {opinion.source_title && (
                                          <Tag color="blue" style={{ marginTop: 4, fontSize: '11px' }}>
                                            {opinion.source_title}
                                          </Tag>
                                        )}
                                      </div>
                                    </List.Item>
                                  )}
                                />
                              </Card>
                            </Col>
                          </Row>
                        </div>
                      </Card>
                    </div>
                  </div>
                )}

                {/* Single Source Analysis */}
                {!selectedSession.is_multiple && (
                  <div style={{ display: 'flex', height: 'calc(100vh - 400px)', gap: 24 }}>
                    {/* Source URL */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                      <Card
                        title={
                          <Space>
                            <LinkOutlined />
                            Source URL
                          </Space>
                        }
                        style={{ height: '100%' }}
                        bodyStyle={{ padding: 16, height: 'calc(100% - 57px)', overflow: 'auto' }}
                      >
                        {selectedSession.url ? (
                          <a
                            href={selectedSession.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              fontSize: '14px',
                              wordBreak: 'break-all',
                              display: 'block',
                              padding: '12px 16px',
                              background: '#f8f9fa',
                              border: '1px solid #dee2e6',
                              borderRadius: '6px',
                              textDecoration: 'none',
                              color: '#0066cc',
                              width: '100%',
                              transition: 'all 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = '#e9ecef';
                              e.currentTarget.style.borderColor = '#adb5bd';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = '#f8f9fa';
                              e.currentTarget.style.borderColor = '#dee2e6';
                            }}
                          >
                            <LinkOutlined style={{ marginRight: 8 }} />
                            {selectedSession.url}
                          </a>
                        ) : (
                          <div style={{
                            padding: 16,
                            textAlign: 'center',
                            color: '#999',
                            fontStyle: 'italic'
                          }}>
                            No source URL available
                          </div>
                        )}
                      </Card>
                    </div>

                    {/* Analysis Results */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                      <Card 
                        title={
                          <Space>
                            <SearchOutlined />
                            Analysis Results
                          </Space>
                        }
                        style={{ height: '100%' }}
                        bodyStyle={{ padding: 0, height: 'calc(100% - 57px)', overflow: 'auto' }}
                      >
                        <div style={{ padding: 16 }}>
                          <Row gutter={[16, 16]}>
                            <Col span={12}>
                              <Card 
                                title={
                                  <Space>
                                    <Text style={{ color: '#52c41a' }}>✓ Facts</Text>
                                    <Tag color="green">{selectedSession.facts.length}</Tag>
                                  </Space>
                                }
                                size="small"
                                style={{ height: '400px', overflow: 'auto' }}
                              >
                                <List
                                  dataSource={selectedSession.facts}
                                  renderItem={(fact) => (
                                    <List.Item style={{ padding: '8px 0' }}>
                                      <div style={{ width: '100%' }}>
                                        <Paragraph style={{ margin: 0, fontSize: '13px' }}>
                                          {fact.sentence}
                                        </Paragraph>
                                        {fact.citations && fact.citations.length > 0 && (
                                          <div style={{ marginTop: 4 }}>
                                            <Text type="secondary" style={{ fontSize: '11px' }}>
                                              <LinkOutlined /> {fact.citations.length} source(s)
                                            </Text>
                                          </div>
                                        )}
                                      </div>
                                    </List.Item>
                                  )}
                                />
                              </Card>
                            </Col>

                            <Col span={12}>
                              <Card 
                                title={
                                  <Space>
                                    <Text style={{ color: '#faad14' }}>💭 Opinions</Text>
                                    <Tag color="orange">{selectedSession.opinions.length}</Tag>
                                  </Space>
                                }
                                size="small"
                                style={{ height: '400px', overflow: 'auto' }}
                              >
                                <List
                                  dataSource={selectedSession.opinions}
                                  renderItem={(opinion) => (
                                    <List.Item style={{ padding: '8px 0' }}>
                                      <Paragraph style={{ margin: 0, fontSize: '13px' }}>
                                        {opinion.sentence}
                                      </Paragraph>
                                    </List.Item>
                                  )}
                                />
                              </Card>
                            </Col>
                          </Row>
                        </div>
                      </Card>
                    </div>
                  </div>
                )}
              </>
            )}
          </Card>
        </Col>
      </Row>
    </AppLayout>
  );
};

export default BiasResearch;
