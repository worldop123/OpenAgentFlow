# API参考文档

## 概述

OpenAgentFlow提供完整的RESTful API，支持AI Agent管理、工作流执行、插件管理等核心功能。

**基础URL**: `http://localhost:8000` (本地部署)
**API版本**: `v1`
**内容类型**: `application/json`

## 认证

### API密钥认证
```http
Authorization: Bearer <your_api_key>
```

### JWT认证
```http
Authorization: Bearer <jwt_token>
```

## 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 500 | 服务器错误 |

## 健康检查

### 获取系统健康状态
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-03-20T17:42:00Z",
  "services": {
    "database": "connected",
    "cache": "connected",
    "ai_services": "available"
  }
}
```

## Agent管理

### 获取Agent列表
```http
GET /api/v1/agents
```

**查询参数**:
- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，默认50
- `type` (可选): Agent类型过滤
- `status` (可选): 状态过滤

**响应示例**:
```json
{
  "agents": [
    {
      "id": "agent_123",
      "name": "客服助手",
      "description": "处理客户咨询的AI助手",
      "type": "llm",
      "status": "active",
      "created_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1,
    "pages": 1
  }
}
```

### 创建Agent
```http
POST /api/v1/agents
```

**请求体**:
```json
{
  "name": "数据分析助手",
  "description": "用于数据分析的AI助手",
  "type": "llm",
  "config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "你是一个专业的数据分析师..."
  },
  "metadata": {
    "tags": ["analysis", "data"]
  }
}
```

### 获取特定Agent
```http
GET /api/v1/agents/{agent_id}
```

### 更新Agent
```http
PUT /api/v1/agents/{agent_id}
```

### 删除Agent
```http
DELETE /api/v1/agents/{agent_id}
```

### 执行Agent
```http
POST /api/v1/agents/{agent_id}/execute
```

**请求体**:
```json
{
  "input": "分析一下最近的销售数据",
  "parameters": {
    "temperature": 0.7
  },
  "session_id": "session_123"
}
```

## 工作流管理

### 获取工作流列表
```http
GET /api/v1/workflows
```

### 创建工作流
```http
POST /api/v1/workflows
```

**请求体**:
```json
{
  "name": "客户服务流程",
  "description": "完整的客户服务自动化流程",
  "nodes": [
    {
      "id": "start",
      "type": "input",
      "data": {
        "label": "客户咨询"
      }
    },
    {
      "id": "ai_response",
      "type": "agent",
      "data": {
        "label": "AI回复",
        "agent_id": "agent_123"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "start",
      "target": "ai_response"
    }
  ],
  "settings": {
    "max_execution_time": 300,
    "retry_count": 3
  }
}
```

### 获取工作流详情
```http
GET /api/v1/workflows/{workflow_id}
```

### 执行工作流
```http
POST /api/v1/workflows/{workflow_id}/execute
```

**请求体**:
```json
{
  "input_data": {
    "customer_query": "产品价格是多少？",
    "customer_id": "cust_123"
  },
  "parameters": {
    "priority": "high",
    "timeout": 60
  }
}
```

### 获取执行历史
```http
GET /api/v1/workflows/{workflow_id}/executions
```

**查询参数**:
- `status` (可选): 执行状态过滤
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期
- `limit` (可选): 限制数量

## 插件管理

### 获取插件列表
```http
GET /api/v1/plugins
```

### 获取插件详情
```http
GET /api/v1/plugins/{plugin_name}
```

### 启用插件
```http
POST /api/v1/plugins/{plugin_name}/enable
```

### 禁用插件
```http
POST /api/v1/plugins/{plugin_name}/disable
```

### 更新插件配置
```http
POST /api/v1/plugins/{plugin_name}/config
```

**请求体**:
```json
{
  "config": {
    "api_key": "your_api_key",
    "webhook_url": "https://example.com/webhook"
  }
}
```

### 扫描新插件
```http
POST /api/v1/plugins/scan
```

## 工具集成

### 飞书工具

#### 发送消息
```http
POST /api/v1/tools/feishu/send-message
```

**请求体**:
```json
{
  "receive_id": "ou_123456",
  "receive_id_type": "open_id",
  "content": {
    "text": "Hello from OpenAgentFlow!"
  }
}
```

#### 创建日程
```http
POST /api/v1/tools/feishu/create-calendar-event
```

### 钉钉工具

#### 发送工作通知
```http
POST /api/v1/tools/dingtalk/send-notification
```

### 企业微信工具

#### 发送应用消息
```http
POST /api/v1/tools/wecom/send-message
```

## 数据管理

### 获取数据源列表
```http
GET /api/v1/data/sources
```

### 查询数据
```http
POST /api/v1/data/query
```

**请求体**:
```json
{
  "source_id": "source_123",
  "query": "SELECT * FROM users WHERE status = 'active'",
  "parameters": {},
  "limit": 100
}
```

### 上传数据
```http
POST /api/v1/data/upload
```

**Content-Type**: `multipart/form-data`

**表单字段**:
- `file`: 数据文件
- `source_id`: 数据源ID
- `format`: 数据格式 (csv, json, excel)

## 系统管理

### 获取系统信息
```http
GET /api/v1/system/info
```

**响应示例**:
```json
{
  "name": "OpenAgentFlow",
  "version": "0.1.0",
  "environment": "production",
  "uptime": "5d 3h 12m",
  "memory_usage": "45%",
  "cpu_usage": "22%",
  "database_status": "connected",
  "cache_status": "connected"
}
```

### 获取统计信息
```http
GET /api/v1/system/stats
```

### 获取日志
```http
GET /api/v1/system/logs
```

**查询参数**:
- `level` (可选): 日志级别
- `start_time` (可选): 开始时间
- `end_time` (可选): 结束时间
- `limit` (可选): 限制数量

## 实时通信

### WebSocket连接
```websocket
ws://localhost:8000/ws
```

**连接参数**:
- `token`: 认证令牌
- `client_id`: 客户端ID

**事件类型**:
- `workflow_started`: 工作流开始
- `workflow_completed`: 工作流完成
- `agent_response`: Agent响应
- `error_occurred`: 错误发生

## 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "name",
      "reason": "不能为空"
    },
    "timestamp": "2026-03-20T17:42:00Z"
  }
}
```

### 常见错误码

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| INVALID_REQUEST | 请求参数无效 | 400 |
| UNAUTHORIZED | 未授权 | 401 |
| FORBIDDEN | 禁止访问 | 403 |
| NOT_FOUND | 资源不存在 | 404 |
| VALIDATION_FAILED | 验证失败 | 422 |
| INTERNAL_ERROR | 服务器错误 | 500 |
| SERVICE_UNAVAILABLE | 服务不可用 | 503 |

## 速率限制

### 默认限制
- 匿名用户: 60 请求/分钟
- 认证用户: 1000 请求/分钟
- API密钥: 5000 请求/分钟

### 响应头
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1614589200
```

## 版本控制

API使用URL路径版本控制：
- `v1`: 当前稳定版本
- `v1beta`: 测试版本

## 数据格式

### 日期时间
使用ISO 8601格式：
```json
{
  "created_at": "2026-03-20T17:42:00Z"
}
```

### 分页响应
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 100,
    "pages": 2
  }
}
```

### 排序参数
使用`sort`和`order`参数：
```
GET /api/v1/agents?sort=created_at&order=desc
```

## 示例

### Python示例
```python
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 获取Agent列表
response = requests.get(f"{BASE_URL}/api/v1/agents", headers=headers)
agents = response.json()

# 创建工作流
workflow_data = {
    "name": "数据分析流程",
    "description": "自动数据分析工作流",
    "nodes": [...],
    "edges": [...]
}

response = requests.post(
    f"{BASE_URL}/api/v1/workflows",
    headers=headers,
    json=workflow_data
)

# 执行工作流
execution_data = {
    "input_data": {"query": "分析销售数据"},
    "parameters": {"timeout": 60}
}

response = requests.post(
    f"{BASE_URL}/api/v1/workflows/workflow_id/execute",
    headers=headers,
    json=execution_data
)
```

### JavaScript示例
```javascript
const axios = require('axios');

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Authorization': `Bearer ${process.env.API_KEY}`,
        'Content-Type': 'application/json'
    }
});

// 获取系统信息
async function getSystemInfo() {
    const response = await api.get('/api/v1/system/info');
    return response.data;
}

// 执行Agent
async function executeAgent(agentId, input) {
    const response = await api.post(`/api/v1/agents/${agentId}/execute`, {
        input,
        parameters: { temperature: 0.7 }
    });
    return response.data;
}
```

## 更新日志

### v0.1.0 (2026-03-20)
- 初始版本发布
- 完整的Agent管理API
- 工作流执行引擎
- 插件系统支持
- 企业工具集成

## 支持

如有问题，请：
1. 查看 [官方文档](https://github.com/worldop123/OpenAgentFlow)
2. 提交 [GitHub Issue](https://github.com/worldop123/OpenAgentFlow/issues)
3. 加入 [社区讨论](COMMUNITY.md)