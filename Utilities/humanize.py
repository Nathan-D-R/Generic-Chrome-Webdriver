"""
Humanize Utility
================
Makes browser interactions appear more human-like with random delays and natural patterns.

This module provides functions that mimic human behavior when interacting with web pages:
- Typing with variable speed and occasional typos
- Clicking with mouse movement and random delays
- Scrolling with natural acceleration/deceleration
- Random pauses between actions

Usage:
    from Utilities.humanize import human_click, human_send_keys, human_scroll
    
    element = driver.find_element(By.ID, "search")
    human_send_keys(element, "search query")
    human_click(element)
"""

import time
import random
import logging
from typing import Optional, Union
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


logger = logging.getLogger(__name__)


class HumanizeConfig:
    """Configuration for humanization behavior."""
    
    # Typing speed (seconds per character)
    TYPING_SPEED_MIN = 0.05
    TYPING_SPEED_MAX = 0.15
    
    # Delay between words when typing
    WORD_DELAY_MIN = 0.1
    WORD_DELAY_MAX = 0.3
    
    # Click delays
    CLICK_DELAY_MIN = 0.1
    CLICK_DELAY_MAX = 0.5
    
    # Mouse movement speed
    MOUSE_MOVE_STEPS_MIN = 3
    MOUSE_MOVE_STEPS_MAX = 10
    MOUSE_MOVE_DELAY = 0.02
    
    # Scroll delays
    SCROLL_PAUSE_MIN = 0.1
    SCROLL_PAUSE_MAX = 0.3
    SCROLL_STEP_MIN = 50
    SCROLL_STEP_MAX = 150
    
    # Random action delays
    ACTION_DELAY_MIN = 0.5
    ACTION_DELAY_MAX = 2.0
    
    # Typo probability (0.0 to 1.0)
    TYPO_PROBABILITY = 0.02


def _random_delay(min_delay: float, max_delay: float) -> None:
    """Sleep for a random duration between min and max."""
    time.sleep(random.uniform(min_delay, max_delay))


def _get_nearby_key(char: str) -> str:
    """Get a nearby key on the keyboard (for simulating typos)."""
    keyboard_layout = {
        'q': ['w', 'a'],
        'w': ['q', 'e', 's'],
        'e': ['w', 'r', 'd'],
        'r': ['e', 't', 'f'],
        't': ['r', 'y', 'g'],
        'y': ['t', 'u', 'h'],
        'u': ['y', 'i', 'j'],
        'i': ['u', 'o', 'k'],
        'o': ['i', 'p', 'l'],
        'p': ['o', 'l'],
        'a': ['q', 's', 'z'],
        's': ['w', 'a', 'd', 'x'],
        'd': ['e', 's', 'f', 'c'],
        'f': ['r', 'd', 'g', 'v'],
        'g': ['t', 'f', 'h', 'b'],
        'h': ['y', 'g', 'j', 'n'],
        'j': ['u', 'h', 'k', 'm'],
        'k': ['i', 'j', 'l'],
        'l': ['o', 'k', 'p'],
        'z': ['a', 'x'],
        'x': ['z', 's', 'c'],
        'c': ['x', 'd', 'v'],
        'v': ['c', 'f', 'b'],
        'b': ['v', 'g', 'n'],
        'n': ['b', 'h', 'm'],
        'm': ['n', 'j'],
    }
    
    char_lower = char.lower()
    if char_lower in keyboard_layout:
        nearby = random.choice(keyboard_layout[char_lower])
        return nearby.upper() if char.isupper() else nearby
    return char


def human_send_keys(
    element: WebElement,
    text: str,
    typo_probability: float = None,
    typing_speed_range: tuple = None
) -> None:
    """
    Type text into an element with human-like behavior.
    
    Features:
    - Variable typing speed
    - Occasional typos with corrections
    - Pauses between words
    - Random micro-delays
    
    Args:
        element: WebElement to type into
        text: Text to type
        typo_probability: Chance of making a typo (0.0 to 1.0). Uses config default if None
        typing_speed_range: Tuple of (min, max) seconds per character. Uses config default if None
        
    Example:
        >>> element = driver.find_element(By.ID, "search")
        >>> human_send_keys(element, "Python Selenium")
    """
    if typo_probability is None:
        typo_probability = HumanizeConfig.TYPO_PROBABILITY
    
    if typing_speed_range is None:
        typing_speed_range = (HumanizeConfig.TYPING_SPEED_MIN, HumanizeConfig.TYPING_SPEED_MAX)
    
    logger.debug(f"Human typing: {text}")
    
    words = text.split(' ')
    
    for word_idx, word in enumerate(words):
        for char_idx, char in enumerate(word):
            # Random chance of typo
            if random.random() < typo_probability and char.isalpha():
                # Type wrong character
                wrong_char = _get_nearby_key(char)
                element.send_keys(wrong_char)
                _random_delay(*typing_speed_range)
                
                # Realize mistake and correct it
                _random_delay(0.1, 0.3)  # Pause before correction
                element.send_keys(Keys.BACKSPACE)
                _random_delay(0.05, 0.1)
            
            # Type correct character
            element.send_keys(char)
            _random_delay(*typing_speed_range)
        
        # Add space between words (except after last word)
        if word_idx < len(words) - 1:
            element.send_keys(' ')
            _random_delay(
                HumanizeConfig.WORD_DELAY_MIN,
                HumanizeConfig.WORD_DELAY_MAX
            )
    
    logger.debug("Human typing complete")


def human_click(
    driver: WebDriver,
    element: WebElement,
    move_to_element: bool = True,
    click_delay: tuple = None
) -> None:
    """
    Click an element with human-like behavior.
    
    Features:
    - Moves mouse to element (optional)
    - Random delay before click
    - Natural movement patterns
    
    Args:
        driver: WebDriver instance
        element: WebElement to click
        move_to_element: Whether to move mouse to element first
        click_delay: Tuple of (min, max) seconds before clicking. Uses config default if None
        
    Example:
        >>> button = driver.find_element(By.ID, "submit")
        >>> human_click(driver, button)
    """
    if click_delay is None:
        click_delay = (HumanizeConfig.CLICK_DELAY_MIN, HumanizeConfig.CLICK_DELAY_MAX)
    
    logger.debug(f"Human clicking element: {element.tag_name}")
    
    actions = ActionChains(driver)
    
    if move_to_element:
        # Move to element with random offset
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        
        actions.move_to_element_with_offset(element, offset_x, offset_y)
        
        # Pause after moving
        _random_delay(0.1, 0.3)
    
    # Random delay before clicking
    _random_delay(*click_delay)
    
    # Perform click
    actions.click(element)
    actions.perform()
    
    # Small delay after click
    _random_delay(0.05, 0.15)
    
    logger.debug("Human click complete")


def human_scroll(
    driver: WebDriver,
    direction: str = "down",
    amount: int = None,
    smooth: bool = True
) -> None:
    """
    Scroll the page with human-like behavior.
    
    Features:
    - Multiple small scrolls instead of one large jump
    - Random pauses between scroll steps
    - Natural acceleration/deceleration
    
    Args:
        driver: WebDriver instance
        direction: "down", "up", "top", or "bottom"
        amount: Pixels to scroll (None = full page). Ignored for "top"/"bottom"
        smooth: Whether to use smooth scrolling with multiple steps
        
    Example:
        >>> human_scroll(driver, "down", amount=500)
        >>> human_scroll(driver, "top")
    """
    logger.debug(f"Human scrolling: {direction}, amount: {amount}")
    
    # Handle special cases
    if direction == "top":
        if smooth:
            current_position = driver.execute_script("return window.pageYOffset;")
            _smooth_scroll_to(driver, 0, current_position)
        else:
            driver.execute_script("window.scrollTo(0, 0);")
        logger.debug("Scrolled to top")
        return
    
    if direction == "bottom":
        if smooth:
            current_position = driver.execute_script("return window.pageYOffset;")
            max_height = driver.execute_script("return document.body.scrollHeight;")
            _smooth_scroll_to(driver, max_height, current_position)
        else:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.debug("Scrolled to bottom")
        return
    
    # Default scroll amount is viewport height
    if amount is None:
        amount = driver.execute_script("return window.innerHeight;")
    
    # Adjust amount based on direction
    if direction == "up":
        amount = -amount
    
    if smooth:
        _smooth_scroll_by(driver, amount)
    else:
        driver.execute_script(f"window.scrollBy(0, {amount});")
    
    logger.debug("Human scroll complete")


def _smooth_scroll_by(driver: WebDriver, amount: int) -> None:
    """Perform smooth scrolling in multiple steps."""
    num_steps = random.randint(5, 10)
    step_size = amount // num_steps
    
    for i in range(num_steps):
        # Variable step size for more natural movement
        current_step = step_size + random.randint(-10, 10)
        driver.execute_script(f"window.scrollBy(0, {current_step});")
        
        # Random pause between steps
        _random_delay(
            HumanizeConfig.SCROLL_PAUSE_MIN,
            HumanizeConfig.SCROLL_PAUSE_MAX
        )


def _smooth_scroll_to(driver: WebDriver, target: int, current: int) -> None:
    """Scroll smoothly from current position to target."""
    distance = abs(target - current)
    direction = 1 if target > current else -1
    
    num_steps = max(5, min(15, distance // 100))
    step_size = distance // num_steps
    
    for i in range(num_steps):
        scroll_amount = (step_size * direction) + random.randint(-20, 20)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        _random_delay(
            HumanizeConfig.SCROLL_PAUSE_MIN,
            HumanizeConfig.SCROLL_PAUSE_MAX
        )
    
    # Final adjustment to hit exact target
    driver.execute_script(f"window.scrollTo(0, {target});")


def human_pause(min_delay: float = None, max_delay: float = None) -> None:
    """
    Pause execution for a random human-like duration.
    
    Args:
        min_delay: Minimum delay in seconds. Uses config default if None
        max_delay: Maximum delay in seconds. Uses config default if None
        
    Example:
        >>> human_pause()  # Random pause between 0.5-2.0 seconds
        >>> human_pause(1.0, 3.0)  # Custom range
    """
    if min_delay is None:
        min_delay = HumanizeConfig.ACTION_DELAY_MIN
    if max_delay is None:
        max_delay = HumanizeConfig.ACTION_DELAY_MAX
    
    delay = random.uniform(min_delay, max_delay)
    logger.debug(f"Human pause: {delay:.2f}s")
    time.sleep(delay)


def human_mouse_move(
    driver: WebDriver,
    element: WebElement,
    duration: float = None
) -> None:
    """
    Move mouse to an element with human-like motion.
    
    Features:
    - Curved path instead of straight line
    - Variable speed
    - Random micro-adjustments
    
    Args:
        driver: WebDriver instance
        element: WebElement to move to
        duration: Total duration of movement in seconds. Random if None
        
    Example:
        >>> element = driver.find_element(By.ID, "button")
        >>> human_mouse_move(driver, element)
    """
    if duration is None:
        duration = random.uniform(0.3, 0.8)
    
    logger.debug(f"Human mouse move to element: {element.tag_name}")
    
    actions = ActionChains(driver)
    num_steps = random.randint(
        HumanizeConfig.MOUSE_MOVE_STEPS_MIN,
        HumanizeConfig.MOUSE_MOVE_STEPS_MAX
    )
    
    # Move in multiple small steps
    for i in range(num_steps):
        if i == num_steps - 1:
            # Final move to element
            actions.move_to_element(element)
        else:
            # Intermediate moves with random offsets
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
        
        time.sleep(duration / num_steps)
    
    actions.perform()
    logger.debug("Human mouse move complete")


def human_form_fill(
    driver: WebDriver,
    form_data: dict[str, Union[WebElement, tuple[WebElement, str]]]
) -> None:
    """
    Fill out a form with human-like behavior.
    
    Args:
        driver: WebDriver instance
        form_data: Dictionary mapping field names to (element, value) tuples or just elements
                  If just element is provided, it will be clicked
        
    Example:
        >>> human_form_fill(driver, {
        ...     "username": (username_field, "john.doe@example.com"),
        ...     "password": (password_field, "SecurePass123"),
        ...     "submit": submit_button
        ... })
    """
    logger.info("Human form filling started")
    
    for field_name, field_data in form_data.items():
        # Check if it's a tuple (element, value) or just element
        if isinstance(field_data, tuple):
            element, value = field_data
            logger.debug(f"Filling field: {field_name}")
            
            # Move to field
            human_mouse_move(driver, element)
            human_pause(0.2, 0.5)
            
            # Click field
            human_click(driver, element, move_to_element=False)
            human_pause(0.1, 0.3)
            
            # Type value
            human_send_keys(element, value)
            human_pause(0.3, 0.8)
        else:
            # Just an element to click (like submit button)
            element = field_data
            logger.debug(f"Clicking: {field_name}")
            
            human_mouse_move(driver, element)
            human_pause(0.3, 0.7)
            human_click(driver, element, move_to_element=False)
    
    logger.info("Human form filling complete")
