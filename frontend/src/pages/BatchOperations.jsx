import React, { useState } from 'react';
import {
  Card,
  Upload,
  Button,
  Input,
  Space,
  Table,
  message,
  Modal,
  Select,
  Tag,
  Progress
} from 'antd';
import {
  UploadOutlined,
  PlusOutlined,
  DeleteOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;
const { Option } = Select;

const BatchOperations = () => {
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedContents, setGeneratedContents] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [exportFormat, setExportFormat] = useState('csv');
  const [progress, setProgress] = useState(0);

  const handleKeywordsInput = (value) => {
    const keywordsList = value.split('\n')
      .map(k => k.trim())
      .filter(k => k);
    setKeywords(keywordsList);
  };

  const handleFileUpload = async (info) => {
    if (info.file.status !== 'uploading') {
      const formData = new FormData();
      formData.append('file', info.file);

      try {
        const response = await axios.post(
          'http://localhost:5000/api/batch/import-keywords',
          formData
        );

        if (response.data.success) {
          setKeywords(response.data.keywords_list);
          message.success('关键词导入成功！');
        } else {
          message.error('导入失败：' + response.data.error);
        }
      } catch (error) {
        message.error('请求失败：' + error.message);
      }
    }
  };

  const startBatchGeneration = async () => {
    if (keywords.length === 0) {
      message.warning('请先添加关键词');
      return;
    }

    setLoading(true);
    setProgress(0);
    try {
      const response = await axios.post('http://localhost:5000/api/batch/generate', {
        keywords_list: keywords,
        type: 'article'
      });

      if (response.data.success) {
        setGeneratedContents(response.data.results);
        message.success('批量生成完成！');
      } else {
        message.error('生成失败：' + response.data.error);
      }
    } catch (error) {
      message.error('请求失败：' + error.message);
    } finally {
      setLoading(false);
      setProgress(100);
    }
  };

  const exportContents = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5000/api/batch/export',
        {
          content_ids: selectedRows.map(row => row.content_id),
          format: exportFormat
        },
        {
          responseType: 'blob'
        }
      );

      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `seo_contents_${new Date().getTime()}.${exportFormat}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      message.error('导出失败：' + error.message);
    }
  };

  const columns = [
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
    },
    {
      title: '标题',
      dataIndex: ['content', '标题'],
      key: 'title',
    },
    {
      title: 'SEO得分',
      dataIndex: ['validation', 'seo_score', 'total_score'],
      key: 'seo_score',
      render: (score) => (
        <Tag color={score >= 80 ? 'green' : score >= 60 ? 'orange' : 'red'}>
          {score}分
        </Tag>
      ),
    },
    {
      title: '状态',
      key: 'status',
      render: (_, record) => (
        <Tag color={record.content ? 'green' : 'red'}>
          {record.content ? '生成成功' : '生成失败'}
        </Tag>
      ),
    }
  ];

  return (
    <div>
      <Card title="批量内容生成" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Upload
            accept=".csv,.txt"
            customRequest={handleFileUpload}
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>导入关键词文件</Button>
          </Upload>

          <TextArea
            rows={6}
            placeholder="每行输入一个关键词"
            value={keywords.join('\n')}
            onChange={(e) => handleKeywordsInput(e.target.value)}
          />

          <Space>
            <Button
              type="primary"
              onClick={startBatchGeneration}
              loading={loading}
              icon={<PlusOutlined />}
            >
              开始生成
            </Button>

            <Select
              value={exportFormat}
              onChange={setExportFormat}
              style={{ width: 100 }}
            >
              <Option value="csv">CSV</Option>
              <Option value="json">JSON</Option>
            </Select>

            <Button
              onClick={exportContents}
              disabled={selectedRows.length === 0}
              icon={<DownloadOutlined />}
            >
              导出选中内容
            </Button>
          </Space>

          {loading && (
            <Progress percent={progress} status="active" />
          )}
        </Space>
      </Card>

      <Card title="生成结果">
        <Table
          columns={columns}
          dataSource={generatedContents}
          rowKey="content_id"
          rowSelection={{
            type: 'checkbox',
            onChange: (_, selectedRows) => setSelectedRows(selectedRows),
          }}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default BatchOperations;
