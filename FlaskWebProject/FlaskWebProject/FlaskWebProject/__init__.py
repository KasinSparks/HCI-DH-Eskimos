"""
The flask application package.
"""

import os
from flask import Flask

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'FlaskWebProject', 'Images')
app.config['DATABASE']  = os.path.join(os.getcwd(), 'FlaskWebProject', 'database', 'db.sqlite')

import FlaskWebProject.db
db.init_app(app)

import FlaskWebProject.views
import FlaskWebProject.dhsViews
