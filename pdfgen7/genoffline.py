import os
from playwright.sync_api import sync_playwright
import zipfile

def unzip_file():
    print("Unzipping files...")
    with zipfile.ZipFile('Archive.zip', 'r') as zip_ref:
      zip_ref.extractall('temp')
    print("Files unzipped successfully.")

def generate_pdf():
    unzip_file()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-web-security"])
        page = browser.new_page()
        current_directory = os.getcwd()
        index_html_path = os.path.join(current_directory, 'temp', 'index.html')
        index_html_url = f'file://{index_html_path}'
        page.goto(index_html_uxrl)
        print('Rendering webpage')
        # time.sleep(0.5)
        page.wait_for_load_state('networkidle')
        print('Rendering pdf')
        page.pdf(path='formoffline.pdf')
        print('Saved formoffline.pdf')
        browser.close()

generate_pdf()
