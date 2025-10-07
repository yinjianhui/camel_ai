#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块
提供通用的工具函数，避免代码重复
"""

import os
import sys
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any


def setup_console_encoding():
    """设置控制台编码为UTF-8"""
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


def clean_unprofessional_content(content: str) -> str:
    """清理不专业的内容"""
    # 移除表情符号
    content = re.sub(r'[😀-🙏🌀-🗿]', '', content)
    
    # 移除过于随意的表达
    casual_expressions = [
        r'~+',  # 波浪号
        r'！+',  # 多个感叹号
        r'？+',  # 多个问号
        r'（.*?）',  # 括号内容（通常是口语化表达）
    ]
    
    for pattern in casual_expressions:
        content = re.sub(pattern, '', content)
    
    # 移除多余的空格和换行
    content = re.sub(r'\s+', ' ', content).strip()
    
    return content


def remove_next_speaker_references(content: str) -> str:
    """移除最终总结中的"下一位"相关内容"""
    # 移除包含"下一位"、"继续讨论"、"下一轮"等字眼的句子
    next_speaker_patterns = [
        r'[^。！？]*下一位[^。！？]*[。！？]',
        r'[^。！？]*继续讨论[^。！？]*[。！？]',
        r'[^。！？]*下一轮[^。！？]*[。！？]',
        r'[^。！？]*请.*发言[^。！？]*[。！？]',
        r'[^。！？]*邀请.*发言[^。！？]*[。！？]',
        r'[^。！？]*让我们.*继续[^。！？]*[。！？]',
        r'[^。！？]*接下来[^。！？]*[。！？]',
    ]
    
    for pattern in next_speaker_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # 移除多余的空格和换行
    content = re.sub(r'\s+', ' ', content).strip()
    
    return content


def check_ceo_wants_to_end_meeting(content: str) -> bool:
    """检查CEO是否想要结束会议"""
    content_lower = content.lower()
    
    # 检查结束会议的关键词
    end_keywords = [
        "会议结束", "结束会议", "会议到此结束", "今天的会议", "会议总结",
        "会议结束", "会议结束", "会议结束", "会议结束", "会议结束"
    ]
    
    # 检查是否有结束会议的明确表达
    for keyword in end_keywords:
        if keyword in content_lower:
            return True
    
    # 检查是否有总结性语句
    summary_indicators = [
        "总结一下", "总的来说", "综上所述", "会议总结", "总结会议",
        "会议成果", "会议结论", "会议结束", "会议结束", "会议结束"
    ]
    
    summary_count = sum(1 for indicator in summary_indicators if indicator in content_lower)
    
    # 如果有多于2个总结性指标，且没有邀请下一位发言，可能想要结束会议
    if summary_count >= 2 and "下一位" not in content_lower and "继续" not in content_lower:
        return True
    
    return False


def post_process_ceo_content(content: str, is_meeting_started: bool = True, 
                           is_final_summary: bool = False) -> str:
    """后处理CEO内容"""
    if is_meeting_started:
        # 检查并移除重复的开场白
        opening_keywords = [
            "我们现在开始", "今天召开", "会议开始", "各位同事，上午好",
            "今天我们召开", "开始这次会议", "会议正式开始", "各位同事，我们现在开始",
            "现在开始", "开始会议", "会议现在开始", "各位同事，今天召开",
            "今天召开会议", "召开会议", "开始这次", "会议正式开始"
        ]
        
        lines = content.split('\n')
        filtered_lines = []
        skip_opening = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(kw in line_lower for kw in opening_keywords):
                skip_opening = True
                continue
            
            if skip_opening and (line.strip() == '' or 
                               line.startswith('作为') or 
                               line.startswith('根据') or
                               line.startswith('基于') or
                               line.startswith('关于') or
                               line.startswith('针对')):
                skip_opening = False
            
            if not skip_opening:
                filtered_lines.append(line)
        
        content = '\n'.join(filtered_lines).strip()
        
        # 移除表情符号和过于随意的表达
        content = clean_unprofessional_content(content)
        
        # 如果这是最终总结，移除任何"下一位"相关的内容
        if is_final_summary:
            content = remove_next_speaker_references(content)
    
    return content


def format_duration(duration_seconds: float) -> str:
    """格式化持续时间"""
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟{seconds}秒"
    else:
        return f"{seconds}秒"


def validate_required_fields(data: dict, required_fields: list) -> list:
    """验证必填字段"""
    errors = []
    for field in required_fields:
        if not data.get(field, '').strip():
            errors.append(f"{field}不能为空")
    return errors


def safe_get(dictionary: dict, key: str, default: any = None) -> any:
    """安全获取字典值"""
    return dictionary.get(key, default) if dictionary else default


def save_meeting_content(meeting_data: Dict[str, Any], save_dir: str) -> str:
    """
    保存会议内容到文件
    
    Args:
        meeting_data: 会议数据，包含会议状态、消息、总结等信息
        save_dir: 保存目录
    
    Returns:
        保存的文件路径
    """
    try:
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名（使用会议ID和时间戳）
        meeting_id = meeting_data.get('meeting_id', f"meeting_{int(datetime.now().timestamp())}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建会议数据目录
        meeting_dir = os.path.join(save_dir, f"{meeting_id}_{timestamp}")
        os.makedirs(meeting_dir, exist_ok=True)
        
        # 保存会议基本信息
        meeting_info = {
            'meeting_id': meeting_id,
            'topic': meeting_data.get('topic', ''),
            'background': meeting_data.get('background', ''),
            'start_time': meeting_data.get('start_time'),
            'end_time': meeting_data.get('end_time'),
            'total_rounds': meeting_data.get('current_round', 0),
            'total_messages': len(meeting_data.get('messages', [])),
            'participants': meeting_data.get('participants', []),
            'save_timestamp': datetime.now().isoformat()
        }
        
        # 保存会议基本信息为JSON
        info_file = os.path.join(meeting_dir, 'meeting_info.json')
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(meeting_info, f, ensure_ascii=False, indent=2)
        
        # 保存会议消息记录
        messages_file = os.path.join(meeting_dir, 'messages.json')
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(meeting_data.get('messages', []), f, ensure_ascii=False, indent=2)
        
        # 保存会议总结
        summary = meeting_data.get('summary', {})
        if summary:
            summary_file = os.path.join(meeting_dir, 'summary.json')
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 保存可读的会议记录文本
        transcript_file = os.path.join(meeting_dir, 'transcript.txt')
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"多智能体会议记录\n")
            f.write(f"会议主题：{meeting_info['topic']}\n")
            f.write(f"会议背景：{meeting_info['background']}\n")
            f.write(f"会议ID：{meeting_info['meeting_id']}\n")
            f.write(f"保存时间：{meeting_info['save_timestamp']}\n")
            f.write(f"总轮次：{meeting_info['total_rounds']}\n")
            f.write(f"总发言数：{meeting_info['total_messages']}\n")
            f.write(f"参与者：{', '.join(meeting_info['participants'])}\n")
            f.write("\n=== 会议内容 ===\n\n")
            
            # 写入消息记录
            for msg in meeting_data.get('messages', []):
                timestamp = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%H:%M:%S')
                f.write(f"[{timestamp}] {msg.get('role', 'Unknown')}: {msg.get('content', '')}\n\n")
            
            # 写入会议总结
            if summary:
                f.write("\n=== 会议总结 ===\n\n")
                f.write(summary.get('summary_content', '无总结内容'))
        
        # 保存索引文件（用于快速查找所有会议）
        index_file = os.path.join(save_dir, 'meeting_index.json')
        index_data = []
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except:
                index_data = []
        
        # 添加新会议到索引
        index_entry = {
            'meeting_id': meeting_id,
            'topic': meeting_info['topic'],
            'save_timestamp': meeting_info['save_timestamp'],
            'meeting_dir': os.path.basename(meeting_dir),
            'total_rounds': meeting_info['total_rounds'],
            'total_messages': meeting_info['total_messages'],
            'participants': meeting_info['participants']
        }
        index_data.append(index_entry)
        
        # 保存更新后的索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        return meeting_dir
        
    except Exception as e:
        print(f"保存会议内容失败: {e}")
        raise
