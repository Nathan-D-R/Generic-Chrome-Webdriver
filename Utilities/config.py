"""
Configuration Loader
====================
Loads configuration from .env file with sensible defaults.

This module provides a centralized way to load and access configuration
settings from the .env file.
"""

import os
from typing import Optional
from dotenv import load_dotenv


# Load .env file
load_dotenv()


class Config:
    """Configuration settings loaded from .env file."""
    
    # Chrome Driver Settings
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    WINDOW_SIZE: str = os.getenv("WINDOW_SIZE", "1920x1080")
    STEALTH_MODE: bool = os.getenv("STEALTH_MODE", "false").lower() == "true"
    USE_OPAQUE_DRIVER: bool = os.getenv("USE_OPAQUE_DRIVER", "false").lower() == "true"
    
    # User Agent Settings
    USER_AGENT: Optional[str] = os.getenv("USER_AGENT", None)
    USER_AGENT_PLATFORM: Optional[str] = os.getenv("USER_AGENT_PLATFORM", "random")
    
    # Directory Settings
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", os.path.abspath("./Outputs/Downloads"))
    PROFILE_DIR: Optional[str] = os.getenv("PROFILE_DIR", None)
    LOG_FILE: str = os.getenv("LOG_FILE", "webdriver.log")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Microsoft Login Credentials
    MICROSOFT_USERNAME: Optional[str] = os.getenv("MICROSOFT_USERNAME")
    MICROSOFT_PASSWORD: Optional[str] = os.getenv("MICROSOFT_PASSWORD")
    STAY_SIGNED_IN: bool = os.getenv("STAY_SIGNED_IN", "false").lower() == "true"
    
    # Concurrency Settings
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "3"))
    
    @classmethod
    def get_profile_dir(cls) -> Optional[str]:
        """
        Get Chrome profile directory with expansion of environment variables.
        
        Returns:
            Expanded profile directory path or None
        """
        if cls.PROFILE_DIR:
            return os.path.expanduser(cls.PROFILE_DIR)
        return None
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate configuration and return list of warnings/errors.
        
        Returns:
            List of validation messages (empty if all valid)
        """
        issues = []
        
        if not cls.MICROSOFT_USERNAME:
            issues.append("MICROSOFT_USERNAME not set in .env")
        
        if not cls.MICROSOFT_PASSWORD:
            issues.append("MICROSOFT_PASSWORD not set in .env")
        
        return issues


def print_config():
    """Print current configuration (for debugging)."""
    print("=" * 50)
    print("CONFIGURATION")
    print("=" * 50)
    print(f"Headless: {Config.HEADLESS}")
    print(f"Stealth Mode: {Config.STEALTH_MODE}")
    print(f"Opaque Driver: {Config.USE_OPAQUE_DRIVER}")
    print(f"User Agent: {Config.USER_AGENT or 'Auto-generated'}")
    print(f"User Agent Platform: {Config.USER_AGENT_PLATFORM}")
    print(f"Implicit Wait: {Config.IMPLICIT_WAIT}s")
    print(f"Window Size: {Config.WINDOW_SIZE}")
    print(f"Download Dir: {Config.DOWNLOAD_DIR}")
    print(f"Profile Dir: {Config.get_profile_dir() or 'None'}")
    print(f"Log File: {Config.LOG_FILE}")
    print(f"Log Level: {Config.LOG_LEVEL}")
    print(f"Max Workers: {Config.MAX_WORKERS}")
    print(f"Microsoft Username: {'***' if Config.MICROSOFT_USERNAME else 'Not set'}")
    print(f"Microsoft Password: {'***' if Config.MICROSOFT_PASSWORD else 'Not set'}")
    print(f"Stay Signed In: {Config.STAY_SIGNED_IN}")
    print("=" * 50)
    
    # Show validation warnings
    issues = Config.validate()
    if issues:
        print("\nWARNINGS:")
        for issue in issues:
            print(f"  - {issue}")
        print()
