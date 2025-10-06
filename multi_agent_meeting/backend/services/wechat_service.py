#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信登录服务模块
处理微信扫码登录相关功能
"""

import os
import sys
import time
import uuid
import hashlib
import requests
import qrcode
from io import BytesIO
from typing import Optional, Dict, Any
from datetime import datetime

from models import User, WechatLoginSession, UserSession
from config import config
from logging_config import get_logger

# 设置控制台编码
if sys.platform == "win32":
    try:
        import codecs
        if hasattr(sys.stdout, 'detach'):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
        os.system("chcp 65001 > nul")
    except Exception:
        pass

logger = get_logger(__name__)


class WechatService:
    """微信登录服务"""
    
    def __init__(self):
        self.app_id = config.wechat.app_id
        self.app_secret = config.wechat.app_secret
        self.redirect_uri = config.wechat.redirect_uri
        self.qr_expire_time = config.wechat.qr_code_expire_time
        self.session_expire_time = config.wechat.session_expire_time
        
        # 内存存储（生产环境建议使用Redis）
        self.login_sessions: Dict[str, WechatLoginSession] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.users: Dict[str, User] = {}
        
        logger.info("微信登录服务初始化完成")
    
    def generate_qr_code(self) -> Dict[str, Any]:
        """生成微信登录二维码"""
        try:
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 生成二维码内容（这里使用模拟的微信登录URL）
            # 实际应用中需要调用微信API获取真实的二维码
            qr_content = f"https://open.weixin.qq.com/connect/qrconnect?appid={self.app_id}&redirect_uri={self.redirect_uri}&response_type=code&scope=snsapi_login&state={session_id}#wechat_redirect"
            
            # 生成二维码图片
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # 创建二维码图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            import base64
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # 创建登录会话
            current_time = time.time()
            login_session = WechatLoginSession(
                session_id=session_id,
                qr_code_url=qr_content,
                qr_code_ticket=session_id,  # 使用session_id作为ticket
                state='waiting',
                created_at=current_time,
                expires_at=current_time + self.qr_expire_time
            )
            
            self.login_sessions[session_id] = login_session
            
            logger.info(f"生成微信登录二维码: session_id={session_id}")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'qr_code_url': qr_content,
                'qr_code_base64': f"data:image/png;base64,{qr_code_base64}",
                'expires_in': self.qr_expire_time
            }
            
        except Exception as e:
            logger.error(f"生成微信登录二维码失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_login_status(self, session_id: str) -> Dict[str, Any]:
        """检查登录状态"""
        try:
            if session_id not in self.login_sessions:
                return {
                    'status': 'error',
                    'error': '会话不存在或已过期'
                }
            
            login_session = self.login_sessions[session_id]
            
            # 检查是否过期
            if login_session.is_expired():
                # 清理过期会话
                del self.login_sessions[session_id]
                return {
                    'status': 'error',
                    'error': '二维码已过期，请重新生成'
                }
            
            # 模拟登录状态检查
            # 实际应用中需要调用微信API检查扫码状态
            if login_session.state == 'waiting':
                # 模拟用户扫码（这里为了演示，随机返回扫码状态）
                import random
                if random.random() < 0.1:  # 10%概率模拟扫码
                    login_session.state = 'scanned'
                    logger.info(f"模拟用户扫码: session_id={session_id}")
            
            return {
                'status': 'success',
                'state': login_session.state,
                'expires_at': login_session.expires_at,
                'user_id': login_session.user_id,
                'openid': login_session.openid
            }
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def confirm_login(self, session_id: str, code: str = None) -> Dict[str, Any]:
        """确认登录（模拟微信授权回调）"""
        try:
            if session_id not in self.login_sessions:
                return {
                    'status': 'error',
                    'error': '会话不存在或已过期'
                }
            
            login_session = self.login_sessions[session_id]
            
            if login_session.is_expired():
                del self.login_sessions[session_id]
                return {
                    'status': 'error',
                    'error': '二维码已过期，请重新生成'
                }
            
            if login_session.state != 'scanned':
                return {
                    'status': 'error',
                    'error': '请先扫码'
                }
            
            # 模拟获取用户信息
            # 实际应用中需要调用微信API获取用户信息
            openid = f"mock_openid_{int(time.time())}"
            nickname = f"微信用户_{int(time.time()) % 10000}"
            avatar_url = "https://via.placeholder.com/100x100?text=Avatar"
            
            # 创建或更新用户
            user_id = str(uuid.uuid4())
            current_time = time.time()
            
            user = User(
                id=user_id,
                openid=openid,
                nickname=nickname,
                avatar_url=avatar_url,
                created_at=current_time,
                last_login_at=current_time
            )
            
            self.users[user_id] = user
            
            # 更新登录会话
            login_session.state = 'confirmed'
            login_session.user_id = user_id
            login_session.openid = openid
            
            # 创建用户会话
            user_session_id = str(uuid.uuid4())
            user_session = UserSession(
                session_id=user_session_id,
                user_id=user_id,
                created_at=current_time,
                expires_at=current_time + self.session_expire_time
            )
            
            self.user_sessions[user_session_id] = user_session
            
            logger.info(f"用户登录成功: user_id={user_id}, session_id={session_id}")
            
            return {
                'status': 'success',
                'user_session_id': user_session_id,
                'user': user.to_dict(),
                'expires_at': user_session.expires_at
            }
            
        except Exception as e:
            logger.error(f"确认登录失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def verify_user_session(self, session_id: str) -> Optional[User]:
        """验证用户会话"""
        try:
            if session_id not in self.user_sessions:
                return None
            
            user_session = self.user_sessions[session_id]
            
            if user_session.is_expired() or not user_session.is_active:
                # 清理过期会话
                del self.user_sessions[session_id]
                return None
            
            if user_session.user_id not in self.users:
                return None
            
            return self.users[user_session.user_id]
            
        except Exception as e:
            logger.error(f"验证用户会话失败: {e}")
            return None
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """用户登出"""
        try:
            if session_id in self.user_sessions:
                del self.user_sessions[session_id]
                logger.info(f"用户登出: session_id={session_id}")
            
            return {
                'status': 'success',
                'message': '登出成功'
            }
            
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        try:
            current_time = time.time()
            
            # 清理过期的登录会话
            expired_login_sessions = [
                session_id for session_id, session in self.login_sessions.items()
                if session.is_expired()
            ]
            for session_id in expired_login_sessions:
                del self.login_sessions[session_id]
            
            # 清理过期的用户会话
            expired_user_sessions = [
                session_id for session_id, session in self.user_sessions.items()
                if session.is_expired()
            ]
            for session_id in expired_user_sessions:
                del self.user_sessions[session_id]
            
            if expired_login_sessions or expired_user_sessions:
                logger.info(f"清理过期会话: 登录会话={len(expired_login_sessions)}, 用户会话={len(expired_user_sessions)}")
                
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")


# 全局微信服务实例
wechat_service = WechatService()
