"""OpenAgentFlow - 开源AI Agent工作流平台"""

__version__ = "0.1.0"
__author__ = "OpenAgentFlow Team"
__description__ = "可视化、可组合的AI Agent工作流平台"


# 导入核心模块
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 初始化插件系统
from backend.plugins import plugin_manager

# 启动时加载插件
def init_plugins():
    """初始化插件系统"""
    try:
        # 确保插件目录存在
        plugins_dir = project_root / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        
        # 加载插件
        plugin_manager.load_plugins()
        
        # 启用所有插件（默认）
        for plugin_name in plugin_manager.plugins.keys():
            plugin_manager.enable_plugin(plugin_name)
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"插件系统初始化失败: {e}")
        return False


# 应用启动时自动初始化
if __name__ != "__main__":
    # 作为模块导入时初始化
    init_plugins()


# 导出核心模块
__all__ = [
    "plugin_manager",
    "init_plugins"
]