def makemask(snpath, color):
	from config import datb, prog, path
	import numarray, pyfits, os                                                           	
	id = readcat(snpath,color)
	rawim = pyfits.open(path + snpath + "/" + color + "/reg" + color + "seg.fits")
        imageseg = rawim[0].data
	mask = replacewithzero(imageseg,id)

        fitsobj = pyfits.HDUList()
        hdu = pyfits.PrimaryHDU()
        hdu.data = mask 

        fitsobj.append(hdu)

        os.system('rm ' + path + snpath +  '/' + color + '/mask.fits')
        print "made image"
        fitsobj.writeto(path + snpath +  '/' + color + '/mask.fits')
	return id

def replacebulge(matrix, xcen, ycen, radius):
	import numarray, math, os
	value = 0
	index = 0
	for x in range(int(xcen) - int(radius) - 2,int(xcen) + int(radius) + 2):
		for y in range(int(ycen) - int(radius) + 2,int(ycen) + int(radius) + 2):
			print x, y, math.sqrt(pow(x - xcen,2) + pow(y - ycen,2))
			if radius < math.sqrt(pow(x - xcen,2) + pow(y - ycen,2))	< radius + 2: 
				index = index + 1		
				value = value + matrix[y-1][x-1]
	mean = value / index	
	for x in range(int(xcen) - int(radius) - 2,int(xcen) + int(radius) + 2):
		for y in range(int(ycen) - int(radius) + 2,int(ycen) + int(radius) + 2):
			if math.sqrt(pow(x - xcen,2) + pow(y - ycen,2))	< radius: 
				matrix[y-1][x-1] = mean
	return matrix 

def replacewithzero(matrix,a):
	import numarray
	matrix = numarray.choose(matrix==a,(matrix,0))
	return matrix

def exceptreplace(matrix,a):
	print a
	import numarray
	copymatrix = numarray.array(matrix)
	ones = numarray.ones([len(matrix),len(matrix[0])]) 
	matrix = matrix - (a-1) * ones 
	matrix = numarray.clip(matrix,0,2)
	matrix2 = copymatrix - (a+1) * ones 
        matrix2 = numarray.clip(matrix2,-2,0)
	##print matrix, matrix2
	matrix = copymatrix * matrix * matrix2 * (-1 * ones) / (ones * a)
	#print matrix
	return matrix
def lessthan(matrix,a):
	import numarray
	copymatrix = numarray.array(matrix)
	ones = numarray.ones([len(matrix),len(matrix[0])]) 
	matrix = matrix - (a) * ones 
	matrix = numarray.clip(matrix,-1*1e20,0)
	matrix = matrix * -1 
	matrix = numarray.clip(matrix,-1*1e20,10e-10)
	matrix = matrix * 1e9
	copymatrix = matrix * copymatrix 
	return copymatrix

''' get rid of useless images '''
def cleanup(snpath):
	from config import path
	base = path + snpath + "/" 
	os.system("rm " + base + "weight.fits")
	os.system("rm " + base + "check.fits")
	os.system("rm " + base + "modelg.fits")
	os.system("rm " + base + "search*fits")
	os.system("rm " + base + "galaxy*fits")
	for color in ['u','g','r','i','z']:
		base = path + snpath + "/" + color + "/"
		os.system("rm " + base + "flag*fits")
		os.system("rm " + base + "*seg*fits")
		os.system("rm " + base + "*back*fits")
		os.system("rm " + base + "back*fits")
		os.system("rm " + base + "search*fits")
		os.system("rm " + base + "search*fits")

''' register images '''
def register(snpath,dir):
	import os,sys
        from config import datb, prog, path
	os.chdir(dir)
	os.system("pwd")
	os.system('cp ' + prog + 'keep.cl login.cl')
        out = open('gjd','w')
        #out.write("!rm ./g/regg.fits\n")
	os.system("pwd")
        out.write("cp g/regg.fits ./g/regg.fits\n")
	from glob import glob
	if len(glob("./g/regg.fits")) == 0:
		#os.system("pwd")
		color = 'g'	
		os.system("mkdir " + color)
		os.system("cp all" + color + ".fits ./" + color + "/reg" + color + ".fits")
	#raw_input()
	print len(glob("./u/regu.fits")) 
        for color in ['i','r','u','z']:	
		
		os.system("cp ./g/regg.fits modelg.fits")
		os.system("rm ./" + color + "/reg" + color + "*") 
		os.system("mkdir " + dir + color)
		out.write("!rm reg"+color+".fits\n")	
		out.write("!rm ./" + color + "/reg"+color+"*.fits\n")	
		out.write("!rm ./" + color + "/reg"+color+"*.fits.pl\n")	
		out.write("!rm ./" + color + "/regtemp.fits\n")	
        	out.write("flpr\nflpr\n")	
		out.write("wregister 'all" + color + ".fits' 'modelg.fits' './"+color+"/reg" + color + ".fits' fluxcons+ bound='nearest' const=-10000\n")
        out.write("logout\n")
        out.close()
       	#p = raw_input() 
	os.system("cl < gjd")
	#os.system("cphead g/regg.fits ./" + color + "/regtemps.fits CTYPE1 CTYPE2 CRPIX1 CRPIX2 CRVAL1 CRVAL2 CD1_1 CD1_2 CD2_1 CD2_2") 
	gh = anydbm.open(datb + snpath,'c')
	gh["wregister"] = 'done'
        galname = gh['agalname']
        galname = galname.replace(' ','')	
        #write a coordinates file

def exceptreplace(matrix,a):
	print a
	import numarray
	copymatrix = numarray.array(matrix)
	ones = numarray.ones([len(matrix),len(matrix[0])]) 
	matrix = matrix - (a-1) * ones 
	matrix = numarray.clip(matrix,0,2)
	matrix2 = copymatrix - (a+1) * ones 
        matrix2 = numarray.clip(matrix2,-2,0)
	##print matrix, matrix2
	matrix = copymatrix * matrix * matrix2 * (-1 * ones) / (ones * a)
	#print matrix
	return matrix
def lessthan(matrix,a):
	import numarray
	copymatrix = numarray.array(matrix)
	ones = numarray.ones([len(matrix),len(matrix[0])]) 
	matrix = matrix - (a) * ones 
	matrix = numarray.clip(matrix,-1*1e20,0)
	matrix = matrix * -1 
	matrix = numarray.clip(matrix,-1*1e20,10e-10)
	matrix = matrix * 1e9
	copymatrix = matrix * copymatrix 
	return copymatrix

def openraws(snpath,xcen,ycen,color):
	from config import path, datb, prog
        #Given X0 and Y0, construct an array that contains allg of the correct points
        #read in file
	import anydbm
	db = anydbm.open(datb + snpath, 'c')
	import pyfits
        rawim = pyfits.open(path + snpath + "/" + color + "/reg" + color + ".fits")
        image = rawim[0].data
        rawim = pyfits.open(path + snpath + "/" + color + "/reg" + color + "seg.fits")
        imageseg = rawim[0].data
	X0 = xcen
	Y0 = ycen
                                                                                      
                                                                                      
	#remember that x and y get switched around here and we subtract one 
                                                                                      
        from colorlib import gaussmeasure
	import colorlib
	colorlib.galextinct(snpath)
	print imageseg
        useg = gaussmeasure(imageseg,snpath,color,1,db)
        div = 1
	print X0, Y0
        useg.lightintegerdiv(X0,Y0,div)  # no background subtraction

        id = useg.lightdiv
	print id
	db.close()
	return id

def fixsky(snpath, img,color)	:
	from config import path, datb, prog
	import os,anydbm,re,colorlib
	gh = anydbm.open(datb + snpath,'c')
        #img = path + snpath + "/" + color + "/reg" + color + ".fits"
	print 'gethead ' + img + ' SKY> skyfile'	
        os.system('gethead ' + img + ' SKY> skyfile')
        fhy = open('skyfile','r').readlines()
        if len(fhy) > 0:                                                                           	
        	ki = fhy[0].replace("\n","")
                skyvalue = ki	
		print "natural"
        else: 
        	colorlib.values(	gh, path + snpath +"/g/regg.fits" ,snpath)
        	kk = float(gh['kk' + color])	
                kkErr = float(gh['kkErr' + color])	
                airmass = float(gh['airmass' + color])
        	maggie = float(gh['sky'+color]) 
        	print kk, airmass
        	f0 = 1.0*float(gh['aa'+color]) + kk* airmass #pow(10,1*(float(gh['aa'+color]))*0.4)
        	print maggie,f0, pow(10,0.4*f0)
        	print maggie/pow(10,0.4*f0)
		gh['exptime'] = str(53.9)
        	counts = float(gh['exptime']) * float(gh['avscale']) * float(gh['avscale']) * (maggie/pow(10,0.4*f0)) 
        	skyvalue = counts
        	#mag3 = -2.5 * math.log10(magnitude)
        	print maggie,counts	, skyvalue
        	os.system('sethead ' + img + ' SKY=' + str(skyvalue))
	print color, snpath
	print 'gethead ' + img + ' SKYRMS> skyfile'	
        os.system('gethead ' + img + ' SKYRMS> skyfile')
        fhy = open('skyfile','r').readlines()
        if len(fhy) > 0: 
        	skyrms = fhy[0].replace("\n","")
	
	#return [float(skyvalue),float(skyrms)]
	gh.close()
	return [float(skyvalue),float(10.0)]

def gdbm_shelve(filename, flag="c"):
	return shelve.Shelf(gdbm.open(filename,flag))

def overlap(pimin, pimax, smin, smax):
	#case num 1 no overlap
	if pimin > smax: comp = 0 
	#case num 2 fractional overlap less than
	if pimin < smax and pimin > smin and pimax > smax: comp = smax - pimin
	#case num 3 pixel encloses completely
	if pimin < smin and pimax > smax : comp = 1
	#case num 2 sample encloses pixel
	if smin < pimin and pimax < smax : comp = 1
	#case num 4 fractional greater than
	if pimax > smin and smin > pimin and smax > pimax : comp = pimax-smin
	#case num 5 no overlap
	if  pimax < smin : comp = 0
	return comp

def sample(snx,sny,plist,background):
	#i think that this one just does a little 3 by 3 box	
	import numarray	
	#print "sample" , snx , " " , sny	
	pixellist = numarray.zeros((3,3),type = numarray.Float32) 
	pixels = numarray.zeros((3,3),type = numarray.Float32) 
	#print pixellist	
	cx = round(snx)
	cy = round(sny)
	for xcor in [cx - 1.0 , cx , cx + 1.0]:
		for ycor in [cy - 1.0 , cy , cy + 1.0]:
			#print xcor, cx, ycor, cy, xcor-cx+2, ycor-cy+2
			x = int(xcor-cx+1)
			y = int(ycor-cy+1)	
			#print x ,y 
			#reverse x and y because of image
			pixellist[x][y] = plist[int(ycor)-1][int(xcor)-1]
	#print pixellist	
	#shift to a 3 x 3 grid	
	snx = snx - cx + 1
	sny = sny - cy + 1
	xmin = snx - 0.5
        ymin = sny - 0.5
        xmax = snx + 0.5
        ymax = sny + 0.5
        scale  = 1.00 
       	#figure out which pixels to measure
	tally = 0
	counts = 0	
	vcounts = 0
	for pixelx in range(3):
		for pixely in range(3):
        	        pymin = pixely - scale / 2.0
        	        pymax = pixely + scale / 2.0
        	        pxmin = pixelx - scale / 2.0
        	        pxmax = pixelx + scale / 2.0
        	        compx = overlap(pxmin,pxmax,xmin,xmax)
        	        compy = overlap(pymin,pymax,ymin,ymax)
        	        coeff = compx * compy
        	        #pixels[pixelx][pixely]
        	        #print coeff, tally	
        	        counts = counts + coeff * pixellist[pixelx][pixely]
        	       	vcounts = vcounts + pixellist[pixelx][pixely] 
			tally = tally + coeff
	vavcounts = vcounts / 9.0
	sum = 0
       	for pixelx in range(3):         
        	for pixely in range(3):
			sum = sum + pow((pixellist[pixelx][pixely]-vavcounts),2)
	rms = pow(sum/9.0,0.5)
	#rescale the pixels to account for the difference in pixel scale
        #print counts
        #counts = counts  * pow(scale )
        print "coeff adds up to " , tally
	return [counts,rms]

class ghk:
	def __init__(self,z):
		self.z = z
	def  num(self,x,y):
		#print x[self.z] ,y[self.z],  cmp(float(x[self.z]) ,float(y[self.z]))
		return cmp(float(x[self.z]) ,float(y[self.z]))

def avrms(brlisty):
	count = 0
	commentary = []
	for entry in range(len(brlisty)):
         	count = count + float(brlisty[entry])
         	commentary.append(count) #this creates the fluxstat list
        totalc = count
        avcount = count / len(brlisty)
	for entry in range(len(brlisty)):
         	if float(brlisty[entry]) > avcount: 
			number = entry
			break
        diff = 0
	diff2 = 0
        for entry in range(len(brlisty)):
		diff = diff + pow(float(brlisty[entry]) - avcount,2)
		diff2 = diff2 + pow(float(commentary[entry]) - commentary[number],2)
	rms = pow(diff / len(brlisty), 0.5)
	rms2 = pow(diff2/ totalc, 0.5)
	#the rms in the fluxstat is just the rms / the total. 
       	return [str(avcount),str(rms),count, commentary, str(rms2), str(number)]

def cycle(x,y,lenx): #x,y,image):
	vars = []
	if lenx == 0: vars = [[x,y]]
	if lenx != 0:
		x = x + lenx                    	
	        for yint in range(lenx):	
	        	y = y + 1
	        	vars.append([x, y])
	        for xint in range(2*lenx):	
	        	x = x - 1
	        	vars.append([x, y])
	        for yint in range(2*lenx):	
	        	y = y - 1
	        	vars.append([x, y])
	        for xint in range(2*lenx):	
	        	x = x + 1
	        	vars.append([x, y])
	        for yint in range(lenx):	
	        	y = y + 1
	        	vars.append([x, y])
	print len(vars), lenx
	#print vars
	return vars

ver = "1.43"
#stuff to do here is pretty simple--just figure out what the total magnitude then pick some percent like 95%
class galstat:
	def __init__(self,snpath,bulge='no'):	
	
	def openraws(self,color):
                #Given X0 and Y0, construct an array that contains allg of the correct points
                #read in file

		import pyfits

                div = 1

		
               	rawim = pyfits.open(self.path + self.snpath + "/u/regubackground.fits") 
                self.imageu = rawim[0].data
	        rawim = pyfits.open(self.path + self.snpath + "/u/reguseg.fits")
                self.imagesegu = rawim[0].data
                print "opened u"

	def mkimagesimple(self):
        	print "length of gal " , len(self.newgal)                                                         
        	import anydbm, os
		os.system("mkdir ./shelf/")
		os.system("pwd")
                k3 = anydbm.open('./shelf/' + self.snpath,'c')
                record = open('./record/' + self.snpath,'w')
                import numarray, pyfits
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = numarray.zeros((1489,2048), type = numarray.Float32)
                color = 'g'
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")
                image = rawim[0].data
        	print "galx" , len(self.newgal)
                for each in self.newgal:
                	if each[1]> 0 and each[1] < 1489 and each[0]>0 and each[0] < 2048:
                		hdu.data[each[1]][each[0]] = image[each[1]-1][each[0]-1] 
                fitsobj.append(hdu)
                os.system('rm galaxysim.fits')
                print "sim made image"
                fitsobj.writeto('galaxysim.fits')
		os.system("ls galaxysim.fits")
                os.system('cp galaxysim.fits ' + self.path + self.snpath + "/" + color + "/reggalsim" + color + ".fits" )
		print  self.path + self.snpath + "/" + color + "/reggalsim" + color + ".fits"
		from config import prog
		os.system('cp galaxysim.fits ' + prog + "utilities/simsgals/" + self.snpath + ".fits") 
		os.system("pwd")
	
	def mkimage(self):
		import anydbm, os
		os.system("pwd")
		os.system("mkdir shelf")
                k3 = anydbm.open('./shelf/' + self.snpath,'c')
                record = open('./record/' + self.snpath,'w')
	        import numarray, pyfits
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = numarray.zeros((1488,2048), type = numarray.Float32)
                color = 'g'
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")
                image = rawim[0].data
		print "galx" , len(self.galx)
                for each in self.gal:
                	if each["yr"]> 0 and each["yr"] < 1489 and each["xr"]>0 and each["xr"] < 2048:
				if each["gflg"] == 1:
	                		hdu.data[each["yr"]][each["xr"]] = image[each["yr"]-1][each["xr"]-1] 
                fitsobj.append(hdu)
                os.system('rm galaxy.fits')
                print "made image"
                fitsobj.writeto('galaxy.fits')
	        os.system('cp galaxy.fits ' + self.path + self.snpath + "/" + color + "/reggal" + color + ".fits" )
	def mkfrucimage(self):
        	import anydbm, os
                k3 = anydbm.open('./shelf/' + self.snpath,'c')
                record = open('./record/' + self.snpath,'w')
                import numarray, pyfits
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = numarray.zeros((1488,2048), type = numarray.Float32)
                color = 'g'
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")
                image = rawim[0].data
		print "galfruc" , len(self.galfruc)
                for each in self.galfruc:
                	if each[1]> 0 and each[1] < 1489 and each[0]>0 and each[0] < 2048:
                		hdu.data[each[1]][each[0]] = image[each[1]-1][each[0]-1] 
                fitsobj.append(hdu)
                os.system('rm galaxy.fits')
                print "made image"
                fitsobj.writeto('galaxy.fits')
                os.system('cp galaxy.fits ' + self.path + self.snpath + "/" + color + "/fruc" + color + ".fits" )
		from config import datb, prog
                os.system('cp galaxy.fits ' + prog + "utilities/imsgals/" + self.snpath + ".fits" )

		hdu.data = imageseg
		print idseg, 'here'

                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                image = rawim[0].data
                fitsobj.append(hdu)
                os.system('rm ' + path + snpath +  '/galaxy0.fits')
		os.system("pwd")
                print "made image"
                #fitsobj.writeto(path + snpath +  '/galaxy0.fits')
		ones = numarray.ones([len(image),len(image[0])]) 

                #flgmap is map of pixels associated with galaxy
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                image = rawim[0].data
		flgmap = exceptreplace(imageseg,idseg)
		import numarray, pyfits                                                                      	
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = flgmap 
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                image = rawim[0].data
                fitsobj.append(hdu)
                os.system('rm ' + path + snpath +  '/galaxy.fits')
                print "made image"
                #fitsobj.writeto(path + snpath +  '/galaxy.fits')
		temp = flgmap * (image) # - ones * (1000 + skyvalue))
		
		import numarray, pyfits                                                                      	
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data =temp 
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                image = rawim[0].data
                fitsobj.append(hdu)
                os.system('rm ' + path + snpath +  '/galaxy2.fits')
                print "made image"
                #fitsobj.writeto(path + snpath +  '/galaxy2.fits')
		sum2 = temp.sum()
                light = float(self.db[str(1) + quant[1] + color]) 
		print str(1) + quant[1] + color
		print light, "light"
		lessmap = lessthan(temp,light) 
		sum1 = lessmap.sum()
		
		import numarray, pyfits                                                                      	
                fitsobj = pyfits.HDUList()
                hdu = pyfits.PrimaryHDU()
                hdu.data = lessmap
                rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                image = rawim[0].data
                fitsobj.append(hdu)
                os.system('rm ' + path + snpath +  '/galaxy3.fits')
                print "made image"
                #fitsobj.writeto(path + snpath +  '/galaxy3.fits')
		
		print lessmap, lessthan
		print sum1, flgmap.sum(), idseg
		print sum2
		print self.db['snx'],self.db['sny']
		print "div", sum1/sum2, sum1, sum2	

                name = color + 'fluxstat.pixcounts'  
        	self.db[str(self.skyfactor) + color + name + "fruc3_7-50"+ color] = str(sum1/sum2)
		print 	str(self.skyfactor) + color + name + "fruc3_7-50"+ color, self.db[str(self.skyfactor) + color + name + "fruc3_7-50"+ color]
		
	def pickleit(self): 
       		import pickle                                
		os.system("mkdir pickles")
                f = open("./pickles/" + self.snpath + 'fruc','w')
                m = pickle.Pickler(f)
                pickle.dump(self.gal,m)
	def unpickleit(self): 
        	import pickle                                
                f = open("./pickles/" + self.snpath + 'fruc','r')
                m = pickle.Unpickler(f)
		self.gal = m.load()


	def calcstatbulge(self): 
        	import numarray
        
        	matri = ['u','g','r','i','z']
        	self.skyfactor = 2
        	#print len(self.gal), "length of self.gal"
        	quant = ['.pixcounts','pixccounts']
        	color = 'g'
        	for color in ['g']:
        		from config import path                                                                                                            	
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
        		if color == 'u':
                                imageseg = self.imagesegu 
        			idseg = self.idsegu
        			image = self.imageu
        			skyvalue = self.skyvalueu
        		if color == 'g':
                                imageseg = self.imagesegg 
        			idseg = self.idsegg
        			image = self.imageg
        			skyvalue = self.skyvalueg
        		if color == 'z':
                                imageseg = self.imagesegz 
                        	idseg = self.idsegz
                        	image = self.imagez
                        	skyvalue = self.skyvaluez
        
        		hdu.data = imageseg
        
                        #rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")

                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
			import os
                        os.system('rm ' + path + self.snpath +  '/galaxy0.fits')
        	        os.system("pwd")
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy0.fits')
        	        ones = numarray.ones([len(image),len(image[0])]) 
        	        flgmap = exceptreplace(imageseg,idseg)
        	        
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = flgmap 
                        #rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")

                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy.fits')
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy.fits')
        
        		image = replacebulge(image, float(self.db['bulgex']),float(self.db['bulgey']) ,float(self.db['bulgerad']) )
        	        temp = flgmap * (image) # - ones * (1000 + skyvalue))
        	        
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data =temp 
                        #rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")

                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy2.fits')
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy2.fits')
        	        sum2 = temp.sum()
                        light = float(self.db[str(1) + quant[1] + color]) 
        	        print str(1) + quant[1] + color
        	        print light, "light"
        	        lessmap = lessthan(temp,light) 
        	        sum1 = lessmap.sum()
                                                                                                                                        
        		fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = image
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/nobulge.fits')
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/nobulge.fits')
        
                    
                                                                                                                                                            
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = lessmap
                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + ".fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy3.fits')
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy3.fits')
                                                                                                                                                            
                                                                                                                                                            
        	        print lessmap, lessthan
        	        print sum1, flgmap.sum(), idseg
        	        print sum2
        	        print self.db['snx'],self.db['sny']
        	        print "div", sum1/sum2, sum1, sum2	
                                                                                                                                                            
                        name = color + 'fluxstat.pixcounts'  
        	        self.db[str(self.skyfactor) + color + name + "fruc3_7_bulge-50"+ color] = str(sum1/sum2)
        	        print 	str(self.skyfactor) + color + name + "fruc3_7_bulge-50"+ color, self.db[str(self.skyfactor) + color + name + "fruc3_7_bulge-50"+ color]
        	        print self.db['snx'], self.db['sny'], self.db['newgalx'],self.db['newgaly'], self.db['bettergalx'],self.db['bettergaly']

	def calcstat(self): 
        	import numarray, os
        	matri = ['u','g','r','i','z']
        	self.skyfactor = 2
        	quant = ['.pixcounts','pixccounts']
        	for color in ['g']:
        		from config import path                                                                                                            	
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                                                                                                                                                                 
        		if color == 'u':
                                imageseg = self.imagesegu 
        			idseg = self.idsegu
        			image = self.imageu
        			skyvalue = self.skyvalueu
                                                                                                                                                                 
        		if color == 'g':
                                imageseg = self.imagesegg 
                        	idseg = self.idsegg
                        	image = self.imageg
                        	skyvalue = self.skyvalueg
                                                                                                                                                                 
        		if color == 'z':
                                imageseg = self.imagesegz 
        			idseg = self.idsegz
        			image = self.imagez
        			skyvalue = self.skyvaluez
                                                                                                                                                                 
        		hdu.data = imageseg
        		print idseg, 'here'
                                                                                                                                                                 
                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy0.fits')
        	        os.system("pwd")
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy0.fits')
        	        ones = numarray.ones([len(image),len(image[0])]) 
        	        flgmap = exceptreplace(imageseg,idseg)
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = flgmap 
                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy.fits')
                        print "made image"
                        fitsobj.writeto(path + self.snpath +  '/galaxy.fits')
        	        temp = flgmap * (image) # - ones * (1000 + skyvalue))
        	        
        	        import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data =temp 
                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy2.fits')
                        print "made image"
                        #fitsobj.writeto(path + self.snpath +  '/galaxy2.fits')
        	        sum2 = temp.sum()
                        light = float(self.db[str(1) + quant[1] + color]) 
        	        print str(1) + quant[1] + color
        	        print light, "light"
        	        lessmap = lessthan(temp,light) 
        	        sum1 = lessmap.sum()
        	        
        		import numarray, pyfits                                                                      	
                        fitsobj = pyfits.HDUList()
                        hdu = pyfits.PrimaryHDU()
                        hdu.data = lessmap
                        rawim = pyfits.open(self.path + self.snpath + "/" + color + "/reg" + color + "background.fits")
                        image = rawim[0].data
                        fitsobj.append(hdu)
                        os.system('rm ' + path + self.snpath +  '/galaxy3.fits')
                        print "made image"
                        #fitsobj.writeto(path + self.snpath +  '/galaxy3.fits')
        	        
        		print lessmap, lessthan
        	        print sum1, flgmap.sum(), idseg
        	        print sum2
        	        print self.db['snx'],self.db['sny']
        	        print "div", sum1/sum2, sum1, sum2	
                        name = color + 'fluxstat.pixcounts'  
        	        self.db[str(self.skyfactor) + color + name + "fruc3_7-50"+ color] = str(sum1/sum2)
        	        print 	str(self.skyfactor) + color + name + "fruc3_7-50"+ color, self.db[str(self.skyfactor) + color + name + "fruc3_7-50"+ color]
