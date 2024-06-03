from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:5501/pdfgen8api/assets/to_zip/")
    print(page.title())
    page.wait_for_load_state('networkidle')
    page.pdf(path='test.pdf')
    browser.close()