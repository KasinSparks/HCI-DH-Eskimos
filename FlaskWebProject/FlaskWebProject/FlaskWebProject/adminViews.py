from flask import Blueprint, flash, g, redirect, render_template, request, url_for

## will be used to show 404 or 403 request
from werkzeug.exceptions import abort

from FlaskWebProject.auth import login_required
from FlaskWebProject.db import getDB

from datetime import datetime

bp = Blueprint('adminViews', __name__, url_prefix='/add')


@bp.route('/admin')
@login_required
def admin():
	return NotImplemented


@bp.route('/user', methods=('GET', 'POST'))
@login_required
def user():

	return NotImplemented