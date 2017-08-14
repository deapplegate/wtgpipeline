''' convert radeg to something else '''
def makera(radeg,decdeg):
	gh = {}
	gh['ra'] = str(radeg)
	if float(decdeg) > 0: positive = '+'
	else: positive = '-'
        gh['dec'] = str(abs(float(decdeg)))
        hh =  '%(var)02d' % {'var':int(float(gh['ra'])/(360.0 / 24.0))}
        print hh
        mm =  '%(var)02d' % {'var': int((float(gh['ra']) - float(hh) * (360.0 / 24.0))/(360.0 / (24.0 * 60.0)))}
        print mm
        ss =  '%(var)02d' % {'var':int( (float(gh['ra']) - (360.0/24.0)*( float(hh)+float(mm)/60.0)) /(360.0 / (24.0 * 60.0 * 60.0)))}
        decdd = '%(var)02d' % {'var': int(float(gh['dec'])/(1.0))}
        print decdd
        decmm = '%(var)02d' % {'var': int((float(gh['dec']) - float(decdd) )/( 1. / (60.0)))}
        print decmm
        decss = '%(var)02d' % {'var':int((float(gh['dec']) - float(decdd) - (float(decmm)/60.0))/(1. / ( 60.0 * 60.0)))}
        print gh['ra'], gh['dec']
        ra =  str(hh) + ":" + str(mm) +  ":" + str(ss) 
        dec =  positive + str(decdd) + ":" + str(decmm) +  ":" + str(decss) 
	return ra, dec

''' convert position to degrees '''
def convertpos(agalra, agaldec):
	print agalra, agaldec
        rlist = ['','',''] 
        dlist = ['','',''] 
        rlist[0] = agalra[0:2] 
        rlist[1] = agalra[3:5] 
        rlist[2] = agalra[6:] 
        dsign = agaldec[0]
        dmul = float(dsign + '1')
        dlist[0] = agaldec[1:3] 
        dlist[1] = agaldec[4:6] 
        dlist[2] = agaldec[7:] 
        import string
        print rlist, dlist, dsign
        radeg = (360/24.0)*string.atof(rlist[0]) + (360.0/(24.0*60))*string.atof(rlist[1]) + (360.0/(24.0*60.0*60.0))*string.atof(rlist[2])
        spectrara = radeg
        decdeg = dmul * (string.atof(dlist[0]) + (1/60.0)*string.atof(dlist[1]) + string.atof(dlist[2])*(1/(60.0*60.0))                           )
	print radeg, decdeg
	return radeg, decdeg

import os
os.system('rm temp')
#filt = "(((((Ra>" + str(radeg - 0.33333) + ") AND (Ra<" + str(radeg + 0.33333) + ")) AND (Dec>" + str(decdeg - 0.33333) + ")) AND (Dec<" + str(decdeg + 0.33333) + ")) AND (Umag<90))"
agalra = '22:16:24' #'03:54:38.0'
agaldec = '+00:21:00' #'+00:28:00.0'

radeg, decdeg = convertpos(agalra, agaldec)

position = ["Ra>" + str(radeg - 2.) + ")","Ra<" + str(radeg + 2.) + ")","Dec>" + str(decdeg - 2.) + ")","Dec<" + str(decdeg + 2.) + ")"]
mags = ["Bmag<90)","Vmag<90)","Rmag<90)","Imag<90)"]

filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',mags+position)
print filt
command = 'ldacfilter -i /nfs/slac/g/ki/ki02/xoc/anja/Stetson/Stetson_std_2.0.cat -t STDTAB -o temp -c "' + filt + ';" '
print command
os.system(command)
from glob import glob
out = open('out','w')
if len(glob('temp')) > 0:
	readoutvars = ["Ra","Dec","Bmag","Vmag","Rmag","Imag","Verr","BmVerr","VmRerr","RmIerr","VmIerr"] 
        printoutvars = ["Ra","Dec","Bmag","Vmag","Rmag","Imag","Berr","Verr","Rerr","Ierr"]
        readout = reduce(lambda x,y: x + ' ' + y,readoutvars)
        command = 'ldactoasc -i temp -t STDTAB  -b -k ' + readout + ' > tempstr'
	os.system(command)
	lines = open('tempstr','r').readlines()
	for line in lines:
		import re	
		res = re.split('\s+',line)
		radeg = res[0]
		decdeg = res[1]
		ra, dec = makera(radeg,decdeg)	
		out.write(str(ra) + ' ' + str(dec) + '\n')
