"""
Chrome WebDriver Factory
========================
Utility for creating pre-configured Chrome WebDriver instances.

This module provides a factory function to create Chrome WebDriver instances
with sensible defaults for stability, downloads, and privacy settings.
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)


def create_driver(
    headless: bool = False,
    profile_dir: str = None,
    download_dir: str = None,
    implicit_wait: int = 10,
    window_size: str = "1920x1080"
) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver with pre-configured options.
    
    Args:
        headless: Run browser without GUI
        profile_dir: Path to Chrome user profile directory (for persistent sessions)
        download_dir: Directory for downloaded files
        implicit_wait: Default wait time in seconds for element lookups
        window_size: Browser window size (used in headless mode)
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
        
    Example:
        >>> driver = create_driver(download_dir="./downloads")
        >>> driver.get("https://example.com")
    """
    chrome_options = Options()

    # Headless mode configuration
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={window_size}")
        logger.info("Running in headless mode")
    
    # Custom profile for persistent sessions
    if profile_dir:
        chrome_options.add_argument(f"user-data-dir={profile_dir}")
        logger.info(f"Using Chrome profile: {profile_dir}")
    
    # Stability and anti-detection options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-extensions")

    # Download and privacy preferences
    if download_dir:
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"Download directory: {download_dir}")
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values": {
                "notifications": 2,      # Block notifications
                "media_stream": 2,       # Block camera/microphone
                "geolocation": 2,        # Block location
                "local_discovery": 2     # Block local network discovery
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
    
    # Create WebDriver instance
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    driver.implicitly_wait(implicit_wait)
    logger.info("Chrome WebDriver created successfully")
    
    return driver
