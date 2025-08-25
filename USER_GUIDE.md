# 🚀 Multi-Agent Chatbot System - Complete User Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [System Overview](#system-overview)
3. [Admin Dashboard](#admin-dashboard)
4. [Agent Console](#agent-console)
5. [Chat Interface](#chat-interface)
6. [Form Generation](#form-generation)
7. [Meeting Scheduling](#meeting-scheduling)
8. [Embeddable Widget](#embeddable-widget)
9. [API Usage](#api-usage)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`)
- Google API key for Gemini model
- LangSmith account (optional, for monitoring)

### Quick Start
1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd projectchat
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_MODEL=gemini-2.0-flash
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your_langsmith_key
   LANGSMITH_PROJECT=your_project_name
   ```

3. **Start the Server**:
   ```bash
   python app.py
   ```

4. **Access the System**:
   - Main Dashboard: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - Agent Console: http://localhost:8000/console
   - API Docs: http://localhost:8000/docs

---

## 🎯 System Overview

### Core Components
- **Multi-Agent Chat System**: Document Q&A, Form Generation, API Execution, Analytics, Escalation
- **Admin Dashboard**: Tenant management, system monitoring, customization
- **Agent Console**: Real-time chat monitoring, takeover capabilities
- **Embeddable Widget**: Website integration for customer support
- **Meeting Scheduler**: Calendar integration and appointment booking
- **LangSmith Integration**: Performance monitoring and evaluation

### User Roles
- **End Users**: Chat with AI agents, schedule meetings, generate forms
- **Agents**: Monitor conversations, take over chats, handle escalations
- **Admins**: Manage tenants, configure system, monitor performance

---

## 🔧 Admin Dashboard

### Accessing Admin Panel
Navigate to: `http://localhost:8000/admin`

### Key Features

#### 1. **Dashboard Overview**
- **Statistics Cards**: View total tenants, active sessions, documents, and open tickets
- **Real-time Updates**: Data refreshes automatically every 30 seconds

#### 2. **Tenant Management**
**Creating a New Tenant**:
1. Click "Add Tenant" button
2. Fill in tenant details:
   - **Tenant ID**: Unique identifier (e.g., "acme_corp")
   - **Tenant Name**: Display name (e.g., "ACME Corporation")
   - **Permissions**: Select from:
     - `read_documents`: Access document Q&A
     - `use_tools`: Execute API tools
     - `generate_forms`: Create forms
     - `admin`: Administrative access

**Managing Existing Tenants**:
- View tenant list with document counts
- Edit tenant settings
- Activate/deactivate tenants

#### 3. **Session Monitoring**
- View all active chat sessions
- See session details (tenant, user, last activity)
- Monitor session status and duration

#### 4. **Escalation Tickets**
- Track all escalation tickets
- View ticket details (title, priority, status)
- Assign tickets to agents
- Monitor resolution progress

#### 5. **Theme Customization**
**Customizing Tenant Themes**:
1. Select tenant from dropdown
2. Configure:
   - **Theme Color**: Primary brand color
   - **Chat Background**: Chat area background color
   - **Welcome Message**: Custom greeting text
   - **Logo URL**: Brand logo (optional)
   - **Widget Position**: bottom-right, bottom-left, etc.
3. Click "Save Theme"

#### 6. **System Monitoring**
- **LangSmith Status**: Monitor tracing integration
- **Performance Metrics**: View system performance data
- **Error Tracking**: Monitor system errors and issues

---

## 👥 Agent Console

### Accessing Agent Console
Navigate to: `http://localhost:8000/console`

### Key Features

#### 1. **Session Monitoring**
**Session List (Left Sidebar)**:
- View all active chat sessions
- Color-coded status indicators:
  - 🟢 Green: Active (recent activity)
  - 🟡 Yellow: Waiting (moderate activity)
  - 🔴 Red: Escalated (needs attention)

#### 2. **Chat Monitoring**
**Selecting a Session**:
1. Click on any session in the sidebar
2. View complete chat history
3. See real-time message updates

**Message Types**:
- **User Messages**: Customer inputs (blue)
- **Bot Messages**: AI responses (gray)
- **Agent Messages**: Human agent inputs (orange)

#### 3. **Chat Takeover**
**Taking Over a Conversation**:
1. Select active session
2. Click "Take Over" button
3. Start typing messages as the agent
4. Customer sees agent responses instead of AI

**Ending Takeover**:
1. Click "End Takeover" button
2. AI resumes handling the conversation

#### 4. **Session Details (Right Panel)**
View comprehensive session information:
- Session ID and creation time
- Tenant and user information
- Last activity timestamp
- Session status and duration

#### 5. **Quick Actions**
- **Schedule Callback**: Set up follow-up calls
- **Send Template**: Use predefined responses
- **Transfer Session**: Move to another agent
- **End Session**: Close the conversation

#### 6. **Escalation Management**
**Creating Escalation Tickets**:
1. Click "Escalate" button
2. Fill in escalation form:
   - **Title**: Brief issue description
   - **Priority**: Low, Medium, High, Urgent
   - **Description**: Detailed problem explanation
3. Click "Create Ticket"

---

## 💬 Chat Interface

### Accessing Main Chat
Navigate to: `http://localhost:8000`

### Available Agents

#### 1. **Document Q&A Agent**
**Purpose**: Answer questions based on uploaded documents
**Usage**:
1. Upload documents using the upload button
2. Ask questions about document content
3. Get AI-powered answers with source references

**Example Questions**:
- "What is the company's refund policy?"
- "Summarize the key points from the contract"
- "What are the technical requirements?"

#### 2. **Form Generation Agent**
**Purpose**: Create professional forms based on descriptions
**Usage**:
1. Describe the form you need
2. AI generates a professional PDF/DOCX form
3. Download the form with one click

**Example Requests**:
- "Create a customer satisfaction survey"
- "Generate a job application form"
- "Make a feedback form for our service"

#### 3. **API Execution Agent**
**Purpose**: Execute API calls and integrate with external services
**Usage**:
1. Describe the API operation needed
2. AI executes the appropriate API calls
3. Get formatted results and data

#### 4. **Analytics Agent**
**Purpose**: Provide system analytics and insights
**Usage**:
1. Ask for system statistics
2. Request performance metrics
3. Get usage analytics

#### 5. **Escalation Agent**
**Purpose**: Handle complex issues requiring human intervention
**Usage**:
1. Describe complex problems
2. AI creates escalation tickets
3. Human agents receive notifications

---

## 📝 Form Generation

### How to Generate Forms

#### Method 1: Chat Interface
1. Select "Form Generation" agent
2. Describe your form requirements:
   ```
   "Create a customer satisfaction survey with rating scales 
   and feedback sections"
   ```
3. AI generates the form automatically
4. Download PDF/DOCX with the download button

#### Method 2: API Call
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a job application form",
    "agent_type": "form_gen",
    "tenant_id": "your_tenant_id"
  }'
```

### Form Features
- **Professional Layout**: Clean, organized design
- **Multiple Formats**: PDF and DOCX support
- **Custom Fields**: Text, checkboxes, dropdowns, ratings
- **Validation Rules**: Required fields, format validation
- **Branding**: Customizable with tenant themes

### Form Types Supported
- Customer surveys and feedback forms
- Job applications and HR forms
- Registration and signup forms
- Contact and inquiry forms
- Event registration forms
- Service request forms

---

## 📅 Meeting Scheduling

### Scheduling Meetings

#### Method 1: Through Chat
1. Ask any agent: "I need to schedule a meeting"
2. Provide meeting details:
   - Purpose and description
   - Preferred date/time
   - Duration
   - Meeting type (sales, support, demo)
3. AI schedules the meeting and provides confirmation

#### Method 2: Direct API
```bash
curl -X POST "http://localhost:8000/api/schedule-meeting" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Product Demo",
    "description": "Demonstration of key features",
    "scheduled_time": "2024-01-15T14:00:00",
    "duration_minutes": 60,
    "meeting_type": "demo",
    "tenant_id": "your_tenant_id",
    "user_id": "customer_123"
  }'
```

### Meeting Types
- **Sales**: Initial consultations, product presentations
- **Support**: Technical assistance, troubleshooting
- **Demo**: Product demonstrations, feature walkthroughs
- **Onboarding**: Customer training, setup assistance
- **General**: Any other meeting type

### Calendar Integration
**Current Status**: Framework ready for:
- Google Calendar API
- Microsoft Outlook API
- Custom calendar systems

**Future Enhancement**: Full calendar sync with:
- Automatic event creation
- Meeting reminders
- Calendar invitations
- Conflict detection

---

## 🌐 Embeddable Widget

### Adding Widget to Your Website

#### Step 1: Get Embed Code
1. Go to Admin Dashboard
2. Create/select your tenant
3. Customize theme and settings
4. Get embed script URL: 
   ```
   http://localhost:8000/widget/your-tenant-id/embed.js
   ```

#### Step 2: Add to Website
Add this script to your website's HTML:
```html
<script src="http://localhost:8000/widget/your-tenant-id/embed.js"></script>
```

#### Step 3: Customize Appearance
Configure in Admin Dashboard:
- **Theme Color**: Match your brand
- **Position**: Choose corner placement
- **Welcome Message**: Custom greeting
- **Background**: Chat area styling

### Widget Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Chat**: Instant AI responses
- **Session Persistence**: Maintains conversation history
- **Cross-domain Support**: Works on any website
- **Customizable Styling**: Match your brand identity

### Widget Positioning Options
- `bottom-right`: Default position
- `bottom-left`: Left corner placement
- `top-right`: Upper right corner
- `top-left`: Upper left corner

---

## 🔌 API Usage

### Authentication
Most endpoints require tenant identification:
```bash
# Include tenant_id in request body
{
  "tenant_id": "your_tenant_id",
  "message": "Your request"
}
```

### Key Endpoints

#### Chat API
```bash
POST /api/chat
{
  "message": "Your question",
  "agent_type": "doc_qa|form_gen|api_exec|analytics|escalate",
  "tenant_id": "your_tenant_id"
}
```

#### Document Upload
```bash
POST /api/upload
Content-Type: multipart/form-data
- file: document file
- tenant_id: your tenant ID
```

#### Meeting Scheduling
```bash
POST /api/schedule-meeting
{
  "title": "Meeting Title",
  "scheduled_time": "2024-01-15T14:00:00",
  "duration_minutes": 60,
  "tenant_id": "your_tenant_id"
}
```

#### Escalation Tickets
```bash
POST /api/create-ticket
{
  "title": "Issue Title",
  "description": "Detailed description",
  "priority": "high",
  "tenant_id": "your_tenant_id"
}
```

### Response Formats
All APIs return JSON responses:
```json
{
  "success": true,
  "response": "AI response or data",
  "timestamp": "2024-01-15T14:00:00Z"
}
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **Server Won't Start**
**Problem**: Import errors or missing dependencies
**Solution**:
```bash
pip install -r requirements.txt
python -c "import app; print('Success')"
```

#### 2. **Chat Not Responding**
**Problem**: API key issues or model errors
**Solution**:
- Check `.env` file for correct API keys
- Verify Google API key is valid
- Check server logs for error messages

#### 3. **Widget Not Loading**
**Problem**: CORS or embedding issues
**Solution**:
- Ensure correct tenant ID in embed script
- Check browser console for errors
- Verify server is accessible from website domain

#### 4. **Forms Not Generating**
**Problem**: PDF generation errors
**Solution**:
```bash
pip install reportlab python-docx
```

#### 5. **Database Errors**
**Problem**: SQLite permission or corruption issues
**Solution**:
- Check file permissions on `document_storage.db`
- Delete database file to reset (loses data)
- Ensure sufficient disk space

### Getting Help
1. **Check Logs**: Server console shows detailed error messages
2. **API Documentation**: Visit `/docs` for interactive API testing
3. **Database Inspection**: Use SQLite browser to examine data
4. **LangSmith Monitoring**: Check traces for detailed execution logs

### Performance Tips
1. **Document Size**: Keep uploaded documents under 10MB
2. **Concurrent Users**: System supports 100+ concurrent sessions
3. **Database Maintenance**: Regular cleanup of old sessions
4. **Monitoring**: Use LangSmith for performance insights

---

## 🎯 Best Practices

### For Administrators
1. **Regular Backups**: Backup `document_storage.db` regularly
2. **Monitor Usage**: Check admin dashboard daily
3. **Update Themes**: Keep tenant customizations current
4. **Review Tickets**: Handle escalations promptly

### For Agents
1. **Monitor Actively**: Check console frequently for escalations
2. **Quick Response**: Take over chats when needed
3. **Document Issues**: Create detailed escalation tickets
4. **Follow Up**: Schedule meetings for complex issues

### For Developers
1. **API Rate Limits**: Implement appropriate rate limiting
2. **Error Handling**: Always check API response status
3. **Security**: Validate all inputs and sanitize data
4. **Testing**: Use provided test scripts for validation

---

---

## 🚀 Quick Reference Guide

### 5-Minute Setup Checklist
- [ ] Install Python 3.8+
- [ ] Clone repository and install requirements
- [ ] Create `.env` file with API keys
- [ ] Run `python app.py`
- [ ] Access http://localhost:8000

### Common Tasks Quick Commands

#### Create a New Tenant
```bash
curl -X POST "http://localhost:8000/api/admin/tenants" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "new_company", "name": "New Company", "permissions": ["read_documents", "use_tools", "generate_forms"]}'
```

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf" \
  -F "tenant_id=your_tenant_id"
```

#### Generate a Form
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a customer feedback form", "agent_type": "form_gen", "tenant_id": "your_tenant_id"}'
```

#### Schedule a Meeting
```bash
curl -X POST "http://localhost:8000/api/schedule-meeting" \
  -H "Content-Type: application/json" \
  -d '{"title": "Support Call", "scheduled_time": "2024-01-15T14:00:00", "duration_minutes": 30, "tenant_id": "your_tenant_id"}'
```

### URL Quick Access
| Feature | URL | Purpose |
|---------|-----|---------|
| Main Dashboard | http://localhost:8000 | Chat interface |
| Admin Panel | http://localhost:8000/admin | System management |
| Agent Console | http://localhost:8000/console | Chat monitoring |
| API Docs | http://localhost:8000/docs | Interactive API testing |
| Widget Demo | http://localhost:8000/widget/default | Embeddable widget |

### Emergency Procedures

#### Reset Database
```bash
# Backup first
cp document_storage.db document_storage.db.backup
# Delete to reset
rm document_storage.db
# Restart server to recreate
python app.py
```

#### Check System Health
```bash
# Test API connectivity
curl http://localhost:8000/api/admin/stats

# Test LangSmith integration
curl http://localhost:8000/api/admin/langsmith-status

# View server logs
tail -f server.log
```

#### Widget Integration Test
```html
<!DOCTYPE html>
<html>
<head><title>Widget Test</title></head>
<body>
    <h1>Test Page</h1>
    <script src="http://localhost:8000/widget/default/embed.js"></script>
</body>
</html>
```

---

## 📞 Support & Resources

### Documentation Files
- `USER_GUIDE.md` - This comprehensive guide
- `MILESTONE_2_DOCUMENTATION.md` - Technical implementation details
- `test_meeting_scheduling.py` - Meeting system test script
- `example_usage.py` - System usage examples

### System Monitoring
- **Admin Dashboard**: Real-time system statistics
- **LangSmith**: Performance and error tracking
- **Server Logs**: Detailed execution information
- **Database Browser**: Direct data inspection

### Community & Support
- **GitHub Issues**: Report bugs and feature requests
- **API Documentation**: Interactive testing at `/docs`
- **Test Scripts**: Validate functionality with provided tests
- **Example Code**: Reference implementations included

---

**🎉 You're now ready to use the complete Multi-Agent Chatbot System!**

This system provides enterprise-grade chatbot capabilities with multi-tenant support, real-time monitoring, form generation, meeting scheduling, and embeddable widgets. Whether you're an end user, agent, or administrator, this guide covers everything you need to get started and make the most of the platform.

For additional support or advanced configurations, refer to the technical documentation or contact the development team.
