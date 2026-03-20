"""工作流单元测试"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from backend.workflow.engine import WorkflowEngine, WorkflowInstance, NodeType


class TestWorkflowEngine:
    """WorkflowEngine测试类"""
    
    def test_workflow_engine_initialization(self):
        """测试WorkflowEngine初始化"""
        engine = WorkflowEngine()
        
        assert engine.workflows == {}
        assert engine.agents == {}
    
    def test_create_workflow(self):
        """测试创建工作流"""
        engine = WorkflowEngine()
        
        workflow = engine.create_workflow(
            name="Test Workflow",
            description="Test Description"
        )
        
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test Description"
        assert workflow.id in engine.workflows
    
    def test_get_workflow(self):
        """测试获取工作流"""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(name="Test Workflow")
        
        result = engine.get_workflow(workflow.id)
        
        assert result == workflow
    
    def test_delete_workflow(self):
        """测试删除工作流"""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(name="Test Workflow")
        
        assert workflow.id in engine.workflows
        
        engine.delete_workflow(workflow.id)
        
        assert workflow.id not in engine.workflows
    
    def test_register_agent(self):
        """测试注册Agent"""
        engine = WorkflowEngine()
        
        mock_agent = Mock()
        mock_agent.name = "Test Agent"
        
        engine.register_agent(mock_agent)
        
        assert mock_agent.name in engine.agents
        assert engine.agents[mock_agent.name] == mock_agent


class TestWorkflowInstance:
    """WorkflowInstance测试类"""
    
    def test_workflow_instance_initialization(self):
        """测试WorkflowInstance初始化"""
        nodes = [
            {
                "id": "start",
                "type": "input",
                "position": {"x": 100, "y": 100},
                "data": {"label": "开始"}
            },
            {
                "id": "ai_agent",
                "type": "agent",
                "position": {"x": 300, "y": 100},
                "data": {"label": "AI处理", "agent_id": "test_agent"}
            }
        ]
        
        edges = [
            {
                "id": "edge-1",
                "source": "start",
                "target": "ai_agent"
            }
        ]
        
        instance = WorkflowInstance(
            workflow_id="test_workflow",
            nodes=nodes,
            edges=edges
        )
        
        assert instance.workflow_id == "test_workflow"
        assert len(instance.nodes) == 2
        assert len(instance.edges) == 1
    
    @pytest.mark.asyncio
    async def test_workflow_instance_execute(self):
        """测试工作流执行"""
        nodes = [
            {
                "id": "start",
                "type": "input",
                "position": {"x": 100, "y": 100},
                "data": {"label": "开始"}
            },
            {
                "id": "ai_agent",
                "type": "agent",
                "position": {"x": 300, "y": 100},
                "data": {"label": "AI处理", "agent_id": "test_agent"}
            },
            {
                "id": "end",
                "type": "output",
                "position": {"x": 500, "y": 100},
                "data": {"label": "结束"}
            }
        ]
        
        edges = [
            {
                "id": "edge-1",
                "source": "start",
                "target": "ai_agent"
            },
            {
                "id": "edge-2",
                "source": "ai_agent",
                "target": "end"
            }
        ]
        
        instance = WorkflowInstance(
            workflow_id="test_workflow",
            nodes=nodes,
            edges=edges
        )
        
        # Mock agent
        mock_agent = AsyncMock()
        mock_agent.process = AsyncMock(return_value="Mocked response")
        
        instance.agents = {"test_agent": mock_agent}
        
        input_data = {"message": "Hello"}
        result = await instance.execute(input_data)
        
        assert result is not None
        assert "message" in result
        assert "workflow_id" in result
        
        # 检查agent是否被调用
        mock_agent.process.assert_awaited_once_with(input_data)
    
    @pytest.mark.asyncio
    async def test_workflow_instance_execute_without_agents(self):
        """测试没有Agent的工作流执行"""
        nodes = [
            {
                "id": "start",
                "type": "input",
                "data": {"label": "开始"}
            }
        ]
        
        edges = []
        
        instance = WorkflowInstance(
            workflow_id="test_workflow",
            nodes=nodes,
            edges=edges
        )
        
        input_data = {"message": "Hello"}
        result = await instance.execute(input_data)
        
        assert result is not None
        assert "workflow_id" in result
        assert "execution_result" in result
    
    @pytest.mark.asyneno
    async def test_workflow_instance_execute_with_conditional_nodes(self):
        """测试有条件节点的工作流执行"""
        nodes = [
            {
                "id": "start",
                "type": "input",
                "data": {"label": "开始"}
            },
            {
                "id": "condition",
                "type": "condition",
                "data": {
                    "label": "条件判断",
                    "condition": "input.value > 10"
                }
            },
            {
                "id": "true_branch",
                "type": "agent",
                "data": {
                    "label": "大于10处理",
                    "agent_id": "agent_high"
                }
            },
            {
                "id": "false_branch",
                "type": "agent",
                "data": {
                    "label": "小于等于10处理",
                    "agent_id": "agent_low"
                }
            }
        ]
        
        edges = [
            {"id": "e1", "source": "start", "target": "condition"},
            {"id": "e2", "source": "condition", "target": "true_branch"},
            {"id": "e3", "source": "condition", "target": "false_branch"}
        ]
        
        instance = WorkflowInstance(
            workflow_id="test_conditional",
            nodes=nodes,
            edges=edges
        )
        
        # Mock agents
        mock_agent_high = AsyncMock()
        mock_agent_high.process = AsyncMock(return_value="High value processed")
        
        mock_agent_low = AsyncMock()
        mock_agent_low.process = AsyncMock(return_value="Low value processed")
        
        instance.agents = {
            "agent_high": mock_agent_high,
            "agent_low": mock_agent_low
        }
        
        # 测试条件为真
        input_data = {"value": 15}
        result = await instance.execute(input_data)
        
        # 检查正确的agent被调用
        mock_agent_high.process.assert_awaited_once()
        mock_agent_low.process.assert_not_awaited()
        
        # 测试条件为假
        input_data = {"value": 5}
        await instance.execute(input_data)
        
        mock_agent_low.process.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_workflow_instance_execute_error_handling(self):
        """测试工作流执行错误处理"""
        nodes = [
            {
                "id": "start",
                "type": "input",
                "data": {"label": "开始"}
            },
            {
                "id": "failing_agent",
                "type": "agent",
                "data": {
                    "label": "会失败的Agent",
                    "agent_id": "failing_agent"
                }
            }
        ]
        
        edges = [
            {"id": "e1", "source": "start", "target": "failing_agent"}
        ]
        
        instance = WorkflowInstance(
            workflow_id="test_error",
            nodes=nodes,
            edges=edges
        )
        
        # Mock agent抛出异常
        mock_agent = AsyncMock()
        mock_agent.process = AsyncMock(side_effect=Exception("Agent failed"))
        
        instance.agents = {"failing_agent": mock_agent}
        
        input_data = {"message": "Hello"}
        result = await instance.execute(input_data)
        
        # 检查错误被捕获并返回错误信息
        assert "error" in result
        assert result["status"] == "error"
        assert "Agent failed" in result["error"]


class TestNodeTypes:
    """节点类型测试类"""
    
    def test_node_type_enum(self):
        """测试节点类型枚举"""
        node_types = [t.value for t in NodeType]
        
        assert "input" in node_types
        assert "output" in node_types
        assert "agent" in node_types
        assert "condition" in node_types
        assert "tool" in node_types
        
        # 测试特定值
        assert NodeType.INPUT.value == "input"
        assert NodeType.AGENT.value == "agent"
    
    def test_node_type_from_string(self):
        """测试从字符串获取节点类型"""
        assert NodeType("input") == NodeType.INPUT
        assert NodeType("agent") == NodeType.AGENT
        assert NodeType("condition") == NodeType.CONDITION
        
        with pytest.raises(ValueError):
            NodeType("invalid_type")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])