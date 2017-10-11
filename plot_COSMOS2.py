import astropy, astropy.io.fits as pyfits, os, pylab

params = {'backend' : 'ps',
     'text.usetex' : True,
      'ps.usedistiller' : 'xpdf',
      'ps.distiller.res' : 6000}
pylab.rcParams.update(params)
                                       

fig_size = [8.5,8.5]
params = {'axes.labelsize' : 22,
          'text.fontsize' : 22,
          'legend.fontsize' : 22,
          'xtick.labelsize' : 12,
          'ytick.labelsize' : 12,
          'figure.figsize' : fig_size}
pylab.rcParams.update(params)

set = 'CWWSB_capak'
web = os.environ['sne'] + '/photoz/COSMOS' + set + '/'
os.system('mkdir -p ' + web)

C = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/cosmos_lephare.cat')['OBJECTS'].data
U = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.' + set + '.list.all.bpz.tab')['STDTAB'].data
#M = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/all.APERCWWSB_capak.list.cat.bpz1.tab')['STDTAB'].data
P = open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_aper/COSMOS_PHOTOZ.APER.1.' + set + '.list.all.probs').readlines()

import scipy, pylab
zs = scipy.arange(0.01000,4.0100,0.0100)
def parse(i,Z):
    y = scipy.array([float(x) for x in P[i+1][:-1].split(' ')[1:-1]])
    vec = zip(zs,y)
    tot = 0
    for v in vec:
        tot += v[1]
        if v[0] > Z: break 
    
    if False: #tot < 0.01:    
        print Z, tot
        pylab.scatter(zs,y)
        pylab.show()

    return tot

CZ = []
UZ = []
fracs = []
fracs_T = {'0':[[],[]],'1':[[],[]],'2':[[],[]],'3':[[],[]],'4':[[],[]],'5':[[],[]],'6':[[],[]]}
fracs_M = [[[0,20],[],[]],[[20,21],[],[]],[[21,23],[],[]],[[23,25],[],[]],[[25,30],[],[]]]
fracs_O = [[[0,0.2],[],[]],[[0.2,0.4],[],[]],[[0.4,0.6],[],[]],[[0.6,0.8],[],[]],[[0.8,1.0],[],[]]]
rec = open('rec','w')
for i in range(40000):
    if i%100: print i
    cosmos_z = C.field('zp_best')[i]
    our_z = U.field('BPZ_Z_B')[i]
    frac = parse(i,cosmos_z)
    #if  U.field('BPZ_ODDS')[i] > 0.5 and our_z > 0.0 and our_z < 1.25 and cosmos_z > 0 and 0 < U.field('BPZ_M_0')[i] < 25 and U.field('BPZ_T_B')[i] < 5.5: # and our_z > 0.5:

    if  U.field('BPZ_ODDS')[i] > 0.5 and our_z > 0.0 and cosmos_z > 0 and 0 < U.field('BPZ_M_0')[i] < 25: # and U.field('BPZ_T_B')[i] < 5.5: # and our_z > 0.5:

        if U.field('NFILT')[i] == 6:
            rec.write(str(our_z) + ' ' + str(cosmos_z) + ' ' + str(i) + ' ' + str(U.field('SeqNr')[i]) + '\n') 
            CZ.append(cosmos_z)
            UZ.append(our_z)
            fracs.append(frac)
            fracs_T[str(int(U.field('BPZ_T_B')[i]))][0].append(frac)
            fracs_T[str(int(U.field('BPZ_T_B')[i]))][1].append([cosmos_z,our_z])
            for o in range(len(fracs_M)):
                if fracs_M[o][0][0] < U.field('BPZ_M_0')[i] < fracs_M[o][0][1]:                
                    fracs_M[o][1].append(frac)
                    fracs_M[o][2].append([cosmos_z,our_z])

    ''' want bpz_odds starting from 0 '''
    if  U.field('BPZ_ODDS')[i] > 0 and our_z > 0.0 and our_z < 1.25 and cosmos_z > 0 and 0 < U.field('BPZ_M_0')[i] < 25 and U.field('BPZ_T_B')[i] < 5.5: # and our_z > 0.5:
        if U.field('NFILT')[i] == 6:
            for o in range(len(fracs_O)):
                if fracs_O[o][0][0] < U.field('BPZ_ODDS')[i] < fracs_O[o][0][1]:                
                    fracs_O[o][1].append(frac)
                    fracs_O[o][2].append([cosmos_z,our_z])


        else:
            print 'hi'            
            #raw_input()




rec.close()

pdz = open(web + '/pdz.html','w')



pylab.clf()
pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
pylab.scatter(CZ,UZ,s=0.05)
pylab.plot([0,6],[0,6],color='red')
pylab.xlim([0,6.])
pylab.ylim([0,4.])
pylab.ylabel('UBVriz Redshift')
pylab.xlabel('COSMOS-30 Redshift')
pylab.savefig(web + 'usvscosmos04.png')
pylab.savefig(web + 'usvscosmos04.pdf')
pdz.write('<img src=usvscosmos04.png></img><br>\n')
#pylab.show()

pylab.clf()

pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
pylab.scatter(CZ,UZ,s=0.05)
pylab.axhline(y=1.2,xmin=-10,xmax=100,width=3)
pylab.plot([0,5],[0,5],color='red',width=3)
pylab.xlim([0,1.5])
pylab.ylim([0,1.5])

pylab.ylabel('UBVriz Redshift')
pylab.xlabel('COSMOS-30 Redshift')

pylab.savefig(web + 'usvscosmos02.png')
pylab.savefig(web + 'usvscosmos02.pdf')
pdz.write('<img src=usvscosmos02.png></img><br>\n')
#pylab.show()

pylab.clf()

pylab.axes([0.125,0.15,0.95-0.125,0.95-0.15])
a, b, varp = pylab.hist((scipy.array(CZ)-scipy.array(UZ))/(1+scipy.array(CZ)),bins=scipy.arange(-0.2,0.2,0.016),color='blue',edgecolor='black')
pylab.ylabel('Galaxies')
pylab.xlabel('(z$_{UBVriz}i$ - z$_{COSMOS-30}$)/(1+z$_{COSMOS-30}$)')
pylab.savefig(web + 'usvscosmoshist.png')
pylab.savefig(web + 'usvscosmoshist.pdf')
pdz.write('<img src=usvscosmoshist.png></img><br>\n')
pdz.write('<h1>Complete Set (w/ redshift ODDS cuts)</h1><br>\n')
import pylab

params = {'backend' : 'ps',
     'text.usetex' : True,
      'ps.usedistiller' : 'xpdf',
      'ps.distiller.res' : 6000}
pylab.rcParams.update(params)

fig_width = 6
fig_height = 6                                       

fig_size = [fig_width,fig_height]
params = {'axes.labelsize' : 20,
          'text.fontsize' : 16,
          'legend.fontsize' : 20,
          'xtick.labelsize' : 16,
          'ytick.labelsize' : 16,
          'figure.figsize' : fig_size}
pylab.rcParams.update(params)


#pylab.hist(fracs)
pylab.clf()
n, bins, patches = pylab.hist(fracs, 10000, normed=1, histtype='step', cumulative=True)
pylab.plot([0,1],[0,1],c='red')
pylab.xlim([0,1])
pylab.ylim([0,1])
pylab.title('ALL')
pylab.ylabel('Cumulative Fraction')
pylab.xlabel('Fraction')
pylab.savefig(web + 'all.png')
pdz.write('<img width=600px src=all.png></img><br>\n')
#pylab.show()


pdz.write('<h1>Magnitude Cuts</h1><br>\n')
for f in fracs_M:
    if len(f[1]):
        pylab.clf()                                                                          
        n, bins, patches = pylab.hist(f[1], 10000, normed=1, histtype='step', cumulative=True)
        pylab.plot([0,1],[0,1],color='red')
        pylab.xlim([0,1])
        pylab.ylim([0,1])
        pylab.ylabel('Cumulative Fraction')
        pylab.xlabel('Fraction')
        key = str(f[0][0]) + 'to' + str(f[0][1])
        pylab.title(key + ' magnitudes')
        pylab.savefig(web + key + '.png')

        pylab.clf()
        a, b, varp = pylab.hist(scipy.array(f[2])[:,0]-scipy.array(f[2])[:,1],bins=scipy.arange(-1.2,1.2,0.016),color='blue',edgecolor='black')
        pylab.ylabel('Number of Galaxies',fontsize='x-large')
        pylab.xlabel('COSMOS - US (redshift)',fontsize='x-large')
        pylab.title(key)
        pylab.savefig(web + key + 'hist.png')

        pylab.clf()
        pylab.scatter(scipy.array(f[2])[:,0],scipy.array(f[2])[:,1],s=0.05)
        pylab.plot([0,10],[0,10],c='red')
        pylab.ylabel('US',fontsize='x-large')
        pylab.xlabel('THEM (COSMOS)',fontsize='x-large')
        pylab.xlim((0,2))
        pylab.ylim((0,2))
        pylab.title(key)
        pylab.savefig(web + key + 'scatter.png')



        pdz.write('<img width=500px src=' + key + '.png></img><img width=500px src=' + key + 'hist.png><img width=500px src=' + key + 'scatter.png></img><br>\n')
    
pdz.write('<h1>Type Cuts (lower # is earlier type)</h1><br>\n')

w = 1
for key in sorted(fracs_T.keys()):
    if len(fracs_T[key][0]):
        w += 1
        import pylab                                                                                
        #pylab.hist(fracs)
        pylab.clf()
        bins_x = scipy.arange(0,1.05,0.05)
        n, bins, patches = pylab.hist(fracs_T[key][0], bins=bins_x, histtype='bar') #, cumulative=True)
        expected = float(len(fracs_T[key][0])) / len(bins_x)
        pylab.plot([0,1],[expected,expected],color='red')
        pylab.xlim([0,1])
        #pylab.ylim([0,1])
        pylab.ylabel('Galaxies')
        pylab.xlabel('$P(z_{estimate} < z_{spec})$ ')
        pylab.title(key)
        pylab.savefig(web + key + '.png')
        pylab.savefig(web + key + '.pdf')
        
        pylab.clf()
        a, b, varp = pylab.hist(scipy.array(fracs_T[key][1])[:,0] - scipy.array(fracs_T[key][1])[:,1],bins=scipy.arange(-1.2,1.2,0.016),color='blue',edgecolor='black')
        pylab.ylabel('Number of Galaxies',fontsize='x-large')
        pylab.xlabel('COSMOS - US (redshift)',fontsize='x-large')
        pylab.title(key)
        pylab.savefig(web + key + 'hist.png')

        pylab.clf()
        pylab.scatter(scipy.array(fracs_T[key][1])[:,0],scipy.array(fracs_T[key][1])[:,1],s=0.05)
        pylab.plot([0,10],[0,10],c='red')
        pylab.ylabel('US',fontsize='x-large')
        pylab.xlabel('THEM (COSMOS)',fontsize='x-large')
        pylab.title(key)
        pylab.xlim((0,2))
        pylab.ylim((0,2))
        pylab.savefig(web + key + 'scatter.png')

        pdz.write('<img width=500px src=' + key + '.png></img><img width=500px src=' + key + 'hist.png><img width=500px src=' + key + 'scatter.png></img><br>\n')
        if w % 2: pdz.write('<br></n>')
        #pylab.show()

pdz.write('<h1>ODDS Cuts</h1><br>\n')

for f in fracs_O:
    if len(f[1]):
        pylab.clf()                                                                          
        n, bins, patches = pylab.hist(f[1], 10000, normed=1, histtype='step') #, cumulative=True)
        pylab.plot([0,1],[0,1],color='red')
        pylab.xlim([0,1])
        pylab.ylim([0,1])
        pylab.ylabel('Cumulative Fraction')
        pylab.xlabel('Fraction')
        key = str(f[0][0]) + 'to' + str(f[0][1])
        pylab.title(key + ' ODDS')
        pylab.savefig(web + key + '.png')

        pylab.clf()
        a, b, varp = pylab.hist(scipy.array(f[2])[:,0]-scipy.array(f[2])[:,1],bins=scipy.arange(-1.2,1.2,0.016),color='blue',edgecolor='black')
        pylab.ylabel('Number of Galaxies',fontsize='x-large')
        pylab.xlabel('COSMOS - US (redshift)',fontsize='x-large')
        pylab.title(key)
        pylab.savefig(web + key + 'hist.png')

        pylab.clf()
        pylab.scatter(scipy.array(f[2])[:,0],scipy.array(f[2])[:,1],s=0.05)
        pylab.plot([0,10],[0,10],c='red')
        pylab.ylabel('US',fontsize='x-large')
        pylab.xlabel('THEM (COSMOS)',fontsize='x-large')
        pylab.xlim((0,2))
        pylab.ylim((0,2))
        pylab.title(key)
        pylab.savefig(web + key + 'scatter.png')



        pdz.write('<img width=500px src=' + key + '.png></img><img width=500px src=' + key + 'hist.png><img width=500px src=' + key + 'scatter.png></img><br>\n')



















pdz.close()
