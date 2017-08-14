from utilities import *
from numpy import *
import sys,re,os

cluster = sys.argv[1]
inputtable = sys.argv[2]
filters = sys.argv[3:]

filters_dat = [['W-J-B','b',4.031,0],['W-J-V','v',3.128,1],['W-C-RC','r',2.548,2],['W-C-IC','i',1.867,3],['W-S-Z+','z',1.481,4]]

filters_info = []
colors = []
for filter in filters:
	for filter_dat in filters_dat:
		if filter_dat[0] == filter:
			filters_info.append(filter_dat)
			colors.append(filter_dat[1])

#FIX INPUT CATALOGS

cptable = '/tmp/cptable'

inputrenamea = '/tmp/inputa' # 
inputrenameb = '/tmp/inputb' # 
inputrenamec = '/tmp/inputc' # 
inputrenamed = '/tmp/inputd' # 

inputrename1 = '/tmp/input1' # 
inputrename2 = '/tmp/input2' # 
starrename1 = '/tmp/star1' # 
outputtable = '/tmp/output2'
outrename1 = '/tmp/out1'
outrename2 = '/tmp/out2'
outrename3 = '/tmp/out3'
tempfile = '/tmp/tempfile'

os.system('cp ' + inputtable + ' ' + cptable)

#RETRIEVE CALIBRATION INFO
#A2219 [3,2,3,2,2]
vars_fit = [3,2,3,2,2]

vars_fit = [3,2,3,3,3]
cal_dict = get_calibrations(cluster,vars_fit)
print cal_dict

#POPULATE MATRICIES

num = len(filters)

color_matrix = zeros((num,num))

print colors
for filter in filters_info:
	colorminus = re.split('m',cal_dict['COLORUSED_' + filter[1]])
        plus = colorminus[0].lower()
        minus = colorminus[1].lower()
	print plus, minus
	print color_index(filter[1],colors), color_index(plus,colors)
        color_matrix[color_index(filter[1],colors)][color_index(plus,colors)] = 1.	
        color_matrix[color_index(filter[1],colors)][color_index(minus,colors)] = -1.			

color_term = array([cal_dict['COLORTERM_'+x[1]] for x in filters_info])
airmass_term = array([cal_dict['AIRMASSTERM_'+x[1]] for x in filters_info])
i = 0
for filter in filters_info:
	if vars_fit[filter[3]] != 3:
		airmass_term[i] = 0 
	i += 1
print airmass_term

zps = array([cal_dict['ZP_'+x[1]] for x in filters_info])

print color_term, airmass_term, zps, color_matrix

mag_name = 'MAG_AUTO'	
magerr_name = 'MAGERR_AUTO'

list_filt = []
list_filt_pair = []
for filter in colors:
	arr = [[mag_name + "_" + filter , magerr_name + '_' + filter ]]
	list_filt += arr[0] 
	list_filt_pair += arr
list = list_filt + ['SeqNr'] #+ ['Bmag_star','Vmag_star','Rmag_star', 'Imag_star','zmag_star']#+ ['Z_rs','ALPHA_J2000','ALPHA_J2000_rs','DELTA_J2000','DELTA_J2000_rs','OldSeqNr']
keys = reduce(lambda x,y: x + " " + y,list)

command="ldactoasc -b -i " + inputtable + " -t OBJECTS -k " + keys + " > " + tempfile
print command
os.system(command)

output = open(outrename1,'w')
ll = open(tempfile,'r').readlines()
print 'here'
dict = []
output_list = []

assume_color = {'VmR_red':1.2,'VmR_blue':0.3,'RmI_red':1.8,'RmI_blue':0.4,'Imz_red':0.2,'Imz_blue':-0.3}

for line in ll:
	import re
	dict = {}
	res = re.split('\s+',line)
	if res[0] == '': res = res[1:]
	for i in range(len(list)):
		dict[list[i]] = float(res[i])

	#print [dict[mag_name + '_' + x[1]] for x in filters_info]


	for x in  filters_info:
		colorminus = re.split('m',cal_dict['COLORUSED_' + x[1]])
                plus = colorminus[0].lower()
                minus = colorminus[1].lower()
		if dict[mag_name + '_' + plus] > 95 and dict[mag_name + '_' + minus] < 95:
			if assume_color.has_key(plus.upper() + 'm' + minus.upper() + '_red'):
				dict[mag_name + '_' + plus] =  dict[mag_name + '_' + minus] + assume_color[plus.upper() + 'm' + minus.upper() + '_red'] 
		if float(dict[mag_name + '_' + plus]) < 95 and float(dict[mag_name + '_' + minus]) > 95:
			if assume_color.has_key(plus.upper() + 'm' + minus.upper() + '_blue'):
				dict[mag_name + '_' + minus] =  dict[mag_name + '_' + plus] - assume_color[plus.upper() + 'm' + minus.upper() + '_blue'] 

	b_inst = array([float(dict[mag_name + '_' + x[1]]) for x in filters_info])
	airmass = array([dict[mag_name + '_' + x[1]] for x in filters_info])

		

	b_calib = b_inst
	
       
	#print b_calib
 
        for j in range(10):
		#print airmass_term*array(dot(color_matrix,b_calib))* array(dot(color_matrix,b_calib))
		#print color_term * array(dot(color_matrix,b_calib))  
		#print zps
		#print b_inst






        	b_calib = b_inst + airmass_term*array(dot(color_matrix,b_calib))* array(dot(color_matrix,b_calib)) + color_term * array(dot(color_matrix,b_calib)) + zps #+ airmass_term * airmass 

		#print b_calib

        #b_calib = b_inst + zps #airmass_term*array(dot(color_matrix,b_calib))* array(dot(color_matrix,b_calib)) + color_term * array(dot(color_matrix,b_calib)) + zps #+ airmass_term * airmass 

	#b_calib = array([float(dict[x[1].upper() + 'mag_star']) for x in filters_info])
	

        #b_calib = b_inst + color_term * array(dot(color_matrix,b_calib)) + zps #+ airmass_term * airmass 
	
	i = 0
	for filter in colors:	
		dict['calib_' + filter] = b_calib[i]
		output.write(str(dict['calib_' + filter]).replace('nan','999') .replace('inf','999')+ ' ')
		i += 1
	output.write(str(int(dict['SeqNr'])))
	output.write('\n')
	
	output_list.append(dict)

output.close()

asconf = '/tmp/ascout.conf'
asc = open(asconf,'w')
for filter in colors:
	asc.write('#\nCOL_NAME = ' + mag_name + '_color_' + filter + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
	#asc.write('#\nCOL_NAME = ' + mag_name_err + '_color_' + filter + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')

asc.write('#\nCOL_NAME = PhotSeqNr\nCOL_TTYPE= LONG\nCOL_HTYPE= INT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
asc.close()

command = "asctoldac -i " + outrename1 + " -o " + outrename2 + " -t OBJECTS -c " + asconf
print command
os.system(command)

input = reduce(lambda x,y: x + " " + y,[mag_name + '_color_' + filter for filter in colors] + ['PhotSeqNr'])

command = "ldacjoinkey -t OBJECTS -i " + inputtable + " -p " + outrename2 + " -o " + outputtable + " -k " + input
print command
os.system(command)
