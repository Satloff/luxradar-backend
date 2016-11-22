#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
import datetime
# MAIN
#
# Handle invitation link sent to user via invitee.
#

form = cgi.FieldStorage() #Fetch the form data if any by get or post
if "pid" in form:
	userid = form.getvalue("pid")
	userid = userid.decode('base64','strict')
	msg =  create_cookie('userrefer',userid) #create cookie for user used at time of registration.
	finalhtml = 'Reload <script> window.location = "'+SITEURL+'";</script>'
	output(finalhtml,msg)

else:
	finalhtml = 'Reload <script> window.location = "'+SITEURL+'";</script>'
	output(finalhtml)

