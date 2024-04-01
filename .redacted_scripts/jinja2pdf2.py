import json
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

def generate_pdf(html_content, output_filename):
    try:
        # Directly use the HTML content string with WeasyPrint
        HTML(string=html_content).write_pdf(output_filename)
        return True
    except Exception as e:
        print(f"Error generating {output_filename}: {e}")
        return False

# Load your JSON data
with open('data2.json', 'r') as file:
    entries = json.load(file)

# Initialize the Jinja environment and load your template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('bankformsimple2.html')

# Loop through each entry in your JSON data, render the HTML, and generate a PDF
for index, entry in enumerate(entries):
    # Render the HTML content from the template and the current entry's data
    html_out = template.render(entry)
    
    # Define the output PDF filename
    pdf_filename = f'{index+1}_{entry.get("form_id", "unknown")}.pdf'
    
    # Generate the PDF using the rendered HTML content
    if generate_pdf(html_out, pdf_filename):
        print(f'{index + 1}. Successfully generated PDF for {entry.get("form_id", "unknown")}: {pdf_filename}')
    else:
        print(f'{index + 1}. Failed to generate PDF for {entry.get("form_id", "unknown")}')
