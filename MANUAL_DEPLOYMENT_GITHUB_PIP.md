# 多智能体会议系统 - 基于GitHub和pip的手动部署指南

## 📋 部署信息

### 服务器信息
- **服务器IP**: 111.229.108.199
- **登录账号**: root
- **操作系统**: Linux (推荐Ubuntu 20.04+或CentOS 7+)
- **Python版本要求**: 3.11
- **访问方式**: 公网IP直接访问
- **项目路径**: /root

### 项目信息
- **项目地址**: https://github.com/yinjianhui/camel_ai.git
- **项目名称**: camel_ai
- **主要组件**: 多智能体会议系统 (multi_agent_meeting)
- **后端端口**: 5000
- **前端端口**: 80 (通过Nginx代理)
- **部署路径**: /root

## 🚀 完整手动部署步骤

### 第一步：连接服务器

```bash
# 使用SSH连接到服务器
ssh root@111.229.108.199

# 连接成功后，确认服务器信息
hostname
uname -a
```

### 第二步：更新系统并安装基础软件

```bash
# Ubuntu/Debian系统
apt update && apt upgrade -y
apt install -y python3.11 python3.11-pip python3.11-venv nginx git curl wget

# CentOS/RHEL系统
yum update -y
yum install -y python3.11 python3.11-pip nginx git curl wget

# 验证Python版本
python3.11 --version
# 应该显示: Python 3.11.x

# 验证pip版本
pip3.11 --version
```

### 第三步：在/root目录下克隆代码

```bash
# 进入root目录
cd /root

# 克隆项目代码
git clone https://github.com/yinjianhui/camel_ai.git

# 检查项目结构
ls -la

# 进入项目目录
cd camel_ai
```

### 第三步（新增）：前端API配置优化说明
**重要更新**: 前端API配置已优化，使用相对路径自动适配服务器环境。

**优化内容**:
- **前端配置**: 使用相对路径（空字符串）自动适配当前域名
- **自动适配**: 前端自动使用当前访问的域名进行API调用
- **环境无关**: 开发和生产环境使用相同配置，无需修改

**实际配置**:
```javascript
// 当前前端配置（已优化）
apiBase: '', // 使用相对路径自动适应当前域名

// 系统状态自动获取
systemStatus: {
    serverUrl: window.location.origin, // 当前服务器地址
    apiBaseUrl: '' // API基础URL（相对路径）
}
```

**优势**:
1. **完全自动**: 无需任何手动配置，前端自动适配
2. **环境无关**: 开发、测试、生产环境配置完全一致
3. **零维护**: 服务器IP、域名变更时完全无需修改前端代码
4. **最大灵活性**: 支持任意访问方式（IP、域名、端口等）

**实际API调用示例**:
```javascript
// 健康检查（自动适配当前域名）
const response = await fetch(`${this.apiBase}/api/health`, {
    method: 'GET',
    timeout: 5000
});

// 启动会议（自动适配当前域名）
const data = await this.apiCall(`${this.apiBase}/api/start_meeting`, {
    method: 'POST',
    body: JSON.stringify({...})
});

// WebSocket连接（自动适配当前域名）
this.socket = io(this.apiBase, { // 使用相对路径
    transports: ['websocket', 'polling'],
    timeout: 20000,
    forceNew: true
});
```

**系统初始化**:
```javascript
// 系统启动时自动获取当前环境信息
initializeSystemStatus() {
    // 设置服务器URL和API基础URL
    this.systemStatus.serverUrl = window.location.origin;
    this.systemStatus.apiBaseUrl = this.apiBase;
    
    // 记录当前环境信息
    this.log('info', '系统状态初始化完成', {
        serverUrl: this.systemStatus.serverUrl,
        apiBaseUrl: this.systemStatus.apiBaseUrl,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
    });
}
```

**部署优势**:
- **开箱即用**: 部署后前端立即自动适配服务器环境
- **无需配置**: 不需要在前端代码中配置任何服务器地址
- **无缝切换**: 支持IP访问、域名访问、带端口访问等多种方式
- **负载均衡友好**: 支持多服务器负载均衡环境
- **HTTPS友好**: 自动适配HTTP和HTTPS协议

**预期输出应该包含以下目录和文件：**
```
drwxr-xr-x  4 root root    4096 Oct  7 14:00 Legion
drwxr-xr-x  4 root root    4096 Oct  7 14:00 multi_agent_meeting
-rw-r--r--  1 root root    1234 Oct  7 14:00 .gitignore
-rw-r--r--  1 root root    5678 Oct  7 14:00 deploy_to_server.ps1
```

### 第四步：安装项目依赖

```bash
cd /root/camel_ai

# 验证Python版本
python3.11 --version
# 应该显示: Python 3.11.x

# 升级pip到最新版本
python3.11 -m pip install --upgrade pip

# 安装项目依赖
python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt

# 验证依赖安装
python3.11 -m pip list
```

**预期应该包含以下包:**
```
flask==2.2.5
flask-cors==4.0.0
flask-socketio==5.3.5
camel-ai==0.2.1
python-socketio==5.10.0
openai==1.3.0
python-dotenv==1.0.0
```

### 第五步：验证关键依赖包

```bash
# 验证Flask相关包
python3.11 -c "import flask; print('Flask版本:', flask.__version__)"
python3.11 -c "import flask_cors; print('Flask-CORS版本:', flask_cors.__version__)"
python3.11 -c "import flask_socketio; print('Flask-SocketIO版本:', flask_socketio.__version__)"

# 验证CAMEL-AI模块
python3.11 -c "import camel_ai; print('CAMEL-AI版本:', camel_ai.__version__)"
python3.11 -c "from camel.agents import ChatAgent; print('ChatAgent导入成功')"
python3.11 -c "from camel.messages import BaseMessage; print('BaseMessage导入成功')"
python3.11 -c "from camel.models import ModelFactory; print('ModelFactory导入成功')"

# 验证OpenAI包
python3.11 -c "import openai; print('OpenAI版本:', openai.__version__)"

# 验证其他依赖
python3.11 -c "import python_socketio; print('Python-SocketIO导入成功')"
python3.11 -c "import dotenv; print('python-dotenv导入成功')"
```

### 第六步：配置环境变量

```bash
# 复制环境配置示例文件
# 注意：这一步是必需的，因为应用通过os.getenv()读取环境变量配置
# 即使不使用虚拟环境，.env文件仍然是应用配置的标准方式
cp multi_agent_meeting/backend/env.example multi_agent_meeting/backend/.env

# 编辑配置文件
nano multi_agent_meeting/backend/.env
```

**在.env文件中添加以下配置：**
```bash
# Flask配置
FLASK_SECRET_KEY=multi_agent_meeting_secret_key_2024
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# API配置（已预配置，无需修改）
API_BASE_URL=https://api.deepseek.com/v1
API_MODEL_TYPE=deepseek-chat
API_TEMPERATURE=0.7
API_MAX_TOKENS=4096
API_TIMEOUT=30

# 会议配置
MEETING_MAX_ROUNDS=13
MEETING_TIMER_SECONDS=5
MEETING_MAX_HISTORY=20
MEETING_AUTO_SAVE_INTERVAL=300
MEETING_AGENT_COUNT=4
MEETING_CEO_AGENT_ID=0

# 日志配置
LOG_LEVEL=INFO
LOG_ENABLE_CONSOLE=True
LOG_ENABLE_FILE=True

# WebSocket配置
WEBSOCKET_CORS_ORIGINS=*
WEBSOCKET_ASYNC_MODE=threading
WEBSOCKET_PING_TIMEOUT=60
WEBSOCKET_PING_INTERVAL=25
```

### 第七步：验证API密钥配置

```bash
# 检查API密钥配置（已预配置）
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"
```

**预期输出应该显示4个API密钥：**
```python
self.api_keys: List[str] = [
    "sk-be71c40c6090410dbd554490cf7629d5",
    "sk-f06a9bfd2bc1423991dd6d5094e1a2cd", 
    "sk-54022c1f872a4af1bc52fc9071b2a18d",
    "sk-d8dd47f48a8f433ca437ccf425f0c125"
]
```

### 第八步：创建必要的目录并设置权限

```bash
# 创建日志、临时文件和会议保存目录
mkdir -p multi_agent_meeting/backend/logs
mkdir -p multi_agent_meeting/backend/temp
mkdir -p multi_agent_meeting/backend/saved_meetings

# 设置目录权限（赋予所有用户所有权限）
chmod -R 777 multi_agent_meeting/backend/logs
chmod -R 777 multi_agent_meeting/backend/temp
chmod -R 777 multi_agent_meeting/backend/saved_meetings

# 设置其他目录权限
chmod -R 755 multi_agent_meeting/backend/
chown -R root:root multi_agent_meeting/backend/
```

### 第九步：测试应用启动

```bash
# 进入后端目录
cd multi_agent_meeting/backend

# 手动启动应用进行测试
python3.11 app_new.py &
```

**预期输出应该显示：**
```
多智能体会议系统后端启动
============================================================
创建Flask应用
CORS配置: origins=*
API路由注册完成
SocketIO配置: async_mode=threading
Flask应用创建完成
验证环境配置
环境配置验证通过
系统配置信息:
  Flask: 0.0.0.0:5000
  调试模式: False
  API基础URL: https://api.deepseek.com/v1
  模型类型: deepseek-chat
  会议最大轮次: 13
  日志级别: INFO
  WebSocket异步模式: threading
API密钥配置:
  智能体1: sk-be71c40c...
  智能体2: sk-f06a9bf...
  智能体3: sk-54022c1...
  智能体4: sk-d8dd47f...
目录配置:
  日志目录: /root/camel_ai/multi_agent_meeting/backend/logs
  临时目录: /root/camel_ai/multi_agent_meeting/backend/temp
启动Web服务器...
```

### 第十步：验证应用运行状态

```bash
# 检查端口监听
netstat -tlnp | grep :5000

# 测试API健康检查
curl http://localhost:5000/api/health

# 停止测试应用
pkill -f "python app_new.py"
```

### 第十一步：创建systemd服务

```bash
# 创建systemd服务文件
nano /etc/systemd/system/multi-agent-meeting.service
```

**添加以下内容：**
```ini
[Unit]
Description=Multi Agent Meeting System
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/root/camel_ai
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/root/camel_ai
ExecStart=/usr/bin/python3.11 multi_agent_meeting/backend/app_new.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 第十二步：配置Nginx反向代理

```bash
# 创建Nginx配置文件
nano /etc/nginx/sites-available/multi-agent-meeting
```

**添加以下配置：**
```nginx
server {
    listen 80;
    server_name 111.229.108.199;  # 服务器IP地址

    # 前端静态文件
    location / {
        root /root/camel_ai/multi_agent_meeting/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 第十三步：启用Nginx站点

```bash
# 启用站点
ln -s /etc/nginx/sites-available/multi-agent-meeting /etc/nginx/sites-enabled/

# 删除默认站点（可选）
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 重新加载Nginx配置
systemctl reload nginx
```

### 第十四步：配置防火墙

```bash
# Ubuntu/Debian系统 (ufw)
ufw allow 22
ufw allow 80
ufw allow 5000
ufw enable

# CentOS/RHEL系统 (firewalld)
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

### 第十五步：启动服务

```bash
# 重新加载systemd配置
systemctl daemon-reload

# 启用服务（开机自启）
systemctl enable multi-agent-meeting

# 启动服务
systemctl start multi-agent-meeting

# 检查服务状态
systemctl status multi-agent-meeting
```

**预期输出应该显示服务正在运行：**
```
● multi-agent-meeting.service - Multi Agent Meeting System
   Loaded: loaded (/etc/systemd/system/multi-agent-meeting.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2024-10-07 14:00:00 CST; 5s ago
 Main PID: 12345 (python)
    Tasks: 2 (limit: 1137)
   Memory: 45.6M
   CGroup: /system.slice/multi-agent-meeting.service
           └─12345 /usr/bin/python3.11 multi_agent_meeting/backend/app_new.py
```

### 第十六步：验证部署

```bash
# 检查服务日志
journalctl -u multi-agent-meeting -f --lines=50

# 检查端口监听
netstat -tlnp | grep :5000
netstat -tlnp | grep :80

# 测试API健康检查
curl http://localhost:5000/api/health

# 测试公网访问
curl http://111.229.108.199/api/health
```

### 第十七步：访问应用

现在您可以通过以下地址访问应用：

**前端页面：**
```
http://111.229.108.199
```

**API接口：**
```
http://111.229.108.199/api/health
http://111.229.108.199/api/meetings
http://111.229.108.199/api/config
```

## 🔧 服务管理命令

### 启动/停止/重启服务
```bash
# 启动服务
systemctl start multi-agent-meeting

# 停止服务
systemctl stop multi-agent-meeting

# 重启服务
systemctl restart multi-agent-meeting

# 查看服务状态
systemctl status multi-agent-meeting

# 启用/禁用开机自启
systemctl enable multi-agent-meeting
systemctl disable multi-agent-meeting
```

### 查看日志
```bash
# 查看服务日志（实时）
journalctl -u multi-agent-meeting -f

# 查看服务日志（最近100行）
journalctl -u multi-agent-meeting -n 100

# 查看应用日志
tail -f /root/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 更新代码和依赖
```bash
cd /root/camel_ai

# 拉取最新代码
git pull origin master

# 更新依赖（如果有新的依赖包）
python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt

# 重启服务
systemctl restart multi-agent-meeting

# 检查服务状态
systemctl status multi-agent-meeting
```

### 重新安装依赖
```bash
cd /root/camel_ai

# 卸载所有包（谨慎使用）
python3.11 -m pip freeze | xargs python3.11 -m pip uninstall -y

# 重新安装依赖
python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt

# 重启服务
systemctl restart multi-agent-meeting
```

## 🐛 故障排除

### 1. 服务启动失败

```bash
# 检查服务状态
systemctl status multi-agent-meeting

# 查看详细日志
journalctl -u multi-agent-meeting -n 50

# 检查Python环境
python3.11 --version
python3.11 -c "import flask, flask_cors, flask_socketio, camel_ai, openai"

# 手动启动测试
python3.11 multi_agent_meeting/backend/app_new.py
```

### 2. 依赖包安装问题

```bash
# 检查pip版本
pip --version

# 升级pip
python3.11 -m pip install --upgrade pip

# 清理pip缓存
python3.11 -m pip cache purge

# 重新安装依赖
python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt --force-reinstall

# 检查包冲突
python3.11 -m pip check
```

### 3. CAMEL-AI模块问题

```bash
# 检查CAMEL-AI安装
pip show camel-ai

# 重新安装CAMEL-AI
python3.11 -m pip uninstall camel-ai -y
python3.11 -m pip install camel-ai==0.2.1

# 验证CAMEL-AI组件
python3.11 -c "
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType
print('CAMEL-AI所有组件验证成功')
"
```

### 4. 端口被占用

```bash
# 检查端口占用
netstat -tlnp | grep :5000
netstat -tlnp | grep :80

# 终止占用进程
kill -9 <PID>
```

### 5. 权限问题

```bash
# 修复权限
chown -R root:root /root/camel_ai
chmod -R 755 /root/camel_ai
chmod -R 755 /root/camel_ai/multi_agent_meeting/backend/

# 确保logs、temp、saved_meetings目录有所有权限
chmod -R 777 /root/camel_ai/multi_agent_meeting/backend/logs
chmod -R 777 /root/camel_ai/multi_agent_meeting/backend/temp
chmod -R 777 /root/camel_ai/multi_agent_meeting/backend/saved_meetings
```

### 6. Nginx配置问题

```bash
# 测试Nginx配置
nginx -t

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 重新加载Nginx
systemctl reload nginx
```

### 7. API密钥问题

```bash
# 检查API密钥配置
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"

# 检查环境变量
cat multi_agent_meeting/backend/.env
```

## 📊 部署验证清单

### 系统环境验证
- [ ] 服务器连接成功 (ssh root@111.229.108.199)
- [ ] 系统更新完成 (apt/yum update)
- [ ] Python 3.11安装成功 (python3.11 --version)
- [ ] pip安装成功 (pip3.11 --version)
- [ ] Nginx安装成功 (nginx -v)
- [ ] Git安装成功 (git --version)

### 项目文件验证
- [ ] 项目克隆成功 (git clone)
- [ ] 项目目录结构完整 (ls -la)
- [ ] requirements.txt文件存在
- [ ] env.example文件存在
- [ ] app_new.py文件存在

### Python环境验证
- [ ] Python 3.11版本正确 (python3.11 --version)
- [ ] pip升级完成 (python3.11 -m pip install --upgrade pip)
- [ ] 系统Python环境可用

### 依赖包安装验证
- [ ] 所有依赖包安装成功 (pip install -r requirements.txt)
- [ ] Flask相关包导入正常
- [ ] CAMEL-AI模块导入正常
- [ ] OpenAI包导入正常
- [ ] 其他依赖包导入正常

### 服务配置验证
- [ ] systemd服务创建成功 (multi-agent-meeting.service)
- [ ] Nginx配置创建成功 (sites-available/multi-agent-meeting)
- [ ] Nginx站点启用成功 (sites-enabled/multi-agent-meeting)
- [ ] 防火墙规则配置成功 (端口80, 5000开放)
- [ ] 目录权限设置正确 (chmod, chown)

### 服务启动验证
- [ ] 手动启动测试成功 (python app_new.py)
- [ ] 服务启动成功 (systemctl start multi-agent-meeting)
- [ ] 服务运行状态正常 (systemctl status multi-agent-meeting)
- [ ] 端口监听正常 (netstat -tlnp)
- [ ] 日志输出正常 (journalctl -u multi-agent-meeting)

### 功能验证
- [ ] 前端页面可访问 (http://111.229.108.199)
- [ ] API健康检查正常 (curl http://111.229.108.199/api/health)
- [ ] WebSocket连接正常 (浏览器开发者工具检查)
- [ ] 智能体会议功能正常 (创建会议测试)

## 🎯 部署完成后的访问方式

### 主要访问地址
- **系统主页**: http://111.229.108.199
- **API健康检查**: http://111.229.108.199/api/health
- **系统配置**: http://111.229.108.199/api/config

### 管理命令速查
```bash
# 查看服务状态
systemctl status multi-agent-meeting

# 重启服务
systemctl restart multi-agent-meeting

# 查看日志
journalctl -u multi-agent-meeting -f

# 更新代码和依赖
cd /root/camel_ai && git pull origin master && python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt && systemctl restart multi-agent-meeting
```

## 🔄 更新和维护

### 代码更新
```bash
cd /root/camel_ai
git pull origin master
python3.11 -m pip install -r multi_agent_meeting/backend/requirements.txt
systemctl restart multi-agent-meeting
```

### 依赖更新
```bash
cd /root/camel_ai
python3.11 -m pip install --upgrade -r multi_agent_meeting/backend/requirements.txt
systemctl restart multi-agent-meeting
```

### 系统更新
```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# CentOS/RHEL
yum update -y
```

## 📞 技术支持

如果部署过程中遇到问题，请检查：
1. **服务日志**: `journalctl -u multi-agent-meeting -f`
2. **应用日志**: `tail -f /root/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log`
3. **Nginx日志**: `tail -f /var/log/nginx/error.log`
4. **系统资源**: `htop`, `df -h`, `free -h`
5. **网络连接**: `netstat -tlnp`, `curl http://localhost:5000/api/health`
6. **Python环境**: `python3.11 --version && python3.11 -m pip list`

## 🚨 生产环境常见问题及解决方案

### 1. Vue开发版本警告
**问题**: 浏览器控制台显示 `You are running a development build of Vue. Make sure to use the production build (*.prod.js) when deploying for production.`

**解决方案**:
```bash
# 编辑前端HTML文件，将Vue开发版本替换为生产版本
nano /root/camel_ai/multi_agent_meeting/frontend/index.html

# 将这行：
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

# 替换为：
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
```

### 2. Favicon 404错误
**问题**: 浏览器控制台显示 `/favicon.ico:1 Failed to load resource: the server responded with a status of 404 (Not Found)`

**解决方案**:
```bash
# 创建一个简单的favicon.ico文件或添加到Nginx配置中
# 方法1：创建favicon.ico
cd /root/camel_ai/multi_agent_meeting/frontend
wget -O favicon.ico https://www.google.com/favicon.ico

# 方法2：在Nginx配置中添加favicon处理
nano /etc/nginx/sites-available/multi-agent-meeting

# 在server块中添加：
location = /favicon.ico {
    access_log off;
    log_not_found off;
    return 204;
}
```

### 3. CEO发言失败和JavaScript函数错误
**问题**: 
- `CEO发言失败 Error: 会议已结束`
- `Uncaught TypeError: this.startCeoTimer is not a function`

**解决方案**:
```bash
# 检查前端JavaScript代码，确保所有函数都正确定义
nano /root/camel_ai/multi_agent_meeting/frontend/app.js

# 确保以下函数都存在并正确定义：

# 1. startCeoTimer函数 - CEO定时器管理
startCeoTimer() {
    this.log('info', '启动CEO定时器');
    
    // 清除现有定时器
    if (this.ceoTimer) {
        clearInterval(this.ceoTimer);
        this.ceoTimer = null;
    }
    
    // 设置新的定时器，定期检查会议状态
    this.ceoTimer = setInterval(() => {
        this.checkMeetingStatus();
    }, 5000); // 每5秒检查一次
    
    // 立即执行一次检查
    this.checkMeetingStatus();
},

# 2. stopCeoTimer函数 - 停止CEO定时器
stopCeoTimer() {
    this.log('info', '停止CEO定时器');
    
    if (this.ceoTimer) {
        clearInterval(this.ceoTimer);
        this.ceoTimer = null;
    }
},

# 3. checkMeetingStatus函数 - 检查会议状态
async checkMeetingStatus() {
    try {
        const data = await this.apiCall(`${this.apiBase}/api/meeting_status`, {
            method: 'GET'
        });
        
        if (data.status === 'success' && data.meeting_state) {
            this.log('debug', '会议状态检查成功', data.meeting_state);
            
            // 如果会议已结束但前端未更新，则更新状态
            if (data.meeting_state.status === 'ended' && !this.showSummary) {
                this.log('info', '检测到会议已结束，更新前端状态');
                this.stopCeoTimer();
                this.isThinking = false;
                this.currentSpeakerId = null;
                this.waitingForCeo = false;
                this.generateSummary();
            }
        }
    } catch (error) {
        this.log('warn', '检查会议状态失败', error);
    }
},

# 4. 在beforeUnmount中添加定时器清理
beforeUnmount() {
    // 断开WebSocket连接
    if (this.socket) {
        this.socket.disconnect();
    }
    
    // 停止CEO定时器
    this.stopCeoTimer();
    
    // 移除键盘事件监听
    document.removeEventListener('keydown', this.handleKeydown);
}

# 5. 检查会议状态逻辑，确保CEO发言时会议未结束
async startCeoSpeak() {
    // 检查会议是否已结束
    if (this.showSummary || !this.meetingStarted) {
        this.log('info', '会议已结束，停止CEO发言');
        return;
    }
    
    this.log('info', 'CEO开始发言（轮次总结）');
    
    try {
        const data = await this.apiCall(`${this.apiBase}/api/ceo_speak`, {
            method: 'POST'
        });
        
        if (data.status === 'success') {
            // 处理CEO发言成功逻辑
        } else {
            // 检查是否是会议结束错误
            if (data.error && data.error.includes('会议正在结束')) {
                this.log('info', '会议正在结束，停止CEO发言');
                this.isThinking = false;
                return;
            }
            throw new Error(data.error || '发言失败');
        }
    } catch (error) {
        this.log('error', 'CEO发言失败', error);
        this.showNotification('CEO发言失败：' + error.message, 'error');
        this.isThinking = false;
    }
}
```

**修复后的效果**:
- ✅ `startCeoTimer` 函数已正确定义，不再出现 `is not a function` 错误
- ✅ CEO定时器管理完善，包括启动、停止和状态检查
- ✅ 会议状态监控机制健全，能够及时检测会议结束状态
- ✅ 组件销毁时自动清理定时器，避免内存泄漏
- ✅ CEO发言逻辑增强，包含会议状态检查和错误处理

### 4. WebSocket连接不稳定
**问题**: `WebSocket connection failed: Invalid frame header` 和 `WebSocket连接断开`

**解决方案**:
```bash
# 1. 后端WebSocket配置优化
nano /root/camel_ai/multi_agent_meeting/backend/config.py

# 确保WebSocket配置包含优化参数：
@dataclass
class WebSocketConfig:
    """WebSocket配置"""
    cors_allowed_origins: str = "*"
    async_mode: str = "threading"
    ping_timeout: int = 60
    ping_interval: int = 25
    # 新增WebSocket优化配置
    engineio_logger: bool = False  # 禁用Engine.IO日志以减少干扰
    manage_session: bool = True  # 启用会话管理
    http_compression: bool = True  # 启用HTTP压缩
    compression_threshold: int = 1024  # 压缩阈值
    cookie: str = None  # 禁用cookie以简化跨域
    cors_credentials: bool = False  # 禁用CORS凭据以简化跨域

# 2. 后端应用WebSocket配置更新
nano /root/camel_ai/multi_agent_meeting/backend/app_new.py

# 确保SocketIO实例创建时包含优化参数：
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

# 3. 前端WebSocket配置优化
nano /root/camel_ai/multi_agent_meeting/frontend/app.js

# 修改WebSocket连接配置（已在前端代码中实现）：
# 前端已包含完整的WebSocket优化配置，包括：
# - 传输协议优先级和降级机制
# - 增强的重连策略
# - 详细的错误处理和日志记录
# - 自动降级到HTTP长轮询
# - 协议升级监控

# 4. Nginx WebSocket代理配置优化
nano /etc/nginx/sites-available/multi-agent-meeting

# 替换WebSocket代理配置为：
location /socket.io/ {
    proxy_pass http://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 增加超时配置
    proxy_connect_timeout 75s;
    proxy_send_timeout 75s;
    proxy_read_timeout 75s;
    
    # 增加缓冲区配置
    proxy_buffering off;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    
    # WebSocket特定优化
    proxy_set_header Sec-WebSocket-Extensions $http_sec_websocket_extensions;
    proxy_set_header Sec-WebSocket-Key $http_sec_websocket_key;
    proxy_set_header Sec-WebSocket-Version $http_sec_websocket_version;
    
    # 启用支持WebSocket的HTTP/1.1
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    
    # 连接池优化
    proxy_socket_keepalive on;
    proxy_keepalive_timeout 75s;
    proxy_keepalive_requests 1000;
}

# 在nginx.conf的http块中添加：
http {
    # ... 其他配置 ...
    
    # WebSocket支持映射
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }
    
    # 增加客户端超时
    client_body_timeout 75s;
    client_header_timeout 75s;
    
    # 增加代理超时
    proxy_connect_timeout 75s;
    proxy_send_timeout 75s;
    proxy_read_timeout 75s;
    
    # 启用gzip压缩（对WebSocket数据传输有帮助）
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/json
        application/xml+rss;
}

# 5. 系统级优化
# 增加系统文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数（在/etc/sysctl.conf中添加）：
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3

# 应用内核参数
sysctl -p

# 6. 重启服务
systemctl restart nginx
systemctl restart multi-agent-meeting
```

**修复后的效果**:
- ✅ **Invalid frame header错误** - 通过优化WebSocket协议处理和代理配置得到解决
- ✅ **连接稳定性** - 增强的重连机制和降级策略确保连接稳定
- ✅ **协议兼容性** - 支持WebSocket和HTTP长轮询的无缝切换
- ✅ **性能优化** - 启用压缩、连接池和超时优化提升性能
- ✅ **系统资源** - 优化文件描述符和内核参数提升系统承载能力

### 5. 生产环境性能优化
**解决方案**:
```bash
# 压缩前端资源
apt install -y gzip

# 配置Nginx启用压缩
nano /etc/nginx/nginx.conf

# 在http块中添加或确保以下配置存在：
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/javascript
    application/xml+rss
    application/json;

# 设置浏览器缓存
nano /etc/nginx/sites-available/multi-agent-meeting

# 在server块中添加：
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 6. 生产环境安全加固
**解决方案**:
```bash
# 隐藏Nginx版本
nano /etc/nginx/nginx.conf

# 在http块中添加：
server_tokens off;

# 添加安全响应头
nano /etc/nginx/sites-available/multi-agent-meeting

# 在server块中添加：
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# 配置防火墙限制访问
ufw allow from your_trusted_ip to any port 22
ufw allow from any to any port 80
ufw allow from any to any port 443
ufw deny from any to any port 5000  # 禁止直接访问后端端口
```

### 7. 生产环境监控和日志
**解决方案**:
```bash
# 安装监控工具
apt install -y htop iotop nethogs

# 配置日志轮转
nano /etc/logrotate.d/multi-agent-meeting

# 添加以下内容：
/root/camel_ai/multi_agent_meeting/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload multi-agent-meeting
    endscript
}

# 设置系统资源监控
echo "* * * * * root /usr/bin/df -h >> /var/log/system_monitor.log" >> /etc/crontab
echo "* * * * * root /usr/bin/free -h >> /var/log/system_monitor.log" >> /etc/crontab
```

---

**部署完成后，您可以通过 http://111.229.108.199 访问您的多智能体会议系统！**

祝您使用愉快！🎉

---

**部署完成后，您可以通过 http://111.229.108.199 访问您的多智能体会议系统！**

祝您使用愉快！🎉
