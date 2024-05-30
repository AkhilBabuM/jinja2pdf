import zipfile
import http.server
import time
import socketserver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Define a custom handler to serve the files locally
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

def serve_files(server):
    server.serve_forever()

def main():
    try:
        print("Unzipping files...")
        with zipfile.ZipFile('Archive.zip', 'r') as zip_ref:
            zip_ref.extractall('temp')
        print("Files unzipped successfully.")

        # Start a local server to serve the files
        PORT = 8001
        httpd = socketserver.TCPServer(('localhost', PORT), MyHTTPRequestHandler)
        server_task = serve_files(httpd)
        print(f"Serving at http://localhost:{PORT}")

        # Create a Selenium WebDriver
        print("Creating Selenium WebDriver...")
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode
        driver = webdriver.Chrome(service=service, options=options)

        # Navigate to the HTML page
        print("Navigating to HTML page...")
        driver.get(f'http://localhost:{PORT}/temp/index.html')

        # Print the page as PDF
        print("Printing page as PDF...")
        driver.execute_script('window.print();')

        # Wait for the PDF to be generated
        time.sleep(5)  # Adjust the delay based on your page's complexity

        # Save the PDF
        driver.execute_script('document.title = "rendered_form";')
        driver.execute_script('window.print();')

        print("PDF generated and saved.")

        # Quit the WebDriver
        driver.quit()

        httpd.shutdown()  # Stop the local server after rendering
        server_task.join()  # Wait for server to shutdown before continuing
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
