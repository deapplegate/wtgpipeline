''' get date '''
def id_to_date(id):
	import re, os
        file = "/afs/slac.stanford.edu/u/ki/pkelly/pipeline/bluh2"
        command =  "/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/caldate -d  31/12/1998 -i " + id + " > " + file 
        os.system(command)
        yy = open(file,'r').readlines()
        date = ((re.split('\s+',yy[0])[-2]))
	return date

''' get gabodsid '''
def gabodsid(inputdate):
	import re, os
	file = "/afs/slac.stanford.edu/u/ki/pkelly/pipeline/bluh"
        command =  "/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/mjd -t  22:00:00 -d " + inputdate + " > " + file 
	print command
	os.system(command)
        yy = open(file,'r').readlines()
        MJD = ((re.split('\s+',yy[0])[-2]))

	file = "/afs/slac.stanford.edu/u/ki/pkelly/pipeline/bluh"
	os.system("/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/nightid -t  22:00:00 -d 31/12/1998 -m " + MJD + "> " + file )
	yy = open(file,'r').readlines()
	oo = int(float(re.split('\s+',yy[1])[-2]))
	return oo

def get_gabodsid(file,filter,type): 		
	import os
	command = "dfits " + file + " | grep GABODSID > hh" + filter  + type
	print command
	os.system(command)
	jj = open('hh' + filter + type,'r').readlines()
	import re
	date = re.split('\s+',jj[0])[1]
	return date 

def get_date(file,filter,type): 		
	import os
	command = "dfits " + file + " | grep DATE-OBS > hh" + filter
	print command
	os.system(command)
	jj = open('hh' + filter + type,'r').readlines()
	import re
	date = re.split('\'',jj[0])[1]
	year = float(date[0:4])
	month = float(date[5:7])
	day = float(date[8:])
	return (year, month, day)

''' see if one date falls inside two limits format is date = [yyyy,mm,dd] '''
def inside(date, down_limit, up_limit):
	good = 0
	print date[0], date[1], date[2], down_limit[0], up_limit[0]
	if (date[0] > down_limit[0]) and (date[0] < up_limit[0]):
		good = 1	
	elif date[0] == down_limit[0]: 
		if date[1] > down_limit[1]:
			good = 1
		elif date[1] == down_limit[1]:
			if date[2] > down_limit[2]:
				good = 1
	elif date[0] == up_limit[0]: 
        	if date[1] < up_limit[1]:
        		good = 1
        	elif date[1] == up_limit[1]:
			if date[2] < up_limit[2]:
        			good = 1
	print good	
	return good

''' the only thing that matters is the date '''
''' P_IMCOMBFLAT_IMCAT '''
'''
    P_IMCOMBFLAT_IMCAT=${BIN}/imcombflat

    ${P_IMCOMBFLAT_IMCAT} -i  flat_images_$$\
                    -o ${RESULTDIR[${CHIP}]}/$3_${CHIP}.fits \
                    -s 1 -e 0 1 
'''
	
def runit(): #dir,target_dir):

	import os
	dir = os.environ['skyflatraw'] + 'nobackup/SUBARU/auxilary/W-J-B_SKYFLAT/' 
	target_dir = os.environ['xoc'] + 'nobackup/SUBARU/auxiliary/skyflat_B'
	chip_confs = [[[2001,10,18],[2002,9,5],'_10_1'],[[2002,9,5],[2100,1,1],'_10_2']]

	''' split into different chip configurations '''
        from glob import glob
        list = glob(dir + "*fits")

	for chip_conf in chip_confs:
		newdir = target_dir + chip_conf[2]
                #anjadir = os.environ['subdir'] + "SUBARU/skyflat" + chip_conf[2]
                os.system('mkdir ' + newdir)
                #os.system('ln -s ' + newdir + ' ' + anjadir )
        for file in list:
        	(year, month, day) = get_date(file) 
		for chip_conf in chip_confs:
			print year, month,day, chip_conf[0], chip_conf[1]
			print inside([year,month,day],chip_conf[0],chip_conf[1])
			if inside((year,month,day),chip_conf[0],chip_conf[1]):
				try:
	        	                os.system("cp " + file + ' ' + target_dir + chip_conf[2] + '/')	
				except: print 'failed'

def combineperiods(interval,dir,filter,type,edit):

	
	paramslist = [{'method': 'MEDIAN','lo_clip':'3.0 3.0'}]#,{'method': 'CLIPMEAN','lo_clip':'3.0 3.0'},{'method': 'CLIPMEAN','lo_clip':'2.0 2.0'}]
	params = paramslist[0]
	import os, re
	statsxmin = '500'
	statsxmax = '1500'
	statsymin = '1500'
	statsymax = '2500'

	statsxminbin = '100'
        statsxmaxbin = '1100'
        statsyminbin = '100'
        statsymaxbin = '900'

	firstchip = 'yes'
	uu = open('rosetta','w')

	fildir =  filter + '_'	

	os.system('mkdir ' + fildir)
	os.system('chmod +rwx ' + fildir)
	batchfiles = open(fildir + 'batchfiles_' + filter + type ,'w')
	batchbincovfiles = open(fildir + 'batchbincovfiles_' + filter + type ,'w')
	batchdivfiles = open(fildir + 'batchdivfiles_' + filter + type,'w')
	batchnormfiles = open(fildir + 'batchnormfiles_' + filter + type,'w')
	batchcovfiles = open(fildir + 'batchcovfiles_' + filter + type,'w')
	batcheachfiles = open(fildir + 'batcheachfiles_' + filter + type,'w')

	batchnormeachfiles = open(fildir + 'batchnormeachfiles_' + filter + type,'w')

	from glob import glob
	
	u2 = open('reject.' + filter + '.' + type,'r').readlines()	
	rejectfiles = []
	for line in u2:
		temp = re.split('\/',line[:-1])[-1]
		out = re.split('_',temp)[0]
		if out != '':
			rejectfiles.append(out)


	print len(rejectfiles)
	## now reject files that have been labelled after dividing them by the median
	badfilename = 'reject.' + filter + '.norm.' + type
	if edit != '' and len(glob(badfilename)) > 0:
		u2 = open(badfilename,'r').readlines()	
                for line in u2:
                	temp = re.split('\/',line[:-1].replace('div_',''))[-1]
                	out = re.split('_',temp)[0]
			if out != '' and out[0] == 'S':
	                	rejectfiles.append(out)

	print len(rejectfiles)


	list = glob(dir + "/SUPA*10OC.fits")
	print dir

	print dir + "/SUPA*10OC.fits"
	# isolate the good binned divided files  
	div_list = glob(dir + "BINNED/div_SUPA*mos_normal.fits")
	goodfiles = open(fildir + 'goodfile','w')
	print 'total number of divided images', len(div_list)
        for line in div_list:
        	#print re.split('\/',line)
        	temp = re.split('\/',line)[-1]
        	temp = re.split('_',temp)[0]
        	bad = 0
        	for file in rejectfiles:
        		import string
        		if string.find(temp,file) != -1:
        			bad = 1
        	if bad == 0:
                	goodfiles.write(line + '\n')
	


	
        files = []
	badfiles = []
        for line in list:
        	#print re.split('\/',line)
        	temp = re.split('\/',line)[-1]
		temp = re.split('_',temp)[0]
		bad = 0
		for file in rejectfiles:
			import string
			if string.find(temp,file) != -1:
				bad = 1
		if bad == 0:
	        	files.append(temp)
		else:
	        	badfiles.append(temp)

	


	print files
	print dir
	imstatfile = open(fildir + 'imstatfile_' + type,'w')
	for chipnumber in range(1,11):
		''' first break up images into different epochs '''   
	        month_period = 6	
                from glob import glob
                #list = glob(dir + "*OC.fits")
	        command = "imstats `ls " + dir + "/SUPA*" + str(chipnumber) + "OC.fits` -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o " + fildir + "outliststats" + str(chipnumber)  + '_' + type
		imstatfile.write('bsub -R rhel40 -q short ' + command + '\n')
	print "REMEMBER TO RUN BATCH QUEUE"
	#raw_input()
	#import random
	#random_number = str(int(100000*random.random()))
	
	raw_input()
	for chipnumber in range(1,11):
		#print command
		#os.system(command)
		list = open(fildir + 'outliststats' + str(chipnumber)+ '_' + type,'r').readlines()
	        datelist = []
		index = 0
	        for file in list:
			if file[0] != '#' and file[0] != '':	
				filename = re.split('\s+',file)[0]	
				#mode = re.split('\s+',file)[1]
				bad = 1
				for file2 in files:
					if string.find(filename,file2) != -1:
						bad = 0
				# reject files with low or high modes
				#if mode <  or mode > :
				#	bad = 1
				if bad == 0:		
					index = index + 1
                			gabodsid = get_gabodsid(filename,filter,type)       	                                                                      
	        	                datelist.append([gabodsid,file[:-1],filename])
       				        command =  "/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/caldate -d 31/12/1998 -i " + gabodsid + " >  " + fildir + "temp "  
	                                os.system(command)
				        yy = open(fildir + 'temp','r').readlines()
                                        date = ((re.split('\s+',yy[0])[-2]))
				        uu.write(gabodsid + " " + date + "\n")
				
	        datelist.sort()	
		
		print datelist
		rr = open(fildir + 'dates_' + type,'w')
		rr2 = open(fildir + 'inputflipper','w')
		for obs in datelist:
			date = id_to_date(obs[0])	
			rr.write(str(obs[0]) + ' ' + str(date) + ' ' + str(obs[2]) + '\n')
			rr2.write(str(obs[2]).replace(type.upper(),type.upper() + '/BINNED').replace('10OC','mosOC') + '\n')
		rr.close()
		rr2.close()
	       
	        limit_up = float(datelist[-1][0])
	        limit_down = float(datelist[0][0])
	        ''' a six month period is approximately 30*6=180 days '''
	        
	        diff_year = int((limit_up - limit_down) / 180.0) + 1

		''' define your date ranges from dates file written out above '''
		#brackets = [[1523,1639],[1843,1846],[1878,1902],[1993,1994],[2268,2668]]
		#brackets = [[1878,1878],[1902,1902],[2268,2668]]
		#brackets = [[2268,2668]]

		if type == 'domeflat':	
			if filter == 'b':        	
		        	random_number = 1
                        if filter == 'v':
		        	random_number = 1
                        if filter == 'r':
		        	random_number = 1
                        if filter == 'i':
		        	random_number = 1
                        if filter == 'z':
		        	random_number = 1

		if type == 'skyflat':	
			if filter == 'b':   
                        	random_number = 1
                        if filter == 'v':
                        	random_number = 1
                        if filter == 'r':
                        	random_number = 1
                        if filter == 'i':
                        	random_number = 1
                        if filter == 'z':
                        	random_number = 1

		if type == 'skyflat':
			if filter == 'b':   
		        	brackets = [[1345,1729],[1845,2555],[1345,1524],[1640,1729],[1845,1998],[2316,2555],[1340,1345],[1490,1495],[1638,1643],[1666,1672],[1725,1730],[1845,1849],[1870,1875],[1877,1883],[1900,1907],[1928,1933],[1994,2003],[2312,2319],[2523,2529],[2729,2735],[2876,2882]]
		        if filter == 'v':
		        	brackets = [[1550,1800],[1801,2399],[2400,10000],[1550,1581],[1703,1758],[1842,1874],[2198,2319],[2407,2556]]
		        if filter == 'r':
		        	brackets = [[1403,2000],[2001,10000],[1496,1497],[1526,1554],[1639,1694],[2196,2261],[2732,2823]]
		        if filter == 'i':
		        	brackets = [[1551,1755],[1877,2052],[2315,2731]] #[1551,1611],[1877,2731],[1551,1554],[1577,1611],[1755,1755],[1877,1903],[2052,2558],[2731,2731],[1548,1553],[1582,1590],[1606,1614],[1723,1732],[1752,1758]]
		        if filter == 'z':
		        	brackets = [[1555,1639],[1843,1846],[1902,2268]] #[[1523,1846],[1878,2668],[1523,1639],[1843,1846],[1878,1902],[1993,1994],[2268,2668],[1521,1525],[1553,1557],[1637,1642],[1841,1849],[1875,1881],[1900,1906],[1991,1997]]

		if type == 'domeflat':
			if filter == 'b':
				brackets = [[1340,1345],[1490,1495],[1638,1643],[1666,1672],[1725,1730],[1845,1849],[1870,1875],[1877,1883],[1900,1907],[1928,1933],[1994,2003],[2312,2319],[2523,2529],[2729,2735],[2876,2882]]
			if filter == 'i':
				brackets = [[1551,1611],[1728,1903],[2439,2529]] #[[[1548,1553],[1582,1590],[1606,1614],[1723,1732],[1752,1758]]
			if filter == 'z':
				brackets = [[1523,1642],[1843,1879],[1901,2268]] #[[[1521,1525],[1553,1557],[1637,1642],[1841,1849],[1875,1881],[1900,1906],[1991,1997]]

		''' read in dates and make brackets '''
		filelists = {}
		for bracket in brackets:
                	filelists[str(bracket[0]) + '_' + str(bracket[1])] = []
                firstchip = 'no'

		if 1 == 0: #firstchip == 'yes':                                                                                                                   
	       		''' loop through the periods and make date brackets '''	 
	                brackets = []
	                filelists = {}
	                for i in range(diff_year):
	                	start = limit_down + i * 180
	                	end = limit_down + (i + 1) * 180
	                	brackets.append([start, end])
	                	filelists[str(start) + '_' + str(month_period)] = []
			firstchip = 'no'
		
		filelists['all'] = []
	        ''' go through observations and which time bracket each observation fits into '''
	        for obs in datelist:
	        	filelists['all'].append(obs[1])
	        	for bracket in brackets:	
				if bracket[0] <= float(obs[0])  and float(obs[0]) <= bracket[1]: 
	        			filelists[str(bracket[0]) + '_' + str(bracket[1])].append(obs[1])
	        #for params in paramslist:
		scriptname = fildir + type + 'script' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber)	
		outinfo = dir + scriptname  

		''' script to do imcombine '''
		script = open(scriptname,'w')
		''' script to divide by superflat'''
		divscript = open(scriptname + ".py",'w')

		divcovscript = open(scriptname + "_cov.py",'w')
		
		scriptnameeach = fildir + type + 'eachscript' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + '.py'	


		outinfoeach = dir + scriptnameeach


		''' script to do each each image '''
		scripteach = open(scriptnameeach,'w')
		batcheachfiles.write('bsub -R rhel40 -q medium -e ' + outinfoeach + 'norm -o ' + outinfoeach + 'norm python ' + scriptnameeach + '\n')
	
			
		if chipnumber == 1:
			''' script to bin and normalize'''                                                                                              	
		        normscript = open(scriptname + "_norm.py",'w')

		        bincovscript = open(scriptname + "_bincov.py",'w')

		        normeachscript = open(scriptname + "_normeach.py",'w')

		        batchnormfiles.write('bsub -R rhel40 -q medium -e ' + outinfo + 'norm -o ' + outinfo + 'norm python ' + scriptname + '_norm.py\n')
		        batchnormeachfiles.write('bsub -R rhel40 -q medium -e ' + outinfo + 'norm -o ' + outinfo + 'norm python ' + scriptname + '_normeach.py\n')
			batchbincovfiles.write('bsub -R rhel40 -q short -e ' + outinfo + 'bincov -o ' + outinfo + 'bincov python ' + scriptname + '_bincov.py\n')


		batchcovfiles.write('bsub -R rhel40 -q short -e ' + outinfo + 'cov -o ' + outinfo + 'cov python ' + scriptname + '_cov.py\n') 
		batchdivfiles.write('bsub -R rhel40 -q medium -e ' + outinfo + 'py -o ' + outinfo + 'py python ' + scriptname + '.py\n')
		batchfiles.write('bsub -R rhel40 -q medium -e ' + outinfo + ' -o ' + outinfo + ' source ' + scriptname + '\n')

		for key in filelists.keys(): 
	        	file = open(fildir + key + '_chip' + str(chipnumber),'w')                              	
	                for ele in filelists[key]:
	                	file.write(ele.replace('1OC.fits',str(chipnumber) + 'OC.fits') + '\n')
	                file.close()

	        	''' rescale -s 1 '''
	                method = params['method'] 
			if len(filelists[key]) > 10:
				if type == 'domeflat':    	
		                        lo_hi_rank = '1 3'
                                                           
			        if type == 'skyflat':
		                        lo_hi_rank = '1 3'
			elif len(filelists[key]) > 6:	
				if type == 'domeflat':    	
                                        lo_hi_rank = '0 0'
                                                           
                                if type == 'skyflat':
                                        lo_hi_rank = '1 1'
			else:	
                        	if type == 'domeflat':    	
                                        lo_hi_rank = '0 0'
                                                           
                                if type == 'skyflat':
                                        lo_hi_rank = '0 0'


	                lo_hi_rej = '10 30000'
	                lo_hi_clip = params['lo_clip'] 
	        	input_list = key
	        	output_image = edit + key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
	                command = "imcombflat -i " + fildir + input_list + "_chip" + str(chipnumber) + " -o "  + dir + output_image  + " -s 1 -c " + method + " -e " + lo_hi_rank + " -t " + lo_hi_rej + " -l " +  lo_hi_clip
	        	script.write(command + '\n')

	        	divided_prefix = edit + 'div_' + key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" 
			cov_prefix = divided_prefix.replace('div','cov') 
			divided_image = divided_prefix + "_" + str(chipnumber) + ".fits"
			cov_image = divided_prefix.replace('div','cov') + "_" + str(chipnumber) + ".fits"
			binned_image = "/BINNED/" + divided_prefix + "_mos.fits"
			binned_normal_image = "/BINNED/" + divided_prefix + "_mos_normal.fits"

			binned_image = "/BINNED/" + divided_prefix + "_mos.fits"
			binned_normal_image = "/BINNED/" + divided_prefix + "_mos_normal.fits"

			cov_binned_image = "/BINNED/" + cov_prefix + "_mos.fits"
			cov_binned_normal_image = "/BINNED/" + cov_prefix + "_mos_normal.fits"


			if key != 'all':	
				''' divide each chip by the comprehensive 'all' flat '''   
	        	        all_image = edit + 'all_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
				divscript.write("print '" + output_image + "'\n")
                                divscript.write("import re,os, anydbm\n")
			        divscript.write("os.system('rm " + dir + divided_image + "')\n")
			        divscript.write("os.system(\"ic '%1 %2 / ' " + dir + output_image + " " + dir + all_image + " > " + dir + divided_image + "\")\n")

				''' bin chips and normalize binned image '''
                                normscript.write("import re,os, anydbm\n")
				normscript.write("os.putenv('INSTRUMENT','SUBARU')\n")
				dd = re.split('\/',dir)
				basedir = reduce(lambda x,y: x + '/' + y,dd[:-2]) + '/'
				enddir = dd[-2]
			
				if chipnumber == 1:	
					normscript.write("os.system(\"rm " + dir + binned_image + "\")\n")
				        normscript.write("os.system(\"rm " + dir + binned_normal_image + "\")\n")	
				        normscript.write("os.system(\"./create_binnedmosaics.sh " + basedir + " " + enddir + " " +  divided_prefix + " '' 8 -32 \")\n") 
				        normscript.write("os.system(\"imstats " + dir + binned_image + " -s " + statsxminbin + " " + statsxmaxbin + " " + statsyminbin + " " + statsymaxbin + " -o " +fildir +  "outlist \")\n") 
                                        normscript.write("p = open('" + fildir + "outlist').readlines()[-1]\n")	
                                        normscript.write("mode = re.split('\s+',p)[1]\n")
					normscript.write("anydbm.open('modedir','c')['mode_" + filter + type + divided_prefix + '_' + str(random_number )+ '_\'] = mode\n'  )
                                        normscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + binned_image + " > " + dir + binned_normal_image + "\")\n")

                                	bincovscript.write("import re,os, anydbm\n")
					bincovscript.write("os.putenv('INSTRUMENT','SUBARU')\n")
					bincovscript.write("os.system(\"rm " + dir + binned_image + "\")\n")
                                        bincovscript.write("os.system(\"rm " + dir + binned_normal_image + "\")\n")	
                                        bincovscript.write("os.system(\"./create_binnedmosaics.sh " + basedir + " " + enddir + " " +  cov_prefix + " '' 8 -32 \")\n") 
                                divcovscript.write("import re,os, anydbm\n")
				divcovscript.write("os.system('rm " + dir + cov_image + "')\n")
				divcovscript.write("mode = anydbm.open('modedir','r')['mode_" + divided_prefix + '_' + str(random_number) + '_\']\n' ) 
                                divcovscript.write("os.system(\"ic '%1 \" +  mode  + \" / 1 - ' " + dir + divided_image + " > " + dir + cov_image + "\")\n")
				

			        #divscript.write("os.system('rm divoutA.fits')\n")
			        #divscript.write("os.system('rm divoutB.fits')\n")
	        	        #divscript.write("os.system(\"imstats " + dir + output_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outlist\")\n") 
			        #divscript.write("p = open('outlist').readlines()[-1]\n")	
			        #divscript.write("import re\n")
			        #divscript.write("mode = re.split('\s+',p)[1]\n")
			        #divscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + output_image + " > divoutA.fits \")\n")
			        #divscript.write("os.system(\"imstats " + dir + all_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outlist\")\n") 
                                #divscript.write("p = open('outlist').readlines()[-1]\n")	
                                #divscript.write("mode = re.split('\s+',p)[1]\n")
                                #divscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + all_image + " > divoutB.fits \")\n")
			        #divscript.write("os.system(\"ic '%1 %2 / ' divoutA.fits divoutB.fits > " + dir + divided_image + "\")\n")
			        #divscript.write("os.system('rm divoutA.fits')\n")
			        #divscript.write("os.system('rm divoutB.fits')\n")
	                	print command

		for ele in datelist:
			print ele

		        filename = ele[2]
	        	all_image = edit + 'all_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
			divided_image = filename.replace('SUPA','div_SUPA')
		        all_image = edit + 'all_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
                        scripteach.write("print '" + filename + "'\n")
                        scripteach.write("import re,os\n")
                        scripteach.write("os.system('rm " + divided_image + "')\n")
                        scripteach.write("os.system(\"ic '%1 %2 / ' " + filename + " " + dir + all_image + " > " + divided_image + "\")\n")	

			dd = re.split('\/',dir)
			basedir = reduce(lambda x,y: x + '/' + y,dd[:-2]) + '/'
			enddir = dd[-2]

			if chipnumber == 1:
				temp = re.split('\/',filename[:-1])[-1]
                                out = re.split('_',temp)[0]
				divided_prefix = 'div_' + out
				binned_image = "/BINNED/" + divided_prefix + "_mosOC.fits"
                        	binned_normal_image = "/BINNED/" + divided_prefix + "_mos_normal.fits"
				normeachscript.write("import os,re\n")
				normeachscript.write("os.putenv('INSTRUMENT','SUBARU')\n")
				normeachscript.write("os.system(\"rm " + dir + binned_image + "\")\n")	                                                                                                         	
                                normeachscript.write("os.system(\"rm " + dir + binned_normal_image + "\")\n")	
                                normeachscript.write("os.system(\"./create_binnedmosaics.sh " + basedir + " " + enddir + " " +  divided_prefix + " OC 8 -32 \")\n") 
                                normeachscript.write("os.system(\"imstats " + divided_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o " +fildir +  "outlist \")\n") 
                                normeachscript.write("p = open('" + fildir + "outlist').readlines()[-1]\n")	
                                normeachscript.write("mode = re.split('\s+',p)[1]\n")
                                normeachscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + binned_image + " > " + dir + binned_normal_image + "\")\n")

		script.close()
	#os.system(command)

	''' make lists of files to combine together, then combine them '''
        #os.system("ic '%1 %2 /' " + img + " " + flat + " > " + img.replace('.fits','M.fits'))
	#get_date()
	batchfiles.close()

	
		

if __name__ == '__main__':
	import os
	#dir = os.environ['dougdir'] + 'nobackup/SUBARU/skyflats/' 
	#dir = os.environ['skyflatraw'] + 'nobackup/SUBARU/auxilary/W-J-B_SKYFLAT/' 
	#target_dir = os.environ['xoc'] + 'nobackup/SUBARU/skyflats/skyflat_B'
	#runit(dir,target_dir) 
	#raw_input()

	import sys
	filter = sys.argv[1]
	type = sys.argv[2]

	if type == 'domeflat': 
		if filter == 'b':                                                           	
	        	location = os.environ['subdir'] + '2007-07-18_domeflat_b/DOMEFLAT/'
                                                                                             
	        if filter == 'v':
	        	location = os.environ['subdir'] + '2007-07-18_domeflat_v/DOMEFLAT/'
                                                                                             
	        if filter == 'r':
	        	location = os.environ['subdir'] + '2007-07-18_domeflat_r/DOMEFLAT/'
                                                                                             
	        if filter == 'i':
	        	location = os.environ['subdir'] + '2007-07-18_domeflat_i/DOMEFLAT/'
                                                                                             
	        if filter == 'z':
	        	location = os.environ['subdir'] + '2007-07-18_domeflat_z/DOMEFLAT/'

	if type == 'skyflat': 
        	if filter == 'b':                                                           	
                	location = os.environ['subdir'] + '2007-07-18_skyflat_b/SKYFLAT/'
                                                                                             
                                                                                             
                if filter == 'v':
                	location = os.environ['subdir'] + '2007-07-18_skyflat_v/SKYFLAT/'
                                                                                             
                if filter == 'r':
                	location = os.environ['subdir'] + '2007-07-18_skyflat_r/SKYFLAT/'
                                                                                             
                if filter == 'i':
                	location = os.environ['subdir'] + '2007-07-18_skyflat_i/SKYFLAT/'
                                                                                             
                if filter == 'z':
                	location = os.environ['subdir'] + '2007-07-18_skyflat_z/SKYFLAT/'




	combineperiods(6,location,filter,type,'edit')
	''' then need to run ./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${DOUGDIR}/skyflat_10_2 '''
	#os.environ['dougdir'] + 'nobackup/SUBARU/skyflats' +
