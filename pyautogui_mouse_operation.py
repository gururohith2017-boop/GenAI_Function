import pyautogui
import time

pyautogui.moveTo(10, 10, duration=1)
pyautogui.click() 
pyautogui.rightClick()  # Right-click   
pyautogui.move(50, 0, duration=1) 
pyautogui.leftClick()  # Left-click at the current position
pyguiautogui.doubleClick()  # Double-click at the current position
pyautogui.dragTo(40, 40, duration=1)  # Drag the mouse to (400, 400)
pyautogui.scroll(-50)  # Scroll up
pyautogui.scroll(50)  # Scroll down