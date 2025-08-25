#!/usr/bin/env python3
"""
Simple test runner for the document upload fix
"""

import subprocess
import sys
import os

def run_test():
    """Run the test script"""
    print("🧪 Running Document Upload and Vector Store Fix Tests...")
    print("=" * 60)
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test.py"], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n🎉 All tests completed successfully!")
        else:
            print(f"\n💥 Tests failed with exit code: {result.returncode}")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: test.py file not found!")
        print("Make sure you're running this from the correct directory.")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_test()
    sys.exit(exit_code)
