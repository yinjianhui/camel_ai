#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议管理服务模块
处理会议的生命周期管理
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from utils import (
    setup_console_encoding, post_process_ceo_content, 
    check_ceo_wants_to_end_meeting, remove_next_speaker_references,
    clean_unprofessional_content, format_duration
)

from camel.messages import BaseMessage

from models import (
    MeetingConfig, MeetingState, Message, MeetingSummary, 
    Agent, SpeakerDecision
)
from services.agent_service import AgentService
from config import config
from logging_config import get_logger
from prompts import PromptConfig

# 设置控制台编码
setup_console_encoding()

logger = get_logger(__name__)


class MeetingService:
    """会议管理服务类"""
    
    def __init__(self):
        self.agent_service = AgentService()
        self.state = MeetingState()
        self.logger = logger
    
    def initialize_meeting(self, meeting_config: MeetingConfig) -> bool:
        """
        初始化会议
        
        Args:
            meeting_config: 会议配置
        
        Returns:
            是否初始化成功
        """
        self.logger.info(f"开始初始化会议: topic='{meeting_config.topic}'")
        
        try:
            # 验证配置
            errors = meeting_config.validate()
            if errors:
                self.logger.error(f"会议配置验证失败: {errors}")
                return False
            
            # 重置状态
            self._reset_state()
            
            # 设置会议基本信息
            self.state.topic = meeting_config.topic
            self.state.background = meeting_config.background
            self.state.start_time = time.time()
            self.state.meeting_id = f"meeting_{int(time.time())}"
            
            # 创建智能体
            self._create_agents(meeting_config.agents)
            
            # 激活会议
            self.state.is_active = True
            
            self.logger.info(f"会议初始化成功: meeting_id={self.state.meeting_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"会议初始化失败: error={e}")
            return False
    
    def _reset_state(self) -> None:
        """重置会议状态"""
        self.logger.debug("重置会议状态")
        self.state = MeetingState()
        self.agent_service.clear_agents()
    
    def _create_agents(self, agents_config: List[Dict[str, str]]) -> None:
        """创建智能体"""
        self.logger.debug(f"创建智能体: count={len(agents_config)}")
        
        for i, agent_config in enumerate(agents_config):
            try:
                agent = self.agent_service.create_agent(
                    agent_id=i,
                    role=agent_config['role'],
                    description=agent_config['description'],
                    api_key=config.get_api_key(i)
                )
                self.agent_service.add_agent(agent)
                self.logger.debug(f"智能体创建成功: {agent}")
                
            except Exception as e:
                self.logger.error(f"创建智能体失败: index={i}, config={agent_config}, error={e}")
                raise
    
    def ceo_speak(self) -> Dict[str, Any]:
        """
        CEO发言（轮次总结和下一轮安排）
        
        Returns:
            发言结果
        """
        self.logger.info("CEO开始发言（轮次总结）")
        
        try:
            # 检查会议状态
            if not self._is_meeting_active():
                return {"status": "error", "error": "会议已结束"}
            
            # 检查会议是否正在结束
            if self.state.is_ending:
                self.logger.info("会议正在结束，停止CEO发言")
                return {"status": "error", "error": "会议正在结束"}
            
            # 检查是否达到或超过最大轮次限制
            if self.state.current_round >= config.meeting.max_rounds:
                self.logger.info(f"已达到最大轮次限制({config.meeting.max_rounds})，强制结束会议")
                return self._force_end_meeting_at_max_rounds()
            
            # 获取CEO智能体
            ceo_agent = self.agent_service.get_agent_by_id(config.meeting.ceo_agent_id)
            if not ceo_agent or not ceo_agent.agent:
                return {"status": "error", "error": "CEO智能体初始化失败"}
            
            # 构建输入内容（轮次总结）
            input_content = self._build_ceo_round_summary_input()
            
            # 创建用户消息
            user_message = BaseMessage.make_user_message(
                role_name="用户",
                content=input_content
            )
            
            # 生成回复
            ceo_content = self.agent_service.generate_response(ceo_agent, user_message)
            
            # 后处理内容
            ceo_content = post_process_ceo_content(ceo_content, len(self.state.messages) > 0, False)
            
            # 检查CEO是否想要结束会议
            meeting_should_end = check_ceo_wants_to_end_meeting(ceo_content)
            
            # 创建消息记录
            message = self._create_message(config.meeting.ceo_agent_id, ceo_agent.role, ceo_content)
            self._add_message(message)
            
            if meeting_should_end:
                # CEO想要结束会议，设置会议结束标志
                self.state.is_ending = True
                self.logger.info("CEO决定结束会议")
                next_speaker_id = config.meeting.ceo_agent_id  # 不再有下一个发言者
            else:
                # 决定下一个发言者（按顺序）
                next_speaker_id = self._get_next_speaker_by_order()
            
            self.logger.info(f"CEO发言完成: message_id={message.agent_id}, next_speaker_id={next_speaker_id}, meeting_should_end={meeting_should_end}")
            
            return {
                "status": "success",
                "message": message.to_dict(),
                "current_round": self.state.current_round,
                "next_speaker_id": next_speaker_id,
                "meeting_should_end": meeting_should_end,
                "meeting_ended": self.state.is_ended()
            }
            
        except Exception as e:
            self.logger.error(f"CEO发言失败: error={e}")
            return {"status": "error", "error": str(e)}
    
    def agent_speak(self, agent_id: int) -> Dict[str, Any]:
        """
        智能体发言
        
        Args:
            agent_id: 智能体ID
        
        Returns:
            发言结果
        """
        self.logger.info(f"智能体开始发言: agent_id={agent_id}")
        
        try:
            # 检查会议状态
            if not self._is_meeting_active():
                return {"status": "error", "error": "会议已结束"}
            
            # 检查会议是否正在结束
            if self.state.is_ending:
                self.logger.info("会议正在结束，停止智能体发言")
                return {"status": "error", "error": "会议正在结束"}
            
            # 检查是否接近最大轮次限制，如果是则阻止智能体发言，让CEO做最终总结
            if self.state.current_round >= config.meeting.max_rounds - 1:
                self.logger.info(f"接近最大轮次限制({config.meeting.max_rounds})，阻止智能体发言，等待CEO最终总结")
                return {
                    "status": "error", 
                    "error": "已达到最大轮次限制，等待CEO最终总结",
                    "should_ceo_speak": True,
                    "reason": "达到最大轮次限制"
                }
            
            # 验证智能体ID
            if agent_id >= len(self.agent_service.list_agents()) or agent_id == config.meeting.ceo_agent_id:
                return {"status": "error", "error": "无效的智能体ID"}
            
            # 获取智能体
            agent = self.agent_service.get_agent_by_id(agent_id)
            if not agent or not agent.agent:
                return {"status": "error", "error": f"智能体 {agent.role} 初始化失败"}
            
            # 构建输入内容
            input_content = self._build_agent_input(agent)
            
            # 创建用户消息
            user_message = BaseMessage.make_user_message(
                role_name="用户",
                content=input_content
            )
            
            # 生成回复
            agent_content = self.agent_service.generate_response(agent, user_message)
            
            # 创建消息记录
            message = self._create_message(agent_id, agent.role, agent_content)
            self._add_message(message)
            
            # 检查轮次是否完成
            round_complete = self._is_round_complete()
            
            if round_complete:
                # 轮次完成，下一个发言者是CEO
                next_speaker_id = config.meeting.ceo_agent_id
                self.logger.info(f"轮次完成，下一个发言者：CEO")
            else:
                # 轮次未完成，按顺序决定下一个智能体
                next_speaker_id = self._get_next_speaker_by_order()
                self.logger.info(f"轮次未完成，下一个发言者：智能体{next_speaker_id}")
            
            self.logger.info(f"智能体发言完成: agent_id={agent_id}, role='{agent.role}', round_complete={round_complete}, next_speaker_id={next_speaker_id}")
            
            return {
                "status": "success",
                "message": message.to_dict(),
                "current_round": self.state.current_round,
                "next_speaker_id": next_speaker_id,
                "round_complete": round_complete,
                "meeting_ended": self.state.is_ended()
            }
            
        except Exception as e:
            self.logger.error(f"智能体发言失败: agent_id={agent_id}, error={e}")
            return {"status": "error", "error": str(e)}
    
    def _is_meeting_active(self) -> bool:
        """检查会议是否活跃"""
        return self.state.is_active and not self.state.is_ended()
    
    def _build_ceo_round_summary_input(self) -> str:
        """构建CEO轮次总结输入内容"""
        conversation_history = self._get_conversation_history()
        speaker_stats = self._get_speaker_statistics()
        
        if len(self.state.messages) == 0:
            # 会议刚开始
            return PromptConfig.get_ceo_meeting_start_input(self.state.topic, self.state.background)
        else:
            # 轮次总结
            return PromptConfig.get_ceo_round_summary_input(
                self.state.topic, self.state.background, conversation_history, speaker_stats
            )
    
    def _build_force_end_meeting_input(self) -> str:
        """构建强制结束会议的输入内容"""
        conversation_history = self._get_conversation_history()
        speaker_stats = self._get_speaker_statistics()
        
        return PromptConfig.get_ceo_force_end_input(
            self.state.topic, self.state.background, conversation_history, 
            speaker_stats, self.state.current_round, config.meeting.max_rounds
        )
    
    def _build_agent_input(self, agent: Agent) -> str:
        """构建智能体输入内容"""
        conversation_history = self._get_conversation_history()
        
        return PromptConfig.get_agent_input(
            self.state.topic, self.state.background, conversation_history,
            agent.role, agent.description
        )
    
    def _get_conversation_history(self) -> str:
        """获取对话历史"""
        if not self.state.messages:
            return "这是会议的开始。"
        
        history = "会议对话历史：\n"
        for msg_dict in self.state.messages[-config.meeting.max_conversation_history:]:
            history += f"{msg_dict['role']}: {msg_dict['content']}\n"
        return history
    
    def _get_speaker_statistics(self) -> str:
        """获取发言统计信息"""
        if not self.state.speaker_counts:
            return "暂无发言统计"
        
        stats = "各智能体发言次数：\n"
        agents = self.agent_service.list_agents()
        
        for agent in agents:
            count = self.state.speaker_counts.get(agent.id, 0)
            stats += f"- {agent.role}: {count}次\n"
        
        return stats
    
    def _get_next_speaker_by_order(self) -> int:
        """按顺序决定下一个发言者"""
        agents = self.agent_service.list_agents()
        if not agents:
            return 1  # 默认返回第一个非CEO智能体
        
        non_ceo_agents = [agent for agent in agents if agent.id != config.meeting.ceo_agent_id]
        if not non_ceo_agents:
            return 1
        
        # 获取当前轮次中已发言的非CEO智能体
        current_round_messages = [msg for msg in self.state.messages if msg.get('round_number', 0) == self.state.current_round]
        current_round_non_ceo_speakers = [msg.get('agent_id', -1) for msg in current_round_messages if msg.get('agent_id', -1) != config.meeting.ceo_agent_id]
        
        # 如果当前轮次还没有非CEO智能体发言，返回第一个
        if not current_round_non_ceo_speakers:
            return 1
        
        # 找到最后一个发言的非CEO智能体
        last_speaker_id = current_round_non_ceo_speakers[-1]
        
        # 找到下一个智能体
        for i, agent in enumerate(non_ceo_agents):
            if agent.id == last_speaker_id:
                # 返回下一个智能体，如果到了最后一个就返回第一个
                next_index = (i + 1) % len(non_ceo_agents)
                return non_ceo_agents[next_index].id
        
        return 1  # 默认返回第一个
    
    def _is_round_complete(self) -> bool:
        """检查当前轮次是否完成（所有非CEO智能体都已发言）"""
        agents = self.agent_service.list_agents()
        non_ceo_agents = [agent for agent in agents if agent.id != config.meeting.ceo_agent_id]
        if not non_ceo_agents:
            return True
        
        # 获取最近的消息，检查是否所有非CEO智能体都已发言
        # 从最新的消息开始，找到CEO发言的位置，然后检查CEO发言后所有非CEO智能体是否都已发言
        recent_messages = self.state.messages[-10:] if len(self.state.messages) > 10 else self.state.messages
        
        # 找到最近的CEO发言位置
        last_ceo_index = -1
        for i, msg in enumerate(reversed(recent_messages)):
            if msg.get('agent_id', -1) == config.meeting.ceo_agent_id:  # CEO发言
                last_ceo_index = len(recent_messages) - 1 - i
                break
        
        if last_ceo_index == -1:
            # 如果没有找到CEO发言，检查所有消息
            messages_to_check = recent_messages
        else:
            # 从CEO发言后的消息开始检查
            messages_to_check = recent_messages[last_ceo_index + 1:]
        
        # 获取这些消息中的非CEO智能体
        non_ceo_speakers = set(msg.get('agent_id', -1) for msg in messages_to_check if msg.get('agent_id', -1) != config.meeting.ceo_agent_id)
        
        # 检查是否所有非CEO智能体都已发言
        for agent in non_ceo_agents:
            if agent.id not in non_ceo_speakers:
                return False
        
        return True
    
    def _force_end_meeting_at_max_rounds(self) -> Dict[str, Any]:
        """在达到最大轮次限制时强制结束会议"""
        self.logger.info("强制结束会议：已达到最大轮次限制")
        
        try:
            # 获取CEO智能体
            ceo_agent = self.agent_service.get_agent_by_id(config.meeting.ceo_agent_id)
            if not ceo_agent or not ceo_agent.agent:
                return {"status": "error", "error": "CEO智能体初始化失败"}
            
            # 构建强制结束会议的输入内容
            input_content = self._build_force_end_meeting_input()
            
            # 创建用户消息
            user_message = BaseMessage.make_user_message(
                role_name="用户",
                content=input_content
            )
            
            # 生成CEO的最终总结发言
            ceo_content = self.agent_service.generate_response(ceo_agent, user_message)
            
            # 后处理内容
            ceo_content = post_process_ceo_content(ceo_content, True, True)
            
            # 创建消息记录
            message = self._create_message(config.meeting.ceo_agent_id, ceo_agent.role, ceo_content)
            self._add_message(message)
            
            # 强制设置会议结束标志
            self.state.is_ending = True
            
            self.logger.info(f"强制结束会议完成: message_id={message.agent_id}, current_round={self.state.current_round}")
            
            return {
                "status": "success",
                "message": message.to_dict(),
                "current_round": self.state.current_round,
                "next_speaker_id": config.meeting.ceo_agent_id,  # 不再有下一个发言者
                "meeting_should_end": True,
                "meeting_ended": True,
                "forced_end": True,
                "reason": "已达到最大轮次限制"
            }
            
        except Exception as e:
            self.logger.error(f"强制结束会议失败: error={e}")
            return {"status": "error", "error": str(e)}
    
    
    def _create_message(self, agent_id: int, role: str, content: str) -> Message:
        """创建消息记录"""
        return Message(
            agent_id=agent_id,
            role=role,
            content=content,
            timestamp=time.time(),
            round_number=self.state.current_round + 1
        )
    
    def _add_message(self, message: Message) -> None:
        """添加消息到状态"""
        self.state.messages.append(message.to_dict())
        self.state.current_round += 1
        
        # 更新发言统计
        if message.agent_id not in self.state.speaker_counts:
            self.state.speaker_counts[message.agent_id] = 0
        self.state.speaker_counts[message.agent_id] += 1
        
        self.logger.debug(f"添加消息: {message}, 发言统计: {self.state.speaker_counts}")
    
    def end_meeting(self) -> Dict[str, Any]:
        """结束会议并生成总结"""
        self.logger.info("开始结束会议")
        
        try:
            if not self.state.is_active:
                return {"status": "error", "error": "会议未开始"}
            
            # 立即设置会议结束标志，停止智能体发言
            self.state.is_ending = True
            self.logger.info("会议结束标志已设置，智能体发言已停止")
            
            # 设置结束时间
            self.state.end_time = time.time()
            
            # 生成会议总结
            summary = self._generate_meeting_summary()
            
            # 停用会议
            self.state.is_active = False
            
            self.logger.info(f"会议结束: meeting_id={self.state.meeting_id}, duration={summary.get_formatted_duration()}")
            
            return {
                "status": "success",
                "summary": summary.to_dict(),
                "total_messages": len(self.state.messages),
                "total_rounds": self.state.current_round
            }
            
        except Exception as e:
            self.logger.error(f"结束会议失败: error={e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_meeting_summary(self) -> MeetingSummary:
        """生成会议总结"""
        self.logger.debug("生成会议总结")
        
        try:
            # 使用CEO智能体生成总结
            ceo_agent = self.agent_service.get_agent_by_id(config.meeting.ceo_agent_id)
            conversation_summary = self._get_conversation_history()
            
            if ceo_agent and ceo_agent.agent:
                summary_request = BaseMessage.make_user_message(
                    role_name="用户",
                    content=PromptConfig.get_meeting_summary_input(
                        self.state.topic, self.state.background, self.state.current_round,
                        len(self.state.messages), conversation_summary
                    )
                )
                
                summary_content = self.agent_service.generate_response(ceo_agent, summary_request)
            else:
                # 使用默认总结
                summary_content = self._generate_default_summary(conversation_summary)
            
            # 创建总结对象
            summary = MeetingSummary(
                topic=self.state.topic,
                background=self.state.background,
                total_rounds=self.state.current_round,
                total_messages=len(self.state.messages),
                duration=self.state.get_duration() or 0,
                summary_content=summary_content,
                participants=[agent.role for agent in self.agent_service.list_agents()]
            )
            
            self.logger.debug("会议总结生成完成")
            return summary
            
        except Exception as e:
            self.logger.error(f"生成会议总结失败: error={e}")
            # 返回默认总结
            return self._generate_default_summary("")
    
    def _generate_default_summary(self, conversation_summary: str) -> str:
        """生成默认总结"""
        return f"""会议总结报告

会议主题：{self.state.topic}
会议背景：{self.state.background}
会议轮次：{self.state.current_round}
总发言数：{len(self.state.messages)}

会议讨论内容：
{conversation_summary}

主要成果：
1. 各智能体从不同专业角度对主题进行了深入讨论
2. 形成了多角度的观点和建议
3. 为后续决策提供了重要参考

后续行动计划：
1. 整理会议记录中的关键观点
2. 制定具体的实施方案
3. 安排后续跟进会议

会议结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def get_transcript(self) -> str:
        """获取会议记录"""
        self.logger.debug("生成会议记录")
        
        transcript = f"""多智能体会议记录
会议主题：{self.state.topic}
会议背景：{self.state.background}
会议时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总轮次：{self.state.current_round}
总发言数：{len(self.state.messages)}

=== 会议内容 ===

"""
        
        for msg_dict in self.state.messages:
            timestamp = datetime.fromtimestamp(msg_dict['timestamp']).strftime('%H:%M:%S')
            transcript += f"[{timestamp}] {msg_dict['role']}: {msg_dict['content']}\n\n"
        
        return transcript
    
    def get_meeting_state(self) -> MeetingState:
        """获取会议状态"""
        return self.state
    
    def is_meeting_active(self) -> bool:
        """检查会议是否活跃"""
        return self.state.is_active and not self.state.is_ended()
    
    def restart_meeting(self) -> Dict[str, Any]:
        """重启会议（清空当前会议状态）"""
        self.logger.info("开始重启会议")
        
        try:
            # 立即设置会议结束标志，停止所有智能体发言
            self.state.is_ending = True
            self.logger.info("会议重启标志已设置，停止所有发言")
            
            # 重置会议状态
            self._reset_state()
            
            self.logger.info("会议重启成功，状态已清空")
            
            return {
                "status": "success",
                "message": "会议已重启，可以重新配置和开始新会议"
            }
            
        except Exception as e:
            self.logger.error(f"重启会议失败: error={e}")
            return {"status": "error", "error": str(e)}
    
    def get_meeting_status(self) -> Dict[str, Any]:
        """获取会议状态（用于健康检查）"""
        return {
            "is_active": self.state.is_active,
            "current_round": self.state.current_round,
            "max_rounds": config.meeting.max_rounds,
            "topic": self.state.topic,
            "background": self.state.background,
            "agents_count": len(self.state.agents) if self.state.agents else 0,
            "messages_count": len(self.state.messages),
            "current_speaker_id": self.state.current_speaker_id,
            "meeting_id": self.state.meeting_id
        }