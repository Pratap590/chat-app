#!/usr/bin/env python3
"""
Direct System Check - Quick verification of core functionality
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Check if all core modules import correctly"""
    print("🔍 Checking Core Imports...")
    try:
        from main import (
            create_tenant, get_system_stats, get_tool_stats,
            node_doc_qa, node_form_gen, node_api_exec, 
            node_analytics, node_escalate, set_current_tenant,
            search_web, get_weather, get_document_stats_tool
        )
        print("✅ All core imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def check_basic_functionality():
    """Check basic system functionality"""
    print("\n🔍 Checking Basic Functionality...")
    try:
        from main import create_tenant, set_current_tenant, get_system_stats
        
        # Create test tenant
        tenant_id = "quick_test"
        create_tenant(tenant_id, "Quick Test", ["read_documents", "use_tools", "generate_forms"])
        set_current_tenant(tenant_id)
        
        # Get system stats
        stats = get_system_stats()
        print(f"✅ System stats: {stats.get('tenants', {}).get('total', 0)} tenants")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        traceback.print_exc()
        return False

def check_tools():
    """Check if tools are properly defined"""
    print("\n🔍 Checking Tools...")
    try:
        from main import get_tenant_tools, set_current_tenant
        
        set_current_tenant("quick_test")
        tools = get_tenant_tools("quick_test")
        # Handle both function tools and StructuredTool objects
        tool_names = []
        for tool in tools:
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', str(tool)))
            tool_names.append(tool_name)
        
        print(f"✅ Found {len(tools)} tools: {tool_names}")
        
        # Check for required tools
        required_tools = ['search_web', 'get_weather', 'get_document_stats_tool']
        missing_tools = [tool for tool in required_tools if tool not in tool_names]
        
        if missing_tools:
            print(f"⚠️ Missing tools: {missing_tools}")
            return False
        else:
            print("✅ All required tools present")
            return True
            
    except Exception as e:
        print(f"❌ Tools check error: {e}")
        traceback.print_exc()
        return False

def test_search_web_directly():
    """Test search_web function directly"""
    print("\n🔍 Testing Search Web Function...")
    try:
        from main import search_web
        
        result = search_web("Python programming")
        print(f"✅ Search result: {result[:100]}...")
        
        # Check if result is meaningful
        if len(result) > 20 and "rate limited" not in result.lower():
            print("✅ Search web working")
            return True
        else:
            print(f"⚠️ Search result may be limited: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Search web error: {e}")
        traceback.print_exc()
        return False

def test_weather_directly():
    """Test weather function directly"""
    print("\n🔍 Testing Weather Function...")
    try:
        from main import get_weather
        
        result = get_weather("New York")
        print(f"✅ Weather result: {result[:100]}...")
        
        # Check if result contains weather data
        if any(word in result.lower() for word in ["temperature", "°c", "°f", "weather", "humidity"]):
            print("✅ Weather function working")
            return True
        else:
            print(f"⚠️ Weather result may be limited: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Weather function error: {e}")
        traceback.print_exc()
        return False

def test_node_functionality():
    """Test node functions"""
    print("\n🔍 Testing Node Functions...")
    try:
        from main import node_analytics, MessagesState, set_current_tenant
        
        set_current_tenant("quick_test")
        
        # Test analytics node
        state = MessagesState(messages=[("user", "Show me system statistics")])
        result = node_analytics(state)
        
        if result and 'messages' in result:
            response = result['messages'][0]
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, tuple):
                content = response[1]
            else:
                content = str(response)
            
            print(f"✅ Analytics node result: {content[:100]}...")
            return True
        else:
            print("❌ Analytics node returned no result")
            return False
            
    except Exception as e:
        print(f"❌ Node functionality error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all checks"""
    print("🚀 DIRECT SYSTEM CHECK")
    print("=" * 50)
    
    checks = [
        ("Core Imports", check_imports),
        ("Basic Functionality", check_basic_functionality), 
        ("Tools Check", check_tools),
        ("Search Web", test_search_web_directly),
        ("Weather Function", test_weather_directly),
        ("Node Functions", test_node_functionality)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All systems operational!")
        return True
    else:
        print("⚠️ Some issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)