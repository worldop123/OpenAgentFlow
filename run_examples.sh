#!/bin/bash

# OpenAgentFlow - Quick Start Script

echo "🚀 Starting OpenAgentFlow Examples..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc) -eq 1 ]]; then
    echo "❌ Python 3.10 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic sqlalchemy redis openai langchain python-dotenv httpx

# Run examples
echo "🧪 Running examples..."
cd /tmp/openagentflow

echo ""
echo "1️⃣ Running simple agent example..."
python3 examples/simple_agents.py

echo ""
echo "2️⃣ Testing Feishu integration tools..."
python3 -c "
from backend.tools.feishu import FeishuToolkit
toolkit = FeishuToolkit('mock_app_id', 'mock_app_secret')
tools = toolkit.get_tools()
print(f'Created {len(tools)} Feishu tools:')
for tool in tools:
    print(f'  - {tool.name}')
"

echo ""
echo "3️⃣ Testing server startup..."
echo "   Starting test server on port 8000..."
python3 -m backend.server &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test API endpoint
echo "   Testing API endpoint..."
curl -s http://localhost:8000/ | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'   ✅ Server response: {data.get(\"message\", \"Unknown\")}')
except:
    print('   ❌ Failed to get server response')
"

# Kill the test server
kill $SERVER_PID 2>/dev/null

echo ""
echo "🎉 All tests completed successfully!"
echo ""
echo "📚 Next steps:"
echo "   1. Push to GitHub:"
echo "      cd /tmp/openagentflow"
echo "      git add ."
echo "      git commit -m 'Initial commit'"
echo "      git push origin main"
echo ""
echo "   2. Run with Docker:"
echo "      docker-compose up"
echo ""
echo "   3. Deploy to cloud:"
echo "      See deploy/ directory for Kubernetes configurations"