# 多智能体会议系统 - Linux云服务器部署指南

## 📋 部署前准备

### 1. 服务器要求
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

### 第四步：创建Python虚拟环境
```bash
cd /opt/camel_ai

# 删除可能存在的Windows虚拟环境（如果有）
rm -rf venv

# 创建新的Linux虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 验证Python版本
python --version
# 应该显示: Python 3.x.x
```

### 第五步：安装项目依赖
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 安装后端依赖
pip install -r multi_agent_meeting/backend/requirements.txt

# 验证依赖安装
pip list
# 应该包含: flask, flask-cors, flask-socketio, camel-ai, openai等
```

### Git部署的优势
- ✅ **版本控制**: 使用Git管理代码版本，便于回滚和更新
- ✅ **环境一致性**: 在服务器上重新创建虚拟环境，确保兼容性
- ✅ **自动化部署**: 支持CI/CD自动化部署流程
- ✅ **代码同步**: 开发和生产环境代码完全同步
- ✅ **分支管理**: 支持多环境分支管理（开发、测试、生产）

### 第六步：配置环境变量
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

# 其他配置保持默认即可
```

### 第七步：验证API密钥配置
```bash
# 检查API密钥配置（已预配置）
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"
```

**说明：**
- 项目已预配置了4个有效的API密钥，无需额外配置
- 系统会为4个智能体（CEO、Agent1、Agent2、Agent3）分配不同的API密钥
- API密钥已包含在项目中，确保系统可以正常运行

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

- [ ] 服务器基础环境安装完成（Python 3.8+）
- [ ] Git仓库克隆成功
- [ ] Python虚拟环境创建成功
- [ ] 项目依赖包安装完成
- [ ] 环境变量配置完成
- [ ] API密钥配置正确
- [ ] systemd服务创建并启动
- [ ] Nginx反向代理配置完成
- [ ] 防火墙规则配置完成
- [ ] 服务健康检查通过
- [ ] 前端页面可以正常访问
- [ ] WebSocket连接正常
- [ ] 智能体会议功能正常

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
├── venv/                   # Python虚拟环境（自动创建）
│   ├── bin/python         # Python解释器
│   ├── bin/pip            # 包管理器
│   └── lib/python3.x/     # 依赖包
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
- **Python环境**: `/opt/camel_ai/venv/` - 自动创建的虚拟环境

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
pip install -r multi_agent_meeting/backend/requirements.txt  # 更新依赖
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

# 2. 运行快速部署脚本
chmod +x multi_agent_meeting/deploy/quick-deploy.sh
./multi_agent_meeting/deploy/quick-deploy.sh

# 3. 验证API密钥配置（已预配置）
cat multi_agent_meeting/backend/config.py | grep -A 6 "api_keys"

# 4. 重启服务
sudo systemctl restart multi-agent-meeting
```

感谢使用多智能体会议系统！如有问题，请参考故障排除部分或联系技术支持。
测试文件
