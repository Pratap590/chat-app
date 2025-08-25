#!/usr/bin/env python3
"""
Script to re-index the CSV file after fixing the processing error
"""

import sys
import os
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import document_storage, ingest_single_document
import shutil

def reindex_csv():
    """Re-index the CSV file"""
    tenant_id = "default"
    csv_file_path = "uploads/default/20250822_210121_products.csv"
    
    print("Re-indexing CSV file after fix")
    print("=" * 40)
    
    # Get the current document
    documents = document_storage.get_documents_by_tenant(tenant_id)
    csv_doc = None
    for doc in documents:
        if doc.filename == "20250822_210121_products.csv":
            csv_doc = doc
            break
    
    if csv_doc:
        print(f"Found CSV document: {csv_doc.document_id}")
        
        # Delete the document using API endpoint simulation
        print("Deleting existing CSV document...")
        try:
            # Simulate the API deletion process
            import sqlite3
            
            # Delete file from filesystem
            if os.path.exists(csv_doc.file_path):
                os.remove(csv_doc.file_path)
                print(f"Deleted file: {csv_doc.file_path}")
            
            # Remove from database
            conn = sqlite3.connect(document_storage.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE document_id = ?", (csv_doc.document_id,))
            conn.commit()
            conn.close()
            print("Removed from database")
            
            # Clean the vector store manually
            index_dir = "indices/faiss_default"
            if os.path.exists(index_dir):
                print("Removing old vector store index...")
                shutil.rmtree(index_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"Error during deletion: {e}")
    
    # Re-ingest the CSV file
    if os.path.exists(csv_file_path):
        print(f"Re-ingesting CSV file: {csv_file_path}")
        result = ingest_single_document(tenant_id, csv_file_path)
        
        if result.get("success"):
            print("✅ CSV file re-indexed successfully!")
            print(f"Document ID: {result.get('document_id')}")
        else:
            print(f"❌ Failed to re-index CSV: {result.get('message')}")
    else:
        print(f"❌ CSV file not found: {csv_file_path}")

if __name__ == "__main__":
    reindex_csv()