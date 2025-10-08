const { createApp } = Vue;

createApp({
    data() {
        return {
            // 配置数据
            config: {
                topic: '',
                background: '',
                agents: [
                    { role: 'CEO', description: '' },
                    { role: '', description: '' },
                    { role: '', description: '' },
                    { role: '', description: '' }
                ]
            },
            
            // 会议状态
            meetingStarted: false,
            currentRound: 0,
            maxRounds: 13, // 默认值，将从后端获取
            currentSpeakerId: null,
            messages: [],
            
            // CEO发言相关
            waitingForCeo: false,
            
            // UI状态
            loading: false,
            loadingText: '加载中...',
            isThinking: false,
            showSummary: false,
            summary: '',
            
            // WebSocket
            socket: null,
            
            // API配置 - 使用相对路径自动适应当前域名
            apiBase: '',
            
            // 系统状态
            systemStatus: {
                backendConnected: false,
                lastHealthCheck: null,
                connectionRetries: 0,
                maxRetries: 3,
                serverUrl: window.location.origin, // 当前服务器地址
                apiBaseUrl: '' // API基础URL（相对路径）
            },
            
            // 日志配置
            enableDebugLogs: true,
            logLevel: 'info' // debug, info, warn, error
        };
    },
    
    computed: {
        canStartMeeting() {
            // 检查是否所有必填项都已填写
            if (!this.config.topic || !this.config.background) {
                return false;
            }
            
            // 检查CEO描述
            if (!this.config.agents[0].description) {
                return false;
            }
            
            // 检查其他三个智能体
            for (let i = 1; i < 4; i++) {
                if (!this.config.agents[i].role || !this.config.agents[i].description) {
                    return false;
                }
            }
            
            return true;
        },
        
        roundProgress() {
            // 使用从后端获取的maxRounds配置
            if (this.maxRounds <= 0) return 0;
            return Math.min((this.currentRound / this.maxRounds) * 100, 100);
        },
        
        isNearMaxRounds() {
            // 使用从后端获取的maxRounds配置
            if (this.maxRounds <= 0) return false;
            return this.currentRound >= this.maxRounds * 0.8; // 达到80%时提醒
        }
    },
    
    methods: {
        // 获取最大轮次配置（已废弃，现在直接从maxRounds属性获取）
        getMaxRounds() {
            // 返回当前的最大轮次配置
            return this.maxRounds;
        },

        // 初始化系统状态
        initializeSystemStatus() {
            this.log('info', '初始化系统状态');
            
            // 设置服务器URL和API基础URL
            this.systemStatus.serverUrl = window.location.origin;
            this.systemStatus.apiBaseUrl = this.apiBase;
            
            // 记录当前环境信息
            this.log('info', '系统状态初始化完成', {
                serverUrl: this.systemStatus.serverUrl,
                apiBaseUrl: this.systemStatus.apiBaseUrl,
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            });
            
            // 显示系统信息（仅在调试模式）
            if (this.enableDebugLogs && this.logLevel === 'debug') {
                this.showNotification(`系统已启动: ${this.systemStatus.serverUrl}`, 'info');
            }
        },
        
        // 日志记录方法
        log(level, message, data = null) {
            if (!this.enableDebugLogs) return;
            
            const levels = { debug: 0, info: 1, warn: 2, error: 3 };
            const currentLevel = levels[this.logLevel] || 1;
            const messageLevel = levels[level] || 1;
            
            if (messageLevel >= currentLevel) {
                const timestamp = new Date().toISOString();
                const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
                
                if (data) {
                    console.log(logMessage, data);
                } else {
                    console.log(logMessage);
                }
            }
        },
        
        // 健康检查方法
        async checkBackendHealth() {
            try {
                this.log('debug', '开始健康检查');
                const response = await fetch(`${this.apiBase}/api/health`, {
                    method: 'GET',
                    timeout: 5000
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.systemStatus.backendConnected = true;
                    this.systemStatus.lastHealthCheck = new Date();
                    this.systemStatus.connectionRetries = 0;
                    this.log('info', '后端健康检查成功', data);
                    return true;
                } else {
                    throw new Error(`健康检查失败: ${response.status}`);
                }
            } catch (error) {
                this.systemStatus.backendConnected = false;
                this.systemStatus.connectionRetries++;
                this.log('error', '后端健康检查失败', error);
                
                if (this.systemStatus.connectionRetries >= this.systemStatus.maxRetries) {
                    this.showNotification('后端服务连接失败，请检查服务器状态', 'error');
                }
                return false;
            }
        },
        
        // 带重试的API调用
        async apiCall(url, options = {}, retries = 3) {
            for (let i = 0; i < retries; i++) {
                try {
                    this.log('debug', `API调用: ${url}`, { attempt: i + 1, options });
                    
                    const response = await fetch(url, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            ...options.headers
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    this.log('debug', `API调用成功: ${url}`, data);
                    return data;
                    
                } catch (error) {
                    this.log('warn', `API调用失败: ${url}`, { attempt: i + 1, error: error.message });
                    
                    if (i === retries - 1) {
                        throw error;
                    }
                    
                    // 等待后重试
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                }
            }
        },
        
        async startMeeting() {
            this.loading = true;
            this.loadingText = '正在初始化智能体...';
            this.log('info', '开始启动会议');
            
            try {
                // 验证配置
                if (!this.validateConfig()) {
                    this.loading = false;
                    return;
                }
                
                // 检查后端健康状态
                const isHealthy = await this.checkBackendHealth();
                if (!isHealthy) {
                    throw new Error('后端服务不可用');
                }
                
                const data = await this.apiCall(`${this.apiBase}/api/start_meeting`, {
                    method: 'POST',
                    body: JSON.stringify({
                        topic: this.config.topic.trim(),
                        background: this.config.background.trim(),
                        agents: this.config.agents.map(agent => ({
                            role: agent.role.trim(),
                            description: agent.description.trim()
                        }))
                    })
                });
                
                if (data.status === 'success') {
                    this.meetingStarted = true;
                    this.initializeWebSocket();
                    // 会议开始，CEO先发言
                    this.currentSpeakerId = 0;
                    this.isThinking = true;
                    
                    // 获取会议状态以获取最大轮次信息
                    await this.getMeetingStatus();
                    
                    this.startCeoSpeak();
                    
                    this.log('info', '会议启动成功', { 
                        maxRounds: this.maxRounds, 
                        currentRound: this.currentRound 
                    });
                    this.showNotification('会议启动成功！', 'success');
                } else {
                    throw new Error(data.error || '未知错误');
                }
            } catch (error) {
                this.log('error', '启动会议失败', error);
                this.showNotification('启动会议失败：' + error.message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        validateConfig() {
            const errors = [];
            
            if (!this.config.topic.trim()) {
                errors.push('会议主题不能为空');
            }
            
            if (!this.config.background.trim()) {
                errors.push('会议背景不能为空');
            }
            
            if (!this.config.agents[0].description.trim()) {
                errors.push('CEO描述不能为空');
            }
            
            for (let i = 1; i < this.config.agents.length; i++) {
                const agent = this.config.agents[i];
                if (!agent.role.trim()) {
                    errors.push(`智能体${i + 1}的角色名称不能为空`);
                }
                if (!agent.description.trim()) {
                    errors.push(`智能体${i + 1}的角色描述不能为空`);
                }
            }
            
            if (errors.length > 0) {
                this.showNotification(errors.join('；'), 'error');
                return false;
            }
            
            return true;
        },
        
        showNotification(message, type = 'info') {
            // 创建通知元素
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            notification.setAttribute('role', 'alert');
            notification.setAttribute('aria-live', 'polite');
            
            // 添加样式
            Object.assign(notification.style, {
                position: 'fixed',
                top: '20px',
                right: '20px',
                padding: '16px 24px',
                borderRadius: '8px',
                color: 'white',
                fontWeight: '500',
                zIndex: '3000',
                maxWidth: '400px',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
                transform: 'translateX(100%)',
                transition: 'transform 0.3s ease-out',
                backgroundColor: type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#667eea'
            });
            
            document.body.appendChild(notification);
            
            // 显示动画
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // 自动隐藏
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 4000);
        },
        
        initializeWebSocket() {
            this.log('info', '初始化WebSocket连接');
            
            // 如果已经存在连接，先断开
            if (this.socket) {
                this.log('info', '断开现有WebSocket连接');
                this.socket.disconnect();
                this.socket = null;
            }
            
            try {
                // 优化WebSocket连接配置
                this.socket = io(this.apiBase, {
                    // 传输协议优先级：先尝试websocket，失败后回退到polling
                    transports: ['websocket', 'polling'],
                    
                    // 连接超时时间
                    timeout: 30000,
                    
                    // 强制创建新连接
                    forceNew: true,
                    
                    // 重连配置
                    reconnection: true,
                    reconnectionAttempts: 10, // 增加重连尝试次数
                    reconnectionDelay: 1000, // 初始重连延迟
                    reconnectionDelayMax: 5000, // 最大重连延迟
                    randomizationFactor: 0.5, // 随机化因子避免重连风暴
                    
                    // Engine.IO 配置
                    upgrade: true, // 允许传输协议升级
                    rememberUpgrade: false, // 不记住升级，避免缓存问题
                    path: '/socket.io/', // 明确指定路径
                    
                    // 超时配置
                    pingTimeout: 60000, // ping超时时间
                    pingInterval: 25000, // ping间隔时间
                    
                    // 调试配置
                    autoConnect: true, // 自动连接
                    multiplex: false, // 禁用多路复用，避免连接冲突
                    
                    // 安全配置
                    withCredentials: false, // 禁用凭据，简化跨域
                    transports: ['websocket', 'polling'] // 再次确保传输协议
                });
                
                // 连接成功事件
                this.socket.on('connect', () => {
                    this.log('info', 'WebSocket连接成功', { 
                        socketId: this.socket.id,
                        transport: this.socket.io.engine.transport.name 
                    });
                    this.showNotification('实时连接已建立', 'success');
                });
                
                // 连接断开事件
                this.socket.on('disconnect', (reason) => {
                    this.log('warn', 'WebSocket连接断开', { 
                        reason,
                        wasConnecting: this.socket.io.engine?.priorTransport?.name
                    });
                    
                    // 根据断开原因显示不同的提示
                    if (reason === 'io server disconnect') {
                        this.showNotification('服务器主动断开连接，正在重新连接...', 'warn');
                    } else if (reason === 'transport close') {
                        this.showNotification('网络连接中断，正在尝试重连...', 'error');
                    } else if (reason === 'ping timeout') {
                        this.showNotification('连接超时，正在重新建立连接...', 'warn');
                    } else {
                        this.showNotification('连接已断开，正在尝试重连...', 'error');
                    }
                });
                
                // 连接错误事件
                this.socket.on('connect_error', (error) => {
                    this.log('error', 'WebSocket连接错误', { 
                        error: error.message,
                        type: error.type,
                        description: error.description
                    });
                    
                    // 根据错误类型显示不同的提示
                    if (error.message.includes('Invalid frame header')) {
                        this.showNotification('WebSocket协议错误，正在尝试降级连接...', 'error');
                        // 强制使用polling传输
                        if (this.socket.io) {
                            this.socket.io.opts.transports = ['polling'];
                        }
                    } else if (error.message.includes('Network')) {
                        this.showNotification('网络连接失败，请检查网络设置', 'error');
                    } else if (error.message.includes('timeout')) {
                        this.showNotification('连接超时，正在重新尝试...', 'warn');
                    } else {
                        this.showNotification('连接失败，请检查网络状态', 'error');
                    }
                });
                
                // 重连尝试事件
                this.socket.io.on('reconnect_attempt', (attemptNumber) => {
                    this.log('info', 'WebSocket重连尝试', { attemptNumber });
                    this.showNotification(`正在尝试重新连接 (${attemptNumber}/10)...`, 'warn');
                });
                
                // 重连成功事件
                this.socket.io.on('reconnect', () => {
                    this.log('info', 'WebSocket重连成功');
                    this.showNotification('连接已恢复', 'success');
                });
                
                // 重连失败事件
                this.socket.io.on('reconnect_failed', () => {
                    this.log('error', 'WebSocket重连失败');
                    this.showNotification('无法建立连接，请刷新页面重试', 'error');
                });
                
                // 消息接收事件
                this.socket.on('new_message', (message) => {
                    this.log('debug', '收到新消息', message);
                    this.handleNewMessage(message);
                });
                
                // 其他错误事件
                this.socket.on('error', (error) => {
                    this.log('error', 'WebSocket错误', error);
                    this.showNotification('连接出现错误，正在尝试恢复...', 'error');
                });
                
                // 监听传输协议变化
                if (this.socket.io.engine) {
                    this.socket.io.engine.on('upgrade', (transport) => {
                        this.log('info', 'WebSocket传输协议升级', { from: this.socket.io.engine.priorTransport?.name, to: transport.name });
                    });
                }
                
            } catch (error) {
                this.log('error', 'WebSocket初始化失败', error);
                this.showNotification('实时连接初始化失败，请刷新页面重试', 'error');
                
                // 初始化失败后，尝试降级到仅使用polling
                setTimeout(() => {
                    this.log('info', '尝试降级到HTTP长轮询连接');
                    try {
                        this.socket = io(this.apiBase, {
                            transports: ['polling'],
                            timeout: 30000,
                            forceNew: true,
                            reconnection: true,
                            reconnectionAttempts: 5,
                            reconnectionDelay: 2000
                        });
                        
                        this.socket.on('connect', () => {
                            this.log('info', '降级连接成功');
                            this.showNotification('已切换到备用连接模式', 'success');
                        });
                        
                        this.socket.on('new_message', (message) => {
                            this.log('debug', '收到新消息（降级模式）', message);
                            this.handleNewMessage(message);
                        });
                        
                    } catch (fallbackError) {
                        this.log('error', '降级连接也失败', fallbackError);
                        this.showNotification('无法建立任何连接，请检查网络和服务器状态', 'error');
                    }
                }, 2000);
            }
        },
        
        async getMeetingStatus() {
            try {
                const data = await this.apiCall(`${this.apiBase}/api/meeting_status`, {
                    method: 'GET'
                });
                
                if (data.status === 'success' && data.meeting_state) {
                    // 更新最大轮次配置
                    this.maxRounds = data.meeting_state.max_rounds || 13;
                    // 更新当前轮次
                    this.currentRound = data.meeting_state.current_round || 0;
                    this.log('info', '获取会议状态成功', { 
                        maxRounds: this.maxRounds, 
                        currentRound: this.currentRound 
                    });
                }
            } catch (error) {
                this.log('warn', '获取会议状态失败', error);
                // 如果获取失败，使用默认值并显示警告
                this.maxRounds = 13; // 使用默认值
                this.showNotification('无法获取会议配置，使用默认设置', 'warn');
            }
        },
        
        async startCeoSpeak() {
            // 检查会议是否已结束
            if (this.showSummary || !this.meetingStarted) {
                this.log('info', '会议已结束，停止CEO发言');
                return;
            }
            
            this.log('info', 'CEO开始发言（轮次总结）');
            
            try {
                const data = await this.apiCall(`${this.apiBase}/api/ceo_speak`, {
                    method: 'POST'
                });
                
                if (data.status === 'success') {
                    // 消息已通过WebSocket添加，不需要重复添加
                    this.currentRound = data.current_round;
                    
                    this.log('info', 'CEO发言成功', { 
                        round: data.current_round, 
                        nextSpeaker: data.next_speaker_id,
                        meetingShouldEnd: data.meeting_should_end
                    });
                    
                    // 滚动到底部
                    this.$nextTick(() => {
                        this.scrollToBottom();
                    });
                    
                    // 检查CEO是否想要结束会议
                    if (data.meeting_should_end) {
                        // CEO决定结束会议
                        this.isThinking = false;
                        if (data.forced_end && data.reason === '已达到最大轮次限制') {
                            this.showNotification(`会议已达到最大轮次限制(${this.maxRounds}轮)，CEO正在生成最终总结...`, 'info');
                        } else {
                            this.showNotification('CEO决定结束会议，正在生成总结...', 'info');
                        }
                        setTimeout(() => {
                            this.generateSummary();
                        }, 1000);
                    } else {
                        // 延迟后让下一个智能体发言
                        setTimeout(() => {
                            if (!this.showSummary && this.meetingStarted) {
                                this.nextAgentSpeak(data.next_speaker_id);
                            }
                        }, 1000);
                    }
                } else {
                    // 检查是否是会议结束错误
                    if (data.error && data.error.includes('会议正在结束')) {
                        this.log('info', '会议正在结束，停止CEO发言');
                        this.isThinking = false;
                        return;
                    }
                    throw new Error(data.error || '发言失败');
                }
            } catch (error) {
                this.log('error', 'CEO发言失败', error);
                this.showNotification('CEO发言失败：' + error.message, 'error');
                this.isThinking = false;
                // 如果CEO发言失败，尝试继续会议流程
                if (!this.showSummary && this.meetingStarted) {
                    setTimeout(() => {
                        this.nextAgentSpeak(1); // 默认让第一个智能体发言
                    }, 2000);
                }
            }
        },
        
        async nextAgentSpeak(agentId) {
            // 检查会议是否已结束
            if (this.showSummary || !this.meetingStarted) {
                this.log('info', '会议已结束，停止智能体发言', { agentId });
                return;
            }
            
            this.currentSpeakerId = agentId;
            this.isThinking = true;
            this.log('info', '智能体开始发言', { agentId });
            
            try {
                const data = await this.apiCall(`${this.apiBase}/api/agent_speak/${agentId}`, {
                    method: 'POST'
                });
                
                if (data.status === 'success') {
                    // 消息已通过WebSocket添加，不需要重复添加
                    this.currentRound = data.current_round;
                    
                    this.log('info', '智能体发言成功', { 
                        agentId, 
                        round: data.current_round,
                        meetingEnded: data.meeting_ended,
                        nextSpeaker: data.next_speaker_id
                    });
                    
                    this.$nextTick(() => {
                        this.scrollToBottom();
                    });
                    
                    // 检查会议是否结束
                    if (data.meeting_ended) {
                        this.isThinking = false;
                        if (data.forced_end && data.reason === '已达到最大轮次限制') {
                            this.showNotification(`会议已达到最大轮次限制(${this.maxRounds}轮)，CEO正在生成最终总结...`, 'info');
                        } else {
                            this.showNotification('会议已结束，正在生成总结...', 'info');
                        }
                        await this.generateSummary();
                    } else {
                        // 检查轮次是否完成
                        if (data.round_complete) {
                            // 轮次结束，CEO总结
                            setTimeout(() => {
                                if (!this.showSummary && this.meetingStarted) {
                                    this.isThinking = false;
                                    this.currentSpeakerId = 0;
                                    this.startCeoSpeak();
                                }
                            }, 1000);
                        } else {
                            // 继续下一个智能体发言
                            setTimeout(() => {
                                if (!this.showSummary && this.meetingStarted) {
                                    this.nextAgentSpeak(data.next_speaker_id);
                                }
                            }, 1000);
                        }
                    }
                } else {
                    // 检查是否是达到最大轮次限制的情况
                    if (data.should_ceo_speak && data.reason === '达到最大轮次限制') {
                        this.log('info', '达到最大轮次限制，触发CEO最终总结', data);
                        this.showNotification(`已达到最大轮次限制(${this.maxRounds}轮)，CEO将进行最终总结...`, 'info');
                        this.isThinking = false;
                        this.currentSpeakerId = 0;
                        setTimeout(() => {
                            if (!this.showSummary && this.meetingStarted) {
                                this.startCeoSpeak();
                            }
                        }, 1000);
                        return;
                    }
                    
                    // 检查是否是会议结束错误
                    if (data.error && data.error.includes('会议正在结束')) {
                        this.log('info', '会议正在结束，停止智能体发言');
                        this.isThinking = false;
                        return;
                    }
                    throw new Error(data.error || '发言失败');
                }
            } catch (error) {
                this.log('error', '智能体发言失败', { agentId, error });
                this.showNotification('智能体发言失败：' + error.message, 'error');
                this.isThinking = false;
                // 尝试继续会议
                setTimeout(() => {
                    if (!this.showSummary && this.meetingStarted) {
                        this.waitingForCeo = true;
                        this.currentSpeakerId = 0;
                        this.startCeoTimer();
                    }
                }, 2000);
            }
        },
        
        async restartMeeting() {
            if (!confirm('确定要重新开始会议吗？当前会议将被清空，不会保存记录。')) {
                return;
            }
            
            // 立即停止智能体发言流程
            this.waitingForCeo = false;
            this.isThinking = false;
            this.currentSpeakerId = null;
            
            this.loading = true;
            this.loadingText = '正在重启会议...';
            
            this.log('info', '用户手动重启会议，停止所有发言流程');
            
            try {
                const data = await this.apiCall(`${this.apiBase}/api/restart_meeting`, {
                    method: 'POST'
                });
                
                if (data.status === 'success') {
                    // 重置所有前端状态
                    this.meetingStarted = false;
                    this.currentRound = 0;
                    this.maxRounds = 13; // 重置为默认值
                    this.currentSpeakerId = null;
                    this.messages = [];
                    this.waitingForCeo = false;
                    this.isThinking = false;
                    this.showSummary = false;
                    this.summary = '';
                    
                    // 清空配置（可选，用户可能想保留配置）
                    // this.config.topic = '';
                    // this.config.background = '';
                    // this.config.agents = [
                    //     { role: 'CEO', description: '' },
                    //     { role: '', description: '' },
                    //     { role: '', description: '' },
                    //     { role: '', description: '' }
                    // ];
                    
                    this.log('info', '会议重启成功，返回配置页面');
                    this.showNotification('会议已重启，可以重新开始！', 'success');
                } else {
                    throw new Error(data.error || '重启会议失败');
                }
            } catch (error) {
                this.log('error', '重启会议失败', error);
                this.showNotification('重启会议失败：' + error.message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async endMeeting() {
            if (!confirm('确定要结束会议吗？会议记录将被保存。')) {
                return;
            }
            
            // 立即停止智能体发言流程
            this.waitingForCeo = false;
            this.isThinking = false;
            this.currentSpeakerId = null;
            
            this.loading = true;
            this.loadingText = '正在结束会议并生成总结...';
            
            this.log('info', '用户手动结束会议，停止所有发言流程');
            
            await this.generateSummary();
        },
        
        async generateSummary() {
            this.log('info', '开始生成会议总结');
            try {
                // 确保停止所有发言流程
                this.waitingForCeo = false;
                this.isThinking = false;
                this.currentSpeakerId = null;
                
                const data = await this.apiCall(`${this.apiBase}/api/end_meeting`, {
                    method: 'POST'
                });
                
                if (data.status === 'success') {
                    this.summary = data.summary;
                    this.showSummary = true;
                    this.log('info', '会议总结生成成功');
                    this.showNotification('会议总结生成成功！', 'success');
                } else {
                    throw new Error(data.error || '生成总结失败');
                }
            } catch (error) {
                this.log('error', '生成总结失败', error);
                this.showNotification('生成总结失败：' + error.message, 'error');
            } finally {
                this.loading = false;
            }
        },
        
        async downloadTranscript() {
            this.log('info', '开始下载会议记录');
            try {
                this.showNotification('正在准备下载...', 'info');
                const response = await fetch(`${this.apiBase}/api/download_transcript`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `meeting_transcript_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.log('info', '会议记录下载成功');
                this.showNotification('会议记录下载成功！', 'success');
            } catch (error) {
                this.log('error', '下载失败', error);
                this.showNotification('下载失败：' + error.message, 'error');
            }
        },
        
        closeSummary() {
            this.showSummary = false;
        },
        
        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },
        
        scrollToBottom() {
            const container = this.$refs.messagesContainer;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        },
        
        getCurrentSpeakerName() {
            if (this.currentSpeakerId === 0) {
                return 'CEO';
            }
            // 从配置中获取智能体信息
            const agent = this.config.agents[this.currentSpeakerId];
            return agent ? agent.role : '智能体';
        },
        
        
        // 键盘导航支持
        handleKeydown(event) {
            // ESC键关闭模态框
            if (event.key === 'Escape') {
                if (this.showSummary) {
                    this.closeSummary();
                }
            }
        },

        // 处理Unicode转义字符
        decodeUnicodeString(str) {
            if (!str || typeof str !== 'string') {
                return str;
            }
            
            try {
                // 方法1：使用JSON.parse处理Unicode转义字符
                if (str.includes('\\u')) {
                    return JSON.parse('"' + str + '"');
                }
                return str;
            } catch (error) {
                try {
                    // 方法2：手动替换Unicode转义字符
                    return str.replace(/\\u[\dA-Fa-f]{4}/g, (match) => {
                        return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
                    });
                } catch (error2) {
                    this.log('warn', 'Unicode字符解析失败，使用原始内容', error2);
                    return str;
                }
            }
        },

        // 处理新消息
        handleNewMessage(message) {
            this.log('info', '收到新消息', message);
            
            // 检查消息是否已存在（防止重复）
            if (message.message_id) {
                const existingMessage = this.messages.find(msg => msg.message_id === message.message_id);
                if (existingMessage) {
                    this.log('warn', '检测到重复消息ID，跳过处理', message);
                    return;
                }
            } else {
                // 如果没有message_id，使用旧的方法检查
                const existingMessage = this.messages.find(msg => 
                    msg.agent_id === message.agent_id && 
                    msg.content === message.content && 
                    Math.abs(msg.timestamp - message.timestamp) < 1000
                );
                
                if (existingMessage) {
                    this.log('warn', '检测到重复消息，跳过处理', message);
                    return;
                }
            }
            
            // 处理消息内容中的Unicode转义字符
            if (message.content && typeof message.content === 'string') {
                message.content = this.decodeUnicodeString(message.content);
            }
            
            // 直接添加消息到列表（一次性显示）
            this.messages.push(message);
            
            // 更新当前发言者
            this.currentSpeakerId = message.agent_id;
            
            // 滚动到底部
            this.$nextTick(() => {
                this.scrollToBottom();
            });
            
            // 检查是否会议结束
            if (message.meeting_ended) {
                this.log('info', '会议已结束');
                this.endMeeting();
            }
        },

        // CEO定时器管理
        startCeoTimer() {
            this.log('info', '启动CEO定时器');
            
            // 清除现有定时器
            if (this.ceoTimer) {
                clearInterval(this.ceoTimer);
                this.ceoTimer = null;
            }
            
            // 设置新的定时器，定期检查会议状态
            this.ceoTimer = setInterval(() => {
                this.checkMeetingStatus();
            }, 5000); // 每5秒检查一次
            
            // 立即执行一次检查
            this.checkMeetingStatus();
        },

        // 停止CEO定时器
        stopCeoTimer() {
            this.log('info', '停止CEO定时器');
            
            if (this.ceoTimer) {
                clearInterval(this.ceoTimer);
                this.ceoTimer = null;
            }
        },

        // 检查会议状态
        async checkMeetingStatus() {
            try {
                const data = await this.apiCall(`${this.apiBase}/api/meeting_status`, {
                    method: 'GET'
                });
                
                if (data.status === 'success' && data.meeting_state) {
                    this.log('debug', '会议状态检查成功', data.meeting_state);
                    
                    // 如果会议已结束但前端未更新，则更新状态
                    if (data.meeting_state.status === 'ended' && !this.showSummary) {
                        this.log('info', '检测到会议已结束，更新前端状态');
                        this.stopCeoTimer();
                        this.isThinking = false;
                        this.currentSpeakerId = null;
                        this.waitingForCeo = false;
                        this.generateSummary();
                    }
                }
            } catch (error) {
                this.log('warn', '检查会议状态失败', error);
            }
        },

    },
    
    mounted() {
        // 初始化系统状态
        this.initializeSystemStatus();
        
        // 添加键盘事件监听
        document.addEventListener('keydown', this.handleKeydown);
        
        // 设置页面标题
        document.title = '多智能体会议系统 - CAMEL-AI 智能协作平台';
        
        // 初始化时检查后端健康状态并获取配置
        this.checkBackendHealth().then(() => {
            // 健康检查成功后获取会议配置
            this.getMeetingStatus();
        }).catch(() => {
            // 如果健康检查失败，使用默认配置
            this.maxRounds = 13;
            this.log('warn', '后端健康检查失败，使用默认最大轮次配置', { maxRounds: this.maxRounds });
        });
        
        // 定期健康检查
        setInterval(() => {
            this.checkBackendHealth();
        }, 30000); // 每30秒检查一次
    },
    
        beforeUnmount() {
            // 断开WebSocket连接
            if (this.socket) {
                this.socket.disconnect();
            }
            
            // 停止CEO定时器
            this.stopCeoTimer();
            
            // 移除键盘事件监听
            document.removeEventListener('keydown', this.handleKeydown);
        }
}).mount('#app');
