
def add_stars(radeg, decdeg, out):
	import os
        os.system('rm temp')
        #filt = "(((((Ra>" + str(radeg - 0.33333) + ") AND (Ra<" + str(radeg + 0.33333) + ")) AND (Dec>" + str(decdeg - 0.33333) + ")) AND (Dec<" + str(decdeg + 0.33333) + ")) AND (Umag<90))"
        
        position = ["Ra>" + str(radeg - 0.33333) + ")","Ra<" + str(radeg + 0.33333) + ")","Dec>" + str(decdeg - 0.33333) + ")","Dec<" + str(decdeg + 0.33333) + ")"]
        mags = ["Bmag<90)","Vmag<90)","Rmag<90)","Imag<90)"]
        
        filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',mags+position)
        print filt
        command = 'ldacfilter -i /nfs/slac/g/ki/ki02/xoc/anja/Stetson/Stetson_std_2.0.cat -t STDTAB -o temp -c "' + filt + ';" '
        print command
        os.system(command)
	from glob import glob
	if len(glob('temp')) > 0:
       		readoutvars = ["Ra","Dec","Bmag","Vmag","Rmag","Imag","Verr","BmVerr","VmRerr","RmIerr","VmIerr"] 
                printoutvars = ["Ra","Dec","Bmag","Vmag","Rmag","Imag","Berr","Verr","Rerr","Ierr"]
                readout = reduce(lambda x,y: x + ' ' + y,readoutvars)
                command = 'ldactoasc -i temp -t STDTAB  -b -k ' + readout + ' > tempstr'
                print command
                os.system(command)
                templines = open('tempstr','r').readlines()
                from math import *
                for line in templines:
                	import re
                	spt = re.split('\s+',line)
                	dict = {}
                	index = 0
                	for var in readoutvars:
                		dict[var] = float(spt[index])
                		index += 1
                	dict['Berr'] = sqrt(dict['BmVerr']**2. - dict['Verr']**2.)
                	dict['Rerr'] = sqrt(dict['VmRerr']**2. - dict['Verr']**2.)
                	dict['Ierr'] = sqrt(dict['VmIerr']**2. - dict['Verr']**2.)
                	for vari in printoutvars: 
                		if vari == 'Ra' or vari == 'Dec': 
                			stva = '%(num).9f' % {'num':dict[vari]}
                		else: 
                			stva = '%(num).4f' % {'num':dict[vari]}
                
                		out.write(stva + ' ')
                	out.write('\n')
        
        	

def add_sdss_stars(radeg,decdeg,out_sdss,sdss_fields):
	import sqlcl
        #lines = sqlcl.query("select ra,dec,u,g,r,i,z from star").readlines()                                                                                                                                         
	ramin = (radeg - 0.33333) 
	ramax = (radeg + 0.33333)
	decmin = (decdeg - 0.33333)
	decmax = (decdeg + 0.33333)                                                                                                                                           		
        query = "select clean, ra,dec,raErr,decErr,objID,psfMag_u,psfMag_g,psfMag_r,psfMag_i,psfMag_z,psfMagErr_u,psfMagErr_g,psfMagErr_r,psfMagErr_i,psfMagErr_z,flags_u,flags_g,flags_r,flags_i,flags_z from star where ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + "    \
            AND ((flags & 0x10000000) != 0) \
                AND ((flags & 0x8100000800a4) = 0) \
            AND (((flags & 0x400000000000) = 0) or (psfmagerr_g <= 0.2)) \
               AND (((flags & 0x100000000000) = 0) or (flags & 0x1000) = 0) \
         "
        
        #query = "select top 10 flags_u, flags2_u from star where ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " "\
        
        #query = "select top 10 psfMagu, psfMagg, psfMagr, psfMagi, psfMagz, from star where ra between " + str(ramin)[:8] + " and  " + str(ramax)[:8] + " and  dec between " + str(decmin)[:8] + " and " +str(decmax)[:8]  + " "
        print query
        
        lines = sqlcl.query(query).readlines()
        uu = open('store','w')
        import pickle
        pickle.dump(lines,uu)
        
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
	if len(data) > 0:	
		sdss_fields.write(str(radeg) + " " + str(decdeg) + " 0.3333333 0.3333333\n")
       		print len(data)                                                
                
                seqnr = 1
                for els in range(len(data)): 
                	if 1==1: #data[els].has_key('u'):
                
                		import math
                
                		ra = data[els]['ra']      
                		dec = data[els]['dec']      
                		u = data[els]['psfMag_u']      
                                g = data[els]['psfMag_g']
                                r = data[els]['psfMag_r']
                                i = data[els]['psfMag_i']
                                z = data[els]['psfMag_z']
                		uerr = data[els]['psfMagErr_u']      
                                gerr = data[els]['psfMagErr_g']
                                rerr = data[els]['psfMagErr_r']
                                ierr = data[els]['psfMagErr_i']
                                zerr = data[els]['psfMagErr_z']
                                                                               
	        		vars = [ra,dec,u,g,r,i,z,uerr,gerr,rerr,ierr,zerr]
	        		varsstr = reduce(lambda x,y: x + ' ' + y,vars)
	        		out_sdss.write(varsstr + '\n')

	
out = open('catout','w')
out_sdss = open('catout.sdss','w')
sdss_fields = open('sdssfields','w')
herve = open('herve','r').readlines()
import re
for line in herve: 
	spt = re.split('\s+',line)
	print '########################## ' + spt[2] + ' ########################'
	#add_stars(float(spt[0]),float(spt[1]),out)
	add_sdss_stars(float(spt[0]),float(spt[1]),out_sdss,sdss_fields)
