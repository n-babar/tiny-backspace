import asyncio
from main import app, CodeRequest
from fastapi.testclient import TestClient

# Test the app directly
client = TestClient(app)

# Test the /code endpoint
data = {
    "repoUrl": "https://github.com/example/simple-api",
    "prompt": "Add input validation to all POST endpoints and return proper error messages"
}

response = client.post("/code", json=data)
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content: {response.text[:200]}...")  # First 200 chars 