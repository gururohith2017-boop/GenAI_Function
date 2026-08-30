from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://playwright.dev")
    page.screenshot(path="playwright_screenshot.png")
    browser.close()
#navigation
page.goto("https://playwright.dev/docs/intro")
page.screenshot(path="playwright_screenshot2.png")
  