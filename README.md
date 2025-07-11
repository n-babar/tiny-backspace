# Tiny Backspace

A minimal coding agent that creates GitHub PRs from prompts using FastAPI and Server-Sent Events.

## 🌐 Public URL
If deployed, you can access the API at:

```
https://<your-deployment-domain>/
```

Replace `<your-deployment-domain>` with your actual deployment address (e.g., on Render, Heroku, AWS, etc.).

- **Health check:** `GET /health`
- **API info:** `GET /`
- **Main endpoint:** `POST /code`
- **Legacy endpoint:** `POST /code/legacy`

## 🖥️ Running Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** The requirements.txt file includes all necessary dependencies. Optional LLM and cloud sandboxing packages are already included and will be installed automatically.

2. **Install GitHub CLI (for PR creation):**
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

3. **Set environment variables:**
   - `GITHUB_TOKEN` (required for PR creation)
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (optional, for LLM features)

4. **Authenticate GitHub CLI:**
   ```bash
   gh auth login --with-token <<< "your-github-token"
   ```

5. **Start the server:**
   ```bash
   # From the project directory
   uvicorn main:app --reload --port 8000
   
   # Or with environment variables
   export GITHUB_TOKEN="your-token"
   uvicorn main:app --reload --port 8000
   ```

6. **Test the API:**
   ```bash
   python test.py
   ```

## 🤖 Coding Agent Approach

This project uses a **hybrid agent approach**:
- **LLM-Enhanced Agent:** Uses OpenAI or Anthropic LLMs for code analysis and generation if API keys are provided.
- **Rule-Based Agent:** Falls back to a deterministic, rule-based agent if LLMs are unavailable or fail.

**Why this approach?**
- **Reliability:** Ensures the system always works, even if LLM APIs are down or unavailable.
- **Flexibility:** Users can opt-in to advanced LLM features or stick with the rule-based agent.
- **Transparency:** The system clearly indicates which agent was used and why in the PR and API responses.

## 🚀 Features

### Core Features
- **FastAPI-based streaming API** with Server-Sent Events
- **Sandboxed repository cloning** for security
- **Coding agent** for analysis and modification
- **Git operations** (commit, push, PR creation)
- **Error handling** and graceful degradation

### Enhanced Features
- **LLM Integration**: OpenAI GPT-4/3.5 and Anthropic Claude support
- **Cloud Sandboxing**: Docker containers and AWS Lambda framework
- **Backward Compatibility**: Original endpoints still work
- **Configuration Management**: Runtime configuration updates
- **Health Monitoring**: Component status reporting

## 📋 Requirements

### Core Dependencies
```bash
pip install -r requirements.txt
```

### Optional Dependencies
For LLM features:
```bash
pip install openai anthropic
```

For cloud sandboxing:
```bash
pip install docker boto3
```

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

## 🚀 Quick Start

### 1. Start the Server

```bash
# Start the enhanced server
python main.py

# Or with uvicorn
uvicorn main:app --reload --port 8000
```

### 2. Test the API

```bash
# Run comprehensive tests
python test.py
```

### 3. Make a Request

#### Basic Usage (Backward Compatible)
```bash
curl -X POST "http://localhost:8000/code/legacy" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/username/repo",
    "prompt": "Add error handling"
  }'
```

#### Enhanced Usage (LLM + Cloud Sandboxing)
```bash
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/username/repo",
    "prompt": "Add error handling to the main function",
    "use_llm": true,
    "llm_provider": "openai",
    "llm_model": "gpt-4",
    "use_cloud_sandbox": true,
    "sandbox_provider": "docker"
  }'
```

**Note:** Use `--no-buffer` flag to see real-time streaming events.

## 📚 API Reference

### Endpoints

#### `POST /code`
Main endpoint with LLM and cloud sandboxing support.

**Request Body:**
```json
{
  "repoUrl": "string",
  "prompt": "string",
  "use_llm": false,
  "llm_provider": "rule_based",
  "llm_model": "gpt-4",
  "use_cloud_sandbox": false,
  "sandbox_provider": "local"
}
```

**Response:** Server-Sent Events stream

#### `POST /code/legacy`
Original endpoint for backward compatibility.

**Request Body:**
```json
{
  "repoUrl": "string",
  "prompt": "string"
}
```

#### `GET /health`
Enhanced health check with component status.

**Response:**
```json
{
  "status": "healthy",
  "service": "tiny-backspace-enhanced",
  "components": {
    "git_operations": "available",
    "coding_agent": "available",
    "llm_agent": "available",
    "cloud_sandbox": "available",
    "openai": "available",
    "anthropic": "not_installed",
    "docker": "available"
  }
}
```

#### `GET /`
API information and feature list.

#### `POST /config`
Update runtime configuration.

## 🔧 Advanced Usage

### LLM Configuration

#### OpenAI
```python
from llm_agent import LLMConfig, LLMCodingAgent

config = LLMConfig(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key",
    max_tokens=4000,
    temperature=0.1
)

agent = LLMCodingAgent(config)
```

#### Anthropic
```python
config = LLMConfig(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    api_key="your-api-key",
    max_tokens=4000,
    temperature=0.1
)
```

### Cloud Sandboxing

#### Docker
```python
from cloud_sandbox import CloudSandboxConfig, CloudSandbox

config = CloudSandboxConfig(
    provider="docker",
    timeout_seconds=300,
    memory_limit_mb=1024,
    cpu_limit=2.0,
    docker_image="python:3.9-slim"
)

sandbox = CloudSandbox(config)
```

## 🧪 Testing

### Run All Tests
```bash
python test.py
```

### Test Specific Features
```bash
# Test LLM features (requires API keys)
export OPENAI_API_KEY="your-key"
python test.py

# Test Docker sandboxing (requires Docker)
python test.py
```

### Manual Testing
```bash
# Start server
python main.py

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

## 🔒 Security & Safety

### Sandboxing Features
- **Isolated Execution**: All code runs in controlled environments
- **Resource Limits**: Memory and CPU constraints prevent abuse
- **Timeout Controls**: Automatic termination of long-running processes
- **Cleanup**: Automatic resource cleanup after execution

### API Security
- **Environment Variables**: Secure API key management
- **Error Handling**: No sensitive information in error messages
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Framework ready for production deployment

## 🛠️ Deployment

### Development
```bash
# Local development
python main.py
```

### Production
```bash
# Docker deployment
docker build -t tiny-backspace-enhanced .
docker run -p 8000:8000 tiny-backspace-enhanced

# Environment variables
export GITHUB_TOKEN="your-token"
export OPENAI_API_KEY="your-key"
export DEFAULT_LLM_PROVIDER="openai"
export DEFAULT_SANDBOX_PROVIDER="docker"
```

### Cloud Deployment
- **AWS Lambda**: Serverless deployment ready
- **Docker Containers**: Container orchestration ready
- **Kubernetes**: Helm charts can be created
- **CI/CD**: GitHub Actions integration ready

## 📊 Project Structure

```
tiny-backspace/
├── main.py              # Enhanced FastAPI application
├── coding_agent.py      # Core coding agent
├── git_operations.py    # Git operations
├── llm_agent.py         # LLM integration
├── cloud_sandbox.py     # Cloud sandboxing
├── config.py            # Configuration management
├── requirements.txt     # Dependencies
├── test.py              # Comprehensive test suite
├── README.md            # This file
└── example_repo/        # Example repository for testing
```

## 🆘 Troubleshooting

### Common Issues

#### LLM API Errors
- Check API key validity
- Verify API quota and limits
- Ensure proper environment variables

#### Docker Sandbox Issues
- Verify Docker is running
- Check Docker permissions
- Ensure sufficient disk space

#### GitHub Token Issues
- Verify token has appropriate permissions
- Check token expiration
- Ensure repository access

### Debug Mode
```bash
export DEBUG=true
python main.py
```

### Logs
Check application logs for detailed error information and debugging.

