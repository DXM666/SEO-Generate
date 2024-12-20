import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SearchOutlined,
  CloudUploadOutlined
} from '@ant-design/icons';

import Home from './pages/Home';
import './index.css';

const { Header, Content, Sider } = Layout;

// 临时页面组件
const Generator = () => <div>内容生成</div>;
const History = () => <div>历史记录</div>;
const Analysis = () => <div>内容分析</div>;
const Batch = () => <div>批量操作</div>;

const App = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页'
    },
    {
      key: '/generator',
      icon: <FileTextOutlined />,
      label: '内容生成'
    },
    {
      key: '/history',
      icon: <SearchOutlined />,
      label: '历史记录'
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: '内容分析'
    },
    {
      key: '/batch',
      icon: <CloudUploadOutlined />,
      label: '批量操作'
    }
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider>
        <div className="logo" />
        <Menu
          theme="dark"
          defaultSelectedKeys={['/']}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: 0 }}>
          <h1 style={{ margin: 0, textAlign: 'center' }}>SEO内容生成器</h1>
        </Header>
        <Content style={{ margin: '16px' }}>
          <div style={{ padding: 24, background: '#fff', minHeight: 360 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/generator" element={<Generator />} />
              <Route path="/history" element={<History />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/batch" element={<Batch />} />
            </Routes>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

const AppWrapper = () => (
  <Router>
    <App />
  </Router>
);

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<AppWrapper />);
