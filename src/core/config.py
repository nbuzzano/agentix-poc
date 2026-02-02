"""Configuration management for Agentix"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration for Agentix pipeline"""

    # Paths
    DATA_INPUT_PATH: str = os.getenv("DATA_INPUT_PATH", "./data/input")
    DATA_OUTPUT_PATH: str = os.getenv("DATA_OUTPUT_PATH", "./data/output")
    LOGS_PATH: str = os.getenv("LOGS_PATH", "./logs")
    SYNTHETIC_DATA_PATH: str = os.getenv("SYNTHETIC_DATA_PATH", "./data/synthetic")

    # API
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    MODEL: str = os.getenv("MODEL", "claude-3-5-sonnet-20241022")

    # Pipeline
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TRANSLATION_STRATEGY: str = os.getenv("TRANSLATION_STRATEGY", "basic")
    
    # Validation
    VALIDATE_SYNTAX: bool = os.getenv("VALIDATE_SYNTAX", "true").lower() == "true"
    VALIDATE_WITH_DATA: bool = os.getenv("VALIDATE_WITH_DATA", "true").lower() == "true"
    SYNTHETIC_DATA_ROWS: int = int(os.getenv("SYNTHETIC_DATA_ROWS", "100"))

    @classmethod
    def ensure_paths(cls) -> None:
        """Ensure all required paths exist"""
        for path in [cls.DATA_INPUT_PATH, cls.DATA_OUTPUT_PATH, 
                     cls.LOGS_PATH, cls.SYNTHETIC_DATA_PATH]:
            Path(path).mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set")
        return True
