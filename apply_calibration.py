''' dynamically generates configuration file '''
def make_conf(colors,pipelinedir):
	single_col = [['Ra','Ra'],['Dec','Dec'],['Xpos','Xpos'],['Ypos','Ypos'],['PosErr','PosErr'],['FIELD_POS','Field'],['Flag','Flag']]
	all_col = [['MAG_AUTO','mag'],['MAGERR_AUTO','err'],['Flag','flag'],['MaxVal','maxval'],['AIRMASS','airmass'],['COLORMIN','colormin'],['COLORPLU','colorplu']]
	three_methods = [['ZP','zeropoint'],['COL','colorterm'],['COEFF','airmasscoeff']]

	out = open(pipelinedir + '/photconf/test_ssc','w')
	out.write('MAKE_PAIRS=NO\n')

	for col in single_col:	
		out.write('#\nCOL_NAME = ' + col[1] + '\n')
		out.write('COL_INPUT = ' + col[0] + '\n')
		out.write('COL_MERGE = AVERAGE\n')
		out.write('COL_CHAN = 0\n')

	i = 0
	dict = {}
	for c in ['B','V','R','I','z']:
		dict[c] = str(i)
		i += 1

	for color in colors:
		for col in all_col:	                       	
                	out.write('#\nCOL_NAME = ' + color + col[1] + '\n')
                	out.write('COL_INPUT = ' + col[0] + '\n')
                	out.write('COL_MERGE = AVERAGE\n')
                	out.write('COL_CHAN = ' + dict[color] + '\n')
		for num in [1,2,3]:
	       		for col in three_methods:	                     
                        	out.write('#\nCOL_NAME = ' + color + col[1] + str(num) + '\n')
                        	out.write('COL_INPUT = ' + col[0] + str(num) + '\n')
                        	out.write('COL_MERGE = AVERAGE\n')
                        	out.write('COL_CHAN = ' + dict[color] + '\n')
	out.close()

def color_index(color, colors):
	i = 0
	for c in colors:
		if c == color: 
			break
		i += 1
	return i

def calibrate_magnitudes(row,colors,kind_calib):
	if kind_calib == 'no_color':
		magnitudes = []
		for color in colors: 
			row[color +'mag'] = float(row[color +'mag']) + float(row[color + 'zeropoint' + kind_calib])	
			row['calib'] = 'yes'
			
		return row

	# not finished yet
	if kind_calib == 'color':
		import numpy                                                                    	
	        #first construct color matrix
	        color_matrix = numpy.zeros((len(colors),len(colors)))

		zps = numpy.zeros(1,len(colors))		
                colorterm = numpy.zeros(len(colors),1)
                airmassterm = numpy.zeros(len(colors),1)		

		cindex = 0
	        for color in colors:
			cindex += 1
	        	import re
	        	colorminus = re.split('m',row[color + 'colorcal'])
	        	plus = colorminus[0]
	        	minus = colorminus[1]
	        	color_matrix[color_index(color,colors)][color_index(plus,color)] = 1.	
	        	color_matrix[color_index(color,colors)][color_index(minus,color)] = -1.	
			
			zps[0][cindex] = float(row[color + 'zeropoint3' ])
			colorterm[0][cindex] = float(row[color + 'colorterm3' ])
			airmassterm[0][cindex] = float(row[color + 'airmasscoeff3' ])
		
		for j in range(10):	
			b_calib = b_inst + colorterm * color_matrix * b_inst + airmassterm * airmasses + zps
			b_inst = b_calib



import sys, os, re
#print 'You need to run this from the BASH shell and source progs.ini first OR set up the right environmental variables'
cluster = sys.argv[1] #FULL PATH i.e. MACS0025-12
pipelinedir = sys.argv[2]
#targetimage = sys.argv[3]
caldir = '/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/' + cluster + '/CALIBRATION/'
kind_calib = 'no_color'
PHOTOCONF = pipelinedir + os.environ['PHOTCONF'][1:]
# need to read in the color used in the fit for each band i.e. (B-V) for B band
colors = ['B','V','R'] #,'I','z']
make_conf(colors,pipelinedir)
os.system('source progs.ini')

#move to processed cluster directory
for color in colors:
	os.chdir(caldir)
	os.chdir(color)
	#need to paste together catalogs after astrometry has been applied -- this is catalog cat5
	os.system('rm merge_*')
       	command = 'ldacpaste -i *cat7 -o merge_chips.cat'	
	print command
	os.system(command)
        #now need to join together the OBJECTS and FIELDS tables with make_join
	command = 'make_join -i merge_chips.cat -o merge_join.cat -c ' + PHOTOCONF + '/make_join_3SEC.conf'
	print command + '\n\n\n\n'
      	os.system(command) 
       	#os.system('ldacrentab -i merge_temp_join.cat5 -o merge_join.cat5 -t OBJECTS STDTAB')

os.chdir(caldir)
	 
#then need to ASSOCIATE and MAKE_SSC


os.system('rm ' + caldir + 'pairs*cat')
filelist = [ caldir + '/'+y+'/merge_join.cat' for y in colors]
filelist_assoc = [caldir + '/'+y+'/merge_assoc.cat' for y in colors]
for file in filelist_assoc: os.system('rm ' + file)
filelist = reduce(lambda x,y: x + ' ' + y,filelist)
filelist_assoc = reduce(lambda x,y: x + ' ' + y,filelist_assoc)
print filelist 

command = 'associate -i ' + filelist + ' -t OBJECTS -o ' + filelist_assoc + ' -c ' + PHOTOCONF + '/fullastrom.conf.associate' #/std.conf.associate'
print command

print '\n\n\n\n'
os.system(command)
command = 'make_ssc -i ' + filelist_assoc + ' -o pairs.cat -t OBJECTS  -c ' + PHOTOCONF + '/test_ssc' #'/fullastrom.make_ssc.pairs'
print command
os.system(command)
#filter stars to make sure only using unsaturated well extracted magnitudes
colors_mag = ['' + x + 'mag != 0) ' for x in colors] 
colors_mag_2 = ['' + x + 'mag < 99) ' for x in colors] 
colors_flag = ['' + x + 'flag = 0)' for x in colors] 
colors_maxval = ['' + x + 'maxval < 25000)' for x in colors] 
filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',colors_mag + colors_mag_2 + colors_flag + colors_maxval)
command = '/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/ldacfilter -i ' + caldir + '/pairs.cat -t PSSC -o ' + caldir + '/pairs.filt.cat -c "' + filt + ';"'
print command
os.system(command)

#then read out

#now need to read 
os.chdir(pipelinedir)
command = "ldactoasc  -i " + caldir + "/pairs.filt.cat -t PSSC > ./ldac_tmp" 
print command + '\n\n\n'
os.system(command)

k = open('./ldac_tmp','r').readlines()
#for line in ldac_tab:

list = []
import re
# READ IN COLUMN INFO
for each in k:
	tt = re.split('\s+',each[:-1])
	if tt[0] == '': tt = tt[1:]            	
	if tt[0] == "#":
		list.append([int(tt[1]),tt[2]])

# READ IN DATA
data = []
for each in k:
	tt = re.split('\s+',each[:-1])
	if tt[0] == '': tt = tt[1:]
	if tt[0] != "#":
		pp = {}                                       	
	        for ele in list:
	        	pp[ele[1] ] =  tt[ele[0] - 1]
	        data.append(pp)

color_keys = [x + 'mag' for x in colors]
errs_keys = [x + 'err' for x in colors]
keys = ['Ra','Dec'] + color_keys + errs_keys

os.chdir(pipelinedir)
print data[0] 
cal_data = []
ofile = open('calcat.txt','w')
for row in data:
	rw = calibrate_magnitudes(row,colors,kind_calib)
	line  = reduce(lambda x,y: x + ' ' + y, [str(rw[key]) for key in keys])
	print line
	ofile.write(line + '\n')
ofile.close()

asc = open('asctoldac_phot.conf','w')
asc.write('VERBOSE = DEBUG\n')
for column in keys: 
	if len(column) == 2:	
		name = column[1]
	else: name = column 
	if column == 'objID' or column[0:3] == 'fla': 
		type = 'STRING'
		htype = 'STRING'
		depth = '128'
	elif column == 'Flag':
		type = 'SHORT'
		htype = 'INT'
		depth = '1'
	else: 
		type = 'FLOAT'
		htype = 'FLOAT'
		depth = '1'
	asc.write('#\nCOL_NAME = ' + name + '\nCOL_TTYPE= ' + type + '\nCOL_HTYPE= ' + htype + '\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= ' + depth + '\n')

	
asc.close()	

command = "asctoldac -i calcat.txt
