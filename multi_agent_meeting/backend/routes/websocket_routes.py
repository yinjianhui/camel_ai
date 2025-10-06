#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket相关路由
"""

from flask import request
from flask_socketio import emit

from utils import setup_console_encoding

from logging_config import get_logger

# 设置控制台编码
setup_console_encoding()

logger = get_logger(__name__)


def register_websocket_events(socketio):
    """注册WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接"""
        logger.info(f"客户端连接: session_id={request.sid}")
        emit('connected', {'message': '连接成功'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接"""
        logger.info(f"客户端断开连接: session_id={request.sid}")
    
    @socketio.on('join_meeting')
    def handle_join_meeting(data):
        """加入会议"""
        logger.info(f"客户端加入会议: session_id={request.sid}, data={data}")
        emit('joined_meeting', {'message': '已加入会议'})
    
    @socketio.on('error')
    def handle_error(error):
        """处理错误"""
        logger.error(f"WebSocket错误: session_id={request.sid}, error={error}")
        emit('error', {'message': '发生错误', 'error': str(error)})
    
    logger.info("WebSocket事件处理器注册完成")
