import http.server
import socketserver
import threading
import os
import time
from playwright.sync_api import sync_playwright
import zipfile

class StoppableTCPServer(socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def serve_forever(self):
        while not self._stop_event.is_set():
            self.handle_request()

    def stop(self):
        self._stop_event.set()

def unzip_file():
    print("Unzipping files...")
    with zipfile.ZipFile('Archive.zip', 'r') as zip_ref:
        zip_ref.extractall('temp')
    print("Files unzipped successfully.")

def start_server():
    current_directory = os.getcwd()
    os.chdir(os.path.join(current_directory, 'temp'))
    Handler = http.server.SimpleHTTPRequestHandler
    server = StoppableTCPServer(("", 8002), Handler)

    def run_server():
        print("Server started at http://localhost:8002")
        server.serve_forever()
        server.server_close()
        print("Server stopped")

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    time.sleep(1)  # Give the server a moment to start

    return server, server_thread

def generate_pdf():
    unzip_file()
    server, server_thread = start_server()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8002/index.html')
        print('Rendering webpage')
        time.sleep(3)  # Allow the page to fully load
        print('Rendering pdf')
        page.pdf(path='../form5.pdf')
        print('Saved form.pdf')
        browser.close()

    server.stop()
    server_thread.join()

generate_pdf()
