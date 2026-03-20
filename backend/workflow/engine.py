"""Workflow engine for orchestrating multiple agents"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from ..agent.base import BaseAgent, AgentMessage


class NodeType(str, Enum):
    """Types of workflow nodes"""
    AGENT = "agent"
    CONDITION = "condition"
    DELAY = "delay"
    WEBHOOK = "webhook"
    TOOL = "tool"


class WorkflowNode(BaseModel):
    """A node in the workflow"""
    id: str
    type: NodeType
    agent_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    next_nodes: List[str] = Field(default_factory=list)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})


class Workflow(BaseModel):
    """A complete workflow definition"""
    id: str
    name: str
    description: str
    nodes: Dict[str, WorkflowNode] = Field(default_factory=dict)
    edges: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class WorkflowEngine:
    """Engine that executes workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_history: Dict[str, List[Dict]] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the engine"""
        self.agents[agent.name] = agent
        
    def create_workflow(self, name: str, description: str) -> Workflow:
        """Create a new workflow"""
        workflow_id = f"wf_{len(self.workflows) + 1}"
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description
        )
        self.workflows[workflow_id] = workflow
        return workflow
        
    def add_node(
        self,
        workflow_id: str,
        node_type: NodeType,
        agent_id: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> WorkflowNode:
        """Add a node to a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        node_id = f"node_{len(self.workflows[workflow_id].nodes) + 1}"
        node = WorkflowNode(
            id=node_id,
            type=node_type,
            agent_id=agent_id,
            config=config or {}
        )
        
        self.workflows[workflow_id].nodes[node_id] = node
        self.workflows[workflow_id].updated_at = datetime.now()
        return node
        
    def connect_nodes(self, workflow_id: str, from_node_id: str, to_node_id: str):
        """Connect two nodes in a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow = self.workflows[workflow_id]
        
        if from_node_id not in workflow.nodes:
            raise ValueError(f"Node {from_node_id} not found")
        if to_node_id not in workflow.nodes:
            raise ValueError(f"Node {to_node_id} not found")
            
        workflow.nodes[from_node_id].next_nodes.append(to_node_id)
        workflow.edges.append({"from": from_node_id, "to": to_node_id})
        workflow.updated_at = datetime.now()
        
    async def execute_workflow(
        self,
        workflow_id: str,
        initial_input: Dict[str, Any],
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a workflow from start to finish"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow = self.workflows[workflow_id]
        execution_id = execution_id or f"exec_{len(self.execution_history) + 1}"
        
        # Find start nodes (nodes with no incoming edges)
        start_nodes = [
            node for node in workflow.nodes.values()
            if not any(edge["to"] == node.id for edge in workflow.edges)
        ]
        
        if not start_nodes:
            raise ValueError("No start nodes found in workflow")
            
        execution_log = []
        results = {}
        
        # Simple linear execution for now
        # TODO: Implement parallel execution and branching
        for start_node in start_nodes:
            current_node = start_node
            while current_node:
                node_result = await self._execute_node(
                    workflow_id, current_node, initial_input, results
                )
                
                execution_log.append({
                    "node_id": current_node.id,
                    "node_type": current_node.type,
                    "timestamp": datetime.now().isoformat(),
                    "result": node_result
                })
                
                results[current_node.id] = node_result
                
                # Move to next node
                if current_node.next_nodes:
                    current_node = workflow.nodes[current_node.next_nodes[0]]
                else:
                    current_node = None
                    
        self.execution_history[execution_id] = execution_log
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "results": results,
            "log": execution_log,
            "status": "completed"
        }
        
    async def _execute_node(
        self,
        workflow_id: str,
        node: WorkflowNode,
        initial_input: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Any:
        """Execute a single workflow node"""
        if node.type == NodeType.AGENT and node.agent_id:
            if node.agent_id not in self.agents:
                raise ValueError(f"Agent {node.agent_id} not found")
                
            agent = self.agents[node.agent_id]
            message = AgentMessage(
                sender="workflow_engine",
                content=json.dumps({
                    "input": initial_input,
                    "previous_results": previous_results,
                    "config": node.config
                })
            )
            
            response = await agent.think(message)
            return response.content
            
        elif node.type == NodeType.CONDITION:
            # Simple condition evaluation
            condition = node.config.get("condition", "true")
            # TODO: Implement proper condition evaluation
            return {"condition_result": True}
            
        elif node.type == NodeType.DELAY:
            delay_seconds = node.config.get("seconds", 1)
            await asyncio.sleep(delay_seconds)
            return {"delayed": delay_seconds}
            
        else:
            return {"node_type": node.type, "config": node.config}