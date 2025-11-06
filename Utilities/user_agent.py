"""
User Agent Factory
==================
Generates realistic user agent strings for Chrome WebDriver.

This module provides functions to generate and rotate user agent strings
to avoid detection and fingerprinting.
"""

import random
import logging
from typing import Optional, Literal
from datetime import datetime


logger = logging.getLogger(__name__)


# Operating System templates
OS_TEMPLATES = {
    "windows": [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 11.0; Win64; x64",
    ],
    "mac": [
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 11_6_0",
        "Macintosh; Intel Mac OS X 12_0_0",
        "Macintosh; Intel Mac OS X 13_0_0",
        "Macintosh; Intel Mac OS X 14_0_0",
    ],
    "linux": [
        "X11; Linux x86_64",
        "X11; Ubuntu; Linux x86_64",
    ]
}

# Chrome versions (recent stable versions)
CHROME_VERSIONS = [
    "119.0.0.0",
    "120.0.0.0",
    "121.0.0.0",
    "122.0.0.0",
]

# Safari versions (for Mac)
SAFARI_VERSIONS = [
    "537.36",
]

# WebKit versions
WEBKIT_VERSIONS = [
    "537.36",
]


class UserAgentFactory:
    """Factory for generating realistic user agent strings."""
    
    def __init__(self, platform: Optional[Literal["windows", "mac", "linux", "random"]] = "random"):
        """
        Initialize the user agent factory.
        
        Args:
            platform: Target platform ("windows", "mac", "linux", or "random")
        """
        self.platform = platform
        self._last_ua = None
        
    def generate(
        self,
        chrome_version: Optional[str] = None,
        os_version: Optional[str] = None
    ) -> str:
        """
        Generate a realistic Chrome user agent string.
        
        Args:
            chrome_version: Specific Chrome version (e.g., "120.0.0.0"). Random if None
            os_version: Specific OS version string. Random if None
            
        Returns:
            str: Complete user agent string
            
        Example:
            >>> factory = UserAgentFactory(platform="windows")
            >>> ua = factory.generate()
            >>> print(ua)
            Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...
        """
        # Determine platform
        platform = self.platform
        if platform == "random" or platform is None:
            platform = random.choice(["windows", "mac", "linux"])
        
        # Select OS version
        if os_version is None:
            os_version = random.choice(OS_TEMPLATES[platform])
        
        # Select Chrome version
        if chrome_version is None:
            chrome_version = random.choice(CHROME_VERSIONS)
        
        # Select WebKit version
        webkit_version = random.choice(WEBKIT_VERSIONS)
        
        # Select Safari version
        safari_version = random.choice(SAFARI_VERSIONS)
        
        # Build user agent string
        user_agent = (
            f"Mozilla/5.0 ({os_version}) "
            f"AppleWebKit/{webkit_version} (KHTML, like Gecko) "
            f"Chrome/{chrome_version} Safari/{safari_version}"
        )
        
        self._last_ua = user_agent
        logger.debug(f"Generated user agent: {user_agent}")
        
        return user_agent
    
    def get_last(self) -> Optional[str]:
        """
        Get the last generated user agent.
        
        Returns:
            str: Last generated user agent or None
        """
        return self._last_ua
    
    @staticmethod
    def get_chrome_versions() -> list[str]:
        """Get list of available Chrome versions."""
        return CHROME_VERSIONS.copy()
    
    @staticmethod
    def get_platforms() -> list[str]:
        """Get list of available platforms."""
        return list(OS_TEMPLATES.keys())


class UserAgentRotator:
    """Rotates through a pool of user agents."""
    
    def __init__(
        self,
        platforms: Optional[list[str]] = None,
        pool_size: int = 10
    ):
        """
        Initialize user agent rotator.
        
        Args:
            platforms: List of platforms to use. All if None
            pool_size: Number of user agents to generate in pool
        """
        self.platforms = platforms or ["windows", "mac", "linux"]
        self.pool_size = pool_size
        self.pool = []
        self.current_index = 0
        self._generate_pool()
        
    def _generate_pool(self) -> None:
        """Generate pool of user agents."""
        logger.info(f"Generating user agent pool of size {self.pool_size}")
        self.pool = []
        
        for _ in range(self.pool_size):
            platform = random.choice(self.platforms)
            factory = UserAgentFactory(platform=platform)
            ua = factory.generate()
            self.pool.append(ua)
        
        # Shuffle pool
        random.shuffle(self.pool)
        logger.debug(f"Generated {len(self.pool)} user agents")
    
    def get_next(self) -> str:
        """
        Get next user agent from pool (round-robin).
        
        Returns:
            str: User agent string
        """
        ua = self.pool[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.pool)
        return ua
    
    def get_random(self) -> str:
        """
        Get random user agent from pool.
        
        Returns:
            str: User agent string
        """
        return random.choice(self.pool)
    
    def refresh_pool(self) -> None:
        """Regenerate the entire pool with new user agents."""
        self._generate_pool()
        self.current_index = 0
        logger.info("User agent pool refreshed")
    
    def get_pool(self) -> list[str]:
        """Get current pool of user agents."""
        return self.pool.copy()


# Convenience functions for quick usage
def generate_user_agent(
    platform: Literal["windows", "mac", "linux", "random"] = "random"
) -> str:
    """
    Quick function to generate a single user agent.
    
    Args:
        platform: Target platform or "random"
        
    Returns:
        str: User agent string
        
    Example:
        >>> ua = generate_user_agent("windows")
        >>> print(ua)
    """
    factory = UserAgentFactory(platform=platform)
    return factory.generate()


def get_windows_user_agent() -> str:
    """Generate a Windows Chrome user agent."""
    return generate_user_agent("windows")


def get_mac_user_agent() -> str:
    """Generate a macOS Chrome user agent."""
    return generate_user_agent("mac")


def get_linux_user_agent() -> str:
    """Generate a Linux Chrome user agent."""
    return generate_user_agent("linux")


def get_random_user_agent() -> str:
    """Generate a random Chrome user agent."""
    return generate_user_agent("random")


# Pre-configured rotators for common use cases
_global_rotator = None


def get_rotator(platforms: Optional[list[str]] = None, pool_size: int = 10) -> UserAgentRotator:
    """
    Get or create a global user agent rotator.
    
    Args:
        platforms: List of platforms to use
        pool_size: Size of the user agent pool
        
    Returns:
        UserAgentRotator: Global rotator instance
    """
    global _global_rotator
    if _global_rotator is None:
        _global_rotator = UserAgentRotator(platforms=platforms, pool_size=pool_size)
    return _global_rotator


# User Agent validation and parsing
def parse_user_agent(user_agent: str) -> dict:
    """
    Parse a user agent string into components.
    
    Args:
        user_agent: User agent string to parse
        
    Returns:
        dict: Parsed components (browser, version, os, etc.)
        
    Example:
        >>> ua = generate_user_agent()
        >>> info = parse_user_agent(ua)
        >>> print(info['browser'], info['version'])
    """
    info = {
        "browser": None,
        "version": None,
        "os": None,
        "platform": None,
    }
    
    # Extract Chrome version
    if "Chrome/" in user_agent:
        start = user_agent.index("Chrome/") + 7
        end = user_agent.index(" ", start) if " " in user_agent[start:] else len(user_agent)
        info["browser"] = "Chrome"
        info["version"] = user_agent[start:end]
    
    # Extract OS
    if "Windows" in user_agent:
        info["os"] = "Windows"
        info["platform"] = "windows"
    elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
        info["os"] = "macOS"
        info["platform"] = "mac"
    elif "Linux" in user_agent:
        info["os"] = "Linux"
        info["platform"] = "linux"
    
    return info


def is_valid_user_agent(user_agent: str) -> bool:
    """
    Check if a user agent string appears valid.
    
    Args:
        user_agent: User agent string to validate
        
    Returns:
        bool: True if appears valid
    """
    required_parts = ["Mozilla", "AppleWebKit", "Chrome", "Safari"]
    return all(part in user_agent for part in required_parts)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    print("=" * 80)
    print("User Agent Factory Examples")
    print("=" * 80)
    
    # Generate single user agents
    print("\n1. Generate specific platform user agents:")
    print(f"Windows: {get_windows_user_agent()}")
    print(f"macOS:   {get_mac_user_agent()}")
    print(f"Linux:   {get_linux_user_agent()}")
    
    # Generate random
    print("\n2. Generate random user agents:")
    for i in range(3):
        print(f"Random {i+1}: {get_random_user_agent()}")
    
    # Use factory
    print("\n3. Using UserAgentFactory:")
    factory = UserAgentFactory(platform="windows")
    for i in range(3):
        ua = factory.generate()
        print(f"Generated {i+1}: {ua}")
    
    # Use rotator
    print("\n4. Using UserAgentRotator:")
    rotator = UserAgentRotator(platforms=["windows", "mac"], pool_size=5)
    print(f"Pool size: {len(rotator.get_pool())}")
    for i in range(7):
        print(f"Next {i+1}: {rotator.get_next()}")
    
    # Parse user agent
    print("\n5. Parsing user agent:")
    ua = get_random_user_agent()
    print(f"User Agent: {ua}")
    info = parse_user_agent(ua)
    print(f"Parsed: {info}")
    print(f"Valid: {is_valid_user_agent(ua)}")
    
    print("\n" + "=" * 80)
