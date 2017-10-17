#!/usr/bin/env python
#adam-use# example of how to use optparse
#adam-example# for a more specific example, see adam_bigmacs-apply_zps.py, which would be called like this:
#	ipython -i -- adam_bigmacs-apply_zps.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bigmacs_cleaned_offsets.list

#######################

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
	                  help='output catalog name. ')
	parser.add_option('-z', '--zeropoints',
	                  dest='zeropoints_fl',
	                  help='cleaned zeropoints list name. ')

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
	if options.zeropoints_fl is None:
	    parser.error('Need to specify zeropoints catalog file!')
	main(flinput=options.input_fl,flzps=options.zeropoints_fl,flnew=options.output_fl)
