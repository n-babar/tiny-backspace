import requests
import json

def test_streaming_endpoint():
    url = "http://127.0.0.1:8000/code"
    data = {
        "repoUrl": "https://github.com/example/simple-api",
        "prompt": "Add input validation to all POST endpoints and return proper error messages"
    }

    print("Testing Tiny Backspace streaming endpoint...")
    print("=" * 50)
    
    try:
        with requests.post(url, json=data, stream=True) as resp:
            print(f"Status Code: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('content-type')}")
            print("\nStreaming Events:")
            print("-" * 30)
            
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            event_type = event_data.get('type', 'unknown')
                            message = event_data.get('message', '')
                            
                            # Color coding for different event types
                            if event_type == 'info':
                                print(f"ℹ️  INFO: {message}")
                            elif event_type == 'progress':
                                print(f"⏳ PROGRESS: {message}")
                            elif event_type == 'success':
                                print(f"✅ SUCCESS: {message}")
                            elif event_type == 'warning':
                                print(f"⚠️  WARNING: {message}")
                            elif event_type == 'error':
                                print(f"❌ ERROR: {message}")
                            elif event_type == 'change':
                                print(f"📝 CHANGE: {message}")
                            elif event_type == 'done':
                                print(f"🎉 DONE: {message}")
                                if 'pr_url' in event_data:
                                    print(f"🔗 PR URL: {event_data['pr_url']}")
                            else:
                                print(f"❓ {event_type.upper()}: {message}")
                                
                        except json.JSONDecodeError:
                            print(f"Raw line: {line_str}")
                            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://127.0.0.1:8000")
        print("Start the server with: python3 -m uvicorn main:app --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_streaming_endpoint() 