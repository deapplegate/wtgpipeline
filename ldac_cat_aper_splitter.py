#! /usr/bin/env python
#adam-used# array version of ldac cat entries MACS1226+21.unstacked.cat (like MAG_APER-*) split into two scalar entries (like MAG_APER0- and MAG_APER1-) with the second one being saved into MACS1226+21.unstacked.split_apers.cat
# 	ex. MAG_APER-SUBARU-10_3-1-W-S-Z+ split into MAG_APER0-SUBARU-10_3-1-W-S-Z+ & MAG_APER1-SUBARU-10_3-1-W-S-Z+
#adam-example# python adam_bigmacs-cat_array_splitter.py /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.cat
import sys, os,glob
import ldac
import astropy, astropy.io.fits as pyfits
from adam_quicktools_ArgCleaner import ArgCleaner
#flnew=flinput.replace("unstacked","unstacked.split_apers")
#flproto=flinput.replace("unstacked","unstacked.proto-tmp")
def main(flinput,flnew,movedir=False):
	fo=pyfits.open(flinput)
	cat=fo['LDAC_OBJECTS']
	flproto=flinput.replace(".ldac",".proto-tmp.ldac")

	aper_keys=[]
	aper1_keys=[]
	for key in cat.data.names:
		if "_APER" in key:
			aper_keys.append(key)

	#catnew=ldac.openObjectFile(flnew)
	newcols=[]
	for key in aper_keys:
		oldcol=cat.data[key]
		oldcolkeys=cat.columns[key]
		Napers=oldcol.shape[-1]
		if not oldcol.shape[-1]>=2:
			raise Exception("this column doesn't seem to need to be split (shape is "+str(col.shape)+"), but it has APER- in the name. Thats weird and contradictory")
		for i in range(Napers):
			keynew=key.replace("APER","APER%s" % (i))
			#print keynew
			aper1_keys.append(keynew)
			newcol=pyfits.Column(name=keynew,format='1E',array=oldcol[:,i],unit=oldcolkeys.unit)
			newcols.append(newcol)

	hdu = pyfits.PrimaryHDU()
	hduSTDTAB = pyfits.BinTableHDU.from_columns(newcols)
	hdulist = pyfits.HDUList([hdu])
	hdulist.append(hduSTDTAB)
	hdulist[1].header.set('EXTNAME','LDAC_OBJECTS')
	hdulist.writeto(flproto,overwrite=True)

	os.system("ldacjoinkey -p "+flproto+" -i "+flinput+" -o "+flnew+" -t LDAC_OBJECTS -k "+' '.join(aper1_keys))
	os.system("rm -f "+flproto)
	if movedir:
		os.system("mv "+flinput+" "+movedir)
		os.system("mv "+flnew+" "+flinput)
	return


# FLUX_APER1
# FLUXERR_APER1
# MAG_APER1
# MAGERR_APER1

if __name__=="__main__":
	args=ArgCleaner(sys.argv)
	cluster,refcat=args
	#adam-old# astrom_dir='/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B/SCIENCE/astrom_photom_scamp_PANSTARRS/cat/'
	find_astrom_dir='/gpfs/slac/kipac/fs1/u/awright/SUBARU/%s/*/SCIENCE/astrom_photom_scamp_%s/cat/' % (cluster,refcat)
	astrom_dir=glob.glob(find_astrom_dir)[0]
	if not os.path.isdir(astrom_dir+'old_ldac/'):
		os.mkdir(astrom_dir+'old_ldac/')
	fls=glob.glob(astrom_dir+'SUPA*.ldac')
	for fl in fls:
		print 'splitting ',fl
		main(fl,fl.replace('SUPA','FIXED'),astrom_dir+'old_ldac/')

#fl='SUPA0154653_1OCFSF.ldac'
#import astromatic_wrapper as aw
#fo=pyfits.open(astrom_dir+fl)
#for tab in fo:
#    if not tab.data is None:
#        print tab.data.names
#fnum=0
#tbls=[]
#while 1:
#	fnum+=1
#	try:
#		tbls.append(aw.utils.ldac.get_table_from_ldac(astrom_dir+fl, frame=fnum))
#	except ValueError:
#		break
