#!/usr/bin/env python3
"""
Detailed debug script to check the retrieval and Q&A process
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import get_retriever_for_tenant, node_doc_qa, MessagesState, document_storage, set_current_tenant

def debug_doc_qa_process():
    """Debug the entire document Q&A process"""
    tenant_id = "default"
    set_current_tenant(tenant_id)
    
    print("Document Q&A Process Debug")
    print("=" * 50)
    
    # Test 1: Check if retriever works
    print("\n1. Testing retriever function:")
    retriever = get_retriever_for_tenant(tenant_id)
    if retriever:
        print("✅ Retriever created successfully")
        
        # Test retrieval with specific CSV queries
        test_queries = [
            "What is the price of the Laptop Pro?",
            "Laptop Pro",
            "price 1200",
            "Electronics category"
        ]
        
        for query in test_queries:
            print(f"\n   Testing query: '{query}'")
            docs = retriever(query, k=5)
            print(f"   Retrieved {len(docs)} documents:")
            for i, doc in enumerate(docs):
                content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                print(f"     {i+1}. {content_preview}")
                print(f"        Source: {doc.metadata.get('source', 'Unknown')}")
    else:
        print("❌ No retriever available")
        return
    
    # Test 2: Check document storage
    print("\n\n2. Testing document storage:")
    documents = document_storage.get_documents_by_tenant(tenant_id)
    print(f"   Found {len(documents)} documents:")
    for doc in documents:
        print(f"     - {doc.filename} ({doc.file_type}) - ID: {doc.document_id}")
    
    # Test 3: Test the actual node_doc_qa function
    print("\n\n3. Testing node_doc_qa function:")
    
    test_message = "What is the price of the Laptop Pro?"
    state = MessagesState(messages=[("user", test_message)])
    
    try:
        result = node_doc_qa(state)
        print("✅ node_doc_qa executed successfully")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    response = last_message.content
                elif isinstance(last_message, tuple) and len(last_message) > 1:
                    response = last_message[1]
                else:
                    response = str(last_message)
                
                if len(response) > 500:
                    print(f"\nResponse: {response[:500]}...")
                else:
                    print(f"\nResponse: {response}")
        else:
            print(f"Unexpected result format: {result}")
            
    except Exception as e:
        print(f"❌ Error in node_doc_qa: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_doc_qa_process()