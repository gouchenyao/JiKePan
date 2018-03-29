import os
import datetime

from flask import Flask

from flask_bootstrap import Bootstrap


app = Flask(__name__)

app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY = 'JiKePan',
    DATABASE = os.path.join(app.root_path, 'data', 'database','ji_ke_pan.db'),
    UPLOAD_FOLDER =  os.path.join(app.root_path, 'data', 'files'),
    THUMBNAIL_FOLDER =  os.path.join(app.root_path, 'data/thumbnail/'),
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024,))

app.permanent_session_lifetime = datetime.timedelta(seconds=10 * 60)

bootstrap = Bootstrap(app)