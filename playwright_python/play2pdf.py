import asyncio
import os
import json
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

directory_name = "renders"
template_name = "t1simple.html"
data_name = "data1.json"

if not os.path.exists(directory_name):
    os.makedirs(directory_name)

async def generate_pdf(html_content, output_filename):
    async with async_playwright() as p:
        try:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Set content and generate PDF
            await page.set_content(html_content)
            output_name = os.path.join(directory_name, output_filename)
            await page.pdf(path=output_name, format='A4', print_background=True)
            
            await browser.close()
            print(f"Successfully generated PDF: {output_name}")
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

async def main():
    # Load JSON data
    with open(data_name, "r") as file:
        entries = json.load(file)

    # Load and render template
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template_name)

    tasks = []
    for index, entry in enumerate(entries):
        html_out = template.render(entry)
        pdf_filename = f'{template_name}_{index+1}_{entry.get("form_id", "unknown")}.pdf'
        task = asyncio.create_task(generate_pdf(html_out, pdf_filename))
        tasks.append(task)

    await asyncio.gather(*tasks)

# Run the main function in the asyncio event loop
asyncio.run(main())
