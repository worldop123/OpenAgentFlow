"""插件系统 - 支持动态扩展功能"""

import importlib
import inspect
import pkgutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Plugin:
    """插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
        self.config = {}
    
    def on_load(self):
        """插件加载时调用"""
        pass
    
    def on_enable(self):
        """插件启用时调用"""
        pass
    
    def on_disable(self):
        """插件禁用时调用"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "description": getattr(self, "description", ""),
            "author": getattr(self, "author", ""),
            "website": getattr(self, "website", "")
        }


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[callable]] = {}
        
        # 创建插件目录
        self.plugin_dir.mkdir(exist_ok=True)
    
    def load_plugins(self):
        """加载所有插件"""
        logger.info(f"从 {self.plugin_dir} 加载插件...")
        
        # 扫描插件目录
        for module_info in pkgutil.iter_modules([str(self.plugin_dir)]):
            try:
                self.load_plugin(module_info.name)
            except Exception as e:
                logger.error(f"加载插件 {module_info.name} 失败: {e}")
    
    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """加载单个插件"""
        try:
            # 导入插件模块
            module = importlib.import_module(f"plugins.{plugin_name}")
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.warning(f"插件 {plugin_name} 没有找到Plugin类")
                return None
            
            # 创建插件实例
            plugin = plugin_class()
            plugin.on_load()
            
            # 注册插件
            self.plugins[plugin.name] = plugin
            
            logger.info(f"插件 {plugin.name} v{plugin.version} 加载成功")
            return plugin
            
        except Exception as e:
            logger.error(f"加载插件 {plugin_name} 失败: {e}")
            return None
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        if plugin_name not in self.plugins:
            logger.error(f"插件 {plugin_name} 不存在")
            return False
        
        plugin = self.plugins[plugin_name]
        if plugin.enabled:
            logger.warning(f"插件 {plugin_name} 已经启用")
            return True
        
        try:
            plugin.on_enable()
            plugin.enabled = True
            logger.info(f"插件 {plugin_name} 已启用")
            return True
        except Exception as e:
            logger.error(f"启用插件 {plugin_name} 失败: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        if plugin_name not in self.plugins:
            logger.error(f"插件 {plugin_name} 不存在")
            return False
        
        plugin = self.plugins[plugin_name]
        if not plugin.enabled:
            logger.warning(f"插件 {plugin_name} 已经禁用")
            return True
        
        try:
            plugin.on_disable()
            plugin.enabled = False
            logger.info(f"插件 {plugin_name} 已禁用")
            return True
        except Exception as e:
            logger.error(f"禁用插件 {plugin_name} 失败: {e}")
            return False
    
    def register_hook(self, hook_name: str, callback: callable):
        """注册钩子函数"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """调用钩子函数"""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    logger.error(f"钩子 {hook_name} 调用失败: {e}")
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """获取插件"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [plugin.get_info() for plugin in self.plugins.values()]


# 全局插件管理器实例
plugin_manager = PluginManager()


class AgentPlugin(Plugin):
    """Agent插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.agent_types = []
    
    def register_agent_type(self, agent_type: str, agent_class):
        """注册Agent类型"""
        self.agent_types.append({
            "type": agent_type,
            "class": agent_class,
            "plugin": self.name
        })


class ToolPlugin(Plugin):
    """工具插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.tools = []
    
    def register_tool(self, tool_name: str, tool_func: callable, description: str = ""):
        """注册工具"""
        self.tools.append({
            "name": tool_name,
            "function": tool_func,
            "description": description,
            "plugin": self.name
        })


class WorkflowPlugin(Plugin):
    """工作流插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.node_types = []
        self.workflow_templates = []
    
    def register_node_type(self, node_type: str, node_class):
        """注册节点类型"""
        self.node_types.append({
            "type": node_type,
            "class": node_class,
            "plugin": self.name
        })
    
    def register_workflow_template(self, template_name: str, template_data: Dict[str, Any]):
        """注册工作流模板"""
        self.workflow_templates.append({
            "name": template_name,
            "data": template_data,
            "plugin": self.name
        })