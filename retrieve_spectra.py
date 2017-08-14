def convert_to_pogson(magnitude,filter):
	from math import *
	b_values = {'u':1.4E-10,'g':0.9E-10,'r':1.2E-10,'i':1.8E-10,'z':7.4E-10}
	b = b_values[filter]
	try:
		flux_ratio = sinh(-1.*log(10)*magnitude/2.5 - log(b))*2*b	
	except: flux_ratio = -99
	#print flux_ratio

	if flux_ratio > 0:
	        pogson_magnitude = -2.5 * log10(flux_ratio)
	else: pogson_magnitude = -999

	#print pogson_magnitude, magnitude
	
	return pogson_magnitude


''' make sure we have a clean sample of SDSS stars '''
def inspect_flags(flags1,flags2):

	flcodes = {'PEAKCENTER':[1,5],'NOTCHECKED':[1,19],'DEBLEND_NOPEAK':[2,14],'PSF_FLUX_INTERP':[2,15],'BAD_COUNTS_ERROR':[2,8],'INTERP_CENTER':[2,12],'CR':[1,12],'BINNED1':[1,28],'BRIGHT':[1,1],'SATURATED':[1,18],'EDGE':[1,2],'BLENDED':[1,3],'NODEBLEND':[1,6],'NOPROFILE':[1,7]}

	good = 1

	for i in range(5):
        	
		dict = {}	

		if (int(flag) & 2**n): flag_up_2.append(n)	
                                                           
	        for fl in flcodes.keys():
	        	flag_num = flcodes[fl][0]
	        	bit_num = flcodes[fl][0]
			flags = [flags1[i],flags2[i]]
			dict[fl] = flags[flag_num] & 2**int(bit_num)
				
		
		print dict	

	        good = 1
	return good



		
import os, sys, anydbm, time
img = sys.argv[1]
outcat = sys.argv[2]
print img
os.system("rm outim")
os.system('rm ' + outcat)
os.system('rm sdss_out')

import commands, string
command = 'dfits ' + img + ' | fitsort -d CD2_1'
print command
print commands.getoutput(command)
if string.find(commands.getoutput(command),'KEY') == -1:
	imcom = "dfits " + img + " | fitsort CRPIX1 CRPIX2 CRVAL1 CRVAL2 CD2_1 CD1_2 > ./outim"
else:
	imcom = "dfits " + img + " | fitsort CRPIX1 CRPIX2 CRVAL1 CRVAL2 CDELT1 CDELT2 > ./outim"

print imcom
os.system(imcom)
import re
print open('outim','r').readlines()
com = re.split('\s+',open("outim",'r').readlines()[1][:-1]  )
print com
crpix1 = float(com[1])
crpix2 = float(com[2])
crval1 = float(com[3])
crval2 = float(com[4])
cdelt1 = float(com[5])
cdelt2 = float(com[6])
print crpix1, crval1, cdelt1
#ramin = crval1 - crpix1*cdelt1 

ramin = crval1 - 9000*cdelt1 
print ramin
ramax = crval1 + 9000*cdelt1
if ramax < ramin: 
	top = ramin
	ramin = ramax
	ramax = top

decmin = crval2 - 9000*cdelt2 
decmax = crval2 + 9000*cdelt2
import sqlcl
#lines = sqlcl.query("select ra,dec,u,g,r,i,z from star").readlines()

flags =  reduce(lambda x,y: x + ' AND ' + y, ["   ((flags_" + color + " & 0x10000000) != 0) \
        AND ((flags_" + color + " & 0x8100000800a4) = 0) \
    AND (((flags_" + color + " & 0x400000000000) = 0) or (psfmagerr_" + color + " <= 0.2)) \
       AND (((flags_" + color + " & 0x100000000000) = 0) or (flags_" + color + " & 0x1000) = 0) \
 AND (flags_" + color + " & dbo.fPhotoFlags('BLENDED') = 0) " for color in ['u','g','r','i','z']])




query = "select ra,dec,z, zConf from SpecObj where   ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " AND z < 1.5 AND zConf > 0.90 " # AND flags & dbo.fPhotoFlags('BLENDED') = 0 "# AND   " + flags 


#query = "select clean, ra,dec,raErr,decErr,objID,rowcErr_u,colcErr_u,rowcErr_g,colcErr_g,rowcErr_r,colcErr_r,rowcErr_i,colcErr_i,rowcErr_z,colcErr_z,psfMag_u,psfMag_g,psfMag_r,psfMag_i,psfMag_z,psfMagErr_u,psfMagErr_g,psfMagErr_r,psfMagErr_i,psfMagErr_z,flags_u,flags_g,flags_r,flags_i,flags_z, flags from star where   ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " AND flags & dbo.fPhotoFlags('BLENDED') = 0 "# AND   " + flags 

print query
#query = "select top 10 flags_u, flags2_u from star where ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " "\

#query = "select top 10 psfMagu, psfMagg, psfMagr, psfMagi, psfMagz, from star where ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " "
print query

lines = sqlcl.query(query).readlines()
uu = open('store','w')
import pickle
pickle.dump(lines,uu)

#import pickle
#f=open('store','r')
#m=pickle.Unpickler(f)
#lines=m.load()


#raw_input()
columns = lines[0][:-1].split(',')
print columns
data = []
print columns 

for line in range(1,len(lines[1:])+1): 
	dt0 = {}
	for j in range(len(lines[line][:-1].split(','))): dt0[columns[j]] = lines[line][:-1].split(',')[j]
	#print line
	import string
	if string.find(lines[line][:-1],'font') == -1: 
		data.append(dt0)
	#if string.find(lines[line][:-1],'font') != -1: 
		#print lines[line][:-1]
		#raw_input()

print len(data)
print len(data[0])


outwrite = open('sdss_out','w')
print len(data)


query = "select ra,dec,z, zConf from SpecObj where   ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " AND z < 1.5 AND zConf > 0.90 " # AND flags & dbo.fPhotoFlags('BLENDED') = 0 "# AND   " + flags 

keys = ['Nr',['dec','Dec'],['ra','Ra'],['z','Z'],['zConf','ZConf']]
seqnr = 1
for els in range(len(data)): 
		seqnr += 1 
		data[els]['Nr'] = seqnr

	        lineh = ""	
	        #print data[els]
		if 1 == 1: # data[els]['clean'] == 0:  #inspect_flags([data[els]['flags_u'],data[els]['flags_g'],data[els]['flags_r'],data[els]['flags_i'],data[els]['flags_z']],[data[els]['flags2_u'],data[els]['flags2_g'],data[els]['flags2_r'],data[els]['flags2_i'],data[els]['flags2_z']]):

			#print keys
			#raw_input()
	       		for key in keys:                                                                             
			        print key	
				if type(key) == type([]):	
					key_dict = key[0]
					key  = key[1]
				else: 
					key_dict = key
		        	if (key == 'SeqNr' or key_dict=='ra' or key_dict=='dec' or key[0:3] == 'Fla'): 
		        		num = '%(s)s' % {'s' : str(data[els][key_dict])}
		        	else:
		        		num = '%(num).4f' % {'num' : float(data[els][key_dict])}
		        		num = '%s' % num
				num.strip()
		        	#elif key[0:2] != 'ra' and key[0:3] != 'dec': 
		        		#yy = ''
		        		#for y in range(128):
		        		#	if y < len(str(data[els][key])):
		        		#		yy = yy + str(data[els][key])[y]
		        		#	else:
		        		#		yy = yy + ' '
		        		#num = yy 
		        	#else: num = str(data[els][key])
	                	lineh = lineh + num  + " "
	                #print lineh
	                outwrite.write(lineh + "\n")
outwrite.close()

#lineh= "lc -C -B "
#for key in data[els].keys():
#	lineh = lineh + " -N '1 1 " + str(key) + "' "
#lineh = lineh + " < outwrite > outf.cat"
#print lineh
#os.system(lineh)

asc = open('asctoldac_spectra.conf','w')
asc.write('VERBOSE = DEBUG\n')
for column in keys: 
	if type(column) == type([]):	
		name = column[1]
	else: name = column 
	if column == 'objID' or column[0:3] == 'fla': 
		type_var = 'STRING'
		htype_var = 'STRING'
		depth = '128'
	elif column == 'Flag':
		type_var = 'SHORT'
		htype_var = 'INT'
		depth = '1'
	elif column == 'SeqNr':
		type_var = 'LONG'
		htype_var = 'INT'
		depth = '1'
	elif len(column) ==2: #column == 'Ra' or column == 'Dec':
		type_var = 'DOUBLE'
		htype_var = 'FLOAT'
		depth = '1'
	else: 
		type_var = 'FLOAT'
		htype_var = 'FLOAT'
		depth = '1'
        print name, type_var, htype_var, depth                    
	asc.write('#\nCOL_NAME = ' + name + '\nCOL_TTYPE= ' + type_var + '\nCOL_HTYPE= ' + htype_var + '\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= ' + depth + '\n')

	
asc.close()	

command = "asctoldac -i sdss_out -c asctoldac_spectra.conf -t OBJECTS -o " + outcat
os.system(command)
print command
