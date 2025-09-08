#!/usr/bin/env python3
"""
Demo: API Discovery Output Comparison
Shows the difference between verbose and structured output formats
"""

def show_old_vs_new_output():
    print("=" * 60)
    print("📊 API DISCOVERY OUTPUT COMPARISON")
    print("=" * 60)
    
    print("\n❌ OLD VERBOSE OUTPUT (for UI):")
    print("-" * 40)
    old_output = """🔍 **API ENDPOINT ANALYSIS**
📍 **URL**: GET https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-order-status?order_id=ORD002
📊 **Status Code**: 200 (OK)

📋 **RESPONSE HEADERS**:
   • Content-Type: application/json
   • Content-Length: 60
   • Server: cloudflare
   • Date: Mon, 25 Aug 2025 14:29:46 GMT

📄 **RESPONSE BODY ANALYSIS**:
   ✅ **Success Response**: 200
   📊 **Data Type**: JSON
   📐 **Structure Analysis**:
      📦 Object with 2 properties:
        • order_id: str (e.g., 'ORD002')
        • status: str (e.g., 'Shipped')
   📋 **Sample Response**:
      ```json
      {
  "order_id": "ORD002",
  "status": "Shipped"
}
      ```

🛠️ **USAGE RECOMMENDATIONS**:
   📍 **Base URL**: https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-order-status
   🔗 **Query Parameters**: order_id=ORD002
   📋 **Parameter Structure**:
      • order_id: ORD002 (example value)

🔧 **TOOL REGISTRATION SUGGESTION**:
   To use this API regularly, you can register it as a tool:
   ```
   /tool.httpget get_order_status https://oamrapppfdexxiyoesxo.supabase.co/functions/v1
   # Then use with path: /get-order-status
   ```"""
    
    print(old_output)
    
    print("\n\n✅ NEW STRUCTURED OUTPUT (for UI):")
    print("-" * 40)
    new_output = """**API ANALYSIS**
• **Method**: GET
• **Status**: 200 (OK)
• **Endpoint**: https://oamrapppfdexxiyoesxo.supabase.co/functions/v1/get-order-status
• **Parameters**:
  - order_id: ORD002
• **Format**: JSON
• **Structure**:
  - order_id: str
  - status: str
• **Sample**: `{"order_id":"ORD002","status":"Shipped"}`
• **Register**: `/tool.httpget get_order_status https://oamrapppfdexxiyoesxo.supabase.co/functions/v1`"""
    
    print(new_output)
    
    print("\n\n📈 IMPROVEMENTS:")
    print("• 🎯 Concise and scannable")
    print("• 📱 Better for UI display")
    print("• ⚡ Quick to read and understand")
    print("• 🎨 Less visual clutter")
    print("• 📋 Structured format")
    print("• 🔧 Essential information only")
    
    print("\n📊 METRICS:")
    print(f"• Old output: {len(old_output.splitlines())} lines")
    print(f"• New output: {len(new_output.splitlines())} lines")
    print(f"• Reduction: {((len(old_output.splitlines()) - len(new_output.splitlines())) / len(old_output.splitlines()) * 100):.1f}%")
    
    print("\n🎯 **PERFECT FOR:**")
    print("• Chat interfaces")
    print("• Mobile displays") 
    print("• Quick API scanning")
    print("• Technical summaries")
    print("• Developer workflows")

if __name__ == "__main__":
    show_old_vs_new_output()