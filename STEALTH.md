# Stealth Mode - Anti-Detection Guide

⚠️ **IMPORTANT**: Use responsibly and only on websites you have permission to automate. Always respect robots.txt and terms of service.

## What is Stealth Mode?

Stealth mode applies multiple techniques to make Chrome WebDriver less detectable by anti-bot systems. It's disabled by default and must be explicitly enabled.

## How to Enable

### Option 1: Via Configuration (.env)

```env
STEALTH_MODE=true
```

Then create driver normally:
```python
from Utilities.driver_factory import create_driver
from Utilities.config import Config

driver = create_driver(stealth_mode=Config.STEALTH_MODE)
```

### Option 2: Direct Parameter

```python
driver = create_driver(stealth_mode=True)
```

## Anti-Detection Techniques Applied

### 1. Navigator.webdriver Override
**Problem**: Websites can detect `navigator.webdriver === true`  
**Solution**: Override to return `undefined`

```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
```

### 2. Chrome Automation Flags
**Problem**: Chrome exposes automation-related command line flags  
**Solution**: 
- Remove `--enable-automation` flag
- Disable automation extension
- Hide infobars

```python
chrome_options.add_argument("--exclude-switches=enable-automation")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
```

### 3. User Agent Spoofing
**Problem**: Default user agent may identify as automation  
**Solution**: Use realistic Chrome user agent

```python
user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

### 4. Chrome Runtime Object
**Problem**: Missing `window.navigator.chrome` object  
**Solution**: Add realistic chrome object

```javascript
window.navigator.chrome = {
    runtime: {},
};
```

### 5. Permissions API
**Problem**: Permissions API behaves differently in automation  
**Solution**: Override to return expected values

```javascript
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);
```

### 6. Plugins Array
**Problem**: Headless Chrome has no plugins  
**Solution**: Inject realistic plugin array

```javascript
// Chrome PDF Plugin, Chrome PDF Viewer, WebKit built-in PDF
navigator.plugins = [/* realistic plugin list */]
```

### 7. Languages Array
**Problem**: Single language looks suspicious  
**Solution**: Add realistic language preferences

```javascript
navigator.languages = ['en-US', 'en']
```

### 8. WebGL Fingerprinting
**Problem**: WebGL vendor reveals automation  
**Solution**: Spoof WebGL vendor and renderer

```javascript
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    // ...
}
```

### 9. User Agent Data API
**Problem**: New API can reveal automation  
**Solution**: Inject realistic userAgentData

```javascript
navigator.userAgentData = {
    brands: [
        { brand: "Not.A/Brand", version: "8" },
        { brand: "Chromium", version: "120" },
        { brand: "Google Chrome", version: "120" }
    ],
    mobile: false,
    platform: "Windows"
}
```

### 10. Window and Frame Detection
**Problem**: iframe size detection  
**Solution**: Override offsetHeight calculations

## Detection Methods We Combat

| Detection Method | Status | How We Handle |
|-----------------|--------|---------------|
| navigator.webdriver | ✅ Fixed | Override to undefined |
| Chrome DevTools Protocol | ✅ Fixed | Disable automation flags |
| Missing plugins | ✅ Fixed | Inject realistic plugins |
| WebGL fingerprint | ✅ Fixed | Spoof vendor/renderer |
| User Agent | ✅ Fixed | Use realistic UA |
| Permissions API | ✅ Fixed | Override query method |
| Languages array | ✅ Fixed | Add multiple languages |
| Chrome object | ✅ Fixed | Add runtime object |
| userAgentData | ✅ Fixed | Inject realistic data |
| Canvas fingerprinting | ⚠️ Partial | Limited mitigation |
| Behavioral analysis | ⚠️ Partial | Use with humanize.py |
| Mouse movement patterns | ⚠️ Partial | Use with humanize.py |
| Network fingerprinting | ❌ Not handled | Use residential proxies |
| TLS fingerprinting | ❌ Not handled | System-level change needed |

## Best Practices

### 1. Combine with Humanize Utility

```python
from Utilities.humanize import human_send_keys, human_click, human_scroll

# Stealth mode + human-like interactions
driver = create_driver(stealth_mode=True)
driver.get("https://example.com")

element = driver.find_element(By.ID, "search")
human_send_keys(element, "search query")
human_click(driver, element)
human_scroll(driver, "down", 300)
```

### 2. Use Realistic Timing

```python
from Utilities.humanize import human_pause
import random

# Random delays between actions
human_pause(1.0, 3.0)

# Vary your patterns
for i in range(10):
    # Do something
    time.sleep(random.uniform(2, 5))
```

### 3. Rotate User Agents (Advanced)

```python
# Manually override user agent per session
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
    # Add more...
]

# Note: Currently driver_factory uses fixed UA
# Consider modifying for rotation
```

### 4. Use Chrome Profile

```python
# Persistent cookies and login state
driver = create_driver(
    stealth_mode=True,
    profile_dir="./chrome_profile"
)
```

### 5. Disable Headless (if possible)

```python
# Headless mode is easier to detect
driver = create_driver(
    stealth_mode=True,
    headless=False  # More stealthy
)
```

## Testing Your Stealth Setup

Visit these sites to test detection:

1. **https://bot.sannysoft.com/**  
   Comprehensive bot detection test

2. **https://arh.antoinevastel.com/bots/areyouheadless**  
   Headless Chrome detection

3. **https://abrahamjuliot.github.io/creepjs/**  
   Advanced fingerprinting test

4. **https://pixelscan.net/**  
   Canvas fingerprinting test

## What Stealth Mode CANNOT Prevent

❌ **IP-based rate limiting** - Use proxies  
❌ **CAPTCHA challenges** - Manual solving or services  
❌ **Behavioral analysis** - Need human-like patterns  
❌ **Advanced ML models** - Sophisticated detection  
❌ **Network-level detection** - TLS/HTTP2 fingerprints  
❌ **Account-based tracking** - Session monitoring  

## Limitations

- **Not foolproof**: Advanced sites may still detect automation
- **Maintenance required**: Detection methods evolve
- **Performance impact**: JavaScript injections add overhead
- **Compatibility**: May break on some sites
- **Legal responsibility**: You must comply with ToS

## Debugging Stealth Mode

Enable debug logging to see what's applied:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

driver = create_driver(stealth_mode=True)
# Check logs for "Applying stealth JavaScript patches"
```

### Check Applied Patches

```python
# In browser console after page load
console.log(navigator.webdriver);  // Should be undefined
console.log(navigator.plugins);    // Should show plugins
console.log(navigator.languages);  // Should show ['en-US', 'en']
```

## Responsible Use Guidelines

1. ✅ **DO** respect robots.txt
2. ✅ **DO** rate-limit your requests
3. ✅ **DO** identify yourself in user agent (when appropriate)
4. ✅ **DO** comply with website Terms of Service
5. ❌ **DON'T** use for scraping without permission
6. ❌ **DON'T** bypass paywalls or authentication
7. ❌ **DON'T** overwhelm servers with requests
8. ❌ **DON'T** use for malicious purposes

## When to Use Stealth Mode

**Good use cases:**
- Testing your own websites
- Authorized monitoring/testing
- Research with permission
- Personal automation of your own accounts

**Bad use cases:**
- Scraping without permission
- Bypassing security measures
- Mass data collection
- Evading rate limits

## Alternative Approaches

If stealth mode isn't enough, consider:

1. **Playwright** with stealth patches
2. **Puppeteer-extra** with stealth plugin
3. **Selenium-stealth** Python package
4. **Undetected ChromeDriver** package
5. **Residential proxies** for IP rotation
6. **Browser automation services** (Bright Data, Oxylabs)

## Further Reading

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Selenium Stealth Package](https://github.com/diprajpatra/selenium-stealth)
- [Bot Detection Research](https://antoinevastel.com/bot%20detection/2018/01/17/detect-chrome-headless-v2.html)
- [Web Scraping Legal Guide](https://benbernardblog.com/web-scraping-and-crawling-are-perfectly-legal-right/)

---

**Remember**: Just because you *can* bypass detection doesn't mean you *should*. Always prioritize ethical automation practices.
