"""
Tiny Backspace - Enhanced FastAPI Application

A minimal coding agent that creates GitHub PRs from prompts with LLM integration 
and cloud sandboxing support.
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import asyncio
import json
import os
import logging
from typing import Optional
from git_operations import GitOperations
from coding_agent import CodingAgent
from llm_agent import LLMCodingAgent, LLMConfig
from cloud_sandbox import CloudSandbox, CloudSandboxConfig
from dataclasses import asdict

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tiny Backspace",
    description="A minimal coding agent that creates GitHub PRs from prompts with LLM and cloud sandboxing support",
    version="2.0.0"
)

# Set up OpenTelemetry tracing
resource = Resource(attributes={"service.name": "tiny-backspace"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

class CodeRequest(BaseModel):
    repoUrl: str = Field(..., description="GitHub repository URL")
    prompt: str = Field(..., description="Coding prompt/instruction")
    use_llm: bool = Field(False, description="Use LLM for code analysis and generation")
    llm_provider: str = Field("rule_based", description="LLM provider: openai, anthropic, or rule_based")
    llm_model: str = Field("gpt-4", description="LLM model name")
    use_cloud_sandbox: bool = Field(False, description="Use cloud sandboxing")
    sandbox_provider: str = Field("local", description="Sandbox provider: local, docker, aws, gcp")

class ConfigRequest(BaseModel):
    """Configuration for LLM and sandboxing"""
    llm_config: Optional[LLMConfig] = None
    sandbox_config: Optional[CloudSandboxConfig] = None

@app.get("/")
async def root():
    """Root endpoint with enhanced API information"""
    return {
        "name": "Tiny Backspace",
        "description": "A minimal coding agent that creates GitHub PRs from prompts with LLM and cloud sandboxing support",
        "version": "2.0.0",
        "features": {
            "llm_support": "OpenAI, Anthropic, and rule-based coding agents",
            "cloud_sandboxing": "Docker, AWS, GCP, and local sandboxing",
            "streaming_api": "Real-time progress updates via Server-Sent Events"
        },
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/code": "POST - Create PR from coding prompt",
            "/config": "POST - Configure LLM and sandboxing settings"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with component status"""
    status = {
        "status": "healthy",
        "service": "tiny-backspace",
        "components": {
            "git_operations": "available",
            "coding_agent": "available",
            "llm_agent": "available",
            "cloud_sandbox": "available"
        }
    }
    
    # Check LLM availability
    try:
        import openai
        status["components"]["openai"] = "available"
    except ImportError:
        status["components"]["openai"] = "not_installed"
    
    try:
        import anthropic
        status["components"]["anthropic"] = "available"
    except ImportError:
        status["components"]["anthropic"] = "not_installed"
    
    # Check Docker availability
    try:
        import docker
        docker.from_env().ping()
        status["components"]["docker"] = "available"
    except Exception:
        status["components"]["docker"] = "not_available"
    
    return status

@app.post("/config")
async def configure_system(request: ConfigRequest):
    """Configure LLM and sandboxing settings"""
    config = {
        "llm_config": asdict(request.llm_config) if request.llm_config else None,
        "sandbox_config": asdict(request.sandbox_config) if request.sandbox_config else None
    }
    
    # Store configuration (in a real app, you'd persist this)
    app.state.config = config
    
    return {
        "message": "Configuration updated",
        "config": config
    }

async def enhanced_event_generator(repo_url: str, prompt: str, use_llm: bool = False, 
                                 llm_provider: str = "openai", llm_model: str = "gpt-4",
                                 use_cloud_sandbox: bool = False, sandbox_provider: str = "local"):
    """Enhanced event generator with LLM and cloud sandboxing support"""
    git_ops = None
    agent = None
    sandbox = None
    
    try:
        # Get GitHub token from environment
        github_token = os.getenv('GITHUB_TOKEN')
        
        # Step 1: Initialize components
        yield f"data: {json.dumps({'type': 'info', 'message': 'Received request', 'repoUrl': repo_url, 'prompt': prompt})}\n\n"
        await asyncio.sleep(0.5)
        
        # Initialize cloud sandbox if requested
        if use_cloud_sandbox:
            yield f"data: {json.dumps({'type': 'progress', 'message': f'Initializing {sandbox_provider} sandbox...'})}\n\n"
            try:
                sandbox_config = CloudSandboxConfig(provider=sandbox_provider)
                sandbox = CloudSandbox(sandbox_config)
                yield f"data: {json.dumps({'type': 'success', 'message': f'{sandbox_provider} sandbox initialized'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to initialize sandbox: {str(e)}'})}\n\n"
                return
            await asyncio.sleep(0.5)
        
        # Step 2: Clone repository
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Cloning repository...'})}\n\n"
        
        if sandbox:
            # Use cloud sandbox for cloning
            try:
                sandbox_dir, clone_result = sandbox.clone_repository(repo_url)
                if not clone_result.get("success"):
                    raise Exception(f"Failed to clone repository: {clone_result.get('error')}")
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to clone repository in sandbox: {str(e)}'})}\n\n"
                return
        else:
            # Use local git operations
            git_ops = GitOperations(github_token)
            sandbox_dir = git_ops.clone_repo(repo_url)
        
        yield f"data: {json.dumps({'type': 'success', 'message': f'Repository cloned to {sandbox_dir}'})}\n\n"
        await asyncio.sleep(0.5)
        
        # Step 3: Initialize coding agent
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Initializing coding agent...'})}\n\n"
        
        if use_llm:
            # Use LLM-enhanced agent
            api_key = os.getenv(f"{llm_provider.upper()}_API_KEY")
            if not api_key:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Missing API key for {llm_provider}. Set {llm_provider.upper()}_API_KEY environment variable.'})}\n\n"
                return
            llm_config = LLMConfig(
                provider=llm_provider,
                model=llm_model,
                api_key=api_key
            )
            agent = LLMCodingAgent(llm_config)
            yield f"data: {json.dumps({'type': 'info', 'message': f'LLM agent initialized with {llm_provider}/{llm_model}'})}\n\n"
        else:
            # Use rule-based agent
            agent = CodingAgent(sandbox_dir)
            yield f"data: {json.dumps({'type': 'info', 'message': 'Rule-based agent initialized'})}\n\n"
        
        await asyncio.sleep(0.5)
        
        # Step 4: Analyze code
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Analyzing codebase...'})}\n\n"
        if use_llm and isinstance(agent, LLMCodingAgent):
            analysis = agent.analyze_code(sandbox_dir, prompt)
            files_to_modify = analysis.get('files_to_modify', [])
            yield f"data: {json.dumps({'type': 'info', 'message': f'LLM analysis complete. Files to modify: {len(files_to_modify)}'})}\n\n"
        elif not use_llm and isinstance(agent, CodingAgent):
            analysis = agent.analyze_repository()
            file_count = len(analysis["files"])
            yield f"data: {json.dumps({'type': 'info', 'message': f'Repository analysis complete. Found {file_count} files.'})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Agent type mismatch for analysis.'})}\n\n"
            return
        await asyncio.sleep(0.5)
        
        # Step 5: Generate changes
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Generating changes...'})}\n\n"
        if use_llm and isinstance(agent, LLMCodingAgent):
            changes = agent.modify_code(sandbox_dir, analysis, prompt)
            applied_changes = []
            for change in changes:
                file_path = change.get('file')
                new_content = change.get('new_content')
                description = change.get('description', '')
                if file_path and new_content is not None:
                    with open(os.path.join(sandbox_dir, file_path), 'w') as f:
                        f.write(new_content)
                    applied_changes.append(f"Modified {file_path}: {description}")
        elif not use_llm and isinstance(agent, CodingAgent):
            changes = agent.generate_changes(prompt)
            applied_changes = agent.apply_changes(changes) if changes else []
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Agent type mismatch for code modification.'})}\n\n"
            return
        
        yield f"data: {json.dumps({'type': 'info', 'message': f'Generated {len(applied_changes)} changes'})}\n\n"
        await asyncio.sleep(0.5)
        
        # Step 6: Apply changes
        if applied_changes:
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Changes applied successfully'})}\n\n"
            for change in applied_changes:
                yield f"data: {json.dumps({'type': 'change', 'message': change})}\n\n"
                await asyncio.sleep(0.2)
        else:
            yield f"data: {json.dumps({'type': 'warning', 'message': 'No changes generated for this prompt'})}\n\n"
        
        # Step 7: Git operations
        if applied_changes:
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Creating git branch...'})}\n\n"
            
            if not git_ops:
                git_ops = GitOperations(github_token)
            
            branch_name = f"feature/auto-{prompt.lower().replace(' ', '-')[:20]}"
            git_ops.create_branch(branch_name)
            yield f"data: {json.dumps({'type': 'success', 'message': f'Created branch: {branch_name}'})}\n\n"
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Committing changes...'})}\n\n"
            commit_message = f"Auto-generated changes: {prompt}"
            git_ops.commit_changes(commit_message)
            yield f"data: {json.dumps({'type': 'success', 'message': 'Changes committed'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Step 8: Push and create PR (if token available)
            if github_token:
                yield f"data: {json.dumps({'type': 'progress', 'message': 'Pushing branch to remote...'})}\n\n"
                try:
                    git_ops.push_branch(branch_name)
                    yield f"data: {json.dumps({'type': 'success', 'message': 'Branch pushed to remote'})}\n\n"
                    await asyncio.sleep(0.5)
                    
                    yield f"data: {json.dumps({'type': 'progress', 'message': 'Creating pull request...'})}\n\n"
                    pr_title = f"Auto-generated: {prompt}"
                    # Add analysis/approach to PR body if available
                    analysis_section = ""
                    if 'llm_analysis' in analysis and analysis['llm_analysis']:
                        analysis_section += f"\n\n### Analysis/Reasoning (from agent):\n{analysis['llm_analysis']}"
                    if 'approach' in analysis and analysis['approach']:
                        analysis_section += f"\n\n### Approach:\n{analysis['approach']}"
                    pr_body = f"""
## Auto-generated changes

This PR was automatically generated based on the prompt: \"{prompt}\"

### Agent used:
- {'LLM' if use_llm else 'Rule-based'} agent ({llm_provider}/{llm_model if use_llm else 'N/A'})
- {'Cloud' if use_cloud_sandbox else 'Local'} sandboxing ({sandbox_provider})
{analysis_section}

### Changes made:
{chr(10).join([f"- {change}" for change in applied_changes])}

### Generated by Tiny Backspace
                    """
                    
                    pr_url = git_ops.create_pull_request(repo_url, branch_name, pr_title, pr_body)
                    yield f"data: {json.dumps({'type': 'success', 'message': 'Pull request created!', 'pr_url': pr_url})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to create PR: {str(e)}'})}\n\n"
                    pr_url = None
            else:
                yield f"data: {json.dumps({'type': 'warning', 'message': 'No GitHub token provided. Skipping PR creation.'})}\n\n"
                pr_url = None
        
        # Step 9: Final result
        if applied_changes and github_token and pr_url:
            yield f"data: {json.dumps({'type': 'done', 'message': 'Process completed successfully!', 'pr_url': pr_url, 'changes': applied_changes})}\n\n"
        elif applied_changes:
            yield f"data: {json.dumps({'type': 'done', 'message': 'Changes applied locally. Set GITHUB_TOKEN to create PR.', 'changes': applied_changes})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'done', 'message': 'No changes were made for this prompt.'})}\n\n"
            
    except Exception as e:
        logger.error(f"Error in enhanced event generator: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"
    finally:
        # Cleanup
        if git_ops:
            git_ops.cleanup()
        if sandbox and 'sandbox_dir' in locals() and sandbox_dir:
            sandbox.cleanup(sandbox_dir)

@app.post("/code")
async def code_endpoint(request: Request, body: CodeRequest):
    """Enhanced code endpoint with LLM and cloud sandboxing support"""
    async def streamer():
        async for event in enhanced_event_generator(
            body.repoUrl, 
            body.prompt,
            body.use_llm,
            body.llm_provider,
            body.llm_model,
            body.use_cloud_sandbox,
            body.sandbox_provider
        ):
            yield event
            await asyncio.sleep(0.1)
    
    return StreamingResponse(streamer(), media_type="text/event-stream")

# Backward compatibility endpoint
@app.post("/code/legacy")
async def legacy_code_endpoint(request: Request, body: CodeRequest):
    """Legacy endpoint for backward compatibility"""
    async def streamer():
        async for event in enhanced_event_generator(
            body.repoUrl, 
            body.prompt,
            use_llm=False,
            llm_provider="rule_based",
            llm_model="gpt-4",
            use_cloud_sandbox=False,
            sandbox_provider="local"
        ):
            yield event
            await asyncio.sleep(0.1)
    
    return StreamingResponse(streamer(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
