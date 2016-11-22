#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *

import uuid
from decimal import *
import datetime
import logging

# MAIN
#
# Default image resize script.
#


import PIL
from PIL import Image

print """\
Content-Type: text/html\n
"""

def image_resize(imagepath, dimensions, rotate=None): 

	""" Resizes an image to be as close as possible to specified dimensions. Image is a django image-model-field.
		Will both scale up and down the image to meet this while keeping the proportions
		in width and height
	"""

	if imagepath and os.path.isfile(imagepath):

		im = Image.open(imagepath)
		logging.debug ('resizing image from %s x %s --> %s x %s ' % (im.size[0], im.size[1], dimensions[0], dimensions[1]))

		if rotate:
		    logging.debug('first rotating image %s' % rotate)
		    im = im.rotate(90)

		srcWidth = Decimal(im.size[0])
		srcHeight = Decimal(im.size[1])

		resizeWidth = srcWidth
		resizeHeight = srcHeight

		aspect = resizeWidth / resizeHeight # Decimal

		logging.debug('resize aspect is %s' % aspect)

		if resizeWidth > dimensions[0] or resizeHeight > dimensions[1]:
		    # if width or height is bigger we need to shrink things
		    if resizeWidth > dimensions[0]:
		        resizeWidth = Decimal(dimensions[0])
		        resizeHeight = resizeWidth / aspect

		    if resizeHeight > dimensions[1] :
		        aspect = resizeWidth / resizeHeight
		        resizeHeight = Decimal(dimensions[1])
		        resizeWidth = resizeHeight * aspect

		else:
		    # if both width and height are smaller we need to increase size
		    if resizeWidth < dimensions[0]:
		        resizeWidth = Decimal(dimensions[0])
		        resizeHeight = resizeWidth / aspect

		    if resizeHeight > dimensions[1] :
		        aspect = resizeWidth / resizeHeight
		        resizeHeight = Decimal(dimensions[1])
		        resizeWidth = resizeHeight * aspect

		im = im.resize((resizeWidth, resizeHeight), Image.ANTIALIAS)

		logging.debug('resized image to %s %s' % im.size)
		im.save(imagepath)

	else:
		# no action, due to no image or no image in path
		pass

	return imagepath

image = image_resize('/var/www/html/scripts/luxradar_py/images/8/d/1/8d175d777d2f.jpg', [1000,800], rotate=None)

html = '<img src="http://www.luxradar.com/images/8/d/1/8d175d777d2f.jpg" alt ="Neha" />'
print html
