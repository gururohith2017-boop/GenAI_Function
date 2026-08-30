from playwright.sync_api import sync_playwright
from openpyxl import Workbook


with sync_playwright() as p:

    # Open Chrome
    browser = p.chromium.launch(headless=False)

    # Create new browser page
    page = browser.new_page()

    # Open Cricbuzz
    page.goto("https://www.cricbuzz.com/")

    # Wait for page to load
    page.wait_for_timeout(5000)

    # Get all text from the page
    page_text = page.locator("body").inner_text()

    print("Cricbuzz page opened")
    print(page_text[:2000])

    # Create Excel file
    workbook = Workbook()

    # Select first sheet
    sheet = workbook.active

    # Add column headings
    sheet["A1"] = "Match Information"

    # Save some Cricbuzz text into Excel
    sheet["A2"] = page_text[:2000]

    # Save Excel file
    workbook.save("cricbuzz_score.xlsx")

    print("Score saved successfully in Excel!")

    # Close browser
    browser.close()