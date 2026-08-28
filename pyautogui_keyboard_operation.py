import pyautogui
import time

# Open Windows Run
pyautogui.hotkey('win', 'r')

# Wait for Run window
time.sleep(1)

# Type Notepad
pyautogui.write('notepad', interval=0.1)

# Press Enter
pyautogui.press('enter')

# Wait for Notepad to open
time.sleep(2)

# Type first message
pyautogui.write(
    'Hello, this is an automated message!',
    interval=0.1
)

# Press Enter
pyautogui.press('enter')

# Type second message
pyautogui.write(
    'This message was sent using PyAutoGUI.',
    interval=0.1
)