#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
from PIL import Image

# MAIN
#
# Page to create Thumbs link for images. 
#

noimg= SITEURL+'thumbs/no_photo.jpg'
try:
	form = cgi.FieldStorage() #Fetch the form data if any by get or post
	if "img" in form : #if img exits in form parameters
		imagepath = form.getvalue("img")
		if os.path.isfile('thumbs/'+imagepath): #check if image exits in thumbs
			noimg = ('thumbs/'+imagepath)
		else:  #Create thumb of image
			if os.path.isfile(imagepath):
				newdir = imagepath.split('/')
				dirstr = 'thumbs/' + imagepath.replace(newdir[-1],'')
				#output(dirstr)
				#sys.exit()
				if not os.path.exists(dirstr):
					os.makedirs(dirstr)
				imageorg = Image.open(imagepath)
				temp = imageorg.copy()
				temp.save('thumbs/'+imagepath, quality=95)  
				image = image_resize('thumbs/'+imagepath, [240,1222532], rotate=None)
				noimg = (image)
			else:
				noimg = (noimg)
	else:
		noimg = (noimg) #return no photo
	
	jpgfile = Image.open(noimg) #read image content
	data_uri = open(noimg, 'rb').read()
	print "Content-type:image/"+jpgfile.format+"\r\n" #display image
	print data_uri
except Exception , e:
	output(str(e))

