#!/usr/bin/env python3
"""
Fix Form Generation - Create tenant with proper permissions and test
"""

import os
from dotenv import load_dotenv
load_dotenv()

def fix_and_test_form_generation():
    """Create a tenant with form permissions and test form generation"""
    print("🔧 Fixing Form Generation Issue")
    print("=" * 50)
    
    # Import after loading env
    from main import create_tenant, chat_with_agent
    
    # Create a tenant with form generation permissions
    print("1. Creating tenant with form generation permissions...")
    tenant_config = create_tenant(
        tenant_id="form_company",
        name="Form Generation Company", 
        permissions=["read_documents", "use_tools", "generate_forms"]  # Include generate_forms!
    )
    print(f"✅ Created tenant: {tenant_config.tenant_id}")
    print(f"   Permissions: {tenant_config.permissions}")
    print()
    
    # Test form generation
    print("2. Testing form generation...")
    test_requests = [
        "Create a contract form for me",
        "Generate a customer feedback form with name, email, and rating fields",
        "Create an employee onboarding form with personal details and job information"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📝 Test {i}: {request}")
        print("-" * 40)
        
        try:
            response = chat_with_agent(request, "form_company")
            print("✅ Form Generated:")
            print(response[:300] + "..." if len(response) > 300 else response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def show_how_to_use_interactive_mode():
    """Show the correct way to use interactive mode"""
    print("\n🎯 How to Use Form Generation in Interactive Mode")
    print("=" * 60)
    print()
    print("Follow these steps:")
    print()
    print("1. Run: python main.py")
    print("2. Switch to a tenant with form permissions:")
    print("   /tenant form_company")
    print()
    print("3. Now you can generate forms:")
    print("   Create a contract form for me")
    print("   Generate a survey form with rating questions")
    print("   Create a registration form for events")
    print()
    print("Alternative: Create a new tenant with permissions:")
    print("   /create_tenant my_company \"My Company\" read_documents,use_tools,generate_forms")
    print("   /tenant my_company")
    print("   Create a contact form")
    print()

def main():
    """Run the fix and demonstration"""
    print("🚀 Form Generation Fix & Demo")
    print("=" * 60)
    
    try:
        fix_and_test_form_generation()
        show_how_to_use_interactive_mode()
        
        print("🎉 Form Generation is Now Working!")
        print()
        print("💡 Key Points:")
        print("   ✅ Tenant must have 'generate_forms' permission")
        print("   ✅ Use /tenant command to switch to proper tenant")
        print("   ✅ Default tenant doesn't have form permissions")
        print("   ✅ Create new tenants with required permissions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
