# API 文档

## 概述

OpenAgentFlow提供完整的RESTful API，支持AI Agent管理、工作流执行、插件管理等功能。所有API都遵循OpenAPI 3.0规范。

**基础URL**: `http://localhost:8000` (本地部署)  
**API版本**: `v1`  
**内容类型**: `application/json`  
**认证方式**: Bearer Token / API Key

## 快速开始

### 1. 获取访问令牌

```bash
# 使用API密钥认证
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key_here"
  }'

# 响应示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 2. 测试连接

```bash
# 使用令牌测试连接
curl -X GET http://localhost:8000/health \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 响应示例
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-03-20T17:58:00Z"
}
```

## 认证和授权

### 认证方式

#### 1. API密钥认证
```http
Authorization: Bearer <api_key>
```

#### 2. JWT令牌认证
```http
Authorization: Bearer <jwt_token>
```

#### 3. OAuth2认证
```http
Authorization: Bearer <oauth2_token>
```

### 权限范围

| 权限 | 描述 | 端点示例 |
|------|------|----------|
| `agents:read` | 读取Agent信息 | GET /api/v1/agents |
| `agents:write` | 创建/更新Agent | POST /api/v1/agents |
| `agents:execute` | 执行Agent | POST /api/v1/agents/{id}/execute |
| `workflows:read` | 读取工作流 | GET /api/v1/workflows |
| `workflows:write` | 创建/更新工作流 | POST /api/v1/workflows |
| `workflows:execute` | 执行工作流 | POST /api/v1/workflows/{id}/execute |
| `plugins:manage` | 管理插件 | POST /api/v1/plugins/{name}/enable |
| `system:admin` | 系统管理 | GET /api/v1/system/info |

## 端点参考

### 健康检查

#### GET /health
检查服务健康状态

**参数**: 无  
**认证**: 可选

**响应**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-03-20T17:58:00Z",
  "services": {
    "database": "connected",
    "cache": "connected",
    "ai_services": "available"
  }
}
```

#### GET /ready
检查服务就绪状态

**参数**: 无  
**认证**: 可选

**响应**:
```json
{
  "ready": true,
  "checks": {
    "database": true,
    "cache": true,
    "ai_provider": true
  }
}
```

### Agent管理

#### GET /api/v1/agents
获取Agent列表

**查询参数**:
| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| `page` | integer | 否 | 页码 | 1 |
| `limit` | integer | 否 | 每页数量 | 50 |
| `type` | string | 否 | Agent类型过滤 | - |
| `status` | string | 否 | 状态过滤 | - |
| `search` | string | 否 | 搜索关键词 | - |

**响应**:
```json
{
  "agents": [
    {
      "id": "agent_123456",
      "name": "客服助手",
      "description": "处理客户咨询的AI助手",
      "type": "llm",
      "config": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
      },
      "status": "active",
      "created_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z",
      "created_by": "user_123",
      "tags": ["customer_service", "ai"]
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

#### POST /api/v1/agents
创建新Agent

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
    "system_prompt": "你是一个专业的数据分析师...",
    "tools": ["data_analysis", "chart_generation"]
  },
  "metadata": {
    "tags": ["analysis", "data", "ai"],
    "category": "data_science",
    "version": "1.0.0"
  }
}
```

**响应**:
```json
{
  "id": "agent_789012",
  "name": "数据分析助手",
  "description": "用于数据分析的AI助手",
  "type": "llm",
  "config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  },
  "status": "active",
  "created_at": "2026-03-20T17:58:00Z",
  "updated_at": "2026-03-20T17:58:00Z",
  "created_by": "user_123"
}
```

#### GET /api/v1/agents/{agent_id}
获取特定Agent详情

**路径参数**:
- `agent_id`: Agent ID (必填)

**响应**:
```json
{
  "id": "agent_123456",
  "name": "客服助手",
  "description": "处理客户咨询的AI助手",
  "type": "llm",
  "config": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "你是一个专业的客服助手...",
    "tools": ["customer_service", "faq"]
  },
  "status": "active",
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z",
  "created_by": "user_123",
  "statistics": {
    "total_executions": 150,
    "success_rate": 0.95,
    "avg_response_time": 1.2
  }
}
```

#### PUT /api/v1/agents/{agent_id}
更新Agent

**路径参数**:
- `agent_id`: Agent ID (必填)

**请求体**:
```json
{
  "name": "客服助手-增强版",
  "description": "增强版客服助手，支持多语言",
  "config": {
    "model": "gpt-4",
    "temperature": 0.5,
    "max_tokens": 2000
  },
  "metadata": {
    "tags": ["customer_service", "multilingual", "ai"],
    "version": "2.0.0"
  }
}
```

#### DELETE /api/v1/agents/{agent_id}
删除Agent

**路径参数**:
- `agent_id`: Agent ID (必填)

**响应**:
```json
{
  "success": true,
  "message": "Agent已删除",
  "agent_id": "agent_123456"
}
```

#### POST /api/v1/agents/{agent_id}/execute
执行Agent

**路径参数**:
- `agent_id`: Agent ID (必填)

**请求体**:
```json
{
  "input": "分析一下最近的销售数据趋势",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": false
  },
  "session_id": "session_123",
  "context": {
    "user_id": "user_123",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai"
  }
}
```

**响应**:
```json
{
  "success": true,
  "result": "根据最近30天的销售数据显示...",
  "agent_id": "agent_123456",
  "execution_id": "exec_789012",
  "execution_time": 1.5,
  "tokens_used": {
    "prompt": 150,
    "completion": 350,
    "total": 500
  },
  "metadata": {
    "model": "gpt-3.5-turbo",
    "finish_reason": "stop"
  }
}
```

### 工作流管理

#### GET /api/v1/workflows
获取工作流列表

**查询参数**:
| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| `page` | integer | 否 | 页码 | 1 |
| `limit` | integer | 否 | 每页数量 | 50 |
| `status` | string | 否 | 状态过滤 | - |
| `search` | string | 否 | 搜索关键词 | - |
| `sort_by` | string | 否 | 排序字段 | created_at |
| `sort_order` | string | 否 | 排序顺序 | desc |

**响应**:
```json
{
  "workflows": [
    {
      "id": "workflow_123456",
      "name": "客户服务流程",
      "description": "完整的客户服务自动化流程",
      "version": 1,
      "status": "active",
      "nodes_count": 5,
      "edges_count": 4,
      "created_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z",
      "created_by": "user_123",
      "tags": ["customer_service", "automation"]
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

#### POST /api/v1/workflows
创建工作流

**请求体**:
```json
{
  "name": "数据分析流程",
  "description": "自动数据分析工作流",
  "nodes": [
    {
      "id": "start",
      "type": "input",
      "position": {"x": 100, "y": 100},
      "data": {
        "label": "数据输入",
        "description": "输入原始数据",
        "schema": {
          "type": "object",
          "properties": {
            "data": {"type": "array"},
            "format": {"type": "string"}
          },
          "required": ["data"]
        }
      }
    },
    {
      "id": "analysis",
      "type": "agent",
      "position": {"x": 300, "y": 100},
      "data": {
        "label": "AI分析",
        "agent_id": "agent_123456",
        "parameters": {
          "analysis_type": "trend",
          "time_range": "30d"
        }
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "start",
      "target": "analysis",
      "label": "原始数据",
      "condition": null
    }
  ],
  "settings": {
    "max_execution_time": 300,
    "retry_count": 3,
    "concurrent_executions": 5,
    "timeout_action": "fail"
  },
  "variables": {
    "default_time_range": "30d",
    "output_format": "markdown"
  },
  "metadata": {
    "tags": ["data_analysis", "automation", "ai"],
    "category": "data_science",
    "version": "1.0.0"
  }
}
```

#### GET /api/v1/workflows/{workflow_id}
获取工作流详情

**路径参数**:
- `workflow_id`: 工作流ID (必填)

**响应**:
```json
{
  "id": "workflow_123456",
  "name": "客户服务流程",
  "description": "完整的客户服务自动化流程",
  "definition": {
    "nodes": [...],
    "edges": [...],
    "variables": {...},
    "settings": {...}
  },
  "version": 1,
  "status": "active",
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z",
  "created_by": "user_123",
  "statistics": {
    "total_executions": 500,
    "success_rate": 0.92,
    "avg_execution_time": 15.3,
    "last_execution": "2026-03-20T17:58:00Z"
  }
}
```

#### POST /api/v1/workflows/{workflow_id}/execute
执行工作流

**路径参数**:
- `workflow_id`: 工作流ID (必填)

**请求体**:
```json
{
  "input_data": {
    "customer_query": "产品价格是多少？",
    "customer_id": "cust_123",
    "language": "zh-CN",
    "channel": "web"
  },
  "parameters": {
    "priority": "high",
    "timeout": 60,
    "async": false,
    "callback_url": "https://example.com/webhook"
  },
  "context": {
    "user_id": "user_123",
    "session_id": "session_456",
    "environment": "production"
  }
}
```

**响应 (同步执行)**:
```json
{
  "execution_id": "exec_789012",
  "workflow_id": "workflow_123456",
  "status": "completed",
  "result": {
    "response": "产品价格是999元，目前有促销活动...",
    "suggestions": ["查看详情", "联系客服"],
    "metadata": {
      "processed_by": "客服助手",
      "confidence": 0.95
    }
  },
  "execution_time": 2.5,
  "started_at": "2026-03-20T17:58:00Z",
  "completed_at": "2026-03-20T17:58:02Z",
  "logs": [
    {
      "timestamp": "2026-03-20T17:58:00Z",
      "level": "info",
      "message": "工作流执行开始",
      "node_id": "start"
    },
    {
      "timestamp": "2026-03-20T17:58:01Z",
      "level": "info",
      "message": "Agent执行完成",
      "node_id": "analysis",
      "agent_id": "agent_123456"
    }
  ]
}
```

**响应 (异步执行)**:
```json
{
  "execution_id": "exec_789012",
  "workflow_id": "workflow_123456",
  "status": "started",
  "message": "工作流已开始异步执行",
  "started_at": "2026-03-20T17:58:00Z",
  "check_status_url": "http://localhost:8000/api/v1/executions/exec_789012"
}
```

#### GET /api/v1/workflows/{workflow_id}/executions
获取工作流执行历史

**查询参数**:
| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| `page` | integer | 否 | 页码 | 1 |
| `limit` | integer | 否 | 每页数量 | 50 |
| `status` | string | 否 | 执行状态过滤 | - |
| `start_date` | string | 否 | 开始日期 | - |
| `end_date` | string | 否 | 结束日期 | - |
| `sort_by` | string | 否 | 排序字段 | started_at |
| `sort_order` | string | 否 | 排序顺序 | desc |

**响应**:
```json
{
  "executions": [
    {
      "id": "exec_789012",
      "workflow_id": "workflow_123456",
      "status": "completed",
      "input_data": {"customer_query": "产品价格是多少？"},
      "output_data": {"response": "产品价格是999元..."},
      "started_at": "2026-03-20T17:58:00Z",
      "completed_at": "2026-03-20T17:58:02Z",
      "execution_time": 2.5,
      "error_message": null
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

### 插件管理

#### GET /api/v1/plugins
获取插件列表

**响应**:
```json
{
  "plugins": [
    {
      "name": "Slack Integration",
      "version": "1.0.0",
      "description": "Slack消息和文件集成",
      "author": "OpenAgentFlow Team",
      "enabled": true,
      "installed_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z",
      "capabilities": ["messaging", "file_upload"]
    },
    {
      "name": "Machine Learning",
      "version": "1.0.0",
      "description": "机器学习和数据分析功能",
      "author": "OpenAgentFlow Team",
      "enabled": true,
      "installed_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z",
      "capabilities": ["classification", "regression", "data_processing"]
    }
  ]
}
```

#### POST /api/v1/plugins/{plugin_name}/enable
启用插件

**路径参数**:
- `plugin_name`: 插件名称 (必填)

**响应**:
```json
{
  "success": true,
  "message": "插件已启用",
  "plugin": "Slack Integration",
  "enabled": true
}
```

#### POST /api/v1/plugins/{plugin_name}/disable
禁用插件

**路径参数**:
- `plugin_name`: 插件名称 (必填)

**响应**:
```json
{
  "success": true,
  "message": "插件已禁用",
  "plugin": "Slack Integration",
  "enabled": false
}
```

### 工具集成

#### POST /api/v1/tools/feishu/send-message
发送飞书消息

**请求体**:
```json
{
  "receive_id": "ou_123456",
  "receive_id_type": "open_id",
  "msg_type": "text",
  "content": {
    "text": "Hello from OpenAgentFlow!"
  },
  "uuid": "unique_message_id_123",
  "config": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  }
}
```

#### POST /api/v1/tools/dingtalk/send-notification
发送钉钉工作通知

**请求体**:
```json
{
  "agent_id": "agent_123456",
  "userid_list": "user123,user456",
  "dept_id_list": "dept123",
  "to_all_user": false,
  "msg": {
    "msgtype": "text",
    "text": {
      "content": "工作流执行完成：数据分析报告已生成"
    }
  },
  "config": {
    "app_key": "your_app_key",
    "app_secret": "your_app_secret"
  }
}
```

### 系统管理

#### GET /api/v1/system/info
获取系统信息

**响应**:
```json
{
  "name": "OpenAgentFlow",
  "version": "0.1.0",
  "environment": "production",
  "uptime": "5d 3h 12m",
  "memory_usage": "45%",
  "cpu_usage": "22%",
  "database_status": "connected",
  "cache_status": "connected",
  "ai_services": {
    "openai": "available",
    "feishu": "connected",
    "dingtalk": "connected"
  },
  "statistics": {
    "total_agents": 25,
    "total_workflows": 15,
    "total_executions": 1250,
    "active_users": 50
  }
}
```

#### GET /api/v1/system/metrics
获取系统指标

**响应**:
```json
{
  "system": {
    "cpu": {
      "usage": 22.5,
      "cores": 8,
      "load_average": [1.2, 1.5, 1.8]
    },
    "memory": {
      "total": 17179869184,
      "used": 7730941132,
      "free": 9448928048,
      "percentage": 45.0
    },
    "disk": {
      "total": 107374182400,
      "used": 32212254720,
      "free": 75161927680,
      "percentage": 30.0
    }
  },
  "application": {
    "requests_per_second": 12.5,
    "response_time_avg": 150,
    "error_rate": 0.02,
    "active_connections": 45
  }
}
```

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "name",
      "reason": "不能为空",
      "value": null
    },
    "timestamp": "2026-03-20T17:58:00Z",
    "request_id": "req_123456789"
  }
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|--------|------------|------|----------|
| `INVALID_REQUEST` | 400 | 请求参数无效 | 检查请求参数格式 |
| `UNAUTHORIZED` | 401 | 未授权 | 提供有效的认证令牌 |
| `FORBIDDEN` | 403 | 禁止访问 | 检查用户权限 |
| `NOT_FOUND` | 404 | 资源不存在 | 检查资源ID |
| `VALIDATION_FAILED` | 422 | 验证失败 | 检查输入数据 |
| `RATE_LIMITED` | 429 | 请求频率过高 | 降低请求频率 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 | 联系技术支持 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 | 稍后重试 |

## 速率限制

### 默认限制

| 用户类型 | 限制 | 窗口 |
|----------|------|------|
| 匿名用户 | 60 请求/分钟 | 每分钟 |
| 认证用户 | 1000 请求/分钟 | 每分钟 |
| API密钥 | 5000 请求/分钟 | 每分钟 |

### 响应头

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1614589200
Retry-After: 60
```

## WebSocket API

### 连接端点

```
ws://localhost:8000/ws
```

### 连接参数

```javascript
// JavaScript连接示例
const ws = new WebSocket('ws://localhost:8000/ws?token=your_token&client_id=client_123');
```

### 事件类型

#### 客户端 → 服务器
```json
{
  "type": "subscribe",
  "channel": "workflow_updates",
  "workflow_id": "workflow_123456"
}
```

#### 服务器 → 客户端
```json
{
  "type": "workflow_update",
  "workflow_id": "workflow_123456",
  "execution_id": "exec_789012",
  "status": "running",
  "progress": 50,
  "timestamp": "2026-03-20T17:58:00Z"
}
```

### 事件列表

| 事件类型 | 描述 | 数据格式 |
|----------|------|----------|
| `workflow_started` | 工作流开始执行 | `{workflow_id, execution_id}` |
| `workflow_progress` | 工作流进度更新 | `{workflow_id, execution_id, progress, current_node}` |
| `workflow_completed` | 工作流执行完成 | `{workflow_id, execution_id, result, status}` |
| `workflow_failed` | 工作流执行失败 | `{workflow_id, execution_id, error, error_details}` |
| `agent_response` | Agent响应 | `{agent_id, request_id, response, tokens_used}` |
| `system_alert` | 系统告警 | `{level, message, timestamp, details}` |

## 批量操作

### 批量创建Agent

```bash
POST /api/v1/agents/batch
```

**请求体**:
```json
{
  "agents": [
    {
      "name": "客服助手-中文",
      "type": "llm",
      "config": {"model": "gpt-3.5-turbo", "language": "zh-CN"}
    },
    {
      "name": "客服助手-英文",
      "type": "llm",
      "config": {"model": "gpt-3.5-turbo", "language": "en-US"}
    }
  ]
}
```

### 批量执行工作流

```bash
POST /api/v1/workflows/batch-execute
```

**请求体**:
```json
{
  "workflow_id": "workflow_123456",
  "inputs": [
    {"customer_id": "cust_001", "query": "产品价格"},
    {"customer_id": "cust_002", "query": "售后服务"}
  ],
  "parallel": true,
  "max_concurrent": 5
}
```

## 数据导出

### 导出Agent配置

```bash
GET /api/v1/agents/{agent_id}/export
```

**查询参数**:
- `format`: 导出格式 (json, yaml)

### 导出工作流执行历史

```bash
GET /api/v1/workflows/{workflow_id}/executions/export
```

**查询参数**:
- `format`: 导出格式 (json, csv, excel)
- `start_date`: 开始日期
- `end_date`: 结束日期

## API版本控制

### 版本策略

- 使用URL路径版本控制: `/api/v1/`
- 向后兼容性保证
- 弃用通知提前90天

### 当前版本

```
v1 (稳定版)
├── 功能: 完整的Agent和工作流管理
├── 状态: 生产就绪
└── 维护: 长期支持
```

### 未来版本

```
v2 (规划中)
├── 功能: 微服务架构、实时协作
├── 预计发布时间: 2026年Q3
└── 迁移指南: 提供迁移工具
```

## SDK和客户端

### Python SDK

```python
from openagentflow import OpenAgentFlow

# 初始化客户端
client = OpenAgentFlow(
    base_url="http://localhost:8000",
    api_key="your_api_key"
)

# 创建Agent
agent = client.agents.create(
    name="数据分析助手",
    type="llm",
    config={"model": "gpt-3.5-turbo"}
)

# 执行Agent
result = client.agents.execute(
    agent_id=agent.id,
    input="分析销售数据"
)

# 创建工作流
workflow = client.workflows.create(
    name="客户服务流程",
    nodes=[...],
    edges=[...]
)
```

### JavaScript SDK

```javascript
import { OpenAgentFlow } from 'openagentflow';

// 初始化客户端
const client = new OpenAgentFlow({
  baseURL: 'http://localhost:8000',
  apiKey: 'your_api_key'
});

// 创建Agent
const agent = await client.agents.create({
  name: '数据分析助手',
  type: 'llm',
  config: { model: 'gpt-3.5-turbo' }
});

// 执行Agent
const result = await client.agents.execute(agent.id, {
  input: '分析销售数据'
});
```

## 实用工具

### API测试工具

```bash
# 使用curl测试
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "测试消息",
    "parameters": {"temperature": 0.7}
  }'

# 使用httpie测试
http POST http://localhost:8000/api/v1/agents/execute \
  Authorization:"Bearer $API_KEY" \
  input="测试消息" \
  parameters:='{"temperature": 0.7}'
```

### 监控端点

```bash
# 健康检查
curl http://localhost:8000/health

# 性能指标
curl http://localhost:8000/metrics

# 版本信息
curl http://localhost:8000/version
```

## 更新日志

### v0.1.0 (2026-03-20)
- 初始版本发布
- 完整的Agent管理API
- 工作流执行引擎
- 插件系统支持
- 企业工具集成

### v0.2.0 (计划中)
- 批量操作支持
- 实时WebSocket API
- 增强的错误处理
- 性能优化

## 支持

如有问题，请：

1. **查看文档**: [官方文档](https://github.com/worldop123/OpenAgentFlow)
2. **提交Issue**: [GitHub Issues](https://github.com/worldop123/OpenAgentFlow/issues)
3. **社区支持**: [Discord频道](COMMUNITY.md)
4. **商业支持**: [联系销售](COMMERCIAL.md)

## 许可证

本API遵循MIT许可证。详情请查看[LICENSE](../LICENSE)文件。