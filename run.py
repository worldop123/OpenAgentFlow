#!/usr/bin/env python3
"""
OpenAgentFlow 启动脚本
最小可运行版本
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """设置环境"""
    print("🔧 设置环境...")
    
    # 检查环境变量文件
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  未找到 .env 文件，使用默认配置")
        print("💡 建议复制 .env.example 为 .env 并配置API密钥")
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # 导入配置
    from config import config
    config.print_summary()
    
    # 验证配置
    if not config.validate():
        print("❌ 配置验证失败，请检查环境变量")
        sys.exit(1)
    
    return config

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "python-dotenv",
        "httpx",
        "openai"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("💡 请运行: pip install " + " ".join(missing))
        return False
    
    print("✅ 所有依赖已安装")
    return True

def create_database():
    """创建数据库"""
    print("🗄️  初始化数据库...")
    
    try:
        from backend.database import init_db
        init_db()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动 OpenAgentFlow 服务器...")
    
    import uvicorn
    from config import config
    
    uvicorn.run(
        "backend.server:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

def run_example():
    """运行示例"""
    print("🧪 运行示例...")
    
    try:
        from examples.simple_agents import main
        asyncio.run(main())
        return True
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*50)
    print("🎯 OpenAgentFlow - AI Agent 工作流平台")
    print("="*50)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="OpenAgentFlow 启动脚本")
    parser.add_argument("--setup", action="store_true", help="仅进行设置检查")
    parser.add_argument("--example", action="store_true", help="运行示例")
    parser.add_argument("--server", action="store_true", help="启动服务器")
    parser.add_argument("--all", action="store_true", help="运行所有检查")
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认运行所有
    if not any([args.setup, args.example, args.server, args.all]):
        args.all = True
    
    # 设置环境
    config = setup_environment()
    
    success = True
    
    if args.setup or args.all:
        success = check_dependencies() and success
        success = create_database() and success
    
    if args.example or args.all:
        success = run_example() and success
    
    if args.server or args.all:
        if success:
            start_server()
        else:
            print("❌ 前置检查失败，无法启动服务器")
            sys.exit(1)
    
    if not success:
        print("\n⚠️  部分步骤失败，请检查上述错误")
        sys.exit(1)

if __name__ == "__main__":
    main()