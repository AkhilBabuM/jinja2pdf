import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright
from io import BytesIO
import config

class PDFGenerator:
    def __init__(self):
        self.app = FastAPI()
        # Starting server for static files
        self.app.mount("/static", StaticFiles(directory=config.STATIC_DIRECTORY, html=True), name="static")

    def _run_server(self, host="0.0.0.0", port=8000):
        # Run the FastAPI server
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

    @staticmethod
    def _ensure_directory_exists(path):
        # Ensure the specified directory exists, creating it if necessary.
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory {path} created")
        else:
            print(f"Directory {path} exists")

    @staticmethod
    def _save_data_file(json_data: str, destination: str):
        # Save the JSON string to the specified destination as a JSON file.
        try:
            with open(destination, "w") as f:
                json.dump(json.loads(json_data), f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    @staticmethod
    async def _generate_pdf(url: str, output_path: str):
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

    def generate_pdf_endpoint(self):
        @self.app.post("/generate_pdf")
        async def generate_pdf_endpoint(
            form_submit_data: str = Form(...),
            form_uri: str = Query(...),
            record_id: str = Query(...),
        ):
            """
            Generate a PDF from the submitted form data and HTML template selected using form_uri.

            INPUT:
            - form_submit_data: JSON string with form submission data
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
                self._ensure_directory_exists(data_directory)
                self._save_data_file(form_submit_data, data_path_name)
                self._ensure_directory_exists(render_path)

                # Assigning the url to access the webpage with populated form
                _index_html_url = config.get_index_html_url(config.PORT_NUMBER, form_uri, record_id)
                print(f"\n{_index_html_url}\n")

                # Generating the pdf using the url and saving it
                _pdf_output_path = os.path.join(render_path, _pdf_name)
                await self._generate_pdf(_index_html_url, _pdf_output_path)

                with open(_pdf_output_path, "rb") as f:
                    _pdf_content = f.read()

                # Return a streaming response of generated pdf
                return StreamingResponse(BytesIO(_pdf_content), media_type="application/pdf")

            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Usage
pdf_generator = PDFGenerator()
pdf_generator.generate_pdf_endpoint()
pdf_generator._run_server()
