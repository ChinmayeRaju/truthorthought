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
  CheckCircleOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  BulbOutlined,
  RobotOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import apiService from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ResearchAlignedPostQuestionnaire: React.FC = () => {
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
      console.log('Research-aligned post-questionnaire data:', allFormFields);
      
      try {
        await form.validateFields();
        console.log('All fields validated successfully');
      } catch (validationError) {
        console.error('Validation failed for some fields:', validationError);
      }
      
      const values = allFormFields;
      const currentSessionId = sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const questionnaireKey = `research_post_questionnaire_${currentSessionId}`;
      
      let analysisSessionData = null;
      try {
        const storedAnalysisData = localStorage.getItem(`analysis_session_${currentSessionId}`);
        if (storedAnalysisData) {
          analysisSessionData = JSON.parse(storedAnalysisData);
        }
      } catch (error) {
        console.warn('Could not retrieve analysis session data:', error);
      }
      
      const dataToSave = {
        ...values,
        timestamp: new Date().toISOString(),
        type: 'research_post',
        sessionId: currentSessionId,
        ...(analysisSessionData && { analysisSessionData })
      };
      
      // Submit to backend
      const response = await apiService.submitQuestionnaire(dataToSave);
      
      if (response.success) {
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
                questionnaire_type: 'research_post',
                completion_time: new Date().toISOString(),
                total_questions: Object.keys(dataToSave).filter(key => !['timestamp', 'type', 'sessionId', 'analysisSessionData'].includes(key)).length
              }
            })
          });
        } catch (error) {
          console.warn('Failed to log interaction:', error);
        }
        
        message.success('Post-study questionnaire completed and saved! Thank you for your participation.');
        setTimeout(() => {
          navigate('/research-dashboard');
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

  const researchAlignedPostSteps = [
    {
      title: 'AI Accuracy Perception',
      icon: <CheckCircleOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>AI System Accuracy Assessment (RQ1: NLP Accuracy Outcomes)</Title>
          <Paragraph>
            Please evaluate the accuracy and effectiveness of the AI system in distinguishing facts from opinions.
          </Paragraph>
          
          <Form.Item
            name="aiAccuracyPerception"
            label="How accurate do you think the AI system was at distinguishing facts from opinions?"
            rules={[{ required: true, message: 'Please rate the AI accuracy' }]}
          >
            <Slider
              min={1}
              max={5}
              marks={{
                1: 'Very inaccurate',
                2: 'Somewhat inaccurate',
                3: 'Moderately accurate',
                4: 'Very accurate',
                5: 'Extremely accurate'
              }}
              step={1}
              defaultValue={1}
              tooltip={{ formatter: (value) => `${value}/5` }}
            />
          </Form.Item>

          <Form.Item
            name="aiVsHumanAccuracy"
            label="Compared to your own judgment, how would you rate the AI's accuracy?"
            rules={[{ required: true, message: 'Please compare AI vs human accuracy' }]}
          >
            <Radio.Group>
              <Radio value="muchWorse">Much worse than my judgment</Radio>
              <Radio value="worse">Somewhat worse than my judgment</Radio>
              <Radio value="similar">Similar to my judgment</Radio>
              <Radio value="better">Somewhat better than my judgment</Radio>
              <Radio value="muchBetter">Much better than my judgment</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="aiTrustChange"
            label="How has your trust in AI for fact/opinion classification changed after using this system?"
            rules={[{ required: true, message: 'Please indicate trust change' }]}
          >
            <Radio.Group>
              <Radio value="decreasedSignificantly">Decreased significantly</Radio>
              <Radio value="decreasedSlightly">Decreased slightly</Radio>
              <Radio value="noChange">No change</Radio>
              <Radio value="increasedSlightly">Increased slightly</Radio>
              <Radio value="increasedSignificantly">Increased significantly</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="aiClassificationAgreement"
            label="How often did you agree with the AI's fact/opinion classifications?"
            rules={[{ required: true, message: 'Please estimate agreement frequency' }]}
          >
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
          </Form.Item>

          <Form.Item
            name="aiAccuracyExpectationComparison"
            label="How did the AI's actual performance compare to your initial expectations?"
            rules={[{ required: true, message: 'Please compare with expectations' }]}
          >
            <Radio.Group>
              <Radio value="muchWorse">Much worse than expected</Radio>
              <Radio value="worse">Somewhat worse than expected</Radio>
              <Radio value="asExpected">About as expected</Radio>
              <Radio value="better">Somewhat better than expected</Radio>
              <Radio value="muchBetter">Much better than expected</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="aiErrorTypes"
            label="What types of errors did you notice the AI making? (Select all that apply)"
            rules={[{ required: true, message: 'Please select error types or "No errors noticed"' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="factsAsOpinions">Classifying facts as opinions</Checkbox></Col>
                <Col span={12}><Checkbox value="opinionsAsFacts">Classifying opinions as facts</Checkbox></Col>
                <Col span={12}><Checkbox value="contextMissing">Missing context or nuance</Checkbox></Col>
                <Col span={12}><Checkbox value="complexStatements">Struggling with complex statements</Checkbox></Col>
                <Col span={12}><Checkbox value="impliedMeaning">Missing implied meaning</Checkbox></Col>
                <Col span={12}><Checkbox value="culturalContext">Missing cultural context</Checkbox></Col>
                <Col span={12}><Checkbox value="inconsistency">Inconsistent classifications</Checkbox></Col>
                <Col span={12}><Checkbox value="noErrors">No significant errors noticed</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Cognitive Load & Interface',
      icon: <ThunderboltOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Cognitive Load & Interface Effectiveness (RQ2: Interface Strategies)</Title>
          <Paragraph>
            Please assess the mental effort required and the effectiveness of the interface design.
          </Paragraph>
          
          <Form.Item
            name="mentalDemand"
            label="How mentally demanding was it to use the AI-assisted analysis tool?"
            rules={[{ required: true, message: 'Please rate mental demand' }]}
            
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Very low',
                  25: 'Low',
                  50: 'Moderate',
                  75: 'High',
                  100: 'Very high'
                }}
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>

          <Form.Item
            name="effortRequired"
            label="How much effort was required to understand and use the AI classifications?"
            rules={[{ required: true, message: 'Please rate effort required' }]}
            
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Very low',
                  25: 'Low',
                  50: 'Moderate',
                  75: 'High',
                  100: 'Very high'
                }}
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>

          <Form.Item
            name="frustrationLevel"
            label="How frustrated were you while using the AI analysis tool?"
            rules={[{ required: true, message: 'Please rate frustration level' }]}
            
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
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}/100` }}
              />
          </Form.Item>

          <Form.Item
            name="factOpinionClarity"
            label="How clear were fact–opinion distinctions?"
            rules={[{ required: true, message: 'Please rate fact-opinion clarity' }]}
          >
            <Slider
              min={1}
              max={7}
              marks={{
                1: 'Very unclear',
                2: 'Unclear',
                3: 'Somewhat unclear',
                4: 'Neutral',
                5: 'Somewhat clear',
                6: 'Clear',
                7: 'Very clear'
              }}
              step={1}
              defaultValue={4}
              tooltip={{ formatter: (value) => `${value}/7` }}
            />
          </Form.Item>

          <Form.Item
            name="sourceInfluence"
            label="How much did the source labels (BBC, CNN, Guardian) influence your trust in the system?"
            rules={[{ required: true, message: 'Please rate source influence' }]}
          >
            <Slider
              min={1}
              max={5}
              marks={{
                1: 'Not at all',
                2: 'Slightly',
                3: 'Moderately',
                4: 'Considerably',
                5: 'Extremely'
              }}
              step={1}
              defaultValue={3}
              tooltip={{ formatter: (value) => `${value}/5` }}
            />
          </Form.Item>

          <Form.Item
            name="interfaceUsability"
            label="How would you rate the overall usability of the interface?"
            rules={[{ required: true, message: 'Please rate interface usability' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very poor',
                  2: 'Poor',
                  3: 'Average',
                  4: 'Good',
                  5: 'Excellent'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="learningSupport"
            label="How well did the interface support your learning about fact/opinion distinction?"
            rules={[{ required: true, message: 'Please rate learning support' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very poorly',
                  2: 'Poorly',
                  3: 'Adequately',
                  4: 'Well',
                  5: 'Very well'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="cognitiveLoadComparison"
            label="Compared to analyzing news without AI assistance, the mental effort required was:"
            rules={[{ required: true, message: 'Please compare cognitive load' }]}
          >
            <Radio.Group>
              <Radio value="muchLess">Much less effort</Radio>
              <Radio value="somewhatLess">Somewhat less effort</Radio>
              <Radio value="similar">Similar effort</Radio>
              <Radio value="somewhatMore">Somewhat more effort</Radio>
              <Radio value="muchMore">Much more effort</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="interfaceFeatureHelpfulness"
            label="Which interface features were most helpful? (Select all that apply)"
            rules={[{ required: true, message: 'Please select helpful features' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="highlighting">Text highlighting</Checkbox></Col>
                <Col span={12}><Checkbox value="explanations">AI explanations</Checkbox></Col>
                <Col span={12}><Checkbox value="confidence">Confidence scores</Checkbox></Col>
                <Col span={12}><Checkbox value="citations">Source citations</Checkbox></Col>
                <Col span={12}><Checkbox value="categories">Clear categorization</Checkbox></Col>
                <Col span={12}><Checkbox value="navigation">Easy navigation</Checkbox></Col>
                <Col span={12}><Checkbox value="feedback">Immediate feedback</Checkbox></Col>
                <Col span={12}><Checkbox value="summary">Summary views</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Divider>Decision-Making Clarity & Understanding</Divider>

          <Form.Item
            name="decisionMakingConfidence"
            label="How confident were you in forming your own judgment after reading the article?"
            rules={[{ required: true, message: 'Please rate your confidence' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Not confident at all',
                  2: 'Slightly confident',
                  3: 'Somewhat confident',
                  4: 'Moderately confident',
                  5: 'Quite confident',
                  6: 'Very confident',
                  7: 'Extremely confident'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="informationInfluence"
            label="To what extent did the information influence how you evaluated the article?"
            rules={[{ required: true, message: 'Please rate the influence' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'No influence',
                  2: 'Very little influence',
                  3: 'Little influence',
                  4: 'Moderate influence',
                  5: 'Considerable influence',
                  6: 'Strong influence',
                  7: 'Very strong influence'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="claritySemanticDifferential"
            label="Rate the overall clarity of the information presentation:"
            rules={[{ required: true, message: 'Please rate clarity' }]}
            
          >
            <div>
              <Text>Confusing</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Clear</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="factOpinionDistinction"
            label="How clearly could you distinguish between facts and opinions in the article?"
            rules={[{ required: true, message: 'Please rate distinction clarity' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Not clear at all',
                  2: 'Slightly clear',
                  3: 'Somewhat clear',
                  4: 'Moderately clear',
                  5: 'Quite clear',
                  6: 'Very clear',
                  7: 'Extremely clear'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="objectiveSubjectiveUnderstanding"
            label="How easy was it to understand what information was objective versus subjective?"
            rules={[{ required: true, message: 'Please rate understanding ease' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Very difficult',
                  2: 'Difficult',
                  3: 'Somewhat difficult',
                  4: 'Neither easy nor difficult',
                  5: 'Somewhat easy',
                  6: 'Easy',
                  7: 'Very easy'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Divider>Efficiency & Cognitive Load Assessment</Divider>

          <Form.Item
            name="evaluationSpeed"
            label="It was quick to evaluate the article using this approach."
            rules={[{ required: true, message: 'Please rate agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="effortRequiredSanitized"
            label="The process required less effort than I expected."
            rules={[{ required: true, message: 'Please rate agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="judgmentSpeed"
            label="I could reach a judgment without spending too much time."
            rules={[{ required: true, message: 'Please rate agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="focusEfficiency"
            label="I was able to focus on what mattered without unnecessary reading."
            rules={[{ required: true, message: 'Please rate agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="timeSemanticDifferential"
            label="Rate the time required for the evaluation process:"
            rules={[{ required: true, message: 'Please rate time requirement' }]}
            
          >
            <div>
              <Text>Time-consuming</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Quick</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="effortSemanticDifferential"
            label="Rate the effort required for the evaluation process:"
            rules={[{ required: true, message: 'Please rate effort' }]}
            
          >
            <div>
              <Text>Effortful</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Effortless</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="judgmentSpeedSemanticDifferential"
            label="Rate the speed of reaching judgment:"
            rules={[{ required: true, message: 'Please rate judgment speed' }]}
            
          >
            <div>
              <Text>Slow to reach judgment</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Fast to reach judgment</Text>
            </div>
          </Form.Item>

          <Divider>Perception of Balance</Divider>

          <Form.Item
            name="informationBalance"
            label="How balanced did you find the information presented in the article?"
            rules={[{ required: true, message: 'Please rate balance perception' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Very unbalanced',
                  2: 'Unbalanced',
                  3: 'Somewhat unbalanced',
                  4: 'Neither balanced nor unbalanced',
                  5: 'Somewhat balanced',
                  6: 'Balanced',
                  7: 'Very balanced'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="perspectiveAwareness"
            label="To what extent did the article make you aware of different perspectives?"
            rules={[{ required: true, message: 'Please rate perspective awareness' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Not at all',
                  2: 'Very little',
                  3: 'Little',
                  4: 'Moderate extent',
                  5: 'Considerable extent',
                  6: 'Great extent',
                  7: 'Very great extent'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Skill Development & Learning',
      icon: <BulbOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Bias Detection Improvement & Learning Transfer (RQ3: Skill Development)</Title>
          <Paragraph>
            Please assess how the AI assistance affected your bias detection skills and learning.
          </Paragraph>
          
          <Form.Item
            name="biasDetectionConfidenceChange"
            label="How has your confidence in detecting bias changed after using the AI tool?"
            rules={[{ required: true, message: 'Please indicate confidence change' }]}
          >
            <Radio.Group>
              <Radio value="decreasedSignificantly">Decreased significantly</Radio>
              <Radio value="decreasedSlightly">Decreased slightly</Radio>
              <Radio value="noChange">No change</Radio>
              <Radio value="increasedSlightly">Increased slightly</Radio>
              <Radio value="increasedSignificantly">Increased significantly</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="skillDevelopmentPerception"
            label="Do you feel your fact/opinion analysis skills improved through using the AI tool?"
            rules={[{ required: true, message: 'Please assess skill development' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'No improvement',
                  2: 'Slight improvement',
                  3: 'Moderate improvement',
                  4: 'Significant improvement',
                  5: 'Major improvement'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="learningMechanisms"
            label="How did the AI tool help you learn? (Select all that apply)"
            rules={[{ required: true, message: 'Please select learning mechanisms' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="examples">Provided good examples</Checkbox></Col>
                <Col span={12}><Checkbox value="explanations">Clear explanations of decisions</Checkbox></Col>
                <Col span={12}><Checkbox value="patterns">Helped identify patterns</Checkbox></Col>
                <Col span={12}><Checkbox value="mistakes">Showed me my mistakes</Checkbox></Col>
                <Col span={12}><Checkbox value="consistency">Demonstrated consistent criteria</Checkbox></Col>
                <Col span={12}><Checkbox value="feedback">Immediate feedback on judgments</Checkbox></Col>
                <Col span={12}><Checkbox value="practice">Provided practice opportunities</Checkbox></Col>
                <Col span={12}><Checkbox value="confidence">Built my confidence</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="skillTransferConfidence"
            label="How confident are you that you could apply what you learned to analyze news without AI assistance?"
            rules={[{ required: true, message: 'Please rate transfer confidence' }]}
            
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

          <Form.Item
            name="independentAnalysisImprovement"
            label="Do you think your ability to independently analyze news for bias has improved?"
            rules={[{ required: true, message: 'Please assess independent analysis improvement' }]}
          >
            <Radio.Group>
              <Radio value="significantlyWorse">Significantly worse</Radio>
              <Radio value="slightlyWorse">Slightly worse</Radio>
              <Radio value="noChange">No change</Radio>
              <Radio value="slightlyBetter">Slightly better</Radio>
              <Radio value="significantlyBetter">Significantly better</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="newSkillsLearned"
            label="What new skills or insights did you gain from using the AI tool?"
            rules={[{ required: true, message: 'Please describe new skills learned' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Describe any new approaches, techniques, or insights you gained about analyzing news content for facts, opinions, and bias..."
            />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Behavioral Changes & Comparison',
      icon: <BarChartOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Behavioral Changes & Traditional vs AI Methods (RQ4: Behavioral Impact)</Title>
          <Paragraph>
            Please reflect on how the AI tool changed your approach compared to traditional media literacy methods.
          </Paragraph>
          
          <Form.Item
            name="approachChange"
            label="How has your approach to analyzing news content changed after using the AI tool?"
            rules={[{ required: true, message: 'Please describe approach changes' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Describe how your method of evaluating news articles for facts, opinions, and bias has changed..."
            />
          </Form.Item>

          <Form.Item
            name="aiVsTraditionalPreference"
            label="Comparing AI assistance to traditional media literacy methods, which do you prefer?"
            rules={[{ required: true, message: 'Please indicate your preference' }]}
          >
            <Radio.Group>
              <Radio value="stronglyTraditional">Strongly prefer traditional methods</Radio>
              <Radio value="somewhatTraditional">Somewhat prefer traditional methods</Radio>
              <Radio value="noPreference">No strong preference</Radio>
              <Radio value="somewhatAI">Somewhat prefer AI assistance</Radio>
              <Radio value="stronglyAI">Strongly prefer AI assistance</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="effectivenessComparison"
            label="How effective was AI assistance compared to traditional methods you've used?"
            rules={[{ required: true, message: 'Please compare effectiveness' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Much less effective',
                  2: 'Less effective',
                  3: 'Similarly effective',
                  4: 'More effective',
                  5: 'Much more effective'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="behavioralChanges"
            label="What specific changes in your news consumption behavior do you anticipate? (Select all that apply)"
            rules={[{ required: true, message: 'Please select anticipated changes' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="moreCarefulAnalysis">More careful analysis of articles</Checkbox></Col>
                <Col span={12}><Checkbox value="seekMultipleSources">Seek multiple sources more often</Checkbox></Col>
                <Col span={12}><Checkbox value="questionAssumptions">Question my assumptions more</Checkbox></Col>
                <Col span={12}><Checkbox value="lookForBias">Actively look for bias indicators</Checkbox></Col>
                <Col span={12}><Checkbox value="checkCredibility">Check source credibility more often</Checkbox></Col>
                <Col span={12}><Checkbox value="slowDown">Take more time before forming opinions</Checkbox></Col>
                <Col span={12}><Checkbox value="useAITools">Seek out AI analysis tools</Checkbox></Col>
                <Col span={12}><Checkbox value="noChanges">No anticipated changes</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="traditionalMethodsStillUseful"
            label="Which traditional media literacy methods do you still find most valuable?"
            rules={[{ required: true, message: 'Please select valuable traditional methods' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="sourceChecking">Source credibility checking</Checkbox></Col>
                <Col span={12}><Checkbox value="crossReferencing">Cross-referencing multiple sources</Checkbox></Col>
                <Col span={12}><Checkbox value="factChecking">Using fact-checking websites</Checkbox></Col>
                <Col span={12}><Checkbox value="authorResearch">Researching author credentials</Checkbox></Col>
                <Col span={12}><Checkbox value="dateChecking">Checking publication dates</Checkbox></Col>
                <Col span={12}><Checkbox value="languageAnalysis">Analyzing language and tone</Checkbox></Col>
                <Col span={12}><Checkbox value="evidenceEvaluation">Evaluating supporting evidence</Checkbox></Col>
                <Col span={12}><Checkbox value="contextSeeking">Seeking broader context</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'Automation Balance Preferences',
      icon: <RobotOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Optimal Automation Balance (RQ5: Human-AI Balance)</Title>
          <Paragraph>
            Please indicate your preferences for the optimal balance between AI automation and human judgment.
          </Paragraph>
          
          <Form.Item
            name="optimalAutomationLevel"
            label="What level of AI automation do you think is optimal for news analysis?"
            rules={[{ required: true, message: 'Please select optimal automation level' }]}
          >
            <Radio.Group>
              <Radio value="minimal">Minimal - AI provides basic suggestions only</Radio>
              <Radio value="moderate">Moderate - AI analyzes but human reviews all decisions</Radio>
              <Radio value="balanced">Balanced - AI handles routine cases, human handles complex ones</Radio>
              <Radio value="high">High - AI makes most decisions with human oversight</Radio>
              <Radio value="maximum">Maximum - AI handles everything with minimal human input</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="trustBalancePreference"
            label="What balance of trust between AI and human judgment feels most comfortable?"
            rules={[{ required: true, message: 'Please indicate trust balance preference' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Rely entirely on human judgment',
                  2: 'Mostly human, some AI input',
                  3: 'Equal balance',
                  4: 'Mostly AI, some human oversight',
                  5: 'Rely entirely on AI judgment'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="controlSatisfaction"
            label="How satisfied were you with the level of control you had over the AI's decisions?"
            rules={[{ required: true, message: 'Please rate control satisfaction' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very dissatisfied',
                  2: 'Dissatisfied',
                  3: 'Neutral',
                  4: 'Satisfied',
                  5: 'Very satisfied'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="automationImprovements"
            label="How could the balance between automation and human control be improved?"
            rules={[{ required: true, message: 'Please suggest improvements' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="Describe how the system could better balance AI automation with human judgment and control..."
            />
          </Form.Item>

          <Form.Item
            name="overrideFrequency"
            label="How often did you feel the need to override or disagree with the AI's classifications?"
            rules={[{ required: true, message: 'Please estimate override frequency' }]}
            
          >
            <Slider
                min={0}
                max={100}
                marks={{
                  0: 'Never',
                  25: 'Rarely',
                  50: 'Sometimes',
                  75: 'Often',
                  100: 'Always'
                }}
                step={5}
                defaultValue={0}
                tooltip={{ formatter: (value) => `${value}%` }}
              />
          </Form.Item>

          <Form.Item
            name="agencyFeeling"
            label="How much did you feel like you maintained agency and decision-making power while using the AI tool?"
            rules={[{ required: true, message: 'Please rate sense of agency' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'No agency',
                  2: 'Little agency',
                  3: 'Moderate agency',
                  4: 'Strong agency',
                  5: 'Complete agency'
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
      title: 'Adoption & Individual Factors',
      icon: <TrophyOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Technology Adoption & Individual Differences (RQ6: Adoption Factors)</Title>
          <Paragraph>
            Please assess your likelihood of adopting this technology and factors that influenced your experience.
          </Paragraph>
          
          <Form.Item
            name="agencyAndInfluence"
            label="To what extent did you experience agency and influence over the automated classification and analytical processes during your interaction with the system?"
            rules={[{ required: true, message: 'Please rate your sense of agency' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'No agency or influence',
                  2: 'Limited agency',
                  3: 'Moderate agency',
                  4: 'Substantial agency',
                  5: 'Complete agency and control'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="citationEffectiveness"
            label="How effectively did the provided citations, source attributions, and reference materials enhance your comprehension of the system's classification logic and analytical reasoning?"
            rules={[{ required: true, message: 'Please rate citation effectiveness' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not effective at all',
                  2: 'Slightly effective',
                  3: 'Moderately effective',
                  4: 'Very effective',
                  5: 'Extremely effective'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="mostValuableInterfaceElement"
            label="Which interface element or analytical feature provided the greatest value in supporting your news analysis workflow and decision-making process?"
            rules={[{ required: true, message: 'Please select the most valuable feature' }]}
          >
            <Radio.Group>
              <Radio value="credibilityIndicators">Source credibility indicators and outlet reputation scoring</Radio>
              <Radio value="stakeholderMapping">Key stakeholder identification and relevance mapping</Radio>
              <Radio value="citationNetworks">Citation networks and reference validation systems</Radio>
              <Radio value="contentHighlighting">Content highlighting for bias indicators and factual claims</Radio>
              <Radio value="other">Alternative features not listed above</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="comprehensiveCoverage"
            label="Rate your confidence that you encountered all critical factual information, key stakeholder perspectives, and relevant context necessary for comprehensive understanding of the article's subject matter"
            rules={[{ required: true, message: 'Please rate comprehensiveness' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Completely missed important elements',
                  2: 'Missed some important elements',
                  3: 'Adequate coverage',
                  4: 'Good coverage',
                  5: 'Fully comprehensive coverage'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="timeEfficiencyImprovement"
            label="Did the automated analysis system demonstrably reduce the time required for thorough news comprehension compared to traditional sequential reading and manual fact-checking methods?"
            rules={[{ required: true, message: 'Please assess time efficiency' }]}
          >
            <Radio.Group>
              <Radio value="significantlyReduced">Significantly reduced time required</Radio>
              <Radio value="moderatelyReduced">Moderately reduced time required</Radio>
              <Radio value="slightlyReduced">Slightly reduced time required</Radio>
              <Radio value="noChange">No change in time required</Radio>
              <Radio value="increased">Actually increased time required</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="emotionalBurdenReduction"
            label="Did the structured separation of factual content from opinion-based commentary reduce the emotional burden and psychological stress typically associated with news consumption?"
            rules={[{ required: true, message: 'Please assess emotional impact' }]}
          >
            <Radio.Group>
              <Radio value="significantlyReduced">Significantly reduced emotional burden</Radio>
              <Radio value="moderatelyReduced">Moderately reduced emotional burden</Radio>
              <Radio value="slightlyReduced">Slightly reduced emotional burden</Radio>
              <Radio value="noChange">No change in emotional burden</Radio>
              <Radio value="increased">Actually increased emotional burden</Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="systematicBiasDetection"
            label="Did you detect systematic bias, editorial slant, or ideological positioning in the analyzed content? Describe the specific manifestations, techniques, or patterns through which this bias was expressed."
            rules={[{ required: true, message: 'Please describe any bias detected' }]}
          >
            <TextArea
              rows={4}
              placeholder="Describe any systematic bias, editorial slant, or ideological positioning you detected, including specific techniques or patterns. If no bias was detected, please state 'No systematic bias detected'..."
            />
          </Form.Item>

          <Form.Item
            name="continuedUseIntention"
            label="How likely are you to continue using AI-assisted news analysis tools in the future?"
            rules={[{ required: true, message: 'Please rate likelihood of continued use' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very unlikely',
                  2: 'Unlikely',
                  3: 'Neutral',
                  4: 'Likely',
                  5: 'Very likely'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="perceivedUtility"
            label="How useful do you find AI assistance for news analysis?"
            rules={[{ required: true, message: 'Please rate perceived utility' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Not useful',
                  2: 'Slightly useful',
                  3: 'Moderately useful',
                  4: 'Very useful',
                  5: 'Extremely useful'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="recommendationLikelihood"
            label="How likely are you to recommend this AI tool to others?"
            rules={[{ required: true, message: 'Please rate recommendation likelihood' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very unlikely',
                  2: 'Unlikely',
                  3: 'Neutral',
                  4: 'Likely',
                  5: 'Very likely'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="individualFactorsInfluence"
            label="Which of your personal characteristics do you think most influenced your experience with the AI tool? (Select all that apply)"
            rules={[{ required: true, message: 'Please select influential personal factors' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="techComfort">Technology comfort level</Checkbox></Col>
                <Col span={12}><Checkbox value="education">Educational background</Checkbox></Col>
                <Col span={12}><Checkbox value="age">Age</Checkbox></Col>
                <Col span={12}><Checkbox value="profession">Professional background</Checkbox></Col>
                <Col span={12}><Checkbox value="learningStyle">Learning style preferences</Checkbox></Col>
                <Col span={12}><Checkbox value="cognitiveStyle">Cognitive decision-making style</Checkbox></Col>
                <Col span={12}><Checkbox value="newsExperience">Previous news analysis experience</Checkbox></Col>
                <Col span={12}><Checkbox value="aiExperience">Previous AI tool experience</Checkbox></Col>
                <Col span={12}><Checkbox value="personalInterests">Personal interests and expertise</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="adoptionBarriers"
            label="What would prevent you from using AI news analysis tools in the future? (Select all that apply)"
            rules={[{ required: true, message: 'Please select barriers or "No barriers"' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={12}><Checkbox value="accuracy">Concerns about accuracy</Checkbox></Col>
                <Col span={12}><Checkbox value="cost">Cost considerations</Checkbox></Col>
                <Col span={12}><Checkbox value="complexity">Too complex to use</Checkbox></Col>
                <Col span={12}><Checkbox value="trust">Lack of trust in AI</Checkbox></Col>
                <Col span={12}><Checkbox value="privacy">Privacy concerns</Checkbox></Col>
                <Col span={12}><Checkbox value="skillLoss">Fear of losing critical thinking skills</Checkbox></Col>
                <Col span={12}><Checkbox value="availability">Limited availability</Checkbox></Col>
                <Col span={12}><Checkbox value="noBarriers">No significant barriers</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Divider>Technology Adoption Assessment (TAM)</Divider>

          <Form.Item
            name="futureUseConsideration"
            label="I would consider using this tool in the future."
            rules={[{ required: true, message: 'Please rate your agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="likelyToUse"
            label="If this tool were available, I would likely use it."
            rules={[{ required: true, message: 'Please rate your agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="recommendToOthers"
            label="I would recommend this tool to others who read similar articles."
            rules={[{ required: true, message: 'Please rate your agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="toolUsefulness"
            label="Using this tool would be useful for me."
            rules={[{ required: true, message: 'Please rate your agreement' }]}
            
          >
            <Slider
                min={1}
                max={7}
                marks={{
                  1: 'Strongly disagree',
                  2: 'Disagree',
                  3: 'Somewhat disagree',
                  4: 'Neither agree nor disagree',
                  5: 'Somewhat agree',
                  6: 'Agree',
                  7: 'Strongly agree'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/7` }}
              />
          </Form.Item>

          <Form.Item
            name="useLikelihoodSemanticDifferential"
            label="Rate your likelihood of using this tool:"
            rules={[{ required: true, message: 'Please rate use likelihood' }]}
            
          >
            <div>
              <Text>Unlikely to use</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Likely to use</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="interestSemanticDifferential"
            label="Rate your interest in this tool:"
            rules={[{ required: true, message: 'Please rate interest level' }]}
            
          >
            <div>
              <Text>Not interested</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Very interested</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="recommendationSemanticDifferential"
            label="Rate your likelihood of recommending this tool:"
            rules={[{ required: true, message: 'Please rate recommendation likelihood' }]}
            
          >
            <div>
              <Text>Would not recommend</Text>
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
                style={{ margin: '0 16px' }}
              />
              <Text>Would strongly recommend</Text>
            </div>
          </Form.Item>

          <Form.Item
            name="overallSatisfaction"
            label="Overall, how satisfied were you with your experience using the AI news analysis tool?"
            rules={[{ required: true, message: 'Please rate overall satisfaction' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very dissatisfied',
                  2: 'Dissatisfied',
                  3: 'Neutral',
                  4: 'Satisfied',
                  5: 'Very satisfied'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="finalComments"
            label="Any final comments about your experience with the AI news analysis tool?"
          >
            <TextArea
              rows={4}
              placeholder="Optional: Share any additional thoughts, suggestions for improvement, or reflections on your experience..."
            />
          </Form.Item>
        </Space>
      ),
    },
    {
      title: 'AI Feature Evaluation',
      icon: <EyeOutlined />,
      content: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Title level={4}>Most Relevant Personnel & Impactful Quotes Assessment</Title>
          <Paragraph>
            Please evaluate the AI-generated "Most Relevant Personnel" and "Most Impactful Quotes" features that were displayed with the news article.
          </Paragraph>
          
          <Form.Item
            name="personnelRelevanceAccuracy"
            label="How accurately did the AI identify the most relevant personnel in the article?"
            rules={[{ required: true, message: 'Please rate personnel identification accuracy' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very inaccurate',
                  2: 'Inaccurate',
                  3: 'Somewhat accurate',
                  4: 'Accurate',
                  5: 'Very accurate'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="personnelHelpfulness"
            label="How helpful was the 'Most Relevant Personnel' section for understanding the article?"
            rules={[{ required: true, message: 'Please rate personnel section helpfulness' }]}
            
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

          <Form.Item
            name="quotesRelevanceAccuracy"
            label="How accurately did the AI identify the most impactful quotes from the article?"
            rules={[{ required: true, message: 'Please rate quote identification accuracy' }]}
            
          >
            <Slider
                min={1}
                max={5}
                marks={{
                  1: 'Very inaccurate',
                  2: 'Inaccurate',
                  3: 'Somewhat accurate',
                  4: 'Accurate',
                  5: 'Very accurate'
                }}
                step={1}
                defaultValue={1}
                tooltip={{ formatter: (value) => `${value}/5` }}
              />
          </Form.Item>

          <Form.Item
            name="quotesHelpfulness"
            label="How helpful was the 'Most Impactful Quotes' section for understanding key messages?"
            rules={[{ required: true, message: 'Please rate quotes section helpfulness' }]}
            
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

          <Form.Item
            name="featureUsagePreference"
            label="Which of these AI-generated features would you most want to see in future news analysis tools?"
            rules={[{ required: true, message: 'Please select your preferences' }]}
          >
            <Checkbox.Group>
              <Row>
                <Col span={24}><Checkbox value="relevantPersonnel">Most Relevant Personnel identification</Checkbox></Col>
                <Col span={24}><Checkbox value="impactfulQuotes">Most Impactful Quotes extraction</Checkbox></Col>
                <Col span={24}><Checkbox value="factOpinionClassification">Fact/Opinion classification</Checkbox></Col>
                <Col span={24}><Checkbox value="biasDetection">Bias detection and analysis</Checkbox></Col>
                <Col span={24}><Checkbox value="sourceCredibility">Source credibility assessment</Checkbox></Col>
                <Col span={24}><Checkbox value="contextualInformation">Additional contextual information</Checkbox></Col>
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="featureImprovementSuggestions"
            label="How could the 'Most Relevant Personnel' and 'Most Impactful Quotes' features be improved?"
          >
            <TextArea
              rows={3}
              placeholder="Optional: Suggest improvements for better personnel identification and quote selection..."
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
            Research Post-Study Questionnaire
          </Title>
          <Paragraph style={{ textAlign: 'center', marginBottom: '32px', color: '#666' }}>
            This questionnaire measures the outcomes and changes resulting from your use of the AI news analysis tool. 
            Your responses help us understand the effectiveness of AI assistance across all our research questions.
          </Paragraph>
          
          <Steps current={currentStep} style={{ marginBottom: '32px' }}>
            {researchAlignedPostSteps.map((step, index) => (
              <Steps.Step key={index} title={step.title} icon={step.icon} />
            ))}
          </Steps>

          <Form form={form} layout="vertical" style={{ minHeight: '500px' }}>
            <div>{researchAlignedPostSteps[currentStep].content}</div>
          </Form>

          <Divider />

          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <Space>
              {currentStep > 0 && (
                <Button onClick={prev} size="large">
                  Previous
                </Button>
              )}
              {currentStep < researchAlignedPostSteps.length - 1 && (
                <Button type="primary" onClick={next} size="large">
                  Next
                </Button>
              )}
              {currentStep === researchAlignedPostSteps.length - 1 && (
                <Button type="primary" onClick={handleSubmit} loading={loading} size="large">
                  Complete Post-Study Questionnaire
                </Button>
              )}
            </Space>
          </div>

          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Text type="secondary">
              Step {currentStep + 1} of {researchAlignedPostSteps.length} | Research Questions: RQ1-RQ6
            </Text>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
};

export default ResearchAlignedPostQuestionnaire;