"""
Chrome WebDriver Factory
========================
Utility for creating pre-configured Chrome WebDriver instances.

This module provides a factory function to create Chrome WebDriver instances
with sensible defaults for stability, downloads, and privacy settings.
"""

import os
import logging
from typing import Optional, Literal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from Utilities.user_agent import generate_user_agent


logger = logging.getLogger(__name__)


def create_driver(
    headless: bool = False,
    profile_dir: str = None,
    download_dir: str = None,
    implicit_wait: int = 10,
    window_size: str = "1920x1080",
    stealth_mode: bool = False,
    user_agent: Optional[str] = None,
    user_agent_platform: Optional[Literal["windows", "mac", "linux", "random"]] = None,
    use_opaque_driver: bool = False
) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver with pre-configured options.
    
    Args:
        headless: Run browser without GUI
        profile_dir: Path to Chrome user profile directory (for persistent sessions)
        download_dir: Directory for downloaded files
        implicit_wait: Default wait time in seconds for element lookups
        window_size: Browser window size (used in headless mode)
        stealth_mode: Enable anti-detection features (experimental)
        user_agent: Custom user agent string. Auto-generated if None
        user_agent_platform: Platform for user agent generation ("windows", "mac", "linux", "random")
        use_opaque_driver: Wrap driver in OpaqueDriver for undetectable interactions
        
    Returns:
        webdriver.Chrome or OpaqueDriver: Configured driver instance
        
    Example:
        >>> driver = create_driver(download_dir="./downloads", stealth_mode=True)
        >>> driver.get("https://example.com")
        
        >>> # Use opaque driver for undetectable interactions
        >>> driver = create_driver(stealth_mode=True, use_opaque_driver=True)
        >>> element = driver.find_element(By.ID, "search")
        >>> element.send_keys("query")  # Automatically uses human-like typing
        
    Warning:
        stealth_mode is experimental and may not work on all websites.
        Use responsibly and respect website terms of service.
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
    
    # Stealth mode - additional anti-detection measures
    if stealth_mode:
        logger.info("Stealth mode enabled - applying anti-detection measures")
        
        # Additional Chrome arguments for stealth
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--exclude-switches=enable-automation")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        
        # Exclude automation switches
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # User agent configuration
    if user_agent is None and (stealth_mode or user_agent_platform):
        # Generate realistic user agent
        platform = user_agent_platform or "random"
        user_agent = generate_user_agent(platform)
        logger.info(f"Generated user agent: {user_agent}")
    
    if user_agent:
        chrome_options.add_argument(f"user-agent={user_agent}")
        logger.debug(f"Using custom user agent")

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
    
    # Apply stealth JavaScript patches if enabled
    if stealth_mode:
        _apply_stealth_patches(driver)
    
    driver.implicitly_wait(implicit_wait)
    logger.info("Chrome WebDriver created successfully")
    
    # Wrap in OpaqueDriver if requested
    if use_opaque_driver:
        from Utilities.opaque_driver import create_opaque_driver
        logger.info("Wrapping driver in OpaqueDriver for undetectable interactions")
        return create_opaque_driver(
            driver,
            use_human_behavior=True,
            auto_pause=True,
            pause_range=(0.5, 2.0)
        )
    
    return driver


def _apply_stealth_patches(driver: webdriver.Chrome) -> None:
    """
    Apply JavaScript patches to hide automation indicators.
    
    This function overrides various browser properties that can be used
    to detect automated browsing.
    
    Args:
        driver: WebDriver instance to patch
    """
    logger.debug("Applying stealth JavaScript patches")
    
    # Override navigator.webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    # Override Chrome automation properties
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            window.navigator.chrome = {
                runtime: {},
            };
        """
    })
    
    # Override permissions
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """
    })
    
    # Override plugins to appear more realistic
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "WebKit built-in PDF"
                    }
                ],
            });
        """
    })
    
    # Override languages
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """
    })
    
    # Override WebGL vendor
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
        """
    })
    
    # Override hairline feature
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
                get: function() {
                    return this.clientHeight;
                }
            });
        """
    })
    
    # Override user agent data
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'userAgentData', {
                get: () => ({
                    brands: [
                        { brand: "Not.A/Brand", version: "8" },
                        { brand: "Chromium", version: "120" },
                        { brand: "Google Chrome", version: "120" }
                    ],
                    mobile: false,
                    platform: "Windows"
                }),
            });
        """
    })
    
    logger.debug("Stealth patches applied successfully")
