"""DingTalk (钉钉) integration tools for OpenAgentFlow"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..agent.base import AgentTool


class DingTalkMessage(BaseModel):
    """DingTalk message structure"""
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
    content: str
    msg_type: str = "text"


class DingTalkToolkit:
    """Collection of DingTalk tools for AI Agents"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        
    def get_tools(self) -> List[AgentTool]:
        """Get all DingTalk tools as AgentTool objects"""
        return [
            self._create_send_message_tool(),
            self._create_create_group_tool(),
            self._create_send_work_notification_tool(),
            self._create_get_department_info_tool(),
            self._create_send_task_tool()
        ]
    
    def _create_send_message_tool(self) -> AgentTool:
        """Create tool for sending DingTalk messages"""
        def send_dingtalk_message(
            content: str,
            chat_id: Optional[str] = None,
            user_id: Optional[str] = None,
            msg_type: str = "text"
        ) -> Dict[str, Any]:
            """Send a message to DingTalk
            
            Args:
                content: Message content
                chat_id: Group chat ID

                user_id: User ID
                msg_type: Message type: text, markdown, image
            """
            # Mock implementation
            print(f"[DingTalk] Sending {msg_type} message: {content[:50]}...")
            
            return {
                "success": True,
                "message_id": f"ding_msg_{hash(content) % 10000}",
                "content": content,
                "recipient": chat_id or user_id
            }
        
        return AgentTool(
            name="send_dingtalk_message",
            description="Send a message to DingTalk (钉钉) chat or user",
            parameters={
                "content": "Message content (required)",
                "chat_id": "Group chat ID (optional)",
                "user_id": "User ID (optional)",
                "msg_type": "Message type: text, markdown, image (default: text)"

            },
            function=send_dingtalk_message

        )
    
    def _create_create_group_tool(self) -> AgentTool:
        """Create tool for creating DingTalk groups"""
        def create_dingtalk_group(
            name: str,
            user_ids: List[str],
            description: Optional[str] = None

        ) -> Dict[str, Any]:
            """Create a new group chat in DingTalk
            
            Args:
                name: Group name

                user_ids: List of user IDs to add

                description: Group description (optional)
            """
            print(f"[DingTalk] Creating group: {name}")
            
            return {
                "success": True,
                "group_id": f"ding_group_{hash(name) % 10000}",
                "name": name,
                "user_ids": user_ids,
                "chat_url": "https://example.com/dingtalk/group/mock"

            }
        
        return AgentTool(
            name="create_dingtalk_group",
            description="Create a new group chat in DingTalk (钉钉)",
            parameters={
                "name": "Group name (required)",
                "user_ids": "List of user IDs to add (required)",
                "description": "Group description (optional)"
            },
            function=create_dingtalk_group

        )
    
    def _create_send_work_notification_tool(self) -> AgentTool:
        """Create tool for sending work notifications"""
        def send_work_notification(
            title: str,
            content: str,
            user_ids: List[str],
            priority: str = "normal"
        ) -> Dict[str, Any]:
            """Send a work notification in DingTalk
            
            Args:
                title: Notification title

                content: Notification content
                user_ids: List of user IDs to notify

                priority: Priority level: normal, urgent (default: normal)"
            """
            print(f"[DingTalk] Sending work notification: {title}")
            
            return {
                "success": True,
                "notification_id": f"ding_notif_{hash(title) % 10000}",
                "title": title,
                "content": content,
                "priority": priority,
                "sent_to": len(user_ids)

            }
        
        return AgentTool(
            name="send_work_notification",
            description="Send work notifications via DingTalk (钉钉)",
            parameters={
                "title": "Notification title (required)",
                "content": "Notification content (required)",
                "user_ids": "List of user IDs to notify (required)",
                "priority": "Priority level: normal, urgent (default: normal)"
            },
            function=send_work_notification

        )
    
    def _create_get_department_info_tool(self) -> AgentTool:
        """Create tool for getting department information"""
        def get_department_info(
            department_id: str
        ) -> Dict[str, Any]:
            """Get department information from DingTalk
            
            Args:
                department_id: Department ID
            """
            print(f"[DingTalk] Getting department info: {department_id}")
            
            return {
                "success": True,
                "department_id": department_id,
                "name": "Engineering Department",
                "parent_id": "0",
                "user_count": 50,
                "sub_departments": ["frontend", "backend", "devops"]
            }
        
        return AgentTool(
            name="get_department_info",
            description="Get department information from DingTalk (钉钉)",
            parameters={
                "department_id": "Department ID (required)"
            },
            function=get_department_info

        )
    
    def _create_send_task_tool(self) -> AgentTool:
        """Create tool for sending tasks"""
        def send_task(
            title: str,
            description: str,
            user_ids: List[str],
            due_date: Optional[str] = None
        ) -> Dict[str, Any]:
            """Assign tasks to users in DingTalk
            
            Args:
                title: Task title
                description: Task description
                user_ids: List of user IDs to assign
                due_date: Due date (ISO format) (optional)"
            """
            print(f"[DingTalk] Sending task: {title}")
            
            return {
                "success": True,
                "task_id": f"ding_task_{hash(title) % 10000}",
                "title": title,
                "description": description,
                "assigned_to": user_ids,
                "status": "pending",
                "created_at": "2024-01-01T10:00:00Z"

            }
        
        return AgentTool(
            name="send_task",
            description="Assign tasks to users via DingTalk (钉钉)",
            parameters={
                "title": "Task title (required)",
                "description": "Task description (required)",
                "user_ids": "List of user IDs to assign (required)",
                "due_date": "Due date (ISO format) (optional)"
            },
            function=send_task

        )


if __name__ == "__main__":
    toolkit = DingTalkToolkit(app_key="mock_app_key", app_secret="mock_app_secret")

    tools = toolkit.get_t