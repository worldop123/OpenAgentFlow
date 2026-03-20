# 🚀 Getting Started with OpenAgentFlow

OpenAgentFlow is an open-source platform for building and orchestrating AI Agent workflows. Think of it as Zapier for AI Agents!

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- Docker (optional, for containerized deployment)
- OpenAI API key (or other LLM provider)

## 🔧 Installation

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/OpenAgentFlow.git
cd OpenAgentFlow

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Option 2: Docker Installation

```bash
# Using Docker Compose
docker-compose up

# Or build manually
docker build -t openagentflow .
docker run -p 8000:8000 openagentflow
```

### Option 3: Development Installation

```bash
# Clone and install with development dependencies
git clone https://github.com/yourusername/OpenAgentFlow.git
cd OpenAgentFlow
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 🎯 Quick Start

### 1. Create Your First Agent

```python
from openagentflow import LLMAgent, AgentMessage

# Create an AI assistant
assistant = LLMAgent(
    name="AI_Assistant",
    description="Helpful AI assistant",
    model="gpt-3.5-turbo"
)

# Send a message
message = AgentMessage(
    sender="User",
    content="Hello, how are you?"
)
response = await assistant.think(message)
print(response.content)
```

### 2. Create a Workflow

```python
from openagentflow import WorkflowEngine

# Initialize workflow engine
engine = WorkflowEngine()

# Create a workflow
workflow = engine.create_workflow(
    name="Content Creation",
    description="Research → Write → Edit workflow"
)

# Add agents to workflow
research_agent = LLMAgent(name="Researcher", description="Research specialist")
write_agent = LLMAgent(name="Writer", description="Content writer")
edit_agent = LLMAgent(name="Editor", description="Content editor")

engine.register_agent(research_agent)
engine.register_agent(write_agent)
engine.register_agent(edit_agent)

# Execute workflow
result = await engine.execute_workflow(
    workflow_id=workflow.id,
    initial_input={"topic": "AI in healthcare"}
)
```

### 3. Use Built-in Tools

```python
from openagentflow.tools import FeishuToolkit

# Initialize Feishu tools
feishu = FeishuToolkit(app_id="your_app_id", app_secret="your_app_secret")
tools = feishu.get_tools()

# Create agent with Feishu tools
agent = LLMAgent(
    name="Feishu_Assistant",
    description="Assistant that can use Feishu",
    tools=tools
)

# Now the agent can send Feishu messages, check calendars, etc.
```

## 🌐 API Server

Start the API server:

```bash
# Start development server
uvicorn openagentflow.server:app --reload

# Or use the provided script
python -m openagentflow.server
```

API will be available at: `http://localhost:8000`

### API Endpoints

- `GET /` - Welcome message and API info
- `POST /agents` - Create a new agent
- `GET /agents` - List all agents
- `POST /workflows` - Create a new workflow
- `POST /workflows/{id}/execute` - Execute a workflow
- `GET /docs` - Interactive API documentation (Swagger UI)

## 🧪 Examples

Check the `examples/` directory for more examples:

```bash
# Run all examples
./run_examples.sh

# Or run specific examples
python examples/simple_agents.py
python examples/feishu_integration.py
```

## 🔗 Integrations

OpenAgentFlow supports various integrations:

### Feishu (Lark) Integration
- Send messages to individuals or groups
- Check calendar availability
- Create calendar events
- Search messages

### GitHub Integration (Coming Soon)
- Create issues and PRs
- Check CI/CD status
- Manage repositories

### Custom Integrations
You can create custom tools by extending the `AgentTool` class.

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f deploy/kubernetes/

# Check pods
kubectl get pods -n openagentflow
```

### Cloud Providers
- AWS: ECS/EKS deployment files in `deploy/aws/`
- GCP: GKE deployment files in `deploy/gcp/`
- Azure: AKS deployment files in `deploy/azure/`

## 📚 Learning Resources

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Documentation](./docs/API.md)
- [Agent Development Guide](./docs/AGENT_DEVELOPMENT.md)
- [Workflow Design Patterns](./docs/WORKFLOW_PATTERNS.md)
- [Contributing Guide](./CONTRIBUTING.md)

## 🆘 Need Help?

- Check the [FAQ](./docs/FAQ.md)
- Open an [Issue](https://github.com/yourusername/OpenAgentFlow/issues)
- Join our [Discord Community](https://discord.gg/openagentflow)

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Happy Building!** 🚀

If you find OpenAgentFlow useful, please give us a ⭐ on GitHub!