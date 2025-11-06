# User Agent Factory

Generate realistic and rotating user agent strings to avoid fingerprinting and detection.

## Features

- **Realistic Chrome user agents** for Windows, macOS, and Linux
- **User agent rotation** with configurable pools
- **Automatic generation** when creating drivers in stealth mode
- **Custom user agents** for specific requirements
- **Parsing and validation** utilities

## Quick Start

### Generate Single User Agent

```python
from Utilities.user_agent import generate_user_agent

# Random platform
ua = generate_user_agent("random")

# Specific platform
windows_ua = generate_user_agent("windows")
mac_ua = generate_user_agent("mac")
linux_ua = generate_user_agent("linux")
```

### Convenience Functions

```python
from Utilities.user_agent import (
    get_windows_user_agent,
    get_mac_user_agent,
    get_linux_user_agent,
    get_random_user_agent
)

ua = get_windows_user_agent()
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...
```

### Use with Driver Factory

```python
from Utilities.driver_factory import create_driver

# Auto-generate user agent based on platform
driver = create_driver(
    stealth_mode=True,
    user_agent_platform="windows"  # or "mac", "linux", "random"
)

# Use custom user agent
driver = create_driver(
    stealth_mode=True,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
)
```

### Configuration via .env

```env
# Auto-generate user agent
USER_AGENT=
USER_AGENT_PLATFORM=random

# Or use specific user agent
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
```

## User Agent Factory Class

For more control, use the `UserAgentFactory` class:

```python
from Utilities.user_agent import UserAgentFactory

# Create factory for specific platform
factory = UserAgentFactory(platform="windows")

# Generate multiple user agents
for i in range(5):
    ua = factory.generate()
    print(f"UA {i+1}: {ua}")

# Generate with specific Chrome version
ua = factory.generate(chrome_version="120.0.0.0")

# Get last generated UA
last_ua = factory.get_last()
```

## User Agent Rotator

For concurrent or multi-session automation, use the rotator:

```python
from Utilities.user_agent import UserAgentRotator

# Create rotator with pool of user agents
rotator = UserAgentRotator(
    platforms=["windows", "mac"],
    pool_size=10
)

# Get next user agent (round-robin)
ua1 = rotator.get_next()
ua2 = rotator.get_next()
ua3 = rotator.get_next()

# Get random user agent from pool
ua_random = rotator.get_random()

# Refresh pool with new user agents
rotator.refresh_pool()

# Get current pool
all_uas = rotator.get_pool()
print(f"Pool contains {len(all_uas)} user agents")
```

### Concurrent Workers with Rotation

```python
from concurrent.futures import ThreadPoolExecutor
from Utilities.user_agent import UserAgentRotator
from Utilities.driver_factory import create_driver

# Create global rotator
rotator = UserAgentRotator(platforms=["windows", "mac"], pool_size=5)

def worker_task(worker_id):
    # Each worker gets a different user agent
    ua = rotator.get_next()
    
    driver = create_driver(
        stealth_mode=True,
        user_agent=ua
    )
    
    try:
        driver.get("https://example.com")
        # Do work...
    finally:
        driver.quit()

# Run workers
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(worker_task, i) for i in range(5)]
```

## User Agent Parsing

Extract information from user agent strings:

```python
from Utilities.user_agent import parse_user_agent, is_valid_user_agent

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Parse components
info = parse_user_agent(ua)
print(info)
# {
#     'browser': 'Chrome',
#     'version': '120.0.0.0',
#     'os': 'Windows',
#     'platform': 'windows'
# }

# Validate user agent
if is_valid_user_agent(ua):
    print("Valid user agent")
```

## Available Chrome Versions

The factory includes recent stable Chrome versions:

```python
from Utilities.user_agent import UserAgentFactory

versions = UserAgentFactory.get_chrome_versions()
print(versions)
# ['119.0.0.0', '120.0.0.0', '121.0.0.0', '122.0.0.0']

platforms = UserAgentFactory.get_platforms()
print(platforms)
# ['windows', 'mac', 'linux']
```

## Global Rotator

Use a global rotator for application-wide user agent rotation:

```python
from Utilities.user_agent import get_rotator

# Get or create global rotator
rotator = get_rotator(platforms=["windows", "mac"], pool_size=20)

# Use across application
ua1 = rotator.get_next()
ua2 = rotator.get_next()
```

## User Agent Formats

### Windows
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/120.0.0.0 Safari/537.36
```

### macOS
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) 
AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/120.0.0.0 Safari/537.36
```

### Linux
```
Mozilla/5.0 (X11; Linux x86_64) 
AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/120.0.0.0 Safari/537.36
```

## Best Practices

### 1. Use Rotation for Multiple Sessions

```python
# Don't use same UA for all requests
rotator = UserAgentRotator(pool_size=10)

for session in sessions:
    ua = rotator.get_next()
    driver = create_driver(user_agent=ua)
    # ...
```

### 2. Match Platform to Your System (Optional)

```python
import platform

# Use OS-matching user agent for better consistency
system = platform.system().lower()
if system == "windows":
    ua = get_windows_user_agent()
elif system == "darwin":  # macOS
    ua = get_mac_user_agent()
else:
    ua = get_linux_user_agent()
```

### 3. Combine with Stealth Mode

```python
# User agent alone isn't enough
driver = create_driver(
    stealth_mode=True,  # Required for full anti-detection
    user_agent_platform="random"
)
```

### 4. Refresh Rotator Pool Periodically

```python
rotator = UserAgentRotator(pool_size=10)

# After N requests or time period
requests_count = 0
for request in requests:
    if requests_count % 100 == 0:
        rotator.refresh_pool()
    
    ua = rotator.get_next()
    # Make request...
    requests_count += 1
```

### 5. Log User Agents for Debugging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Factory logs generated user agents
ua = generate_user_agent("windows")
# DEBUG:Utilities.user_agent:Generated user agent: Mozilla/5.0...
```

## Advanced Usage

### Custom User Agent Pool

```python
from Utilities.user_agent import UserAgentRotator

# Create custom pool
custom_uas = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36",
    # Add your own...
]

rotator = UserAgentRotator(pool_size=0)
rotator.pool = custom_uas
```

### Session-Specific User Agents

```python
# Store user agent per session for consistency
sessions = {}

def get_session_user_agent(session_id):
    if session_id not in sessions:
        sessions[session_id] = generate_user_agent("random")
    return sessions[session_id]

# All requests for session use same UA
ua = get_session_user_agent("user_123")
driver = create_driver(user_agent=ua)
```

### Testing User Agent Detection

```python
driver = create_driver(
    stealth_mode=True,
    user_agent_platform="windows"
)

driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent")

# Check if detected user agent matches what we set
detected_ua = driver.find_element(By.ID, "detected_value").text
print(f"Detected: {detected_ua}")
```

## Integration Examples

### With Microsoft Login

```python
from Utilities.driver_factory import create_driver
from Utilities.microsoft_login import microsoft_login
from Utilities.config import Config

# Use realistic user agent for Microsoft
driver = create_driver(
    stealth_mode=Config.STEALTH_MODE,
    user_agent_platform="windows"  # Match Microsoft's typical users
)

microsoft_login(driver)
```

### With Humanize

```python
from Utilities.humanize import human_send_keys, human_click
from Utilities.user_agent import get_windows_user_agent

# Combine realistic UA with human-like behavior
driver = create_driver(
    stealth_mode=True,
    user_agent=get_windows_user_agent()
)

element = driver.find_element(By.ID, "search")
human_send_keys(element, "search query")
human_click(driver, element)
```

### Multi-Account Automation

```python
accounts = ["user1", "user2", "user3"]
rotator = UserAgentRotator(pool_size=len(accounts))

for account in accounts:
    ua = rotator.get_next()
    driver = create_driver(stealth_mode=True, user_agent=ua)
    
    # Each account appears to use different browser
    # ...
    
    driver.quit()
```

## Maintenance

### Update Chrome Versions

Edit `Utilities/user_agent.py`:

```python
# Add new versions as Chrome updates
CHROME_VERSIONS = [
    "119.0.0.0",
    "120.0.0.0",
    "121.0.0.0",
    "122.0.0.0",  # Add latest
]
```

### Add More OS Versions

```python
OS_TEMPLATES = {
    "windows": [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 11.0; Win64; x64",  # Windows 11
    ],
    # Add more variations...
}
```

## Limitations

- Only generates Chrome user agents (not Firefox, Safari, etc.)
- Limited OS version variations
- Static WebKit/Safari versions
- No mobile user agents (currently desktop only)

## Testing

Run the user agent factory directly to test:

```bash
python -m Utilities.user_agent
```

This will generate and display example user agents for each platform.

---

**Note**: User agent rotation is one part of anti-detection. Combine with stealth mode, humanize utility, and proper rate limiting for best results.
