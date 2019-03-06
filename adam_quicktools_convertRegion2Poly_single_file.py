#!/usr/bin/env python
#adam-example# ./adam_quicktools_convertRegion2Poly_single_file.py
#adam-does# back-up all region files in this directory, then ensures proper format for weighwatchers and save output
############################
# @file convertRegion2Poly.py
# @author Douglas Applegate
# @date 3/12/08
#
# @brief Reads a region file, ensures proper format for weighwatchers
#
# !!!!!!!!!!!!!WARNING: MODIFIES EXISTING REGION FILES!!!!!!!!!!!!
#
#############################

__cvs_id__ = "$Id: convertRegion2Poly.py,v 1.4 2010-11-12 20:33:56 dapple Exp $"

#############################

import regionfile, shutil, sys, re, glob, os, datetime

#import BonnLogger
#__bonn_logger_id__ = BonnLogger.parseLog(sys.argv)


#############################

useage = '''
convertRegions2Poly.py maindir dir

  or

convertRegions2Poly.py < in.reg > out.reg
'''

##############################

def doDirectory(dir):

    filenames = glob.glob('%s/*.reg' % dir)

    backupdir='%s/backup_%s' % (dir, datetime.datetime.now().strftime('%y-%m-%d_%H-%M'))
    os.mkdir(backupdir)

    for filename in filenames:

        print 'Processing %s...' % filename

        base=os.path.basename(filename)

        os.rename(filename, '%s/%s' % (backupdir, base))

        input = open('%s/%s' % (backupdir, base))
        output = open(filename, 'w')
        doFile(input, output)
        input.close()
        output.close()


##############################

def doFile(inputfile, outputfile):

    if type(inputfile) == type('a'):
        input = open(inputfile)
    else:
        input = inputfile

    try:
    	regions = regionfile.parseRegionFile(input.readlines())
    except:
	print "adam-look", inputfile
	raise

    if len(regions) == 0:
        return

    convertedRegions = [ region.toPolygon() for region in regions ]

    regionfile.writeRegionFile(outputfile, convertedRegions, overwrite = True)


##############################

import adam_backup_regs
if __name__ == '__main__':

    from adam_quicktools_ArgCleaner import ArgCleaner
    print 'len(sys.argv)=',len(sys.argv)
    args=ArgCleaner(sys.argv)
    if len(args)==1:
	if args[0].endswith('.reg'):
	
            filename=args[0]
	    base=os.path.basename(filename).split('.reg')[0]
	    dirname=os.path.dirname(filename)
	    ## first back-up entire directory
	    adam_backup_regs.backup_regions(dirname)

	    backup_filename=dirname+'/'+base+'_before_convertRegion2Poly.reg'
	    os.rename(filename, backup_filename)
	    output = open(filename, 'w')
	    input = open(backup_filename, 'r')
	    doFile(input, output)
	    output.close()
	    input.close()

    sys.exit()
    if len(sys.argv) == 1:
        doFile(sys.stdin, sys.stdout)

    elif len(sys.argv) == 2:
        doDirectory(sys.argv[1])

    elif len(sys.argv) == 3:

        dir = '%s/%s/reg' % (sys.argv[1], sys.argv[2])
        doDirectory(dir)

    #    BonnLogger.updateStatus(__bonn_logger_id__, 0)

    else:

        print useage
    #    BonnLogger.updateStatus(__bonn_logger_id__, 1)
        sys.exit(1)
