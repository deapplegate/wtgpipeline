#!/usr/bin/env python
######################
# Tests multiple parts of the photometry pipeline as an integrated unit
# ie do_photometry(_3sec).sh CALIB APPLY SLR
######################

import unittest, sys, shutil, os, subprocess, utilities
import numpy as np, pyfits
import ldac

######################

__cvs_id__ = "$Id: test_calibration_pipeline.py,v 1.2 2010-09-01 01:38:56 dapple Exp $"

######################

os.environ['PHOTOMETRY_TEST'] = '1'

import measure_unstacked_photometry, fit_phot, photocalibrate_cat

import photometry_db
assert(photometry_db.testMode)

#####



#####

class TestPipeline(unittest.TestCase):

    def makeAllPhotCat(self):

        cols = []
        cols.append(pyfits.Column(name = 'SeqNr', format = 'J', array = np.arange(1, 501)))

        alpha = 152.136393
        delta = 56.703567
        cols.append(pyfits.Column(name = 'ALPHA_J2000', format = 'E', array = alpha*np.ones(500)))
        cols.append(pyfits.Column(name = 'DELTA_J2000', format = 'E', array = delta*np.ones(500)))
        self.target_mag = 25.5
        ebv = utilities.getDust([alpha], [delta])
        for filter, zp in self.targetZPs.iteritems():

            extinction = utilities.getExtinction(filter)
            
            raw_mag = (self.target_mag - zp + ebv*extinction)*np.ones(500)
            raw_flux = 10**(-0.4*(raw_mag))
            fluxerr = 0.002*raw_flux
            flux = raw_flux + fluxerr*np.random.standard_normal(500)
            mags, magerrs = measure_unstacked_photometry.calcMags(flux, fluxerr)



            cols.append(pyfits.Column(name = 'MAG_%s-%s' % (self.fluxtype, filter), format = 'E', array = mags))
            cols.append(pyfits.Column(name = 'MAGERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = magerrs))
            cols.append(pyfits.Column(name = 'FLUX_%s-%s' % (self.fluxtype, filter), format = 'E', array = flux))
            cols.append(pyfits.Column(name = 'FLUXERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxerr))

        hdu = pyfits.new_table(pyfits.ColDefs(cols))
        hdu.header.update('EXTNAME', 'OBJECTS')
        hdu.writeto(self.all_phot_file, clobber=True)
        self.uncalibrated = ldac.LDACCat(hdu)


    ####
    def makeStarCats(self):

        ### star catalogs

        seqnr = np.arange(501, 601)
        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = np.random.randint(0, len(pickles), len(seqnr))
        filter_cols = {}
        for filter, zp in self.targetZPs.iteritems():

            if filter == 'SUBARU-COADD-1-W-J-V':
                raw_mag = pickles['SUBARU-10_2-1-W-J-V'][sample]
            else:
                raw_mag = pickles[filter][sample]
            raw_flux = 10**(-0.4*(raw_mag - zp))
            fluxerr = 0.002*raw_flux
            flux = raw_flux + fluxerr*np.random.standard_normal(len(sample))
            mags, magerrs = measure_unstacked_photometry.calcMags(flux, fluxerr)

            filter_cols[filter] = [mags, magerrs, flux, fluxerr]


        ### star cat 
        cols = []
        cols.append(pyfits.Column(name = 'SeqNr', format = 'J', array = seqnr))
        cols.append(pyfits.Column(name = 'ALPHA_J2000', format = 'E', array = 152.136393*np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'DELTA_J2000', format = 'E', array = 56.703567*np.ones_like(seqnr)))
        for filter, (mags, magerrs, fluxs, fluxerrs) in filter_cols.iteritems():
            cols.append(pyfits.Column(name = 'MAG_%s-%s' % (self.fluxtype, filter), format = 'E', array = mags))
            cols.append(pyfits.Column(name = 'MAGERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = magerrs))
            cols.append(pyfits.Column(name = 'FLUX_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxs))
            cols.append(pyfits.Column(name = 'FLUXERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxerrs))

        hdu = pyfits.new_table(pyfits.ColDefs(cols))
        hdu.header.update('EXTNAME', 'OBJECTS')
        hdu.writeto(self.star_cat_file, clobber=True)

        ### matched catalog

        cols = []
        cols.append(pyfits.Column(name = 'SeqNr', format = 'J', array = seqnr))
        for filter, (mags, magerrs, fluxs, fluxerrs) in filter_cols.iteritems():
            cols.append(pyfits.Column(name = 'SEx_MAG_%s-%s' % (self.fluxtype, filter), format = 'E', array = mags))
            cols.append(pyfits.Column(name = 'SEx_MAGERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = magerrs))
            cols.append(pyfits.Column(name = 'SEx_FLUX_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxs))
            cols.append(pyfits.Column(name = 'SEx_FLUXERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxerrs))

        cols.append(pyfits.Column(name = 'Clean', format = 'J', array = np.zeros_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_BackGr', format = 'E', array = np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_Flag', format = 'J', array = np.zeros_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_Xpos', format = 'E', array = np.random.uniform(0, 5000, len(seqnr))))
        cols.append(pyfits.Column(name = 'SEx_Ypos', format = 'E', array = np.random.uniform(0, 5000, len(seqnr))))
        


        for sdss in 'u g r i z'.split():

            cols.append(pyfits.Column(name = '%smag' % sdss, format = 'E', array = pickles_sdss['%sp' % sdss][sample]))
            cols.append(pyfits.Column(name = '%serr' % sdss, format = 'E', array = 0.2*pickles_sdss['%sp' % sdss][sample]))

        for color in 'umg gmr rmi imz'.split():

            f1, f2 = color.split('m')

            cols.append(pyfits.Column(name = color, format = 'E', array = pickles_sdss['%sp' % f1][sample] - pickles_sdss['%sp' % f2][sample]))
            cols.append(pyfits.Column(name = '%serr' % color, format = 'E', array = 0.2*np.ones_like(seqnr)))


        hdu = pyfits.new_table(pyfits.ColDefs(cols))
        hdu.header.update('EXTNAME', 'PSSC')

        hdu.writeto(self.matched_catalog_file, clobber=True)


    ####


    def setUp(self):

        self.photrepo = '/nfs/slac/g/ki/ki06/anja/SUBARU/photometry'
        self.subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
        self.cluster = 'pipeline_testcluster'
        self.maindir = '%s/%s' % (self.subarudir, self.cluster)
        self.lensing_filter = 'W-J-V'
        self.detect_filter = 'W-J-V'
        self.photdir = '%s/%s/PHOTOMETRY_%s_%s' % (self.photrepo, self.cluster, self.detect_filter, self.mode)
        self.slr_cat = '%s/%s.slr.cat' % (self.photdir, self.cluster)

        self.matched_catalog_file = '%s/%s.sdss.matched.cat' % (self.photdir, self.cluster)
        self.star_cat_file = '%s/%s.stars.cat' % (self.photdir, self.cluster)
        self.all_phot_file = '%s/%s.unstacked.cat' % (self.photdir, self.cluster)

        self.targetZPs = {'SUBARU-10_2-1-W-J-V' : 27.05,
                          'SUBARU-10_1-1-W-J-V' : 26.90,
                          'SUBARU-COADD-1-W-J-V' : 27.00,
                          'SUBARU-8-2-W-C-RC' : 28.1,
                          'SPECIAL-0-1-K' : 23.0,
                          'MEGAPRIME-0-1-u' : 24.6,
                          'SUBARU-9-1-W-C-IC' : 27.25,
                          'SUBARU-9-2-W-C-IC' : 27.35}
      
                          

        if os.path.exists(self.maindir):
            shutil.rmtree(self.maindir)
        if os.path.exists(self.photdir):
            shutil.rmtree(self.photdir)

        os.mkdir(self.maindir)
        os.mkdir(self.photdir)
        os.symlink(self.photdir, '%s/PHOTOMETRY_%s_%s' % (self.maindir, self.detect_filter, self.mode))


        #seqnr 1 - 500 are galaxies, 501 - 600 are stars

        self.makeAllPhotCat()

        
        self.makeStarCats()


        ### SPECIAL-K and MEGAPRIME FAKERY
        os.makedirs('%s/K/SCIENCE/coadd_%s_all' % (self.maindir, self.cluster))
        hdu = pyfits.PrimaryHDU(np.ones((100,100)))
        hdu.header.update('MAGZP', 22.7)
        hdu.writeto('%s/K/SCIENCE/coadd_%s_all/coadd.fits' % (self.maindir, self.cluster), clobber=True)

        os.makedirs('%s/u/SCIENCE/coadd_%s_all' % (self.maindir, self.cluster))
        hdu = pyfits.PrimaryHDU(np.ones((100,100)))
        hdu.header.update('MAGZP', self.targetZPs['MEGAPRIME-0-1-u'])
        hdu.writeto('%s/u/SCIENCE/coadd_%s_all/coadd.fits' % (self.maindir, self.cluster), clobber=True)


            
            

    ######

    def tearDown(self):
        pass
#        if os.path.exists(self.maindir):
#            shutil.rmtree(self.maindir)
#        if os.path.exists(self.photdir):
#            shutil.rmtree(self.photdir)
#
    ######

    def testCalibration(self):

        retcode = subprocess.call(('./do_photometry.sh %(cluster)s %(detect)s %(lensing)s %(mode)s CALIB' % \
                                      {'cluster' : self.cluster,
                                       'detect' : self.detect_filter,
                                       'lensing' : self.lensing_filter,
                                       'mode' : self.mode}).split())

        self.assertEquals(retcode, 0)

        db = photometry_db.Photometry_db()

        for filter, zp in self.targetZPs.iteritems():
            if filter == 'SUBARU-COADD-1-W-J-V':
                continue
            calib = db.findCalibration(cluster = self.cluster, filter = filter, mode = self.mode).calibration
            self.assertTrue(calib is not None)
            self.assertTrue(np.abs(calib.zp - zp) < 1.0, '%s %3.2f %3.2f' % (filter, calib.zp, zp))


        retcode = subprocess.call(('./do_photometry.sh %(cluster)s %(detect)s %(lensing)s %(mode)s APPLY SLR' % \
                                      {'cluster' : self.cluster,
                                       'detect' : self.detect_filter,
                                       'lensing' : self.lensing_filter,
                                       'mode' : self.mode}).split())


        self.assertEquals(retcode, 0)

        self.assertTrue(os.path.exists(self.slr_cat))
        
        calibrated = ldac.openObjectFile(self.slr_cat)
        self.assertTrue((self.uncalibrated['SeqNr'] == calibrated['SeqNr']).all())

        zp_cat = ldac.openObjectFile(self.slr_cat, 'ZPS')
        zps = {}
        for filter, zp in zip(zp_cat['filter'], zp_cat['zeropoints']):
            zps[filter] = zp
        
        for filter, zp in self.targetZPs.iteritems():

            self.assertTrue(np.abs(zp - zps[filter]) < 1.0, '%s %3.2f %3.2f' % (filter, calib.zp,zp))

            magname = 'MAG_%s-%s' % (self.fluxtype, filter)

            self.assertTrue((np.abs(self.target_mag - calibrated[magname]) < 1).all(), 'Filter: %s Target: %3.3f Actual: %3.3f' % (filter, self.target_mag, calibrated[magname][0]))
            





#############################

class TestPipelineAPER(TestPipeline):

    def setUp(self):
        self.mode = 'aper'
        self.fluxtype = 'APER1'
        TestPipeline.setUp(self)
        
######################################

class TestPipelineISO(TestPipeline):
    
    def setUp(self):

        self.mode = 'iso'
        self.fluxtype = 'ISO'
        TestPipeline.setUp(self)

        #setup some confusing database entries

        db = photometry_db.Photometry_db()

        for filter in self.targetZPs.keys():

            cali = db.registerSpecialFiltersCalibration(self.cluster, filter=filter, file = 'fakefile', zp=10., mode='aper')
            db.updateCalibration(self.cluster, filter = filter, calibration = cali, mode='aper' )

########################################

class TestPipeline3Sec(TestPipeline):

    def setUp(self):
        
        self.mode='iso'
        self.fluxtype = 'ISO'

        self.photrepo = '/nfs/slac/g/ki/ki06/anja/SUBARU/photometry'
        self.subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
        self.cluster = 'pipeline_testcluster'
        self.maindir = '%s/%s' % (self.subarudir, self.cluster)
        self.lensing_filter = 'W-J-V'
        self.detect_filter = 'W-J-V'
        self.photdir = '%s/%s/PHOTOMETRY_%s_%s' % (self.photrepo, self.cluster, self.detect_filter, self.mode)
        self.slr_cat = '%s/%s.slr.cat' % (self.photdir, self.cluster)

        self.star_cat_file = '%s/%s.stars.cat' % (self.photdir, self.cluster)
        self.all_phot_file = '%s/%s.unstacked.cat' % (self.photdir, self.cluster)

        self.phot3secdir = '%s/W-C-RC_2007-07-18_CALIB/PHOTOMETRY_3sec' % (self.maindir)
        self.matched_catalog_file = '%s/%s.sdss.matched.cat' % (self.phot3secdir, self.cluster)



        self.targetZPs = {'SUBARU-10_2-1-W-J-V' : 27.05,
                          'SUBARU-10_1-1-W-J-V' : 26.90,
                          'SUBARU-COADD-1-W-J-V' : 27.00,
                          'SUBARU-8-2-W-C-RC' : 28.1,
                          'SPECIAL-0-1-K' : 23.0,
                          'MEGAPRIME-0-1-u' : 24.6,
                          'SUBARU-9-1-W-C-IC' : 27.25,
                          'SUBARU-9-2-W-C-IC' : 27.35}
      
                          


        if os.path.exists(self.maindir):
            shutil.rmtree(self.maindir)
        if os.path.exists(self.photdir):
            shutil.rmtree(self.photdir)

        os.mkdir(self.maindir)
        os.mkdir(self.photdir)
        os.symlink(self.photdir, '%s/PHOTOMETRY_%s_%s' % (self.maindir, self.detect_filter, self.mode))

        os.makedirs(self.phot3secdir)



        #seqnr 1 - 500 are galaxies, 501 - 600 are stars

        self.makeAllPhotCat()

        
        self.makeStarCats()


        ### SPECIAL-K and MEGAPRIME FAKERY
        os.makedirs('%s/K/SCIENCE/coadd_%s_all' % (self.maindir, self.cluster))
        hdu = pyfits.PrimaryHDU(np.ones((100,100)))
        hdu.header.update('MAGZP', 22.7)
        hdu.writeto('%s/K/SCIENCE/coadd_%s_all/coadd.fits' % (self.maindir, self.cluster), clobber=True)

        os.makedirs('%s/u/SCIENCE/coadd_%s_all' % (self.maindir, self.cluster))
        hdu = pyfits.PrimaryHDU(np.ones((100,100)))
        hdu.header.update('MAGZP', self.targetZPs['MEGAPRIME-0-1-u'])
        hdu.writeto('%s/u/SCIENCE/coadd_%s_all/coadd.fits' % (self.maindir, self.cluster), clobber=True)






    ####

    def makeStarCats(self):

        ### star catalogs

        seqnr = np.arange(501, 601)
        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = np.random.randint(0, len(pickles), len(seqnr))

        filter_cols = {}
        for filter, zp in self.targetZPs.iteritems():

            if filter == 'SUBARU-COADD-1-W-J-V':
                raw_mag = pickles['SUBARU-10_2-1-W-J-V'][sample]
            else:
                raw_mag = pickles[filter][sample]
            raw_flux = 10**(-0.4*(raw_mag - zp))
            fluxerr = 0.002*raw_flux
            flux = raw_flux + fluxerr*np.random.standard_normal(len(sample))
            mags, magerrs = measure_unstacked_photometry.calcMags(flux, fluxerr)

            filter_cols[filter] = [mags, magerrs, flux, fluxerr]


        ### star cat 
        cols = []
        cols.append(pyfits.Column(name = 'SeqNr', format = 'J', array = seqnr))
        cols.append(pyfits.Column(name = 'ALPHA_J2000', format = 'E', array = 152.136393*np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'DELTA_J2000', format = 'E', array = 56.703567*np.ones_like(seqnr)))
        for filter, (mags, magerrs, fluxs, fluxerrs) in filter_cols.iteritems():
            cols.append(pyfits.Column(name = 'MAG_%s-%s' % (self.fluxtype, filter), format = 'E', array = mags))
            cols.append(pyfits.Column(name = 'MAGERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = magerrs))
            cols.append(pyfits.Column(name = 'FLUX_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxs))
            cols.append(pyfits.Column(name = 'FLUXERR_%s-%s' % (self.fluxtype, filter), format = 'E', array = fluxerrs))

        hdu = pyfits.new_table(pyfits.ColDefs(cols))
        hdu.header.update('EXTNAME', 'OBJECTS')
        hdu.writeto(self.star_cat_file, clobber=True)

        ### matched catalog

        cols = []
        cols.append(pyfits.Column(name = 'SeqNr', format = 'J', array = seqnr))
        filter = 'SUBARU-8-2-W-C-RC'
        mags, magerrs, fluxs, fluxerrs = filter_cols[filter]

        threesec_flux, threesec_fluxerr = photocalibrate_cat.applyOffset(fluxs, fluxerrs, fit_phot.__3sec_zp__)
        threesec_mags, threesec_magerrs = measure_unstacked_photometry.calcMags(threesec_flux, threesec_fluxerr)
        

        cols.append(pyfits.Column(name = 'SEx_MAG_AUTO', format = 'E', array = threesec_mags))
        cols.append(pyfits.Column(name = 'SEx_MAGERR_AUTO', format = 'E', array = threesec_magerrs))
        cols.append(pyfits.Column(name = 'SEx_FLUX_AUTO', format = 'E', array = threesec_flux))
        cols.append(pyfits.Column(name = 'SEx_FLUXERR_AUTO', format = 'E', array = threesec_fluxerr))

        cols.append(pyfits.Column(name = 'Clean', format = 'J', array = np.zeros_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_BackGr', format = 'E', array = np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = np.ones_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_Flag', format = 'J', array = np.zeros_like(seqnr)))
        cols.append(pyfits.Column(name = 'SEx_Xpos', format = 'E', array = np.random.uniform(0, 5000, len(seqnr))))
        cols.append(pyfits.Column(name = 'SEx_Ypos', format = 'E', array = np.random.uniform(0, 5000, len(seqnr))))
        


        for sdss in 'u g r i z'.split():

            cols.append(pyfits.Column(name = '%smag' % sdss, format = 'E', array = pickles_sdss['%sp' % sdss][sample]))
            cols.append(pyfits.Column(name = '%serr' % sdss, format = 'E', array = 0.2*pickles_sdss['%sp' % sdss][sample]))

        for color in 'umg gmr rmi imz'.split():

            f1, f2 = color.split('m')

            cols.append(pyfits.Column(name = color, format = 'E', array = pickles_sdss['%sp' % f1][sample] - pickles_sdss['%sp' % f2][sample]))
            cols.append(pyfits.Column(name = '%serr' % color, format = 'E', array = 0.2*np.ones_like(seqnr)))


        hdu = pyfits.new_table(pyfits.ColDefs(cols))
        hdu.header.update('EXTNAME', 'PSSC')

        hdu.writeto(self.matched_catalog_file, clobber=True)


    ###

    def testCalibration(self):

        retcode = subprocess.call(('./do_photometry_3sec.sh %(cluster)s %(detect)s %(mode)s CALIB' % \
                                      {'cluster' : self.cluster,
                                       'detect' : self.detect_filter,
                                       'mode' : self.mode}).split())

        self.assertEquals(retcode, 0)

        db = photometry_db.Photometry_db()
        calib = db.getZeropoint(cluster = self.cluster, filter = 'SUBARU-8-2-W-C-RC', mode=self.mode)
        self.assertTrue(calib is not None)
        self.assertTrue(np.abs(calib.zp - self.targetZPs['SUBARU-8-2-W-C-RC']) < 1.)
        

        retcode = subprocess.call(('./do_photometry.sh %(cluster)s %(detect)s %(lensing)s %(mode)s APPLY SLR' % \
                                       {'cluster' : self.cluster,
                                        'detect' : self.detect_filter,
                                        'lensing' : self.lensing_filter,
                                        'mode' : self.mode}).split())

        self.assertEquals(retcode, 0)


        self.assertTrue(os.path.exists(self.slr_cat))

        zp_cat = ldac.openObjectFile(self.slr_cat, 'ZPS')
        zps = {}
        for filter, zp in zip(zp_cat['filter'], zp_cat['zeropoints']):
            zps[filter] = zp
        
        for filter, zp in self.targetZPs.iteritems():

            self.assertTrue(np.abs(zp - zps[filter]) < 1.0)




##############################

def test():

#    testcases = [TestPipelineISO, TestPipelineAPER, TestPipeline3Sec]
    testcases = [TestPipelineAPER]


    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)



##############################
# COMMANDLINE EXECUTABLE
##############################

if __name__ == '__main__':
    
    test()

