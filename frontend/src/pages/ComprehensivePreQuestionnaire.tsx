import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Button,
  Steps,
  Typography,
  Space,
  Radio,
  Checkbox,
  Slider,
  Input,
  message,
  Row,
  Col,
  Select,
  Rate,
  Divider
} from 'antd';
import {
  UserOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  BulbOutlined,
  HeartOutlined,
  SafetyOutlined,
  EyeOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiService from '../services/api';
import AppLayout from '../components/AppLayout';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ComprehensivePreQuestionnaire: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showOutletRanking, setShowOutletRanking] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const sessionId = searchParams.get('sessionId');

  // Watch for changes in media trust to show/hide outlet ranking
  const watchMediaTrust = Form.useWatch('mediaTrustGeneral', form);
  
  useEffect(() => {
    // Show outlet ranking if user indicates some level of trust (3 or higher on 5-point scale)
    setShowOutletRanking(watchMediaTrust >= 3);
  }, [watchMediaTrust]);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const allFormFields = form.getFieldsValue(true);
      console.log('Comprehensive pre-questionnaire data:', allFormFields);
      
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
      }
      
      const values = allFormFields;
      const currentSessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const dataToSave = {
        ...values,
        timestamp: new Date().toISOString(),
        type: 'comprehensive_pre',
        sessionId: currentSessionId
      };
      
      // Submit to backend using new comprehensive data system
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
        // Also save to localStorage as backup
        const questionnaireKey = `comprehensive_pre_questionnaire_${currentSessionId}`;
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
                questionnaire_type: 'comprehensive_pre',
                completion_time: new Date().toISOString(),
                total_questions: Object.keys(dataToSave).length
              }
            })
          });
        } catch (error) {
          console.warn('Failed to log interaction:', error);
        }
        
        message.success('Comprehensive pre-study questionnaire completed and saved! Redirecting to the analysis tool...');
        setTimeout(() => {
          navigate(`/analysis?sessionId=${currentSessionId}&fromQuestionnaire=true`);
        }, 1500);
      } else {
        throw new Error(response.message || 'Failed to save questionnaire data');
      }
      
    } catch (error) {
      console.error('Submission failed:', error);
      message.error('Failed to save questionnaire data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const comprehensivePreQuestionnaireSteps = [
    {
      title: 'Media Trust Foundation',
      icon: <SafetyOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>General Media Trust Assessment</Title>
          <Paragraph>
            We begin by understanding your overall relationship with news media and information sources.
          </Paragraph>
          
          <Form.Item
            name="mediaTrustGeneral"
            label="Regarding politics and war coverage, do you trust news media in general?"
            rules={[{ required: true, message: 'Please indicate your level of trust' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly distrust',
                  2: 'Somewhat distrust',
                  3: 'Neutral',
                  4: 'Somewhat trust',
                  5: 'Strongly trust'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="mediaCredibilityFactors"
            label="What factors most influence your trust in a news source? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one factor' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="reputation">Established reputation</Checkbox></Col>
                <Col span={12}><Checkbox value="transparency">Transparency in reporting</Checkbox></Col>
                <Col span={12}><Checkbox value="factChecking">Fact-checking practices</Checkbox></Col>
                <Col span={12}><Checkbox value="sourceAttribution">Clear source attribution</Checkbox></Col>
                <Col span={12}><Checkbox value="editorialStandards">Editorial standards</Checkbox></Col>
                <Col span={12}><Checkbox value="corrections">Willingness to issue corrections</Checkbox></Col>
                <Col span={12}><Checkbox value="independence">Editorial independence</Checkbox></Col>
                <Col span={12}><Checkbox value="expertise">Journalist expertise</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="informationVerificationHabits"
            label="How do you typically verify important news information?"
            rules={[{ required: true, message: 'Please describe your verification habits' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="Describe how you check if news information is accurate (e.g., cross-reference sources, check official statements, consult fact-checkers, etc.)"
            />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Outlet Assessment',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>News Outlet Evaluation</Title>
          
          {showOutletRanking && (
            <>
              <Paragraph>
                Since you indicated some level of trust in news media, please rank these outlets based on your trust level for political and war coverage.
              </Paragraph>
              
              <Row gutter={[16, 16]}>
                <Col span={24}>
                  <Form.Item
                    name="outletTrustRankingBBC"
                    label="BBC:"
                    rules={[{ required: showOutletRanking, message: 'Please rank BBC' }]}
                  >
                    <Select placeholder="Select ranking" style={{ width: '100%' }}>
                      <Option value={1}>1 (Most trusted)</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={4}>4</Option>
                      <Option value={5}>5 (Least trusted)</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={24}>
                  <Form.Item
                    name="outletTrustRankingCNN"
                    label="CNN:"
                    rules={[{ required: showOutletRanking, message: 'Please rank CNN' }]}
                  >
                    <Select placeholder="Select ranking" style={{ width: '100%' }}>
                      <Option value={1}>1 (Most trusted)</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={4}>4</Option>
                      <Option value={5}>5 (Least trusted)</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={24}>
                  <Form.Item
                    name="outletTrustRankingGuardian"
                    label="The Guardian:"
                    rules={[{ required: showOutletRanking, message: 'Please rank The Guardian' }]}
                  >
                    <Select placeholder="Select ranking" style={{ width: '100%' }}>
                      <Option value={1}>1 (Most trusted)</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={4}>4</Option>
                      <Option value={5}>5 (Least trusted)</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={24}>
                  <Form.Item
                    name="outletTrustRankingReuters"
                    label="Reuters:"
                    rules={[{ required: showOutletRanking, message: 'Please rank Reuters' }]}
                  >
                    <Select placeholder="Select ranking" style={{ width: '100%' }}>
                      <Option value={1}>1 (Most trusted)</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={4}>4</Option>
                      <Option value={5}>5 (Least trusted)</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={24}>
                  <Form.Item
                    name="outletTrustRankingAP"
                    label="Associated Press (AP):"
                    rules={[{ required: showOutletRanking, message: 'Please rank Associated Press' }]}
                  >
                    <Select placeholder="Select ranking" style={{ width: '100%' }}>
                      <Option value={1}>1 (Most trusted)</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={4}>4</Option>
                      <Option value={5}>5 (Least trusted)</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}

          <Form.Item
            name="perceivedBiasTopics"
            label="In which topics do you perceive the most media bias? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one topic area' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="politics">Politics</Checkbox></Col>
                <Col span={12}><Checkbox value="war">War and conflict</Checkbox></Col>
                <Col span={12}><Checkbox value="economics">Economics</Checkbox></Col>
                <Col span={12}><Checkbox value="climate">Climate change</Checkbox></Col>
                <Col span={12}><Checkbox value="healthcare">Healthcare</Checkbox></Col>
                <Col span={12}><Checkbox value="technology">Technology</Checkbox></Col>
                <Col span={12}><Checkbox value="social">Social issues</Checkbox></Col>
                <Col span={12}><Checkbox value="international">International relations</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="biasDetectionConfidence"
            label="How confident are you in your ability to detect bias in news reporting?"
            rules={[{ required: true, message: 'Please rate your confidence' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not confident',
                  2: 'Slightly confident',
                  3: 'Moderately confident',
                  4: 'Very confident',
                  5: 'Extremely confident'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Psychological Impact',
      icon: <HeartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Emotional and Psychological Effects</Title>
          <Paragraph>
            Understanding how news consumption affects your mental well-being and emotional state.
          </Paragraph>
          
          <Form.Item
            name="newsEmotionalDraining"
            label="Do you find news consumption emotionally draining or depressing?"
            rules={[{ required: true, message: 'Please indicate how news affects you emotionally' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Never',
                  2: 'Rarely',
                  3: 'Sometimes',
                  4: 'Often',
                  5: 'Always'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="newsMoodImpact"
            label="How does regular news exposure affect your daily mood and outlook?"
            rules={[{ required: true, message: 'Please describe the impact on your mood' }]}
          >
            <Radio.Group>
              <Radio value="veryPositive">Very positive impact</Radio>
              <Radio value="positive">Somewhat positive impact</Radio>
              <Radio value="neutral">No significant impact</Radio>
              <Radio value="negative">Somewhat negative impact</Radio>
              <Radio value="veryNegative">Very negative impact</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newsAnxietyRelationship"
            label="What is the relationship between your news consumption and personal anxiety levels?"
            rules={[{ required: true, message: 'Please describe this relationship' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="Describe how news consumption affects your anxiety levels (e.g., increases anxiety about world events, helps you feel informed and less anxious, no relationship, etc.)"
            />
          </Form.Item>

          <Form.Item
            name="stressfulNewsTopics"
            label="Which news topics cause you the most stress or anxiety? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one topic' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="war">War and conflict</Checkbox></Col>
                <Col span={12}><Checkbox value="politics">Political developments</Checkbox></Col>
                <Col span={12}><Checkbox value="economy">Economic news</Checkbox></Col>
                <Col span={12}><Checkbox value="health">Health crises</Checkbox></Col>
                <Col span={12}><Checkbox value="climate">Climate change</Checkbox></Col>
                <Col span={12}><Checkbox value="crime">Crime and violence</Checkbox></Col>
                <Col span={12}><Checkbox value="disasters">Natural disasters</Checkbox></Col>
                <Col span={12}><Checkbox value="social">Social unrest</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'News Behaviors',
      icon: <EyeOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>News Consumption and Avoidance Behaviors</Title>
          
          <Form.Item
            name="newsAvoidanceBehaviors"
            label="Do you ever intentionally avoid news? If so, when and why?"
            rules={[{ required: true, message: 'Please describe your news avoidance behaviors' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Describe situations where you avoid news (e.g., during stressful periods, before bed, on weekends, when feeling overwhelmed, etc.) and your reasons"
            />
          </Form.Item>

          <Form.Item
            name="newsCheckingFrequency"
            label="How frequently do you check news throughout a typical day?"
            rules={[{ required: true, message: 'Please select your checking frequency' }]}
          >
            <Radio.Group>
              <Radio value="constantly">Constantly throughout the day</Radio>
              <Radio value="hourly">Every few hours</Radio>
              <Radio value="twiceDaily">Twice daily (morning and evening)</Radio>
              <Radio value="daily">Once daily</Radio>
              <Radio value="fewTimesWeek">A few times per week</Radio>
              <Radio value="weekly">Weekly</Radio>
              <Radio value="rarely">Rarely</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newsCheckingTriggers"
            label="What typically triggers you to check the news? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one trigger' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="routine">Daily routine</Checkbox></Col>
                <Col span={12}><Checkbox value="breaking">Breaking news alerts</Checkbox></Col>
                <Col span={12}><Checkbox value="social">Social media mentions</Checkbox></Col>
                <Col span={12}><Checkbox value="conversations">Conversations with others</Checkbox></Col>
                <Col span={12}><Checkbox value="boredom">Boredom or free time</Checkbox></Col>
                <Col span={12}><Checkbox value="anxiety">Anxiety about current events</Checkbox></Col>
                <Col span={12}><Checkbox value="work">Work-related needs</Checkbox></Col>
                <Col span={12}><Checkbox value="curiosity">General curiosity</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="preferredNewsFormat"
            label="What format do you prefer for consuming news?"
            rules={[{ required: true, message: 'Please select your preferred format' }]}
          >
            <Radio.Group>
              <Radio value="articles">Full articles</Radio>
              <Radio value="headlines">Headlines and summaries</Radio>
              <Radio value="video">Video reports</Radio>
              <Radio value="audio">Audio/podcasts</Radio>
              <Radio value="social">Social media posts</Radio>
              <Radio value="mixed">Mixed formats</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Crisis Information',
      icon: <ClockCircleOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Information Sources During Crises</Title>
          <Paragraph>
            Understanding where you turn for information during important or crisis situations.
          </Paragraph>
          
          <Form.Item
            name="crisisInformationSources"
            label="During major crises or breaking news events, what are your preferred information sources? (Rank top 3)"
            rules={[{ required: true, message: 'Please select and rank your top 3 sources' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="traditionalNews">Traditional news websites</Checkbox></Col>
                <Col span={12}><Checkbox value="socialMedia">Social media platforms</Checkbox></Col>
                <Col span={12}><Checkbox value="government">Government official sources</Checkbox></Col>
                <Col span={12}><Checkbox value="liveTV">Live television news</Checkbox></Col>
                <Col span={12}><Checkbox value="radio">Radio news</Checkbox></Col>
                <Col span={12}><Checkbox value="newsApps">News mobile apps</Checkbox></Col>
                <Col span={12}><Checkbox value="friends">Friends and family</Checkbox></Col>
                <Col span={12}><Checkbox value="experts">Expert/specialist sources</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="crisisInformationSpeed"
            label="During a crisis, how important is the speed of information versus accuracy?"
            rules={[{ required: true, message: 'Please indicate your preference' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Speed most important',
                  2: 'Speed somewhat important',
                  3: 'Equally important',
                  4: 'Accuracy somewhat important',
                  5: 'Accuracy most important'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="informationOverloadCoping"
            label="How do you cope with information overload during major news events?"
            rules={[{ required: true, message: 'Please describe your coping strategies' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="Describe strategies you use when there's too much information (e.g., limit sources, take breaks, focus on official sources, discuss with others, etc.)"
            />
          </Form.Item>

          <Form.Item
            name="misinformationConcern"
            label="How concerned are you about misinformation during crisis situations?"
            rules={[{ required: true, message: 'Please rate your concern level' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not concerned',
                  2: 'Slightly concerned',
                  3: 'Moderately concerned',
                  4: 'Very concerned',
                  5: 'Extremely concerned'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Demographics & Background',
      icon: <UserOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Background Information</Title>
          
          <Form.Item
            name="age"
            label="Age"
            rules={[{ required: true, message: 'Please enter your age' }]}
          >
            <Input placeholder="Enter your age" type="number" min={18} max={100} />
          </Form.Item>

          <Form.Item
            name="education"
            label="Highest level of education completed"
            rules={[{ required: true, message: 'Please select your education level' }]}
          >
            <Select placeholder="Select education level">
              <Option value="highSchool">High school or equivalent</Option>
              <Option value="someCollege">Some college</Option>
              <Option value="bachelors">Bachelor's degree</Option>
              <Option value="masters">Master's degree</Option>
              <Option value="doctorate">Doctorate degree</Option>
              <Option value="other">Other</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="profession"
            label="Profession/Field of work"
            rules={[{ required: true, message: 'Please enter your profession' }]}
          >
            <Input placeholder="Enter your profession or field of work" />
          </Form.Item>

          <Form.Item
            name="politicalInterest"
            label="How interested are you in politics and current affairs?"
            rules={[{ required: true, message: 'Please rate your interest level' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not interested',
                  2: 'Slightly interested',
                  3: 'Moderately interested',
                  4: 'Very interested',
                  5: 'Extremely interested'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="techComfort"
            label="How comfortable are you with using digital technology and online tools?"
            rules={[{ required: true, message: 'Please rate your comfort level' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not comfortable',
                  2: 'Slightly comfortable',
                  3: 'Moderately comfortable',
                  4: 'Very comfortable',
                  5: 'Extremely comfortable'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="additionalComments"
            label="Any additional comments about your news consumption habits or media trust?"
          >
            <TextArea 
              rows={3} 
              placeholder="Optional: Share any additional thoughts about your relationship with news media..."
            />
          </Form.Item>
        </Space>
      ),
    },
  ];

  const next = () => {
    setCurrentStep(currentStep + 1);
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <AppLayout>
      <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
        <Card>
          <Title level={2} style={{ textAlign: 'center', marginBottom: '16px' }}>
            Comprehensive Media Consumption Assessment
          </Title>
          <Paragraph style={{ textAlign: 'center', marginBottom: '32px', color: '#666' }}>
            This questionnaire helps us understand your relationship with news media, information sources, 
            and how news consumption affects your well-being. Your responses will help us better understand 
            media consumption patterns and their psychological impacts.
          </Paragraph>
          
          <Steps current={currentStep} style={{ marginBottom: '32px' }}>
            {comprehensivePreQuestionnaireSteps.map((step, index) => (
              <Steps.Step key={index} title={step.title} icon={step.icon} />
            ))}
          </Steps>

          <Form form={form} layout="vertical" style={{ minHeight: '500px' }}>
            <div>{comprehensivePreQuestionnaireSteps[currentStep].content}</div>
          </Form>

          <Divider />

          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <Space>
              {currentStep > 0 && (
                <Button onClick={prev} size="large">
                  Previous
                </Button>
              )}
              {currentStep < comprehensivePreQuestionnaireSteps.length - 1 && (
                <Button type="primary" onClick={next} size="large">
                  Next
                </Button>
              )}
              {currentStep === comprehensivePreQuestionnaireSteps.length - 1 && (
                <Button type="primary" onClick={handleSubmit} loading={loading} size="large">
                  Complete Assessment
                </Button>
              )}
            </Space>
          </div>

          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Text type="secondary">
              Step {currentStep + 1} of {comprehensivePreQuestionnaireSteps.length}
            </Text>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
};

export default ComprehensivePreQuestionnaire;