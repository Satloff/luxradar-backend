#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
from sendemail import email
import uuid
import datetime

form = cgi.FieldStorage() #Fetch the form data if any by get or post
errormsg= ""
if "pid" in form:
	html = activate_user(form.getvalue("pid")) #Activate user account by confirmation link sent by email.
	if html:
		errormsg= "alert('Account is activated.'); "
	else:
		errormsg= "alert('Link expired'); "

#Redirect user to home page
finalhtml = '<html><body><script>'+errormsg+'window.location="'+SITEURL+'index.py";</script></body></html>';
output(finalhtml)
