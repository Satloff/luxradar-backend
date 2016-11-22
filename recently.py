#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

# MAIN
#
# Determine if any values are passed to the Python script
#
headerhtml  = headerReturn(1)
topFile = headerhtml[0]
bottomFile= headerhtml[1]

form = cgi.FieldStorage()
	
if debug: debughtml = debughtml + "[Main] Arguments are: "+str(form)+"<br>"

if debug: debughtml = debughtml + "[Main] DB is: open<br>"
searchname = ''
searchtype = ''

finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container">		<div class="font1 font2" style="text-align: left; margin: 0px auto; width: 339px;">Page not Found.</div></div></div>'
html = topFile.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile

try:
	if get_cookie("userdatasite"):
		finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container"><div class="font1 font2" style="text-align: left; margin: 0px auto;">	--userhtml--	</div></div></div>'
		htmluser = recentActivity()
		finalhtml1 = finalhtml1.replace("--userhtml--",(htmluser)).replace("--pagination--",'')
		html = topFile.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile
	else:
		html = '<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>'
	html = encodeCharAt(html) #encode special characters
	output(html)
except Exception , e:
	output(str(e))
