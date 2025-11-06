# Humanize Utility

Make browser interactions appear more human-like to avoid detection.

## Features

### 🎯 Human Typing
- Variable typing speed between characters
- Occasional typos with corrections
- Pauses between words
- Natural rhythm

### 🖱️ Human Clicking
- Mouse movement to element
- Random offset clicks
- Delays before/after clicks
- Curved mouse paths

### 📜 Human Scrolling
- Multiple small scrolls (not one big jump)
- Random pauses between steps
- Natural acceleration/deceleration
- Smooth motion

### ⏸️ Random Pauses
- Configurable delay ranges
- Realistic timing between actions

## Quick Reference

```python
from Utilities.humanize import (
    human_send_keys,
    human_click,
    human_scroll,
    human_pause,
    human_mouse_move,
    human_form_fill
)

# Type like a human (with typos!)
element = driver.find_element(By.ID, "search")
human_send_keys(element, "search query")

# Click with mouse movement
button = driver.find_element(By.ID, "submit")
human_click(driver, button)

# Scroll naturally
human_scroll(driver, "down", amount=500)
human_scroll(driver, "top")  # Scroll to top
human_scroll(driver, "bottom")  # Scroll to bottom

# Random pause
human_pause()  # 0.5-2.0 seconds
human_pause(1.0, 3.0)  # Custom range

# Move mouse naturally
human_mouse_move(driver, element)

# Fill entire form
human_form_fill(driver, {
    "username": (username_field, "user@example.com"),
    "password": (password_field, "SecurePass123"),
    "submit": submit_button
})
```

## Configuration

Customize behavior in `Utilities/humanize.py`:

```python
class HumanizeConfig:
    # Typing speed (seconds per character)
    TYPING_SPEED_MIN = 0.05
    TYPING_SPEED_MAX = 0.15
    
    # Click delays
    CLICK_DELAY_MIN = 0.1
    CLICK_DELAY_MAX = 0.5
    
    # Typo probability (0.0 to 1.0)
    TYPO_PROBABILITY = 0.02
    
    # And more...
```

## Examples

### Google Search

```python
# Navigate and wait
driver.get("https://www.google.com")
human_pause(1.0, 2.0)

# Type search query with human behavior
search_box = driver.find_element(By.NAME, "q")
human_send_keys(search_box, "Python Selenium")
human_pause()

# Submit and scroll
search_box.submit()
human_pause()
human_scroll(driver, "down", amount=300)
```

### Form Login

```python
# Find form elements
email = driver.find_element(By.ID, "email")
password = driver.find_element(By.ID, "password")
submit = driver.find_element(By.ID, "submit")

# Fill form naturally
human_form_fill(driver, {
    "email": (email, "user@example.com"),
    "password": (password, "SecurePassword"),
    "submit": submit
})
```

### Custom Typing

```python
# Adjust typo probability and speed
human_send_keys(
    element,
    "Fast typing with no typos",
    typo_probability=0.0,
    typing_speed_range=(0.02, 0.05)
)
```

## How It Works

### Typing Simulation
1. Splits text into words
2. Types each character with random delay
3. Occasionally makes typos (nearby keys)
4. Realizes mistake and corrects with backspace
5. Pauses between words

### Click Simulation
1. Moves mouse to element in curved path
2. Adds random offset (±5 pixels)
3. Pauses before clicking
4. Performs click
5. Short pause after click

### Scroll Simulation
1. Calculates total distance
2. Breaks into 5-15 steps
3. Each step has slight variation
4. Random pauses between steps
5. Natural acceleration curve

## Tips

- **Use with caution**: Some sites may still detect automation
- **Adjust config**: Tune timing for your specific needs
- **Combine methods**: Use multiple humanize functions together
- **Test locally**: Verify behavior before production use
- **Random seeds**: Consider setting random seed for reproducible testing

## Anti-Detection Features

✅ Variable timing (not robotic)  
✅ Typo simulation (humans make mistakes)  
✅ Curved mouse paths (not straight lines)  
✅ Random offsets (not pixel-perfect)  
✅ Natural scrolling (not instant jumps)  
✅ Realistic pauses (not constant delays)  

**Note**: While these techniques make automation more human-like, they don't guarantee undetectability. Always respect website terms of service and robots.txt files.
