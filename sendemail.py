#!/usr/bin/python
# -*- coding: utf-8 -*-
#http://segfault.in/2010/12/sending-gmail-from-python/
from config import *

import re
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# MAIN
#
# Send email via SMTP Server Default Functions. 
#

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
sender = 'info@luxradar.com' #Sender email id
password = "reader123" #Sender password to authenticate SMTP Server 

def email_attach(data):
    msg = MIMEMultipart()
    msg['Subject'] = data['subject']
    msg['To'] = data['recipient']
    msg['From'] = sender

    img = MIMEImage(open(data['path'], 'rb').read(), _subtype=data['filetype'])
    img.add_header('Content-Disposition', 'attachment', filename=data['filename'])
    msg.attach(img)

    part = MIMEText('text', "html")
    part.set_payload(data['message'])
    msg.attach(part)
 
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password) 
    session.sendmail(sender, msg['To'], msg.as_string())
    session.quit()

def email(data):
	subject = data['subject']
	body = data['message']
	headers = ["From: " + sender,
		       "Subject: " + subject,
		       "To: " + data['recipient'],
		       "MIME-Version: 1.0",
		       "Content-Type: text/html"]
	headers = "\r\n".join(headers)
	 
	#session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	session= smtplib.SMTP('localhost')
	#session.ehlo()
	#session.starttls()
	#session.ehlo
	#session.login(sender, password)
	 
	session.sendmail(sender, data['recipient'], headers + "\r\n\r\n" + body)
	session.quit()

def emailtest(data):
	subject = data['subject']
	body = data['message']
	headers = ["From: {0}".format(sender),
		       "Subject: {0}".format(subject),
		       "To: {0}".format(data['recipient']),
		       "MIME-Version: 1.0",
		       "Content-Type: text/html"]
	headers = "\r\n".join(headers)
	 
	#session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	session= smtplib.SMTP('localhost') 
	#~ session.ehlo()
	#~ session.starttls()
	#~ session.ehlo
	#~ session.login(sender, password)
	 
	session.sendmail(sender, data['recipient'], headers + "\r\n\r\n" + body)
	session.quit()

if os.environ['REQUEST_METHOD'] == 'GET': #Only POST method Allowed on thi page.	
	form = cgi.FieldStorage()
	if "actionSample" in form:	
		print "Content-type:text/html\r\n\r\n"
		print "Trigger Emails\r\n"
		data = {'subject':"forget password email","message":"Forget your password.....","recipient":"rohitg.ghrix@gmail.com"}
		print data 
		email(data)

