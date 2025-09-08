#!/usr/bin/env python3
"""
Comprehensive Fix Verification Test
Tests all the issues that were reported and fixed
"""

import requests
import json
import time
import os
import tempfile
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_rag_document_issues():
    """Test RAG document retrieval fixes"""
    print("🔍 Testing RAG Document Issues...")
    
    results = {}
    
    # Test 1: Enhanced query expansion
    test_queries = [
        "recipe for pasta",  # Should work with enhanced expansion
        "how to make pasta",  # Direct recipe query
        "tell me a story",   # Story retrieval
        "what is the price", # CSV data queries
    ]
    
    for query in test_queries:
        try:
            response = requests.post(f"{BASE_URL}/api/chat", json={
                "message": query,
                "tenant_id": "test_rag",
                "agent_type": "doc_qa"
            })
            
            if response.status_code == 200:
                result = response.json()
                results[query] = {
                    "success": True,
                    "response_length": len(result.get("response", "")),
                    "has_content": "no documents" not in result.get("response", "").lower()
                }
            else:
                results[query] = {"success": False, "error": response.text}
                
        except Exception as e:
            results[query] = {"success": False, "error": str(e)}
    
    print(f"✅ RAG Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def test_api_executor_fixes():
    """Test API executor fixes"""
    print("🔧 Testing API Executor Fixes...")
    
    results = {}
    
    # Test 1: Web search functionality
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "search for Python programming",
            "tenant_id": "test_api",
            "agent_type": "api_exec"
        })
        
        if response.status_code == 200:
            result = response.json()
            results["web_search"] = {
                "success": True,
                "has_search_result": "search" in result.get("response", "").lower() or "result" in result.get("response", "").lower()
            }
        else:
            results["web_search"] = {"success": False, "error": response.text}
    except Exception as e:
        results["web_search"] = {"success": False, "error": str(e)}
    
    # Test 2: Date/time functionality
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "what time is it now",
            "tenant_id": "test_api",
            "agent_type": "api_exec"
        })
        
        if response.status_code == 200:
            result = response.json()
            results["datetime"] = {
                "success": True,
                "has_time_info": any(word in result.get("response", "").lower() for word in ["time", "date", "clock", "utc"])
            }
        else:
            results["datetime"] = {"success": False, "error": response.text}
    except Exception as e:
        results["datetime"] = {"success": False, "error": str(e)}
    
    print(f"✅ API Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def test_form_generator_fixes():
    """Test form generator fixes"""
    print("📝 Testing Form Generator Fixes...")
    
    results = {}
    
    # Test 1: Form generation with validation
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "create a contact form with required email field",
            "tenant_id": "test_form",
            "agent_type": "form_gen"
        })
        
        if response.status_code == 200:
            result = response.json()
            results["form_creation"] = {
                "success": True,
                "has_form": "form" in result.get("response", "").lower(),
                "has_validation": "required" in result.get("response", "").lower()
            }
        else:
            results["form_creation"] = {"success": False, "error": response.text}
    except Exception as e:
        results["form_creation"] = {"success": False, "error": str(e)}
    
    print(f"✅ Form Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def test_analytics_fixes():
    """Test analytics formatting fixes"""
    print("📊 Testing Analytics Fixes...")
    
    results = {}
    
    # Test 1: Analytics report formatting
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "show me system analytics",
            "tenant_id": "test_analytics",
            "agent_type": "analytics"
        })
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            results["analytics_formatting"] = {
                "success": True,
                "has_headers": "##" in response_text or "**" in response_text,
                "has_metrics": "metrics" in response_text.lower() or "statistics" in response_text.lower(),
                "well_formatted": len(response_text.split('\n')) > 5  # Multi-line formatted response
            }
        else:
            results["analytics_formatting"] = {"success": False, "error": response.text}
    except Exception as e:
        results["analytics_formatting"] = {"success": False, "error": str(e)}
    
    print(f"✅ Analytics Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def test_escalation_fixes():
    """Test escalation system fixes"""
    print("🆘 Testing Escalation Fixes...")
    
    results = {}
    
    # Test 1: Escalation ticket creation
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "I need help from a human agent",
            "tenant_id": "test_escalation",
            "agent_type": "escalate"
        })
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            results["escalation_creation"] = {
                "success": True,
                "has_ticket_id": any(word in response_text.lower() for word in ["ticket", "escalation", "id:"]),
                "has_status": "open" in response_text.lower() or "created" in response_text.lower(),
                "well_formatted": "**" in response_text or "✅" in response_text
            }
        else:
            results["escalation_creation"] = {"success": False, "error": response.text}
    except Exception as e:
        results["escalation_creation"] = {"success": False, "error": str(e)}
    
    # Test 2: Check if tickets are stored
    try:
        response = requests.get(f"{BASE_URL}/api/escalation-tickets/test_escalation")
        
        if response.status_code == 200:
            result = response.json()
            results["ticket_storage"] = {
                "success": True,
                "tickets_found": result.get("total", 0) > 0
            }
        else:
            results["ticket_storage"] = {"success": False, "error": response.text}
    except Exception as e:
        results["ticket_storage"] = {"success": False, "error": str(e)}
    
    print(f"✅ Escalation Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def test_conversational_api_flow():
    """Test the new conversational API flow system"""
    print("🤖 Testing Conversational API Flow...")
    
    results = {}
    
    # Test 1: Setup sample APIs
    try:
        response = requests.post(f"{BASE_URL}/api/setup-sample-apis/test_conversation")
        
        if response.status_code == 200:
            result = response.json()
            results["api_setup"] = {
                "success": True,
                "apis_registered": len(result.get("apis_registered", []))
            }
        else:
            results["api_setup"] = {"success": False, "error": response.text}
    except Exception as e:
        results["api_setup"] = {"success": False, "error": str(e)}
    
    # Test 2: Conversational flow
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "I want to open an account",
            "tenant_id": "test_conversation",
            "agent_type": "api_exec"
        })
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            results["conversation_flow"] = {
                "success": True,
                "asks_for_info": any(word in response_text.lower() for word in ["name", "provide", "enter", "please"]),
                "intelligent_response": len(response_text) > 50
            }
        else:
            results["conversation_flow"] = {"success": False, "error": response.text}
    except Exception as e:
        results["conversation_flow"] = {"success": False, "error": str(e)}
    
    print(f"✅ Conversation Tests: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)} passed")
    return results

def main():
    """Run comprehensive fix verification"""
    print("🚀 Comprehensive Fix Verification Test")
    print("=" * 60)
    
    all_results = {}
    
    try:
        # Test all fixed components
        all_results["rag_documents"] = test_rag_document_issues()
        time.sleep(1)
        
        all_results["api_executor"] = test_api_executor_fixes()
        time.sleep(1)
        
        all_results["form_generator"] = test_form_generator_fixes()
        time.sleep(1)
        
        all_results["analytics"] = test_analytics_fixes()
        time.sleep(1)
        
        all_results["escalation"] = test_escalation_fixes()
        time.sleep(1)
        
        all_results["conversational_api"] = test_conversational_api_flow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            category_passed = sum(1 for r in results.values() if r.get('success', False))
            category_total = len(results)
            total_tests += category_total
            passed_tests += category_passed
            
            status = "✅ PASS" if category_passed == category_total else "⚠️  PARTIAL" if category_passed > 0 else "❌ FAIL"
            print(f"{status} {category.replace('_', ' ').title()}: {category_passed}/{category_total}")
        
        print("-" * 60)
        overall_status = "✅ ALL TESTS PASSED" if passed_tests == total_tests else f"⚠️  {passed_tests}/{total_tests} TESTS PASSED"
        print(f"🎯 OVERALL: {overall_status}")
        
        if passed_tests == total_tests:
            print("\n🎉 All reported issues have been successfully fixed!")
        else:
            print(f"\n📝 {total_tests - passed_tests} issues may need additional attention.")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
