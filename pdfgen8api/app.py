import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from playwright.sync_api import sync_playwright
from io import BytesIO
import time

app = FastAPI()



@app.post("/generate_pdf")
def generate_pdf(zip_file: UploadFile = File(...), form_data: UploadFile = File(...), form_submit_data: UploadFile = File(...)):
    temp_dir = 'temp'
    extracted_dir = 'extracted'
    render_dir = 'renders'
    pdf_name = 'form_output.pdf'
    extracted_dir = os.path.join(temp_dir, extracted_dir)
    zip_file_path = os.path.join(temp_dir, zip_file.filename)
    form_data_path = os.path.join(temp_dir, form_data.filename)
    form_submit_data_path = os.path.join(temp_dir, form_submit_data.filename)

    try:
        # Create temp directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if not os.path.exists(extracted_dir):
            os.makedirs(extracted_dir)

        # Save uploaded files
        with open(zip_file_path, 'wb') as f:
            shutil.copyfileobj(zip_file.file, f)
        with open(form_data_path, 'wb') as f:
            shutil.copyfileobj(form_data.file, f)
        with open(form_submit_data_path, 'wb') as f:
            shutil.copyfileobj(form_submit_data.file, f)

        # Unzip the zip file
        shutil.unpack_archive(zip_file_path, extracted_dir)

        # Copy JSON files to extracted directory
        shutil.copy(form_data_path, extracted_dir)
        shutil.copy(form_submit_data_path, extracted_dir)

        # Construct index_html_path with cwd
        index_html_path = os.path.join(os.getcwd(), extracted_dir, 'index.html')
        index_html_url = f'file://{index_html_path}'

        # Run Playwright Async API to generate PDF
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch(headless=True)
        #     page = await browser.new_page()
        #     await page.goto(index_html_url)
        #     await page.wait_for_load_state('networkidle')
        #     await page.pdf(path=f'{extracted_dir}/form_output.pdf')
        #     await browser.close()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-web-security"])
            page = browser.new_page()
            page.goto(index_html_url)
            print('Rendering webpage')
            # time.sleep(2)
            page.wait_for_load_state('networkidle')
            print('Rendering pdf')
            page.pdf(path=f'{render_dir}/{pdf_name}')
            print(f'Saved {pdf_name}')
            browser.close()

        # Return the generated PDF
        with open(f'{render_dir}/form_output.pdf', 'rb') as f:
            pdf_content = f.read()
        return StreamingResponse(BytesIO(pdf_content), media_type='application/pdf')


    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
