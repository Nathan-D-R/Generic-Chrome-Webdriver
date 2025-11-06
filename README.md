# Generic Chrome WebDriver

A reusable Selenium Chrome WebDriver setup with common utilities for web automation.

## Features

- **Pre-configured Chrome driver** with stability options
- **Microsoft login automation** with account picker support
- **Custom download directory** management
- **Chrome profile support** for persistent sessions
- **Concurrent execution** example with thread pools

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Credentials

Create a `.env` file in the project root for the following features:


Microsoft Login:
```env
microsoft_username="your-email@example.com"
microsoft_password="your-password"
```

### 3. Run the Notebook

Open `Driver.ipynb` and run the cells to:
- Initialize a Chrome driver
- Perform Microsoft login
- Run concurrent browser tasks

## Project Structure

```
Generic Chrome Webdriver/
├── Driver.ipynb              # Main notebook with examples
├── requirements.txt          # Python dependencies
├── .env                      # Credentials (copy .env.example to make this)
├── Utilities/
│   ├── microsoft_login.py    # Microsoft authentication helper
│   └── __init__.py
└── Outputs/                  # General Output Directory (Ignored by .gitignore)
    └── Downloads/            # Default download location
```

## Usage Examples

### Basic Driver Setup

```python
from selenium import webdriver
from Driver import create_driver

# Create driver with download directory
driver = create_driver(download_dir="./Outputs/Downloads")
driver.get("https://example.com")
```

### Microsoft Login

```python
from Utilities.microsoft_login import microsoft_login

# Auto-login using .env credentials
microsoft_login(driver, stay_signed_in=False)
```

The login utility handles:
- Account picker page (selects existing account or "Use another account")
- Username entry
- Password entry
- "Stay signed in?" prompt

### Concurrent Execution

```python
from concurrent.futures import ThreadPoolExecutor

def worker_task(worker_id):
    worker_driver = create_driver()
    # Perform tasks...
    worker_driver.quit()

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(worker_task, i) for i in range(3)]
```

## Configuration Options

### Driver Options

```python
driver = create_driver(
    headless=False,           # Run browser in background
    profile_dir=None,         # Use custom Chrome profile
    download_dir=None         # Set download directory
)
```

### Microsoft Login Options

```python
microsoft_login(
    driver,
    username=None,            # Or load from .env
    password=None,            # Or load from .env
    stay_signed_in=False,     # Handle "Stay signed in?" prompt
    timeout=20                # Wait timeout in seconds
)
```

## Requirements

- Python 3.7+
- Chrome browser installed
- See `requirements.txt` for package dependencies

## Notes

- Drivers are automatically managed via `webdriver-manager`
- Logs are written to `sandbox.log`
- Chrome profile path is customizable for session persistence
- All utilities include error handling and logging
