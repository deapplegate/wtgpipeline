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
				#raw_input()

def combineperiods(interval,dir):
	import os

	''' first break up images into different epochs '''
	month_period = 6	
        from glob import glob
	print dir + "*OC.fits"
        list = glob(dir + "*OC.fits")
	datelist = []
	print list
	for file in list:
        	(year, month, day) = get_date(file) 
		datelist.append([year,month,day,file])

	datelist.sort()	
	limit_up = datelist[0]
	limit_down = datelist[-1]

	year_percent = month_period / 12.0
	diff_year = int(limit_up[0] - limit_down[0] + (limit_up[1] - limit_down[1]) / 12.0) + 1
	
	print diff_year	

	''' loop through the periods and make date brackets '''	
	year = limit_down[0]	
	month = limit_down[1]
	start = [year, month, 1] 
	brackets = []
	filelists = {}
	for i in range(diff_year):
		month_end = (start[0] + month_period) 
		if month_end > 12: 
			month_end = month_end - 12
			year = year + 1
		end = [year, month_end, 1] 
		brackets.append([start, end])
		filelists[str(start[0]) + '_' + str(start[1]) + '_' + str(start[2]) + '_' + str(month_period)] = []
		import copy
		start = copy.deepcopy(end)

	''' go through observations and which time bracket each observation fits into '''
	for obs in datelist:
		for bracket in brackets:	
			if inside([obs[0],obs[1],obs[2]],bracket[0],bracket[1]):
				filelists[str(bracket[0]) + '_' + str(bracket[1]) + '_' + str(bracket[2]) + '_' + str(month_period)].append(obs[3])

	paramslist = [{'method': 'MEAN','lo_clip':'3.0 3.0'},{'method': 'CLIPMEAN','lo_clip':'3.0 3.0'},{'method': 'CLIPMEAN','lo_clip':'2.0 2.0'}]

	script = open('script','w')

	for key in filelists.keys():
		file = open(key,'r')
		for ele in filelists[key]:
			file.write(ele + '\n')
		file.close()

		for params in paramslist:
			''' rescale -s 1 '''
	                method = params['method'] 
	                lo_hi_rank = '1 1'
	                lo_hi_rej = '4000 30000'
	                lo_hi_clip = params['lo_clip'] 
			input_list = key
			output_image = key + '_' + params['method'] + '_' + params['lo_clip'] + ".fits"
	                command = "imcombflat -i " + input_list + " -o " + output_image + " -s 1 -c " + method + " -e " + lo_hi_rank + " -t " + lo_hi_rej + " -l " +  lo_hi_clip
			script.write(command + '\n')
	                print command

	script.close()

	#os.system(command)

	''' make lists of files to combine together, then combine them '''
        #os.system("ic '%1 %2 /' " + img + " " + flat + " > " + img.replace('.fits','M.fits'))
	#get_date()

if __name__ == '__main__':
	import os
	dir = os.environ['dougdir'] + 'nobackup/SUBARU/skyflats/' 
	#runit(dir) 
	location = os.environ['subdir'] + 'SUBARU/2007-07-18_skyflat_test/SKYFLAT/'
	combineperiods(6,location)
	''' then need to run ./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${DOUGDIR}/skyflat_10_2 '''
