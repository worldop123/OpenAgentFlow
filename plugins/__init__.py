"""OpenAgentFlow 插件包

此包包含所有可用插件。插件系统支持动态扩展功能，
包括新的Agent类型、工具和工作流模板。

插件开发指南:
1. 继承 Plugin 基类
2. 实现 on_load(), on_enable(), on_disable()
3. 注册工具、Agent类型或工作流模板
4. 将插件文件放在此目录中
"""

import os
import importlib
import pkgutil
from typing import List, Dict, Any


# 自动发现插件
def discover_plugins() -> List[str]:
    """自动发现所有插件模块"""
    plugins = []
    
    # 获取当前目录
    plugin_dir = os.path.dirname(__file__)
    
    # 遍历所有.py文件（排除__init__.py）
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # 移除.py后缀
            plugins.append(module_name)
    
    return plugins


# 加载所有插件
def load_all_plugins() -> Dict[str, Any]:
    """加载所有插件并返回插件实例"""
    from backend.plugins import Plugin
    
    plugin_instances = {}
    discovered = discover_plugins()
    
    for plugin_name in discovered:
        try:
            # 导入插件模块
            module = importlib.import_module(f"plugins.{plugin_name}")
            
            # 查找插件实例
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, Plugin):
                    plugin_instances[attr.name] = attr
                    break
        
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"无法加载插件 {plugin_name}: {e}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"加载插件 {plugin_name} 时出错: {e}")
    
    return plugin_instances


# 插件列表
__all__ = discover_plugins()

# 导出常用功能
__version__ = "1.0.0"
__author__ = "OpenAgentFlow Team"
__description__ = "OpenAgentFlow插件包"