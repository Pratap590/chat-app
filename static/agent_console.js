class AgentConsole {
    constructor() {
        this.currentSessionId = null;
        this.isTakenOver = false;
        this.sessions = new Map();
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadSessions();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendAgentMessage();
        });

        // Auto-resize textarea
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = chatInput.scrollHeight + 'px';
        });
    }

    async loadSessions() {
        try {
            const response = await fetch('/api/admin/sessions');
            const data = await response.json();
            
            this.sessions.clear();
            data.sessions.forEach(session => {
                this.sessions.set(session.session_id, session);
            });
            
            this.renderSessionList();
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }

    renderSessionList() {
        const sessionList = document.getElementById('sessionList');
        sessionList.innerHTML = '';

        if (this.sessions.size === 0) {
            sessionList.innerHTML = '<li style="color: #a0aec0; text-align: center; padding: 20px;">No active sessions</li>';
            return;
        }

        this.sessions.forEach((session, sessionId) => {
            const sessionItem = document.createElement('li');
            sessionItem.className = `session-item ${sessionId === this.currentSessionId ? 'active' : ''}`;
            sessionItem.onclick = () => this.selectSession(sessionId);

            const statusClass = this.getSessionStatusClass(session);
            const timeAgo = this.getTimeAgo(session.last_activity);

            sessionItem.innerHTML = `
                <div class="session-status ${statusClass}"></div>
                <div class="session-info">
                    <div class="session-tenant">${session.tenant_id}</div>
                    <div class="session-time">${timeAgo}</div>
                </div>
            `;

            sessionList.appendChild(sessionItem);
        });
    }

    getSessionStatusClass(session) {
        // This would be enhanced with real status logic
        const lastActivity = new Date(session.last_activity);
        const now = new Date();
        const minutesAgo = (now - lastActivity) / (1000 * 60);

        if (minutesAgo < 5) return 'status-active';
        if (minutesAgo < 30) return 'status-waiting';
        return 'status-escalated';
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMins / 60);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return time.toLocaleDateString();
    }

    async selectSession(sessionId) {
        this.currentSessionId = sessionId;
        const session = this.sessions.get(sessionId);
        
        if (!session) return;

        // Update UI
        this.renderSessionList();
        this.updateSessionDetails(session);
        await this.loadChatHistory(sessionId);
        
        // Show chat interface
        document.getElementById('chatActions').style.display = 'flex';
        document.getElementById('chatInputContainer').style.display = 'block';
        document.getElementById('chatTitle').textContent = `Session: ${sessionId.substring(0, 8)}...`;
    }

    updateSessionDetails(session) {
        document.getElementById('detailSessionId').textContent = session.session_id.substring(0, 16) + '...';
        document.getElementById('detailTenant').textContent = session.tenant_id;
        document.getElementById('detailUser').textContent = session.user_id || 'Anonymous';
        document.getElementById('detailStarted').textContent = new Date(session.created_at).toLocaleString();
        document.getElementById('detailLastActivity').textContent = new Date(session.last_activity).toLocaleString();
        document.getElementById('detailStatus').textContent = session.status || 'Active';
    }

    async loadChatHistory(sessionId) {
        try {
            const response = await fetch(`/api/admin/sessions/${sessionId}/messages`);
            const data = await response.json();
            
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';

            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    this.addMessageToChat(message.content, message.role, message.timestamp);
                });
            } else {
                chatMessages.innerHTML = '<div style="text-align: center; color: #a0aec0; padding: 20px;">No messages yet</div>';
            }

            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading chat history:', error);
            document.getElementById('chatMessages').innerHTML = '<div style="text-align: center; color: #f56565; padding: 20px;">Error loading messages</div>';
        }
    }

    addMessageToChat(content, role, timestamp) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatarClass = role === 'user' ? 'avatar-user' : role === 'agent' ? 'avatar-agent' : 'avatar-bot';
        const avatarIcon = role === 'user' ? 'U' : role === 'agent' ? 'A' : 'B';

        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">${avatarIcon}</div>
            <div class="message-content">
                ${content}
                <div class="message-time">${new Date(timestamp).toLocaleTimeString()}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
    }

    async sendAgentMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message || !this.currentSessionId) return;

        // Add message to chat immediately
        this.addMessageToChat(message, 'agent', new Date().toISOString());
        input.value = '';
        input.style.height = 'auto';

        try {
            const response = await fetch('/api/agent/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    message: message,
                    agent_id: 'console_agent'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            this.scrollToBottom();
        } catch (error) {
            console.error('Error sending message:', error);
            this.showNotification('Failed to send message', 'error');
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    startRealTimeUpdates() {
        // Poll for updates every 5 seconds
        setInterval(() => {
            this.loadSessions();
            if (this.currentSessionId) {
                this.loadChatHistory(this.currentSessionId);
            }
        }, 5000);
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10001;
            background: ${type === 'success' ? '#48bb78' : '#f56565'};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Global functions for HTML onclick handlers
function takeoverChat() {
    if (!agentConsole.currentSessionId) return;
    
    agentConsole.isTakenOver = true;
    document.getElementById('takeoverBtn').style.display = 'none';
    document.getElementById('endTakeoverBtn').style.display = 'inline-block';
    document.getElementById('takeoverNotice').style.display = 'block';
    
    agentConsole.showNotification('Chat takeover activated', 'success');
}

function endTakeover() {
    agentConsole.isTakenOver = false;
    document.getElementById('takeoverBtn').style.display = 'inline-block';
    document.getElementById('endTakeoverBtn').style.display = 'none';
    document.getElementById('takeoverNotice').style.display = 'none';
    
    agentConsole.showNotification('Chat takeover ended', 'success');
}

function escalateSession() {
    const form = document.getElementById('escalationForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function submitEscalation() {
    const title = document.getElementById('escalationTitle').value;
    const priority = document.getElementById('escalationPriority').value;
    const description = document.getElementById('escalationDescription').value;
    
    if (!title || !description) {
        agentConsole.showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    // TODO: Implement escalation submission
    agentConsole.showNotification('Escalation ticket created', 'success');
    cancelEscalation();
}

function cancelEscalation() {
    document.getElementById('escalationForm').style.display = 'none';
    document.getElementById('escalationTitle').value = '';
    document.getElementById('escalationDescription').value = '';
}

function scheduleCallback() {
    agentConsole.showNotification('Callback scheduling feature coming soon!', 'info');
}

function sendTemplate() {
    agentConsole.showNotification('Template feature coming soon!', 'info');
}

function transferSession() {
    agentConsole.showNotification('Session transfer feature coming soon!', 'info');
}

function endSession() {
    if (confirm('Are you sure you want to end this session?')) {
        agentConsole.showNotification('Session ended', 'success');
    }
}

// Initialize console when page loads
let agentConsole;
document.addEventListener('DOMContentLoaded', () => {
    agentConsole = new AgentConsole();
});
