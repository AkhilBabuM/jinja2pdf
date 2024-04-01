import json
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

def generate_pdf(html_content, output_filename):
    try:
        HTML(string=html_content).write_pdf(output_filename)
        return True
    except Exception as e:
        print(f"Error generating {output_filename}: {e}")
        return False

with open('data2.json', 'r') as file:
    entries = json.load(file)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('bankformsimple2.html')

for index, entry in enumerate(entries):
    html_out = template.render(entry)
    
    pdf_filename = f'{index+1}_{entry.get("form_id", "unknown")}.pdf'
    
    if generate_pdf(html_out, pdf_filename):
        print(f'{index + 1}. Successfully generated PDF for {entry.get("form_id", "unknown")}: {pdf_filename}')
    else:
        print(f'{index + 1}. Failed to generate PDF for {entry.get("form_id", "unknown")}')
