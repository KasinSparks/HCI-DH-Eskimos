from flask import Blueprint, flash, g, redirect, render_template, request, url_for

## will be used to show 404 or 403 request
from werkzeug.exceptions import abort

#from . import auth
#from . import db

from FlaskWebProject.auth import login_required
from FlaskWebProject.db import getDB

from datetime import datetime

bp = Blueprint('userViews', __name__)

@bp.route('/index')
def index():
	return render_template(
		'auth/login.html',
		title='Login Page',
		year=datetime.now().year,
	)

@bp.route('/profile')
@login_required
def profile():
	return render_template(
		'loginSuccessTest.html',
		status='granted',
		year=datetime.now().year
		)