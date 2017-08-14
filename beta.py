import os
import MySQLdb
import os, sys, anydbm, time
import bashreader
dict = bashreader.parseFile('progs.ini')

table = sys.argv[1]
cluster = sys.argv[2]

tempfile = '/tmp/outkey'
ebvfile = '/tmp/outebv'
os.system('rm ' + ebvfile)
ppid = os.getppid()
command = "ldactoasc -b  -i " + table + " -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > " + ebvfile 
print command
os.system(command)
tempmap = '/tmp/map' #+ str(ppid)
templines = '/tmp/lines' #+ str(ppid)
tempfile = '/tmp/file.cat' #+ str(ppid)
temptable = '/tmp/table.cat' #+ str(ppid)
tempcal = '/tmp/cal.cat' #+ str(ppid)

os.system('cp ' + table + ' ' + temptable)

if 1==1:
        print 'running dust_getval'
        os.system('dust_getval interp=y ipath=/nfs/slac/g/ki/ki03/xoc/pkelly/DUST/maps infile=' + ebvfile + ' outfile=' + tempmap + ' noloop=y') 
        print 'finished'
        command = "gawk '{print $3}' " + tempmap + " > " + templines 
        print command
        os.system(command)
        command = "asctoldac -i " + templines + " -o " + tempfile + " -c " + dict['photconf'] + "/EBV.conf -t OBJECTS  "
        print command
        os.system(command)
        command = "ldacjoinkey -o " + temptable + " -i " + table + " -p " + tempfile + " -t OBJECTS -k EBV" 
        print command
        os.system(command)

db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
c = db2.cursor()
c.execute("describe photometry_db") 
results = c.fetchall()
columns = []
for column in results:
	columns.append(column[0])

filters = [['W-J-B','b',4.031],['W-J-V','v',3.128],['W-C-RC','r',2.548],['W-C-IC','i',1.867],['W-S-Z+','z',1.481]]

for filter in filters:
	long_filter = filter[0]
	short_filter = filter[1]
	extcoeff = filter[2]

	command = "select * from photometry_db where NUMBERVARS=2 AND BONN_FILTER='" + str(long_filter) + "' AND cluster='" + str(cluster) + "'"
        print command
        c.execute(command)
        results = c.fetchall()
	if len(results) > 0:
        
       		print results                                                                                                                    
                use_phot = results[-1]
                
                result_lines = []
                for result in results:
                	line = {}
                        for i in range(len(columns)):
                        	line[columns[i]] = result[i]
                	result_lines.append(line)
                
                use = result_lines[-1]
	
		print use
                
                COLORUSED = use['colorused']	
                COLORTERM = use['COLOR']
                AIRMASSTERM = use['AIRMASS']
                ZP = use['ZP']
               
		mag_name = 'MAG_AUTO'	
		col_name = mag_name + '_cal'
			 
                #command = "ldaccalc -i " + temptable + " -t OBJECTS -c '(" + mag_name + "_" + short_filter + " + " + str(ZP) + " - EBV*" +str(extcoeff) + ");'  -k FLOAT -n " + col_name+ "_" + short_filter + " '' -o " + tempcal

                command = "ldaccalc -i " + temptable + " -t OBJECTS -c '(" + mag_name + "_" + short_filter + " - EBV*" +str(extcoeff) + ");'  -k FLOAT -n " + col_name+ "_" + short_filter + " '' -o " + tempcal
		print command
		os.system(command)
		os.system("mv " + tempcal + " " + temptable)
                #b_calib = b_inst + array(colorterm) * array(dot(color_matrix, b_calib)) + array(airmassterm) * array(airmasses) + zps

os.system("mv " + temptable + " " + tempcal)


u = convert_to_pogson(float(data[els]['psfMag_u']),'u')
g = convert_to_pogson(float(data[els]['psfMag_g']),'g')
r = convert_to_pogson(float(data[els]['psfMag_r']),'r')
i = convert_to_pogson(float(data[els]['psfMag_i']),'i')
z = convert_to_pogson(float(data[els]['psfMag_z']),'z')


uerr = float(data[els]['psfMagErr_u'])      
gerr = float(data[els]['psfMagErr_g'])
rerr = float(data[els]['psfMagErr_r'])
ierr = float(data[els]['psfMagErr_i'])
zerr = float(data[els]['psfMagErr_z'])

data[els]['Bmag'] = u - 0.8116*(u - g) + 0.1313#  sigma = 0.0095
data[els]['Berr'] = math.sqrt( (uerr*0.19)**2. + (0.8119*gerr)**2.) 
#B = g + 0.3130*(g - r) + 0.2271#  sigma = 0.0107

#V = g - 0.2906*(u - g) + 0.0885#  sigma = 0.0129
data[els]['Vmag'] = g - 0.5784*(g - r) - 0.0038#  sigma = 0.0054
data[els]['Verr'] = math.sqrt( (gerr*0.42)**2. + (0.57*rerr)**2.) 

#R = r - 0.1837*(g - r) - 0.0971#  sigma = 0.0106
data[els]['Rmag'] = r - 0.2936*(r - i) - 0.1439#  sigma = 0.0072
data[els]['Rerr'] = math.sqrt( (rerr*0.71)**2. + (0.29*ierr)**2.) 

data[els]['Imag'] = r - 1.2444*(r - i) - 0.3820#  sigma = 0.0078
data[els]['Ierr'] = math.sqrt( (rerr*0.24)**2. + (1.244*ierr)**2.) 
