# 贡献指南

感谢您对OpenAgentFlow项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进UI/UX设计
- 🌐 翻译本地化

## 🚀 开始贡献

### 1. 设置开发环境

```bash
# 1. Fork项目
# 在GitHub上点击Fork按钮

# 2. 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/OpenAgentFlow.git
cd OpenAgentFlow

# 3. 添加上游仓库
git remote add upstream https://github.com/worldop123/OpenAgentFlow.git

# 4. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 5. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. 设置环境变量
cp .env.example .env
# 编辑 .env 文件
```

### 2. 创建分支

```bash
# 同步最新代码
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name
# 或修复Bug
git checkout -b fix/issue-number-description
```

### 3. 开发流程

#### 代码规范

我们使用以下工具确保代码质量：

```bash
# 代码格式化
black backend/ tests/
isort backend/ tests/

# 代码检查
flake8 backend/ tests/
mypy backend/

# 运行测试
pytest tests/ -v --cov=backend

# 构建文档
mkdocs serve
```

#### 提交规范

我们使用约定式提交：

```bash
# 提交类型：
# feat: 新功能
# fix: 修复Bug
# docs: 文档更新
# style: 代码格式（不影响功能）
# refactor: 代码重构
# test: 测试相关
# chore: 构建过程或辅助工具

# 提交示例：
git commit -m "feat: 添加飞书消息发送功能"
git commit -m "fix: 修复工作流执行时的内存泄漏"
git commit -m "docs: 更新快速开始指南"
```

### 4. 测试

所有新功能必须包含测试：

```python
# 单元测试示例
import pytest
from backend.agent.base import LLMAgent

def test_llm_agent_initialization():
    """测试LLMAgent初始化"""
    agent = LLMAgent(name="Test Agent", model="gpt-3.5-turbo")
    assert agent.name == "Test Agent"
    assert agent.model == "gpt-3.5-turbo"

# API测试示例
from fastapi.testclient import TestClient

def test_health_endpoint():
    """测试健康检查端点"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 5. 提交Pull Request

1. 推送您的分支到GitHub
2. 在GitHub上创建Pull Request
3. 填写PR模板
4. 等待代码审查

## 📋 Pull Request模板

### 描述
请简要描述这个PR的目的：

### 相关Issue
链接相关Issue（如果有）：
- Fixes #123
- Related to #456

### 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 测试相关
- [ ] 其他（请说明）：

### 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 更新了CHANGELOG.md
- [ ] 代码审查通过

### 测试结果
- 单元测试：✅ 通过 / ❌ 失败
- API测试：✅ 通过 / ❌ 失败
- 集成测试：✅ 通过 / ❌ 失败

### 截图（如果适用）
<!-- 添加UI变更的截图 -->

## 🐛 报告Bug

### Bug报告模板

```markdown
## 问题描述
清晰简洁地描述问题

## 重现步骤
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 预期行为
清晰简洁地描述您期望发生的事情

## 实际行为
清晰简洁地描述实际发生的事情

## 环境信息
- 操作系统：[例如 Windows 10, macOS 12.0]
- 浏览器：[例如 Chrome 96, Safari 15]
- OpenAgentFlow版本：[例如 0.1.0]
- Python版本：[例如 3.11.0]

## 截图
如果适用，添加截图

## 日志
如果有相关日志，请粘贴

## 可能的解决方案
如果您有解决方案的建议
```

## 💡 提出新功能

### 功能请求模板

```markdown
## 功能描述
清晰简洁地描述您想要的功能

## 使用场景
描述这个功能的使用场景

- [场景1]：当用户需要...时
- [场景2]：在...情况下

## 替代方案
描述您考虑过的替代方案

## 附加信息
添加任何其他信息或截图
```

## 🏗️ 项目结构

```
.
├── backend/           # 后端代码
│   ├── agent/        # Agent实现
│   ├── api/          # API端点
│   ├── database/     # 数据库相关
│   ├── server/       # 服务器配置
│   └── tools/        # 工具集成
├── frontend/         # 前端代码
├── tests/            # 测试代码
├── docs/             # 文档
├── examples/         # 示例代码
└── scripts/          # 构建脚本
```

## 🔧 核心开发

### Agent开发

```python
# 自定义Agent示例
from backend.agent.base import BaseAgent

class CustomAgent(BaseAgent):
    """自定义Agent示例"""
    
    def __init__(self, name, custom_param):
        super().__init__(name)
        self.custom_param = custom_param
    
    async def process(self, input_data):
        """处理输入数据"""
        # 实现您的逻辑
        return f"Processed: {input_data}"
    
    async def validate(self):
        """验证Agent配置"""
        return True
```

### 工具集成开发

```python
# 新工具集成示例
from backend.tools.base import BaseTool

class NewTool(BaseTool):
    """新工具集成"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get("api_key")
    
    async def send_message(self, recipient, message):
        """发送消息"""
        # 实现API调用
        pass
```

## 📚 文档贡献

### 文档结构

```
docs/
├── index.md          # 主页
├── getting-started/  # 快速开始
├── user-guide/       # 用户指南
├── api-reference/    # API参考
├── development/      # 开发指南
└── examples/         # 示例
```

### 编写文档

- 使用Markdown格式
- 包含代码示例
- 添加截图或图表
- 保持语言简洁明了

## 🎨 设计贡献

### UI/UX指南

1. **设计系统**
   - 使用项目设计规范
   - 保持一致性
   - 响应式设计

2. **组件开发**
   - 可复用组件
   - 适当的文档
   - 测试覆盖

3. **用户体验**
   - 用户友好的界面
   - 清晰的反馈
   - 无障碍访问

## 🌐 翻译贡献

### 本地化流程

1. 复制语言文件
2. 翻译文本内容
3. 测试翻译
4. 提交PR

```bash
# 翻译文件位置
static/locales/
├── en/              # 英语
├── zh-CN/           # 简体中文
└── zh-TW/           # 繁体中文
```

## 🏆 贡献者公约

### 行为准则

1. **尊重他人**
   - 使用友好和尊重的语言
   - 接受建设性批评
   - 专注于项目而不是个人

2. **协作精神**
   - 帮助新成员
   - 分享知识和经验
   - 共同解决问题

3. **专业态度**
   - 保持专业
   - 遵守截止日期
   - 承担责任

### 沟通渠道

- **GitHub Issues**: Bug报告和功能请求
- **Pull Requests**: 代码贡献
- **Discord**: 实时讨论
- **邮件列表**: 重要公告

## 📈 贡献者排名

我们使用以下指标评估贡献：

1. **代码贡献**: PR数量和质量
2. **问题解决**: 解决的Issue数量
3. **文档贡献**: 文档改进
4. **社区支持**: 帮助其他用户
5. **测试贡献**: 编写测试用例

## 🎉 感谢贡献者

所有贡献者将被记录在项目的贡献者列表中：

```bash
# 查看贡献者
git shortlog -sn --all
```

---

感谢您为OpenAgentFlow项目做出贡献！您的每一份努力都将帮助这个项目变得更好。🚀