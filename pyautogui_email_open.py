import pyautogui
import time
import pyscreeze

# Open Gmail
pyautogui.hotkey('win', 'r')
time.sleep(1)

pyautogui.write('chrome', interval=0.1)
pyautogui.press('enter')

time.sleep(3)

# Open Gmail
pyautogui.write('https://mail.google.com', interval=0.05)
pyautogui.press('enter')

time.sleep(5)
screenshot = pyautogui.screenshot()
screenshot.save('gmail_screenshot.png')