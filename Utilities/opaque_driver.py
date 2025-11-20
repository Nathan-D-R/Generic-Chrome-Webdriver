"""
Opaque Driver Wrapper
=====================
A transparent wrapper around Selenium WebDriver that automatically uses undetectable
methods for operations that are commonly fingerprinted or detected.

This wrapper intercepts standard WebDriver calls and routes them through either:
- Native WebDriver (for undetectable operations)
- Custom implementations (for detectable operations)

The goal is to provide the same API as WebDriver while being undetectable.
"""

import time
import logging
from typing import Optional, Union, List, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from Utilities.humanize import (
    human_send_keys,
    human_click,
    human_scroll,
    human_pause
)


logger = logging.getLogger(__name__)


class OpaqueElement:
    """
    Wrapper around WebElement that uses undetectable methods.
    Provides the same API as WebElement but routes through custom implementations.
    """
    
    def __init__(self, element: WebElement, driver: 'OpaqueDriver'):
        """
        Initialize opaque element wrapper.
        
        Args:
            element: Underlying WebElement
            driver: OpaqueDriver instance for context
        """
        self._element = element
        self._driver = driver
        logger.debug(f"OpaqueElement created for {element.tag_name}")
    
    def click(self, human_like: bool = None) -> None:
        """
        Click element using undetectable method.
        
        Args:
            human_like: Use human-like clicking. Defaults to driver setting
        """
        use_human = human_like if human_like is not None else self._driver.use_human_behavior
        
        if use_human:
            logger.debug("Using human-like click")
            human_click(self._driver._driver, self._element, move_to_element=True)
        else:
            # Use JavaScript click to avoid MouseEvent detection
            logger.debug("Using JavaScript click")
            self._driver._driver.execute_script("arguments[0].click();", self._element)
    
    def send_keys(self, *value, human_like: bool = None) -> None:
        """
        Send keys using undetectable method.
        
        Args:
            value: Text to type
            human_like: Use human-like typing. Defaults to driver setting
        """
        use_human = human_like if human_like is not None else self._driver.use_human_behavior
        text = ''.join(str(v) for v in value)
        
        if use_human:
            logger.debug(f"Using human-like typing for: {text}")
            human_send_keys(self._element, text)
        else:
            # Use JavaScript for instant typing (still detectable but faster)
            logger.debug(f"Using JavaScript typing for: {text}")
            self._driver._driver.execute_script(
                f"arguments[0].value = '{text}';"
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                self._element
            )
    
    def clear(self) -> None:
        """Clear element using undetectable method."""
        logger.debug("Clearing element")
        # Use JavaScript to avoid KeyEvent detection
        self._driver._driver.execute_script(
            "arguments[0].value = '';"
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            self._element
        )
    
    def submit(self) -> None:
        """Submit form using undetectable method."""
        logger.debug("Submitting form")
        # Use JavaScript form submission
        self._driver._driver.execute_script("arguments[0].submit();", self._element)
    
    # Pass-through properties (these are undetectable)
    @property
    def text(self) -> str:
        """Get element text (undetectable)."""
        return self._element.text
    
    @property
    def tag_name(self) -> str:
        """Get element tag name (undetectable)."""
        return self._element.tag_name
    
    def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute (undetectable)."""
        return self._element.get_attribute(name)
    
    def get_property(self, name: str) -> Optional[str]:
        """Get element property (undetectable)."""
        return self._element.get_property(name)
    
    def is_displayed(self) -> bool:
        """Check if element is displayed (undetectable)."""
        return self._element.is_displayed()
    
    def is_enabled(self) -> bool:
        """Check if element is enabled (undetectable)."""
        return self._element.is_enabled()
    
    def is_selected(self) -> bool:
        """Check if element is selected (undetectable)."""
        return self._element.is_selected()
    
    @property
    def location(self) -> dict:
        """Get element location (undetectable)."""
        return self._element.location
    
    @property
    def size(self) -> dict:
        """Get element size (undetectable)."""
        return self._element.size
    
    @property
    def rect(self) -> dict:
        """Get element rectangle (undetectable)."""
        return self._element.rect
    
    def screenshot(self, filename: str) -> bool:
        """Take element screenshot (undetectable)."""
        return self._element.screenshot(filename)
    
    # Access to underlying element if needed
    @property
    def underlying_element(self) -> WebElement:
        """Get underlying WebElement."""
        return self._element


class OpaqueDriver:
    """
    Wrapper around WebDriver that automatically uses undetectable methods.
    
    This class provides the same interface as WebDriver but routes detectable
    operations through custom implementations.
    """
    
    def __init__(
        self,
        driver: WebDriver,
        use_human_behavior: bool = True,
        auto_pause: bool = True,
        pause_range: tuple = (0.5, 2.0)
    ):
        """
        Initialize opaque driver wrapper.
        
        Args:
            driver: Underlying WebDriver instance
            use_human_behavior: Use human-like interactions by default
            auto_pause: Automatically pause between actions
            pause_range: Range for auto-pause duration (min, max) in seconds
        """
        self._driver = driver
        self.use_human_behavior = use_human_behavior
        self.auto_pause = auto_pause
        self.pause_range = pause_range
        logger.info(f"OpaqueDriver initialized (human_behavior={use_human_behavior})")
    
    def _auto_pause_if_enabled(self) -> None:
        """Automatically pause if enabled."""
        if self.auto_pause:
            human_pause(*self.pause_range)
    
    # Element finding - wrap in OpaqueElement
    def find_element(self, by: str, value: str) -> OpaqueElement:
        """
        Find element and return opaque wrapper.
        
        Args:
            by: Locator strategy (By.ID, By.CSS_SELECTOR, etc.)
            value: Locator value
            
        Returns:
            OpaqueElement: Wrapped element
        """
        logger.debug(f"Finding element: {by}={value}")
        element = self._driver.find_element(by, value)
        return OpaqueElement(element, self)
    
    def find_elements(self, by: str, value: str) -> List[OpaqueElement]:
        """
        Find elements and return opaque wrappers.
        
        Args:
            by: Locator strategy
            value: Locator value
            
        Returns:
            List[OpaqueElement]: List of wrapped elements
        """
        logger.debug(f"Finding elements: {by}={value}")
        elements = self._driver.find_elements(by, value)
        return [OpaqueElement(elem, self) for elem in elements]
    
    # Navigation - undetectable, pass through
    def get(self, url: str) -> None:
        """
        Navigate to URL with optional auto-pause.
        
        Args:
            url: URL to navigate to
        """
        logger.info(f"Navigating to: {url}")
        self._driver.get(url)
        self._auto_pause_if_enabled()
    
    def back(self) -> None:
        """Go back in browser history."""
        logger.debug("Navigating back")
        self._driver.back()
        self._auto_pause_if_enabled()
    
    def forward(self) -> None:
        """Go forward in browser history."""
        logger.debug("Navigating forward")
        self._driver.forward()
        self._auto_pause_if_enabled()
    
    def refresh(self) -> None:
        """Refresh current page."""
        logger.debug("Refreshing page")
        self._driver.refresh()
        self._auto_pause_if_enabled()
    
    # Scrolling - use undetectable method
    def scroll(
        self,
        direction: str = "down",
        amount: int = None,
        smooth: bool = True
    ) -> None:
        """
        Scroll page using human-like behavior.
        
        Args:
            direction: "down", "up", "top", or "bottom"
            amount: Pixels to scroll (None = full viewport)
            smooth: Use smooth scrolling
        """
        logger.debug(f"Scrolling: {direction}, amount={amount}")
        human_scroll(self._driver, direction=direction, amount=amount, smooth=smooth)
        if self.auto_pause:
            human_pause(0.2, 0.5)
    
    def scroll_to_element(self, element: Union[OpaqueElement, WebElement]) -> None:
        """
        Scroll element into view using JavaScript.
        
        Args:
            element: Element to scroll to
        """
        underlying = element.underlying_element if isinstance(element, OpaqueElement) else element
        logger.debug(f"Scrolling to element: {underlying.tag_name}")
        self._driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            underlying
        )
        time.sleep(0.5)  # Wait for scroll to complete
    
    # JavaScript execution - undetectable, pass through
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript (undetectable).
        
        Args:
            script: JavaScript code to execute
            args: Arguments to pass to script
            
        Returns:
            Script return value
        """
        logger.debug(f"Executing script: {script[:50]}...")
        return self._driver.execute_script(script, *args)
    
    def execute_async_script(self, script: str, *args) -> Any:
        """Execute async JavaScript (undetectable)."""
        logger.debug(f"Executing async script: {script[:50]}...")
        return self._driver.execute_async_script(script, *args)
    
    # Screenshots - undetectable, pass through
    def save_screenshot(self, filename: str) -> bool:
        """Take screenshot (undetectable)."""
        logger.info(f"Taking screenshot: {filename}")
        return self._driver.save_screenshot(filename)
    
    def get_screenshot_as_png(self) -> bytes:
        """Get screenshot as PNG bytes (undetectable)."""
        return self._driver.get_screenshot_as_png()
    
    def get_screenshot_as_base64(self) -> str:
        """Get screenshot as base64 string (undetectable)."""
        return self._driver.get_screenshot_as_base64()
    
    # Window management - undetectable, pass through
    @property
    def current_window_handle(self) -> str:
        """Get current window handle (undetectable)."""
        return self._driver.current_window_handle
    
    @property
    def window_handles(self) -> List[str]:
        """Get all window handles (undetectable)."""
        return self._driver.window_handles
    
    def switch_to_window(self, window_name: str) -> None:
        """Switch to window (undetectable)."""
        logger.debug(f"Switching to window: {window_name}")
        self._driver.switch_to.window(window_name)
    
    def close(self) -> None:
        """Close current window (undetectable)."""
        logger.debug("Closing window")
        self._driver.close()
    
    def quit(self) -> None:
        """Quit driver (undetectable)."""
        logger.info("Quitting driver")
        self._driver.quit()
    
    # Frame switching - undetectable, pass through
    def switch_to_frame(self, frame_reference: Union[int, str, WebElement]) -> None:
        """Switch to iframe (undetectable)."""
        logger.debug(f"Switching to frame: {frame_reference}")
        self._driver.switch_to.frame(frame_reference)
    
    def switch_to_default_content(self) -> None:
        """Switch to default content (undetectable)."""
        logger.debug("Switching to default content")
        self._driver.switch_to.default_content()
    
    def switch_to_parent_frame(self) -> None:
        """Switch to parent frame (undetectable)."""
        logger.debug("Switching to parent frame")
        self._driver.switch_to.parent_frame()
    
    # Alert handling - undetectable, pass through
    @property
    def switch_to_alert(self):
        """Switch to alert (undetectable)."""
        return self._driver.switch_to.alert
    
    # Cookie management - undetectable, pass through
    def get_cookies(self) -> List[dict]:
        """Get all cookies (undetectable)."""
        return self._driver.get_cookies()
    
    def get_cookie(self, name: str) -> Optional[dict]:
        """Get specific cookie (undetectable)."""
        return self._driver.get_cookie(name)
    
    def add_cookie(self, cookie_dict: dict) -> None:
        """Add cookie (undetectable)."""
        logger.debug(f"Adding cookie: {cookie_dict.get('name')}")
        self._driver.add_cookie(cookie_dict)
    
    def delete_cookie(self, name: str) -> None:
        """Delete cookie (undetectable)."""
        logger.debug(f"Deleting cookie: {name}")
        self._driver.delete_cookie(name)
    
    def delete_all_cookies(self) -> None:
        """Delete all cookies (undetectable)."""
        logger.debug("Deleting all cookies")
        self._driver.delete_all_cookies()
    
    # Wait utilities - enhanced with auto-pause
    def wait_for_element(
        self,
        by: str,
        value: str,
        timeout: int = 10
    ) -> OpaqueElement:
        """
        Wait for element to be present.
        
        Args:
            by: Locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            OpaqueElement: Wrapped element
        """
        logger.debug(f"Waiting for element: {by}={value} (timeout={timeout}s)")
        element = WebDriverWait(self._driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return OpaqueElement(element, self)
    
    def wait_for_element_clickable(
        self,
        by: str,
        value: str,
        timeout: int = 10
    ) -> OpaqueElement:
        """
        Wait for element to be clickable.
        
        Args:
            by: Locator strategy
            value: Locator value
            timeout: Maximum wait time in seconds
            
        Returns:
            OpaqueElement: Wrapped element
        """
        logger.debug(f"Waiting for element clickable: {by}={value} (timeout={timeout}s)")
        element = WebDriverWait(self._driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return OpaqueElement(element, self)
    
    # Properties - undetectable, pass through
    @property
    def current_url(self) -> str:
        """Get current URL (undetectable)."""
        return self._driver.current_url
    
    @property
    def title(self) -> str:
        """Get page title (undetectable)."""
        return self._driver.title
    
    @property
    def page_source(self) -> str:
        """Get page source (undetectable)."""
        return self._driver.page_source
    
    def implicitly_wait(self, time_to_wait: float) -> None:
        """Set implicit wait (undetectable)."""
        self._driver.implicitly_wait(time_to_wait)
    
    # Access to underlying driver
    @property
    def underlying_driver(self) -> WebDriver:
        """Get underlying WebDriver instance."""
        return self._driver
    
    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - quit driver."""
        self.quit()
        return False


# Convenience function to create opaque driver
def create_opaque_driver(
    driver: WebDriver,
    use_human_behavior: bool = True,
    auto_pause: bool = True,
    pause_range: tuple = (0.5, 2.0)
) -> OpaqueDriver:
    """
    Create an opaque driver wrapper.
    
    Args:
        driver: WebDriver instance to wrap
        use_human_behavior: Use human-like interactions by default
        auto_pause: Automatically pause between actions
        pause_range: Range for auto-pause duration
        
    Returns:
        OpaqueDriver: Wrapped driver instance
        
    Example:
        >>> from Utilities.driver_factory import create_driver
        >>> from Utilities.opaque_driver import create_opaque_driver
        >>>
        >>> raw_driver = create_driver(stealth_mode=True)
        >>> driver = create_opaque_driver(raw_driver)
        >>>
        >>> driver.get("https://example.com")
        >>> element = driver.find_element(By.ID, "search")
        >>> element.send_keys("search query")  # Uses human-like typing
        >>> element.click()  # Uses human-like clicking
    """
    return OpaqueDriver(
        driver=driver,
        use_human_behavior=use_human_behavior,
        auto_pause=auto_pause,
        pause_range=pause_range
    )
