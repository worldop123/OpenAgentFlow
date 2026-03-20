#!/bin/bash

# OpenAgentFlow 简化启动脚本
# 不需要安装依赖，直接运行核心功能

echo "🚀 启动 OpenAgentFlow 简化版"
echo "========================================"

# 检查Python版本
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python版本: $PYTHON_VERSION"

# 检查核心文件
echo "📁 检查项目结构..."
if [ -f "backend/server.py" ]; then
    echo "✅ server.py 存在"
else
    echo "❌ server.py 不存在"
    exit 1
fi

if [ -f "config.py" ]; then
    echo "✅ config.py 存在"
else
    echo "❌ config.py 不存在"
    exit 1
fi

# 创建.env文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置API密钥"
fi

# 创建数据库目录
mkdir -p data

# 运行系统检查
echo "🔧 运行系统检查..."
python3 -c "
import sys
print('Python路径:', sys.executable)
print('Python版本:', sys.version)

# 检查基本模块
modules = ['json', 'datetime', 'typing', 'pathlib', 'os', 'sys']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')

print('\\n✅ 基本检查完成')
"

# 启动服务器
echo "🚀 启动服务器..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"

# 运行服务器
cd /tmp/openagentflow && python3 -m backend.server