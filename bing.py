#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
from BeautifulSoup import BeautifulSoup
import urllib2

def bing(user):
	imageArr = []
	for x in range(1,2):
		#Search Query
		value = user
		X = value.replace(" ", "%20"); #Replace spaces with %20
		link = 'http://www.bing.com/images/search?q='+X
		page=urllib2.urlopen(link)
		soup = BeautifulSoup(page.read())
		images=soup.findAll('div',{'class':'dg_u'})

		for element in images:
			text = unicode.join(u'\n',map(unicode,element))  # Convert Beautiful Soup to String
			#--------Link Isolation-------#
			beg = "imgurl"
			end = ",oh"
			image_link = text[text.find(beg)+8:text.find(end)-1]
			imageArr.append(image_link)
			#print image_link
			#-----End Link Isolation----#
	return imageArr

import json

form = cgi.FieldStorage() #Fetch the form data if any by get or post
if "namevalue" in form: #if image uuid exits in form parameters
	namevalue = form.getvalue("namevalue")
	checkname = getNameAttribute(addslashes(namevalue))
	if checkname:
		finalresponse = [0,'Attribute name Exits.']
	else:
		attrimage = getImageByName(encodeCharAt(namevalue))
		if attrimage:
			finalresponse = [0,attrimage]
		else:
			imageArr = bing(namevalue)
			finalresponse = [1,imageArr]
else:
	finalresponse = []

output(json.dumps(finalresponse))
