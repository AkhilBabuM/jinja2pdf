from playwright.sync_api import sync_playwright
import time

def generate_pdf(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(3)
        page.pdf(path='output.pdf')
        browser.close()

generate_pdf('http://127.0.0.1:5501/pdfgen6/temp/index.html')
