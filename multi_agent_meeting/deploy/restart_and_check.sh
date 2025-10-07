#!/bin/bash
# 重启服务并检查访问状态脚本

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

# 获取服务器IP
get_server_ip() {
    # 尝试多种方式获取IP
    IP=$(curl -s ifconfig.me 2>/dev/null || \
         curl -s ipinfo.io/ip 2>/dev/null || \
         hostname -I | awk '{print $1}' || \
         echo "your-server-ip")
    echo $IP
}

# 重启服务
restart_service() {
    log_info "重启 $SERVICE_NAME 服务..."
    
    # 重启服务
    sudo systemctl restart $SERVICE_NAME
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_success "服务重启成功"
    else
        log_error "服务重启失败"
        sudo systemctl status $SERVICE_NAME
        return 1
    fi
}

# 检查端口监听
check_ports() {
    log_info "检查端口监听状态..."
    
    # 检查5000端口
    if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
        log_success "✓ 端口5000监听正常"
    else
        log_error "✗ 端口5000未监听"
        return 1
    fi
    
    # 检查80端口（nginx）
    if netstat -tlnp 2>/dev/null | grep -q ":80"; then
        log_success "✓ 端口80监听正常"
    else
        log_warning "⚠ 端口80未监听（nginx可能未运行）"
    fi
}

# 检查nginx状态
check_nginx() {
    log_info "检查Nginx状态..."
    
    if sudo systemctl is-active --quiet nginx; then
        log_success "✓ Nginx运行正常"
    else
        log_warning "⚠ Nginx未运行，尝试启动..."
        sudo systemctl start nginx
        sleep 2
        
        if sudo systemctl is-active --quiet nginx; then
            log_success "✓ Nginx启动成功"
        else
            log_error "✗ Nginx启动失败"
            return 1
        fi
    fi
}

# 测试应用响应
test_application() {
    log_info "测试应用响应..."
    
    SERVER_IP=$(get_server_ip)
    
    # 测试后端API
    if curl -s -f http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "✓ 后端API响应正常"
    else
        log_error "✗ 后端API无响应"
        return 1
    fi
    
    # 测试前端访问
    if curl -s -f http://localhost/ > /dev/null 2>&1; then
        log_success "✓ 前端页面访问正常"
    else
        log_warning "⚠ 前端页面可能有问题"
    fi
    
    # 测试外部IP访问
    log_info "测试外部IP访问（可能需要几分钟时间生效）..."
    if curl -s -f --connect-timeout 10 http://$SERVER_IP/ > /dev/null 2>&1; then
        log_success "✓ 外部IP访问正常"
    else
        log_warning "⚠ 外部IP访问测试失败，可能是防火墙或网络问题"
    fi
}

# 检查防火墙
check_firewall() {
    log_info "检查防火墙设置..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        if sudo ufw status | grep -q "Status: active"; then
            if sudo ufw status | grep -q "5000"; then
                log_success "✓ 防火墙已开放5000端口"
            else
                log_warning "⚠ 防火墙未开放5000端口，正在添加..."
                sudo ufw allow 5000
                log_success "✓ 防火墙已开放5000端口"
            fi
            
            if sudo ufw status | grep -q "80"; then
                log_success "✓ 防火墙已开放80端口"
            else
                log_warning "⚠ 防火墙未开放80端口，正在添加..."
                sudo ufw allow 80
                log_success "✓ 防火墙已开放80端口"
            fi
        else
            log_info "防火墙未启用"
        fi
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL
        if sudo firewall-cmd --state &> /dev/null; then
            if sudo firewall-cmd --list-ports | grep -q "5000/tcp"; then
                log_success "✓ 防火墙已开放5000端口"
            else
                log_warning "⚠ 防火墙未开放5000端口，正在添加..."
                sudo firewall-cmd --permanent --add-port=5000/tcp
                sudo firewall-cmd --reload
                log_success "✓ 防火墙已开放5000端口"
            fi
            
            if sudo firewall-cmd --list-services | grep -q "http"; then
                log_success "✓ 防火墙已开放80端口"
            else
                log_warning "⚠ 防火墙未开放80端口，正在添加..."
                sudo firewall-cmd --permanent --add-service=http
                sudo firewall-cmd --reload
                log_success "✓ 防火墙已开放80端口"
            fi
        else
            log_info "防火墙未启用"
        fi
    else
        log_info "未检测到防火墙管理工具"
    fi
}

# 显示访问信息
show_access_info() {
    SERVER_IP=$(get_server_ip)
    
    echo
    echo "🎉 服务重启完成！"
    echo "=================================="
    echo "📱 访问地址："
    echo "   前端界面: http://$SERVER_IP/"
    echo "   后端API:  http://$SERVER_IP/api/"
    echo ""
    echo "🔧 管理命令："
    echo "   查看服务状态: sudo systemctl status $SERVICE_NAME"
    echo "   查看服务日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "   重启服务: sudo systemctl restart $SERVICE_NAME"
    echo "   重启Nginx: sudo systemctl restart nginx"
    echo ""
    echo "📋 如果无法访问，请检查："
    echo "   1. 防火墙设置"
    echo "   2. 云服务器安全组"
    echo "   3. 域名解析（如果使用域名）"
    echo "=================================="
}

# 主函数
main() {
    echo "🚀 重启服务并检查访问状态"
    echo "=================================="
    
    restart_service
    check_ports
    check_nginx
    check_firewall
    test_application
    show_access_info
    
    log_success "所有检查完成！"
}

# 执行主函数
main "$@"
