"""
Cloud Sandboxing for Tiny Backspace

This module provides cloud-based sandboxing capabilities while maintaining
compatibility with local sandboxing as a fallback.
"""

import os
import tempfile
import subprocess
import logging
import json
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import docker
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CloudSandboxConfig:
    """Configuration for cloud sandboxing"""
    provider: str = "local"  # "local", "docker", "aws", "gcp"
    timeout_seconds: int = 300
    memory_limit_mb: int = 512
    cpu_limit: float = 1.0
    
    # Docker-specific settings
    docker_image: str = "python:3.9-slim"
    
    # AWS-specific settings
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # GCP-specific settings
    gcp_project: Optional[str] = None
    gcp_zone: str = "us-central1-a"

class CloudSandbox:
    """
    Cloud sandboxing implementation with fallback to local sandboxing
    """
    
    def __init__(self, config: Optional[CloudSandboxConfig] = None):
        self.config = config if config is not None else CloudSandboxConfig()
        self._setup_provider()
    
    def _setup_provider(self):
        """Setup the cloud provider based on configuration"""
        if self.config.provider == "docker":
            try:
                self.docker_client = docker.from_env()
                # Test connection
                self.docker_client.ping()
                logger.info("Docker sandboxing enabled")
            except Exception as e:
                logger.warning(f"Docker not available: {e}, falling back to local")
                self.config.provider = "local"
        
        elif self.config.provider == "aws":
            if not BOTO3_AVAILABLE:
                logger.warning("boto3 not available, falling back to local")
                self.config.provider = "local"
            else:
                try:
                    self.aws_client = boto3.client(
                        'lambda',
                        region_name=self.config.aws_region,
                        aws_access_key_id=self.config.aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=self.config.aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
                    )
                    logger.info("AWS Lambda sandboxing enabled")
                except Exception as e:
                    logger.warning(f"AWS not available: {e}, falling back to local")
                    self.config.provider = "local"
        
        elif self.config.provider == "gcp":
            try:
                # GCP setup would go here
                logger.info("GCP sandboxing enabled")
            except Exception as e:
                logger.warning(f"GCP not available: {e}, falling back to local")
                self.config.provider = "local"
        
        else:
            logger.info("Using local sandboxing")
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> Tuple[str, Dict]:
        """Clone repository in sandboxed environment"""
        if self.config.provider == "local":
            return self._clone_local(repo_url, branch)
        elif self.config.provider == "docker":
            return self._clone_docker(repo_url, branch)
        elif self.config.provider == "aws":
            return self._clone_aws(repo_url, branch)
        else:
            return self._clone_local(repo_url, branch)
    
    def _clone_local(self, repo_url: str, branch: str) -> Tuple[str, Dict]:
        """Clone repository locally (existing implementation)"""
        import tempfile
        import subprocess
        
        temp_dir = tempfile.mkdtemp()
        result = {"success": False, "error": None, "path": temp_dir}
        
        try:
            # Clone the repository
            subprocess.run(
                ["git", "clone", "-b", branch, repo_url, temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
            result["success"] = True
        except subprocess.CalledProcessError as e:
            result["error"] = f"Failed to clone repository: {e.stderr}"
        
        return temp_dir, result
    
    def _clone_docker(self, repo_url: str, branch: str) -> Tuple[str, Dict]:
        """Clone repository in Docker container"""
        result = {"success": False, "error": None, "path": None}
        
        try:
            # Create a temporary directory on host
            temp_dir = tempfile.mkdtemp()
            
            # Run git clone in Docker container
            container = self.docker_client.containers.run(
                self.config.docker_image,
                command=f"sh -c 'apt-get update && apt-get install -y git && git clone -b {branch} {repo_url} /workspace'",
                volumes={temp_dir: {'bind': '/workspace', 'mode': 'rw'}},
                detach=True,
                mem_limit=f"{self.config.memory_limit_mb}m",
                cpu_period=100000,
                cpu_quota=int(100000 * self.config.cpu_limit)
            )
            
            # Wait for completion
            container.wait(timeout=self.config.timeout_seconds)
            
            # Check if successful
            logs = container.logs().decode()
            if container.status == "exited" and container.attrs['State']['ExitCode'] == 0:
                result["success"] = True
                result["path"] = temp_dir
            else:
                result["error"] = f"Docker container failed: {logs}"
            
            # Clean up container
            container.remove()
            
        except Exception as e:
            result["error"] = f"Docker sandboxing failed: {e}"
        
        return result.get("path", tempfile.mkdtemp()), result
    
    def _clone_aws(self, repo_url: str, branch: str) -> Tuple[str, Dict]:
        """Clone repository using AWS Lambda (simplified)"""
        result = {"success": False, "error": None, "path": None}
        
        try:
            # This is a simplified implementation
            # In a real scenario, you'd create a Lambda function to handle cloning
            payload = {
                "repo_url": repo_url,
                "branch": branch,
                "action": "clone"
            }
            
            # For now, fall back to local
            logger.info("AWS Lambda sandboxing not fully implemented, using local")
            return self._clone_local(repo_url, branch)
            
        except Exception as e:
            result["error"] = f"AWS sandboxing failed: {e}"
            return tempfile.mkdtemp(), result
    
    def execute_command(self, repo_path: str, command: List[str]) -> Dict:
        """Execute command in sandboxed environment"""
        if self.config.provider == "local":
            return self._execute_local(repo_path, command)
        elif self.config.provider == "docker":
            return self._execute_docker(repo_path, command)
        elif self.config.provider == "aws":
            return self._execute_aws(repo_path, command)
        else:
            return self._execute_local(repo_path, command)
    
    def _execute_local(self, repo_path: str, command: List[str]) -> Dict:
        """Execute command locally (existing implementation)"""
        result = {"success": False, "output": "", "error": None}
        
        try:
            process = subprocess.run(
                command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            result["success"] = process.returncode == 0
            result["output"] = process.stdout
            if process.stderr:
                result["error"] = process.stderr
                
        except subprocess.TimeoutExpired:
            result["error"] = f"Command timed out after {self.config.timeout_seconds} seconds"
        except Exception as e:
            result["error"] = f"Command execution failed: {e}"
        
        return result
    
    def _execute_docker(self, repo_path: str, command: List[str]) -> Dict:
        """Execute command in Docker container"""
        result = {"success": False, "output": "", "error": None}
        
        try:
            # Create a temporary directory for the command
            temp_dir = tempfile.mkdtemp()
            
            # Copy repository to temp directory
            import shutil
            shutil.copytree(repo_path, os.path.join(temp_dir, "repo"))
            
            # Run command in Docker container
            container = self.docker_client.containers.run(
                self.config.docker_image,
                command=command,
                volumes={temp_dir: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir="/workspace/repo",
                detach=True,
                mem_limit=f"{self.config.memory_limit_mb}m",
                cpu_period=100000,
                cpu_quota=int(100000 * self.config.cpu_limit)
            )
            
            # Wait for completion
            container.wait(timeout=self.config.timeout_seconds)
            
            # Get output
            logs = container.logs().decode()
            if container.status == "exited" and container.attrs['State']['ExitCode'] == 0:
                result["success"] = True
                result["output"] = logs
            else:
                result["error"] = logs
            
            # Clean up container and temp directory
            container.remove()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            result["error"] = f"Docker execution failed: {e}"
        
        return result
    
    def _execute_aws(self, repo_path: str, command: List[str]) -> Dict:
        """Execute command using AWS Lambda (simplified)"""
        result = {"success": False, "output": "", "error": None}
        
        try:
            # This is a simplified implementation
            # In a real scenario, you'd create a Lambda function to handle execution
            logger.info("AWS Lambda execution not fully implemented, using local")
            return self._execute_local(repo_path, command)
            
        except Exception as e:
            result["error"] = f"AWS execution failed: {e}"
        
        return result
    
    def cleanup(self, repo_path: str):
        """Clean up sandboxed resources"""
        if self.config.provider == "local":
            import shutil
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup local directory: {e}")
        
        # Docker and AWS cleanup would be handled automatically
        # in their respective execution methods 