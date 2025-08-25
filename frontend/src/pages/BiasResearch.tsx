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
  Select,
  Form,
  Steps,
  Radio,
  Checkbox,
  Slider,
  Input,
  Rate,
  Divider
} from 'antd';
import { useNavigate } from 'react-router-dom';
import { 
  ExperimentOutlined, 
  BarChartOutlined, 
  FileTextOutlined,
  LinkOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  RobotOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  TrophyOutlined,
  UserOutlined
} from '@ant-design/icons';
import AppLayout from '../components/AppLayout';
import { apiService } from '../services/api';
import type { SessionInfo, BiasAnalysisSession, IndividualResult } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const BiasResearch: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [selectedSession, setSelectedSession] = useState<BiasAnalysisSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(false);
  
  // Post-questionnaire state
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [questionnaireLoading, setQuestionnaireLoading] = useState(false);

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

  // Post-questionnaire submission handler
  const handleQuestionnaireSubmit = async () => {
    try {
      setQuestionnaireLoading(true);
      
      const allFormFields = form.getFieldsValue(true);
      console.log('Post-questionnaire part 2 data:', allFormFields);
      
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
      }
      
      const values = allFormFields;
      const currentSessionId = selectedSession?.session_id || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const questionnaireKey = `bias_analysis_post_questionnaire2_${currentSessionId}`;
      
      const dataToSave = {
        ...values,
        timestamp: new Date().toISOString(),
        type: 'post_experiment_questionnaire2',
        sessionId: currentSessionId,
        biasSessionData: selectedSession
      };
      
      // Submit to backend using comprehensive data system
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
        // Also save to localStorage as backup
        localStorage.setItem(questionnaireKey, JSON.stringify(dataToSave));
        
        // Log the questionnaire completion interaction
        try {
          await fetch('/api/log_interaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: currentSessionId,
              type: 'questionnaire_completion',
              data: {
                questionnaire_type: 'post_experiment_questionnaire2',
                completion_time: new Date().toISOString(),
                total_questions: Object.keys(dataToSave).length
              }
            })
          });
        } catch (error) {
          console.warn('Failed to log interaction:', error);
        }
        
        message.success('Bias analysis questionnaire completed! Proceeding to post-study questionnaire.');
        
        // Navigate to post questionnaire with session ID and bias research flag
        navigate(`/post-questionnaire?type=post&sessionId=${currentSessionId}&fromBiasResearch=true`);
      } else {
        throw new Error(response.message || 'Failed to save questionnaire data');
      }
      
    } catch (error) {
      console.error('Submission failed:', error);
      message.error('Failed to save questionnaire data. Please try again.');
    } finally {
      setQuestionnaireLoading(false);
    }
  };

  // Questionnaire navigation functions
  const nextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // Complete Post-Experiment Questionnaire steps (from EnhancedQuestionnaires.tsx)
  const postQuestionnaireSteps = [
    {
      title: 'Task Difficulty',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Task Experience (NASA-TLX)</Title>
          
          <Form.Item
            name="mentalDemand"
            label="How mentally demanding was the task?"
            rules={[{ required: true, message: 'Please rate the mental demand' }]}
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Very Low',
                  25: 'Low',
                  50: 'Medium',
                  75: 'High',
                  100: 'Very High'
                }}
                step={1}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>

          <Form.Item
            name="effortRequired"
            label="How much effort did you need to classify statements?"
            rules={[{ required: true, message: 'Please rate the effort required' }]}
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Very Low',
                  25: 'Low',
                  50: 'Medium',
                  75: 'High',
                  100: 'Very High'
                }}
                step={1}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>

          <Form.Item
            name="frustrationLevel"
            label="How frustrated were you while using Truth or Thought?"
            rules={[{ required: true, message: 'Please rate your frustration level' }]}
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Not at all',
                  25: 'Slightly',
                  50: 'Moderately',
                  75: 'Very',
                  100: 'Extremely'
                }}
                step={1}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'System Clarity',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>System Understanding</Title>
          
          <Form.Item
            name="factOpinionClarity"
            label="How clear were fact–opinion distinctions?"
            rules={[{ required: true, message: 'Please rate the clarity' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very unclear',
                  2: 'Unclear',
                  3: 'Neutral',
                  4: 'Clear',
                  5: 'Very clear'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="sourceInfluence"
            label="How much did the source labels (BBC, CNN, Guardian) influence your trust in the system?"
            rules={[{ required: true, message: 'Please rate the influence' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not at all',
                  2: 'Slightly',
                  3: 'Moderately',
                  4: 'Significantly',
                  5: 'Completely'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="explanationHelpfulness"
            label="Did the citations/sources help you understand classifications?"
            rules={[{ required: true, message: 'Please rate the helpfulness' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not helpful',
                  2: 'Slightly helpful',
                  3: 'Moderately helpful',
                  4: 'Very helpful',
                  5: 'Extremely helpful'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Perspective & Understanding',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Truth or Thought Model Impact</Title>
          
          <Form.Item
            name="perspectiveAwareness"
            label="To what extent did Truth or Thought make you aware of different perspectives in the articles?"
            rules={[{ required: true, message: 'Please rate the perspective awareness' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="objectiveSubjectiveClarity"
            label="How easy was it to understand what information was objective versus subjective using Truth or Thought?"
            rules={[{ required: true, message: 'Please rate the clarity' }]}
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Very Difficult',
                  2: 'Difficult',
                  3: 'Somewhat Difficult',
                  4: 'Neutral',
                  5: 'Somewhat Easy',
                  6: 'Easy',
                  7: 'Very Easy'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="biasDetectionImprovement"
            label="Truth or Thought helped me better detect bias in news articles"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Efficiency & Speed',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Truth or Thought Efficiency</Title>
          
          <Form.Item
            name="quickEvaluation"
            label="It was quick to evaluate the article using Truth or Thought"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="lessEffortThanExpected"
            label="The process required less effort than I expected"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="quickJudgment"
            label="I could reach a judgment without spending too much time"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="focusedReading"
            label="I was able to focus on what mattered without unnecessary reading"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Usability Assessment',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Truth or Thought Usability</Title>
          
          <Form.Item
            name="timeConsumingQuick"
            label="Using Truth or Thought was:"
            rules={[{ required: true, message: 'Please rate the time factor' }]}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <Text>Time-consuming</Text>
                <Text>Quick</Text>
              </div>
              <Slider
                min={1}
                max={7}
                marks={{
                  1: '1',
                  2: '2',
                  3: '3',
                  4: '4',
                  5: '5',
                  6: '6',
                  7: '7'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="effortfulEffortless"
            label="Using Truth or Thought was:"
            rules={[{ required: true, message: 'Please rate the effort factor' }]}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <Text>Effortful</Text>
                <Text>Effortless</Text>
              </div>
              <Slider
                min={1}
                max={7}
                marks={{
                  1: '1',
                  2: '2',
                  3: '3',
                  4: '4',
                  5: '5',
                  6: '6',
                  7: '7'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="slowFastJudgment"
            label="Reaching judgment with Truth or Thought was:"
            rules={[{ required: true, message: 'Please rate the judgment speed' }]}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <Text>Slow to reach judgment</Text>
                <Text>Fast to reach judgment</Text>
              </div>
              <Slider
                min={1}
                max={7}
                marks={{
                  1: '1',
                  2: '2',
                  3: '3',
                  4: '4',
                  5: '5',
                  6: '6',
                  7: '7'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="confusingClear"
            label="Truth or Thought was:"
            rules={[{ required: true, message: 'Please rate the clarity' }]}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <Text>Confusing</Text>
                <Text>Clear</Text>
              </div>
              <Slider
                min={1}
                max={7}
                marks={{
                  1: '1',
                  2: '2',
                  3: '3',
                  4: '4',
                  5: '5',
                  6: '6',
                  7: '7'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Future Usage Intent',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Truth or Thought Adoption</Title>
          
          <Form.Item
            name="futureUsage"
            label="I would consider using Truth or Thought in the future"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="likelyToUse"
            label="If Truth or Thought were available, I would likely use it"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="recommendToOthers"
            label="I would recommend Truth or Thought to others who read similar articles"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="comparedToTraditional"
            label="Truth or Thought is more effective than traditional news reading methods"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="trustInAnalysis"
            label="I trust the analysis provided by Truth or Thought"
            rules={[{ required: true, message: 'Please rate your agreement' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly Disagree',
                  2: 'Disagree',
                  3: 'Neutral',
                  4: 'Agree',
                  5: 'Strongly Agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Features & Issues',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>System Features</Title>
          
          <Form.Item
            name="mostHelpfulFeature"
            label="Which feature did you find most helpful?"
            rules={[{ required: true, message: 'Please select at least one feature' }]}
          >
            <Checkbox.Group>
              <Checkbox value="sourceLabel">Source label</Checkbox>
              <Checkbox value="relevantPersonnel">Relevant personnel</Checkbox>
              <Checkbox value="citationsSources">Citations/Sources</Checkbox>
              <Checkbox value="impactfulQuotes">Impactful Quotes</Checkbox>
              <Checkbox value="none">None</Checkbox>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="otherHelpfulFeature"
            label="If other, please specify:"
            dependencies={['mostHelpfulFeature']}
          >
            <Input placeholder="Describe the other helpful feature..." />
          </Form.Item>

          <Form.Item
            name="issuesEncountered"
            label="Were there any issues you encountered?"
            rules={[{ required: true, message: 'Please describe any issues or write "None"' }]}
          >
            <TextArea rows={3} placeholder="Describe any issues you encountered or write 'None'..." />
          </Form.Item>

          <Form.Item
            name="missedFacts"
            label="Did we miss any facts or information in the articles?"
            rules={[{ required: true, message: 'Please rate if facts were missed' }]}
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not at all',
                  2: 'A few',
                  3: 'Some',
                  4: 'Many',
                  5: 'Very many'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="missedFactsSpecify"
            label="If yes, please specify what facts were missed:"
            dependencies={['missedFacts']}
          >
            <TextArea rows={3} placeholder="Describe what facts or information were missed..." />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Article Familiarity',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Prior Knowledge Assessment</Title>
          
          <Form.Item
            name="articleFamiliarity"
            label="Were you familiar with the article content before using Truth or Thought?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="yes">Yes, I was familiar with this article/topic</Radio>
              <Radio value="no">No, this was new content for me</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="familiarityBiasImpact"
            label="If you were familiar with the article, do you think that prior knowledge was a bias factor in analyzing facts and opinions?"
            dependencies={['articleFamiliarity']}
            rules={[
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (getFieldValue('articleFamiliarity') === 'yes' && !value) {
                    return Promise.reject(new Error('Please rate the bias impact'));
                  }
                  return Promise.resolve();
                },
              }),
            ]}
          >
            <Radio.Group>
              <Space direction="vertical">
                <Radio value={1}>1 - Not a bias factor at all</Radio>
                <Radio value={2}>2 - Minimal bias factor</Radio>
                <Radio value={3}>3 - Moderate bias factor</Radio>
                <Radio value={4}>4 - Significant bias factor</Radio>
                <Radio value={5}>5 - Major bias factor</Radio>
              </Space>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="modelEffectivenessNewContent"
            label="If the content was new to you, do you think Truth or Thought did a good job helping you capture the facts and opinions in the article?"
            dependencies={['articleFamiliarity']}
            rules={[
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (getFieldValue('articleFamiliarity') === 'no' && !value) {
                    return Promise.reject(new Error('Please rate the model effectiveness'));
                  }
                  return Promise.resolve();
                },
              }),
            ]}
          >
            <Radio.Group>
              <Space direction="vertical">
                <Radio value={1}>1 - Poor job, didn't help much</Radio>
                <Radio value={2}>2 - Below average, some help</Radio>
                <Radio value={3}>3 - Average, moderately helpful</Radio>
                <Radio value={4}>4 - Good job, quite helpful</Radio>
                <Radio value={5}>5 - Excellent job, very helpful</Radio>
              </Space>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Final Comments',
      icon: <UserOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Additional Feedback</Title>
          
          <Form.Item
            name="additionalComments"
            label="Any additional comments or suggestions?"
            rules={[{ required: true, message: 'Please provide feedback or write "None"' }]}
          >
            <TextArea rows={4} placeholder="Share any additional thoughts, suggestions, or feedback..." />
          </Form.Item>
        </Space>
      ),
    },
  ];

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

                {/* Post-Experiment Questionnaire 2 */}
                {selectedSession && (
                  <Card
                    title={
                      <Space>
                        <ExperimentOutlined style={{ color: '#722ed1' }} />
                        Post-Experiment Questionnaire 2
                      </Space>
                    }
                    style={{ marginTop: 24 }}
                  >
                    <div style={{ marginBottom: 24 }}>
                      <Title level={4} style={{ marginBottom: 8 }}>
                        Post-Experiment Questionnaire 2
                      </Title>
                      <Paragraph style={{ color: '#666' }}>
                        This questionnaire measures the outcomes and changes resulting from your use of the AI bias analysis tool.
                        Your responses help us understand the effectiveness of AI assistance across all our research questions.
                      </Paragraph>
                    </div>
                    
                    <Steps current={currentStep} style={{ marginBottom: 32 }}>
                      {postQuestionnaireSteps.map((step, index) => (
                        <Steps.Step key={index} title={step.title} icon={step.icon} />
                      ))}
                    </Steps>

                    <Form form={form} layout="vertical" style={{ minHeight: '400px' }}>
                      <div>{postQuestionnaireSteps[currentStep].content}</div>
                    </Form>

                    <Divider />

                    <div style={{ marginTop: 32, textAlign: 'center' }}>
                      <Space>
                        {currentStep > 0 && (
                          <Button onClick={prevStep} size="large">
                            Previous
                          </Button>
                        )}
                        {currentStep < postQuestionnaireSteps.length - 1 && (
                          <Button type="primary" onClick={nextStep} size="large">
                            Next
                          </Button>
                        )}
                        {currentStep === postQuestionnaireSteps.length - 1 && (
                          <Button
                            type="primary"
                            onClick={handleQuestionnaireSubmit}
                            loading={questionnaireLoading}
                            size="large"
                          >
                            Complete Post-Experiment Questionnaire 2
                          </Button>
                        )}
                      </Space>
                    </div>

                    <div style={{ marginTop: 24, textAlign: 'center' }}>
                      <Text type="secondary">
                        Step {currentStep + 1} of {postQuestionnaireSteps.length} | Complete Post-Experiment Assessment
                      </Text>
                    </div>
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

export default BiasResearch;
