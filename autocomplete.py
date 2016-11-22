#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
import json

# MAIN
#
# Page to display the search hints in dropdown with ajax. 
#

#
# Search database for the list of attributes associated with the passed attribute value
#	
def getImageAttributesAll(part):
	queryTerm = "SELECT `name`, `pcat`, `psubcat`, `uuid`, `orignalurl`, `description`, `imagename` FROM `imageindex` WHERE status=1 and name LIKE '{0}%' GROUP BY `name` ORDER BY `name` limit 0,4".format(part)
	curs.execute(queryTerm)
	return curs.fetchall()

def gettotalcount(attribute_name):
	totalRecordsc = 0
	queryTerm1 = 'select count(*) as count  from (SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name` like "{0}%"   group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1  WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and r1.`attribute_name_reverse` like reverse("%{0}") group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL like "{0}%" group by r3.`uuid` UNION SELECT r3.original_image_title,r3.uuid,r3.original_image_URL FROM `filenames` as r3 INNER JOIN `image_attributes` AS r1   WHERE r1.`uuid` = r3.`uuid` and r3.`status` in (1) and r1.status in (1) and  r3.original_image_URL_rev like reverse("%{0}") group by r3.`uuid` ) as r2;'.format(attribute_name)
	curs1 = conn.cursor(oursql.DictCursor)
	curs1.execute((queryTerm1))
	totalRecords2 = curs1.fetchall()
	curs1.close()
	totalRecords = len(totalRecords2)
	if totalRecords > 0:
		totalRecordsc =  (totalRecords2[0]['count'])
	return totalRecordsc
#
# The list of attributes associated with the passed attribute_name
#	
def getSelectType(part):
	dict = getImageAttributesAll(part) #get all attributes form DB.
	i = 0
	htmldiv=[]
	totalRecordsc = gettotalcount(part)
	for i in range (len(dict)):
		htmldiv1={}
		htmldiv1['name'] = str(dict[i]['name'].encode( "utf-8" ))
		htmldiv1['uuid'] = str(dict[i]['uuid'])
		htmldiv1['imagename'] = str(dict[i]['imagename'])
		first = htmldiv1['uuid'][0]+"/"
		second =htmldiv1['uuid'][1]+"/"	
		if getbucketImage(dict[i]['imagename']): 
			imagepath = 'http://s3-us-west-2.amazonaws.com/luxradarimages/Images/'+ str(first+second) + dict[i]['imagename']
		else: 
			imagepath =  dict[i]['orignalurl']
		description = showCharacterLimit(dict[i]['description'],60,'...')
		htmldiv1['imagepath'] = str(imagepath)
		htmldiv1['description'] = (description)
		category = getSubCategoryById(dict[i]['psubcat'])
		htmldiv1['category'] = category[0]['name']
		htmldiv1['count'] = totalRecordsc
		htmldiv.append(htmldiv1)
		i = i + 1
	return json.dumps(htmldiv) #return response in json format

form = cgi.FieldStorage() #Fetch the form data if any by get or post

if "term" not in form: #check if term (serach input name) in Post parameters for ajax pagination
	output('not in action')
else:
	finalhtml = getSelectType(form.getvalue("term"))
	output(finalhtml)
