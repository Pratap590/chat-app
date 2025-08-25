class AdminDashboard {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
        this.checkLangSmithStatus();
        setInterval(() => this.refreshData(), 30000); // Refresh every 30 seconds
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadStats(),
                this.loadTenants(),
                this.loadSessions(),
                this.loadTickets()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/admin/stats');
            const data = await response.json();
            
            document.getElementById('totalTenants').textContent = data.total_tenants || 0;
            document.getElementById('activeSessions').textContent = data.active_sessions || 0;
            document.getElementById('totalDocuments').textContent = data.total_documents || 0;
            document.getElementById('openTickets').textContent = data.open_tickets || 0;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadTenants() {
        try {
            const response = await fetch('/api/admin/tenants');
            const data = await response.json();
            
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Tenant ID</th>
                            <th>Name</th>
                            <th>Status</th>
                            <th>Documents</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.tenants.map(tenant => `
                            <tr>
                                <td>${tenant.tenant_id}</td>
                                <td>${tenant.name}</td>
                                <td><span class="status-badge ${tenant.is_active ? 'status-active' : 'status-inactive'}">
                                    ${tenant.is_active ? 'Active' : 'Inactive'}
                                </span></td>
                                <td>${tenant.document_count || 0}</td>
                                <td>
                                    <button class="btn btn-secondary" onclick="adminDashboard.editTenant('${tenant.tenant_id}')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-danger" onclick="adminDashboard.deleteTenant('${tenant.tenant_id}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            document.getElementById('tenantsTable').innerHTML = tableHtml;
            
            // Update customization tenant dropdown
            const select = document.getElementById('customizationTenant');
            select.innerHTML = '<option value="">Select a tenant...</option>' +
                data.tenants.map(tenant => `<option value="${tenant.tenant_id}">${tenant.name}</option>`).join('');
                
        } catch (error) {
            console.error('Error loading tenants:', error);
        }
    }

    async loadSessions() {
        try {
            const response = await fetch('/api/admin/sessions');
            const data = await response.json();
            
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Tenant</th>
                            <th>User</th>
                            <th>Status</th>
                            <th>Last Activity</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.sessions.map(session => `
                            <tr>
                                <td>${session.session_id.substring(0, 8)}...</td>
                                <td>${session.tenant_id}</td>
                                <td>${session.user_id || 'Anonymous'}</td>
                                <td><span class="status-badge status-active">${session.status}</span></td>
                                <td>${new Date(session.last_activity).toLocaleString()}</td>
                                <td>
                                    <button class="btn btn-secondary" onclick="adminDashboard.viewSession('${session.session_id}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-danger" onclick="adminDashboard.terminateSession('${session.session_id}')">
                                        <i class="fas fa-stop"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            document.getElementById('sessionsTable').innerHTML = tableHtml;
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }

    async loadTickets() {
        try {
            const response = await fetch('/api/admin/tickets');
            const data = await response.json();
            
            const tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Ticket ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.tickets.map(ticket => `
                            <tr>
                                <td>${ticket.ticket_id.substring(0, 8)}...</td>
                                <td>${ticket.title}</td>
                                <td><span class="status-badge ${ticket.status === 'open' ? 'status-pending' : 'status-active'}">
                                    ${ticket.status}
                                </span></td>
                                <td>${ticket.priority}</td>
                                <td>${new Date(ticket.created_at).toLocaleString()}</td>
                                <td>
                                    <button class="btn btn-secondary" onclick="adminDashboard.viewTicket('${ticket.ticket_id}')">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn" onclick="adminDashboard.assignTicket('${ticket.ticket_id}')">
                                        <i class="fas fa-user-plus"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            document.getElementById('ticketsTable').innerHTML = tableHtml;
        } catch (error) {
            console.error('Error loading tickets:', error);
        }
    }

    async checkLangSmithStatus() {
        try {
            const response = await fetch('/api/admin/langsmith-status');
            const data = await response.json();
            
            const statusElement = document.getElementById('langsmithStatus');
            if (data.enabled) {
                statusElement.innerHTML = '<span style="color: green;">✅ Connected</span>';
                statusElement.innerHTML += ` - Project: ${data.project}`;
            } else {
                statusElement.innerHTML = '<span style="color: red;">❌ Disabled</span>';
            }
        } catch (error) {
            document.getElementById('langsmithStatus').innerHTML = '<span style="color: red;">❌ Error</span>';
        }
    }

    setupEventListeners() {
        // Create tenant form
        document.getElementById('createTenantForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.createTenant();
        });

        // Customization tenant selection
        document.getElementById('customizationTenant').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadTenantCustomization(e.target.value);
            }
        });
    }

    async createTenant() {
        const tenantId = document.getElementById('newTenantId').value;
        const tenantName = document.getElementById('newTenantName').value;
        const permissions = Array.from(document.querySelectorAll('#createTenantForm input[type="checkbox"]:checked'))
            .map(cb => cb.value);

        try {
            const response = await fetch('/api/admin/tenants', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tenant_id: tenantId,
                    name: tenantName,
                    permissions: permissions
                })
            });

            if (response.ok) {
                this.closeModal('createTenantModal');
                await this.loadTenants();
                await this.loadStats();
                this.showNotification('Tenant created successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Failed to create tenant', 'error');
            }
        } catch (error) {
            this.showNotification('Error creating tenant', 'error');
        }
    }

    async loadTenantCustomization(tenantId) {
        try {
            const response = await fetch(`/api/admin/tenants/${tenantId}/customization`);
            const data = await response.json();
            
            document.getElementById('themeColor').value = data.theme_color || '#667eea';
            document.getElementById('chatBgColor').value = data.chat_background_color || '#ffffff';
            document.getElementById('welcomeMessage').value = data.welcome_message || 'Hello! How can I help you today?';
        } catch (error) {
            console.error('Error loading tenant customization:', error);
        }
    }

    async saveCustomization() {
        const tenantId = document.getElementById('customizationTenant').value;
        if (!tenantId) {
            this.showNotification('Please select a tenant first', 'error');
            return;
        }

        const customization = {
            theme_color: document.getElementById('themeColor').value,
            chat_background_color: document.getElementById('chatBgColor').value,
            welcome_message: document.getElementById('welcomeMessage').value
        };

        try {
            const response = await fetch(`/api/admin/tenants/${tenantId}/customization`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(customization)
            });

            if (response.ok) {
                this.showNotification('Customization saved successfully!', 'success');
            } else {
                this.showNotification('Failed to save customization', 'error');
            }
        } catch (error) {
            this.showNotification('Error saving customization', 'error');
        }
    }

    async refreshData() {
        await this.loadDashboardData();
    }

    async refreshSessions() {
        await this.loadSessions();
    }

    async refreshTickets() {
        await this.loadTickets();
    }

    showNotification(message, type) {
        // Create notification element
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
            z-index: 1001;
            background: ${type === 'success' ? '#48bb78' : '#f56565'};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    // Placeholder methods for future implementation
    async editTenant(tenantId) {
        this.showNotification('Edit tenant feature coming soon!', 'info');
    }

    async deleteTenant(tenantId) {
        if (confirm(`Are you sure you want to delete tenant ${tenantId}?`)) {
            this.showNotification('Delete tenant feature coming soon!', 'info');
        }
    }

    async viewSession(sessionId) {
        this.showNotification('View session feature coming soon!', 'info');
    }

    async terminateSession(sessionId) {
        if (confirm('Are you sure you want to terminate this session?')) {
            this.showNotification('Terminate session feature coming soon!', 'info');
        }
    }

    async viewTicket(ticketId) {
        this.showNotification('View ticket feature coming soon!', 'info');
    }

    async assignTicket(ticketId) {
        this.showNotification('Assign ticket feature coming soon!', 'info');
    }
}

// Global functions for HTML onclick handlers
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

function showCreateTenantModal() {
    document.getElementById('createTenantModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function saveCustomization() {
    adminDashboard.saveCustomization();
}

// Initialize dashboard when page loads
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});

// Export for use in other files
window.AdminDashboard = AdminDashboard;
