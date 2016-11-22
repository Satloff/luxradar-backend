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

print("/home/ghrix/Pictures/elecbill-jan-15.png")
