#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

# MAIN
#
# Display Search Result. 
#

headerhtml  = headerReturn(1) #call header function
topFile = headerhtml[0] #header html
bottomFile= headerhtml[1] #Footer html

form = cgi.FieldStorage() #Fetch the form data if any by get or post
	
if debug: debughtml = debughtml + "[Main] Arguments are: "+str(form)+"<br>"

if debug: debughtml = debughtml + "[Main] DB is: open<br>"

searchname = ''
searchtype = ''

#default 404 page
finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container">		<div class="font1 font2" style="text-align: left; margin: 0px auto; width: 339px;">Page not Found.</div></div></div>'
html = topFile.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile

try:
	if "name" in form : #if name (Search Text) exist in form parameters
		limit = 8 #limit to display result per page
		if form.getvalue("pageid") is None: #get pageid if any
			pageid = 1
			start = 0
		else:
			pageid = int(form.getvalue("pageid"))
			start = (int(pageid) - 1) * limit
		
		if "start" in form: #if start exist in form parameters
			start = int(form.getvalue("start"))
			pageid = int(start/limit) 
			
		type = ""
		name = form.getvalue("name") #get Search text
		if name == " " or name is None:
			name = ""
		name = name[2:]
		searchname = name
		searchtype = type
		imageUUIDList = getImageUUIDListSearch(type, name, limit,start) #get all uuid For Search text with limit
		totalcount = int(imageUUIDList[0]) #total number of result found
		#output(str(imageUUIDList[1]))
		#sys.exit()
		if "submitPage" not in form :	#if submitPage (For ajax pagination result) not exist in form parameters
			if totalcount == 0:
				userhtml = "Nothing found with {0}".format(name)
			else:
				userhtml = processSearchPageImages(imageUUIDList[1],name) #process all image data and return html
				#userhtml = ''
			#output(userhtml)
			#sys.exit()
			#~ finalhtml1 = Read_File("searchresult.html").replace("--searchfor--",(name))
			finalhtml1 = Read_File("searchresult.html").replace("--searchfor--",(name))
			pagination = ''
			'''if totalcount > limit:
				pagination = getPagination(SITEURL+'search.py?name='+name,pageid,totalcount,limit,1)'''
		
			userlikedform = get_likeForm(True) #get form for liking the images
			userdata = headerhtml[2] #get user data
			
			#Parse all varible to template to give html output
			finalhtml1 = finalhtml1.replace("--userhtml--",userhtml).replace("--pagination--",userlikedform+pagination).replace("--total--",str(totalcount)).replace("--userid--",str(userdata[2]))
			html = topFile.replace("--search-type--",'').replace("--search-name--",(name)) + finalhtml1 + bottomFile
		else:
			#Run in case of pagination hit via ajax
			userhtml = processSearchPageImages(imageUUIDList[1],name,0) #process all image data and return html
			if userhtml != '':
				html = '<div class="images-grid" >'+userhtml+'<a class="endless_more">&nbsp;</a></div>'
			else:
				html = ''
	else:
		html = '<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>'
		html = 'test'
	html = encodeCharAt(html)	
	output(html) #Display output Html
except Exception , e:
	output(str(e))
