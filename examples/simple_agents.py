"""Example: Simple AI Agents for OpenAgentFlow"""

import asyncio
from backend.agent.base import LLMAgent, AgentMessage


async def example_single_agent():
    """Example of a single agent conversation"""
    print("🤖 Creating AI Assistant Agent...")
    
    # Create an AI assistant agent
    assistant = LLMAgent(
        name="AI_Assistant",
        description="A helpful AI assistant that answers questions",
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful AI assistant. Answer questions clearly and concisely."
    )
    
    # Simulate a conversation
    user_message = AgentMessage(
        sender="User",
        content="What is OpenAgentFlow and why is it useful?"
    )
    
    print(f"👤 User: {user_message.content}")
    response = await assistant.think(user_message)
    print(f"🤖 AI Assistant: {response.content}")
    
    return assistant


async def example_multi_agent_workflow():
    """Example of multiple agents working together"""
    print("\n🔄 Creating multi-agent workflow...")
    
    # Create specialized agents
    researcher = LLMAgent(
        name="Researcher",
        description="Researches topics and gathers information",
        model="gpt-3.5-turbo",
        system_prompt="You are a research specialist. Find relevant information and summarize key points."
    )
    
    writer = LLMAgent(
        name="Writer",
        description="Writes content based on research",
        model="gpt-3.5-turbo",
        system_prompt="You are a professional writer. Create well-structured content from research notes."
    )
    
    editor = LLMAgent(
        name="Editor",
        description="Reviews and improves written content",
        model="gpt-3.5-turbo",
        system_prompt="You are an editor. Check for clarity, grammar, and structure improvements."
    )
    
    # Simulate a research -> write -> edit workflow
    research_topic = "The impact of AI Agents on business automation"
    
    print(f"📚 Researching: {research_topic}")
    research_request = AgentMessage(sender="User", content=research_topic)
    research_result = await researcher.think(research_request)
    
    print(f"📝 Writing article based on research...")
    write_request = AgentMessage(
        sender="Researcher",
        content=f"Research findings: {research_result.content}\n\nPlease write an article about this."
    )
    article = await writer.think(write_request)
    
    print(f"✏️ Editing the article...")
    edit_request = AgentMessage(
        sender="Writer", 
        content=f"Article draft: {article.content}\n\nPlease review and improve."
    )
    final_article = await editor.think(edit_request)
    
    print(f"\n✅ Final Article Preview:")
    print(f"   Title: {research_topic}")
    print(f"   Length: {len(final_article.content)} characters")
    print(f"   First 200 chars: {final_article.content[:200]}...")
    
    return researcher, writer, editor


async def example_custom_tools():
    """Example of agents using custom tools"""
    print("\n🛠️ Creating agents with custom tools...")
    
    # Define some simple tools
    from backend.agent.base import AgentTool
    
    def calculate_sum(numbers: list) -> float:
        """Calculate the sum of numbers"""
        return sum(numbers)
    
    def get_current_time() -> str:
        """Get current time"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create tools
    calculator_tool = AgentTool(
        name="calculator",
        description="Calculate mathematical operations",
        parameters={"numbers": "list of numbers to sum"},
        function=calculate_sum
    )
    
    time_tool = AgentTool(
        name="get_time",
        description="Get current date and time",
        parameters={},
        function=get_current_time
    )
    
    # Create agent with tools
    smart_agent = LLMAgent(
        name="Smart_Assistant",
        description="An assistant that can use tools",
        model="gpt-3.5-turbo",
        tools=[calculator_tool, time_tool]
    )
    
    # Test tool usage
    print("🧮 Testing calculator tool...")
    test_numbers = [1, 2, 3, 4, 5]
    result = calculator_tool.function(test_numbers)
    print(f"   Sum of {test_numbers} = {result}")
    
    print("⏰ Testing time tool...")
    current_time = time_tool.function()
    print(f"   Current time: {current_time}")
    
    return smart_agent


if __name__ == "__main__":
    """Run all examples"""
    print("=" * 60)
    print("🚀 OpenAgentFlow Examples")
    print("=" * 60)
    
    # Run examples
    asyncio.run(example_single_agent())
    asyncio.run(example_multi_agent_workflow())
    asyncio.run(example_custom_tools())
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)