"""插件管理API端点"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.plugins import plugin_manager

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])


# 请求/响应模型
class PluginInfo(BaseModel):
    name: str
    version: str
    enabled: bool
    description: str = ""
    author: str = ""
    website: str = ""


class PluginConfig(BaseModel):
    config: Dict[str, Any] = {}


class PluginActionRequest(BaseModel):
    action: str  # enable, disable, reload


@router.get("/", response_model=List[PluginInfo])
async def list_plugins():
    """获取所有插件列表"""
    try:
        plugins = plugin_manager.list_plugins()
        return plugins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取插件列表失败: {str(e)}")


@router.get("/{plugin_name}", response_model=PluginInfo)
async def get_plugin(plugin_name: str):
    """获取特定插件信息"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"插件 {plugin_name} 不存在")
    
    return plugin.get_info()


@router.post("/{plugin_name}/config")
async def update_plugin_config(plugin_name: str, config: PluginConfig):
    """更新插件配置"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"插件 {plugin_name} 不存在")
    
    try:
        plugin.config = config.config
        return {"message": f"插件 {plugin_name} 配置已更新", "config": plugin.config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/{plugin_name}/enable")
async def enable_plugin(plugin_name: str):
    """启用插件"""
    success = plugin_manager.enable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"启用插件 {plugin_name} 失败")
    
    return {"message": f"插件 {plugin_name} 已启用"}


@router.post("/{plugin_name}/disable")
async def disable_plugin(plugin_name: str):
    """禁用插件"""
    success = plugin_manager.disable_plugin(plugin_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"禁用插件 {plugin_name} 失败")
    
    return {"message": f"插件 {plugin_name} 已禁用"}


@router.post("/{plugin_name}/reload")
async def reload_plugin(plugin_name: str):
    """重新加载插件"""
    try:
        # 先禁用
        plugin_manager.disable_plugin(plugin_name)
        
        # 重新加载
        plugin_manager.load_plugin(plugin_name)
        
        # 如果之前是启用的，重新启用
        plugin = plugin_manager.get_plugin(plugin_name)
        if plugin and plugin.enabled:
            plugin_manager.enable_plugin(plugin_name)
        
        return {"message": f"插件 {plugin_name} 已重新加载"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载插件失败: {str(e)}")


@router.post("/scan")
async def scan_plugins():
    """扫描并加载新插件"""
    try:
        plugin_manager.load_plugins()
        
        plugins = plugin_manager.list_plugins()
        return {
            "message": "插件扫描完成",
            "plugins_found": len(plugins),
            "plugins": plugins
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"扫描插件失败: {str(e)}")


@router.get("/hooks/available")
async def get_available_hooks():
    """获取可用的钩子列表"""
    try:
        hooks = list(plugin_manager.hooks.keys())
        return {
            "hooks": hooks,
            "count": len(hooks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取钩子列表失败: {str(e)}")


@router.get("/{plugin_name}/tools")
async def get_plugin_tools(plugin_name: str):
    """获取插件提供的工具"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"插件 {plugin_name} 不存在")
    
    if hasattr(plugin, "tools"):
        return {
            "plugin": plugin_name,
            "tools": plugin.tools
        }
    else:
        return {
            "plugin": plugin_name,
            "tools": [],
            "message": "该插件没有提供工具"
        }


@router.get("/{plugin_name}/agents")
async def get_plugin_agents(plugin_name: str):
    """获取插件提供的Agent类型"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"插件 {plugin_name} 不存在")
    
    if hasattr(plugin, "agent_types"):
        return {
            "plugin": plugin_name,
            "agent_types": plugin.agent_types
        }
    else:
        return {
            "plugin": plugin_name,
            "agent_types": [],
            "message": "该插件没有提供Agent类型"
        }


@router.get("/{plugin_name}/workflows")
async def get_plugin_workflows(plugin_name: str):
    """获取插件提供的工作流模板"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"插件 {plugin_name} 不存在")
    
    if hasattr(plugin, "workflow_templates"):
        return {
            "plugin": plugin_name,
            "workflow_templates": plugin.workflow_templates
        }
    else:
        return {
            "plugin": plugin_name,
            "workflow_templates": [],
            "message": "该插件没有提供工作流模板"
        }


@router.post("/hooks/{hook_name}/call")
async def call_hook(hook_name: str, data: Dict[str, Any] = None):
    """调用钩子函数"""
    try:
        args = data.get("args", []) if data else []
        kwargs = data.get("kwargs", {}) if data else {}
        
        results = plugin_manager.call_hook(hook_name, *args, **kwargs)
        
        return {
            "hook": hook_name,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用钩子失败: {str(e)}")


@router.get("/system/health")
async def plugin_system_health():
    """插件系统健康检查"""
    try:
        plugins = plugin_manager.list_plugins()
        enabled_plugins = [p for p in plugins if p["enabled"]]
        
        return {
            "status": "healthy",
            "total_plugins": len(plugins),
            "enabled_plugins": len(enabled_plugins),
            "disabled_plugins": len(plugins) - len(enabled_plugins),
            "hooks_registered": len(plugin_manager.hooks)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# 插件市场相关端点（未来扩展）
@router.get("/marketplace/categories")
async def get_marketplace_categories():
    """获取插件市场分类"""
    return {
        "categories": [
            {"id": "ai_ml", "name": "AI/机器学习", "count": 5},
            {"id": "enterprise", "name": "企业工具", "count": 3},
            {"id": "data", "name": "数据处理", "count": 2},
            {"id": "communication", "name": "通讯工具", "count": 4},
            {"id": "productivity", "name": "生产力工具", "count": 3}
        ]
    }


@router.get("/marketplace/search")
async def search_marketplace(query: str = "", category: str = ""):
    """搜索插件市场"""
    # 这里可以集成实际的插件市场API
    return {
        "query": query,
        "category": category,
        "results": [
            {
                "id": "slack_integration",
                "name": "Slack集成",
                "description": "Slack消息和文件集成",
                "category": "communication",
                "downloads": 1500,
                "rating": 4.5
            },
            {
                "id": "ml_tools",
                "name": "机器学习工具包",
                "description": "数据预处理和模型训练工具",
                "category": "ai_ml",
                "downloads": 2300,
                "rating": 4.8
            }
        ]
    }