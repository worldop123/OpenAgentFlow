"""API端点测试"""

import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from main import create_app
from backend.database import SessionLocal, Base, engine


class TestAPIAgents:
    """Agent API端点测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 创建测试数据库表
        Base.metadata.create_all(bind=engine)
        
        app = create_app()
        client = TestClient(app)
        
        yield client
        
        # 清理
        Base.metadata.drop_all(bind=engine)
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_list_agents_empty(self, client):
        """测试空Agent列表"""
        response = client.get("/api/v1/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_agent_success(self, client):
        """测试创建Agent成功"""
        agent_data = {
            "name": "Test Agent",
            "description": "Test Description",
            "agent_type": "llm",
            "config": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
            }
        }
        
        response = client.post("/api/v1/agents", json=agent_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == agent_data["name"]
        assert data["description"] == agent_data["description"]
        assert data["agent_type"] == agent_data["agent_type"]
        assert "id" in data
    
    def test_create_agent_missing_name(self, client):
        """测试创建Agent缺少名称"""
        agent_data = {
            "description": "Test Description",
            "agent_type": "llm"
        }
        
        response = client.post("/api/v1/agents", json=agent_data)
        
        # FastAPI应该验证失败
        assert response.status_code == 422
    
    def test_get_agent_not_found(self, client):
        """测试获取不存在的Agent"""
        response = client.get("/api/v1/agents/999")
        
        assert response.status_code == 404
    
    def test_create_and_get_agent(self, client):
        """测试创建并获取Agent"""
        # 创建Agent
        agent_data = {
            "name": "Test Agent",
            "description": "Test Description",
            "agent_type": "llm",
            "config": {"model": "gpt-3.5-turbo"}
        }
        
        create_response = client.post("/api/v1/agents", json=agent_data)
        assert create_response.status_code == 201
        created_agent = create_response.json()
        
        # 获取Agent
        agent_id = created_agent["id"]
        get_response = client.get(f"/api/v1/agents/{agent_id}")
        
        assert get_response.status_code == 200
        retrieved_agent = get_response.json()
        
        assert retrieved_agent["id"] == created_agent["id"]
        assert retrieved_agent["name"] == created_agent["name"]
        assert retrieved_agent["description"] == created_agent["description"]
    
    def test_update_agent(self, client):
        """测试更新Agent"""
        # 创建Agent
        agent_data = {
            "name": "Original Agent",
            "description": "Original Description",
            "agent_type": "llm"
        }
        
        create_response = client.post("/api/v1/agents", json=agent_data)
        agent = create_response.json()
        
        # 更新Agent
        update_data = {
            "name": "Updated Agent",
            "description": "Updated Description"
        }
        
        response = client.put(f"/api/v1/agents/{agent['id']}", json=update_data)
        
        assert response.status_code == 200
        updated_agent = response.json()
        
        assert updated_agent["name"] == update_data["name"]
        assert updated_agent["description"] == update_data["description"]
    
    def test_delete_agent(self, client):
        """测试删除Agent"""
        # 创建Agent
        agent_data = {
            "name": "Agent to Delete",
            "description": "Will be deleted",
            "agent_type": "llm"
        }
        
        create_response = client.post("/api/v1/agents", json=agent_data)
        agent = create_response.json()
        
        # 删除Agent
        response = client.delete(f"/api/v1/agents/{agent['id']}")
        
        assert response.status_code == 200
        
        # 验证Agent已被删除（应该返回404）
        get_response = client.get(f"/api/v1/agents/{agent['id']}")
        assert get_response.status_code == 404


class TestAPIWorkflows:
    """Workflow API端点测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        Base.metadata.create_all(bind=engine)
        
        app = create_app()
        client = TestClient(app)
        
        yield client
        
        Base.metadata.drop_all(bind=engine)
    
    def test_list_workflows_empty(self, client):
        """测试空工作流列表"""
        response = client.get("/api/v1/workflows")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_workflow_success(self, client):
        """测试创建工作流成功"""
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Workflow Description",
            "nodes": [
                {
                    "id": "start",
                    "type": "input",
                    "data": {"label": "开始"}
                }
            ],
            "edges": [],
            "status": "draft"
        }
        
        response = client.post("/api/v1/workflows", json=workflow_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == workflow_data["name"]
        assert data["description"] == workflow_data["description"]
        assert data["status"] == workflow_data["status"]
        assert "id" in data
    
    def test_create_workflow_invalid_nodes(self, client):
        """测试创建工作流节点无效"""
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "nodes": [],  # 空节点列表应该被拒绝
            "edges": [],
            "status": "draft"
        }
        
        response = client.post("/api/v1/workflows", json=workflow_data)
        
        # 应该返回400或422
        assert response.status_code in [400, 422]
    
    def test_validate_workflow(self, client):
        """测试验证工作流"""
        # 首先创建工作流
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "nodes": [
                {
                    "id": "start",
                    "type": "input",
                    "data": {"label": "开始"}
                },
                {
                    "id": "end",
                    "type": "output",
                    "data": {"label": "结束"}
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start",
                    "target": "end"
                }
            ],
            "status": "draft"
        }
        
        create_response = client.post("/api/v1/workflows", json=workflow_data)
        workflow = create_response.json()
        
        # 验证工作流
        response = client.post(f"/api/v1/workflows/{workflow['id']}/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data
    
    def test_execute_workflow(self, client):
        """测试执行工作流"""
        # 创建工作流
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "nodes": [
                {
                    "id": "start",
                    "type": "input",
                    "data": {"label": "开始"}
                }
            ],
            "edges": [],
            "status": "active"
        }
        
        create_response = client.post("/api/v1/workflows", json=workflow_data)
        workflow = create_response.json()
        
        # 执行工作流
        execution_data = {
            "workflow_id": workflow["id"],
            "input_data": {"message": "Hello"},
            "priority": 1
        }
        
        response = client.post(
            f"/workflows/{workflow['id']}/execute",
            json=execution_data
        )
        
        # 应该返回执行ID
        assert response.status_code == 200
        data = response.json()
        
        assert "execution_id" in data
        assert "status" in data
        assert data["status"] == "started"
    
    def test_activate_workflow(self, client):
        """测试激活工作流"""
        # 创建工作流（草稿状态）
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "nodes": [{"id": "start", "type": "input", "data": {"label": "开始"}}],
            "edges": [],
            "status": "draft"
        }
        
        create_response = client.post("/api/v1/workflows", json=workflow_data)
        workflow = create_response.json()
        
        # 激活工作流
        response = client.post(f"/api/v1/workflows/{workflow['id']}/activate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active"
        assert data["message"] == "工作流已激活"
    
    def test_pause_workflow(self, client):
        """测试暂停工作流"""
        # 创建工作流（活跃状态）
        workflow_data = {
            "name": "Test Workflow",
            "description": "Test Description",
            "nodes": [{"id": "start", "type": "input", "data": {"label": "开始"}}],
            "edges": [],
            "status": "active"
        }
        
        create_response = client.post("/api/v1/workflows", json=workflow_data)
        workflow = create_response.json()
        
        # 暂停工作流
        response = client.post(f"/api/v1/workflows/{workflow['id']}/pause")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "paused"
        assert data["message"] == "工作流已暂停"


class TestAPIAuthentication:
    """API认证测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        Base.metadata.create_all(bind=engine)
        
        app = create_app()
        client = TestClient(app)
        
        yield client
        
        Base.metadata.drop_all(bind=engine)
    
    def test_cors_headers(self, client):
        """测试CORS头部"""
        response = client.get("/health")
        
        # 检查CORS头部
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
    
    def test_content_type_json(self, client):
        """测试Content-Type头部"""
        response = client.get("/health")
        
        assert "Content-Type" in response.headers
        assert "application/json" in response.headers["Content-Type"]


class TestAPIErrorHandling:
    """API错误处理测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        Base.metadata.create_all(bind=engine)
        
        app = create_app()
        client = TestClient(app)
        
        yield client
        
        Base.metadata.drop_all(bind=engine)
    
    def test_invalid_json_request(self, client):
        """测试无效的JSON请求"""
        response = client.post("/api/v1/agents", data="invalid json")
        
        # 应该返回400错误
        assert response.status_code == 422
    
    def test_endpoint_not_found(self, client):
        """测试不存在的端点"""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_invalid_http_method(self, client):
        """测试无效的HTTP方法"""
        response = client.patch("/api/v1/agents")  # PATCH方法未实现
        
        # 应该返回405错误
        assert response.status_code == 405
    
    def test_server_error_handling(self, client):
        """测试服务器错误处理"""
        # 通过创建无效数据触发服务器错误
        agent_data = {
            "name": None,  # 无效名称
            "agent_type": "llm"
        }
        
        response = client.post("/api/v1/agents", json=agent_data)
        
        # 应该返回400或500错误
        assert response.status_code in [400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])