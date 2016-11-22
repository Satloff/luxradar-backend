#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *

# MAIN
#
# Display User  Setting page. 
#

form = cgi.FieldStorage() #Fetch the form data if any by get or post
if get_cookie("userdatasite"): #Check user logined or not 
	html = ''
	headerhtml  = headerReturn() #call header function
	topFile = headerhtml[0] #header html
	bottomFile= headerhtml[1] #Footer html
	userdata = headerhtml[2] #User cookie data html
	userdata1 = headerhtml[3] #User full data html
	finalhtml = userdata1
	html = html + topFile.replace("--serachType--",'').replace("--STATICURL--",STATICURL).replace("--SITEURL--",SITEURL).replace("--imagename--",'').replace("--imageid--",'')
	bottomFile = bottomFile.replace("--imageid--",'')
	if len(finalhtml) > 0:
		#finalhtml1 = Read_File("usersetting.html") #Read template file
		finalhtml1 = Read_File("settings-profile.html") #Read template file
		finalhtmljs =Read_File("usersettingjs.html") #Read template js file
		useremail = ''
		if userdata1[0]['usertype'] not in ['FB','twitter']:
			useremail = str(userdata1[0]['useremail'])
	DOB = ''
	genderhtml = ''
	#assign parameters to html
	finalhtml1 = finalhtml1.replace("--fullname--",str(userdata1[0]['fullname'])).replace("--username--",str(userdata1[0]['username'])).replace("--useremail--",useremail).replace("--userid--",str(userdata[2])).replace("--SITEURL--",SITEURL).replace("--STATICURL--",STATICURL)
	userprofile = get_userprofile(str(userdata[2])) #get user profile Data #uid
	totalRecords = len(userprofile)
	if totalRecords != 0: #user profile exits
		website = CheckNone(userprofile[0]['website'])
		location = CheckNone(userprofile[0]['location'])
		about = CheckNone(userprofile[0]['about'])
		birthdate = CheckNone(userprofile[0]['birthdate'])
		gender = CheckNone(userprofile[0]['gender'])
		twitter = CheckNone(userprofile[0]['twitter'])
		facebook = CheckNone(userprofile[0]['facebook'])
		instagram = CheckNone(userprofile[0]['instagram'])
		google = CheckNone(userprofile[0]['google'])
		#user Profile pic Default if not exists
		if userprofile[0]['profilepic'] is None or userprofile[0]['profilepic'] == '':
			profilepic = 'defualtprofile.jpg'
		else:
			profilepic = userprofile[0]['profilepic']
		genderhtml = 'jQ(\'input[value="'+gender+'"]\').attr("checked", true);'
		DOB = birthdate
		profilephoto = SITEURL+'images/userimages/'+profilepic
		#assign All variable to template file
		finalhtml1 = finalhtml1.replace("--website--",website).replace("--location--",location).replace("--about--",about).replace("--birthdate--",birthdate).replace("--gender--",gender).replace("--twitter--",twitter).replace("--facebook--",facebook).replace("--instagram--",instagram).replace("--google--",google).replace("--profilephoto--",profilephoto).replace("--useremail--",useremail)
	else:
		#assign All variable to template file
		profilephoto = SITEURL+'images/userimages/defualtprofile.jpg'
		finalhtml1 = finalhtml1.replace("--website--",'').replace("--location--",'').replace("--about--",'').replace("--birthdate--",'').replace("--gender--",'').replace("--twitter--",'').replace("--facebook--",'').replace("--instagram--",'').replace("--google--",'').replace("--profilephoto--",profilephoto).replace("--useremail--",useremail)		
	html = html.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1.replace("--DOB--",DOB).replace("--gender--",genderhtml) + bottomFile.replace("</body>",'').replace("</html>",'') +str(finalhtmljs).replace("--DOB--",DOB).replace("--gender--",genderhtml)
	html = encodeCharAt(html) #encode special characters
	output(html)  #Display output Html

else:
	finalhtml = '<script> window.location = "'+SITEURL+'sign-in.py";</script>'
	output(finalhtml) #Display output Html

