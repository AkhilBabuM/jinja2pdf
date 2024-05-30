import http.server
import socketserver
import threading
import os
import time
from playwright.sync_api import sync_playwright
import zipfile

def unzip_file():
    print("Unzipping files...")
    with zipfile.ZipFile('Archive.zip', 'r') as zip_ref:
      zip_ref.extractall('temp')
    print("Files unzipped successfully.")

def start_server():
    current_directory = os.getcwd()

    os.chdir(os.path.join(current_directory, 'temp'))

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8002), Handler) as httpd:
        print("Server started at http://localhost:8002")
        httpd.serve_forever()

def generate_pdf():
    unzip_file()
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/index.html')
        print('Rendering webpage')
        time.sleep(3)
        print('Rendering pdf')
        page.pdf(path='../form.pdf')
        print('Saved form.pdf')
        browser.close()

generate_pdf()
