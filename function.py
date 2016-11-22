#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from decimal import *
import logging
import PIL
from PIL import Image
from datetime import datetime
import re
import cStringIO
#
# Authenticate user and create login session for it.
# parameter : mypostlist => List of Post parameters
#
def authenticate(mypostlist):
	h = hashlib.new('ripemd160')
	h.update(mypostlist.getvalue('password'))
	userpwd = h.hexdigest()
	if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", str(mypostlist.getvalue('useremail'))):
		queryTerm = "SELECT id,role,username,useremail,fullname FROM `users` WHERE `useremail`='{0}' and `password`='{1}' and status=1".format(mypostlist.getvalue('useremail'),userpwd)
	else:
		queryTerm = "SELECT id,role,username,useremail,fullname FROM `users` WHERE `username`='{0}' and `password`='{1}' and status=1".format(mypostlist.getvalue('useremail'),userpwd)
	
	curs.execute(queryTerm)
	totalRecords = curs.fetchall()
	totalRecords1 = len(totalRecords)
	if totalRecords1 > 0:
		msg =  create_cookie('userdatasite',(totalRecords[0]['username'])+'::'+str(totalRecords[0]['role'])+'::'+str(totalRecords[0]['id'])+'::'+(totalRecords[0]['useremail']))
		return  msg  # generate HTTP headers
	else:
		return ""

#
# Function to Return Cookie data. 
# parameter : cookiename => Name of cookie
#
def get_cookie(cookiename):
	if 'HTTP_COOKIE' in os.environ:
		cookie_string=os.environ.get('HTTP_COOKIE')
		c=Cookie.SimpleCookie()
		c.load(cookie_string)
		try:
		    data=c[cookiename].value
		    return data
		except KeyError:
		    return False
	return False
	
#
# Check if user logined or not.
#
def get_loginsuer():
	if get_cookie("userdatasite"):
		userdata = get_cookie("userdatasite").split('::')
		return userdata
	else:
		finalhtml = '<html><body><script>window.location="'+SITEURL+'/sign-in.py";</script></body></html>';
		output(finalhtml)
		sys.exit();
		

#
# Make http request to url with parameters
# parameter : url => Url on which data to post via POST method, param => Parameters to send
#
def postData(url,param):
	http=urllib3.PoolManager()
	r = http.request('POST',url,param)
	return r.data

#
# Make http request to url with parameters
# parameter : url => Url on which data to post via GET method, param => Parameters to send
#
def headData(url,param):
	http=urllib3.PoolManager()
	r = http.request('GET',url,param)
	return r.data

#
# Create a headers to create cookie
# parameter : cookiename => Name of cookie, value => Value of cookie.
#
def create_cookie(cookiename,value):
	C = Cookie.SimpleCookie()
	C[cookiename] = value
	C[cookiename]["path"] = "/"
	C[cookiename]['expires']=1*1*24*60*60
	return  C

#
# Create a headers to Delete cookie
# parameter : cookiename => Name of cookie
#
def delete_cookie(cookiename):
	C = Cookie.SimpleCookie()
	C[cookiename] = ''
	C[cookiename]["path"] = "/"
	C[cookiename]['expires']='Thu, 01 Jan 1970 00:00:00 GMT'
	return  C
#
# Check if user exists for forgot password request
#
def forget_password(useremail):
	queryTerm = "SELECT id FROM `users` WHERE `useremail`='{0}' and status=1".format(useremail)
	curs.execute(queryTerm)
	if curs.fetchall():
		return True  # generate HTTP headers
	else:
		return False
#
#Update table to know user request for forgot password
#
def update_forget_password(useremail,uid):
	queryTerm = "UPDATE `users` SET resetpassword='{0}',resetdate=CURDATE() WHERE `useremail`='{1}'".format(uid,useremail)
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False

#
#Check if user request for reset password
#
def reset_password(pid):
	queryTerm = "SELECT id FROM `users` WHERE `resetpassword`='{0}' and CURDATE() <= DATE_ADD(resetdate,INTERVAL 1 DAY)".format(pid)
	curs.execute(queryTerm)
	if curs.fetchall():
		return True  # generate HTTP headers
	else:
		return False

#
#Update user password
#
def update_password(pwd,pid):
	h = hashlib.new('ripemd160')
	h.update(pwd)
	userpwd = h.hexdigest()
	queryTerm = "UPDATE `users` SET password='{0}',resetpassword='Updated',resetdate='1970-1-1' WHERE `resetpassword`='{1}'".format(userpwd,pid)
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False

#
#Insert user through email
#
def register_user(form,uid):
	h = hashlib.new('ripemd160')
	h.update(form.getvalue("password"))
	userpwd = h.hexdigest()
	firstname=str(form.getvalue("firstname"))
	lastname=str(form.getvalue("lastname"))
	fullname= firstname + " " +lastname
	
	queryTerm = "Insert into `users` SET password='{0}',useremail='{1}',username='{2}',resetpassword='{3}',role=0,status=1,resetdate='1970-1-1',fullname='{4}' ,usertype='email',`createdAt` = NOW(),updatedAt= NOW() ".format(userpwd,form.getvalue("email"),form.getvalue("username"),uid,fullname)
	curs.execute(queryTerm)
	#~ queryTerm1 = "Insert into `setting_preferences` SET userid= '{0}',language='hi' ,timezone=1 ,currency='USD' ,profilevisibility='everyone',updatedAt= '0000-00-00 00:00:00' ".format(curs.lastrowid)
	#~ curs.execute(queryTerm1)
	if  curs.lastrowid:
		return True  # generate HTTP headers
	else:
		return False

#
#Insert user via facebook
#
def register_user_fb(form,uid):
	queryTerm = "SELECT id,role,username,useremail,fullname FROM `users` WHERE `userid` = '"+form.getvalue("username")+"'"
	curs.execute(queryTerm)
	data1 = curs.fetchall()
	if len(data1) > 0:
		msg =  create_cookie('userdatasite',str(data1[0]['fullname'])+'::'+str(data1[0]['role'])+'::'+str(data1[0]['id'])+'::'+str(data1[0]['useremail']))
		return  msg  # generate HTTP headers
	else:	
		h = hashlib.new('ripemd160')
		h.update(form.getvalue("username"))
		userpwd = h.hexdigest()
		queryTerm = "Insert into `users` SET password='{0}',useremail='{1}' ,username='{2}',resetpassword='Updated' ,role=0,status=1,resetdate='1970-1-1', fullname='{3}', userid='{4}',usertype='FB',`createdAt` = NOW() ".format(userpwd,form.getvalue("username"),form.getvalue("username"),form.getvalue("fullname"),form.getvalue("username"))
		curs.execute(queryTerm)
		queryTerm1 = "Insert into `setting_preferences` SET userid= '{0}',language='hi' ,timezone=1 ,currency='USD' ,profilevisibility='everyone',updatedAt= '0000-00-00 00:00:00' ".format(curs.lastrowid)
		curs.execute(queryTerm1)
	if  curs.lastrowid:
		msg =  create_cookie('userdatasite',str(form.getvalue("fullname"))+'::'+str(0)+'::'+str(curs.lastrowid)+'::'+str(form.getvalue("username")))
		return  msg  # generate HTTP headers
	else:
		return False

#
#Insert user via twitter
#
def register_user_twitter(finalhtml,name):
	#finalhtml = get_cookie('twitter_final_step')
	queryTerm = "SELECT id,role,username,useremail,fullname FROM `users` WHERE `userid` = '"+finalhtml['user_id']+"'"
	curs.execute(queryTerm)
	data1 = curs.fetchall()
	if len(data1) > 0:
		msg =  create_cookie('userdatasite',str(data1[0]['fullname'])+'::'+str(data1[0]['role'])+'::'+str(data1[0]['id'])+'::'+str(data1[0]['useremail']))
		return  msg  # generate HTTP headers
	else:	
		h = hashlib.new('ripemd160')
		h.update(finalhtml["user_id"])
		userpwd = h.hexdigest()
		queryTerm = "Insert into `users` SET password='{0}',useremail='{1}' ,username='{2}',resetpassword='Updated' ,role=0,status=1,resetdate='1970-1-1', fullname='{3}', userid='{4}',usertype='twitter',`createdAt` = NOW() ".format(userpwd,finalhtml["screen_name"],finalhtml["user_id"],name,finalhtml["user_id"])
		curs.execute(queryTerm)
		queryTerm1 = "Insert into `setting_preferences` SET userid= '{0}',language='hi' ,timezone=1 ,currency='USD' ,profilevisibility='everyone',updatedAt= '0000-00-00 00:00:00' ".format(curs.lastrowid)
		curs.execute(queryTerm1)
	if  curs.lastrowid:
		msg =  create_cookie('userdatasite',str(name)+'::'+str(0)+'::'+str(curs.lastrowid)+'::'+str(finalhtml["user_id"]))
		return  msg  # generate HTTP headers
	else:
		return False		

#
#Insert user via google
#
def register_user_google(form,uid):
	queryTerm = "SELECT id,role,username,useremail,fullname FROM `users` WHERE `userid` = '"+form.getvalue("username")+"'"
	curs.execute(queryTerm)
	data1 = curs.fetchall()
	if len(data1) > 0:
		msg =  create_cookie('userdatasite',str(data1[0]['fullname'])+'::'+str(data1[0]['role'])+'::'+str(data1[0]['id'])+'::'+str(data1[0]['useremail']))
		return  msg  # generate HTTP headers
	else:	
		h = hashlib.new('ripemd160')
		h.update(form.getvalue("username"))
		userpwd = h.hexdigest()
		queryTerm = "Insert into `users` SET password='{0}',useremail='{1}' ,username='{2}',resetpassword='Updated' ,role=0,status=1,resetdate='1970-1-1', fullname='{3}', userid='{4}',usertype='google' ,`createdAt` = NOW() ".format(userpwd,form.getvalue("useremail"),form.getvalue("username"),form.getvalue("fullname"),form.getvalue("username"))
		curs.execute(queryTerm)
		queryTerm1 = "Insert into `setting_preferences` SET userid= '{0}',language='hi' ,timezone=1 ,currency='USD' ,profilevisibility='everyone',updatedAt= '0000-00-00 00:00:00' ".format(curs.lastrowid)
		curs.execute(queryTerm1)
	if  curs.lastrowid:
		msg =  create_cookie('userdatasite',str(form.getvalue("fullname"))+'::'+str(0)+'::'+str(curs.lastrowid)+'::'+str(form.getvalue("username")))
		return  msg  # generate HTTP headers
	else:
		return False

#
#Activate user by confirmation link sent on signup
#
def activate_user(uid):
	queryTerm = "UPDATE `users` SET status=1,resetpassword='Updated',resetdate='1970-1-1'  WHERE `resetpassword`='{0}'".format(uid)
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False
#
#Update user Details
#
def update_user(formdata,uid):
	queryTerm = "UPDATE `users` SET username='{0}',useremail='{1}',password='{2}' ,fullname='{4}' WHERE `id`='{3}'".format(formdata['username'],formdata['useremail'],formdata['password'],uid,formdata['fullname'])
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False

#
#Update user profile Details
#
def update_userprofile(formdata1,uid,profilepic):
	formdata = {}
	fieldsarr = ['website' ,'location' ,'about'  ,'birthdate' ,'gender', 'twitter' ,'facebook' ,'instagram' , 'google']
	for fieldsarr1 in fieldsarr:
		if formdata1.getvalue(fieldsarr1) is None: 
			formdata[fieldsarr1]=''
		else:
			formdata[fieldsarr1]=formdata1.getvalue(fieldsarr1)
		
	userprofile = get_userprofile(uid)
	totalRecords = len(userprofile)
	if userprofile[0]['userida'] is None:
		queryTerm = "Insert into `user_profile` SET  `website`='{0}',`location`='{1}',`about`='{2}' ,`birthdate`='{3}',`gender`='{4}',`twitter`='{5}',`facebook`='{6}', `instagram`='{7}', `google`='{8}' ,`userid`='{9}',`profilepic`='{10}'".format(formdata['website'],formdata['location'],formdata['about'],formdata['birthdate'],formdata['gender'],formdata['twitter'],formdata['facebook'],formdata['instagram'],formdata['google'],uid,profilepic)
	else:
		if profilepic == '':
			profilepic = userprofile[0]['profilepic']
		queryTerm = "UPDATE `user_profile` SET  `website`='{0}',`location`='{1}',`about`='{2}' , `birthdate`='{3}', `gender`='{4}',`twitter`='{5}', `facebook`='{6}', `instagram`='{7}', `google`='{8}', `profilepic`='{10}' WHERE `userid`='{9}'".format(formdata['website'],formdata['location'],formdata['about'],formdata['birthdate'],formdata['gender'],formdata['twitter'],formdata['facebook'],formdata['instagram'],formdata['google'],uid,profilepic)
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False	

#
#Delete user profile pic
#
def deleteuserpic(uid):
	userprofile = get_userprofile(uid)
	totalRecords = len(userprofile)
	if totalRecords > 0:
		if userprofile[0]['profilepic'] is not None:
			queryTerm = "UPDATE `user_profile` SET  `profilepic`='' WHERE `userid`='{0}'".format(uid)
			curs.execute(queryTerm)
			file_path = IMAGEFOLDER +"userimages/"+userprofile[0]['profilepic']
			os.unlink(file_path)
			return True
	return False

#
#Return user profile data by userid
#	
def get_userprofile(uid):
 	global debughtml
	queryTerm = 'SELECT a.`userid` as userida , a.`website`, a.`location`, a.`about`, a.`birthdate`, a.`gender`, a.`twitter`, a.`facebook`, a.`instagram`, a.`google`, a.`profilepic`, a.`featuredimg`,b.`useremail`, b.`role`, b.`username`, b.`password`, b.`status`, b.`resetpassword`, b.`resetdate`, b.`fullname`, b.`userid`, b.`usertype`, b.`createdAt`, b.`updatedAt`FROM  `users` b  LEFT JOIN  `user_profile` a  on `a`.`userid`   = `b`.`id`  WHERE `b`.`id` = '+str(uid)+' '
	curs.execute(queryTerm)
	if debug: debugtml = debughtml + "[get_userprofile] searched query term: "+queryTerm+"<br>"
	return curs.fetchall()

#
#Update user username and and status
#
def update_user_username(formdata,uid):
	queryTerm = "UPDATE `users` SET username='{0}',status=1 WHERE `id`='{1}'".format(formdata.getvalue("username"),uid)
	curs.execute(queryTerm)
	if curs.rowcount > 0:
		return True
	else:
		return False
		
#
# Search database for the record at the index value specified
#
def getImageInfoFromIndex(indexValue, curs):
	global debughtml
	queryTerm = 'SELECT * FROM `filenames` WHERE status=1 and `index` = '+str(indexValue)+' '
	curs.execute(queryTerm)
	if debug: debugtml = debughtml + "[getImageInfoFromIndex] searched query term: "+queryTerm+"<br>"
	return curs.fetchone()

#
# Search database for the record at the UUID value specified with status is active
#
def getImageInfoFromUUID(uuid, curs):
	global debughtml
	queryTerm = 'SELECT * FROM `filenames` WHERE status=1 and `uuid` = "'+uuid+'"'
	curs.execute(queryTerm)
	if debug: debughtml = debughtml + "[getImageInfoFromUUID] searched query term: "+queryTerm+"<br>"
	return curs.fetchone()

#
# Search database for the record at the UUID value specified
#
def getImageInfoFromUUIDAll(uuid, curs):
	global debughtml
	curs1 = conn.cursor(oursql.DictCursor)
	queryTerm = "SELECT * FROM `filenames` WHERE `uuid` = '"+uuid+"'"
	curs1.execute(queryTerm)
	recored = curs1.fetchone()
	curs1.close()
	if debug: debughtml = debughtml + "[getImageInfoFromUUID] searched query term: "+queryTerm+"<br>"
	return recored

#
# Process the passed dict item to unpack the name of the image and the uuid
#
def getImageUUID(dict):
	global debughtml
	type = dict['original_image_title']
	finaltype1 = type.split('.')
	type1 = '.'+finaltype1[-1] 
	feature = dict['original_image_URL']
#	feature = feature.strip(' Photograph')
	uuid = dict['uuid']
	if debug: debughtml = debughtml + "[getImageUUID] got record: "+str(feature)+str(uuid)+str(type)+"<br>"
	return [feature,uuid,type1]


#
# Search database for the list of attributes associated with the passed uuid
#	
def getImageAttributes(uuid, curs):
	global debughtml
	queryTerm = 'SELECT * FROM `image_attributes` WHERE `uuid` = "'+uuid+'" and `status`=1'
	curs.execute(queryTerm)
	if debug: debughtml = debughtml + "[getImageAttributes] got attributes for: "+str(uuid)+str(queryTerm)+"<br>"
	return curs.fetchall()

#
# Search database for the list of attributes associated with the passed uuid unapprove attirbutes
#	
def getImageAttributesnoapprove(uuid, curs):
	global debughtml
	queryTerm = 'SELECT * FROM `image_attributes` WHERE `uuid` = "'+uuid+'" and `status`=0'
	curs.execute(queryTerm)
	if debug: debughtml = debughtml + "[getImageAttributesnoapprove] got attributes for: "+str(uuid)+str(queryTerm)+"<br>"
	return curs.fetchall()
	
#
# Search database for the list of attributes associated with the passed search terms
#	
def getImageUUIDList(type,name, curs):
	global debughtml
	attribute_AND =  ''
	attribute_type = ''
	attribute_name = ''
	attribute_status = 'r1.status=1 and'
	if type == '%' or type == '' or type is None:
		attribute_type = ''
	else:
		type = type.replace('-s-','(').replace('-ss-',')').replace('-sss-',"'")
		attribute_type = 'r1.`attribute_type` = "'+type+'"'
	if name == '%' or name == '' or name is None:
		attribute_name = ''
	else:
		name = name.replace('-s-','(').replace('-ss-',')').replace('-sss-',"'")
		attribute_name = 'r1.`attribute_name` = "'+name+'"'

	if attribute_name != '' and attribute_type != '':
		attribute_AND = 'AND'

	if attribute_name == '' and attribute_type == '':
		attribute_status = 'r1.status=1'
	
	if 	attribute_name == '' :
		queryTerm = 'SELECT r1.* FROM `image_attributes` AS r1 JOIN   (SELECT (RAND() * (SELECT MAX(`index`) FROM `image_attributes`)) AS `index`)  AS r2 INNER JOIN `filenames` as r3  WHERE r1.`uuid` = r3.`uuid` and r3.`status` = 1  and r1.`index` >= r2.`index` and {0} {1} {2} {3} ORDER BY r1.`index` ASC  LIMIT 1'.format(attribute_status,attribute_type,attribute_AND,attribute_name)
	else:
		queryTerm = 'SELECT r1.* FROM `image_attributes` AS r1 INNER JOIN `filenames` as r3  WHERE r1.`uuid` = r3.`uuid` and r3.`status` = 1  and {0} {1} {2} {3} '.format(attribute_status,attribute_type,attribute_AND,attribute_name)
	#output(queryTerm)
	#sys.exit()
	curs.execute(queryTerm)
	if debug: debughtml = debughtml + "[getImageUUIDList] searched query term: "+queryTerm+"<br>"
	return curs.fetchall()


#
# Search database for the list of attributes associated with the passed uuid where status is active
#	
def getImageAttributesAll():
	global debughtml
	queryTerm = 'SELECT attribute_type FROM `image_attributes` WHERE status=1 GROUP BY `attribute_type` ORDER BY `attribute_type`'
	curs.execute(queryTerm)
	if debug: debughtml = debughtml + "[getImageAttributesAll] got attributes for: "+queryTerm+"<br>"
	return curs.fetchall()


#
# Encode spcial characters
#
def encodeCharAt(char):
	try:
		name = char.encode("utf-8").strip()
	except Exception:
		name = char.decode("utf-8").encode("utf-8").strip()
	return name

#
# Process the passed dict item to unpack the name and type of each attribute
#	
def unpackImageAttributes(dict):
	global debughtml
	list = []
	i = 0
	for i in range (len(dict)):
		name = (dict[i]['attribute_name'])
		type1 = (dict[i]['attribute_type'])
		index = (dict[i]['index'])
		i = i + 1
		list.append([name, type1,index])
	if debug: debughtml = debughtml + "[unpackImageAttributes] got: "+str(list)+"<br>"
	return list

#
# Create the directory information for the image read
#
def getImageLocation(uuid):
	try:
		
		dir = IMAGEURL+"images/"
		first = uuid[0]+"/"
		second = uuid[1]+"/"	
		third = uuid[2]+"/"
		return str(dir+first+second+third+uuid)
	except Exception as e:
		return 'not found'
#
# Create the relative directory information for the image read
#
def getImageLocationpath(uuid):
	try:
		
		dir = "images/"
		first = uuid[0]+"/"
		second = uuid[1]+"/"	
		third = uuid[2]+"/"
		return str(dir+first+second+third+uuid)
	except ValueError:
		print "Oops!  That was no valid number.  Try again..."
# Parse Attribute list of image to Html
#		
def printAttributesList(list):
	i = 0
	attribute = ''
	for i in range (len(list)):
		name = (list[i][0])
		type = (list[i][1])
		i = i + 1
		attribute = attribute + '<span>'+type+': '+'<a style="cursor:pointer;" onclick="submitSearch(\''+type.replace("'","-sss-")+'\',\''+name.replace("'","-sss-")+'\');">'+name+'</a></span><br>'
	return attribute

#
# Parse Attribute (not approved) list of image to Html
#
def printAttributesList1(list):
	i = 0
	attribute = '<h4>Waiting For Admin Approval.</h4><ul>'
	for i in range (len(list)):
		name = (list[i][0])
		type = (list[i][1])
		i = i + 1
		attribute = attribute + '<li><span>'+type+': '+''+name+'</span></li>'
	return attribute+'</ul>'

#
#Fetch user by ID
#	
def getUserByID(uid):
	queryTerm = "SELECT id,username,useremail,status,password,fullname,userid,usertype,createdAt,updatedAt FROM `users` WHERE id={0}".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	return totalRecords1
	
#
#Fetch user by Username
#	

def getUserByUsername(uid):
	queryTerm = "SELECT id,username,useremail,status,fullname,userid,usertype,createdAt,updatedAt FROM `users` WHERE username='{0}' and role <> '1' and status=1".format(uid)
	curs.execute(queryTerm)
	return curs.fetchall()

#
#Resize the image
#	
	
def image_resize(imagepath, dimensions, rotate=None): 

	""" Resizes an image to be as close as possible to specified dimensions. Image is a django image-model-field.
		Will both scale up and down the image to meet this while keeping the proportions
		in width and height
	"""

	if imagepath and os.path.isfile(imagepath):

		im = Image.open(imagepath)
		logging.debug ('resizing image from %s x %s --> %s x %s ' % (im.size[0], im.size[1], dimensions[0], dimensions[1]))

		if rotate:
		    logging.debug('first rotating image %s' % rotate)
		    im = im.rotate(90)

		srcWidth = Decimal(im.size[0])
		srcHeight = Decimal(im.size[1])

		resizeWidth = srcWidth
		resizeHeight = srcHeight

		aspect = resizeWidth / resizeHeight # Decimal

		logging.debug('resize aspect is %s' % aspect)

		if resizeWidth > dimensions[0] or resizeHeight > dimensions[1]:
		    # if width or height is bigger we need to shrink things
		    if resizeWidth > dimensions[0]:
		        resizeWidth = Decimal(dimensions[0])
		        resizeHeight = resizeWidth / aspect

		    if resizeHeight > dimensions[1] :
		        aspect = resizeWidth / resizeHeight
		        resizeHeight = Decimal(dimensions[1])
		        resizeWidth = resizeHeight * aspect

		'''else:
		    # if both width and height are smaller we need to increase size
		    if resizeWidth < dimensions[0]:
		        resizeWidth = Decimal(dimensions[0])
		        resizeHeight = resizeWidth / aspect

		    if resizeHeight > dimensions[1] :
		        aspect = resizeWidth / resizeHeight
		        resizeHeight = Decimal(dimensions[1])
		        resizeWidth = resizeHeight * aspect'''

		im = im.resize((resizeWidth, resizeHeight), Image.ANTIALIAS)

		logging.debug('resized image to %s %s' % im.size)
		im.save(imagepath)

	else:
		# no action, due to no image or no image in path
		pass

	return imagepath

#
#Return Html of user notifications
#	

def usernotification():
	html = '''
					<div  class="drop-block">
						<a href="#" class="opener">
							<span class="text">Notifications</span>
							<span class="quantity">3</span>
						</a>
						<div class="drop">
							<div class="drop-holder">
								<div class="drop-frame">
									<div class="heading">
										<h2>notifications</h2>
									</div>
									<ul class="list-notifications">
										<li>
											<div class="item">
												<div class="item-frame">
													<a href="#" class="img-holder">
														<img src="--STATICURL--images/img29.jpg" height="25" width="25" alt="Image description">
													</a>
													<a href="#" class="img-right">
														<img src="--STATICURL--images/img27.jpg" height="42" width="42" alt="Image description">
													</a>
												</div>
												<div class="item-holder">
													<a href="#">Joe Lawson </a>liked <a href="#">your photo</a>
												</div>
											</div>
										</li>
										<li>
											<div class="item">
												<div class="item-frame">
													<a href="#" class="img-holder">
														<img src="--STATICURL--images/img30.jpg" height="25" width="25" alt="Image description">
													</a>
												</div>
												<div class="item-holder">
													<a href="#">Frances Jordan </a>followed you
												</div>
											</div>
										</li>
										<li>
											<div class="item">
												<div class="item-frame">
													<a href="#" class="img-holder">
														<img src="--STATICURL--images/img23.png" height="25" width="25" alt="Image description">
													</a>
													<a href="#" class="img-right">
														<img src="--STATICURL--images/img31.jpg" height="42" width="42" alt="Image description">
													</a>
												</div>
												<div class="item-holder">
													<a href="#">Paul Rice </a>liked <a href="#">Fujifilm X100S</a>
												</div>
											</div>
										</li>
									</ul>
								</div>
							</div>
						</div>
					</div>
				'''
	return html

#
#Return Html Header/footer and other user data for templates
#	
def headerReturn(showaddattribute=0):
	addattribute = ''
	if showaddattribute != 0:
		addattribute = '<li><a href="javascript:;" data-toggle="modal" data-target="#addModal1" >Add Attribute</a></li><li class="divider"></li>'

	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userdata1 = getUserByID(userdata[2])
		fullname1 = userdata1[0]['fullname'].capitalize()
		fullname = re.sub(" ", ",", str(fullname1))
		fname = fullname.split(",");
		lengthoffname = len(fname)
		if lengthoffname > 2:
			firstname = fname[0]+" "+fname[1].capitalize()
		else:
			firstname = fname[0]
		firstnamelen= len(firstname)
		if firstnamelen > 7:
			dots = firstname[0:6]+"..."
		else:
			dots= firstname	
		#~ dots = showCharacterLimit(str(firstname),7,'...')
		totalRecords = len(userdata1)
		if totalRecords == 0:
			finalhtml = '<script> window.location = "'+SITEURL+'logout.py";</script>'
			output(finalhtml)
			sys.exit()
		topFile    = Read_File("header.html")
		lowFile  =  Read_File("showimage.html")
		loginjs = Read_File("loginuserjs.html").replace('--status--',str(userdata1[0]['status']))
		bottomFile = Read_File("footer.html").replace('--loginjs--',loginjs)
		loginFile = Read_File("loginuser.html")
		userprofile =get_userprofile(str(userdata[2]))
		
		if userprofile[0]['profilepic'] is None or userprofile[0]['profilepic'] == '':
			profilepic = 'defualtprofile.jpg'
		else:
			profilepic = userprofile[0]['profilepic']
		profilephoto = SITEURL+'images/userimages/'+profilepic
		myaccountHtml ='<div class="drop-block">  <a href="'+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'" class="img-holder">	<img src= "--profilePicSrc--" height="220" width="220" alt="Image description"> </a> <a class="opener" href='+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'>'+dots+'<i class="icon-arrow-bottom"></i>	</a> <div class="drop"> <div class="drop-holder">	<div class="drop-frame"> <ul> <li> <a href="'+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'">My Account</a></li>	<li><a href="'+SITEURL+'setting.py">Settings</a></li> <li><a href="#">Invite a friend</a></li> <li><a  href="'+SITEURL+'logout.py">Sign Out</a></li> </ul> </div>	</div> </div> </div> '
		#~ myaccountHtml ='<div class="drop-block">  <a href="" class="img-holder">	<img src= "--profilePicSrc--" height="220" width="220" alt="Image description"> </a> <a href="#" class="opener"><span class="text"> <a href="'+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'">'+userdata[0]+'	</span> <i class="icon-arrow-bottom"></i> </a> <div class="drop"> <div class="drop-holder">	<div class="drop-frame"> <ul> <li> <a href="#">My Account</a></li>	<li><a href="'+SITEURL+'setting.py">Settings</a></li> <li><a href="#">Invite a friend</a></li> <li><a  href="'+SITEURL+'logout.py">Sign Out</a></li> <li><a href="#myModal1" class="lightbox">Login</a></li> </ul> </div>	</div> </div> </div> '
										
		#~ myaccountHtml='<a data-toggle="dropdown" class="dropdown-toggle" href="javascript:;">Profile<i class="icon-angle-down"></i></a><ul class="dropdown-menu"><div class="aro aro2"></div><li><a href="'+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'">'+userdata[0]+'</a></li><li><a href="'+SITEURL+'setting.py">Settings</a></li><div style="border-bottom:1px lightgray solid;"></div><li><a data-target="#myModalSendinvite" id="myModalSendinvitebtn" data-toggle="modal" href="javascript:;">Invite-Friend</a></li><li><a  href="'+SITEURL+'logout.py">Sign Out</a></li></ul>'

		usernotificationhtml = usernotification().replace('--STATICURL--',STATICURL)
		#<div class="btn-group" style="padding-left: 5px;">  <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown"> Hi,'+userdata[0]+' <span class="caret"></span>  </button>  <ul class="dropdown-menu" role="menu"><li><a href="'+SITEURL+urllib.quote(userdata1[0]['username'].encode("utf8"))+'">Profile</a></li><li class="divider"></li><li><a href="'+SITEURL+'setting.py">My account</a></li><li class="divider"></li><li><a href="'+SITEURL+'recently.py" >Recent Log</a></li><li class="divider"></li><li><a data-target="#myModalSendinvite" id="myModalSendinvitebtn" data-toggle="modal" href="javascript:;" >Send Invites</a></li><li class="divider"></li><li><a href="'+SITEURL+'logout.py" >Logout</a></li></ul></div>'
		
		addbutton = '<a href="#popup2" class="btn lightbox">add</a>'
		addbuttonlist = '<li><a href="#popup2" class="lightbox"><span class="ico icon-ico-1"></span>Upload image</a></li><li><a href="#popup4" class="lightbox"><span class="ico icon-plus-circle"></span>Add attribute</a></li>'
		imagessrc = '<div id="dragandrophandler">Drag & Drop Files Here</div><p class="msg">ds</p><br><br><div id="status1"></div>'
		
		#~ loginhtml ='<div class="btn-group">  <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown"> Add <span class="caret"></span>  </button>  <ul class="dropdown-menu" role="menu">'+addattribute+'<li><a href="'+SITEURL+'addimage.py" >Add image</a></li></ul></div>'
		loginhtml ='<div class="btn-group">  <li><a href="'+SITEURL+'addimage.py" >Add image</a></li></ul></div>'
		category = processCategoryHtml1()
		
		topFile = topFile.replace("--loginhtml--",loginFile).replace('--addbuttonlist--',addbuttonlist).replace('--addimage--',loginhtml).replace('--loginbutton--','').replace('--username--',userdata[0]).replace('--userid--',userdata[2]).replace('--useremail--',userdata[3]).replace('--myaccount--',myaccountHtml).replace('--usernotification--',usernotificationhtml).replace('--addbutton--',addbutton).replace('--categoryhtml--',category).replace('--registerbutton--','').replace('--profilePicSrc--',profilephoto).replace('--imagetitle--','').replace('--error--','').replace("--category--",category).replace("--serachType--",'').replace("--SITEURL--",SITEURL).replace("--imagename--",'').replace("--attributesList1--",'').replace("--search-type--",'').replace("--search-name--",'').replace('--imagessrc--',imagessrc)
		return [topFile,bottomFile,userdata,userdata1,]
	else:
		#~ finalhtml = '<script> window.location = "'+SITEURL+'sign-in.py";</script>'
		#~ output(finalhtml)
		#~ sys.exit()
		topFile    = Read_File("header.html")
		lowFile  =  Read_File("showimage.html")
		loginjs = Read_File("loginjs.html")
		bottomFile = Read_File("footer.html").replace('--loginjs--',loginjs)
		loginFile = Read_File("login.html")
		signinFile = Read_File("sign-in.html").replace("--SITEURL--",SITEURL)
		category = processCategoryHtml()
		addbuttonlist = '<li><a href="#myModal1" class="lightbox"><span class="ico icon-ico-1"></span>Upload image</a></li><li><a href="#myModal1" class="lightbox"><span class="ico icon-plus-circle"></span>Add attribute</a></li>'

		topFile = topFile.replace("--loginhtml--",loginFile).replace('--addbuttonlist--',addbuttonlist).replace('--loginbutton--','<a href="#myModal1" class="lightbox btn">Login</a>').replace('--registerbutton--','<a href="javascript:void(0);" title="register"><i class="icon-user"></i>Register</a>').replace('--myaccount--','').replace('--usernotification--','').replace('--addbutton--','').replace('--categoryhtml--',category).replace('--profilePicSrc--','')
		
		return [topFile,bottomFile,lowFile,signinFile]

#
#Handle the errors 
#
def htmlErrorHandler(htmlerror):
	if 'Duplicate entry' in htmlerror:
		htmlerror1 = htmlerror.split(',')
		htmlerror2 = htmlerror1[1].replace('Duplicate entry','').replace('"','').replace("'",'').replace("`",'').replace('for key','already exit for').split('_')
		htmlerror = str(htmlerror2[0])+'.'
	return htmlerror

#
# Check whether user is follwing or not 
# parameter uid => userid and fid => followerid
#
def isFollowing(uid,fid):
	queryTerm = "Select id from `user_followers` where `userid`='{0}' and `followerid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return True
	else:
		return False

#
# Return total number of user which user is following
# parameter uid => userid 
#

def getFollowing(uid):
	queryTerm = "Select count(*) as count from `user_followers` where `userid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return str(totalRecords1[0]['count'])
	else:
		return '0'	
#
# Return list of user of user which user is following 
# parameter uid => userid 
#

def getFollowingList(uid):
	queryTerm = "Select b.`username`,b.`id`,b.`fullname` from `user_followers` a  INNER JOIN  `users` b  where a.`userid`='{0}' and a.`followerid` = b.`id`".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''	
		
#
# Return total number of user follower 
# parameter uid => userid 
#

def getFollower(fid):
	queryTerm = "Select count(*) as count from `user_followers` where `followerid`='{0}'".format(fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return str(totalRecords1[0]['count'])
	else:
		return '0'	
#
# Return list of user follower 
# parameter uid => userid 
#
def getFollowerList(uid):
	queryTerm = "Select b.`username`,b.`id`,b.`fullname` from `user_followers` a  INNER JOIN  `users` b  where a.`followerid`='{0}' and a.`userid` = b.`id`".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''	

#
# handle follow/unfollow of user
# parameter uid => userid and fid => followerid
#	
def follower_unfollow(uid,fid):
	chk = isFollowing(uid,fid)
	if chk:
		queryTerm = "Delete from `user_followers` where `userid`='{0}' and `followerid`='{1}'".format(uid,fid)
	else:
		queryTerm = "Insert into `user_followers` SET `userid`='{0}',`followerid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	curs1.close()

#
# Return list of images uploaded by user.
# parameter uid => userid , start => starting from , end => number of records to display on page
#		
def get_useruploads(uid,start=0,end=6):
	queryTerm = "SELECT uuid FROM `user_filenames` where  `userid`='{0}' order by createdAt DESC limit {1},{2}".format(uid,start,end)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''

#
# Return count of images uploaded by user.
# parameter uid => userid
#	
def get_useruploadsCount(uid):
	queryTerm = "SELECT count(*) as count FROM `user_filenames` where  `userid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0


#------------- attributecount------------
# Return count of attribute likedcount by user.
# parameter uid => userid
#	
def get_attributelikedCount(uid):
	queryTerm = "SELECT count(*) as count FROM `attribute_like` where  `userid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0



#
# Return list of images identified by user.
# parameter uid => userid , start => starting from , end => number of records to display on page
#	#(if need images instead of attributes:- select uuid from image_attribute where index == attribute_id ) 		
def get_useridentify(uid,start=0,end=6):
	#~ queryTerm = "SELECT a.uuid, b.attribute_type, c.attributeid FROM imageindex AS a INNER JOIN image_attributes AS b ON a.name = b.attribute_type INNER JOIN user_images_attributes_check AS c ON b.index = c.attributeid WHERE c.userid ='{0}' GROUP BY `uuid` limit {1},{2}".format(uid,start,end)
	queryTerm = " SELECT a.uuid, b.attribute_name, c.attributeid FROM imageindex AS a INNER JOIN image_attributes AS b ON a.name = b.attribute_name INNER JOIN user_images_attributes AS c  ON b.index = c.attributeid where c.userid ='{0}' ORDER BY `c`.`attributeid` DESC limit {1},{2}".format(uid,start,end)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''

#
# Return count of images identified by user.
# parameter uid => userid
#
def get_useridentifyCount(uid):
	queryTerm = "SELECT  count(distinct a.uuid) as count, a.uuid, b.attribute_name, c.attributeid FROM imageindex AS a INNER JOIN image_attributes AS b ON a.name = b.attribute_name INNER JOIN user_images_attributes AS c  ON b.index = c.attributeid where c.userid = '{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0

#
# Return list of images Liked by user.
# parameter uid => userid , start => starting from , end => number of records to display on page
#

def get_userLiked(uid,start=0,end=6):
	queryTerm = "SELECT imageuid FROM `image_like` where  `userid`='{0}' order by createdAt DESC limit {1},{2}  ".format(uid,start,end)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''



#
# Return list of images Liked by user in attribute image.
# parameter uid => userid , start => starting from , end => number of records to display on page
#

def get_userLikedattribute(uid,start=0,end=6):
	queryTerm = "SELECT attributeid FROM `attribute_like` where  `userid`='{0}' order by createdAt DESC limit {1},{2}  ".format(uid,start,end)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''

# Return count of images liked by user.
# parameter uid => userid
#		
def get_userLikedCount(uid):
	queryTerm = "Select count(*) as count from `image_like` where `userid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0


# my function 
# Return user liked list of image
# parameter : type => Attribute type, name => attribute name , uuid => image uuid
#

#~ def get_userLikedrelated(uid,start,limit):
	#~ queryTerm = "SELECT imageuid FROM `image_like` WHERE `userid` = '{0}' limit {1},{2}".format(uid,start,limit) 
	#~ curs1 = conn.cursor(oursql.DictCursor)
	#~ curs1.execute(queryTerm)
	#~ totalRecords1 = curs1.fetchall()
	#~ curs1.close()
	#~ totalRecords = len(totalRecords1)
	#~ # parameter useruploads => list of images , uuid => image uuid (uuid/imageuid),h1text = can give blank
	#~ html = processUserProfilePageimages(totalRecords1,uid,'') 
	#~ linkhtml= ''
	#~ if totalRecords >= limit:
		#~ #linkhtml = '<nav id="page-nav"><a class="load-link" href="'+SITEURL+'showthing.py?namesearch=namesearch&uuid='+str(uuid)+'&start='+str(int(start)+limit)+'"></a></nav>'
		#~ linkhtml = '<nav id="page-nav"><a class="load-link" href="'+SITEURL+'profile.py?name=name&uid='+str(uid)+'&start='+str(int(start)+limit)+'"></a></nav>'
	#~ if totalRecords > 0:
		#~ return (html+linkhtml)
	#~ else:
		#~ return ''


#
# Return list of images owned by user.
# parameter uid => userid , start => starting from , end => number of records to display on page
#	#(if need images instead of attributes:- select uuid from image_attribute where index == attribute_id ) 		
def get_ownit(uid,start=0,end=6):
	queryTerm = "SELECT `imageid` FROM `attribute_actions` where ownit = 'liked' and  userid = '{0}' ORDER BY `id` DESC limit {1},{2}".format(uid,start,end)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''

#
# Return count of images owned by user.
# parameter uid => userid
#	
def get_ownCount(uid):
	queryTerm = "SELECT count(*) as count FROM `attribute_actions` where `ownit` = 'liked' and `userid` = '{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0




#
# Return number of likes for attribute image
# parameter uid => imageuid(uuid) , strin => Need string output or Integer 
#
def getattributeImagelikes(uid,strin=1):
	queryTerm = "Select count(*) as count from `attribute_like` where `attributeid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if strin == 1:
		if totalRecords > 0:
			return str(totalRecords1[0]['count'])
		else:
			return '0'
	else:
		if totalRecords > 0:
			return totalRecords1[0]['count']
		else:
			return 0
		



# Return html of likes for attribute image
# parameter uid => imageuid(uuid)
#
def getattributeImagelikesHtml(uid):
	like = getattributeImagelikes(uid,0)
	if like > 1:
		return  str(like) + " likes"
	elif like == 1:
		return  str(like) + " like"
	else:
		return ''









#
# Return count of unique uuid in filenames (table).
# parameter randm => current generated uuid
#		
def get_uniqueuuid(randm):
	queryTerm = "Select count(*) as count from `filenames` where `uuid`='{0}'".format(randm)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return int(totalRecords1[0]['count'])
	else:
		return 0


		
		
#
# Return number of likes for image
# parameter uid => imageuid(uuid) , strin => Need string output or Integer 
#
def getImagelikes(uid,strin=1):
	queryTerm = "Select count(*) as count from `image_like` where `imageuid`='{0}'".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if strin == 1:
		if totalRecords > 0:
			return str(totalRecords1[0]['count'])
		else:
			return '0'
	else:
		if totalRecords > 0:
			return totalRecords1[0]['count']
		else:
			return 0
		
#
# Return html of likes for image
# parameter uid => imageuid(uuid)
#
def getImagelikesHtml(uid):
	like = getImagelikes(uid,0)
	if like > 1:
		return  str(like) + " likes"
	elif like == 1:
		return  str(like) + " like"
	else:
		return ''

#
# Check either image is liked or not by a user.
# parameter fid => imageuid(uuid) , uid => userid
#
		
def isLiked(uid,fid):
	queryTerm = "Select userid from `image_like` where `userid`='{0}' and `imageuid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return True
	else:
		return False
		
		
		
		
		
# Check either image is liked or not by a user for attribute image.
# parameter fid => imageuid(uuid) , uid => userid
#
		
def isLikedattribute(uid,fid):
	queryTerm = "Select userid from `attribute_like` where `userid`='{0}' and `attributeid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return True
	else:
		return False		
		
		
		
		
		
#
# Handle either image is liked or not by a user.
# parameter fid => imageuid(uuid) , uid => userid
#
			
def img_likeunlike(uid,fid):
	chk = isLiked(uid,fid)
	if chk:
		queryTerm = "Delete from `image_like` where `userid`='{0}' and `imageuid`='{1}'".format(uid,fid)
	else:
		queryTerm = "Insert into `image_like` SET `userid`='{0}',`imageuid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	curs1.close()


# Handle either image is liked or not by a user for attribute image.
# parameter fid => imageuid(uuid) , uid => userid
#
			
def img_likeunlikeattribute(uid,fid):
	chk = isLikedattribute(uid,fid)
	if chk:
		queryTerm = "Delete from `attribute_like` where `userid`='{0}' and `attributeid`='{1}'".format(uid,fid)
	else:
		queryTerm = "Insert into `attribute_like` SET `userid`='{0}',`attributeid`='{1}'".format(uid,fid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	curs1.close()




#
# Return the user of image
# parameter index => imageuid(uuid) , uid => userid
#
def get_userofimage(uid,index):
	queryTerm = "SELECT a.`userid`,u.`fullname`, u.`username` FROM `user_filenames` a    INNER JOIN `users` u    where a.`uuid`='{0}' and a.`userid` = u.`id` ".format(uid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0: 
		if totalRecords1[0][index] is None:
			return totalRecords1[0]['username']
		return totalRecords1[0][index]
	else:
		return 'luxradar'

#
# Return the Html for images
# parameter useruploads => list of images , uuid => image uuid parameter (uuid or imageuid) , h1text => Title text
#		
def processUserProfilePageimagesold(useruploads,uuid,h1text):
	useruploadshtml = ''
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo =get_userofimage(str(userupload[uuid]),'fullname')
		#Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		likehtml = get_likehtmlforimage(str(userupload[uuid]))
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			#useruploadshtml = str(userinfo)
			useruploadshtml = useruploadshtml + '<div class="col-md-2 text-center" ><a href="'+SITEURL+'image/'+(userupload[uuid])+'" ><img id="'+(userupload[uuid])+'" alt="'+(imageType[0])+'"   src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath((userupload[uuid]))+imageType[2]+'" class="randompic"></a> <br /> <span> by '+str(userinfo)+' </span>'+likehtml+'</div>'
	if h1text != '':
		useruploadshtml = '<h1>'+h1text+' : '+str(len(useruploads))+'</h1>' + useruploadshtml
	return useruploadshtml

#
# Return the Html for images
# parameter useruploads => list of images , uuid => image uuid parameter (uuid or imageuid) , h1text => Title text
#
def processUserProfilePageimages(useruploads,uuid,h1text):
	useruploadshtml = ''
	useruploadshtml1 = []
	
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo = get_userofimage(str(userupload[uuid]),'fullname')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			#useruploadshtml1.append(('<div class="img_content allcompany text-center" ><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" class="randompic"></a> <br /> <span> by '+userinfo+' <br /> '+Imagelikes+' </span></div>'))
			#~ '<div class="row"><div class="img-block"><div class="img-holder"><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" class="randompic"></a></div><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a><a class="like-holder" href="#"><span class="icone-like"><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>Let it rain</strong><p>By:<a href="#">'+userinfo+'</a></p></div></div></div></div>'
			useruploadshtml1.append(('<div class="img-block"><div class="img-holder"><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" style="auto; height:310px;"></a></div><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a><a class="like-holder" href="#"><span class="icone-like"><i class="icon-heart"></i><i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>Let it rain</strong><p>By:<a href="#">' +userinfo+'</a></p></div></div></div>'))
	useruploadshtml = "".join(useruploadshtml1)

	return useruploadshtml
#######################################################
	#~ for userupload in useruploads:
		#~ imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		#~ userinfo = get_userofimage(str(userupload[uuid]),'fullname')
		#~ Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		#~ if imageinfo is not None:
			#~ imageType = getImageUUID(imageinfo)
			#~ #useruploadshtml1.append(('<div class="img_content allcompany text-center" ><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" class="randompic"></a> <br /> <span> by '+userinfo+' <br /> '+Imagelikes+' </span></div>'))
			#~ '<div class="row"><div class="img-block"><div class="img-holder"><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" class="randompic"></a></div><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a><a class="like-holder" href="#"><span class="icone-like"><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>Let it rain</strong><p>By:<a href="#">'+userinfo+'</a></p></div></div></div></div>'
			#~ if (i<=1):
				#~ useruploadshtml1.append(('<div class="img-block"><div class="img-holder"><a href="'+SITEURL+'image/'+str(userupload[uuid])+'" ><img id="'+str(userupload[uuid])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" style="width:310px; height:310px;"></a></div><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a><a class="like-holder" href="#"><span class="icone-like"><i class="icon-heart"></i><i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>Let it rain</strong><p>By:<a href="#">' +userinfo+'</a></p></div></div></div>'))
				#~ i=i+1
			#~ else:
				#~ useruploadshtml = "".join(useruploadshtml1)
				#~ divrow1.append(('<div class="row">'+useruploadshtml+'</div>'))
				#~ useruploadshtml1 = []
				#~ i=0	
	#~ divrow = "".join(divrow1)
	#~ return divrow.decode('utf-8')
##################################################################

#
# Return the Html for image Liked showimage.py
# parameter  uuid => image uuid
#
def get_likehtmlforimage(uuid):
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid =  str(userdata[2])
	else:
		userid = 0
	likeimagepath = 'likeimageiconfalse.png'
	likeimagetrue = False
	totallikes = getImagelikes(str(uuid))
	likeimagetrue = isLiked(userid,str(uuid))
	if likeimagetrue:
		likeimagetrue = '1'
		likeimagepath = '<span class="icone-like"><i class="icon-heart2 myicon-heart2"></i></span>'
	else:
		likeimagetrue = '0'
		likeimagepath = '<span class="icone-like"><i class="icon-heart"></i><i class="icon-heart2"></i></span>'
		
	htmlbtn = ''
	if userid != 0:
		htmlbtn = '<a class="likeimage like-holder" title="Like Image" rel="'+str(uuid)+'">'+likeimagepath+'<span class="quantity">--Imagelikes--</span></a>'
		#htmlbtn = '<button type="button" class="btn" style="background-color: rgb(255, 255, 255); border: 1px solid rgb(204, 204, 204); margin-top: 9px; box-shadow: 1px 2px 1px 1px rgb(204, 204, 204);">Total Likes : <span class="badge" style="background-color: rgb(255, 38, 69);">'+str(totallikes)+'</span></button>'+htmlbtn
	return htmlbtn
	#return '<button type="button" class="btn" style="background-color: rgb(255, 255, 255); border: 1px solid rgb(204, 204, 204); margin-top: 9px; box-shadow: 1px 2px 1px 1px rgb(204, 204, 204);">Total Likes : <span class="badge" style="background-color: rgb(255, 38, 69);">'+str(totallikes)+'</span></button>'+htmlbtn

# return the HTML for image liked index.py

def get_likehtmlforindexpage(uuid):
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid =  str(userdata[2])
	else:
		userid = 0
	likeimagepath = 'likeimageiconfalse.png'
	likeimagetrue = False
	#~ totallikes = getImagelikes(str(uuid))
	likeimagetrue = isLiked(userid,str(uuid))
	if likeimagetrue:
		likeimagetrue = '1'
		likeimagepath = '<span class="icone-like"><i class="icon-heart2 myicon-heart2"></i></span>'
	else:
		likeimagetrue = '0'
		likeimagepath = '<span class="icone-like"><i class="icon-heart"></i><i class="icon-heart2"></i></span>'
		
	htmlbtn = ''
	if userid != 0:
		htmlbtn = '<a class="likeimage like-holder" title="Like Image" rel="'+str(uuid)+'">'+likeimagepath
		#htmlbtn = '<button type="button" class="btn" style="background-color: rgb(255, 255, 255); border: 1px solid rgb(204, 204, 204); margin-top: 9px; box-shadow: 1px 2px 1px 1px rgb(204, 204, 204);">Total Likes : <span class="badge" style="background-color: rgb(255, 38, 69);">'+str(totallikes)+'</span></button>'+htmlbtn
	return htmlbtn



# return the HTML for attribute imageliked liked showthing.py

def get_likehtmlforattributeimage(uuid):
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid =  str(userdata[2])
	else:
		userid = 0
	#likeimagepath = 'likeimageiconfalse.png'
	likeimagetrue = False
	#~ totallikes = getImagelikes(str(uuid))
	likeimagetrue = isLikedattribute(userid,str(uuid))
	if likeimagetrue:
		likeimagetrue = '1'
		likeimagepath = '<span class="icone-like"><i class="icon-heart2 myicon-heart2"></i></span>'
	else:
		likeimagetrue = '0'
		likeimagepath = '<span class="icone-like"><i class="icon-heart"></i><i class="icon-heart2"></i></span>'
		
	htmlbtn = ''
	if userid != 0:
		htmlbtn = '<a class="attrlikeimage like-holder" title="Like Image" rel="'+str(uuid)+'">'+likeimagepath
		#htmlbtn = '<button type="button" class="btn" style="background-color: rgb(255, 255, 255); border: 1px solid rgb(204, 204, 204); margin-top: 9px; box-shadow: 1px 2px 1px 1px rgb(204, 204, 204);">Total Likes : <span class="badge" style="background-color: rgb(255, 38, 69);">'+str(totallikes)+'</span></button>'+htmlbtn
	return htmlbtn


# Return the form to like the image for attribute image
# parameter  reloadtrue => need to reload page or not
#	
def get_likeFormattribute(reloadtrue = False):
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid =  str(userdata[2])
	else:
		userid = ''
	attr_reloadtruehtml = ''
	if reloadtrue :
		attr_reloadtruehtml = '<input type="hidden" value="true" name="reload">'
	attr_htmlform = '<form method="post" action="'+SITEURL+'login.py" id="attrformlikeimage"><input type="hidden" id="attr_lk_imageid" value=""  name="attrimageid"><input type="hidden" value="'+userid+'"  name="userid1"><input type="hidden" value="attrlikeimage"  name="attrlikeimage">'+attr_reloadtruehtml+'<input type="hidden" value="attrlikeimage" name="action"></form>'
	return attr_htmlform
#
# Return the form to like the image
# parameter  reloadtrue => need to reload page or not
#	
def get_likeForm(reloadtrue = False):
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid =  str(userdata[2])
	else:
		userid = ''
	reloadtruehtml = ''
	if reloadtrue :
		reloadtruehtml = '<input type="hidden" value="true" name="reload">'
	htmlform = '<form method="post" action="'+SITEURL+'login.py" id="formlikeimage"><input type="hidden" id="lk_imageid" value=""  name="imageid"><input type="hidden" value="'+userid+'"  name="userid"><input type="hidden" value="likeimage"  name="likeimage">'+reloadtruehtml+'<input type="hidden" value="likeimage" name="action"></form>'
	return htmlform

#
# Return the pagination for a page
# parameter : url => page url, pageid => page number , totalcount => number of records,limit => number of records to display
# userfrnd => Url is user friendly or not.
#
def getPagination(url,pageid,totalcount,limit,userfrnd=0):
	noofpages = totalcount/limit
	lastc  = totalcount%limit
	currentpageloop = pageid/10
	itemonpage = 0
	if pageid > 0:
		itemonpage = totalcount - ((int(pageid) - 1) * limit)
		if itemonpage > limit:
			itemonpage = limit
		
	if pageid > noofpages:
		currentpageloop = currentpageloop -1
	if currentpageloop == 0:
		currentpageloopst = currentpageloop*10+1
		currentpageloopend = currentpageloopst + 10
	else:
		currentpageloopst = currentpageloop*10
		currentpageloopend = currentpageloopst + 11
		
	if pageid == 1 or pageid < 1:
		Previous =1
	else:
 		Previous =str(pageid-1)

	Next =str(pageid+1)
	if lastc == 0:
		noofpages = noofpages - 1
	if currentpageloopst < 0:
		currentpageloopst = 1
		currentpageloopend = pageid
	if userfrnd == 1:
		if '?' in url:
			urldef = '&pageid='
		else:
			urldef = '?pageid='
	else:
		urldef = '/'
	paginationhtml=''
	paginationhtml = paginationhtml + '<div class="pagination"><a class="button" href="'+str(url)+urldef+'1"><span><img width="12" height="9" alt="First" src="'+STATICURL+'/images/arrow-stop-180-small.gif"> First</span></a><a class="button" href="'+str(url)+urldef+str(Previous)+'"><span><img width="12" height="9" alt="Previous" src="'+STATICURL+'/images/arrow-180-small.gif"> Prev</span></a><div class="numbers">Showing '+str(itemonpage)+' of total '+str(totalcount)+' results. <span>Page:</span>'
	for i in range(currentpageloopst,currentpageloopend):
		if i == noofpages+1 and pageid == i:
			paginationhtml = paginationhtml + '<span class="current">'+str(i)+'</span>'
			return paginationhtml +'<div style="clear: both;"></div></div>'
		elif i == pageid:
			paginationhtml = paginationhtml + '<span class="current">'+str(i)+'</span> <span>|</span>'
		elif i <= noofpages:
			paginationhtml = paginationhtml + '<a href="'+url+urldef+str(i)+'">'+str(i)+'</a> <span>|</span>'

	if noofpages+1 > 10:
		paginationhtml = paginationhtml + '<span>...</span><span>|</span>'
  	
  	paginationhtml = paginationhtml + '<a href="'+url+urldef+str(noofpages+1)+'">'+str(noofpages+1)+'</a></div><a class="button" href="'+url+urldef+str(Next)+'"><span>Next <img width="12" height="9" alt="Next"  src="'+STATICURL+'/images/arrow-000-small.gif"></span></a><a class="button last"  href="'+url+urldef+str(noofpages+1)+'"><span>Last <img width="12" height="9" alt="Last"  src="'+STATICURL+'/images/arrow-stop-000-small.gif"></span></a>'
  	#+str(currentpageloopst)+'--'+str(currentpageloopend)
	paginationhtml = paginationhtml +'<div style="clear: both;"></div></div>'
	return paginationhtml
#
# Return related images of image
# parameter : attributesList=> List of attribute of image, uuid => image uuid
#	
def get_relatedImages(attributesList,uuid):
	atrributeArr = ['Actress','Actor']
	atrributeArr1 = ['Brand']
	atrributeArr2 = ['Designer','Public Figure','Model']
	i = 0
	type=''
	name=''
	type1=''
	name1=''
	type2=''
	name2=''

	for i in range (len(attributesList)):
		if attributesList[i][1] in atrributeArr and type == '':
			type = attributesList[i][1]
			name = attributesList[i][0]
		if attributesList[i][1] in atrributeArr1 and type1 == '':
			type1 = attributesList[i][1]
			name1 = attributesList[i][0]
		if attributesList[i][1] in atrributeArr1 and type2 == '':
			type2 = attributesList[i][1]
			name2 = attributesList[i][0]
		i = i + 1
	
	if type == '' and type1 == '' and type2 == '':
		type = attributesList[0][1]
		name = attributesList[0][0]
		html = get_relatedImagesSql(type,name,uuid)
	elif type == '' and type1 == '':
		html = get_relatedImagesSql(type2,name2,uuid)
	else:
		html = ''
		if 	type != '':
			html = html + get_relatedImagesSql(type,name,uuid)
		if 	type1 != '':
			html = html + get_relatedImagesSql(type1,name1,uuid)
	
	return html

#
# Return related  images list of image
# parameter : type => Attribute type, name => attribute name , uuid => image uuid
#

def get_relatedImagesSql(type,name,uuid):
	queryTerm = "SELECT uuid FROM `image_attributes` WHERE `attribute_name` = '{0}' and `attribute_type` = '{1}' and `status`=1 and uuid != '{2}' limit 0,3".format(addslashes((name)),addslashes(type),uuid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	html = processRelatedimages(totalRecords1,'uuid','More photos for '+(type) +' : '+(name)) 
	if totalRecords > 0:
		return (html)
	else:
		return ''


#
# Return related  images list of image
# parameter : type => Attribute type, name => attribute name , uuid => image uuid
#

def get_AttributerelatedImages(name,uuid,start,limit):
	queryTerm = "SELECT uuid FROM `image_attributes` WHERE `attribute_name` = '{0}' and `status`=1 limit {1},{2}".format(addslashes(name),start,limit)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	html = processAttributerelatedImages(totalRecords1,'uuid') 
	linkhtml= ''
	if totalRecords >= limit:
		linkhtml = '<nav id="page-nav"><a class="load-link" href="'+SITEURL+'showthing.py?namesearch=namesearch&uuid='+str(uuid)+'&start='+str(int(start)+limit)+'"></a></nav>'
	if totalRecords > 0:
		return (html+linkhtml)
	else:
		return ''

#
# Return html for related images of image thing page
# parameter : useruploads => List of images,uuid => image uuid parameter (uuid or imageuid) , h1text => Title text
#
#~  3-3-3-3 format (DEFAULT)



#############oldfunction############
def processAttributerelatedImagessss(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo =get_userofimage(str(userupload[uuid]),'fullname')
		userinfo1 =get_userofimage(str(userupload[uuid]),'username')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		likehtml = get_likehtmlforindexpage(str(userupload[uuid]))
		likeForm = get_likeForm(True) 
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			dots = showCharacterLimit(imageType[0],20,'...')
		if Imagelikes != '':
			Imagelikes = Imagelikes.replace('likes','').replace('like','')
			Imagelikes = Imagelikes.strip()
		try:
			imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
		except Exception as e:
			continue
		if i == 4 : #664
			if get_cookie("userdatasite"):
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

			i = 1
		else:
			j = j+1
			if i == 1:
				useruploadshtml1.append('<div class="images-row three-blocks">')
			if get_cookie("userdatasite"):
				useruploadshtml1.append(('<div class="row"> <div class="img-block"> <a href="'+SITEURL+'image/'+str(userupload[uuid])+'" class="img-holder"> <span class="holder-box-w"><img src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" style="width:'+imageDimension[0]+'px;" alt="Image description"></span></a> <div class="info"> <div class="info-holder"> <a href="#" class="btn btn-add icone-share"><i class="icon-share"></i></a> <a href="#" class="like-holder"> <span class="icone-like"> <i class="icon-heart"></i> <i class="icon-heart3"></i></span> <span class="quantity">32</span></a></div><div class="img-caption"> <strong>Let it rain</strong> <p>By: <a href="#">Gary Barnett</a></p></div></div></div></div>'))
				#~ useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:auto; height:250px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

				
			if i == 3:
				useruploadshtml1.append('</div>')
				i = 1
			else:		
				i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %3==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml


####################endfunction#################





#~ 
def processAttributerelatedImages(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo =get_userofimage(str(userupload[uuid]),'fullname')
		userinfo1 =get_userofimage(str(userupload[uuid]),'username')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		likehtml = get_likehtmlforindexpage(str(userupload[uuid]))
		likeForm = get_likeForm(True) 
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			dots = showCharacterLimit(imageType[0],20,'...')
			dots1 = showCharacterLimit(imageType[0],100,'...')
		if Imagelikes != '':
			Imagelikes = Imagelikes.replace('likes','').replace('like','')
			Imagelikes = Imagelikes.strip()
		try:
			imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
		except Exception as e:
			continue
		if i == 4 : #664
			if get_cookie("userdatasite"):
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share  lightbox" href="#sharepopup">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

			i = 1
		else:
			j = j+1
			if i == 1:
				useruploadshtml1.append('<div class="images-row three-blocks"><div class="row">')
			if get_cookie("userdatasite"):
				
				if int(imageDimension[0]) > int(imageDimension[1]):
					useruploadshtml1.append(('<div class="img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"> <img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"> <span class="holder-box-w"><img style="width:'+imageDimension[0]+'px; height:'+imageDimension[1]+'px;"src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
					
				elif int(imageDimension[0]) < int(imageDimension[1]):
					useruploadshtml1.append(('<div class="img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"> <img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"> <span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;height:'+imageDimension[1]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			
				else:
						useruploadshtml1.append(('<div class="img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"> <img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"> <span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;height:'+imageDimension[1]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share  lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

				
			if i == 3:
				useruploadshtml1.append('</div></div>')
				i = 1
			else:		
				i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j%3==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div></div>"
	return useruploadshtml

 



# Return html for related images of image profile page 2-2 format attribute image
# parameter : useruploads => List of images,uuid => image uuid parameter (uuid or imageuid) , h1text => Title text
# ---------------------------------EDITED--------------------------------------------

def get_attribute_imagenamesss(imagedata):
	#~ imagename_list=[]
	for imgs in imagedata:
		imguuid = str(imgs['attributeid'])
		#~ imguuid = '741f6b78d5'
		queryTerm = "SELECT * FROM `imageindex` where  `uuid`='{0}'".format(imguuid)
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords1 = curs1.fetchall()
		curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return ''

#~ 2-1-2-1 format
def processAttributerelatedImages2(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo =get_userofimage(str(userupload[uuid]),'fullname')
		userinfo1 =get_userofimage(str(userupload[uuid]),'username')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		likehtml = get_likehtmlforindexpage(str(userupload[uuid]))
		likeForm = get_likeForm(True) 
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			dots = showCharacterLimit(imageType[0],20,'...')
		if Imagelikes != '':
			Imagelikes = Imagelikes.replace('likes','').replace('like','')
			Imagelikes = Imagelikes.strip()
		try:
			imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
		except Exception as e:
			continue
		if i == 3 : #664
			if get_cookie("userdatasite"):
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

			i = 1
		else:
			j = j+1
			if i == 1:
				useruploadshtml1.append('<div class="images-row">')
			if get_cookie("userdatasite"):
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:auto; height:310px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

				
			if i == 2:
				useruploadshtml1.append('</div>')
			
			i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %2==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml

def ProcessProfileAttributeImages(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for imgs in useruploads:
		imguuid = str(imgs['attributeid'])
		queryTerm = "SELECT * FROM `imageindex` where  `uuid`='{0}'".format(imguuid)
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords1 = curs1.fetchall()
		curs1.close()
		totalRecords = len(totalRecords1)
		
		for userupload in totalRecords1:
			userattributelikedform = get_likeFormattribute(True)
			#~ imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
			imageinfo = userupload['name']
			userinfo =get_userofimage(str(userupload[uuid]),'fullname')
			userinfo1 =get_userofimage(str(userupload[uuid]),'username')
			Imagelikes = getattributeImagelikesHtml(str(userupload[uuid]))
			likehtml = get_likehtmlforattributeimage(str(userupload[uuid]))
			
			uuids = totalRecords1[0]['imagename']		
			dir = "imagesnew/"
			first = uuids[0]+"/"
			second = uuids[1]+"/"	
			third = uuids[2]+"/"
			imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
			#~ useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>....</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				
			#~ if os.path.isfile(str(dir+first+second+third) + uuids): #check if image exits in thumbs
				#~ imagepath =  SITEURL+ str(dir+first+second+third) + uuids  
			#~ else: 
				#~ if getbucketImage(uuids): 
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/7/4/741fb85ba2.jpg'
				#~ else: 
					#~ imagepath =  useruploads['orignalurl']
			#~ 
			if imageinfo is not None:
				dots = showCharacterLimit(imageinfo,20,'...')
				dots1 = showCharacterLimit(imageinfo,100,'...')
			#~ if Imagelikes != '':
				#~ Imagelikes = Imagelikes.replace('likes','').replace('like','')
				#~ Imagelikes = Imagelikes.strip()
			#~ try:
				#~ imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
			#~ except Exception as e:
				#~ continue
			imagename = getImageByUuid(str(userupload[uuid]))
			try:
				imageDimension = getImageDimensionAWS(imagepath)
			except Exception as e:
				continue
			if i == 4 : #664
				if get_cookie("userdatasite"):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'">THING<img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+userattributelikedform+'</div>'))
				else:
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

				i = 1
			else:
				j = j+1
			
				if i == 1:
					useruploadshtml1.append('<div class="images-row three-blocks">')
				if get_cookie("userdatasite"):
					if int(imageDimension[0]) > int(imageDimension[1]):
						
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class = "holder-box-w"><img style="width:'+imageDimension[0]+'px; height:250px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
					elif int(imageDimension[1]) > int(imageDimension[0]):
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class = "holder-box-h"><img style="width:'+imageDimension[0]+'px; height:250px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
					else:
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class = "holder-box-h"><img style="width:'+imageDimension[0]+'px; height:250px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
						
				else:
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:auto; height:310px;" src="'+SITEURL+''+imagepath+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

						
				if i == 3:
					useruploadshtml1.append('</div>')
					i = 1
					j = 0
				else:		
					i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %3==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml				
				

					#~ 
				#~ if i == 2:
					#~ useruploadshtml1.append('</div>')
					#~ i = 1
					#~ j = 0
				#~ else:		
					#~ i = i+1			
#~ 
	#~ 
	#~ useruploadshtml = "".join(useruploadshtml1)
	#~ if j %2==0:
		#~ i=1
	#~ else:
		#~ useruploadshtml = useruploadshtml + "</div>"
	#~ return useruploadshtml

################## identified profile page images########
def ProcessProfileIdentifiedImages(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for imgs in useruploads:
		imguuid = str(imgs['uuid'])
		queryTerm = "SELECT * FROM `imageindex` where  `uuid`='{0}'".format(imguuid)
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords1 = curs1.fetchall()
		curs1.close()
		totalRecords = len(totalRecords1)		
			
		
		for userupload in totalRecords1:
			userattributelikedform = get_likeFormattribute(True)
			#~ imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
			imageinfo = userupload['name']
			userinfo =get_userofimage(str(userupload[uuid]),'fullname')
			userinfo1 =get_userofimage(str(userupload[uuid]),'username')
			Imagelikes = getattributeImagelikesHtml(str(userupload[uuid]))
			likehtml = get_likehtmlforattributeimage(str(userupload[uuid]))
			getimageid = getImageByUuid
			uuids = totalRecords1[0]['imagename']	
			dir = "imagesnew/"
			first = uuids[0]+"/"
			second = uuids[1]+"/"	
			third = uuids[2]+"/"
			imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
			#~ useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>....</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				
			#~ if os.path.isfile(str(dir+first+second+third) + uuids): #check if image exits in thumbs
				#~ imagepath =  SITEURL+ str(dir+first+second+third) + uuids  
			#~ else: 
				#~ if getbucketImage(uuids): 
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/7/4/741fb85ba2.jpg'
				#~ else: 
					#~ imagepath =  useruploads['orignalurl']
			#~ 
			if imageinfo is not None:
				dots = showCharacterLimit(imageinfo,20,'...')
				dots1 = showCharacterLimit(imageinfo,100,'...')
			#~ if Imagelikes != '':
				#~ Imagelikes = Imagelikes.replace('likes','').replace('like','')
				#~ Imagelikes = Imagelikes.strip()
			#~ try:
				#~ imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
			#~ except Exception as e:
			try:
				imageDimension = getImageDimensionAWS(imagepath)
			except Exception as e:
				continue	
			if i == 4 : #664
				if get_cookie("userdatasite"):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'">THING<img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+userattributelikedform+'</div>'))
				else:
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

				i = 1
			else:
				j = j+1
			
				if i == 1:
					useruploadshtml1.append('<div class="images-row three-blocks">')
				if get_cookie("userdatasite"):
					if int(imageDimension[0]) > int(imageDimension[1]):
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
					elif int(imageDimension[1]) > int(imageDimension[0]):
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
					else:
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
				else:
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:auto; height:310px;" src="'+SITEURL+''+imagepath+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

						
				if i == 3:
					useruploadshtml1.append('</div>')
					i = 1
					j = 0
				else:		
					i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %3==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml				



####################### end idenified profile page images




##############  ownit profile images###########################
def ProcessProfileOwnitImages(useruploads,uuid):
	userdata = get_loginsuer()
	userid = userdata[2]
	useruploadshtml = ''
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for imgs in useruploads:
		imguuid = str(imgs['imageid'])
		queryTerm = "SELECT * FROM `imageindex` where  `uuid`='{0}'".format(imguuid)
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords1 = curs1.fetchall()
		curs1.close()
		totalRecords = len(totalRecords1)		
			
		
		for userupload in totalRecords1:
			userattributelikedform = get_likeFormattribute(True)
			#~ imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
			imageinfo = userupload['name']
			userinfo =get_userofimage(str(userupload[uuid]),'fullname')
			userinfo1 =get_userofimage(str(userupload[uuid]),'username')
			Imagelikes = getattributeImagelikesHtml(str(userupload[uuid]))
			likehtml = get_likehtmlforattributeimage(str(userupload[uuid]))
			getimageid = getImageByUuid
			uuids = totalRecords1[0]['imagename']	
			dir = "imagesnew/"
			first = uuids[0]+"/"
			second = uuids[1]+"/"	
			third = uuids[2]+"/"
			imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
			#~ useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>....</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				
			#~ if os.path.isfile(str(dir+first+second+third) + uuids): #check if image exits in thumbs
				#~ imagepath =  SITEURL+ str(dir+first+second+third) + uuids  
			#~ else: 
				#~ if getbucketImage(uuids): 
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + uuids
					#~ imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/7/4/741fb85ba2.jpg'
				#~ else: 
					#~ imagepath =  useruploads['orignalurl']
			#~ 
			if imageinfo is not None:
				dots = showCharacterLimit(imageinfo,20,'...')
				dots1 = showCharacterLimit(imageinfo,100,'...')
			#~ if Imagelikes != '':
				#~ Imagelikes = Imagelikes.replace('likes','').replace('like','')
				#~ Imagelikes = Imagelikes.strip()
			#~ try:
				#~ imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
			#~ except Exception as e:
			try:
				imageDimension = getImageDimensionAWS(imagepath)
			except Exception as e:
				continue				#~ continue
				
			if i == 4 : #664
				if get_cookie("userdatasite"):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'">THING<img style="width:310px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share " href="#">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'+userattributelikedform+'</div>'))
				else:
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

				i = 1
			else:
				j = j+1
			
				if i == 1:
					useruploadshtml1.append('<div class="images-row three-blocks">')
				if get_cookie("userdatasite"):
					if int(imageDimension[0]) > int(imageDimension[1]):		
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))
					elif int(imageDimension[1]) > int(imageDimension[0]):
						useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img width="320" height="320" alt="image description" src="'+STATICURL+'images/img-base-2.png"><span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;" src="'+imagepath+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup" rel="'+str(userupload[uuid])+'"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div>'+userattributelikedform+'</div>'))

							
				else:
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'thing/'+str(userupload[uuid])+'"><img style="width:auto; height:310px;" src="'+SITEURL+''+imagepath+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+SITEURL+''+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

						
				if i == 3:
					useruploadshtml1.append('</div>')
					i = 1
					j = 0
				else:		
					i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %3==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml				
				







#################  end ownit profile images#######################


#
# Return html for related images of image
# parameter : useruploads => List of images,uuid => image uuid parameter (uuid or imageuid) , h1text => Title text
#
def processRelatedimages(useruploads,uuid,h1text):
	useruploadshtml = ''
	for userupload in useruploads:
		imageinfo = getImageInfoFromUUIDAll(str(userupload[uuid]), curs)
		userinfo =get_userofimage(str(userupload[uuid]),'fullname')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		if imageinfo is not None:
			imageType = getImageUUID(imageinfo)
			useruploadshtml = useruploadshtml + '<li><a class="img-holder"  href="'+SITEURL+'image/'+(userupload[uuid])+'" ><img id="'+(userupload[uuid])+'"    src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath((userupload[uuid]))+imageType[2]+'" height="68" width="68" class="randompic"></a></li>'
	#if useruploadshtml != '':
		#useruploadshtml = '<div class="similar-imgs" ><h1 class="font2">'+h1text+'</h1>' + useruploadshtml + '</div>'
	return useruploadshtml

#
# Return html for attribute identified by a user.
# parameter : userid => user id,attributeid =>  Attribute id
#
def get_attributeUserCheck(userid,attributeid):
	queryTerm = "SELECT `check` FROM `user_images_attributes_check`   where  `userid`='{0}' and `attributeid`='{1}' ".format(userid,attributeid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	html = ''
	if totalRecords > 0:
		no =  int(totalRecords1[0]['check'])
	else:
		no = 12
	if no == 0:
		html = "You said NO."
	elif no == 1:
		html = "You said Yes."
	return html
#
# Return html for actions identified by a user.
# parameter : userid => user id,imageid =>  imageid
#
def get_currentactionvalue(userid,imageid):
	queryTerm = "Select wantit, ownit, sale FROM `attribute_actions` where  `userid`='{0}' and `imageid`='{1}'".format(userid,imageid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	def_value={'wantit':'liked','ownit':'liked','sale':'liked'}
	values={}
	if totalRecords > 0:
		if str(totalRecords1[0]['wantit']) =='liked' :
			values['wantit'] = 'unliked' 
		else:
			values['wantit'] = 'liked'
			 
		if str(totalRecords1[0]['ownit']) =='liked' :
			values['ownit'] = 'unliked'
		else:

			values['ownit'] = 'liked'
		if str(totalRecords1[0]['sale']) =='liked' :

			values['sale'] = 'unliked'
		else:
			values['sale'] = 'liked'
			
		return values
	
	else:
		return def_value
	
			
#
# Return html for comments of image.
# parameter : uuid => image uuid
#
def getimageComment(uuid):
	queryTerm = "SELECT * FROM `image_comment`   where  `uuid`='{0}' and `status`='1' order by id ASC ".format(uuid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	html = ''
	userid = 0
	if get_cookie("userdatasite"):
		userdata = get_loginsuer()
		userid = userdata[2]
		
	if totalRecords > 0:
		for userupload in totalRecords1:
			userprofile =get_userprofile(str(userupload['userid']))
			if userprofile[0]['profilepic'] is None or userprofile[0]['profilepic'] == '':
				profilepic = 'defualtprofile.jpg'
			else:
				profilepic = userprofile[0]['profilepic']
			profilephoto = SITEURL+'images/userimages/'+profilepic
			fullname =userprofile[0]['fullname']
			username = userprofile[0]['username']
			if fullname is None:
				fullname =username
			profilelink = SITEURL+username
			fmt = '%A %b,%d %Y %I:%M %p'
			d2 = userupload['createdAt'].strftime(fmt)
			if userupload['reportabuse'] != 1:
				abusehtml = '<a title="Report Abuse" class="randompic_rabuse_a" rel="{0}"><img style="display:none;" class="randompic_rabuse"  src="{1}/images/abuse-sign.jpg" />Report Abuse</a>'.format(userupload['id'],STATICURL)
			else:
				abusehtml = '<a title="Reported Abused" >Abused</a>'
			if str(userid) == str(userupload['userid']):
				abusehtml = '<a title="delete" class="randompic_delete_a" rel="{0}"><img class="randompic_rabuse"  src="{1}/images/del-sign.jpg" /></a>'.format(userupload['id'],STATICURL)
			html = html + '<div class="list-comments"><div class="comment"><div class="comment-holder"> <a href="'+SITEURL+'{5}" class="img-holder"><img src="{2}" height="47" width="47" alt="Image"></a><span class="comment-time"></span></div><span class="comment-text"><strong><a href="{3}">{0}</a></strong> {1}</span></div></div>'.format(fullname,(userupload['comment']),profilephoto,profilelink,abusehtml,username)
						
			#html = html + '<div style="border-bottom: 1px solid #ccc; padding: 10px 2px 2px;" class="col-md-12"> <div class="col-md-1"><img class="randompic_sm" src="{2}" /> <br /> </div><div class="col-md-9"><a href="{3}" target="_blank">{0}</a><br />{1}</div><div class="col-md-2">{4} </div></div>'.format(fullname,(userupload['comment']),profilephoto,profilelink,abusehtml)
			#by <br /> at {4} d2
		   
	return html
		   
		
#
# Return blank if string is none.
# parameter : string => string
#
def CheckNone(string):
	if string is None:
		return ''
	else:
		return string



#
# Search database for the list of attributes associated with the passed search terms
#	
def getImageUUIDListSearch(type,name,limit,start):
	global debughtml
	attribute_name = ''

	if name == '%' or name == '' or name is None:
		attribute_name = ''
	else:
		name = name.replace('-s-','(').replace('-ss-',')').replace('-sss-',"'")
		attribute_name = addslashes(name.strip())
		#attribute_name = 'r1.`attribute_name` = "{0}"'.format(name)
	#queryTerm = 'SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `image_attributes` AS r1 INNER JOIN `filenames` as r3  WHERE r1.`uuid` in (r3.`uuid`) and r3.`status` in (1) and {0} {1} {2} {3}  group by r3.`uuid` limit {4},{5}'.format(attribute_status,attribute_type,attribute_AND,attribute_name,start,limit)
	#queryTerm1 = 'SELECT count(DISTINCT(r1.`uuid`)) as count FROM `image_attributes` AS r1 INNER JOIN `filenames` as r3  WHERE r1.`uuid` in (r3.`uuid`) and r3.`status` in (1) and {0} {1} {2} {3}'.format(attribute_status,attribute_type,attribute_AND,attribute_name)
	#output((queryTerm)+'<br />'+queryTerm1)
	#sys.exit()
	#queryTerm = 'SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name` like "{0}%" group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL like "{0}%" group by r3.`uuid` limit {1},{2};'.format(attribute_name,start,limit)
	
	#queryTerm1 = 'select count(*) as count  from (SELECT r3.uuid FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name` like "{0}%" group by r3.`uuid` UNION SELECT r3.uuid FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL like "{0}%" group by r3.`uuid`) as r2;'.format(attribute_name,start,limit)
	
	queryTerm = 'SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name` like "{0}%"   group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name_reverse` like reverse("%{0}") group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL like "{0}%" group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL_rev like reverse("%{0}") group by r3.`uuid` limit {1},{2};'.format(attribute_name,start,limit)
	
	queryTerm1 = 'select count(*) as count  from (SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name` like "{0}%"   group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name_reverse` like reverse("%{0}") group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL like "{0}%" group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL_rev like reverse("%{0}") group by r3.`uuid` ) as r2;'.format(attribute_name)
	
	#output((queryTerm)+'<br />'+queryTerm1)
	#sys.exit()
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute((queryTerm))
	totalRecords1 = curs1.fetchall()
	curs1.close()
	if start == 0:
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute((queryTerm1))
		totalRecords2 = curs1.fetchall()
		curs1.close()
		totalRecords = len(totalRecords2)
		if totalRecords > 0:
			totalRecordsc =  (totalRecords2[0]['count'])
	else:
		totalRecordsc = 0
	if debug: debughtml = debughtml + "[getImageUUIDList] searched query term: "+queryTerm+"<br>"
	return [totalRecordsc,totalRecords1]


#
# Return the dimesion of an image.
# parameter : path => path of image
#
def getImageDimension(path):
	#535,532
	dimensions = [122850,122850]
	imageorg = Image.open(path)
	srcWidth = Decimal(imageorg.size[0])
	srcHeight = Decimal(imageorg.size[1])
	resizeWidth = srcWidth
	resizeHeight = srcHeight
	aspect = resizeWidth / resizeHeight # Decimal

	if resizeWidth > dimensions[0] or resizeHeight > dimensions[1]:
		# if width or height is bigger we need to shrink things
		if resizeWidth > dimensions[0]:
			resizeWidth = Decimal(dimensions[0])
			resizeHeight = resizeWidth / aspect

		if resizeHeight > dimensions[1] :
			aspect = resizeWidth / resizeHeight
			resizeHeight = Decimal(dimensions[1])
			resizeWidth = resizeHeight * aspect 
			
	return [str(int(resizeWidth)),str(int(resizeHeight))]
	
########## get image dimension for aws images###
def getImageDimensionAWS(path):
	#535,532
	dimensions = [122850,122850]
	file = cStringIO.StringIO(urllib.urlopen(path).read())
	imageorg = Image.open(file)
	srcWidth = Decimal(imageorg.size[0])
	srcHeight = Decimal(imageorg.size[1])
	resizeWidth = srcWidth
	resizeHeight = srcHeight
	aspect = resizeWidth / resizeHeight # Decimal

	if resizeWidth > dimensions[0] or resizeHeight > dimensions[1]:
		# if width or height is bigger we need to shrink things
		if resizeWidth > dimensions[0]:
			resizeWidth = Decimal(dimensions[0])
			resizeHeight = resizeWidth / aspect

		if resizeHeight > dimensions[1] :
			aspect = resizeWidth / resizeHeight
			resizeHeight = Decimal(dimensions[1])
			resizeWidth = resizeHeight * aspect 
			
	return [str(int(resizeWidth)),str(int(resizeHeight))]


#########  end image dimension#########	
	

#
# Return the substring if need to limit the character of string.
# parameter : text => String,limit=> number of charcters to show, append=> Test to append in last (...)
#
def showCharacterLimit(text,limit,append):
	finaltext = text[0:limit]
	if len(text) > limit:
		newtext = text[0:limit]
		newtextar = newtext.split(" ")
		if len(newtextar) > 0:
			newtextar[-1] = ''
			finaltext = ' '.join(newtextar).strip() + append
	return finaltext

#
# Return html for search results. index.py images
# parameter : searchResult => List of images,name=> Search parameter, header=> Need title in html or not
#
def processSearchImages(searchResult,name,header=1):	
		
	useruploadshtml = ''
	uuid= 'uuid'
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for userupload in searchResult:
		userinfo = get_userofimage(str(userupload[uuid]),'fullname')
		userinfo1 = get_userofimage(str(userupload[uuid]),'username')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		
	
		imageType = getImageUUID(userupload) #col-sm-6 col-lg-4
		Imageid = imageType[1]
		dots = showCharacterLimit(imageType[0],20,'...')
		dots1 = showCharacterLimit(imageType[0],100,'...')
		if Imagelikes != '':
			Imagelikes = Imagelikes.replace('likes','').replace('like','')
			Imagelikes = Imagelikes.strip()
	
		imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
		likehtml = get_likehtmlforindexpage(str(userupload[uuid]))
		if i == 3 : #664
			if get_cookie("userdatasite"):
				userdata = get_loginsuer()
				userid = userdata[2]
				if int(imageDimension[0]) > int(imageDimension[1]):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#sharepopup">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				elif int(imageDimension[1]) > int(imageDimension[0]):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#sharepopup">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))					
				else:
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#sharepopup">Share</a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))					

			else:
				if int(imageDimension[0]) > int(imageDimension[1]):
					
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder lightbox" href="#myModal1"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i>  <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				elif int(imageDimension[1]) > int(imageDimension[0]):
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder lightbox" href="#myModal1"><span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i>  <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))
				else:
					useruploadshtml1.append(('<div class="images-row single-image "> <div class=" allcompany img-block large"><a class="img-holder lightbox" href="#myModal1"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add btn-share lightbox" href="#myModal1">Share</a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i>  <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div></div>'))

						

			i = 1
		
		else:
			j = j+1
			if i == 1:
				useruploadshtml1.append('<div class="images-row">')
		
			if get_cookie("userdatasite"):
				userdata = get_loginsuer()
				userid = userdata[2]
				if int(imageDimension[0]) > int(imageDimension[1]):
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-w"><img src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))
				elif int(imageDimension[1]) > int(imageDimension[0]):
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-h"><img src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))				
				else:
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))				

			else:
				if int(imageDimension[0]) > int(imageDimension[1]):		
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder lightbox" href="#myModal1"><span class="holder-box-w"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox " href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))
				elif int(imageDimension[1]) > int (imageDimension[0]):
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder lightbox" href="#myModal1"><span class="holder-box-h"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox " href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))
				else:
					useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder lightbox" href="#myModal1"><img style="width:'+imageDimension[0]+'px;" src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#myModal1"><i class="icon-share"></i></a><a class="like-holder lightbox " href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

						

	
			if i == 2:
				useruploadshtml1.append('</div>')
			
			i = i+1			

	
	useruploadshtml = "".join(useruploadshtml1)
	if j %2==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"

	return useruploadshtml



#
# Return html for search results.
# parameter : searchResult => List of images,name=> Search parameter, header=> Need title in html or not
#
def processSearchPageImages(searchResult,name,header=1):			
	useruploadshtml = ''
	uuid= 'uuid'
	useruploadshtml1 = []
	useruploadshtml2 = []
	i=1
	j=0
	for userupload in searchResult:
		userinfo = get_userofimage(str(userupload[uuid]),'fullname')
		userinfo1 = get_userofimage(str(userupload[uuid]),'username')
		Imagelikes = getImagelikesHtml(str(userupload[uuid]))
		likehtml = get_likehtmlforindexpage(str(userupload[uuid]))
		likeForm = get_likeForm(True) 

		imageType = getImageUUID(userupload) #col-sm-6 col-lg-4
		dots = showCharacterLimit(imageType[0],20,'...')
		dots1 = showCharacterLimit(imageType[0],100,'...')
		if Imagelikes != '':
			Imagelikes = Imagelikes.replace('likes','').replace('like','')
			Imagelikes = Imagelikes.strip()
		
		imageDimension = getImageDimension(getImageLocationpath(str(userupload[uuid]))+imageType[2])
		if i == 1:
			useruploadshtml1.append('<div class="images-row four-blocks">')
		if get_cookie("userdatasite"):
			userdata = get_loginsuer()
			userid = userdata[2]
			if int(imageDimension[0]) > int(imageDimension[1]):
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-w"><img  src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			elif int(imageDimension[1]) > int(imageDimension[0]):
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><span class="holder-box-h"><img  src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></span></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
			else:
				useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img  src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share lightbox" href="#sharepopup"><i class="icon-share"></i></a>'+likehtml+'<span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><input type="hidden" id="full_image_name" value="'+dots1+'"/><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div>'+likeForm+'</div>'))
		else:
			useruploadshtml1.append(('<div class=" allcompany img-block"><a class="img-holder" href="'+SITEURL+'image/'+str(userupload[uuid])+'"><img  src="'+SITEURL+''+getImageLocationpath(str(userupload[uuid]))+imageType[2]+'" /></a><div class="info"><div class="info-holder"><a class="btn btn-add icone-share" href="#"><i class="icon-share"></i></a><a class="like-holder lightbox" href="#myModal1"><span class="icone-like"><i class="icon-heart"></i> <i class="icon-heart2"></i></span><span class="quantity">'+Imagelikes+'</span></a></div><div class="img-caption"><strong>'+dots+'</strong><p>By: <a href="'+userinfo1+'">'+userinfo+'</a></p></div></div></div>'))

				
		if i == 4:
			j=j+1
			useruploadshtml1.append('</div>')
		i = i+1		
		if i == 5:
			i = 1
				
	useruploadshtml = "".join(useruploadshtml1)
	if j%4==0:
		i=1
	else:
		useruploadshtml = useruploadshtml + "</div>"
	return useruploadshtml


#
# Add slashes in string.
# parameter : s => String
#
def addslashes(s):
    s = encodeCharAt(s)
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s

#
# Return the List of recent activity of login user.
#
def recentActivity():
	userdata = get_loginsuer()
	userid = userdata[2]
	userinfo = getUserByID(userid)
	username = userinfo[0]['username']
	if userinfo[0]['fullname'] is not None:
		username = userinfo[0]['fullname']
	#image liked Start
	queryTerm = "SELECT a.imageuid,a.createdAt,b.original_image_URL,b.uuid,b.original_image_title FROM `image_like` a INNER JOIN `filenames` b on a.imageuid = b.uuid where   a.`userid`='{0}' order by a.`createdAt` DESC limit 0,10  ".format(userid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecordLike = '<h2>Picture Liked</h2><hr>'
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		for record in totalRecords1:
			imageType = getImageUUID(record)
			totalRecordLike = totalRecordLike + '<p>'+username+' liked image '+(record['original_image_URL'])+' <a href="'+SITEURL+'image/'+str(record['uuid'])+'" ><img id="'+str(record['uuid'])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(record['uuid']))+imageType[2]+'" class="randompic"></a></p><hr>'
	#image liked End
	#image added Start
	queryTerm = "SELECT a.createdAt,b.original_image_URL,b.uuid,b.original_image_title FROM `user_filenames` a INNER JOIN `filenames` b on a.uuid = b.uuid where   a.`userid`='{0}' order by a.`createdAt` DESC limit 0,10  ".format(userid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecordAdded = '<h2>Picture Added.</h2><hr>'
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		for record in totalRecords1:
			imageType = getImageUUID(record)
			totalRecordAdded = totalRecordAdded + '<p>'+username+' added image '+ (record['original_image_URL'])+' <a href="'+SITEURL+'image/'+str(record['uuid'])+'" ><img id="'+str(record['uuid'])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(record['uuid']))+imageType[2]+'" class="randompic"></a></p><hr>'
	#image added End
	#image identified Start
	queryTerm = "SELECT a.createdAt,b.original_image_URL,b.uuid,b.original_image_title,c.attribute_name,c.attribute_type FROM `user_images_attributes` a INNER JOIN `image_attributes` c on c.index = a.attributeid INNER JOIN `filenames` b on a.uuid = b.uuid  where   a.`userid`='{0}' order by a.`createdAt` DESC limit 0,10  ".format(userid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecordidentified = '<h2>Picture Identified</h2><hr>'
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		for record in totalRecords1:
			imageType = getImageUUID(record)
			totalRecordidentified = totalRecordidentified + '<p>'+username+' identified image '+(record['original_image_URL'])+' as "'+(record['attribute_type'])+' : '+ (record['attribute_name'])+'" <a href="'+SITEURL+'image/'+str(record['uuid'])+'" ><img id="'+str(record['uuid'])+'" src="'+SITEURL+'imagethumb.py?img='+getImageLocationpath(str(record['uuid']))+imageType[2]+'" class="randompic"></a></p><hr>'
	#image identified End
	
	return (totalRecordLike) + (totalRecordAdded) + (totalRecordidentified)
#
# Return the List of popular images.
# parameter : start => Start count , count => Number images to display
#	
def popular(start,count):
	#image liked Start
	queryTerm = "select DISTINCT tbl.uuid, tbl.original_image_URL,tbl.uuid,tbl.original_image_title from ((SELECT b.original_image_URL,b.uuid,b.original_image_title,COUNT(a.`imageuid`) as cnt FROM `image_like` a INNER JOIN `filenames` b on a.imageuid = b.uuid  WHERE a.createdAt > NOW() - INTERVAL 1 MONTH and b.status=1 GROUP BY a.`imageuid` ) union  (SELECT b.original_image_URL,b.uuid,b.original_image_title,COUNT(a.`imageuid`) as cnt FROM `image_like` a INNER JOIN `filenames` b on a.imageuid = b.uuid  WHERE b.status=1 GROUP BY a.`imageuid`  ))  as tbl order by tbl.cnt DESC limit {0},{1} ".format(start,count)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	totalRecords4 = 0
	if totalRecords < count:
		if totalRecords == 0:
			queryTerm = "select count(*) as count from ((SELECT b.original_image_URL,b.uuid,b.original_image_title FROM `image_like` a INNER JOIN `filenames` b on a.imageuid = b.uuid  WHERE a.createdAt > NOW() - INTERVAL 1 MONTH and b.status=1 GROUP BY a.`imageuid`) union  (SELECT b.original_image_URL,b.uuid,b.original_image_title FROM `image_like` a INNER JOIN `filenames` b on a.imageuid = b.uuid  WHERE b.status=1 GROUP BY a.`imageuid` )) as tbl;"
			curs1 = conn.cursor(oursql.DictCursor)
			curs1.execute(queryTerm)
			totalRecords2 = curs1.fetchall()
			curs1.close()
			totalRecordsc =  int(totalRecords2[0]['count'])
			starts = start - totalRecordsc
			counts = count
		else:
			starts = 0
			counts = count - totalRecords
		queryTerm = "SELECT b.original_image_URL,b.uuid,b.original_image_title FROM `image_like` a Right  JOIN `filenames` b on a.imageuid = b.uuid  WHERE b.status=1 and a.imageuid is null  limit {0},{1} ".format(starts,counts)
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords3 = curs1.fetchall()
		curs1.close()
		totalRecords4 = len(totalRecords3)
	
	if totalRecords > 0:
		if totalRecords4 > 0:
			return processSearchImages(totalRecords1+totalRecords3,'',0)
		else:
			return processSearchImages(totalRecords1,'',0)
	else:
		if totalRecords4 > 0:
			return processSearchImages(totalRecords3,'',0)
		else:
			return ''
		
#
# Return the List of latest images.
# parameter : start => Start count , count => Number images to display
#	
def latest(start,count):
	#image liked Start
	queryTerm = "SELECT b.original_image_URL,b.uuid,b.original_image_title FROM `filenames` b where b.status=1 order by b.index DESC limit {0},{1} ".format(start,count)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return processSearchImages(totalRecords1,'',0)
	else:
		return ''

#
# Return the List of following images of login user.
# parameter : start => Start count , count => Number images to display
#
def following(start,count):
	if get_cookie("userdatasite"):
		#image liked Start
		userdata = get_loginsuer()
		userid = userdata[2]
		followinglist = getFollowingList(userid)
		userarr1 = '0'
		if followinglist != '':
			userarr = []
			for followinglist1 in followinglist:
				userarr.append(str(followinglist1['id']))
			userarr1 = ",".join(userarr)
		queryTerm = "SELECT b.original_image_URL,b.uuid,b.original_image_title FROM `filenames` as b INNER JOIN `user_filenames` AS a  on b.`uuid` = a.`uuid`  where b.status=1 and a.userid in ({2}) order by b.index DESC limit {0},{1} ".format(start,count,str(userarr1))
		curs1 = conn.cursor(oursql.DictCursor)
		curs1.execute(queryTerm)
		totalRecords1 = curs1.fetchall()
		curs1.close()
		totalRecords = len(totalRecords1)
		if totalRecords > 0:
			return processSearchImages(totalRecords1,'',0)
		else:
			return ''
	else:
		return 'Need to login.'
#
# Return the List of needshelp images.
# parameter : start => Start count , count => Number images to display
#
def needshelp(start,count):
	#image liked Start
	queryTerm = "SELECT r3.original_image_title,r3.uuid,r3.original_image_URL,count(r1.uuid) as itemCount FROM `filenames` as r3 LEFT JOIN `image_attributes` AS r1  on r1.`uuid` = r3.`uuid` WHERE r3.`status` = 1 and r1.status =1 group by r1.uuid having itemCount <= 1  limit {0},{1} ".format(start,count)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return processSearchImages(totalRecords1,'',0)
	else:
		return ''

#
# Insert the info of user invitation.
# parameter : useremail => User email to whom invitation sent , userid => User id (who is sending invitation)
#
def insert_invitation(useremail,userid):
	queryTerm = "Insert into `user_referrals` SET userid='{1}',referalemail='{0}',status='0',`createdAt` = NOW() ".format(useremail,userid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	lastid = curs1.lastrowid
	curs1.close()
	if lastid :
		return True  # generate HTTP headers
	else:
		return False

#
# Update the info of user invitation.
# parameter : useremail => User email to whom invitation sent
#
def update_invitation(useremail):
	queryTerm = "update `user_referrals` SET status='1' where referalemail='{0}' ".format(useremail)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	lastid = curs1.lastrowid
	curs1.close()

#
# Check whether email already exist in DB or not.
# parameter : email => User email to whom invitation need to sent
#
def checkuser_invitation(email):
	queryTerm = "SELECT userid as id from `user_referrals` where referalemail='{0}' UNION SELECT id FROM `users`  where useremail='{0}' ".format(email)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return True  
	else:
		return False

#
# Return the array of user to whom invitation sent and not sent.
# parameter : useremail => User email to whom invitation sent , userid => User id (who is sending invitation)
#
def update_sendinvite(useremail,userid):
	emailsent = []
	emailtosent = []
	if ',' in useremail:
		emails = useremail.split(',')
	else:
		emails = [useremail]

	for email in emails:
		checkemail = checkuser_invitation(email)
		if checkemail:
			emailsent.append(email)
		else:
			emailtosent.append(email)
			insert_invitation(email,userid)
	return [emailsent,emailtosent]

def getCategory():
	queryTerm = "SELECT * FROM `categories` where `status` = 1 ORDER BY `categories`.`name` ASC "
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1  
	else:
		return False

def getCategoryById(id):
	queryTerm = "SELECT * FROM `categories` where `id` = {0}".format(id)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1  
	else:
		return False

def getSubCategory(pid):
	queryTerm = "SELECT * FROM `sub_categories` where `status` = 1 and `pid` ='{0}' ORDER BY  `name` ASC".format(pid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1  
	else:
		return False

def getSubCategoryById(id):
	queryTerm = "SELECT * FROM `sub_categories` where `id` = {0}".format(id)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1  
	else:
		return False

def processCategoryHtml():
	searchResult = getCategory()
	categoryhtml = ''
	categoryhtmlli = ''
	if searchResult:
		categoryhtml1 = []
		categoryhtml2 = []
		i=1
		for category in searchResult:
			categoryChildhtml = ''
			categoryChild= getSubCategory(category['id'])
			
			if categoryChild:
				categoryChildhtml1 = []
				for categoryChild1 in categoryChild:
					categoryChildhtml1.append('<li><a href="#'+str(categoryChild1['id'])+'">{0}</a></li>'.format(categoryChild1['name'].encode('utf-8')))
				#~ categoryChildhtml = "".join(categoryChildhtml1)
				categoryChildhtml = '<ul class="drop '+category['name'].encode('utf-8')	+'"><li><ul class="drop-in drop-'+str(i)+'-in">'+categoryChildhtml+'</ul></li></ul>'
				categoryhtml2.append(categoryChildhtml)
			categoryhtml1.append('<li id="'+category['name'].encode('utf-8')+'" ><a href="#'+str(category['id'])+'">{0}</a>{1}</li>'.format(category['name'],''))
			i=i+1
		categoryhtmlli = "".join(categoryhtml1)
		categoryhtmlli1 = "".join(categoryhtml2)
		#~ categoryhtml2 = '<div class="drop-left"><ul id="uni-ids">'+categoryhtmlli+'</ul></div>'+categoryhtmlli1
		categoryhtml2 = '<ul>'+categoryhtmlli+'</ul>'+categoryhtmlli1
		
	return categoryhtml2.decode('utf-8')

def processCategoryHtml1():
	searchResult = getCategory()
	categorylist = ''
	categorysublist = ''
	if searchResult:
		categorylist1 = []
		for category in searchResult:
			categorysublist2 = []
			list_subcategory= getSubCategory(category['id'])
			for subcat_items in list_subcategory:
				categorysublist2.append('<li id="'+str(subcat_items['id'])+'"> <a href="'+str(subcat_items['id'])+'" >'+subcat_items['name']+'</a>')
				categorysublist = "".join(categorysublist2)
			#~ categorylist1.append('<li class="main_cat" id="'+category['name'].encode('utf-8')+'" ><a href="#'+str(category['id'])+'">'+category['name']+'</a><ul class="insideit">'+categorysublist+'</ul></li>')
			categorylist1.append('<li class="main_cat" id="'+category['name'].encode('utf-8')+'" ><a href="#'+str(category['id'])+'">'+category['name']+'</a></li>')
		categorylist = "".join(categorylist1)
		listElements = '<ul>'+categorylist+'</ul>'		
	return listElements.decode('utf-8')

def getImageByName(name):
	queryTerm = "SELECT uuid,imagename FROM `imageindex` WHERE `name` LIKE '{0}' limit 1".format(addslashes(name))
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		uuid = totalRecords1[0]['imagename']  
		dir = "images/"
		first = uuid[0]+"/"
		second = uuid[1]+"/"	
		third = uuid[2]+"/"
		if getbucketImage(totalRecords1[0]['imagename']) : 
			return ['http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + totalRecords1[0]['imagename'],totalRecords1[0]['uuid']]
		else: 
			return False 
		if os.path.isfile(str(dir+first+second+third) + totalRecords1[0]['imagename']): #check if image exits in thumbs
			return [SITEURL+ str(dir+first+second+third) + totalRecords1[0]['imagename'],totalRecords1[0]['uuid']]  
		else: 
			return False
	else:
		return False

def getImageByUuid(uuid):
	queryTerm = "SELECT * FROM `imageindex` WHERE `uuid` = '{0}' limit 1".format(uuid)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1
	else:
		return False

#
# Search database for the record at the index value specified
#
def getNameAttribute(indexValue):
	queryTerm = "SELECT uuid FROM `imageindex` WHERE `name` = '{0}' ".format(indexValue)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return True  
	else:
		return False


#
# Profile visibilty for user
#
def Profilevisibilty():
	queryTerm = "SELECT userid FROM `setting_preferences` WHERE `profilevisibility` = 'onlyyou' "
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	list1 = []
	for vs in totalRecords1:
		vs1 = vs
		list1.append(vs1)
		
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return list1  
	else:
		return ''





def getbucketImage(imagename):
		first = imagename[0]+"/"
		second = imagename[1]+"/"	
		#https://s3-us-west-2.amazonaws.com/luxradarimages/Images/0/0/00006dd29c.jpg
		imageurl = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + imagename
		import urllib2
		try:
			data = urllib2.urlopen(imageurl).read()
		except Exception as e:
			return False
		if '<Error>' in data:
			return False
		else:
			return imageurl

#
# get value of setting-prefrences page
#

def get_settingspreferences(uid):
	queryTerm = 'SELECT * FROM `setting_preferences` WHERE `userid` =' +str(uid)+'  '
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1  
	elif totalRecords == None:
		pass
#
# get current password
#
def get_currentpassword(uid):
	queryTerm = 'SELECT password FROM `users` WHERE `id` =' +str(uid)+' and status=1'
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return totalRecords1

#
# function to encode the password during update password
#
def get_encode(val):
	h = hashlib.new('ripemd160')
	h.update(val)
	userpwd = h.hexdigest()
	return userpwd

#
# get email id by username
#	
def get_useremail(username):
	queryTerm = "SELECT useremail FROM `users` WHERE `username` ='{0}' and status=1".format(username)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	totalRecords1 = curs1.fetchall()
	curs1.close()
	for email in totalRecords1:
		email1 = email['useremail']
	totalRecords = len(totalRecords1)
	if totalRecords > 0:
		return email1  
	else:
		return ""

	
	
