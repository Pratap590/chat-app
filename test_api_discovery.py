#!/usr/bin/env python3
"""
Test script for the new API Discovery functionality
This demonstrates how the API discovery feature works with the provided Supabase APIs
"""

import requests
import json
from typing import Any, List, Optional, Dict

def analyze_api_response(url: str, method: str, response: requests.Response, 
                        request_headers: dict, request_body: Optional[dict]) -> str:
    """Analyze an API response and provide detailed insights."""
    
    analysis_parts = []
    analysis_parts.append(f"🔍 **API ENDPOINT ANALYSIS**")
    analysis_parts.append(f"📌 **URL**: {method.upper()} {url}")
    analysis_parts.append(f"📊 **Status Code**: {response.status_code} ({response.reason})")
    
    # Response headers analysis
    analysis_parts.append(f"\n📋 **RESPONSE HEADERS**:")
    important_headers = ['content-type', 'content-length', 'server', 'date', 'cache-control', 'access-control-allow-origin']
    for header in important_headers:
        if header in response.headers:
            analysis_parts.append(f"   • {header.title()}: {response.headers[header]}")
    
    # Content type analysis
    content_type = response.headers.get('content-type', '').lower()
    
    # Response body analysis
    analysis_parts.append(f"\n📄 **RESPONSE BODY ANALYSIS**:")
    
    if response.status_code >= 400:
        analysis_parts.append(f"   ❌ **Error Response**: {response.status_code}")
        try:
            error_text = response.text[:500]
            analysis_parts.append(f"   📝 **Error Details**: {error_text}")
        except:
            analysis_parts.append(f"   📝 **Error Details**: Unable to read error response")
    else:
        analysis_parts.append(f"   ✅ **Success Response**: {response.status_code}")
        
        # Try to parse and analyze JSON response
        if 'json' in content_type:
            try:
                json_data = response.json()
                analysis_parts.append(f"   📊 **Data Type**: JSON")
                analysis_parts.append(f"   📊 **Structure Analysis**:")
                
                structure_info = analyze_json_structure(json_data)
                analysis_parts.extend([f"      {line}" for line in structure_info])
                
                # Sample data (truncated)
                sample_data = json.dumps(json_data, indent=2)[:800]
                if len(json.dumps(json_data)) > 800:
                    sample_data += "\n      ... (truncated)"
                analysis_parts.append(f"   📋 **Sample Response**:")
                analysis_parts.append(f"      ```json\n      {sample_data}\n      ```")
                
            except json.JSONDecodeError:
                analysis_parts.append(f"   ⚠️ **JSON Parse Error**: Response claims to be JSON but is not valid")
                analysis_parts.append(f"   📝 **Raw Content**: {response.text[:500]}")
        
        # Handle other content types
        elif 'text' in content_type or 'html' in content_type:
            analysis_parts.append(f"   📊 **Data Type**: Text/HTML")
            analysis_parts.append(f"   📝 **Content Preview**: {response.text[:300]}")
        else:
            analysis_parts.append(f"   📊 **Data Type**: {content_type or 'Unknown'}")
            analysis_parts.append(f"   📊 **Content Length**: {len(response.content)} bytes")
    
    # API Usage recommendations
    analysis_parts.append(f"\n🛠️ **USAGE RECOMMENDATIONS**:")
    
    if response.status_code < 400:
        # Generate usage example
        if '?' in url:
            base_url, params = url.split('?', 1)
            analysis_parts.append(f"   📌 **Base URL**: {base_url}")
            analysis_parts.append(f"   🔗 **Query Parameters**: {params}")
            
            # Parse query parameters
            try:
                from urllib.parse import parse_qs, urlparse
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                analysis_parts.append(f"   📋 **Parameter Structure**:")
                for param, values in query_params.items():
                    analysis_parts.append(f"      • {param}: {values[0]} (example value)")
            except:
                pass
        
        # Tool registration suggestion
        tool_name = url.split('/')[-1].replace('-', '_')
        if '?' in tool_name:
            tool_name = tool_name.split('?')[0]
        
        analysis_parts.append(f"\n🔧 **TOOL REGISTRATION SUGGESTION**:")
        analysis_parts.append(f"   To use this API regularly, you can register it as a tool:")
        
        if '?' in url:
            base_url = url.split('?')[0].rsplit('/', 1)[0]
            path = '/' + url.split('?')[0].split('/')[-1]
            analysis_parts.append(f"   ```")
            analysis_parts.append(f"   /tool.httpget {tool_name} {base_url}")
            analysis_parts.append(f"   # Then use with path: {path}")
            analysis_parts.append(f"   ```")
    
    return "\n".join(analysis_parts)


def analyze_json_structure(data: Any, level: int = 0, max_level: int = 3) -> List[str]:
    """Recursively analyze JSON structure and return insights."""
    indent = "  " * level
    structure_info = []
    
    if level > max_level:
        structure_info.append(f"{indent}... (nested structure continues)")
        return structure_info
    
    if isinstance(data, dict):
        structure_info.append(f"{indent}📦 Object with {len(data)} properties:")
        for key, value in list(data.items())[:5]:  # Limit to first 5 properties
            value_type = type(value).__name__
            if isinstance(value, list) and value:
                structure_info.append(f"{indent}  • {key}: Array[{len(value)}] of {type(value[0]).__name__}")
            elif isinstance(value, dict):
                structure_info.append(f"{indent}  • {key}: Object")
                if level < max_level:
                    structure_info.extend(analyze_json_structure(value, level + 1, max_level))
            else:
                example_value = str(value)[:50]
                if len(str(value)) > 50:
                    example_value += "..."
                structure_info.append(f"{indent}  • {key}: {value_type} (e.g., '{example_value}')")
        
        if len(data) > 5:
            structure_info.append(f"{indent}  ... and {len(data) - 5} more properties")
    
    elif isinstance(data, list):
        structure_info.append(f"{indent}📋 Array with {len(data)} items")
        if data and level < max_level:
            structure_info.append(f"{indent}  Sample item structure:")
            structure_info.extend(analyze_json_structure(data[0], level + 1, max_level))
    
    else:
        value_type = type(data).__name__
        example_value = str(data)[:50]
        if len(str(data)) > 50:
            example_value += "..."
        structure_info.append(f"{indent}📄 {value_type}: '{example_value}'")
    
    return structure_info


def test_api_discovery():
    """Test the API discovery functionality with the provided Supabase APIs."""
    
    print("🚀 Testing API Discovery Functionality")
    print("=" * 60)
    
    # Sample APIs provided by the user
    sample_apis = [
        "https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-order-status?order_id=ORD002",
        "https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-product-price?id=2bc2af12-1287-4fdf-adbd-6a76358ca9dd"
    ]
    
    for i, url in enumerate(sample_apis, 1):
        print(f"\n🔍 **API {i} ANALYSIS**")
        print(f"URL: {url}")
        print("-" * 40)
        
        try:
            # Make the API request
            headers = {"User-Agent": "API-Discovery-Test/1.0"}
            response = requests.get(url, headers=headers, timeout=15)
            
            # Analyze the response
            analysis = analyze_api_response(url, "GET", response, headers, None)
            print(analysis)
            
        except requests.exceptions.Timeout:
            print(f"❌ **Timeout**: API request timed out after 15 seconds")
        except requests.exceptions.ConnectionError:
            print(f"❌ **Connection Error**: Unable to connect to the API")
        except Exception as e:
            print(f"❌ **Error**: {e}")
        
        print("\n" + "=" * 60)
    
    print("\n✅ **API Discovery Test Complete**")
    print("\n💡 **Key Features Demonstrated**:")
    print("  • Automatic API structure analysis")
    print("  • Response format detection")
    print("  • Parameter identification")
    print("  • Tool registration suggestions")
    print("  • Error handling and diagnostics")


if __name__ == "__main__":
    test_api_discovery()