import http.server
import socketserver
import threading
import os
import time
from playwright.sync_api import sync_playwright

def start_server():
     # Get the current directory
    current_directory = os.getcwd()

    # Change to the temp directory in the current directory
    os.chdir(os.path.join(current_directory, 'temp'))

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        print("Server started at http://localhost:8000")
        httpd.serve_forever()

def generate_pdf():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait for the server to start (you can add a timeout if needed)
    time.sleep(1)

    # Navigate to the local server URL and save as PDF
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/index.html')
        print('Rendering webpage')
        time.sleep(3)
        print('Rendering pdf')
        page.pdf(path='form.pdf')
        print('Saved form.pdf')
        browser.close()

# Start the server and generate PDF
generate_pdf()
