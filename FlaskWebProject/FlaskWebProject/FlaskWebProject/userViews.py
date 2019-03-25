from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app

import os

## will be used to show 404 or 403 request
from werkzeug.exceptions import abort

from FlaskWebProject.auth import login_required
from FlaskWebProject.db import query_db

from FlaskWebProject.ImageRender import imgGet

from werkzeug.utils import secure_filename

from datetime import datetime

bp = Blueprint('userViews', __name__)

@bp.route('/index')
def index():
	return render_template(
		'auth/login.html',
		title='Login Page',
		year=datetime.now().year,
	)

## TODO: have it so there is another render template if user is not logged in
@bp.route('/profile')
@login_required
def profile():

	## debug.... DELETE ME
	#print(g.user['User_Name'])

	## query string for the connected cases
	queryStr = 'SELECT UID_Connected_Person FROM Connected_Person WHERE UID_Client=?'
	## result form connected cases query
	connected_cases_list = query_db(queryStr, (g.user['UID_Users'],))

	## debug.... DELETE ME
	#for clients in connected_cases_list:
	#	print(clients)

	## get the client data from the previous query
	connected_client_list = []
	queryStr = 'SELECT * FROM Client WHERE UID_Client=?'
	for clients in connected_cases_list:
		connected_client_list.append(query_db(queryStr, (clients['UID_Connected_Person'],), True))

	## get the current user's data to display at the top of accordion
	queryStr = 'SELECT * FROM Client WHERE UID_Client=?'
	currUser = query_db(queryStr, (g.user['UID_Users'],), True)

	## get the current user's social worker data
	queryStr = 'SELECT * FROM Social_Worker WHERE UID_Social_Worker=?'
	socialWorker = query_db(queryStr, (currUser['Social_Worker_UID'],), True)

	## get the current user's current county office
	queryStr = 'SELECT * FROM County_Office WHERE UID_County_Office=?'
	countyOffice = query_db(queryStr, (currUser['County_Office_UID'],), True)

	return render_template(
		'userViews/profile.html',
		title='Profile Page',
		worker=socialWorker,
		clientData=currUser,
		connectedCases=connected_client_list,
		countyOffice=countyOffice,
		year=datetime.now().year
		)


@bp.route('/uploads')
@login_required
def uploads():

	## get the user's previous uploads
	queryStr = 'SELECT * FROM Uploads WHERE Client_UID=?'
	uploadList = query_db(queryStr, (g.user['UID_Users'],))

	return render_template(
		'userViews/uploads.html',
		title='Uploads Page',
		year=datetime.now().year,
		uploads=uploadList
		)


@bp.route('/uploads/render', methods=('GET', 'POST'))
@login_required
def render():

	## get the data from the form submited

	## we can use g.user to get the user's username and save location
	saveLoc = g.user['User_Name']
	fileName = request.form['fileName']

	## generate the path for the image location
	path = os.path.join(saveLoc, fileName)

	

	return render_template(
		'userViews/imageViewer.html',
		title='View Upload',
		year=datetime.now().year,
		img=imgGet(path)
		)


@bp.route('/uploads/upload_document')
@login_required
def upload_doc():

	## get the data for the type Drop-Down-Data (ddd)
	queryStr = 'SELECT * FROM Document_Type'
	ddd = query_db(queryStr)

	return render_template(
		'userViews/uploadDocument.html',
		title='Image Upload',
		year=datetime.now().year,
		typeData=ddd
		)


@bp.route('/uploads/submit_document', methods=('GET', 'POST'))
@login_required
def submit_document():
	## get the image from the form
	image = request.files['image']
	#print(image)
	#fileName = secure_filename(image.filename)
	

	## get the user's client ID
	id = g.user['User_Name']

	## save the data from the form
	docName = request.form['docName']
	currDate = datetime.today()
	docType = request.form['docType']
	fileName = secure_filename(docName + '_' + str(currDate))

	customDateFormat = str(currDate.year) + '-' + str(currDate.month) + '-' + str(currDate.day)
	customDateFormat += ' ' + str(currDate.hour) + ':' + str(currDate.minute)

	## submit the data to the database
	from FlaskWebProject.db import getDB
	command = 'INSERT INTO Uploads (Client_UID, Date_Uploaded, Document_Type, File_Name, Doc_Name) VALUES (?,?,?,?,?);'
	### TODO: change the doctype from 0 to a value the user picks
	curr = getDB().execute(command, (g.user['UID_Users'], customDateFormat, docType, fileName, docName,))
	getDB().commit()
	curr.close()

	## save the image and create dir if needed
	if not os.path.isdir(os.path.join(current_app.config['UPLOAD_FOLDER'], id)):
		## dir does not already exist. Make new dir for user's uploads
		## TODO: hash the user name for the folder
		os.mkdir(os.path.join(current_app.config['UPLOAD_FOLDER'], str(id)))

	## save image
	## TODO: put the date and time into the file name
	image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], str(id), fileName))


	## redirect user back to upload page on success
	return redirect(url_for('userViews.uploads'))

	## error must of occured with the redirect
	return render_template(
		'userViews/uploadDocument.html',
		title='Image Upload',
		year=datetime.now().year
		)


#TODO: needs value checking bad
@bp.route('/calendar', methods=('GET', 'POST'))
def calendar():

	from FlaskWebProject.calendar_module import generateCal
	from FlaskWebProject.calendar_module import nameOfMonth

	y = request.args.get('year')
	m = request.args.get('month')

	if y is None:
		y = datetime.now().year
	else:
		y = int(y)
		

	if m is None:
		m = datetime.now().month
	else:
		m = int(m)
	
	## set next and previous months
	### prevent overflows by mod 12
	nm = (m % 12) + 1
	### prevent underflows, first thing i thought of, prob. a better way out there
	pm = (m - 1) % 12 if m != 1 else 12

	## set the next and previous year if needed
	if m == 12:
		ny = y + 1
		py = y
	elif m == 1:
		ny = y
		py = y - 1
	else:
		ny = y
		py = y

	## select the events that occur in the month displayed
	queryStr = 'SELECT * FROM Calendar WHERE Event_Date_Month=? AND Event_Date_Year=?;'
	queryResult = query_db(queryStr, (m, y))

	return render_template(
		'userViews/calendar.html',
		title='Calendar',
		year=y,
		month=m,
		monthName=nameOfMonth(m),
		calData=generateCal(m,y),
		currDate=datetime.now(),
		nextMonth=nm,
		prevMonth=pm,
		nextYear=ny,
		prevYear=py,
		deadlines=queryResult
		)