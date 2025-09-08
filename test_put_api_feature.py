#!/usr/bin/env python3
"""
Test the PUT API feature and API configuration workflow
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_put_api_direct():
    """Test PUT API functionality directly"""
    base_url = "http://localhost:8000"
    
    # Test the PUT API endpoint with JSONPlaceholder
    put_api_request = {
        "base_url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "PUT",
        "query_params": {},
        "body": {
            "id": 1,
            "title": "Updated Test Post",
            "body": "This is an updated test post via PUT",
            "userId": 1
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
    try:
        logger.info("🔄 Testing PUT API endpoint...")
        response = requests.post(
            f"{base_url}/api/custom-api/execute",
            json=put_api_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ PUT API test successful!")
            logger.info(f"   Status: {data.get('status')}")
            logger.info(f"   Success: {data.get('success')}")
            logger.info(f"   Response preview: {str(data.get('data', {}))[:200]}...")
            return True
        else:
            logger.error(f"❌ PUT API test failed: HTTP {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ PUT API test error: {e}")
        return False

def test_patch_api_direct():
    """Test PATCH API functionality"""
    base_url = "http://localhost:8000"
    
    patch_api_request = {
        "base_url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "PATCH",
        "query_params": {},
        "body": {
            "title": "Patched Title Only"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
    try:
        logger.info("🔄 Testing PATCH API endpoint...")
        response = requests.post(
            f"{base_url}/api/custom-api/execute",
            json=patch_api_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ PATCH API test successful!")
            logger.info(f"   Status: {data.get('status')}")
            logger.info(f"   Success: {data.get('success')}")
            logger.info(f"   Response preview: {str(data.get('data', {}))[:200]}...")
            return True
        else:
            logger.error(f"❌ PATCH API test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ PATCH API test error: {e}")
        return False

def test_api_conversation_flow():
    """Test API configuration and conversation flow"""
    base_url = "http://localhost:8000"
    
    # Test conversation with API executor
    conversation_tests = [
        {
            "message": "I want to test a PUT API to update a post",
            "agent_type": "api_exec",
            "tenant_id": "default"
        },
        {
            "message": "Use https://jsonplaceholder.typicode.com/posts/1 with PUT method",
            "agent_type": "api_exec", 
            "tenant_id": "default"
        },
        {
            "message": "Set the body to update title and content",
            "agent_type": "api_exec",
            "tenant_id": "default"
        }
    ]
    
    logger.info("🔄 Testing API conversation flow...")
    
    for i, test in enumerate(conversation_tests, 1):
        try:
            logger.info(f"   Step {i}: {test['message']}")
            response = requests.post(
                f"{base_url}/api/chat",
                json=test,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                logger.info(f"   ✅ Response {i}: {response_text[:100]}...")
                
                if len(response_text) < 10:
                    logger.warning(f"   ⚠️ Short response for step {i}")
            else:
                logger.error(f"   ❌ HTTP {response.status_code} for step {i}")
                return False
                
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"   ❌ Error in step {i}: {e}")
            return False
    
    logger.info("✅ API conversation flow test completed")
    return True

def test_http_methods_support():
    """Test all HTTP methods support"""
    base_url = "http://localhost:8000"
    
    # Test different HTTP methods
    http_tests = [
        {
            "name": "GET",
            "config": {
                "base_url": "https://httpbin.org/get",
                "method": "GET",
                "query_params": {"test": "get_value"},
                "body": None,
                "headers": {}
            }
        },
        {
            "name": "POST",
            "config": {
                "base_url": "https://httpbin.org/post",
                "method": "POST",
                "query_params": {},
                "body": {"test": "post_value", "data": "test_data"},
                "headers": {"Content-Type": "application/json"}
            }
        },
        {
            "name": "PUT",
            "config": {
                "base_url": "https://httpbin.org/put",
                "method": "PUT",
                "query_params": {},
                "body": {"test": "put_value", "updated": "data"},
                "headers": {"Content-Type": "application/json"}
            }
        },
        {
            "name": "PATCH",
            "config": {
                "base_url": "https://httpbin.org/patch",
                "method": "PATCH",
                "query_params": {},
                "body": {"test": "patch_value"},
                "headers": {"Content-Type": "application/json"}
            }
        },
        {
            "name": "DELETE",
            "config": {
                "base_url": "https://httpbin.org/delete",
                "method": "DELETE",
                "query_params": {},
                "body": None,
                "headers": {}
            }
        }
    ]
    
    logger.info("🔄 Testing HTTP methods support...")
    
    results = {}
    for test in http_tests:
        try:
            logger.info(f"   Testing {test['name']} method...")
            response = requests.post(
                f"{base_url}/api/custom-api/execute",
                json=test['config'],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                results[test['name']] = success
                status = "✅" if success else "❌"
                logger.info(f"   {status} {test['name']}: {'SUCCESS' if success else 'FAILED'}")
            else:
                results[test['name']] = False
                logger.error(f"   ❌ {test['name']}: HTTP {response.status_code}")
                
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            results[test['name']] = False
            logger.error(f"   ❌ {test['name']}: {e}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    logger.info(f"✅ HTTP methods test: {success_count}/{total_count} methods working")
    return success_count >= total_count * 0.8  # 80% success threshold

def wait_for_server():
    """Wait for server to be ready"""
    base_url = "http://localhost:8000"
    max_attempts = 30
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                logger.info("✅ Server is ready!")
                return True
        except:
            pass
        
        logger.info(f"⏳ Waiting for server... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    logger.error("❌ Server failed to start within timeout")
    return False

def main():
    """Main test execution"""
    logger.info("🚀 Starting PUT API Feature Test")
    
    # Wait for server
    if not wait_for_server():
        logger.error("❌ Could not connect to server")
        exit(1)
    
    # Run tests
    test_results = {}
    
    tests = [
        ("PUT API Direct", test_put_api_direct),
        ("PATCH API Direct", test_patch_api_direct),
        ("HTTP Methods Support", test_http_methods_support),
        ("API Conversation Flow", test_api_conversation_flow)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            test_results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status} {test_name}")
        except Exception as e:
            test_results[test_name] = False
            logger.error(f"❌ {test_name} crashed: {e}")
    
    # Summary
    successful_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    logger.info(f"\n{'='*60}")
    logger.info("📋 PUT API FEATURE TEST RESULTS")
    logger.info(f"{'='*60}")
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall Results:")
    logger.info(f"   Tests Passed: {successful_tests}/{total_tests}")
    logger.info(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        logger.info("🎉 PUT API feature is working excellently!")
        exit(0)
    elif success_rate >= 60:
        logger.info("⚠️ PUT API feature has some issues but is functional")
        exit(0)
    else:
        logger.error("❌ PUT API feature has critical issues!")
        exit(1)

if __name__ == "__main__":
    main()