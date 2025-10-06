#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置和管理
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

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


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则使用默认路径
        max_file_size: 单个日志文件最大大小（字节）
        backup_count: 保留的日志文件数量
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
    
    Returns:
        配置好的logger实例
    """
    
    # 创建logger
    logger = logging.getLogger('multi_agent_meeting')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 日志格式
    detailed_format = (
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    simple_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    
    # 控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # 设置控制台输出编码为UTF-8
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8')
            except:
                pass
        
        # 使用彩色格式化器
        console_formatter = ColoredFormatter(simple_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if enable_file:
        # 创建日志目录
        if log_file is None:
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'meeting_{datetime.now().strftime("%Y%m%d")}.log')
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # 使用RotatingFileHandler实现日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # 使用详细格式化器
        file_formatter = logging.Formatter(detailed_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # 防止日志重复
    logger.propagate = False
    
    return logger


def get_logger(name: str = 'multi_agent_meeting') -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logger实例
    """
    return logging.getLogger(name)


# 创建默认logger
default_logger = setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    enable_console=True,
    enable_file=True
)
