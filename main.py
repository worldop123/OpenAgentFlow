#!/usr/bin/env python3
"""
OpenAgentFlow 主入口文件
完整可运行版本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('openagentflow.log')
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """检查依赖"""
    logger = setup_logging()
    
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("sqlalchemy", "sqlalchemy"),
        ("python-dotenv", "dotenv"),
        ("httpx", "httpx")
    ]
    
    missing = []
    for pip_name, import_name in required:
        try:
            __import__(import_name)
            logger.info(f"✅ {pip_name}")
        except ImportError:
            missing.append(pip_name)
            logger.warning(f"❌ {pip_name}")
    
    if missing:
        logger.error(f"缺少依赖: {', '.join(missing)}")
        logger.info("请运行: pip install " + " ".join(missing))
        return False
    
    return True

def setup_environment():
    """设置环境"""
    logger = setup_logging()
    
    # 加载环境变量
    env_file = project_root / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info("✅ 加载环境变量文件")
    else:
        logger.warning("⚠️  未找到 .env 文件，使用默认配置")
        logger.info("💡 建议复制 .env.example 为 .env 并配置API密钥")
    
    # 导入配置
    try:
        from config import config
        config.print_summary()
        return config
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        return None

def init_database():
    """初始化数据库"""
    logger = setup_logging()
    
    try:
        from backend.database import init_db
        init_db()
        logger.info("✅ 数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def create_app():
    """创建FastAPI应用"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    
    from config import config
    from backend.api import agents, workflows
    
    # 创建应用
    app = FastAPI(
        title=config.APP_NAME,
        description=config.APP_DESCRIPTION,
        version=config.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
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
    static_dir = project_root / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 注册API路由
    app.include_router(agents.router)
    app.include_router(workflows.router)
    
    # 根端点
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用 OpenAgentFlow",
            "name": config.APP_NAME,
            "version": config.APP_VERSION,
            "description": config.APP_DESCRIPTION,
            "docs": "/docs",
            "endpoints": {
                "agents": "/api/v1/agents",
                "workflows": "/api/v1/workflows"
            }
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": config.APP_NAME,
            "version": config.APP_VERSION
        }
    
    @app.get("/system/info")
    async def system_info():
        import platform
        
        return {
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version()
            },
            "app": {
                "name": config.APP_NAME,
                "version": config.APP_VERSION,
                "host": config.HOST,
                "port": config.PORT
            }
        }
    
    return app

def run_server():
    """运行服务器"""
    logger = setup_logging()
    
    logger.info("🚀 启动 OpenAgentFlow 服务器")
    logger.info("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        logger.error("依赖检查失败")
        sys.exit(1)
    
    # 设置环境
    config = setup_environment()
    if not config:
        logger.error("环境设置失败")
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        logger.error("数据库初始化失败")
        sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    # 导入uvicorn
    import uvicorn
    
    # 运行服务器
    logger.info(f"🌐 服务器地址: http://{config.HOST}:{config.PORT}")
    logger.info(f"📚 API文档: http://{config.HOST}:{config.PORT}/docs")
    logger.info("=" * 50)
    logger.info("按 Ctrl+C 停止服务器")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    run_server()