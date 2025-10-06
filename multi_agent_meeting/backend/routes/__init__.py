#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由模块初始化文件
"""

import os
import sys

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

from routes.meeting_routes import meeting_bp
from routes.websocket_routes import register_websocket_events

__all__ = ['meeting_bp', 'register_websocket_events']
