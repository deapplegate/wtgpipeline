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

def get_gabodsid(file): 		
	import os
	command = "dfits " + file + " | grep GABODSID > hh"
	print command
	os.system(command)
	jj = open('hh','r').readlines()
	import re
	date = re.split('\s+',jj[0])[1]
	return date 

def get_date(file): 		
	command = "dfits " + file + " | grep DATE-OBS > hh"
	print command
	os.system(command)
	jj = open('hh','r').readlines()
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
	
def runit(dir):
	import os
	chip_confs = [[[2001,10,18],[2002,9,5],'_10_1'],[[2002,9,5],[2100,1,1],'_10_2']]

	''' split into different chip configurations '''
        from glob import glob
        list = glob(dir + "*fits")

	for chip_conf in chip_confs:
		newdir = os.environ['dougdir'] + "SUBARU/skyflat" + chip_conf[2]
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
	        	                os.system("cp " + file + ' ' + os.environ['dougdir'] + 'nobackup/SUBARU/skyflats' + chip_conf[2] + '/')	
				except: print 'failed'

def combineperiods(interval,dir):
	import os, re
	statsxmin = '500'
	statsxmax = '1500'
	statsymin = '1500'
	statsymax = '2500'
	firstchip = 'yes'
	uu = open('rosetta','w')

	batchfiles = open('batchfiles','w')

	from glob import glob
	
	u2 = open('reject.skyflat','r').readlines()	
	rejectfiles = []
	for line in u2:
		print line
		print re.split('\/',line)
		temp = re.split('\/',line[:-1])[-1]
		out = re.split('_',temp)[0]
		rejectfiles.append(out)
	print rejectfiles		

	list = glob(dir + "*10OC.fits")
        files = []
	badfiles = []
        for line in list:
		print line
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
        print len(files	) , len(badfiles)	
	
	for chipnumber in range(1,11):
		''' first break up images into different epochs '''   
	        month_period = 6	
                from glob import glob
	        print dir + "*" + str(chipnumber) + "OC.fits"
                #list = glob(dir + "*OC.fits")

	        command = "imstats `ls " + dir + "*" + str(chipnumber) + "OC.fits` -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outliststats" + str(chipnumber) 
		print command
		#os.system(command)
		list = open('outliststats' + str(chipnumber),'r').readlines()
	        datelist = []
	        print list
		index = 0
	        for file in list:
			print file
			if file[0] != '#' and file[0] != '':	
				print file
				filename = re.split('\s+',file)[0]	
				bad = 1
				for file2 in files:
					#print filename, file
					if string.find(filename,file2) != -1:
						bad = 0
				if bad == 0:		
					index = index + 1
                			gabodsid = get_gabodsid(filename)       	                                                                      
					print filename
	        	                datelist.append([gabodsid,file[:-1],filename])
       				        command =  "/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/caldate -d 31/12/1998 -i " + gabodsid + " >  temp "  
	                                print command
	                                os.system(command)
				        yy = open('temp','r').readlines()
                                        date = ((re.split('\s+',yy[0])[-2]))
				        uu.write(gabodsid + " " + date + "\n")
				
			#print len(datelist), datelist
	        datelist.sort()	
		rr = open('dates','w')
		for obs in datelist:
			rr.write(str(obs[0]) + ' ' + str(obs[2]) + '\n')
		rr.close()
		raw_input()

		print datelist
		print index
		print datelist
	        
	        limit_up = float(datelist[-1][0])
	        limit_down = float(datelist[0][0])
                                                                                                                                                            
	        ''' a six month period is approximately 30*6=180 days '''
	        
	        diff_year = int((limit_up - limit_down) / 180.0) + 1
	        print diff_year	, limit_up, limit_down
		if 1 == 1: #firstchip == 'yes':                                                                                                                   
	       		''' loop through the periods and make date brackets '''	 
	                brackets = []
	                filelists = {}
	                for i in range(diff_year):
	                	start = limit_down + i * 180
	                	end = limit_down + (i + 1) * 180
	                	brackets.append([start, end])
	                	filelists[str(start) + '_' + str(month_period)] = []
			firstchip = 'no'
                                                                                                                                                            
	        print brackets 
                        
                                                                                                                                    
		filelists['all'] = []
	        ''' go through observations and which time bracket each observation fits into '''
	        for obs in datelist:
	        	filelists['all'].append(obs[1])
	        	for bracket in brackets:	
	        		print bracket, obs
				''' also make a master flat '''
					
			
				''' figure out where the brackets go '''	
	        		if bracket[0] <= float(obs[0])  and float(obs[0]) < bracket[1]: 
	        			filelists[str(bracket[0]) + '_' + str(month_period)].append(obs[1])
                                                                                                                                                            
	        #print filelists
                                           
	        paramslist = [{'method': 'MEDIAN','lo_clip':'3.0 3.0'},{'method': 'CLIPMEAN','lo_clip':'3.0 3.0'},{'method': 'CLIPMEAN','lo_clip':'2.0 2.0'}]
	        for params in paramslist:
			scriptname = 'script' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber)	
		       	outinfo = dir + scriptname  
			script = open(scriptname,'w')
			divscript = open(scriptname + ".py",'w')
		        batchfiles.write('bsub -R rhel40 -q long -e ' + outinfo + ' -o ' + outinfo + ' source ' + scriptname + '\n')
			for key in filelists.keys(): 
	        		file = open(key + '_chip' + str(chipnumber),'w')                              	
	        	        for ele in filelists[key]:
					print ele
	        	        	file.write(ele.replace('1OC.fits',str(chipnumber) + 'OC.fits') + '\n')
	        	        file.close()

	        		''' rescale -s 1 '''
	                        method = params['method'] 
	                        lo_hi_rank = '1 1'
	                        lo_hi_rej = '4000 30000'
	                        lo_hi_clip = params['lo_clip'] 
	        		input_list = key
	        		output_image = key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
	                        command = "imcombflat -i " + input_list + "_chip" + str(chipnumber) + " -o "  + dir + output_image  + " -s 1 -c " + method + " -e " + lo_hi_rank + " -t " + lo_hi_rej + " -l " +  lo_hi_clip

	        		script.write(command + '\n')

	        		divided_image = 'div_' + key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"

	        		#norm_image = 'div_' + key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
	        		norm_image = 'div_' + key + '_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
				normscript.write("os.system(\"imstats " + dir + output_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outlist\")\n") 
                                normscript.write("p = open('outlist').readlines()[-1]\n")	
                                normscript.write("import re\n")
                                normscript.write("mode = re.split('\s+',p)[1]\n")
                                normscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + output_image + " > " + norm_image + " \")\n")





				if key != 'all':	
					''' divide by the comprehensive flat '''                                                                                                                     	
                                                                                                                                                                                                      
	        		        all_image = 'all_' + params['method'] + '_' + params['lo_clip'].replace(' ','_') + "_chip" + str(chipnumber) + ".fits"
					divscript.write("print '" + output_image + "'\n")
                                        divscript.write("import re,os\n")
				        divscript.write("os.system('rm divoutA.fits')\n")
				        divscript.write("os.system('rm divoutB.fits')\n")
	        		        divscript.write("os.system(\"imstats " + dir + output_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outlist\")\n") 
				        divscript.write("p = open('outlist').readlines()[-1]\n")	
				        divscript.write("import re\n")
				        divscript.write("mode = re.split('\s+',p)[1]\n")
				        divscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + output_image + " > divoutA.fits \")\n")
				        divscript.write("os.system(\"imstats " + dir + all_image + " -s " + statsxmin + " " + statsxmax + " " + statsymin + " " + statsymax + " -o outlist\")\n") 
                                        divscript.write("p = open('outlist').readlines()[-1]\n")	
                                        divscript.write("mode = re.split('\s+',p)[1]\n")
                                        divscript.write("os.system(\"ic '%1 \" + mode + \" / ' " + dir + all_image + " > divoutB.fits \")\n")
				        divscript.write("os.system(\"ic '%1 %2 / ' divoutA.fits divoutB.fits > " + dir + divided_image + "\")\n")
				        divscript.write("os.system('rm divoutA.fits')\n")
				        divscript.write("os.system('rm divoutB.fits')\n")
	                        print command
		script.close()

	#os.system(command)

	''' make lists of files to combine together, then combine them '''
        #os.system("ic '%1 %2 /' " + img + " " + flat + " > " + img.replace('.fits','M.fits'))
	#get_date()
	batchfiles.close()

if __name__ == '__main__':
	import os
	dir = os.environ['dougdir'] + 'nobackup/SUBARU/skyflats/' 
	#runit(dir) 
	location = os.environ['subdir'] + 'SUBARU/2007-07-18_skyflat_test/SKYFLAT/'
	combineperiods(6,location)
	''' then need to run ./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${DOUGDIR}/skyflat_10_2 '''
