#!/usr/bin/python
# -*- coding: utf-8 -*-
from config import *
from function import *
import datetime

# MAIN
#
# Display Profile page of user. 
#


start=0
limit = 6
form = cgi.FieldStorage() #Fetch the form data if any by get or post
if get_cookie("userdatasite"): #Check user logined or not 
	if "namesearch" in form:
		start = form.getvalue("start")
		name = form.getvalue("namesearch")
		userid = form.getvalue('userid')
		if name == 'useridentified':
			userimages = get_useridentify(str(userid),start,limit) #get images identify by user
			imageuid = 'uuid'
		elif  name == 'useradded':
			userimages = get_useruploads(str(userid),start,limit) #get images uploaded by user
			imageuid = 'uuid'
		elif  name == 'userliked':
			userimages = get_userLiked(str(userid),start,limit) #get images Liked by user
			imageuid = 'imageuid'
		elif name == 'ownit':
			userimages = get_ownit(str(userid),start,limit) #get images owned by user
			imageuid = 'uuid'
		elif name == 'attributeliked':
			userimages = get_userLikedattribute(str(userid),start,limit) #get images Liked by user
			#userimages = get_attribute_imagename(userimagesdata) #get images Liked by user
			imageuid = 'uuid'		
			
		else:
			userimages = ''
		html = 'No more images'
		linkhtml = ''
		if len(userimages) >= limit:
			linkhtml = '<nav><a class="load-link" href="'+SITEURL+'profile.py?userid='+str(userid)+'&namesearch='+name+'&start='+str(int(start)+limit)+'"></a></nav>'
		if userimages != '':
			if name == 'attributeliked':
				html = ProcessProfileAttributeImages(userimages,imageuid) #process images and return html
			elif name =='ownit':
				html = ProcessProfileOwnitImages(userimages,imageuid) #process images and return html
			elif name == 'useridentified':
				html = ProcessProfileIdentifiedImages(userimages,imageuid) #process images and return html

			else:			
				html = processAttributerelatedImages(userimages,imageuid) #process images and return html		
		html = encodeCharAt(html+linkhtml) #Encode special Charaters 
		output(html)
		sys.exit();




	if "username" in form: #if username exist in form parameters
		
		headerhtml  = headerReturn() #call header function
		topFile = headerhtml[0] #header html
		bottomFile= headerhtml[1] #Footer html
		finalhtml = getUserByUsername(form.getvalue('username')) #get user info by username
		start=0
		limit = 6 #limit to display images of user liked
		#for ajax pagination of user images
		
		if "name" in form : #if name exist in form parameters
			html = ''
			userimages=''
			name = form.getvalue("name")
			if form.getvalue("pageid") is None: #if pageid  exist in form parameters
				pageid = 1
				start = 0
			else:
				pageid = int(form.getvalue("pageid"))
				start = (int(pageid) - 1) * limit
				
			if "start" in form:
				start = int(form.getvalue("start"))
				pageid = int(start/limit) 
				
			if name == 'useridentified':
				userimages = get_useridentify(str(finalhtml[0]['id']),start,limit) #get images identify by user
				imageuid = 'uuid'
			elif  name == 'useradded':
				userimages = get_useruploads(str(finalhtml[0]['id']),start,limit) #get images uploaded by user
				imageuid = 'uuid'
			elif  name == 'userliked':
				userimages = get_userLiked(str(finalhtml[0]['id']),start,limit) #get images Liked by user
				imageuid = 'imageuid'
			elif name == 'ownit':
				userimages = get_ownit(str(finalhtml[0]['id']),start,limit) #get images owned by user
				imageuid = 'imageid'
			elif  name == 'attributeliked':
				userimages = get_userLikedattribute(str(userid),start,limit) #get images Liked by user
				#userimages = get_attribute_imagename(userimagesdata) #get images Liked by user
				imageuid = 'attributeid'		
			else:
				userimages = ''			
			
			if userimages != '':
				html = processUserProfilePageimages(userimages,imageuid,'') #process images and return html
				
			if html != '':
				html = html+'<a class="endless_more_1">&nbsp;</a>' #for ajax pagination
			else:
				html = ''
		else: #for default profile page 
			html = ''
			loginuser = 'style="display:none;"'
			followme = ''
			follower = '0'
			following = '0'
			if get_cookie("userdatasite"): #Check user logined or not 
				userdata = headerhtml[2] #User cookie data html
				userdata1 = headerhtml[3] #User full data html
				if len(finalhtml) > 0:
					#follow me form 
					followme = """<a  class="btn btn-follow" onclick="formSubmit('#form-followme');">--followmemage--</a>
										<form method="post" action="--SITEURL--login.py" id="form-followme">
										<input type="hidden" value="--userid--"  name="userid">
										<input type="hidden" value="--followme--"  name="followme">
										<input type="hidden" value="true" name="reload">
										<input type="hidden" value="followme" name="action">
									</form>"""
					chk = isFollowing(str(userdata1[0]['id']),str(finalhtml[0]['id'])) #check whether logined user is following or not
					if chk:
						followmemage =  'Unfollow'
					else:
						followmemage =  'Follow'

					followme = followme.replace('--userid--',str(userdata1[0]['id'])).replace('--followme--',str(finalhtml[0]['id'])).replace('--followmemage--',followmemage)
					if userdata1[0]['id'] == finalhtml[0]['id']:
						loginuser = ''
						followme = ''
			#Parse all varible to template to give html output
			html = html + topFile.replace("--serachType--",'').replace("--SITEURL--",SITEURL).replace("--imagename--",'').replace("--imageid--",'')
			bottomFile = bottomFile.replace("--imageid--",'')
			
			if len(finalhtml) > 0:
				following = getFollowing(str(finalhtml[0]['id'])) #get count of following user
				follower = getFollower(str(finalhtml[0]['id'])) #get count of follower
				followinglist = getFollowingList(str(finalhtml[0]['id'])) #get list of following user
				followerlist = getFollowerList(str(finalhtml[0]['id'])) #get list of follower
				followerlisthtml =''
				followinglisthtml=''			
				#Html for follower list
				if followerlist != '':
					follower = str(follower)
					followerlisthtml = '<ul class="followers-pop">'
					for followerlist1 in followerlist:
						if followerlist1['fullname'] is None:
							
							followerlist1['fullname'] = followerlist1['username']
					
						followerspic = get_userprofile(str(followerlist1['id'])) #get followers profile pictures
						followerprofilepic1 = followerspic[0]['profilepic']
						
						if followerprofilepic1 == None:
							followerprofilepic ="defualtprofile.jpg"
						else:
							followerprofilepic = followerprofilepic1
							
						followerlisthtml = followerlisthtml + '<li> <div class="item"> <div class="item-frame"> <a href="#" class="img-right"> <img src="--SITEURL--images/userimages/'+str(followerprofilepic)+'" height="75" width="75" alt="Image description"> </a> </div>  <div class="item-holder"> <a href="'+SITEURL+followerlist1['username']+'" title="View profile" target="_blank" >'+followerlist1['fullname']+'</a> <p>Luxradar</p> </div></div></li>'
					followerlisthtml = followerlisthtml + '</ul>'
				#Html for followin list	
				if followinglist != '':
					following = str(following)
					followinglisthtml = '<ul class="followers-pop">'
					for followinglist1 in followinglist:
						if followinglist1['fullname'] is None:
							followinglist1['fullname'] = followinglist1['username']
						
						followingpic = get_userprofile(str(followinglist1['id']))
						followingprofilepic1 = followingpic[0]['profilepic']	
						if followingprofilepic1 == None:
							followingprofilepic ="defualtprofile.jpg"
						else:
							followingprofilepic = followingprofilepic1
							
						followinglisthtml = followinglisthtml + '<li><div class="item"> <div class="item-frame"> <a href="#" class="img-right"> <img src="--SITEURL--images/userimages/'+str(followingprofilepic)+'" height="75" width="75" alt="Image description"> </a> </div>  <div class="item-holder"> <a href="'+SITEURL+followinglist1['username']+'" title="View profile" target="_blank">'+followinglist1['fullname']+'</a> <p>Luxradar</p> </div></div></li>'
					followinglisthtml = followinglisthtml + '</ul>'

				#User created at and updated profile
				if finalhtml[0]['createdAt'] is not None:
					d = datetime.datetime.strptime(str(finalhtml[0]['createdAt']), "%Y-%m-%d %H:%M:%S")
					#~ d1 = datetime.datetime.strptime(str(finalhtml[0]['updatedAt']), "%Y-%m-%d %H:%M:%S")
					time1= d.strftime("%B %d, %Y")
					#~ time2= d1.strftime(" On %B %d, %Y at %I:%M %p")
				else:
					time1= ''
					
				finalhtml1 = Read_File("profilepage.html") #read profile template
				userprofile = get_userprofile(str(finalhtml[0]['id'])) #get user profile data
				totalRecords = len(userprofile)
				
				if totalRecords != 0: #check if user have profile data
					website = CheckNone(userprofile[0]['website'])
					location = CheckNone(userprofile[0]['location'])
					about = CheckNone(userprofile[0]['about'])
					birthdate = CheckNone(userprofile[0]['birthdate'])
					gender = CheckNone(userprofile[0]['gender'])
					twitter = CheckNone(userprofile[0]['twitter'])
					facebook = CheckNone(userprofile[0]['facebook'])
					instagram = CheckNone(userprofile[0]['instagram'])
					featuredimg = CheckNone(userprofile[0]['featuredimg'])
					websitetext = website.replace("http://www.",'').replace("/",' ')
					google = CheckNone(userprofile[0]['google'])
					#user Profile pic Default if not exists
					if userprofile[0]['profilepic'] is None or userprofile[0]['profilepic'] == '':
						profilepic = 'defualtprofile.jpg'
					else:
						profilepic = userprofile[0]['profilepic']
					if featuredimg is None or featuredimg == '':
						featuredimgsrc = getImageLocationpath(str('c43e32be8a'))+'.jpg'
						imageUUID = 'c43e32be8a'
						fimg_dim = (getImageDimension(featuredimgsrc))
						if int(fimg_dim[0])>int(fimg_dim[1]):
							add_span = '<span class="holder-box-w">'
						elif int(fimg_dim[0])<int(fimg_dim[1]):
							add_span = '<span class="holder-box-h">'
					else:
						featuredimg1 = featuredimg.split('.')
						featuredimgsrc = getImageLocationpath(str(featuredimg1[0]))+'.'+featuredimg1[1]
						imageUUID = str(featuredimg1[0])
						fimg_dim = (getImageDimension(featuredimgsrc))
						if int(fimg_dim[0])>int(fimg_dim[1]):
							add_span = '<span class="holder-box-w">'
						elif int(fimg_dim[0])<int(fimg_dim[1]):
							add_span = '<span class="holder-box-h">'

				else:
					website = 'javascript:;'
					location = ''
					about = ''
					twitter = 'javascript:;'
					facebook = 'javascript:;'
					instagram = 'javascript:;'
					google = 'javascript:;'
					profilepic = 'defualtprofile.jpg'
					websitetext = ''
					featuredimgsrc = getImageLocation(str('c43e32be8a'))+'.jpg'
					imageUUID = 'c43e32be8a'
					
				imageAttributes = getImageAttributes(str(imageUUID), curs) #get attributes of featured image
				attributesList = unpackImageAttributes(imageAttributes) #unpack attributes of featured image
				record = getImageInfoFromUUIDAll(imageUUID, curs) #get info of featured image
				imageUUID1 = getImageUUID(record)
				profilephoto = SITEURL+'images/userimages/'+profilepic
				featuredlike = get_likehtmlforimage(imageUUID)
				userinfo =get_userofimage(str(imageUUID),'fullname') #Get User fullname
				userinfo1 =get_userofimage(str(imageUUID),'username')
				featureImagelikes = getImagelikes(str(imageUUID)) #Get Likes of feature image on profile page
				likeForm = get_likeForm(True)
				likeimage = '<div align="center" class="col-md-10">--likebtn--'+likeForm+'</div>'
				likeimage = str(likeimage).replace("--userid--",str(userdata[2]))
				#get Like button for image
				likebtn = get_likehtmlforimage(str(imageUUID))
				likedimage1 = str(likeimage).replace("--likebtn--",str(likebtn)).replace('--Imagelikes--',featureImagelikes)
				#*****************************************************
				visibilty1 = Profilevisibilty()
						
				private_profile_access = ''
				
				for vis in visibilty1:
					visibilty2 = vis['userid']
					
					profile_url_username = getUserByUsername(form.getvalue('username'))
					chek_user = str(profile_url_username[0]['id'])
												
					if (str(userdata[2])) == str(chek_user):			
						profile_access = "you can see"
					
					else:
						if (str(chek_user) == str(visibilty2)):
							private_profile_access = "This user is private"
						else:
							public_profile_access = "public user"
						
								

						
				#Parse all varible to template to give html output
				finalhtml1 = finalhtml1.replace('--followerlist--',str(followerlisthtml)).replace('--likedimage1--',str(likedimage1)).replace('--userinfo1--',str(userinfo1)).replace('--userinfo--',str(userinfo)).replace('--followinglist--',str(followinglisthtml)).replace('--follower--',str(follower)).replace('--following--',str(following)).replace('--followme--',str(followme)).replace('--featuredlike--',featuredlike).replace('--imagepath--',featuredimgsrc).replace('--websitetext--',websitetext).replace('--fullname--',str(finalhtml[0]['fullname'])).replace('--profilepic--',profilephoto).replace('--location--',location).replace('--website--',website).replace('--about--',about).replace('--twitter--',twitter).replace('--facebook--',facebook).replace('--google--',google).replace('--instagram--',instagram).replace('--loginuser--',loginuser).replace('--SITEURL--',SITEURL).replace('--STATICURL--',STATICURL).replace("--imagename--",str(imageUUID1[0])).replace("--imageattr--",printAttributesList(attributesList)).replace("--imagefid--",str(imageUUID)).replace("--private_profile_access--",private_profile_access).replace("--fdim_w--",fimg_dim[0]).replace("--fdim_h--",fimg_dim[1]).replace("--fimg_dim--",str(fimg_dim)).replace("--add_span--",add_span)
				
				
				#get list of user images uploaded, identified and liked
				 
				useruploads = get_useruploads(str(finalhtml[0]['id'])) #image uploaded by user 
				useridentify = get_useridentify(str(finalhtml[0]['id'])) #image identified by user
				attributeuserliked = get_userLikedattribute(str(finalhtml[0]['id'])) #image attribute liked by user
				ownit = get_ownit(str(finalhtml[0]['id'])) #images owned by user
				#~ attributeuserliked = get_attribute_imagename(attributeuserliked1) #image attribute liked by user
				
				useruploads_count = str(get_useruploadsCount(str(finalhtml[0]['id']))) #count ofimage uploaded by user
				userliked_count = str(get_userLikedCount(str(finalhtml[0]['id']))) #count ofimage LIKED by user
				useridd_count = str(get_useridentifyCount(str(finalhtml[0]['id']))) #count ofimage IDENTIFIED by user
				own_count = str(get_ownCount(str(finalhtml[0]['id']))) #count ofimage OWNED by user
				attributecount= str(get_attributelikedCount(str(finalhtml[0]['id']))) #count ofimage attribute liked by user

				userid = str(finalhtml[0]['id'])
				
				ownithtml=''
				linkhtml=''
				if ownit != '':
					ownithtml=ProcessProfileOwnitImages(ownit,'uuid')
					if len(ownit)>= limit:
						linkhtml = '<nav><a class="load-link" href="'+SITEURL+'profile.py?userid='+str(finalhtml[0]['id'])+'&namesearch=ownit&start='+str(int(start)+limit)+'"></a></nav>'
					ownithtml = ownithtml + linkhtml
				else:
					ownithtml = 'No image found'			
				
				
				attributelikedhtml=''
				linkhtml=''
				if attributeuserliked != '':
					attributelikedhtml=ProcessProfileAttributeImages(attributeuserliked,'uuid')
					if len(attributeuserliked)>= limit:
						linkhtml = '<nav><a class="load-link" href="'+SITEURL+'profile.py?userid='+str(finalhtml[0]['id'])+'&namesearch=attributeliked&start='+str(int(start)+limit)+'"></a></nav>'
					attributelikedhtml = attributelikedhtml + linkhtml
				else:
					attributelikedhtml = 'No image found'
				
				
				useruploadshtml = ''
				linkhtml = ''
				if useruploads != '':
					useruploadshtml = processAttributerelatedImages(useruploads,'uuid')
					if len(useruploads) >= limit:
						linkhtml = '<nav><a class="load-link" href="'+SITEURL+'profile.py?userid='+str(finalhtml[0]['id'])+'&namesearch=useradded&start='+str(int(start)+limit)+'"></a></nav>'
					useruploadshtml = useruploadshtml + linkhtml
				else:
					useruploadshtml = 'No image found'
							
				useridentifyhtml = ''
				linkhtml = ''
				if useridentify != '':
					useridentifyhtml = ProcessProfileIdentifiedImages(useridentify,'uuid')
					if len(useridentify) >= limit:
						linkhtml = '<nav><a class="load-link" href="'+SITEURL+'profile.py?userid='+str(finalhtml[0]['id'])+'&namesearch=useridentified&start='+str(int(start)+limit)+'"></a></nav>'
					useridentifyhtml = useridentifyhtml + linkhtml
				else:
					useridentifyhtml = 'No image found'
						
				userliked = get_userLiked(str(finalhtml[0]['id'])) #image Liked by user
				
				userlikedhtml = ''
				if userliked != '':
					userlikedhtml = processAttributerelatedImages(userliked,'imageuid')   # imageUUID
					linkhtml = ''
					length = len(userliked)
					if len(userliked) >= limit:
						linkhtml = '<nav><a class="load-link '+str(length)+'" href="'+SITEURL+'profile.py?userid='+str(finalhtml[0]['id'])+'&namesearch=userliked&start='+str(int(start)+limit)+'"></a></nav>'
					userlikedhtml = userlikedhtml + linkhtml
					#~ userlikedhtml = get_userLikedrelated(str(finalhtml[0]['id']),start,limit)
					
					
				else:
					userlikedhtml = 'No image found'
				
				userlikedform = get_likeForm(True)
				#userattributelikedform = get_likeFormattribute(True)
				
				#Parse all varible to template to give html output .replace('--attributelikedhtml--',(attributelikedhtml))
				finalhtml1 = finalhtml1.replace('--username--',(str(finalhtml[0]['username']))).replace('--attributecount--',(attributecount)).replace('--userid--',(userid)).replace('--useridentified--',(useridentifyhtml)).replace('--own_count--',(own_count)).replace('--useridd_count--',(useridd_count)).replace('--userliked_count--',(userliked_count)).replace('--userupload_count--',(useruploads_count)).replace('--useradded--',(useruploadshtml)).replace('--userliked--',(userlikedhtml+userlikedform)).replace('--attributelikedhtml--',(attributelikedhtml)).replace('--userowned--',(ownithtml))
				#finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container">		<div class="font1 font2" style="text-align: left; margin: 0px auto; width: 339px;">FullName : '+str(finalhtml[0]['fullname'])+'<br />Username : '+str(finalhtml[0]['username'])+'<br />URL : '+str(SITEURL)+str(finalhtml[0]['username'])+'<br />Social ID : '+str(finalhtml[0]['userid'])+'<br />Email : '+str(finalhtml[0]['useremail'])+'<br />Member Since : '+str(time1)+'<br />Last updated : '+str(time2)+'</div></div></div>'
			
			else: #404 page not found
				finalhtml1 = '<div class=" no_bg" style="font-size: 29px; padding-top: 24px; text-align: justify;">	<div class="container"> <div class="font1 font2" style="text-align: left; margin: 0px auto; width: 339px;">Page not Found.</div></div></div>'

			html = html.replace("--search-type--",'').replace("--search-name--",'') + finalhtml1 + bottomFile
		html = encodeCharAt(html)
		output(html) #Display output Html 

	else:
		finalhtml = 'Reload <script> window.location = "'+SITEURL+'";</script>'
		output(finalhtml)

else:
	finalhtml = '<script> window.location = "'+SITEURL+'sign-in.py";</script>'
	output(finalhtml)
	sys.exit()
