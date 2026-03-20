"""Workflow API端点"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from backend.database import get_db, Workflow, WorkflowExecution
from backend.workflow.engine import WorkflowEngine, WorkflowInstance

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

# Pydantic模型
class WorkflowBase(BaseModel):
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    nodes: List[Dict[str, Any]] = Field(..., description="节点列表")
    edges: List[Dict[str, Any]] = Field(..., description="边列表")

class WorkflowCreate(WorkflowBase):
    status: str = Field("draft", description="状态: draft, active, paused")

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None

class WorkflowResponse(WorkflowBase):
    id: int
    status: str
    created_by: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class ExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="输入数据")
    priority: int = Field(1, ge=1, le=3, description="优先级 (1-3)")

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

# 工作流引擎实例
workflow_engine = WorkflowEngine()

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    status: Optional[str] = Query(None, description="按状态过滤"),
    db: Session = Depends(get_db)
):
    """获取工作流列表"""
    query = db.query(Workflow)
    
    if status:
        query = query.filter(Workflow.status == status)
    
    workflows = query.offset(skip).limit(limit).all()
    return workflows

@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """创建新工作流"""
    # 检查名称是否已存在
    existing = db.query(Workflow).filter(Workflow.name == workflow_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"工作流名称 '{workflow_data.name}' 已存在")
    
    # 验证节点和边
    if not workflow_data.nodes:
        raise HTTPException(status_code=400, detail="工作流必须包含至少一个节点")
    
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

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """获取特定工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """更新工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    # 更新字段
    update_data = workflow_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """删除工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    # 检查是否有正在执行的工作流
    executions = db.query(WorkflowExecution).filter(
        WorkflowExecution.workflow_id == workflow_id,
        WorkflowExecution.status == "running"
    ).count()
    
    if executions > 0:
        raise HTTPException(status_code=400, detail="工作流正在执行，无法删除")
    
    db.delete(workflow)
    db.commit()
    
    return {"message": f"工作流 {workflow_id} 已删除"}

@router.post("/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(
    workflow_id: int,
    execution_data: ExecutionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    if workflow.status != "active":
        raise HTTPException(status_code=400, detail="工作流未激活")
    
    # 创建执行记录
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
            
            # 创建工作流实例
            workflow_instance = WorkflowInstance(
                workflow_id=str(workflow_id),
                nodes=workflow.nodes,
                edges=workflow.edges
            )
            
            # 执行工作流
            result = await workflow_instance.execute(execution_data.input_data)
            
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新执行记录
            execution.status = "completed"
            execution.output_data = result
            execution.completed_at = end_time
            execution.duration_ms = duration
            
            db.commit()
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds() * 1000)
            
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = end_time
            execution.duration_ms = duration
            
            db.commit()
    
    # 启动后台任务
    background_tasks.add_task(execute_background)
    
    return {
        "execution_id": execution.execution_id,
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "status": "started",
        "message": "工作流执行已启动",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/{workflow_id}/executions", response_model=List[ExecutionResponse])
async def list_workflow_executions(
    workflow_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    status: Optional[str] = Query(None, description="按状态过滤"),
    db: Session = Depends(get_db)
):
    """获取工作流执行记录"""
    query = db.query(WorkflowExecution).filter(
        WorkflowExecution.workflow_id == workflow_id
    )
    
    if status:
        query = query.filter(WorkflowExecution.status == status)
    
    executions = query.order_by(WorkflowExecution.started_at.desc()).offset(skip).limit(limit).all()
    return [execution.to_dict() for execution in executions]

@router.post("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """验证工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    errors = []
    warnings = []
    
    # 验证节点
    for node in workflow.nodes:
        if "id" not in node:
            errors.append(f"节点缺少ID: {node}")
        if "type" not in node:
            errors.append(f"节点缺少类型: {node}")
    
    # 验证边
    node_ids = {node.get("id") for node in workflow.nodes}
    for edge in workflow.edges:
        if "source" not in edge:
            errors.append(f"边缺少源节点: {edge}")
        elif edge["source"] not in node_ids:
            warnings.append(f"边引用了不存在的源节点: {edge['source']}")
        
        if "target" not in edge:
            errors.append(f"边缺少目标节点: {edge}")
        elif edge["target"] not in node_ids:
            warnings.append(f"边引用了不存在的目标节点: {edge['target']}")
    
    # 检查是否有孤立节点
    connected_nodes = set()
    for edge in workflow.edges:
        connected_nodes.add(edge.get("source"))
        connected_nodes.add(edge.get("target"))
    
    for node in workflow.nodes:
        node_id = node.get("id")
        if node_id and node_id not in connected_nodes:
            warnings.append(f"节点 {node_id} 未连接到任何其他节点")
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "node_count": len(workflow.nodes),
            "edge_count": len(workflow.edges),
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    }

@router.post("/{workflow_id}/activate")
async def activate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """激活工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    workflow.status = "active"
    db.commit()
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "status": "active",
        "message": "工作流已激活"
    }

@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """暂停工作流"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流未找到")
    
    workflow.status = "paused"
    db.commit()
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "status": "paused",
        "message": "工作流已暂停"
    }