# OpenAgentFlow

> **可组合的AI Agent工作流平台**  
> 开源的AI Agent协作框架，让多个AI智能体协同完成复杂任务

## 🎯 愿景
构建一个类似Zapier + LangChain + AutoGPT的开源平台，实现可视化编排多个AI Agent协同工作。

## ✨ 核心特性
- **可视化工作流编排** - 拖拽式创建AI Agent工作流
- **多模型支持** - GPT、Claude、本地模型无缝切换
- **工具集成** - 飞书、GitHub、API等常用工具
- **自主执行** - Agent可自主决策和任务分解
- **监控分析** - 实时追踪工作流执行状态

## 🏗️ 技术栈
- **后端**: Python + FastAPI + PostgreSQL + Redis
- **前端**: React + TypeScript + Tailwind CSS
- **部署**: Docker + Kubernetes
- **AI**: OpenAI API、Claude API、本地模型支持

## 🚀 快速开始
```bash
# 克隆仓库
git clone https://github.com/yourusername/OpenAgentFlow.git

# 安装依赖
cd OpenAgentFlow
pip install -r requirements.txt

# 启动服务
python -m openagentflow.server
```

## 📖 文档
- [架构设计](./docs/architecture.md)
- [API文档](./docs/api.md)
- [开发指南](./docs/development.md)
- [部署指南](./docs/deployment.md)

## 🤝 贡献
欢迎提交Issue和PR！详见[贡献指南](./CONTRIBUTING.md)。

## 📄 许可证
MIT License