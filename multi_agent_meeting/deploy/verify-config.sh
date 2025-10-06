#!/bin/bash
# 部署配置验证脚本
# 验证所有配置文件中的路径和Git地址是否正确

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

# 验证Git地址
verify_git_url() {
    log_info "验证Git地址配置..."
    
    # 检查部署文档中的Git地址
    if grep -q "https://github.com/yinjianhui/camel_ai.git" multi_agent_meeting/DEPLOYMENT_GUIDE.md; then
        log_success "✓ DEPLOYMENT_GUIDE.md 中的Git地址正确"
    else
        log_error "✗ DEPLOYMENT_GUIDE.md 中的Git地址不正确"
        return 1
    fi
    
    # 检查快速部署脚本中的Git地址
    if grep -q "https://github.com/yinjianhui/camel_ai.git" multi_agent_meeting/deploy/quick-deploy.sh; then
        log_success "✓ quick-deploy.sh 中的Git地址正确"
    else
        log_error "✗ quick-deploy.sh 中的Git地址不正确"
        return 1
    fi
    
    log_success "Git地址验证完成"
}

# 验证项目路径
verify_project_paths() {
    log_info "验证项目路径配置..."
    
    # 检查systemd服务配置中的路径
    if grep -q "WorkingDirectory=/opt/camel_ai" multi_agent_meeting/deploy/multi-agent-meeting.service; then
        log_success "✓ systemd服务配置中的工作目录路径正确"
    else
        log_error "✗ systemd服务配置中的工作目录路径不正确"
        return 1
    fi
    
    if grep -q "ExecStart=/opt/camel_ai/venv/bin/python multi_agent_meeting/backend/app_new.py" multi_agent_meeting/deploy/multi-agent-meeting.service; then
        log_success "✓ systemd服务配置中的执行路径正确"
    else
        log_error "✗ systemd服务配置中的执行路径不正确"
        return 1
    fi
    
    # 检查Nginx配置中的路径
    if grep -q "root /opt/camel_ai/multi_agent_meeting/frontend;" multi_agent_meeting/deploy/nginx.conf; then
        log_success "✓ Nginx配置中的前端路径正确"
    else
        log_error "✗ Nginx配置中的前端路径不正确"
        return 1
    fi
    
    # 检查部署脚本中的路径
    if grep -q 'PROJECT_DIR="/opt/camel_ai"' multi_agent_meeting/deploy/deploy.sh; then
        log_success "✓ deploy.sh 中的项目路径正确"
    else
        log_error "✗ deploy.sh 中的项目路径不正确"
        return 1
    fi
    
    log_success "项目路径验证完成"
}

# 验证文件存在性
verify_file_existence() {
    log_info "验证关键文件存在性..."
    
    local files=(
        "multi_agent_meeting/DEPLOYMENT_GUIDE.md"
        "multi_agent_meeting/deploy/quick-deploy.sh"
        "multi_agent_meeting/deploy/deploy.sh"
        "multi_agent_meeting/deploy/multi-agent-meeting.service"
        "multi_agent_meeting/deploy/nginx.conf"
        "multi_agent_meeting/backend/app_new.py"
        "multi_agent_meeting/backend/requirements.txt"
        "multi_agent_meeting/backend/env.example"
        "multi_agent_meeting/frontend/index.html"
        "multi_agent_meeting/frontend/app.js"
        "multi_agent_meeting/frontend/style.css"
    )
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✓ $file 存在"
        else
            log_error "✗ $file 不存在"
            return 1
        fi
    done
    
    log_success "文件存在性验证完成"
}

# 验证脚本权限
verify_script_permissions() {
    log_info "验证脚本权限..."
    
    local scripts=(
        "multi_agent_meeting/deploy/quick-deploy.sh"
        "multi_agent_meeting/deploy/deploy.sh"
        "multi_agent_meeting/deploy/verify-config.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -x "$script" ]]; then
            log_success "✓ $script 具有执行权限"
        else
            log_warning "⚠ $script 缺少执行权限，正在添加..."
            chmod +x "$script"
            if [[ -x "$script" ]]; then
                log_success "✓ $script 执行权限已添加"
            else
                log_error "✗ 无法为 $script 添加执行权限"
                return 1
            fi
        fi
    done
    
    log_success "脚本权限验证完成"
}

# 验证配置一致性
verify_config_consistency() {
    log_info "验证配置一致性..."
    
    # 检查所有配置文件中使用相同的项目根路径
    local expected_path="/opt/camel_ai"
    
    # 检查systemd服务
    if ! grep -q "WorkingDirectory=$expected_path" multi_agent_meeting/deploy/multi-agent-meeting.service; then
        log_error "✗ systemd服务配置中的路径不一致"
        return 1
    fi
    
    # 检查Nginx配置
    if ! grep -q "root $expected_path/multi_agent_meeting/frontend;" multi_agent_meeting/deploy/nginx.conf; then
        log_error "✗ Nginx配置中的路径不一致"
        return 1
    fi
    
    # 检查部署脚本
    if ! grep -q "PROJECT_DIR=\"$expected_path\"" multi_agent_meeting/deploy/deploy.sh; then
        log_error "✗ deploy.sh中的路径不一致"
        return 1
    fi
    
    log_success "配置一致性验证完成"
}

# 生成验证报告
generate_verification_report() {
    log_info "生成验证报告..."
    
    local report_file="verification_report.txt"
    
    cat > "$report_file" << EOF
多智能体会议系统部署配置验证报告
===================================
生成时间: $(date)
验证结果: 成功

验证项目:
1. Git地址配置 - 通过
2. 项目路径配置 - 通过  
3. 关键文件存在性 - 通过
4. 脚本权限配置 - 通过
5. 配置一致性检查 - 通过

关键配置摘要:
- Git仓库: https://github.com/yinjianhui/camel_ai.git
- 项目根目录: /opt/camel_ai
- 后端应用: /opt/camel_ai/multi_agent_meeting/backend/app_new.py
- 前端文件: /opt/camel_ai/multi_agent_meeting/frontend/
- 虚拟环境: /opt/camel_ai/venv/
- 服务名称: multi-agent-meeting

部署命令:
1. 快速部署: ./multi_agent_meeting/deploy/quick-deploy.sh
2. 手动部署: 参考 multi_agent_meeting/DEPLOYMENT_GUIDE.md
3. 更新部署: ./multi_agent_meeting/deploy/deploy.sh deploy

注意事项:
- 请确保在部署前配置正确的API密钥
- 建议使用非root用户进行部署
- 确保服务器满足最低系统要求

EOF
    
    log_success "验证报告已生成: $report_file"
}

# 主函数
main() {
    echo "多智能体会议系统部署配置验证"
    echo "=================================="
    
    verify_git_url
    verify_project_paths
    verify_file_existence
    verify_script_permissions
    verify_config_consistency
    generate_verification_report
    
    echo
    echo "🎉 所有配置验证通过！"
    echo "=================================="
    echo "项目已准备好进行部署"
    echo "使用以下命令开始部署:"
    echo "  ./multi_agent_meeting/deploy/quick-deploy.sh"
    echo
}

# 执行主函数
main "$@"
