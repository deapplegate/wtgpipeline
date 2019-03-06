#!/usr/bin/env python

# Python module for photometric calibration.
# It needs the Python modules ppgplot and
# mpfit to be installed.

# 03.03.2005 Fixed a serious bug in the rejection loop. Instead
#            of using the remaining points we always used all points
#            and rejected points until the original fit matched the data
# 15.02.2005 Fixed the range of the y-axes in the plots to more
#            sensible values
# 14.02.2005 Fixed a bug when more paramters were fitted than
#            data points were present
#            We now rescale points to the airmass/color at which
#            they are plotted (zero)
#            Check that label is set
# 10.12.2004 Now takes a new argument "label" to be
#            used as axis label in the color plot

import copy
import getopt
import string
import sys

import mpfit
import Numeric

from ppgplot   import *

import BonnLogger


def phot_funct_2(p, fjac=None, y=None, err=None):
    model = p[0]
    status = 0
    return([status, (model-y)/err])

def phot_funct_1(p, fjac=None, color=None, y=None, err=None):
    model = p[0] + p[1]*color
    status = 0
    return([status, (model-y)/err])

def phot_funct_0(p, fjac=None, airmass=None, color=None, y=None, err=None):
    model = p[0] + p[1]*color*color + p[2]*color
    status = 0
    return([status, (model-y)/err])


def readInput(file):
    f = open(file, "r")

    instMagList = []
    stdMagList = []
    magErrList = []
    colList = []
    airmassList = []

    for line in f.readlines():
        instMag, stdMag, col, airmass, instMagErr, stdMagErr = string.split(line)
        magErr = (float(instMagErr)**2. + float(stdMagErr)**2.)**0.5
        magErrList.append(magErr)
        instMagList.append(float(instMag))
        stdMagList.append(float(stdMag))
        colList.append(float(col))
        airmassList.append(float(airmass))
    f.close()

    instMag = Numeric.array(instMagList)
    stdMag = Numeric.array(stdMagList)
    data = stdMag - instMag
    airmass = Numeric.array(airmassList)
    color = Numeric.array(colList)
    magErr = Numeric.array(magErrList)

    return data, airmass, color, magErr 


def photCalib(data_save, airmass_save, color_save, err_save, p, sigmareject, maxSigIter=50):
    save_len = len(data_save)
    
    parinfos = [[{"value": p[0], "fixed": 0},{"value": p[1], "fixed": 0, "limited": [0,1], "limits": [-99, 0]},{"value": p[2], "fixed": 0}],[{"value": p[0], "fixed": 0},{"value": p[1], "fixed": 0}],[{"value": p[0], "fixed": 0}]]

    phot_functs = [phot_funct_0, phot_funct_1, phot_funct_2]

    solutions = [] 
    for fit_type in [0,1,2]:
        
        airmass = copy.copy(airmass_save)
        color = copy.copy(color_save)
        data_tmp = copy.copy(data_save)
        err = copy.copy(err_save)

        #first apply coefficients we are holding fixed  
        data = copy.copy(data_tmp)
        if fit_type == 1:
                for i in range(len(data_tmp)):
                        data[i] = data_tmp[i] - p[1]*airmass[i]
        if fit_type == 2:
                for i in range(len(data_tmp)):
                        data[i] = data_tmp[i] - p[1]*airmass[i] - p[2]*color[i]
        print data_tmp[0], data[0]

        data_rec = copy.copy(data)

        parinfo = parinfos[fit_type]

        #for j in range(len(parinfo)):
            #if j in fixedList:
            #    print "Element", j, "is fixed at", p[j]
            #    parinfo[j]["fixed"] = 1
            #else:
            #    parinfo[j]["fixed"] = 0
        for i in range(maxSigIter):
            old_len = len(data)
            fas = [{"airmass": airmass,"color": color, "y": data, "err": err},{"color": color,"y": data, "err": err}, {"y": data, "err": err}]
            fa = fas[fit_type] 
            phot_funct = phot_functs[fit_type]
 
            m =  mpfit.mpfit(phot_funct, functkw=fa,
                             parinfo=parinfo,
                             maxiter=1000, quiet=1)
            print m.covar, m.params, m.perror 
            if (m.status <= 0):
                print 'error message = ', m.errmsg
                condition = Numeric.zeros(len(data))
                break

            #airmass = copy.copy(airmass_save)
            #color = copy.copy(color_save)
            #data = copy.copy(data_save)
            #err = copy.copy(err_save)

            # Compute a 3 sigma rejection criterion
            #condition = preFilter(m.params, data_save, data,
            #                           airmass_save, airmass,
            #                           color_save, color)

            params = [0,0,0] 
            perror = [0,0,0]

            print m.params,m.perror, m.covar
            if fit_type == 0:
                params = copy.copy(m.params)
                perror = copy.copy(m.perror)

            if fit_type == 1:
                params[0] = m.params[0]
                params[2] = m.params[1]
                params[1] = p[1]
                perror[0] = m.perror[0]
                perror[2] = m.perror[1]
                
            if fit_type == 2:
                params[0] = m.params[0]
                params[1] = p[1]
                params[2] = p[2]
                perror[0] = m.perror[0]

            # Compute a 3 sigma rejection criterion
            print params, data_rec[0], data[0]
            condition, redchisq = SigmaCond(params, data_save, data,
                                       airmass_save, airmass,
                                       color_save, color, err_save, err, sigmareject)
          
            print redchisq 
            # Keep everything (from the full data set!) that is within
            # the 3 sigma criterion
            #data_sig = Numeric.compress(condition, data_save)
            data = Numeric.compress(condition, data_rec)
            airmass = Numeric.compress(condition, airmass_save)
            color = Numeric.compress(condition, color_save)
            err = Numeric.compress(condition, err_save)
            new_len = len(data)
           
            if float(new_len)/float(save_len) < 0.5:
                print "Rejected more than 50% of all measurements."
                print "Aborting this fit."
                break
            
            # No change
            if new_len == old_len:
                print "Converged! (%d iterations)" % (i+1, )
                print "Kept %d/%d stars." % (new_len, save_len)
                break
        print params, perror, condition
        meanerr = Numeric.sum(err_save)/len(err_save)
        solutions.append([params, perror, redchisq, meanerr, condition])
    return solutions


def SigmaCond(p, data_save, data, airmass_save, airmass, color_save, color, err_save, err, sigmareject):
    if len(data_save) > 1:
        #airmass = airmass[int(0.1*len(airmass)):int(0.9*len(airmass))]
        #color = color[int(0.1*len(color)):int(0.9*len(color))]
        #data = data[int(0.1*len(data)):int(0.9*len(data))]
        mo = p[0] + p[1]*airmass + p[2]*color
        mo_save = p[0] + p[1]*airmass_save + p[2]*color_save
        print len(data), len(mo), len(err)
        reddm = (data-mo)/err
        redchisq = Numeric.sqrt(Numeric.sum(Numeric.power(reddm, 2)) / (len(reddm) - 1))
        dm = data-mo
        dm_save = data_save - mo_save
        mean =  Numeric.sum(dm)/len(dm)
        sigma = Numeric.sqrt(Numeric.sum(Numeric.power(mean-dm, 2)) / (len(dm) - 1))
        #condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * sigma)
        condition = Numeric.less(Numeric.fabs(dm_save), float(sigmareject) * err_save)
    else:
        condition = Numeric.zeros(len(data_save))
    return condition, redchisq

def makePlots(data, airmass, color, outfile, solutions, label):
    file = outfile+".ps"
    pgbeg(file+"/cps", 2, 3)

    pgiden()
    for i in range(3):
        result = solutions[i]

        # Airmass plot
        pgpanl(1, i+1)
        airMin = 1
        airMax = Numeric.sort(airmass)[-1]*1.1
        print result
        dataAirMax = result[0][0]+result[0][1]+1
        dataAirMin = result[0][0]+result[0][1]-1
        dataColMax = result[0][0]+1
        dataColMin = result[0][0]-1
        colMinVal = Numeric.sort(color)[0]
        if colMinVal < 0:
            colMin = colMinVal*1.1
        else:
            colMin = colMinVal*0.95
        colMax = Numeric.sort(color)[-1]*1.1
        
        if result[0] and result[1]:
            eqStr = "%d parameter fit: Mag-Mag(Inst) = %.2f\\(2233)%.2f + (%.2f\\(2233)%.2f) airmass + "\
                    "(%.2f\\(2233)%.2f) color" % \
                    (3-i, result[0][0], result[1][0], result[0][1], result[1][1], result[0][2], result[1][2])
        else:
            eqStr = "%d parameter fit not possible" % (3-i, )
        
        fixenv([1, airMax] ,
               [dataAirMin, dataAirMax],
               eqStr, label=["Airmass", "Mag - Mag(Inst)"])

        condition = result[4]
        goodAirmass = Numeric.compress(condition, airmass)
        goodData = Numeric.compress(condition, data)
        goodColor = Numeric.compress(condition, color)
        badAirmass = Numeric.compress(Numeric.logical_not(condition), airmass)
        badData = Numeric.compress(Numeric.logical_not(condition), data)
        badColor = Numeric.compress(Numeric.logical_not(condition), color)
       
        if len(goodData):
            pgsci(3)
            # Rescale to zero color and filter for data within
            # our plotting range
            plotData = goodData-result[0][2]*goodColor
            plotCond1 = Numeric.less(plotData, dataAirMax)
            plotCond2 = Numeric.greater(plotData, dataAirMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotAirmass = Numeric.compress(plotCond, goodAirmass)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotAirmass, plotData, 5)
            print type(plotAirmass), type(plotData)

        if len(badData):
            pgsci(2)
            plotData = badData-result[0][2]*badColor
            plotCond1 = Numeric.less(plotData, dataAirMax)
            plotCond2 = Numeric.greater(plotData, dataAirMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotAirmass = Numeric.compress(plotCond, badAirmass)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotAirmass, plotData, 5)
        pgsci(1)

        a = Numeric.arange(1, airMax, 0.01)
        m = result[0][0] + result[0][1] * a
        pgline(a, m)
        
        # Color Plot
        pgpanl(2, i+1)

        fixenv([colMin, colMax] ,
               [dataColMin, dataColMax],
               eqStr, label=[label, "Mag - Mag(Inst)"])

        if len(goodData):
            pgsci(3)
            # Rescale to zero airmass and filter for data within
            # our plotting range
            plotData = goodData-result[0][1]*goodAirmass
            plotCond1 = Numeric.less(plotData, dataColMax)
            plotCond2 = Numeric.greater(plotData, dataColMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotColor = Numeric.compress(plotCond, goodColor)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotColor, plotData, 5)
        if len(badData):
            pgsci(2)
            plotData = badData-result[0][1]*badAirmass
            plotCond1 = Numeric.less(plotData, dataColMax)
            plotCond2 = Numeric.greater(plotData, dataColMin)
            plotCond = Numeric.logical_and(plotCond1, plotCond2)
            plotColor = Numeric.compress(plotCond, badColor)
            plotData = Numeric.compress(plotCond, plotData)
            pgpt(plotColor, plotData, 5)
        pgsci(1)

        a = Numeric.arange(colMin, colMax, 0.01)
        m = result[0][0] + result[0][2] * a
        pgline(a, m)
    return

def fixenv (xrange=[0,1], yrange=[0,1], fname="none", ci = 1, label=["x", "y"]):
                              # set axis ranges.
    pgswin(xrange[0], xrange[1], yrange[0], yrange[1])     
    pgsci(ci)                # set color index.
    pgbox()                  # draw axes. 
    pgsci(1)                 # back to color index 1 (white)
    pglab(label[0], label[1], fname)     # label the plot
    return


def saveResults(file, solutions, step, sigmareject, cluster, colorused):
    f = open(file+".asc", "w")
    which_solution = 0
    
    import MySQLdb, sys, os, re                                                                         
    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()
    #c.execute("DROP TABLE IF EXISTS photometry_db")

    for result in solutions:
        which_solution += 1
        if Numeric.sometrue(result[2]):
            import os , time
            user_name = os.environ['USER']
            bonn_target = os.environ['BONN_TARGET']
            bonn_filter = os.environ['BONN_FILTER']
            time_now = time.asctime() 
            user = user_name #+ str(time.time())
            standardstartype = os.environ['STANDARDSTARTYPE']
            floatvars = {'ZP':result[0][0],'AIRMASS':result[0][1],'COLOR':result[0][2],'ZPERR':result[1][0],'AIRMASSERR':result[1][1],'COLORERR':result[1][2],'REDCHISQ':result[2],'MEANERR':result[3]} 
            stringvars = {'USER':user_name,'BONN_TARGET':bonn_target,'BONN_FILTER':bonn_filter,'TIME':time_now,'CHOICE':'', 'NUMBERVARS':4-which_solution,'STANDARDSTARTYPE':standardstartype,'USER': user, 'step': step, 'sigmareject':sigmareject, 'cluster':cluster,'colorused':colorused} 
 
            # make database if it doesn't exist
            make_db = reduce(lambda x,y: x + ',' + y,[x  + ' float(30)' for x in floatvars.keys()])
            make_db += ',' + reduce(lambda x,y: x + ',' + y,[x  + ' varchar(80)' for x in stringvars.keys()])
            command = "CREATE TABLE IF NOT EXISTS photometry_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id), " + make_db + ")"
            print command
            #c.execute(command)

            # insert new observation 
            names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
            values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])

            names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
            values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])

            command = "INSERT INTO photometry_db (" + names + ") VALUES (" + values + ")"
            print command
            #c.execute(command)

            f.write("%s %s %s\n" % (result[0][0], result[0][1], result[0][2]))
            f.write("%s %s %s\n" % (result[1][0], result[1][1], result[1][2]))
            f.write("%s#ReducedChiSq\n" % (result[2]))
            f.write("%s#MeanError\n" % (result[3]))
            f.write("%s\n" % (id))
        else:
            f.write("-1 -1 -1\n")
            f.write("-1 -1 -1\n")
            f.write("-1#ReducedChiSq\n")
            f.write("-1#MeanError\n")
            f.write("%s\n" % (id))
    f.close
    return id
                


def usage():
    print "Usage:"
    print "photo_abs.py -i input -f filter -n GABODSID - e ext. coeff. -c color coeff. -o output -l label"
    print
    print "    -i, --input=STRING        Input file, must have 4 columns: Instrumental Mag, Standard Mag, Color, Airmass"
    print "    -o, --output=STRING       Output file basename"
    print "    -n, --night=INT           GABODSID, unique numerical night identifier"
    print "    -e, --extinction=FLOAT    Default value of extinction coefficient for one/two parameter fit"
    print "    -c, --color=FLOAT         Default value of color term for one parameter fit"
    print "    -l, --label=STRING        Label for color axis (e.g. B-V)"
    print
    print "Author:"
    print "    Joerg Dietrich <dietrich@astro.uni-bonn.de>"
    print
    return
    


if __name__ == "__main__":

    __bonn_logger_id__ = BonnLogger.addCommand('maskBadOverscans.py', 
                                                       sys.argv[1:])


    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "i:n:o:e:c:l:s:",
                                   ["input=", "night=", "extinction=",
                                    "color=", "output=", "label=","sigmareject=","step=","cluster=","colorused="])
    except getopt.GetoptError:
        usage()
        BonnLogger.updateStatus(__bonn_logger_id__, 1)
        sys.exit(2)
    print sys.argv[1:]

    infile = night = extcoeff = colcoeff = outfile = label = sigmareject = step = cluster = colorused = None
    for o, a in opts:
        if o in ("-i", "--input"):
            infile = a
        elif o in ("-o", "--output"):
            outfile = a
        elif o in ("-n", "--night"):
            night = int(a)
        elif o in ("-e", "--extinction"):
            extcoeff  = float(a)
        elif o in ("-c", "--color"):
            colcoeff = float(a)
        elif o in ("-l", "--label"):
            label = a
        elif o in ("-s", "--sigmareject"):
            sigmareject = float(a)
        elif o in ("-t", "--step"):
            step = a
        elif o in ("-c", "--cluster"):
            cluster = a
        elif o in ("-u", "--colorused"):
            colorused = a
        else:
            print "option:", o
            usage()
            BonnLogger.updateStatus(__bonn_logger_id__, 1)
            sys.exit(2)
    print cluster
    #raw_input()
            
    if not infile or night==None or not outfile or \
           extcoeff==None or colcoeff==None or label==None:
        #print infile, night, outfile, coeff, color
        usage()
        BonnLogger.updateStatus(__bonn_logger_id__, 1)
        sys.exit(2)

    data, airmass, color, magErr = readInput(infile)
    solutions = photCalib(data, airmass, color, magErr, [24, extcoeff, colcoeff], sigmareject)
    makePlots(data, airmass, color, outfile, solutions, label)
    saveResults(outfile, solutions, step, sigmareject, cluster, colorused)

    BonnLogger.updateStatus(__bonn_logger_id__, 0)
