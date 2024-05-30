import os
import threading
import time
from flask import Flask, send_from_directory, request
from playwright.sync_api import sync_playwright
import zipfile

app = Flask(__name__)

# Directory where the unzipped files will be served from
unzip_dir = 'temp'

@app.route('/')
def index():
    return send_from_directory(unzip_dir, 'index.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'Server shutting down...'

def unzip_file():
    print("Unzipping files...")
    with zipfile.ZipFile('Archive.zip', 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)
    print("Files unzipped successfully.")

def run_flask():
    app.run(port=8003)

def generate_pdf():
    unzip_file()

    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    # Use Playwright to navigate to the Flask server URL and generate the PDF
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8003/')
        print('Rendering webpage')
        time.sleep(3)  # Allow the page to fully load
        print('Rendering pdf')
        page.pdf(path='../form5.pdf')
        print('Saved form.pdf')
        browser.close()

    # Stop the Flask server
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8003/shutdown', wait_until='networkidle')

    server_thread.join()

if __name__ == '__main__':
    generate_pdf()
