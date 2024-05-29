from playwright.async_api import async_playwright
import os
import asyncio

async def render_html_to_pdf(html_file, output_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Load HTML file
            await page.goto(f'file://{html_file}')

            # Wait for specific elements or conditions before PDF generation
            # await page.wait_for_selector('.some-element-class')  # Replace with actual selector

            # Inject custom JavaScript using addScriptTag
            await page.add_script_tag(path='script.js')  # Path to your custom JavaScript file

            await page.wait_for_timeout(5000)  # Wait for additional time if needed
            # Export as PDF
            await page.pdf(path=output_file)
            print("PDF exported successfully.")
        except Exception as e:
            print(f"Error rendering PDF: {e}")
        finally:
            await browser.close()

# Example usage
async def main():
    current_directory = os.getcwd()
    html_file = os.path.join(current_directory, "index.html")
    output_file = "output.pdf"

    await render_html_to_pdf(html_file, output_file)

# Run the main function
asyncio.run(main())