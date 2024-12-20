import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { FileTextOutlined, BarChartOutlined, ClockCircleOutlined } from '@ant-design/icons';

const Home = () => {
  return (
    <div>
      <h2>欢迎使用SEO内容生成器</h2>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="已生成内容"
              value={123}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="分析报告"
              value={45}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="本月生成"
              value={67}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home;
