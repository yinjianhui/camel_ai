#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
管理系统的各种配置参数
"""

import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass

# 设置控制台编码为UTF-8
if sys.platform == "win32":
    try:
        import codecs
        # 检查是否支持detach方法
        if hasattr(sys.stdout, 'detach'):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
        # 设置控制台代码页为UTF-8
        os.system("chcp 65001 > nul")
    except Exception:
        # 如果设置失败，忽略错误继续运行
        pass


@dataclass
class APIConfig:
    """API配置"""
    base_url: str = "https://api.deepseek.com/v1"
    model_type: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30


@dataclass
class MeetingConfig:
    """会议配置"""
    max_rounds: int = 13
    default_timer_seconds: int = 5
    max_conversation_history: int = 20
    auto_save_interval: int = 300  # 5分钟
    agent_count: int = 4  # 智能体数量
    ceo_agent_id: int = 0  # CEO智能体ID


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class WebSocketConfig:
    """WebSocket配置"""
    cors_allowed_origins: str = "*"
    async_mode: str = "threading"
    ping_timeout: int = 60
    ping_interval: int = 25
    # 新增WebSocket优化配置
    engineio_logger: bool = False  # 禁用Engine.IO日志以减少干扰
    manage_session: bool = True  # 启用会话管理
    http_compression: bool = True  # 启用HTTP压缩
    compression_threshold: int = 1024  # 压缩阈值
    cookie: str = None  # 禁用cookie以简化跨域
    cors_credentials: bool = False  # 禁用CORS凭据以简化跨域


class Config:
    """主配置类"""
    
    def __init__(self):
        # API密钥配置
        self.api_keys: List[str] = [
            "sk-be71c40c6090410dbd554490cf7629d5",
            "sk-f06a9bfd2bc1423991dd6d5094e1a2cd", 
            "sk-54022c1f872a4af1bc52fc9071b2a18d",
            "sk-d8dd47f48a8f433ca437ccf425f0c125"
        ]
        
        # Flask配置
        self.flask_secret_key: str = os.getenv('FLASK_SECRET_KEY', 'multi_agent_meeting_secret_key')
        self.flask_host: str = os.getenv('FLASK_HOST', '0.0.0.0')
        self.flask_port: int = int(os.getenv('FLASK_PORT', '5000'))
        self.flask_debug: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        
        # API配置
        self.api = APIConfig(
            base_url=os.getenv('API_BASE_URL', 'https://api.deepseek.com/v1'),
            model_type=os.getenv('API_MODEL_TYPE', 'deepseek-chat'),
            temperature=float(os.getenv('API_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('API_MAX_TOKENS', '4096')),
            timeout=int(os.getenv('API_TIMEOUT', '30'))
        )
        
        # 会议配置
        self.meeting = MeetingConfig(
            max_rounds=int(os.getenv('MEETING_MAX_ROUNDS', '13')),
            default_timer_seconds=int(os.getenv('MEETING_TIMER_SECONDS', '5')),
            max_conversation_history=int(os.getenv('MEETING_MAX_HISTORY', '20')),
            auto_save_interval=int(os.getenv('MEETING_AUTO_SAVE_INTERVAL', '300')),
            agent_count=int(os.getenv('MEETING_AGENT_COUNT', '4')),
            ceo_agent_id=int(os.getenv('MEETING_CEO_AGENT_ID', '0'))
        )
        
        # 日志配置
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
            enable_console=os.getenv('LOG_ENABLE_CONSOLE', 'True').lower() == 'true',
            enable_file=os.getenv('LOG_ENABLE_FILE', 'True').lower() == 'true'
        )
        
        # WebSocket配置
        self.websocket = WebSocketConfig(
            cors_allowed_origins=os.getenv('WEBSOCKET_CORS_ORIGINS', '*'),
            async_mode=os.getenv('WEBSOCKET_ASYNC_MODE', 'threading'),
            ping_timeout=int(os.getenv('WEBSOCKET_PING_TIMEOUT', '60')),
            ping_interval=int(os.getenv('WEBSOCKET_PING_INTERVAL', '25'))
        )
        
        # 文件路径配置
        self.logs_dir: str = os.path.join(os.path.dirname(__file__), 'logs')
        self.temp_dir: str = os.path.join(os.path.dirname(__file__), 'temp')
        self.meetings_save_dir: str = os.path.join(os.path.dirname(__file__), 'saved_meetings')
        
        # 确保目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.meetings_save_dir, exist_ok=True)
    
    def get_api_key(self, index: int) -> str:
        """获取指定索引的API密钥"""
        if 0 <= index < len(self.api_keys):
            return self.api_keys[index]
        return self.api_keys[0]  # 默认返回第一个
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证API密钥
        if not self.api_keys or len(self.api_keys) < 4:
            errors.append("API密钥配置不完整，需要至少4个密钥")
        
        # 验证Flask配置
        if not self.flask_secret_key:
            errors.append("Flask密钥不能为空")
        
        if not (1 <= self.flask_port <= 65535):
            errors.append("Flask端口必须在1-65535之间")
        
        # 验证API配置
        if not self.api.base_url:
            errors.append("API基础URL不能为空")
        
        if not (0.0 <= self.api.temperature <= 2.0):
            errors.append("API温度参数必须在0.0-2.0之间")
        
        if self.api.max_tokens <= 0:
            errors.append("API最大令牌数必须大于0")
        
        # 验证会议配置
        if self.meeting.max_rounds <= 0:
            errors.append("会议最大轮次必须大于0")
        
        if self.meeting.default_timer_seconds <= 0:
            errors.append("默认计时器秒数必须大于0")
        
        if self.meeting.agent_count <= 0:
            errors.append("智能体数量必须大于0")
        
        if self.meeting.ceo_agent_id < 0:
            errors.append("CEO智能体ID不能为负数")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        return {
            'flask': {
                'host': self.flask_host,
                'port': self.flask_port,
                'debug': self.flask_debug
            },
            'api': {
                'base_url': self.api.base_url,
                'model_type': self.api.model_type,
                'temperature': self.api.temperature,
                'max_tokens': self.api.max_tokens,
                'timeout': self.api.timeout
            },
            'meeting': {
                'max_rounds': self.meeting.max_rounds,
                'default_timer_seconds': self.meeting.default_timer_seconds,
                'max_conversation_history': self.meeting.max_conversation_history,
                'auto_save_interval': self.meeting.auto_save_interval,
                'agent_count': self.meeting.agent_count,
                'ceo_agent_id': self.meeting.ceo_agent_id
            },
            'logging': {
                'level': self.logging.level,
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count,
                'enable_console': self.logging.enable_console,
                'enable_file': self.logging.enable_file
            },
            'websocket': {
                'cors_allowed_origins': self.websocket.cors_allowed_origins,
                'async_mode': self.websocket.async_mode,
                'ping_timeout': self.websocket.ping_timeout,
                'ping_interval': self.websocket.ping_interval
            },
            'paths': {
                'logs_dir': self.logs_dir,
                'temp_dir': self.temp_dir,
                'meetings_save_dir': self.meetings_save_dir
            }
        }


# 全局配置实例
config = Config()

# 为了向后兼容，保留原有的API_KEYS
API_KEYS = config.api_keys
