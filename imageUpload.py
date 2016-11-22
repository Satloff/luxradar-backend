#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
from PIL import Image
import cgitb; cgitb.enable()
import boto
from boto.s3.key import Key
import logging,os


# MAIN
#
# Page to create Thumbs link for images. 
#
#http://www3.images.coolspotters.com/photos/572321/alligator-profile.jpg
#4104f0185b.jpg
#4104f0185b
import urllib, cStringIO

try:
	form = cgi.FieldStorage() #Fetch the form data if any by get or post
	uuid = form.getvalue("uuid")
	filename = form.getvalue("filename")
	imageurl1 = form.getvalue("imageurl")
	imageurl = cStringIO.StringIO(urllib.urlopen(imageurl1).read())
	imagename = imageurl1.split('/')
	imageext1 = imagename[-1].split('.')
	imageext = imageext1[-1]
	filename = uuid+'.'+imageext
	dir = IMAGEFOLDER
	first = uuid[0]+"/"
	second = uuid[1]+"/"	
	third = uuid[2]+"/"
	dirstr =  str(dir+first+second+third)
	dirstr1 = str("Images"+"/"+uuid[0]+"/"+uuid[1]+"/") #Assign directory path for image
	imagepath = dirstr+filename
	imagepath1 = dirstr1+filename
	
	if os.path.isfile(imagepath):
		output(filename+" already Exits")
	else:
		if not os.path.exists(dirstr):
			os.makedirs(dirstr)
		imageorg = Image.open(imageurl)
		temp = imageorg.copy()
		temp.save(imagepath, quality=100)  
		
		
		########### upload image on aws using boto##############
		
		# set boto lib debug to critical
		logging.getLogger('boto').setLevel(logging.CRITICAL)
		bucket_name = 'luxradarimages'
		# connect to the bucket
		#id= "img161"
		conn = boto.connect_s3('AKIAJ4RN764AJXNPZ3FQ','PlOdeTmxyoDNs8b7cgxlz40Rw+mFdFdznRajs54C')
		bucket = conn.get_bucket(bucket_name)
		# go through each version of the file
		key = dirstr1+filename 
		full_key_name = dirstr+filename
		# create a key to keep track of our file in the storage

		#k = Key(bucket)
		#k.key = key
		k = bucket.new_key(key)
		k.set_contents_from_filename(full_key_name)
		# we need to make it public so it can be accessed publicly
		# using a URL like http://s3.amazonaws.com/bucket_name/key
		k.make_public()
		# remove the file from the web server
		#os.remove(fn)
		#print "<center><h1>Welcome to python world.</h1></center>"
		output(filename)	
		########### end upload image on aws using boto##############	
				
except Exception , e:
	output(str(e))

