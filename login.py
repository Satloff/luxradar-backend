#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

from sendemail import email,emailtest
import uuid
import datetime
import re

# MAIN
#
# Handle user authentication and registration and other ajax request.
#


if os.environ['REQUEST_METHOD'] == 'GET': #Only POST method Allowed on thi page.
	output("Access Deined.")
	sys.exit()
	
form = cgi.FieldStorage() #Fetch the form data if any by get or post
if "action" not in form: #Display login html
	output("Page not found.") 
else: 
	if "userlogin" in form: #handle post request for authenticate user
		html = authenticate(form)
		if "Set-Cookie:" in str(html):
			finalhtml = '1||'
			output(finalhtml,html)
		else:
			finalhtml = 'Invalid User or password.'
			output(finalhtml,html)
	elif "userregister" in form: #handle post request for user Registration
		uid = uuid.uuid4()
		htmlerror = ''
		try: #Try to Add user in DB
			html = register_user(form,str(uid)) #Create user account
			if get_cookie("userrefer"):
				update_invitation(form.getvalue("email"))
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			resetlink = SITEURL+'activate.py?pid='+str(uid) #Create Activation link
			forgethtml = Read_File("activateaccount.html")
			firstname = form.getvalue("firstname")
			lastname = form.getvalue("lastname")
			language = 'hi'
			timezone = '1'
			currency = 'USD'
			profilevisibility = 'everyone'
			fullname = str(firstname+" "+lastname)
			resetdate = datetime.date.today()
			finalhtml = forgethtml.replace('--username--',fullname).replace('--language--',language).replace('--timezone--',timezone).replace('--currency--',currency).replace('--profilevisibility--',profilevisibility).replace('--resetlink--',str(resetlink))
			data = {'subject':"Regarding your luxradar.com Signup","message":finalhtml,"recipient":form.getvalue("email")}
			email(data) #Send email verfication to user
			finalhtml = '1||To activate your account, please click the link in the activation email which has been sent to you.';
			output(finalhtml)
		else:
			finalhtml = htmlErrorHandler(htmlerror)
			output(finalhtml)
	elif "userforgot" in form: #handle post request for user forgot password
		useremail = form.getvalue("useremail")
		html = forget_password(useremail) #Check user exits in DB and Active 
		if html:
			uid = uuid.uuid4()
			resetlink = SITEURL+'resetpassword.py?pid='+str(uid) #Create Reset password link
			update_forget_password(useremail,uid) #update DB fields for reseting password
			forgethtml = Read_File("resetpasswordemail.html")
			resetdate = datetime.date.today()
			finalhtml = forgethtml.replace('--resetlink--',resetlink).replace('--useremail--',useremail).replace('--resetdate--',str(resetdate))
			data = {'subject':"Your luxradar.com account - Password Recovery Link","message":finalhtml,"recipient":useremail}
			email(data) #Send Email
			finalhtml = '1||To reset your password, please click the link in the email which has been sent to you.' #redirect user to login page
			output(finalhtml)
		else:
			finalhtml = 'Email not found in our records.'
			output(finalhtml)
	elif "userupdate" in form: #handle post request for user data update
		userdata = getUserByID(form.getvalue("userupdate")) #get all dat of user by id
		if form.getvalue("userupdate") == str(userdata[0]['id']):
			if form.getvalue("password") is None or form.getvalue("password") == '' : #In case of blank password update old password
				password = userdata[0]['password']
				
			else: #In case of new password 
				userpwd = form.getvalue("password")
				h = hashlib.new('ripemd160')
				h.update(userpwd)
				password = h.hexdigest()

			formdata={}
			if form.getvalue("email") is None:
				formdata['useremail'] =userdata[0]['useremail']
			else: 
				formdata['useremail'] = form.getvalue("email")
			formdata['username']=userdata[0]['username']
			formdata['fullname']=form.getvalue("fullname")
			formdata['password']=password
			imageerror = ''
			try: #Try to Update user in DB
				finalhtml = update_user(formdata,form.getvalue("userupdate")) #Create user account
				profilepic = ''
				if "profilephoto" in form:
					fileitem = form['profilephoto']	
					if fileitem.filename:
						#output(fileitem.filename)
						#sys.exit()
						# strip leading path from file name to avoid directory traversal attacks
						fn = os.path.basename(fileitem.filename)
						finaltype = fn.split('.')[-1]
						filesize1 = [400,400]
						randm = form.getvalue("userupdate")
						dirstr = IMAGEFOLDER+"/userimages/"
						if finaltype in ['jpg','jpeg','gif','png']:
							imageerror = ''
							profilepic = randm +'.'+finaltype
							open(dirstr + randm +'.'+finaltype, 'wb').write(fileitem.file.read())
							while True:
								try:
									image = image_resize(dirstr + randm +'.'+finaltype, [filesize1[0],filesize1[1]], rotate=None)
									break
								except IOError:
									time.sleep(3)
						else:
							imageerror = "Invalid file format for profile picture."
				update_userprofile(form,form.getvalue("userupdate"),profilepic)
			except Exception , e:
				finalhtml = False
				htmlerror = str(e)
			if finalhtml:	
				if form.getvalue("userupdate") == str(userdata[0]['id']) :
					msguser =  create_cookie('userdatasite',str(formdata['fullname'])+'::'+str(userdata[0]['id'])+'::'+str(form.getvalue("userupdate"))+'::'+str(form.getvalue("email")))
				finalhtml = '1||Account updated.'+imageerror
				output(finalhtml,msguser)
			else:
				htmlerror = htmlErrorHandler(htmlerror)
				output(htmlerror)
		else:
			output(str(userdata))
	elif "addattribute" in form: #handle post request for adding image attribute
		if get_cookie("userdatasite"):
			uid= str(form.getvalue("addattribute"))
			AttributeName= str(form.getvalue("AttributeName"))
			AttributeValue= str(form.getvalue("AttributeValue"))
			status = 0
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select attribute_name from `image_attributes` where  `attribute_type`='{0}' and `attribute_name`='{1}' and `uuid`='{2}'".format(AttributeName,AttributeValue,uid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			curs1.close()
			if totalRecords1 > 0:
				finalhtml = '1||Attribute already Exits.'
			else:
				curs1 = conn.cursor(oursql.DictCursor)
				queryTerm = "Insert into `image_attributes` SET  `attribute_type`='{0}',`attribute_name`='{1}',`uuid`='{2}',`status`='{3}'".format(AttributeName,AttributeValue,uid,status)
				curs1.execute(queryTerm)
				userdata = get_loginsuer()
				queryTerm1 = "Insert into `user_images_attributes` SET  `userid`='{0}',`uuid`='{1}',`attributeid`='{2}'".format(userdata[2],uid,curs1.lastrowid)
				curs1.execute(queryTerm1)
				finalhtml = '1||Attribute Added. Request Sent for admin approval.';
				curs1.close()
			output(finalhtml)
		else:
			output("Authentication fail.")
	elif "fbregister" in form: #handle post request for user Registration via facebook
		uid = uuid.uuid4()
		htmlerror = ''
		try: #Try to Add user in DB
			html = register_user_fb(form,str(uid)) #Create user account
		except Exception , e:
			html = ''
			htmlerror = str(e).replace('"',"`")
		if "Set-Cookie:" in str(html):
			finalhtml = '1||'
			output(finalhtml,html)
		else:
			finalhtml = htmlErrorHandler(htmlerror)
			output(finalhtml)
	elif "googleregister" in form: #handle post request for user Registration via google
		uid = uuid.uuid4()
		htmlerror = ''
		try: #Try to Add user in DB
			html = register_user_google(form,str(uid)) #Create user account
		except Exception , e:
			html = ''
			htmlerror = str(e).replace('"',"`")
		if "Set-Cookie:" in str(html):
			finalhtml = '1||'
			output(finalhtml,html)
		else:
			htmlerror = htmlErrorHandler(htmlerror)
			output(htmlerror)
	elif "addusername" in form: #handle post request for username in facebook and twitter
		htmlerror = ''
		userdata = get_loginsuer()
		uid = userdata[2]
		try: #Try to Add user in DB
			html = update_user_username(form,str(uid)) #Create user account
		except Exception , e:
			html = ''
			htmlerror = str(e).replace('"',"`")
			
		if  htmlerror == '':
			finalhtml = "1||";
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
	elif "deleteuserpic" in form: #handle post request for delete user profile pic
		htmlerror = ''
		uid = form.getvalue("deleteuserpic")
		try: #Try to Add user in DB
			html = deleteuserpic(str(uid)) #delete user pic
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
	elif "featuredimage" in form: #handle post request for user featured image
		htmlerror = ''
		imageid = form.getvalue("featuredimage")
		usertrue = form.getvalue("usertrue")
		userid = form.getvalue("userid")
		featuredimagetrue = form.getvalue("featuredimagetrue")
		try: #Try to Add user in DB
			if featuredimagetrue == '1':
				imageid = ''
			if usertrue == '0':
				queryTerm = "Insert into `user_profile` SET `featuredimg`='{0}',`userid`='{1}'".format(imageid,userid)
			else:
				queryTerm = "UPDATE `user_profile` SET  `featuredimg`='{0}' WHERE `userid`='{1}'".format(imageid,userid)
			curs1 = conn.cursor(oursql.DictCursor)
			curs1.execute(queryTerm)
			curs1.close()
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
		
		
	elif "attribute_actions1" in form: #handle post request for user attribute action
		htmlerror = ''
		imageid = form.getvalue("attributeimage")
		userid = form.getvalue("userid")
		wantit1 = form.getvalue("wantit")		
		try:                 #Try to Add user in DB
			if wantit1 == "liked":
				wantit = 'liked'
			else:
				wantit = "unliked"	
		
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select wantit from `attribute_actions` where  `userid`='{0}' and `imageid`='{1}'".format(userid,imageid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			if totalRecords1 > 0:
				queryTerm1= "UPDATE `attribute_actions` SET  `wantit`='{2}' WHERE `userid`='{1}' and `imageid`='{0}'".format(imageid,userid,wantit)
				curs1.execute(queryTerm1)
			else:
				
				queryTerm1 = "Insert into `attribute_actions` SET `imageid`='{0}',`userid`='{1}',`wantit`='{2}' ".format(imageid,userid,wantit)
				curs1.execute(queryTerm1)
			  
			curs1.close()
			html = True 
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
	
	elif "attribute_actions2" in form: #handle post request for user attribute action
		htmlerror = ''
		imageid = form.getvalue("attributeimage")
		userid = form.getvalue("userid")
		ownit1 = form.getvalue("ownit")
		
		try:                 #Try to Add user in DB				
			if ownit1 == "liked":
				ownit = "liked"
			else:
				ownit = "unliked"		
		
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select ownit from `attribute_actions` where  `userid`='{0}' and `imageid`='{1}'".format(userid,imageid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			if totalRecords1 > 0:
				queryTerm1= "UPDATE `attribute_actions` SET  `ownit`='{2}' WHERE `userid`='{1}' and `imageid`='{0}'".format(imageid,userid,ownit)
				curs1.execute(queryTerm1)
			else:
				queryTerm1 = "Insert into `attribute_actions` SET `imageid`='{0}',`userid`='{1}',`ownit`='{2}' ".format(imageid,userid,ownit)
				curs1.execute(queryTerm1)
			  
			curs1.close()
			html = True 
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
	
	elif "attribute_actions3" in form: #handle post request for user attribute action
		htmlerror = ''
		imageid = form.getvalue("attributeimage")
		userid = form.getvalue("userid")
		sale1 = form.getvalue("sale")
		
		try:                 #Try to Add user in DB		
			if sale1 == "liked":
				sale = "liked"
			else:
				sale = "unliked"				
		
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select sale from `attribute_actions` where  `userid`='{0}' and `imageid`='{1}'".format(userid,imageid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			if totalRecords1 > 0:
				queryTerm1= "UPDATE `attribute_actions` SET  `sale`='{2}' WHERE `userid`='{1}' and `imageid`='{0}'".format(imageid,userid,sale)
				curs1.execute(queryTerm1)
			else:
				
				queryTerm1 = "Insert into `attribute_actions` SET `imageid`='{0}',`userid`='{1}',`sale`='{2}' ".format(imageid,userid,sale)
				curs1.execute(queryTerm1)
			  
			curs1.close()
			html = True 
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 	
		
		
#------------ setting preference----------------------------------------#

	elif "userupdate1" in form: #handle post request for user attribute action
		htmlerror = ''
		userid = form.getvalue("userupdate1")
		language=form.getvalue("language")
		timezone=form.getvalue("timezone")
		currency=form.getvalue("currency")
		visibilty=form.getvalue("visibility")
		
		try: #Try to Add user in DB						
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select * from `setting_preferences` where  `userid`='{0}'".format(userid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			if totalRecords1 > 0:
				queryTerm1= "UPDATE `setting_preferences` SET  `language`='{1}',`timezone`='{2}',`currency`='{3}',`profilevisibility`='{4}' WHERE `userid`='{0}'".format(userid,language,timezone,currency,visibilty)
				curs1.execute(queryTerm1)
			else:
				
				queryTerm1 = "Insert into `setting_preferences` SET  `language`='{1}',`timezone`='{2}',`currency`='{3}',`profilevisibility`='{4}' , `userid`='{0}'".format(userid,language,timezone,currency,visibilty)
				curs1.execute(queryTerm1)
			  
			curs1.close()
			html = True 
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 


#------------ setting password----------------------------------------#

	elif "passwordupdate" in form: #handle post request for user attribute action
		htmlerror = ''
		userid = form.getvalue("passwordupdate")
		userpwd = form.getvalue("confirmpassword")
		h = hashlib.new('ripemd160')
		h.update(userpwd)
		password = h.hexdigest()

		
		try: #Try to Add user in DB						
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm= "UPDATE `users` SET  `password`='{0}' WHERE `id`='{1}'".format(password,userid)
			curs1.execute(queryTerm)
  
			curs1.close()
			html = True 
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 


		
			

	elif "followme" in form: #handle post request for following the user
		htmlerror = ''
		userid = form.getvalue("userid")
		followme = form.getvalue("followme")
		try: #Try to Add user in DB
			follower_unfollow(userid,followme)
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
	elif "likeimage" in form: #handle post request for Liking the image
		htmlerror = ''
		userid = form.getvalue("userid")
		imageid = form.getvalue("imageid")
		
		try: #Try to Add user in DB
			img_likeunlike(userid,imageid)
			
			
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
		
	#---------------------------attributelikeimage--------------------
	elif "attrlikeimage" in form: #handle post request for Liking the image
		htmlerror = ''
		userid = form.getvalue("userid1")
		imageid = form.getvalue("attrimageid")
		
		try: #Try to Add user in DB
			
			img_likeunlikeattribute(userid,imageid)
			
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 	
	
	
		
	elif "checkimageattribute" in form: #handle post request for image attribute is verfied or not
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			attributeid = form.getvalue("attributeid")
			status1 = form.getvalue("status")
			if status1 == "Yes":
				status = 1
			else:
				status = 0
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Select attributeid from `user_images_attributes_check` where  `userid`='{0}' and `attributeid`='{1}'".format(userid,attributeid)
			curs1.execute(queryTerm)
			totalRecords = curs1.fetchall()
			totalRecords1 = len(totalRecords)
			if totalRecords1 > 0:
				queryTerm1 = "Update `user_images_attributes_check` SET  `check`='{2}' where  `userid`='{0}' and `attributeid`='{1}'".format(userid,attributeid,status)
				curs1.execute(queryTerm1)
			else:
				queryTerm1 = "Insert into `user_images_attributes_check` SET  `userid`='{0}',`attributeid`='{1}',`check`='{2}'".format(userid,attributeid,status)
				curs1.execute(queryTerm1)
			curs1.close()
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
	elif "addimagecomment" in form: #handle post request for image comment
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			comment = form.getvalue("comment")
			uuid = form.getvalue("uuid")
			resetdate = datetime.datetime.now()
			status = 1
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm1 = "Insert into `image_comment` SET  `userid`='{0}',`uuid`='{1}',`comment`='{2}',`status`='1',`reportabuse`='0',`createdAt`='{3}'".format	(userid,uuid,re.escape(comment),resetdate)
			curs1.execute(queryTerm1)
			curs1.close()
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
	elif "reportcommentabuse" in form: #handle post request for report comment abuse
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			comment = form.getvalue("commentid")
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm1 = "Update `image_comment` SET  `reportabuse`='1' where `id`='{0}' ".format(comment)
			curs1.execute(queryTerm1)
			curs1.close()
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml) 
	elif "reportcommentdelete" in form: #handle post request for deleting image comment
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			comment = form.getvalue("commentid")
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm1 = "Delete from `image_comment` where `id`='{0}' ".format(comment)
			curs1.execute(queryTerm1)
			curs1.close()
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")

		if html:
			finalhtml = "1||"; 
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
	elif "shareemail" in form: #handle post request for share image via email
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			
			email1 = form.getvalue("email")
			if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email1):
				email = email1
			else:
				email = get_useremail(str(form.getvalue("email")))
			
			comment = form.getvalue("comment")
			imagelink = form.getvalue("imagelink")
			userprofile =get_userprofile(str(userid))
			fullname =userprofile[0]['fullname']
			username = userprofile[0]['username']
			if fullname is None:
				fullname =username
			finalhtml1 = '<html><body>{0} sent you a link to Luxradar: {1} <br /> <br /> {2}  <br />  <br />Thanks, <br />The Luxradar Team</body></html>'.format(fullname,imagelink,comment)
			subject  = "{0} wants to add something to your radar!".format(fullname)
			data = {'subject':(subject),"message":(finalhtml1),"recipient":(email)}
			emailtest(data) #Send email to user
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")
		if html:
			finalhtml = '1||Email has been sent to {0}.'.format(email)
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)



	elif "shareemail1" in form: #handle post request for share image via email
		htmlerror = ''
		try: #Try to Add user in DB
			userid = form.getvalue("userid1")
			if  userid=="--userid--":
				raise Exception("You need to Login.")
			email2 = form.getvalue("email1")
			if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email2):
				email = email2
			else:
				email = get_useremail(str(form.getvalue("email1")))
			
			
			comment = form.getvalue("comment1")
			imagelink = form.getvalue("imagelink1")
			userprofile =get_userprofile(str(userid))
			fullname =userprofile[0]['fullname']
			username = userprofile[0]['username']
			if fullname is None:
				fullname =username
			finalhtml1 = '<html><body>{0} sent you a link to Luxradar: {1} <br /> <br /> {2}  <br />  <br />Thanks, <br />The Luxradar Team</body></html>'.format(fullname,imagelink,comment)
			subject  = "{0} wants to add something to your radar!".format(fullname)
			data = {'subject':(subject),"message":(finalhtml1),"recipient":(email)}
			emailtest(data) #Send email to user
			html = True
		except Exception , e:
			html = False
			htmlerror = str(e).replace('"',"`")


		if html:
			finalhtml = '1||Email has been sent to {0}.'.format(email)
		else:
			finalhtml = htmlErrorHandler(htmlerror)
		output(finalhtml)
	elif "sendinvite" in form: #handle post request for sending invitation to friends
		if get_cookie("userdatasite"):
			userdata = get_loginsuer()
			userdata1 = getUserByID(userdata[2])
			totalRecords = len(userdata1)
			if totalRecords == 0:
				finalhtml = 'Invalid Login'
				output(finalhtml)
				sys.exit()
				
			useremail = form.getvalue("send_email")
			messagetxt = form.getvalue("message")
			username =  userdata1[0]['username'].encode("utf8")
			username = username.encode('base64','strict');
			resetlink = SITEURL+'invitesend.py?pid='+str(username)+'::'+str(userdata[2]) #Create Reset password link
			emailsent = update_sendinvite(useremail,userdata[2]) #update DB fields for reseting password
			emailalreadysent= ''
			emailsentto = ''
			if len(emailsent[0]) > 0:
				emailalreadysent = ",".join(emailsent[0])
			if len(emailsent[1]) > 0:
				emailsentto = ",".join(emailsent[1])
			if 	emailsentto != '':
				forgethtml = Read_File("sendinvite_email.html")
				finalhtml = forgethtml.replace('--resetlink--',resetlink).replace('--username--',userdata[0]).replace('--messagetxt--',messagetxt)
				data = {'subject':" you to luxradar.com","message":finalhtml,"recipient":useremail}
				email(data) #Send Email
			if emailalreadysent != '':
				finalhtml = '1||Invitation sent to {0}. Already Sent to {1}'.format(emailsentto,emailalreadysent)
			else:
				finalhtml = '1||Invitation sent to {0}.'.format(emailsentto)
			output(finalhtml)
		else:
			finalhtml = 'Invalid Login'
		output(finalhtml)
	else:
		output("Invalid parameters")
		
