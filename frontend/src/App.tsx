import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import MainAnalysis from './pages/MainAnalysis';
import BiasResearch from './pages/BiasResearch';
import Questionnaires from './pages/Questionnaires';

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#3498db',
          colorSuccess: '#27ae60',
          colorWarning: '#f39c12',
          colorError: '#e74c3c',
          borderRadius: 8,
          fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<MainAnalysis />} />
          <Route path="/questionnaires" element={<Questionnaires />} />
          <Route path="/bias_research" element={<BiasResearch />} />
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App;
