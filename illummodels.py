########################
# @file illummodels.py
# @date 3/23/2009
## Storage model for illumination correction models
########################

from numpy import *
import os.path, re, astropy.io.fits as pyfits, sys, illumcorutils

##########################

__cvs_id__ = "$Id: illummodels.py,v 1.10 2009-05-14 21:33:11 dapple Exp $"

##########################

# Example
def BiPolyBasis(order):
    # c + x + y + x^2 + xy + y^2 + ...
    basis = [lambda x,y: 1]
    for o in xrange(1,order+1):
        for pow in xrange(0,o):
            def base(x,y):
                return (x**(o-pow))*(y**(pow))
            basis.append(base)
    return basis

def BiPolyModel(params, order):

    def model(x,y):

        paramIndex = 0
        sum = params[paramIndex]*ones_like(x)
        paramIndex += 1

        for o in xrange(1,order+1):
            for pow in xrange(0,o+1):
                sum += params[paramIndex]*(x**(o-pow))*(y**(pow))
                paramIndex += 1
        return sum


    return model

###############################################

chebyshev3 = [lambda x:ones_like(x),
              lambda x:x,
              lambda x:2*x**2-1,
              lambda x:4*x**3.-3*x]

#assumes chips are on a global coordinate system of [0,1e4]
cheby_coord_conv_x = lambda x:( 2.*x - 10460) / 10460.
cheby_coord_conv_y = lambda y:( 2.*y - 10000) / 10000.

def Chebeyshev3Model(params):

    def model(x,y):

        xp = cheby_coord_conv_x(x)
        yp = cheby_coord_conv_y(y)

        sum = zeros_like(x)
        xchebys = [f(xp) for f in chebyshev3]
        ychebys = [f(yp) for f in chebyshev3]
        paramCount = 0
        for i in xrange(4):
            for j in xrange(4):
                sum = sum + params[paramCount]*xchebys[i]*ychebys[j]
                paramCount += 1
        
        return sum

    return model

##################################################

class UnreadableException(Exception): pass

#################################################

###For now, just assume 3rd order
def readChebyCoeffs(fitInfo, rotation):

#    sample = fitInfo['sample']
    sample='sdss'
    column_prefix = '%s$all' % sample

    print fitInfo['%s$positioncolumns' % column_prefix]

    params = zeros(16)
    paramCount = 0
    for i in xrange(4):
        for j in xrange(4):
            term = '%(rot)d$%(xterm)dx%(yterm)dy' % {'rot' : rotation,
                                                     'xterm' : i, 
                                                     'yterm' : j}
            colname = '%s$%s' % (column_prefix, term)
            if colname in fitInfo and fitInfo[colname] is not None and term in fitInfo['%s$positioncolumns' % column_prefix]:
                params[paramCount] = float(fitInfo[colname])
                print '%s %f' % (colname, params[paramCount])
            paramCount += 1

    return params
            

##################################################

def findExposureModel(filename):


    #need to know cluster, filter
    try:
        header = pyfits.getheader(filename)
    
        object = header['OBJNAME']
        filter = header['FILTER']
        pprun = header['PPRUN']
        rotation = header['ROTATION']

    except KeyError:
        raise UnreadableException('Cannot Read Header, Skipping: %s' % filename)


    fit = illumcorutils.get_fits(object, filter, pprun)

    coeffs = readChebyCoeffs(fit, rotation)

                                
    return Chebeyshev3Model(coeffs)

#################################################

#################################################

#assumes measured - standoardX
deltaMag2Flux =  lambda deltaMag: 10**(deltaMag/2.5)

subaru_chip_relpos = array([[ -0.00000000e+00,  -0.00000000e+00],
                            [  2.12800000e+03,  -3.00000000e+00],
                            [  4.22300000e+03,  -2.00000000e+00],
                            [  6.34600000e+03,  -3.00000000e+00],
                            [  8.50800000e+03,   5.00000000e+00],
                            [ -3.30000000e+01,   4.10700000e+03],
                            [  2.09600000e+03,   4.11500000e+03],
                            [  4.25200000e+03,   4.11200000e+03],
                            [  6.34000000e+03,   4.11900000e+03],
                            [  8.46800000e+03,   4.11900000e+03]])

def findCoordShift(chip):
    
    ###insert database calls here

    offset = subaru_chip_relpos[chip - 1]
    return lambda x,y : (x + offset[0], y + offset[1])
    
    

def findChipModel(filename):

    file = os.path.basename(filename)
    base, ext = os.path.splitext(filename)

    match = re.match('(\w+)_(\d+)', file)
    if match is None:
        sys.stderr.write('Cannot Understand Filename: %s\n' % file)
        return
    expid = match.group(1)
    chip = int(match.group(2))
    
    coordshift = findCoordShift(chip)

    exposureModel = findExposureModel(filename)
    
    illumModel = lambda x,y : deltaMag2Flux(exposureModel(*coordshift(x,y)))

    return illumModel
