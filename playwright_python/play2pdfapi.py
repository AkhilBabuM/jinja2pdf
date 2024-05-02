import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from jinja2 import Environment, Template
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

# Directory where generated PDFs will be stored
pdf_directory = "generated_pdfs"
if not os.path.exists(pdf_directory):
    os.makedirs(pdf_directory)

async def generate_pdf(html_content: str, output_filename: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html_content)
            pdf_path = os.path.join(pdf_directory, output_filename)
            await page.pdf(path=pdf_path, format='A4', print_background=True)
            await browser.close()
            return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

@app.post("/generate-pdf/")
async def create_pdf(template: UploadFile = File(...), json_data: UploadFile = File(...)):
    # Read and parse the template and JSON data
    template_data = await template.read()
    json_data = await json_data.read()
    try:
        entries = json.loads(json_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    
    # Load and render the template
    template_str = Template(template_data.decode())
    output_files = []
    for index, entry in enumerate(entries):
        html_content = template_str.render(entry)
        output_filename = f"pdf_{index+1}.pdf"
        pdf_path = await generate_pdf(html_content, output_filename)
        if pdf_path:
            output_files.append(pdf_path)
    
    if not output_files:
        raise HTTPException(status_code=500, detail="Failed to generate PDFs")
    
    return {"message": "PDFs generated successfully", "files": output_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)

# uvicorn play2pdfapi:app --reload --host 0.0.0.0 --port 5500

