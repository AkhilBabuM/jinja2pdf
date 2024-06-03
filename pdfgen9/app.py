import os
import shutil
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import StreamingResponse
from playwright.sync_api import sync_playwright
from io import BytesIO

app = FastAPI()
delete_temp = False

@app.post("/generate_pdf")
def generate_pdf(
    zip_file: UploadFile = File(...),
    form_data: UploadFile = File(...),
    form_submit_data: UploadFile = File(...),
    org: str = Header(...),
    form: str = Header(...),
    subid: str = Header(...)
):
    print(f"Headers: org={org}, form={form}, subid={subid}")
    print(f"Files: zip_file={zip_file.filename}, form_data={form_data.filename}, form_submit_data={form_submit_data.filename}")
    
    temp_dir = 'temp'
    extracted_dir = 'extracted'
    render_dir = 'renders'
    pdf_name = f'{subid}.pdf'

    extracted_dir = os.path.join(temp_dir, extracted_dir)
    subid_dir = os.path.join(temp_dir, subid)

    zip_file_path = os.path.join(temp_dir, zip_file.filename)
    form_data_path = os.path.join(subid_dir, form_data.filename)
    form_submit_data_path = os.path.join(subid_dir, form_submit_data.filename)

    try:
        # Create necessary directories
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if not os.path.exists(extracted_dir):
            os.makedirs(extracted_dir)
        if not os.path.exists(subid_dir):
            os.makedirs(subid_dir)

        print("created directories")

        # Save uploaded files to disk
        with open(zip_file_path, 'wb') as f:
            shutil.copyfileobj(zip_file.file, f)
        with open(form_data_path, 'wb') as f:
            shutil.copyfileobj(form_data.file, f)
        with open(form_submit_data_path, 'wb') as f:
            shutil.copyfileobj(form_submit_data.file, f)

        shutil.unpack_archive(zip_file_path, extracted_dir)

        shutil.copy(form_data_path, extracted_dir)
        shutil.copy(form_submit_data_path, extracted_dir)

        index_html_path = os.path.join(os.getcwd(), extracted_dir, 'index.html')
        index_html_url = f'http://127.0.0.1:5501/pdfgen9/webserve/index.html?org={org}&form={form}&subid={subid}'
        print(index_html_url)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
            page = browser.new_page()
            page.goto(index_html_url)
            page.wait_for_load_state('networkidle')
            if not os.path.exists(render_dir):
                os.makedirs(render_dir)
            page.pdf(path=f'{render_dir}/{pdf_name}')
            browser.close()

        with open(f'{render_dir}/{pdf_name}', 'rb') as f:
            pdf_content = f.read()
        return StreamingResponse(BytesIO(pdf_content), media_type='application/pdf')

    finally:
        if delete_temp and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("PDF Saved and sent")

# uvicorn app:app --host 0.0.0.0 --port 8000
