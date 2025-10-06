#!/bin/bash
# 多智能体会议系统快速部署脚本
# 支持Git部署和虚拟环境自动创建

set -e

echo "🚀 开始部署多智能体会议系统..."

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
        log_warning "建议不要使用root用户运行此脚本"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统要求
check_system() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        log_info "检测到操作系统: $NAME $VERSION"
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [[ $total_mem -lt 2048 ]]; then
        log_warning "系统内存不足2GB，可能影响性能"
    else
        log_success "内存检查通过: ${total_mem}MB"
    fi
    
    # 检查磁盘空间
    available_space=$(df / | awk 'NR==2{print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        log_warning "磁盘空间不足10GB"
    else
        log_success "磁盘空间检查通过"
    fi
}

# 安装基础软件
install_dependencies() {
    log_info "安装基础软件..."
    
    if command -v apt &> /dev/null; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv nginx git curl wget
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y python3 python3-pip nginx git curl wget
    else
        log_error "不支持的包管理器"
        exit 1
    fi
    
    log_success "基础软件安装完成"
}

# 克隆项目代码
clone_project() {
    log_info "克隆项目代码..."
    
    sudo mkdir -p /opt/camel_ai
    sudo chown $USER:$USER /opt/camel_ai
    cd /opt/camel_ai
    
    # 检查是否已经存在项目文件
    if [[ -d ".git" ]]; then
        log_info "项目已存在，更新代码..."
        git pull origin master
    else
        log_info "克隆项目代码..."
        git clone https://github.com/yinjianhui/camel_ai.git .
    fi
    
    log_success "项目代码准备完成"
}

# 创建Python虚拟环境
setup_python_env() {
    log_info "创建Python虚拟环境..."
    
    cd /opt/camel_ai
    
    # 删除可能存在的Windows虚拟环境
    if [[ -d "venv" ]]; then
        log_info "删除现有虚拟环境..."
        rm -rf venv
    fi
    
    # 创建新的虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 检查Python版本
    python_version=$(python --version 2>&1)
    log_success "Python环境创建完成: $python_version"
    
    # 安装依赖包
    log_info "安装项目依赖..."
    pip install -r multi_agent_meeting/backend/requirements.txt
    
    # 验证关键依赖包
    if python -c "import flask, flask_cors, flask_socketio" 2>/dev/null; then
        log_success "依赖包安装完成"
    else
        log_error "依赖包安装失败"
        exit 1
    fi
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [[ ! -f "/opt/camel_ai/multi_agent_meeting/backend/.env" ]]; then
        cp /opt/camel_ai/multi_agent_meeting/backend/env.example /opt/camel_ai/multi_agent_meeting/backend/.env
        log_warning "已创建环境配置文件，请编辑 /opt/camel_ai/multi_agent_meeting/backend/.env 配置API密钥"
    else
        log_success "环境配置文件已存在"
    fi
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    sudo tee /etc/systemd/system/multi-agent-meeting.service > /dev/null <<EOF
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
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable multi-agent-meeting
    
    log_success "systemd服务创建完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 获取服务器IP或域名
    read -p "请输入您的域名或IP地址 (直接回车使用IP): " server_name
    if [[ -z "$server_name" ]]; then
        server_name="_"
    fi
    
    sudo tee /etc/nginx/sites-available/multi-agent-meeting > /dev/null <<EOF
server {
    listen 80;
    server_name $server_name;

    # 前端静态文件
    location / {
        root /opt/camel_ai/multi_agent_meeting/frontend;
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
    
    sudo ln -sf /etc/nginx/sites-available/multi-agent-meeting /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    log_success "Nginx配置完成"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    
    sudo chown -R www-data:www-data /opt/camel_ai
    sudo chmod -R 755 /opt/camel_ai
    
    log_success "权限设置完成"
}

# 创建项目目录
create_project_dir() {
    log_info "创建项目目录..."
    
    sudo mkdir -p /opt/camel_ai
    sudo chown $USER:$USER /opt/camel_ai
    cd /opt/camel_ai
    
    log_success "项目目录创建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    sudo systemctl start multi-agent-meeting
    
    # 等待服务启动
    sleep 3
    
    if sudo systemctl is-active --quiet multi-agent-meeting; then
        log_success "多智能体会议服务启动成功"
    else
        log_error "服务启动失败，请检查日志: sudo journalctl -u multi-agent-meeting -f"
        exit 1
    fi
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        sudo ufw allow 22
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw --force enable
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload
    else
        log_warning "未检测到防火墙，请手动配置"
    fi
    
    log_success "防火墙配置完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    if sudo systemctl is-active --quiet multi-agent-meeting; then
        log_success "✓ 服务运行正常"
    else
        log_error "✗ 服务未运行"
        return 1
    fi
    
    # 检查端口
    if netstat -tlnp | grep -q ":5000"; then
        log_success "✓ 端口5000监听正常"
    else
        log_error "✗ 端口5000未监听"
        return 1
    fi
    
    # 检查Nginx
    if sudo systemctl is-active --quiet nginx; then
        log_success "✓ Nginx运行正常"
    else
        log_error "✗ Nginx未运行"
        return 1
    fi
    
    log_success "健康检查通过！"
}

# 显示部署信息
show_deployment_info() {
    echo
    echo "🎉 部署完成！"
    echo "=================================="
    echo "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
    echo "服务状态: sudo systemctl status multi-agent-meeting"
    echo "查看日志: sudo journalctl -u multi-agent-meeting -f"
    echo "重启服务: sudo systemctl restart multi-agent-meeting"
    echo "=================================="
    echo
    log_warning "请记得编辑 /opt/camel_ai/multi_agent_meeting/backend/.env 配置API密钥"
}

# 主函数
main() {
    echo "多智能体会议系统快速部署脚本"
    echo "支持Git部署和虚拟环境自动创建"
    echo "=================================="
    
    check_root
    check_system
    install_dependencies
    create_project_dir
    
    clone_project
    setup_python_env
    setup_environment
    create_systemd_service
    setup_nginx
    set_permissions
    start_services
    setup_firewall
    health_check
    show_deployment_info
}

# 执行主函数
main "$@"
