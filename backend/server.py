"""Main server for OpenAgentFlow"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from workflow.engine import WorkflowEngine, Workflow, WorkflowNode
from agent.base import LLMAgent


app = FastAPI(
    title="OpenAgentFlow",
    description="Composable AI Agent Workflow Platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow engine
engine = WorkflowEngine()


class CreateAgentRequest(BaseModel):
    name: str
    description: str
    model: str = "gpt-3.5-turbo"
    system_prompt: Optional[str] = None


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str


class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    input_data: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OpenAgentFlow",
        "version": "0.1.0",
        "endpoints": {
            "agents": "/agents",
            "workflows": "/workflows",
            "execute": "/workflows/{id}/execute"
        }
    }


@app.post("/agents")
async def create_agent(request: CreateAgentRequest):
    """Create a new agent"""
    agent = LLMAgent(
        name=request.name,
        description=request.description,
        model=request.model,
        system_prompt=request.system_prompt
    )
    engine.register_agent(agent)
    return {
        "status": "success",
        "agent": {
            "name": agent.name,
            "description": agent.description,
            "model": agent.model
        }
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "model": getattr(agent, 'model', 'unknown')
            }
            for agent in engine.agents.values()
        ]
    }


@app.post("/workflows")
async def create_workflow(request: CreateWorkflowRequest):
    """Create a new workflow"""
    workflow = engine.create_workflow(
        name=request.name,
        description=request.description
    )
    return {
        "status": "success",
        "workflow": workflow.dict()
    }


@app.get("/workflows")
async def list_workflows():
    """List all workflows"""
    return {
        "workflows": [
            workflow.dict()
            for workflow in engine.workflows.values()
        ]
    }


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow"""
    if workflow_id not in engine.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return engine.workflows[workflow_id].dict()


@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest
):
    """Execute a workflow"""
    try:
        result = await engine.execute_workflow(
            workflow_id=workflow_id,
            initial_input=request.input_data
        )
        return {
            "status": "success",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/{workflow_id}/nodes")
async def add_workflow_node(
    workflow_id: str,
    node_data: Dict[str, Any]
):
    """Add a node to a workflow"""
    try:
        from workflow.engine import NodeType
        
        node_type = NodeType(node_data.get("type", "agent"))
        agent_id = node_data.get("agent_id")
        config = node_data.get("config", {})
        
        node = engine.add_node(
            workflow_id=workflow_id,
            node_type=node_type,
            agent_id=agent_id,
            config=config
        )
        
        return {
            "status": "success",
            "node": node.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workflows/{workflow_id}/connect")
async def connect_workflow_nodes(
    workflow_id: str,
    connection: Dict[str, str]
):
    """Connect two nodes in a workflow"""
    try:
        engine.connect_nodes(
            workflow_id=workflow_id,
            from_node_id=connection["from"],
            to_node_id=connection["to"]
        )
        return {"status": "success"}
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )