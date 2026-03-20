# 用户指南

欢迎使用OpenAgentFlow！本指南将帮助您快速上手并充分利用平台的所有功能。

## 快速开始

### 第一步：安装和部署

#### 使用Docker（推荐）
```bash
# 克隆项目
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件，配置您的API密钥

# 启动服务
docker-compose up -d

# 访问应用
# 前端界面: http://localhost:8000
# API文档: http://localhost:8000/docs
```

#### 本地安装
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
python main.py
```

### 第二步：配置AI服务

在`.env`文件中配置您的AI服务：

```bash
# OpenAI配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_MODEL=gpt-3.5-turbo

# 飞书配置（可选）
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 钉钉配置（可选）
DINGTALK_APP_KEY=your_app_key
DINGTALK_APP_SECRET=your_app_secret

# 企业微信配置（可选）
WECOM_CORP_ID=your_corp_id
WECOM_CORP_SECRET=your_corp_secret
```

## 核心概念

### 什么是Agent？

Agent是OpenAgentFlow中的智能执行单元，每个Agent都有特定的功能：

- **LLM Agent**: 基于大语言模型的智能助手
- **工具Agent**: 执行特定任务的工具
- **条件Agent**: 根据条件做出决策
- **插件Agent**: 通过插件扩展的功能

### 什么是工作流？

工作流是由多个节点组成的执行流程：

```
输入 → Agent处理 → 条件判断 → 多个分支 → 输出
```

## 基础操作

### 创建第一个Agent

#### 通过Web界面
1. 访问 `http://localhost:8000`
2. 点击左侧菜单的 "AI Agent"
3. 点击 "创建Agent" 按钮
4. 填写Agent信息：
   - 名称: 客服助手
   - 类型: LLM Agent
   - 模型: gpt-3.5-turbo
   - 系统提示: "你是一个专业的客服助手..."
5. 点击 "保存"

#### 通过API
```bash
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "客服助手",
    "description": "处理客户咨询",
    "type": "llm",
    "config": {
      "model": "gpt-3.5-turbo",
      "temperature": 0.7
    }
  }'
```

### 测试Agent

#### 在Web界面测试
1. 在Agent列表中找到您的Agent
2. 点击 "测试" 按钮
3. 输入测试内容: "你好，我想咨询产品价格"
4. 查看AI的回复

#### 通过API测试
```bash
curl -X POST http://localhost:8000/api/v1/agents/{agent_id}/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你好，我想咨询产品价格",
    "parameters": {
      "temperature": 0.7
    }
  }'
```

## 创建工作流

### 使用可视化设计器

1. **访问工作流设计器**
   - 点击左侧菜单的 "工作流"
   - 点击 "新建工作流"

2. **添加节点**
   - 从左侧面板拖拽节点到画布
   - 节点类型包括：
     - 输入节点: 工作流起点
     - 输出节点: 工作流终点
     - Agent节点: 执行AI任务
     - 条件节点: 根据条件分支
     - 工具节点: 调用外部工具

3. **连接节点**
   - 点击节点的输出端口
   - 拖动到目标节点的输入端口

4. **配置节点**
   - 双击节点进行配置
   - 为Agent节点选择具体的Agent
   - 设置条件和参数

5. **保存工作流**
   - 点击右上角 "保存"
   - 输入工作流名称和描述

### 示例工作流：客户服务流程

创建一个简单的客户服务工作流：

```
客户咨询 → AI回复 → 满意度检查 → [满意] 结束 / [不满意] 人工客服
```

**步骤**:
1. 添加 "输入节点"，命名为 "客户咨询"
2. 添加 "Agent节点"，选择 "客服助手" Agent
3. 添加 "条件节点"，设置条件为 "满意度 >= 8"
4. 添加两个 "输出节点"，分别命名为 "服务完成" 和 "转人工客服"
5. 连接所有节点

### 执行工作流

#### 在Web界面执行
1. 在工作流列表中找到您的工作流
2. 点击 "执行" 按钮
3. 输入测试数据
4. 查看执行结果和流程图

#### 通过API执行
```bash
curl -X POST http://localhost:8000/api/v1/workflows/{workflow_id}/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "customer_query": "产品价格是多少？",
      "customer_id": "cust_123"
    }
  }'
```

## 企业工具集成

### 飞书集成

#### 配置飞书应用
1. 在飞书开放平台创建应用
2. 获取 App ID 和 App Secret
3. 在 `.env` 文件中配置：
   ```
   FEISHU_APP_ID=your_app_id
   FEISHU_APP_SECRET=your_app_secret
   ```

#### 使用飞书工具
```python
from backend.tools.feishu import FeishuTool

# 初始化工具
feishu = FeishuTool(app_id="your_app_id", app_secret="your_app_secret")

# 发送消息
await feishu.send_message(
    user_id="ou_xxx",
    message="Hello from OpenAgentFlow!"
)

# 创建日程
await feishu.create_calendar_event(
    summary="团队会议",
    start_time="2026-03-21T10:00:00+08:00",
    end_time="2026-03-21T11:00:00+08:00",
    attendees=["ou_xxx", "ou_yyy"]
)
```

#### 在工作流中使用飞书
1. 在工作流中添加 "工具节点"
2. 选择 "飞书工具"
3. 配置具体操作（发送消息、创建日程等）
4. 连接其他节点

### 钉钉集成

#### 配置钉钉机器人
1. 在钉钉开放平台创建机器人
2. 获取 Webhook URL
3. 在工作流中使用钉钉节点

### 企业微信集成

#### 配置企业微信应用
1. 在企业微信管理后台创建应用
2. 获取 Corp ID 和 Secret
3. 配置环境变量

## 插件系统

### 安装插件

#### 从插件市场安装
1. 访问 "插件市场"
2. 浏览可用插件
3. 点击 "安装" 按钮

#### 手动安装
1. 将插件文件复制到 `plugins/` 目录
2. 重启服务
3. 在Web界面启用插件

### 使用插件

#### Slack插件示例
```python
# 在Python代码中使用
from plugins.slack_plugin import SlackPlugin

# 初始化插件
slack = SlackPlugin()
slack.on_enable()

# 发送消息
await slack.send_message({
    "channel": "#general",
    "text": "工作流执行完成！"
})
```

#### 机器学习插件示例
```python
from plugins.ml_plugin import MLPlugin

# 初始化插件
ml = MLPlugin()
ml.on_enable()

# 使用机器学习功能
result = await ml.data_preprocessing({
    "data": [[1, 2, 3], [4, 5, 6]]
})
```

### 开发自定义插件

参考 [插件开发指南](plugin-development.md)

## 高级功能

### 条件分支

在工作流中使用条件节点实现智能决策：

```json
{
  "id": "condition_1",
  "type": "condition",
  "data": {
    "label": "满意度检查",
    "condition": "input.satisfaction_score >= 8",
    "true_branch": "high_satisfaction",
    "false_branch": "low_satisfaction"
  }
}
```

### 循环执行

使用循环节点处理重复任务：

```json
{
  "id": "loop_1",
  "type": "loop",
  "data": {
    "label": "处理列表",
    "items": "input.data_list",
    "item_var": "current_item",
    "max_iterations": 100
  }
}
```

### 并行处理

使用并行节点同时执行多个任务：

```json
{
  "id": "parallel_1",
  "type": "parallel",
  "data": {
    "label": "并行处理",
    "branches": [
      {"name": "分析数据", "agent_id": "analyst"},
      {"name": "生成报告", "agent_id": "reporter"},
      {"name": "发送通知", "agent_id": "notifier"}
    ]
  }
}
```

## 数据管理

### 数据源配置

1. **数据库连接**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/openagentflow
   ```

2. **API数据源**
   ```json
   {
     "name": "销售数据API",
     "type": "rest_api",
     "url": "https://api.example.com/sales",
     "auth_type": "bearer_token",
     "auth_token": "your_token"
   }
   ```

### 数据转换

使用数据转换节点处理数据：

```json
{
  "id": "transform_1",
  "type": "transform",
  "data": {
    "label": "数据清洗",
    "operations": [
      {"type": "filter", "condition": "price > 0"},
      {"type": "map", "expression": "item.price * 0.9"},
      {"type": "aggregate", "field": "price", "operation": "sum"}
    ]
  }
}
```

## 监控和日志

### 查看执行历史

1. 访问 "监控" 页面
2. 查看工作流执行历史
3. 筛选和搜索特定执行

### 查看日志

#### Web界面
1. 访问 "系统日志" 页面
2. 查看实时日志
3. 按级别筛选

#### 命令行
```bash
# 查看Docker日志
docker-compose logs -f openagentflow

# 查看特定服务日志
docker-compose logs openagentflow --tail=100
```

### 性能监控

1. **系统状态**
   - CPU使用率
   - 内存使用率
   - 磁盘空间

2. **业务指标**
   - 工作流执行次数
   - Agent调用次数
   - 平均响应时间
   - 错误率

## 安全和权限

### 用户认证

#### API密钥认证
```bash
# 生成API密钥
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "name": "生产环境密钥",
    "scopes": ["agents:read", "workflows:execute"]
  }'
```

#### JWT认证
```bash
# 获取访问令牌
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

### 权限控制

基于角色的访问控制（RBAC）：

- **管理员**: 所有权限
- **开发者**: 创建和执行工作流
- **操作员**: 执行工作流
- **查看者**: 只读权限

### 数据加密

- 配置文件加密
- 数据库字段加密
- 传输数据加密（HTTPS）

## 故障排除

### 常见问题

#### 1. 服务启动失败
**症状**: Docker容器无法启动
**解决方案**:
```bash
# 检查日志
docker-compose logs

# 检查端口占用
netstat -tulpn | grep :8000

# 重新构建镜像
docker-compose build --no-cache
```

#### 2. AI服务连接失败
**症状**: Agent无法调用AI模型
**解决方案**:
```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试API连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 3. 数据库连接失败
**症状**: 无法访问数据库
**解决方案**:
```bash
# 检查数据库服务
docker-compose ps postgres

# 检查连接字符串
echo $DATABASE_URL

# 重启数据库
docker-compose restart postgres
```

### 调试模式

启用调试模式获取更多信息：

```bash
# 设置环境变量
DEBUG=true
LOG_LEVEL=debug

# 重启服务
docker-compose restart openagentflow
```

### 获取帮助

1. **查看文档**: [官方文档](https://github.com/worldop123/OpenAgentFlow)
2. **提交Issue**: [GitHub Issues](https://github.com/worldop123/OpenAgentFlow/issues)
3. **社区支持**: [Discord频道](COMMUNITY.md)

## 最佳实践

### 工作流设计

1. **保持简单**: 每个工作流专注于一个业务目标
2. **错误处理**: 添加错误处理节点
3. **日志记录**: 记录关键步骤的执行结果
4. **性能优化**: 避免不必要的节点

### Agent设计

1. **明确职责**: 每个Agent专注于特定任务
2. **参数化配置**: 通过参数控制行为
3. **错误恢复**: 实现重试机制
4. **资源管理**: 控制API调用频率

### 部署建议

1. **生产环境**: 使用Docker Compose或Kubernetes
2. **监控报警**: 设置关键指标监控
3. **备份策略**: 定期备份数据和配置
4. **安全加固**: 启用HTTPS和访问控制

## 更新和升级

### 版本升级

```bash
# 备份数据
./deploy.sh backup

# 更新代码
git pull origin main

# 重新构建
docker-compose build

# 重启服务
docker-compose up -d
```

### 数据迁移

1. **导出数据**
   ```bash
   ./deploy.sh backup
   ```

2. **导入数据**
   ```bash
   ./deploy.sh restore /path/to/backup
   ```

## 下一步

- 探索 [高级功能](advanced-features.md)
- 学习 [插件开发](plugin-development.md)
- 加入 [社区](COMMUNITY.md)
- 查看 [商业支持](COMMERCIAL.md)

祝您使用愉快！🚀