#! /usr/bin/env python
#adam-does# Makes plots of seeing measures and e1,e2 to determine which exposures look good
#adam-use# Use to determine which plots to include in the "good" coadd before running do_coadd_batch.sh
#adam-example# ./Plot_cluster_seeing_e1e2.py MACS1226+21

### NOTE: This assumes that W-C-RC is the lensing band!

#the basics
import pyfits
from matplotlib.pyplot import *
from numpy import *
from glob import glob
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from UsefulTools import names, FromPick_data_true, FromPick_data_spots, GetMiddle, GetSpots_bins_values, ShortFileString, num2str
import imagetools
import astropy
from astropy.io import ascii
import sys,os,inspect                                                                                                                                                                                                                                                          
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
args=imagetools.ArgCleaner(sys.argv,FileString)
cluster=args[0]

# make files like this:
os.system("ls -1 /nfs/slac/g/ki/ki18/anja/SUBARU/%s/W-C-RC/SCIENCE/%s_SUPA*.cat | head -n 1 > tmp_cluster.txt" % (cluster,cluster))
with open("tmp_cluster.txt",'r') as fo:
    l=fo.read()
    catname=l.split("/")[-1]
    supa=catname[len(cluster)+1:-5]


os.system("/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/ldactoasc -i /nfs/slac/g/ki/ki18/anja/SUBARU/%s/W-C-RC/SCIENCE/%s_%s.cat -t STATS -k SEEING seeing_fwhmse seeing_rh_al e1 e2 > %s_seeings_and_e1e2.txt" % (cluster,cluster,supa,cluster))
os.system("/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/ldactoasc -i /nfs/slac/g/ki/ki18/anja/SUBARU/%s/W-C-RC/SCIENCE/%s_%s.cat -t STATS -s -b -k IMAGENAME > IMAGENAMES.txt" % (cluster,cluster,supa))

fl="%s_seeings_and_e1e2.txt" % (cluster)
tab = ascii.read(fl,Reader=ascii.SExtractor)
exposures = ascii.read("IMAGENAMES.txt",Reader=ascii.NoHeader)['col1'].data
Nexps=len(exposures)

f1=figure(figsize=(20,13))
ax1=f1.add_subplot(2,1,1)
ax1.set_title("%s seeing" % (cluster))
ax2=f1.add_subplot(2,1,2)
ax2.set_title("%s ellipticity" % (cluster))
#for seekey in ['SEEING', 'seeing_fwhmse', 'seeing_rh_al']:
ax1.plot(range(1,Nexps+1),tab['SEEING'].data,color='r',marker="o",label='SEEING')
ax1.plot(range(1,Nexps+1),tab['seeing_fwhmse'].data,color='g',marker="s",label='seeing_fwhmse')
ax1.plot(range(1,Nexps+1),tab['seeing_rh_al'].data,color='b',marker="d",label='seeing_rh_al')
ax1.set_xticklabels(exposures,rotation='vertical')
ax2.plot(range(1,Nexps+1),tab['e1'].data,color='r',marker="o",label='e1')
ax2.plot(range(1,Nexps+1),tab['e2'].data,color='b',marker="s",label='e2')
ax2.set_xticklabels(exposures,rotation='vertical')
ax2.legend()
ax1.legend()
f1.subplots_adjust(hspace=.31)
f1.tight_layout()
f1.savefig('plt_%s_seeing_e1e2' % (cluster))
os.system("rm -r tmp_cluster.txt")
