import requests

url = "http://127.0.0.1:8000/code"
data = {
    "repoUrl": "https://github.com/example/simple-api",
    "prompt": "Add input validation to all POST endpoints and return proper error messages"
}

with requests.post(url, json=data, stream=True) as resp:
    for line in resp.iter_lines():
        if line:
            print(line.decode()) 