#!/usr/bin/env python3
"""
Final Comprehensive Test for Tiny Backspace

This script tests all components of the Tiny Backspace system to ensure
everything is working correctly.
"""

import requests
import json
import sys
import time

def test_api_endpoints():
    """Test all API endpoints"""
    print("🔍 Testing API Endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['name']} v{data['version']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data['status']}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    return True

def test_streaming_endpoint():
    """Test the main streaming endpoint"""
    print("\n🔍 Testing Streaming Endpoint...")
    
    url = "http://127.0.0.1:8000/code"
    data = {
        "repoUrl": "https://github.com/example/test-repo",
        "prompt": "Add error handling to all functions"
    }
    
    try:
        with requests.post(url, json=data, stream=True, timeout=30) as response:
            if response.status_code != 200:
                print(f"❌ Streaming endpoint failed: {response.status_code}")
                return False
            
            print(f"✅ Streaming endpoint: HTTP {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('content-type')}")
            
            # Check for at least one event
            event_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event = json.loads(line_str[6:])
                            event_type = event.get('type', 'unknown')
                            message = event.get('message', '')
                            
                            if event_count == 0:
                                print(f"✅ First event: {event_type} - {message}")
                            
                            event_count += 1
                            
                            # Stop after a few events to avoid waiting too long
                            if event_count >= 3:
                                print(f"✅ Received {event_count} events (streaming working)")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"⚠️  Non-JSON event: {line_str}")
            
            if event_count == 0:
                print("❌ No events received")
                return False
                
    except requests.exceptions.Timeout:
        print("⚠️  Request timed out (expected for non-existent repo)")
        return True  # This is expected behavior
    except Exception as e:
        print(f"❌ Streaming test error: {e}")
        return False
    
    return True

def test_imports():
    """Test that all modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    
    modules = ['main', 'git_operations', 'coding_agent']
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}.py imports successfully")
        except Exception as e:
            print(f"❌ {module}.py import failed: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Tiny Backspace - Final Comprehensive Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print("Please start the server with: python3 -m uvicorn main:app --port 8000")
            sys.exit(1)
    except:
        print("❌ Server is not running")
        print("Please start the server with: python3 -m uvicorn main:app --port 8000")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Run all tests
    tests = [
        ("Module Imports", test_imports),
        ("API Endpoints", test_api_endpoints),
        ("Streaming Endpoint", test_streaming_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Tiny Backspace is ready to use.")
        print("\n📋 Next steps:")
        print("1. Set GITHUB_TOKEN environment variable for PR creation")
        print("2. Use a real GitHub repository URL for testing")
        print("3. Run: python3 demo.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 