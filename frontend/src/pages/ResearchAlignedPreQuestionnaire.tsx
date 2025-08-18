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
  RobotOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import apiService from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ResearchAlignedPreQuestionnaire: React.FC = () => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const sessionId = searchParams.get('sessionId');

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const allFormFields = form.getFieldsValue(true);
      console.log('Research-aligned pre-questionnaire data:', allFormFields);
      
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
      }
      
      const values = allFormFields;
      const currentSessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const questionnaireKey = `research_pre_questionnaire_${currentSessionId}`;
      
      const dataToSave = {
        ...values,
        timestamp: new Date().toISOString(),
        type: 'research_pre',
        sessionId: currentSessionId
      };
      
      // Submit to backend (saves to Excel)
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
        // Also save to localStorage as backup
        localStorage.setItem(questionnaireKey, JSON.stringify(dataToSave));
        
        message.success('Pre-study questionnaire completed and saved! Redirecting to the analysis tool...');
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

  const researchAlignedSteps = [
    {
      title: 'Demographics & Individual Differences',
      icon: <UserOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Background Information (RQ6: Individual Differences)</Title>
          <Paragraph>
            Understanding your background helps us analyze how individual differences affect AI tool utility and adoption.
          </Paragraph>
          
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Form.Item
                name="age"
                label="Age"
                rules={[{ required: true, message: 'Please select your age range' }]}
              >
                <Select placeholder="Select your age range">
                  <Option value="18-24">18-24</Option>
                  <Option value="25-34">25-34</Option>
                  <Option value="35-44">35-44</Option>
                  <Option value="45-54">45-54</Option>
                  <Option value="55-64">55-64</Option>
                  <Option value="65+">65+</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="education"
                label="Highest education level"
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
            </Col>
          </Row>

          <Form.Item
            name="profession"
            label="Profession/Field of work"
            rules={[{ required: true, message: 'Please enter your profession' }]}
          >
            <Input placeholder="Enter your profession or field of work" />
          </Form.Item>

          <Form.Item
            name="technologyComfort"
            label="How comfortable are you with using digital technology and AI tools?"
            rules={[{ required: true, message: 'Please rate your technology comfort' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very uncomfortable',
                  2: 'Uncomfortable',
                  3: 'Neutral',
                  4: 'Comfortable',
                  5: 'Very comfortable'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="learningStyle"
            label="How do you prefer to learn new information?"
            rules={[{ required: true, message: 'Please select your learning preference' }]}
          >
            <Radio.Group>
              <Radio value="visual">Visual (charts, diagrams, highlighting)</Radio>
              <Radio value="textual">Textual (reading, written explanations)</Radio>
              <Radio value="interactive">Interactive (hands-on, trial and error)</Radio>
              <Radio value="structured">Structured (step-by-step guidance)</Radio>
              <Radio value="exploratory">Exploratory (self-discovery)</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="cognitiveStyle"
            label="When making decisions, do you typically:"
            rules={[{ required: true, message: 'Please select your decision-making style' }]}
          >
            <Radio.Group>
              <Radio value="analytical">Analyze details carefully before deciding</Radio>
              <Radio value="intuitive">Go with your gut feeling</Radio>
              <Radio value="systematic">Follow a systematic process</Radio>
              <Radio value="collaborative">Seek input from others</Radio>
              <Radio value="quick">Make quick decisions and adjust as needed</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Fact/Opinion Detection Baseline',
      icon: <ExperimentOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Current Fact/Opinion Detection Abilities (RQ1: NLP Accuracy Baseline)</Title>
          <Paragraph>
            These questions establish your current confidence and methods for distinguishing facts from opinions in news content.
          </Paragraph>
          
          <Form.Item
            name="factOpinionConfidence"
            label="How confident are you in your ability to distinguish facts from opinions in news articles?"
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

          <Form.Item
            name="factOpinionMethods"
            label="What methods do you currently use to distinguish facts from opinions? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one method' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="sourceCredibility">Check source credibility</Checkbox></Col>
                <Col span={12}><Checkbox value="crossReference">Cross-reference with other sources</Checkbox></Col>
                <Col span={12}><Checkbox value="languageAnalysis">Analyze language and tone</Checkbox></Col>
                <Col span={12}><Checkbox value="evidenceCheck">Look for supporting evidence</Checkbox></Col>
                <Col span={12}><Checkbox value="authorExpertise">Consider author expertise</Checkbox></Col>
                <Col span={12}><Checkbox value="factCheckers">Use fact-checking websites</Checkbox></Col>
                <Col span={12}><Checkbox value="intuition">Rely on intuition/gut feeling</Checkbox></Col>
                <Col span={12}><Checkbox value="other">Other methods</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="factOpinionAccuracy"
            label="How accurate do you think you are at distinguishing facts from opinions?"
            rules={[{ required: true, message: 'Please estimate your accuracy' }]}
            initialValue={0}
          >
            <div>
              <Slider
                min={0}
                max={100}
                marks={{
                  0: '0%',
                  25: '25%',
                  50: '50%',
                  75: '75%',
                  100: '100%'
                }}
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}%` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="factOpinionChallenges"
            label="What do you find most challenging about distinguishing facts from opinions in news?"
            rules={[{ required: true, message: 'Please describe your challenges' }]}
          >
            <TextArea 
              rows={3} 
              placeholder="Describe the main difficulties you encounter when trying to separate factual information from opinion statements..."
            />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Bias Detection & Media Literacy',
      icon: <EyeOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Bias Detection Baseline (RQ3) & Traditional Media Literacy (RQ4)</Title>
          <Paragraph>
            Understanding your current bias detection skills and traditional media literacy practices.
          </Paragraph>
          
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

          <Form.Item
            name="biasDetectionMethods"
            label="What methods do you use to detect bias in news articles? (Select all that apply)"
            rules={[{ required: true, message: 'Please select at least one method' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="languageTone">Analyze language and tone</Checkbox></Col>
                <Col span={12}><Checkbox value="sourceSelection">Examine source selection</Checkbox></Col>
                <Col span={12}><Checkbox value="omittedInfo">Look for omitted information</Checkbox></Col>
                <Col span={12}><Checkbox value="multipleOutlets">Compare across outlets</Checkbox></Col>
                <Col span={12}><Checkbox value="authorBackground">Research author background</Checkbox></Col>
                <Col span={12}><Checkbox value="headlineAnalysis">Analyze headlines vs content</Checkbox></Col>
                <Col span={12}><Checkbox value="emotionalLanguage">Identify emotional language</Checkbox></Col>
                <Col span={12}><Checkbox value="statisticalManipulation">Check for statistical manipulation</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="mediaLiteracyTraining"
            label="Have you received formal training in media literacy or critical thinking?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group>
              <Radio value="extensive">Yes, extensive training</Radio>
              <Radio value="some">Yes, some training</Radio>
              <Radio value="minimal">Minimal training</Radio>
              <Radio value="none">No formal training</Radio>
              <Radio value="selfTaught">Self-taught through experience</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newsEvaluationProcess"
            label="Describe your typical process for evaluating the credibility of a news article:"
            rules={[{ required: true, message: 'Please describe your evaluation process' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Walk through the steps you typically take when you encounter a news article and want to assess its credibility and potential bias..."
            />
          </Form.Item>

          <Form.Item
            name="informationVerificationFrequency"
            label="How often do you verify news information through multiple sources?"
            rules={[{ required: true, message: 'Please select frequency' }]}
          >
            <Radio.Group>
              <Radio value="always">Always</Radio>
              <Radio value="usually">Usually</Radio>
              <Radio value="sometimes">Sometimes</Radio>
              <Radio value="rarely">Rarely</Radio>
              <Radio value="never">Never</Radio>
            </Radio.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Automation & AI Preferences',
      icon: <RobotOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Automation Preferences & AI Trust (RQ5: Automation Balance)</Title>
          <Paragraph>
            Understanding your preferences for automated assistance versus human judgment in information processing.
          </Paragraph>
          
          <Form.Item
            name="automationPreference"
            label="In general, do you prefer automated tools or manual processes for analyzing information?"
            rules={[{ required: true, message: 'Please indicate your preference' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Strongly prefer manual',
                  2: 'Prefer manual',
                  3: 'No preference',
                  4: 'Prefer automated',
                  5: 'Strongly prefer automated'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="aiTrustLevel"
            label="How much do you trust AI systems to make accurate judgments about information?"
            rules={[{ required: true, message: 'Please rate your trust level' }]}
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
            name="aiExperienceLevel"
            label="How much experience do you have with AI-powered tools?"
            rules={[{ required: true, message: 'Please select your experience level' }]}
          >
            <Radio.Group>
              <Radio value="extensive">Extensive - I use AI tools regularly</Radio>
              <Radio value="moderate">Moderate - I've used several AI tools</Radio>
              <Radio value="limited">Limited - I've tried a few AI tools</Radio>
              <Radio value="minimal">Minimal - I've barely used any AI tools</Radio>
              <Radio value="none">None - This would be my first AI tool experience</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="automationConcerns"
            label="What concerns, if any, do you have about using AI for news analysis? (Select all that apply)"
            rules={[{ required: true, message: 'Please select your concerns or "No concerns"' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="accuracy">Accuracy of AI judgments</Checkbox></Col>
                <Col span={12}><Checkbox value="bias">AI system bias</Checkbox></Col>
                <Col span={12}><Checkbox value="transparency">Lack of transparency</Checkbox></Col>
                <Col span={12}><Checkbox value="overReliance">Over-reliance on automation</Checkbox></Col>
                <Col span={12}><Checkbox value="skillAtrophy">Loss of critical thinking skills</Checkbox></Col>
                <Col span={12}><Checkbox value="privacy">Privacy concerns</Checkbox></Col>
                <Col span={12}><Checkbox value="manipulation">Potential for manipulation</Checkbox></Col>
                <Col span={12}><Checkbox value="noConcerns">No significant concerns</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Cognitive Processing & Interface Preferences',
      icon: <ThunderboltOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Cognitive Load & Interface Preferences (RQ2: Interface Strategies)</Title>
          <Paragraph>
            Understanding how you process information and your preferences for interface design to optimize cognitive load.
          </Paragraph>
          
          <Form.Item
            name="informationProcessingStyle"
            label="When reading news articles, how do you typically process information?"
            rules={[{ required: true, message: 'Please select your processing style' }]}
          >
            <Radio.Group>
              <Radio value="sequential">Read sequentially from beginning to end</Radio>
              <Radio value="scanning">Scan for key points and important information</Radio>
              <Radio value="skimming">Skim headlines and first paragraphs</Radio>
              <Radio value="detailed">Read carefully and analyze in detail</Radio>
              <Radio value="comparative">Compare with other sources while reading</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="cognitiveLoadFactors"
            label="What makes news analysis mentally demanding for you? (Select all that apply)"
            rules={[{ required: true, message: 'Please select factors that increase mental effort' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="complexLanguage">Complex language and jargon</Checkbox></Col>
                <Col span={12}><Checkbox value="informationVolume">Large volume of information</Checkbox></Col>
                <Col span={12}><Checkbox value="contradictoryInfo">Contradictory information</Checkbox></Col>
                <Col span={12}><Checkbox value="timeConstraints">Time pressure to make judgments</Checkbox></Col>
                <Col span={12}><Checkbox value="uncertainSources">Uncertain source credibility</Checkbox></Col>
                <Col span={12}><Checkbox value="emotionalContent">Emotionally charged content</Checkbox></Col>
                <Col span={12}><Checkbox value="technicalDetails">Technical or statistical details</Checkbox></Col>
                <Col span={12}><Checkbox value="multipleViewpoints">Multiple conflicting viewpoints</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="preferredInformationPresentation"
            label="How do you prefer information to be presented for easy understanding?"
            rules={[{ required: true, message: 'Please select your preference' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="bulletPoints">Bullet points and lists</Checkbox></Col>
                <Col span={12}><Checkbox value="highlighting">Color coding and highlighting</Checkbox></Col>
                <Col span={12}><Checkbox value="summaries">Executive summaries</Checkbox></Col>
                <Col span={12}><Checkbox value="visualAids">Charts and visual aids</Checkbox></Col>
                <Col span={12}><Checkbox value="stepByStep">Step-by-step breakdowns</Checkbox></Col>
                <Col span={12}><Checkbox value="comparisons">Side-by-side comparisons</Checkbox></Col>
                <Col span={12}><Checkbox value="examples">Concrete examples</Checkbox></Col>
                <Col span={12}><Checkbox value="plainText">Plain text paragraphs</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="mentalEffortNews"
            label="How much mental effort does it typically take you to analyze a news article for bias and accuracy?"
            rules={[{ required: true, message: 'Please rate the mental effort required' }]}
            initialValue={0}
          >
            <div>
              <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Very low effort',
                  25: 'Low effort',
                  50: 'Moderate effort',
                  75: 'High effort',
                  100: 'Very high effort'
                }}
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="learningMechanismsPreference"
            label="What learning features would best help you analyze news content and detect bias?"
            rules={[{ required: true, message: 'Please select your preferred learning mechanisms' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={24}><Checkbox value="stepByStepGuidance">Step-by-step reasoning guides</Checkbox></Col>
                <Col span={24}><Checkbox value="practiceExamples">Practice examples with explanations</Checkbox></Col>
                <Col span={24}><Checkbox value="realtimeFeedback">Real-time feedback on your analysis</Checkbox></Col>
                <Col span={24}><Checkbox value="analyticalFrameworks">Structured checklists and frameworks</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'News Consumption Patterns',
      icon: <SettingOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Current News Consumption & Expectations</Title>
          <Paragraph>
            Understanding your current news consumption patterns and expectations for AI assistance.
          </Paragraph>
          
          <Form.Item
            name="generalMediaTrust"
            label="What is your general confidence level in the accuracy, objectivity, and reliability of mainstream news reporting across different outlets and platforms?"
            rules={[{ required: true, message: 'Please rate your confidence in mainstream media' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very low confidence',
                  2: 'Low confidence',
                  3: 'Moderate confidence',
                  4: 'High confidence',
                  5: 'Very high confidence'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
            </div>
          </Form.Item>

          <div style={{ marginBottom: '24px' }}>
            <Text strong>Rank these news organizations from most to least trustworthy based on your perception of their accuracy, objectivity, and editorial standards:</Text>
            <div style={{ marginTop: '16px' }}>
              <Text>Click to select your ranking (1 = Most trustworthy, 5 = Least trustworthy):</Text>
            </div>
          </div>

          <Form.Item
            name="mostTrustworthy"
            label="1st - Most Trustworthy"
            rules={[{ required: true, message: 'Please select most trustworthy' }]}
          >
            <Radio.Group>
              <Radio value="cnn">CNN</Radio>
              <Radio value="bbc">BBC</Radio>
              <Radio value="guardian">The Guardian</Radio>
              <Radio value="reuters">Reuters</Radio>
              <Radio value="dailymail">Daily Mail</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="secondTrustworthy"
            label="2nd - Second Most Trustworthy"
            rules={[{ required: true, message: 'Please select second most trustworthy' }]}
          >
            <Radio.Group>
              <Radio value="cnn">CNN</Radio>
              <Radio value="bbc">BBC</Radio>
              <Radio value="guardian">The Guardian</Radio>
              <Radio value="reuters">Reuters</Radio>
              <Radio value="dailymail">Daily Mail</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="thirdTrustworthy"
            label="3rd - Middle Trustworthy"
            rules={[{ required: true, message: 'Please select third most trustworthy' }]}
          >
            <Radio.Group>
              <Radio value="cnn">CNN</Radio>
              <Radio value="bbc">BBC</Radio>
              <Radio value="guardian">The Guardian</Radio>
              <Radio value="reuters">Reuters</Radio>
              <Radio value="dailymail">Daily Mail</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="fourthTrustworthy"
            label="4th - Second Least Trustworthy"
            rules={[{ required: true, message: 'Please select fourth most trustworthy' }]}
          >
            <Radio.Group>
              <Radio value="cnn">CNN</Radio>
              <Radio value="bbc">BBC</Radio>
              <Radio value="guardian">The Guardian</Radio>
              <Radio value="reuters">Reuters</Radio>
              <Radio value="dailymail">Daily Mail</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="leastTrustworthy"
            label="5th - Least Trustworthy"
            rules={[{ required: true, message: 'Please select least trustworthy' }]}
          >
            <Radio.Group>
              <Radio value="cnn">CNN</Radio>
              <Radio value="bbc">BBC</Radio>
              <Radio value="guardian">The Guardian</Radio>
              <Radio value="reuters">Reuters</Radio>
              <Radio value="dailymail">Daily Mail</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newsEmotionalImpact"
            label="Rate the typical emotional impact and psychological burden you experience when consuming news content, particularly regarding political events, social issues, and crisis reporting"
            rules={[{ required: true, message: 'Please rate the emotional impact' }]}
            initialValue={1}
          >
            <div>
              <Slider
                min={1}
                max={10}
                marks={{
                  1: 'Completely unaffected',
                  3: 'Mildly affected',
                  5: 'Moderately affected',
                  7: 'Significantly affected',
                  10: 'Severely distressing'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/10` }}
              />
            </div>
          </Form.Item>

          <Form.Item
            name="newsConsumptionFrequency"
            label="How often do you read or consume news content?"
            rules={[{ required: true, message: 'Please select your consumption frequency' }]}
          >
            <Radio.Group>
              <Radio value="multiple">Multiple times per day</Radio>
              <Radio value="daily">Once daily</Radio>
              <Radio value="fewTimes">A few times per week</Radio>
              <Radio value="weekly">Weekly</Radio>
              <Radio value="occasionally">Occasionally</Radio>
              <Radio value="rarely">Rarely</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newsSourceTypes"
            label="What types of news sources do you typically use? (Select all that apply)"
            rules={[{ required: true, message: 'Please select your news sources' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="traditionalNews">Traditional news websites</Checkbox></Col>
                <Col span={12}><Checkbox value="socialMedia">Social media platforms</Checkbox></Col>
                <Col span={12}><Checkbox value="newsAggregators">News aggregators (Google News, etc.)</Checkbox></Col>
                <Col span={12}><Checkbox value="newsletters">Email newsletters</Checkbox></Col>
                <Col span={12}><Checkbox value="podcasts">News podcasts</Checkbox></Col>
                <Col span={12}><Checkbox value="television">Television news</Checkbox></Col>
                <Col span={12}><Checkbox value="radio">Radio news</Checkbox></Col>
                <Col span={12}><Checkbox value="print">Print newspapers/magazines</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="aiExpectations"
            label="What do you expect from an AI tool that helps analyze news content?"
            rules={[{ required: true, message: 'Please describe your expectations' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Describe what you would want an AI tool to do when helping you analyze news articles for facts, opinions, and bias..."
            />
          </Form.Item>

          <Form.Item
            name="successMetrics"
            label="How would you measure whether an AI news analysis tool is successful?"
            rules={[{ required: true, message: 'Please select success metrics' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="accuracy">High accuracy in classifications</Checkbox></Col>
                <Col span={12}><Checkbox value="timeEfficiency">Saves time in analysis</Checkbox></Col>
                <Col span={12}><Checkbox value="learningImprovement">Improves my analysis skills</Checkbox></Col>
                <Col span={12}><Checkbox value="confidenceBoost">Increases my confidence</Checkbox></Col>
                <Col span={12}><Checkbox value="biasReduction">Helps reduce my own bias</Checkbox></Col>
                <Col span={12}><Checkbox value="comprehensiveness">Catches things I might miss</Checkbox></Col>
                <Col span={12}><Checkbox value="easeOfUse">Easy and intuitive to use</Checkbox></Col>
                <Col span={12}><Checkbox value="transparency">Provides clear explanations</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="additionalComments"
            label="Any additional comments about your news consumption habits or expectations for AI assistance?"
          >
            <TextArea 
              rows={3} 
              placeholder="Optional: Share any additional thoughts about how you consume news or what you hope to gain from AI-assisted analysis..."
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
            Research Pre-Study Questionnaire
          </Title>
          <Paragraph style={{ textAlign: 'center', marginBottom: '32px', color: '#666' }}>
            This questionnaire establishes baseline measurements for our research on AI-assisted news analysis. 
            Your responses help us understand how individual differences, current skills, and preferences 
            affect the utility and adoption of AI tools for media literacy.
          </Paragraph>
          
          <Steps current={currentStep} style={{ marginBottom: '32px' }}>
            {researchAlignedSteps.map((step, index) => (
              <Steps.Step key={index} title={step.title} icon={step.icon} />
            ))}
          </Steps>

          <Form form={form} layout="vertical" style={{ minHeight: '500px' }}>
            <div>{researchAlignedSteps[currentStep].content}</div>
          </Form>

          <Divider />

          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <Space>
              {currentStep > 0 && (
                <Button onClick={prev} size="large">
                  Previous
                </Button>
              )}
              {currentStep < researchAlignedSteps.length - 1 && (
                <Button type="primary" onClick={next} size="large">
                  Next
                </Button>
              )}
              {currentStep === researchAlignedSteps.length - 1 && (
                <Button type="primary" onClick={handleSubmit} loading={loading} size="large">
                  Complete Pre-Study Questionnaire
                </Button>
              )}
            </Space>
          </div>

          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Text type="secondary">
              Step {currentStep + 1} of {researchAlignedSteps.length} | Research Questions: RQ1-RQ6
            </Text>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
};

export default ResearchAlignedPreQuestionnaire;