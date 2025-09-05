import React, { useState } from 'react';
import { Form, Radio, Input, Slider, Button, Card, Typography, Space, message, Divider } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import type { ExitQuestionnaireData } from '../types';
import AppLayout from '../components/AppLayout';
import apiService from '../services/api';

const { Title, Text } = Typography;
const { TextArea } = Input;

const ExitQuestionnaire: React.FC = () => {
  const [form] = Form.useForm();
  const [submitted, setSubmitted] = useState(false);
  const [showBiasDescription, setShowBiasDescription] = useState(false);
  const [showPersonnelDescription, setShowPersonnelDescription] = useState(false);

  const taskOptions = [
    { label: 'Task 1', value: 'task1' },
    { label: 'Task 2', value: 'task2' },
    { label: 'Both equal', value: 'equal' }
  ];

  const biasOptions = [
    { label: 'Task 1', value: 'task1' },
    { label: 'Task 2', value: 'task2' },
    { label: 'No difference', value: 'no_difference' }
  ];

  const personnelInfluenceOptions = [
    { label: 'Task 1', value: 'task1' },
    { label: 'Task 2', value: 'task2' },
    { label: 'No difference', value: 'no_difference' }
  ];

  const handleBiasChange = (e: any) => {
    const value = e.target.value;
    setShowBiasDescription(value === 'task1' || value === 'task2');
  };

  const handlePersonnelInfluenceChange = (e: any) => {
    const value = e.target.value;
    setShowPersonnelDescription(value === 'task1' || value === 'task2');
  };

  const onFinish = async (values: any) => {
    try {
      const sessionId = `exit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const exitData: ExitQuestionnaireData = {
        ...values,
        sessionId,
        timestamp: new Date().toISOString(),
        type: 'exit'
      };

      console.log('Exit questionnaire data:', exitData);
      
      // Submit to backend
      const response = await apiService.submitQuestionnaire(exitData);
      
      if (response.success) {
        const existingData = JSON.parse(localStorage.getItem('exitQuestionnaires') || '[]');
        existingData.push(exitData);
        localStorage.setItem('exitQuestionnaires', JSON.stringify(existingData));

        try {
          await fetch('/api/log_interaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: exitData.sessionId,
              type: 'questionnaire_completion',
              data: {
                questionnaire_type: 'exit',
                completion_time: new Date().toISOString(),
                total_questions: Object.keys(exitData).length
              }
            })
          });
        } catch (error) {
          console.warn('Failed to log interaction:', error);
        }

        console.log('Exit questionnaire submitted successfully:', exitData);
        
        setSubmitted(true);
        message.success('Exit questionnaire submitted and saved successfully!');
      } else {
        throw new Error(response.message || 'Failed to save questionnaire data');
      }
    } catch (error) {
      console.error('Error submitting exit questionnaire:', error);
      message.error('Failed to submit questionnaire. Please try again.');
    }
  };

  if (submitted) {
    return (
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 20px' }}>
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <CheckCircleOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '20px' }} />
            <Title level={2}>Thank You!</Title>
            <Text style={{ fontSize: '16px', color: '#666' }}>
              Your exit questionnaire has been submitted successfully. Thank you for participating in our research study!
            </Text>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '20px' }}>
      <Card>
        <Title level={2} style={{ textAlign: 'center', marginBottom: '30px' }}>
          Exit Questionnaire - Comparing Task 1 vs Task 2
        </Title>
        
        <Text style={{ display: 'block', marginBottom: '30px', fontSize: '16px', color: '#666' }}>
          Please compare your experience between Task 1 and Task 2. Your responses will help us understand 
          the effectiveness of different approaches to fact-opinion analysis.
        </Text>

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          size="large"
        >
          {/* Question 1: Which task felt easier overall? */}
          <Form.Item
            name="easierTask"
            label="1. Which task felt easier overall?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 2: Which task helped you understand the content better? */}
          <Form.Item
            name="betterUnderstanding"
            label="2. Which task helped you understand the content better?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 3: In which task did you feel more in control of your own judgment? */}
          <Form.Item
            name="moreControl"
            label="3. In which task did you feel more in control of your own judgment?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 4: Which task saved you more time? */}
          <Form.Item
            name="timeSaving"
            label="4. Which task saved you more time?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 5: Which task felt less mentally demanding? */}
          <Form.Item
            name="lessMentalDemand"
            label="5. Which task felt less mentally demanding?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 6: Which task made you trust the fact–opinion distinction more? */}
          <Form.Item
            name="moreTrust"
            label="6. Which task made you trust the fact–opinion distinction more?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 7: Did you notice more bias in one task compared to the other? */}
          <Form.Item
            name="biasNoticed"
            label="7. Did you notice more bias in one task compared to the other?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group 
              options={biasOptions} 
              onChange={handleBiasChange}
            />
          </Form.Item>

          {showBiasDescription && (
            <Form.Item
              name="biasDescription"
              label="Please describe the difference in bias you noticed:"
              rules={[{ required: true, message: 'Please describe the bias difference' }]}
            >
              <TextArea rows={3} placeholder="Describe the bias difference you observed..." />
            </Form.Item>
          )}

          {/* Question 8: Were you influenced by key personnel names? */}
          <Form.Item
            name="personnelInfluence"
            label="8. Were you influenced by key personnel names (reporters, experts, political figures) in forming your judgments in either task?"
            rules={[{ required: true, message: 'Please rate your level of influence' }]}
          >
            <Radio.Group>
              <Space direction="vertical">
                <Radio value={1}>1 - Not at all</Radio>
                <Radio value={2}>2 - Slightly</Radio>
                <Radio value={3}>3 - Moderately</Radio>
                <Radio value={4}>4 - Considerably</Radio>
                <Radio value={5}>5 - Extremely</Radio>
              </Space>
            </Radio.Group>
          </Form.Item>

          {/* Question 9: Did that influence differ between tasks? */}
          <Form.Item
            name="personnelInfluenceDifference"
            label="9. If yes, did that influence differ between Task 1 and Task 2?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group 
              options={personnelInfluenceOptions}
              onChange={handlePersonnelInfluenceChange}
            />
          </Form.Item>

          {showPersonnelDescription && (
            <Form.Item
              name="personnelInfluenceDescription"
              label="Please describe how the personnel influence differed between tasks:"
              rules={[{ required: true, message: 'Please describe the personnel influence difference' }]}
            >
              <TextArea rows={3} placeholder="Describe how personnel influence differed between tasks..." />
            </Form.Item>
          )}

          {/* Question 10: Overall preference for future use */}
          <Form.Item
            name="futurePreference"
            label="10. Overall, which task would you prefer to use in the future?"
            rules={[{ required: true, message: 'Please select an option' }]}
          >
            <Radio.Group options={taskOptions} />
          </Form.Item>

          {/* Question 11: Additional comments */}
          <Form.Item
            name="additionalComments"
            label="11. Any other comments or suggestions?"
          >
            <TextArea 
              rows={4} 
              placeholder="Please share any additional thoughts, suggestions, or feedback about your experience..."
            />
          </Form.Item>

          <Divider />

          <Form.Item style={{ textAlign: 'center', marginTop: '30px' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              size="large"
              style={{ minWidth: '200px' }}
            >
              Submit Exit Questionnaire
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

const ExitQuestionnaireWithLayout: React.FC = () => {
  return (
    <AppLayout>
      <ExitQuestionnaire />
    </AppLayout>
  );
};

export default ExitQuestionnaireWithLayout;