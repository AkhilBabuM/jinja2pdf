# config.py

# Port number
PORT_NUMBER = '8000'

# Directory names
RENDER_DIR = 'renders'
STATIC_DIR = 'static'

# Base URL for the static files
def get_index_html_url(port_number, form_uri, record_id):
    return f'http://127.0.0.1:{port_number}/static/{form_uri}/index.html?record_id={record_id}'
