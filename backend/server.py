"""FastAPI server for OpenAgentFlow - Complete Version"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import config
from backend.database import get_db, Agent, Workflow, WorkflowExecution, Tool
from backend.agent.base import BaseAgent, LLMAgent, ToolAgent
from backend.workflow.engine import WorkflowEngine, WorkflowInstance, NodeType

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic模型
class AgentCreate(BaseModel):
    name: str = Field(..., description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    agent_type: str = Field("llm", description="Agent类型: llm, tool, condition")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent配置")

class AgentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    agent_type: str
    config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class WorkflowCreate(BaseModel):
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    nodes: List[Dict[str, Any]] = Field(..., description="节点列表")
    edges: List[Dict[str, Any]] = Field(..., description="边列表")
    status: str = Field("draft", description="状态: draft, active, paused")

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    status: str
    created_by: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        orge_mode = True

class ExecutionRequest(BaseModel):
    workflow_id: int = Field(..., description="工作流ID")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    priority: int = Field(1, description="优先级 (1-3)")

class ExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: int
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: str
    completed_at: Optional[str]
    duration_ms: Optional[int]

# 全局工作流引擎
workflow_engine = WorkflowEngine()

# API端点

@app.get("/", response_class=HTMLResponse)
async def root():
    """根端点"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenAgentFlow API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2563eb;
            }
            .endpoint {
                background: #f8fafc;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #2563eb;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                background: #2563eb;
                color: white;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 OpenAgentFlow API</h1>
            <p>Composable AI Agent Workflow Platform</p>
            
            <h2>📚 文档</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/docs">API 文档 (Swagger UI)</a>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/redoc">API 文档 (ReDoc)</a>
            </div>
            
            <h2>🔧 API 端点</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/agents">/agents - 获取所有Agent</a>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span>/agents - 创建新Agent</span>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <a href="/workflows">/workflows - 获取所有工作流</a>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span>/workflows - 创建新工作流</span>
            </div>
            
            <h2>📊 系统信息</h2>
            <p>版本: {version}</p>
            <p>主机: {host}:{port}</p>
            <p>调试模式: {debug}</p>
        </div>
    </body>
    </html>
    """.format(
        version=config.APP_VERSION,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    ))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": config.APP_NAME,
        "version": config.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/system/info")
async def system_info():
    """系统信息"""
    import platform
    import sys
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "machine": platform.machine()
        },
        "app": {
            "name": config.APP_NAME,
            "version": config.APP_VERSION,
            "host": config.HOST,
            "port": config.PORT,
            "debug": config.DEBUG,
            "log_level": config.LOG_LEVEL
        },
        "database": {
            "type": config.DATABASE_URL.split("://")[0]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Agent端点
@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有Agent"""
    agents = db.query(Agent).filter(Agent.is_active == True).offset(skip).limit(limit).all()
    return agents

@app.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """创建新Agent"""
    # 检查Agent名称是否已存在
    existing_agent = db.query(Agent).filter(Agent.name == agent_data.name).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail="Agent name already exists")
    
    # 创建Agent
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        agent_type=agent_data.agent_type,
        config=agent_data.config or {}
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """获取特定Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """更新Agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 更新字段
    agent.name = agent_data.name
    agent.description = agent_data.description
    agent.agent_type = agent_data.agent_type
    agent.config = agent_data.config or {}
    agent.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(agent)
    
    return agent

@app.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: Depends(get_db)
):
    """删除Agent (软删除)"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = False
    agent.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"status": "success", "message": f"Agent {agent_id} deleted"}

# Workflow端点
@app.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有工作流"""
    workflows = db.query(Workflow).offset(skip).limit(limit).all()
    return workflows

@app.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """创建新工作流"""
    # 创建工作流
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        nodes=workflow_data.nodes,
        edges=workflow_data.edges,
        status=workflow_data.status
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return workflow

@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """获取特定工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """更新工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # 更新字段
    workflow.name = workflow_data.name
    workflow.description = workflow_data.description
    workflow.nodes = workflow_data.nodes
    workflow.edges = workflow_data.edges
    workflow.status = workflow_data.status
    workflow.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(workflow)
    
    return workflow

@app.post("/workflows/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    workflow_id: int,
    execution_data: ExecutionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行工作流"""
    # 获取工作流
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status != "active":
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    # 创建执行记录
    import uuid
    from datetime import datetime
    
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        execution_id=str(uuid.uuid4()),
        input_data=execution_data.input_data,
        status="running"
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # 后台执行工作流
    async def execute_background():
        try:
            start_time = datetime.utcnow()
            
            # 从数据库加载Agent
            agents = db.query(Agent).filter(Agent.is_active == True).all()
            
            # 创建工作流实例
            workflow_instance = WorkflowInstance(
                workflow_id=str(workflow_id),
                nodes=workflow.nodes,
                edges=workflow.edges,
                agents={str(agent.id): agent for agent in agents}
            )
            
            # 执行工作流
            result = await workflow_instance.execute(
                input_data=execution_data.input_data or {}
            )
            
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新执行记录
            execution.status = "completed"
            execution.output_data = result
            execution.completed_at = end_time
            execution.duration_ms = duration
            
            db.commit()
            
            logger.info(f"Workflow {workflow_id} execution {execution.execution_id} completed in {duration}ms")
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = end_time
            execution.duration_ms = duration
            
            db.commit()
            
            logger.error(f"Workflow {workflow_id} execution {execution.execution_id} failed: {str(e)}")
            
            # 不在这里抛出异常，避免影响API响应
            # 可以通过监控系统记录错误
    
    # 启动后台任务
    background_tasks.add_task(execute_background)
    
    return {
        "execution_id": execution.execution_id,
        "workflow_id": workflow_id,
        "status": "started",
        "message": "Workflow execution started in background",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """获取执行结果"""
    execution = db.query(WorkflowExecution).filter(
        WorkflowExecution.execution_id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution.to_dict()

# Tool端点
@app.get("/tools")
async def list_tools(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有工具"""
    tools = db.query(Tool).filter(Tool.is_active == True).offset(skip).limit(limit).all()
    return [tool.to_dict() for tool in tools]

# 中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = datetime.utcnow()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # 记录日志
    logger.info(
        f"method={request.method} path={request.url.path} "
        f"status_code={response.status_code} "
        f"duration={process_time:.2f}ms"
    )
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# 启动函数
def start():
    """启动服务器"""
    import sys
    
    # 检查依赖
    required_packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-dotenv"]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("💡 请运行: pip install " + " ".join(missing))
        sys.exit(1)
    
    # 启动服务器
    uvicorn.run(
        "backend.server:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    start()