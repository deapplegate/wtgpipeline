'''
All functions associated with crossval analysis of shape distributions, for purposes
of KIPAC tea talk, to take place on May 31
'''
#######################################

import shapedistro, crossval, glob, ldac, os, re
import numpy as np


#####################################


def makeMasterCrossval(nsets, dir, prefix, psf, component = None):

    
    shear, trueshear, snratio, size = shapedistro.prepCats(psf, component)

    cat = {'g' : shear,
           'true_g' : trueshear,
           'snratio' : snratio,
           'size' : size}

    crossval_cats = crossval.makeCrossValCats(cat, nsets)
    
    for i, training_testing_cats in enumerate(crossval_cats):

        basename = '%s/%s.s%d' % (dir, prefix, i)

        for cattype, crossvalcat in zip('training testing'.split(), training_testing_cats):
        
            catname = '%s.%s.cat' % (basename, cattype)

            print catname

            crossvalcat.saveas(catname, overwrite=True)



###############################################

def makeBinnedCats(dir, prefix, selectors, outputdir):

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    catfiles = glob.glob('%s/%s*.cat' % (dir, prefix))

    for catfile in catfiles:

        dirname, filebase = os.path.split(catfile)
        base, ext = os.path.splitext(filebase)

        basename='%s/%s' % (outputdir, base)

        cat = ldac.openObjectFile(catfile)



        bincats = crossval.createBins(cat, selectors)
        
        for key, bincat in bincats.iteritems():

            if key == '':

                catname = '%s.cat' % basename                

            else:
                
                catname =  '%s.%s.cat' % (basename, '.'.join(map(str, key)))
                   
            print catname

            bincat.saveas(catname, overwrite=True)



####################################################


sn_selectors = [lambda cat: cat['snratio'] < 4, 
                lambda cat: np.logical_and(cat['snratio'] >= 4, cat['snratio'] < 5),
                lambda cat: np.logical_and(cat['snratio'] >= 5, cat['snratio'] < 6),
                lambda cat: np.logical_and(cat['snratio'] >= 6, cat['snratio'] < 8),
                lambda cat: np.logical_and(cat['snratio'] >= 8, cat['snratio'] < 10),
                lambda cat: np.logical_and(cat['snratio'] >= 10, cat['snratio'] < 20),
                lambda cat: cat['snratio'] > 20]

size_selectors = [lambda cat: cat['size'] <= 1.5,
                  lambda cat: cat['size'] > 1.5]

size3_selectors = [lambda cat: cat['size'] <= 1.5,
                   lambda cat: np.logical_and(cat['size'] > 1.5, cat['size'] <= 2.5),
                   lambda cat: cat['size'] > 2.5]

size4_selectors = [lambda cat: cat['size'] <= 1.3,
                   lambda cat: np.logical_and(cat['size'] > 1.3, cat['size'] <= 1.5),
                   lambda cat: np.logical_and(cat['size'] > 1.5, cat['size'] <= 2.0),
                   lambda cat: cat['size'] > 2.0]




########################################################

def readPostPreds(dir, prefix):

    postpred = {}

    ppfiles = glob.glob('%s/%s*pp' % (dir, prefix))

    for ppfile in ppfiles:

        elements = ppfile.split('.')
        crosscat = int(elements[1].strip('s'))
        if crosscat not in postpred:
            postpred[crosscat] = 0


        input = open(ppfile)
        logp = float(input.readline())
        input.close()

        postpred[crosscat] += logp
        
    return postpred
            

