import os
import subprocess
from zipfile import ZipFile
from pathlib import Path
from playwright.sync_api import sync_playwright

def unzip_file(zip_file, extract_to):
    with ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def render_html_to_pdf(html_file, output_file):
    # Continue with rendering HTML to PDF
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f'file://{html_file}')
        page.wait_for_load_state("networkidle")

        page.pdf(path=output_file)

        browser.close()

# Example usage
current_directory = os.getcwd()
zip_file_path = os.path.join(current_directory, "zip_file.zip")
extracted_dir_path = os.path.join(current_directory, "extracted_dir")
html_template_path = os.path.join(extracted_dir_path, "index.html")
output_html_path = os.path.join(current_directory, "html", "rendered.html")
output_pdf_path = os.path.join(current_directory, "pdfs", "output.pdf")

# Unzip the file
unzip_file(zip_file_path, extracted_dir_path)

# Run genhtml.py to generate HTML
genhtml_program = os.path.join(extracted_dir_path, "genhtml.py")
subprocess.run(["python", genhtml_program])

# Render prerendered HTML to PDF
render_html_to_pdf(output_html_path, output_pdf_path)

# Move rendered files to respective directories
os.rename(output_html_path, output_html_path)  # Move rendered HTML
os.rename(output_pdf_path, output_pdf_path)  # Move rendered PDF

print("HTML and PDF rendered successfully.")
