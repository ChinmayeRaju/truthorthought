import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Table,
  Button,
  Space,
  Tabs,
  Progress,
  Tag,
  Divider,
  message,
  Select,
  Descriptions
} from 'antd';
import {
  DownloadOutlined,
  BarChartOutlined,
  UserOutlined,
  ExperimentOutlined,
  TrophyOutlined,
  TeamOutlined,
  BulbOutlined,
  EyeOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import { QuestionnaireAnalyzer } from '../utils/questionnaireAnalysis';
import type { SessionData } from '../utils/questionnaireAnalysis';
import AppLayout from '../components/AppLayout';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const ResearchDashboard: React.FC = () => {
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('all');

  useEffect(() => {
    loadSessionData();
  }, []);

  const loadSessionData = () => {
    setLoading(true);
    try {
      const data = QuestionnaireAnalyzer.getAllSessionData();
      console.log('Loaded session data:', data);
      console.log('LocalStorage keys:', Object.keys(localStorage));
      
      // Debug individual sessions
      data.forEach((session, index) => {
        console.log(`Session ${index}:`, session);
        console.log(`Pre-questionnaire keys:`, session.preQuestionnaire ? Object.keys(session.preQuestionnaire) : 'None');
        console.log(`Post-questionnaire keys:`, session.postQuestionnaire ? Object.keys(session.postQuestionnaire) : 'None');
      });
      
      setSessions(data);
    } catch (error) {
      message.error('Failed to load session data');
      console.error('Error loading session data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    try {
      const csv = QuestionnaireAnalyzer.exportToCSV(sessions);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `questionnaire_data_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      message.success('Data exported successfully');
    } catch (error) {
      message.error('Failed to export data');
      console.error('Export error:', error);
    }
  };

  // Calculate summary statistics
  const completedSessions = sessions.filter(s => s.preQuestionnaire && s.postQuestionnaire);
  const preOnlySessions = sessions.filter(s => s.preQuestionnaire && !s.postQuestionnaire);
  const completionRate = sessions.length > 0 ? (completedSessions.length / sessions.length) * 100 : 0;

  // Analyze data using new analysis functions
  const taskLoadAnalysis = QuestionnaireAnalyzer.analyzeTaskLoad(completedSessions);
  const clarityAnalysis = QuestionnaireAnalyzer.analyzeSystemClarity(completedSessions);
  const trustAnalysis = QuestionnaireAnalyzer.analyzeTrustFactors(completedSessions);
  const featureAnalysis = QuestionnaireAnalyzer.analyzeFeatureEffectiveness(completedSessions);
  const userExperienceAnalysis = QuestionnaireAnalyzer.analyzeUserExperience(completedSessions);
  const contentGapAnalysis = QuestionnaireAnalyzer.analyzeContentGaps(completedSessions);
  const demographicsAnalysis = QuestionnaireAnalyzer.analyzeDemographics(completedSessions);

  // Calculate average satisfaction (using a relevant metric from new questionnaire)
  const avgClarity = clarityAnalysis.averageClarity;

  const overviewCards = [
    {
      title: 'Total Participants',
      value: sessions.length,
      icon: <UserOutlined />,
      color: '#3498db'
    },
    {
      title: 'Completed Studies',
      value: completedSessions.length,
      icon: <TrophyOutlined />,
      color: '#27ae60'
    },
    {
      title: 'Completion Rate',
      value: `${completionRate.toFixed(1)}%`,
      icon: <BarChartOutlined />,
      color: '#f39c12'
    },
    {
      title: 'Avg Clarity Rating',
      value: `${avgClarity.toFixed(1)}/5`,
      icon: <ExperimentOutlined />,
      color: '#e74c3c'
    }
  ];

  const researchQuestionTabs = [
    {
      key: '1',
      title: 'Task Load (NASA-TLX)',
      icon: <BarChartOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="NASA-TLX Analysis">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Average Mental Demand"
                    value={taskLoadAnalysis.mentalDemandScores.length > 0 
                      ? (taskLoadAnalysis.mentalDemandScores.reduce((a, b) => a + b, 0) / taskLoadAnalysis.mentalDemandScores.length).toFixed(1)
                      : 0}
                    suffix="/ 100"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Average Effort Required"
                    value={taskLoadAnalysis.effortScores.length > 0 
                      ? (taskLoadAnalysis.effortScores.reduce((a, b) => a + b, 0) / taskLoadAnalysis.effortScores.length).toFixed(1)
                      : 0}
                    suffix="/ 100"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Average Frustration"
                    value={taskLoadAnalysis.frustrationScores.length > 0 
                      ? (taskLoadAnalysis.frustrationScores.reduce((a, b) => a + b, 0) / taskLoadAnalysis.frustrationScores.length).toFixed(1)
                      : 0}
                    suffix="/ 100"
                  />
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={24}>
                  <Statistic
                    title="Overall Task Load Index"
                    value={taskLoadAnalysis.averageTLX.toFixed(1)}
                    suffix="/ 100"
                  />
                  <Progress 
                    percent={taskLoadAnalysis.averageTLX} 
                    strokeColor={taskLoadAnalysis.averageTLX > 70 ? '#ff4d4f' : taskLoadAnalysis.averageTLX > 40 ? '#faad14' : '#52c41a'}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '2',
      title: 'System Clarity',
      icon: <BulbOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Fact-Opinion Clarity">
              <Statistic
                title="Average Clarity Rating"
                value={clarityAnalysis.averageClarity.toFixed(1)}
                suffix="/ 5"
              />
              <Progress 
                percent={clarityAnalysis.averageClarity * 20} 
                strokeColor="#52c41a"
              />
              <Divider />
              <div>
                <Text strong>Clarity Distribution:</Text>
                {Object.entries(clarityAnalysis.clarityDistribution).map(([rating, count]) => (
                  <div key={rating} style={{ marginTop: 8 }}>
                    <Text>{rating}/5: </Text>
                    <Tag color="blue">{count} participants</Tag>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="User Control & Trust">
              <Row gutter={16}>
                <Col span={24}>
                  <Statistic
                    title="Average Control Level"
                    value={clarityAnalysis.controlScores.length > 0 
                      ? (clarityAnalysis.controlScores.reduce((a, b) => a + b, 0) / clarityAnalysis.controlScores.length).toFixed(1)
                      : 0}
                    suffix="/ 5"
                  />
                </Col>
              </Row>
              <Divider />
              <Row gutter={16}>
                <Col span={24}>
                  <Statistic
                    title="Source Label Influence"
                    value={clarityAnalysis.sourceInfluenceScores.length > 0 
                      ? (clarityAnalysis.sourceInfluenceScores.reduce((a, b) => a + b, 0) / clarityAnalysis.sourceInfluenceScores.length).toFixed(1)
                      : 0}
                    suffix="/ 5"
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '3',
      title: 'Trust & Bias',
      icon: <ExperimentOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Trusted News Outlets">
              <div>
                {Object.entries(trustAnalysis.trustedOutlets)
                  .sort(([,a], [,b]) => (b as number) - (a as number))
                  .map(([outlet, count]) => (
                    <div key={outlet} style={{ marginBottom: 8 }}>
                      <Text>{outlet.toUpperCase()}: </Text>
                      <Tag color="green">{count}</Tag>
                    </div>
                  ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Bias Perceptions">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="See Outlets as Biased"
                    value={trustAnalysis.biasPerceptions.yes}
                    suffix={`/ ${trustAnalysis.biasPerceptions.yes + trustAnalysis.biasPerceptions.no}`}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Don't See Bias"
                    value={trustAnalysis.biasPerceptions.no}
                    suffix={`/ ${trustAnalysis.biasPerceptions.yes + trustAnalysis.biasPerceptions.no}`}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '4',
      title: 'Feature Effectiveness',
      icon: <TeamOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Most Helpful Features">
              <div>
                {Object.entries(featureAnalysis.featureFrequency)
                  .sort(([,a], [,b]) => (b as number) - (a as number))
                  .map(([feature, count]) => (
                    <div key={feature} style={{ marginBottom: 8 }}>
                      <Text>{feature.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}: </Text>
                      <Tag color="blue">{count}</Tag>
                    </div>
                  ))}
              </div>
              <Divider />
              <Statistic
                title="Average Explanation Helpfulness"
                value={featureAnalysis.explanationHelpfulness.length > 0 
                  ? (featureAnalysis.explanationHelpfulness.reduce((a, b) => a + b, 0) / featureAnalysis.explanationHelpfulness.length).toFixed(1)
                  : 0}
                suffix="/ 5"
              />
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '5',
      title: 'User Experience',
      icon: <UserOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Confidence Changes">
              <div>
                <Text strong>Pre vs Post Confidence:</Text>
                {userExperienceAnalysis.confidenceChanges.map((change, index) => (
                  <div key={index} style={{ marginTop: 8 }}>
                    <Text>
                      {change.pre} → {change.post} 
                      <Tag color={change.change > 0 ? 'green' : change.change < 0 ? 'red' : 'blue'}>
                        {change.change > 0 ? '+' : ''}{change.change.toFixed(1)}
                      </Tag>
                    </Text>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Performance by Tech Experience">
              <div>
                {Object.entries(userExperienceAnalysis.experienceByTech).map(([tech, data]) => (
                  <div key={tech} style={{ marginBottom: 12 }}>
                    <Text strong>{tech.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</Text>
                    <br />
                    <Text>Avg Clarity: {data.clarity.length > 0 ? (data.clarity.reduce((a, b) => a + b, 0) / data.clarity.length).toFixed(1) : 'N/A'}/5</Text>
                    <br />
                    <Text>Avg Control: {data.control.length > 0 ? (data.control.reduce((a, b) => a + b, 0) / data.control.length).toFixed(1) : 'N/A'}/5</Text>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '6',
      title: 'Content Gaps',
      icon: <BulbOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Missed Facts Analysis">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Average Missed Facts Rating"
                    value={contentGapAnalysis.averageMissedFacts.toFixed(1)}
                    suffix="/ 5"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Issues Reported"
                    value={contentGapAnalysis.issuesReported.length}
                    suffix="participants"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Qualitative Gaps"
                    value={contentGapAnalysis.qualitativeGaps.length}
                    suffix="responses"
                  />
                </Col>
              </Row>
              {contentGapAnalysis.issuesReported.length > 0 && (
                <>
                  <Divider />
                  <div>
                    <Text strong>Common Issues:</Text>
                    {contentGapAnalysis.issuesReported.slice(0, 5).map((issue, index) => (
                      <div key={index} style={{ marginTop: 8, padding: 8, background: '#f5f5f5' }}>
                        <Text>{issue}</Text>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </Card>
          </Col>
        </Row>
      )
    }
  ];

  // Show no data state if no sessions
  if (!loading && sessions.length === 0) {
    return (
      <AppLayout>
        <div style={{ padding: '24px' }}>
          <div style={{ marginBottom: 24 }}>
            <Title level={2}>
              <DashboardOutlined style={{ marginRight: 8, color: '#3498db' }} />
              Research Dashboard
            </Title>
            <Paragraph>
              Comprehensive analysis of questionnaire data for NLP bias detection research.
            </Paragraph>
          </div>

          <Card style={{ textAlign: 'center', padding: '48px 24px' }}>
            <div style={{ marginBottom: 24 }}>
              <UserOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
              <Title level={3} style={{ color: '#8c8c8c' }}>No Data Available</Title>
              <Paragraph style={{ color: '#8c8c8c', fontSize: 16 }}>
                The research dashboard will populate once participants complete questionnaires.
              </Paragraph>
            </div>
            
            <div style={{ marginBottom: 24 }}>
              <Title level={4}>To generate data for analysis:</Title>
              <div style={{ textAlign: 'left', maxWidth: 500, margin: '0 auto' }}>
                <Paragraph>
                  <Text strong>1.</Text> Go to the <Text code>/</Text> route to complete the <Text strong>pre-questionnaire</Text>
                </Paragraph>
                <Paragraph>
                  <Text strong>2.</Text> Navigate to <Text code>/analysis</Text> to use the bias detection tool
                </Paragraph>
                <Paragraph>
                  <Text strong>3.</Text> After 30 seconds of interaction, complete the <Text strong>post-questionnaire</Text>
                </Paragraph>
                <Paragraph>
                  <Text strong>4.</Text> Return here to view comprehensive analytics and insights
                </Paragraph>
              </div>
            </div>

            <Space>
              <Button type="primary" onClick={() => window.location.href = '/'}>
                Start Pre-Questionnaire
              </Button>
              <Button onClick={loadSessionData} loading={loading}>
                Refresh Data
              </Button>
            </Space>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div style={{ padding: '24px' }}>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            <DashboardOutlined style={{ marginRight: 8, color: '#3498db' }} />
            Research Dashboard
          </Title>
          <Paragraph>
            Comprehensive analysis of questionnaire data for NLP bias detection research.
          </Paragraph>
          
          <Space style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              icon={<DownloadOutlined />} 
              onClick={exportData}
              disabled={sessions.length === 0}
            >
              Export Data (CSV)
            </Button>
            <Button onClick={loadSessionData} loading={loading}>
              Refresh Data
            </Button>
            <Select
              value={selectedTimeRange}
              onChange={setSelectedTimeRange}
              style={{ width: 150 }}
            >
              <Option value="all">All Time</Option>
              <Option value="week">Last Week</Option>
              <Option value="month">Last Month</Option>
            </Select>
          </Space>
        </div>

        {/* Overview Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          {overviewCards.map((card, index) => (
            <Col xs={24} sm={12} md={6} key={index}>
              <Card>
                <Statistic
                  title={card.title}
                  value={card.value}
                  prefix={React.cloneElement(card.icon, { style: { color: card.color } })}
                />
              </Card>
            </Col>
          ))}
        </Row>

        {/* Research Questions Analysis */}
        <Card>
          <Tabs 
            defaultActiveKey="1" 
            type="card"
            items={researchQuestionTabs.map(tab => ({
              key: tab.key,
              label: (
                <span>
                  {tab.icon}
                  {tab.title}
                </span>
              ),
              children: tab.content
            }))}
          />
        </Card>

        {/* Session Details Table */}
        <Card title="Session Details" style={{ marginTop: 24 }}>
          <Table
            dataSource={sessions.map((session) => ({
              key: session.sessionId,
              sessionId: session.sessionId,
              preCompleted: !!session.preQuestionnaire,
              postCompleted: !!session.postQuestionnaire,
              preTimestamp: session.preQuestionnaire?.timestamp,
              postTimestamp: session.postQuestionnaire?.timestamp,
              clarity: session.postQuestionnaire?.factOpinionClarity || 'N/A',
              session: session
            }))}
            columns={[
              { 
                title: 'Session ID', 
                dataIndex: 'sessionId', 
                key: 'sessionId',
                render: (text) => <Text code>{text.slice(-8)}</Text>
              },
              { 
                title: 'Pre-Questionnaire', 
                dataIndex: 'preCompleted', 
                key: 'preCompleted',
                render: (completed) => (
                  <Tag color={completed ? 'green' : 'red'}>
                    {completed ? 'Completed' : 'Pending'}
                  </Tag>
                )
              },
              { 
                title: 'Post-Questionnaire', 
                dataIndex: 'postCompleted', 
                key: 'postCompleted',
                render: (completed) => (
                  <Tag color={completed ? 'green' : 'red'}>
                    {completed ? 'Completed' : 'Pending'}
                  </Tag>
                )
              },
              { 
                title: 'Clarity Rating', 
                dataIndex: 'clarity', 
                key: 'clarity',
                render: (score) => score !== 'N/A' ? `${score}/5` : 'N/A'
              }
            ]}
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: '16px 0' }}>
                  <Row gutter={[16, 16]}>
                    {record.session.preQuestionnaire && (
                      <Col span={12}>
                        <Card title="Pre-Questionnaire Responses" size="small">
                          <Descriptions column={1} size="small">
                            {Object.entries(record.session.preQuestionnaire)
                              .filter(([key]) => key !== 'timestamp' && key !== 'type')
                              .map(([key, value]) => (
                                <Descriptions.Item key={key} label={key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}>
                                  {Array.isArray(value) 
                                    ? value.join(', ') 
                                    : typeof value === 'object' 
                                      ? JSON.stringify(value)
                                      : String(value || 'N/A')}
                                </Descriptions.Item>
                              ))}
                          </Descriptions>
                        </Card>
                      </Col>
                    )}
                    {record.session.postQuestionnaire && (
                      <Col span={12}>
                        <Card title="Post-Questionnaire Responses" size="small">
                          <Descriptions column={1} size="small">
                            {Object.entries(record.session.postQuestionnaire)
                              .filter(([key]) => key !== 'timestamp' && key !== 'type')
                              .map(([key, value]) => (
                                <Descriptions.Item key={key} label={key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}>
                                  {Array.isArray(value) 
                                    ? value.join(', ') 
                                    : typeof value === 'object' 
                                      ? JSON.stringify(value)
                                      : String(value || 'N/A')}
                                </Descriptions.Item>
                              ))}
                          </Descriptions>
                        </Card>
                      </Col>
                    )}
                  </Row>
                </div>
              ),
              expandIcon: ({ expanded, onExpand, record }) => (
                <Button 
                  type="text" 
                  icon={<EyeOutlined />} 
                  onClick={e => onExpand(record, e)}
                  size="small"
                >
                  {expanded ? 'Hide' : 'View'} Details
                </Button>
              )
            }}
            pagination={{ pageSize: 10 }}
            loading={loading}
          />
        </Card>
      </div>
    </AppLayout>
  );
};

export default ResearchDashboard;