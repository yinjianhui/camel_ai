# 多智能体会议系统 - 手动部署指南

## 📋 部署信息

### 服务器信息
- **服务器IP**: 111.229.108.199
- **登录账号**: root
- **操作系统**: Linux (推荐Ubuntu 20.04+或CentOS 7+)
- **Python版本要求**: 3.11
- **访问方式**: 公网IP直接访问

### 项目信息
- **项目地址**: https://github.com/yinjianhui/camel_ai.git
- **项目名称**: camel_ai
- **主要组件**: 多智能体会议系统 (multi_agent_meeting)
- **后端端口**: 5000
- **前端端口**: 80 (通过Nginx代理)

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
```

### 第三步：创建项目目录并克隆代码

```bash
# 创建项目目录
mkdir -p /opt/camel_ai
cd /opt/camel_ai

# 克隆项目代码
git clone https://github.com/yinjianhui/camel_ai.git .

# 检查项目结构
ls -la
```

**预期输出应该包含以下目录和文件：**
```
drwxr-xr-x  4 root root    4096 Oct  7 13:00 Legion
drwxr-xr-x  4 root root    4096 Oct  7 13:00 multi_agent_meeting
drwxr-xr-x  2 root root    4096 Oct  7 13:00 venv
-rw-r--r--  1 root root    1234 Oct  7 13:00 .gitignore
-rw-r--r--  1 root root    5678 Oct  7 13:00 deploy_to_server.ps1
```

### 第四步：验证预配置虚拟环境

```bash
cd /opt/camel_ai

# 检查venv目录是否存在
if [[ -d "venv" ]]; then
    echo "✅ 发现预配置的虚拟环境"
    
    # 检查虚拟环境的完整性
    if [[ -f "venv/bin/python" && -f "venv/bin/pip" ]]; then
        echo "✅ 虚拟环境文件完整"
        
        # 激活虚拟环境
        source venv/bin/activate
        
        # 验证Python版本
        python_version=$(python --version 2>&1)
        echo "✅ Python版本: $python_version"
        
        # 验证关键依赖包
        if python -c "import flask, flask_cors, flask_socketio, camel, camel_ai, openai" 2>/dev/null; then
            echo "✅ 所有关键依赖包已安装，包括CAMEL-AI模块"
            
            # 验证CAMEL-AI模块的核心组件
            if python -c "from camel.agents import ChatAgent; from camel.messages import BaseMessage; from camel.models import ModelFactory; from camel.types import ModelPlatformType" 2>/dev/null; then
                echo "✅ CAMEL-AI模块核心组件验证通过"
            else
                echo "⚠️  CAMEL-AI模块组件不完整，将重新安装"
                pip install -r multi_agent_meeting/backend/requirements.txt
            fi
        else
            echo "⚠️  部分依赖包缺失，将重新安装"
            pip install -r multi_agent_meeting/backend/requirements.txt
        fi
    else
        echo "❌ 虚拟环境文件不完整，将重新创建"
        rm -rf venv
        python3.11 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r multi_agent_meeting/backend/requirements.txt
    fi
else
    echo "❌ 未发现预配置虚拟环境，将创建新的"
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r multi_agent_meeting/backend/requirements.txt
fi
```

### 第五步：验证依赖包安装

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 验证依赖安装
pip list
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

### 第六步：配置环境变量

```bash
# 复制环境配置示例文件
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

### 第八步：创建必要的目录

```bash
# 创建日志、临时文件和会议保存目录
mkdir -p multi_agent_meeting/backend/logs
mkdir -p multi_agent_meeting/backend/temp
mkdir -p multi_agent_meeting/backend/saved_meetings

# 设置目录权限
chmod -R 755 multi_agent_meeting/backend/
chown -R root:root multi_agent_meeting/backend/
```

### 第九步：创建systemd服务

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
WorkingDirectory=/opt/camel_ai
Environment=PATH=/opt/camel_ai/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/camel_ai
ExecStart=/opt/camel_ai/venv/bin/python multi_agent_meeting/backend/app_new.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 第十步：配置Nginx反向代理

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
        root /opt/camel_ai/multi_agent_meeting/frontend;
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

### 第十一步：启用Nginx站点

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

### 第十二步：配置防火墙

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

### 第十三步：启动服务

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
   Active: active (running) since Mon 2024-10-07 13:00:00 CST; 5s ago
 Main PID: 12345 (python)
    Tasks: 2 (limit: 1137)
   Memory: 45.6M
   CGroup: /system.slice/multi-agent-meeting.service
           └─12345 /opt/camel_ai/venv/bin/python multi_agent_meeting/backend/app_new.py
```

### 第十四步：验证部署

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

### 第十五步：访问应用

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
tail -f /opt/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 更新代码
```bash
cd /opt/camel_ai

# 拉取最新代码
git pull origin master

# 激活虚拟环境
source venv/bin/activate

# 更新依赖（如果有新的依赖包）
pip install -r multi_agent_meeting/backend/requirements.txt

# 重启服务
systemctl restart multi-agent-meeting

# 检查服务状态
systemctl status multi-agent-meeting
```

## 🐛 故障排除

### 1. 服务启动失败

```bash
# 检查服务状态
systemctl status multi-agent-meeting

# 查看详细日志
journalctl -u multi-agent-meeting -n 50

# 检查Python环境
source venv/bin/activate
python --version
python -c "import flask, flask_cors, flask_socketio, camel_ai, openai"

# 手动启动测试
source venv/bin/activate
python multi_agent_meeting/backend/app_new.py
```

### 2. 端口被占用

```bash
# 检查端口占用
netstat -tlnp | grep :5000
netstat -tlnp | grep :80

# 终止占用进程
kill -9 <PID>
```

### 3. 权限问题

```bash
# 修复权限
chown -R root:root /opt/camel_ai
chmod -R 755 /opt/camel_ai
chmod -R 755 /opt/camel_ai/multi_agent_meeting/backend/
```

### 4. Nginx配置问题

```bash
# 测试Nginx配置
nginx -t

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 重新加载Nginx
systemctl reload nginx
```

### 5. API密钥问题

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
- [ ] Nginx安装成功 (nginx -v)
- [ ] Git安装成功 (git --version)

### 项目文件验证
- [ ] 项目克隆成功 (git clone)
- [ ] 项目目录结构完整 (ls -la)
- [ ] 预配置虚拟环境存在 (venv/目录)
- [ ] 虚拟环境文件完整 (venv/bin/python, venv/bin/pip)
- [ ] 依赖包安装成功 (pip list)
- [ ] 环境配置文件存在 (.env文件)
- [ ] API密钥配置正确 (config.py中的api_keys)

### 服务配置验证
- [ ] systemd服务创建成功 (multi-agent-meeting.service)
- [ ] Nginx配置创建成功 (sites-available/multi-agent-meeting)
- [ ] Nginx站点启用成功 (sites-enabled/multi-agent-meeting)
- [ ] 防火墙规则配置成功 (端口80, 5000开放)
- [ ] 目录权限设置正确 (chmod, chown)

### 服务启动验证
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

# 更新代码
cd /opt/camel_ai && git pull origin master && systemctl restart multi-agent-meeting
```

## 📞 技术支持

如果部署过程中遇到问题，请检查：
1. **服务日志**: `journalctl -u multi-agent-meeting -f`
2. **应用日志**: `tail -f /opt/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log`
3. **Nginx日志**: `tail -f /var/log/nginx/error.log`
4. **系统资源**: `htop`, `df -h`, `free -h`
5. **网络连接**: `netstat -tlnp`, `curl http://localhost:5000/api/health`

---

**部署完成后，您可以通过 http://111.229.108.199 访问您的多智能体会议系统！**

祝您使用愉快！🎉
