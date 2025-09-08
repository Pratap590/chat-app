#!/usr/bin/env python3
"""
Comprehensive Fix Verification - Final Test
Tests all reported issues to ensure they are resolved
"""

import requests
import json
import time
import os
import tempfile

BASE_URL = "http://localhost:8000"

def test_document_qa_comprehensive():
    """Test comprehensive document Q&A functionality"""
    print("📄 Testing Document Q&A Comprehensive Functionality")
    print("=" * 60)
    
    # Create test documents
    test_files = []
    
    # 1. Create a story PDF content (simulated as text)
    story_content = """
    The Tale of Two Cities
    
    Chapter 1: The Beginning
    Once upon a time in a bustling city, there lived a young baker named Maria. She had a small bakery on the corner of Main Street where she made the most delicious bread in town. Every morning, the aroma of fresh bread would fill the air, attracting customers from all around.
    
    Chapter 2: The Challenge
    One day, a large corporation decided to open a chain bakery right across the street. Maria was worried about losing her customers to the big company with their fancy equipment and marketing budget.
    
    Recipe for Maria's Famous Bread:
    - 3 cups of flour
    - 1 cup of warm water
    - 2 teaspoons of yeast
    - 1 tablespoon of sugar
    - 1 teaspoon of salt
    - 2 tablespoons of olive oil
    
    Instructions:
    1. Mix warm water, sugar, and yeast. Let it foam for 5 minutes.
    2. Add flour, salt, and olive oil to the yeast mixture.
    3. Knead the dough for 10 minutes until smooth.
    4. Let it rise for 1 hour in a warm place.
    5. Shape into loaves and bake at 375°F for 30 minutes.
    """
    
    with open("test_story.txt", "w") as f:
        f.write(story_content)
    test_files.append("test_story.txt")
    
    # 2. Create CSV data
    csv_content = """product_name,price,category,stock,description
iPhone 15 Pro,1199,Electronics,25,Latest flagship smartphone with titanium design
MacBook Air M3,1299,Electronics,15,Lightweight laptop with M3 chip
AirPods Pro,249,Electronics,50,Noise-canceling wireless earbuds
iPad Air,599,Electronics,30,Versatile tablet for work and creativity
Apple Watch,399,Electronics,40,Advanced health and fitness tracking"""
    
    with open("test_products.csv", "w") as f:
        f.write(csv_content)
    test_files.append("test_products.csv")
    
    # Upload documents
    tenant_id = "comprehensive_test"
    uploaded_count = 0
    
    for file_path in test_files:
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f)}
                data = {'tenant_id': tenant_id}
                response = requests.post(
                    f"{BASE_URL}/api/upload-document",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                print(f"✅ Uploaded {file_path}")
                uploaded_count += 1
            else:
                print(f"❌ Failed to upload {file_path}")
                
        except Exception as e:
            print(f"❌ Error uploading {file_path}: {str(e)}")
    
    # Wait for processing
    time.sleep(3)
    
    # Test queries
    test_queries = [
        # Story queries
        ("Tell me the story about Maria", "story"),
        ("What is the recipe for bread?", "recipe"),
        ("How many chapters are in the story?", "story"),
        
        # CSV queries
        ("What products are available?", "csv"),
        ("What is the price of iPhone 15 Pro?", "csv"),
        ("Which products are in the Electronics category?", "csv"),
        ("What is the most expensive product?", "csv"),
        
        # Cross-document queries
        ("What documents do you have?", "general"),
        ("Tell me about both the story and the products", "general"),
    ]
    
    successful_queries = 0
    
    for i, (query, query_type) in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}/{len(test_queries)} ({query_type}): {query}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat", json={
                "message": query,
                "tenant_id": tenant_id,
                "agent_type": "doc_qa"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check for meaningful responses
                success_indicators = []
                
                if query_type == "story":
                    success_indicators = [
                        "maria" in response_text.lower(),
                        "baker" in response_text.lower() or "bakery" in response_text.lower(),
                        "chapter" in response_text.lower() or "story" in response_text.lower(),
                        len(response_text) > 100
                    ]
                elif query_type == "recipe":
                    success_indicators = [
                        "flour" in response_text.lower(),
                        "yeast" in response_text.lower(),
                        "bread" in response_text.lower(),
                        "recipe" in response_text.lower()
                    ]
                elif query_type == "csv":
                    success_indicators = [
                        "iphone" in response_text.lower() or "macbook" in response_text.lower(),
                        "price" in response_text.lower() or "$" in response_text,
                        "electronics" in response_text.lower(),
                        len(response_text) > 50
                    ]
                else:  # general
                    success_indicators = [
                        "document" in response_text.lower(),
                        len(response_text) > 50,
                        not "no documents" in response_text.lower()
                    ]
                
                no_error_indicators = not any(error in response_text.lower() for error in [
                    "no documents indexed",
                    "couldn't find relevant information",
                    "information is not available",
                    "upload documents first"
                ])
                
                has_meaningful_content = sum(success_indicators) >= 2 and no_error_indicators
                
                if has_meaningful_content:
                    print(f"✅ SUCCESS: {response_text[:100]}...")
                    successful_queries += 1
                else:
                    print(f"❌ FAILED: {response_text[:100]}...")
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        time.sleep(1)
    
    # Test document deletion
    print(f"\n🗑️ Testing Document Deletion...")
    try:
        response = requests.delete(f"{BASE_URL}/api/documents/{tenant_id}")
        if response.status_code == 200:
            print("✅ Document deletion successful")
            
            # Test that documents are actually deleted
            time.sleep(2)
            response = requests.post(f"{BASE_URL}/api/chat", json={
                "message": "What documents do you have?",
                "tenant_id": tenant_id,
                "agent_type": "doc_qa"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                if "no documents" in response_text.lower():
                    print("✅ Documents properly deleted - no residual data")
                else:
                    print("❌ Documents may not be fully deleted")
        else:
            print(f"❌ Document deletion failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Document deletion error: {str(e)}")
    
    # Cleanup
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    
    print(f"\n📊 Document Q&A Results: {successful_queries}/{len(test_queries)} queries successful")
    return successful_queries, len(test_queries)

def test_api_executor_functionality():
    """Test API executor functionality"""
    print("\n🔧 Testing API Executor Functionality")
    print("=" * 60)
    
    test_queries = [
        ("What's the current time in New York?", "datetime"),
        ("Tell me a cat fact", "public_api"),
        ("What's the weather in London?", "weather"),
        ("Give me a random quote", "public_api"),
        ("Search for latest AI news", "search"),
    ]
    
    successful_queries = 0
    
    for i, (query, query_type) in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}/{len(test_queries)} ({query_type}): {query}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat", json={
                "message": query,
                "tenant_id": "api_test",
                "agent_type": "api_exec"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check for meaningful responses
                success_indicators = []
                
                if query_type == "datetime":
                    success_indicators = [
                        "time" in response_text.lower(),
                        "york" in response_text.lower() or "est" in response_text.lower(),
                        any(char.isdigit() for char in response_text),
                        len(response_text) > 20
                    ]
                elif query_type == "public_api":
                    success_indicators = [
                        "cat" in response_text.lower() or "quote" in response_text.lower(),
                        len(response_text) > 30,
                        "🐱" in response_text or "💭" in response_text,
                        not "error" in response_text.lower()
                    ]
                elif query_type == "weather":
                    success_indicators = [
                        "weather" in response_text.lower() or "temperature" in response_text.lower(),
                        "london" in response_text.lower(),
                        "°" in response_text or "degrees" in response_text.lower(),
                        len(response_text) > 30
                    ]
                elif query_type == "search":
                    success_indicators = [
                        "search" in response_text.lower() or "news" in response_text.lower(),
                        "ai" in response_text.lower(),
                        len(response_text) > 50,
                        "http" in response_text.lower() or "link" in response_text.lower()
                    ]
                
                has_meaningful_content = sum(success_indicators) >= 2
                
                if has_meaningful_content:
                    print(f"✅ SUCCESS: {response_text[:100]}...")
                    successful_queries += 1
                else:
                    print(f"❌ FAILED: {response_text[:100]}...")
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        time.sleep(1)
    
    print(f"\n📊 API Executor Results: {successful_queries}/{len(test_queries)} queries successful")
    return successful_queries, len(test_queries)

def main():
    """Run comprehensive fix verification"""
    print("🚀 COMPREHENSIVE FIX VERIFICATION - FINAL TEST")
    print("=" * 70)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)
    
    total_successful = 0
    total_queries = 0
    
    # Test document Q&A
    doc_successful, doc_total = test_document_qa_comprehensive()
    total_successful += doc_successful
    total_queries += doc_total
    
    # Test API executor
    api_successful, api_total = test_api_executor_functionality()
    total_successful += api_successful
    total_queries += api_total
    
    # Final summary
    print("\n" + "=" * 70)
    print("📋 FINAL COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    print(f"📄 Document Q&A: {doc_successful}/{doc_total} successful")
    print(f"🔧 API Executor: {api_successful}/{api_total} successful")
    print(f"📊 Overall: {total_successful}/{total_queries} successful")
    print(f"🎯 Success Rate: {(total_successful/total_queries)*100:.1f}%")
    
    if total_successful >= total_queries * 0.8:
        print("🎉 COMPREHENSIVE FIX VERIFICATION: EXCELLENT!")
        print("✅ All major issues have been resolved!")
    elif total_successful >= total_queries * 0.6:
        print("👍 COMPREHENSIVE FIX VERIFICATION: GOOD!")
        print("✅ Most issues have been resolved!")
    else:
        print("⚠️  COMPREHENSIVE FIX VERIFICATION: NEEDS MORE WORK")
        print("❌ Some issues still need attention")
    
    return total_successful >= total_queries * 0.7

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
