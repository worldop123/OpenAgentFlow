"""数据库模块"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

from config import config

# 创建数据库引擎
engine = create_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

class Agent(Base):
    """AI Agent 模型"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)  # llm, tool, condition, etc.
    config = Column(JSON, nullable=True)  # Agent配置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Workflow(Base):
    """工作流模型"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    nodes = Column(JSON, nullable=False)  # 工作流节点
    edges = Column(JSON, nullable=False)  # 工作流边
    status = Column(String(20), default="draft")  # draft, active, paused, archived
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": self.nodes,
            "edges": self.edges,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class WorkflowExecution(Base):
    """工作流执行记录"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, index=True)
    execution_id = Column(String(100), unique=True, index=True)
    status = Column(String(20), default="running")  # running, completed, failed, cancelled
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms
        }

class Tool(Base):
    """工具模型"""
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    tool_type = Column(String(50), nullable=False)  # feishu, dingtalk, wecom, custom
    config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tool_type": self.tool_type,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

def init_db():
    """初始化数据库"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    # 创建默认数据
    session = SessionLocal()
    try:
        # 检查是否已有默认Agent
        if not session.query(Agent).first():
            # 创建默认LLM Agent
            default_agent = Agent(
                name="Default LLM Agent",
                description="默认的LLM AI Agent",
                agent_type="llm",
                config={
                    "model": config.DEFAULT_MODEL,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            session.add(default_agent)
            
            # 创建默认工作流
            default_workflow = Workflow(
                name="示例工作流",
                description="一个简单的示例工作流",
                nodes=[
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
                        "data": {"label": "AI处理", "agent_id": 1}
                    },
                    {
                        "id": "end",
                        "type": "output",
                        "position": {"x": 500, "y": 100},
                        "data": {"label": "结束"}
                    }
                ],
                edges=[
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
            )
            session.add(default_workflow)
            
            session.commit()
            print("✅ 默认数据创建完成")
        else:
            print("✅ 数据库已初始化")
    
    except Exception as e:
        session.rollback()
        print(f"❌ 创建默认数据失败: {e}")
        raise
    finally:
        session.close()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()