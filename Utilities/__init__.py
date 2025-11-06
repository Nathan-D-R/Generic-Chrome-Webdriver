"""
Utilities Package
=================
Reusable components for web automation with Selenium.

Available modules:
- microsoft_login: Automate Microsoft authentication flows
"""

from .microsoft_login import microsoft_login, wait_for_login_redirect, MicrosoftLoginError

__all__ = [
    'microsoft_login',
    'wait_for_login_redirect', 
    'MicrosoftLoginError'
]

__version__ = '1.0.0'
