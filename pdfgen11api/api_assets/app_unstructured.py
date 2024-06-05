import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from playwright.sync_api import sync_playwright
from io import BytesIO
import config

app = FastAPI()

app.mount("/static", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")


@app.post("/generate_pdf")
def generate_pdf(
    form_submit_data: UploadFile = File(...),
    form_uri: str = Query(...),
    sub_id: str = Query(...),
):
    print(f"\nHeaders: form={form_uri}, sub_id={sub_id}\n")
    print(f"Files: form_submit_data={form_submit_data.filename}\n")

    pdf_name = config.generate_pdf_name(sub_id)
    data_dir = os.path.join(config.STATIC_DIR, form_uri, "data")
    form_submit_data_path = os.path.join(data_dir, f"{sub_id}.json")
    render_dir_path = os.path.join(config.STATIC_DIR, form_uri, config.RENDER_DIR)

    print(f"form submit data path {form_submit_data_path}")

    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Directory {data_dir} created")
        else:
            print("Data Directory already exists")

        with open(form_submit_data_path, "wb") as f:
            shutil.copyfileobj(form_submit_data.file, f)

        if not os.path.exists(render_dir_path):
            os.makedirs(render_dir_path)
            print(f"Directory {render_dir_path} created")
        else:
            print("Render Directory already exists")

        index_html_url = config.get_index_html_url(config.PORT_NUMBER, form_uri, sub_id)
        print(f"\n{index_html_url}\n")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
            page = browser.new_page()
            page.goto(index_html_url)
            page.wait_for_load_state("networkidle")
            page.pdf(path=f"{render_dir_path}/{pdf_name}")
            browser.close()

        with open(f"{render_dir_path}/{pdf_name}", "rb") as f:
            pdf_content = f.read()
        return StreamingResponse(BytesIO(pdf_content), media_type="application/pdf")

    finally:
        print("PDF Saved and sent\n")


# uvicorn app:app --host 0.0.0.0 --port 8000
