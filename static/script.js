// Multi-Agent Chatbot System JavaScript

class ChatbotApp {
    constructor() {
        this.currentAgent = null;
        this.currentTenant = 'default';
        this.selectedFormat = 'pdf';
        this.uploadInProgress = false;
        // State for quick custom API connector (generalized)
        this.customApi = { baseUrl: null, method: 'GET', queryKeys: [], awaitingParams: false };
        this.init();
    }

    init() {
        // Show loading state
        this.showAgentLoadingState();
        this.loadAgents();
        this.loadTenants();
        this.setupEventListeners();

        // Load document list for doc_qa agent
        if (this.currentAgent === 'doc_qa') {
            this.loadDocumentList();
        }
    }

    showAgentLoadingState() {
        const agentGrid = document.getElementById('agentGrid');
        // Only show loading if there are no agents already displayed
        if (!agentGrid.querySelector('.agent-card')) {
            agentGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 15px;"></i>
                    <p>Loading agents...</p>
                </div>
            `;
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');

        // Agent selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.agent-card')) {
                const agentCard = e.target.closest('.agent-card');
                const agentType = agentCard.dataset.agent;
                console.log(`Agent card clicked: ${agentType}`);
                this.selectAgent(agentType);
            }
        });

        // Back to agents
        document.getElementById('backToAgents').addEventListener('click', () => {
            this.showAgentGrid();
        });

        // Chat input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => this.sendMessage());

        // File upload
        this.setupFileUpload();

        // Format selection - initialize from active button
        const activeFormatBtn = document.querySelector('.format-btn.active');
        if (activeFormatBtn) {
            this.selectedFormat = activeFormatBtn.dataset.format;
            console.log('Initial format from active button:', this.selectedFormat);
        }

        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.selectedFormat = e.target.dataset.format;
                console.log('Format selected:', this.selectedFormat);
                this.showNotification(`Format changed to ${this.selectedFormat.toUpperCase()}`, 'info');
            });
        });

        // Tenant management
        document.getElementById('tenantSelect').addEventListener('change', (e) => {
            this.currentTenant = e.target.value;
        });

        document.getElementById('createTenantBtn').addEventListener('click', () => {
            this.showModal('createTenantModal');
        });

        // Modal handling
        this.setupModals();

        // Create tenant form
        document.getElementById('createTenantForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createTenant();
        });

        // Document refresh button
        document.getElementById('refreshDocs').addEventListener('click', () => {
            this.loadDocumentList();
        });

        // Setup Custom API controls if present
        this.setupCustomApiControls();
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            if (response.ok) {
                const agents = await response.json();
                this.renderAgents(agents);
                return;
            }
        } catch (error) {
            console.error('Failed to load agents from API:', error);
        }

        // Fallback: render default agents (for when viewing HTML directly)
        console.log('Loading default agents as fallback');
        this.renderDefaultAgents();
    }

    renderDefaultAgents() {
        const agentGrid = document.getElementById('agentGrid');

        // Check if agents are already displayed
        if (agentGrid.querySelector('.agent-card')) {
            console.log('Agents already displayed, skipping default render');
            return;
        }

        const defaultAgents = {
            "doc_qa": {
                "name": "Document Q&A",
                "description": "Upload documents and ask questions based on their content",
                "icon": "📄",
                "features": ["Document Upload", "RAG Search", "Contextual Answers"]
            },
            "form_gen": {
                "name": "Form Generator",
                "description": "Generate professional forms with PDF/DOC export",
                "icon": "📝",
                "features": ["PDF Export", "DOCX Export", "Professional Templates"]
            },
            "api_exec": {
                "name": "API Executor",
                "description": "Execute API calls and external tool operations",
                "icon": "🔧",
                "features": ["Weather API", "Web Search", "Custom Tools"]
            },
            "analytics": {
                "name": "Analytics",
                "description": "System analytics and data insights",
                "icon": "📊",
                "features": ["Usage Statistics", "Performance Metrics", "Reports"]
            },
            "escalate": {
                "name": "Escalation",
                "description": "Human support and ticket management",
                "icon": "🆘",
                "features": ["Ticket Creation", "Human Handoff", "Support Queue"]
            }
        };
        this.renderAgents(defaultAgents);
    }

    renderAgents(agents) {
        const agentGrid = document.getElementById('agentGrid');

        if (!agents || Object.keys(agents).length === 0) {
            // Don't clear existing agents if API fails
            console.log('No agents from API, keeping existing agents');
            return;
        }

        // Clear and render new agents only if we have valid data
        agentGrid.innerHTML = '';
        Object.entries(agents).forEach(([key, agent]) => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.dataset.agent = key;

            agentCard.innerHTML = `
                <div class="agent-header">
                    <div class="agent-icon">${agent.icon}</div>
                    <div class="agent-info">
                        <h3>${agent.name}</h3>
                        <p>${agent.description}</p>
                    </div>
                </div>
                <ul class="agent-features">
                    ${agent.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
            `;

            agentGrid.appendChild(agentCard);
        });

        console.log(`Rendered ${Object.keys(agents).length} agents from API`);
    }

    async loadTenants() {
        try {
            const response = await fetch('/api/tenants');
            if (response.ok) {
                const data = await response.json();
                const tenantSelect = document.getElementById('tenantSelect');

                tenantSelect.innerHTML = '';
                data.tenants.forEach(tenant => {
                    const option = document.createElement('option');
                    option.value = tenant.tenant_id;
                    option.textContent = tenant.name;
                    tenantSelect.appendChild(option);
                });
                return;
            }
        } catch (error) {
            console.error('Failed to load tenants from API:', error);
        }

        // Fallback: create default tenant option
        const tenantSelect = document.getElementById('tenantSelect');
        tenantSelect.innerHTML = '<option value="default">Default</option>';
    }

    selectAgent(agentType) {
        console.log(`selectAgent called with: ${agentType}`);
        this.currentAgent = agentType;
        console.log(`Current agent set to: ${this.currentAgent}`);
        this.showChatInterface(agentType);
    }

    showChatInterface(agentType) {
        console.log(`showChatInterface called with: ${agentType}`);

        const agentGrid = document.getElementById('agentGrid');
        const chatContainer = document.getElementById('chatContainer');
        const analyticsDashboard = document.getElementById('analyticsDashboard');

        console.log('Elements found:', {
            agentGrid: !!agentGrid,
            chatContainer: !!chatContainer,
            analyticsDashboard: !!analyticsDashboard
        });

        if (agentGrid) agentGrid.style.display = 'none';
        if (chatContainer) chatContainer.style.display = 'flex';
        if (analyticsDashboard) analyticsDashboard.style.display = 'none';

        // Update agent info
        const agentInfo = this.getAgentInfo(agentType);
        document.getElementById('currentAgentIcon').textContent = agentInfo.icon;
        document.getElementById('currentAgentName').textContent = agentInfo.name;

        // Update chat header
        this.updateChatHeader(agentType);

        // Show/hide specific sections
        this.toggleAgentSections(agentType);

        // Clear chat messages
        this.clearChatMessages();

        // Load analytics if analytics agent
        if (agentType === 'analytics') {
            this.loadAnalytics();
        }
    }

    showAgentGrid() {
        document.getElementById('agentGrid').style.display = 'grid';
        document.getElementById('chatContainer').style.display = 'none';
        document.getElementById('analyticsDashboard').style.display = 'none';
        this.currentAgent = null;
    }

    toggleAgentSections(agentType) {
        // Hide all sections first
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('formOptions').style.display = 'none';
        document.getElementById('apiOptions').style.display = 'none';
        document.getElementById('analyticsPreview').style.display = 'none';
        document.getElementById('escalationOptions').style.display = 'none';
        document.getElementById('generatedFiles').style.display = 'none';

        // Show relevant sections based on agent type
        if (agentType === 'doc_qa') {
            document.getElementById('uploadSection').style.display = 'block';
            this.loadDocumentList();
            this.showDocQAWelcome();
        } else if (agentType === 'form_gen') {
            document.getElementById('formOptions').style.display = 'block';
            this.setupFormTemplates();
            this.showFormGenWelcome();
        } else if (agentType === 'api_exec') {
            document.getElementById('apiOptions').style.display = 'block';
            this.setupApiTools();
            this.showApiExecWelcome();
        } else if (agentType === 'analytics') {
            document.getElementById('analyticsPreview').style.display = 'block';
            this.loadQuickStats();
            this.showAnalyticsWelcome();
        } else if (agentType === 'escalate') {
            document.getElementById('escalationOptions').style.display = 'block';
            this.setupEscalationCategories();
            this.showEscalationWelcome();
        }
    }

    getAgentInfo(agentType) {
        const agentMap = {
            'doc_qa': { icon: '📄', name: 'Document Q&A' },
            'form_gen': { icon: '📝', name: 'Form Generator' },
            'api_exec': { icon: '🔧', name: 'API Executor' },
            'analytics': { icon: '📊', name: 'Analytics' },
            'escalate': { icon: '🆘', name: 'Escalation' }
        };
        return agentMap[agentType] || { icon: '🤖', name: 'Agent' };
    }

    updateChatHeader(agentType) {
        const chatHeaderTitle = document.getElementById('chatHeaderTitle');
        const chatHeaderSubtitle = document.getElementById('chatHeaderSubtitle');

        const headerMap = {
            'doc_qa': {
                title: 'Chat with Your Documents',
                subtitle: 'Ask questions about your uploaded documents below'
            },
            'form_gen': {
                title: 'Form Generation Chat',
                subtitle: 'Describe the form you want to create'
            },
            'api_exec': {
                title: 'API Executor Chat',
                subtitle: 'Ask me to execute tools and API calls'
            },
            'analytics': {
                title: 'Analytics Chat',
                subtitle: 'Ask for system statistics and insights'
            },
            'escalate': {
                title: 'Support Chat',
                subtitle: 'Describe your issue for escalation to support'
            }
        };

        const headerInfo = headerMap[agentType] || {
            title: 'Chat Interface',
            subtitle: 'Start a conversation below'
        };

        if (chatHeaderTitle) chatHeaderTitle.textContent = headerInfo.title;
        if (chatHeaderSubtitle) chatHeaderSubtitle.textContent = headerInfo.subtitle;
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        if (!uploadArea || !fileInput) {
            console.error('Upload elements not found');
            return;
        }

        console.log('Setting up file upload listeners...');
        console.log('Upload area element:', uploadArea);
        console.log('File input element:', fileInput);

        // Click to upload
        uploadArea.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Upload area clicked, creating new file input...');

            // Visual feedback
            uploadArea.style.opacity = '0.7';
            setTimeout(() => {
                uploadArea.style.opacity = '1';
            }, 200);

            // Create a new file input element that's guaranteed to work
            const newFileInput = document.createElement('input');
            newFileInput.type = 'file';
            newFileInput.accept = '.pdf,.docx,.txt,.md,.csv,.json';
            newFileInput.style.position = 'absolute';
            newFileInput.style.left = '-9999px';
            newFileInput.style.opacity = '0';

            // Add to document temporarily
            document.body.appendChild(newFileInput);

            // Set up the change event for the new input
            newFileInput.addEventListener('change', (event) => {
                console.log('New file input changed, files selected:', event.target.files.length);

                if (event.target.files && event.target.files.length > 0) {
                    this.handleFileUpload(event.target.files);
                }

                // Remove the temporary input
                document.body.removeChild(newFileInput);
            });

            // Trigger the file dialog
            console.log('Triggering new file input click...');
            newFileInput.click();
            console.log('New file input clicked');
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            console.log('Files dropped:', files.length);
            if (files.length > 0) {
                this.handleFileUpload(files);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('File input changed, files selected:', e.target.files.length);

            const files = e.target.files;
            if (files && files.length > 0) {
                console.log('Processing selected files immediately...');

                // Process files immediately
                this.handleFileUpload(files);

                // Clear the input to allow re-uploading the same file
                setTimeout(() => {
                    e.target.value = '';
                }, 500);
            } else {
                console.log('No files selected or files array is empty');
            }
        });

        // Also listen for input event as a backup
        fileInput.addEventListener('input', (e) => {
            console.log('File input event triggered');
            if (e.target.files && e.target.files.length > 0) {
                this.handleFileUpload(e.target.files);
            }
        });

        console.log('File upload setup completed');

        // Add a test function to the window for debugging
        window.testUploadClick = () => {
            console.log('Testing upload click...');
            console.log('Upload area:', uploadArea);
            console.log('File input:', fileInput);
            if (uploadArea) {
                uploadArea.click();
            } else {
                console.error('Upload area not found!');
            }
        };
    }

    async handleFileUpload(files) {
        console.log('handleFileUpload called with', files.length, 'files');

        // Prevent duplicate uploads
        if (this.uploadInProgress) {
            this.showNotification('Upload already in progress. Please wait...', 'warning');
            return;
        }

        if (!files || files.length === 0) {
            console.log('No files to upload');
            return;
        }

        const uploadedFiles = document.getElementById('uploadedFiles');
        if (!uploadedFiles) {
            console.error('Upload files container not found');
            return;
        }

        // Handle multiple files upload
        if (files.length > 1) {
            console.log('Multiple files detected, using batch upload');
            return this.handleMultipleFileUpload(files);
        }

        // Single file upload
        console.log('Starting single file upload');
        this.uploadInProgress = true;

        try {
            for (const file of files) {
                console.log('Processing file:', file.name, 'Size:', file.size, 'Type:', file.type);

                // Validate file before upload
                if (!this.validateFile(file)) {
                    console.log('File validation failed for:', file.name);
                    continue;
                }

                console.log('File validation passed for:', file.name);

            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-file-${this.getFileIcon(this.getFileExtension(file.name))}"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${this.formatFileSize(file.size)})</span>
                </div>
                <div class="processing-status processing">
                    <i class="fas fa-spinner fa-spin"></i> Uploading...
                </div>
            `;
            uploadedFiles.appendChild(fileItem);

            // Show immediate feedback
            this.showNotification(`Uploading "${file.name}"...`, 'info');

            try {
                    console.log('Creating FormData for file upload...');
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('tenant_id', this.currentTenant);
                    formData.append('user_id', this.currentUser || '');

                    console.log('Sending upload request to /api/upload-document...');
                    const response = await fetch('/api/upload-document', {
                        method: 'POST',
                        body: formData
                    });

                    console.log('Upload response status:', response.status);

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    console.log('Upload result:', result);
                const statusDiv = fileItem.querySelector('.processing-status');

                if (result.success) {
                    statusDiv.className = 'processing-status success';
                    statusDiv.innerHTML = `<i class="fas fa-check"></i> ${result.duplicate ? 'Already exists' : 'Processed and indexed successfully'}`;
                    this.showNotification(`Document "${file.name}" ${result.duplicate ? 'already exists' : 'uploaded and indexed for RAG'}`, 'success');

                    // Add document info
                    if (!result.duplicate) {
                        const infoDiv = document.createElement('div');
                        infoDiv.className = 'file-info';
                        infoDiv.innerHTML = `<small>Chunks: ${result.chunks || 0} | ID: ${result.document_id.substring(0, 8)}...</small>`;
                        fileItem.appendChild(infoDiv);
                    }

                    // Add helpful message about asking questions and highlight chat interface
                    if (this.currentAgent === 'doc_qa' && !result.duplicate) {
                        setTimeout(() => {
                            this.addMessage(`Document "${file.name}" has been processed and indexed. You can now ask questions about its content!`, 'system');
                            this.highlightChatInterface();
                            this.showChatSuggestions();
                            this.scrollToChatInterface();
                        }, 1000);
                    } else if (this.currentAgent === 'doc_qa' && result.duplicate) {
                        // Even for duplicates, show the chat interface
                        setTimeout(() => {
                            this.addMessage(`Document "${file.name}" already exists in the system. You can ask questions about any uploaded documents!`, 'system');
                            this.highlightChatInterface();
                            this.showChatSuggestions();
                            this.scrollToChatInterface();
                        }, 1000);
                    }

                    // Refresh document list
                    this.loadDocumentList();
                } else {
                    statusDiv.className = 'processing-status error';
                    statusDiv.innerHTML = '<i class="fas fa-times"></i> Processing failed';
                    this.showNotification(`Failed to process "${file.name}": ${result.detail || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                console.error('Upload error for file:', file.name, error);
                const statusDiv = fileItem.querySelector('.processing-status');
                if (statusDiv) {
                    statusDiv.className = 'processing-status error';
                    statusDiv.innerHTML = '<i class="fas fa-times"></i> Upload failed';
                }
                this.showNotification(`Upload failed for "${file.name}": ${error.message}`, 'error');
            }
        }
        } finally {
            // Reset upload flag
            this.uploadInProgress = false;
        }
    }

    async handleMultipleFileUpload(files) {
        const uploadedFiles = document.getElementById('uploadedFiles');

        // Create a batch upload indicator
        const batchItem = document.createElement('div');
        batchItem.className = 'file-item batch-upload';
        batchItem.innerHTML = `
            <i class="fas fa-files"></i>
            <span>Uploading ${files.length} files...</span>
            <div class="processing-status">
                <i class="fas fa-spinner fa-spin"></i>
                Processing batch...
            </div>
        `;
        uploadedFiles.appendChild(batchItem);

        try {
            const formData = new FormData();
            for (const file of files) {
                formData.append('files', file);
            }
            formData.append('tenant_id', this.currentTenant);
            formData.append('user_id', this.currentUser || '');

            const response = await fetch('/api/upload-multiple-documents', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            const statusDiv = batchItem.querySelector('.processing-status');

            if (result.success) {
                statusDiv.className = 'processing-status success';
                statusDiv.innerHTML = `<i class="fas fa-check"></i> Batch completed: ${result.successful} successful, ${result.failed} failed, ${result.duplicates} duplicates`;

                // Show individual results
                result.results.forEach(fileResult => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <i class="fas fa-file"></i>
                        <span>${fileResult.filename}</span>
                        <div class="processing-status ${fileResult.success ? 'success' : 'error'}">
                            <i class="fas fa-${fileResult.success ? 'check' : 'times'}"></i>
                            ${fileResult.success ? (fileResult.duplicate ? 'Already exists' : 'Success') : 'Failed'}
                        </div>
                    `;
                    uploadedFiles.appendChild(fileItem);
                });

                this.showNotification(`Batch upload completed: ${result.successful}/${result.total_files} successful`, 'success');
                this.loadDocumentList();

                // Show chat interface enhancements for successful batch upload
                if (this.currentAgent === 'doc_qa' && result.successful > 0) {
                    setTimeout(() => {
                        this.addMessage(`${result.successful} documents have been processed and indexed. You can now ask questions about their content!`, 'system');
                        this.highlightChatInterface();
                        this.showChatSuggestions();
                        this.scrollToChatInterface();
                    }, 1500);
                }
            } else {
                statusDiv.className = 'processing-status error';
                statusDiv.innerHTML = '<i class="fas fa-times"></i> Batch failed';
                this.showNotification('Batch upload failed', 'error');
            }
        } catch (error) {
            const statusDiv = batchItem.querySelector('.processing-status');
            statusDiv.className = 'processing-status error';
            statusDiv.innerHTML = '<i class="fas fa-times"></i> Batch failed';
            this.showNotification(`Batch upload failed: ${error.message}`, 'error');
        }
    }

    async loadDocumentList() {
        try {
            // Show loading state
            const docListContainer = document.getElementById('documentList');
            if (docListContainer) {
                docListContainer.innerHTML = `
                    <div class="loading-docs">
                        <i class="fas fa-spinner fa-spin"></i> Loading documents...
                    </div>
                `;
            }

            const response = await fetch(`/api/documents/${this.currentTenant}`);
            const result = await response.json();

            if (result.success) {
                this.displayDocumentList(result.documents);
            } else {
                // Show error state
                if (docListContainer) {
                    docListContainer.innerHTML = `
                        <div class="error-docs">
                            <i class="fas fa-exclamation-triangle"></i> Failed to load documents
                            <button class="btn btn-sm btn-secondary" onclick="chatbotApp.loadDocumentList()" style="margin-left: 10px;">
                                <i class="fas fa-retry"></i> Retry
                            </button>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Failed to load document list:', error);
            // Show error state
            const docListContainer = document.getElementById('documentList');
            if (docListContainer) {
                docListContainer.innerHTML = `
                    <div class="error-docs">
                        <i class="fas fa-exclamation-triangle"></i> Error loading documents
                        <button class="btn btn-sm btn-secondary" onclick="chatbotApp.loadDocumentList()" style="margin-left: 10px;">
                            <i class="fas fa-retry"></i> Retry
                        </button>
                    </div>
                `;
            }
        }
    }

    displayDocumentList(documents) {
        // Get the document list container
        let docListContainer = document.getElementById('documentList');

        if (!docListContainer) {
            console.error('Document list container not found');
            return;
        }

        // Clear any loading or error states and create the full document list
        docListContainer.innerHTML = `
            <div class="document-header">
                <h4>📄 Document Library (${documents.length})</h4>
                <button class="btn btn-sm btn-secondary" onclick="chatbotApp.loadDocumentList()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            <div class="document-items"></div>
        `;

        const docItems = docListContainer.querySelector('.document-items');
        if (docItems) {
            if (documents.length === 0) {
                docItems.innerHTML = `
                    <div class="no-documents">
                        <i class="fas fa-folder-open"></i>
                        <p>No documents uploaded yet</p>
                        <small>Upload documents using the area above to get started</small>
                    </div>
                `;
            } else {
                docItems.innerHTML = documents.map(doc => `
                    <div class="document-item" data-doc-id="${doc.document_id}">
                        <div class="doc-info">
                            <i class="fas fa-file-${this.getFileIcon(doc.file_type)}"></i>
                            <div class="doc-details">
                                <span class="doc-name" title="${doc.original_name}">${doc.original_name}</span>
                                <small class="doc-meta">
                                    ${this.formatFileSize(doc.file_size)} • ${doc.chunk_count} chunks •
                                    <span class="upload-time">${this.formatUploadTime(doc.created_at)}</span>
                                </small>
                            </div>
                        </div>
                        <button class="delete-doc-btn" onclick="chatbotApp.deleteDocument('${doc.document_id}')" title="Delete document">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `).join('');
            }
        }
    }

    getFileIcon(fileType) {
        const iconMap = {
            '.pdf': 'pdf',
            '.docx': 'word',
            '.txt': 'text',
            '.md': 'markdown',
            '.csv': 'csv',
            '.json': 'code'
        };
        return iconMap[fileType] || 'file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatUploadTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const now = new Date();
        const uploadTime = new Date(timestamp);
        const diffMs = now - uploadTime;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return uploadTime.toLocaleDateString();
    }

    validateFile(file) {
        const allowedTypes = ['.pdf', '.docx', '.txt', '.md', '.csv', '.json'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        const fileExtension = this.getFileExtension(file.name);

        if (!allowedTypes.includes(fileExtension)) {
            this.showNotification(`File type "${fileExtension}" not supported. Allowed types: ${allowedTypes.join(', ')}`, 'error');
            return false;
        }

        if (file.size > maxSize) {
            this.showNotification(`File "${file.name}" is too large. Maximum size is 50MB.`, 'error');
            return false;
        }

        if (file.size === 0) {
            this.showNotification(`File "${file.name}" is empty.`, 'error');
            return false;
        }

        return true;
    }

    getFileExtension(filename) {
        return filename.toLowerCase().substring(filename.lastIndexOf('.'));
    }

    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`/api/documents/${this.currentTenant}/${documentId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            if (result.success) {
                this.showNotification('Document deleted successfully', 'success');
                this.loadDocumentList();
            } else {
                this.showNotification('Failed to delete document', 'error');
            }
        } catch (error) {
            this.showNotification(`Delete failed: ${error.message}`, 'error');
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        messageInput.value = '';

        // Custom API quick flow for API Executor
        if (this.currentAgent === 'api_exec' && this.customApi && this.customApi.baseUrl) {
            const params = this.extractParamsFromMessage(message, this.customApi.queryKeys || []);
            const hasAny = Object.keys(params).length > 0;
            if ((this.customApi.awaitingParams && hasAny) || hasAny) {
                await this.executeCustomApi(params);
                return;
            } else if (this.customApi.awaitingParams && (!hasAny)) {
                const needed = (this.customApi.queryKeys || []).map(k => `<code>${k}</code>`).join(', ');
                this.addMessage(`Please provide required parameter(s): ${needed}`, 'system');
                return;
            }
        }

        // Check if doc_qa agent and no documents uploaded
        if (this.currentAgent === 'doc_qa') {
            const status = await this.debugTenantStatus();
            if (status && !status.retriever_available) {
                this.addMessage('Please upload documents first using the upload area above before asking questions.', 'system');
                return;
            }
        }

        // Show loading
        this.showLoading(true);

        try {
            // Prepare request body
            const requestBody = {
                message: message,
                agent_type: this.currentAgent,
                tenant_id: this.currentTenant
            };

            // Add format preference for form generation
            if (this.currentAgent === 'form_gen' && this.selectedFormat) {
                requestBody.message = `${message} (format: ${this.selectedFormat})`;
                console.log('Form generation request:', {
                    originalMessage: message,
                    finalMessage: requestBody.message,
                    selectedFormat: this.selectedFormat,
                    agent: this.currentAgent
                });
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                const result = await response.json();

                if (result.success) {
                    // Handle new form generation with preview and download
                    if (result.form_generated && result.html_content) {
                        console.log('✅ HTML form detected - showing interactive interface');
                        // Store HTML data for editing and download
                        window.lastGeneratedForm = {
                            htmlContent: result.html_content,
                            filename: result.filename,
                            contentType: result.content_type,
                            fileFormat: result.file_format,
                            fileSize: result.file_size,
                            preview: result.preview,
                            interactive: result.interactive
                        };

                        // Create simplified HTML form interface with only Live Preview
                        const htmlFormSection = `
                            <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); border-radius: 12px; border: 1px solid #e2e8f0;">
                                <div style="text-align: center; margin-bottom: 15px;">
                                    <h4 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">
                                        <i class="fas fa-code" style="color: #e53e3e; margin-right: 8px;"></i>
                                        Interactive HTML Form Ready
                                    </h4>
                                    <p style="margin: 0; color: #718096; font-size: 14px;">
                                        ${result.filename} • ${(result.file_size / 1024).toFixed(1)} KB • HTML
                                    </p>
                                </div>

                                <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                                    <button onclick="showHTMLPreview()"
                                    style="
                                        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                                        color: white;
                                        border: none;
                                        padding: 12px 24px;
                                        border-radius: 8px;
                                        font-size: 16px;
                                        font-weight: 600;
                                        cursor: pointer;
                                        transition: all 0.3s ease;
                                        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
                                        display: inline-flex;
                                        align-items: center;
                                        gap: 8px;
                                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(72, 187, 120, 0.4)'"
                                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(72, 187, 120, 0.3)'">
                                        <i class="fas fa-eye"></i>
                                        Live Preview
                                    </button>
                                </div>
                            </div>
                        `;

                        // Add the response with enhanced HTML form editor
                        this.addMessage(result.response + htmlFormSection, 'bot');
                    }
                    // Handle new form generation with preview and download (for PDF/DOCX)
                    else if (result.form_generated && result.file_content) {
                        // Store file data for download button
                        window.lastGeneratedFile = {
                            content: result.file_content,
                            filename: result.filename,
                            contentType: result.content_type,
                            fileFormat: result.file_format,
                            fileSize: result.file_size,
                            preview: result.preview
                        };

                        // Create enhanced download section with preview
                        const downloadSection = `
                            <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); border-radius: 12px; border: 1px solid #e2e8f0;">
                                <div style="text-align: center; margin-bottom: 15px;">
                                    <h4 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">
                                        <i class="fas fa-file-${result.file_format === 'pdf' ? 'pdf' : 'word'}" style="color: ${result.file_format === 'pdf' ? '#e53e3e' : '#3182ce'}; margin-right: 8px;"></i>
                                        Form Ready for Download
                                    </h4>
                                    <p style="margin: 0; color: #718096; font-size: 14px;">
                                        ${result.filename} • ${(result.file_size / 1024).toFixed(1)} KB • ${result.file_format.toUpperCase()}
                                    </p>
                                </div>

                                <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                                    <button onclick="showFormPreview()"
                                    style="
                                        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                                        color: white;
                                        border: none;
                                        padding: 10px 20px;
                                        border-radius: 8px;
                                        font-size: 14px;
                                        font-weight: 600;
                                        cursor: pointer;
                                        transition: all 0.3s ease;
                                        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.3);
                                        display: inline-flex;
                                        align-items: center;
                                        gap: 6px;
                                    " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(72, 187, 120, 0.4)'"
                                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(72, 187, 120, 0.3)'">
                                        <i class="fas fa-eye"></i>
                                        Preview Form
                                    </button>

                                    <button onclick="downloadGeneratedFile()"
                                    style="
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        border: none;
                                        padding: 10px 20px;
                                        border-radius: 8px;
                                        font-size: 14px;
                                        font-weight: 600;
                                        cursor: pointer;
                                        transition: all 0.3s ease;
                                        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                                        display: inline-flex;
                                        align-items: center;
                                        gap: 6px;
                                    " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'"
                                       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(102, 126, 234, 0.3)'">
                                        <i class="fas fa-download"></i>
                                        Download ${result.file_format.toUpperCase()}
                                    </button>
                                </div>
                            </div>
                        `;

                        // Add the response with enhanced download section
                        this.addMessage(result.response + downloadSection, 'bot');

                        // Auto-download the file after a short delay
                        setTimeout(() => {
                            downloadGeneratedFile();
                        }, 1500);
                    }
                    // Handle legacy form generation with auto-download
                    else if (result.auto_download && result.file_content) {
                        // Store file data for download button
                        window.lastGeneratedFile = {
                            content: result.file_content,
                            filename: result.filename,
                            contentType: result.content_type
                        };

                        // Add download button to the response
                        const downloadButton = `
                            <div class="download-section" style="margin-top: 15px; text-align: center;">
                                <button onclick="downloadGeneratedFile()" class="download-btn" style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    border: none;
                                    padding: 12px 24px;
                                    border-radius: 8px;
                                    font-size: 16px;
                                    font-weight: 600;
                                    cursor: pointer;
                                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                                    transition: all 0.3s ease;
                                    display: inline-flex;
                                    align-items: center;
                                    gap: 8px;
                                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.4)'"
                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(102, 126, 234, 0.3)'">
                                    <i class="fas fa-download"></i>
                                    Download ${result.file_format.toUpperCase()} Form
                                </button>
                            </div>
                        `;

                        // Add the response with download button
                        this.addMessage(result.response + downloadButton, 'bot');
                    }
                    // Handle auto-download response (legacy)
                    else if (result.auto_download && result.download_id) {
                        this.addMessage(result.response, 'bot');
                        this.triggerAutoDownload(result.download_id, result.filename);
                    }
                    // Handle different response types
                    else if (typeof result.response === 'object' && result.response.download_url) {
                        // Form generation response with download
                        this.addMessage(result.response.response || 'Form generated successfully!', 'bot');
                        this.showGeneratedFile(result.response.filename, result.response.download_url);
                    } else if (typeof result.response === 'string') {
                        this.addMessage(result.response, 'bot');

                        // Check for download links in text response
                        if (result.response.includes('/downloads/')) {
                            this.extractAndShowDownloads(result.response);
                        }
                    } else {
                        this.addMessage(JSON.stringify(result.response), 'bot');
                    }
                } else {
                    this.addMessage('Sorry, I encountered an error processing your request.', 'bot');
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Chat error:', error);
            console.log(`Current agent in error handler: ${this.currentAgent}`);
            // Fallback response when server is not available
            this.addMessage(
                `🤖 Demo Mode: This is a simulated response for the "${this.getAgentInfo(this.currentAgent).name}" agent. ` +
                `Your message was: "${message}". To enable full functionality, please start the server with "python app.py".`,
                'bot'
            );

            // Show a helpful notification
            this.showNotification('Demo mode - Server not running. Start with "python app.py" for full functionality.', 'warning');
        } finally {
            this.showLoading(false);
        }
    }

    addMessage(content, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Enhanced content processing for news results
        let processedContent = content;
        
        // Handle download links in bot messages
        if (type === 'bot' && content.includes('/downloads/')) {
            processedContent = this.processDownloadLinks(processedContent);
        }
        
        // Enhanced news content formatting
        if (type === 'bot' && this.containsNewsContent(processedContent)) {
            processedContent = this.enhanceNewsContent(processedContent);
        }
        
        messageDiv.innerHTML = processedContent;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Try to extract a parameter value from natural language text
    extractParamValue(text, paramKey) {
        if (!text) return '';
        const t = String(text).trim();
        // 1) If the text contains a URL with the param, extract it
        try {
            const urlMatch = t.match(/https?:[^\s]+/i);
            if (urlMatch) {
                const u = new URL(urlMatch[0]);
                const v = u.searchParams.get(paramKey);
                if (v) return v;
            }
        } catch (_) {}

        // 2) Patterns like "paramKey=VALUE" or "paramKey: VALUE"
        const keyRegex = new RegExp(`${paramKey}\s*[:=]\s*([^\s,;]+)`, 'i');
        const keyMatch = t.match(keyRegex);
        if (keyMatch && keyMatch[1]) return keyMatch[1].replace(/["'`]/g, '');

        // 3) Quoted token
        const quoted = t.match(/["'`](.+?)["'`]/);
        if (quoted && quoted[1]) return quoted[1];

        // 4) First token that contains a digit (IDs often include digits)
        const digitToken = t.match(/\b[^\s,;:]+\d[^\s,;:]*\b/);
        if (digitToken) return digitToken[0];

        // 5) Fallback: if it's a single word, use as-is
        if (!t.includes(' ')) return t;
        return '';
    }

    async executeCustomApi(paramMap) {
        try {
            this.showLoading(true);
            const query_params = paramMap && typeof paramMap === 'object' ? paramMap : {};
            const reqBody = {
                base_url: this.customApi.baseUrl,
                method: this.customApi.method || 'GET',
                query_params
            };
            const resp = await fetch('/api/custom-api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqBody)
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const result = await resp.json();

            let qs = '';
            const entries = Object.entries(query_params);
            if (entries.length) {
                qs = '?' + entries.map(([k,v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
            }
            const calledUrl = result.url || `${this.customApi.baseUrl}${qs}`;

            let summary = '';
            const data = result.data || result;
            if (data && typeof data === 'object') {
                if ('status' in data && ('order_id' in data || 'id' in data)) {
                    const oid = data.order_id || data.id || entries[0]?.[1] || '';
                    summary = `<div style="margin-bottom:8px;"><strong>${this.escapeHtml(String(oid))}</strong> status: <strong>${this.escapeHtml(String(data.status))}</strong></div>`;
                } else if ('message' in data) {
                    summary = `<div style="margin-bottom:8px;"><strong>API Message:</strong> ${this.escapeHtml(String(data.message))}</div>`;
                }
            }

            let payloadHtml = '';
            if (result.data) {
                payloadHtml = `<pre style="white-space:pre-wrap;background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">${this.escapeHtml(JSON.stringify(result.data, null, 2))}</pre>`;
            } else if (result.text) {
                payloadHtml = `<pre style="white-space:pre-wrap;background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">${this.escapeHtml(result.text)}</pre>`;
            } else {
                payloadHtml = `<em>No content returned</em>`;
            }
            this.addMessage(`<div><div style="margin-bottom:6px;color:#4a5568;">Called: <code>${this.escapeHtml(calledUrl)}</code></div>${summary}${payloadHtml}</div>`, 'bot');
            this.customApi.awaitingParams = false;
            const messageInput = document.getElementById('messageInput');
            if (messageInput) messageInput.placeholder = 'Type your message...';
        } catch (e) {
            console.error('Custom API call failed:', e);
            this.addMessage(`Failed to call custom API: ${this.escapeHtml(e.message || String(e))}`, 'bot');
        } finally {
            this.showLoading(false);
        }
    }

    escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
    
    containsNewsContent(content) {
        const newsIndicators = [
            '📡 **Live RSS News Results',
            '🚨 **Monitoring Setup',
            '📰 **Current News Search',
            '📰 **Global News Search',
            '🔍 **Security & Terrorism Information'
        ];
        return newsIndicators.some(indicator => content.includes(indicator));
    }
    
    enhanceNewsContent(content) {
        let html = content;
        
        // Convert basic markdown to HTML
        html = html
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        
        // Enhanced processing for RSS feed results
        if (html.includes('📡 **Live RSS News Results')) {
            html = this.formatRSSResults(html);
        }
        
        // Enhanced processing for monitoring setup
        if (html.includes('🚨 **Monitoring Setup')) {
            html = this.formatMonitoringSetup(html);
        }
        
        // Enhanced processing for news search results
        if (html.includes('📰 **Current News Search') || html.includes('📰 **Global News Search')) {
            html = this.formatNewsSearch(html);
        }
        
        return html;
    }
    
    formatRSSResults(html) {
        // Add success indicator
        html = html.replace('📡 **Live RSS News Results', 
            '<div class="rss-success-indicator"><i class="fas fa-satellite-dish"></i>Live RSS News Results');
        
        // Format individual articles with enhanced structure
        const articleRegex = /\*\*(\d+\. .*?)\*\*<br>📰 (.*?) \| 📅 (.*?)<br>(📝 .*?<br>)?🔗 (.*?)<br>/g;
        
        html = html.replace(articleRegex, (match, title, source, time, summary, link) => {
            return `
                <div class="news-article">
                    <h4>${title.replace(/^\d+\. /, '')}</h4>
                    <div class="news-meta">
                        <span class="news-source">${source}</span>
                        <span class="news-time"><i class="fas fa-clock"></i> ${time}</span>
                    </div>
                    ${summary ? `<div class="news-summary">${summary.replace('📝 ', '').replace('<br>', '')}</div>` : ''}
                    <a href="${link}" target="_blank" class="news-link">
                        <i class="fas fa-external-link-alt"></i> Read Full Article
                    </a>
                </div>
            `;
        });
        
        return html;
    }
    
    formatMonitoringSetup(html) {
        // Format alert setup sections with better structure
        html = html.replace('🚨 **Monitoring Setup', 
            '<div class="alert-setup-section"><h4><i class="fas fa-bell"></i>Monitoring Setup');
        
        // Format Google Alerts section
        html = html.replace('🔔 **Google Alerts', 
            '<h5><i class="fab fa-google"></i>Google Alerts (Automated Email Updates):</h5>');
        
        // Convert hashtag lists to styled elements
        const hashtagRegex = /#(\w+)/g;
        html = html.replace(hashtagRegex, '<span class="hashtag">#$1</span>');
        
        // Format links as clickable elements
        const urlRegex = /(https?:\/\/[^\s<]+)/g;
        html = html.replace(urlRegex, '<a href="$1" target="_blank" class="alert-link"><i class="fas fa-external-link-alt"></i>Open Link</a>');
        
        return html + '</div>';
    }
    
    formatNewsSearch(html) {
        // Add security warning for terrorism-related content
        if (html.toLowerCase().includes('terrorism') || html.toLowerCase().includes('terror')) {
            html += `
                <div class="security-warning">
                    <h5><i class="fas fa-shield-alt"></i>Security Information Notice</h5>
                    <p>Please verify all security-related information through official government sources. Cross-reference multiple reliable news outlets before taking any action based on this information.</p>
                </div>
            `;
        }
        
        // Format news source URLs as clickable links
        const newsUrlRegex = /• ([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s<]*)/g;
        html = html.replace(newsUrlRegex, '• <a href="https://$1" target="_blank" class="news-link"><i class="fas fa-external-link-alt"></i>$1</a>');
        
        return html;
    }

    processDownloadLinks(content) {
        // Extract download URLs and create clickable links
        const downloadRegex = /\/downloads\/([^"\s]+)/g;
        return content.replace(downloadRegex, (match, filename) => {
            return `<a href="${match}" class="download-link" download="${filename}">
                <i class="fas fa-download"></i> Download ${filename}
            </a>`;
        });
    }

    clearChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '<div class="welcome-message"><p>Welcome! How can I help you today?</p></div>';
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/system-stats');
            const stats = await response.json();
            this.renderAnalytics(stats);
        } catch (error) {
            this.showNotification('Failed to load analytics', 'error');
        }
    }

    renderAnalytics(stats) {
        const systemStats = document.getElementById('systemStats');
        const toolStats = document.getElementById('toolStats');

        systemStats.innerHTML = this.formatStats(stats.system);
        toolStats.innerHTML = this.formatStats(stats.tools);
    }

    formatStats(stats) {
        return Object.entries(stats).map(([key, value]) => 
            `<div><strong>${key}:</strong> ${JSON.stringify(value)}</div>`
        ).join('');
    }

    async createTenant() {
        const tenantId = document.getElementById('tenantId').value;
        const tenantName = document.getElementById('tenantName').value;
        const permissions = Array.from(document.querySelectorAll('#createTenantModal input[type="checkbox"]:checked'))
            .map(cb => cb.value);

        try {
            const response = await fetch('/api/create-tenant', {
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

            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Tenant created successfully', 'success');
                this.hideModal('createTenantModal');
                this.loadTenants();
            } else {
                this.showNotification('Failed to create tenant', 'error');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'error');
        }
    }

    setupModals() {
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.hideModal(modal.id);
            });
        });

        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('show');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    highlightChatInterface() {
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('messageInput');

        if (chatMessages && chatInput) {
            // Add a subtle highlight animation to draw attention
            chatMessages.style.border = '2px solid #667eea';
            chatMessages.style.borderRadius = '8px';
            chatMessages.style.transition = 'all 0.3s ease';

            // Highlight the input field
            chatInput.style.border = '2px solid #667eea';
            chatInput.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.3)';
            chatInput.placeholder = 'Ask me anything about your uploaded documents...';

            // Add a pulsing animation to draw attention
            chatInput.style.animation = 'pulse 2s infinite';

            // Remove highlights after a few seconds
            setTimeout(() => {
                chatMessages.style.border = '';
                chatMessages.style.borderRadius = '';
                chatInput.style.border = '';
                chatInput.style.boxShadow = '';
                chatInput.style.animation = '';
                chatInput.placeholder = 'Type your message...';
            }, 8000);
        }
    }

    showChatSuggestions() {
        const suggestions = [
            "What is this document about?",
            "Summarize the main points",
            "What are the key topics covered?",
            "Extract important information from the document"
        ];

        // Add suggestion buttons temporarily
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'chat-suggestions';
            suggestionsDiv.innerHTML = `
                <div class="suggestions-header">
                    <i class="fas fa-lightbulb"></i> Try asking:
                </div>
                <div class="suggestions-buttons">
                    ${suggestions.map(suggestion =>
                        `<button class="suggestion-btn" data-suggestion="${suggestion}">${suggestion}</button>`
                    ).join('')}
                </div>
            `;

            chatMessages.appendChild(suggestionsDiv);

            // Scroll to show suggestions
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Add click handlers for suggestions
            suggestionsDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const suggestion = btn.dataset.suggestion;
                    const messageInput = document.getElementById('messageInput');
                    if (messageInput) {
                        messageInput.value = suggestion;
                        messageInput.focus();
                        // Remove suggestions after selection
                        suggestionsDiv.remove();
                    }
                });
            });

            // Auto-remove suggestions after 30 seconds
            setTimeout(() => {
                if (suggestionsDiv.parentNode) {
                    suggestionsDiv.remove();
                }
            }, 30000);
        }
    }

    showDocQAWelcome() {
        // Clear existing messages
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';

            // Add welcome message
            this.addMessage(`Welcome to Document Q&A! 📄`, 'system');
            this.addMessage(`I can help you analyze and answer questions about your documents. Here's how to get started:

1. **Upload Documents**: Use the upload area above to add PDF, DOCX, TXT, MD, CSV, or JSON files
2. **Wait for Processing**: I'll process and index your documents for search
3. **Ask Questions**: Once uploaded, you can ask me anything about the document content

Try uploading a document first, then ask questions like:
• "What is this document about?"
• "Summarize the main points"
• "What are the key findings?"`, 'system');

            // Scroll to show the chat interface
            setTimeout(() => {
                this.scrollToChatInterface();
            }, 500);
        }
    }

    showFormGenWelcome() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';

            this.addMessage(`Welcome to Form Generator! 📝`, 'system');
            this.addMessage(`I can help you create professional forms in PDF or DOCX format. Here's how:

1. **Choose Format**: Select PDF or DOCX output format above
2. **Use Templates**: Click on quick templates for common forms
3. **Describe Your Form**: Tell me what kind of form you need
4. **Get Your Form**: I'll generate and provide a download link

Try asking me to create forms like:
• "Create a customer feedback form"
• "Generate a job application form"
• "Make a contact information form"
• "Create a survey with rating questions"`, 'system');

            setTimeout(() => {
                this.scrollToChatInterface();
            }, 500);
        }
    }

    showApiExecWelcome() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';

            this.addMessage(`Welcome to API Executor! 🔧`, 'system');
            this.addMessage(`I can execute various API calls and tools for you. Available tools:

**Core Tools:**
• **Weather**: Get current weather for any city
• **Web Search**: Search the internet for information
• **API Discovery**: Analyze and discover API endpoint structures
• **Document Stats**: Get statistics about uploaded documents

**New Feature - API Discovery:**
• **Discover API**: Analyze any API endpoint to understand its structure
• **Supabase Examples**: Analyze sample Supabase APIs provided

**Try asking me:**
• "What's the weather in New York?"
• "Search for latest AI news"
• "Discover this API: https://api.example.com/users"
• "Analyze the Supabase sample APIs"
• "What's inside this API: https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-order-status?order_id=ORD002"

**API Discovery Examples:**
I can now automatically analyze APIs to tell you:
- Response structure and data types
- Required parameters
- Authentication methods
- Usage examples and tool registration commands`, 'system');

            setTimeout(() => {
                this.scrollToChatInterface();
            }, 500);
        }
    }

    showAnalyticsWelcome() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';

            this.addMessage(`Welcome to Analytics! 📊`, 'system');
            this.addMessage(`I can provide insights and statistics about the system. Available analytics:

**System Statistics**: Overall system performance and usage
**Document Stats**: Information about uploaded documents
**Tool Usage**: Statistics about tool calls and performance
**User Activity**: Usage patterns and trends

Try asking me:
• "Show me system statistics"
• "How many documents are uploaded?"
• "What are the most used tools?"
• "Generate a usage report"
• "Show performance metrics"`, 'system');

            setTimeout(() => {
                this.scrollToChatInterface();
            }, 500);
        }
    }

    showEscalationWelcome() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';

            this.addMessage(`Welcome to Escalation Support! 🆘`, 'system');
            this.addMessage(`I can help escalate your request to human support. I'll create a support ticket and connect you with the right team.

**Issue Categories**:
• Technical Issues
• Billing Questions
• Feature Requests
• General Support

Please describe your issue and I'll:
1. Create a support ticket
2. Route to the appropriate team
3. Provide you with a ticket number
4. Estimate response time

Try telling me:
• "I have a technical problem with document upload"
• "I need help with my billing"
• "I want to request a new feature"`, 'system');

            setTimeout(() => {
                this.scrollToChatInterface();
            }, 500);
        }
    }

    scrollToChatInterface() {
        // Scroll to make the chat interface visible
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Also focus on the input field to draw attention
            setTimeout(() => {
                const messageInput = document.getElementById('messageInput');
                if (messageInput) {
                    messageInput.focus();
                }
            }, 1000);
        }
    }

    async debugTenantStatus() {
        try {
            const response = await fetch(`/api/debug/tenant/${this.currentTenant}`);
            const status = await response.json();
            console.log('Tenant Debug Status:', status);

            if (!status.retriever_available) {
                this.showNotification('No documents indexed yet. Please upload documents first.', 'warning');
            }

            return status;
        } catch (error) {
            console.error('Debug status check failed:', error);
            return null;
        }
    }

    // Agent-specific setup methods
    setupFormTemplates() {
        document.querySelectorAll('.template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const template = e.target.dataset.template;
                this.insertTemplateQuery(template);
            });
        });
    }

    setupApiTools() {
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                document.getElementById('messageInput').value = query;
            });
        });
    }

    setupCustomApiControls() {
        const setBtn = document.getElementById('setCustomApiBtn');
        const urlField = document.getElementById('customApiUrl');
        if (!setBtn || !urlField) return;

        setBtn.addEventListener('click', () => {
            let urlInput = (urlField.value || '').trim();
            if (!urlInput) {
                this.showNotification('Please enter an API URL', 'warning');
                return;
            }

            // Allow user to paste with or without protocol
            let u;
            try {
                u = new URL(urlInput);
            } catch (_) {
                try { u = new URL(`https://${urlInput}`); } catch (e) {
                    this.showNotification('Invalid URL. Include protocol like https://', 'error');
                    return;
                }
            }

            const baseUrl = `${u.origin}${u.pathname}`;
            const queryKeys = Array.from(u.searchParams.keys());

            this.customApi = {
                baseUrl,
                method: 'GET',
                queryKeys,
                awaitingParams: queryKeys.length > 0
            };

            // Compose guidance message
            if (queryKeys.length > 0) {
                const needed = queryKeys.map(k => `<code>${k}</code>`).join(', ');
                this.addMessage(`Custom API configured for <code>${this.escapeHtml(baseUrl)}</code>. Provide ${needed} in your next message (e.g., <code>${queryKeys[0]}=VALUE</code> or just the value if obvious).`, 'system');
                const messageInput = document.getElementById('messageInput');
                if (messageInput) {
                    const first = queryKeys[0];
                    messageInput.placeholder = `Enter ${first} (e.g., VALUE)`;
                    messageInput.focus();
                }
            } else {
                this.addMessage(`Custom API configured for <code>${this.escapeHtml(baseUrl)}</code>. Ask a question or include parameters like <code>key=value</code>.`, 'system');
            }

            this.showNotification('Custom API is set.', 'success');
        });
    }

    parseKeyVariations(key) {
        const variants = new Set([key]);
        variants.add(key.replace(/[_\-]/g, ' '));
        variants.add(key.replace(/[_\-]/g, ''));
        return Array.from(variants).filter(Boolean);
    }

    extractParamsFromMessage(text, keys = []) {
        const params = {};
        const t = String(text || '').trim();
        if (!t) return params;

        // 1) If message includes a URL, parse all params from it
        try {
            const urlMatch = t.match(/https?:[^\s]+/i);
            if (urlMatch) {
                const u = new URL(urlMatch[0]);
                u.searchParams.forEach((v, k) => {
                    if (!keys.length || keys.includes(k)) params[k] = v;
                });
            }
        } catch (_) {}

        // 2) Generic key=value or key: value pairs
        const pairRegex = /(\b[\w\-]+\b)\s*[:=]\s*([\w\-\.\/:]+)\b/g;
        let m;
        while ((m = pairRegex.exec(t)) !== null) {
            const k = m[1];
            const v = m[2];
            if (!keys.length || keys.includes(k)) params[k] = v.replace(/["'`]/g, '');
        }

        // 3) For known keys, attempt natural-language patterns like "key is VALUE"
        for (const key of keys) {
            if (params[key]) continue;
            const vars = this.parseKeyVariations(key).map(v => v.replace(/[-/\\]/g, '\\$&'));
            const re = new RegExp(`(?:${vars.join('|')})\s*(?:is|=|:)?\s*([\\w\\-]+)`, 'i');
            const mm = t.match(re);
            if (mm && mm[1]) params[key] = mm[1].replace(/["'`]/g, '');
        }

        // 4) If only one key is required and still missing, try to extract a token with digits
        if (keys.length === 1 && !params[keys[0]]) {
            const token = (t.match(/\b[^\s,;:]+\d[^\s,;:]*\b/) || [])[0];
            if (token) params[keys[0]] = token;
        }

        return params;
    }

    setupEscalationCategories() {
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                const category = e.target.dataset.category;
                this.insertEscalationQuery(category);
            });
        });
    }

    insertTemplateQuery(template) {
        const templates = {
            'contact': 'Create a professional contact form with name, email, phone, and message fields',
            'survey': 'Generate a customer satisfaction survey with rating scales and feedback sections',
            'application': 'Create a job application form with personal info, experience, and skills sections',
            'feedback': 'Design a feedback form for product or service evaluation',
            'registration': 'Create an event registration form with participant details and preferences'
        };

        const query = templates[template] || `Create a ${template} form`;
        document.getElementById('messageInput').value = query;
    }

    insertEscalationQuery(category) {
        const queries = {
            'technical': 'I need technical support with a system issue',
            'billing': 'I have a question about my billing or account',
            'feature': 'I would like to request a new feature or enhancement',
            'other': 'I need assistance with something else'
        };

        const query = queries[category] || 'I need help from a human agent';
        document.getElementById('messageInput').value = query;
    }

    async loadQuickStats() {
        try {
            const response = await fetch('/api/system-stats');
            const data = await response.json();

            // Update document count
            const docResponse = await fetch(`/api/documents/${this.currentTenant}`);
            const docData = await docResponse.json();

            document.getElementById('docCount').textContent = docData.total || 0;
            document.getElementById('chatCount').textContent = data.system?.total_conversations || 0;
            document.getElementById('toolCount').textContent = data.tools?.total_calls || 0;
        } catch (error) {
            console.error('Failed to load quick stats:', error);
            document.getElementById('docCount').textContent = '-';
            document.getElementById('chatCount').textContent = '-';
            document.getElementById('toolCount').textContent = '-';
        }
    }

    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`/api/documents/${this.currentTenant}/${documentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Document deleted successfully', 'success');
                this.loadDocumentList(); // Refresh the list
            } else {
                throw new Error('Failed to delete document');
            }
        } catch (error) {
            console.error('Delete failed:', error);
            this.showNotification('Failed to delete document', 'error');
        }
    }

    showGeneratedFile(filename, downloadUrl) {
        const generatedFiles = document.getElementById('generatedFiles');
        const filesList = document.getElementById('filesList');

        generatedFiles.style.display = 'block';

        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-name">${filename}</div>
                <div class="file-size">Ready for download</div>
            </div>
            <a href="${downloadUrl}" class="btn btn-sm btn-primary" download>
                <i class="fas fa-download"></i> Download
            </a>
        `;

        filesList.appendChild(fileItem);
    }

    extractAndShowDownloads(responseText) {
        // Extract download URLs from response text
        const downloadRegex = /\/downloads\/[^\s)]+/g;
        const matches = responseText.match(downloadRegex);

        if (matches) {
            matches.forEach(url => {
                const filename = url.split('/').pop();
                this.showGeneratedFile(filename, url);
            });
        }
    }

    triggerAutoDownload(downloadId, filename) {
        // Create a temporary link to trigger download
        const downloadUrl = `/api/download/${downloadId}`;

        // Show a download message with button
        const downloadMessage = `
            <div class="download-notification">
                <div class="download-info">
                    <i class="fas fa-file-download"></i>
                    <span>Form generated: <strong>${filename}</strong></span>
                </div>
                <button class="btn btn-primary download-btn" onclick="window.chatbotApp.downloadFile('${downloadUrl}', '${filename}')">
                    <i class="fas fa-download"></i> Download Now
                </button>
            </div>
        `;

        this.addMessage(downloadMessage, 'bot');

        // Auto-trigger download after a short delay
        setTimeout(() => {
            this.downloadFile(downloadUrl, filename);
        }, 1000);
    }

    downloadFile(downloadUrl, filename) {
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        link.style.display = 'none';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Show success notification
        this.showNotification(`Download started: ${filename}`, 'success');
    }
}

// Global function to download generated file
function downloadGeneratedFile() {
    if (!window.lastGeneratedFile) {
        alert('No file available for download');
        return;
    }

    try {
        // Create blob and download
        const byteCharacters = atob(window.lastGeneratedFile.content);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: window.lastGeneratedFile.contentType });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = window.lastGeneratedFile.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Show success notification
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification('File downloaded successfully!', 'success');
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading file. Please try again.');
    }
}

// Global function to show form preview
function showFormPreview() {
    if (!window.lastGeneratedFile || !window.lastGeneratedFile.preview) {
        alert('No form preview available');
        return;
    }

    const { preview, filename, fileFormat, fileSize } = window.lastGeneratedFile;

    // Create modal for form preview
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;

    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 80%;
        max-height: 80%;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
    `;

    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px;">
            <h3 style="margin: 0; color: #2d3748; font-size: 20px;">
                <i class="fas fa-file-${fileFormat === 'pdf' ? 'pdf' : 'word'}" style="color: ${fileFormat === 'pdf' ? '#e53e3e' : '#3182ce'}; margin-right: 10px;"></i>
                Form Preview
            </h3>
            <button onclick="this.closest('.modal-overlay').remove()" style="
                background: #f56565;
                color: white;
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">×</button>
        </div>

        <div style="margin-bottom: 20px; padding: 15px; background: #f7fafc; border-radius: 8px; border-left: 4px solid #667eea;">
            <p style="margin: 0; color: #4a5568; font-size: 14px;">
                <strong>File:</strong> ${filename} • <strong>Size:</strong> ${(fileSize / 1024).toFixed(1)} KB • <strong>Format:</strong> ${fileFormat.toUpperCase()}
            </p>
        </div>

        <div style="white-space: pre-wrap; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #2d3748; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; max-height: 400px; overflow-y: auto;">
            ${preview.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}
        </div>

        <div style="margin-top: 20px; text-align: center; padding-top: 15px; border-top: 1px solid #e2e8f0;">
            <button onclick="downloadGeneratedFile(); this.closest('.modal-overlay').remove();" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                display: inline-flex;
                align-items: center;
                gap: 8px;
                margin-right: 10px;
            ">
                <i class="fas fa-download"></i>
                Download ${fileFormat.toUpperCase()}
            </button>

            <button onclick="this.closest('.modal-overlay').remove()" style="
                background: #e2e8f0;
                color: #4a5568;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            ">
                Close Preview
            </button>
        </div>
    `;

    modal.className = 'modal-overlay';
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Initialize the app when DOM is loaded
let chatbotApp;
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing ChatbotApp...');
    try {
        chatbotApp = new ChatbotApp();
        window.chatbotApp = chatbotApp; // Make globally accessible
        console.log('ChatbotApp initialized successfully');
    } catch (error) {
        console.error('Error initializing ChatbotApp:', error);
        console.log('ChatbotApp initialization failed, fallback handlers should work');
    }
});

// Global function to show HTML form preview with form filling and editing capabilities
function showHTMLPreview() {
    if (!window.lastGeneratedForm || !window.lastGeneratedForm.htmlContent) {
        alert('No HTML form available for preview');
        return;
    }

    const { htmlContent, filename } = window.lastGeneratedForm;

    // Create modal for HTML form preview
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;

    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        width: 90%;
        height: 90%;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
        display: flex;
        flex-direction: column;
    `;

    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 2px solid #e2e8f0; background: #f8f9fa;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">
                <i class="fas fa-eye" style="color: #48bb78; margin-right: 10px;"></i>
                Live Form Preview - ${filename}
            </h3>
            <div style="display: flex; gap: 10px; align-items: center;">
                <button onclick="editCompanyInfo()" style="
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    <i class="fas fa-building"></i> Edit Company
                </button>
                <button onclick="this.closest('.modal-overlay').remove()" style="
                    background: #f56565;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 35px;
                    height: 35px;
                    cursor: pointer;
                    font-size: 16px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        <div style="flex: 1; overflow: auto; padding: 0;">
            <iframe id="htmlPreviewFrame" style="width: 100%; height: 100%; border: none;"></iframe>
        </div>
        <div style="padding: 20px; background: #f8f9fa; border-top: 1px solid #e2e8f0; text-align: center;">
            <div style="margin-bottom: 15px;">
                <p style="margin: 0 0 10px 0; color: #4a5568; font-size: 14px; font-weight: 600;">
                    <i class="fas fa-info-circle" style="color: #4299e1; margin-right: 6px;"></i>
                    Fill out the form above, then click Submit Form to save your data
                </p>
            </div>
            <div style="display: flex; gap: 15px; justify-content: center; align-items: center; flex-wrap: wrap;">
                <button onclick="downloadFormAs('pdf')" style="
                    background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
                    color: white;
                    border: none;
                    padding: 14px 28px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(245, 101, 101, 0.3);
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(245, 101, 101, 0.4)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(245, 101, 101, 0.3)'">
                    <i class="fas fa-file-pdf"></i> Download PDF
                </button>
                <button onclick="downloadFormAs('docx')" style="
                    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                    color: white;
                    border: none;
                    padding: 14px 28px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(66, 153, 225, 0.4)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(66, 153, 225, 0.3)'">
                    <i class="fas fa-file-word"></i> Download DOCX
                </button>
            </div>
        </div>
    `;

    modal.className = 'modal-overlay';
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Load HTML content into iframe and enable form interaction
    const iframe = document.getElementById('htmlPreviewFrame');
    iframe.onload = function() {
        iframe.contentDocument.open();
        iframe.contentDocument.write(htmlContent);
        iframe.contentDocument.close();
        
        // Initialize form data capture
        initializeFormDataCapture(iframe);
    };
    iframe.src = 'about:blank';
}

// Global function to show HTML editor
function showHTMLEditor() {
    if (!window.lastGeneratedForm || !window.lastGeneratedForm.htmlContent) {
        alert('No HTML form available for editing');
        return;
    }

    const { htmlContent, filename } = window.lastGeneratedForm;

    // Create modal for HTML editor
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
    `;

    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        width: 95%;
        height: 95%;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
        display: flex;
        flex-direction: column;
    `;

    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 2px solid #e2e8f0; background: #f8f9fa;">
            <h3 style="margin: 0; color: #2d3748; font-size: 18px;">
                <i class="fas fa-code" style="color: #667eea; margin-right: 10px;"></i>
                HTML Form Editor - ${filename}
            </h3>
            <div style="display: flex; gap: 10px; align-items: center;">
                <button onclick="updatePreview()" style="
                    background: #48bb78;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    <i class="fas fa-sync-alt"></i> Update Preview
                </button>
                <button onclick="this.closest('.modal-overlay').remove()" style="
                    background: #f56565;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 35px;
                    height: 35px;
                    cursor: pointer;
                    font-size: 16px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
        <div style="flex: 1; display: flex; overflow: hidden;">
            <div style="flex: 1; display: flex; flex-direction: column; border-right: 1px solid #e2e8f0;">
                <div style="padding: 10px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #334155;">
                    <i class="fas fa-code"></i> HTML Source Code
                </div>
                <textarea id="htmlEditor" style="
                    flex: 1;
                    border: none;
                    padding: 15px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 13px;
                    line-height: 1.5;
                    resize: none;
                    outline: none;
                    tab-size: 2;
                ">${htmlContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
            </div>
            <div style="flex: 1; display: flex; flex-direction: column;">
                <div style="padding: 10px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #334155;">
                    <i class="fas fa-eye"></i> Live Preview
                </div>
                <iframe id="htmlEditorPreview" style="flex: 1; border: none;"></iframe>
            </div>
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-top: 1px solid #e2e8f0; text-align: center;">
            <button onclick="saveEditedHTML()" style="
                background: #48bb78;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                margin-right: 10px;
                cursor: pointer;
                font-weight: 600;
            ">
                <i class="fas fa-save"></i> Save Changes
            </button>
            <button onclick="downloadFormAs('html')" style="
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                margin-right: 10px;
                cursor: pointer;
                font-weight: 600;
            ">
                <i class="fas fa-download"></i> Download HTML
            </button>
            <button onclick="downloadFormAs('pdf')" style="
                background: #f56565;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                margin-right: 10px;
                cursor: pointer;
                font-weight: 600;
            ">
                <i class="fas fa-file-pdf"></i> Download PDF
            </button>
            <button onclick="downloadFormAs('docx')" style="
                background: #4299e1;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            ">
                <i class="fas fa-file-word"></i> Download DOCX
            </button>
        </div>
    `;

    modal.className = 'modal-overlay';
    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Initialize the preview
    updatePreview();
}

// Global function to update HTML preview
function updatePreview() {
    const editor = document.getElementById('htmlEditor');
    const preview = document.getElementById('htmlEditorPreview');
    
    if (editor && preview) {
        const htmlContent = editor.value.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        preview.onload = function() {
            preview.contentDocument.open();
            preview.contentDocument.write(htmlContent);
            preview.contentDocument.close();
        };
        preview.src = 'about:blank';
    }
}

// Global function to save edited HTML
function saveEditedHTML() {
    const editor = document.getElementById('htmlEditor');
    
    if (editor && window.lastGeneratedForm) {
        const editedHTML = editor.value.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        window.lastGeneratedForm.htmlContent = editedHTML;
        window.lastGeneratedForm.fileSize = new Blob([editedHTML]).size;
        
        // Show success notification
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification('HTML changes saved successfully!', 'success');
        } else {
            alert('HTML changes saved successfully!');
        }
    }
}

// Global function to download form in different formats with filled data
function downloadFormAs(format) {
    if (!window.lastGeneratedForm) {
        alert('No form available for download');
        return;
    }

    let { htmlContent, filename } = window.lastGeneratedForm;
    
    // If we have saved form data, use the filled version
    if (window.lastGeneratedForm.filledHtmlContent) {
        htmlContent = window.lastGeneratedForm.filledHtmlContent;
    }
    
    if (format === 'html') {
        // Download HTML directly
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success notification
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification(`HTML form downloaded as ${filename}!`, 'success');
        }
    } else {
        // For PDF/DOCX conversion, send request to backend with filled data
        const formData = {
            htmlContent: htmlContent,
            filename: filename.replace('.html', ''),
            format: format
        };
        
        // Show loading notification
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification(`Converting completed form to ${format.toUpperCase()}...`, 'info');
        }
        
        // Make API call to convert and download
        fetch('/api/convert-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error(`Failed to convert to ${format.toUpperCase()}`);
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${formData.filename}_completed.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success notification
            if (window.chatbotApp && window.chatbotApp.showNotification) {
                window.chatbotApp.showNotification(`Completed form downloaded as ${format.toUpperCase()}!`, 'success');
            }
        })
        .catch(error => {
            console.error('Conversion error:', error);
            if (window.chatbotApp && window.chatbotApp.showNotification) {
                window.chatbotApp.showNotification(`Failed to convert to ${format.toUpperCase()}: ${error.message}`, 'error');
            } else {
                alert(`Failed to convert to ${format.toUpperCase()}: ${error.message}`);
            }
        });
    }
}

// Function to initialize form data capture in the iframe
function initializeFormDataCapture(iframe) {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const form = iframeDoc.querySelector('form');
        
        // Replace placeholder download buttons with functional ones
        replacePlaceholderDownloadButtons(iframeDoc);
        
        if (form) {
            // Find and enhance the Submit Form button
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"], button');
            submitButtons.forEach(button => {
                const buttonText = button.textContent || button.value || '';
                if (buttonText.toLowerCase().includes('submit') || button.type === 'submit') {
                    // Replace submit button functionality
                    button.onclick = function(e) {
                        e.preventDefault();
                        
                        // Automatically save form data
                        saveFormData();
                        
                        // Show visual feedback
                        const originalText = button.textContent;
                        const originalBg = button.style.backgroundColor;
                        button.textContent = '✓ Saved!';
                        button.style.backgroundColor = '#48bb78';
                        button.style.color = 'white';
                        
                        // Reset button after 2 seconds
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.backgroundColor = originalBg;
                        }, 2000);
                        
                        return false;
                    };
                    
                    // Enhance button styling
                    button.style.cursor = 'pointer';
                    button.style.transition = 'all 0.3s ease';
                }
            });
            
            // Prevent default form submission
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                saveFormData();
                return false;
            });
            
            // Add auto-save on input changes
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('change', function() {
                    // Auto-save form data on changes (silent save)
                    if (window.lastGeneratedForm) {
                        const formData = captureFormData(iframe);
                        window.lastGeneratedForm.formData = formData;
                        const filledHTML = applyFormDataToHTML(window.lastGeneratedForm.htmlContent, formData);
                        window.lastGeneratedForm.filledHtmlContent = filledHTML;
                    }
                });
            });
        }
    } catch (error) {
        console.error('Error initializing form data capture:', error);
    }
}

// Function to replace placeholder download buttons with functional ones
function replacePlaceholderDownloadButtons(iframeDoc) {
    try {
        // Find and replace PDF download buttons
        const pdfButtons = iframeDoc.querySelectorAll('button, input[type="button"], a');
        pdfButtons.forEach(button => {
            const buttonText = button.textContent || button.value || '';
            if (buttonText.toLowerCase().includes('download pdf') || buttonText.toLowerCase().includes('pdf')) {
                button.onclick = function(e) {
                    e.preventDefault();
                    // Call the parent window's download function
                    window.parent.downloadFormAs('pdf');
                    return false;
                };
                button.style.cursor = 'pointer';
                button.style.backgroundColor = '#f56565';
                button.style.color = 'white';
                console.log('Replaced PDF download button');
            }
            
            // Replace DOCX download buttons
            if (buttonText.toLowerCase().includes('download docx') || buttonText.toLowerCase().includes('docx')) {
                button.onclick = function(e) {
                    e.preventDefault();
                    // Call the parent window's download function
                    window.parent.downloadFormAs('docx');
                    return false;
                };
                button.style.cursor = 'pointer';
                button.style.backgroundColor = '#4299e1';
                button.style.color = 'white';
                console.log('Replaced DOCX download button');
            }
        });
        
        // Also add onclick handlers to any JavaScript download functions in the iframe
        const scripts = iframeDoc.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.textContent.includes('PDF download functionality')) {
                // Replace the alert with actual functionality
                script.textContent = script.textContent.replace(
                    /alert\([^)]*PDF download[^)]*\);?/gi,
                    'window.parent.downloadFormAs("pdf");'
                );
            }
            if (script.textContent.includes('DOCX download functionality')) {
                // Replace the alert with actual functionality
                script.textContent = script.textContent.replace(
                    /alert\([^)]*DOCX download[^)]*\);?/gi,
                    'window.parent.downloadFormAs("docx");'
                );
            }
        });
        
    } catch (error) {
        console.error('Error replacing placeholder download buttons:', error);
    }
}

// Function to capture form data from the iframe
function captureFormData(iframe) {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const form = iframeDoc.querySelector('form');
        const formData = {};
        
        if (form) {
            // Capture all input types
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.name || input.id) {
                    const key = input.name || input.id;
                    
                    if (input.type === 'checkbox') {
                        if (input.checked) {
                            // For checkboxes, store the value or 'Yes' if no value
                            formData[key] = input.value || 'Yes';
                        }
                    } else if (input.type === 'radio') {
                        if (input.checked) {
                            formData[key] = input.value;
                        }
                    } else if (input.tagName.toLowerCase() === 'select') {
                        // For select elements, get the selected option
                        const selectedOption = input.options[input.selectedIndex];
                        if (selectedOption && selectedOption.value) {
                            formData[key] = selectedOption.value;
                        } else if (selectedOption && selectedOption.text) {
                            formData[key] = selectedOption.text;
                        }
                    } else {
                        // For text inputs, textareas, etc.
                        if (input.value && input.value.trim()) {
                            formData[key] = input.value.trim();
                        }
                    }
                }
            });
            
            // Additional pass: Look for any selected options that might be missed
            const selects = form.querySelectorAll('select');
            selects.forEach(select => {
                const key = select.name || select.id;
                if (key && select.value) {
                    formData[key] = select.value;
                }
            });
            
            // Additional pass: Look for checked items that might be missed
            const checkedItems = form.querySelectorAll('input:checked');
            checkedItems.forEach(item => {
                const key = item.name || item.id;
                if (key) {
                    if (item.type === 'checkbox' || item.type === 'radio') {
                        formData[key] = item.value || 'Yes';
                    }
                }
            });
        }
        
        console.log('Captured form data:', formData);
        return formData;
    } catch (error) {
        console.error('Error capturing form data:', error);
        return {};
    }
}

// Function to apply form data to HTML content
function applyFormDataToHTML(htmlContent, formData) {
    let updatedHTML = htmlContent;
    
    // Apply form data to the HTML by updating input values
    for (const [key, value] of Object.entries(formData)) {
        if (value) {
            // Update text input values
            updatedHTML = updatedHTML.replace(
                new RegExp(`(<input[^>]*name=["']${key}["'][^>]*type=["'](?:text|email|tel|url|password)["'][^>]*)>`, 'gi'),
                `$1 value="${value}">`
            );
            
            // Update input values (general pattern)
            updatedHTML = updatedHTML.replace(
                new RegExp(`(<input[^>]*name=["']${key}["'][^>]*)>`, 'gi'),
                `$1 value="${value}">`
            );
            
            // Update textarea values
            updatedHTML = updatedHTML.replace(
                new RegExp(`(<textarea[^>]*name=["']${key}["'][^>]*>)[^<]*</textarea>`, 'gi'),
                `$1${value}</textarea>`
            );
            
            // Update select values - mark option as selected
            // Pattern 1: Match exact value
            updatedHTML = updatedHTML.replace(
                new RegExp(`(<option[^>]*value=["']${value}["'][^>]*)(>)`, 'gi'),
                `$1 selected$2`
            );
            
            // Pattern 2: Match option text content
            updatedHTML = updatedHTML.replace(
                new RegExp(`(<option[^>]*>)(${value})(</option>)`, 'gi'),
                `<option selected>$2$3`
            );
            
            // Update checkbox/radio buttons
            if (value === 'Yes' || value === 'on' || value === '1') {
                updatedHTML = updatedHTML.replace(
                    new RegExp(`(<input[^>]*name=["']${key}["'][^>]*type=["'](?:checkbox|radio)["'][^>]*)(>)`, 'gi'),
                    `$1 checked$2`
                );
            } else {
                // For specific values, check the matching checkbox/radio
                updatedHTML = updatedHTML.replace(
                    new RegExp(`(<input[^>]*name=["']${key}["'][^>]*value=["']${value}["'][^>]*type=["'](?:checkbox|radio)["'][^>]*)(>)`, 'gi'),
                    `$1 checked$2`
                );
                updatedHTML = updatedHTML.replace(
                    new RegExp(`(<input[^>]*type=["'](?:checkbox|radio)["'][^>]*name=["']${key}["'][^>]*value=["']${value}["'][^>]*)(>)`, 'gi'),
                    `$1 checked$2`
                );
            }
        }
    }
    
    return updatedHTML;
}

// Function to save form data
function saveFormData() {
    const iframe = document.getElementById('htmlPreviewFrame');
    if (!iframe || !window.lastGeneratedForm) {
        alert('No form data to save');
        return;
    }
    
    try {
        // Capture current form data
        const formData = captureFormData(iframe);
        
        // Apply form data to HTML content
        const filledHTML = applyFormDataToHTML(window.lastGeneratedForm.htmlContent, formData);
        
        // Store the filled version
        window.lastGeneratedForm.formData = formData;
        window.lastGeneratedForm.filledHtmlContent = filledHTML;
        
        // Count filled fields for user feedback
        const filledFieldsCount = Object.keys(formData).filter(key => formData[key] && formData[key].trim()).length;
        
        // Show success notification with field count
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification(
                `Form data saved! ${filledFieldsCount} fields captured. Ready for PDF/DOCX download.`, 
                'success'
            );
        } else {
            alert(`Form data saved! ${filledFieldsCount} fields captured. Ready for download.`);
        }
        
        console.log('Saved form data:', formData);
        console.log(`Captured ${filledFieldsCount} filled fields`);
    } catch (error) {
        console.error('Error saving form data:', error);
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification('Error saving form data: ' + error.message, 'error');
        } else {
            alert('Error saving form data: ' + error.message);
        }
    }
}

// Function to edit company information
function editCompanyInfo() {
    if (!window.lastGeneratedForm) {
        alert('No form available for editing');
        return;
    }
    
    // Extract current company name from HTML (simple extraction)
    let currentCompanyName = 'Your Company Name';
    const companyMatch = window.lastGeneratedForm.htmlContent.match(/<h1[^>]*>([^<]+)</i);
    if (companyMatch) {
        currentCompanyName = companyMatch[1].trim();
    }
    
    // Create company info editor modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10001;
        backdrop-filter: blur(5px);
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        width: 500px;
        max-width: 90%;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
    `;
    
    modalContent.innerHTML = `
        <h3 style="margin: 0 0 20px 0; color: #2d3748; font-size: 20px;">
            <i class="fas fa-building" style="color: #667eea; margin-right: 10px;"></i>
            Edit Company Information
        </h3>
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">Company Name:</label>
            <input type="text" id="companyNameInput" value="${currentCompanyName}" style="
                width: 100%;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
            ">
        </div>
        <div style="margin-bottom: 20px;">
            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">Company Logo:</label>
            <div style="border: 2px dashed #e2e8f0; border-radius: 6px; padding: 20px; text-align: center; background: #f8f9fa;">
                <input type="file" id="companyLogoInput" accept="image/*" style="display: none;" onchange="handleLogoUpload(this)">
                <div id="logoPreview" style="margin-bottom: 15px; min-height: 60px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #718096; font-size: 14px;">No logo selected</span>
                </div>
                <button onclick="document.getElementById('companyLogoInput').click()" style="
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    <i class="fas fa-upload"></i> Choose Logo
                </button>
                <button onclick="clearLogo()" style="
                    background: #f56565;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-left: 10px;
                ">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
        </div>
        <div style="text-align: right;">
            <button onclick="this.closest('.modal-overlay').remove()" style="
                background: #e2e8f0;
                color: #4a5568;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                margin-right: 10px;
                cursor: pointer;
            ">Cancel</button>
            <button onclick="saveCompanyInfo()" style="
                background: #48bb78;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            ">Save Changes</button>
        </div>
    `;
    
    modal.className = 'modal-overlay';
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Focus on the input
    setTimeout(() => {
        document.getElementById('companyNameInput').focus();
        document.getElementById('companyNameInput').select();
    }, 100);
}

// Function to save company information
function saveCompanyInfo() {
    const input = document.getElementById('companyNameInput');
    const logoInput = document.getElementById('companyLogoInput');

    if (!input || !window.lastGeneratedForm) {
        return;
    }

    const newCompanyName = input.value.trim();
    if (!newCompanyName) {
        alert('Please enter a company name');
        return;
    }

    // Handle logo upload if provided
    let logoDataUrl = null;
    if (logoInput && logoInput.files && logoInput.files[0]) {
        const file = logoInput.files[0];

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file');
            return;
        }

        // Validate file size (max 2MB)
        if (file.size > 2 * 1024 * 1024) {
            alert('Logo file size must be less than 2MB');
            return;
        }

        // Convert to data URL
        const reader = new FileReader();
        reader.onload = function(e) {
            logoDataUrl = e.target.result;
            updateCompanyInfo(newCompanyName, logoDataUrl);
        };
        reader.readAsDataURL(file);
        return; // Exit here, updateCompanyInfo will be called from reader.onload
    }

    // No logo provided, just update company name
    updateCompanyInfo(newCompanyName, logoDataUrl);
}

// Separate function to handle the actual update
function updateCompanyInfo(companyName, logoDataUrl) {
    
    try {
        // Update company name in HTML content
        let updatedHTML = window.lastGeneratedForm.htmlContent;
        
        // Extract current company name from HTML (improved detection)
        let currentCompanyName = 'Your Company Name';
        
        // Enhanced company name detection - find ANY displayed text that could be company name
        const companyPatterns = [
            /<div[^>]*class="[^"]*company-name[^>]*>([^<]+)<\/div>/i, // Company name divs
            /<p[^>]*class="[^"]*company-name[^>]*>([^<]+)<\/p>/i,     // Company name paragraphs
            /<h1[^>]*>([^<]+)<\/h1>/i,                               // H1 tags
            /<h2[^>]*>([^<]+)<\/h2>/i,                               // H2 tags
            /<h3[^>]*>([^<]+)<\/h3>/i,                               // H3 tags
            /<span[^>]*color[^>]*>([^<]+)<\/span>/i,                 // Colored spans
            /<strong[^>]*>([^<]+)<\/strong>/i,                       // Strong tags
            /<b[^>]*>([^<]+)<\/b>/i,                                // Bold tags
            /<div[^>]*class="[^"]*form-title[^>]*>([^<]+)<\/div>/i,  // Form title divs
            /<p[^>]*style="[^"]*font-weight[^>]*>([^<]+)<\/p>/i     // Bold paragraphs
        ];
        
        // Find the most likely company name by checking patterns in order of priority
        for (let pattern of companyPatterns) {
            const matches = updatedHTML.match(new RegExp(pattern.source, 'gi'));
            if (matches) {
                for (let match of matches) {
                    const textMatch = match.match(pattern);
                    if (textMatch && textMatch[1]) {
                        const potential = textMatch[1].trim();
                        // Accept any meaningful text that's not obviously system text
                        if (potential.length > 1 && potential.length < 100 && 
                            !potential.toLowerCase().includes('submit') &&
                            !potential.toLowerCase().includes('button') &&
                            !potential.toLowerCase().includes('click') &&
                            !potential.toLowerCase().includes('required') &&
                            !potential.toLowerCase().includes('field') &&
                            !potential.toLowerCase().includes('form') &&
                            !potential.toLowerCase().includes('download') &&
                            !potential.toLowerCase().includes('clear') &&
                            !potential.toLowerCase().includes('reset') &&
                            !potential.match(/^[\s\*\-\.\(\)\[\]]+$/) &&
                            !potential.match(/^\d+$/) &&
                            !potential.match(/^[a-z_]+$/)) { // Skip variable names
                            currentCompanyName = potential;
                            console.log('Found company name via pattern:', potential);
                            break;
                        }
                    }
                }
                if (currentCompanyName !== 'Your Company Name') break;
            }
        }
        
        // If still no company name found, search for any substantial text content
        if (currentCompanyName === 'Your Company Name') {
            // Look for text content in common display elements
            const textElements = updatedHTML.match(/<(?:h[1-6]|p|div|span)[^>]*>([^<]{2,80})<\/(?:h[1-6]|p|div|span)>/gi);
            if (textElements) {
                for (let element of textElements) {
                    const textMatch = element.match(/>([^<]+)</)
                    if (textMatch) {
                        const text = textMatch[1].trim();
                        // More permissive acceptance for any reasonable text
                        if (text && text.length >= 3 && text.length <= 80 &&
                            !text.toLowerCase().includes('submit') &&
                            !text.toLowerCase().includes('required') &&
                            !text.toLowerCase().includes('field') &&
                            !text.toLowerCase().includes('button') &&
                            !text.toLowerCase().includes('download') &&
                            !text.toLowerCase().includes('instructions') &&
                            !text.toLowerCase().includes('progress') &&
                            !text.toLowerCase().includes('completion') &&
                            !text.toLowerCase().includes('form id') &&
                            !text.toLowerCase().includes('created') &&
                            !text.toLowerCase().includes('section') &&
                            !text.toLowerCase().includes('click') &&
                            !text.toLowerCase().includes('clear') &&
                            !text.toLowerCase().includes('data') &&
                            !text.match(/^[\s\*\-\.\(\)\[\]]+$/) &&
                            !text.match(/^\d+%?$/) &&
                            !text.match(/^[a-z_]+$/) &&
                            !text.includes('://') && // Skip URLs
                            !text.includes('@') &&   // Skip emails
                            !/^\d+\s*(minute|field|section)/i.test(text)) { // Skip counts
                            currentCompanyName = text;
                            console.log('Found text-based company name:', text);
                            break;
                        }
                    }
                }
            }
        }
        
        console.log('Current company name detected:', currentCompanyName);
        console.log('New company name:', newCompanyName);
        
        // Handle logo upload if present
        let logoHTML = '';
        if (window.selectedLogo) {
            logoHTML = `<div style="text-align: center; margin-bottom: 20px;">
                <img src="${window.selectedLogo.data}" alt="${newCompanyName} Logo" style="
                    max-width: 150px;
                    max-height: 80px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                ">
            </div>`;
            
            // Store logo in form data
            window.lastGeneratedForm.companyLogo = window.selectedLogo;
        }
        
        // Replace the current company name with the new one
        // Use a more flexible approach to replace the actual current name
        const escapeRegex = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const currentNameRegex = new RegExp(escapeRegex(currentCompanyName), 'gi');
        
        updatedHTML = updatedHTML.replace(currentNameRegex, newCompanyName);
        
        // Also replace common placeholder patterns
        updatedHTML = updatedHTML.replace(/Your Company Name/gi, newCompanyName);
        updatedHTML = updatedHTML.replace(/\[Your Company Name\]/gi, newCompanyName);
        updatedHTML = updatedHTML.replace(/\[Company Name\]/gi, newCompanyName);
        updatedHTML = updatedHTML.replace(/Company Name/gi, newCompanyName);
        
        // Insert logo HTML after the opening body tag or at the top of content
        if (logoHTML) {
            // Try to insert after body tag
            if (updatedHTML.includes('<body')) {
                updatedHTML = updatedHTML.replace(/(<body[^>]*>)/i, `$1\n${logoHTML}`);
            } else {
                // If no body tag, insert at the beginning of content
                const contentStart = updatedHTML.indexOf('<div') || updatedHTML.indexOf('<form') || 0;
                if (contentStart > 0) {
                    updatedHTML = updatedHTML.slice(0, contentStart) + logoHTML + updatedHTML.slice(contentStart);
                } else {
                    updatedHTML = logoHTML + updatedHTML;
                }
            }
        }
        
        // Replace email domains (handle both current and placeholder)
        const currentDomain = currentCompanyName.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/gi, '');
        const newDomain = newCompanyName.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/gi, '');
        
        updatedHTML = updatedHTML.replace(/@yourcompany\.com/gi, `@${newDomain}.com`);
        updatedHTML = updatedHTML.replace(/support@yourcompany\.com/gi, `support@${newDomain}.com`);
        updatedHTML = updatedHTML.replace(new RegExp(`@${escapeRegex(currentDomain)}\.com`, 'gi'), `@${newDomain}.com`);
        updatedHTML = updatedHTML.replace(new RegExp(`support@${escapeRegex(currentDomain)}\.com`, 'gi'), `support@${newDomain}.com`);
        
        // Update the stored HTML content
        window.lastGeneratedForm.htmlContent = updatedHTML;
        window.lastGeneratedForm.companyName = newCompanyName; // Store for easy access
        
        // If we have filled content, update that too
        if (window.lastGeneratedForm.filledHtmlContent) {
            let filledHTML = window.lastGeneratedForm.filledHtmlContent;
            filledHTML = filledHTML.replace(currentNameRegex, newCompanyName);
            filledHTML = filledHTML.replace(/Your Company Name/gi, newCompanyName);
            filledHTML = filledHTML.replace(/\[Your Company Name\]/gi, newCompanyName);
            filledHTML = filledHTML.replace(/\[Company Name\]/gi, newCompanyName);
            filledHTML = filledHTML.replace(/Company Name/gi, newCompanyName);
            filledHTML = filledHTML.replace(/@yourcompany\.com/gi, `@${newDomain}.com`);
            filledHTML = filledHTML.replace(/support@yourcompany\.com/gi, `support@${newDomain}.com`);
            filledHTML = filledHTML.replace(new RegExp(`@${escapeRegex(currentDomain)}\.com`, 'gi'), `@${newDomain}.com`);
            
            // Add logo to filled content too
            if (logoHTML) {
                if (filledHTML.includes('<body')) {
                    filledHTML = filledHTML.replace(/(<body[^>]*>)/i, `$1\n${logoHTML}`);
                } else {
                    const contentStart = filledHTML.indexOf('<div') || filledHTML.indexOf('<form') || 0;
                    if (contentStart > 0) {
                        filledHTML = filledHTML.slice(0, contentStart) + logoHTML + filledHTML.slice(contentStart);
                    } else {
                        filledHTML = logoHTML + filledHTML;
                    }
                }
            }
            
            window.lastGeneratedForm.filledHtmlContent = filledHTML;
        }
        
        // Close the modal immediately with comprehensive cleanup
        try {
            // Primary approach - find the exact modal
            const saveButton = document.querySelector('button[onclick="saveCompanyInfo()"]');
            if (saveButton) {
                const modal = saveButton.closest('.modal-overlay');
                if (modal) {
                    modal.remove();
                }
            }
            
            // Secondary approach - remove all modal overlays
            const allModals = document.querySelectorAll('.modal-overlay');
            allModals.forEach(m => {
                try {
                    m.remove();
                } catch (e) {
                    console.warn('Error removing modal:', e);
                }
            });
            
            // Tertiary approach - remove by style attributes
            const overlays = document.querySelectorAll('div[style*="position: fixed"]');
            overlays.forEach(overlay => {
                if (overlay.style.zIndex === '10001' || 
                    overlay.style.backgroundColor === 'rgba(0, 0, 0, 0.5)' ||
                    overlay.querySelector('button[onclick*="saveCompanyInfo"]')) {
                    try {
                        overlay.remove();
                    } catch (e) {
                        console.warn('Error removing overlay:', e);
                    }
                }
            });
            
            // Final cleanup - remove any remaining modal-like elements
            const modalElements = document.querySelectorAll('[class*="modal"], [id*="modal"]');
            modalElements.forEach(element => {
                if (element.style.position === 'fixed' || 
                    element.style.zIndex === '10001' ||
                    element.querySelector('input[id="companyNameInput"]')) {
                    try {
                        element.remove();
                    } catch (e) {
                        console.warn('Error removing modal element:', e);
                    }
                }
            });
            
            // Clear any modal-related event listeners
            document.removeEventListener('keydown', arguments.callee);
            
        } catch (error) {
            console.error('Error during modal cleanup:', error);
        }
        
        // Refresh the preview if it's open
        const iframe = document.getElementById('htmlPreviewFrame');
        if (iframe) {
            try {
                // Use srcdoc for better compatibility
                iframe.srcdoc = updatedHTML;
                
                // Wait for iframe to load and then initialize
                iframe.onload = function() {
                    initializeFormDataCapture(iframe);
                };
                
                // Fallback for older browsers
                setTimeout(() => {
                    if (iframe.contentDocument) {
                        initializeFormDataCapture(iframe);
                    }
                }, 500);
            } catch (e) {
                console.warn('Error updating iframe:', e);
                // Fallback method
                try {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    iframeDoc.open();
                    iframeDoc.write(updatedHTML);
                    iframeDoc.close();
                    initializeFormDataCapture(iframe);
                } catch (e2) {
                    console.error('Failed to update iframe with both methods:', e2);
                }
            }
        }
        
        // Show success notification
        if (window.chatbotApp && window.chatbotApp.showNotification) {
            window.chatbotApp.showNotification(`Company name updated to "${newCompanyName}"!`, 'success');
        } else {
            alert(`Company name updated to "${newCompanyName}"!`);
        }
        
        console.log('Company name updated successfully from:', currentCompanyName, 'to:', newCompanyName);
    } catch (error) {
        console.error('Error updating company name:', error);
        alert('Error updating company name: ' + error.message);
    }
}

// Function to handle logo upload
function handleLogoUpload(input) {
    const file = input.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            return;
        }
        
        // Validate file size (max 2MB)
        if (file.size > 2 * 1024 * 1024) {
            alert('Please select an image smaller than 2MB.');
            return;
        }
        
        // Create file reader
        const reader = new FileReader();
        reader.onload = function(e) {
            const logoPreview = document.getElementById('logoPreview');
            logoPreview.innerHTML = `
                <img src="${e.target.result}" style="
                    max-width: 100px;
                    max-height: 60px;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                " alt="Company Logo">
            `;
            
            // Store logo data for saving
            window.selectedLogo = {
                data: e.target.result,
                name: file.name,
                type: file.type
            };
        };
        reader.readAsDataURL(file);
    }
}

// Function to clear logo
function clearLogo() {
    const logoPreview = document.getElementById('logoPreview');
    logoPreview.innerHTML = '<span style="color: #718096; font-size: 14px;">No logo selected</span>';
    
    // Clear file input
    const logoInput = document.getElementById('companyLogoInput');
    if (logoInput) {
        logoInput.value = '';
    }
    
    // Clear stored logo data
    window.selectedLogo = null;
}
