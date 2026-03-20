"""WeCom (企业微信) integration tools for OpenAgentFlow"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..agent.base import AgentTool


class WeComMessage(BaseModel):
    """WeCom message structure"""
    to_user: Optional[str] = None
    to_party: Optional[str] = None
    to_tag: Optional[str] = None
    msg_type: str = "text"
    content: str


class WeComToolkit:
    """Collection of WeCom (企业微信) tools for AI Agents"""
    
    def __init__(self, corp_id: str, corp_secret: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        
    def get_tools(self) -> List[AgentTool]:
        """Get all WeCom tools as AgentTool objects"""
        return [
            self._create_send_message_tool(),
            self._create_send_news_tool(),
            self._create_send_task_tool(),
            self._create_get_user_info_tool(),
            self._create_create_app_tool(),
            self._create_send_approval_tool()
        ]
    
    def _create_send_message_tool(self) -> AgentTool:
        """Create tool for sending WeCom messages"""
        def send_wecom_message(
            content: str,
            msg_type: str = "text",
            to_user: Optional[str] = None,
            to_party: Optional[str] = None,
            to_tag: Optional[str] = None
        ) -> Dict[str, Any]:
            """Send a message to WeCom (企业微信)
            
            Args:
                content: Message content
                msg_type: Message type: text, markdown, image, news
                to_user: User ID (@all for all users)
                to_party: Department ID
                to_tag: Tag ID
            """
            print(f"[WeCom] Sending {msg_type} message: {content[:50]}...")
            
            return {
                "success": True,
                "message_id": f"wecom_msg_{hash(content) % 10000}",
                "msg_type": msg_type,
                "recipient": {
                    "user": to_user,
                    "party": to_party,
                    "tag": to_tag
                },
                "content": content
            }
        
        return AgentTool(
            name="send_wecom_message",
            description="Send a message to WeCom (企业微信)",
            parameters={
                "content": "Message content (required)",
                "msg_type": "Message type: text, markdown, image, news (default: text)",
                "to_user": "User ID (@all for all users) (optional)",
                "to_party": "Department ID (optional)",
                "to_tag": "Tag ID (optional)"
            },
            function=send_wecom_message
        )
    
    def _create_send_news_tool(self) -> AgentTool:
        """Create tool for sending news articles"""
        def send_wecom_news(
            title: str,
            description: str,
            url: str,
            pic_url: Optional[str] = None,
            to_user: Optional[str] = None
        ) -> Dict[str, Any]:
            """Send a news article to WeCom
            
            Args:
                title: Article title
                description: Article description
                url: Article URL
                pic_url: Cover image URL (optional)
                to_user: User ID (@all for all users) (optional)
            """
            print(f"[WeCom] Sending news: {title}")
            
            return {
                "success": True,
                "news_id": f"wecom_news_{hash(title) % 10000}",
                "title": title,
                "description": description,
                "url": url,
                "sent_to": to_user or "@all"
            }
        
        return AgentTool(
            name="send_wecom_news",
            description="Send news articles to WeCom (企业微信)",
            parameters={
                "title": "Article title (required)",
                "description": "Article description (required)",
                "url": "Article URL (required)",
                "pic_url": "Cover image URL (optional)",
                "to_user": "User ID (@all for all users) (optional)"
            },
            function=send_wecom_news
        )
    
    def _create_send_task_tool(self) -> AgentTool:
        """Create tool for sending tasks"""
        def send_wecom_task(
            title: str,
            description: str,
            user_ids: List[str],
            due_time: Optional[str] = None,
            priority: int = 1
        ) -> Dict[str, Any]:
            """Send a task to WeCom users
            
            Args:
                title: Task title
                description: Task description
                user_ids: List of user IDs
                due_time: Due time (ISO format) (optional)
                priority: Priority level (1-3, default: 1)
            """
            print(f"[WeCom] Sending task: {title}")
            
            return {
                "success": True,
                "task_id": f"wecom_task_{hash(title) % 10000}",
                "title": title,
                "description": description,
                "assigned_to": user_ids,
                "priority": priority,
                "status": "pending"
            }
        
        return AgentTool(
            name="send_wecom_task",
            description="Send tasks to WeCom (企业微信) users",
            parameters={
                "title": "Task title (required)",
                "description": "Task description (required)",
                "user_ids": "List of user IDs (required)",
                "due_time": "Due time (ISO format) (optional)",
                "priority": "Priority level (1-3, default: 1)"
            },
            function=send_wecom_task
        )
    
    def _create_get_user_info_tool(self) -> AgentTool:
        """Create tool for getting user information"""
        def get_wecom_user_info(
            user_id: str
        ) -> Dict[str, Any]:
            """Get user information from WeCom
            
            Args:
                user_id: User ID
            """
            print(f"[WeCom] Getting user info: {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "name": "张三",
                "department": ["Engineering", "Backend"],
                "position": "Senior Developer",
                "mobile": "138****8888",
                "email": "zhangsan@company.com",
                "status": "active"
            }
        
        return AgentTool(
            name="get_wecom_user_info",
            description="Get user information from WeCom (企业微信)",
            parameters={
                "user_id": "User ID (required)"
            },
            function=get_wecom_user_info
        )
    
    def _create_create_app_tool(self) -> AgentTool:
        """Create tool for creating WeCom applications"""
        def create_wecom_app(
            name: str,
            description: str,
            app_type: str = "custom"
        ) -> Dict[str, Any]:
            """Create a new WeCom application
            
            Args:
                name: Application name
                description: Application description
                app_type: Application type: custom, approval, report, etc.
            """
            print(f"[WeCom] Creating app: {name}")
            
            return {
                "success": True,
                "app_id": f"wecom_app_{hash(name) % 10000}",
                "name": name,
                "description": description,
                "type": app_type,
                "secret": f"app_secret_{hash(name) % 10000}",
                "access_token": f"token_{hash(name) % 10000}"
            }
        
        return AgentTool(
            name="create_wecom_app",
            description="Create a new WeCom (企业微信) application",
            parameters={
                "name": "Application name (required)",
                "description": "Application description (required)",
                "app_type": "Application type: custom, approval, report, etc. (default: custom)"
            },
            function=create_wecom_app
        )
    
    def _create_send_approval_tool(self) -> AgentTool:
        """Create tool for sending approval requests"""
        def send_wecom_approval(
            template_id: str,
            applicant_user_id: str,
            approver_user_ids: List[str],
            data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Send an approval request in WeCom
            
            Args:
                template_id: Approval template ID
                applicant_user_id: Applicant user ID
                approver_user_ids: List of approver user IDs
                data: Approval data
            """
            print(f"[WeCom] Sending approval request")
            
            return {
                "success": True,
                "approval_id": f"wecom_approval_{hash(str(data)) % 10000}",
                "template_id": template_id,
                "applicant": applicant_user_id,
                "approvers": approver_user_ids,
                "status": "pending",
                "create_time": "2024-01-01T10:00:00Z"
            }
        
        return AgentTool(
            name="send_wecom_approval",
            description="Send approval requests via WeCom (企业微信)",
            parameters={
                "template_id": "Approval template ID (required)",
                "applicant_user_id": "Applicant user ID (required)",
                "approver_user_ids": "List of approver user IDs (required)",
                "data": "Approval data (required)"
            },
            function=send_wecom_approval
        )


if __name__ == "__main__":
    # Test the toolkit
    toolkit = WeComToolkit(corp_id="mock_corp_id", corp_secret="mock_corp_secret")
    tools = toolkit.get_tools()
    print(f"Created {len(tools)} WeCom tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")