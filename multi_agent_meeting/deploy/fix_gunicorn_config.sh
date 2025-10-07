#!/bin/bash
# 修复gunicorn配置并重启服务脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

SERVICE_NAME="multi-agent-meeting"
SERVICE_FILE="/etc/systemd/system/multi-agent-meeting.service"
BACKEND_DIR="/opt/camel_ai/multi_agent_meeting/backend"

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 备份原服务文件
backup_service_file() {
    if [[ -f "$SERVICE_FILE" ]]; then
        cp "$SERVICE_FILE" "$SERVICE_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "原服务文件已备份"
    fi
}

# 安装新的服务文件
install_service_file() {
    log_info "安装新的systemd服务文件..."
    
    # 确保目录存在
    mkdir -p "$(dirname "$SERVICE_FILE")"
    
    # 复制服务文件
    cp "$BACKEND_DIR/../deploy/multi-agent-meeting.service" "$SERVICE_FILE"
    
    # 设置权限
    chmod 644 "$SERVICE_FILE"
    
    log_success "服务文件安装完成"
}

# 检查并安装eventlet
check_eventlet() {
    log_info "检查eventlet依赖..."
    
    # 激活虚拟环境
    source /opt/camel_ai/venv/bin/activate
    
    # 检查eventlet是否已安装
    if ! python -c "import eventlet" 2>/dev/null; then
        log_info "安装eventlet..."
        pip install eventlet
        log_success "eventlet安装完成"
    else
        log_success "eventlet已安装"
    fi
}

# 重新加载systemd配置
reload_systemd() {
    log_info "重新加载systemd配置..."
    systemctl daemon-reload
    systemctl reset-failed $SERVICE_NAME
    log_success "systemd配置重新加载完成"
}

# 重启服务
restart_service() {
    log_info "重启 $SERVICE_NAME 服务..."
    
    # 停止服务
    systemctl stop $SERVICE_NAME || true
    
    # 等待进程完全停止
    sleep 2
    
    # 启动服务
    systemctl start $SERVICE_NAME
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "服务重启成功"
    else
        log_error "服务重启失败"
        systemctl status $SERVICE_NAME
        return 1
    fi
}

# 检查服务状态
check_service_status() {
    log_info "检查服务状态..."
    
    # 检查服务是否运行
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "✓ 服务运行正常"
        
        # 检查端口监听
        if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
            log_success "✓ 端口5000监听正常"
        else
            log_error "✗ 端口5000未监听"
            return 1
        fi
        
        # 测试应用响应
        if curl -s -f http://localhost:5000/api/health > /dev/null 2>&1; then
            log_success "✓ 应用响应正常"
        else
            log_warning "⚠ 应用健康检查失败，但可能仍在启动中"
        fi
        
    else
        log_error "✗ 服务未运行"
        systemctl status $SERVICE_NAME
        return 1
    fi
}

# 查看最新日志
show_logs() {
    log_info "显示最新日志..."
    echo "----------------------------------------"
    journalctl -u $SERVICE_NAME --no-pager -n 20
    echo "----------------------------------------"
}

# 获取服务器IP
get_server_ip() {
    IP=$(curl -s ifconfig.me 2>/dev/null || \
         curl -s ipinfo.io/ip 2>/dev/null || \
         hostname -I | awk '{print $1}' || \
         echo "your-server-ip")
    echo $IP
}

# 显示访问信息
show_access_info() {
    SERVER_IP=$(get_server_ip)
    
    echo
    echo "🎉 gunicorn配置修复完成！"
    echo "=================================="
    echo "📱 访问地址："
    echo "   前端界面: http://$SERVER_IP/"
    echo "   后端API:  http://$SERVER_IP/api/"
    echo "   健康检查: http://$SERVER_IP/api/health"
    echo ""
    echo "🔧 管理命令："
    echo "   查看服务状态: sudo systemctl status $SERVICE_NAME"
    echo "   查看服务日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "   重启服务: sudo systemctl restart $SERVICE_NAME"
    echo ""
    echo "📋 如果无法访问，请检查："
    echo "   1. 防火墙设置 (sudo ufw allow 80, sudo ufw allow 5000)"
    echo "   2. 云服务器安全组"
    echo "   3. nginx状态 (sudo systemctl status nginx)"
    echo "=================================="
}

# 主函数
main() {
    echo "🔧 修复gunicorn配置并重启服务"
    echo "=================================="
    
    check_root
    backup_service_file
    check_eventlet
    install_service_file
    reload_systemd
    restart_service
    check_service_status
    show_logs
    show_access_info
    
    log_success "所有修复完成！"
}

# 执行主函数
main "$@"
