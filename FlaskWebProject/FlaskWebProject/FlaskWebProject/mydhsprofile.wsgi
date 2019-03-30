#!/usr/bin/python
import sys


sys.path.insert(0,"/var/www/HCI-DH-Eskimos/FlaskWebProject/FlaskWebProject/")
from FlaskWebProject import create_app
application = create_app()
