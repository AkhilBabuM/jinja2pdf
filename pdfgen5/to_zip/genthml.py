import json
from bs4 import BeautifulSoup

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
            if field_data["fieldtype"] == "Text":
                textarea = soup.new_tag("textarea")
                textarea.append(form_submit_data[field_data["fieldname"]] if field_data["fieldname"] in form_submit_data else "")
                textarea["name"] = field_data["fieldname"]
                field_element.append(textarea)
            else:
                field_element.append(BeautifulSoup(create_input_field(field_data), 'html.parser'))

            if current_column:
                current_column.append(field_element)
            elif current_section:
                current_section.append(field_element)
            else:
                content_div.append(field_element)
    
    for fieldname in field_order:
        field_data = next((field for field in fields if field["fieldname"] == fieldname), None)
        if field_data and fieldname in form_submit_data:
            input_element = soup.find(attrs={"name": fieldname})
            if input_element:
                input_element['value'] = form_submit_data[fieldname]

    return str(soup)

# Usage
if __name__ == "__main__":
    import sys

    # Load JSON data from command line arguments
    html_template_path = sys.argv[1]
    form_data_path = sys.argv[2]
    form_submit_data_path = sys.argv[3]
    output_html_path = sys.argv[4]

    with open(html_template_path, 'r') as file:
        html_template = file.read()

    form_data = json.load(open(form_data_path))
    form_submit_data = json.load(open(form_submit_data_path))

    # Generate prerendered HTML
    prerendered_html = generate_html(html_template, form_data, form_submit_data)

    # Save prerendered HTML to a file
    with open(output_html_path, 'w') as file:
        file.write(prerendered_html)
