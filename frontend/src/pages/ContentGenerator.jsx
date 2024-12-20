import React, { useState } from 'react';
import { Form, Input, Button, Card, Select, message, Spin } from 'antd';
import axios from 'axios';

const { TextArea } = Input;
const { Option } = Select;

const ContentGenerator = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/generate', {
        keywords: values.keywords,
        type: values.contentType
      });

      if (response.data.success) {
        setGeneratedContent(response.data.content);
        message.success('内容生成成功！');
      } else {
        message.error('内容生成失败：' + response.data.error);
      }
    } catch (error) {
      message.error('请求失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="SEO内容生成" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="keywords"
            label="关键词"
            rules={[{ required: true, message: '请输入关键词' }]}
          >
            <Input placeholder="请输入目标关键词，多个关键词用逗号分隔" />
          </Form.Item>

          <Form.Item
            name="contentType"
            label="内容类型"
            rules={[{ required: true, message: '请选择内容类型' }]}
          >
            <Select placeholder="请选择内容类型">
              <Option value="article">文章</Option>
              <Option value="product">产品描述</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              生成内容
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          <Spin tip="正在生成内容..." />
        </div>
      )}

      {generatedContent && (
        <Card title="生成结果" style={{ marginTop: 24 }}>
          <div>
            <h3>标题</h3>
            <p>{generatedContent.标题}</p>

            <h3>Meta描述</h3>
            <p>{generatedContent.meta描述}</p>

            <h3>正文</h3>
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {generatedContent.正文}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ContentGenerator;
