# SEO内容生成与优化系统

这是一个基于AI的SEO内容生成和优化系统，用于自动生成和优化电商网站的SEO内容。

## 功能特点

- AI驱动的SEO内容生成
- 内容质量监督与反馈机制
- 自动化的SEO优化建议
- 可视化的内容管理后台

## 技术栈

### 后端
- Python Flask
- OpenAI GPT
- MongoDB
- Elasticsearch

### 前端
- React
- Ant Design
- Axios

## 安装说明

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
创建.env文件并配置以下变量：
```
OPENAI_API_KEY=your_api_key
MONGO_URI=your_mongodb_uri
```

## 项目结构

```
SEO-Generate/
├── backend/              # 后端代码
│   ├── api/             # API路由
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── frontend/            # 前端代码
│   ├── src/
│   ├── public/
│   └── package.json
├── requirements.txt     # Python依赖
└── README.md           # 项目说明
```
