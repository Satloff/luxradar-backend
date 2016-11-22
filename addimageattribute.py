#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
import json
import urllib2
import uuid
form = cgi.FieldStorage() #Fetch the form data if any by get or post
if "categoryname" in form: #if image uuid exits in form parameters
	category = getCategory()
	if category:
		finalresponse = category
	else:
		finalresponse = []
elif "categoryid" in form:
	category = getSubCategory(form.getvalue('categoryid'))
	if category:
		finalresponse = category
	else:
		finalresponse = []


elif "namevalue1" in form:
	namevalue1 = form.getvalue('namevalue1')
	imuuid = form.getvalue('imuuid')
	queryTerm = "Insert into `image_attributes` SET  `attribute_type`='{0}',`attribute_name`='{1}',`uuid`='{2}',`status`='{3}'".format(addslashes(namevalue1),addslashes(namevalue1),imuuid,'1')
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute(queryTerm)
	finalresponse = ['1','Image Tagged with Attribute.',imuuid]


elif "namevalue" in form:
	uuid1 = form.getvalue('uuid')
	#uuid1 = str(uuid.uuid4()).split('-')[-1] #get random number
	namevalue = form.getvalue('namevalue')
	attributecategory = form.getvalue('attributecategoryy')
	attributesubcategory = form.getvalue('attributesubcategoryy')
	imgurl = form.getvalue('imgurl')
	attributedesc = form.getvalue('attributedesc')
	checkname = getNameAttribute(addslashes(namevalue))
	if checkname:
		finalresponse = ['0','Attribute name Exits.',uuid1]
	else:
		if uuid1 == '0':
			uuid2 = uuid.uuid4()
			uuid3 = str(uuid2).split('-')
			uuid1 = uuid3[-1]
	 		imgext = imgurl.split('.')
			imagename = str(uuid1)+'.'+imgext[-1]
			queryTerm = "INSERT INTO `imageindex`(`name`, `pcat`, `psubcat`, `uuid`, `orignalurl`, `description`, `imagename`, `spots`, `links`, `status`) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','0','0',1)".format(addslashes(namevalue),attributecategory,attributesubcategory,uuid1,addslashes(imgurl),addslashes(attributedesc),addslashes(imagename))
			curs1 = conn.cursor(oursql.DictCursor)
			curs1.execute(queryTerm)
			
			userdata = get_loginsuer()
			queryTerm1 = "Insert into `user_images_attributes` SET  `userid`='{0}',`uuid`='{1}',`attributeid`='{2}'".format(userdata[2],uuid1,curs1.lastrowid)
			#queryTerm1 = "Insert into `user_images_attributes` SET  `userid`='{0}',`uuid`='{1}'".format(userdata[2],uuid1)
			curs1.execute(queryTerm1)
			curs1.close()
			link = SITEURL+"imageUpload.py?uuid="+uuid1+"&filename="+imagename+"&imageurl="+imgurl
			page=urllib2.urlopen(link)
			finalresponse = ['1','Attribute Added.',str(uuid1)]
		else:
			imgext = imgurl.split('.')
			imageuuid = uuid1
			uuid1 = str(uuid.uuid4()).split('-')[-1] #get random number
			imagename = uuid1+'.'+imgext[-1]
			queryTerm = "INSERT INTO `imageindex`(`name`, `pcat`, `psubcat`, `uuid`, `orignalurl`, `description`, `imagename`, `spots`, `links`, `status`) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','0','0',1)".format(addslashes(namevalue),attributecategory,attributesubcategory,uuid1,addslashes(imgurl),addslashes(attributedesc),addslashes(imagename))
			curs1 = conn.cursor(oursql.DictCursor)
			curs1.execute(queryTerm)
			curs1.close()
			curs1 = conn.cursor(oursql.DictCursor)
			queryTerm = "Insert into `image_attributes` SET  `attribute_type`='{0}',`attribute_name`='{1}',`uuid`='{2}',`status`='{3}'".format(addslashes(namevalue),addslashes(namevalue),imageuuid,'1')
			curs1.execute(queryTerm)
			curs1.close()
			
			userdata = get_loginsuer()
			queryTerm1 = "Insert into `user_images_attributes` SET  `userid`='{0}',`uuid`='{1}',`attributeid`='{2}'".format(userdata[2],imageuuid,curs1.lastrowid)
			curs1 = conn.cursor(oursql.DictCursor)
			curs1.execute(queryTerm1)
			curs1.close()
			link = SITEURL+"imageUpload.py?uuid="+uuid1+"&filename="+imagename+"&imageurl="+imgurl
			page=urllib2.urlopen(link)
			finalresponse = ['1','Attribute Added.',uuid1]
else:
	finalresponse = []

output(json.dumps(finalresponse))
