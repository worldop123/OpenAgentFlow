# 插件开发指南

欢迎来到OpenAgentFlow插件开发指南！本指南将帮助您创建自定义插件来扩展平台功能。

## 概述

OpenAgentFlow的插件系统允许您：
- 添加新的Agent类型
- 集成外部工具和服务
- 提供工作流模板
- 扩展系统功能

## 插件架构

### 插件类型

1. **Agent插件**: 添加新的Agent类型
2. **工具插件**: 集成外部工具
3. **工作流插件**: 提供预定义工作流模板
4. **系统插件**: 扩展系统功能

### 插件结构

```
my_plugin/
├── __init__.py
├── plugin.py          # 主插件文件
├── agents.py          # Agent实现
├── tools.py           # 工具实现
├── workflows.py       # 工作流模板
├── config.yaml        # 插件配置
└── README.md          # 插件说明
```

## 开发环境设置

### 1. 创建开发环境

```bash
# 克隆OpenAgentFlow
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 创建插件目录

```bash
# 在plugins目录下创建新插件
mkdir -p plugins/my_plugin
cd plugins/my_plugin
```

## 创建第一个插件

### 1. 创建插件基类

```python
# plugins/my_plugin/plugin.py
import logging
from typing import Dict, Any
from backend.plugins import Plugin

logger = logging.getLogger(__name__)


class MyPlugin(Plugin):
    """我的第一个插件"""
    
    def __init__(self):
        super().__init__("MyPlugin", "1.0.0")
        self.description = "我的第一个OpenAgentFlow插件"
        self.author = "Your Name"
        self.website = "https://github.com/yourusername"
    
    def on_load(self):
        """插件加载时调用"""
        logger.info(f"插件 {self.name} v{self.version} 正在加载...")
        
        # 注册功能
        self.register_agent_type("my_agent", MyAgent)
        self.register_tool("my_tool", self.my_tool_function, "我的工具函数")
        
        logger.info(f"插件 {self.name} 加载完成")
    
    def on_enable(self):
        """插件启用时调用"""
        logger.info(f"插件 {self.name} 已启用")
        
        # 检查配置
        if not self.config.get("api_key"):
            logger.warning("API密钥未配置")
    
    def on_disable(self):
        """插件禁用时调用"""
        logger.info(f"插件 {self.name} 已禁用")
    
    # 工具函数示例
    async def my_tool_function(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """我的工具函数示例"""
        input_data = context.get("input", "")
        return {
            "success": True,
            "result": f"处理结果: {input_data}",
            "processed_by": self.name
        }


# 插件实例
plugin = MyPlugin()
```

### 2. 创建Agent类

```python
# plugins/my_plugin/agents.py
from typing import Dict, Any
from backend.agent.base import BaseAgent


class MyAgent(BaseAgent):
    """自定义Agent示例"""
    
    def __init__(self, name: str, custom_param: str = "default"):
        super().__init__(name)
        self.custom_param = custom_param
        self.initialized = False
    
    async def initialize(self):
        """初始化Agent"""
        if not self.initialized:
            # 执行初始化逻辑
            self.initialized = True
            return {"success": True, "message": "Agent已初始化"}
        return {"success": True, "message": "Agent已经初始化"}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        try:
            # 处理逻辑
            result = {
                "input": input_data,
                "processed_by": self.name,
                "custom_param": self.custom_param,
                "timestamp": "2026-03-20T17:42:00Z"
            }
            
            # 可以调用其他服务或API
            if self.config.get("call_external_api", False):
                external_result = await self.call_external_api(input_data)
                result["external_result"] = external_result
            
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "agent": self.name,
                    "version": "1.0.0"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def call_external_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用外部API示例"""
        # 这里实现实际的API调用
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.example.com/process",
                json=data,
                headers={"Authorization": f"Bearer {self.config.get('api_key')}"}
            ) as response:
                return await response.json()
    
    async def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        errors = []
        
        if not self.name:
            errors.append("Agent名称不能为空")
        
        if self.config.get("api_key") and len(self.config["api_key"]) < 10:
            errors.append("API密钥太短")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": [] if errors else ["配置验证通过"]
        }
```

### 3. 创建工具类

```python
# plugins/my_plugin/tools.py
from typing import Dict, Any, List, Optional
import aiohttp
import json


class MyTool:
    """自定义工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
    
    async def initialize(self):
        """初始化工具"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理数据"""
        try:
            # 数据验证
            if not data:
                return {"success": False, "error": "数据不能为空"}
            
            # 处理逻辑
            processed = []
            for item in data:
                processed_item = self._process_item(item)
                processed.append(processed_item)
            
            return {
                "success": True,
                "processed_count": len(processed),
                "data": processed,
                "summary": {
                    "total_items": len(data),
                    "valid_items": len(processed)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个数据项"""
        # 这里实现具体的处理逻辑
        processed = item.copy()
        
        # 示例：添加处理时间戳
        processed["processed_at"] = "2026-03-20T17:42:00Z"
        
        # 示例：数据转换
        if "value" in processed:
            processed["value_double"] = processed["value"] * 2
        
        return processed
    
    async def call_webhook(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用Webhook"""
        try:
            await self.initialize()
            
            async with self.session.post(url, json=data) as response:
                status = response.status
                response_data = await response.json()
                
                return {
                    "success": 200 <= status < 300,
                    "status_code": status,
                    "data": response_data,
                    "headers": dict(response.headers)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### 4. 创建工作流模板

```python
# plugins/my_plugin/workflows.py
from typing import Dict, Any, List


class WorkflowTemplates:
    """工作流模板"""
    
    @staticmethod
    def get_data_processing_template() -> Dict[str, Any]:
        """数据处理工作流模板"""
        return {
            "name": "数据处理流程",
            "description": "标准的数据处理工作流",
            "nodes": [
                {
                    "id": "data_input",
                    "type": "input",
                    "data": {
                        "label": "数据输入",
                        "description": "输入原始数据"
                    }
                },
                {
                    "id": "data_validation",
                    "type": "agent",
                    "data": {
                        "label": "数据验证",
                        "agent_id": "data_validator",
                        "parameters": {
                            "validation_rules": {
                                "required_fields": ["id", "name", "value"],
                                "value_range": {"min": 0, "max": 1000}
                            }
                        }
                    }
                },
                {
                    "id": "data_processing",
                    "type": "agent",
                    "data": {
                        "label": "数据处理",
                        "agent_id": "my_agent",
                        "parameters": {
                            "processing_type": "normalize",
                            "output_format": "json"
                        }
                    }
                },
                {
                    "id": "result_output",
                    "type": "output",
                    "data": {
                        "label": "结果输出",
                        "description": "输出处理结果"
                    }
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "data_input",
                    "target": "data_validation",
                    "label": "原始数据"
                },
                {
                    "id": "e2",
                    "source": "data_validation",
                    "target": "data_processing",
                    "label": "验证通过"
                },
                {
                    "id": "e3",
                    "source": "data_processing",
                    "target": "result_output",
                    "label": "处理结果"
                }
            ],
            "settings": {
                "timeout": 300,
                "retry_count": 3,
                "concurrent_executions": 5
            }
        }
    
    @staticmethod
    def get_notification_template() -> Dict[str, Any]:
        """通知工作流模板"""
        return {
            "name": "通知流程",
            "description": "事件触发通知的工作流",
            "nodes": [
                {
                    "id": "event_trigger",
                    "type": "input",
                    "data": {
                        "label": "事件触发",
                        "description": "监控事件触发"
                    }
                },
                {
                    "id": "event_analysis",
                    "type": "agent",
                    "data": {
                        "label": "事件分析",
                        "agent_id": "event_analyzer",
                        "parameters": {
                            "analysis_type": "severity",
                            "threshold": 0.8
                        }
                    }
                },
                {
                    "id": "notification_decision",
                    "type": "condition",
                    "data": {
                        "label": "通知决策",
                        "condition": "severity >= 0.7",
                        "true_branch": "send_notification",
                        "false_branch": "log_only"
                    }
                },
                {
                    "id": "send_notification",
                    "type": "agent",
                    "data": {
                        "label": "发送通知",
                        "agent_id": "notifier",
                        "parameters": {
                            "channels": ["email", "slack"],
                            "priority": "high"
                        }
                    }
                },
                {
                    "id": "log_only",
                    "type": "agent",
                    "data": {
                        "label": "仅记录日志",
                        "agent_id": "logger",
                        "parameters": {
                            "log_level": "info"
                        }
                    }
                },
                {
                    "id": "process_complete",
                    "type": "output",
                    "data": {
                        "label": "处理完成",
                        "description": "通知流程完成"
                    }
                }
            ],
            "edges": [
                {"id": "e1", "source": "event_trigger", "target": "event_analysis"},
                {"id": "e2", "source": "event_analysis", "target": "notification_decision"},
                {"id": "e3", "source": "notification_decision", "target": "send_notification"},
                {"id": "e4", "source": "notification_decision", "target": "log_only"},
                {"id": "e5", "source": "send_notification", "target": "process_complete"},
                {"id": "e6", "source": "log_only", "target": "process_complete"}
            ]
        }
```

### 5. 插件配置文件

```yaml
# plugins/my_plugin/config.yaml
plugin:
  name: "MyPlugin"
  version: "1.0.0"
  description: "我的自定义插件"
  author: "Your Name"
  website: "https://github.com/yourusername"
  
  dependencies:
    python:
      - "aiohttp>=3.8.0"
      - "pydantic>=2.0.0"
    
    system:
      - "redis"
      - "postgresql"
  
  configuration:
    api_key:
      type: "string"
      required: true
      description: "API访问密钥"
    
    endpoint:
      type: "string"
      required: false
      default: "https://api.example.com"
      description: "API端点"
    
    timeout:
      type: "integer"
      required: false
      default: 30
      description: "请求超时时间（秒）"
  
  permissions:
    - "agents:create"
    - "agents:execute"
    - "tools:use"
    - "workflows:read"
  
  hooks:
    - "on_workflow_start"
    - "on_workflow_complete"
    - "on_agent_execute"
```

## 插件测试

### 1. 单元测试

```python
# tests/plugins/test_my_plugin.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from plugins.my_plugin.plugin import MyPlugin
from plugins.my_plugin.agents import MyAgent


class TestMyPlugin:
    """MyPlugin测试类"""
    
    def test_plugin_initialization(self):
        """测试插件初始化"""
        plugin = MyPlugin()
        
        assert plugin.name == "MyPlugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "我的第一个OpenAgentFlow插件"
        assert plugin.author == "Your Name"
    
    def test_plugin_on_load(self):
        """测试插件加载"""
        plugin = MyPlugin()
        
        with patch.object(plugin, 'register_agent_type') as mock_register:
            with patch('logging.getLogger') as mock_logger:
                plugin.on_load()
                
                # 验证Agent类型被注册
                mock_register.assert_called()
    
    @pytest.mark.asyncio
    async def test_my_tool_function(self):
        """测试工具函数"""
        plugin = MyPlugin()
        
        context = {"input": "测试数据"}
        result = await plugin.my_tool_function(context)
        
        assert result["success"] is True
        assert "处理结果" in result["result"]
        assert result["processed_by"] == "MyPlugin"


class TestMyAgent:
    """MyAgent测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建测试Agent"""
        return MyAgent(name="测试Agent", custom_param="test")
    
    def test_agent_initialization(self, agent):
        """测试Agent初始化"""
        assert agent.name == "测试Agent"
        assert agent.custom_param == "test"
        assert agent.initialized is False
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, agent):
        """测试Agent初始化方法"""
        result = await agent.initialize()
        
        assert result["success"] is True
        assert agent.initialized is True
    
    @pytest.mark.asyncio
    async def test_agent_process(self, agent):
        """测试Agent处理"""
        input_data = {"message": "Hello"}
        
        with patch.object(agent, 'call_external_api', new_callable=AsyncMock) as mock_api:
            mock_api.return_value = {"api_result": "success"}
            
            result = await agent.process(input_data)
            
            assert result["success"] is True
            assert result["data"]["input"] == input_data
            assert result["data"]["custom_param"] == "test"
    
    @pytest.mark.asyncio
    async def test_agent_validate_config(self, agent):
        """测试配置验证"""
        # 测试有效配置
        agent.name = "ValidAgent"
        agent.config = {"api_key": "valid_api_key_12345"}
        
        result = await agent.validate_config()
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
        # 测试无效配置
        agent.name = ""
        agent.config = {"api_key": "short"}
        
        result = await agent.validate_config()
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
```

### 2. 集成测试

```python
# tests/plugins/test_integration.py
import pytest
import asyncio
from backend.plugins import plugin_manager
from plugins.my_plugin.plugin import plugin as my_plugin


class TestPluginIntegration:
    """插件集成测试"""
    
    @pytest.fixture
    def manager(self):
        """创建插件管理器"""
        return plugin_manager
    
    @pytest.mark.asyncio
    async def test_plugin_loading(self, manager):
        """测试插件加载"""
        # 加载插件
        manager.load_plugin("my_plugin")
        
        # 验证插件已加载
        plugin = manager.get_plugin("MyPlugin")
        assert plugin is not None
        assert plugin.name == "MyPlugin"
    
    @pytest.mark.asyncio
    async def test_plugin_enable_disable(self, manager):
        """测试插件启用和禁用"""
        # 启用插件
        success = manager.enable_plugin("MyPlugin")
        assert success is True
        
        plugin = manager.get_plugin("MyPlugin")
        assert plugin.enabled is True
        
        # 禁用插件
        success = manager.disable_plugin("MyPlugin")
        assert success is True
        assert plugin.enabled is False
    
    @pytest.mark.asyncio
    async def test_plugin_tools(self, manager):
        """测试插件工具"""
        plugin = manager.get_plugin("MyPlugin")
        
        # 验证工具已注册
        assert hasattr(plugin, "tools")
        assert len(plugin.tools) > 0
        
        # 测试工具调用
        tool_result = await plugin.my_tool_function({"input": "测试"})
        assert tool_result["success"] is True
```

## 插件部署

### 1. 打包插件

```bash
# 创建插件包
cd plugins/my_plugin
tar -czvf my_plugin-1.0.0.tar.gz .

# 或使用Python打包
python setup.py sdist bdist_wheel
```

### 2. 安装插件

#### 手动安装
```bash
# 复制插件文件
cp -r my_plugin/ /path/to/openagentflow/plugins/

# 重启服务
docker-compose restart openagentflow
```

#### 通过插件市场安装
1. 将插件发布到插件市场
2. 在Web界面点击"安装"
3. 系统自动下载和安装

### 3. 插件配置

在Web界面配置插件：
1. 访问"插件管理"
2. 找到您的插件
3. 点击"配置"
4. 输入配置参数
5. 点击"保存"

## 最佳实践

### 1. 代码质量

- 遵循PEP 8规范
- 添加类型注解
- 编写文档字符串
- 实现错误处理

### 2. 性能优化

- 使用异步编程
- 实现连接池
- 缓存频繁访问的数据
- 优化数据库查询

### 3. 安全性

- 验证输入数据
- 安全存储敏感信息
- 实现访问控制
- 记录安全日志

### 4. 可维护性

- 模块化设计
- 配置驱动
- 完整的测试覆盖
- 清晰的错误信息

## 调试和故障排除

### 1. 调试插件

```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 添加调试点
import pdb
pdb.set_trace()
```

### 2. 查看插件日志

```bash
# 查看插件相关日志
docker-compose logs openagentflow | grep -i myplugin

# 查看详细日志
tail -f /var/log/openagentflow/plugins.log
```

### 3. 常见问题

#### 插件未加载
**可能原因**:
- 插件目录位置错误
- 依赖缺失
- 语法错误

**解决方案**:
```bash
# 检查插件位置
ls -la plugins/

# 检查依赖
pip list | grep aiohttp

# 检查语法
python -m py_compile plugins/my_plugin/plugin.py
```

#### 插件功能不可用
**可能原因**:
- 插件未启用
- 配置错误
- 权限不足

**解决方案**:
```bash
# 检查插件状态
curl http://localhost:8000/api/v1/plugins/MyPlugin

# 检查配置
curl http://localhost:8000/api/v1/plugins/MyPlugin/config

# 启用插件
curl -X POST http://localhost:8000/api/v1/plugins/MyPlugin/enable
```

## 发布插件

### 1. 准备发布

```bash
# 更新版本号
# 在plugin.py中更新__version__

# 更新CHANGELOG.md
# 描述新功能和修复

# 更新README.md
# 提供使用说明
```

### 2. 测试发布

```bash
# 运行所有测试
pytest tests/plugins/ -v

# 打包测试
python setup.py sdist
twine check dist/*

# 在测试环境安装
pip install dist/my_plugin-1.0.0.tar.gz
```

### 3. 发布到市场

#### 手动发布
1. 创建GitHub Release
2. 上传插件包
3. 更新插件市场列表

#### 自动发布
使用GitHub Actions自动发布：
```yaml
# .github/workflows/publish.yml
name: Publish Plugin

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Publish to Plugin Market
        run: |
          # 发布逻辑
          echo "发布插件..."
```

## 插件示例

### 完整插件示例

查看我们的示例插件：
- [Slack插件](../plugins/slack_plugin.py)
- [机器学习插件](../plugins/ml_plugin.py)

### 插件模板

使用我们的插件模板快速开始：
```bash
# 下载插件模板
git clone https://github.com/worldop123/openagentflow-plugin-template.git

# 自定义模板
cd openagentflow-plugin-template
# 修改配置和代码
```

## 获取帮助

- **文档**: [插件开发文档](https://github.com/worldop123/OpenAgentFlow/docs)
- **问题**: [GitHub Issues](https://github.com/worldop123/OpenAgentFlow/issues)
- **讨论**: [Discord频道](COMMUNITY.md)
- **示例**: [示例插件](../examples/)

祝您开发愉快！🚀