import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# set the config file for the database


# returns the current data base
def getDB():
	if 'db' not in g:
		g.db = sqlite3.connect(current_app.config['DATABASE'], 
								detect_types = sqlite3.PARSE_DECLTYPES)
		g.db.row_factory = sqlite3.Row

	return g.db

# close the current data base
def closeDB(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()

# from http://flask.pocoo.org/docs/1.0/patterns/sqlite3/
def query_db(query, args=(), one=False):
	cur = getDB().execute(query, args)
	rv = cur.fetchall()
	cur.close()

	# close database connection
	closeDB()
	return (rv[0] if rv else None) if one else rv

def initDB():
	db = getDB()

	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def initDB_command():
	initDB()
	click.echo('Initialized the database')

def init_app(app):
	app.teardown_appcontext(closeDB)
	app.cli.add_command(initDB_command)