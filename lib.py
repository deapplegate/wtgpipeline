def galextinct(cluster, gh):	
	import urllib, os, re, string, anydbm
	from config import datb, dataloc
	img = dataloc + "/" + cluster + "/images/" + cluster + '.B.s0.2.fits'
        print img
        imcom = "gethead " + img + " CRPIX1 CRPIX2 CRVAL1 CRVAL2 CDELT1 CDELT2 > ./outim"
        print imcom
	#os.system(imcom)
        import re
        com = re.split('\s+',open("outim",'r').readlines()[0][:-1]  )
        crpix1 = float(com[0])
        crpix2 = float(com[1])
        crval1 = float(com[2])
        crval2 = float(com[3])
        cdelt1 = float(com[4])
        cdelt2 = float(com[5])
	gh['ra'] = str(crval1)
	gh['dec'] = str(crval2)
	hh =  int(float(gh['ra'])/(360.0 / 24.0))
	print hh
	mm =  int((float(gh['ra']) - hh * (360.0 / 24.0))/(360.0 / (24.0 * 60.0)))
	print mm
	ss =  int( (float(gh['ra']) - (360.0/24.0)*( hh+mm/60.0)) /(360.0 / (24.0 * 60.0 * 60.0)))
	decdd =  int(float(gh['dec'])/(1.0))
	print decdd
	decmm =  int((float(gh['dec']) - decdd )/(360.0 / (24.0 * 60.0)))
	print decmm
	decss =  int((float(gh['dec']) - decdd - (360.0/24.0)*(decmm/60.0))/(360.0 / (24.0 * 60.0 * 60.0)))
	print gh['ra'], gh['dec']
	print "lon=\"" + str(hh) + "h" + str(mm) +  "m" + str(ss) + "s\""
        print "lat=\"" + str(decdd) + "h" + str(decmm) +  "m" + str(decss) + "s\""
	outpos = 'extinct'	
	form = range(13)	
	form[0]= "host=\'nedwww.ipac.caltech.edu\'"
	form[1]= "url=\'/cgi-bin/nph-calc\'" 
	form[2]= "method=POST"
	form[3] = "in_csys=Equatorial"
        form[4] = "in_equinox='J2000.0'" 
	form[5] = "obs_epoch='2000.0'"	
	form[6] = "lon=\"" + gh['ra'][0:7] + "d\"" ## + str(hh) + "h" + str(mm) +  "m" + str(ss) + "s\""
	print "lon=\"" + gh['ra'][0:7] + "d\""
	form[7] = "lat=\"" +gh['dec'][0:7] + "d\"" ##3+ str(decdd) + "h" + str(decmm) +  "m" + str(decss) + "s\""
        form[8] = "pa=0.0" 
	form[9]= "out_csys=Equitorial"
	form[10]= "out_equinox='J2000.0'"
	form[11] = "file=" + outpos
	command = "method=POST host=nedwww.ipac.caltech.edu url=/cgi-bin/nph-calc" #command + form[0]	
	for j in range(3, 12):
                command = command + " " + str(form[j])
        print "Submitting image request.."
       	print command 
	os.system("perl ./webquery " + command)	
	page = open(outpos).readlines()
	for q in ['U','B','V','R','J','I','H','K']:
		for m in page:
			if m[0:3] == q + ' (' :
				line = re.split('\s+', m)	
				gh[q] = line[2] 	
				print line, q, gh[q]	

	ebv= float(gh['B']) - float(gh['V'])
                                                                                         
        #converting extinction to sloan filters using conversions in schlegel et al 1998
        gh['sdssU'] = str(5.155 * ebv)
        gh['sdssG'] = str(3.793 * ebv)
        gh['sdssR'] = str(2.751 * ebv)
        gh['sdssI'] = str(2.086 * ebv)
        gh['sdssZ'] = str(1.479 * ebv)
	gh['Z'] = gh['sdssZ'] 
	print gh['sdssI']
	for ju in gh.keys(): print ju, gh[ju]
        #print gh.keys()	

def correctmag(magarray,db,star='yes'):

	
	''' mag array is an array of instrumental magnitudes [B,Berr,V,Verr,R,Rerr,I,Ierr,z,zerr] '''
	ui = magarray 

	poly = 0

	colors = ['B','V','R','I','Z']
        cors = []	
        terms = []
        import lib
        galextinct = []
	errs = [0,0,0,0,0]
        for j in range(5):      
        	if poly == 1: cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])],float(db[colors[j]+'c'])])
        	else: cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])]])
        	terms.append([float(db[colors[j]+'siga']),float(db[colors[j]+'sigb'])])
        	galextinct.append(float(db[colors[j]]))
	magsout = []	
	errsout = []
	
        for j in range(5):     
        
        	import math                                                                      	
        	errshold = [0.03,0.02,0.02,0.02,0.02]
        	errs[j] = math.sqrt( pow(errshold[j],2.0) + pow(ui[1+2*j],2.0) + pow(terms[j][0],2))# + pow(terms[j][1],2))
        	AB_cor = [-0.075,0.007, 0.208, 0.443, 0]	
        	if float(ui[2*cors[j][2][0]]) < 90 and float(ui[2*cors[j][2][1]]) < 90:
        		color = (float(ui[2*cors[j][2][0]]) - float(ui[2*cors[j][2][1]]))
        		if poly == 1: correction = color * color * cors[j][3] +  color * cors[j][1] + cors[j][0] 
        		else: 
        			correction =  color * cors[j][0] + cors[j][1] 
        	else: 
        		correction = cors[j][1] 
        	magzero = [27.66,27.57,27.60,27.28,27.24]
        	if float(ui[j*2+1]) > 90: 
        		mag = -99 
        		stellarmag = -99
        		magsout.append("99")#corrections including galactic reddenning and zeropoint offset
			#the threshold is the one-sigma detection limit--you use this even for 
        		#negative values of flux--so if you're 3-sigma in the R-band that's ok.	
        		thresh = ui[13 + j]	#/float(db['DETECT_THRESH']) 
        		maglimit = -1.0 * cors[j][1] + -2.5*math.log10(thresh ) + magzero[j]
        		errsout.append(maglimit)				
        		flag = 1
        	else:
        		mag = float(ui[j*2]) - correction - galextinct[j] + float(AB_cor[j])
        		stellarmag = float(ui[j*2]) - correction 
			if star == 'yes':
	        		magsout.append(stellarmag)
			else:
	        		magsout.append(mag)
        		errsout.append(errs[j])
        	#idnum = ui[12]
	return [magsout,errsout]
	
	
