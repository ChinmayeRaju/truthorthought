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
  Divider
} from 'antd';
import { 
  ExperimentOutlined, 
  UserOutlined, 
  QuestionCircleOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import apiService from '../services/api';

const { Title, Paragraph } = Typography;
const { Step } = Steps;

const Questionnaires: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
      const values = await form.validateFields();
      
      // Generate session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const dataToSave = {
        ...values,
        sessionId,
        timestamp: new Date().toISOString(),
        type: 'basic'
      };
      
      // Submit to backend (saves to Excel)
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
        // Also store questionnaire data in localStorage as backup
        localStorage.setItem(`questionnaire_${sessionId}`, JSON.stringify(dataToSave));
        
        message.success('Questionnaire completed and saved! Redirecting to analysis...');
        
        // Redirect to main analysis with session info
        setTimeout(() => {
          navigate(`/?sessionId=${sessionId}&fromQuestionnaire=true`);
        }, 1500);
      } else {
        throw new Error(response.message || 'Failed to save questionnaire data');
      }
      
    } catch (error) {
      console.log('Submission failed:', error);
      message.error('Please complete all required fields');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
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
        </Space>
      ),
    },
    {
      title: 'Media Literacy',
      icon: <QuestionCircleOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your media literacy habits</Title>
          
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
            name="biasAwareness"
            label="How confident are you in identifying media bias?"
            rules={[{ required: true, message: 'Please select an option' }]}
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
      title: 'Initial Perceptions',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your initial thoughts</Title>
          
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
            name="factOpinionConfidence"
            label="How confident are you in distinguishing facts from opinions in news?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="very-confident">Very confident</Radio>
              <Radio value="confident">Confident</Radio>
              <Radio value="somewhat-confident">Somewhat confident</Radio>
              <Radio value="not-confident">Not confident</Radio>
              <Radio value="struggle">Often struggle</Radio>
            </Radio.Group>
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
  ];

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
                <ExperimentOutlined style={{ color: '#3498db', marginRight: 8 }} />
                Research Study Questionnaire
              </Title>
              <Paragraph type="secondary" style={{ fontSize: 16 }}>
                This questionnaire helps us understand your media consumption habits and initial perceptions. 
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
                      background: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
                      border: 'none',
                      borderRadius: 8,
                      height: 48,
                      fontSize: 16,
                      fontWeight: 600,
                    }}
                  >
                    Complete & Start Analysis
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

export default Questionnaires;
