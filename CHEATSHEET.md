# Selenium WebDriver Cheatsheet

## Setup

```python
from Driver import create_driver

driver = create_driver(
    headless=False,
    profile_dir=None,
    download_dir="./Outputs/Downloads"
)
```

## Navigation

```python
driver.get("https://example.com")
driver.back()
driver.forward()
driver.refresh()
driver.current_url
driver.title
```

## Finding Elements

```python
from selenium.webdriver.common.by import By

# Single element
driver.find_element(By.ID, "element_id")
driver.find_element(By.NAME, "element_name")
driver.find_element(By.CLASS_NAME, "class_name")
driver.find_element(By.TAG_NAME, "tag_name")
driver.find_element(By.CSS_SELECTOR, "div.class")
driver.find_element(By.XPATH, "//div[@id='example']")
driver.find_element(By.LINK_TEXT, "Click here")
driver.find_element(By.PARTIAL_LINK_TEXT, "Click")

# Multiple elements
elements = driver.find_elements(By.CLASS_NAME, "item")
```

## Interacting with Elements

```python
element = driver.find_element(By.ID, "submit")

element.click()
element.send_keys("text to type")
element.clear()
element.submit()
element.text                    # Get text content
element.get_attribute("href")   # Get attribute value
element.is_displayed()
element.is_enabled()
element.is_selected()
```

## Waits

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Explicit wait
wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.ID, "element_id"))
)

# Common conditions
EC.presence_of_element_located((By.ID, "id"))
EC.visibility_of_element_located((By.ID, "id"))
EC.element_to_be_clickable((By.ID, "id"))
EC.title_contains("text")
EC.url_contains("text")

# Implicit wait (global default)
driver.implicitly_wait(10)
```

## Dropdowns

```python
from selenium.webdriver.support.ui import Select

dropdown = Select(driver.find_element(By.ID, "dropdown_id"))
dropdown.select_by_visible_text("Option Text")
dropdown.select_by_value("option_value")
dropdown.select_by_index(0)
```

## Alerts

```python
alert = driver.switch_to.alert
alert.text          # Get alert text
alert.accept()      # Click OK
alert.dismiss()     # Click Cancel
alert.send_keys("text")  # Type in alert
```

## Windows & Tabs

```python
# Get current window handle
current_window = driver.current_window_handle

# Get all window handles
windows = driver.window_handles

# Switch to window
driver.switch_to.window(windows[1])

# Open new tab (execute script)
driver.execute_script("window.open('');")
driver.switch_to.window(driver.window_handles[-1])

# Close current window
driver.close()
```

## Frames

```python
# Switch to frame
driver.switch_to.frame("frame_name")
driver.switch_to.frame(0)  # By index
driver.switch_to.frame(driver.find_element(By.ID, "frame_id"))

# Switch back to main content
driver.switch_to.default_content()

# Switch to parent frame
driver.switch_to.parent_frame()
```

## JavaScript Execution

```python
# Execute script
driver.execute_script("alert('Hello');")

# Return value
result = driver.execute_script("return document.title;")

# Scroll
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.execute_script("arguments[0].scrollIntoView();", element)

# Click (bypass overlays)
driver.execute_script("arguments[0].click();", element)
```

## Screenshots

```python
driver.save_screenshot("screenshot.png")
element.screenshot("element.png")
```

## Cookies

```python
# Get all cookies
cookies = driver.get_cookies()

# Get specific cookie
driver.get_cookie("cookie_name")

# Add cookie
driver.add_cookie({"name": "key", "value": "value"})

# Delete cookie
driver.delete_cookie("cookie_name")
driver.delete_all_cookies()
```

## Common Patterns

### Wait and Click

```python
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "button_id"))
)
element.click()
```

### Fill Form

```python
driver.find_element(By.ID, "username").send_keys("user@example.com")
driver.find_element(By.ID, "password").send_keys("password123")
driver.find_element(By.ID, "submit").click()
```

### Handle Stale Element

```python
from selenium.common.exceptions import StaleElementReferenceException

try:
    element.click()
except StaleElementReferenceException:
    element = driver.find_element(By.ID, "element_id")
    element.click()
```

### Check if Element Exists

```python
from selenium.common.exceptions import NoSuchElementException

try:
    element = driver.find_element(By.ID, "element_id")
    print("Element exists")
except NoSuchElementException:
    print("Element not found")
```

## Cleanup

```python
driver.quit()  # Close browser and end session
```
