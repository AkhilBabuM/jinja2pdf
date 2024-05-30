import os
import subprocess
from playwright.sync_api import sync_playwright

def render_html_to_pdf(html_file, output_file):
    # Run the program to generate HTML
    generate_html_program = "genhtml.py"
    subprocess.run(["python", generate_html_program])

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
output_html_path = os.path.join(current_directory, "rendered.html")
output_pdf_path = os.path.join(current_directory, "output.pdf")

# Render prerendered HTML to PDF
render_html_to_pdf(output_html_path, output_pdf_path)
