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
  const [studyData, setStudyData] = useState<any>({ participants: [], statistics: {} });
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('all');
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      // Load both legacy localStorage data and new comprehensive study data
      const legacyData = QuestionnaireAnalyzer.getAllSessionData();
      console.log('Loaded legacy session data:', legacyData);
      
      console.log('Attempting to fetch comprehensive study data from API...');
      const comprehensiveData = await QuestionnaireAnalyzer.getAllStudyData();
      console.log('API Response:', comprehensiveData);
      
      setSessions(legacyData);
      if (comprehensiveData && comprehensiveData.success) {
        console.log('Setting study data:', comprehensiveData);
        setStudyData(comprehensiveData);
      } else {
        console.warn('API call failed or returned no data:', comprehensiveData);
        message.warning('Could not load comprehensive study data from server. Showing legacy data only.');
      }
    } catch (error) {
      message.error('Failed to load study data');
      console.error('Error loading study data:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async () => {
    setExportLoading(true);
    try {
      // Export comprehensive study data
      const result = await QuestionnaireAnalyzer.exportStudyData('all');
      
      if (result.success) {
        message.success(`Study data exported successfully! Files: ${Object.keys(result.files).join(', ')}`);
        
        // Also export legacy data as backup
        const csv = QuestionnaireAnalyzer.exportToCSV(sessions);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `legacy_questionnaire_data_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        throw new Error(result.message || 'Export failed');
      }
    } catch (error) {
      message.error('Failed to export data');
      console.error('Export error:', error);
    } finally {
      setExportLoading(false);
    }
  };

  const exportSpecificData = async (exportType: string) => {
    setExportLoading(true);
    try {
      const result = await QuestionnaireAnalyzer.exportStudyData(exportType);
      
      if (result.success && result.files) {
        // Download each exported file
        const fileNames = Object.keys(result.files);
        let downloadCount = 0;
        
        for (const fileName of fileNames) {
          const filePath = result.files[fileName];
          // Extract just the filename from the full path
          const actualFileName = filePath.split('\\').pop() || filePath.split('/').pop() || fileName;
          
          try {
            // Create download link for each file
            const downloadUrl = `/api/download_export/${actualFileName}`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = actualFileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            downloadCount++;
            
            // Small delay between downloads to avoid browser blocking
            if (fileNames.length > 1) {
              await new Promise(resolve => setTimeout(resolve, 500));
            }
          } catch (downloadError) {
            console.error(`Failed to download ${actualFileName}:`, downloadError);
          }
        }
        
        if (downloadCount > 0) {
          message.success(`${exportType.replace('_', ' ')} data exported successfully! ${downloadCount} file(s) downloaded.`);
        } else {
          message.warning(`Export completed but no files were downloaded. Files are available on the server.`);
        }
      } else {
        throw new Error(result.message || 'Export failed');
      }
    } catch (error) {
      message.error(`Failed to export ${exportType.replace('_', ' ')} data`);
      console.error('Export error:', error);
    } finally {
      setExportLoading(false);
    }
  };

  const exportExitData = () => {
    try {
      const exitData = QuestionnaireAnalyzer.getAllExitQuestionnaireData();
      const csv = QuestionnaireAnalyzer.exportExitQuestionnaireToCSV(exitData);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `exit_questionnaire_data_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      message.success('Exit questionnaire data exported successfully');
    } catch (error) {
      message.error('Failed to export exit questionnaire data');
      console.error('Export error:', error);
    }
  };

  const viewParticipantDetails = (participant: any) => {
    console.log('Viewing participant details:', participant);
    message.info(`Viewing details for participant ${participant.session_id}`);
  };

  // Calculate summary statistics from both legacy and comprehensive data
  const completedSessions = sessions.filter(s => s.preQuestionnaire && s.postQuestionnaire);
  const preOnlySessions = sessions.filter(s => s.preQuestionnaire && !s.postQuestionnaire);
  const completionRate = sessions.length > 0 ? (completedSessions.length / sessions.length) * 100 : 0;
  
  // Use comprehensive statistics if available
  const stats = studyData.statistics || {};
  const participants = studyData.participants || [];

  // Analyze data using analysis functions
  const taskLoadAnalysis = QuestionnaireAnalyzer.analyzeTaskLoad(completedSessions);
  const clarityAnalysis = QuestionnaireAnalyzer.analyzeSystemClarity(completedSessions);
  const trustAnalysis = QuestionnaireAnalyzer.analyzeTrustFactors(completedSessions);
  const featureAnalysis = QuestionnaireAnalyzer.analyzeFeatureEffectiveness(completedSessions);
  const userExperienceAnalysis = QuestionnaireAnalyzer.analyzeUserExperience(completedSessions);
  const contentGapAnalysis = QuestionnaireAnalyzer.analyzeContentGaps(completedSessions);
  const demographicsAnalysis = QuestionnaireAnalyzer.analyzeDemographics(completedSessions);
  
  // Exit questionnaire analysis
  const exitQuestionnaireData = QuestionnaireAnalyzer.getAllExitQuestionnaireData();
  const exitAnalysis = QuestionnaireAnalyzer.analyzeExitQuestionnaire(exitQuestionnaireData);

  // Calculate average satisfaction (using a relevant metric from new questionnaire)
  const avgClarity = clarityAnalysis.averageClarity;

  const overviewCards = [
    {
      title: 'Total Participants',
      value: stats.total_participants || sessions.length,
      icon: <UserOutlined />,
      color: '#3498db'
    },
    {
      title: 'Completed Studies',
      value: stats.completed_full_study || completedSessions.length,
      icon: <TrophyOutlined />,
      color: '#27ae60'
    },
    {
      title: 'Completion Rate',
      value: stats.total_participants > 0 ? 
        `${((stats.completed_full_study || 0) / stats.total_participants * 100).toFixed(1)}%` :
        `${completionRate.toFixed(1)}%`,
      icon: <BarChartOutlined />,
      color: '#f39c12'
    },
    {
      title: 'Analysis Sessions',
      value: stats.total_analysis_sessions || 0,
      icon: <ExperimentOutlined />,
      color: '#e74c3c'
    }
  ];

  if (loading) {
    return (
      <AppLayout>
        <div style={{ padding: '24px' }}>
          <div style={{ marginBottom: 24 }}>
            <Title level={2}>
              <DashboardOutlined /> Research Dashboard
            </Title>
            <Paragraph>Loading study data...</Paragraph>
          </div>
          <Card style={{ textAlign: 'center', padding: '48px 24px' }}>
            <Text>Loading comprehensive study data...</Text>
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
            <DashboardOutlined /> Research Dashboard
          </Title>
          <Paragraph>Comprehensive analysis of study data and participant responses</Paragraph>
          
          <Space style={{ marginBottom: 16 }} wrap>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => exportSpecificData('pre_questionnaires')}
              loading={exportLoading}
              disabled={participants.length === 0}
            >
              Export Pre-Questionnaires
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => exportSpecificData('post_questionnaires')}
              loading={exportLoading}
              disabled={participants.length === 0}
            >
              Export Post Questionnaires
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => exportSpecificData('bias_analysis_questionnaires')}
              loading={exportLoading}
              disabled={participants.length === 0}
            >
              Export Bias Analysis Questionnaires
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => exportSpecificData('exit_questionnaires')}
              loading={exportLoading}
              disabled={participants.length === 0}
            >
              Export Exit Questionnaires
            </Button>
            <Button onClick={loadAllData} loading={loading}>
              Refresh Data
            </Button>
            <Select
              value={selectedTimeRange}
              onChange={setSelectedTimeRange}
              style={{ width: 200 }}
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


        {/* Study Statistics Summary */}
        {Object.keys(stats).length > 0 && (
          <Card title="Study Statistics Summary" style={{ marginBottom: 24 }}>
            <Row gutter={[16, 16]}>
              <Col span={6}>
                <Statistic
                  title="Total Participants"
                  value={stats.total_participants}
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Completed Comprehensive Pre"
                  value={stats.completed_comprehensive_pre}
                  suffix={`/ ${stats.total_participants}`}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Completed Research Pre"
                  value={stats.completed_research_pre}
                  suffix={`/ ${stats.total_participants}`}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Completed Research Post"
                  value={stats.completed_research_post}
                  suffix={`/ ${stats.total_participants}`}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Completed Exit"
                  value={stats.completed_exit}
                  suffix={`/ ${stats.total_participants}`}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Full Study Completion"
                  value={stats.completed_full_study}
                  suffix={`/ ${stats.total_participants}`}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Avg Analysis Sessions"
                  value={stats.avg_analysis_sessions_per_participant?.toFixed(1) || '0.0'}
                  suffix="per participant"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="Avg Interactions"
                  value={stats.avg_interactions_per_participant?.toFixed(1) || '0.0'}
                  suffix="per participant"
                />
              </Col>
            </Row>
          </Card>
        )}

      </div>
    </AppLayout>
  );
};

export default ResearchDashboard;