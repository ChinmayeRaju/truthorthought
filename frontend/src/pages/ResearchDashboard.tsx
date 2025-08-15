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
  DatePicker,
  Descriptions,
  Collapse
} from 'antd';
import {
  DownloadOutlined,
  BarChartOutlined,
  UserOutlined,
  ExperimentOutlined,
  TrophyOutlined,
  TeamOutlined,
  BulbOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { QuestionnaireAnalyzer } from '../utils/questionnaireAnalysis';
import type { SessionData } from '../utils/questionnaireAnalysis';
import AppLayout from '../components/AppLayout';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

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
        if (session.preQuestionnaire) {
          console.log(`Pre-questionnaire ${index}:`, session.preQuestionnaire);
          console.log(`Pre-questionnaire keys:`, Object.keys(session.preQuestionnaire));
        }
        if (session.postQuestionnaire) {
          console.log(`Post-questionnaire ${index}:`, session.postQuestionnaire);
          console.log(`Post-questionnaire keys:`, Object.keys(session.postQuestionnaire));
        }
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

  // Analyze data for each research question
  const nlpAccuracyAnalysis = QuestionnaireAnalyzer.analyzeNLPAccuracy(completedSessions);
  const interfaceAnalysis = QuestionnaireAnalyzer.analyzeInterfaceStrategies(completedSessions);
  const biasDetectionAnalysis = QuestionnaireAnalyzer.analyzeBiasDetectionImprovement(completedSessions);
  const behavioralAnalysis = QuestionnaireAnalyzer.analyzeBehavioralChanges(completedSessions);
  const automationAnalysis = QuestionnaireAnalyzer.analyzeAutomationBalance(completedSessions);
  const individualDifferencesAnalysis = QuestionnaireAnalyzer.analyzeIndividualDifferences(completedSessions);

  // Calculate average satisfaction
  const avgSatisfaction = completedSessions.length > 0
    ? completedSessions.reduce((sum, s) => sum + (s.postQuestionnaire?.overallSatisfaction || 0), 0) / completedSessions.length
    : 0;

  // Calculate skill improvement percentage
  const skillImprovementCount = biasDetectionAnalysis.skillImprovementRatings.filter(
    rating => ['significantly-improved', 'somewhat-improved', 'slightly-improved'].includes(rating)
  ).length;
  const skillImprovementRate = completedSessions.length > 0 
    ? (skillImprovementCount / completedSessions.length) * 100 
    : 0;

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
      title: 'Avg Satisfaction',
      value: `${avgSatisfaction.toFixed(1)}/10`,
      icon: <ExperimentOutlined />,
      color: '#e74c3c'
    }
  ];

  const researchQuestionTabs = [
    {
      key: '1',
      title: 'NLP Accuracy',
      icon: <BarChartOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="NLP Accuracy Perception Analysis">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Average Perceived Accuracy"
                    value={nlpAccuracyAnalysis.perceivedAccuracy.length > 0 
                      ? (nlpAccuracyAnalysis.perceivedAccuracy.reduce((a, b) => a + b, 0) / nlpAccuracyAnalysis.perceivedAccuracy.length).toFixed(1)
                      : 0}
                    suffix="/ 10"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Accuracy Expectations Met"
                    value={nlpAccuracyAnalysis.accuracyGap.filter(gap => gap >= 0).length}
                    suffix={`/ ${nlpAccuracyAnalysis.accuracyGap.length}`}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="High Accuracy Ratings (8+)"
                    value={nlpAccuracyAnalysis.perceivedAccuracy.filter(rating => rating >= 8).length}
                    suffix={`/ ${nlpAccuracyAnalysis.perceivedAccuracy.length}`}
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
      title: 'Interface Strategies',
      icon: <BulbOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="User Agency Ratings">
              <div>
                {Object.entries(
                  interfaceAnalysis.userAgencyRatings.reduce((acc, rating) => {
                    acc[rating] = (acc[rating] || 0) + 1;
                    return acc;
                  }, {} as Record<string, number>)
                ).map(([rating, count]) => (
                  <div key={rating} style={{ marginBottom: 8 }}>
                    <Text>{rating.replace('-', ' ')}: </Text>
                    <Tag color="blue">{count}</Tag>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Most Effective Learning Mechanisms">
              <div>
                {Object.entries(interfaceAnalysis.learningMechanisms)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([mechanism, count]) => (
                    <div key={mechanism} style={{ marginBottom: 8 }}>
                      <Text>{mechanism.replace('-', ' ')}: </Text>
                      <Tag color="green">{count}</Tag>
                    </div>
                  ))}
              </div>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '3',
      title: 'Bias Detection Skills',
      icon: <ExperimentOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Skill Improvement Analysis">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Reported Skill Improvement"
                    value={skillImprovementRate.toFixed(1)}
                    suffix="%"
                  />
                  <Progress percent={skillImprovementRate} strokeColor="#52c41a" />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Increased Confidence"
                    value={biasDetectionAnalysis.confidenceChanges.filter(
                      change => ['much-more-confident', 'more-confident', 'slightly-more-confident'].includes(change)
                    ).length}
                    suffix={`/ ${biasDetectionAnalysis.confidenceChanges.length}`}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Independent Detection Capability"
                    value={biasDetectionAnalysis.independentDetectionChanges.filter(
                      change => ['much-more-capable', 'more-capable', 'slightly-more-capable'].includes(change)
                    ).length}
                    suffix={`/ ${biasDetectionAnalysis.independentDetectionChanges.length}`}
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
      title: 'Behavioral Changes',
      icon: <TeamOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Future Verification Behavior">
              <div>
                {Object.entries(
                  behavioralAnalysis.verificationChanges.reduce((acc, change) => {
                    acc[change] = (acc[change] || 0) + 1;
                    return acc;
                  }, {} as Record<string, number>)
                ).map(([change, count]) => (
                  <div key={change} style={{ marginBottom: 8 }}>
                    <Text>{change.replace('-', ' ')}: </Text>
                    <Tag color="blue">{count}</Tag>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Tool Adoption Intention">
              <div>
                {Object.entries(
                  behavioralAnalysis.toolAdoptionIntention.reduce((acc, intention) => {
                    acc[intention] = (acc[intention] || 0) + 1;
                    return acc;
                  }, {} as Record<string, number>)
                ).map(([intention, count]) => (
                  <div key={intention} style={{ marginBottom: 8 }}>
                    <Text>{intention.replace('-', ' ')}: </Text>
                    <Tag color="green">{count}</Tag>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '5',
      title: 'Automation Balance',
      icon: <BarChartOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Automation Preference vs Experience">
              <Table
                dataSource={Object.entries(automationAnalysis.satisfactionByBalance).map(([balance, scores]) => ({
                  key: balance,
                  balance: balance.replace('-', ' '),
                  count: scores.length,
                  avgSatisfaction: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
                }))}
                columns={[
                  { title: 'Automation Balance', dataIndex: 'balance', key: 'balance' },
                  { title: 'Participants', dataIndex: 'count', key: 'count' },
                  { title: 'Avg Satisfaction', dataIndex: 'avgSatisfaction', key: 'avgSatisfaction' }
                ]}
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: '6',
      title: 'Individual Differences',
      icon: <UserOutlined />,
      content: (
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card title="Satisfaction by Tech Experience">
              <div>
                {Object.entries(individualDifferencesAnalysis.satisfactionByExperience).map(([exp, scores]) => (
                  <div key={exp} style={{ marginBottom: 12 }}>
                    <Text strong>{exp.replace('-', ' ')}</Text>
                    <br />
                    <Text>Avg: {(scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)}/10</Text>
                    <Progress 
                      percent={(scores.reduce((a, b) => a + b, 0) / scores.length) * 10} 
                      size="small"
                      showInfo={false}
                    />
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Adoption by Demographics">
              <div>
                {Object.entries(individualDifferencesAnalysis.adoptionByDemographics)
                  .slice(0, 8)
                  .map(([demo, adoptions]) => {
                    const positiveAdoption = adoptions.filter(a => 
                      ['definitely', 'probably', 'maybe'].includes(a)
                    ).length;
                    const rate = (positiveAdoption / adoptions.length) * 100;
                    
                    return (
                      <div key={demo} style={{ marginBottom: 8 }}>
                        <Text>{demo.replace('-', ' ')}: </Text>
                        <Tag color={rate > 60 ? 'green' : rate > 40 ? 'orange' : 'red'}>
                          {rate.toFixed(0)}%
                        </Tag>
                      </div>
                    );
                  })}
              </div>
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
              <BarChartOutlined style={{ marginRight: 8, color: '#3498db' }} />
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
            <BarChartOutlined style={{ marginRight: 8, color: '#3498db' }} />
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
            dataSource={sessions.map((session, index) => ({
              key: session.sessionId,
              sessionId: session.sessionId,
              preCompleted: !!session.preQuestionnaire,
              postCompleted: !!session.postQuestionnaire,
              preTimestamp: session.preQuestionnaire?.timestamp,
              postTimestamp: session.postQuestionnaire?.timestamp,
              satisfaction: session.postQuestionnaire?.overallSatisfaction || 'N/A',
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
                title: 'Satisfaction',
                dataIndex: 'satisfaction',
                key: 'satisfaction',
                render: (score) => score !== 'N/A' ? `${score}/10` : 'N/A'
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
                            {record.session.preQuestionnaire && Object.entries(record.session.preQuestionnaire)
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
                            {record.session.postQuestionnaire && Object.entries(record.session.postQuestionnaire)
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