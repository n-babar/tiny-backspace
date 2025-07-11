"""
Configuration management for Tiny Backspace Enhanced

This module provides configuration management for LLM and cloud sandboxing features.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from llm_agent import LLMConfig
from cloud_sandbox import CloudSandboxConfig

@dataclass
class AppConfig:
    """Main application configuration"""
    # API settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # GitHub settings
    github_token: Optional[str] = None
    
    # LLM settings
    default_llm_provider: str = "rule_based"
    default_llm_model: str = "gpt-4"
    
    # Sandbox settings
    default_sandbox_provider: str = "local"
    
    # Security settings
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 300  # 5 minutes
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            github_token=os.getenv("GITHUB_TOKEN"),
            default_llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "rule_based"),
            default_llm_model=os.getenv("DEFAULT_LLM_MODEL", "gpt-4"),
            default_sandbox_provider=os.getenv("DEFAULT_SANDBOX_PROVIDER", "local"),
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", "10485760")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "300"))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)

class ConfigManager:
    """Configuration manager for the application"""
    
    def __init__(self):
        self.app_config = AppConfig.from_env()
        self.llm_configs: Dict[str, LLMConfig] = {}
        self.sandbox_configs: Dict[str, CloudSandboxConfig] = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default configurations"""
        # Default LLM configurations
        self.llm_configs["openai"] = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY") or "",
            max_tokens=4000,
            temperature=0.1
        )
        
        self.llm_configs["anthropic"] = LLMConfig(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            api_key=os.getenv("ANTHROPIC_API_KEY") or "",
            max_tokens=4000,
            temperature=0.1
        )
        
        self.llm_configs["rule_based"] = LLMConfig(
            provider="rule_based",
            model="rule_based",
            max_tokens=0,
            temperature=0.0
        )
        
        # Default sandbox configurations
        self.sandbox_configs["local"] = CloudSandboxConfig(
            provider="local",
            timeout_seconds=300,
            memory_limit_mb=512,
            cpu_limit=1.0
        )
        
        self.sandbox_configs["docker"] = CloudSandboxConfig(
            provider="docker",
            timeout_seconds=300,
            memory_limit_mb=1024,
            cpu_limit=2.0,
            docker_image="python:3.9-slim"
        )
        
        self.sandbox_configs["aws"] = CloudSandboxConfig(
            provider="aws",
            timeout_seconds=300,
            memory_limit_mb=512,
            cpu_limit=1.0,
            aws_region="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    def get_llm_config(self, provider: str = None) -> LLMConfig:
        """Get LLM configuration for the specified provider"""
        provider = provider or self.app_config.default_llm_provider
        return self.llm_configs.get(provider, self.llm_configs["rule_based"])
    
    def get_sandbox_config(self, provider: str = None) -> CloudSandboxConfig:
        """Get sandbox configuration for the specified provider"""
        provider = provider or self.app_config.default_sandbox_provider
        return self.sandbox_configs.get(provider, self.sandbox_configs["local"])
    
    def update_llm_config(self, provider: str, config: LLMConfig):
        """Update LLM configuration for a provider"""
        self.llm_configs[provider] = config
    
    def update_sandbox_config(self, provider: str, config: CloudSandboxConfig):
        """Update sandbox configuration for a provider"""
        self.sandbox_configs[provider] = config
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available providers"""
        return {
            "llm": {
                "openai": {
                    "available": bool(os.getenv("OPENAI_API_KEY")),
                    "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
                },
                "anthropic": {
                    "available": bool(os.getenv("ANTHROPIC_API_KEY")),
                    "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
                },
                "rule_based": {
                    "available": True,
                    "models": ["rule_based"]
                }
            },
            "sandbox": {
                "local": {
                    "available": True,
                    "description": "Local file system sandboxing"
                },
                "docker": {
                    "available": self._check_docker_availability(),
                    "description": "Docker container sandboxing"
                },
                "aws": {
                    "available": bool(os.getenv("AWS_ACCESS_KEY_ID")),
                    "description": "AWS Lambda sandboxing"
                }
            }
        }
    
    def _check_docker_availability(self) -> bool:
        """Check if Docker is available"""
        try:
            import docker
            docker.from_env().ping()
            return True
        except Exception:
            return False

# Global configuration instance
config_manager = ConfigManager() 