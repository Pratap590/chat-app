#!/usr/bin/env python3
"""
Debug form generation permissions
"""

import os
from dotenv import load_dotenv
load_dotenv()

def debug_permissions():
    """Debug the permission system"""
    print("🔍 Debugging Form Generation Permissions")
    print("=" * 50)
    
    from main import (
        create_tenant, get_tenant_config, create_session, 
        has_permission, CURRENT_SESSION, CURRENT_TENANT_ID
    )
    
    # 1. Create tenant with explicit permissions
    print("1. Creating tenant with form permissions...")
    try:
        tenant_config = create_tenant(
            "debug_forms", 
            "Debug Forms", 
            permissions=["read_documents", "use_tools", "generate_forms"]
        )
        print(f"✅ Created: {tenant_config.tenant_id}")
        print(f"   Permissions: {tenant_config.permissions}")
    except Exception as e:
        print(f"❌ Error creating tenant: {e}")
        return
    
    # 2. Verify tenant exists and has permissions
    print("\n2. Verifying tenant configuration...")
    config = get_tenant_config("debug_forms")
    if config:
        print(f"✅ Tenant found: {config.tenant_id}")
        print(f"   Name: {config.name}")
        print(f"   Permissions: {config.permissions}")
        print(f"   Has generate_forms: {'generate_forms' in config.permissions}")
    else:
        print("❌ Tenant not found!")
        return
    
    # 3. Create session
    print("\n3. Creating session...")
    try:
        session = create_session("debug_forms")
        print(f"✅ Session created: {session.session_id[:8]}...")
        print(f"   Tenant ID: {session.tenant_id}")
        print(f"   Permissions: {session.permissions}")
        print(f"   Has generate_forms: {'generate_forms' in session.permissions}")
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return
    
    # 4. Test permission check with session
    print("\n4. Testing permission check with session...")
    has_perm = has_permission("generate_forms", session)
    print(f"   has_permission('generate_forms', session): {has_perm}")
    
    # 5. Test permission check with global session
    print("\n5. Testing with global session context...")
    global CURRENT_SESSION, CURRENT_TENANT_ID
    original_session = CURRENT_SESSION
    original_tenant = CURRENT_TENANT_ID
    
    try:
        CURRENT_SESSION = session
        CURRENT_TENANT_ID = "debug_forms"
        
        has_perm_global = has_permission("generate_forms")
        print(f"   has_permission('generate_forms') with global context: {has_perm_global}")
        
        # 6. Test form generation directly
        print("\n6. Testing form generation node...")
        from main import node_form_gen
        
        mock_state = {
            "messages": [
                type('MockMessage', (), {
                    'type': 'human',
                    'content': 'Create a simple contact form'
                })()
            ]
        }
        
        result = node_form_gen(mock_state)
        response = result["messages"][0]
        
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, tuple):
            content = response[1]
        else:
            content = str(response)
        
        print(f"   Form generation result: {content[:100]}...")
        
        if "Permission denied" in content:
            print("❌ Still getting permission denied!")
        else:
            print("✅ Form generation working!")
            
    finally:
        CURRENT_SESSION = original_session
        CURRENT_TENANT_ID = original_tenant

def test_chat_with_agent():
    """Test the chat_with_agent function specifically"""
    print("\n" + "=" * 50)
    print("🧪 Testing chat_with_agent function")
    print("=" * 50)
    
    from main import chat_with_agent
    
    try:
        result = chat_with_agent("Create a simple form", "debug_forms")
        print(f"Result: {result[:200]}...")
        
        if "Permission denied" in result:
            print("❌ chat_with_agent still has permission issues")
        else:
            print("✅ chat_with_agent working!")
            
    except Exception as e:
        print(f"❌ Error in chat_with_agent: {e}")

def main():
    """Run all debugging tests"""
    try:
        debug_permissions()
        test_chat_with_agent()
        
        print("\n" + "=" * 50)
        print("🎯 Summary:")
        print("If you see 'Permission denied', the issue is in the session context.")
        print("If you see form JSON, the system is working correctly!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
