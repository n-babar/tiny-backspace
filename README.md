# Tiny Backspace

A minimal coding agent that creates GitHub PRs from prompts using FastAPI and Server-Sent Events.

## 🌐 Public URL

When deployed to a cloud platform, you can access the API at:

```
https://<your-deployment-domain>/
```

**Examples:**
- Render: `https://tiny-backspace.onrender.com/`
- Heroku: `https://your-app-name.herokuapp.com/`
- Railway: `https://tiny-backspace.railway.app/`
- AWS: `https://your-api-gateway-url.amazonaws.com/`

**Available Endpoints:**
- **Health Check:** `GET /health` - Check if the service is running
- **API Info:** `GET /` - Get API documentation and status
- **Main Endpoint:** `POST /code` - Create PRs with LLM and sandboxing support
- **Legacy Endpoint:** `POST /code/legacy` - Original endpoint for backward compatibility

**Note:** Replace `<your-deployment-domain>` with your actual deployment URL after deploying to your chosen platform.

## ��️ Running Locally

### Prerequisites
- Python 3.8+
- GitHub CLI (for PR creation)
- GitHub Personal Access Token

### Setup Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install GitHub CLI:**
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

3. **Set environment variables:**
   ```bash
   export GITHUB_TOKEN="your-github-token"
   # Optional: For LLM features
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   ```

4. **Authenticate GitHub CLI:**
   ```bash
   gh auth login --with-token <<< "your-github-token"
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Test the API:**
   ```bash
   python test.py
   ```

## 🤖 Coding Agent Approach

This project uses a **hybrid agent approach**:

### **Rule-Based Agent (Default)**
- **Works without API keys** - always available
- **Handles basic prompts** like:
  - "Create a new Python file with a function"
  - "Add a new test file called integration_test.py"
  - "Create a new configuration file"
- **Fast and predictable** - instant responses
- **Limited to simple patterns** - creates basic files and functions

### **LLM-Enhanced Agent (Optional)**
- **Requires OpenAI or Anthropic API keys**
- **Handles complex prompts** like:
  - "Refactor the authentication system to use JWT tokens"
  - "Add comprehensive error handling to all API endpoints"
  - "Convert this synchronous code to async/await"
- **Analyzes codebase** and generates intelligent changes
- **Falls back to rule-based** if LLMs are unavailable

### **Why This Approach?**
- **Reliability:** System always works, even if LLM APIs are down
- **Flexibility:** Users can choose simple or advanced features
- **Transparency:** Clear indication of which agent was used

## 🚀 Features

### Core Features
- **FastAPI-based streaming API** with Server-Sent Events
- **Sandboxed repository cloning** for security
- **Hybrid coding agent** (rule-based + LLM)
- **Git operations** (commit, push, PR creation)
- **Real-time event streaming** for progress updates

### Enhanced Features
- **LLM Integration**: OpenAI GPT-4/3.5 and Anthropic Claude support
- **Cloud Sandboxing**: Docker containers and AWS Lambda framework
- **Backward Compatibility**: Original endpoints still work
- **Health Monitoring**: Component status reporting

## 📋 API Usage

### Basic Usage (Rule-Based Agent)
```bash
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/username/repo",
    "prompt": "Create a new Python file with a function",
    "use_llm": false
  }' --no-buffer
```

### Advanced Usage (LLM Agent)
```bash
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/username/repo",
    "prompt": "Add comprehensive error handling to all API endpoints",
    "use_llm": true,
    "llm_provider": "openai",
    "llm_model": "gpt-4"
  }' --no-buffer
```

### Legacy Endpoint (Backward Compatible)
```bash
curl -X POST "http://localhost:8000/code/legacy" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/username/repo",
    "prompt": "Add error handling"
  }'
```

**Note:** Use `--no-buffer` flag to see real-time streaming events.

## 🔧 Configuration

### Environment Variables

#### Required
- `GITHUB_TOKEN`: GitHub personal access token for PR creation

#### Optional LLM
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEFAULT_LLM_PROVIDER`: Default LLM provider (openai, anthropic, rule_based)
- `DEFAULT_LLM_MODEL`: Default LLM model

#### Optional Sandboxing
- `AWS_ACCESS_KEY_ID`: AWS access key for Lambda sandboxing
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for Lambda sandboxing
- `DEFAULT_SANDBOX_PROVIDER`: Default sandbox provider (local, docker, aws)

#### Server Configuration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)

## 🧪 Testing

### Run All Tests
```bash
python test.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test basic functionality
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/n-babar/tiny-backspace",
    "prompt": "Create a new Python file with a function",
    "use_llm": false
  }' --no-buffer
```

## 🛠️ Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000
kill -9 <process-id>

# Check imports
python3 -c "import main; print('✅ Imports successful')"
```

#### GitHub Token Issues
- Verify token has `repo` permissions
- Check token expiration
- Ensure repository access

#### LLM API Errors
- Check API key validity
- Verify API quota and limits
- Ensure proper environment variables

#### Docker Sandbox Issues
- Verify Docker is running
- Check Docker permissions
- Ensure sufficient disk space

### Debug Mode
```bash
export DEBUG=true
python main.py
```

## 📊 Project Structure

```
tiny-backspace/
├── main.py              # FastAPI application
├── coding_agent.py      # Rule-based coding agent
├── llm_agent.py         # LLM integration
├── git_operations.py    # Git operations
├── cloud_sandbox.py     # Cloud sandboxing
├── config.py            # Configuration management
├── requirements.txt     # Dependencies
├── test.py              # Test suite
└── README.md            # This file
```

