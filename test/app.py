#!/usr/bin/env python3
"""
FastAPI GUI Application for Multi-Agent Chatbot System
Provides web interface for all agents with file upload, download, and interactive features
"""

import os
import json
import tempfile
import shutil
import sqlite3
import secrets
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

# Import our main chatbot system
from main import (
    chat_with_agent, create_tenant, get_tenant_config,
    ingest_documents_from_dir, get_system_stats, get_tool_stats,
    FORM_GENERATOR, _json_to_professional_form,
    node_form_gen, node_doc_qa, node_api_exec, node_analytics, node_escalate,
    CURRENT_TENANT_ID, set_current_tenant
)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Chatbot System",
    description="Web interface for document RAG, form generation, API execution, and analytics",
    version="1.0.0"
)

# Create directories for static files and uploads
static_dir = Path("static")
templates_dir = Path("templates")
uploads_dir = Path("uploads")
downloads_dir = Path("downloads")

for directory in [static_dir, templates_dir, uploads_dir, downloads_dir]:
    directory.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for API requests
class ChatRequest(BaseModel):
    message: str
    agent_type: str
    tenant_id: str = "default"

class FormGenerationRequest(BaseModel):
    description: str
    format: str = "pdf"  # pdf or docx
    tenant_id: str = "default"

class TenantRequest(BaseModel):
    tenant_id: str
    name: str
    permissions: List[str] = ["read_documents", "use_tools", "generate_forms"]

# Global variables for session management
current_sessions = {}

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

@app.post("/api/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Form("default"),
    user_id: str = Form(None)
):
    """Enhanced upload and process documents for RAG with multiple document support"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md', '.csv', '.json'}
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Set current tenant context
        set_current_tenant(tenant_id)

        # Create tenant-specific upload directory
        tenant_upload_dir = uploads_dir / tenant_id
        tenant_upload_dir.mkdir(exist_ok=True)

        # Save uploaded file with unique name to prevent conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = tenant_upload_dir / safe_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ensure tenant exists in registry
        from main import _tenant_registry, create_tenant
        if tenant_id not in _tenant_registry:
            create_tenant(tenant_id, f"Tenant {tenant_id}", ["read_documents", "use_tools", "generate_forms"])

        # Process single document with enhanced metadata
        from main import ingest_single_document
        result = ingest_single_document(tenant_id, str(file_path), user_id)

        if not result["success"]:
            # Clean up file if processing failed
            if file_path.exists():
                file_path.unlink()
            raise Exception(result["message"])

        return {
            "success": True,
            "message": result["message"],
            "document_id": result["document_id"],
            "filename": file.filename,
            "file_path": str(file_path),
            "tenant_id": tenant_id,
            "indexed": True,
            "chunks": result.get("chunks", 0),
            "duplicate": result.get("duplicate", False)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/upload-multiple-documents")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    tenant_id: str = Form("default"),
    user_id: str = Form(None)
):
    """Upload and process multiple documents simultaneously"""
    try:
        # Validate all files first
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md', '.csv', '.json'}
        for file in files:
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type '{file.filename}'. Allowed: {', '.join(allowed_extensions)}"
                )

        # Set current tenant context
        set_current_tenant(tenant_id)

        # Create tenant-specific upload directory
        tenant_upload_dir = uploads_dir / tenant_id
        tenant_upload_dir.mkdir(exist_ok=True)

        # Save all files
        file_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for i, file in enumerate(files):
            safe_filename = f"{timestamp}_{i:03d}_{file.filename}"
            file_path = tenant_upload_dir / safe_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_paths.append(str(file_path))

        # Ensure tenant exists in registry
        from main import _tenant_registry, create_tenant
        if tenant_id not in _tenant_registry:
            create_tenant(tenant_id, f"Tenant {tenant_id}", ["read_documents", "use_tools", "generate_forms"])

        # Process multiple documents
        from main import ingest_multiple_documents
        result = ingest_multiple_documents(tenant_id, file_paths, user_id)

        return {
            "success": True,
            "message": f"Processed {result['total_files']} files",
            "total_files": result["total_files"],
            "successful": result["successful"],
            "failed": result["failed"],
            "duplicates": result["duplicates"],
            "results": result["results"],
            "tenant_id": tenant_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple upload failed: {str(e)}")

@app.get("/api/documents/{tenant_id}")
async def get_documents(tenant_id: str):
    """Get all documents for a tenant"""
    try:
        from main import document_storage
        documents = document_storage.get_documents_by_tenant(tenant_id)

        return {
            "success": True,
            "documents": [
                {
                    "document_id": doc.document_id,
                    "filename": doc.filename,
                    "original_name": doc.original_name,
                    "file_size": doc.file_size,
                    "file_type": doc.file_type,
                    "upload_timestamp": doc.upload_timestamp,
                    "chunk_count": doc.chunk_count,
                    "indexed": doc.indexed,
                    "tags": doc.tags
                }
                for doc in documents
            ],
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@app.delete("/api/documents/{tenant_id}/{document_id}")
async def delete_document(tenant_id: str, document_id: str):
    """Delete a specific document"""
    try:
        from main import document_storage
        documents = document_storage.get_documents_by_tenant(tenant_id)

        # Find the document
        doc_to_delete = None
        for doc in documents:
            if doc.document_id == document_id:
                doc_to_delete = doc
                break

        if not doc_to_delete:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete file from filesystem
        if os.path.exists(doc_to_delete.file_path):
            os.remove(doc_to_delete.file_path)

        # Remove from database
        conn = sqlite3.connect(document_storage.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
        conn.commit()
        conn.close()

        # TODO: Remove from vector store (requires rebuilding index)

        return {
            "success": True,
            "message": f"Document '{doc_to_delete.filename}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/api/chat-history/{tenant_id}/{session_id}")
async def get_chat_history(tenant_id: str, session_id: str, limit: int = 50):
    """Get chat history for a session"""
    try:
        from main import document_storage
        messages = document_storage.get_chat_history(session_id, limit)

        return {
            "success": True,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "agent_type": msg.agent_type,
                    "document_references": msg.document_references
                }
                for msg in messages
            ],
            "total": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for all agents"""
    try:
        # Set current tenant context
        set_current_tenant(request.tenant_id)

        # Ensure tenant exists in registry
        from main import _tenant_registry, create_tenant
        if request.tenant_id not in _tenant_registry:
            create_tenant(request.tenant_id, f"Tenant {request.tenant_id}", ["read_documents", "use_tools", "generate_forms"])

        # For doc_qa agent, check if documents are indexed
        if request.agent_type == "doc_qa":
            from main import get_retriever_for_tenant
            retriever = get_retriever_for_tenant(request.tenant_id)
            if retriever is None:
                return {
                    "success": True,
                    "response": f"No documents indexed for tenant '{request.tenant_id}'. Please upload documents first using the upload area above.",
                    "agent": request.agent_type,
                    "timestamp": datetime.now().isoformat()
                }

        # Route to appropriate agent
        if request.agent_type == "doc_qa":
            response = chat_with_agent(request.message, request.tenant_id)
        elif request.agent_type == "form_gen":
            response = await handle_form_generation(request.message, request.tenant_id)
        elif request.agent_type == "api_exec":
            response = chat_with_agent(request.message, request.tenant_id)
        elif request.agent_type == "analytics":
            response = chat_with_agent(request.message, request.tenant_id)
        elif request.agent_type == "escalate":
            response = chat_with_agent(request.message, request.tenant_id)
        else:
            response = chat_with_agent(request.message, request.tenant_id)

        # Handle auto-download response for form generation
        if isinstance(response, dict) and response.get("auto_download"):
            # Store file content temporarily for download
            download_id = secrets.token_hex(16)
            current_sessions[download_id] = {
                "file_content": response["file_content"],
                "filename": response["filename"],
                "content_type": response["content_type"],
                "timestamp": datetime.now()
            }

            return {
                "success": True,
                "response": response["response"],
                "auto_download": True,
                "download_id": download_id,
                "filename": response["filename"],
                "agent": request.agent_type,
                "timestamp": datetime.now().isoformat()
            }

        return {
            "success": True,
            "response": response,
            "agent": request.agent_type,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

async def handle_form_generation(message: str, tenant_id: str) -> Dict[str, Any]:
    """Handle form generation with automatic download"""
    try:
        # Detect file format preference
        file_format = "pdf"
        if any(word in message.lower() for word in ["doc", "docx", "word"]):
            file_format = "docx"

        # Generate form using the main system
        response = chat_with_agent(message, tenant_id)

        # Check if form was generated successfully
        if "Form ID:" in response and ("generated_forms/" in response or "File:" in response):
            # Extract file path from response
            lines = response.split('\n')
            file_path = None
            form_title = "Generated Form"
            form_sections = 0
            form_fields = 0

            for line in lines:
                if "File:" in line:
                    file_path = line.split("File:")[-1].strip()
                elif "generated_forms/" in line and not file_path:
                    file_path = line.strip()
                elif "Title:" in line:
                    form_title = line.split("Title:")[-1].strip()
                elif "Sections:" in line:
                    try:
                        form_sections = int(line.split("Sections:")[-1].strip())
                    except:
                        pass
                elif "Total Fields:" in line:
                    try:
                        form_fields = int(line.split("Total Fields:")[-1].strip())
                    except:
                        pass

            if file_path and os.path.exists(file_path):
                # Read the file content for direct download
                filename = Path(file_path).name

                with open(file_path, 'rb') as f:
                    file_content = f.read()

                # Clean up the generated file (don't save to folder)
                try:
                    os.remove(file_path)
                except:
                    pass  # Ignore cleanup errors

                # Create a clean preview message
                preview_message = f"""
                <div class="form-preview">
                    <div class="form-preview-header">
                        <h3>📝 {form_title}</h3>
                        <div class="form-stats">
                            <span class="stat"><i class="fas fa-layer-group"></i> {form_sections} sections</span>
                            <span class="stat"><i class="fas fa-edit"></i> {form_fields} fields</span>
                            <span class="stat"><i class="fas fa-file-{file_format}"></i> {file_format.upper()}</span>
                        </div>
                    </div>
                    <div class="form-preview-body">
                        <p>Your professional form has been generated successfully and is ready for download.</p>
                    </div>
                </div>
                """

                return {
                    "response": preview_message,
                    "auto_download": True,
                    "file_content": file_content,
                    "file_format": file_format,
                    "filename": filename,
                    "content_type": "application/pdf" if file_format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "success": True
                }

        # If no file was generated, return the response as-is
        return {
            "response": response,
            "success": True
        }

    except Exception as e:
        return {
            "response": f"❌ Form generation error: {str(e)}",
            "success": False
        }

@app.post("/api/generate-form")
async def generate_form_endpoint(request: FormGenerationRequest):
    """Dedicated form generation endpoint"""
    try:
        result = await handle_form_generation(request.description, request.tenant_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Form generation failed: {str(e)}")

@app.get("/api/download/{download_id}")
async def download_generated_file(download_id: str):
    """Download auto-generated files using download ID"""
    if download_id not in current_sessions:
        raise HTTPException(status_code=404, detail="Download not found or expired")

    session_data = current_sessions[download_id]

    # Clean up the session after download
    del current_sessions[download_id]

    # Return the file content as a response
    from fastapi.responses import Response
    return Response(
        content=session_data["file_content"],
        media_type=session_data["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={session_data['filename']}"
        }
    )

@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download generated files from downloads folder (legacy)"""
    file_path = downloads_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/api/system-stats")
async def get_system_statistics():
    """Get system statistics for analytics"""
    try:
        system_stats = get_system_stats()
        tool_stats = get_tool_stats()
        
        return {
            "system": system_stats,
            "tools": tool_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.post("/api/create-tenant")
async def create_tenant_endpoint(request: TenantRequest):
    """Create a new tenant"""
    try:
        tenant_config = create_tenant(
            request.tenant_id,
            request.name,
            request.permissions
        )
        
        return {
            "success": True,
            "tenant_id": tenant_config.tenant_id,
            "name": tenant_config.name,
            "permissions": tenant_config.permissions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tenant creation failed: {str(e)}")

@app.get("/api/tenants")
async def list_tenants():
    """List all available tenants"""
    from main import _tenant_registry
    tenants = []

    for tenant_id, config in _tenant_registry.items():
        tenants.append({
            "tenant_id": tenant_id,
            "name": config.name,
            "permissions": config.permissions
        })

    # Ensure default tenant exists
    if not tenants:
        tenants.append({
            "tenant_id": "default",
            "name": "Default Tenant",
            "permissions": ["read_documents", "use_tools", "generate_forms"]
        })

    return {"tenants": tenants}

@app.get("/api/debug/tenant/{tenant_id}")
async def debug_tenant_status(tenant_id: str):
    """Debug endpoint to check tenant document indexing status"""
    try:
        from main import get_retriever_for_tenant, _tenant_index_path
        import os

        # Check if tenant exists
        from main import _tenant_registry
        tenant_exists = tenant_id in _tenant_registry

        # Check if index directory exists
        index_path = _tenant_index_path(tenant_id)
        index_exists = os.path.exists(index_path)

        # Check if retriever can be created
        retriever = get_retriever_for_tenant(tenant_id)
        retriever_available = retriever is not None

        # List files in upload directory
        upload_path = uploads_dir / tenant_id
        uploaded_files = []
        if upload_path.exists():
            uploaded_files = [f.name for f in upload_path.iterdir() if f.is_file()]

        return {
            "tenant_id": tenant_id,
            "tenant_exists": tenant_exists,
            "index_path": index_path,
            "index_exists": index_exists,
            "retriever_available": retriever_available,
            "uploaded_files": uploaded_files,
            "upload_path": str(upload_path)
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/api/tools/{tenant_id}")
async def get_tenant_tools(tenant_id: str):
    """Get available tools for a tenant"""
    try:
        from main import get_tenant_tools
        tools = get_tenant_tools(tenant_id)

        return {
            "success": True,
            "tools": [
                {
                    "name": getattr(tool, 'name', getattr(tool, '__name__', str(tool))),
                    "description": getattr(tool, 'description', 'No description available'),
                    "args": getattr(tool, 'args', {}) if hasattr(tool, 'args') else {}
                }
                for tool in tools
            ],
            "total": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")

@app.post("/api/escalate")
async def create_escalation(request: ChatRequest):
    """Create an escalation ticket"""
    try:
        # Set current tenant context
        set_current_tenant(request.tenant_id)

        # Use the escalation agent
        response = chat_with_agent(request.message, request.tenant_id)

        return {
            "success": True,
            "response": response,
            "agent": "escalate",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Escalation failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Chatbot Web Interface...")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
