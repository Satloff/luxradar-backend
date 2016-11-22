#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

# MAIN
#
# Reset User password. 
#

form = cgi.FieldStorage() #Fetch the form data if any by get or post
if "pid" in form: #Check link is valid or not
	if "action" not in form: #Display Reset password Form
		resetpasswordcheck = reset_password(form.getvalue("pid"))
		if resetpasswordcheck: #If link is valid or not expired
			resetpassword = Read_File("resetpassword.html")
			finalhtml = resetpassword.replace('--STATICURL--',STATICURL).replace('--SITEURL--',SITEURL)
			output(finalhtml)
		else:
			finalhtml = '<html><body><script>alert("Link Expired."); window.location="'+SITEURL+'index.py";</script></body></html>';
			output(finalhtml)
	else: #handle post request for Reset password
		resetpassword = update_password(form.getvalue("password"),form.getvalue("pid"))
		finalhtml = '<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>';
		output(finalhtml)	
else:
	finalhtml = '<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>';
	output(finalhtml)
