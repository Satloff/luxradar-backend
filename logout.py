#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

form = cgi.FieldStorage() #Fetch the form data if any by get or post
html = ''
if get_cookie("userdatasite"): #if user cookie exits
	html = delete_cookie("userdatasite") #Delete user cookie to logout.
html1 = ''
if get_cookie("userrefer"): #delete cookie in case of user invitee
	html1 = "document.cookie='userrefer=John;expires=-1';"
	
if get_cookie("fbsr_216890365177211"): #delete cookie in case of Facebook
	finalhtml = '<html><body><script>document.cookie="usernamefbcheck=logout";'+html1+'window.location="'+SITEURL+'index.py";</script></body></html>';
else:
	finalhtml = "<html><body><script>document.cookie='fbm_216890365177211=John;expires=-1';"+html1+"window.location='"+SITEURL+"index.py';</script></body></html>";
	#finalhtml = 'document.cookie='fbsr_216890365177211=John;expires=-1';<html><body><script>window.location="'+SITEURL+'index.py";</script></body></html>';
output(finalhtml,html)
