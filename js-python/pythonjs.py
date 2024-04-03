import os
import json
import subprocess
from jinja2 import Environment, FileSystemLoader

directory_name = "htmls"
template_name = "t1simple.html"
data_name = "data1.json"
js_script_path = "pythonjs.js"  # Path to your JS script

if not os.path.exists(directory_name):
    os.makedirs(directory_name)

with open(data_name, "r") as file:
    entries = json.load(file)

env = Environment(loader=FileSystemLoader("."))
template = env.get_template(template_name)

for index, entry in enumerate(entries):
    html_out = template.render(entry)
    html_filename = os.path.join(directory_name, f'{index+1}_{entry.get("form_id", "unknown")}.html')

    with open(html_filename, 'w') as html_file:
        html_file.write(html_out)

    # Call the JS script to generate PDF from HTML
    subprocess.run(["node", js_script_path, html_filename, f'{html_filename}.pdf'])
