import os
import json
import pdfkit
from jinja2 import Environment, FileSystemLoader

directory_name = "renders"
template_name = "t2table.html"
data_name = "data1.json"

if not os.path.exists(directory_name):
    os.makedirs(directory_name)


def generate_pdf(html_content, output_filename):
    try:
        output_name = os.path.join(directory_name, output_filename)
        pdfkit.from_string(html_content, output_name)
        return True
    except Exception as e:
        print(f"Error generating {output_name}: {e}")
        return False


with open(data_name, "r") as file:
    entries = json.load(file)

env = Environment(loader=FileSystemLoader("."))
template = env.get_template(template_name)

for index, entry in enumerate(entries):
    html_out = template.render(entry)

    pdf_filename = f'{template_name}_{index+1}_{entry.get("form_id", "unknown")}.pdf'

    if generate_pdf(html_out, pdf_filename):
        print(
            f'{index + 1}. Successfully generated PDF for {entry.get("form_id", "unknown")}: {pdf_filename}'
        )
    else:
        print(
            f'{index + 1}. Failed to generate PDF for {entry.get("form_id", "unknown")}'
        )
