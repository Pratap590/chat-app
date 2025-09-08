#!/usr/bin/env python3
"""
Comprehensive API Executor Cross-Check and Testing
Tests all API executor functionality including the new PUT API feature
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List
import threading
import uvicorn
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIExecutorTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {}
        self.server_process = None
        
    def start_test_server(self):
        """Start the FastAPI server in a separate thread"""
        def run_server():
            import app
            uvicorn.run(app.app, host="127.0.0.1", port=8000, log_level="warning")
        
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Test server started successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to start test server: {e}")
            return False
    
    def test_basic_api_executor_agent(self) -> Dict[str, Any]:
        """Test basic API executor agent functionality"""
        logger.info("🔄 Testing Basic API Executor Agent")
        
        test_cases = [
            {
                "name": "Weather Query",
                "message": "What's the weather like today?",
                "tenant_id": "default",
                "agent_type": "api_exec"
            },
            {
                "name": "Time Query", 
                "message": "What time is it now?",
                "tenant_id": "default",
                "agent_type": "api_exec"
            },
            {
                "name": "Cat Fact Query",
                "message": "Tell me a cat fact",
                "tenant_id": "default", 
                "agent_type": "api_exec"
            }
        ]
        
        results = {}
        for test_case in test_cases:
            try:
                logger.info(f"Testing: {test_case['name']}")
                
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=test_case,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    success = len(data.get('response', '')) > 10
                    results[test_case['name']] = {
                        'success': success,
                        'response_length': len(data.get('response', '')),
                        'status_code': response.status_code,
                        'response_preview': data.get('response', '')[:100] + '...'
                    }
                    logger.info(f"✅ {test_case['name']}: {'SUCCESS' if success else 'PARTIAL'}")
                else:
                    results[test_case['name']] = {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'status_code': response.status_code
                    }
                    logger.warning(f"⚠️ {test_case['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[test_case['name']] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"❌ {test_case['name']}: {e}")
                
            time.sleep(1)  # Rate limiting
        
        success_count = sum(1 for r in results.values() if r.get('success'))
        total_count = len(results)
        
        return {
            'success': success_count >= total_count * 0.6,  # 60% success threshold
            'details': f"Basic API Executor: {success_count}/{total_count} successful",
            'results': results,
            'success_rate': (success_count / total_count) * 100
        }
    
    def test_custom_api_execution(self) -> Dict[str, Any]:
        """Test custom API execution with different HTTP methods"""
        logger.info("🔄 Testing Custom API Execution")
        
        test_apis = [
            {
                "name": "GET JSONPlaceholder Posts",
                "base_url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "GET",
                "query_params": {},
                "body": None,
                "headers": {"Accept": "application/json"}
            },
            {
                "name": "POST JSONPlaceholder",
                "base_url": "https://jsonplaceholder.typicode.com/posts",
                "method": "POST",
                "query_params": {},
                "body": {
                    "title": "Test Post",
                    "body": "This is a test post",
                    "userId": 1
                },
                "headers": {"Content-Type": "application/json"}
            },
            {
                "name": "PUT JSONPlaceholder",
                "base_url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "PUT",
                "query_params": {},
                "body": {
                    "id": 1,
                    "title": "Updated Post",
                    "body": "This is an updated test post",
                    "userId": 1
                },
                "headers": {"Content-Type": "application/json"}
            },
            {
                "name": "Cat Facts API",
                "base_url": "https://catfact.ninja/fact",
                "method": "GET",
                "query_params": {},
                "body": None,
                "headers": {}
            }
        ]
        
        results = {}
        for api_test in test_apis:
            try:
                logger.info(f"Testing Custom API: {api_test['name']}")
                
                response = requests.post(
                    f"{self.base_url}/api/custom-api/execute",
                    json=api_test,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    api_success = data.get('success', False)
                    results[api_test['name']] = {
                        'success': api_success,
                        'status_code': response.status_code,
                        'api_status': data.get('status', 'unknown'),
                        'has_data': bool(data.get('data') or data.get('text')),
                        'response_preview': str(data.get('data', data.get('text', '')))[:150] + '...'
                    }
                    logger.info(f"✅ {api_test['name']}: {'SUCCESS' if api_success else 'FAILED'}")
                else:
                    results[api_test['name']] = {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'status_code': response.status_code
                    }
                    logger.warning(f"⚠️ {api_test['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[api_test['name']] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"❌ {api_test['name']}: {e}")
                
            time.sleep(1)  # Rate limiting
        
        success_count = sum(1 for r in results.values() if r.get('success'))
        total_count = len(results)
        
        return {
            'success': success_count >= total_count * 0.75,  # 75% success threshold
            'details': f"Custom API Execution: {success_count}/{total_count} successful",
            'results': results,
            'success_rate': (success_count / total_count) * 100
        }
    
    def test_dynamic_api_management(self) -> Dict[str, Any]:
        """Test dynamic API registration and management"""
        logger.info("🔄 Testing Dynamic API Management")
        
        tenant_id = "test_tenant"
        test_api_config = {
            "name": "test_weather_api",
            "base_url": "https://api.openweathermap.org/data/2.5/weather",
            "method": "GET",
            "description": "Get weather information",
            "parameters": {
                "q": {"description": "City name", "required": True},
                "appid": {"description": "API key", "required": True}
            },
            "auth_type": "api_key",
            "auth_value": "dummy_key"
        }
        
        results = {}
        
        try:
            # Test API registration
            logger.info("Testing API registration")
            response = requests.post(
                f"{self.base_url}/api/dynamic-apis/{tenant_id}",
                json=test_api_config,
                timeout=15
            )
            
            registration_success = response.status_code == 200
            results['registration'] = {
                'success': registration_success,
                'status_code': response.status_code,
                'response': response.text[:200] if not registration_success else "Success"
            }
            
            if registration_success:
                logger.info("✅ API registration successful")
                
                # Test API listing
                logger.info("Testing API listing")
                response = requests.get(
                    f"{self.base_url}/api/dynamic-apis/{tenant_id}",
                    timeout=15
                )
                
                listing_success = response.status_code == 200
                if listing_success:
                    data = response.json()
                    has_registered_api = any(api.get('name') == test_api_config['name'] for api in data.get('apis', []))
                    listing_success = has_registered_api
                
                results['listing'] = {
                    'success': listing_success,
                    'status_code': response.status_code,
                    'found_registered_api': listing_success
                }
                
                if listing_success:
                    logger.info("✅ API listing successful")
                else:
                    logger.warning("⚠️ API listing failed or API not found")
                
                # Test API removal
                logger.info("Testing API removal")
                response = requests.delete(
                    f"{self.base_url}/api/dynamic-apis/{tenant_id}/{test_api_config['name']}",
                    timeout=15
                )
                
                removal_success = response.status_code == 200
                results['removal'] = {
                    'success': removal_success,
                    'status_code': response.status_code
                }
                
                if removal_success:
                    logger.info("✅ API removal successful")
                else:
                    logger.warning("⚠️ API removal failed")
            else:
                logger.warning("⚠️ API registration failed, skipping further tests")
                results['listing'] = {'success': False, 'error': 'Skipped due to registration failure'}
                results['removal'] = {'success': False, 'error': 'Skipped due to registration failure'}
                
        except Exception as e:
            logger.error(f"❌ Dynamic API management test error: {e}")
            results['error'] = str(e)
        
        success_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get('success'))
        total_count = len([r for r in results.values() if isinstance(r, dict) and 'success' in r])
        
        return {
            'success': success_count >= total_count * 0.66,  # 66% success threshold
            'details': f"Dynamic API Management: {success_count}/{total_count} successful",
            'results': results,
            'success_rate': (success_count / total_count) * 100 if total_count > 0 else 0
        }
    
    def test_conversation_flow_api(self) -> Dict[str, Any]:
        """Test conversational API parameter collection"""
        logger.info("🔄 Testing Conversation Flow API")
        
        try:
            # Start a conversation that requires parameter collection
            conversation_tests = [
                {
                    "name": "Multi-step API conversation",
                    "messages": [
                        "I want to check the weather",
                        "New York",
                        "Today"
                    ],
                    "expected_responses": 3
                }
            ]
            
            results = {}
            for test in conversation_tests:
                try:
                    responses = []
                    for i, message in enumerate(test["messages"]):
                        logger.info(f"Sending message {i+1}: {message}")
                        
                        response = requests.post(
                            f"{self.base_url}/api/chat",
                            json={
                                "message": message,
                                "agent_type": "api_exec",
                                "tenant_id": "default"
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            responses.append(data.get('response', ''))
                            logger.info(f"Response {i+1}: {data.get('response', '')[:100]}...")
                        else:
                            logger.warning(f"HTTP {response.status_code} for message {i+1}")
                        
                        time.sleep(1)
                    
                    success = len(responses) == test["expected_responses"] and all(len(r) > 10 for r in responses)
                    results[test["name"]] = {
                        'success': success,
                        'responses_count': len(responses),
                        'expected_count': test["expected_responses"],
                        'all_responses_valid': all(len(r) > 10 for r in responses)
                    }
                    
                except Exception as e:
                    results[test["name"]] = {
                        'success': False,
                        'error': str(e)
                    }
            
            success_count = sum(1 for r in results.values() if r.get('success'))
            total_count = len(results)
            
            return {
                'success': success_count >= total_count * 0.5,  # 50% success threshold (experimental feature)
                'details': f"Conversation Flow API: {success_count}/{total_count} successful",
                'results': results,
                'success_rate': (success_count / total_count) * 100 if total_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Conversation flow test error: {e}")
            return {
                'success': False,
                'details': f"Conversation Flow API test failed: {e}",
                'results': {},
                'success_rate': 0
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all API executor tests"""
        logger.info("🚀 Starting Comprehensive API Executor Cross-Check")
        
        # Start test server
        if not self.start_test_server():
            return {
                'success': False,
                'error': 'Failed to start test server',
                'results': {}
            }
        
        all_results = {}
        
        # Run all test suites
        test_suites = [
            ('Basic API Executor', self.test_basic_api_executor_agent),
            ('Custom API Execution', self.test_custom_api_execution),
            ('Dynamic API Management', self.test_dynamic_api_management),
            ('Conversation Flow', self.test_conversation_flow_api)
        ]
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running {suite_name} Tests")
            logger.info(f"{'='*60}")
            
            try:
                result = test_func()
                all_results[suite_name] = result
                
                status = "✅ PASSED" if result['success'] else "❌ FAILED"
                logger.info(f"{status} {suite_name}: {result['details']}")
                
            except Exception as e:
                logger.error(f"❌ {suite_name} test suite failed: {e}")
                all_results[suite_name] = {
                    'success': False,
                    'error': str(e),
                    'details': f"{suite_name} test suite crashed"
                }
        
        # Calculate overall results
        successful_suites = sum(1 for r in all_results.values() if r.get('success'))
        total_suites = len(all_results)
        overall_success_rate = (successful_suites / total_suites) * 100 if total_suites > 0 else 0
        
        overall_success = successful_suites >= total_suites * 0.75  # 75% threshold
        
        # Generate summary report
        logger.info(f"\n{'='*80}")
        logger.info("📋 COMPREHENSIVE API EXECUTOR TEST RESULTS")
        logger.info(f"{'='*80}")
        
        for suite_name, result in all_results.items():
            status = "✅ PASSED" if result.get('success') else "❌ FAILED"
            details = result.get('details', 'No details')
            success_rate = result.get('success_rate', 0)
            logger.info(f"{status} {suite_name}: {details} ({success_rate:.1f}%)")
        
        logger.info(f"\n🎯 Overall Results:")
        logger.info(f"   Test Suites Passed: {successful_suites}/{total_suites}")
        logger.info(f"   Overall Success Rate: {overall_success_rate:.1f}%")
        logger.info(f"   Status: {'✅ EXCELLENT' if overall_success_rate >= 90 else '✅ GOOD' if overall_success_rate >= 75 else '⚠️ NEEDS IMPROVEMENT' if overall_success_rate >= 50 else '❌ CRITICAL ISSUES'}")
        
        return {
            'success': overall_success,
            'overall_success_rate': overall_success_rate,
            'successful_suites': successful_suites,
            'total_suites': total_suites,
            'details': f"API Executor Comprehensive Test: {successful_suites}/{total_suites} suites passed",
            'results': all_results
        }

def main():
    """Main test execution"""
    tester = APIExecutorTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    results_file = Path("api_executor_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if results['success']:
        logger.info("🎉 API Executor comprehensive test completed successfully!")
        exit(0)
    else:
        logger.error("❌ API Executor has critical issues that need to be addressed!")
        exit(1)

if __name__ == "__main__":
    main()