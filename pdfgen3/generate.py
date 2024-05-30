import json
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def create_input_field(field_data):
    input_element = ""
    if field_data['fieldtype'] == "Data":
        input_element = f'<input type="text" name="{field_data["fieldname"]}" />'
    elif field_data['fieldtype'] == "Int":
        input_element = f'<input type="number" name="{field_data["fieldname"]}" />'
    elif field_data['fieldtype'] == "Select":
        options = "".join([f'<option value="{option}">{option}</option>' for option in field_data['options'].split("\n")])
        input_element = f'<select name="{field_data["fieldname"]}">{options}</select>'
    elif field_data['fieldtype'] == "Text":
        input_element = f'<textarea name="{field_data["fieldname"]}"></textarea>'
    else:
        input_element = f'<input type="text" name="{field_data["fieldname"]}" />'
    return input_element

def generate_html(content, form_data, form_submit_data):
    field_order = form_data["field_order"]
    fields = form_data["fields"]

    soup = BeautifulSoup(content, 'html.parser')
    content_div = soup.find(id="content")

    current_section = None
    current_column = None

    for fieldname in field_order:
        field_data = next((field for field in fields if field["fieldname"] == fieldname), None)
        if not field_data:
            continue

        if field_data["fieldtype"] == "Section Break":
            current_section = soup.new_tag("div", **{"class": "section"})
            section_header = soup.new_tag("h2")
            section_header.string = field_data["label"]
            current_section.append(section_header)
            current_section.append(soup.new_tag("br"))
            content_div.append(current_section)
            current_column = None
        elif field_data["fieldtype"] == "Column Break":
            current_column = soup.new_tag("div", **{"class": "column-break"})
            current_section.append(current_column)
        else:
            field_element = soup.new_tag("div", **{"class": "field"})
            label = soup.new_tag("label")
            label.string = field_data["label"]
            field_element.append(label)
            field_element.append(soup.new_tag("br"))
            if field_data["fieldtype"] == "Text":  # Check if the field is a Text type
                textarea = soup.new_tag("textarea")
                textarea.append(form_submit_data[field_data["fieldname"]] if field_data["fieldname"] in form_submit_data else "")
                textarea["name"] = field_data["fieldname"]  # Set the name attribute separately
                field_element.append(textarea)
            else:
                field_element.append(BeautifulSoup(create_input_field(field_data), 'html.parser'))

            if current_column:
                current_column.append(field_element)
            elif current_section:
                current_section.append(field_element)
            else:
                content_div.append(field_element)
    
    # Populate form with data from another JSON file
    for fieldname in field_order:
        field_data = next((field for field in fields if field["fieldname"] == fieldname), None)
        if field_data and fieldname in form_submit_data:
            input_element = soup.find(attrs={"name": fieldname})
            if input_element:
                input_element['value'] = form_submit_data[fieldname]

    return str(soup)

def render_html_to_pdf(html_file, output_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f'file://{html_file}')
        page.wait_for_load_state("networkidle")

        page.pdf(path=output_file)

        browser.close()

# Example usage
current_directory = os.getcwd()
html_template_path = os.path.join(current_directory, "index.html")
form_data_path = os.path.join(current_directory, "form_data.json")
form_submit_data_path = os.path.join(current_directory, "form_submit_data.json")
output_html_path = os.path.join(current_directory, "rendered.html")
output_pdf_path = os.path.join(current_directory, "output.pdf")

# Load HTML template
with open(html_template_path, 'r') as file:
    html_template = file.read()

# Fetch JSON data
form_data = fetch_json(form_data_path)
form_submit_data = fetch_json(form_submit_data_path)

# Generate prerendered HTML
prerendered_html = generate_html(html_template, form_data, form_submit_data)

# Save prerendered HTML to a file
with open(output_html_path, 'w') as file:
    file.write(prerendered_html)

# Render prerendered HTML to PDF
render_html_to_pdf(output_html_path, output_pdf_path)
