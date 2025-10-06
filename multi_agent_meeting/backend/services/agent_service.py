#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体服务模块
处理智能体的创建、管理和交互
"""

import time
from typing import Dict, List, Optional, Any

from utils import setup_console_encoding
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelPlatformType
from camel.models import ModelFactory

from models import Agent, Message, SpeakerDecision
from config import config
from logging_config import get_logger
from prompts import PromptConfig

# 设置控制台编码
setup_console_encoding()

logger = get_logger(__name__)


class AgentService:
    """智能体服务类"""
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.logger = logger
    
    def create_agent(self, agent_id: int, role: str, description: str, api_key: str) -> Agent:
        """
        创建智能体
        
        Args:
            agent_id: 智能体ID
            role: 角色名称
            description: 角色描述
            api_key: API密钥
        
        Returns:
            创建的智能体实例
        """
        self.logger.info(f"开始创建智能体: ID={agent_id}, role='{role}'")
        
        try:
            agent = Agent(
                id=agent_id,
                role=role,
                description=description,
                api_key=api_key
            )
            
            # 初始化模型
            self._initialize_model(agent)
            
            # 创建CAMEL智能体
            self._create_camel_agent(agent)
            
            self.logger.info(f"智能体创建成功: {agent}")
            return agent
            
        except Exception as e:
            self.logger.error(f"创建智能体失败: ID={agent_id}, role='{role}', error={e}")
            raise
    
    def _initialize_model(self, agent: Agent) -> None:
        """初始化模型"""
        self.logger.debug(f"初始化模型: agent_id={agent.id}, role='{agent.role}'")
        
        try:
            model = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI_COMPATIBILITY_MODEL,
                model_type=config.api.model_type,
                url=config.api.base_url,
                api_key=agent.api_key,
                model_config_dict={
                    "temperature": config.api.temperature,
                    "max_tokens": config.api.max_tokens
                }
            )
            agent.model = model
            self.logger.debug(f"模型初始化成功: agent_id={agent.id}")
            
        except Exception as e:
            self.logger.error(f"模型初始化失败: agent_id={agent.id}, error={e}")
            raise
    
    def _create_camel_agent(self, agent: Agent) -> None:
        """创建CAMEL智能体"""
        self.logger.debug(f"创建CAMEL智能体: agent_id={agent.id}, role='{agent.role}'")
        
        try:
            # 创建系统提示
            system_message = self._create_system_message(agent)
            
            # 创建CAMEL智能体
            agent.agent = ChatAgent(
                system_message=system_message,
                model=agent.model
            )
            
            self.logger.debug(f"CAMEL智能体创建成功: agent_id={agent.id}")
            
        except Exception as e:
            self.logger.error(f"CAMEL智能体创建失败: agent_id={agent.id}, error={e}")
            raise
    
    def _create_system_message(self, agent: Agent) -> BaseMessage:
        """创建系统消息"""
        if agent.id == config.meeting.ceo_agent_id:  # CEO智能体
            content = PromptConfig.get_ceo_system_prompt(agent.role, agent.description)
        else:  # 其他智能体
            content = PromptConfig.get_agent_system_prompt(agent.role, agent.description)
        
        return BaseMessage.make_assistant_message(
            role_name=agent.role,
            content=content
        )
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """根据ID获取智能体"""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_agent_by_role(self, role: str) -> Optional[Agent]:
        """根据角色名称获取智能体"""
        for agent in self.agents:
            if agent.role == role:
                return agent
        return None
    
    def list_agents(self) -> List[Agent]:
        """获取所有智能体列表"""
        return self.agents.copy()
    
    def clear_agents(self) -> None:
        """清空所有智能体"""
        self.logger.info("清空所有智能体")
        self.agents.clear()
    
    def add_agent(self, agent: Agent) -> None:
        """添加智能体到列表"""
        self.agents.append(agent)
        self.logger.info(f"添加智能体到列表: {agent}")
    
    def remove_agent(self, agent_id: int) -> bool:
        """移除智能体"""
        for i, agent in enumerate(self.agents):
            if agent.id == agent_id:
                removed_agent = self.agents.pop(i)
                self.logger.info(f"移除智能体: {removed_agent}")
                return True
        return False
    
    def generate_response(self, agent: Agent, user_message: BaseMessage) -> str:
        """
        生成智能体回复
        
        Args:
            agent: 智能体实例
            user_message: 用户消息
        
        Returns:
            智能体回复内容
        """
        self.logger.debug(f"生成智能体回复: agent_id={agent.id}, role='{agent.role}'")
        
        try:
            if not agent.agent:
                raise ValueError(f"智能体 {agent.role} 未正确初始化")
            
            start_time = time.time()
            response = agent.agent.step(user_message)
            end_time = time.time()
            
            content = response.msgs[0].content
            duration = end_time - start_time
            
            self.logger.info(f"智能体回复生成成功: agent_id={agent.id}, duration={duration:.2f}s, content_length={len(content)}")
            self.logger.debug(f"智能体回复内容: agent_id={agent.id}, content='{content[:100]}...'")
            
            return content
            
        except Exception as e:
            self.logger.error(f"生成智能体回复失败: agent_id={agent.id}, error={e}")
            raise
    
    def decide_next_speaker(self, ceo_content: str, agents: List[Agent], speaker_counts: Dict[int, int] = None) -> SpeakerDecision:
        """
        决定下一个发言人
        
        Args:
            ceo_content: CEO发言内容
            agents: 智能体列表
            speaker_counts: 发言次数统计
        
        Returns:
            发言人决策结果
        """
        self.logger.debug(f"决定下一个发言人: content_length={len(ceo_content)}, speaker_counts={speaker_counts}")
        
        try:
            ceo_content_lower = ceo_content.lower()
            
            # 首先尝试从CEO发言中提取具体的角色名称
            for agent in agents:
                if agent.id == config.meeting.ceo_agent_id:
                    continue  # 排除CEO
                agent_role_lower = agent.role.lower()
                
                # 检查CEO发言中是否包含该角色的完整名称或关键词
                if (agent_role_lower in ceo_content_lower or 
                    any(word in ceo_content_lower for word in agent_role_lower.split()) or
                    any(word in agent_role_lower for word in ceo_content_lower.split() if len(word) > 2)):
                    
                    decision = SpeakerDecision(
                        agent_id=agent.id,
                        agent_role=agent.role,
                        decision_reason=f"CEO明确指定了角色: {agent.role}",
                        confidence=0.9
                    )
                    
                    self.logger.info(f"CEO指定发言人: {decision}")
                    return decision
            
            # 如果没有明确指定，使用关键词匹配策略
            # decision = self._keyword_based_decision(ceo_content_lower, agents, speaker_counts)
            if decision:
                self.logger.info(f"关键词匹配发言人: {decision}")
                return decision
            
            # 使用轮询策略，优先选择发言次数最少的智能体
            decision = self._round_robin_decision(agents, speaker_counts)
            self.logger.info(f"轮询选择发言人: {decision}")
            return decision
            
        except Exception as e:
            self.logger.error(f"决定下一个发言人失败: error={e}")
            # 返回默认选择
            return SpeakerDecision(
                agent_id=1,
                agent_role=agents[1].role if len(agents) > 1 else "智能体1",
                decision_reason="默认选择",
                confidence=0.1
            )
    
    def _keyword_based_decision(self, ceo_content_lower: str, agents: List[Agent], speaker_counts: Dict[int, int] = None) -> Optional[SpeakerDecision]:
        """基于关键词的决策"""
        keyword_mappings = [
            (['技术', '架构', '系统', '开发', '算法', '工程师'], ['技术', '开发', '架构', '工程师', '专家']),
            (['市场', '用户', '营销', '推广', '品牌'], ['市场', '营销', '推广', '品牌']),
            (['产品', '设计', '体验', '功能'], ['产品', '设计', '体验']),
            (['运营', '管理', '执行', '实施', '生产'], ['运营', '管理', '执行', '生产']),
            (['财务', '成本', '预算', '投资'], ['财务', '会计', '预算']),
            (['安全', '风险', '预警', '监测'], ['安全', '风险', '监测'])
        ]
        
        for ceo_keywords, agent_keywords in keyword_mappings:
            if any(keyword in ceo_content_lower for keyword in ceo_keywords):
                # 找到匹配的智能体，优先选择发言次数最少的
                matching_agents = []
                for agent in agents:
                    if agent.id == config.meeting.ceo_agent_id:
                        continue  # 排除CEO
                    if any(agent_keyword in agent.role.lower() for agent_keyword in agent_keywords):
                        matching_agents.append(agent)
                
                if matching_agents:
                    # 如果有发言统计，选择发言次数最少的
                    if speaker_counts:
                        best_agent = min(matching_agents, key=lambda a: speaker_counts.get(a.id, 0))
                    else:
                        best_agent = matching_agents[0]
                    
                    return SpeakerDecision(
                        agent_id=best_agent.id,
                        agent_role=best_agent.role,
                        decision_reason=f"关键词匹配: {ceo_keywords} -> {best_agent.role}",
                        confidence=0.7
                    )
        
        return None
    
    def _round_robin_decision(self, agents: List[Agent], speaker_counts: Dict[int, int] = None) -> SpeakerDecision:
        """轮询决策"""
        if len(agents) <= 1:
            return SpeakerDecision(
                agent_id=0,
                agent_role="CEO",
                decision_reason="没有其他智能体",
                confidence=0.1
            )
        
        # 获取非CEO智能体
        non_ceo_agents = [agent for agent in agents if agent.id != config.meeting.ceo_agent_id]
        
        if speaker_counts:
            # 选择发言次数最少的智能体
            target_agent = min(non_ceo_agents, key=lambda a: speaker_counts.get(a.id, 0))
            min_count = speaker_counts.get(target_agent.id, 0)
            decision_reason = f"轮询策略选择（发言次数最少: {min_count}次）"
        else:
            # 如果没有发言统计，选择第一个非CEO智能体
            target_agent = non_ceo_agents[0]
            decision_reason = "轮询策略选择（默认）"
        
        return SpeakerDecision(
            agent_id=target_agent.id,
            agent_role=target_agent.role,
            decision_reason=decision_reason,
            confidence=0.5
        )
