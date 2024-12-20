import React, { useState } from 'react';
import { Card, Input, Button, Progress, List, Typography, message } from 'antd';
import axios from 'axios';

const { TextArea } = Input;
const { Title, Text } = Typography;

const ContentAnalysis = () => {
  const [content, setContent] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!content.trim()) {
      message.warning('请输入需要分析的内容');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/validate', {
        content: content
      });

      if (response.data.success) {
        setAnalysis(response.data.validation);
        message.success('内容分析完成！');
      } else {
        message.error('分析失败：' + response.data.error);
      }
    } catch (error) {
      message.error('请求失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="SEO内容分析" style={{ marginBottom: 24 }}>
        <TextArea
          rows={6}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="请输入需要分析的内容"
        />
        <Button
          type="primary"
          onClick={handleAnalyze}
          loading={loading}
          style={{ marginTop: 16 }}
        >
          开始分析
        </Button>
      </Card>

      {analysis && (
        <Card title="分析结果">
          <div style={{ marginBottom: 24 }}>
            <Title level={4}>SEO得分</Title>
            <Progress
              type="circle"
              percent={analysis.seo_score.total_score}
              format={(percent) => `${percent}分`}
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <Title level={4}>关键词密度</Title>
            <Text>
              状态: {analysis.keyword_density.status === 'optimal' ? '适中' : 
                     analysis.keyword_density.status === 'high' ? '过高' : '过低'}
            </Text>
            <Progress
              percent={analysis.keyword_density.value * 100 / 3}
              status={analysis.keyword_density.status === 'optimal' ? 'success' : 'exception'}
            />
          </div>

          <div>
            <Title level={4}>可读性分析</Title>
            <Progress percent={analysis.readability.score} />
            {analysis.readability.suggestions.length > 0 && (
              <List
                size="small"
                header={<div>改进建议</div>}
                bordered
                dataSource={analysis.readability.suggestions}
                renderItem={item => <List.Item>{item}</List.Item>}
              />
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default ContentAnalysis;
