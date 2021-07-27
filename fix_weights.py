import sys,os
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from import_tools import *
from scipy import ndimage
s = ndimage.generate_binary_structure(2,2)


def fixwt(filt,i,cutval):
	globwtfl2='/u/ki/awright/data/2015-12-15_%s/WEIGHTS/globalweight_%s.fits' % (filt,i)
	globwtfl1='/u/ki/awright/data/2015-12-15_%s/WEIGHTS/ORIGINAL_globalweights/globalweight_%s.fits' % (filt,i)
	#os.mkdir('/u/ki/awright/data/2015-12-15_%s/WEIGHTS/fixed_globalweights/' % (filt))
	globwtflnew='/u/ki/awright/data/2015-12-15_%s/WEIGHTS/fixed_globalweights/globalweight_%s.fits' % (filt,i)
	globwtfo1=pyfits.open(globwtfl1)[0].data
	globwtfo2=pyfits.open(globwtfl2)[0].data
	globwtfo2_header=pyfits.open(globwtfl2)[0].header
	#labels1,Nlabels1=ndimage.measurements.label(globwtfo1==0,s)
	labels2,Nlabels2=ndimage.measurements.label(globwtfo2==0,s)
	#print globwtfl1,(globwtfo1==0).sum(),globwtfo1[globwtfo1>0].min(),Nlabels1
	#print globwtfl2,(globwtfo2==0).sum(),globwtfo2[globwtfo2>0].min(),Nlabels2
	fitfl8=pyfits.open('/u/ki/awright/data/2015-12-15_%s/BASE_WEIGHT/BASE_WEIGHT_%s.fits' % (filt,i))
	wt8=fitfl8[0].data
	#labels8_7,Nlabels_7=ndimage.measurements.label((wt8<.7),s)
	spots2=globwtfo2==0
	spots1=globwtfo1==0
	labels_old=unique(labels2[spots1])
	label2_list=range(1,1+Nlabels2)
	for l in labels_old:
	    label2_list.remove(l)
	labels_2not1=array(label2_list)
	min_labels2=ndimage.measurements.minimum(wt8,labels=labels2,index=label2_list)
	cut_labels2_bools=(min_labels2>cutval)
	print "%10s,%2i: percent=%.2f, #=%6i, (with min>%.2f), total_percent=%.2f" % (filt,i,cut_labels2_bools.mean()*100,cut_labels2_bools.sum(),cutval,cut_labels2_bools.sum()/float(Nlabels2))
	head_str="put back: per=%.2f #=%6i with min>%.2f" % (cut_labels2_bools.mean()*100,cut_labels2_bools.sum(),cutval,)
	rid_labels2=labels_2not1[cut_labels2_bools]
	slices2=scipy.ndimage.find_objects(labels2)
	globwt2new=globwtfo2
	for rid_label in rid_labels2:
		sl=slices2[rid_label-1]
		lab2sl=labels2[sl]
		spot2sl=lab2sl==rid_label
		globwt2new[sl][spot2sl]=wt8[sl][spot2sl]
	hdu=astropy.io.fits.PrimaryHDU(globwt2new)
	hdu.header=globwtfo2_header
	hdu.header['FIXWT']=head_str
	hdu.writeto(name=globwtflnew,overwrite=True)

base_cut=.58
cuts=[base_cut , base_cut+.1 , base_cut+.2 , base_cut+.1 , base_cut , base_cut , base_cut+.1 , base_cut+.2 , base_cut+.05 , base_cut]
for i in range(1,11):
	for filt in ('W-J-B','W-C-RC','W-S-Z+'):
		cutval=cuts[i-1]
		fixwt(filt,i,cutval)
