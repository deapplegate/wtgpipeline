def gencomsfile(cluster, spectype):
	if spectype == 'spec': database = "spectramerge"
	if spectype == 'full': database = "subarudb"
	list = []
	list.append([1,1,1,1,1])
	for j in range(5):
		default = [1,1,1,1,1]
		default[j] = 0
		list.append(default)
        for j in range(5):
        	default = [1,1,1,1,1]
        	default[j] = 0
        	for k in range(j+1,len(default)):
        		coop = []	
        		for ele in default: coop.append(ele)	
        		coop[k] = 0
        		list.append(coop)
	listfile = []
	
	import os
        import MySQLdb
        db = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
        c = db.cursor()
	c.execute("drop table tcat  ")	
	c.execute("create table tcat (tcatobjid int) ")	
	for step in [0]: #-20, -15, -10,-5,-2,-1,1,2,5,10, 15, 20]:#[-2,-1,1,2]: 
        	for cindex in  range(1):
			colnames = ['B','V','R','I','z']
        		color = colnames[cindex] 
			file = 'bpz' + str(step) + str(color) 
			varname = str(step) + str(color) 	
			varname =	varname.replace('-','minus').replace('.','dot')
			file = file.replace('.','_').replace('-','minus')+ ".specout"
			photoznum = 1 # because of the index         
		        import glob
			print len(glob.glob(os.environ[cluster] + file))
		        if len(glob.glob(os.environ[cluster] + file))>0: 	
		        	photoz = open(os.environ[cluster] + file,'r').readlines()[1:]	
		        	for linen in range(len(photoz)):
		        		if photoz[linen][0] != "#":
		        			import re  
		        		        parsed = re.split('\s+',photoz[linen][:-1])
						if parsed[0] == '': parsed = parsed[1:]
		        		        bpzz =  parsed[1]
		        			bpzzdown = parsed[2]
		        			bpzzup= parsed[3]	
		        		        id = parsed[0] 
		        			import dblib
		        			goahead = 0
		        			if dblib.checkdb("bpzz"+varname,cluster + database + "") != 1:
		        				goahead = 1
		        				print ""
							print "alter table  " + cluster + database + " add column bpzz" + varname + " float"
		        				c.execute("alter table  " + cluster + database + " add column bpzz" + varname + " float")     	
		        			        c.execute("alter table  " + cluster + database + " add column bpzzup" + varname + " float") 
		        			        c.execute("alter table  " + cluster + database + " add column bpzzdown" + varname + " float") 

		        		        cexec = "UPDATE " + cluster + database + " SET bpzz" + varname + " = " + str(bpzz) + ", bpzzup" + varname + " = " + str(bpzzup) + ", bpzzdown" + varname + " = " + str(bpzzdown) + " where subobjid = " + str(id) + ""  								
						print cexec
						#raw_input()
						c.execute(cexec)
import os
import MySQLdb
import os, sys, anydbm, time
from config import datb, dataloc
cluster = sys.argv[1]
spectype = 'full'
if len(sys.argv) > 2:
	if sys.argv[2] == 'spec': spectype = 'spec'
gencomsfile(cluster, spectype)


#db[sys.argv[0][:-3]] = 'Finished/' + time.asctime()
