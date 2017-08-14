def savecorrections(uilist,db,inj,cluster):
	for ui in uilist:
		colnames = ['B','V','R','I','z']                                 

		colors = ['B','V','R','I','Z']
                cors = []	
                terms = []
	        errs = [0.08,0.07,0.08,0.08,0.09]
                import lib
                galextinct = []
                for j in range(5):      
                	cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])]])
                	terms.append([float(db[colors[j]+'siga']),float(db[colors[j]+'sigb'])])
                	#galextinct.append(float(db[colors[j]]))
                for j in [inj]:     
                
                	import math                                                                      	
                	errshold = [0.03,0.02,0.02,0.02,0.02]
			##print ui
			##print ui[1+2*j], 1 + 2*j
                	errs[j] = math.sqrt( pow(errshold[j],2.0) + pow(ui[1+2*j],2.0) + pow(terms[j][0],2))# + pow(terms[j][1],2))
                	#THROW OUT CORRECTION COLOR TERM IF ONE OF THE VALUES IS BAD!
                	##print 2*cors[j][2][0], ui
                	##print cors, terms, galextinct, ui
                	
                	if float(ui[2*cors[j][2][0]]) < 90 and float(ui[2*cors[j][2][1]]) < 90:
                		correction = (float(ui[2*cors[j][2][0]]) - float(ui[2*cors[j][2][1]])) * cors[j][0] + cors[j][1] #+ galextinct[j]
                	else: 
                		correction = cors[j][1] #+ galextinct[j]
                	magzero = [27.66,27.57,27.60,27.28,27.24]
                	if 1 == 0 : #float(ui[j*2+1]) > 90: 
                		mag = -99 
                		magsout.append("99")#corrections including galactic reddenning and zeropoint offset
                		#the threshold is the one-sigma detection limit--you use this even for 
                		#negative values of flux--so if you're 3-sigma in the R-band that's ok.	
                		thresh = ui[13 + j]	/float(db['DETECT_THRESH']) 
                		maglimit = -1.0 * cors[j][1] + -2.5*math.log10(thresh ) + magzero[j]
                		errsout.append(maglimit)				
                		flag = 1
                		##print ui[j*2], correction, 	ui[2*cors[j][2][0]], ui[2*cors[j][2][1]], cors[j][0], cors[j][1], galextinct[j]
                	mag = float(ui[j*2]) - correction
                	idnum = ui[12]
                	#c.execute("UPDATE " + cluster + "subarudb SET  sexmag" + colnames[j] + " = " + str(mag) + ", sexmagerr" + colnames[j] + " = " + str(errs[j]) + " where subobjid = " + str(idnum) + ""  )
			mag = float(ui[j*2]) - correction
                        if float(ui[j*2]) <= 0: 
                        	mag = -99 
			##print ui
                        idnum = ui[12]
                        import dblib  
                        database = "" + cluster + outputdb 
                        if dblib.checkdb("mag" + colnames[j],database) != 1:
                        	c.execute("alter table " + database + " add column mag" + colnames[j] + " float(30,20)")   
                        if dblib.checkdb("magerr" + colnames[j],database) != 1:
                                c.execute("alter table " + database + " add column magerr" + colnames[j] + " float(30,20)")     	
			query = "UPDATE " + database + " SET  mag" + colnames[j] + " = " + str(mag) + ", magerr" + colnames[j] + " = " + str(errs[j]) + " where subobjid = " + str(idnum) + ""  
			##print query
                        c.execute(query)
			#print database 
			
			#raw_input()
                        #database2 = "" + cluster + "subarudb"
			##print database2
			#raw_input()
                        #c.execute("UPDATE " + database2 + " SET  sexmag" + colnames[j] + " = " + str(mag) + ", sexmagerr" + colnames[j] + " = " + str(errs[j]) + " where fieldsubobjid = " + str(idnum) + ""  )
	
import os
import MySQLdb
import os, sys, anydbm, time
from config import datb, dataloc
cluster = sys.argv[1]

colors = ['B','V','R','I','Z']
import lib 
#print datb + cluster
db = anydbm.open("./db/"+ cluster,'c')

spectype = 'full'
if len(sys.argv) > 2:
	if sys.argv[2] == 'spec': spectype = 'spec'
	if sys.argv[2] == 'star': spectype = 'star'
	if sys.argv[2] == 'starsdss': spectype = 'starsdss'

lib.galextinct(cluster,db)
os.system("mkdir " + cluster)
db[sys.argv[0][:-3]] = 'Started/' + time.asctime()

import os
import MySQLdb
db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
c = db2.cursor()

colnames = ['B','V','R','I','z']

for j in []: #range(5):                                                                                      	
 	c.execute("alter table catalog add column mag" + colnames[j] + " float")     	
        c.execute("alter table catalog add column magerr" + colnames[j] + " float")     	

for j in []: #range(5):                                                                                      	
 	c.execute("alter table subarudb add column mag" + colnames[j] + " float")     	
        c.execute("alter table subarudb add column magerr" + colnames[j] + " float")     	

#c.execute("select mag_0__0_,flux_0__0_,mag_1__0_,flux_1__0_,mag_2__0_,flux_2__0_,mag_3__0_,flux_3__0_,mag_4__0_,flux_4__0_,xs_3__0_,xs_3__1_,objid from subarudb ")
#c.execute("drop table if exists " + cluster + "spectramerge")

#c.execute("create table " + cluster + "spectramerge select * from " + cluster + "spectradb inner join " + cluster + "subarudb on " + cluster + "spectradb.spectrara between " + cluster + "subarudb.X_WORLD_R - 0.00027 and " + cluster + "subarudb.X_WORLD_R + 0.00027 and " + cluster + "spectradb.spectradec between " + cluster + "subarudb.Y_WORLD_R - 0.00027 and " + cluster + "subarudb.Y_WORLD_R + 0.00027" ) # and (" + cluster + "spectradb.spectraz > 0.58 or " + cluster + "spectradb.spectraz < 0.5) ")

#c.execute("select MAG_AUTO_B, MAGERR_AUTO_B, MAG_AUTO_V, MAGERR_AUTO_V,MAG_AUTO_R, MAGERR_AUTO_R,MAG_AUTO_I, MAGERR_AUTO_I,MAG_AUTO_Z, MAGERR_AUTO_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R from " + cluster + "spectramerge")

#c.execute("select MAG_AUTOMATIC_B, MAGERR_AUTOMATIC_B, MAG_AUTOMATIC_V, MAGERR_AUTOMATIC_V,MAG_AUTOMATIC_R, MAGERR_AUTOMATIC_R,MAG_AUTOMATIC_I, MAGERR_AUTOMATIC_I,MAG_AUTOMATIC_Z, MAGERR_AUTOMATIC_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R from " + cluster + "subarudb where CLASS_STAR_R > 0.4 limit 600")

#c.execute("select MAG_AUTOMATIC_B, MAGERR_AUTOMATIC_B, MAG_AUTOMATIC_V, MAGERR_AUTOMATIC_V,MAG_AUTOMATIC_R, MAGERR_AUTOMATIC_R,MAG_AUTOMATIC_I, MAGERR_AUTOMATIC_I,MAG_AUTOMATIC_Z, MAGERR_AUTOMATIC_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R, spectraz from " + cluster + "spectramerge")

#print "create temp"



''' see if we have already cross matched with the spectroscopic z's '''
c.execute("describe " + cluster + "subarudb")
results = c.fetchall()
alreadymatched = 0
for line in results:
	for ele in line: 
		if ele == 'spectraz':
			alreadymatched =1 
if alreadymatched == 1: print "already combined"

#c.execute("drop table if exists " + cluster + "subarudb")
#c.execute("create table " + cluster + "subarudb select * from " + cluster + "tempsave") 
#c.execute("drop table if exists " + cluster + "tempsave")

if  spectype == 'full' and alreadymatched == 0:
	c.execute("drop table if exists " + cluster + "tempsave")
        c.execute("create table " + cluster + "tempsave like " + cluster + "subarudb")
        c.execute("insert " + cluster + "tempsave select * from " + cluster + "subarudb")
        c.execute("drop table if exists " + cluster + "temp")
        c.execute("create table " + cluster + "temp select * from " + cluster + "spectradb right outer join " + cluster + "subarudb on " + cluster + "spectradb.spectrara between " + cluster + "subarudb.X_WORLD_R - 0.00027 and " + cluster + "subarudb.X_WORLD_R + 0.00027 and " + cluster + "spectradb.spectradec between " + cluster + "subarudb.Y_WORLD_R - 0.00027 and " + cluster + "subarudb.Y_WORLD_R + 0.00027 group by " + cluster + "subarudb.subobjid" )
        c.execute("alter table " + cluster + "temp add PRIMARY KEY (subobjid)")
        c.execute("drop table if exists " + cluster + "subarudb")
        c.execute("rename table " + cluster + "temp to " + cluster + "subarudb")

if spectype == 'full':
	c.execute("select MAG_APER_B, MAGERR_APER_B, MAG_APER_V, MAGERR_APER_V,MAG_APER_R, MAGERR_APER_R,MAG_APER_I, MAGERR_APER_I,MAG_APER_Z, MAGERR_APER_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R, spectraz from " + cluster + "subarudb where MAG_APER_V is not null")  # and spectraz is not null")
	outputdb = "subarudb"


if spectype == 'star':
	c.execute("select MAG_AUTOMATIC_B, MAGERR_AUTOMATIC_B, MAG_AUTOMATIC_V, MAGERR_AUTOMATIC_V,MAG_AUTOMATIC_R, MAGERR_AUTOMATIC_R,MAG_AUTOMATIC_I, MAGERR_AUTOMATIC_I,MAG_AUTOMATIC_Z, MAGERR_AUTOMATIC_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R, spectraz from " + cluster + "subarudb where MAG_AUTOMATIC_V is not null")  # and spectraz is not null")
	outputdb = "subarudb"

if spectype == 'starsdss':

	print 'starsdss'
	c.execute("select MAG_AUTOMATIC_B, MAGERR_AUTOMATIC_B, MAG_AUTOMATIC_V, MAGERR_AUTOMATIC_V,MAG_AUTOMATIC_R, MAGERR_AUTOMATIC_R,MAG_AUTOMATIC_I, MAGERR_AUTOMATIC_I,MAG_AUTOMATIC_Z, MAGERR_AUTOMATIC_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R, CLASS_STAR_R from " + cluster + "mergesub where MAG_AUTOMATIC_V is not null")  # and spectraz is not null")
	outputdb = "mergesub"
	
	spectype = 'star'

#c.execute("describe " + cluster + "spectramerge")
#results = c.fetchall()
#alreadymatched = 0
#for line in results:
#	for ele in line: 
#		if ele == 'spectraz':
#			alreadymatched =1 
#if alreadymatched == 1: print "already combined"

if spectype == 'spec' and alreadymatched == 0:
        c.execute("drop table if exists " + cluster + "temp")
        c.execute("create table " + cluster + "temp select * from " + cluster + "spectradb inner join " + cluster + "subarudb on " + cluster + "spectradb.spectrara between " + cluster + "subarudb.X_WORLD_R - 0.00027 and " + cluster + "subarudb.X_WORLD_R + 0.00027 and " + cluster + "spectradb.spectradec between " + cluster + "subarudb.Y_WORLD_R - 0.00027 and " + cluster + "subarudb.Y_WORLD_R + 0.00027 group by " + cluster + "subarudb.subobjid" )
        c.execute("alter table " + cluster + "temp add PRIMARY KEY (subobjid)")
        c.execute("drop table if exists " + cluster + "spectramerge")
        c.execute("rename table " + cluster + "temp to " + cluster + "spectramerge")

if spectype == 'spec':
	outputdb = "spectramerge"
	c.execute("select MAG_APER_B, MAGERR_APER_B, MAG_APER_V, MAGERR_APER_V,MAG_APER_R, MAGERR_APER_R,MAG_APER_I, MAGERR_APER_I,MAG_APER_Z, MAGERR_APER_Z, X_IMAGE_R, Y_IMAGE_R,subobjid,THRESHOLD_B,THRESHOLD_V,THRESHOLD_R,THRESHOLD_I,THRESHOLD_Z, CLASS_STAR_R, spectraz from " + cluster + "spectramerge where MAG_APER_V is not null")



	
results = c.fetchall()
xswrite = open('xs','w')
spacer = open('spacer','w')
magsouttot = []
errsouttot = []
badspots = []
xstot = []
space = []
specz = []
badmeasure = []
objids = []
pp = 0
ll = 0
import dblib
if dblib.checkdb("sexmagB","" + cluster + outputdb) != 1:
	for j in range(5):  
        	c.execute("ALTER table " + cluster +  outputdb + " add column sexmag" + colnames[j] + " float(30,20)")
        	c.execute("ALTER table " + cluster + outputdb + " add column sexmagerr" + colnames[j] + " float(30,20)")

if dblib.checkdb("stellarmagpoissonerrB","" + cluster + outputdb) != 1:
	for j in range(5):  
        	c.execute("ALTER table " + cluster +  outputdb + " add column stellarmagpoissonerr" + colnames[j] + " float(30,20)")
        	c.execute("ALTER table " + cluster +  outputdb + " add column stellarmag" + colnames[j] + " float(30,20)")
        	c.execute("ALTER table " + cluster + outputdb + " add column stellarmagerr" + colnames[j] + " float(30,20)")






##rt = open('rt','r').readlines()
list = []
##for mle in rt:	
	##list.append(mle[:-1].replace('\t',''))
#print "here"

#for lem in range(5):  
	#savecorrections(results,db,lem,cluster)
#print len(results)
poly = 0
count = 0
for ui in results:
	count = count + 1
	if count % 100 == 0: print count
	objid = ui[12]
	##print objid
	good = 0
	##for mle in list:
		##if float(objid) == float(mle): good = 1
	if 1 == 1:
		import re          
	        kill = 0
	        bad = 0
	        errs = [0.08,0.07,0.08,0.08,0.09]
	        errshold = [0.08,0.07,0.08,0.08,0.09]
	        badlist = [1,1,1,1,1]
	        for j in range(5):
			#print ui
	        	if float(ui[2*j]) == 0: 
	        		bad = bad + 1
	        		errs[j] = 10000000 #set error on missing measurement really high
	        		badlist[j] = 0
	        	if bad == 3 or float(ui[2*j]) < 0: 
	        		kill = 1 
		class_star = ui[18]
		if float(class_star > -10.0):	
			kill = 0
		else: kill = 1

		spectraz = ui[19]

		flag = 0
	        errsout=[]
		errspoisson = [1,1,1,1,1]
	        magsout = []
		#print kill
		#raw_input()
	        if kill == 0:
	        	pop = ""
	        	id = 0
	        	for ele in ui: 
	        		pop = pop + str(id) + " " + str(ele) + ", "
	        		id = id  + 1
	        	##print pop
			colors = ['B','V','R','I','Z']
			cors = []	
			terms = []
			import lib
			galextinct = []
	        	for j in range(5):      
				#cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])]])

				if poly == 1: cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])],float(db[colors[j]+'c'])])
				else: cors.append([float(db[colors[j]+'b']),float(db[colors[j]+'a']),[int(db[colors[j]+'band1']),int(db[colors[j]+'band2'])]])
				terms.append([float(db[colors[j]+'siga']),float(db[colors[j]+'sigb'])])
				galextinct.append(float(db[colors[j]]))
			#print terms
	        	for j in range(5):     
			
	        		import math                                                                      	
	        		errshold = [0.03,0.02,0.02,0.02,0.02]
	        		errs[j] = math.sqrt( pow(errshold[j],2.0) + pow(ui[1+2*j],2.0) + pow(terms[j][0],2))# + pow(terms[j][1],2))
	        		errspoisson[j] = math.sqrt(  pow(ui[1+2*j],2.0) )# + pow(terms[j][1],2))
	        		#THROW OUT CORRECTION COLOR TERM IF ONE OF THE VALUES IS BAD!
				##print 2*cors[j][2][0], ui
				##print cors, terms, galextinct, ui
				AB_cor = [-0.075,0.007, 0.208, 0.443, 0]	
				#AB_cor = [0,0,0,0,-0.522]
	        		if float(ui[2*cors[j][2][0]]) < 90 and float(ui[2*cors[j][2][1]]) < 90:
					color = (float(ui[2*cors[j][2][0]]) - float(ui[2*cors[j][2][1]]))
					if poly == 1: correction = color * color * cors[j][3] +  color * cors[j][1] + cors[j][0] 
	        			else: 
						correction =  color * cors[j][0] + cors[j][1] 
	        		else: 
	        			correction = cors[j][1] 
	        		magzero = [27.66,27.57,27.60,27.28,27.24]
	        		ll = ll + 1
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
	        			magsout.append(mag)
	        			errsout.append(errs[j])
	        		idnum = ui[12]

				if spectype != 'star':	
					query = "UPDATE " + cluster + outputdb + " SET  sexmag" + colnames[j] + " = " + str(mag) + ", sexmagerr" + colnames[j] + " = " + str(errs[j]) + " where subobjid = " + str(idnum) + ""  	
	        		        c.execute(query)
				if spectype == 'star':	
					query = "UPDATE " + cluster + outputdb + " SET  stellarmag" + colnames[j] + " = " + str(stellarmag) + ", stellarmagerr" + colnames[j] + " = " + str(errs[j]) + ", stellarmagpoissonerr" + colnames[j] + " = " + str(errspoisson[j]) + " where subobjid = " + str(idnum) + ""  	

	        		        c.execute(query)
				#print query
				#raw_input()
	        	xs = [ui[10],ui[11]]	
	        	xstot.append(xs)
		if flag == 0:
	       		objid = ui[12]                           
	                objids.append(ui[12])	
			##print magsout
	                magsouttot.append(magsout)		
			specz.append(spectraz)
			##print errsout
			#raw_input()
	                errsouttot.append(errsout)
	                badspots.append(badlist)
	                badmeasure.append(kill)

#print len(magsouttot), "magsouttot"

for combonum in range(len(badspots)):
	combo = badspots[combonum]
	listst = ""
	for ele in combo : listst = listst + str(ele)
	if badmeasure[combonum] == 0:
		spacer.write(listst + " " + str(objids[combonum]) + "\n")
	else:
		spacer.write("bad" + " " + str(objids[combonum]) + "\n")
#print "here"
stuff = open(cluster + "bpz",'w')
stuff.write("\n")
combo1 = [1,1,1,1,1]
for stepn in [0]: #-20, -15, -10,-5,-2,-1,1,2,5,10, 15, 20]: 
	for cindex in  range(1):
		color = colnames[cindex] 
		listst = ""                                                                                                                       	
	        for ele in combo1 : listst = listst + str(ele)
	        listgood = []
	        filterlist = ['subaru_B.par','subaru_V.par','subaru_R.par','subaru_I.par','subaru_z.par']
	        filterlist2 = ['subarume/subaru_B.pb','subarume/subaru_V.pb','subarume/subaru_R.pb','subarume/subaru_I.pb','subarume/subaru_z.pb']
	        filterl2 = []
	        filterl = []
	        
	        #print "here"
	        for ele in range(len(combo1)) : 
	        	if combo1[ele] == 1: 
	        		listgood.append(ele)
	        		filterl.append(filterlist[ele])
	        		filterl2.append(filterlist2[ele])
	        filters = ""
	        filters2  = ""
	        for fil in filterl: filters = filters + "'" + fil + "',"	
	        for fil in filterl2: filters2 = filters2 + "" + fil + ","	
	        filters = filters[:-1]
	        filters2 = filters2[:-1]
		file = 'bpz' + str(stepn) + str(color)
		step = stepn * float(db[colors[cindex]+'sigb'])
		file = file.replace('.','_').replace('-','minus')
	        sert = open(os.environ[cluster] + file ,'w')
		
	        listnow = []
	        for combo in range(len(badspots)):
	        	if combo1 == badspots[combo] and 0 == badmeasure[combo]: 
	        		listnow.append(combo)
	        for combo in listnow:
	        	sert.write(str(objids[combo]) + " ")
	        	for ele in listgood:             		
				if ele == cindex:
                        		sert.write(str(magsouttot[combo][ele] + step) + " " + str(errsouttot[combo][ele]) + " ")
				else:
                        		sert.write(str(magsouttot[combo][ele]) + " " + str(errsouttot[combo][ele]) + " ")
			#print str(specz[combo])[0], combo
			if str(specz[combo])[0] != 'N':
				if 0.52 < float(specz[combo])  < 0.6:
					sert.write("\n")
				else: 
					print specz[combo]
		                        sert.write(" 0 " + str(specz[combo]) + " hey\n")
				print "spec"
			else: sert.write("\n")
		sert.close()
	        if len(listnow) > 0:
	        	stuff.write("\
zphot 	-c $LEPHAREDIR/config/me.para -FILTER_LIST $LEPHAREWORK/" + filters2 + " -CAT_IN " + os.environ[cluster] +  file + " -CAT_OUT " + os.environ[cluster] + file + ".specout\n")

#print pp / float(ll)
	
	
db[sys.argv[0][:-3]] = 'Finished/' + time.asctime()
db.close()

