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
  Col
} from 'antd';
import {
  UserOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  BulbOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';

const { Title, Text } = Typography;
const { TextArea } = Input;

const EnhancedQuestionnaires: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const sessionId = searchParams.get('sessionId');
  const isPostQuestionnaire = searchParams.get('type') === 'post';

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
        }, 1500);
      } else {
        message.success('Pre-study questionnaire completed! Redirecting to the analysis tool...');
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

  // Pre-experiment questionnaire steps
  const preQuestionnaireSteps = [
    {
      title: 'News Familiarity',
      icon: <UserOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your News Reading Habits</Title>
          
          <Form.Item
            name="newsFamiliarity"
            label="How familiar are you with online news sources like BBC, CNN, Guardian?"
            rules={[{ required: true, message: 'Please rate your familiarity' }]}
            initialValue={3}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not familiar',
                  2: 'Slightly familiar',
                  3: 'Moderately familiar',
                  4: 'Very familiar',
                  5: 'Extremely familiar'
                }}
                step={1}
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="newsFrequency"
            label="How often do you read online news?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="daily">Daily</Radio>
              <Radio value="weekly">Weekly</Radio>
              <Radio value="monthly">Monthly</Radio>
              <Radio value="rarely">Rarely</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="factOpinionConfidence"
            label="How confident are you in distinguishing facts from opinions in news articles?"
            rules={[{ required: true, message: 'Please rate your confidence' }]}
            initialValue={3}
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Trust & Bias',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Your Trust in News Sources</Title>
          
          <Form.Item
            name="trustedOutlets"
            label="Which outlets do you trust the most?"
            rules={[{ required: true, message: 'Please select at least one option' }]}
          >
            <Checkbox.Group>
              <Checkbox value="bbc">BBC</Checkbox>
              <Checkbox value="cnn">CNN</Checkbox>
              <Checkbox value="guardian">Guardian</Checkbox>
              <Checkbox value="other">Other</Checkbox>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="outletsBiased"
            label="Do you feel certain outlets are more biased than others?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="yes">Yes</Radio>
              <Radio value="no">No</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="biasedOutletsSpecify"
            label="If yes, which outlets do you consider biased?"
            dependencies={['outletsBiased']}
          >
            <TextArea rows={2} placeholder="Specify which outlets and why..." />
          </Form.Item>

          <Form.Item
            name="aiFamiliarityTools"
            label="How familiar are you with AI-assisted fact/opinion tools?"
            rules={[{ required: true, message: 'Please rate your familiarity' }]}
            initialValue={3}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not familiar',
                  2: 'Slightly familiar',
                  3: 'Moderately familiar',
                  4: 'Very familiar',
                  5: 'Extremely familiar'
                }}
                step={1}
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Reading Habits',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>How You Process News</Title>
          
          <Form.Item
            name="headlineReliance"
            label="How much do you rely on headlines to judge whether something is fact or opinion?"
            rules={[{ required: true, message: 'Please rate your reliance' }]}
            initialValue={3}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not at all',
                  2: 'Slightly',
                  3: 'Moderately',
                  4: 'Very much',
                  5: 'Completely'
                }}
                step={1}
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="crossCheckFrequency"
            label="How often do you cross-check news statements with other sources?"
            rules={[{ required: true, message: 'Please rate your frequency' }]}
            initialValue={3}
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Demographics',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>About You</Title>
          
          <Form.Item
            name="techExperience"
            label="How do you rate your experience with technology?"
            rules={[{ required: true, message: 'Please select your experience level' }]}
          >
            <Radio.Group>
              <Radio value="beginner">Beginner</Radio>
              <Radio value="intermediate">Intermediate</Radio>
              <Radio value="advanced">Advanced</Radio>
              <Radio value="expert">Expert</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="age"
            label="Age"
            rules={[{ required: true, message: 'Please enter your age' }]}
          >
            <Input placeholder="Enter your age" type="number" />
          </Form.Item>

          <Form.Item
            name="profession"
            label="Profession"
            rules={[{ required: true, message: 'Please enter your profession' }]}
          >
            <Input placeholder="Enter your profession" />
          </Form.Item>
        </Space>
      ),
    },
  ];

  // Post-experiment questionnaire steps
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
            initialValue={50}
          >
            <div>
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
                defaultValue={50}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="effortRequired"
            label="How much effort did you need to classify statements?"
            rules={[{ required: true, message: 'Please rate the effort required' }]}
            initialValue={50}
          >
            <div>
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
                defaultValue={50}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="frustrationLevel"
            label="How frustrated were you while using Truth or Thought?"
            rules={[{ required: true, message: 'Please rate your frustration level' }]}
            initialValue={50}
          >
            <div>
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
                defaultValue={50}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
            </div>
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
            initialValue={3}
          >
            <div>
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="controlLevel"
            label="How much control did you feel over the classification process?"
            rules={[{ required: true, message: 'Please rate your sense of control' }]}
            initialValue={3}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'No control',
                  2: 'Little control',
                  3: 'Some control',
                  4: 'Good control',
                  5: 'Full control'
                }}
                step={1}
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="sourceInfluence"
            label="How much did the source labels (BBC, CNN, Guardian) influence your trust in the system?"
            rules={[{ required: true, message: 'Please rate the influence' }]}
            initialValue={3}
          >
            <div>
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="explanationHelpfulness"
            label="Did the explanations (if provided) help you understand classifications?"
            rules={[{ required: true, message: 'Please rate the helpfulness' }]}
            initialValue={3}
          >
            <div>
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
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
              <Checkbox value="explanation">Explanation</Checkbox>
              <Checkbox value="citations">Citations</Checkbox>
              <Checkbox value="highlighting">Highlighting</Checkbox>
              <Checkbox value="other">Other</Checkbox>
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
            initialValue={3}
          >
            <div>
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
                defaultValue={3}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
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

  const steps = isPostQuestionnaire ? postQuestionnaireSteps : preQuestionnaireSteps;

  const next = () => {
    setCurrentStep(currentStep + 1);
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <AppLayout>
      <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
        <Card>
          <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
            {isPostQuestionnaire ? 'Post-Experiment Questionnaire' : 'Pre-Experiment Questionnaire'}
          </Title>
          
          <Steps current={currentStep} style={{ marginBottom: '32px' }}>
            {steps.map((step, index) => (
              <Steps.Step key={index} title={step.title} icon={step.icon} />
            ))}
          </Steps>

          <Form form={form} layout="vertical" style={{ minHeight: '400px' }}>
            <div>{steps[currentStep].content}</div>
          </Form>

          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <Space>
              {currentStep > 0 && (
                <Button onClick={prev}>
                  Previous
                </Button>
              )}
              {currentStep < steps.length - 1 && (
                <Button type="primary" onClick={next}>
                  Next
                </Button>
              )}
              {currentStep === steps.length - 1 && (
                <Button type="primary" onClick={handleSubmit} loading={loading}>
                  Submit {isPostQuestionnaire ? 'Post-Experiment' : 'Pre-Experiment'} Questionnaire
                </Button>
              )}
            </Space>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
};

export default EnhancedQuestionnaires;