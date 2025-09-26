"""Configuration management for the agent demo."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for the AI agent."""
    
    # API Configuration
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model_name: str = "deepseek-chat"
    
    # Agent Behavior
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout_seconds: int = 60
    
    # Safety Settings
    confirm_destructive_operations: bool = True
    max_file_size_mb: int = 10
    allowed_file_extensions: list = None
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.py', '.txt', '.md', '.json', '.yaml', '.yml']


def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    
    # Load .env file if it exists
    load_env()
    
    # Get API key (try both DeepSeek and OpenAI)
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing API key. Please set DEEPSEEK_API_KEY or OPENAI_API_KEY in .env file."
        )
    
    # Get base URL
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # Get model name
    model_name = os.getenv("MODEL_NAME", "deepseek-chat")
    
    # Get agent behavior settings
    max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "60"))
    
    # Get safety settings
    confirm_destructive = os.getenv("CONFIRM_DESTRUCTIVE", "true").lower() == "true"
    max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    return AgentConfig(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        confirm_destructive_operations=confirm_destructive,
        max_file_size_mb=max_file_size,
    )


def load_env() -> None:
    """Load .env from common locations (cwd, script dir, parents)."""
    candidates: list[Path] = []
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    
    # Prefer closer files first
    candidates.extend([cwd / ".env", script_dir / ".env"])
    candidates.extend(p / ".env" for p in script_dir.parents)
    candidates.extend(p / ".env" for p in cwd.parents)

    loaded_any = False
    
    # Try python-dotenv first if available
    try:
        from dotenv import load_dotenv as _load
        for env_path in candidates:
            if env_path.is_file():
                _load(env_path)
                loaded_any = True
                break
    except Exception:
        pass

    if loaded_any:
        return

    # Fallback: simple parser
    for env_path in candidates:
        try:
            if not env_path.is_file():
                continue
            with env_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            break
        except Exception:
            continue


def validate_config(config: AgentConfig) -> None:
    """Validate configuration settings."""
    
    if not config.api_key:
        raise ValueError("API key is required")
    
    if config.max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    
    if not 0 <= config.temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")
    
    if config.timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    
    if config.max_file_size_mb <= 0:
        raise ValueError("max_file_size_mb must be positive")