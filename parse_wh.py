f = open('whmosaic.txt','r').readlines()
fout = open('whmosaic_ccd.txt','w')
waves = []
qes = []
import pylab
for l in f:
    x,y=l[:-1].split(' ')
    print x,y
    wave,qe = 300+(float(x)-230.)/(1030.-230.)*(1000.-300.), 90.-(float(y)-273)/(659.-273.)*(90.-0.)
    waves.append(10.*wave)
    qes.append(qe)
    print wave,qe        
    fout.write(str(10.*wave) + ' ' + str(qe/100.) + '\n')

fout.close()
#pylab.plot(waves,qes)
#pylab.show()

