PORT_NUMBER = '8000'

# Directory names
RENDER_DIRECTORY = 'renders'
STATIC_DIRECTORY = 'static'
DATA_DIRECTORY = 'data'

# Base URL for the static files
def get_index_html_url(port_number, form_uri, record_id):
    return f'http://127.0.0.1:{port_number}/static/{form_uri}/index.html?record_id={record_id}'
