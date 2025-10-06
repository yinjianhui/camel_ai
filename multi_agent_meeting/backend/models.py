#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型模块
定义系统中使用的数据结构
"""

import os
import sys
from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict, List
from datetime import datetime

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
class Agent:
    """智能体数据结构"""
    id: int
    role: str
    description: str
    api_key: str
    agent: Optional[Any] = None  # CAMEL ChatAgent实例
    model: Optional[Any] = None  # 模型实例
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def __str__(self) -> str:
        return f"Agent(id={self.id}, role='{self.role}', description='{self.description[:50]}...')"


@dataclass
class Message:
    """消息数据结构"""
    agent_id: int
    role: str
    content: str
    timestamp: float
    round_number: int
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def get_formatted_time(self) -> str:
        """获取格式化的时间"""
        return datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S')
    
    def __str__(self) -> str:
        return f"Message(agent_id={self.agent_id}, role='{self.role}', round={self.round_number})"


@dataclass
class MeetingConfig:
    """会议配置数据结构"""
    topic: str
    background: str
    agents: List[Dict[str, str]]
    # max_rounds 将从config中设置，不在此处定义
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        if not self.topic.strip():
            errors.append("会议主题不能为空")
        
        if not self.background.strip():
            errors.append("会议背景不能为空")
        
        # 智能体数量验证将在config中统一管理
        if len(self.agents) == 0:
            errors.append("必须配置至少1个智能体")
        
        for i, agent in enumerate(self.agents):
            if not agent.get('role', '').strip():
                errors.append(f"智能体{i+1}的角色不能为空")
            if not agent.get('description', '').strip():
                errors.append(f"智能体{i+1}的描述不能为空")
        
        return errors


@dataclass
class MeetingState:
    """会议状态数据结构"""
    is_active: bool = False
    current_round: int = 0
    # max_rounds 将从config中设置，不在此处定义
    topic: str = ""
    background: str = ""
    agents: List[Dict] = None
    messages: List[Dict] = None
    current_speaker_id: int = 0
    meeting_id: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    is_ending: bool = False  # 会议是否正在结束
    speaker_counts: Dict[int, int] = None  # 每个智能体的发言次数统计
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if self.messages is None:
            self.messages = []
        if self.speaker_counts is None:
            self.speaker_counts = {}
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def get_duration(self) -> Optional[float]:
        """获取会议持续时间（秒）"""
        if self.start_time is None:
            return None
        
        end_time = self.end_time or datetime.now().timestamp()
        return end_time - self.start_time
    
    def is_ended(self) -> bool:
        """检查会议是否已结束"""
        # max_rounds 将在使用时从config中获取
        return not self.is_active or self.is_ending


@dataclass
class SpeakerDecision:
    """发言人决策结果"""
    agent_id: int
    agent_role: str
    decision_reason: str
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def __str__(self) -> str:
        return f"SpeakerDecision(agent_id={self.agent_id}, role='{self.agent_role}', reason='{self.decision_reason}')"


@dataclass
class MeetingSummary:
    """会议总结数据结构"""
    topic: str
    background: str
    total_rounds: int
    total_messages: int
    duration: float
    summary_content: str
    key_points: List[str] = None
    action_items: List[str] = None
    participants: List[str] = None
    
    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []
        if self.action_items is None:
            self.action_items = []
        if self.participants is None:
            self.participants = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def get_formatted_duration(self) -> str:
        """获取格式化的持续时间"""
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟{seconds}秒"
        elif minutes > 0:
            return f"{minutes}分钟{seconds}秒"
        else:
            return f"{seconds}秒"
