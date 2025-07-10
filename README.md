# Tiny Backspace

A minimal coding agent that creates GitHub PRs from prompts using FastAPI and Server-Sent Events.

## Overview

Tiny Backspace is a streaming API that takes a GitHub repository URL and a coding prompt, then automatically:
1. Clones the repository into a sandbox
2. Analyzes the codebase
3. Generates and applies code changes based on the prompt
4. Creates a git branch, commits changes, and pushes to remote
5. Creates a pull request with the changes

## Features

- **Streaming API**: Real-time updates via Server-Sent Events
- **Sandboxed Environment**: Safe repository cloning and modification
- **Git Integration**: Automatic branch creation, commits, and PR generation
- **Simple Agent**: Rule-based code modifications (easily extensible to use LLMs)

## Quick Start

### Prerequisites

- Python 3.8+
- Git
- GitHub CLI (optional, for PR creation)

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd tiny-backspace
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up GitHub token (optional, for PR creation):
```bash
export GITHUB_TOKEN=your_github_token_here
```

### Running Locally

1. Start the server:
```bash
python3 -m uvicorn main:app --port 8000
```

2. Test the endpoint:
```bash
python3 test_full_stream.py
```

### API Usage

**Endpoint**: `POST /code`

**Request Body**:
```json
{
  "repoUrl": "https://github.com/example/simple-api",
  "prompt": "Add input validation to all POST endpoints and return proper error messages"
}
```

**Response**: Server-Sent Events stream with real-time updates

### Example Response Stream

```
ℹ️  INFO: Received request
⏳ PROGRESS: Cloning repository...
✅ SUCCESS: Repository cloned to /tmp/tiny_backspace_xxx
⏳ PROGRESS: Initializing coding agent...
ℹ️  INFO: Repository analysis complete. Found 5 files.
⏳ PROGRESS: Analyzing prompt and generating changes...
ℹ️  INFO: Generated 2 changes
⏳ PROGRESS: Applying changes to repository...
📝 CHANGE: Edited app.py: Added type hints to app.py
📝 CHANGE: Created app_test.py: Created test file app_test.py
⏳ PROGRESS: Creating git branch...
✅ SUCCESS: Created branch: feature/auto-add-input-valid
⏳ PROGRESS: Committing changes...
✅ SUCCESS: Changes committed
⏳ PROGRESS: Pushing branch to remote...
✅ SUCCESS: Branch pushed to remote
⏳ PROGRESS: Creating pull request...
✅ SUCCESS: Pull request created!
🎉 DONE: Process completed successfully!
🔗 PR URL: https://github.com/example/simple-api/pull/123
```

## Architecture

### Components

1. **FastAPI Server** (`main.py`): Handles HTTP requests and streams events
2. **Git Operations** (`git_operations.py`): Manages repository cloning, branching, and PR creation
3. **Coding Agent** (`coding_agent.py`): Analyzes codebase and generates changes
4. **Sandbox Environment**: Temporary directory for safe code modification

### Flow

1. **Request Received**: API accepts repo URL and coding prompt
2. **Repository Cloning**: Git operations clone the repo to a temporary sandbox
3. **Code Analysis**: Agent analyzes repository structure and identifies files
4. **Change Generation**: Agent generates code changes based on the prompt
5. **Change Application**: Changes are applied to files in the sandbox
6. **Git Operations**: New branch created, changes committed and pushed
7. **PR Creation**: Pull request created with descriptive title and body
8. **Cleanup**: Temporary sandbox directory removed

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token for PR creation (optional)

### Customization

The coding agent in `coding_agent.py` can be easily extended to:
- Use LLM APIs (OpenAI, Claude, etc.) for more sophisticated code generation
- Add more rule-based transformations
- Integrate with code analysis tools
- Add support for different programming languages

## Testing

### Unit Tests
```bash
python3 simple_test.py
```

### Integration Tests
```bash
python3 test_full_stream.py
```

### Manual Testing
```bash
curl -X POST http://127.0.0.1:8000/code \
  -H "Content-Type: application/json" \
  -d '{"repoUrl": "https://github.com/example/repo", "prompt": "Add error handling"}'
```

## Deployment

### Local Development
```bash
python3 -m uvicorn main:app --reload --port 8000
```

### Production
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

