import os
from playwright.sync_api import sync_playwright
import zipfile
import shutil

zip_file = 'Archive_min.zip'
extract_directory = 'temp'
page_html = 'index.html'
pdf_name = 'form_output.pdf'

data_directory = 'data'
form_data = 'form_data.json'
form_submit_data = 'form_submit_data.json'

def unzip_file():
    print("Unzipping files...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
      zip_ref.extractall(extract_directory)
    print("Files unzipped successfully.")

def copy_data():
    print("Copying Data files to the temp directory...")
    shutil.copy(os.path.join(data_directory, form_data), os.path.join(extract_directory, form_data))
    shutil.copy(os.path.join(data_directory, form_submit_data), os.path.join(extract_directory, form_submit_data))
    print("Data files copied successfully.")

def decimate():
    print("Deleting the temp directory...")
    shutil.rmtree(extract_directory)
    print("Temp directory deleted successfully.")

def generate_pdf():
    unzip_file()
    copy_data()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-web-security"])
        page = browser.new_page()
        current_directory = os.getcwd()
        index_html_path = os.path.join(current_directory, extract_directory, page_html)
        index_html_url = f'file://{index_html_path}'
        page.goto(index_html_url)
        print('Rendering webpage')
        # time.sleep(0.5)
        page.wait_for_load_state('networkidle')
        print('Rendering pdf')
        page.pdf(path=f'renders/{pdf_name}')
        print(f'Saved {pdf_name}')
        browser.close()
    decimate()

generate_pdf()