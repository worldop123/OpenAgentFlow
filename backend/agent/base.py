"""Base Agent class for OpenAgentFlow"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """Message exchanged between agents"""
    sender: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: time.time())


class AgentTool(BaseModel):
    """Tool that an agent can use"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: callable


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: Optional[List[AgentTool]] = None,
        memory_size: int = 10
    ):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.memory = []  # Simple memory buffer
        self.memory_size = memory_size
        
    def add_tool(self, tool: AgentTool):
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
        
    def remember(self, message: AgentMessage):
        """Store a message in memory"""
        self.memory.append(message)
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
            
    @abstractmethod
    async def think(self, input_message: AgentMessage) -> AgentMessage:
        """Process input and generate response"""
        pass
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Any:
        """Execute a specific task"""
        pass
        
    def __str__(self):
        return f"Agent({self.name})"


class LLMAgent(BaseAgent):
    """Agent powered by Large Language Model"""
    
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name, description, **kwargs)
        self.model = model
        self.system_prompt = system_prompt or f"You are {name}: {description}"
        
    async def think(self, input_message: AgentMessage) -> AgentMessage:
        """Generate response using LLM"""
        # This would integrate with OpenAI/Claude API
        # For now, return a placeholder response
        response = AgentMessage(
            sender=self.name,
            content=f"I've processed your message: {input_message.content[:50]}...",
            metadata={"model": self.model}
        )
        self.remember(input_message)
        self.remember(response)
        return response