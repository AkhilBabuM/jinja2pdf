from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    url1="http://127.0.0.1:5501/pdfgen9/webserve/index.html?org=myorg&form=myform&subid=12345"
    
    url2="http://127.0.0.1:5501/pdfgen9/webserve/index.html?org=myorg&form=myform&subid=12346"

    browser = p.chromium.launch()
    page = browser.new_page()

    # Enter URL here
    page.goto(url2) 

    print(page.title())
    page.wait_for_load_state('networkidle')
    page.pdf(path='renders/test2.pdf')
    browser.close()