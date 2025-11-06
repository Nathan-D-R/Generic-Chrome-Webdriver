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

### 2. Setup Configuration

Copy the example environment file and customize it:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # Mac/Linux
```

Edit `.env` with your settings:
- Microsoft credentials (required for login automation)
- Download directories
- Chrome preferences (headless, window size, etc.)
- Logging settings
- Concurrency options

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
├── .env.example              # Example configuration file
├── .env                      # Your configuration (create from .env.example)
├── Utilities/
│   ├── driver_factory.py     # Chrome WebDriver factory
│   ├── config.py             # Configuration loader
│   ├── logging_setup.py      # Logging configuration
│   ├── microsoft_login.py    # Microsoft authentication
│   └── __init__.py
└── Outputs/
    └── Downloads/            # Default download location
```

## Usage Examples

### Basic Driver Setup

```python
from Utilities.driver_factory import create_driver
from Utilities.config import Config

# Create driver using settings from .env
driver = create_driver(
    headless=Config.HEADLESS,
    profile_dir=Config.get_profile_dir(),
    download_dir=Config.DOWNLOAD_DIR
)
driver.get("https://example.com")
```

### Microsoft Login

```python
from Utilities.microsoft_login import microsoft_login
from Utilities.config import Config

# Auto-login using credentials from .env
microsoft_login(driver, stay_signed_in=Config.STAY_SIGNED_IN)
```

The login utility handles:
- Account picker page (selects existing account or "Use another account")
- Username entry
- Password entry
- "Stay signed in?" prompt

### Concurrent Execution

```python
from concurrent.futures import ThreadPoolExecutor
from Utilities.driver_factory import create_driver
from Utilities.config import Config

def worker_task(worker_id):
    worker_driver = create_driver(headless=Config.HEADLESS)
    # Perform tasks...
    worker_driver.quit()

with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
    futures = [executor.submit(worker_task, i) for i in range(Config.MAX_WORKERS)]
```

## Configuration Options

All configuration is managed through the `.env` file. See `.env.example` for all available options.

### Key Settings

**Chrome Driver:**
- `HEADLESS` - Run browser in background (true/false)
- `IMPLICIT_WAIT` - Default wait time for elements (seconds)
- `WINDOW_SIZE` - Browser window size
- `PROFILE_DIR` - Chrome profile path for persistent sessions
- `DOWNLOAD_DIR` - Directory for downloaded files

**Microsoft Login:**
- `MICROSOFT_USERNAME` - Account email
- `MICROSOFT_PASSWORD` - Account password
- `STAY_SIGNED_IN` - Handle "Stay signed in?" prompt (true/false)

**Logging:**
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE` - Log file location

**Concurrency:**
- `MAX_WORKERS` - Maximum concurrent browser instances

## Requirements

- Python 3.7+
- Chrome browser installed
- See `requirements.txt` for package dependencies

## Notes

- All configuration is centralized in `.env` for easy management
- Drivers are automatically managed via `webdriver-manager`
- Logs location is configurable via `LOG_FILE` in `.env`
- Chrome profile path supports environment variables (e.g., `~/` expands to home directory)
- All utilities include comprehensive error handling and logging
- Use `print_config()` to display current configuration and validate settings
