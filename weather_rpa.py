import pyautogui
import time

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1

# ------------------------------------------------
# STEP 1: Open Chrome
# ------------------------------------------------

pyautogui.hotkey("win", "r")
pyautogui.write("chrome")
pyautogui.press("enter")

time.sleep(3)

# ------------------------------------------------
# STEP 2: Open Weather website
# ------------------------------------------------

pyautogui.hotkey("ctrl", "l")

pyautogui.write(
    "https://www.google.com/search?q=Madurai+weather"
)

pyautogui.press("enter")

time.sleep(5)

# ------------------------------------------------
# STEP 3: Take screenshot of weather report
# ------------------------------------------------

pyautogui.screenshot("weather_report.png")

# ------------------------------------------------
# STEP 4: Open Notepad
# ------------------------------------------------

pyautogui.hotkey("win", "r")
pyautogui.write("notepad")
pyautogui.press("enter")

time.sleep(2)

# ------------------------------------------------
# STEP 5: Enter weather information
# ------------------------------------------------

weather_data = """
WEATHER REPORT
==============

Location : Madurai

Weather information checked from Google Weather.

Screenshot saved as:
weather_report.png
"""

pyautogui.write(weather_data)

# ------------------------------------------------
# STEP 6: Save Notepad file
# ------------------------------------------------

pyautogui.hotkey("ctrl", "s")

time.sleep(2)

pyautogui.write("weather_report.txt")

pyautogui.press("enter")

time.sleep(2)

# ------------------------------------------------
# STEP 7: Take screenshot of Notepad
# ------------------------------------------------

pyautogui.screenshot("weather_notepad.png")

print("Weather RPA completed successfully!")
print("Weather screenshot : weather_report.png")
print("Notepad screenshot : weather_notepad.png")
print("Report saved        : weather_report.txt")