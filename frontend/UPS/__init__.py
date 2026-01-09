import os
from flask import Flask

app = Flask(__name__)
app.secret_key = 'secret_key'

# design uploads
app.config['UPLOAD_FOLDER'] = 'UPS/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

from UPS import views