import pylab, pyfits, sys, os

CLUSTER = sys.argv[1]

iaper = '1'

LEPHAREDIR='/nfs/slac/g/ki/ki04/pkelly/lephare_dev/'
LEPHAREWORK='/nfs/slac/g/ki/ki04/pkelly/lepharework/'
SUBARUDIR='/nfs/slac/g/ki/ki05/anja/SUBARU'

dict = {'SUBARUDIR':SUBARUDIR,
    'PHOTOMETRYDIR': 'PHOTOMETRY',
    'CLUSTER':CLUSTER,
    'BPZPATH':os.environ['BPZPATH'],
    'iaper':iaper}

#raw_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.slr.cat' % dict 
#raw_p = pyfits.open(raw_catalog)['STDTAB'].data


output_catalog = '%(CLUSTER)s.1.all.bpz.tab' % dict 

#cat = '%(CLUSTER)s.%(iaper)s.photoz.CWWSB_capak.list.slr.tab' % dict

#output_catalog = '/%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.1.all.bpz.tab' % dict 

print output_catalog 

command = 'do_lensing_pat.sh ' + dict['CLUSTER'] + ' W-J-V ' + output_catalog
print command
os.system(command)
print 'FIX do lensing script '
raw_input()


output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/LENSING/%(CLUSTER)s_fbg.cat' % dict 

probs = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/all.spec.cat.bpz1.probs' % dict

print output_catalog

#output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.1.all.bpz.tab' % dict 

output_catalog = '/%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.1.all.bpz.tab' % dict 

output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.%(iaper)s.photoz.CWWSB_capak.list.slr.tab' % dict 

output_catalog = '%(SUBARUDIR)s/%(CLUSTER)s/ACS/merged_photz.cat' % dict 

print output_catalog
p = pyfits.open(output_catalog)['PSSC'].data
import scipy 

#cols = []
#for name in ['LPH_Z_BEST','LPH_Z_BEST68_HIGH','LPH_Z_BEST68_LOW']:
#    cols.append(pyfits.Column(name=filter,format=column.format,array=raw_p.field(name)))
#for name in ['Xpos','Ypos']:
#    cols.append(pyfits.Column(name=filter,format=column.format,array=raw_p.field(name)))
#tbhdu=pyfits.new_table(pyfits.ColDefs(cols))

''' look for cross-correlation within redshift range '''
#for cut in [' 



if True :
    mask = (p.field('BPZ_Z_B_MAX') - p.field('BPZ_Z_B_MIN'))/(1.+p.field('BPZ_Z_B')) < 0.3 
    #mask = (p.field('BPZ_Z_B_MAX') - p.field('BPZ_Z_B_MIN')) < 0.9
    #p = p[mask]
    mask = p.field('BPZ_ODDS') > 0.95
    p = p[mask]
    mask = p.field('BPZ_Z_B') > 2.9
    #p = p[mask]
    mask = p.field('rg_acs_as') > 0.6
    #p = p[mask]


if False:
    mask = (p.field('LPH_Z_BEST68_HIGH') - p.field('LPH_Z_BEST68_LOW'))/(1. + p.field('BPZ_CHI-SQUARED')) < 0.3
    #mask = (p.field('LPH_Z_VEST') - p.field('BPZ_Z_B_MIN')) < 0.9
    p = p[mask]

    a = p.field('LPH_Z_BEST')
    a, b, varp = pylab.hist(a,bins=scipy.arange(0,4,0.2))
    pylab.xlabel("Z")
    pylab.ylabel("Number of Galaxies")
    pylab.show()


import pylab, scipy

a = p.field('BPZ_Z_B')
print a
#pylab.scatter(a,p.field('rg_acs_as')) #/p.field('rg_Subaru'))
pylab.scatter(a,p.field('rg_Subaru_as')) #/p.field('rg_Subaru'))
#pylab.ylabel("Subaru/ACS size")
#pylab.scatter(p.field('MAG_AUTO'),p.field('rg_acs_as'))
pylab.ylabel("Subaru size arcseconds")
pylab.xlabel("BPZ redshift")
pylab.ylim([0,1.2])

print p.field('SeqNr')

pylab.savefig('lph.png')
pylab.show()

#from ppgplot import *

'''
import Numeric 
a = Numeric.array(p.field('BPZ_Z_B'))
#b = Numeric.array(p.field('LPH_Z_BEST'))

vis = True 
if False: #True:
    if vis:
        pgbeg("/XTERM")
    else:
        output = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.bpzvslph.ps' % dict 
        pgbeg(output + "/cps")
    pgeras()
    pgiden()
    pgswin(0,4.0,0,4.0)
    pgpt(a,b,1)
    pgbox()
    pglab('BPZ','LPH',CLUSTER)
    pgend()
    #pgbeg("0911hist.ps/cps",1,1)
    print 'plotted'

if vis:
    raw_input()
    pgbeg("/XTERM")
else:
    output = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.bpzhist.ps' % dict 
    pgbeg(output + "/cps")
pgeras()
pgiden()
pgswin(0,4,0,1)
import Numeric 
pghist(len(a),a,0,4,40)
pgbox()
pglab('BPZ Z','GALAXIES',CLUSTER)
pgend()

if vis: 
    raw_input()
    pgbeg("/XTERM")
else:
    output = '%(SUBARUDIR)s/%(CLUSTER)s/%(PHOTOMETRYDIR)s/%(CLUSTER)s.lphhist.ps' % dict 
    pgbeg(output + "/cps")
pgeras()
pgiden()
pgswin(0,4,0,1)
import Numeric 
pghist(len(b),b,0,4,40)
pgbox()
pglab('LPH Z','GALAXIES',CLUSTER)
pgend()
'''
