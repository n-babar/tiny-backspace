#!/usr/bin/env python3
"""
Tiny Backspace Demo

This script demonstrates how to use the Tiny Backspace API to automatically
create pull requests from coding prompts.
"""

import requests
import json
import time
import sys

def demo_tiny_backspace():
    """Demonstrate the Tiny Backspace API"""
    
    print("🚀 Tiny Backspace Demo")
    print("=" * 50)
    print()
    
    # Configuration
    api_url = "http://127.0.0.1:8000/code"
    
    # Example request - you can modify these
    repo_url = "https://github.com/example/simple-api"  # Replace with a real public repo
    prompt = "Add input validation to all POST endpoints and return proper error messages"
    
    print(f"📁 Repository: {repo_url}")
    print(f"💡 Prompt: {prompt}")
    print()
    print("⏳ Starting coding process...")
    print("-" * 50)
    
    # Prepare request
    data = {
        "repoUrl": repo_url,
        "prompt": prompt
    }
    
    try:
        # Make streaming request
        with requests.post(api_url, json=data, stream=True) as response:
            if response.status_code != 200:
                print(f"❌ Error: HTTP {response.status_code}")
                return
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            event_type = event.get('type', 'unknown')
                            message = event.get('message', '')
                            
                            # Display event with appropriate emoji
                            if event_type == 'info':
                                print(f"ℹ️  {message}")
                            elif event_type == 'progress':
                                print(f"⏳ {message}")
                            elif event_type == 'success':
                                print(f"✅ {message}")
                            elif event_type == 'warning':
                                print(f"⚠️  {message}")
                            elif event_type == 'error':
                                print(f"❌ {message}")
                            elif event_type == 'change':
                                print(f"📝 {message}")
                            elif event_type == 'done':
                                print(f"🎉 {message}")
                                if 'pr_url' in event:
                                    print(f"🔗 PR URL: {event['pr_url']}")
                                if 'changes' in event:
                                    print("\n📋 Changes made:")
                                    for change in event['changes']:
                                        print(f"   • {change}")
                                break  # End of stream
                            else:
                                print(f"❓ {message}")
                                
                        except json.JSONDecodeError:
                            print(f"Raw: {line_str}")
                            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print()
        print("Make sure the Tiny Backspace server is running:")
        print("   python3 -m uvicorn main:app --port 8000")
        print()
        print("Or check if the server is running on a different port.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🔍 Checking if server is running...")
    
    if not check_server():
        print("❌ Server is not running!")
        print()
        print("Please start the Tiny Backspace server first:")
        print("   python3 -m uvicorn main:app --port 8000")
        print()
        sys.exit(1)
    
    print("✅ Server is running!")
    print()
    
    # Run the demo
    demo_tiny_backspace() 