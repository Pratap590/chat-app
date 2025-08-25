#!/usr/bin/env python3
"""
Simple FastAPI server to test the agents UI
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Chatbot System",
    description="Web interface for document RAG, form generation, API execution, and analytics",
    version="1.0.0"
)

# Create directories for static files
static_dir = Path("static")
templates_dir = Path("templates")

for directory in [static_dir, templates_dir]:
    directory.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/agents")
async def get_agents():
    """Get available agents and their descriptions"""
    agents = {
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
    }
    return agents

@app.get("/api/tenants")
async def list_tenants():
    """List all available tenants"""
    tenants = [{
        "tenant_id": "default",
        "name": "Default Tenant",
        "permissions": ["read_documents", "use_tools", "generate_forms"]
    }]
    return {"tenants": tenants}

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """Simple chat endpoint for testing"""
    return {
        "success": True,
        "response": f"This is a test response for agent '{request.get('agent_type', 'unknown')}'. The full system is not loaded yet, but the UI should work!",
        "agent": request.get('agent_type', 'unknown'),
        "timestamp": "2025-08-15T20:21:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Multi-Agent Chatbot Web Interface...")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
