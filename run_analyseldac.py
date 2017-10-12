#!/usr/bin/env python

import sys, astropy, astropy.io.fits as pyfits, bashreader, ldac, math, os, re, numpy

import adam_quicktools_ArgCleaner
argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
inputfile = argv[0]
outputfile = argv[1]
image = argv[2]

config = bashreader.parseFile('./progs.ini')
npara =int(config.npara)

inputcat = pyfits.open(inputfile)
if inputcat is None:
    print 'Cannot open %s' % inputfile
    sys.exit(1)

root, ext = os.path.splitext(inputfile)


objects = None
hfindpeaks = None
fields = None
for hdu in inputcat:
    try:
        if 'OBJECTS' == hdu.header['EXTNAME']:
            objects = ldac.LDACCat(hdu)
        elif 'HFINDPEAKS' == hdu.header['EXTNAME']:
            hfindpeaks = hdu
        elif 'FIELDS' == hdu.header['EXTNAME']:
            fields = hdu
    except KeyError:
        pass


catsize = int(math.ceil(len(objects) / float(npara)))
index = 0
children = []
for i in xrange(npara):
    endpoint = min(len(objects), index+catsize)
    mask = numpy.zeros(len(objects))
    mask[index:endpoint] = numpy.ones(endpoint - index)
    cat = objects.filter(mask == 1)
    index = endpoint

    infile = '%s_%d.cat' % (root,i)
    outfile = '%s_%d.out.cat' % (root,i)

    hdulist = pyfits.HDUList([pyfits.PrimaryHDU(), hfindpeaks, cat.hdu, fields])
    hdulist.writeto(infile, overwrite = True)

    child = os.fork()
    if child:
        children.append(child)
    else:
        params = {'command' : config.p_analyseldac,
                  'input' : infile,
                  'output' : outfile,
                  'image' : image}
        command='%(command)s -i %(input)s -o %(output)s -x 1 -r -3 -f %(image)s' % params
        print command
	#adam-SHNT# this is the issue!
        os.system(command)
        os._exit(os.EX_OK)
    
for child in children: 
        os.waitpid(child,0)
    
cats = []    
objects = []
for i in xrange(npara):

    file = '%s_%d.out.cat' % (root,i)
    cat = pyfits.open(file)
    if cat is None:
        print 'Cannot open %s' % file
        sys.exit(1)
    objects.append(ldac.openObjects(cat))
    cats.append(cat)

nrows = reduce(lambda x,y: x+len(y), objects, 0)

newobjecthdu = pyfits.BinTableHDU.from_columns(objects[0].hdu.columns, nrows=nrows)
newobjecthdu.header['EXTNAME']= 'OBJECTS'
index = len(objects[0])
for objs in objects[1:]:
    endpoint = index + len(objs)
    for name in objects[0].keys():
        newobjecthdu.data.field(name)[index:endpoint] = objs[name]
    index = endpoint

otherhdus = filter(lambda x: x.header['EXTNAME'] != 'OBJECTS', cats[0][1:])
allhdus = [pyfits.PrimaryHDU(), newobjecthdu]
allhdus.extend(otherhdus)
hdulist = pyfits.HDUList(allhdus)
hdulist.writeto(outputfile, overwrite = True)
    
