"""Agent API端点"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db, Agent
from backend.agent.base import LLMAgent, ToolAgent, create_agent_from_config

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

# Pydantic模型
class AgentBase(BaseModel):
    name: str = Field(..., description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    agent_type: str = Field("llm", description="Agent类型: llm, tool, condition")
    config: Optional[dict] = Field(default_factory=dict, description="Agent配置")

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None

class AgentResponse(AgentBase):
    id: int
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    agent_type: Optional[str] = Query(None, description="按类型过滤"),
    active_only: bool = Query(True, description="只返回活跃的Agent"),
    db: Session = Depends(get_db)
):
    """获取Agent列表"""
    query = db.query(Agent)
    
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    if agent_type:
        query = query.filter(Agent.agent_type == agent_type)
    
    agents = query.offset(skip).limit(limit).all()
    return agents

@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """创建新Agent"""
    # 检查名称是否已存在
    existing = db.query(Agent).filter(Agent.name == agent_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Agent名称 '{agent_data.name}' 已存在")
    
    # 创建Agent
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        agent_type=agent_data.agent_type,
        config=agent_data.config
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """获取特定Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """更新Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    # 更新字段
    update_data = agent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """删除Agent（软删除）"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    agent.is_active = False
    db.commit()
    
    return {"message": f"Agent {agent_id} 已删除"}

@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: int,
    message: str = Query(..., description="测试消息"),
    db: Session = Depends(get_db)
):
    """测试Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    try:
        # 根据配置创建Agent实例
        agent_instance = create_agent_from_config(agent.config)
        
        # 测试消息
        result = await agent_instance.process(message)
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "input": message,
            "output": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent测试失败: {str(e)}")

@router.get("/{agent_id}/tools")
async def get_agent_tools(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """获取Agent可用的工具"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent未找到")
    
    # 根据Agent类型返回可用工具
    if agent.agent_type == "llm":
        tools = [
            {"name": "send_message", "description": "发送消息"},
            {"name": "analyze_text", "description": "分析文本"},
            {"name": "generate_content", "description": "生成内容"}
        ]
    elif agent.agent_type == "tool":
        tools = [
            {"name": "feishu_send", "description": "发送飞书消息"},
            {"name": "dingtalk_send", "description": "发送钉钉消息"},
            {"name": "wecom_send", "description": "发送企业微信消息"}
        ]
    else:
        tools = []
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "tools": tools
    }