# Multi-Agent Chatbot System - Milestone 1 Implementation

A comprehensive multi-agent chatbot system built with LangGraph, LangChain, and Google's Gemini AI, featuring tenant isolation, RAG capabilities, dynamic API connectivity, and form generation.

## 🚀 Features

### ✅ Milestone 1 Complete Implementation

1. **Modular Multi-Agent System**
   - 5 specialized agents: Document Q&A, API Execution, Form Generation, Greeting, and Escalation
   - Enhanced LangGraph orchestration with memory and tool handling
   - Intelligent routing based on user intent

2. **Retrieval-Augmented Generation (RAG)**
   - Tenant-isolated document indexing with FAISS
   - Support for PDF, DOCX, TXT, MD, CSV, and JSON files
   - Enhanced metadata tracking and file change detection
   - Similarity-based retrieval with scoring

3. **Dynamic API Connectivity**
   - HTTP GET and POST tool generation
   - Rate limiting and error handling
   - Tool usage statistics and monitoring
   - Tenant-specific tool registration

4. **Enhanced Features**
   - Authentication and tenant management
   - Permission-based access control
   - Form generation with validation
   - Admin dashboard with system statistics
   - Comprehensive error handling and logging
   - Escalation workflow with ticket generation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Router Agent   │───▶│  Specialized    │
└─────────────────┘    └──────────────────┘    │     Agents      │
                                │               └─────────────────┘
                                ▼                        │
                       ┌──────────────────┐             ▼
                       │  Tool Execution  │    ┌─────────────────┐
                       │      Node        │    │   Response      │
                       └──────────────────┘    │   Generation    │
                                               └─────────────────┘
```

## 🛠️ Installation

1. **Clone and Setup**
```bash
git clone <repository>
cd multi-agent-chatbot
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
# Create .env file
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.0-flash
HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

3. **Run the System**
```bash
python main.py
```

## 📖 Usage Guide

### Basic Commands

```bash
# Set active tenant
/tenant default

# Create new tenant (admin permission required)
/create-tenant company1 "Company One"

# Ingest documents
/ingest ./documents/company_docs

# Register API tools
/tool.httpget weather_api WEATHER_API_BASE_URL WEATHER_API_KEY
/tool.httppost slack_api SLACK_API_BASE_URL SLACK_BOT_TOKEN

# View available tools
/tools

# Check system statistics
/stats

# Generate admin dashboard
/dashboard

# Show permissions
/permissions

# Get help
/help
```

### Agent Interactions

1. **Document Q&A Agent**
```
User: "What is our company policy on remote work?"
Bot: [Searches indexed documents and provides policy information]
```

2. **API Execution Agent**
```
User: "What's the weather in New York?"
Bot: [Uses weather API tool to fetch current weather]
```

3. **Form Generation Agent**
```
User: "Create a customer feedback form"
Bot: [Generates structured JSON form with validation]
```

4. **Escalation Agent**
```
User: "I need to speak with a human agent"
Bot: [Creates escalation ticket and provides reference ID]
```

## 🔧 Configuration

### Tenant Management

```python
# Create tenant with custom permissions
create_tenant(
    tenant_id="enterprise_client",
    name="Enterprise Client Corp",
    permissions=["read_documents", "use_tools", "generate_forms", "admin"]
)

# Set rate limits
config = get_tenant_config("enterprise_client")
config.rate_limits = {
    "default": 0.5,
    "search_web": 2.0,
    "api_calls": 1.0
}
```

### Tool Registration

```python
# Register custom HTTP GET tool
weather_tool = make_http_get_tool(
    name="weather_lookup",
    description="Get weather information for any city",
    base_url_env="WEATHER_API_BASE",
    api_key_env="WEATHER_API_KEY",
    rate_limit_seconds=1.0
)

register_dynamic_tool("tenant_id", weather_tool)
```

### Document Ingestion

```python
# Ingest documents with custom settings
result = ingest_documents_from_dir(
    tenant_id="company1",
    source_dir="./company_documents",
    chunk_size=1500,
    chunk_overlap=200
)
```

## 📊 Monitoring & Analytics

### System Statistics
- Tenant activity and document counts
- Tool usage and success rates
- Session management
- Error tracking and logging

### Admin Dashboard
- HTML dashboard with real-time statistics
- Tenant overview and management
- Tool performance metrics
- System health monitoring

## 🔒 Security Features

### Authentication & Authorization
- Tenant-based isolation
- Session management with tokens
- Permission-based access control
- API key management

### Data Protection
- Tenant-specific document storage
- Isolated vector databases
- Secure API key handling
- Rate limiting and abuse prevention

## 🧪 Testing

### Manual Testing Scenarios

1. **Multi-Tenant Isolation**
```bash
/tenant company1
/ingest ./company1_docs
# Switch tenant
/tenant company2
/ingest ./company2_docs
# Verify documents are isolated
```

2. **API Tool Integration**
```bash
/tool.httpget github_api GITHUB_API_BASE GITHUB_TOKEN
# Test API call
"Get my GitHub repositories"
```

3. **Form Generation**
```bash
# Request form generation
"Create a job application form with name, email, resume upload, and cover letter"
```

4. **Escalation Workflow**
```bash
# Trigger escalation
"I need immediate help with a critical issue"
```

## 📈 Performance Optimization

### Rate Limiting
- Per-tool rate limiting
- Tenant-specific limits
- Adaptive throttling

### Caching
- Vector database caching
- API response caching
- Session state management

### Scalability
- Modular agent architecture
- Stateless design
- Horizontal scaling ready

## 🔮 Future Enhancements

### Planned Features
- Database persistence
- Real-time notifications
- Advanced analytics
- Multi-language support
- Voice interface
- Mobile app integration

### Integration Possibilities
- CRM systems
- Help desk platforms
- Business intelligence tools
- Communication platforms

## 🐛 Troubleshooting

### Common Issues

1. **Google API Key Issues**
```bash
# Verify API key is set
echo $GOOGLE_API_KEY
# Check model availability
/stats
```

2. **Document Ingestion Problems**
```bash
# Check file permissions
ls -la ./documents/
# Verify supported formats
/help
```

3. **Tool Registration Failures**
```bash
# Check environment variables
env | grep API
# Verify permissions
/permissions
```

## 📝 API Reference

### Core Functions

- `create_tenant(tenant_id, name, permissions)` - Create new tenant
- `authenticate_tenant(tenant_id, api_key)` - Authenticate tenant
- `register_dynamic_tool(tenant_id, tool, metadata)` - Register API tool
- `ingest_documents_from_dir(tenant_id, path)` - Ingest documents
- `get_system_stats()` - Get system statistics

### Agent Nodes

- `node_router(state)` - Route to appropriate agent
- `node_doc_qa(state)` - Handle document questions
- `node_api_exec(state)` - Execute API calls
- `node_form_gen(state)` - Generate forms
- `node_escalate(state)` - Handle escalations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create GitHub issue
- Check troubleshooting guide
- Use escalation feature in chatbot

---

**Milestone 1 Status: ✅ COMPLETE**

All required features have been implemented and tested:
- ✅ Modular Multi-Agent System with LangGraph
- ✅ RAG with tenant isolation
- ✅ Dynamic API connectivity
- ✅ Enhanced features and monitoring