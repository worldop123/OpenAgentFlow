"""高级工作流示例 - 使用插件系统"""

import asyncio
import json
from typing import Dict, Any
from backend.agent.factory import AgentFactory
from backend.workflow.engine import WorkflowEngine, WorkflowInstance
from backend.plugins import plugin_manager


class AdvancedWorkflowExample:
    """高级工作流示例"""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        self.agent_factory = AgentFactory()
        self.workflow_id = None
        
        # 注册示例Agents
        self._register_agents()
        
        # 加载插件
        self._load_plugins()
    
    def _register_agents(self):
        """注册示例Agents"""
        # 注册LLM Agent
        llm_agent = self.agent_factory.create_agent(
            name="AI分析助手",
            agent_type="llm",
            config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "system_prompt": "你是一个专业的数据分析师，能够对数据进行深入分析和洞察。"
            }
        )
        
        # 注册工具Agent
        tool_agent = self.agent_factory.create_agent(
            name="数据处理工具",
            agent_type="tool",
            config={
                "tools": ["json_parser", "data_filter", "statistics_calculator"],
                "timeout": 30
            }
        )
        
        # 注册到引擎
        self.engine.register_agent(llm_agent)
        self.engine.register_agent(tool_agent)
    
    def _load_plugins(self):
        """加载插件"""
        print("加载插件...")
        
        # 调用插件管理器加载插件
        plugin_manager.load_plugins()
        
        # 启用所有插件
        for plugin_name in plugin_manager.plugins.keys():
            plugin_manager.enable_plugin(plugin_name)
        
        print(f"已加载 {len(plugin_manager.plugins)} 个插件")
        
        # 显示可用插件
        plugins = plugin_manager.list_plugins()
        for plugin in plugins:
            print(f"  - {plugin['name']} v{plugin['version']} ({'启用' if plugin['enabled'] else '禁用'})")
    
    def create_workflow(self):
        """创建高级工作流"""
        workflow = self.engine.create_workflow(
            name="企业数据分析流程",
            description="集成数据预处理、AI分析和报告生成的完整流程"
        )
        
        self.workflow_id = workflow.id
        
        # 定义节点
        nodes = [
            {
                "id": "data_input",
                "type": "input",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "数据输入",
                    "description": "原始数据输入点"
                }
            },
            {
                "id": "data_cleaning",
                "type": "agent",
                "position": {"x": 300, "y": 100},
                "data": {
                    "label": "数据清洗",
                    "agent_id": "数据处理工具",
                    "tool": "data_filter",
                    "parameters": {
                        "remove_null": True,
                        "normalize": True
                    }
                }
            },
            {
                "id": "ml_analysis",
                "type": "agent",
                "position": {"x": 500, "y": 100},
                "data": {
                    "label": "机器学习分析",
                    "agent_id": "ml_classifier",  # 来自插件
                    "parameters": {
                        "model_type": "random_forest",
                        "train_split": 0.8
                    }
                }
            },
            {
                "id": "ai_insight",
                "type": "agent",
                "position": {"x": 700, "y": 100},
                "data": {
                    "label": "AI深度分析",
                    "agent_id": "AI分析助手",
                    "prompt_template": "基于以下数据，提供深入的业务洞察：{data}"
                }
            },
            {
                "id": "report_generation",
                "type": "agent",
                "position": {"x": 900, "y": 100},
                "data": {
                    "label": "报告生成",
                    "agent_id": "report_generator",  # 可以来自未来插件
                    "format": "markdown",
                    "template": "standard"
                }
            },
            {
                "id": "slack_notification",
                "type": "agent",
                "position": {"x": 1100, "y": 100},
                "data": {
                    "label": "Slack通知",
                    "agent_id": "slack_integration",  # 来自Slack插件
                    "channel": "#data-reports",
                    "message_template": "数据分析完成，请查收报告。"
                }
            },
            {
                "id": "workflow_end",
                "type": "output",
                "position": {"x": 1300, "y": 100},
                "data": {
                    "label": "流程完成",
                    "description": "工作流执行完成"
                }
            }
        ]
        
        # 定义连接
        edges = [
            {
                "id": "e1",
                "source": "data_input",
                "target": "data_cleaning",
                "label": "原始数据"
            },
            {
                "id": "e2",
                "source": "data_cleaning",
                "target": "ml_analysis",
                "label": "清洗后数据"
            },
            {
                "id": "e3",
                "source": "ml_analysis",
                "target": "ai_insight",
                "label": "分析结果"
            },
            {
                "id": "e4",
                "source": "ai_insight",
                "target": "report_generation",
                "label": "洞察信息"
            },
            {
                "id": "e5",
                "source": "report_generation",
                "target": "slack_notification",
                "label": "生成报告"
            },
            {
                "id": "e6",
                "source": "slack_notification",
                "target": "workflow_end",
                "label": "通知完成"
            }
        ]
        
        # 创建条件分支（可选）
        condition_nodes = [
            {
                "id": "quality_check",
                "type": "condition",
                "position": {"x": 300, "y": 250},
                "data": {
                    "label": "数据质量检查",
                    "condition": "data_quality_score >= 0.8",
                    "true_branch": "high_quality_analysis",
                    "false_branch": "data_improvement"
                }
            },
            {
                "id": "high_quality_analysis",
                "type": "agent",
                "position": {"x": 500, "y": 250},
                "data": {
                    "label": "高质量数据分析",
                    "agent_id": "AI分析助手"
                }
            },
            {
                "id": "data_improvement",
                "type": "agent",
                "position": {"x": 500, "y": 400},
                "data": {
                    "label": "数据质量提升",
                    "agent_id": "数据处理工具"
                }
            }
        ]
        
        # 添加条件分支
        nodes.extend(condition_nodes)
        
        # 设置工作流定义
        workflow.nodes = nodes
        workflow.edges = edges
        
        return workflow
    
    async def execute_workflow(self, input_data: Dict[str, Any]):
        """执行工作流"""
        if not self.workflow_id:
            print("错误：未创建工作流")
            return
        
        # 获取工作流
        workflow = self.engine.get_workflow(self.workflow_id)
        
        # 创建工作流实例
        instance = WorkflowInstance(
            workflow_id=workflow.id,
            nodes=workflow.nodes,
            edges=workflow.edges
        )
        
        # 设置Agents
        instance.agents = {
            "AI分析助手": self.engine.agents.get("AI分析助手"),
            "数据处理工具": self.engine.agents.get("数据处理工具"),
            "ml_classifier": plugin_manager.get_plugin("Machine Learning").get_agent("ml_classifier"),
            "slack_integration": plugin_manager.get_plugin("Slack Integration").get_tool("slack_send_message")
        }
        
        print(f"执行工作流：{workflow.name}")
        print(f"输入数据：{json.dumps(input_data, indent=2, ensure_ascii=False)}")
        
        # 执行工作流
        result = await instance.execute(input_data)
        
        print(f"执行结果：{json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    
    def export_workflow(self):
        """导出工作流定义"""
        if not self.workflow_id:
            print("错误：未创建工作流")
            return
        
        workflow = self.engine.get_workflow(self.workflow_id)
        
        workflow_def = {
            "workflow": {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "nodes": workflow.nodes,
                "edges": workflow.edges,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
            },
            "agents": list(self.engine.agents.keys()),
            "plugins": [plugin.name for plugin in plugin_manager.plugins.values()],
            "exported_at": datetime.datetime.now().isoformat()
        }
        
        # 保存到文件
        filename = f"workflow_{workflow.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(workflow_def, f, indent=2, ensure_ascii=False)
        
        print(f"工作流已导出到：{filename}")
        return filename


# 异步执行示例
async def main():
    """主函数示例"""
    print("=" * 60)
    print("OpenAgentFlow 高级工作流示例")
    print("=" * 60)
    
    # 创建示例
    example = AdvancedWorkflowExample()
    
    # 创建工作流
    workflow = example.create_workflow()
    print(f"创建工作流成功：{workflow.name}")
    
    # 准备示例数据
    input_data = {
        "data": [
            {"customer_id": 1, "age": 32, "purchase_amount": 150.5, "category": "electronics"},
            {"customer_id": 2, "age": 45, "purchase_amount": 89.99, "category": "clothing"},
            {"customer_id": 3, "age": 28, "purchase_amount": 250.0, "category": "electronics"},
            {"customer_id": 4, "age": 60, "purchase_amount": 120.75, "category": "home"},
            {"customer_id": 5, "age": 22, "purchase_amount": 75.25, "category": "clothing"}
        ],
        "analysis_type": "customer_segmentation",
        "data_quality_score": 0.85
    }
    
    # 执行工作流
    print("\n执行工作流...")
    result = await example.execute_workflow(input_data)
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    import datetime
    
    # 运行异步主函数
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(main())
    finally:
        loop.close()