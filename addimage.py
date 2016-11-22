#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
from sendemail import email
import uuid
import datetime

# MAIN
#
# Page add images. 
#

form = cgi.FieldStorage() #Fetch the form data if any by get or post
#html Start here
if get_cookie("userdatasite"):
	html = ''
	category = processCategoryHtml1()
	headerhtml  = headerReturn()
	topFile = headerhtml[0]
	bottomFile= headerhtml[1]
	userdata = headerhtml[2]
	imagessrc = '<div style="height:300px; width:210px;" id="dragandrophandler">Drop Image Here</div><p class="msg">ds</p><br><br><div id="status1"></div>'
	myaccount = Read_File("addimages.html").replace('--imagetitle--','').replace('--imagessrc--',imagessrc).replace('--error--','').replace("--category--",category)
	html = html + topFile.replace("--serachType--",'').replace("--SITEURL--",SITEURL).replace("--imagename--",'').replace("--attributesList1--",'').replace("--search-type--",'').replace("--search-name--",'').replace('--imagessrc--',imagessrc)
	html = html + myaccount
	
	output(html)
else: #Redirect to home page incase not login user
	finalhtml = '<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>';
	output(finalhtml)
