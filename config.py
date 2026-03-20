"""OpenAgentFlow 配置文件"""

import os
from typing import Optional

class Config:
    """应用配置"""
    
    # 应用信息
    APP_NAME = "OpenAgentFlow"
    APP_VERSION = "0.1.0"
    APP_DESCRIPTION = "Composable AI Agent Workflow Platform"
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./openagentflow.db")
    
    # AI模型配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
    
    # 飞书配置
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
    
    # 钉钉配置
    DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY", "")
    DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET", "")
    
    # 企业微信配置
    WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")
    WECOM_CORP_SECRET = os.getenv("WECOM_CORP_SECRET", "")
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required for AI functionality")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_summary(cls):
        """打印配置摘要"""
        print(f"\n{'='*50}")
        print(f"{cls.APP_NAME} v{cls.APP_VERSION}")
        print(f"{'='*50}")
        print(f"Server: {cls.HOST}:{cls.PORT}")
        print(f"Debug: {cls.DEBUG}")
        print(f"Database: {cls.DATABASE_URL}")
        print(f"Default Model: {cls.DEFAULT_MODEL}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"{'='*50}\n")


# 全局配置实例
config = Config()