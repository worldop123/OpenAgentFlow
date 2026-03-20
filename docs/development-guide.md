# 开发指南

## 概述

本指南面向OpenAgentFlow的开发者，涵盖从环境搭建到代码贡献的全过程。

## 开发环境设置

### 系统要求

- **操作系统**: Linux/macOS/Windows (WSL2)
- **Python**: 3.11+
- **Node.js**: 18+ (前端开发)
- **Docker**: 20.10+ (容器化开发)
- **Git**: 2.30+

### 1. 克隆项目

```bash
# 克隆主仓库
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 添加上游仓库（用于贡献）
git remote add upstream https://github.com/worldop123/OpenAgentFlow.git
```

### 2. 设置Python环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. 设置数据库

```bash
# 使用Docker启动数据库
docker-compose up -d postgres redis

# 或手动安装PostgreSQL
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# 创建数据库
createdb openagentflow
```

### 4. 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑配置文件
nano .env
```

**关键配置**:
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/openagentflow

# AI服务配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_MODEL=gpt-3.5-turbo

# 开发模式
DEBUG=true
LOG_LEVEL=debug
```

### 5. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py
```

### 6. 启动开发服务器

```bash
# 启动后端服务
python main.py

# 或使用热重载
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端开发服务器（如果需要）
cd frontend
npm install
npm run dev
```

## 项目结构

### 后端结构

```
backend/
├── agent/              # Agent相关
│   ├── base.py        # Agent基类
│   ├── factory.py     # Agent工厂
│   ├── llm_agent.py   # LLM Agent
│   ├── tool_agent.py  # 工具Agent
│   └── registry.py    # Agent注册表
├── api/               # API端点
│   ├── __init__.py
│   ├── agents.py      # Agent API
│   ├── workflows.py   # 工作流API
│   ├── plugins.py     # 插件API
│   └── system.py      # 系统API
├── database/          # 数据库相关
│   ├── models.py      # 数据模型
│   ├── session.py     # 数据库会话
│   └── migrations/    # 数据库迁移
├── workflow/          # 工作流引擎
│   ├── engine.py      # 工作流引擎
│   ├── instance.py    # 工作流实例
│   ├── node.py       # 节点定义
│   └── executor.py    # 执行器
├── tools/             # 工具集成
│   ├── base.py       # 工具基类
│   ├── feishu.py     # 飞书工具
│   ├── dingtalk.py   # 钉钉工具
│   └── wecom.py      # 企业微信工具
├── plugins/           # 插件系统
│   ├── __init__.py
│   ├── manager.py    # 插件管理器
│   └── base.py       # 插件基类
├── server.py          # FastAPI服务器
└── __init__.py
```

### 前端结构

```
frontend/
├── src/
│   ├── components/    # React组件
│   │   ├── Agent/     # Agent相关组件
│   │   ├── Workflow/  # 工作流相关组件
│   │   └── Common/    # 通用组件
│   ├── pages/         # 页面组件
│   │   ├── Agents/    # Agent管理页面
│   │   ├── Workflows/ # 工作流管理页面
│   │   └── Dashboard/ # 仪表板页面
│   ├── services/      # API服务
│   │   ├── api.ts     # API客户端
│   │   └── agents.ts  # Agent服务
│   ├── stores/        # 状态管理
│   │   └── agentStore.ts
│   ├── types/         # TypeScript类型
│   └── utils/         # 工具函数
├── public/            # 静态资源
└── package.json       # 依赖配置
```

## 开发工作流

### 1. 创建功能分支

```bash
# 同步最新代码
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name

# 或修复Bug
git checkout -b fix/issue-number-description
```

### 2. 实现功能

#### 示例：创建新Agent类型

```python
# backend/agent/custom_agent.py
from typing import Dict, Any
from .base import BaseAgent


class CustomAgent(BaseAgent):
    """自定义Agent示例"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.custom_param = config.get("custom_param", "default")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        # 实现处理逻辑
        result = {
            "input": input_data,
            "processed_by": self.name,
            "custom_param": self.custom_param,
            "timestamp": "2026-03-20T17:58:00Z"
        }
        
        return {
            "success": True,
            "data": result
        }
    
    async def validate(self) -> bool:
        """验证Agent配置"""
        if not self.name:
            return False
        if "custom_param" not in self.config:
            return False
        return True
```

#### 示例：创建新API端点

```python
# backend/api/custom_endpoint.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/custom", tags=["custom"])


class CustomRequest(BaseModel):
    name: str
    value: int


class CustomResponse(BaseModel):
    id: str
    name: str
    result: str


@router.post("/", response_model=CustomResponse)
async def create_custom(data: CustomRequest):
    """创建自定义资源"""
    try:
        # 处理逻辑
        result = f"Processed: {data.name} with value {data.value}"
        
        return CustomResponse(
            id="custom_123",
            name=data.name,
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CustomResponse])
async def list_custom():
    """列出自定义资源"""
    return [
        CustomResponse(id="1", name="test1", result="ok"),
        CustomResponse(id="2", name="test2", result="ok")
    ]
```

### 3. 编写测试

```python
# tests/agent/test_custom_agent.py
import pytest
from unittest.mock import Mock, patch
from backend.agent.custom_agent import CustomAgent


class TestCustomAgent:
    """CustomAgent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建测试Agent"""
        return CustomAgent(
            name="Test Agent",
            config={"custom_param": "test"}
        )
    
    def test_agent_initialization(self, agent):
        """测试Agent初始化"""
        assert agent.name == "Test Agent"
        assert agent.custom_param == "test"
    
    @pytest.mark.asyncio
    async def test_agent_process(self, agent):
        """测试Agent处理"""
        input_data = {"message": "Hello"}
        result = await agent.process(input_data)
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["input"] == input_data
    
    @pytest.mark.asyncio
    async def test_agent_validate(self, agent):
        """测试Agent验证"""
        valid = await agent.validate()
        assert valid is True
        
        # 测试无效配置
        invalid_agent = CustomAgent(name="", config={})
        valid = await invalid_agent.validate()
        assert valid is False
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/agent/test_custom_agent.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=backend --cov-report=html

# 运行特定类型的测试
pytest tests/ -m "not slow"
```

### 5. 代码质量检查

```bash
# 代码格式化
black backend/ tests/
isort backend/ tests/

# 代码检查
flake8 backend/ tests/
mypy backend/

# 安全检查
bandit -r backend/
safety check

# 复杂度检查
radon cc backend/ -a
```

### 6. 提交代码

```bash
# 添加更改
git add .

# 提交更改
git commit -m "feat: 添加自定义Agent类型

- 实现CustomAgent类
- 添加相关API端点
- 编写单元测试
- 更新文档"

# 推送分支
git push origin feature/your-feature-name
```

## 核心概念开发

### Agent开发

#### Agent生命周期

```python
class BaseAgent:
    """Agent基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.state = AgentState.IDLE
        self.metrics = AgentMetrics()
    
    async def initialize(self):
        """初始化Agent"""
        self.state = AgentState.INITIALIZING
        # 初始化逻辑
        self.state = AgentState.READY
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        self.state = AgentState.PROCESSING
        
        try:
            result = await self._process_impl(input_data)
            self.state = AgentState.READY
            self.metrics.record_success()
            return result
        except Exception as e:
            self.state = AgentState.ERROR
            self.metrics.record_error()
            raise
    
    async def cleanup(self):
        """清理资源"""
        self.state = AgentState.CLEANING
        # 清理逻辑
        self.state = AgentState.SHUTDOWN
    
    @abstractmethod
    async def _process_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """实际处理实现"""
        pass
```

#### Agent配置管理

```python
from pydantic import BaseModel, Field
from typing import Optional


class AgentConfig(BaseModel):
    """Agent配置模型"""
    
    model: str = Field(default="gpt-3.5-turbo", description="AI模型")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="最大token数")
    system_prompt: Optional[str] = Field(default=None, description="系统提示")
    tools: list[str] = Field(default=[], description="可用工具列表")
    
    class Config:
        extra = "allow"  # 允许额外字段
```

### 工作流开发

#### 工作流节点定义

```python
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class NodeType(str, Enum):
    """节点类型枚举"""
    INPUT = "input"
    OUTPUT = "output"
    AGENT = "agent"
    CONDITION = "condition"
    TOOL = "tool"
    LOOP = "loop"
    PARALLEL = "parallel"


class NodeData(BaseModel):
    """节点数据模型"""
    
    label: str
    description: Optional[str] = None
    config: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class Node(BaseModel):
    """工作流节点"""
    
    id: str
    type: NodeType
    position: Dict[str, float]  # {x, y}
    data: NodeData
    
    class Config:
        use_enum_values = True
```

#### 工作流执行器

```python
import asyncio
from typing import Dict, Any, List
from collections import deque


class WorkflowExecutor:
    """工作流执行器"""
    
    def __init__(self, workflow_instance):
        self.instance = workflow_instance
        self.context = {}
        self.results = {}
        self.execution_log = []
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        # 1. 验证工作流
        await self._validate()
        
        # 2. 构建执行图
        execution_order = self._build_execution_order()
        
        # 3. 初始化上下文
        self.context = input_data.copy()
        
        # 4. 顺序执行节点
        for node_id in execution_order:
            result = await self._execute_node(node_id)
            self.results[node_id] = result
            
            # 记录执行日志
            self.execution_log.append({
                "node_id": node_id,
                "result": result,
                "timestamp": "2026-03-20T17:58:00Z"
            })
        
        # 5. 返回最终结果
        return self._build_final_result()
    
    async def _execute_node(self, node_id: str) -> Dict[str, Any]:
        """执行单个节点"""
        node = self.instance.get_node(node_id)
        
        if node.type == NodeType.AGENT:
            return await self._execute_agent_node(node)
        elif node.type == NodeType.CONDITION:
            return await self._execute_condition_node(node)
        elif node.type == NodeType.TOOL:
            return await self._execute_tool_node(node)
        else:
            return {"success": True, "data": self.context}
    
    def _build_execution_order(self) -> List[str]:
        """构建执行顺序（拓扑排序）"""
        # 基于节点依赖关系构建执行顺序
        pass
```

### 插件开发

#### 插件基类

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging


class Plugin(ABC):
    """插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = False
        self.config = {}
        self.logger = logging.getLogger(f"plugin.{name}")
        
        # 插件能力
        self.agent_types: List[str] = []
        self.tools: List[Dict[str, Any]] = []
        self.workflow_templates: List[Dict[str, Any]] = []
    
    @abstractmethod
    def on_load(self):
        """插件加载时调用"""
        pass
    
    @abstractmethod
    def on_enable(self):
        """插件启用时调用"""
        pass
    
    @abstractmethod
    def on_disable(self):
        """插件禁用时调用"""
        pass
    
    def register_agent_type(self, agent_type: str, agent_class):
        """注册Agent类型"""
        self.agent_types.append({
            "type": agent_type,
            "class": agent_class,
            "plugin": self.name
        })
        self.logger.info(f"注册Agent类型: {agent_type}")
    
    def register_tool(self, tool_name: str, tool_func, description: str = ""):
        """注册工具"""
        self.tools.append({
            "name": tool_name,
            "function": tool_func,
            "description": description,
            "plugin": self.name
        })
        self.logger.info(f"注册工具: {tool_name}")
```

#### 插件示例：天气插件

```python
# plugins/weather_plugin.py
import aiohttp
from typing import Dict, Any
from backend.plugins import Plugin


class WeatherPlugin(Plugin):
    """天气插件"""
    
    def __init__(self):
        super().__init__("Weather", "1.0.0")
        self.description = "天气预报和气象数据"
        self.author = "OpenAgentFlow Team"
        self.api_key = None
    
    def on_load(self):
        """插件加载"""
        self.logger.info("天气插件正在加载...")
        
        # 注册工具
        self.register_tool(
            "get_weather",
            self.get_weather,
            "获取天气预报"
        )
        
        self.register_tool(
            "get_forecast",
            self.get_forecast,
            "获取天气预报（多天）"
        )
        
        # 检查配置
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            self.logger.warning("天气API密钥未配置")
    
    def on_enable(self):
        """插件启用"""
        self.logger.info("天气插件已启用")
        self.enabled = True
    
    def on_disable(self):
        """插件禁用"""
        self.logger.info("天气插件已禁用")
        self.enabled = False
    
    async def get_weather(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气"""
        city = context.get("city", "北京")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.weather.com/v1/{city}",
                    params={"apikey": self.api_key}
                ) as response:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "city": city,
                        "temperature": data.get("temp"),
                        "condition": data.get("condition"),
                        "humidity": data.get("humidity"),
                        "wind_speed": data.get("wind_speed")
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "city": city
            }
    
    async def get_forecast(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气预报"""
        city = context.get("city", "北京")
        days = context.get("days", 3)
        
        # 实现逻辑
        return {
            "success": True,
            "city": city,
            "forecast": [
                {"day": 1, "temp": 25, "condition": "sunny"},
                {"day": 2, "temp": 23, "condition": "cloudy"},
                {"day": 3, "temp": 20, "condition": "rain"}
            ]
        }


# 插件实例
plugin = WeatherPlugin()
```

## 测试策略

### 单元测试

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestExample:
    """示例测试类"""
    
    @pytest.fixture
    def mock_service(self):
        """创建模拟服务"""
        return Mock()
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """测试异步函数"""
        result = await some_async_function()
        assert result == expected_value
    
    def test_with_mock(self, mock_service):
        """使用模拟对象测试"""
        mock_service.process.return_value = "mocked"
        
        result = function_under_test(mock_service)
        
        assert result == "mocked"
        mock_service.process.assert_called_once()
    
    @patch('module.function_to_patch')
    def test_with_patch(self, mock_function):
        """使用patch测试"""
        mock_function.return_value = "patched"
        
        result = test_function()
        
        assert result == "patched"
```

### 集成测试

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from backend.database import Base


class TestAPI:
    """API集成测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 使用测试数据库
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # 创建表
        Base.metadata.create_all(bind=engine)
        
        # 创建测试客户端
        client = TestClient(app)
        
        yield client
        
        # 清理
        Base.metadata.drop_all(bind=engine)
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_agent(self, client):
        """测试创建Agent"""
        agent_data = {
            "name": "Test Agent",
            "type": "llm",
            "config": {"model": "gpt-3.5-turbo"}
        }
        
        response = client.post("/api/v1/agents", json=agent_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["type"] == "llm"
```

### 端到端测试

```python
# tests/e2e/test_workflow.py
import pytest
import asyncio
from typing import Dict, Any


class TestWorkflowE2E:
    """工作流端到端测试"""
    
    @pytest.fixture
    async def workflow_engine(self):
        """创建工作流引擎"""
        from backend.workflow.engine import WorkflowEngine
        engine = WorkflowEngine()
        yield engine
        await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, workflow_engine):
        """测试完整工作流"""
        # 1. 创建工作流
        workflow = workflow_engine.create_workflow(
            name="测试工作流",
            description="端到端测试"
        )
        
        # 2. 添加节点
        workflow.add_node({
            "id": "start",
            "type": "input",
            "data": {"label": "开始"}
        })
        
        # 3. 执行工作流
        input_data = {"message": "Hello"}
        result = await workflow_engine.execute_workflow(
            workflow.id,
            input_data
        )
        
        # 4. 验证结果
        assert result["success"] is True
        assert "execution_id" in result
        assert result["workflow_id"] == workflow.id
```

## 性能优化

### 数据库优化

```python
# 使用连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)

# 批量操作
async def batch_create_agents(agents_data: List[Dict[str, Any]]):
    """批量创建Agent"""
    async with SessionLocal() as session:
        agents = [
            Agent(**data) for data in agents_data
        ]
        session.add_all(agents)
        await session.commit()
```

### 缓存优化

```python
from redis import asyncio as aioredis
import json


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """连接Redis"""
        self.redis = await aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get_with_cache(self, key: str, ttl: int = 300):
        """带缓存的获取"""
        # 尝试从缓存获取
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # 缓存未命中，从数据库获取
        data = await self._get_from_db(key)
        
        # 存入缓存
        await self.redis.setex(
            key,
            ttl,
            json.dumps(data)
        )
        
        return data
```

### 异步优化

```python
import asyncio
from typing import List


async def process_concurrently(tasks: List, max_concurrent: int = 10):
    """并发处理任务"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(task):
        async with semaphore:
            return await process_task(task)
    
    # 使用gather并发执行
    results = await asyncio.gather(
        *[process_with_semaphore(task) for task in tasks],
        return_exceptions=True
    )
    
    return results
```

## 调试技巧

### 日志调试

```python
import logging
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 使用结构化日志
logger.info(
    "agent_execution_start",
    agent_id=agent_id,
    input_size=len(input_data),
    user_id=user_id
)
```

### 调试工具

```python
# 使用pdb调试
import pdb

def debug_function():
    pdb.set_trace()  # 设置断点
    # 调试代码

# 使用调试器
python -m pdb main.py

# 使用ipdb（增强版pdb）
import ipdb
ipdb.set_trace()
```

### 性能分析

```python
import cProfile
import pstats

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 运行代码
result = await workflow_engine.execute_workflow(workflow_id, input_data)

profiler.disable()

# 分析结果
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 代码审查

### 审查清单

1. **代码质量**
   - 遵循PEP 8规范
   - 有意义的变量名
   - 适当的注释
   - 无重复代码

2. **功能正确性**
   - 实现需求功能
   - 边界条件处理
   - 错误处理
   - 测试覆盖

3. **性能考虑**
   - 数据库查询优化
   - 缓存使用
   - 并发处理
   - 内存使用

4. **安全性**
   - 输入验证
   - SQL注入防护
   - XSS防护
   - 权限检查

5. **可维护性**
   - 模块化设计
   - 清晰的接口
   - 文档完整
   - 易于测试

### 审查示例

```python
# 审查前
def process_data(data):
    # 复杂的嵌套逻辑
    result = []
    for item in data:
        if item['status'] == 'active':
            if item['value'] > 0:
                result.append(item['value'] * 2)
    return sum(result)

# 审查后
def process_data(data: List[Dict]) -> float:
    """处理有效数据的平均值"""
    active_items = [
        item for item in data 
        if item['status'] == 'active' and item['value'] > 0
    ]
    
    if not active_items:
        return 0.0
    
    doubled_values = [item['value'] * 2 for item in active_items]
    return sum(doubled_values) / len(doubled_values)
```

## 部署准备

### 版本管理

```bash
# 更新版本号
# 在 setup.py 或 pyproject.toml 中更新版本

# 创建发布标签
git tag -a v0.1.0 -m "版本 0.1.0"
git push origin v0.1.0

# 更新CHANGELOG.md
# 描述新功能、修复和破坏性变更
```

### 文档更新

```bash
# 生成API文档
python -c "import json; from main import app; print(json.dumps(app.openapi()))" > openapi.json

# 生成文档网站
mkdocs build

# 部署文档
mkdocs gh-deploy
```

### 发布检查清单

1. [ ] 所有测试通过
2. [ ] 代码质量检查通过
3. [ ] 文档更新完成
4. [ ] 版本号已更新
5. [ ] CHANGELOG已更新
6. [ ] 依赖已更新
7. [ ] 迁移脚本已测试
8. [ ] 回滚方案已准备

## 贡献流程

### 1. Fork项目
在GitHub上fork项目到您的账户

### 2. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 3. 开发功能
- 编写代码
- 添加测试
- 更新文档

### 4. 提交更改
```bash
git add .
git commit -m "feat: 描述您的功能"
git push origin feature/your-feature-name
```

### 5. 创建Pull Request
在GitHub上创建Pull Request，包含：
- 功能描述
- 相关Issue链接
- 测试结果
- 文档更新

### 6. 代码审查
- 等待维护者审查
- 根据反馈修改代码
- 确保CI通过

### 7. 合并
- 维护者合并PR
- 删除功能分支
- 庆祝贡献！🎉

## 获取帮助

- **文档**: [官方文档](https://github.com/worldop123/OpenAgentFlow)
- **问题**: [GitHub Issues](https://github.com/worldop123/OpenAgentFlow/issues)
- **讨论**: [Discord频道](COMMUNITY.md)
- **示例**: [示例代码](../examples/)

祝您开发愉快！🚀