#!/bin/bash
# 多智能体会议系统自动安装脚本
# 适用于Ubuntu/Debian系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "无法检测操作系统类型"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    log_success "系统包更新完成"
}

# 安装基础软件
install_dependencies() {
    log_info "安装基础软件包..."
    sudo apt install -y python3 python3-pip python3-venv nginx git curl wget unzip
    log_success "基础软件包安装完成"
}

# 创建项目目录
create_project_dir() {
    log_info "创建项目目录..."
    sudo mkdir -p /opt/multi_agent_meeting
    sudo chown $USER:$USER /opt/multi_agent_meeting
    log_success "项目目录创建完成: /opt/multi_agent_meeting"
}

# 设置Python虚拟环境
setup_python_env() {
    log_info "设置Python虚拟环境..."
    cd /opt/multi_agent_meeting
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    log_success "Python虚拟环境设置完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖包..."
    cd /opt/multi_agent_meeting
    source venv/bin/activate
    pip install -r backend/requirements.txt
    log_success "Python依赖包安装完成"
}

# 创建环境配置文件
create_env_config() {
    log_info "创建环境配置文件..."
    cat > /opt/multi_agent_meeting/.env << EOF
# Flask配置
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_SECRET_KEY=$(openssl rand -hex 32)

# API配置
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
EOF
    log_success "环境配置文件创建完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    sudo tee /etc/systemd/system/multi-agent-meeting.service > /dev/null << EOF
[Unit]
Description=Multi Agent Meeting System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/multi_agent_meeting
Environment=PATH=/opt/multi_agent_meeting/venv/bin
ExecStart=/opt/multi_agent_meeting/venv/bin/python backend/app_new.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    log_success "systemd服务创建完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx反向代理..."
    
    # 获取服务器IP或域名
    read -p "请输入您的域名或IP地址 (默认: localhost): " SERVER_NAME
    SERVER_NAME=${SERVER_NAME:-localhost}
    
    sudo tee /etc/nginx/sites-available/multi-agent-meeting > /dev/null << EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    # 前端静态文件
    location / {
        root /opt/multi_agent_meeting/frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket代理
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/multi-agent-meeting /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    sudo nginx -t
    log_success "Nginx配置完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    log_success "防火墙配置完成"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    sudo chown -R www-data:www-data /opt/multi_agent_meeting
    sudo chmod -R 755 /opt/multi_agent_meeting
    sudo chmod +x /opt/multi_agent_meeting/backend/app_new.py
    log_success "文件权限设置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    # 启动并启用服务
    sudo systemctl enable multi-agent-meeting
    sudo systemctl start multi-agent-meeting
    
    # 启动Nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if sudo systemctl is-active --quiet multi-agent-meeting; then
        log_success "多智能体会议服务启动成功"
    else
        log_error "多智能体会议服务启动失败"
        sudo systemctl status multi-agent-meeting
        exit 1
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        log_success "Nginx服务启动成功"
    else
        log_error "Nginx服务启动失败"
        sudo systemctl status nginx
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    if curl -s http://localhost:5000/api/health > /dev/null; then
        log_success "后端API健康检查通过"
    else
        log_warning "后端API健康检查失败，请检查服务状态"
    fi
    
    # 检查Nginx
    if curl -s http://localhost > /dev/null; then
        log_success "Nginx服务正常"
    else
        log_warning "Nginx服务异常，请检查配置"
    fi
}

# 显示完成信息
show_completion_info() {
    echo ""
    echo "=========================================="
    log_success "安装完成！"
    echo "=========================================="
    echo ""
    echo "服务信息："
    echo "  前端地址: http://$SERVER_NAME"
    echo "  后端API: http://$SERVER_NAME/api/"
    echo "  健康检查: http://$SERVER_NAME/api/health"
    echo ""
    echo "管理命令："
    echo "  启动服务: sudo systemctl start multi-agent-meeting"
    echo "  停止服务: sudo systemctl stop multi-agent-meeting"
    echo "  重启服务: sudo systemctl restart multi-agent-meeting"
    echo "  查看状态: sudo systemctl status multi-agent-meeting"
    echo "  查看日志: sudo journalctl -u multi-agent-meeting -f"
    echo ""
    echo "重要提醒："
    echo "  1. 请编辑 /opt/multi_agent_meeting/backend/config.py 配置您的API密钥"
    echo "  2. 如需HTTPS，请运行: sudo certbot --nginx -d $SERVER_NAME"
    echo "  3. 项目文件位置: /opt/multi_agent_meeting"
    echo ""
}

# 主函数
main() {
    echo "=========================================="
    echo "多智能体会议系统自动安装脚本"
    echo "=========================================="
    echo ""
    
    check_root
    check_system
    
    read -p "是否继续安装？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi
    
    update_system
    install_dependencies
    create_project_dir
    
    log_warning "请确保您已经将项目文件上传到 /opt/multi_agent_meeting 目录"
    read -p "项目文件已上传完成？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "请先上传项目文件后再运行此脚本"
        exit 1
    fi
    
    setup_python_env
    install_python_deps
    create_env_config
    create_systemd_service
    configure_nginx
    configure_firewall
    set_permissions
    start_services
    health_check
    show_completion_info
}

# 运行主函数
main "$@"
