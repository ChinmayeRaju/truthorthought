import React, { useState } from 'react';
import {
  Card,
  Form,
  Button,
  Row,
  Col,
  Typography,
  Radio,
  Checkbox,
  message,
  Steps,
  Space,
  Divider,
  Slider,
  Input
} from 'antd';
import { 
  ExperimentOutlined, 
  UserOutlined, 
  QuestionCircleOutlined,
  RocketOutlined,
  BulbOutlined,
  CheckCircleOutlined,
  BarChartOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;
const { TextArea } = Input;

interface EnhancedQuestionnairesProps {
  questionnaireType?: 'pre' | 'post';
}

const EnhancedQuestionnaires: React.FC<EnhancedQuestionnairesProps> = ({ questionnaireType = 'pre' }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const isPostQuestionnaire = questionnaireType === 'post' || searchParams.get('type') === 'post';
  const sessionId = searchParams.get('sessionId');

  const handleNext = async () => {
    try {
      await form.validateFields();
      setCurrentStep(currentStep + 1);
    } catch (error) {
      console.log('Validation failed:', error);
    }
  };

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      // Get ALL form fields regardless of current step
      const allFormFields = form.getFieldsValue(true);
      console.log('All form fields (all steps):', allFormFields);
      console.log('All form field names:', Object.keys(allFormFields));
      console.log('Total field count:', Object.keys(allFormFields).length);
      
      // Validate all fields across all steps
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
        // Continue with submission using all available data
      }
      
      // Use all form data, not just validated fields
      const values = allFormFields;
      
      // Debug: Log what data is being collected
      console.log('Final form data to save:', values);
      console.log('Final field count:', Object.keys(values).length);
      
      const currentSessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const questionnaireKey = isPostQuestionnaire ? `post_questionnaire_${currentSessionId}` : `pre_questionnaire_${currentSessionId}`;
      
      const dataToSave = {
        ...values,
        timestamp: new Date().toISOString(),
        type: isPostQuestionnaire ? 'post' : 'pre'
      };
      
      // Debug: Log what's being saved
      console.log('Data being saved to localStorage:', dataToSave);
      console.log('localStorage key:', questionnaireKey);
      
      // Store questionnaire data
      localStorage.setItem(questionnaireKey, JSON.stringify(dataToSave));
      
      if (isPostQuestionnaire) {
        message.success('Post-study questionnaire completed! Thank you for your participation.');
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        message.success('Pre-study questionnaire completed! Redirecting to analysis...');
        setTimeout(() => {
          navigate(`/analysis?sessionId=${currentSessionId}&fromQuestionnaire=true`);
        }, 1500);
      }
      
    } catch (error) {
      console.log('Submission failed:', error);
      message.error('Please complete all required fields');
    } finally {
      setLoading(false);
    }
  };

  // Pre-questionnaire steps
  const preQuestionnaireSteps = [
    {
      title: 'Demographics',
      icon: <UserOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Tell us about yourself</Title>
          
          <Form.Item
            name="age"
            label="Age Group"
            rules={[{ required: true, message: 'Please select your age group' }]}
          >
            <Radio.Group>
              <Radio value="18-24">18-24</Radio>
              <Radio value="25-34">25-34</Radio>
              <Radio value="35-44">35-44</Radio>
              <Radio value="45-54">45-54</Radio>
              <Radio value="55-64">55-64</Radio>
              <Radio value="65+">65+</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="education"
            label="Highest Education Level"
            rules={[{ required: true, message: 'Please select your education level' }]}
          >
            <Radio.Group>
              <Radio value="high-school">High School</Radio>
              <Radio value="some-college">Some College</Radio>
              <Radio value="bachelors">Bachelor's Degree</Radio>
              <Radio value="masters">Master's Degree</Radio>
              <Radio value="doctorate">Doctorate</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="techExperience"
            label="How would you rate your experience with technology?"
            rules={[{ required: true, message: 'Please rate your tech experience' }]}
          >
            <Radio.Group>
              <Radio value="beginner">Beginner</Radio>
              <Radio value="intermediate">Intermediate</Radio>
              <Radio value="advanced">Advanced</Radio>
              <Radio value="expert">Expert</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="aiExperience"
            label="How familiar are you with AI/machine learning tools?"
            rules={[{ required: true, message: 'Please select your AI experience level' }]}
          >
            <Radio.Group>
              <Radio value="never-used">Never used</Radio>
              <Radio value="basic-awareness">Basic awareness</Radio>
              <Radio value="occasional-use">Occasional use</Radio>
              <Radio value="regular-use">Regular use</Radio>
              <Radio value="professional-use">Professional use</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Media Habits',
      icon: <QuestionCircleOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your media consumption habits</Title>
          
          <Form.Item
            name="mediaConsumption"
            label="Primary News Sources (select all that apply)"
            rules={[{ required: true, message: 'Please select at least one news source' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={8}><Checkbox value="tv">Television</Checkbox></Col>
                <Col span={8}><Checkbox value="online">Online News Sites</Checkbox></Col>
                <Col span={8}><Checkbox value="social">Social Media</Checkbox></Col>
                <Col span={8}><Checkbox value="newspapers">Newspapers</Checkbox></Col>
                <Col span={8}><Checkbox value="radio">Radio</Checkbox></Col>
                <Col span={8}><Checkbox value="podcasts">Podcasts</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="newsFrequency"
            label="How often do you consume news?"
            rules={[{ required: true, message: 'Please select news consumption frequency' }]}
          >
            <Radio.Group>
              <Radio value="multiple-daily">Multiple times daily</Radio>
              <Radio value="daily">Once daily</Radio>
              <Radio value="few-weekly">Few times a week</Radio>
              <Radio value="weekly">Weekly</Radio>
              <Radio value="rarely">Rarely</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="sourceVerification"
            label="How often do you verify information from multiple sources?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="always">Always</Radio>
              <Radio value="often">Often</Radio>
              <Radio value="sometimes">Sometimes</Radio>
              <Radio value="rarely">Rarely</Radio>
              <Radio value="never">Never</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="factChecking"
            label="Do you use fact-checking websites?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="regularly">Regularly</Radio>
              <Radio value="occasionally">Occasionally</Radio>
              <Radio value="rarely">Rarely</Radio>
              <Radio value="never">Never</Radio>
              <Radio value="unaware">Unaware of them</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Bias Detection Skills',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your current bias detection abilities</Title>
          
          <Form.Item
            name="factOpinionConfidence"
            label="How confident are you in distinguishing facts from opinions in news?"
            rules={[{ required: true, message: 'Please rate your confidence' }]}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: 'Not confident at all',
                  5: 'Moderately confident',
                  10: 'Extremely confident'
                }}
                style={{ marginBottom: 20 }}
              />
              <Radio.Group>
                <Radio value="1">1</Radio>
                <Radio value="2">2</Radio>
                <Radio value="3">3</Radio>
                <Radio value="4">4</Radio>
                <Radio value="5">5</Radio>
                <Radio value="6">6</Radio>
                <Radio value="7">7</Radio>
                <Radio value="8">8</Radio>
                <Radio value="9">9</Radio>
                <Radio value="10">10</Radio>
              </Radio.Group>
            </div>
          </Form.Item>

          <Form.Item
            name="biasAwareness"
            label="How confident are you in identifying media bias?"
            rules={[{ required: true, message: 'Please rate your confidence' }]}
          >
            <Radio.Group>
              <Radio value="very-confident">Very confident</Radio>
              <Radio value="confident">Confident</Radio>
              <Radio value="somewhat-confident">Somewhat confident</Radio>
              <Radio value="not-confident">Not confident</Radio>
              <Radio value="no-idea">No idea</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="biasTypes"
            label="Which types of bias can you identify? (select all that apply)"
            rules={[{ required: true, message: 'Please select at least one' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="confirmation">Confirmation bias</Checkbox></Col>
                <Col span={12}><Checkbox value="selection">Selection bias</Checkbox></Col>
                <Col span={12}><Checkbox value="framing">Framing bias</Checkbox></Col>
                <Col span={12}><Checkbox value="political">Political bias</Checkbox></Col>
                <Col span={12}><Checkbox value="emotional">Emotional bias</Checkbox></Col>
                <Col span={12}><Checkbox value="commercial">Commercial bias</Checkbox></Col>
                <Col span={12}><Checkbox value="cultural">Cultural bias</Checkbox></Col>
                <Col span={12}><Checkbox value="unsure">Not sure</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="mediaSkepticism"
            label="How skeptical are you of mainstream media reporting?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="very-skeptical">Very skeptical</Radio>
              <Radio value="skeptical">Skeptical</Radio>
              <Radio value="neutral">Neutral</Radio>
              <Radio value="trusting">Generally trusting</Radio>
              <Radio value="very-trusting">Very trusting</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'AI Perceptions',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your thoughts on AI assistance</Title>
          
          <Form.Item
            name="aiTrust"
            label="How much do you trust AI systems for analyzing news content?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="completely">Completely trust</Radio>
              <Radio value="mostly">Mostly trust</Radio>
              <Radio value="somewhat">Somewhat trust</Radio>
              <Radio value="little">Little trust</Radio>
              <Radio value="no-trust">No trust at all</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="aiAccuracyExpectation"
            label="How accurate do you expect AI to be at distinguishing facts from opinions?"
            rules={[{ required: true, message: 'Please rate expected accuracy' }]}
          >
            <Radio.Group>
              <Radio value="90-100">90-100% accurate</Radio>
              <Radio value="70-89">70-89% accurate</Radio>
              <Radio value="50-69">50-69% accurate</Radio>
              <Radio value="30-49">30-49% accurate</Radio>
              <Radio value="below-30">Below 30% accurate</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="automationPreference"
            label="How much automation would you prefer in bias detection?"
            rules={[{ required: true, message: 'Please select your preference' }]}
          >
            <Radio.Group>
              <Radio value="full-automation">Full automation - AI decides everything</Radio>
              <Radio value="ai-suggestions">AI suggestions with human final decision</Radio>
              <Radio value="balanced">Balanced AI-human collaboration</Radio>
              <Radio value="human-primary">Human primary with AI assistance</Radio>
              <Radio value="minimal-ai">Minimal AI, mostly human judgment</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="learningExpectation"
            label="Do you expect using AI tools will improve your own bias detection skills?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="definitely">Definitely will improve</Radio>
              <Radio value="probably">Probably will improve</Radio>
              <Radio value="maybe">Maybe will improve</Radio>
              <Radio value="probably-not">Probably won't improve</Radio>
              <Radio value="definitely-not">Definitely won't improve</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
  ];

  // Post-questionnaire steps
  const postQuestionnaireSteps = [
    {
      title: 'System Evaluation',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Evaluate the AI system you just used</Title>
          
          <Form.Item
            name="systemAccuracy"
            label="How accurate was the AI at distinguishing facts from opinions?"
            rules={[{ required: true, message: 'Please rate the accuracy' }]}
            initialValue={5}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: '1',
                  3: '3',
                  5: '5',
                  7: '7',
                  10: '10'
                }}
                step={1}
                defaultValue={5}
                tooltip={{ formatter: (value) => `${value}/10` }}
              />
              <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary">Very inaccurate</Text>
                <Text type="secondary">Very accurate</Text>
              </div>
            </div>
          </Form.Item>

          <Form.Item
            name="systemHelpfulness"
            label="How helpful was the AI system for understanding bias?"
            rules={[{ required: true, message: 'Please rate helpfulness' }]}
            initialValue={5}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: '1',
                  3: '3',
                  5: '5',
                  7: '7',
                  10: '10'
                }}
                step={1}
                defaultValue={5}
                tooltip={{ formatter: (value) => `${value}/10` }}
              />
              <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary">Not helpful at all</Text>
                <Text type="secondary">Extremely helpful</Text>
              </div>
            </div>
          </Form.Item>

          <Form.Item
            name="interfaceUsability"
            label="How easy was the interface to use?"
            rules={[{ required: true, message: 'Please rate usability' }]}
            initialValue={5}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: '1',
                  3: '3',
                  5: '5',
                  7: '7',
                  10: '10'
                }}
                step={1}
                defaultValue={5}
                tooltip={{ formatter: (value) => `${value}/10` }}
              />
              <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary">Very difficult</Text>
                <Text type="secondary">Very easy</Text>
              </div>
            </div>
          </Form.Item>

          <Form.Item
            name="userAgency"
            label="Did you feel you maintained control over the analysis process?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="complete-control">Complete control</Radio>
              <Radio value="mostly-control">Mostly in control</Radio>
              <Radio value="some-control">Some control</Radio>
              <Radio value="little-control">Little control</Radio>
              <Radio value="no-control">No control</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="automationBalance"
            label="Was the balance between AI automation and human judgment appropriate?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="too-automated">Too automated</Radio>
              <Radio value="slightly-automated">Slightly too automated</Radio>
              <Radio value="just-right">Just right</Radio>
              <Radio value="slightly-manual">Slightly too manual</Radio>
              <Radio value="too-manual">Too manual</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Learning & Skills',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Changes in your bias detection abilities</Title>
          
          <Form.Item
            name="skillImprovement"
            label="Do you feel your bias detection skills improved after using the system?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="significantly-improved">Significantly improved</Radio>
              <Radio value="somewhat-improved">Somewhat improved</Radio>
              <Radio value="slightly-improved">Slightly improved</Radio>
              <Radio value="no-change">No change</Radio>
              <Radio value="worse">Got worse</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="confidenceChange"
            label="How has your confidence in identifying bias changed?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="much-more-confident">Much more confident</Radio>
              <Radio value="more-confident">More confident</Radio>
              <Radio value="slightly-more-confident">Slightly more confident</Radio>
              <Radio value="no-change">No change</Radio>
              <Radio value="less-confident">Less confident</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="independentDetection"
            label="Do you feel more capable of detecting bias independently (without AI)?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="much-more-capable">Much more capable</Radio>
              <Radio value="more-capable">More capable</Radio>
              <Radio value="slightly-more-capable">Slightly more capable</Radio>
              <Radio value="no-change">No change</Radio>
              <Radio value="less-capable">Less capable</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="learningMechanisms"
            label="What helped you learn the most? (select all that apply)"
            rules={[{ required: true, message: 'Please select at least one' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="ai-explanations">AI explanations</Checkbox></Col>
                <Col span={12}><Checkbox value="examples">Concrete examples</Checkbox></Col>
                <Col span={12}><Checkbox value="practice">Practice with feedback</Checkbox></Col>
                <Col span={12}><Checkbox value="comparisons">Comparing different analyses</Checkbox></Col>
                <Col span={12}><Checkbox value="interactive-features">Interactive features</Checkbox></Col>
                <Col span={12}><Checkbox value="visual-highlights">Visual highlighting</Checkbox></Col>
                <Col span={12}><Checkbox value="step-by-step">Step-by-step process</Checkbox></Col>
                <Col span={12}><Checkbox value="nothing">Nothing helped</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Behavioral Changes',
      icon: <TeamOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Impact on your media consumption behavior</Title>
          
          <Form.Item
            name="futureVerification"
            label="Will you verify news sources more often after this experience?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="definitely-more">Definitely more often</Radio>
              <Radio value="probably-more">Probably more often</Radio>
              <Radio value="maybe-more">Maybe more often</Radio>
              <Radio value="no-change">No change</Radio>
              <Radio value="less-likely">Less likely</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="mediaApproach"
            label="How will your approach to reading news change?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="much-more-critical">Much more critical/analytical</Radio>
              <Radio value="more-critical">More critical/analytical</Radio>
              <Radio value="slightly-more-critical">Slightly more critical</Radio>
              <Radio value="no-change">No change</Radio>
              <Radio value="less-critical">Less critical</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="toolAdoption"
            label="Would you use similar AI bias detection tools in the future?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="definitely">Definitely would use</Radio>
              <Radio value="probably">Probably would use</Radio>
              <Radio value="maybe">Maybe would use</Radio>
              <Radio value="probably-not">Probably wouldn't use</Radio>
              <Radio value="definitely-not">Definitely wouldn't use</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="recommendToOthers"
            label="Would you recommend this tool to others?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="definitely">Definitely recommend</Radio>
              <Radio value="probably">Probably recommend</Radio>
              <Radio value="maybe">Maybe recommend</Radio>
              <Radio value="probably-not">Probably not recommend</Radio>
              <Radio value="definitely-not">Definitely not recommend</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Final Feedback',
      icon: <CheckCircleOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your overall experience and suggestions</Title>
          
          <Form.Item
            name="overallSatisfaction"
            label="Overall satisfaction with the system"
            rules={[{ required: true, message: 'Please rate your satisfaction' }]}
            initialValue={5}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: '1',
                  3: '3',
                  5: '5',
                  7: '7',
                  10: '10'
                }}
                step={1}
                defaultValue={5}
                tooltip={{ formatter: (value) => `${value}/10` }}
              />
              <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
                <Text type="secondary">Very dissatisfied</Text>
                <Text type="secondary">Very satisfied</Text>
              </div>
            </div>
          </Form.Item>

          <Form.Item
            name="mostValuableFeature"
            label="What was the most valuable feature of the system?"
            rules={[{ required: true, message: 'Please provide feedback' }]}
          >
            <TextArea rows={3} placeholder="Describe the feature you found most helpful..." />
          </Form.Item>

          <Form.Item
            name="improvements"
            label="What improvements would you suggest?"
            rules={[{ required: true, message: 'Please provide suggestions' }]}
          >
            <TextArea rows={3} placeholder="Suggest improvements or additional features..." />
          </Form.Item>

          <Form.Item
            name="concerns"
            label="Do you have any concerns about AI-assisted bias detection?"
            rules={[{ required: true, message: 'Please share your thoughts' }]}
          >
            <TextArea rows={3} placeholder="Share any concerns or limitations you noticed..." />
          </Form.Item>

          <Form.Item
            name="additionalComments"
            label="Additional comments (optional)"
          >
            <TextArea rows={3} placeholder="Any other thoughts or feedback..." />
          </Form.Item>
        </Space>
      ),
    },
  ];

  const steps = isPostQuestionnaire ? postQuestionnaireSteps : preQuestionnaireSteps;
  const questionnaireTitle = isPostQuestionnaire ? 'Post-Study Questionnaire' : 'Pre-Study Questionnaire';
  const questionnaireDescription = isPostQuestionnaire 
    ? 'Please share your experience with the AI bias detection system and how it affected your understanding.'
    : 'This questionnaire helps us understand your media consumption habits and initial perceptions.';

  return (
    <AppLayout>
      <Row justify="center" style={{ height: '100%' }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={10}>
          <Card
            style={{ 
              borderRadius: 15, 
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              background: 'white'
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <Title level={2} style={{ marginBottom: 8 }}>
                <ExperimentOutlined style={{ color: isPostQuestionnaire ? '#52c41a' : '#3498db', marginRight: 8 }} />
                {questionnaireTitle}
              </Title>
              <Paragraph type="secondary" style={{ fontSize: 16 }}>
                {questionnaireDescription}
                Your responses will be kept confidential and used only for research purposes.
              </Paragraph>
            </div>

            <Steps current={currentStep} style={{ marginBottom: 32 }}>
              {steps.map((step, index) => (
                <Step key={index} title={step.title} icon={step.icon} />
              ))}
            </Steps>

            <Form form={form} layout="vertical" style={{ minHeight: '400px' }}>
              {steps[currentStep].content}
            </Form>

            <Divider />

            <div style={{ textAlign: 'center' }}>
              <Space>
                {currentStep > 0 && (
                  <Button onClick={handlePrevious}>
                    Previous
                  </Button>
                )}
                
                {currentStep < steps.length - 1 && (
                  <Button type="primary" onClick={handleNext}>
                    Next
                  </Button>
                )}
                
                {currentStep === steps.length - 1 && (
                  <Button 
                    type="primary" 
                    onClick={handleSubmit}
                    loading={loading}
                    icon={<RocketOutlined />}
                    size="large"
                    style={{
                      background: isPostQuestionnaire 
                        ? 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)'
                        : 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
                      border: 'none',
                      borderRadius: 8,
                      height: 48,
                      fontSize: 16,
                      fontWeight: 600,
                    }}
                  >
                    {isPostQuestionnaire ? 'Complete Study' : 'Complete & Start Analysis'}
                  </Button>
                )}
              </Space>
            </div>
          </Card>
        </Col>
      </Row>
    </AppLayout>
  );
};

export default EnhancedQuestionnaires;