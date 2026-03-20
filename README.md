# OpenAgentFlow

<div align="center">

![OpenAgentFlow Logo](https://img.shields.io/badge/OpenAgentFlow-V0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-teal)
![License](https://img.shields.io/badge/License-MIT-orange)
![GitHub Stars](https://img.shields.io/github/stars/worldop123/OpenAgentFlow?style=social)

**可视化、可组合的AI Agent工作流平台**

[🚀 快速开始](#快速开始) | [📖 文档](#文档) | [🔧 功能特性](#功能特性) | [🤝 贡献](#贡献) | [📄 许可证](#许可证)

</div>

## ✨ 项目简介

OpenAgentFlow 是一个开源的、可视化的AI Agent工作流平台，让您能够通过拖拽方式构建复杂的AI应用流程。无论是自动化客服、智能数据分析、还是企业工具集成，OpenAgentFlow都能让AI工作流的构建变得简单直观。

## 🎯 核心特性

### 🎨 **可视化工作流设计器**
- 拖拽式界面，无需编写代码即可创建复杂工作流
- 实时预览工作流执行状态
- 支持条件分支、循环、并行执行等高级功能

### 🤖 **多类型AI Agent支持**
- **LLM Agent**: 集成OpenAI GPT系列模型
- **工具Agent**: 支持飞书、钉钉、企业微信等企业工具
- **自定义Agent**: 支持Python函数和API调用
- **条件Agent**: 实现智能决策逻辑

### 🔗 **企业工具无缝集成**
- **飞书/Lark**: 消息、日程、多维表格
- **钉钉**: 机器人、工作通知、审批流
- **企业微信**: 消息、通讯录、应用管理
- **其他**: REST API、数据库、文件系统

### 🏗️ **现代化技术栈**
- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: 现代化Web界面，响应式设计
- **部署**: Docker + Kubernetes支持
- **CI/CD**: GitHub Actions自动化

## 🚀 快速开始

### 使用Docker一键部署

```bash
# 克隆项目
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件，配置您的API密钥

# 使用Docker Compose启动
docker-compose up -d

# 访问应用
# 前端界面: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 本地开发环境

```bash
# 1. 安装Python 3.11+
# 2. 克隆项目
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 6. 启动开发服务器
python main.py
```

### 使用部署脚本

```bash
# 初始设置
./deploy.sh setup

# 构建和启动
./deploy.sh build
./deploy.sh start

# 查看状态
./deploy.sh status

# 停止服务
./deploy.sh stop
```

## 📖 文档

### 📚 核心概念

#### 1. **Agent（智能体）**
Agent是OpenAgentFlow中的基本执行单元，每个Agent都有特定的功能：

```python
# 创建LLM Agent示例
from backend.agent.base import LLMAgent

agent = LLMAgent(
    name="客服助手",
    description="处理客户咨询的AI助手",
    model="gpt-3.5-turbo",
    system_prompt="你是一个专业的客服助手，回答客户问题时要礼貌且专业。"
)
```

#### 2. **Workflow（工作流）**
工作流是由多个节点（Node）和连接线（Edge）组成的执行流程图：

```json
{
  "name": "客户服务流程",
  "nodes": [
    {
      "id": "start",
      "type": "input",
      "data": { "label": "客户咨询" }
    },
    {
      "id": "ai_response",
      "type": "agent",
      "data": { 
        "label": "AI回复",
        "agent_id": "客服助手"
      }
    },
    {
      "id": "end",
      "type": "output",
      "data": { "label": "回复客户" }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "start",
      "target": "ai_response"
    },
    {
      "id": "e2",
      "source": "ai_response",
      "target": "end"
    }
  ]
}
```

#### 3. **Tool（工具）**
工具是与外部系统集成的接口：

```python
# 飞书工具示例
from backend.tools.feishu import FeishuTool

feishu = FeishuTool(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 发送消息
await feishu.send_message(
    user_id="ou_xxx",
    message="Hello from OpenAgentFlow!"
)
```

### 🔧 API使用

#### 基础API端点

```bash
# 健康检查
GET /health

# 系统信息
GET /system/info

# Agent管理
GET    /api/v1/agents          # 获取Agent列表
POST   /api/v1/agents          # 创建新Agent
GET    /api/v1/agents/{id}     # 获取特定Agent
PUT    /api/v1/agents/{id}     # 更新Agent
DELETE /api/v1/agents/{id}     # 删除Agent

# 工作流管理
GET    /api/v1/workflows          # 获取工作流列表
POST   /api/v1/workflows          # 创建工作流
GET    /api/v1/workflows/{id}     # 获取特定工作流
PUT    /api/v1/workflows/{id}     # 更新工作流
POST   /api/v1/workflows/{id}/execute  # 执行工作流
```

#### API示例

```python
import requests
import json

# 创建Agent
agent_data = {
    "name": "数据分析助手",
    "description": "用于数据分析的AI助手",
    "agent_type": "llm",
    "config": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/agents",
    json=agent_data,
    headers={"Content-Type": "application/json"}
)

print(response.json())
```

### 🎨 前端使用

1. **访问Web界面**: `http://localhost:8000`
2. **创建Agent**: 点击"AI Agent" → "创建Agent"
3. **设计工作流**: 在工作流设计器中拖拽节点
4. **执行测试**: 点击"运行"按钮测试工作流
5. **部署应用**: 将工作流发布为API端点

## 🔧 企业集成

### 飞书集成配置

```bash
# 在 .env 文件中配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 或在UI中配置
1. 访问 "工具集成" → "飞书"
2. 点击"配置"按钮
3. 输入App ID和App Secret
4. 点击"连接"测试
```

### 钉钉集成

```bash
DINGTALK_APP_KEY=your_app_key
DINGTALK_APP_SECRET=your_app_secret
```

### 企业微信集成

```bash
WECOM_CORP_ID=your_corp_id
WECOM_CORP_SECRET=your_corp_secret
WECOM_AGENT_ID=your_agent_id
```

## 🏗️ 项目结构

```
OpenAgentFlow/
├── backend/                 # 后端代码
│   ├── agent/              # Agent相关
│   │   ├── base.py         # Agent基类
│   │   └── factory.py      # Agent工厂
│   ├── api/                # API端点
│   │   ├── agents.py       # Agent API
│   │   └── workflows.py    # 工作流API
│   ├── database.py         # 数据库模型
│   ├── server.py           # FastAPI服务器
│   └── tools/              # 工具集成
│       ├── feishu.py       # 飞书工具
│       ├── dingtalk.py     # 钉钉工具
│       └── wecom.py        # 企业微信工具
├── static/                 # 静态文件
│   ├── css/               # 样式表
│   ├── js/                # JavaScript
│   └── index.html         # 主页
├── tests/                  # 测试代码
│   ├── unit/              # 单元测试
│   ├── api/               # API测试
│   └── integration/       # 集成测试
├── config.py              # 配置文件
├── main.py                # 主入口文件
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose
├── deploy.sh             # 部署脚本
└── README.md             # 项目说明
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看我们的贡献指南：

### 开发流程

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 代码规范

- 使用 **Black** 进行代码格式化
- 使用 **Flake8** 进行代码检查
- 所有新功能必须包含**单元测试**
- 更新 **README.md** 和相关文档

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/ -v

# 代码格式化
black backend/ tests/
isort backend/ tests/

# 代码检查
flake8 backend/ tests/
mypy backend/
```

## 📄 许可证

本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

- **GitHub Issues**: [报告问题或请求功能](https://github.com/worldop123/OpenAgentFlow/issues)
- **Discord**: [加入社区讨论](https://discord.gg/invite/your-discord)
- **文档网站**: [查看完整文档](https://worldop123.github.io/OpenAgentFlow)

## 🚀 路线图

### 近期计划
- [ ] 更多企业工具集成（Slack, Teams等）
- [ ] 移动端应用
- [ ] 工作流模板市场
- [ ] 实时协作功能

### 长期愿景
- [ ] 分布式执行引擎
- [ ] 机器学习模型集成
- [ ] 可视化数据分析
- [ ] 企业级权限管理

---

<div align="center">

**让AI工作流开发变得简单直观**

[⭐ Star 本项目](https://github.com/worldop123/OpenAgentFlow) | [👥 加入社区](COMMUNITY.md) | [💼 商业支持](COMMERCIAL.md)

</div>