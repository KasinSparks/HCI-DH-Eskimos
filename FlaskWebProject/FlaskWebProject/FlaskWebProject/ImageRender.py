from flask import current_app

import os
import base64


## return a image in base64 format for html webpage to render
## this disallows the user to see/access the path the image came from
def imgGet(image, pathInc=False):

	if not pathInc:
		with open(os.path.join(current_app.config['UPLOAD_FOLDER'], image), 'rb') as image_file:
			tempImg = base64.b64encode(image_file.read())
	else:
		with open(image, 'rb') as image_file:
			tempImg = base64.b64encode(image_file.read())
	
	tempImg = tempImg.decode('utf-8') # if you start geting no image check here
											# I had to change this when i converted project to windows

	return tempImg
