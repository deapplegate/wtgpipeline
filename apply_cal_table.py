


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
               
		mag_name = 'MAG_AUTO_color'	
		col_name = mag_name + '_dust'
			 
                #command = "ldaccalc -i " + temptable + " -t OBJECTS -c '(" + mag_name + "_" + short_filter + " + " + str(ZP) + " - EBV*" +str(extcoeff) + ");'  -k FLOAT -n " + col_name+ "_" + short_filter + " '' -o " + tempcal

                command = "ldaccalc -i " + temptable + " -t OBJECTS -c '(" + mag_name + "_" + short_filter + " - EBV*" +str(extcoeff) + ");'  -k FLOAT -n " + col_name+ "_" + short_filter + " '' -o " + tempcal
		print command
		os.system(command)
		os.system("mv " + tempcal + " " + temptable)
                #b_calib = b_inst + array(colorterm) * array(dot(color_matrix, b_calib)) + array(airmassterm) * array(airmasses) + zps

os.system("mv " + temptable + " " + tempcal)









