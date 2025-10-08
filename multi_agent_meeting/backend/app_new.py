#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多智能体会议系统后端 - 重构版本
基于CAMEL-AI框架实现四个智能体的协作对话
采用模块化设计，便于维护和扩展
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from utils import setup_console_encoding

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from logging_config import setup_logging, get_logger
from routes import meeting_bp
from routes.websocket_routes import register_websocket_events
from services.meeting_service import MeetingService

# 设置控制台编码
setup_console_encoding()

# 设置日志
logger = setup_logging(
    log_level=config.logging.level,
    enable_console=config.logging.enable_console,
    enable_file=config.logging.enable_file
)

logger.info("=" * 60)
logger.info("多智能体会议系统后端启动")
logger.info("=" * 60)

def create_app():
    """创建Flask应用"""
    logger.info("创建Flask应用")
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.flask_secret_key
    
    # 配置CORS
    CORS(app, origins=config.websocket.cors_allowed_origins)
    logger.info(f"CORS配置: origins={config.websocket.cors_allowed_origins}")
    
    # 注册蓝图
    app.register_blueprint(meeting_bp)
    logger.info("API路由注册完成")
    
    # 创建SocketIO实例
    socketio = SocketIO(
        app, 
        cors_allowed_origins=config.websocket.cors_allowed_origins,
        async_mode=config.websocket.async_mode,
        ping_timeout=config.websocket.ping_timeout,
        ping_interval=config.websocket.ping_interval,
        # 新增WebSocket优化参数
        engineio_logger=config.websocket.engineio_logger,
        manage_session=config.websocket.manage_session,
        http_compression=config.websocket.http_compression,
        compression_threshold=config.websocket.compression_threshold,
        cookie=config.websocket.cookie,
        cors_credentials=config.websocket.cors_credentials
    )
    logger.info(f"SocketIO配置: async_mode={config.websocket.async_mode}")
    logger.info(f"WebSocket优化: compression={config.websocket.http_compression}, manage_session={config.websocket.manage_session}")
    
    # 注册WebSocket事件
    register_websocket_events(socketio)
    
    # 创建全局会议服务实例
    meeting_service = MeetingService()
    
    # 将服务实例添加到应用上下文
    app.meeting_service = meeting_service
    app.socketio = socketio
    
    logger.info("Flask应用创建完成")
    return app, socketio


def validate_environment():
    """验证环境配置"""
    logger.info("验证环境配置")
    
    # 验证配置
    errors = config.validate_config()
    if errors:
        logger.error("配置验证失败:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("环境配置验证通过")
    return True


def print_startup_info():
    """打印启动信息"""
    logger.info("系统配置信息:")
    logger.info(f"  Flask: {config.flask_host}:{config.flask_port}")
    logger.info(f"  调试模式: {config.flask_debug}")
    logger.info(f"  API基础URL: {config.api.base_url}")
    logger.info(f"  模型类型: {config.api.model_type}")
    logger.info(f"  会议最大轮次: {config.meeting.max_rounds}")
    logger.info(f"  日志级别: {config.logging.level}")
    logger.info(f"  WebSocket异步模式: {config.websocket.async_mode}")
    
    logger.info("API密钥配置:")
    for i, key in enumerate(config.api_keys):
        logger.info(f"  智能体{i+1}: {key[:10]}...")
    
    logger.info("目录配置:")
    logger.info(f"  日志目录: {config.logs_dir}")
    logger.info(f"  临时目录: {config.temp_dir}")




def create_gunicorn_app():
    """为gunicorn创建应用实例"""
    # 验证环境
    if not validate_environment():
        logger.error("环境验证失败，程序退出")
        sys.exit(1)
    
    # 打印启动信息
    print_startup_info()
    
    # 创建应用
    app, socketio = create_app()
    
    # 将socketio实例添加到app中，供gunicorn使用
    app.socketio = socketio
    
    return app


def main():
    """主函数"""
    try:
        # 验证环境
        if not validate_environment():
            logger.error("环境验证失败，程序退出")
            return 1
        
        # 打印启动信息
        print_startup_info()
        
        # 创建应用
        app, socketio = create_app()
        
        # 启动应用
        logger.info("启动Web服务器...")
        
        # 检查是否为生产环境
        if not config.flask_debug:
            logger.info("生产环境模式 - 使用生产服务器配置")
            # 生产环境设置
            socketio.run(
                app, 
                host=config.flask_host, 
                port=config.flask_port, 
                debug=False,
                allow_unsafe_werkzeug=True  # 允许在生产环境使用Werkzeug
            )
        else:
            # 开发环境设置
            socketio.run(
                app, 
                host=config.flask_host, 
                port=config.flask_port, 
                debug=config.flask_debug
            )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        return 1
    finally:
        logger.info("服务器已关闭")
    
    return 0


# 创建gunicorn应用实例
app = create_gunicorn_app()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
