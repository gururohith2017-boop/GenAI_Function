import pyautogui
import time

print("Screenshot will be taken in 5 seconds...")

time.sleep(5)

screenshot = pyautogui.screenshot()

screenshot.save("screenshot.png")

print("Screenshot saved successfully!")


from datetime import datetime

filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")

screenshot = pyautogui.screenshot()
screenshot.save(filename)

print("Screenshot saved as:", filename)