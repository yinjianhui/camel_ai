# 多智能体会议系统

基于CAMEL-AI框架的多智能体协作对话系统，采用模块化架构设计，支持CEO和多个专业智能体的实时会议讨论。

## 🆕 最新优化 (v2.1.0)

### 架构优化
- **统一配置管理**：所有配置参数统一在`config.py`中管理，避免重复配置
- **提示词模块化**：创建`prompts.py`模块，统一管理所有智能体提示词
- **工具函数统一**：创建`utils.py`模块，提供通用工具函数，消除代码重复
- **代码去冗余**：移除重复的控制台编码设置和错误处理代码

### 功能改进
- **CEO总结优化**：修复CEO最终总结问题，确保真正的深度总结，不再出现"下一位"等字样
- **智能体配置**：支持动态配置智能体数量和CEO智能体ID
- **错误处理**：改进错误处理机制，提供更清晰的错误信息

### 代码质量
- **模块化设计**：更清晰的模块分离，便于维护和扩展
- **配置验证**：增强配置验证机制，确保系统稳定运行
- **日志优化**：改进日志记录，提供更详细的调试信息

## 🎯 项目概述

本系统实现了一个智能化的多智能体会议平台，具有以下特点：
- **模块化架构**：采用现代软件工程实践，代码结构清晰，易于维护
- **CEO智能体**：负责会议管理和决策，智能引导讨论进程
- **专业智能体**：3个用户自定义角色，从不同专业角度参与讨论
- **智能发言管理**：基于AI的智能决策下一个发言者
- **完整会议记录**：实时记录、自动总结、文档导出功能

## ✨ 核心功能

- **智能体配置**：CEO + 3个自定义专业角色，每个智能体使用独立API密钥
- **会议管理**：主题设置、智能发言、轮次控制（最多20轮）、实时通信
- **CEO交互**：支持用户输入或5秒自动发言，智能决策下一个发言者
- **会议记录**：实时记录、自动总结、文档导出
- **健康检查**：内置健康检查API，便于监控和运维

## 🏗️ 技术架构

### 后端架构（模块化设计）
- **Flask**：Web框架
- **CAMEL-AI**：多智能体框架
- **DeepSeek API**：大语言模型服务
- **WebSocket**：实时通信
- **模块化设计**：配置管理、服务层、路由层分离

### 前端技术栈
- **Vue.js 3**：前端框架
- **Socket.IO**：实时通信客户端
- **现代CSS**：响应式设计

### 系统架构图
```
前端界面(Vue.js) ←→ 后端API(Flask+CAMEL-AI) ←→ DeepSeek API(4个密钥)
       ↓                    ↓
   WebSocket实时通信
   
后端模块结构：
├── app_new.py          # 主应用入口
├── config.py           # 统一配置管理
├── prompts.py          # 提示词配置模块
├── utils.py            # 通用工具函数
├── logging_config.py   # 日志配置
├── models.py           # 数据模型
├── services/           # 业务服务层
│   ├── meeting_service.py
│   └── agent_service.py
└── routes/             # API路由层
    ├── meeting_routes.py
    └── websocket_routes.py
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 4个DeepSeek API密钥

### 安装步骤

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置API密钥**
编辑 `backend/config.py` 文件，替换为您的真实API密钥：
```python
self.api_keys: List[str] = [
    "sk-your-ceo-api-key-here",
    "sk-your-agent1-api-key-here", 
    "sk-your-agent2-api-key-here",
    "sk-your-agent3-api-key-here"
]
```

3. **启动服务**

**方式一：使用启动脚本（推荐）**
```bash
# 启动新版本（模块化架构）
python start_server.py --version new

# 或指定端口和主机
python start_server.py --version new --port 5000 --host 0.0.0.0 --debug
```

**方式二：直接启动**
```bash
# 启动后端
python app_new.py

# 启动前端（新终端）
cd frontend
python -m http.server 8000
```

访问 `http://localhost:8000` 开始使用

## 📖 使用指南

1. **配置会议**：输入会议主题、背景信息，配置4个智能体角色
2. **开始会议**：CEO开场，智能决策下一个发言者
3. **会议进行**：CEO可输入内容或自动发言，其他智能体按需发言
4. **结束会议**：达到20轮或手动结束，自动生成总结和记录

## 🔧 API接口

### 会议管理API
- `GET /api/health` - 健康检查
- `POST /api/start_meeting` - 启动会议
- `POST /api/ceo_speak` - CEO发言
- `POST /api/agent_speak/<agent_id>` - 智能体发言
- `POST /api/end_meeting` - 结束会议
- `GET /api/download_transcript` - 下载会议记录
- `GET /api/meeting_status` - 获取会议状态

### WebSocket事件
- `connect` - 客户端连接
- `disconnect` - 客户端断开
- `new_message` - 新消息推送
- `join_meeting` - 加入会议
- `error` - 错误处理

## 🎨 界面特性

- **响应式设计**：支持桌面和移动设备
- **实时通信**：WebSocket实时消息推送
- **无障碍支持**：完整的ARIA标签和键盘导航
- **用户体验**：实时状态显示、倒计时进度条、错误提示

## 🐛 故障排除

### 常见问题
1. **API密钥错误** - 检查config.py中的密钥和DeepSeek账户余额
2. **WebSocket连接失败** - 检查防火墙和端口5000占用情况
3. **智能体无响应** - 检查网络连接和后端日志
4. **前端无法连接后端** - 确认后端服务已启动
5. **控制台乱码** - 系统已自动配置UTF-8编码，如仍有问题请检查终端设置

### 日志查看
```bash
# 查看日志文件
tail -f backend/logs/meeting_*.log

# 查看错误日志
grep "ERROR" backend/logs/meeting_*.log
```

### 健康检查
访问 `http://localhost:5000/api/health` 检查服务状态

## 📝 项目结构

```
multi_agent_meeting/
├── backend/                    # 后端服务（模块化架构）
│   ├── app_new.py             # 主应用入口
│   ├── start_server.py        # 启动脚本
│   ├── config.py              # 统一配置管理
│   ├── prompts.py             # 提示词配置模块
│   ├── utils.py               # 通用工具函数
│   ├── logging_config.py      # 日志配置
│   ├── models.py              # 数据模型
│   ├── services/              # 业务服务层
│   │   ├── __init__.py
│   │   ├── meeting_service.py # 会议服务
│   │   └── agent_service.py   # 智能体服务
│   ├── routes/                # API路由层
│   │   ├── __init__.py
│   │   ├── meeting_routes.py  # 会议API路由
│   │   └── websocket_routes.py # WebSocket路由
│   ├── logs/                  # 日志文件目录
│   ├── temp/                  # 临时文件目录
│   └── requirements.txt       # 依赖列表
├── frontend/                  # 前端界面
│   ├── index.html             # 主页面
│   ├── app.js                # Vue.js应用
│   └── style.css             # 样式文件
└── README.md                 # 项目文档
```

## 🔧 开发说明

### 模块化架构优势
- **统一配置管理**：所有配置参数统一在`config.py`中管理，支持环境变量
- **提示词模块化**：`prompts.py`统一管理所有智能体提示词，避免重复配置
- **工具函数统一**：`utils.py`提供通用工具函数，消除代码重复
- **日志系统**：完整的日志记录，支持文件和控制台输出
- **服务分离**：业务逻辑与API路由分离，便于测试和维护
- **错误处理**：统一的错误处理和日志记录
- **健康检查**：内置健康检查API，便于监控

### 扩展开发
- 添加新的智能体类型
- 实现更复杂的发言决策算法
- 集成其他大语言模型
- 添加会议录制功能
- 实现用户认证和权限管理

---

**多智能体会议系统** - 让AI智能体协作更智能！
