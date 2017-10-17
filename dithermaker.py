#!/usr/bin/env python
#######################
# Script to take center RA/DEC location & generate dithered offsets
# for baseline project exposures
########################

### History:

## 2014/07/21 rgm: take out "coordinates": "absolute",
## which we are told is invalid.
## 2014/07/25 rgm: fix --disableoutrigger; add argv to end of config

import sys, argparse, random, numpy as np
import json, math

########################

def generateMainDithers(nexp, dithersize):

    if nexp == 0:
        return []

    exp_offsets = [(0., 0.)]
    
    if nexp == 1:
        return exp_offsets

    OneOffsetPositive = True
    OneOffsetCount = 0

    IndexPositive = True
    IndexCount = 1

    IndexOffsetLeft = True

    for i in range(1, nexp):

        IndexOffset = i
        if not IndexPositive:
            IndexOffset = -i

        OneOffset = 1
        if not OneOffsetPositive:
            OneOffset = -1

        if IndexOffsetLeft:
            exp_offsets.append((IndexOffset*dithersize, OneOffset*dithersize))
        else:
            exp_offsets.append((OneOffset*dithersize, IndexOffset*dithersize))

        IndexOffsetLeft = not IndexOffsetLeft

        OneOffsetCount += 1
        if OneOffsetCount == 2:
            OneOffsetPositive = not OneOffsetPositive
            OneOffsetCount = 0

        IndexCount += 1
        if IndexCount == 2:
            IndexPositive = not IndexPositive
            IndexCount = 0

    return exp_offsets

########################

def absolutePointings(ra, dec, exp_offsets):

    cum_offsets = []
    ra = ra
    dec = dec
    for offset in exp_offsets:
        ra += (offset[0]/3600.)/np.cos(dec*np.pi/180.)
        dec += (offset[1]/3600.)
        cum_offsets.append((ra, dec))

    return cum_offsets

########################

def generateOutriggers(ra, dec, outriggersize):

    exp_positions = []

    posangle = random.uniform(0, 360)

    for i in range(3):
        angle = (posangle + i*(360/3.))*(np.pi/180.)
        exp_positions.append( (ra + outriggersize*np.cos(angle)/np.cos(dec*np.pi/180.), 
                             dec + outriggersize*np.sin(angle)) )

    return exp_positions

########################

def writeExposures(output, exposures):

    json_string = json.dumps(exposures, sort_keys = True, indent=4)

    output.write(json_string)


#######################

def countTime(exposures, overhead):

    nexp = len(exposures)
    if nexp == 0:
        return 0, 0
    imagetime = reduce(lambda x,y:x+y, [x['expTime'] for x in exposures if 'break' not in x])

    totaltime = imagetime + nexp*overhead

    return imagetime, totaltime


########################

def createScript(args):

    output = open(args.scriptname, 'w')


    ### deal with stuff always at the start of the exposure sequence

    start_exposures = []

    if args.breakstart:
        breakKeys = {'break' : True}
        start_exposures.append(breakKeys)

    #short test exposure

    if not args.noshortexp:
        seqid = '%s_%s_%d_short' % (args.object, args.filter, args.visit)
        keywords = {'expType' : 'object', # 'coordinates' : 'absolute',
                    'RA' : args.ra, 'dec' : args.dec, 
                    'filter' : args.filter, 'object' : args.object, 
                    'expTime' : 10,
                    'seqid' : seqid, 'seqnum' : 0, 'seqtot' : 2}
        start_exposures.append(keywords)

        exptime = math.ceil(10**((np.log10(10.) + \
                                       np.log10(args.singletime))/2.))

        keywords = {'expType' : 'object', # 'coordinates' : 'absolute', 
                    'RA' : args.ra, 'dec' : args.dec, 
                    'filter' : args.filter, 'object' : args.object, 
                    'expTime' : exptime,
                    'seqid' : seqid, 'seqnum' : 0, 'seqtot' : 2}
        start_exposures.append(keywords)


        breakKeys = {'break' : True}
        start_exposures.append(breakKeys)

    

    #deal with dithers

    seqid = '%s_%s_%d_dither' % (args.object, args.filter, args.visit)
    nexp = args.nexp


    science_exposures = []
    exposure_offsets = generateMainDithers(nexp = nexp, dithersize=args.dithersize)
    abs_pointings = absolutePointings(args.ra, args.dec, exposure_offsets)

    expIDoffset = args.startwithexpnum
    for seqnum, pointing in enumerate(abs_pointings[expIDoffset:]):
#        keywords = {'expType' : 'object', 'coordinates' : 'absolute', 'RA' : pointing[0], 'DEC' : pointing[1], 
        keywords = {'expType' : 'object', 'RA' : pointing[0], 'DEC' : pointing[1], 
                    'filter' : args.filter, 'object' : args.object, 'expTime' : args.singletime,
                    'seqid' : seqid, 'seqnum' : expIDoffset+seqnum, 'seqtot' : nexp}  
        science_exposures.append(keywords)


    #deal with outriggers
    outrigger_exposures = []

    if not args.disableoutrigger:

        outrigger_positions = generateOutriggers(ra = args.ra, dec = args.dec, outriggersize = args.outriggersize)

        # make sure we grab the central exposure if we aren't taking science images

        outriggerid = '%s_%s_%d_outrigger' % (args.object, args.filter, args.visit)
        outriggernum = 3
        
        if args.nexp == 0:
            outrigger_positions.insert(0,(args.ra, args.dec))
            outriggernum = 4


        for seqnum, exp_pos in enumerate(outrigger_positions):
#            keywords = {'expType' : 'object', 'coordinates' : 'absolute', 
            keywords = {'expType' : 'object', 
                        'RA' : exp_pos[0], 'DEC' : exp_pos[1], 
                        'filter' : args.filter, 'object' : args.object, 'expTime' : args.outriggertime,
                        'seqid' : outriggerid, 'seqnum' : seqnum, 'seqtot' : outriggernum}
            outrigger_exposures.append(keywords)


    if args.outriggerfirst:
        exposures = start_exposures + outrigger_exposures + science_exposures
    else:
        exposures = start_exposures + science_exposures + outrigger_exposures



    if not args.nobreakend:
        breakKeys = {'break' : True}
        exposures.append(breakKeys)

    writeExposures(output, exposures)

    

    output.close()

    calibImage, calibTotal = countTime(start_exposures + outrigger_exposures, args.overhead)
    sciImage, sciTotal = countTime(science_exposures, args.overhead)

    return sciImage, calibImage, sciTotal + calibTotal

    

########################

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--ra', type=float)
    parser.add_argument('--dec', type=float)
    parser.add_argument('--nexp', type=int,
                        help = 'Total number of full-length science exposures')
    parser.add_argument('--singletime', type=int,
                        help = 'Exposure time per image')
    parser.add_argument('--dithersize', type=float, default=60.0,
                        help = 'Basic unit size for dither; arcseconds')
    parser.add_argument('--disableoutrigger', default=False, action='store_true')
    parser.add_argument('--outriggersize', type=float, default = 0.5,
                        help = 'Step size from center for outrigger exp; degrees')
    parser.add_argument('--outriggertime', type=int, default=-1,
                        help = 'Exposure time for each outrigger')
    parser.add_argument('--outriggerfirst', default=False, action='store_true')
    parser.add_argument('--filter', type=str)
    parser.add_argument('--object', type=str)
    parser.add_argument('--visit', type=int, default=0)
    parser.add_argument('--breakstart', default=False, action='store_true')
    parser.add_argument('--nobreakend', default=False, action='store_true')
    parser.add_argument('--startwithexpnum', type=int, default = 0, help='Start at a different initial dither; 0-indexed')
    parser.add_argument('--noshortexp', default=False, action='store_true')
    parser.add_argument('--overhead', type=int, default = 30)
    parser.add_argument('--offset', type=float, default = -4.5,
                        help = 'Offset in DEC direction to place center of cluster in the middle of a chip (in arcmin)')
    parser.add_argument('--scriptname', type=str, default='')

    args = parser.parse_args(argv)

    args.offset = args.offset/60.
    args.dec = args.dec + args.offset

    if args.outriggertime == -1:
        args.outriggertime = args.singletime / 2.

    outriggerFlag = 1
    if args.disableoutrigger:
        outriggerFlag = 0

    if args.scriptname == '':
        args.scriptname = '%s_%s_v%d_sci%d-%d_out%d.script' % (args.object, args.filter, args.visit, args.startwithexpnum, args.nexp, outriggerFlag)

    configfile = '%s.config' % args.scriptname


    print 'Called with configuration:'
    print 'RA: %f' % args.ra
    print 'DEC: %f' % (args.dec - args.offset)
    print 'DEC Offset: %f arcmin' % (60*args.offset)
    print 'Number of Science Exposures: %d' % args.nexp
    print 'Single Exposure: %d' % args.singletime
    print 'Dither Size: %f' % args.dithersize
    print 'Disable Outrigger?: %s' % args.disableoutrigger
    print 'Outrigger First?: %s' % args.outriggerfirst
    print 'Outrigger Size: %f' % args.outriggersize
    print 'Outrigger time: %f' % args.outriggertime
    print 'Filter: %s' % args.filter
    print 'Object: %s' % args.object
    print 'Break Start? : %s' % args.breakstart
    print 'Break End? : %s' % (not args.nobreakend)
    print 'Overhead: %d' % args.overhead
    print 'First Exposure : %d' % args.startwithexpnum
    print 'Script Name: %s' % args.scriptname



    scitime, calibtime, totaltime = createScript(args)

    print
    print 'Science Time: %d' % scitime
    print 'Calib Time: %d' % calibtime
    print 'Total Time: %d' % totaltime

    with open(configfile, 'w') as output:
        output.write('Called with configuration:\n'                  )
        output.write('RA: %f\n' % args.ra                            )
        output.write('DEC: %f\n' % (args.dec - args.offset)            )
        output.write('DEC Offset: %f arcmin\n' % (60*args.offset))
        output.write('Number of Science Exposures: %d\n' % args.nexp )
        output.write('Single Exposure: %d\n' % args.singletime       )
        output.write('Dither Size: %f\n' % args.dithersize           )
        output.write('Disable Outrigger?: %s\n' % args.disableoutrigger       )
        output.write('Outrigger First?: %s\n' % args.outriggerfirst       )
        output.write('Outrigger Size: %f\n' % args.outriggersize     )
        output.write('Outigger Time: %f\n' % args.outriggertime      )
        output.write('Filter: %s\n' % args.filter                    )
        output.write('Object: %s\n' % args.object                    )
        output.write('Break Start? : %s\n' % args.breakstart         )
        output.write('Break End? : %s\n' % (not args.nobreakend)     )
        output.write('Overhead : %d\n' % args.overhead     )
                     
        output.write('First Exposure : %d\n' % args.startwithexpnum  )
        output.write('Script Name: %s\n' % args.scriptname           )
        output.write('Science Time: %d\n' % scitime                  )
        output.write('Calib Time: %d\n' % calibtime                  )
        output.write('Total Time: %d\n' % totaltime                  )
        output.write('Arguments: %s\n' % ' '.join(map(str,sys.argv[1:])))
    

#########################


if __name__ == '__main__':

    main(argv = sys.argv[1:])

