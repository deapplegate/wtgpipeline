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
agalra = '22:16:29' #'03:54:38.0'
agaldec = '-00:19:02' #'+00:28:00.0'
convertpos(agalra,agaldec)
