import React, { useState, useEffect } from 'react';
import { Input, Button, List, Typography, Space, message, Card, Tag, Divider } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined, BulbOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';

const { Text, Paragraph } = Typography;

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  suggestedQuestions?: string[];
  contextInfo?: {
    facts_count: number;
    opinions_count: number;
    domain: string;
    has_verified_sources: boolean;
  };
}

interface ChatComponentProps {
  sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState<string[]>([]);
  const [contextInfo, setContextInfo] = useState<any>(null);

  // Initialize with welcome message and suggestions
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      text: `Hello! I'm your intelligent analysis assistant. I can help you understand the content, identify key facts and opinions, analyze sources, detect potential biases, and answer questions about the article's themes and implications.

What would you like to know about this analysis?`,
      sender: 'assistant',
      timestamp: new Date(),
      suggestedQuestions: [
        'What are the main facts in this article?',
        'Can you summarize the key points?',
        'What sources support the claims made?',
        'Are there any potential biases in this content?'
      ]
    };
    
    setMessages([welcomeMessage]);
    setCurrentSuggestions(welcomeMessage.suggestedQuestions || []);
  }, []);

  const handleSendMessage = async (questionText?: string) => {
    const question = questionText || inputValue.trim();
    if (!question) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: question,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);
    setCurrentSuggestions([]);

    try {
      const response = await apiService.chat(sessionId, question);
      if (response.success) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.answer,
          sender: 'assistant',
          timestamp: new Date(),
          suggestedQuestions: response.suggested_questions || [],
          contextInfo: response.context_info
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        setCurrentSuggestions(response.suggested_questions || []);
        setContextInfo(response.context_info);
      } else {
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.error || 'I apologize, but I encountered an issue processing your question. Please try rephrasing your question.',
          sender: 'assistant',
          timestamp: new Date(),
          suggestedQuestions: response.suggested_questions || [
            'What are the main facts in this article?',
            'Can you summarize the key points?',
            'What sources support the claims made?'
          ]
        };
        setMessages(prev => [...prev, errorMessage]);
        setCurrentSuggestions(errorMessage.suggestedQuestions || []);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'I apologize, but I encountered a network error. Please check your connection and try again.',
        sender: 'assistant',
        timestamp: new Date(),
        suggestedQuestions: [
          'What are the main facts in this article?',
          'Can you summarize the key points?'
        ]
      };
      setMessages(prev => [...prev, errorMessage]);
      setCurrentSuggestions(errorMessage.suggestedQuestions || []);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  return (
    <div style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
      {/* Context Info Bar */}
      {contextInfo && (
        <Card size="small" style={{ marginBottom: 12, backgroundColor: '#f8f9fa' }}>
          <Space wrap>
            <Tag color="blue" icon={<CheckCircleOutlined />}>
              {contextInfo.facts_count} Facts
            </Tag>
            <Tag color="orange" icon={<ExclamationCircleOutlined />}>
              {contextInfo.opinions_count} Opinions
            </Tag>
            <Tag color="green">
              Domain: {contextInfo.domain}
            </Tag>
            {contextInfo.has_verified_sources && (
              <Tag color="cyan" icon={<CheckCircleOutlined />}>
                Verified Sources
              </Tag>
            )}
          </Space>
        </Card>
      )}

      {/* Messages Area */}
      <div style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
        <List
          dataSource={messages}
          renderItem={(message) => (
            <List.Item style={{ padding: '12px 0', border: 'none' }}>
              <div
                style={{
                  width: '100%',
                  display: 'flex',
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: '85%',
                    padding: '16px 20px',
                    borderRadius: 16,
                    background: message.sender === 'user' ? '#1890ff' : '#ffffff',
                    color: message.sender === 'user' ? 'white' : 'black',
                    border: message.sender === 'assistant' ? '1px solid #e8e8e8' : 'none',
                    boxShadow: message.sender === 'assistant' ? '0 2px 8px rgba(0,0,0,0.1)' : 'none',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                    <div style={{
                      fontSize: 18,
                      marginTop: 2,
                      color: message.sender === 'user' ? 'white' : '#1890ff'
                    }}>
                      {message.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <Paragraph
                        style={{
                          margin: 0,
                          color: message.sender === 'user' ? 'white' : 'black',
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.6
                        }}
                      >
                        {message.text}
                      </Paragraph>
                      
                      {/* Show timestamp for assistant messages */}
                      {message.sender === 'assistant' && (
                        <Text
                          type="secondary"
                          style={{
                            fontSize: 11,
                            marginTop: 8,
                            display: 'block'
                          }}
                        >
                          {message.timestamp.toLocaleTimeString()}
                        </Text>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </List.Item>
          )}
        />
      </div>

      {currentSuggestions.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BulbOutlined style={{ color: '#faad14' }} />
            <Text strong style={{ fontSize: 12, color: '#666' }}>
              Suggested questions:
            </Text>
          </div>
          <Space wrap size={[8, 8]}>
            {currentSuggestions.map((suggestion, index) => (
              <Button
                key={index}
                size="small"
                type="default"
                onClick={() => handleSuggestionClick(suggestion)}
                style={{
                  borderRadius: 16,
                  fontSize: 12,
                  height: 'auto',
                  padding: '6px 12px',
                  border: '1px solid #d9d9d9',
                  backgroundColor: '#fafafa'
                }}
                disabled={loading}
              >
                {suggestion}
              </Button>
            ))}
          </Space>
          <Divider style={{ margin: '12px 0' }} />
        </div>
      )}
      
      <div style={{ display: 'flex', gap: 12 }}>
        <Input.TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about facts, opinions, sources, biases, themes, or any aspect of the analysis..."
          autoSize={{ minRows: 2, maxRows: 4 }}
          style={{
            flex: 1,
            borderRadius: 12,
            fontSize: 14
          }}
          disabled={loading}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={() => handleSendMessage()}
          loading={loading}
          disabled={!inputValue.trim()}
          style={{
            height: 'auto',
            minHeight: 48,
            borderRadius: 12,
            paddingLeft: 20,
            paddingRight: 20
          }}
        >
          Send
        </Button>
      </div>
    </div>
  );
};

export default ChatComponent;
