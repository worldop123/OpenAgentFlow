"""Feishu (Lark) integration tools for OpenAgentFlow"""

import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..agent.base import AgentTool


class FeishuMessage(BaseModel):
    """Feishu message structure"""
    chat_id: Optional[str] = None
    open_id: Optional[str] = None
    content: str
    msg_type: str = "text"
    receive_id_type: str = "open_id"


class FeishuToolkit:
    """Collection of Feishu tools for AI Agents"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        # Note: In a real implementation, you would initialize Feishu SDK here
        # from feishu import FeishuClient
        # self.client = FeishuClient(app_id, app_secret)
        
    def get_tools(self) -> List[AgentTool]:
        """Get all Feishu tools as AgentTool objects"""
        return [
            self._create_send_message_tool(),
            self._create_get_user_info_tool(),
            self._create_search_messages_tool(),
            self._create_create_calendar_event_tool(),
            self._create_get_calendar_freebusy_tool()
        ]
    
    def _create_send_message_tool(self) -> AgentTool:
        """Create tool for sending Feishu messages"""
        def send_feishu_message(
            content: str,
            chat_id: Optional[str] = None,
            open_id: Optional[str] = None,
            msg_type: str = "text"
        ) -> Dict[str, Any]:
            """Send a message to Feishu (Lark)
            
            Args:
                content: Message content
                chat_id: Group chat ID (oc_xxx)
                open_id: User open ID (ou_xxx)
                msg_type: Message type: text, post, image, interactive
            """
            # This is a mock implementation
            # In real implementation, you would call Feishu API
            
            message = FeishuMessage(
                chat_id=chat_id,
                open_id=open_id,
                content=content,
                msg_type=msg_type,
                receive_id_type="chat_id" if chat_id else "open_id"
            )
            
            # Simulate API call
            print(f"[Feishu] Sending message: {content[:50]}...")
            
            return {
                "success": True,
                "message_id": f"mock_msg_{hash(content) % 10000}",
                "content": content,
                "recipient": chat_id or open_id
            }
        
        return AgentTool(
            name="send_feishu_message",
            description="Send a message to Feishu (Lark) chat or user",
            parameters={
                "content": "Message content (required)",
                "chat_id": "Group chat ID (oc_xxx) (optional)",
                "open_id": "User open ID (ou_xxx) (optional)",
                "msg_type": "Message type: text, post, image, interactive (default: text)"
            },
            function=send_feishu_message
        )
    
    def _create_get_user_info_tool(self) -> AgentTool:
        """Create tool for getting Feishu user information"""
        def get_feishu_user_info(
            user_id: str,
            user_id_type: str = "open_id"
        ) -> Dict[str, Any]:
            """Get user information from Feishu
            
            Args:
                user_id: User ID in specified type
                user_id_type: open_id, union_id, or user_id
            """
            # Mock implementation
            print(f"[Feishu] Getting user info for {user_id_type}: {user_id}")
            
            return {
                "success": True,
                "user": {
                    "open_id": f"ou_mock_{hash(user_id) % 10000}",
                    "name": "Mock User",
                    "email": "mock@example.com",
                    "department": "Engineering",
                    "avatar_url": "https://example.com/avatar.png"
                }
            }
        
        return AgentTool(
            name="get_feishu_user_info",
            description="Get user information from Feishu (Lark)",
            parameters={
                "user_id": "User ID (required)",
                "user_id_type": "ID type: open_id, union_id, user_id (default: open_id)"
            },
            function=get_feishu_user_info
        )
    
    def _create_search_messages_tool(self) -> AgentTool:
        """Create tool for searching Feishu messages"""
        def search_feishu_messages(
            query: str,
            chat_id: Optional[str] = None,
            days: int = 7
        ) -> List[Dict[str, Any]]:
            """Search messages in Feishu
            
            Args:
                query: Search keywords
                chat_id: Limit to specific chat (optional)
                days: Search within last N days (default: 7)
            """
            # Mock implementation
            print(f"[Feishu] Searching messages: '{query}' in last {days} days")
            
            return [
                {
                    "message_id": f"msg_{i}",
                    "sender": f"User_{i}",
                    "content": f"Sample message containing '{query}'",
                    "timestamp": f"2024-01-{10+i:02d} 10:00:00",
                    "chat_id": chat_id or f"chat_{hash(query) % 100}"
                }
                for i in range(3)
            ]
        
        return AgentTool(
            name="search_feishu_messages",
            description="Search messages in Feishu (Lark)",
            parameters={
                "query": "Search keywords (required)",
                "chat_id": "Limit to specific chat (optional)",
                "days": "Search within last N days (default: 7)"
            },
            function=search_feishu_messages
        )
    
    def _create_create_calendar_event_tool(self) -> AgentTool:
        """Create tool for creating Feishu calendar events"""
        def create_feishu_calendar_event(
            summary: str,
            start_time: str,
            end_time: str,
            description: Optional[str] = None,
            attendees: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Create a calendar event in Feishu
            
            Args:
                summary: Event title
                start_time: Start time (ISO format: 2024-01-01T10:00:00+08:00)
                end_time: End time (ISO format)
                description: Event description (optional)
                attendees: List of user open IDs (optional)
            """
            # Mock implementation
            print(f"[Feishu] Creating calendar event: {summary}")
            
            return {
                "success": True,
                "event_id": f"event_{hash(summary) % 10000}",
                "summary": summary,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": attendees or [],
                "calendar_url": "https://example.com/calendar/mock"
            }
        
        return AgentTool(
            name="create_feishu_calendar_event",
            description="Create a calendar event in Feishu (Lark)",
            parameters={
                "summary": "Event title (required)",
                "start_time": "Start time (ISO format, e.g., 2024-01-01T10:00:00+08:00)",
                "end_time": "End time (ISO format)",
                "description": "Event description (optional)",
                "attendees": "List of user open IDs (optional)"
            },
            function=create_feishu_calendar_event
        )
    
    def _create_get_calendar_freebusy_tool(self) -> AgentTool:
        """Create tool for checking calendar availability"""
        def get_feishu_calendar_freebusy(
            user_ids: List[str],
            start_time: str,
            end_time: str
        ) -> Dict[str, Any]:
            """Check calendar availability for users
            
            Args:
                user_ids: List of user open IDs
                start_time: Start time (ISO format)
                end_time: End time (ISO format)
            """
            # Mock implementation
            print(f"[Feishu] Checking free/busy for {len(user_ids)} users")
            
            return {
                "success": True,
                "time_min": start_time,
                "time_max": end_time,
                "calendars": {
                    user_id: {
                        "busy": [
                            {
                                "start": f"{start_time[:10]}T09:00:00+08:00",
                                "end": f"{start_time[:10]}T10:30:00+08:00"
                            }
                        ],
                        "free_slots": [
                            {
                                "start": f"{start_time[:10]}T14:00:00+08:00",
                                "end": f"{start_time[:10]}T16:00:00+08:00"
                            }
                        ]
                    }
                    for user_id in user_ids
                }
            }
        
        return AgentTool(
            name="get_feishu_calendar_freebusy",
            description="Check calendar availability for Feishu users",
            parameters={
                "user_ids": "List of user open IDs (required)",
                "start_time": "Start time (ISO format)",
                "end_time": "End time (ISO format)"
            },
            function=get_feishu_calendar_freebusy
        )


# Example usage
if __name__ == "__main__":
    # Initialize toolkit
    toolkit = FeishuToolkit(app_id="mock_app_id", app_secret="mock_app_secret")
    
    # Get all tools
    tools = toolkit.get_tools()
    
    print(f"📱 Created {len(tools)} Feishu tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")