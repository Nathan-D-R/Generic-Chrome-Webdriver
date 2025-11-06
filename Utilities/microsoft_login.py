"""
Microsoft Login Utility
=======================
An importable component to handle Microsoft login prompts with Selenium WebDriver.

This module provides functionality to automate the Microsoft authentication flow:
1. Enter username and click "Next"
2. Enter password and click "Sign in"
3. Handle "Stay signed in?" prompt

Usage:
    from Utilities.microsoft_login import microsoft_login
    
    success = microsoft_login(driver, username, password)
    # Or use credentials from environment:
    success = microsoft_login(driver)
"""

import os
import logging
import time
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from Utilities.config import Config


# Configure logger
logger = logging.getLogger(__name__)


class MicrosoftLoginError(Exception):
    """Custom exception for Microsoft login failures."""
    pass


def microsoft_login(
    driver: WebDriver,
    username: Optional[str] = None,
    password: Optional[str] = None,
    stay_signed_in: bool = False,
    timeout: int = 20
) -> bool:
    """
    Automate Microsoft login process.
    
    Args:
        driver: Selenium WebDriver instance
        username: Microsoft account username/email. If None, loads from .env
        password: Microsoft account password. If None, loads from .env
        stay_signed_in: Whether to click "Yes" on "Stay signed in?" prompt
        timeout: Maximum wait time in seconds for each step
        
    Returns:
        bool: True if login successful, False otherwise
        
    Raises:
        MicrosoftLoginError: If login fails due to invalid credentials or page issues
        
    Example:
        >>> from selenium import webdriver
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://login.microsoftonline.com")
        >>> microsoft_login(driver)  # Uses credentials from .env
        True
    """
    # Load credentials from Config if not provided
    if username is None or password is None:
        username = username or Config.MICROSOFT_USERNAME
        password = password or Config.MICROSOFT_PASSWORD
        
        if not username or not password:
            raise MicrosoftLoginError(
                "Username and password must be provided or set in .env file "
                "(MICROSOFT_USERNAME and MICROSOFT_PASSWORD)"
            )
    
    # Remove quotes if present
    username = username.strip('"').strip("'")
    password = password.strip('"').strip("'")
    
    logger.info(f"Starting Microsoft login for user: {username}")
    
    try:
        # Step 0: Handle account picker if it appears
        # Returns True if an account was selected, False if we need to enter username manually
        account_selected = _handle_account_picker(driver, username, timeout)
        
        # Step 1: Enter username and click "Next" (skip if account was already selected)
        if not account_selected:
            if not _enter_username(driver, username, timeout):
                return False
        else:
            logger.info("Skipping username entry (account already selected from picker)")
        
        # Step 2: Enter password and click "Sign in"
        if not _enter_password(driver, password, timeout):
            return False
        
        # Step 3: Handle "Stay signed in?" prompt (if it appears)
        _handle_stay_signed_in(driver, stay_signed_in, timeout)
        
        logger.info("Microsoft login completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Microsoft login failed: {str(e)}")
        raise MicrosoftLoginError(f"Login failed: {str(e)}") from e


def _handle_account_picker(driver: WebDriver, username: str, timeout: int) -> bool:
    """
    Step 0: Handle the "Pick an account" page if it appears.
    
    This page shows a list of previously used accounts and a "Use another account" option.
    If the desired username is in the list, click it. Otherwise, click "Use another account".
    
    Args:
        driver: Selenium WebDriver instance
        username: Microsoft account username/email to look for
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if an existing account was selected (skip username entry),
              False if "Use another account" was clicked or page not present (proceed to username entry)
    """
    try:
        logger.info("Step 0: Checking for account picker page")
        
        # Use a shorter timeout since this page may not appear
        short_timeout = min(timeout, 5)
        
        # Check if we're on the account picker page by looking for the tilesHolder div
        try:
            tiles_holder = WebDriverWait(driver, short_timeout).until(
                EC.presence_of_element_located((By.ID, "tilesHolder"))
            )
            logger.info("Account picker page detected")
            
            # Normalize the username for comparison (remove quotes, lowercase)
            normalized_username = username.strip('"').strip("'").lower()
            
            # Try to find a tile matching the username
            # Tiles have data-test-id attribute with the email
            try:
                account_tile = driver.find_element(
                    By.CSS_SELECTOR, 
                    f'[data-test-id="{normalized_username}"]'
                )
                logger.info(f"Found matching account tile for: {username}")
                account_tile.click()
                logger.info("Clicked on existing account - skipping username entry")
                time.sleep(1)
                return True  # Account selected, skip username entry
                
            except NoSuchElementException:
                logger.info(f"Account {username} not found in picker, looking for 'Use another account'")
                
                # Click "Use another account" button
                # This button is in a div with id="otherTile"
                try:
                    other_account_button = WebDriverWait(driver, short_timeout).until(
                        EC.element_to_be_clickable((By.ID, "otherTile"))
                    )
                    other_account_button.click()
                    logger.info("Clicked 'Use another account'")
                    time.sleep(1)
                    return False  # Need to enter username manually
                    
                except TimeoutException:
                    logger.warning("Could not find 'Use another account' button")
                    return False  # Proceed with username entry as fallback
            
        except TimeoutException:
            # Account picker page didn't appear - this is normal
            logger.info("Account picker page not detected (proceeding to username entry)")
            return False  # Need to enter username manually
        
    except Exception as e:
        logger.warning(f"Error handling account picker: {str(e)}")
        # Don't fail the entire login for this step, but proceed with username entry
        return False


def _enter_username(driver: WebDriver, username: str, timeout: int) -> bool:
    """
    Step 1: Enter username/email and click Next.
    
    Args:
        driver: Selenium WebDriver instance
        username: Microsoft account username/email
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Step 1: Entering username")
        
        # Wait for username input field to be visible
        # The input field has id="i0116"
        username_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "i0116"))
        )
        
        # Clear any existing text and enter username
        username_field.clear()
        username_field.send_keys(username)
        logger.info(f"Username entered: {username}")
        
        # Small delay to ensure text is registered
        time.sleep(0.5)
        
        # Click the "Next" button (id="idSIButton9")
        next_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        next_button.click()
        logger.info("Clicked 'Next' button")
        
        # Wait a moment for the page to transition
        time.sleep(1)
        
        return True
        
    except TimeoutException:
        logger.error("Timeout waiting for username input field or Next button")
        return False
    except Exception as e:
        logger.error(f"Error entering username: {str(e)}")
        return False


def _enter_password(driver: WebDriver, password: str, timeout: int) -> bool:
    """
    Step 2: Enter password and click Sign in.
    
    Args:
        driver: Selenium WebDriver instance
        password: Microsoft account password
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Step 2: Entering password")
        
        # Wait for password input field to be visible
        # The password field has id="i0118"
        password_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "i0118"))
        )
        
        # Wait an extra moment to ensure the field is fully loaded
        time.sleep(0.5)
        
        # Clear any existing text and enter password
        password_field.clear()
        password_field.send_keys(password)
        logger.info("Password entered")
        
        # Small delay to ensure text is registered
        time.sleep(0.5)
        
        # Click the "Sign in" button (id="idSIButton9")
        sign_in_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        sign_in_button.click()
        logger.info("Clicked 'Sign in' button")
        
        # Wait for page to process login
        time.sleep(2)
        
        # Check for login errors
        try:
            error_element = driver.find_element(By.ID, "passwordError")
            if error_element and error_element.is_displayed():
                error_text = error_element.text
                logger.error(f"Login error: {error_text}")
                raise MicrosoftLoginError(f"Invalid credentials: {error_text}")
        except NoSuchElementException:
            # No error - this is good
            pass
        
        return True
        
    except TimeoutException:
        logger.error("Timeout waiting for password input field or Sign in button")
        return False
    except MicrosoftLoginError:
        raise
    except Exception as e:
        logger.error(f"Error entering password: {str(e)}")
        return False


def _handle_stay_signed_in(driver: WebDriver, stay_signed_in: bool, timeout: int) -> bool:
    """
    Step 3: Handle "Stay signed in?" prompt.
    
    This prompt may not always appear. If it doesn't appear within a short timeout,
    we assume login was successful and the prompt was skipped.
    
    Args:
        driver: Selenium WebDriver instance
        stay_signed_in: Whether to click "Yes" (True) or "No" (False)
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if handled successfully or prompt not present
    """
    try:
        logger.info("Step 3: Checking for 'Stay signed in?' prompt")
        
        # Use a shorter timeout since this prompt may not appear
        short_timeout = min(timeout, 10)
        
        # Look for the KMSI (Keep Me Signed In) button
        # "Yes" button has id="idSIButton9"
        # "No" button has id="idBtn_Back"
        
        # Wait for either button to appear
        if stay_signed_in:
            button_id = "idSIButton9"  # Yes
            button_text = "Yes"
        else:
            button_id = "idBtn_Back"   # No
            button_text = "No"
        
        try:
            kmsi_button = WebDriverWait(driver, short_timeout).until(
                EC.element_to_be_clickable((By.ID, button_id))
            )
            
            # Verify this is the KMSI page by checking for the checkbox
            try:
                driver.find_element(By.ID, "KmsiCheckboxField")
                # If we found the checkbox, this is the KMSI page
                kmsi_button.click()
                logger.info(f"Clicked '{button_text}' on 'Stay signed in?' prompt")
                time.sleep(1)
            except NoSuchElementException:
                # Not the KMSI page, button might be for something else
                logger.info("Stay signed in prompt not detected (not on KMSI page)")
                pass
                
        except TimeoutException:
            # Prompt didn't appear - this is normal
            logger.info("Stay signed in prompt did not appear (skipped)")
        
        return True
        
    except Exception as e:
        logger.warning(f"Error handling stay signed in prompt: {str(e)}")
        # Don't fail the entire login for this step
        return True


def wait_for_login_redirect(driver: WebDriver, expected_url: str = None, timeout: int = 30) -> bool:
    """
    Wait for redirect after successful login.
    
    Args:
        driver: Selenium WebDriver instance
        expected_url: Optional URL substring to wait for
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if redirect occurred, False if timeout
        
    Example:
        >>> microsoft_login(driver)
        >>> wait_for_login_redirect(driver, "portal.office.com")
    """
    try:
        logger.info("Waiting for post-login redirect...")
        
        if expected_url:
            WebDriverWait(driver, timeout).until(
                lambda d: expected_url in d.current_url
            )
            logger.info(f"Successfully redirected to: {driver.current_url}")
        else:
            # Wait for URL to change from login page
            WebDriverWait(driver, timeout).until(
                lambda d: "login.microsoftonline.com" not in d.current_url
            )
            logger.info(f"Successfully redirected away from login page to: {driver.current_url}")
        
        return True
        
    except TimeoutException:
        logger.warning(f"Timeout waiting for redirect. Current URL: {driver.current_url}")
        return False