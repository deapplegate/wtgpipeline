from utilities import *
from numpy import *
import sys,re,os

cluster = sys.argv[1]
inputtable = sys.argv[2]
starcat = sys.argv[3]
filters = sys.argv[4:]

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
outputtable = '/tmp/output'
outrename1 = '/tmp/out1'
tempfile = '/tmp/tempfile'

os.system('cp ' + inputtable + ' ' + cptable)

for filter in colors:
	command="ldactoasc -i " + cptable + " -b -s -k MAG_APER_" + filter + " MAGERR_APER_" + filter + " -t OBJECTS > " + inputrenamea 
        os.system(command)
        command = "asctoldac -i " + inputrenamea + " -o " + inputrenameb + " -t OBJECTS -c ./photconf/MAG_APER.conf"
        os.system(command)

	a = ["MAG_APER" + str(i) + " MAG_APER" + str(i) + "_" + filter for i in range(1,7)]   	
	b = ["MAGERR_APER" + str(i) + " MAGERR_APER" + str(i) + "_" + filter for i in range(1,7)]
	line = a + b

	print line

	for ele in line:
		command = "ldacrenkey -i " + inputrenameb + " -o " + inputrenamec + " -k " +ele 
	        print command
	        os.system(command)
		os.system('cp ' + inputrenamec + " " + inputrenameb)

	
	input = reduce(lambda x,y: x + " " + y,["MAG_APER" + str(i) + "_" + filter + " MAGERR_APER" + str(i) + "_" + filter for i in range(1,7)])


        command = "ldacjoinkey -t OBJECTS -i " + cptable + " -p " + inputrenamec + " -o " + inputrenamed + " -k " + input
	print command
	os.system(command)
	os.system("cp " + inputrenamed + " " + cptable)


''' filter for stars '''
command="ldacfilter -i " + cptable + " -c '(CLASS_STAR > 0.95);' -t OBJECTS -o " + inputrename1 
print command
os.system(command)

command = "ldacrentab -i " + inputrename1 + " -t OBJECTS STDTAB FIELDS NULL -o " + inputrename2
print command
os.system(command)
#command = "ldacrenkey -i " + starcat + " -t STDTAB -k Ra ALPHA_J2000 Dec DELTA_J2000 -o " + starrename1
#print command
#os.system(command)

#MATCH
command = "match.sh " + outputtable + " STDTAB " + starcat + " star " +  inputrename2 + " # "
print '\n'
print command

raw_input()

command="ldacfilter -i " + outputtable + " -c '(ALPHA_J2000 != 0 AND ALPHA_J2000_star != 0);' -t STDTAB -o " + outrename1 
print command
os.system(command)

command = "ldactoasc -b  -i " + outrename1 + " -t STDTAB -k ALPHA_J2000 DELTA_J2000 > matchpos " 
print command
os.system(command)

#RETRIEVE CALIBRATION INFO
#A2219 [3,2,3,2,2]
#vars_fit = [3,2,3,2,2]

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



mag_name = 'MAG_APER2'	
magerr_name = 'MAGERR_APER2'

list_filt = []
list_filt_pair = []
for filter in colors:
	arr = [[mag_name + "_" + filter , magerr_name + '_' + filter ]]
	list_filt += arr[0] 
	list_filt_pair += arr
list = list_filt + ['Bmag_star','Vmag_star','Rmag_star', 'Imag_star','zmag_star']#+ ['Z_rs','ALPHA_J2000','ALPHA_J2000_rs','DELTA_J2000','DELTA_J2000_rs','OldSeqNr']
keys = reduce(lambda x,y: x + " " + y,list)

command="ldactoasc -b -i " + outrename1 + " -t STDTAB -k " + keys + " > " + tempfile
print command
os.system(command)

ll = open(tempfile,'r').readlines()
print 'here'
dict = []
output_list = []
for line in ll:
	import re
	dict = {}
	res = re.split('\s+',line)
	if res[0] == '': res = res[1:]
	for i in range(len(list)):
		dict[list[i]] = res[i]

	print [dict[mag_name + '_' + x[1]] for x in filters_info]

	b_inst = array([float(dict[mag_name + '_' + x[1]]) for x in filters_info])
	airmass = array([dict[mag_name + '_' + x[1]] for x in filters_info])

	b_calib = b_inst
	
       
	print b_calib
 
        for j in range(10):
        	b_calib = b_inst + airmass_term*array(dot(color_matrix,b_calib))* array(dot(color_matrix,b_calib)) + color_term * array(dot(color_matrix,b_calib)) + zps #+ airmass_term * airmass 
        	print b_calib


	#b_calib = array([float(dict[x[1].upper() + 'mag_star']) for x in filters_info])
	

        #b_calib = b_inst + color_term * array(dot(color_matrix,b_calib)) + zps #+ airmass_term * airmass 
	

	i = 0
	for filter in colors:	
		dict['calib_' + filter] = b_calib[i]
		i += 1
	
	output_list.append(dict)

	#raw_input()
# now write out calibrated magnitudes

#for val in list_out:
#	outkey.write(str(val) + '\n')
#
#
#outkey.close()
#
#command = "asctoldac -i " + tempfile + " -o " + tempfile + ".cat -c " + dict['photconf'] + "/EBV.conf -t OBJECTS  "
#os.system(command)
#
#command = "ldacjoinkey -o test -i " + table + " -p " + tempfile + ".cat -t OBJECTS -k EBV" 
#os.system(command)
#

import sys, re

from ppgplot   import *
file = sys.argv[1]

x = []
y = []

#file = outfile+".ps"
#pgbeg(file+"/cps",1, 1)
pgbeg("/XWINDOW",1,1)
                         
pgiden()
from Numeric import *

x = []
y = []
for dict in output_list:
	x_val = float(dict['Vmag_star']) - float(dict['Rmag_star'])
	y_val = float(dict['Rmag_star']) - float(dict['Imag_star'])
	if -50 < x_val < 50 and -50 < y_val < 50:
		x.append(x_val)		
	        y.append(y_val)

import copy 
plotx = copy.copy(x)
ploty = copy.copy(y)
x.sort()	
y.sort()
#print plotx
#print x[0], x[-1], y[0], y[-1]

pgswin(x[30],x[-30],y[30],y[-30])
plotx = array(plotx)
ploty = array(ploty)
#pylab.scatter(z,x)
pglab('V-R','R-I','')
pgbox()
#print plotx, ploty
pgsci(2)
pgpt(plotx,ploty,1)

#raw_input()

x = []
y = []
for dict in output_list:
	x_val = float(dict['calib_v']) - float(dict['calib_r'])
	y_val = float(dict['calib_r']) - float(dict['calib_i'])
	if -50 < x_val < 50 and -50 < y_val < 50:
		x.append(x_val)		
	        y.append(y_val)
plotx = array(x)
ploty = array(y)
pgsci(3)
pgpt(plotx,ploty,1)

raw_input()


command = "ldactoasc -b  -i  ldactoasc -i /nfs/slac/g/ki/ki02/xoc/anja/Stetson/Stetson_std_2.0.cat -t STDTAB -k Bmag Vmag Rmag Imag > ./ldac_tmp2" 
os.system(command)

lines = open('./ldac_tmp2','r').readlines()
x = []
y = []
z = []
err = []

for line in lines:
	spt = re.split('\s+',line)
	b = float(spt[0])
	v = float(spt[1])
	r = float(spt[2])
	i = float(spt[3])
	if -10 < b-v < 10 and -10 < v-r < 10:		
		print spt
		x.append(v-r)

		y.append(r-i)

		#err.append(sdss_error)

x2 = x[0:3000]
y2 = y[0:3000]

plotx = array(x2)
ploty = array(y2)
pgsci(4)
pgpt(plotx,ploty,1)
pgend()




