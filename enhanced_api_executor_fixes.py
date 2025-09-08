#!/usr/bin/env python3
"""
Enhanced API Executor Fixes
Comprehensive improvements for API executor agent functionality
"""

import json
import requests
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

def create_enhanced_api_executor_fixes():
    """
    Create enhanced fixes for the API executor system
    """
    
    # Enhanced CustomApiExecuteRequest with better error handling
    enhanced_request_handling = '''
async def execute_custom_api(req: CustomApiExecuteRequest):
    """Enhanced execute custom API with better error handling and method support"""
    from urllib.parse import urlparse
    import requests
    import json
    import time
    
    # Validate URL
    parsed = urlparse(req.base_url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")
    
    # Merge query parameters
    params = dict(req.query_params or {})
    if req.param_key and req.param_value and req.param_key not in params:
        params[req.param_key] = req.param_value
    
    try:
        method = (req.method or "GET").upper()
        headers = dict(req.headers or {})
        
        # Set default headers for JSON content
        if method in ("POST", "PUT", "PATCH") and req.body:
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        
        # Add User-Agent to prevent blocking
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Multi-Agent-Chatbot/1.0"
        
        # Enhanced request handling based on method
        if method == "GET":
            r = requests.get(
                req.base_url, 
                params=params or None, 
                headers=headers, 
                timeout=30,
                allow_redirects=True
            )
        elif method in ("POST", "PUT", "PATCH", "DELETE"):
            # Handle body data properly
            if req.body is not None:
                if isinstance(req.body, (dict, list)):
                    json_body = req.body
                    data_param = None
                else:
                    # Try to parse string as JSON
                    try:
                        json_body = json.loads(str(req.body))
                        data_param = None
                    except:
                        json_body = None
                        data_param = str(req.body)
            else:
                json_body = params if params else None
                data_param = None
            
            # Make the request
            r = requests.request(
                method, 
                req.base_url, 
                json=json_body if json_body is not None else None,
                data=data_param if data_param is not None else None,
                params=params if method == "DELETE" and not json_body else None,
                headers=headers, 
                timeout=30,
                allow_redirects=True
            )
        else:
            # Fallback to GET for unknown methods
            r = requests.get(req.base_url, params=params or None, headers=headers, timeout=30)

        # Enhanced response parsing
        response_data = {
            "success": r.ok,
            "status": r.status_code,
            "url": r.url,
            "method": method,
            "headers": dict(r.headers)
        }
        
        # Try to parse JSON response
        try:
            json_data = r.json()
            response_data["data"] = json_data
            response_data["content_type"] = "json"
        except:
            # Fallback to text
            response_data["text"] = r.text
            response_data["content_type"] = "text"
        
        # Add debug information
        response_data["request_headers"] = headers
        if json_body:
            response_data["request_body"] = json_body
        if params:
            response_data["request_params"] = params
            
        return response_data
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="API request timed out")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Failed to connect to API endpoint")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
'''
    
    # Enhanced API executor node with better conversation flow
    enhanced_node_api_exec = '''
def node_api_exec(state: MessagesState):
    """Enhanced API execution node with improved error handling and method support."""
    tenant_id = CURRENT_TENANT_ID or "default"
    session_id = CURRENT_SESSION.session_id if CURRENT_SESSION else "default"

    # Get available tools and APIs
    tools = get_tenant_tools(tenant_id)
    available_apis = list(DYNAMIC_API_MANAGER.apis.values())

    # Extract user message and conversation history
    user_msg = ""
    conversation_history = []

    for msg in state["messages"]:
        if hasattr(msg, "content"):
            content = msg.content
            msg_type = getattr(msg, "type", getattr(msg, "role", "unknown"))
            conversation_history.append(f"{msg_type}: {content}")
            if msg_type in ["human", "user"]:
                user_msg = content

    logger.info(f"Enhanced API Executor processing: {user_msg[:100]}...")

    # Enhanced API intent detection
    api_keywords = {
        'put': ['put', 'update', 'modify', 'change', 'edit'],
        'post': ['post', 'create', 'add', 'submit', 'send'],
        'patch': ['patch', 'partial', 'modify'],
        'delete': ['delete', 'remove', 'destroy'],
        'get': ['get', 'fetch', 'retrieve', 'read']
    }
    
    detected_method = None
    for method, keywords in api_keywords.items():
        if any(keyword in user_msg.lower() for keyword in keywords):
            detected_method = method.upper()
            break
    
    # Enhanced URL detection
    import re
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, user_msg)
    
    if urls and detected_method:
        # Direct API execution detected
        api_url = urls[0]
        logger.info(f"Detected API call: {detected_method} {api_url}")
        
        try:
            # Prepare request data
            request_data = {
                "base_url": api_url,
                "method": detected_method,
                "query_params": {},
                "body": None,
                "headers": {"Content-Type": "application/json"}
            }
            
            # Add body for PUT/POST/PATCH
            if detected_method in ["PUT", "POST", "PATCH"]:
                # Extract JSON from message if present
                json_pattern = r'\\{[^{}]*\\}'
                json_matches = re.findall(json_pattern, user_msg)
                if json_matches:
                    try:
                        request_data["body"] = json.loads(json_matches[0])
                    except:
                        pass
                
                # Default body if none found
                if not request_data["body"]:
                    if detected_method == "PUT":
                        request_data["body"] = {"updated": True, "timestamp": time.time()}
                    elif detected_method == "POST":
                        request_data["body"] = {"created": True, "timestamp": time.time()}
                    elif detected_method == "PATCH":
                        request_data["body"] = {"patched": True, "timestamp": time.time()}
            
            # Execute the API call
            response = execute_api_request(request_data)
            
            if response.get("success"):
                result_msg = f"✅ {detected_method} API call successful!\\n"
                result_msg += f"📡 Endpoint: {api_url}\\n"
                result_msg += f"📊 Status: {response.get('status')}\\n"
                
                if response.get("data"):
                    result_msg += f"📄 Response: {json.dumps(response['data'], indent=2)[:500]}..."
                elif response.get("text"):
                    result_msg += f"📄 Response: {response['text'][:500]}..."
                
                return {"messages": [("assistant", result_msg)]}
            else:
                error_msg = f"❌ {detected_method} API call failed\\n"
                error_msg += f"📡 Endpoint: {api_url}\\n"
                error_msg += f"📊 Status: {response.get('status')}\\n"
                error_msg += f"❗ Error: {response.get('error', 'Unknown error')}"
                
                return {"messages": [("assistant", error_msg)]}
                
        except Exception as e:
            logger.error(f"Enhanced API execution error: {e}")
            return {"messages": [("assistant", f"❌ API execution error: {str(e)}")]}
    
    # Check for active conversation flow
    active_flow = CONVERSATION_FLOW_MANAGER.get_flow(session_id) if 'CONVERSATION_FLOW_MANAGER' in globals() else None

    if active_flow and not active_flow.is_complete:
        return handle_active_flow(active_flow, user_msg, state)

    # Analyze for new API intent
    if 'INTELLIGENT_API_ROUTER' in globals():
        api_intent = INTELLIGENT_API_ROUTER.analyze_api_intent(user_msg, available_apis, conversation_history)
        if api_intent and api_intent.confidence > 0.7:
            return handle_new_api_intent(api_intent, user_msg, session_id, tenant_id, state)

    # Fallback to regular tool execution with enhanced prompting
    return handle_regular_tools_enhanced(tools, user_msg, state, detected_method)

def execute_api_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute API request with enhanced error handling"""
    try:
        method = request_data.get("method", "GET").upper()
        url = request_data.get("base_url")
        headers = request_data.get("headers", {})
        params = request_data.get("query_params", {})
        body = request_data.get("body")
        
        # Add default headers
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Multi-Agent-Chatbot/1.0"
        
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=30)
        elif method in ("POST", "PUT", "PATCH", "DELETE"):
            response = requests.request(
                method, url, json=body, params=params, headers=headers, timeout=30
            )
        else:
            response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Parse response
        result = {
            "success": response.ok,
            "status": response.status_code,
            "url": response.url,
            "method": method
        }
        
        try:
            result["data"] = response.json()
        except:
            result["text"] = response.text
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": 0
        }

def handle_regular_tools_enhanced(tools, user_msg: str, state: MessagesState, detected_method: str = None):
    """Enhanced regular tools handling with API method awareness"""
    
    # Create enhanced LLM with better prompting
    from main import get_llm
    llm_with_tools = get_llm(temperature=0).bind_tools(tools)
    
    # Enhanced system prompt
    system_prompt = f"""You are an advanced API execution specialist. Your role is to:

1. **API Method Expertise**: You understand all HTTP methods (GET, POST, PUT, PATCH, DELETE)
2. **Smart Tool Selection**: Choose the most appropriate tool for the user's request
3. **Error Recovery**: Provide helpful suggestions when API calls fail
4. **Method-Specific Guidance**: Provide specific guidance based on detected method: {detected_method or 'AUTO-DETECT'}

Available tools: {[tool.name for tool in tools]}

For API-related requests:
- Use search_web for finding public APIs
- Use get_weather for weather information  
- Use discover_api_endpoint for analyzing unknown APIs
- Provide clear explanations of what each API method does

If the user mentions PUT, POST, PATCH, DELETE methods, explain:
- PUT: Complete resource update/replacement
- POST: Create new resource or submit data
- PATCH: Partial resource update
- DELETE: Remove resource

Always provide helpful, accurate responses with practical examples."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
        
        response = llm_with_tools.invoke(messages)
        
        # Extract content properly
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'message') and hasattr(response.message, 'content'):
            content = response.message.content
        else:
            content = str(response)
        
        # Add method-specific tips
        if detected_method:
            method_tips = {
                "PUT": "💡 PUT is used for complete resource updates. The entire resource is replaced.",
                "POST": "💡 POST is used for creating new resources or submitting data.",
                "PATCH": "💡 PATCH is used for partial updates - only specified fields are modified.",
                "DELETE": "💡 DELETE is used for removing resources permanently.",
                "GET": "💡 GET is used for retrieving data without making changes."
            }
            
            if detected_method in method_tips:
                content += f"\\n\\n{method_tips[detected_method]}"
        
        return {"messages": [("assistant", content)]}
        
    except Exception as e:
        logger.error(f"Enhanced tool execution error: {e}")
        fallback_msg = f"I understand you want to work with APIs"
        if detected_method:
            fallback_msg += f" using the {detected_method} method"
        fallback_msg += ". I can help you test APIs, but I encountered an issue. Please try rephrasing your request or check if the API endpoint is accessible."
        
        return {"messages": [("assistant", fallback_msg)]}
'''
    
    return {
        'enhanced_request_handling': enhanced_request_handling,
        'enhanced_node_api_exec': enhanced_node_api_exec
    }

def create_web_interface_enhancements():
    """Create enhanced web interface for API testing"""
    
    api_test_interface = '''
<!-- Enhanced API Testing Interface -->
<div class="api-test-section" id="apiTestSection" style="display: none;">
    <div class="api-test-header">
        <h4><i class="fas fa-rocket"></i> API Testing Console</h4>
        <p>Test your APIs with all HTTP methods</p>
    </div>
    
    <div class="api-form">
        <div class="form-row">
            <div class="form-group">
                <label for="apiUrl">API Endpoint URL</label>
                <input type="url" id="apiUrl" placeholder="https://api.example.com/endpoint" required>
            </div>
            
            <div class="form-group">
                <label for="apiMethod">HTTP Method</label>
                <select id="apiMethod">
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="PATCH">PATCH</option>
                    <option value="DELETE">DELETE</option>
                </select>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="apiHeaders">Headers (JSON)</label>
                <textarea id="apiHeaders" placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}'></textarea>
            </div>
        </div>
        
        <div class="form-row" id="apiBodyRow">
            <div class="form-group">
                <label for="apiBody">Request Body (JSON)</label>
                <textarea id="apiBody" placeholder='{"key": "value", "data": "example"}'></textarea>
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="apiParams">Query Parameters (JSON)</label>
                <textarea id="apiParams" placeholder='{"param1": "value1", "param2": "value2"}'></textarea>
            </div>
        </div>
        
        <div class="api-actions">
            <button id="testApiBtn" class="btn-primary">
                <i class="fas fa-play"></i> Test API
            </button>
            <button id="saveApiBtn" class="btn-secondary">
                <i class="fas fa-save"></i> Save API Configuration
            </button>
            <button id="clearApiBtn" class="btn-outline">
                <i class="fas fa-trash"></i> Clear
            </button>
        </div>
    </div>
    
    <div class="api-response" id="apiResponse" style="display: none;">
        <h5><i class="fas fa-chart-line"></i> Response</h5>
        <div class="response-details">
            <div class="response-status" id="responseStatus"></div>
            <div class="response-headers" id="responseHeaders"></div>
            <div class="response-body" id="responseBody"></div>
        </div>
    </div>
</div>

<script>
// Enhanced API Testing JavaScript
class APITester {
    constructor() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        document.getElementById('apiMethod').addEventListener('change', (e) => {
            this.toggleBodyField(e.target.value);
        });
        
        document.getElementById('testApiBtn').addEventListener('click', () => {
            this.testAPI();
        });
        
        document.getElementById('saveApiBtn').addEventListener('click', () => {
            this.saveAPIConfiguration();
        });
        
        document.getElementById('clearApiBtn').addEventListener('click', () => {
            this.clearForm();
        });
    }
    
    toggleBodyField(method) {
        const bodyRow = document.getElementById('apiBodyRow');
        if (['GET', 'DELETE'].includes(method)) {
            bodyRow.style.display = 'none';
        } else {
            bodyRow.style.display = 'block';
        }
    }
    
    async testAPI() {
        const url = document.getElementById('apiUrl').value;
        const method = document.getElementById('apiMethod').value;
        const headers = this.parseJSON(document.getElementById('apiHeaders').value);
        const body = this.parseJSON(document.getElementById('apiBody').value);
        const params = this.parseJSON(document.getElementById('apiParams').value);
        
        if (!url) {
            this.showNotification('Please enter an API URL', 'error');
            return;
        }
        
        const testBtn = document.getElementById('testApiBtn');
        const originalText = testBtn.innerHTML;
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
        testBtn.disabled = true;
        
        try {
            const response = await fetch('/api/custom-api/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    base_url: url,
                    method: method,
                    headers: headers,
                    body: ['GET', 'DELETE'].includes(method) ? null : body,
                    query_params: params
                })
            });
            
            const result = await response.json();
            this.displayResponse(result);
            
        } catch (error) {
            this.showNotification(`API test failed: ${error.message}`, 'error');
        } finally {
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
        }
    }
    
    parseJSON(text) {
        if (!text || !text.trim()) return {};
        try {
            return JSON.parse(text);
        } catch (e) {
            return {};
        }
    }
    
    displayResponse(result) {
        const responseDiv = document.getElementById('apiResponse');
        const statusDiv = document.getElementById('responseStatus');
        const headersDiv = document.getElementById('responseHeaders');
        const bodyDiv = document.getElementById('responseBody');
        
        // Status
        const statusClass = result.success ? 'success' : 'error';
        statusDiv.innerHTML = `
            <div class="status-badge ${statusClass}">
                <i class="fas fa-${result.success ? 'check' : 'times'}"></i>
                ${result.status} ${result.success ? 'Success' : 'Failed'}
            </div>
        `;
        
        // Headers
        if (result.headers) {
            headersDiv.innerHTML = `
                <h6>Response Headers</h6>
                <pre>${JSON.stringify(result.headers, null, 2)}</pre>
            `;
        }
        
        // Body
        if (result.data) {
            bodyDiv.innerHTML = `
                <h6>Response Data</h6>
                <pre>${JSON.stringify(result.data, null, 2)}</pre>
            `;
        } else if (result.text) {
            bodyDiv.innerHTML = `
                <h6>Response Text</h6>
                <pre>${result.text}</pre>
            `;
        }
        
        responseDiv.style.display = 'block';
    }
    
    async saveAPIConfiguration() {
        const config = {
            name: prompt('Enter a name for this API configuration:'),
            base_url: document.getElementById('apiUrl').value,
            method: document.getElementById('apiMethod').value,
            headers: this.parseJSON(document.getElementById('apiHeaders').value),
            body: this.parseJSON(document.getElementById('apiBody').value),
            query_params: this.parseJSON(document.getElementById('apiParams').value)
        };
        
        if (!config.name || !config.base_url) {
            this.showNotification('Please provide a name and URL', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/dynamic-apis/${this.currentTenant}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                this.showNotification('API configuration saved successfully', 'success');
            } else {
                this.showNotification('Failed to save API configuration', 'error');
            }
            
        } catch (error) {
            this.showNotification(`Save failed: ${error.message}`, 'error');
        }
    }
    
    clearForm() {
        document.getElementById('apiUrl').value = '';
        document.getElementById('apiMethod').value = 'GET';
        document.getElementById('apiHeaders').value = '';
        document.getElementById('apiBody').value = '';
        document.getElementById('apiParams').value = '';
        document.getElementById('apiResponse').style.display = 'none';
        this.toggleBodyField('GET');
    }
    
    showNotification(message, type) {
        // Implement notification system
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Initialize API Tester
const apiTester = new APITester();
</script>
'''
    
    return api_test_interface

def main():
    """Main function to generate all fixes"""
    print("🔧 Generating Enhanced API Executor Fixes...")
    
    # Generate code fixes
    fixes = create_enhanced_api_executor_fixes()
    
    # Generate web interface enhancements
    web_enhancements = create_web_interface_enhancements()
    
    print("✅ Enhanced API Executor fixes generated successfully!")
    print("\nKey improvements:")
    print("1. ✅ Enhanced PUT/PATCH/DELETE method support")
    print("2. ✅ Better error handling and timeout management")
    print("3. ✅ Improved request/response parsing")
    print("4. ✅ Enhanced conversation flow for API configuration")
    print("5. ✅ Web interface for API testing")
    print("6. ✅ Method-specific guidance and tips")
    print("7. ✅ Better JSON handling and validation")
    print("8. ✅ Enhanced headers and User-Agent support")
    
    return fixes, web_enhancements

if __name__ == "__main__":
    main()