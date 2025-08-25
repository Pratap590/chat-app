#!/usr/bin/env python3
"""
Simple Form Generation Example
"""

import json
from main import node_form_gen, create_tenant, create_session, CURRENT_TENANT_ID, CURRENT_SESSION

def demonstrate_form_generation():
    """Show form generation capabilities"""
    print("🎨 Form Generation Example")
    print("=" * 40)
    
    # Create tenant with form permissions
    tenant_config = create_tenant("demo_forms", "Demo Forms Company", 
                                permissions=["generate_forms", "read_documents", "use_tools"])
    print(f"✅ Created tenant: {tenant_config.tenant_id}")
    
    # Create session
    session = create_session("demo_forms")
    print(f"✅ Created session: {session.session_id[:8]}...")
    
    # Set global context (this is what chat_with_agent does)
    global CURRENT_TENANT_ID, CURRENT_SESSION
    CURRENT_TENANT_ID = "demo_forms"
    CURRENT_SESSION = session
    
    # Test form generation requests
    form_requests = [
        {
            "name": "Contact Form",
            "request": "Create a contact form with name, email, phone, and message fields"
        },
        {
            "name": "Survey Form", 
            "request": "Generate a customer satisfaction survey with rating scales and comment boxes"
        },
        {
            "name": "Registration Form",
            "request": "Create an event registration form with personal details and preferences"
        }
    ]
    
    for i, form_req in enumerate(form_requests, 1):
        print(f"\n📝 Example {i}: {form_req['name']}")
        print(f"Request: {form_req['request']}")
        print("-" * 40)
        
        # Create a mock state for the form generation
        mock_state = {
            "messages": [
                {"type": "human", "content": form_req['request']}
            ]
        }
        
        try:
            # Call the form generation node directly
            result = node_form_gen(mock_state)
            response = result["messages"][0]
            
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, tuple):
                content = response[1]
            else:
                content = str(response)
            
            print("Generated Form:")
            print(content)
            
            # Try to extract and format JSON if present
            if '{' in content and '}' in content:
                try:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_str = content[start:end]
                    form_data = json.loads(json_str)
                    
                    print("\n📋 Structured Form Data:")
                    print(f"   Title: {form_data.get('title', 'N/A')}")
                    print(f"   Description: {form_data.get('description', 'N/A')}")
                    print(f"   Fields ({len(form_data.get('fields', []))}):")
                    
                    for field in form_data.get('fields', []):
                        field_type = field.get('type', 'text')
                        field_name = field.get('name', 'unnamed')
                        field_label = field.get('label', field_name)
                        required = " (required)" if field.get('required', False) else ""
                        print(f"     - {field_label}: {field_type}{required}")
                        
                except json.JSONDecodeError:
                    print("\n📋 Form generated as descriptive text")
                    
        except Exception as e:
            print(f"❌ Error generating form: {e}")
        
        print("=" * 40)

def show_form_json_structure():
    """Show the expected JSON structure for forms"""
    print("\n🏗️  Expected Form JSON Structure")
    print("=" * 40)
    
    example_form = {
        "title": "Customer Feedback Form",
        "description": "Please provide your feedback about our service",
        "fields": [
            {
                "name": "customer_name",
                "label": "Full Name",
                "type": "text",
                "required": True,
                "placeholder": "Enter your full name"
            },
            {
                "name": "email",
                "label": "Email Address", 
                "type": "email",
                "required": True,
                "validation": "email"
            },
            {
                "name": "rating",
                "label": "Overall Rating",
                "type": "select",
                "required": True,
                "options": ["1 - Poor", "2 - Fair", "3 - Good", "4 - Very Good", "5 - Excellent"]
            },
            {
                "name": "comments",
                "label": "Additional Comments",
                "type": "textarea",
                "required": False,
                "placeholder": "Please share any additional feedback"
            }
        ],
        "submit_button": "Submit Feedback",
        "validation_rules": {
            "email": "Must be a valid email address",
            "rating": "Please select a rating"
        }
    }
    
    print("Example Form JSON:")
    print(json.dumps(example_form, indent=2))

def main():
    """Run the form generation demonstration"""
    print("🚀 Form Generation Demonstration")
    print("=" * 60)
    
    try:
        demonstrate_form_generation()
        show_form_json_structure()
        
        print("\n🎉 Form Generation Examples Complete!")
        print("\n💡 Key Features:")
        print("   ✅ Dynamic field generation based on requirements")
        print("   ✅ JSON structured output for easy integration")
        print("   ✅ Validation rules and field types")
        print("   ✅ Permission-based access control")
        print("   ✅ Multiple form types (contact, survey, registration)")
        
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
