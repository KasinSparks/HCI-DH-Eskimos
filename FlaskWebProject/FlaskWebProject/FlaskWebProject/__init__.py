"""
The flask application package.
"""

import os
from flask import Flask

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)

	app.config.from_mapping(
		UPLOAD_FOLDER = os.path.join(os.getcwd(), 'FlaskWebProject', 'Images'),
		DATABASE = os.path.join(os.getcwd(), 'FlaskWebProject', 'database', 'db.sqlite')
	)

	import FlaskWebProject.db
	db.init_app(app)

	import FlaskWebProject.views
	import FlaskWebProject.dhsViews

	return app