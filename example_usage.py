#!/usr/bin/env python3
"""
Example usage and testing script for the Multi-Agent Chatbot System
This script demonstrates all the key features implemented in Milestone 1
"""

import os
import sys
from pathlib import Path

# Add the main directory to path
sys.path.append(str(Path(__file__).parent))

from main import (
    create_tenant, authenticate_tenant, create_session,
    register_dynamic_tool, make_http_get_tool, make_http_post_tool,
    ingest_documents_from_dir, get_system_stats, create_admin_dashboard,
    chat_with_agent, CURRENT_TENANT_ID, CURRENT_SESSION
)

def demo_tenant_management():
    """Demonstrate tenant creation and management."""
    print("=== Tenant Management Demo ===")
    
    # Create demo tenants
    tenants = [
        ("demo_company", "Demo Company Inc"),
        ("healthcare_org", "Healthcare Organization"),
        ("tech_startup", "Tech Startup LLC")
    ]
    
    for tenant_id, name in tenants:
        try:
            config = create_tenant(tenant_id, name)
            print(f"✅ Created tenant: {tenant_id} ({name})")
            print(f"   Permissions: {', '.join(config.permissions)}")
        except ValueError as e:
            print(f"⚠️  Tenant {tenant_id} already exists")
    
    print()

def demo_tool_registration():
    """Demonstrate dynamic tool registration."""
    print("=== Dynamic Tool Registration Demo ===")
    
    # Set environment variables for demo (in production, these would be real APIs)
    os.environ["DEMO_API_BASE"] = "https://api.example.com"
    os.environ["DEMO_API_KEY"] = "demo_key_123"
    
    # Register tools for different tenants
    demo_tools = [
        ("demo_company", "company_api", "Company internal API"),
        ("healthcare_org", "patient_api", "Patient management API"),
        ("tech_startup", "github_api", "GitHub integration API")
    ]
    
    for tenant_id, tool_name, description in demo_tools:
        try:
            tool = make_http_get_tool(
                name=tool_name,
                description=description,
                base_url_env="DEMO_API_BASE",
                api_key_env="DEMO_API_KEY"
            )
            register_dynamic_tool(tenant_id, tool)
            print(f"✅ Registered tool '{tool_name}' for tenant '{tenant_id}'")
        except Exception as e:
            print(f"❌ Error registering tool: {e}")
    
    print()

def demo_document_ingestion():
    """Demonstrate document ingestion (simulated)."""
    print("=== Document Ingestion Demo ===")
    
    # Create sample documents directory
    docs_dir = Path("sample_documents")
    docs_dir.mkdir(exist_ok=True)
    
    # Create sample documents
    sample_docs = {
        "company_policy.txt": "Company Policy: Remote work is allowed 3 days per week.",
        "product_guide.md": "# Product Guide\n\nOur product helps businesses automate workflows.",
        "faq.txt": "Q: How do I reset my password?\nA: Click the forgot password link on login page."
    }
    
    for filename, content in sample_docs.items():
        doc_path = docs_dir / filename
        if not doc_path.exists():
            doc_path.write_text(content)
            print(f"📄 Created sample document: {filename}")
    
    # Ingest documents for demo tenant
    try:
        result = ingest_documents_from_dir("demo_company", str(docs_dir))
        print(f"✅ Document ingestion result: {result}")
    except Exception as e:
        print(f"❌ Document ingestion error: {e}")
    
    print()

def demo_agent_interactions():
    """Demonstrate agent interactions."""
    print("=== Agent Interaction Demo ===")
    
    # Set up session for demo
    global CURRENT_TENANT_ID, CURRENT_SESSION
    CURRENT_TENANT_ID = "demo_company"
    try:
        CURRENT_SESSION = create_session("demo_company")
        print(f"✅ Created session: {CURRENT_SESSION.session_id[:8]}...")
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return
    
    # Test different agent interactions
    test_queries = [
        ("Greeting", "Hello, how can you help me today?"),
        ("Document Q&A", "What is our company policy on remote work?"),
        ("API Execution", "What's the weather like today?"),
        ("Form Generation", "Create a customer feedback form with name, email, and rating fields"),
        ("Escalation", "I need to speak with a human agent about a critical issue")
    ]
    
    for agent_type, query in test_queries:
        print(f"\n🤖 Testing {agent_type} Agent:")
        print(f"User: {query}")
        
        try:
            # Use the simplified chat function
            response = chat_with_agent(query, "demo_company")
            print(f"Bot: {response[:200]}{'...' if len(response) > 200 else ''}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

def demo_admin_dashboard():
    """Demonstrate admin dashboard generation."""
    print("=== Admin Dashboard Demo ===")
    
    try:
        # Generate system statistics
        stats = get_system_stats()
        print("📊 System Statistics:")
        print(f"   Tenants: {stats['tenants']['total']} total, {stats['tenants']['active']} active")
        print(f"   Sessions: {stats['sessions']['active']} active")
        print(f"   Tools: {len(stats['tools'])} registered")
        
        # Generate admin dashboard
        dashboard_html = create_admin_dashboard()
        dashboard_file = "demo_admin_dashboard.html"
        
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(dashboard_html)
        
        print(f"✅ Admin dashboard saved to: {dashboard_file}")
        print(f"   Open in browser to view comprehensive system overview")
        
    except Exception as e:
        print(f"❌ Dashboard generation error: {e}")
    
    print()

def demo_error_handling():
    """Demonstrate error handling and recovery."""
    print("=== Error Handling Demo ===")
    
    # Test various error scenarios
    error_tests = [
        ("Invalid tenant authentication", lambda: authenticate_tenant("nonexistent_tenant")),
        ("Permission denied scenario", lambda: create_tenant("test", "Test") if not authenticate_tenant("invalid") else None),
        ("Invalid document path", lambda: ingest_documents_from_dir("demo_company", "/nonexistent/path")),
    ]
    
    for test_name, test_func in error_tests:
        print(f"🧪 Testing: {test_name}")
        try:
            result = test_func()
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   ✅ Properly handled error: {type(e).__name__}: {e}")
    
    print()

def main():
    """Run all demonstration scenarios."""
    print("🚀 Multi-Agent Chatbot System - Milestone 1 Demo")
    print("=" * 60)
    
    # Check environment setup
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Some features may not work.")
        print("   Set your Google API key in the .env file")
        print()
    
    # Run all demos
    demo_tenant_management()
    demo_tool_registration()
    demo_document_ingestion()
    demo_agent_interactions()
    demo_admin_dashboard()
    demo_error_handling()
    
    print("🎉 Demo completed! All Milestone 1 features demonstrated.")
    print("\nNext steps:")
    print("1. Run 'python main.py' for interactive mode")
    print("2. Open demo_admin_dashboard.html in browser")
    print("3. Try the CLI commands listed in README.md")
    print("4. Integrate with your own APIs and documents")

if __name__ == "__main__":
    main()