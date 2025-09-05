import React, { useState } from 'react';
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
} from 'antd';
import {
  UserOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  BulbOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import apiService from '../services/api';

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
  const fromBiasResearch = searchParams.get('fromBiasResearch') === 'true';

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const allFormFields = form.getFieldsValue(true);
      console.log('All form fields (all steps):', allFormFields);
      console.log('All form field names:', Object.keys(allFormFields));
      console.log('Total field count:', Object.keys(allFormFields).length);
      
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
      }
      
      const values = allFormFields;
      
      console.log('Final form data to save:', values);
      console.log('Final field count:', Object.keys(values).length);
      
      const currentSessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const dataToSave = {
        ...values,
        sessionId: currentSessionId,
        timestamp: new Date().toISOString(),
        type: isPostQuestionnaire ? 'post' : 'pre'
      };
      
      console.log('Data being sent to backend:', dataToSave);
      
      // Submit questionnaire data to backend (which saves to Excel)
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
        const questionnaireKey = isPostQuestionnaire ? `post_questionnaire_${currentSessionId}` : `pre_questionnaire_${currentSessionId}`;
        localStorage.setItem(questionnaireKey, JSON.stringify(dataToSave));
        
        if (isPostQuestionnaire) {
          if (fromBiasResearch) {
            message.success('Post-study questionnaire completed! Proceeding to exit questionnaire.');
            setTimeout(() => {
              navigate(`/exit-questionnaire?sessionId=${currentSessionId}`);
            }, 1500);
          } else {
            message.success('Post-study questionnaire completed and saved! Thank you for your participation.');
            setTimeout(() => {
              navigate('/');
            }, 1500);
          }
        } else {
          message.success('Pre-study questionnaire completed and saved! Redirecting to the analysis tool...');
          setTimeout(() => {
            navigate(`/analysis?sessionId=${currentSessionId}&fromQuestionnaire=true`);
          }, 1500);
        }
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
          >
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
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
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
          >
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
          >
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
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
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
          >
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
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="crossCheckFrequency"
            label="How often do you cross-check news statements with other sources?"
            rules={[{ required: true, message: 'Please rate your frequency' }]}
          >
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