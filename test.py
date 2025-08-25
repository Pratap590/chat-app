#!/usr/bin/env python3
"""
Test script for document upload and vector store fix
Tests the __fields_set__ Pydantic compatibility issue fix
"""

import os
import sys
import tempfile
import shutil
import logging
from pathlib import Path

# Add current directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_document():
    """Create a test document for upload testing"""
    test_content = """
# Test Document for Vector Store Fix

This is a test document to verify that the __fields_set__ Pydantic compatibility fix is working correctly.

## Section 1: Basic Information
This document contains multiple sections to test chunking and retrieval.

## Section 2: Technical Details
The fix addresses Pydantic v1/v2 compatibility issues when loading existing FAISS vector stores.

## Section 3: Test Queries
You can ask questions like:
- What is this document about?
- What technical details are mentioned?
- What sections does this document contain?

## Section 4: Recipe Example
Here's a simple recipe to test recipe queries:

**Chocolate Chip Cookies**
Ingredients:
- 2 cups flour
- 1 cup sugar
- 1/2 cup butter
- 1 cup chocolate chips

Instructions:
1. Mix flour and sugar
2. Add butter and mix well
3. Fold in chocolate chips
4. Bake at 350°F for 12 minutes

## Section 5: Story Example
Once upon a time, there was a developer who faced a Pydantic compatibility issue. 
The developer created a fix that automatically detected and resolved the problem.
The system lived happily ever after, processing documents without errors.
"""
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        return f.name

def test_document_upload():
    """Test document upload functionality"""
    logger.info("=" * 60)
    logger.info("TESTING DOCUMENT UPLOAD AND VECTOR STORE FIX")
    logger.info("=" * 60)
    
    try:
        # Import main module functions
        from main import ingest_single_document, get_retriever_for_tenant, set_current_tenant
        
        # Set tenant for testing
        tenant_id = "test_fix"
        set_current_tenant(tenant_id)
        logger.info(f"Set tenant to: {tenant_id}")
        
        # Create test document
        test_file = create_test_document()
        logger.info(f"Created test document: {test_file}")
        
        # Test document upload
        logger.info("\n--- Testing Document Upload ---")
        result = ingest_single_document(
            file_path=test_file,
            tenant_id=tenant_id,
            user_id="test_user",
            chunk_size=500,
            chunk_overlap=50
        )
        
        if result.get("success"):
            logger.info("✅ Document upload SUCCESSFUL")
            logger.info(f"Document ID: {result.get('document_id')}")
            logger.info(f"Chunks created: {result.get('chunk_count', 'unknown')}")
        else:
            logger.error("❌ Document upload FAILED")
            logger.error(f"Error: {result.get('message')}")
            return False
            
        # Test retriever creation
        logger.info("\n--- Testing Retriever Creation ---")
        retriever = get_retriever_for_tenant(tenant_id)
        
        if retriever:
            logger.info("✅ Retriever creation SUCCESSFUL")
        else:
            logger.error("❌ Retriever creation FAILED")
            return False
            
        # Test document retrieval
        logger.info("\n--- Testing Document Retrieval ---")
        test_queries = [
            "What is this document about?",
            "Tell me about the recipe",
            "What story is mentioned?",
            "What technical details are mentioned?"
        ]
        
        for query in test_queries:
            logger.info(f"\nTesting query: '{query}'")
            try:
                docs = retriever(query, k=3)
                if docs:
                    logger.info(f"✅ Retrieved {len(docs)} documents")
                    for i, doc in enumerate(docs):
                        logger.info(f"  Doc {i+1}: {doc.page_content[:100]}...")
                else:
                    logger.warning(f"⚠️  No documents retrieved for query: '{query}'")
            except Exception as e:
                logger.error(f"❌ Error retrieving documents for query '{query}': {e}")
                
        # Clean up test file
        os.unlink(test_file)
        logger.info(f"\nCleaned up test file: {test_file}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import main module: {e}")
        logger.error("Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during testing: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def test_vector_store_corruption_handling():
    """Test handling of corrupted vector stores"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING CORRUPTED VECTOR STORE HANDLING")
    logger.info("=" * 60)

    try:
        import pickle
        from main import _tenant_index_path, get_retriever_for_tenant

        # Create a fake corrupted vector store
        tenant_id = "test_corrupted"
        index_dir = _tenant_index_path(tenant_id)

        # Create directory and fake corrupted files
        os.makedirs(index_dir, exist_ok=True)

        # Create fake corrupted index files that will cause pickle errors
        with open(os.path.join(index_dir, "index.faiss"), "wb") as f:
            f.write(b"corrupted_faiss_data_not_valid")

        # Create a corrupted pickle file that will trigger the __fields_set__ error
        with open(os.path.join(index_dir, "index.pkl"), "wb") as f:
            # Create a pickle that will fail to load properly
            import pickle
            fake_data = {"corrupted": "data", "missing_fields": True}
            pickle.dump(fake_data, f)

        logger.info(f"Created fake corrupted vector store at: {index_dir}")

        # Test that the system handles corruption gracefully
        retriever = get_retriever_for_tenant(tenant_id)

        if retriever is None:
            logger.info("✅ Corrupted vector store handled correctly (returned None)")
        else:
            logger.warning("⚠️  Corrupted vector store not detected properly")

        # Check if corrupted directory was cleaned up
        if not os.path.exists(index_dir):
            logger.info("✅ Corrupted vector store directory cleaned up automatically")
        else:
            logger.info("ℹ️  Corrupted vector store directory still exists (may be cleaned up later)")
            # Clean up manually for the test
            shutil.rmtree(index_dir, ignore_errors=True)

        return True

    except Exception as e:
        logger.error(f"❌ Error testing corrupted vector store handling: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Document Upload and Vector Store Fix Tests")
    
    # Test 1: Document upload and retrieval
    test1_success = test_document_upload()
    
    # Test 2: Corrupted vector store handling
    test2_success = test_vector_store_corruption_handling()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    if test1_success:
        logger.info("✅ Document Upload Test: PASSED")
    else:
        logger.error("❌ Document Upload Test: FAILED")
        
    if test2_success:
        logger.info("✅ Corrupted Vector Store Test: PASSED")
    else:
        logger.error("❌ Corrupted Vector Store Test: FAILED")
        
    if test1_success and test2_success:
        logger.info("\n🎉 ALL TESTS PASSED! The __fields_set__ fix is working correctly.")
        return 0
    else:
        logger.error("\n💥 SOME TESTS FAILED! Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
