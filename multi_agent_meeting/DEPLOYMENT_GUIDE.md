# 多智能体会议系统 - Linux云服务器部署指南

## 📋 部署前准备

### 1. Git仓库配置说明
**重要更新**: 项目已优化.gitignore文件，确保所有必要的依赖脚本、环境配置文件和预配置的虚拟环境都能正常上传到Git仓库。

**包含的关键文件**:
- ✅ **部署脚本**: `multi_agent_meeting/deploy/` 目录下的所有部署脚本
- ✅ **环境配置示例**: `multi_agent_meeting/backend/env.example` 
- ✅ **依赖文件**: `multi_agent_meeting/backend/requirements.txt`
- ✅ **服务配置**: `multi_agent_meeting/deploy/multi-agent-meeting.service`
- ✅ **Nginx配置**: `multi_agent_meeting/deploy/nginx.conf`
- ✅ **预配置虚拟环境**: `venv/` 目录（包含所有已安装的依赖包）
- ✅ **CAMEL-AI模块**: `venv/Lib/site-packages/camel/` 目录（包含camel-ai==0.2.1包）

**忽略的文件**:
- ❌ **实际环境变量**: `.env` 文件（包含敏感信息）
- ❌ **其他环境目录**: `env/`, `ENV/`, `.venv/` 等目录
- ❌ **日志文件**: `logs/` 目录
- ❌ **临时文件**: `temp/` 目录
- ❌ **本地开发文件**: 本地开发过程中的临时文件和缓存

### 2. 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **内存**: 最少2GB，推荐4GB+
- **存储**: 最少10GB可用空间
- **网络**: 公网IP，开放80、443、5000端口
- **Python**: 3.8+ （推荐3.11+）

### 2. 服务器信息
- **服务器IP**: 8.134.128.123
- **操作系统**: CentOS
- **登录账号**: root
- **访问方式**: 通过IP地址直接访问
- **无需配置域名**

### 3. 系统访问
- 系统无需登录即可直接使用
- 无需配置任何第三方登录服务
- 直接通过IP地址访问系统

### 4. 文件上传说明
由于.gitignore已优化，您可以通过以下方式确保所有必要文件都能正确上传：

**方法一：Git推送（推荐）**
```bash
# 确保所有文件都已添加到Git
git add .
git status  # 检查文件状态
git commit -m "更新部署文件和配置"
git push origin master
```

**方法二：手动上传**
如果某些文件未被Git跟踪，可以手动上传：
```bash
# 在服务器上
cd /opt/camel_ai
git pull origin master

# 检查关键文件是否存在
ls -la multi_agent_meeting/deploy/
ls -la multi_agent_meeting/backend/env.example
ls -la multi_agent_meeting/backend/requirements.txt
```

**关键文件清单**:
```
multi_agent_meeting/deploy/
├── quick-deploy.sh      # 快速部署脚本
├── install.sh           # 自动安装脚本
├── deploy.sh            # 部署脚本
├── upload.sh            # 上传脚本
├── multi-agent-meeting.service  # systemd服务配置
├── nginx.conf           # Nginx配置
└── verify-config.sh     # 配置验证脚本

multi_agent_meeting/backend/
├── env.example          # 环境变量配置示例
├── requirements.txt     # Python依赖包列表
└── config.py            # 配置文件（包含API密钥）

venv/                    # 预配置的Python虚拟环境
├── bin/                 # 可执行文件目录 (Linux)
│   ├── python           # Python解释器
│   ├── pip              # 包管理器
│   └── activate         # 激活脚本
├── Scripts/             # 可执行文件目录 (Windows)
│   ├── python.exe       # Python解释器
│   ├── pip.exe          # 包管理器
│   └── activate.bat     # 激活脚本
└── lib/                 # 库文件目录
    └── python3.x/       # Python库文件
        └── site-packages/ # 已安装的依赖包
            ├── camel/           # CAMEL-AI模块
            ├── camel_ai-0.2.1.dist-info/ # CAMEL-AI包信息
            ├── flask/          # Flask框架
            ├── flask_cors/     # 跨域支持
            ├── flask_socketio/  # WebSocket支持
            ├── openai/         # OpenAI接口
            └── ...             # 其他依赖包
```

## 🚀 Git部署步骤（推荐）

### 方式一：快速部署脚本
```bash
# 1. 克隆项目到服务器
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/yinjianhui/camel_ai.git camel_ai
sudo chown -R $USER:$USER camel_ai

# 2. 进入项目目录
cd camel_ai

# 3. 给脚本添加执行权限
chmod +x multi_agent_meeting/deploy/quick-deploy.sh

# 4. 执行快速部署脚本
./multi_agent_meeting/deploy/quick-deploy.sh
```

### 方式二：手动Git部署
```bash
# 1. 创建项目目录并克隆代码
sudo mkdir -p /opt/camel_ai
sudo chown $USER:$USER /opt/camel_ai
cd /opt/camel_ai
git clone https://github.com/yinjianhui/camel_ai.git .

# 2. 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install -r multi_agent_meeting/backend/requirements.txt

# 4. 配置环境变量
cp multi_agent_meeting/backend/env.example multi_agent_meeting/backend/.env
# 编辑 multi_agent_meeting/backend/.env 文件，配置API密钥等

# 5. 创建systemd服务
sudo cp multi_agent_meeting/deploy/multi-agent-meeting.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable multi-agent-meeting
sudo systemctl start multi-agent-meeting

# 6. 配置Nginx
sudo cp multi_agent_meeting/deploy/nginx.conf /etc/nginx/sites-available/multi-agent-meeting
sudo ln -s /etc/nginx/sites-available/multi-agent-meeting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📋 详细部署步骤

### 第一步：连接服务器
```bash
# 使用SSH连接服务器
ssh root@your-server-ip
# 或使用密钥
ssh -i your-key.pem root@your-server-ip
```

### 第二步：更新系统并安装基础软件
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git curl wget

# CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip nginx git curl wget
```

### 第三步：克隆项目代码
```bash
# 创建项目目录
sudo mkdir -p /opt/camel_ai
sudo chown $USER:$USER /opt/camel_ai
cd /opt/camel_ai

# 克隆项目代码
git clone https://github.com/yinjianhui/camel_ai.git .

# 检查项目结构
ls -la
# 应该看到: Legion, multi_agent_meeting, venv, .gitignore 等目录
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
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r multi_agent_meeting/backend/requirements.txt
    fi
else
    echo "❌ 未发现预配置虚拟环境，将创建新的"
    python3 -m venv venv
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

# 预期应该包含以下包:
# flask==2.2.5
# flask-cors==4.0.0
# flask-socketio==5.3.5
# camel-ai==0.2.1 (包含CAMEL-AI多智能体框架)
# python-socketio==5.10.0
# openai==1.3.0
# python-dotenv==1.0.0

# CAMEL-AI模块包含的核心组件:
# - camel.agents.ChatAgent (智能体类)
# - camel.messages.BaseMessage (消息类)
# - camel.models.ModelFactory (模型工厂)
# - camel.types.ModelPlatformType (模型平台类型)
# - camel.types.RoleType (角色类型)
```

### Git部署的优势
- ✅ **版本控制**: 使用Git管理代码版本，便于回滚和更新
- ✅ **环境一致性**: 在服务器上重新创建虚拟环境，确保兼容性
- ✅ **自动化部署**: 支持CI/CD自动化部署流程
- ✅ **代码同步**: 开发和生产环境代码完全同步
- ✅ **分支管理**: 支持多环境分支管理（开发、测试、生产）

### 第六步：验证部署文件完整性
```bash
# 检查所有关键文件是否存在
cd /opt/camel_ai

echo "检查部署脚本..."
ls -la multi_agent_meeting/deploy/
echo "检查环境配置文件..."
ls -la multi_agent_meeting/backend/env.example
echo "检查依赖文件..."
ls -la multi_agent_meeting/backend/requirements.txt
echo "检查服务配置..."
ls -la multi_agent_meeting/deploy/multi-agent-meeting.service
echo "检查预配置虚拟环境..."
ls -la venv/
echo "检查虚拟环境中的Python解释器..."
ls -la venv/bin/python
echo "检查虚拟环境中的pip..."
ls -la venv/bin/pip
```

**预期输出应该包含以下文件**:
```
multi_agent_meeting/deploy/:
- quick-deploy.sh
- install.sh
- deploy.sh
- upload.sh
- multi-agent-meeting.service
- nginx.conf
- verify-config.sh

multi_agent_meeting/backend/:
- env.example
- requirements.txt
- config.py

venv/:
- bin/ (Linux) 或 Scripts/ (Windows)
  - python/python.exe
  - pip/pip.exe
  - activate/activate.bat
  - ...
- lib/
  - python3.x/
    - site-packages/
      - flask/
      - flask_cors/
      - flask_socketio/
      - camel/              # CAMEL-AI模块
      - camel_ai-0.2.1.dist-info/
      - openai/
      - ...
```

### 第七步：配置环境变量
```bash
# 复制环境配置示例文件
cp multi_agent_meeting/backend/env.example multi_agent_meeting/backend/.env

# 编辑配置文件
nano multi_agent_meeting/backend/.env
```

**重要配置项说明：**
```bash
# Flask配置
FLASK_SECRET_KEY=your_very_secure_secret_key_here
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

# 微信登录配置（可选）
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_ENABLE_LOGIN=False  # 默认关闭
```

### 第八步：验证API密钥配置
```bash
# 检查API密钥配置（已预配置）
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"
```

**说明：**
- 项目已预配置了4个有效的API密钥，无需额外配置
- 系统会为4个智能体（CEO、Agent1、Agent2、Agent3）分配不同的API密钥
- API密钥已包含在项目中，确保系统可以正常运行
- 所有配置文件都已通过Git仓库正确上传

### 第八步：创建systemd服务
```bash
# 复制服务配置文件
sudo cp multi_agent_meeting/deploy/multi-agent-meeting.service /etc/systemd/system/

# 或者手动创建服务文件
sudo nano /etc/systemd/system/multi-agent-meeting.service
```

添加以下内容：
```ini
[Unit]
Description=Multi Agent Meeting System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
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

**注意：** 服务配置使用新创建的Linux虚拟环境，确保路径正确。

### 第九步：配置Nginx反向代理
```bash
# 复制Nginx配置文件
sudo cp multi_agent_meeting/deploy/nginx.conf /etc/nginx/sites-available/multi-agent-meeting

# 或者手动创建配置文件
sudo nano /etc/nginx/sites-available/multi-agent-meeting
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name 8.134.128.123;  # 服务器IP地址

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

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/multi-agent-meeting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 第十步：启动服务
```bash
# 设置目录权限
sudo chown -R www-data:www-data /opt/multi_agent_meeting
sudo chmod -R 755 /opt/multi_agent_meeting

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable multi-agent-meeting
sudo systemctl start multi-agent-meeting

# 检查服务状态
sudo systemctl status multi-agent-meeting
```

### 第十一步：配置防火墙
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🔧 服务管理命令

### 启动/停止/重启服务
```bash
sudo systemctl start multi-agent-meeting
sudo systemctl stop multi-agent-meeting
sudo systemctl restart multi-agent-meeting
sudo systemctl status multi-agent-meeting
```

### 查看日志
```bash
# 查看服务日志
sudo journalctl -u multi-agent-meeting -f

# 查看应用日志
tail -f /opt/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log
```

### 更新代码
```bash
cd /opt/camel_ai

# 拉取最新代码
git pull origin master

# 更新依赖（如果有新的依赖包）
source venv/bin/activate
pip install -r multi_agent_meeting/backend/requirements.txt

# 重启服务
sudo systemctl restart multi-agent-meeting

# 检查服务状态
sudo systemctl status multi-agent-meeting
```

### 使用部署脚本更新
```bash
# 使用项目提供的部署脚本
cd /opt/camel_ai
./multi_agent_meeting/deploy/deploy.sh deploy
```

## 🔒 HTTPS配置（可选）

### 使用Let's Encrypt免费SSL证书
```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐛 故障排除

### 常见问题及解决方案

1. **服务启动失败**
```bash
# 检查日志
sudo journalctl -u multi-agent-meeting -n 50
# 检查项目自带的Python环境
ls -la /opt/multi_agent_meeting/venv/bin/python
# 检查虚拟环境
source /opt/multi_agent_meeting/venv/bin/activate
python --version
# 应该显示: Python 3.11.9
```

2. **端口被占用**
```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000
# 或
sudo lsof -i :5000
```

3. **权限问题**
```bash
# 修复权限
sudo chown -R www-data:www-data /opt/multi_agent_meeting
sudo chmod -R 755 /opt/multi_agent_meeting
```

4. **API密钥问题**
```bash
# 检查配置文件
cat /opt/multi_agent_meeting/backend/config.py | grep api_keys
```

5. **Nginx配置问题**
```bash
# 测试Nginx配置
sudo nginx -t
# 重新加载配置
sudo systemctl reload nginx
```

## 📊 监控和维护

### 健康检查
```bash
# 检查服务健康状态
curl http://localhost:5000/api/health
curl http://your-domain.com/api/health
```

### 性能监控
```bash
# 查看系统资源使用
htop
# 查看磁盘使用
df -h
# 查看内存使用
free -h
```

### 日志轮转
```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/multi-agent-meeting
```

添加以下内容：
```
/opt/multi_agent_meeting/backend/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload multi-agent-meeting
    endscript
}
```


## 🎯 部署完成检查清单

### Git和文件检查
- [ ] Git仓库克隆成功
- [ ] 部署脚本文件完整（quick-deploy.sh, install.sh, deploy.sh等）
- [ ] 环境配置示例文件存在（env.example）
- [ ] 依赖文件存在（requirements.txt）
- [ ] 服务配置文件存在（multi-agent-meeting.service）
- [ ] Nginx配置文件存在（nginx.conf）
- [ ] 预配置虚拟环境存在（venv/目录）
- [ ] 虚拟环境文件完整（bin/python, bin/pip等）
- [ ] 虚拟环境中依赖包已安装

### 环境和服务检查
- [ ] 服务器基础环境安装完成（Python 3.8+）
- [ ] Python虚拟环境创建成功
- [ ] 项目依赖包安装完成
- [ ] 环境变量配置完成（.env文件）
- [ ] API密钥配置正确
- [ ] systemd服务创建并启动
- [ ] Nginx反向代理配置完成
- [ ] 防火墙规则配置完成

### 功能验证
- [ ] 服务健康检查通过
- [ ] 前端页面可以正常访问
- [ ] WebSocket连接正常
- [ ] 智能体会议功能正常
- [ ] 日志文件正常生成

## 📞 技术支持

如果遇到问题，请检查：
1. 服务器日志：`sudo journalctl -u multi-agent-meeting -f`
2. 应用日志：`tail -f /opt/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log`
3. Nginx日志：`sudo tail -f /var/log/nginx/error.log`
4. 服务状态：`sudo systemctl status multi-agent-meeting`
5. Git状态：`cd /opt/camel_ai && git status`

部署完成后，您可以通过 `http://8.134.128.123` 访问您的多智能体会议系统！

## 🔄 Git部署的优势

### 版本控制
- **代码追踪**: 每次部署都有明确的版本记录
- **回滚能力**: 出现问题时可以快速回滚到稳定版本
- **分支管理**: 支持开发、测试、生产环境分离

### 自动化部署
- **一键更新**: 使用 `git pull` 即可更新代码
- **依赖管理**: 自动检测并安装新的依赖包
- **服务重启**: 部署脚本自动重启相关服务

### 团队协作
- **代码同步**: 团队成员可以轻松同步最新代码
- **冲突解决**: Git提供完善的冲突解决机制
- **代码审查**: 支持Pull Request代码审查流程

### 文件管理优化
- **完整部署包**: 所有必要的部署脚本和配置文件都已包含在Git仓库中
- **环境一致性**: 通过env.example文件确保环境配置的一致性
- **依赖追踪**: requirements.txt文件确保所有依赖包都能正确安装
- **配置管理**: 服务配置和Nginx配置都纳入版本控制
- **预配置环境**: venv目录包含完整的Python虚拟环境，无需重新安装依赖包

## 🎯 部署总结

### Git部署的优势
本部署方案使用Git进行代码管理，具有以下优势：

1. **版本控制** - 完整的代码版本历史，支持回滚和分支管理
2. **环境一致性** - 在服务器上重新创建虚拟环境，确保兼容性
3. **快速部署** - 使用Git克隆和自动化脚本，简化部署流程
4. **依赖管理** - 自动安装和更新依赖包，避免版本冲突
5. **团队协作** - 支持多人协作开发，代码同步简单
6. **维护简单** - 使用标准化的部署流程，问题排查更容易

### 部署文件结构
```
/opt/camel_ai/
├── .git/                   # Git版本控制
├── venv/                   # Python虚拟环境（预配置，包含所有依赖包）
│   ├── bin/               # 可执行文件目录
│   │   ├── python         # Python解释器
│   │   ├── pip            # 包管理器
│   │   ├── activate       # 激活脚本
│   │   └── ...            # 其他工具
│   └── lib/               # 库文件目录
│       └── python3.x/     # Python库文件
│           └── site-packages/ # 已安装的依赖包
│               ├── flask/
│               ├── flask_cors/
│               ├── flask_socketio/
│               ├── camel_ai/
│               ├── openai/
│               └── ...
├── multi_agent_meeting/    # 项目代码
│   ├── backend/           # 后端代码
│   │   ├── app_new.py     # 主应用文件
│   │   ├── config.py      # 配置文件
│   │   ├── .env           # 环境变量（需配置）
│   │   └── requirements.txt # 依赖列表
│   ├── frontend/          # 前端代码
│   └── deploy/            # 部署脚本
│       ├── quick-deploy.sh # 快速部署脚本
│       ├── nginx.conf     # Nginx配置
│       └── multi-agent-meeting.service # systemd服务
├── Legion/                # 其他项目文件
└── README.md              # 项目说明
```

### 关键配置文件
- **环境变量**: `/opt/camel_ai/multi_agent_meeting/backend/.env` - 配置API密钥等
- **服务配置**: `/etc/systemd/system/multi-agent-meeting.service` - 系统服务
- **Nginx配置**: `/etc/nginx/sites-available/multi-agent-meeting` - 反向代理
- **Python环境**: `/opt/camel_ai/venv/` - 预配置的虚拟环境，包含所有依赖包

### 常用管理命令
```bash
# 服务管理
sudo systemctl start multi-agent-meeting    # 启动服务
sudo systemctl stop multi-agent-meeting     # 停止服务
sudo systemctl restart multi-agent-meeting  # 重启服务
sudo systemctl status multi-agent-meeting   # 查看状态

# 代码更新
cd /opt/camel_ai
git pull origin master                      # 拉取最新代码
source venv/bin/activate                    # 激活虚拟环境

# 如果venv目录有更新，直接使用预配置的环境
# 如果requirements.txt有更新，可选择安装新依赖
pip install -r multi_agent_meeting/backend/requirements.txt --upgrade  # 更新依赖

sudo systemctl restart multi-agent-meeting  # 重启服务

# 日志查看
sudo journalctl -u multi-agent-meeting -f   # 实时日志
tail -f /opt/camel_ai/multi_agent_meeting/backend/logs/meeting_*.log  # 应用日志

# 健康检查
curl http://localhost:5000/api/health       # 本地检查
curl http://your-domain.com/api/health      # 远程检查

# Git管理
git status                                  # 查看状态
git log --oneline -10                       # 查看最近提交
git checkout <commit-hash>                  # 回滚到指定版本
```

## 🚀 快速开始

如果您想快速部署，只需执行以下命令：

```bash
# 1. 克隆项目
sudo mkdir -p /opt/camel_ai
sudo chown $USER:$USER /opt/camel_ai
cd /opt/camel_ai
git clone https://github.com/yinjianhui/camel_ai.git .

# 2. 验证文件完整性
ls -la multi_agent_meeting/deploy/
ls -la multi_agent_meeting/backend/env.example
ls -la multi_agent_meeting/backend/requirements.txt

# 3. 运行快速部署脚本
chmod +x multi_agent_meeting/deploy/quick-deploy.sh
./multi_agent_meeting/deploy/quick-deploy.sh

# 4. 验证API密钥配置（已预配置）
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"

# 5. 重启服务
sudo systemctl restart multi-agent-meeting
```

## 📝 文件管理说明

### .gitignore优化说明
项目已优化.gitignore文件，确保：
- ✅ **部署脚本**: 所有deploy/目录下的脚本都能上传
- ✅ **环境配置示例**: env.example文件能上传，但.env文件被忽略
- ✅ **依赖文件**: requirements.txt文件能上传
- ✅ **服务配置**: systemd和nginx配置文件能上传
- ✅ **预配置虚拟环境**: venv目录能上传，包含所有已安装的依赖包
- ✅ **CAMEL-AI模块**: camel-ai==0.2.1包及其所有组件都能上传
- ❌ **敏感信息**: 实际的.env文件和包含密钥的文件被忽略
- ❌ **其他环境目录**: env/, ENV/, .venv/等其他环境目录被忽略
- ❌ **临时文件**: 日志、缓存等被忽略

### CAMEL-AI模块说明
项目依赖的CAMEL-AI模块（camel-ai==0.2.1）是一个多智能体框架，包含以下核心组件：
- **camel.agents.ChatAgent**: 聊天智能体类，用于创建和管理AI智能体
- **camel.messages.BaseMessage**: 基础消息类，处理智能体间的通信
- **camel.models.ModelFactory**: 模型工厂，创建各种AI模型实例
- **camel.types.ModelPlatformType**: 模型平台类型定义
- **camel.types.RoleType**: 角色类型枚举

这些组件都已预安装在venv目录中，无需在服务器上重新安装。

### 新增文件处理
如果您添加了新的部署脚本或配置文件，请确保：
1. 将文件添加到Git仓库：`git add <filename>`
2. 提交更改：`git commit -m "添加新文件"`
3. 推送到远程仓库：`git push origin master`

### 虚拟环境管理
- **预配置环境**: venv目录现在包含完整的Python虚拟环境，所有依赖包已预安装
- **CAMEL-AI模块**: 包含完整的camel-ai==0.2.1包，支持多智能体对话功能
- **环境更新**: 如果需要更新依赖包，先在本地更新venv目录，然后提交到Git仓库
- **环境验证**: 部署时会自动验证虚拟环境的完整性和CAMEL-AI模块组件
- **跨平台兼容**: 虚拟环境在Linux服务器上直接使用，无需重新创建

**CAMEL-AI模块验证**:
```bash
# 在服务器上验证CAMEL-AI模块
source venv/bin/activate
python -c "from camel.agents import ChatAgent; from camel.messages import BaseMessage; print('CAMEL-AI模块验证成功')"
```

**更新虚拟环境的步骤**:
```bash
# 1. 激活现有虚拟环境
source venv/bin/activate

# 2. 更新依赖包
pip install -r multi_agent_meeting/backend/requirements.txt --upgrade

# 3. 测试环境
python -c "import flask, flask_cors, flask_socketio, camel_ai, openai"

# 4. 提交更新到Git
git add venv/
git commit -m "更新虚拟环境依赖包"
git push origin master
```

### 环境配置管理
- **开发环境**: 使用.env.local（本地开发）
- **测试环境**: 使用.env.test（测试服务器）
- **生产环境**: 使用.env.production（生产服务器）
- **配置模板**: env.example作为所有环境的配置模板

感谢使用多智能体会议系统！如有问题，请参考故障排除部分或联系技术支持。
测试文件
