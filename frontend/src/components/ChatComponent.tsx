import React, { useState } from 'react';
import { Input, Button, List, Typography, Space, message } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';

const { Text } = Typography;

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatComponentProps {
  sessionId: string;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await apiService.chat(sessionId, inputValue);
      if (response.success) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.answer,
          sender: 'assistant',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        message.error('Failed to get response from AI');
      }
    } catch (error) {
      console.error('Chat error:', error);
      message.error('Network error occurred');
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

  return (
    <div style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <div>Ask me anything about the analysis!</div>
          </div>
        ) : (
          <List
            dataSource={messages}
            renderItem={(message) => (
              <List.Item style={{ padding: '8px 0', border: 'none' }}>
                <div
                  style={{
                    width: '100%',
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div
                    style={{
                      maxWidth: '80%',
                      padding: '12px 16px',
                      borderRadius: 12,
                      background: message.sender === 'user' ? '#1890ff' : '#f0f0f0',
                      color: message.sender === 'user' ? 'white' : 'black',
                    }}
                  >
                    <Space>
                      {message.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      <Text style={{ color: message.sender === 'user' ? 'white' : 'black' }}>
                        {message.text}
                      </Text>
                    </Space>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}
      </div>
      
      <div style={{ display: 'flex', gap: 8 }}>
        <Input.TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a follow-up question..."
          autoSize={{ minRows: 1, maxRows: 3 }}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          loading={loading}
          disabled={!inputValue.trim()}
        >
          Send
        </Button>
      </div>
    </div>
  );
};

export default ChatComponent;
