#!/bin/bash
# 多智能体会议系统部署脚本
# 用于更新代码和重启服务

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

# 项目配置
PROJECT_DIR="/opt/camel_ai"
SERVICE_NAME="multi-agent-meeting"

# 检查服务状态
check_service_status() {
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_success "服务正在运行"
        return 0
    else
        log_warning "服务未运行"
        return 1
    fi
}

# 备份当前版本
backup_current_version() {
    log_info "备份当前版本..."
    BACKUP_DIR="/opt/backups/multi_agent_meeting/$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$BACKUP_DIR"
    sudo cp -r "$PROJECT_DIR" "$BACKUP_DIR/"
    log_success "备份完成: $BACKUP_DIR"
}

# 更新代码
update_code() {
    log_info "更新代码..."
    cd "$PROJECT_DIR"
    
    # 如果使用Git
    if [ -d ".git" ]; then
        git pull origin master
        log_success "Git代码更新完成"
    else
        log_warning "未检测到Git仓库，请手动更新代码"
        return 1
    fi
}

# 更新依赖
update_dependencies() {
    log_info "更新Python依赖..."
    cd "$PROJECT_DIR"
    source venv/bin/activate
    pip install -r backend/requirements.txt
    log_success "依赖更新完成"
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    sudo systemctl restart $SERVICE_NAME
    
    # 等待服务启动
    sleep 5
    
    if check_service_status; then
        log_success "服务重启成功"
    else
        log_error "服务重启失败"
        sudo systemctl status $SERVICE_NAME
        return 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务完全启动
    sleep 10
    
    if curl -s http://localhost:5000/api/health > /dev/null; then
        log_success "健康检查通过"
        return 0
    else
        log_error "健康检查失败"
        return 1
    fi
}

# 回滚到备份版本
rollback() {
    log_info "回滚到备份版本..."
    
    # 查找最新的备份
    LATEST_BACKUP=$(ls -t /opt/backups/multi_agent_meeting/ | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "未找到备份文件"
        return 1
    fi
    
    log_info "回滚到备份: $LATEST_BACKUP"
    
    # 停止服务
    sudo systemctl stop $SERVICE_NAME
    
    # 恢复备份
    sudo rm -rf "$PROJECT_DIR"
    sudo cp -r "/opt/backups/multi_agent_meeting/$LATEST_BACKUP" "$PROJECT_DIR"
    
    # 重启服务
    sudo systemctl start $SERVICE_NAME
    
    log_success "回滚完成"
}

# 查看日志
view_logs() {
    log_info "查看服务日志..."
    sudo journalctl -u $SERVICE_NAME -f
}

# 显示帮助信息
show_help() {
    echo "多智能体会议系统部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  deploy     部署/更新代码"
    echo "  restart    重启服务"
    echo "  status     查看服务状态"
    echo "  logs       查看服务日志"
    echo "  rollback   回滚到备份版本"
    echo "  health     健康检查"
    echo "  help       显示帮助信息"
    echo ""
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            log_info "开始部署..."
            backup_current_version
            update_code
            update_dependencies
            restart_service
            health_check
            log_success "部署完成！"
            ;;
        "restart")
            log_info "重启服务..."
            restart_service
            health_check
            ;;
        "status")
            check_service_status
            sudo systemctl status $SERVICE_NAME
            ;;
        "logs")
            view_logs
            ;;
        "rollback")
            rollback
            ;;
        "health")
            health_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
