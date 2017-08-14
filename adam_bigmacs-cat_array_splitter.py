#! /usr/bin/env python
#adam-used# array version of ldac cat entries MACS1226+21.unstacked.cat (like MAG_APER-*) split into two scalar entries (like MAG_APER0- and MAG_APER1-) with the second one being saved into MACS1226+21.unstacked.split_apers.cat
# 	ex. MAG_APER-SUBARU-10_3-1-W-S-Z+ split into MAG_APER0-SUBARU-10_3-1-W-S-Z+ & MAG_APER1-SUBARU-10_3-1-W-S-Z+
#adam-example# python adam_bigmacs-cat_array_splitter.py /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.cat
import sys, os
import ldac
import astropy, astropy.io.fits as pyfits
from adam_quicktools_ArgCleaner import ArgCleaner
#flinput=ArgCleaner()[0]
#flnew=flinput.replace("unstacked","unstacked.split_apers")
#flproto=flinput.replace("unstacked","unstacked.proto-tmp")
def main(flinput,flnew):
	cat=ldac.openObjectFile(flinput)
	flproto=flinput.replace(".cat",".proto-tmp.cat")

	aper_keys=[]
	aper1_keys=[]
	for key in cat.keys():
		if "APER-" in key:
			aper_keys.append(key)
			keynew=key.replace("APER-","APER1-")
			aper1_keys.append(keynew)

	#catnew=ldac.openObjectFile(flnew)
	ncs=[]
	for key in aper_keys:
		keynew=key.replace("APER-","APER1-")
		col=cat[key]
		if not col.shape[-1]==2:
			raise Exception("this column doesn't seem to need to be split (shape is "+str(col.shape)+"), but it has APER- in the name. Thats weird and contradictory")
		ncs.append(pyfits.Column(name=keynew,format='1E',array=col[:,1]))

	hdu = pyfits.PrimaryHDU()
	hduSTDTAB = pyfits.BinTableHDU.from_columns(ncs)
	hdulist = pyfits.HDUList([hdu])
	hdulist.append(hduSTDTAB)
	hdulist[1].header.set('EXTNAME','OBJECTS')
	hdulist.writeto(flproto,clobber=True)

	os.system("ldacjoinkey -p "+flproto+" -i "+flinput+" -o "+flnew+" -t OBJECTS -k "+' '.join(aper1_keys))
	os.system("rm -f "+flproto)
	return


if __name__ == '__main__':
	import optparse
	parser = optparse.OptionParser()
	#example:
	#    parser.add_option('-3', '--threesec',
	#                  dest='threesec',
	#                  action='store_true',
	#                  help='Treat as a 3second exposure',
	#                  default=False)
	#parser.add_option('-c', '--cluster', dest='cluster', help='Cluster name')
	#parser.add_option('-f', '--filtername', dest='filter', help='Filter to calibrate')
	#parser.add_option('-m', '--maindir', dest='maindir', help='subaru directory')
	parser.add_option('-i', '--inputcat',
	                  dest='input_fl',
	                  help='input catalog with vector ldac objects.')
	parser.add_option('-o', '--outputcat',
	                  dest='output_fl',
	                  help='output catalog name. will have only scalar ldac objects.')

	from adam_quicktools_ArgCleaner import ArgCleaner
	argv=ArgCleaner()
	options, args = parser.parse_args(argv)
	#if options.cluster is None:
	#    parser.error('Need to specify cluster!')

	print "Called with:"
	print options

	if options.input_fl is None:
	    parser.error('Need to specify input catalog file!')
	if options.output_fl is None:
	    parser.error('Need to specify output catalog file!')
	main(flinput=options.input_fl,flnew=options.output_fl)
