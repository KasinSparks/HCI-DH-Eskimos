## followed flask tutorial from flask's website for help with auth code
## http://flask.pocoo.org/docs/1.0/tutorial/views/

import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime

from FlaskWebProject.db import query_db
from . import db

# generates a blueprint for the authentication
bp = Blueprint('auth', __name__, url_prefix='/auth')


## some of function code is from http://flask.pocoo.org/docs/1.0/tutorial/views/
@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		## get the data from the html form
		username = request.form['username']
		password = request.form['password']

		## request to open the database and get the reference to it
		from . import db
		database = db.getDB()

		## set a var. for error
		errorVar = None

		## set the sql query
		sqlQuery = 'SELECT * FROM Users WHERE User_Name = ?'

		## get the data for the user
		## using the ? in the query and a tuple will use the flask
		## lib. to defend against sql injections
		user = database.execute(sqlQuery, (username,)).fetchone()


		## check if the username exist in the database
		if user is None:
			errorVar = 'Incorrect login information. Please try again.'
		elif not check_password_hash(user['Password'], password):
			errorVar = 'Incorrect login information. Please try again.'

		## check to see if an error occured
		if errorVar is None:
			# seesion is a special data type (dict) that stored data while the user
			# is using the web app

			## clear any existing session
			session.clear();
			session['user_id'] = user['UID_Users']
			return redirect(url_for('userViews.profile'))

		## an error has occured
		print(errorVar)
		flash(errorVar)

	return render_template('auth/login.html',
		title='Home Page',
		year=datetime.now().year
		)

# allows user to create an account that will be verified by their social worker
@bp.route('/create', methods=('GET', 'POST'))
def create_account():

	## check for url args
	countyVal = request.args.get('county')

	if countyVal is None:
		countyVal = 1
	else:
		## TODO: wrap this in try catch for type execptions
		countyVal = int(countyVal)
		

	from FlaskWebProject.db import query_db

	## get the list of county offices to display
	countyList = query_db('SELECT UID_County_Office, Office_Name FROM County_Office')

	## get the list of social workers
	socialWorkerList = query_db('SELECT First_Name, Last_Name, UID_Social_Worker FROM Social_Worker WHERE County_Office_UID=?', (countyVal,))



	return render_template(
		'auth/createProfile.html',
		title='Create Profile',
		year=datetime.now().year,
		counties=countyList,
		cv=countyVal,
		workers=socialWorkerList
		)

## put the new profile into the database and redirect
@bp.route('/create/submit', methods=('GET', 'POST'))
def submit_new_profile():
	## ensure the all data fields have been submited
	username = request.form['username']
	pt_password = request.form['password']
	firstName = request.form['first_name']
	lastName = request.form['last_name']
	dob = request.form['dob']
	address = request.form['address']
	county_office = request.form['county']
	social_worker = request.form['social_worker']

	can_submit = True

	if username is None or pt_password is None or firstName is None or lastName is None or dob is None or address is None or county_office is None or social_worker is None:
		can_submit = False
	elif username == '' or pt_password == '' or firstName == '' or lastName == '' or dob == '' or address == '' or county_office == '' or social_worker == '':
		can_submit = False

	if can_submit:
		## add the data to the database and redirect to account success created page
		## create a notification for the social worker to approve the request for a profile

		## TODO: add code to check to make sure that these insert into db, e.g. a dupliate of user name wont insert
		userAddCommand = 'INSERT INTO Users (User_Name, Password, Client, Is_Verified) VALUES (?,?,?,?)'
		notificationAddCommand = 'INSERT INTO Notifications (UID_Client, UID_Social_Worker, Notification_Type, Has_Been_Read) VALUES (?,?,?,?)'
		clientAddCommand = 'INSERT INTO Client (UID_Client, First_Name, Last_Name, DOB, Address, Social_Worker_UID, County_Office_UID) VALUES (?,?,?,?,?,?,?)'

		database = db.getDB()
		database.execute(userAddCommand, (username, generate_password_hash(pt_password), 1, 0))
		database.commit()
		uid = db.query_db('SELECT UID_Users FROM Users WHERE User_Name=?', (username,), True)

		database = db.getDB()
		database.execute(clientAddCommand, (int(uid['UID_Users']), firstName, lastName, dob, address, int(social_worker), int(county_office)))
		database.execute(notificationAddCommand, (int(uid['UID_Users']), int(social_worker), 1, 0))
		database.commit()
		database.close()

		return render_template('loginSuccessTest.html')

	else:
		## redirect back to here with previous data entered
		## check for url args
		countyVal = request.args.get('county')

		if countyVal is None:
			countyVal = 1
		else:
			## TODO: wrap this in try catch for type execptions
			countyVal = int(countyVal)		

		## get the list of county offices to display
		countyList = query_db('SELECT UID_County_Office, Office_Name FROM County_Office')

		## get the list of social workers
		socialWorkerList = query_db('SELECT First_Name, Last_Name, UID_Social_Worker FROM Social_Worker WHERE County_Office_UID=?', (countyVal,))

		redirect(url_for('auth.create_account'))
		return render_template(
			'auth/createProfile.html',
			title='Create Profile',
			year=datetime.now().year,
			counties=countyList,
			cv=countyVal,
			workers=socialWorkerList,
			pw=pt_password,
			un=username,
			fn=firstName,
			ln=lastName,
			db=dob,
			a=address,
			uid_sw=social_worker
			)


## check to see if a user is logined in and will use the user id for the current request
@bp.before_app_request
def load_logged_in_user():
	## gets the users id number that is stored in the session when a user logins in
	user_id = session.get('user_id')

	## get and return the user data
	if user_id is None:
		g.user = None
	else:
		sqlQuery = 'SELECT * FROM Users WHERE UID_Users = ?'
		from . import db
		database = db.getDB()
		g.user = database.execute(sqlQuery, (user_id,)).fetchone()


## log the current user out
@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('userViews.index'))


## require a user to be logged in to access a view
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view