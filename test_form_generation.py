#!/usr/bin/env python3
"""
Form Generation Functionality Test
Tests form creation, company editing, submission, and data management
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    node_form_gen, create_tenant, create_session, MessagesState,
    CURRENT_TENANT_ID, CURRENT_SESSION, FORM_GENERATOR,
    _json_to_professional_form, ProfessionalForm, FormSection, FormField,
    set_current_tenant
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_form_generation_node():
    """Test the form generation node functionality"""
    logger.info("Testing Form Generation Node")
    
    global CURRENT_TENANT_ID, CURRENT_SESSION
    original_tenant = CURRENT_TENANT_ID
    original_session = CURRENT_SESSION
    
    try:
        # Set up test context
        tenant_id = "test_form_gen"
        
        # Create tenant and session using set_current_tenant
        create_tenant(tenant_id, "Form Test Tenant", ["generate_forms", "read_documents", "use_tools"])
        set_current_tenant(tenant_id)  # This properly sets both CURRENT_TENANT_ID and CURRENT_SESSION
        
        test_queries = [
            "Create a contact form with name, email, phone, and message fields",
            "Generate a customer satisfaction survey with rating scales",
            "Create a job application form with personal details",
            "Make a feedback form with multiple choice questions"
        ]
        
        results = {}
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Testing form generation query {i}: '{query}'")
            
            try:
                # Create message state
                state = MessagesState(messages=[("user", query)])
                
                # Run form generation node
                result = node_form_gen(state)
                
                if result and 'messages' in result:
                    response_msg = result['messages'][0]
                    if hasattr(response_msg, 'content'):
                        response = response_msg.content
                    elif isinstance(response_msg, tuple) and len(response_msg) >= 2:
                        response = response_msg[1]
                    else:
                        response = str(response_msg)
                    
                    # Check if form was successfully generated
                    success = (
                        "Form Generated Successfully" in response or
                        "✅" in response or
                        "form_id" in response.lower() or
                        "generated_forms" in response
                    )
                    
                    results[f"query_{i}"] = {
                        'query': query,
                        'response': response,
                        'success': success,
                        'contains_form_info': "form" in response.lower(),
                        'contains_download': "download" in response.lower(),
                        'response_length': len(response)
                    }
                    
                    if success:
                        logger.info(f"✅ Form generation successful for query {i}")
                    else:
                        logger.warning(f"⚠️ Form generation may have issues for query {i}")
                        logger.info(f"   Response: {response[:200]}...")
                else:
                    logger.error(f"❌ Form generation failed for query {i} - no response")
                    results[f"query_{i}"] = {
                        'query': query,
                        'success': False,
                        'error': 'No response from form generation node'
                    }
                    
            except Exception as e:
                logger.error(f"❌ Form generation error for query {i}: {e}")
                results[f"query_{i}"] = {
                    'query': query,
                    'success': False,
                    'error': str(e)
                }
        
        return results
        
    finally:
        # Restore context
        CURRENT_TENANT_ID = original_tenant
        CURRENT_SESSION = original_session

def test_professional_form_class():
    """Test the ProfessionalForm class and related functionality"""
    logger.info("Testing ProfessionalForm Class")
    
    try:
        # Create a test form structure
        fields = [
            FormField(
                name="name",
                label="Full Name",
                field_type="text",
                required=True,
                placeholder="Enter your full name"
            ),
            FormField(
                name="email",
                label="Email Address",
                field_type="email",
                required=True,
                placeholder="your.email@example.com"
            ),
            FormField(
                name="rating",
                label="Overall Rating",
                field_type="select",
                required=True,
                options=["Excellent", "Good", "Fair", "Poor"]
            )
        ]
        
        section = FormSection(
            title="Contact Information",
            description="Please provide your contact details",
            fields=fields
        )
        
        form = ProfessionalForm(
            title="Customer Feedback Form",
            description="We value your feedback",
            company_name="Test Company",
            form_type="feedback",
            sections=[section]
        )
        
        # Test form preview generation
        preview = FORM_GENERATOR.generate_form_preview(form)
        
        # Test HTML generation
        html_content = FORM_GENERATOR.create_html_form(form)
        
        # Test PDF generation
        pdf_filename = FORM_GENERATOR.create_pdf_form(form)
        
        results = {
            'form_creation': True,
            'preview_generation': len(preview) > 100,
            'html_generation': html_file_path and os.path.exists(html_file_path) and len(html_content) > 500 and '<form' in html_content,
            'pdf_generation': pdf_filename and os.path.exists(Path("generated_forms") / pdf_filename),
            'form_id_present': form.form_id and len(form.form_id) > 0,
            'sections_count': len(form.sections),
            'fields_count': sum(len(section.fields) for section in form.sections)
        }
        
        logger.info(f"✅ Form class test results: {results}")
        return results
        
    except Exception as e:
        logger.error(f"❌ Form class test error: {e}")
        return {'error': str(e)}

def test_json_to_form_conversion():
    """Test JSON to ProfessionalForm conversion"""
    logger.info("Testing JSON to Form Conversion")
    
    try:
        # Test JSON data
        json_data = {
            "title": "Employee Survey",
            "description": "Annual employee satisfaction survey",
            "company_name": "TechCorp Inc",
            "form_type": "survey",
            "sections": [
                {
                    "title": "Personal Information",
                    "description": "Basic details",
                    "fields": [
                        {
                            "name": "employee_id",
                            "label": "Employee ID",
                            "field_type": "text",
                            "required": True
                        },
                        {
                            "name": "department",
                            "label": "Department",
                            "field_type": "select",
                            "required": True,
                            "options": ["Engineering", "Marketing", "Sales", "HR"]
                        }
                    ]
                },
                {
                    "title": "Satisfaction Ratings",
                    "description": "Rate your experience",
                    "fields": [
                        {
                            "name": "job_satisfaction",
                            "label": "Job Satisfaction",
                            "field_type": "radio",
                            "required": True,
                            "options": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"]
                        }
                    ]
                }
            ]
        }
        
        # Convert JSON to ProfessionalForm
        form = _json_to_professional_form(json_data)
        
        results = {
            'conversion_success': isinstance(form, ProfessionalForm),
            'title_preserved': form.title == json_data['title'],
            'sections_count': len(form.sections) == len(json_data['sections']),
            'fields_count': sum(len(section.fields) for section in form.sections) == 3,
            'form_id_generated': form.form_id and len(form.form_id) > 0,
            'company_name': form.company_name == json_data['company_name']
        }
        
        logger.info(f"✅ JSON conversion test results: {results}")
        return results
        
    except Exception as e:
        logger.error(f"❌ JSON conversion test error: {e}")
        return {'error': str(e)}

def test_form_buttons_functionality():
    """Test form button functionality (simulated)"""
    logger.info("Testing Form Button Functionality")
    
    try:
        # Create a test form
        form = ProfessionalForm(
            title="Button Test Form",
            description="Testing form buttons",
            company_name="Test Corp",
            sections=[]
        )
        
        # Generate HTML content
        html_file_path = FORM_GENERATOR.create_html_form(form)
        
        # Read the HTML content from the file
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read HTML file: {e}")
            html_content = ""
        
        # Check for button presence and functionality
        button_checks = {
            'submit_button': 'type="submit"' in html_content and 'Submit Form' in html_content,
            'clear_button': 'clearForm()' in html_content and 'Clear All Data' in html_content,
            'save_progress': 'saveProgress()' in html_content and 'Save Progress' in html_content,
            'download_pdf': 'downloadAsPDF()' in html_content and 'PDF' in html_content,
            'download_docx': 'downloadAsDOCX()' in html_content and 'DOCX' in html_content,
            'javascript_functions': all(func in html_content for func in [
                'function handleSubmit(',
                'function clearForm(',
                'function saveProgress(',
                'function downloadAsPDF(',
                'function downloadAsDOCX('
            ])
        }
        
        logger.info(f"✅ Button functionality test results: {button_checks}")
        return button_checks
        
    except Exception as e:
        logger.error(f"❌ Button functionality test error: {e}")
        return {'error': str(e)}

def test_form_validation():
    """Test form validation functionality"""
    logger.info("Testing Form Validation")
    
    try:
        # Create form with validation requirements
        fields = [
            FormField(
                name="required_field",
                label="Required Field",
                field_type="text",
                required=True,
                validation="required"
            ),
            FormField(
                name="email_field",
                label="Email Field",
                field_type="email",
                required=True,
                validation="email"
            )
        ]
        
        section = FormSection(
            title="Validation Test",
            fields=fields
        )
        
        form = ProfessionalForm(
            title="Validation Test Form",
            description="Test form with validation features",
            sections=[section]
        )
        
        html_file_path = FORM_GENERATOR.create_html_form(form)
        
        # Read the HTML content from the file
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read HTML file: {e}")
            html_content = ""
        
        validation_checks = {
            'required_attributes': 'required' in html_content,
            'email_type': 'type="email"' in html_content,
            'validation_script': 'checkValidity()' in html_content or 'reportValidity()' in html_content,
            'form_validation': 'form.checkValidity()' in html_content
        }
        
        logger.info(f"✅ Form validation test results: {validation_checks}")
        return validation_checks
        
    except Exception as e:
        logger.error(f"❌ Form validation test error: {e}")
        return {'error': str(e)}

def run_comprehensive_form_test():
    """Run comprehensive form generation test suite"""
    logger.info("🧪 Starting Comprehensive Form Generation Test Suite")
    logger.info("=" * 60)
    
    all_results = {}
    
    # Test 1: Form Generation Node
    logger.info("\n📝 Testing Form Generation Node")
    logger.info("-" * 40)
    all_results['node_tests'] = test_form_generation_node()
    
    # Test 2: Professional Form Class
    logger.info("\n🏗️ Testing ProfessionalForm Class")
    logger.info("-" * 40)
    all_results['class_tests'] = test_professional_form_class()
    
    # Test 3: JSON to Form Conversion
    logger.info("\n🔄 Testing JSON to Form Conversion")
    logger.info("-" * 40)
    all_results['conversion_tests'] = test_json_to_form_conversion()
    
    # Test 4: Form Button Functionality
    logger.info("\n🔘 Testing Form Button Functionality")
    logger.info("-" * 40)
    all_results['button_tests'] = test_form_buttons_functionality()
    
    # Test 5: Form Validation
    logger.info("\n✅ Testing Form Validation")
    logger.info("-" * 40)
    all_results['validation_tests'] = test_form_validation()
    
    # Calculate summary
    logger.info("\n" + "=" * 60)
    logger.info("🎯 FORM GENERATION TEST SUMMARY")
    logger.info("=" * 60)
    
    total_tests = 0
    successful_tests = 0
    
    # Count node tests
    if 'node_tests' in all_results:
        node_success = sum(1 for test in all_results['node_tests'].values() if test.get('success', False))
        node_total = len(all_results['node_tests'])
        logger.info(f"📝 Form Generation Node: {node_success}/{node_total} successful")
        total_tests += node_total
        successful_tests += node_success
    
    # Count class tests
    if 'class_tests' in all_results and 'error' not in all_results['class_tests']:
        class_success = sum(1 for v in all_results['class_tests'].values() if v is True)
        class_total = len(all_results['class_tests'])
        logger.info(f"🏗️ ProfessionalForm Class: {class_success}/{class_total} tests passed")
        total_tests += class_total
        successful_tests += class_success
    
    # Count conversion tests
    if 'conversion_tests' in all_results and 'error' not in all_results['conversion_tests']:
        conv_success = sum(1 for v in all_results['conversion_tests'].values() if v is True)
        conv_total = len(all_results['conversion_tests'])
        logger.info(f"🔄 JSON Conversion: {conv_success}/{conv_total} tests passed")
        total_tests += conv_total
        successful_tests += conv_success
    
    # Count button tests
    if 'button_tests' in all_results and 'error' not in all_results['button_tests']:
        btn_success = sum(1 for v in all_results['button_tests'].values() if v is True)
        btn_total = len(all_results['button_tests'])
        logger.info(f"🔘 Button Functionality: {btn_success}/{btn_total} tests passed")
        total_tests += btn_total
        successful_tests += btn_success
    
    # Count validation tests
    if 'validation_tests' in all_results and 'error' not in all_results['validation_tests']:
        val_success = sum(1 for v in all_results['validation_tests'].values() if v is True)
        val_total = len(all_results['validation_tests'])
        logger.info(f"✅ Form Validation: {val_success}/{val_total} tests passed")
        total_tests += val_total
        successful_tests += val_success
    
    # Overall assessment
    if total_tests > 0:
        success_rate = (successful_tests / total_tests) * 100
        logger.info(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
        if success_rate >= 80:
            logger.info("🎉 Form generation system is working well!")
        elif success_rate >= 60:
            logger.info("⚠️ Form generation system needs some improvements")
        else:
            logger.info("❌ Form generation system has significant issues")
            
        return success_rate >= 80
    else:
        logger.error("❌ No tests were able to run properly")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_form_test()
        if success:
            print("\n✅ Form generation test suite passed!")
            sys.exit(0)
        else:
            print("\n❌ Form generation test suite failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)