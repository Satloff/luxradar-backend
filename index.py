#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

# MAIN
#
# Home page of site. 
#

headerhtml  = headerReturn(1) #call header function
topFile = headerhtml[0] #header html
bottomFile= headerhtml[1] #Footer html

form = cgi.FieldStorage()  #Fetch the form data if any by get or post
	

searchname = ''
searchtype = ''

#404 page not found html
finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container">		<div class="font1 font2" style="text-align: left; margin: 0px auto; width: 339px;">Page not Found.</div></div></div>'
html = topFile.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile

try:
	finalhtml1 = Read_File("homepage.html") #read home page template file
	limit = 9 #limit for images
	if "name" in form : #check if name {value = (popular,latest,following etc)} exist in Post parameters for ajax pagination
		html = ''
		name = form.getvalue("name")
		if form.getvalue("pageid") is None: #set default values
			pageid = 1
			start = 0
		else:
			pageid = int(form.getvalue("pageid"))
			start = (int(pageid) - 1) * limit
		if "start" in form:
			start = int(form.getvalue("start"))
			pageid = int(start/limit) 
			
		if name == 'popular':
			html = popular(start,limit)   #get all popular images
			if html != '':
				html = html + '<a class="endless_more_1">&nbsp;</a>'
			else:
				html = ''
		elif  name == 'latest':
			html = latest(start,limit) #get all latest images
			if html != '':
				html = html +' <a class="endless_more_1">&nbsp;</a>'
			else:
				html = ''
		elif  name == 'following':
			html = following(start,limit)  #get all following images
			if html != '':
				html = html+'<a class="endless_more_1">&nbsp;</a>'
			else:
				html = ''
		elif  name == 'needshelp':
			html = needshelp(start,limit) #get all need help (need to assign attributes) images
			if html != '':
				html = html+'<a class="endless_more_1">&nbsp;</a>'
			else:
				html = ''
	
	else: #by default page display 
		popularhtml = popular(0,limit)  #get popular images
		latesthtml = latest(0,limit) #get latest images
		needshelphtml = needshelp(0,limit) #get needshelp images
		followinghtml = following(0,limit) #get following images
		userdata = headerhtml[2] #get user data
		#Parse all varible to template to give html output 
		finalhtml1 = finalhtml1.replace("--popular--",popularhtml).replace("--latest--",latesthtml).replace("--needshelp--",needshelphtml).replace("--following--",followinghtml).replace("--userid--",str(userdata[2]))
		finalhtml1 = finalhtml1 + get_likeForm(False)
		html = topFile.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile
	html = encodeCharAt(html) #Encode special Charaters 
	output(html)
except Exception , e:
	output(str(e))
