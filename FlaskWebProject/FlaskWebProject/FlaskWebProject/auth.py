## followed flask tutorial from flask's website for help with auth code
## http://flask.pocoo.org/docs/1.0/tutorial/views/

import functools

from flask import Blueprint, flash, g, redirect, render_template, request, seesion, url_for

from werkzeug.security import check_password_hash, generate_password_hash

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
		db = getDB()

		## set a var. for error
		errorVar = None

		## set the sql query
		sqlQuery = 'SELECT * FROM Users WHERE User_Name = ?'

		## get the data for the user
		## using the ? in the query and a tuple will use the flask
		## lib. to defend against sql injections
		user = db.execute(sqlQuery, (username,)).fetchone()


		## check if the username exist in the database
		if user is None:
			error = 'Incorrect login information. Please try again.'
		elif not check_password_hash(user['Password'], password):
			error = 'Incorrect login information. Please try again.'

		## check to see if an error occured
		if error is None:
			# seesion is a special data type (dict) that stored data while the user
			# is using the web app

			## clear any existing session
			session.clear();
			session['user_id'] = user['UID_Users']
			return redirect(url_for('index'))

		## an error has occured
		flash(error)

	return render_template('auth/login.html')


## check to see if a user is logined in and will use the user id for the current request
@bp.before_app_request
def load_logged_in_user():
	## gets the users id number that is stored in the session when a user logins in
	user_id = seesion.get('user_id')

	## get and return the user data
	if user_id is None:
		g.user = None
	else:
		sqlQuery = 'SELECT * FROM Users WHERE UID_Users = ?'
		g.user = getDB().execute(sqlQuery, (user_id,)).fetchone()


## log the current user out
@bp.route('logout')
def logout():
	session.clear()
	return redirect(url_for('index'))


## require a user to be logged in to access a view
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view