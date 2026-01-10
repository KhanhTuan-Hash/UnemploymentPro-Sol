import os
from flask import Flask
import json

app = Flask(__name__)

@app.template_filter('from_json')
def from_json_filter(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []

app.secret_key = 'secret_key'

# design uploads
app.config['UPLOAD_FOLDER'] = 'UPS/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

from UPS import views