#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议相关API路由
"""

import os
import time
import tempfile
import atexit
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file

from utils import setup_console_encoding

from models import MeetingConfig
from services.meeting_service import MeetingService
from logging_config import get_logger
from flask import current_app
from config import config

# 设置控制台编码
setup_console_encoding()

logger = get_logger(__name__)

# 创建蓝图
meeting_bp = Blueprint('meeting', __name__, url_prefix='/api')

# 创建会议服务实例
meeting_service = MeetingService()


@meeting_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    logger.debug("收到健康检查请求")
    
    try:
        # 检查会议服务状态
        meeting_status = meeting_service.get_meeting_status()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "multi-agent-meeting-backend",
            "version": "2.0.0",
            "meeting_status": meeting_status
        }
        
        logger.debug("健康检查成功")
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500


@meeting_bp.route('/start_meeting', methods=['POST'])
def start_meeting():
    """启动会议"""
    logger.info("收到启动会议请求")
    
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("启动会议请求数据为空")
            return jsonify({"status": "error", "error": "无效的请求数据"}), 400
        
        # 提取数据
        topic = data.get('topic', '').strip()
        background = data.get('background', '').strip()
        agents = data.get('agents', [])
        
        logger.debug(f"会议配置: topic='{topic}', background_length={len(background)}, agents_count={len(agents)}")
        
        # 创建会议配置
        meeting_config = MeetingConfig(
            topic=topic,
            background=background,
            agents=agents
        )
        
        # 验证配置
        errors = meeting_config.validate()
        if errors:
            logger.warning(f"会议配置验证失败: {errors}")
            return jsonify({"status": "error", "error": "; ".join(errors)}), 400
        
        # 初始化会议
        success = meeting_service.initialize_meeting(meeting_config)
        
        if success:
            logger.info("会议启动成功")
            return jsonify({"status": "success", "message": "会议启动成功"})
        else:
            logger.error("会议初始化失败")
            return jsonify({"status": "error", "error": "会议初始化失败"}), 500
            
    except Exception as e:
        logger.error(f"启动会议失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/ceo_speak', methods=['POST'])
def ceo_speak():
    """CEO发言（轮次总结）"""
    logger.info("收到CEO发言请求")
    
    try:
        result = meeting_service.ceo_speak()
        
        if result['status'] == 'success':
            # 添加消息ID防止重复
            message_with_id = {
                **result['message'],
                'message_id': f"ceo_{result['current_round']}_{int(time.time() * 1000)}"
            }
            # 通过WebSocket发送新消息
            current_app.socketio.emit('new_message', message_with_id)
            logger.info(f"CEO发言成功: round={result['current_round']}, next_speaker={result.get('next_speaker_id')}")
        else:
            logger.warning(f"CEO发言失败: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"CEO发言处理失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/agent_speak/<int:agent_id>', methods=['POST'])
def agent_speak(agent_id):
    """智能体发言"""
    logger.info(f"收到智能体发言请求: agent_id={agent_id}")
    
    try:
        result = meeting_service.agent_speak(agent_id)
        
        if result['status'] == 'success':
            # 添加消息ID防止重复
            message_with_id = {
                **result['message'],
                'message_id': f"agent_{agent_id}_{result['current_round']}_{int(time.time() * 1000)}"
            }
            # 通过WebSocket发送新消息
            current_app.socketio.emit('new_message', message_with_id)
            logger.info(f"智能体发言成功: agent_id={agent_id}, round={result['current_round']}")
        else:
            logger.warning(f"智能体发言失败: agent_id={agent_id}, error={result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"智能体发言处理失败: agent_id={agent_id}, error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/end_meeting', methods=['POST'])
def end_meeting():
    """结束会议"""
    logger.info("收到结束会议请求")
    
    try:
        result = meeting_service.end_meeting()
        
        if result['status'] == 'success':
            logger.info("会议结束成功")
        else:
            logger.warning(f"会议结束失败: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"结束会议处理失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/download_transcript', methods=['GET'])
def download_transcript():
    """下载会议记录"""
    logger.info("收到下载会议记录请求")
    
    try:
        # 检查是否有会议记录
        state = meeting_service.get_meeting_state()
        if not state.messages:
            logger.warning("没有会议记录可下载")
            return jsonify({"status": "error", "error": "没有会议记录可下载"}), 400
        
        transcript = meeting_service.get_transcript()
        
        # 创建临时文件
        filename = f"meeting_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            encoding='utf-8', 
            suffix='.txt', 
            delete=False,
            prefix='meeting_transcript_'
        )
        
        temp_file.write(transcript)
        temp_file.close()
        
        # 注册清理函数
        def cleanup_temp_file():
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except:
                pass
        
        atexit.register(cleanup_temp_file)
        
        logger.info(f"会议记录文件创建成功: filename={filename}")
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f"下载会议记录失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/restart_meeting', methods=['POST'])
def restart_meeting():
    """重启会议（清空当前会议状态）"""
    logger.info("收到重启会议请求")
    
    try:
        result = meeting_service.restart_meeting()
        
        if result['status'] == 'success':
            logger.info("会议重启成功")
        else:
            logger.warning(f"会议重启失败: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"重启会议处理失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@meeting_bp.route('/meeting_status', methods=['GET'])
def meeting_status():
    """获取会议状态"""
    logger.debug("收到获取会议状态请求")
    
    try:
        state = meeting_service.get_meeting_state()
        meeting_status_data = meeting_service.get_meeting_status()
        
        # 合并状态数据和配置信息
        response_data = {
            "status": "success",
            "meeting_state": {
                **state.to_dict(),
                "max_rounds": meeting_status_data.get("max_rounds", config.meeting.max_rounds),
                "current_round": meeting_status_data.get("current_round", state.current_round)
            }
        }
        
        logger.debug(f"返回会议状态: max_rounds={response_data['meeting_state']['max_rounds']}, current_round={response_data['meeting_state']['current_round']}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"获取会议状态失败: error={e}")
        return jsonify({"status": "error", "error": str(e)}), 500


