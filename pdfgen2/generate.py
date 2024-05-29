import zipfile
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    # Unzip the files
    with zipfile.ZipFile('zipped.zip', 'r') as zip_ref:
        zip_ref.extractall('temp_dir')

    # Load HTML content from the extracted folder
    html_file_path = Path('temp_dir/index.html')
    if html_file_path.exists():
        with open(html_file_path, 'r') as html_file:
            html_content = html_file.read()
    else:
        print("HTML file not found.")
        return

    # Load JSON data
    with open('form_data.json', 'r') as form_data_file:
        form_data = json.load(form_data_file)

    # Render HTML using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        await page.wait_for_load_state("networkidle")
        await page.pdf(path='rendered_form.pdf')
        await browser.close()

    print("HTML rendered and saved as PDF.")

if __name__ == '__main__':
    asyncio.run(main())