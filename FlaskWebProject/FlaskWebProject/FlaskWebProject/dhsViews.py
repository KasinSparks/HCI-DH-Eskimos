"""
Routes and views for the dhs side of the flask application.
"""

import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, url_for, send_from_directory, redirect
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from FlaskWebProject import app
from FlaskWebProject.db import getDB

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
	return render_template('test.html', pageName='PROJECT TEST PAGE', img=imgGet('NoImageIcon.png'))

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