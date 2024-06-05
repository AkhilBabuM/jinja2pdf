import os
import shutil
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from playwright.sync_api import sync_playwright
from io import BytesIO

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.post("/generate_pdf")
def generate_pdf(
    form_data: UploadFile = File(...),
    form_submit_data: UploadFile = File(...),
    # org: str = Header(...),
    form: str = Header(...),
    subid: str = Header(...)
):
    print(f"\nHeaders: form={form}, subid={subid}\n")
    print(f"Files: form_data={form_data.filename}, form_submit_data={form_submit_data.filename}\n")
    
    render_dir = 'renders'
    staticdir = 'static'
    pdf_name = f'{subid}.pdf'

    subid_dir = os.path.join(staticdir, form, subid)

    form_data_path = os.path.join(subid_dir, 'form_data.json')
    form_submit_data_path = os.path.join(subid_dir, 'form_submit_data.json')
    # form_data_path = os.path.join(staticdir, form, subid_dir, 'form_data.json')
    # form_submit_data_path = os.path.join(staticdir, form, subid_dir, 'form_submit_data.json')

    print(f"form data path {form_data_path}")
    print(f"form submit data path {form_submit_data_path}")

    try:
        if not os.path.exists(subid_dir):
            os.makedirs(subid_dir)
            print(f"Directory {subid_dir} created")
            with open(form_data_path, 'wb') as f:
                shutil.copyfileobj(form_data.file, f)
            with open(form_submit_data_path, 'wb') as f:
                shutil.copyfileobj(form_submit_data.file, f)
        else: 
            print("Directory already exists")

        index_html_url = f'http://127.0.0.1:8000/static/{form}/index.html?subid={subid}'
        print(f'\n{index_html_url}\n')


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
        if False and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("PDF Saved and sent\n")

# uvicorn app:app --host 0.0.0.0 --port 8000
