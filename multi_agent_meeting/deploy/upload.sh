#!/bin/bash
# 项目文件上传脚本
# 用于将本地项目文件上传到服务器

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

# 配置变量
LOCAL_PROJECT_DIR="$(dirname "$0")/.."
REMOTE_HOST=""
REMOTE_USER="root"
REMOTE_DIR="/opt/multi_agent_meeting"

# 显示帮助信息
show_help() {
    echo "项目文件上传脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --host HOST     服务器IP地址或域名"
    echo "  -u, --user USER     用户名 (默认: root)"
    echo "  -d, --dir DIR       远程目录 (默认: /opt/multi_agent_meeting)"
    echo "  --help              显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --host 192.168.1.100"
    echo "  $0 --host example.com --user ubuntu"
    echo ""
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                REMOTE_HOST="$2"
                shift 2
                ;;
            -u|--user)
                REMOTE_USER="$2"
                shift 2
                ;;
            -d|--dir)
                REMOTE_DIR="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查参数
check_args() {
    if [ -z "$REMOTE_HOST" ]; then
        log_error "请指定服务器地址"
        show_help
        exit 1
    fi
}

# 检查本地项目目录
check_local_dir() {
    if [ ! -d "$LOCAL_PROJECT_DIR" ]; then
        log_error "本地项目目录不存在: $LOCAL_PROJECT_DIR"
        exit 1
    fi
    
    if [ ! -f "$LOCAL_PROJECT_DIR/backend/app_new.py" ]; then
        log_error "未找到项目文件，请确保在正确的目录中运行此脚本"
        exit 1
    fi
    
    log_success "本地项目目录检查通过"
}

# 测试SSH连接
test_ssh_connection() {
    log_info "测试SSH连接..."
    if ssh -o ConnectTimeout=10 -o BatchMode=yes "$REMOTE_USER@$REMOTE_HOST" exit 2>/dev/null; then
        log_success "SSH连接测试通过"
    else
        log_error "SSH连接失败，请检查："
        echo "  1. 服务器地址是否正确"
        echo "  2. 用户名是否正确"
        echo "  3. SSH密钥是否配置"
        echo "  4. 服务器是否允许SSH连接"
        exit 1
    fi
}

# 创建远程目录
create_remote_dir() {
    log_info "创建远程目录..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "sudo mkdir -p $REMOTE_DIR && sudo chown $REMOTE_USER:$REMOTE_USER $REMOTE_DIR"
    log_success "远程目录创建完成"
}

# 上传项目文件
upload_files() {
    log_info "上传项目文件..."
    
    # 使用rsync上传文件，排除不需要的文件
    rsync -avz --progress \
        --exclude='venv/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        --exclude='.git/' \
        --exclude='.gitignore' \
        --exclude='*.log' \
        --exclude='temp/' \
        --exclude='logs/' \
        --exclude='.env' \
        --exclude='deploy/' \
        "$LOCAL_PROJECT_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"
    
    log_success "项目文件上传完成"
}

# 设置远程权限
set_remote_permissions() {
    log_info "设置远程文件权限..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        sudo chown -R www-data:www-data $REMOTE_DIR
        sudo chmod -R 755 $REMOTE_DIR
        sudo chmod +x $REMOTE_DIR/backend/app_new.py
    "
    log_success "远程文件权限设置完成"
}

# 显示完成信息
show_completion_info() {
    echo ""
    echo "=========================================="
    log_success "文件上传完成！"
    echo "=========================================="
    echo ""
    echo "下一步操作："
    echo "  1. SSH连接到服务器: ssh $REMOTE_USER@$REMOTE_HOST"
    echo "  2. 运行安装脚本: cd $REMOTE_DIR && chmod +x deploy/install.sh && ./deploy/install.sh"
    echo "  3. 配置API密钥: nano $REMOTE_DIR/backend/config.py"
    echo ""
}

# 主函数
main() {
    echo "=========================================="
    echo "多智能体会议系统文件上传脚本"
    echo "=========================================="
    echo ""
    
    parse_args "$@"
    check_args
    check_local_dir
    test_ssh_connection
    create_remote_dir
    upload_files
    set_remote_permissions
    show_completion_info
}

# 运行主函数
main "$@"
