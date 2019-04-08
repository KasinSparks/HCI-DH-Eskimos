"""
The flask application package.
"""

import os
from flask import Flask

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)

	if os.getcwd() == '/':
		database_path = '/var/www/HCI-DH-Eskimos/FlaskWebProject/FlaskWebProject/FlaskWebProject/database'
		upload_path = '/var/www/HCI-DH-Eskimos/FlaskWebProject/FlaskWebProject/FlaskWebProject/Images'
	else:
		database_path = os.path.join(os.getcwd(), 'FlaskWebProject', 'database')
		upload_path = os.path.join(os.getcwd(), 'FlaskWebProject', 'Images')

	app.config.from_mapping(
		SECRET_KEY='changethiskeylater',
		UPLOAD_FOLDER = upload_path,
		DATABASE = os.path.join(database_path, 'db.sqlite')
	)

	import FlaskWebProject.db
	db.init_app(app)

	## auth blueprint
	from . import auth
	app.register_blueprint(auth.bp)
	app.add_url_rule('/', endpoint='userViews.index')
	
	## user views blueprint
	from . import userViews
	app.register_blueprint(userViews.bp)
	
	## admin views blueprint
	from . import adminViews
	app.register_blueprint(adminViews.bp)
	

	##import FlaskWebProject.views
	##import FlaskWebProject.dhsViews

	return app

def run_app():
    if __name__ == '__main__':
        create_app().run()
