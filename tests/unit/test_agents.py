"""Agent单元测试"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from backend.agent.base import BaseAgent, LLMAgent, ToolAgent, create_agent_from_config


class TestBaseAgent:
    """BaseAgent测试类"""
    
    def test_base_agent_initialization(self):
        """测试BaseAgent初始化"""
        agent = BaseAgent(name="Test Agent", description="Test Description")
        
        assert agent.name == "Test Agent"
        assert agent.description == "Test Description"
        assert agent.id is not None
        assert agent.created_at is not None
        assert agent.config == {}
    
    def test_base_agent_to_dict(self):
        """测试to_dict方法"""
        agent = BaseAgent(name="Test Agent", description="Test Description")
        result = agent.to_dict()
        
        assert result["name"] == "Test Agent"
        assert result["description"] == "Test Description"
        assert "id" in result
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_base_agent_process_not_implemented(self):
        """测试process方法未实现"""
        agent = BaseAgent(name="Test Agent")
        
        with pytest.raises(NotImplementedError):
            await agent.process("test input")
    
    @pytest.mark.asyncio
    async def test_base_agent_validate(self):
        """测试validate方法"""
        agent = BaseAgent(name="Test Agent")
        
        # 默认应该返回True
        assert await agent.validate() is True


class TestLLMAgent:
    """LLMAgent测试类"""
    
    def test_llm_agent_initialization(self):
        """测试LLMAgent初始化"""
        agent = LLMAgent(
            name="Test LLM",
            description="Test LLM Agent",
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        assert agent.name == "Test LLM"
        assert agent.description == "Test LLM Agent"
        assert agent.model == "gpt-3.5-turbo"
        assert agent.temperature == 0.7
        assert agent.max_tokens == 1000
        assert agent.system_prompt is None
    
    def test_llm_agent_to_dict(self):
        """测试LLMAgent的to_dict方法"""
        agent = LLMAgent(name="Test LLM", model="gpt-3.5-turbo")
        result = agent.to_dict()
        
        assert result["name"] == "Test LLM"
        assert result["model"] == "gpt-3.5-turbo"
        assert result["agent_type"] == "llm"
        assert "config" in result
    
    @pytest.mark.asyncio
    async def test_llm_agent_process_with_mock(self):
        """测试LLMAgent的process方法（使用mock）"""
        agent = LLMAgent(name="Test LLM", model="gpt-3.5-turbo")
        
        # Mock OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mocked response"))]
        
        with patch('backend.agent.base.openai.chat.completions.create', return_value=mock_response):
            result = await agent.process("Hello, how are you?")
            
            assert result == "Mocked response"
    
    @pytest.mark.asyncio
    async def test_llm_agent_process_with_system_prompt(self):
        """测试带系统提示的LLMAgent"""
        agent = LLMAgent(
            name="Test LLM",
            model="gpt-3.5-turbo",
            system_prompt="You are a helpful assistant."
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Mocked response"))]
        
        with patch('backend.agent.base.openai.chat.completions.create', return_value=mock_response) as mock_create:
            await agent.process("Hello")
            
            # 检查是否包含系统消息
            call_args = mock_create.call_args
            messages = call_args[1].get('messages', [])
            
            assert len(messages) == 2
            assert messages[0]['role'] == 'system'
            assert messages[0]['content'] == "You are a helpful assistant."
    
    @pytest.mark.asyncio
    async def test_llm_agent_validate(self):
        """测试LLMAgent的validate方法"""
        agent = LLMAgent(name="Test LLM", model="gpt-3.5-turbo")
        
        # Mock OpenAI调用
        with patch('backend.agent.base.openai.chat.completions.create'):
            result = await agent.validate()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_llm_agent_validate_failure(self):
        """测试LLMAgent验证失败"""
        agent = LLMAgent(name="Test LLM", model="gpt-3.5-turbo")
        
        # Mock OpenAI调用抛出异常
        with patch('backend.agent.base.openai.chat.completions.create', side_effect=Exception("API Error")):
            result = await agent.validate()
            assert result is False


class TestToolAgent:
    """ToolAgent测试类"""
    
    def test_tool_agent_initialization(self):
        """测试ToolAgent初始化"""
        agent = ToolAgent(
            name="Test Tool",
            description="Test Tool Agent",
            tool_name="feishu_send",
            tool_config={"app_id": "test_app_id"}
        )
        
        assert agent.name == "Test Tool"
        assert agent.description == "Test Tool Description"
        assert agent.tool_name == "feishu_send"
        assert agent.tool_config == {"app_id": "test_app_id"}
    
    def test_tool_agent_to_dict(self):
        """测试ToolAgent的to_dict方法"""
        agent = ToolAgent(name="Test Tool", tool_name="feishu_send")
        result = agent.to_dict()
        
        assert result["name"] == "Test Tool"
        assert result["tool_name"] == "feishu_send"
        assert result["agent_type"] == "tool"
    
    @pytest.mark.asyncio
    async def test_tool_agent_process(self):
        """测试ToolAgent的process方法"""
        agent = ToolAgent(name="Test Tool", tool_name="feishu_send")
        
        # Mock工具执行
        mock_tool = AsyncMock(return_value={"success": True, "message": "Message sent"})
        agent.tool_executor = mock_tool
        
        result = await agent.process("Send message: Hello")
        
        assert result == {"success": True, "message": "Message sent"}
        mock_tool.assert_awaited_once_with("Send message: Hello")
    
    @pytest.mark.asyncio
    async def test_tool_agent_validate(self):
        """测试ToolAgent的validate方法"""
        agent = ToolAgent(name="Test Tool", tool_name="feishu_send")
        
        # Mock工具验证
        mock_validate = AsyncMock(return_value=True)
        agent.validate_tool = mock_validate
        
        result = await agent.validate()
        
        assert result is True
        mock_validate.assert_awaited_once()


class TestAgentFactory:
    """Agent工厂测试类"""
    
    def test_create_llm_agent_from_config(self):
        """测试从配置创建LLMAgent"""
        config = {
            "agent_type": "llm",
            "name": "Test LLM",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000,
            "system_prompt": "Be helpful"
        }
        
        agent = create_agent_from_config(config)
        
        assert isinstance(agent, LLMAgent)
        assert agent.name == "Test LLM"
        assert agent.model == "gpt-3.5-turbo"
        assert agent.temperature == 0.7
    
    def test_create_tool_agent_from_config(self):
        """测试从配置创建ToolAgent"""
        config = {
            "agent_type": "tool",
            "name": "Test Tool",
            "tool_name": "feishu_send",
            "tool_config": {"app_id": "test_app_id"}
        }
        
        agent = create_agent_from_config(config)
        
        assert isinstance(agent, ToolAgent)
        assert agent.name == "Test Tool"
        assert agent.tool_name == "feishu_send"
    
    def test_create_agent_invalid_type(self):
        """测试创建无效类型的Agent"""
        config = {
            "agent_type": "invalid_type",
            "name": "Test Agent"
        }
        
        with pytest.raises(ValueError, match="Unknown agent type"):
            create_agent_from_config(config)
    
    def test_create_agent_missing_type(self):
        """测试创建缺少类型的Agent"""
        config = {
            "name": "Test Agent"
        }
        
        with pytest.raises(ValueError, match="Agent type is required"):
            create_agent_from_config(config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])