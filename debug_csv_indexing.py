#!/usr/bin/env python3
"""
Debug script to check CSV indexing in vector store
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import get_retriever_for_tenant, document_storage, get_document_stats

def debug_csv_indexing():
    """Debug CSV indexing issues"""
    tenant_id = "default"
    
    print("CSV Indexing Debug Report")
    print("=" * 50)
    
    # Check documents in storage
    print("\n1. Documents in storage:")
    documents = document_storage.get_documents_by_tenant(tenant_id)
    for doc in documents:
        print(f"   - {doc.filename} ({doc.file_type}) - ID: {doc.document_id}")
    
    # Check vector store stats
    print("\n2. Vector store statistics:")
    stats = get_document_stats(tenant_id)
    print(f"   - Total chunks: {stats.get('total_chunks', 'N/A')}")
    print(f"   - Unique sources: {stats.get('unique_sources', 'N/A')}")
    print(f"   - File types: {stats.get('file_types', {})}")
    
    # Test retrieval with CSV queries
    print("\n3. Testing retrieval with CSV-specific queries:")
    retriever = get_retriever_for_tenant(tenant_id)
    
    if retriever:
        test_queries = [
            "Laptop Pro",
            "price",
            "Electronics",
            "ProductID",
            "Wireless Mouse",
            "CSV",
            "products"
        ]
        
        for query in test_queries:
            docs = retriever(query, k=3)
            print(f"\n   Query: '{query}'")
            print(f"   Retrieved {len(docs)} documents:")
            for i, doc in enumerate(docs):
                content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                source = doc.metadata.get('source', 'Unknown')
                print(f"     {i+1}. Source: {source}")
                print(f"        Preview: {content_preview}")
    else:
        print("   ❌ No retriever available")

if __name__ == "__main__":
    debug_csv_indexing()