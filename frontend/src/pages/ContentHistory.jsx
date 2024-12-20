import React, { useState, useEffect } from 'react';
import { Table, Card, Input, Select, Button, Space, message, Modal } from 'antd';
import { SearchOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

const ContentHistory = () => {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchKeywords, setSearchKeywords] = useState('');
  const [contentType, setContentType] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });
  const [selectedContent, setSelectedContent] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const fetchContents = async (page = 1, keywords = '', type = '') => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/content/search', {
        params: {
          page,
          limit: pagination.pageSize,
          keywords,
          type
        }
      });

      if (response.data.success) {
        setContents(response.data.contents);
        setPagination({
          ...pagination,
          current: page,
          total: response.data.total || 0
        });
      } else {
        message.error('获取内容列表失败：' + response.data.error);
      }
    } catch (error) {
      message.error('请求失败：' + error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContents();
  }, []);

  const handleSearch = () => {
    fetchContents(1, searchKeywords, contentType);
  };

  const handleTableChange = (pagination) => {
    fetchContents(pagination.current, searchKeywords, contentType);
  };

  const handleDelete = async (contentId) => {
    try {
      const response = await axios.delete(`http://localhost:5000/api/content/${contentId}`);
      if (response.data.success) {
        message.success('删除成功');
        fetchContents(pagination.current, searchKeywords, contentType);
      } else {
        message.error('删除失败：' + response.data.error);
      }
    } catch (error) {
      message.error('请求失败：' + error.message);
    }
  };

  const showContentDetail = (content) => {
    setSelectedContent(content);
    setModalVisible(true);
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      width: '20%',
    },
    {
      title: '内容类型',
      dataIndex: 'content_type',
      key: 'content_type',
      width: '15%',
      render: (text) => text === 'article' ? '文章' : '产品描述'
    },
    {
      title: 'SEO得分',
      dataIndex: ['seo_score', 'total_score'],
      key: 'seo_score',
      width: '15%',
      render: (score) => `${score}分`
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => showContentDetail(record)}
          >
            查看
          </Button>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record._id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="内容历史记录" style={{ marginBottom: 24 }}>
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索关键词"
            value={searchKeywords}
            onChange={(e) => setSearchKeywords(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            placeholder="内容类型"
            value={contentType}
            onChange={setContentType}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="article">文章</Option>
            <Option value="product">产品描述</Option>
          </Select>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
          >
            搜索
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={contents}
          rowKey="_id"
          pagination={pagination}
          onChange={handleTableChange}
          loading={loading}
        />
      </Card>

      <Modal
        title="内容详情"
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedContent && (
          <div>
            <h3>标题</h3>
            <p>{selectedContent.title}</p>

            <h3>Meta描述</h3>
            <p>{selectedContent.meta_description}</p>

            <h3>正文</h3>
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {selectedContent.content}
            </div>

            <h3>SEO分析</h3>
            <p>总分：{selectedContent.seo_score.total_score}分</p>
            <p>标题得分：{selectedContent.seo_score.factors.title}分</p>
            <p>描述得分：{selectedContent.seo_score.factors.meta_description}分</p>
            <p>内容质量得分：{selectedContent.seo_score.factors.content_quality}分</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ContentHistory;
