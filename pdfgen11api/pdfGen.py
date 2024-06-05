import os
import shutil
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright
from io import BytesIO
import config

app = FastAPI()

app.mount("/static", StaticFiles(directory=config.STATIC_DIRECTORY, html=True), name="static")

@app.post("/generate_pdf")
async def generatePdfEndpoint(
    form_submit_data: UploadFile = File(...),
    form_uri: str = Query(...),
    record_id: str = Query(...),
):
    """
    Generate a PDF from the submitted form data and HTML template selected using form_uri.
    
    INPUT:
    - form_submit_data: JSON file with form submission data
    - form_uri: URI of the form template
    - record_id: Record submission ID for retrieving data and naming the output files.
    
    OUTPUT:
    - StreamingResponse with the generated PDF
    """
    try:
        # Assigning paths to variables
        _pdf_name = f'{record_id}.pdf'
        data_directory = os.path.join(config.STATIC_DIRECTORY, form_uri, config.DATA_DIRECTORY)
        data_path_name = os.path.join(data_directory, f"{record_id}.json")
        render_path = os.path.join(config.STATIC_DIRECTORY, form_uri, config.RENDER_DIRECTORY)

        # Creating directory if doesn't exist and saving the data files there
        _ensureDirectoryExists(data_directory)
        _saveDataFile(form_submit_data, data_path_name)
        _ensureDirectoryExists(render_path)

        # Assigning the url to access the webpage with populated form
        _index_html_url = config.get_index_html_url(config.PORT_NUMBER, form_uri, record_id)
        print(f"\n{_index_html_url}\n")

        # Generating the pdf using the url and saving it
        _pdf_output_path = os.path.join(render_path, _pdf_name)
        await _generatePdf(_index_html_url, _pdf_output_path)

        with open(_pdf_output_path, "rb") as f:
            _pdf_content = f.read()
        
        # Return a streaming response of generated pdf
        return StreamingResponse(BytesIO(_pdf_content), media_type="application/pdf")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

def _ensureDirectoryExists(path) -> None:
    # Ensure the specified directory exists, creating it if necessary.
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory {path} created")
    else:
        print(f"Directory {path} exists")

def _saveDataFile(upload_file: UploadFile, destination: str) -> None:
    # Save the uploaded file to the specified destination.
    try:
        with open(destination, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
    
async def _generatePdf(url: str, output_path: str) -> None: 
    # Generate a PDF from the specified HTML url and save it to the output path.
    try:
        async with async_playwright() as p:  
            browser = await p.chromium.launch(headless=True, args=["--disable-web-security"])
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await page.pdf(path=output_path)
            await browser.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {e}")

# To run the server: uvicorn pdfGen:app --host 0.0.0.0 --port 8000