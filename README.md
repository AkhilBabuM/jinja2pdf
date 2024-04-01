# JINJA2PDF

This project generates PDFs from HTML templates and JSON data using Jinja2 and pdfkit.

## Project Structure

- `jinja2pdf.py`: This script uses pdfkit to generate PDFs from an HTML template and JSON data.
- `t1simple.html`: This is the HTML template without any Table components.
- `t2table.html`: This is the HTML template with Table components.
- `data1.json`: This is the JSON data used by `jinja2pdf.py` to populate the templates.
- `renders/`: This directory is where the generated PDFs are stored.

## How to Run

1. Create a Python virtual environment:

```
python3 -m venv .venv
```

2. Activate the virtual environment:

```
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the required Python packages:
  
```
pip install jinja2 pdfkit
```

4. Run the script:

```
python jinja2pdf.py
```