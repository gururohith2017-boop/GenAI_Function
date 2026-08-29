import pyautogui
import pyperclip
import time
from datetime import datetime
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1

# Project folder
PROJECT_FOLDER = Path.cwd()

# Current date and time
now = datetime.now()

current_date = now.strftime("%Y-%m-%d")
current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

# Output filenames
excel_filename = f"daily_report_{current_date}.xlsx"
screenshot_filename = f"daily_report_{current_date}.png"

excel_path = PROJECT_FOLDER / excel_filename
screenshot_path = PROJECT_FOLDER / screenshot_filename


# ============================================================
# STEP 1 - OPEN CHROME
# ============================================================

print("Step 1: Opening Chrome...")

pyautogui.hotkey("win", "r")
time.sleep(1)

pyautogui.write("chrome")
pyautogui.press("enter")

time.sleep(5)


# ============================================================
# STEP 2 - OPEN PUBLIC WEATHER WEBSITE
# ============================================================

print("Step 2: Opening weather website...")

pyautogui.hotkey("ctrl", "l")

# Public weather website
weather_url = "https://wttr.in/Madurai?format=Madurai:+%c+%t"

pyautogui.write(weather_url)
pyautogui.press("enter")

time.sleep(7)


# ============================================================
# STEP 3 - COPY WEATHER DATA
# ============================================================

print("Step 3: Copying weather information...")

# Select everything visible on the webpage
pyautogui.hotkey("ctrl", "a")

# Copy selected text
pyautogui.hotkey("ctrl", "c")

time.sleep(2)

# Read clipboard
weather_data = pyperclip.paste()

print("Weather data received:")
print(weather_data)


# ============================================================
# STEP 4 - CLEAN WEATHER DATA
# ============================================================

weather_data = weather_data.strip()

if not weather_data:
    weather_data = "Weather data could not be fetched"


# ============================================================
# STEP 5 - CREATE COMMENT
# ============================================================

if "rain" in weather_data.lower():
    comment = "Carry an umbrella"
else:
    comment = "Good for outdoor activities"


# ============================================================
# STEP 6 - OPEN MICROSOFT EXCEL
# ============================================================

print("Step 4: Opening Microsoft Excel...")

pyautogui.hotkey("win", "r")
time.sleep(1)

pyautogui.write("excel")
pyautogui.press("enter")

time.sleep(7)


# ============================================================
# STEP 7 - CREATE NEW WORKBOOK
# ============================================================

print("Step 5: Creating Excel report...")

# Excel normally opens a new blank workbook.
# Wait for Excel to be ready.
time.sleep(2)


# ============================================================
# STEP 8 - ENTER HEADERS
# ============================================================

headers = "Date & Time\tWeather\tComment"

pyperclip.copy(headers)

pyautogui.hotkey("ctrl", "v")

pyautogui.press("enter")


# ============================================================
# STEP 9 - ENTER REPORT DATA
# ============================================================

row_data = f"{current_datetime}\t{weather_data}\t{comment}"

pyperclip.copy(row_data)

pyautogui.hotkey("ctrl", "v")

time.sleep(2)


# ============================================================
# STEP 10 - SAVE EXCEL FILE
# ============================================================

print("Step 6: Saving Excel file...")

pyautogui.hotkey("ctrl", "shift", "s")

time.sleep(4)


# Type complete file path
pyperclip.copy(str(excel_path))

pyautogui.hotkey("ctrl", "v")

time.sleep(1)

pyautogui.press("enter")

time.sleep(5)


# ============================================================
# STEP 11 - HANDLE POSSIBLE EXCEL CONFIRMATION
# ============================================================

# Sometimes Excel may display a confirmation dialog.
# Press Enter to accept if one appears.

pyautogui.press("enter")

time.sleep(3)


# ============================================================
# STEP 12 - TAKE SCREENSHOT OF FINAL EXCEL SHEET
# ============================================================

print("Step 7: Taking screenshot...")

pyautogui.screenshot(str(screenshot_path))

time.sleep(2)


# ============================================================
# STEP 13 - FINAL MESSAGE
# ============================================================

print()
print("=" * 60)
print("DAILY REPORT BOT COMPLETED SUCCESSFULLY")
print("=" * 60)

print("Date & Time :", current_datetime)
print("Weather     :", weather_data)
print("Comment     :", comment)
print()
print("Excel file  :", excel_path)
print("Screenshot  :", screenshot_path)
print("=" * 60)