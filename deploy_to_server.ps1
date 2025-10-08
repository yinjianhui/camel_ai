# 多智能体会议系统 - PowerShell部署脚本
# 用于将项目部署到CentOS Linux服务器

# 配置参数
$SERVER_IP = "8.134.128.123"
$SERVER_USER = "root"
$PROJECT_DIR = "/opt/camel_ai"
$GITHUB_REPO = "https://github.com/yinjianhui/camel_ai.git"

# 颜色输出函数
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    Write-Host $Message -ForegroundColor $Color
}

# 执行SSH命令函数
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$ErrorMessage = "SSH命令执行失败"
    )
    
    try {
        Write-ColoredOutput "执行: $Command" "Cyan"
        $result = ssh ${SERVER_USER}@${SERVER_IP} $Command
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✅ 命令执行成功" "Green"
            return $result
        } else {
            Write-ColoredOutput "❌ $ErrorMessage" "Red"
            Write-ColoredOutput "退出代码: $LASTEXITCODE" "Red"
            return $null
        }
    }
    catch {
        Write-ColoredOutput "❌ SSH连接失败: $_" "Red"
        return $null
    }
}

# 检查SSH连接
function Test-SSHConnection {
    Write-ColoredOutput "🔍 检查SSH连接..." "Yellow"
    $result = Invoke-SSHCommand -Command "echo 'SSH连接成功'"
    if ($result -eq $null) {
        Write-ColoredOutput "❌ 无法连接到服务器，请检查SSH配置" "Red"
        exit 1
    }
    Write-ColoredOutput "✅ SSH连接正常" "Green"
}

# 部署主函数
function Start-Deployment {
    Write-ColoredOutput "🚀 开始部署多智能体会议系统到服务器 ${SERVER_IP}" "Yellow"
    Write-ColoredOutput "=================================================" "Yellow"
    
    # 1. 检查SSH连接
    Test-SSHConnection
    
    # 2. 更新系统并安装基础软件
    Write-ColoredOutput "`n📦 更新系统并安装基础软件..." "Yellow"
    Invoke-SSHCommand -Command "yum update -y" -ErrorMessage "系统更新失败"
    Invoke-SSHCommand -Command "yum install -y python3 python3-pip python3-venv nginx git curl wget" -ErrorMessage "基础软件安装失败"
    
    # 3. 检查Python版本
    Write-ColoredOutput "`n🐍 检查Python版本..." "Yellow"
    $pythonVersion = Invoke-SSHCommand -Command "python3 --version"
    if ($pythonVersion -match "Python 3\.1[1-9]") {
        Write-ColoredOutput "✅ Python版本符合要求: $pythonVersion" "Green"
    } else {
        Write-ColoredOutput "⚠️  Python版本可能不符合要求: $pythonVersion" "Yellow"
        Write-ColoredOutput "建议安装Python 3.11+" "Yellow"
    }
    
    # 4. 创建项目目录
    Write-ColoredOutput "`n📁 创建项目目录..." "Yellow"
    Invoke-SSHCommand -Command "mkdir -p ${PROJECT_DIR}" -ErrorMessage "创建项目目录失败"
    Invoke-SSHCommand -Command "chown ${SERVER_USER}:${SERVER_USER} ${PROJECT_DIR}" -ErrorMessage "设置目录权限失败"
    
    # 5. 克隆项目代码
    Write-ColoredOutput "`n📥 克隆项目代码..." "Yellow"
    Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && git clone ${GITHUB_REPO} ." -ErrorMessage "克隆项目失败"
    
    # 6. 前端API配置优化说明
    Write-ColoredOutput "`n🌐 前端API配置优化说明..." "Yellow"
    Write-ColoredOutput "重要更新: 前端API配置已优化，使用相对路径自动适配服务器环境" "Cyan"
    Write-ColoredOutput "优化内容:" "Cyan"
    Write-ColoredOutput "  - 前端配置: 使用相对路径（空字符串）自动适配当前域名" "Cyan"
    Write-ColoredOutput "  - 自动适配: 前端自动使用当前访问的域名进行API调用" "Cyan"
    Write-ColoredOutput "  - 环境无关: 开发和生产环境使用相同配置，无需修改" "Cyan"
    Write-ColoredOutput "优势:" "Cyan"
    Write-ColoredOutput "  1. 完全自动: 无需任何手动配置，前端自动适配" "Cyan"
    Write-ColoredOutput "  2. 环境无关: 开发、测试、生产环境配置完全一致" "Cyan"
    Write-ColoredOutput "  3. 零维护: 服务器IP、域名变更时完全无需修改前端代码" "Cyan"
    Write-ColoredOutput "  4. 最大灵活性: 支持任意访问方式（IP、域名、端口等）" "Cyan"
    Write-ColoredOutput "部署优势:" "Cyan"
    Write-ColoredOutput "  - 开箱即用: 部署后前端立即自动适配服务器环境" "Cyan"
    Write-ColoredOutput "  - 无需配置: 不需要在前端代码中配置任何服务器地址" "Cyan"
    Write-ColoredOutput "  - 无缝切换: 支持IP访问、域名访问、带端口访问等多种方式" "Cyan"
    Write-ColoredOutput "  - 负载均衡友好: 支持多服务器负载均衡环境" "Cyan"
    Write-ColoredOutput "  - HTTPS友好: 自动适配HTTP和HTTPS协议" "Cyan"
    
    # 7. 验证预配置虚拟环境
    Write-ColoredOutput "`n🔍 验证预配置虚拟环境..." "Yellow"
    $venvCheck = Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && if [[ -d 'venv' ]]; then echo 'venv目录存在'; else echo 'venv目录不存在'; fi"
    
    if ($venvCheck -eq "venv目录存在") {
        Write-ColoredOutput "✅ 发现预配置的虚拟环境" "Green"
        
        # 检查虚拟环境完整性
        $venvIntegrity = Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && if [[ -f 'venv/bin/python' && -f 'venv/bin/pip' ]]; then echo '完整'; else echo '不完整'; fi"
        
        if ($venvIntegrity -eq "完整") {
            Write-ColoredOutput "✅ 虚拟环境文件完整" "Green"
            
            # 验证Python版本和依赖包
            $pythonCheck = Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && source venv/bin/activate && python --version"
            Write-ColoredOutput "虚拟环境Python版本: $pythonCheck" "Cyan"
            
            # 验证关键依赖包
            $depsCheck = Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && source venv/bin/activate && python -c 'import flask, flask_cors, flask_socketio, camel, camel_ai, openai' 2>/dev/null && echo '依赖包完整' || echo '依赖包缺失'"
            
            if ($depsCheck -eq "依赖包完整") {
                Write-ColoredOutput "✅ 所有关键依赖包已安装，包括CAMEL-AI模块" "Green"
            } else {
                Write-ColoredOutput "⚠️  部分依赖包缺失，重新安装..." "Yellow"
                Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && source venv/bin/activate && pip install --upgrade pip && pip install -r multi_agent_meeting/backend/requirements.txt" -ErrorMessage "依赖包安装失败"
            }
        } else {
            Write-ColoredOutput "❌ 虚拟环境文件不完整，重新创建..." "Red"
            Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r multi_agent_meeting/backend/requirements.txt" -ErrorMessage "虚拟环境创建失败"
        }
    } else {
        Write-ColoredOutput "❌ 未发现预配置虚拟环境，创建新的..." "Red"
        Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r multi_agent_meeting/backend/requirements.txt" -ErrorMessage "虚拟环境创建失败"
    }
    
    # 7. 配置环境变量
    Write-ColoredOutput "`n⚙️  配置环境变量..." "Yellow"
    Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && cp multi_agent_meeting/backend/env.example multi_agent_meeting/backend/.env" -ErrorMessage "环境变量配置失败"
    
    # 8. 验证API密钥配置
    Write-ColoredOutput "`n� 验证API密钥配置..." "Yellow"
    $apiCheck = Invoke-SSHCommand -Command "cd ${PROJECT_DIR} && cat multi_agent_meeting/backend/config.py | grep -A 6 'api_keys'"
    Write-ColoredOutput "API密钥配置:" "Cyan"
    Write-ColoredOutput $apiCheck "White"
    
    # 9. 创建systemd服务
    Write-ColoredOutput "`n� 创建systemd服务..." "Yellow"
    $serviceConfig = @"
[Unit]
Description=Multi Agent Meeting System
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${PROJECT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/venv/bin/python multi_agent_meeting/backend/app_new.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"@
    
    # 将服务配置写入临时文件并上传
    $serviceConfig | Out-File -FilePath "temp_service.conf" -Encoding UTF8
    scp temp_service.conf ${SERVER_USER}@${SERVER_IP}:/tmp/multi-agent-meeting.service
    Remove-Item temp_service.conf
    
    Invoke-SSHCommand -Command "mv /tmp/multi-agent-meeting.service /etc/systemd/system/ && systemctl daemon-reload" -ErrorMessage "服务配置失败"
    
    # 10. 配置Nginx
    Write-ColoredOutput "`n🌐 配置Nginx反向代理..." "Yellow"
    $nginxConfig = @"
server {
    listen 80;
    server_name ${SERVER_IP};

    # 前端静态文件
    location / {
        root ${PROJECT_DIR}/multi_agent_meeting/frontend;
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
"@
    
    # 将Nginx配置写入临时文件并上传
    $nginxConfig | Out-File -FilePath "temp_nginx.conf" -Encoding UTF8
    scp temp_nginx.conf ${SERVER_USER}@${SERVER_IP}:/tmp/multi-agent-meeting.conf
    Remove-Item temp_nginx.conf
    
    Invoke-SSHCommand -Command "mv /tmp/multi-agent-meeting.conf /etc/nginx/conf.d/ && nginx -t" -ErrorMessage "Nginx配置失败"
    Invoke-SSHCommand -Command "systemctl reload nginx" -ErrorMessage "Nginx重载失败"
    
    # 11. 设置目录权限
    Write-ColoredOutput "`n🔐 设置目录权限..." "Yellow"
    Invoke-SSHCommand -Command "chown -R root:root ${PROJECT_DIR}" -ErrorMessage "目录权限设置失败"
    Invoke-SSHCommand -Command "chmod -R 755 ${PROJECT_DIR}" -ErrorMessage "目录权限设置失败"
    
    # 12. 启动服务
    Write-ColoredOutput "`n🚀 启动服务..." "Yellow"
    Invoke-SSHCommand -Command "systemctl enable multi-agent-meeting" -ErrorMessage "服务启用失败"
    Invoke-SSHCommand -Command "systemctl start multi-agent-meeting" -ErrorMessage "服务启动失败"
    
    # 13. 检查服务状态
    Write-ColoredOutput "`n📊 检查服务状态..." "Yellow"
    $serviceStatus = Invoke-SSHCommand -Command "systemctl status multi-agent-meeting --no-pager"
    Write-ColoredOutput "服务状态:" "Cyan"
    Write-ColoredOutput $serviceStatus "White"
    
    # 14. 配置防火墙
    Write-ColoredOutput "`n🔥 配置防火墙..." "Yellow"
    Invoke-SSHCommand -Command "firewall-cmd --permanent --add-service=http" -ErrorMessage "防火墙配置失败"
    Invoke-SSHCommand -Command "firewall-cmd --permanent --add-service=https" -ErrorMessage "防火墙配置失败"
    Invoke-SSHCommand -Command "firewall-cmd --reload" -ErrorMessage "防火墙重载失败"
    
    # 15. 健康检查
    Write-ColoredOutput "`n🏥 执行健康检查..." "Yellow"
    Start-Sleep -Seconds 10  # 等待服务启动
    $healthCheck = Invoke-SSHCommand -Command "curl -s http://localhost:5000/api/health || echo '健康检查失败'"
    Write-ColoredOutput "健康检查结果: $healthCheck" "Cyan"
    
    # 16. 部署完成
    Write-ColoredOutput "`n🎉 部署完成！" "Green"
    Write-ColoredOutput "=================================================" "Green"
    Write-ColoredOutput "📋 访问信息:" "Yellow"
    Write-ColoredOutput "   前端地址: http://${SERVER_IP}" "Cyan"
    Write-ColoredOutput "   后端API: http://${SERVER_IP}/api" "Cyan"
    Write-ColoredOutput "   健康检查: http://${SERVER_IP}/api/health" "Cyan"
    Write-ColoredOutput "`n📋 管理命令:" "Yellow"
    Write-ColoredOutput "   查看日志: journalctl -u multi-agent-meeting -f" "Cyan"
    Write-ColoredOutput "   重启服务: systemctl restart multi-agent-meeting" "Cyan"
    Write-ColoredOutput "   查看状态: systemctl status multi-agent-meeting" "Cyan"
    Write-ColoredOutput "=================================================" "Green"
}

# 主程序入口
try {
    Start-Deployment
}
catch {
    Write-ColoredOutput "❌ 部署过程中发生错误: $_" "Red"
    Write-ColoredOutput "请检查错误信息并重试" "Red"
    exit 1
}
