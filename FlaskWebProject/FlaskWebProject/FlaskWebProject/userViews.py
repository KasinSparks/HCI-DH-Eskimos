from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app

import os

## will be used to show 404 or 403 request
from werkzeug.exceptions import abort

from FlaskWebProject.auth import login_required
from FlaskWebProject.db import query_db
from . import db

from FlaskWebProject.ImageRender import imgGet

from werkzeug.utils import secure_filename

from datetime import datetime

bp = Blueprint('userViews', __name__)

@bp.route('/index')
def index():
	return render_template(
		'auth/login.html',
		title='Login Page',
		year=datetime.now().year
	)

## TODO: have it so there is another render template if user is not logged in
@bp.route('/profile')
@login_required
def profile():

	## debug.... DELETE ME
	#print(g.user['User_Name'])
	if g.user['Client'] == 1:
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

		## debug.... DELETE ME
		#print(g.user['UID_Users'])
		#print(currUser['Social_Worker_UID'])

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
	elif g.user['social_Worker'] == 1:

		## get the current user's social worker data
		queryStr = 'SELECT * FROM Social_Worker WHERE UID_Social_Worker=?'
		socialWorker = query_db(queryStr, (g.user['UID_Users'],), True)

		## get the current user's current county office
		queryStr = 'SELECT * FROM County_Office WHERE UID_County_Office=?'
		countyOffice = query_db(queryStr, (socialWorker['County_Office_UID'],), True)

		return render_template(
			'socialWorkerViews/sw_profile.html',
			title='Profile Page',
			worker=socialWorker,
			countyOffice=countyOffice,
			year=datetime.now().year
			)



@bp.route('/uploads')
@login_required
def uploads():

	## get the user's previous uploads
	queryStr = """SELECT Uploads.*, Document_Type.Document_Type_Name 
					FROM Uploads 
					INNER JOIN Document_Type ON Uploads.Document_Type=Document_Type.UID_Document_Type
					WHERE Client_UID=?;"""
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
	if request.method == 'POST':
		cid = request.form['cid']

		qryStr = 'SELECT User_Name FROM Users WHERE UID_Users=?'
		clientEmail = query_db(qryStr, (cid,), True)

		saveLoc = clientEmail['User_Name']

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
	## put the date and time into the file name
	fileName = secure_filename(docName + '_' + str(currDate))

	customDateFormat = str(currDate.year) + '-' + str(currDate.month) + '-' + str(currDate.day)
	customDateFormat += ' ' + str(currDate.hour) + ':' + str(currDate.minute)

	## submit the data to the database
	from FlaskWebProject.db import getDB
	command = 'INSERT INTO Uploads (Client_UID, Date_Uploaded, Document_Type, File_Name, Doc_Name) VALUES (?,?,?,?,?);'
	curr = getDB().execute(command, (g.user['UID_Users'], customDateFormat, docType, fileName, docName,))
	getDB().commit()
	curr.close()

	## save the image and create dir if needed
	if not os.path.isdir(os.path.join(current_app.config['UPLOAD_FOLDER'], id)):
		## dir does not already exist. Make new dir for user's uploads
		## TODO: hash the user name for the folder
		os.mkdir(os.path.join(current_app.config['UPLOAD_FOLDER'], str(id)))

	## save image
	image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], str(id), fileName))

	## get the user's social worker
	sqlQry = 'SELECT Social_Worker_UID FROM Client WHERE UID_Client=?'
	swUID = query_db(sqlQry, (g.user['UID_Users'],), True)
	swUID = int(swUID['Social_Worker_UID'])

	## add a notification to the worker that client uploaded a documnet
	sqlCommand = 'INSERT INTO Notifications (UID_Client, UID_Social_Worker, Notification_Type, Has_Been_Read) VALUES (?,?,?,?);'
	curr = getDB().execute(sqlCommand, (g.user['UID_Users'], swUID, 2, 0))
	getDB().commit()
	curr.close()

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
	queryStr = 'SELECT * FROM Calendar WHERE Event_Date_Month=? AND Event_Date_Year=? AND (User_UID=? OR User_UID=?);'
	
	## determines what data to display. -1 for public data and uuid for private data
	if g.user is None:
		queryResult = query_db(queryStr, (m, y, -1, -1))
	else:
		queryResult = query_db(queryStr, (m, y, g.user['UID_Users'], -1))

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



### TODO: move this into a new python file for sw_views
@bp.route('/notifications')
@login_required
def notifications():
	if g.user['social_worker'] == 1:
		## get the current social worker's notifictations
		notifQry = """SELECT Notifications.*, Notification_Type.Name, Client.First_Name, Client.Last_Name 
				FROM Notifications 
				INNER JOIN Notification_Type ON Notifications.Notification_Type=Notification_Type.UID_Notification_Type 
				INNER JOIN Client ON Notifications.UID_Client=Client.UID_Client
				WHERE UID_Social_Worker=? 
				ORDER BY Has_Been_Read ASC;"""
		queryResult = query_db(notifQry, (int(g.user['UID_Users']),))

		return render_template(
			'socialWorkerViews/notifications.html',
			notifications=queryResult,
			year=datetime.now().year,
			title='Notifications'
			)
	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


### TODO: move this into a new python file for sw_views
@bp.route('/notifications/open', methods=('GET', 'POST'))
@login_required
def notifications_open():
	if g.user['social_worker'] == 1:

		uid_Notification = request.args.get('n')

		## set the current notification to has been read to true
		from FlaskWebProject.db import getDB
		db = getDB()
		curr = db.execute('UPDATE Notifications SET Has_Been_Read=? WHERE UID_Notification=?', (1, int(uid_Notification)))
		db.commit()
		curr.close()

		## get the current social worker's notifictations
		notifQry = 'SELECT * FROM Notifications WHERE UID_Notification=?'
		notifQueryResult = query_db(notifQry, (int(uid_Notification),), True)

		## get the client data from the notification
		clientQry = """SELECT Client.*, Case_Status.Case_Status_Name, County_Office.Office_Name 
				FROM Client 
				INNER JOIN Case_Status ON Client.Case_Status=Case_Status.UID_Case_Status
				INNER JOIN County_Office ON Client.County_Office_UID=County_Office.UID_County_Office
				WHERE UID_Client=?"""
		clientQueryResult = query_db(clientQry, (int(notifQueryResult['UID_Client']),), True)

		## get the user status
		userQry = 'SELECT Is_Verified FROM Users WHERE UID_Users=?'
		userQueryResult = query_db(userQry, (int(clientQueryResult['UID_Client']),), True)

		## get the case status names for form
		qryStr = 'SELECT * FROM Case_Status;'
		case_status = query_db(qryStr)

		## get the case types names for form
		qryStr = 'SELECT * FROM Case_Type;'
		case_types = query_db(qryStr)

		## get the county office names for form
		qryStr = 'SELECT * FROM County_Office;'
		co = query_db(qryStr)

		return render_template(
			'socialWorkerViews/notificationsOpen.html',
			notification=notifQueryResult,
			clientData=clientQueryResult,
			verified=userQueryResult,
			year=datetime.now().year,
			title='Notifications Viewer',
			status=case_status,
			caseTypes=case_types,
			offices=co
			)
	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))



@bp.route('/account/confirm', methods=('GET', 'POST'))
@login_required
def confirm_account():
	if g.user['social_worker'] == 1:
		## get the uid for the user to confirm
		uid = int(request.form['u'])
		fn = request.form['fn']
		ln = request.form['ln']
		dob = request.form['dob']
		cs = int(request.form['case_status'])
		ct = int(request.form['case_type'])
		cn = int(request.form['case_num'])
		of = request.form['office']
		ad = request.form['address']


		## make the change to the database
		from FlaskWebProject.db import getDB
		cur = getDB().execute('UPDATE Users SET Is_Verified=? WHERE UID_Users=?;', (1, uid))
		getDB().commit()
		cur.close()

		cur = getDB().execute('UPDATE Client SET First_Name=?, Last_Name=?, DOB=?, Address=?,' +
			'Case_Status=?, Case_Type_UID=?, Case_Number=?, County_Office_UID=? WHERE UID_Client=?;', (fn, ln, dob, ad, cs, ct, cn, of, uid))
		getDB().commit()
		cur.close()

		return redirect(url_for('userViews.notifications'))
	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))



@bp.route('/myClients', methods=('GET', 'POST'))
@login_required
def my_clients():
	if g.user['social_worker'] == 1:

		## get a query of all the social worker's current clients
		clientQryStr = """SELECT Client.*, Case_Type.Case_Type_Name, Case_Status.Case_Status_Name 
					FROM Client 
					INNER JOIN Users ON Client.UID_Client=Users.UID_Users
					INNER JOIN Case_Status ON Client.Case_Status=Case_Status.UID_Case_Status
					INNER JOIN Case_Type ON Client.Case_Type_UID=Case_Type.UID_Case_Type 
					WHERE Social_Worker_UID=? AND Is_Verified=1"""
		clientQryRlt = query_db(clientQryStr, (g.user['UID_Users'],))

		return render_template(
			'socialWorkerViews/myClients.html',
			clients=clientQryRlt,
			year=datetime.now().year,
			title='My Clients'
			)

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


@bp.route('/myClients/client_info', methods=('GET', 'POST'))
@login_required
def client_info():
	if g.user['social_worker'] == 1:

		if request.method == 'POST':
			uid = int(request.form['uid'])
			print('here')
		else:
			clientEmail = request.args.get('ce')
			print(clientEmail)

			queryStr = 'SELECT UID_Users FROM Users WHERE User_Name=?'
			uid = int(query_db(queryStr, (clientEmail,), True)['UID_Users'])

		## query string for the connected cases
		queryStr = 'SELECT UID_Connected_Person FROM Connected_Person WHERE UID_Client=?'
		## result form connected cases query
		connected_cases_list = query_db(queryStr, (uid,))

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
		currUser = query_db(queryStr, (uid,), True)

		## make sure the uid is vaild
		if currUser is None:
			##print('no client found with matching uid')
			return redirect(url_for('userViews.my_clients'))

		## debug.... DELETE ME
		#print(g.user['UID_Users'])
		#print(currUser['Social_Worker_UID'])

		## get the current user's social worker data
		queryStr = 'SELECT * FROM Social_Worker WHERE UID_Social_Worker=?'
		socialWorker = query_db(queryStr, (currUser['Social_Worker_UID'],), True)

		## make sure the uid is vaild check 2
		if socialWorker is None:
			##print('current user (social worker) is not the social worker of the uid client provided')
			return redirect(url_for('userViews.my_clients'))

		## get the current user's current county office
		queryStr = 'SELECT * FROM County_Office WHERE UID_County_Office=?'
		countyOffice = query_db(queryStr, (currUser['County_Office_UID'],), True)

		## get all of the county offices
		queryStr = 'SELECT * FROM County_Office'
		countyOfficeList = query_db(queryStr)

		## get all of the case status
		queryStr = 'SELECT * FROM Case_Type'
		caseTypes = query_db(queryStr)

		## get all of the case types
		queryStr = 'SELECT * FROM Case_Status'
		status = query_db(queryStr)

		return render_template(
			'socialWorkerViews/viewClientData/viewClientData.html',
			title='My Clients',
			clientData=currUser,
			connectedCases=connected_client_list,
			countyOffice=countyOffice,
			officeList=countyOfficeList,
			year=datetime.now().year,
			templateNum=0,
			c=uid,
			status=status,
			caseTypes=caseTypes
			)

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


@bp.route('/myClients/documents', methods=('GET', 'POST'))
@login_required
def documents():
	if g.user['social_worker'] == 1:

		if request.method == 'POST':
			uid = int(request.form['uid'])
		else:
			clientEmail = request.args.get('ce')

			queryStr = 'SELECT UID_Users FROM Users WHERE User_Name=?'
			uid = int(query_db(queryStr, (clientEmail,), True)['UID_Users'])

		queryStr = """SELECT Uploads.*, Document_Type.Document_Type_Name 
					FROM Uploads 
					INNER JOIN Document_Type ON Uploads.Document_Type=Document_Type.UID_Document_Type
					WHERE Client_UID=?;"""
		qryResult = query_db(queryStr, (uid,))

		return render_template(
			'socialWorkerViews/viewClientData/viewClientData.html',
			templateNum=1,
			year=datetime.now().year,
			title='My Clients',
			uploads=qryResult,
			c=uid
			)

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


@bp.route('/myClients/deadlines', methods=('GET', 'POST'))
@login_required
def deadlines():
	if g.user['social_worker'] == 1:

		## TODO: put this block into a function.... It is repeated like 5 times in this doc.
		if request.method == 'POST':
			uid = int(request.form['uid'])
		else:
			clientEmail = request.args.get('ce')

			queryStr = 'SELECT UID_Users FROM Users WHERE User_Name=?'
			uid = int(query_db(queryStr, (clientEmail,), True)['UID_Users'])

		eventQryStr = 'SELECT * FROM Calendar WHERE User_UID=? OR User_UID=?'
		eventQryRlt = query_db(eventQryStr, (uid,-1))

		return render_template(
			'socialWorkerViews/viewClientData/viewClientData.html',
			templateNum=2,
			year=datetime.now().year,
			title='My Clients',
			events=eventQryRlt,
			c=uid
			)

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


def check_for_vaild_args(args=()):
	for a in args:
		if a is None or a == '':
			return False
		
	return True



@bp.route('/myClients/update/deadlines', methods=('GET', 'POST'))
@login_required
def update_deadlines():
	if g.user['social_worker'] == 1:
		## TODO: put this block into a function.... It is repeated like 5 times in this doc.
		if request.method == 'POST':
			uid = int(request.form['uid'])
			e_id = int(request.form['e_id'])
			e_name = request.form['e_name']
			e_des = request.form['e_des']
			e_date = request.form['e_date']
			ec = request.form['ec']
			
			dateComponents = e_date.split('-')
			e_year = int(dateComponents[0])
			e_month = int(dateComponents[1])
			e_day = int(dateComponents[2])

			if check_for_vaild_args((e_name,e_date,e_day,e_month,e_year,e_des,ec,uid,e_id)):
				curr = db.getDB().execute('UPDATE Calendar SET Event_Name=?, Date=?, Event_Date_Day=?, Event_Date_Month=?, Event_Date_Year=?, Event_Description=?, Color=? WHERE User_UID=? AND UUID_Calendar=?', (e_name,e_date,e_day,e_month,e_year,e_des,ec,uid,e_id))
				db.getDB().commit()
				curr.close()
		else:
			clientEmail = request.args.get('ce')
			print('No uid in POST request... Redirecting...')
			return redirect(url_for('userViews.client_info', ce=clientEmail))

		queryStr = 'SELECT User_Name FROM Users WHERE UID_Users=?'
		c_email = query_db(queryStr, (uid,), True)
		return redirect(url_for('userViews.deadlines', ce=c_email['User_Name']))
	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


@bp.route('/myClients/add/deadline', methods=('GET', 'POST'))
@login_required
def add_deadline():
	if g.user['social_worker'] == 1:
		## TODO: put this block into a function.... It is repeated like 5 times in this doc.
		if request.method == 'POST':
			uid = int(request.form['uid'])
			e_name = request.form['e_name']
			e_des = request.form['e_des']
			e_date = request.form['e_date']
			ec = request.form['ec']
			
			dateComponents = e_date.split('-')
			e_year = int(dateComponents[0])
			e_month = int(dateComponents[1])
			e_day = int(dateComponents[2])

			if check_for_vaild_args((e_name,e_date,e_day,e_month,e_year,e_des,ec,uid)):
				curr = db.getDB().execute("""INSERT INTO Calendar 
						(User_UID, Event_Name, Date, Event_Date_Day, Event_Date_Month, Event_Date_Year, 
						Event_Description, Color) 
						VALUES (?,?,?,?,?,?,?,?)""", (uid,e_name,e_date,e_day,e_month,e_year,e_des,ec))
				db.getDB().commit()
				curr.close()
		else:
			clientEmail = request.args.get('ce')
			print('No uid in POST request... Redirecting...')
			return redirect(url_for('userViews.client_info', ce=clientEmail))

		queryStr = 'SELECT User_Name FROM Users WHERE UID_Users=?'
		c_email = query_db(queryStr, (uid,), True)
		return redirect(url_for('userViews.deadlines', ce=c_email['User_Name']))
	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))



@bp.route('/myClients/update/clientData', methods=('GET', 'POST'))
@login_required
def update_clientData():
	if g.user['social_worker'] == 1:
		fn = request.form['fn']
		ln = request.form['ln']
		dob = request.form['dob']
		ad = request.form['address']
		cs = int(request.form['case_status'])
		ct = int(request.form['case_type'])
		cn = int(request.form['case_num'])
		co = int(request.form['office'])


		if request.method == 'POST':
			uid = int(request.form['uid'])
		else:
			clientEmail = request.args.get('ce')

			queryStr = 'SELECT UID_Users FROM Users WHERE User_Name=?'
			uid = int(query_db(queryStr, (clientEmail,), True)['UID_Users'])

		if check_for_vaild_args((fn,ln,dob,ad,uid)):
			curr = db.getDB().execute("""UPDATE Client 
					SET First_Name=?, Last_Name=?, DOB=?, Address=?, Case_Status=?, Case_Type_UID=?, County_Office_UID=?, County_Office_UID=? 
					WHERE UID_Client=?;"""
					, (fn,ln,dob,ad,cs,ct,cn,co,uid))
			db.getDB().commit()
			curr.close()

		queryStr = 'SELECT User_Name FROM Users WHERE UID_Users=?'
		c_email = query_db(queryStr, (uid,), True)

		## todo: display unable to update
		return redirect(url_for('userViews.client_info', ce=c_email['User_Name']))

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))


@bp.route('/myClients/update/officeData', methods=('GET', 'POST'))
@login_required
def update_clientOfficeData():
	if g.user['social_worker'] == 1:
		of = request.form['office']
		
		if request.method == 'POST':
			uid = int(request.form['uid'])
		else:
			clientEmail = request.args.get('ce')

			queryStr = 'SELECT UID_Users FROM Users WHERE User_Name=?'
			uid = int(query_db(queryStr, (clientEmail,), True)['UID_Users'])

		if check_for_vaild_args((of,uid)):
			curr = db.getDB().execute('UPDATE Client SET County_Office_UID=? WHERE UID_Client=?', (of,uid))
			db.getDB().commit()
			curr.close()
		else:
			print('invaild args' + of + uid)


		queryStr = 'SELECT User_Name FROM Users WHERE UID_Users=?'
		c_email = query_db(queryStr, (uid,), True)

		## todo: display unable to update
		return redirect(url_for('userViews.client_info', ce=c_email['User_Name']))

	else:
		## current person logged in is not a social worker
		redirect(url_for('auth.login'))

@bp.route('/notImplemented')
def notImplemented():
	return render_template('notImplemented.html',
			year=datetime.now().year,
			title='Not Implemented');