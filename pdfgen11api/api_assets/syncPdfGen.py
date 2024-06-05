import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from playwright.sync_api import sync_playwright
from io import BytesIO
import config

app = FastAPI()

app.mount("/static", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")

def _ensureDirectoryExists(path) -> None:
    """
    Ensure the specified directory exists, creating it if necessary.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory {path} created")
    else:
        print(f"Directory {path} exists")

def _saveDataFile(upload_file: UploadFile, destination: str) -> None:
    """
    Save the uploaded file to the specified destination.
    """
    try:
        with open(destination, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
    
def _generatePdf(url: str, output_path: str) -> None:
    """
    Generate a PDF from the specified HTML URL and save it to the output path.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.pdf(path=output_path)
            browser.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {e}")

@app.post("/generate_pdf")
def generatePdfEndpoint(
    form_submit_data: UploadFile = File(...),
    form_uri: str = Query(...),
    sub_id: str = Query(...),
):
    """
    Generate a PDF from the submitted form data and HTML template selected using form_uri.
    
    Parameters:
    - form_submit_data: JSON file with form submission data
    - form_uri: URI of the form template
    - sub_id: Submission ID for naming the output files
    
    Returns:
    - StreamingResponse with the generated PDF
    """
    try:
        _pdf_name = f'{sub_id}.pdf'
        data_directory = os.path.join(config.STATIC_DIR, form_uri, "data")
        data_path_name = os.path.join(data_directory, f"{sub_id}.json")
        render_path = os.path.join(config.STATIC_DIR, form_uri, config.RENDER_DIR)

        _ensureDirectoryExists(data_directory)
        _saveDataFile(form_submit_data, data_path_name)
        _ensureDirectoryExists(render_path)

        _index_html_url = config.get_index_html_url(config.PORT_NUMBER, form_uri, sub_id)
        print(f"\n{_index_html_url}\n")

        _pdf_output_path = os.path.join(render_path, _pdf_name)
        _generatePdf(_index_html_url, _pdf_output_path)

        with open(_pdf_output_path, "rb") as f:
            _pdf_content = f.read()

        return StreamingResponse(BytesIO(_pdf_content), media_type="application/pdf")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# To run the server: uvicorn app:app --host 0.0.0.0 --port 8000