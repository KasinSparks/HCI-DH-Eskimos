"""
Routes and views for the dhs side of the flask application.
"""

import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, url_for, send_from_directory, redirect, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from FlaskWebProject import app
from . import db
from FlaskWebProject import calendar_module



#test = Enviroment(app)


# ignore this for now
#UPLOAD_FOLDER = 'static/img'

#UPLOAD_FOLDER = os.getcwd() + '\\FlaskWebProject\\Images'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def imgGet(image):
	# print(static/img/NoImageIcon.png)
	# return 'static/img/NoImageIcon.png'
	# return 'static/img/backgound.jpg'
	# return render_template('imgTest.html', testImg='static/img/backgound.jpg')
	# return open('static/img/'+image, 'r+b').read()
	## folder = UPLOAD_FOLDER + '\\'

	# with open(folder + image, 'rb') as image_file:

	##print("currDir: " + os.curdir)
	##print("osPath: " + os.path.join("test", "test2"))

	with open(os.path.join(app.config['UPLOAD_FOLDER'], image), 'rb') as image_file:
		tempImg = base64.b64encode(image_file.read())
		tempImg = tempImg.decode('utf-8') # if you start geting no image check here
										# I had to change this when i converted project to windows
	# return render_template('imgTest.html', testImg=tempImg)
	return tempImg


@app.route("/test")
def test():
	"""testing"""
	
	## TODO: check the input so XSS or sql injections can not happen
	month = request.args.get('month', default=datetime.today().month, type=int)
	print('month passed: ', month)
	year = request.args.get('year', default=datetime.today().year, type=int)
	print('year passed: ', year)

	return render_template('test.html', 
						title='this is a test', 
						pageName='PROJECT TEST PAGE', 
						img=imgGet('NoImageIcon.png'), 
						numRows=6,
						calData=calendar_module.generateCal(month,year)
						)


@app.route("/result", methods=['GET', 'POST'])
def result():
	#img = request.form.get('test')
	# tempImg = base64.b64encode(img.read())
	img = request.files['test']
	print(img)
	filename = secure_filename(img.filename)
	##savePath = os.getcwd() + app.config['UPLOAD_FOLDER'] + '\\'
	img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	

	# test
	db = getDB()
	db.execute( 'INSERT INTO Clients (username, password) VALUES (?, ?)', ("JohnDoe", generate_password_hash("password")))
	db.commit()

	return render_template('imgTest.html', pageName="Image received", img=imgGet(filename))

@app.route("/login")
def loginPage():
	return render_template(
		'login.html',
		title = 'TEST LOGIN',
		pageName = 'A test login page',
		)

@app.route("/login/submit", methods=['POST'])
def login():
	
	# temp. store the data the user entered in
	userName = request.form.get("username")
	password = request.form.get("password")

	# query string
	queryStr = 'SELECT User_Name FROM Users WHERE User_Name = ? AND Password = ?'

	# perform a query, results come back in a list of values
	user = db.query_db(queryStr, (userName, password), one=True)

	# make sure the data entered is valid
	if user is None:
		print('No user found')
		user = 'no user found'
	else:
		print(user)
		print(user['User_Name'])
		user = user['User_Name']

	

	return render_template(
		'loginSuccessTest.html',
		title = 'TEST LOGIN',
		pageName = 'A test login page',
		status = user
		)