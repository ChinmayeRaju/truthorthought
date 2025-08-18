import React from 'react';
import { Layout, Menu, Typography, Button } from 'antd';
import { BarChartOutlined, ExperimentOutlined, HomeOutlined, DashboardOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Content } = Layout;
const { Title } = Typography;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Truth or Thought',
      onClick: () => navigate('/'),
    },
    {
      key: '/questionnaires',
      icon: <ExperimentOutlined />,
      label: 'Research Study',
      onClick: () => navigate('/questionnaires'),
    },
    {
      key: '/bias_research',
      icon: <BarChartOutlined />,
      label: 'Bias Analysis',
      onClick: () => navigate('/bias_research'),
    },
    {
      key: '/research-dashboard',
      icon: <DashboardOutlined />,
      label: 'Research Dashboard',
      onClick: () => navigate('/research-dashboard'),
    },
    {
      key: '/exit-questionnaire',
      icon: <LogoutOutlined />,
      label: 'Exit Questionnaire',
      onClick: () => navigate('/exit-questionnaire'),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: 'linear-gradient(135deg, #2c3e50 0%, #3498db 100%)',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <Title level={3} style={{ margin: 0, color: 'white' }}>
            Truth or Thought
          </Title>
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'white',
              minWidth: '400px',
            }}
            theme="dark"
          />
        </div>
        <div>
          <Button 
            type="text" 
            style={{ color: 'white' }}
            size="small"
          >
            AI-Powered Analysis
          </Button>
        </div>
      </Header>
      <Content style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        minHeight: 'calc(100vh - 64px)',
        padding: '20px'
      }}>
        {children}
      </Content>
    </Layout>
  );
};

export default AppLayout;
