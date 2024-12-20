import React from 'react';
import { Layout, Menu } from 'antd';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import ContentGenerator from './pages/ContentGenerator';
import ContentAnalysis from './pages/ContentAnalysis';
import ContentHistory from './pages/ContentHistory';
import Analytics from './pages/Analytics';
import BatchOperations from './pages/BatchOperations';
import './App.css';

const { Header, Content, Footer } = Layout;

function App() {
  return (
    <Router>
      <Layout className="layout">
        <Header>
          <div className="logo" />
          <Menu theme="dark" mode="horizontal" defaultSelectedKeys={['1']}>
            <Menu.Item key="1">
              <Link to="/">内容生成</Link>
            </Menu.Item>
            <Menu.Item key="2">
              <Link to="/analysis">内容分析</Link>
            </Menu.Item>
            <Menu.Item key="3">
              <Link to="/history">历史记录</Link>
            </Menu.Item>
            <Menu.Item key="4">
              <Link to="/analytics">数据分析</Link>
            </Menu.Item>
            <Menu.Item key="5">
              <Link to="/batch">批量操作</Link>
            </Menu.Item>
          </Menu>
        </Header>
        <Content style={{ padding: '0 50px', marginTop: 64 }}>
          <div className="site-layout-content">
            <Routes>
              <Route path="/" element={<ContentGenerator />} />
              <Route path="/analysis" element={<ContentAnalysis />} />
              <Route path="/history" element={<ContentHistory />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/batch" element={<BatchOperations />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          SEO内容生成系统 {new Date().getFullYear()}
        </Footer>
      </Layout>
    </Router>
  );
}

export default App;
