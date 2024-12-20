import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Select, Spin, Empty } from 'antd';
import { Line, Pie } from '@ant-design/charts';
import axios from 'axios';

const { Option } = Select;

const Analytics = () => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/analytics/stats?days=${timeRange}`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [timeRange]);

  const renderContentTypesPie = () => {
    if (!stats) return <Empty />;

    const data = [
      { type: '文章', value: stats.content_types.article },
      { type: '产品描述', value: stats.content_types.product }
    ];

    const config = {
      data,
      angleField: 'value',
      colorField: 'type',
      radius: 0.8,
      label: {
        type: 'outer',
        content: '{name} {percentage}'
      }
    };

    return <Pie {...config} />;
  };

  const renderDailyGenerationLine = () => {
    if (!stats) return <Empty />;

    const data = Object.entries(stats.daily_generation).map(([date, count]) => ({
      date,
      count
    }));

    const config = {
      data,
      xField: 'date',
      yField: 'count',
      point: {
        size: 5,
        shape: 'diamond'
      },
      label: {
        style: {
          fill: '#aaa'
        }
      }
    };

    return <Line {...config} />;
  };

  const renderScoreDistributionPie = () => {
    if (!stats) return <Empty />;

    const data = Object.entries(stats.score_distribution).map(([range, count]) => ({
      range,
      count
    }));

    const config = {
      data,
      angleField: 'count',
      colorField: 'range',
      radius: 0.8,
      label: {
        type: 'outer',
        content: '{name} {percentage}'
      }
    };

    return <Pie {...config} />;
  };

  return (
    <div>
      <Card title="内容数据分析" extra={
        <Select
          value={timeRange}
          onChange={setTimeRange}
          style={{ width: 120 }}
        >
          <Option value={7}>近7天</Option>
          <Option value={30}>近30天</Option>
          <Option value={90}>近90天</Option>
        </Select>
      }>
        <Spin spinning={loading}>
          {stats && (
            <>
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}>
                  <Statistic
                    title="总内容数"
                    value={stats.total_content}
                    suffix="篇"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="平均SEO得分"
                    value={stats.average_seo_score}
                    suffix="分"
                    precision={1}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="文章数量"
                    value={stats.content_types.article}
                    suffix="篇"
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="产品描述数量"
                    value={stats.content_types.product}
                    suffix="篇"
                  />
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Card title="内容类型分布">
                    {renderContentTypesPie()}
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="得分分布">
                    {renderScoreDistributionPie()}
                  </Card>
                </Col>
              </Row>

              <Card title="每日内容生成趋势" style={{ marginTop: 24 }}>
                {renderDailyGenerationLine()}
              </Card>

              <Card title="热门关键词" style={{ marginTop: 24 }}>
                <Row gutter={[16, 16]}>
                  {Object.entries(stats.keyword_distribution).map(([keyword, count]) => (
                    <Col span={6} key={keyword}>
                      <Card size="small">
                        <Statistic
                          title={keyword}
                          value={count}
                          suffix="次"
                        />
                      </Card>
                    </Col>
                  ))}
                </Row>
              </Card>
            </>
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default Analytics;
