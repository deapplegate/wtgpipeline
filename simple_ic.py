#! /usr/bin/env python
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning
import pickle, sys, os, re, time, string, math
import random, tempfile, traceback, commands
import MySQLdb

from copy import copy
from glob import glob
import astropy, astropy.io.fits as pyfits, scipy, pylab, numpy
import config_bonn #only need "wavelength_groups"
import utilities
import bashreader #only need "parseFile"
global data_path, tmpdir, test
username = os.environ['USER']
if username=="awright":
        ## get/set env variables
        data_root = '/nfs/slac/g/ki/ki18/anja/SUBARU/' #adam-Warning#
        if 'SUBARUDIR' in os.environ.keys():
                if "pat" in os.environ['SUBARUDIR']: raise Exception("You have /nfs/slac/g/ki/ki18/anja/SUBARU/pat/ as your SUBARUDIR, this is a mistake right?")
        else:
                os.environ['SUBARUDIR']=data_root
        if 'cluster' in os.environ.keys():
                cluster=os.environ['cluster']
        else:
                cluster="MACS1226+21" #adam-Warning#

        ## mess with SQL databases
        #sql databases used by pat: illumination_db, test_try_db, test_fit_db, sdss_db
        #sql databases used by adam: adam_illumination_db, adam_try_db, adam_fit_db, sdss_db
        #c.execute(" CREATE TABLE adam_illumination_db LIKE illumination_db; ")
        #c.execute(" CREATE TABLE adam_try_db LIKE test_try_db; ")
        #c.execute(" CREATE TABLE adam_fit_db LIKE test_fit_db; ")
        #sdss_db will be fine, I can't really mess that one up
        test = 'adam_' #this takes care of test_try_db, test_fit_db #adam-Warning#
        illum_db="adam_illumination_db"

        ## set data_path and tmpdir
        data_path = data_root + cluster+'/'
        tmpdir=data_path+"tmp_simple_ic/"
        os.environ['bonn']='/u/ki/awright/bonnpipeline/' #adam-Warning#

elif username=="pkelly":
        data_root = '/nfs/slac/g/ki/ki18/anja/SUBARU/pat/'
        data_path = data_root + 'MACS1226+21/' #adam-Warning#
        test = 'test_'
        illum_db="illumination_db"
        ''' the idea here is to only create a new temp directory when loading the module for the first time -- otherwise, it will change each time you reload(simple_ic) '''
        if not 'loaded' in locals():
            #tmpdir = tempfile.mkdtemp(dir='/tmp/') + '/'
            #if not os.path.exists('/tmp/%s' % username):
            #    os.mkdir('/tmp/%s/' % username)
            #tmphome = tempfile.mkdtemp(dir='/tmp/%s/' % username) + '/'
            tmpdir = os.environ['subdir'] + '/pattmp/'
            #adam-del#tmphome = tmpdir
            loaded='yes'
else:
        #adam-Warning# set the needed info here regarding target, paths to data, and SQL db stuff
        ## get/set env variables
        if not 'bonn' in os.environ.keys(): raise Exception("Must have environment variable 'bonn' set to bonnpipeline path")

        if 'SUBARUDIR' in os.environ.keys():
                data_root=os.environ['SUBARUDIR']
        else:
                data_root="SET PATH to DATA DIRECTORY HERE" #adam-Warning#

        if 'cluster' in os.environ.keys():
                cluster=os.environ['cluster']
        else:
                cluster="SET CLUSTER NAME HERE" #adam-Warning#

        ## set data_path and tmpdir
        data_path = data_root + cluster+'/'
        tmpdir=data_path+"tmp_simple_ic/"

	#adam-Warning# either handle SQL tables here or at the end!
        #sql databases used by pat which you could copy the structure of: illumination_db, test_try_db, test_fit_db, sdss_db (see mysqldb_params below)
        test = 'name_' #this takes care of test_try_db, test_fit_db #name-Warning# change from generic "name" to username or something
        #c.execute(" CREATE TABLE "+test+"illumination_db LIKE illumination_db; ") #adam-Warning# run this once, then comment out
        #c.execute(" CREATE TABLE "+test+"try_db LIKE test_try_db; ") #adam-Warning# run this once, then comment out
        #c.execute(" CREATE TABLE "+test+"fit_db LIKE test_fit_db; ") #adam-Warning# run this once, then comment out
        #sdss_db will be fine, I can't really mess that one up
        illum_db=test+"illumination_db"

#adam-note# the program paths used in simple_ic.py should be taken from progs.ini for the sake of consistency, since os.system kinda uses whatever paths it wants!
#adam-note# program paths in progs.ini used in this code: "p_sex","p_ldacconv","p_ldactoasc","p_ldaccalc","p_dfits","p_asctoldac","p_ldacjoinkey","p_ldacfilter","p_ldacaddkey","p_associate","p_makessc"
#adam-note# programs used in simple_ic.py: progs=["sex","ldacconv","ldactoasc","ldaccalc","dfits","asctoldac","ldacjoinkey","ldacfilter","ldacaddkey","associate","make_ssc"]
progs_path= bashreader.parseFile(os.environ['bonn']+'/progs.ini') #adam-Warning# both use my progs.ini file so that we have a consistent set of catalogs/files

if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir) # same as: os.system('mkdir -p ' + tmpdir)

#adam-Warning# If you're not working at SLAC you're probably going to use a different mysqldb
mysqldb_params = {'db' : 'subaru',
                  'user' : 'weaklensing',
                  'passwd' : 'darkmatter',
                  'host' : 'ki-sr01'}

#adam-Warning# make this cut consistent with the deeper potential well of the 10_3 config for all funcs (did it for selectGoodStars so far)
config_dict={}
config_dict["SATURATION"]={ "10_1":27000.0 ,"10_2":27000.0 ,"10_3":30000.0 ,"8":27000.0 ,"9":27000.0 }
config_dict["GAIN"]={ "10_1":2.5 ,"10_2":2.5 ,"10_3":3.0 ,"8":2.5 ,"9":2.5 }

## Comments key

# Here are what my comments mean
#------------------------------|-------------------------------------------------------------------------------------------------------------------------------------#
#adam-Warning#		       this is OK for now, but shouldn't be kept like this long-term
#adam-tmp#		       this is commented out temporarily or it's a temporary line/block
#adam-no_more#                 this particular line used to be #adam-tmp#, but it isn't needed anymore, but I'm going to keep it around in case I might want it later
#adam-SHNT#		       Start Here Next Time (SHNT)
#adam-ask#		       I have a question to ask about this line/block of code
#adam-del#		       I think this should be removed later
#adam-fragments_removed#        this portion of the code was removed, if you want to recover it, it can be found in the fragments_removed.py file
#adam-note#                    most important note about whats going on here
#adam-watch#                   If there are problems with this func, then you might want to take another look at whats going on here:
#                              Either I'm suspicious of this part,
#                              or I didn't look at it in-depth,
#                              or I might have changed something (ex. the name of a file), which will later need to be made consistent with other funcs coppied in from calc_test_save.py


## Step by step

# all functions (funcs) have tags to classify them and which step they belong to. (i.e. #main is the main code for a given step and must be called in the body of simple_ic.py, #intermediate means the func is called by another func, etc.)
#Here are the steps that simple_ic.py carries out: (in parentheses are the funcs that each step begins with, i.e. the func with the tag #main)
#step1_add_database: first enter all exposures into the database (gather_exposures)
#step2_sextract    : run sextractor on them (get_astrom_run_sextract)
#step3_run_fit     : get the sdss catalogs and do fitting (match_OBJNAME)
#step4_test_fit    : assess the quality of the fit (testgood,sort_results)
#step5_correct_ims : apply correction to the data (currently it's construct_correction) (later maybe run_correction, find_nearby)


### Adam's Notes ###
#SCAMP reads SExtractor catalogues and produces FITS-like image headers that SWarp can read and use for image stacking and coadding.
#scamp: program that reads SExtractor catalogs (and their preliminary, approximate astrometric data) and computes astrometric and photometric solutions (these calibrations are saved in header files) for any arbitrary sequence of FITS images in an automatic way. Steps are:
#	1. Input catalogues and headers are read and checked for content. SCAMP sorts catalogues by position on the sky ("groups of fields") as well as astrometric and photometric contexts ("instruments").
#	2. Mosaics of detectors undergo a specic pre-treatment to homogenise the astrometric calibration across the focal plane.
#	3. A catalogue of astrometric standards ("reference catalogue") is downloaded from the Vizier database for every group.
#	4. The reference catalogues are utilised by a pattern matching procedure to register all input catalogues.
#	5. All detections and reference sources are cross-matched and an astrometric solution is computed.  This operation is repeated after clipping of outliers.
#	6. A photometric solution is computed in two passes (and outliers are clipped at each iteration).
#	7. Updated astrometric and photometric calibration data are written to external headers.
#swarp: program that resamples and co-adds together FITS images using any arbitrary astrometric projection defined in the WCS standard. Steps are:
#	1. Input image headers are read and checked for content. If configured in fully automatic mode, SWarp will set the characteristics of the output frame based on this information.
#	2. Input images (and their weight-maps, if available) are read one-by-one. Background-maps are built, and subtracted from the images if required.
#	3. Images are resampled, projected into subsections of the output frame, and saved as FITS files. "Projected" weight-maps are created too, even if no weight-maps were given in input.
#	4. A combined output image is created using the information stored in the "Projected" weightmaps.  It consists of a composite of the resampled sub-sections. A composite output weight-map is also written in the process.

#adam-note# include the line `ns.update(locals())` in functions to place the func namespace in the global namespace for debugging
ns=globals()

''' run SExtractor on raw images '''
def sextract(SUPA,FLAT_TYPE): #intermediate #step2_sextract
    '''inputs: SUPA,FLAT_TYPE
    returns:
    purpose: run SExtractor on raw images
    calls: get_files,initialize,get_files,save_exposure,get_files,initialize,combine_cats,paste_cats,save_exposure
    called_by: analyze,fix_radec'''

    print "sextract| START the func. inputs: " , "SUPA=", SUPA ,  "FLAT_TYPE=", FLAT_TYPE
    trial = True #adam-tmp
    #if __name__ == '__main__':
    #    trial = False #adam-tmp
    dict_sextract = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_sextract['FILTER'],dict_sextract['OBJNAME'])
    search_params.update(dict_sextract)
    print "sextract| ",'search_params=',search_params

    print "sextract| ",' SUPA=' ,SUPA , ' FLAT_TYPE=' ,FLAT_TYPE , ' search_params["files"]=' ,search_params["files"]
    kws = utilities.get_header_kw(search_params['files'][0],['PPRUN'])
    print "sextract| ",'kws["PPRUN"]=',kws["PPRUN"]
    pprun = kws['PPRUN']
    search_params['files'].sort()
    children = []
    if True:
        for image in search_params['files']:
            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            BASE = re.split('O',ROOT)[0]
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            print "sextract| ",'image=',image , ' search_params["CRVAL1ASTROMETRY_"+NUM]=',search_params["CRVAL1ASTROMETRY_"+NUM]

        ''' copy over ASTROMETRY keywords to Corrected if they exist for the unCorrected frame '''
        if search_params['CORRECTED']=='True': # and string.find(str(search_params['CRVAL1ASTROMETRY_2']),'None') != -1:
            ''' adding correct WCS info '''
            dict_uncorrected = get_files(SUPA[:-1],FLAT_TYPE)
            d = {}
            akeys = filter(lambda x:string.find(x,'ASTROMETRY')!=-1,dict_uncorrected.keys())
            for key in akeys:
                d[key] = dict_uncorrected[key]
                print "sextract| ",' key=' ,key , ' d[key]=' ,d[key] , ' SUPA[:-1]=' ,SUPA[:-1]
            save_exposure(d,SUPA,FLAT_TYPE)
            os.system('mkdir -p ' + search_params['TEMPDIR'])

            dict_sextract = get_files(SUPA,FLAT_TYPE)
            search_params = initialize(dict_sextract['FILTER'],dict_sextract['OBJNAME'])
            search_params.update(dict_sextract)

            for key in akeys:
                print "sextract| ",' key=' ,key , ' search_params[key]=' ,search_params[key]


        for image in search_params['files']:
            print "sextract| ",'image=',image
            child = False
            if not trial:
                child = os.fork()
                if child:
                    children.append(child)

            params = copy(search_params)
            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            params['ROOT'] = ROOT
            params['ROOT_WEIGHT'] = ROOT.replace('I','')
            BASE = re.split('O',ROOT)[0]
            params['BASE'] = BASE
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            params['NUM'] = NUM
            print "sextract| ",' NUM=' ,NUM , ' BASE=' ,BASE , ' ROOT=' ,ROOT

            if not child:
                if (search_params['CORRECTED']!='True' or (search_params['CORRECTED']=='True' and string.find(str(search_params['CRVAL1ASTROMETRY_' + NUM]),'None') == -1)):
                    try:

                        ## get the correct gain for the configuration
                        dd=utilities.get_header_kw(image,['CONFIG'])
                        config=dd['CONFIG']
                        params['GAIN'] = config_dict['GAIN'][config]
                        print "sextract| (adam-look) config=",config," params['GAIN']=",params['GAIN']
                        print "sextract| ",'ROOT=',ROOT
                        finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params
                        res = re.split('SCIENCE',image)
                        res = re.split('/',res[0])
                        if res[-1]=='':res = res[:-1]
                        params['path'] = reduce(lambda x,y:x+'/'+y,res[:-1])
                        params['fil_directory'] = res[-1]
                        weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
                        #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
                        #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params
                        params['finalflagim'] = weightim
                        im = "/%(path)s/%(fil_directory)s/SCIENCE/%(ROOT)s.fits" % params
                        crpix = utilities.get_header_kw(im,['CRPIX1','CRPIX2'])

                        SDSS1 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params
                        SDSS2 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)sO*.head" % params
                        print "sextract| ",' glob(SDSS1)=' ,glob(SDSS1) , ' glob(SDSS2)=' ,glob(SDSS2)
                        head = None
                        if len(glob(SDSS1)) > 0:
                                head = glob(SDSS1)[0]
                        elif len(glob(SDSS2)) > 0:
                                head = glob(SDSS2)[0]
		        else:
				SDSS1 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R9/%(BASE)s.head" % params
				SDSS2 = "/%(path)s/%(fil_directory)s/SCIENCE/headers_scamp_SDSS-R9/%(BASE)sO*.head" % params
				print "sextract| ",' glob(SDSS1)=' ,glob(SDSS1) , ' glob(SDSS2)=' ,glob(SDSS2)
				if len(glob(SDSS1)) > 0:
				    head = glob(SDSS1)[0]
				elif len(glob(SDSS2)) > 0:
				    head = glob(SDSS2)[0]
			        else:
				    raise Exception("No headers_scamp_SDSS-R9 or headers_scamp_SDSS-R6 directories available")


                        if 1:
                            command = 'mkdir -p %(TEMPDIR)s' % params
                            print "sextract| ",'command=',command
                            os.system(command)
                            imfix = "%(TEMPDIR)s/%(ROOT)s.fixwcs.fits" % params
                            print "sextract| ",'imfix=',imfix

                            os.system('mkdir ' + search_params['TEMPDIR'])
                            command = "cp " + im + " " + imfix
                            print "sextract| ",'command=',command
                            print "sextract| ",'copying file', im
                            utilities.run(command)
                            print "sextract| ",'finished copying'



                        ''' now run sextractor '''
                        if 1:
                            main_file = im #'%(TEMPDIR)s/%(ROOT)s.fixwcs.fits' % params
                            doubles_raw = [{'file_pattern':main_file,'im_type':''},]
                                           #{'file_pattern':subpath+pprun+'/SCIENCE_DOMEFLAT*/'+BASE+'OC*.fits','im_type':'D'},
                                           #{'file_pattern':subpath+pprun+'/SCIENCE_SKYFLAT*/'+BASE+'OC*.fits','im_type':'S'}]
                                           #{'file_pattern':subpath+pprun+'/SCIENCE/OC_IMAGES/'+BASE+'OC*.fits','im_type':'OC'}
                                           # ]

                            print "sextract| ",'doubles_raw=',doubles_raw
                            doubles_output = []
                            for double in doubles_raw:
                                file = glob(double['file_pattern'])
                                print "sextract| ",' double["file_pattern"]=',double["file_pattern"] , ' file=',file

                                if len(file) > 0:
                                    params.update(double)
                                    params['double_cat'] = '%(TEMPDIR)s/%(ROOT)s.%(im_type)s.fixwcs.cat' % params
                                    params['file_double'] = file[0]
                                    #print "sextract| ",params
                                    #for par in ['fwhm','GAIN']:
                                    #    print "sextract| ",par, type(params[par]), params[par]
                                    #params['fwhm'] = 2.

                                    print "sextract| ",' params["fwhm"]=',params["fwhm"]
                                    params['p_sex']=progs_path['p_sex']
                                    command_sex = "nice %(p_sex)s %(TEMPDIR)s%(ROOT)s.fixwcs.fits,%(file_double)s -c %(PHOTCONF)s/phot.conf.sex \
                                    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
                                    -CATALOG_NAME %(double_cat)s \
                                    -FILTER_NAME %(DATACONF)s/default.conv\
                                    -FILTER  Y \
                                    -FLAG_TYPE MAX\
                                    -FLAG_IMAGE ''\
                                    -SEEING_FWHM %(fwhm).3f \
                                    -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
                                    -MAG_ZEROPOINT 27.0 \
                                    -GAIN %(GAIN).3f \
                                    -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT_WEIGHT)s.weight.fits\
                                    -WEIGHT_TYPE MAP_WEIGHT" % params

                                    #-CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
                                    #-CHECKIMAGE_NAME /%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(fil_directory)s/PHOTOMETRY/coadd.segmentation.fits\
                                    catname = "%(TEMPDIR)s/%(ROOT)s.cat" % params
                                    print "sextract| ",' command_sex=',command_sex

                                    ooo=utilities.run(command_sex,[catname])
                                    if ooo!=0: raise Exception("the line utilities.run(command_sex,[catname]) failed\ncommand_sex,[catname]="+command_sex+",["+catname+"]")
                                    #adam-watch# hmm, this doesn't have a -t input, does it need one?
                                    command_ldacconv = progs_path['p_ldacconv'] +' -b 1 -c R -i ' + params['double_cat']  + ' -o '  + params['double_cat'].replace('cat','rawconv')
                                    print "sextract| ",'adam-look(no -t input) command_ldacconv=',command_ldacconv
                                    ooo=utilities.run(command_ldacconv)
                                    if ooo!=0: raise Exception("the line utilities.run(command_ldacconv) failed\ncommand_ldacconv="+command_ldacconv)



                                    #command = progs_path['p_ldactoasc'] + ' -b -q -i ' + params['double_cat'].replace('cat','rawconv') + '  -t OBJECTS\
                                    #        -k ALPHA_J2000 DELTA_J2000 > ' + params['double_cat'].replace('cat','pos')
                                    #print "sextract| ",command
                                    #utilities.run(command)
                                    #print "sextract| ",'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + params['double_cat'].replace('cat','pos')
                                    #print "sextract| ",params['double_cat'].replace('cat','pos')
                                    # Xpos_ABS is difference of CRPIX and zero CRPIX
                                    doubles_output.append({'cat':params['double_cat'].replace('cat','rawconv'),'im_type':double['im_type']})



                            print "sextract| ",' doubles_output=',doubles_output
                            print "sextract| ",'***********************************'

                            outfile = params['TEMPDIR'] + params['ROOT'] + '.conv'
                            print "sextract| ",' len(file),=',len(file)

                            combine_cats(doubles_output,outfile,search_params)

                            #outfile_field = params['TEMPDIR'] + params['ROOT'] + '.field'
                            #command = 'ldacdeltab -i ' + outfile + ' -t FIELDS -o ' + outfile_field
                            #utilities.run(command)

                            command_ldactoasc = progs_path['p_ldactoasc'] + ' -b -q -i ' + outfile + '  -t OBJECTS\
                                            -k ALPHA_J2000 DELTA_J2000 > ' + outfile.replace('conv','pos')
                            print "sextract| ",' command_ldactoasc=',command_ldactoasc
                            ooo=utilities.run(command_ldactoasc)
                            if ooo!=0: raise Exception("the line utilities.run(command_ldactoasc) failed\ncommand_ldactoasc="+command_ldactoasc)
                            #command = 'mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour green ' + outfile.replace('conv','pos')
                            #print "sextract| ",command
                            #utilities.run(command)
                            #print "sextract| ",outfile
                            #print "sextract| ",[search_params[key] for key in ['CRPIX1ZERO', 'CRPIX1', 'CRPIX2ZERO', 'CRPIX2'] ]
                            #print "sextract| ",'ldaccalc -i ' , outfile , ' -o ' , params['TEMPDIR'] , params['ROOT'] , '.newpos -t OBJECTS -c "(Xpos + ' ,  str(search_params['CRPIX1ZERO']) - crpix['CRPIX1']) + ');" -k FLOAT -n Xpos_ABS "" -c "(Ypos + ' + search_params['CRPIX2ZERO'] , crpix['CRPIX2'] , ');" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' , str(params['NUM']) , ');" -k FLOAT -n CHIP "" '
                            print "sextract| ",' search_params["CRPIX1ZERO"]=',search_params["CRPIX1ZERO"] , ' crpix["CRPIX1"]=',crpix["CRPIX1"] , ' search_params["CRPIX2ZERO"]=',search_params["CRPIX2ZERO"] , ' crpix["CRPIX2"]=',crpix["CRPIX2"]


                            command_ldaccalc = progs_path['p_ldaccalc']+' -i ' + outfile + ' -o ' + params['TEMPDIR'] + params['ROOT'] + '.newpos -t OBJECTS -c "(Xpos + ' +  str(float(search_params['CRPIX1ZERO']) - float(crpix['CRPIX1'])) + ');" -k FLOAT -n Xpos_ABS "" -c "(Ypos + ' + str(float(search_params['CRPIX2ZERO']) - float(crpix['CRPIX2'])) + ');" -k FLOAT -n Ypos_ABS "" -c "(Ypos*0 + ' + str(params['NUM']) + ');" -k FLOAT -n CHIP "" '
                            print "sextract| ",' command_ldaccalc=',command_ldaccalc
                            ooo=utilities.run(command_ldaccalc)
                            if ooo!=0: raise Exception("the line utilities.run(command_ldaccalc) failed\ncommand_ldaccalc="+command_ldaccalc)
                    except:
                        print "sextract| ",' traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)
                        if not trial:
                            os._exit(0)
                        if trial:
                            raise
                if not trial:
                    os._exit(0)
        print "sextract| ",' children=',children
        for child in children:
            print "sextract| ",'waiting for', child
            os.waitpid(child,0)

        print "sextract| ",'finished waiting'

    print "sextract| ",' data_path,=',data_path, ' SUPA=',SUPA , ' search_params["FILTER"]=',search_params["FILTER"] , ' search_params["ROTATION"]=',search_params["ROTATION"]

    pasted_cat = data_path + 'PHOTOMETRY/ILLUMINATION/' + 'pasted_' + SUPA + '_' + search_params['FILTER'] + '_' + str(search_params['ROTATION']) + '.cat'
    print "sextract| ",' pasted_cat=',pasted_cat
    os.system('mkdir -p ' + data_path + 'PHOTOMETRY/ILLUMINATION/')

    outcat = search_params['TEMPDIR'] + 'tmppaste_' + SUPA + '.cat'
    newposlist = glob(search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos')
    print "sextract| ",'search_params["TEMPDIR"]+SUPA.replace("I","*I")+"*newpos"=',search_params["TEMPDIR"]+SUPA.replace("I","*I")+"*newpos"
    if len(newposlist) > 1:
        #command = 'ldacpaste -i ' + search_params['TEMPDIR'] + SUPA + '*newpos -o ' + pasted_cat
        #print "sextract| ",command
        files = glob(search_params['TEMPDIR'] + SUPA.replace('I','*I') + '*newpos')
        print "sextract| ",' files=',files , ' search_params["TEMPDIR"]+SUPA.replace("I","*I")+"*newpos"=',search_params["TEMPDIR"]+SUPA.replace("I","*I")+"*newpos"
        paste_cats(files,pasted_cat)
    else:
        command = 'cp ' + newposlist[0] + ' ' + pasted_cat
        utilities.run(command)
    save_exposure({'pasted_cat':pasted_cat},SUPA,FLAT_TYPE)

    command = "rm -rf " + search_params['TEMPDIR'] +"/*"
    os.system(command)

    print "sextract| DONE with func"
    #return exposures, LENGTH1, LENGTH2

def length_swarp(SUPA,FLAT_TYPE,CHIPS): #intermediate #step2_sextract
    '''inputs: SUPA,FLAT_TYPE,CHIPS
    returns:  all_chip_dict
    purpose: from individual chip-level swarp parameters calculate some of the SUPA-level swarp parameters
    calls: get_files,initialize,save_exposure
    called_by: fix_radec'''
    print "length_swarp| START the func. inputs:", ' SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE , ' CHIPS=',CHIPS
    dict_length_swarp = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_length_swarp['FILTER'],dict_length_swarp['OBJNAME'])
    search_params.update(dict_length_swarp)

    all_chip_dict = {}
    NUMScommas = reduce(lambda x,y: str(x) + ',' + str(y),CHIPS.keys())
    all_chip_dict['CHIPS'] = NUMScommas

    print 'length_swarp| sorted(CHIPS.keys())=',sorted(CHIPS.keys())
    NUMS = []
    start = 1
    crpix1s = []
    crpix2s = []
    for CHIP in CHIPS.keys():
        NUMS.append(CHIP)


        if len(CHIPS[CHIP]) == 0:
            print 'length_swarp| CHIP=',CHIP
        if len(CHIPS[CHIP]) > 0:

            crpix = CHIPS[CHIP]
            p = re.compile('\_\d+O')
            file = p.sub('_' + str(CHIP) + 'O',search_params['file'])
            print 'length_swarp| file=',file , ' CHIP=',CHIP

            naxis = utilities.get_header_kw(file,['NAXIS1','NAXIS2'])
            print 'length_swarp| naxis,=',naxis,' CHIP=', CHIP

            for kw in ['NAXIS1','NAXIS2']:
                crpix[kw] = float(naxis[kw])
                print 'length_swarp| naxis[kw]=',naxis[kw]
            print 'length_swarp| file=',file

            if start == 1:
                crpixzero = copy(crpix)
                crpixhigh = copy(crpix)
                start = 0
            print 'length_swarp| float(crpix["CRPIX1"])<float(crpixzero["CRPIX1"])=',float(crpix["CRPIX1"])<float(crpixzero["CRPIX1"]) , ' float(crpix["CRPIX2"])<float(crpixzero["CRPIX2"])=',float(crpix["CRPIX2"])<float(crpixzero["CRPIX2"])
            if float(crpix['CRPIX1']) + 0   >= float(crpixzero['CRPIX1']):
                crpixzero['CRPIX1'] = copy(crpix['CRPIX1'])
            if float(crpix['CRPIX2'])  + 0 >= float(crpixzero['CRPIX2']):
                crpixzero['CRPIX2'] = copy(crpix['CRPIX2'])

            if float(crpix['CRPIX1']) - 0  <= float(crpixhigh['CRPIX1']):
                crpixhigh['CRPIX1'] = copy(crpix['CRPIX1'])
            if float(crpix['CRPIX2']) - 0  <= float(crpixhigh['CRPIX2']):
                crpixhigh['CRPIX2'] = copy(crpix['CRPIX2'])

            crpix1s.append(copy(crpix['CRPIX1']))
            crpix2s.append(copy(crpix['CRPIX2']))

            print 'length_swarp| crpix["CRPIX1"]=',crpix["CRPIX1"] , ' crpix["CRPIX2"]=',crpix["CRPIX2"] , ' crpixzero["CRPIX1"]=',crpixzero["CRPIX1"] , ' crpixzero["CRPIX2"]=',crpixzero["CRPIX2"] , ' crpixhigh["CRPIX1"]=',crpixhigh["CRPIX1"] , ' crpixhigh["CRPIX2"]=',crpixhigh["CRPIX2"]
            print 'length_swarp| crpix.keys()=',crpix.keys()
            for kw in ['CRPIX1','CRPIX2','NAXIS1','NAXIS2','CRVAL1','CRVAL2','CD1_1','CD1_2','CD2_1','CD2_2']:
                all_chip_dict[kw+ '_' + str(CHIP)] = crpix[kw]

    #plot_chips(crpix1s,crpix2s)
    for i in xrange(len(crpix1s)):
        print 'length_swarp| crpix1s[i]=',crpix1s[i] , ' crpix2s[i]=',crpix2s[i] , ' NUMS[i]=',NUMS[i]
    crpix1s.sort()
    crpix2s.sort()

    print 'length_swarp| len(crpix1s)=',len(crpix1s) , ' crpix1s=',crpix1s , ' crpix2s=',crpix2s , ' crpix1s[-1]-crpix1s[0]+crpix["NAXIS1"]=',crpix1s[-1]-crpix1s[0]+crpix["NAXIS1"] , ' crpix2s[-1]-crpix2s[0]+crpix["NAXIS2"]=',crpix2s[-1]-crpix2s[0]+crpix["NAXIS2"]
    print 'length_swarp| all_chip_dict=',all_chip_dict

    LENGTH1 =  abs(float(crpixhigh['CRPIX1']) - float(crpixzero['CRPIX1'])) + float(crpix['NAXIS1'])
    LENGTH2 =  abs(float(crpixhigh['CRPIX2']) - float(crpixzero['CRPIX2'])) + float(crpix['NAXIS2'])

    print 'length_swarp| LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2 , ' crpixzero["CRPIX1"]=',crpixzero["CRPIX1"] , ' crpixzero["CRPIX2"]=',crpixzero["CRPIX2"] , ' crpixhigh["CRPIX1"]=',crpixhigh["CRPIX1"] , ' crpixhigh["CRPIX2"]=',crpixhigh["CRPIX2"]
    all_chip_dict.update({'crfixednew':'third','LENGTH1':LENGTH1,'LENGTH2':LENGTH2,'CRPIX1ZERO':crpixzero['CRPIX1'],'CRPIX2ZERO':crpixzero['CRPIX2'],'CRVAL1':crpix['CRVAL1'],'CRVAL2':crpix['CRVAL2']})
    save_exposure(all_chip_dict,SUPA,FLAT_TYPE)
    print "length_swarp| DONE with func"
    return all_chip_dict

def analyze(SUPA,FLAT_TYPE,params={}):
    '''inputs: SUPA,FLAT_TYPE,params={}
    returns:
    calls: find_seeing,sextract
    called_by: match_OBJNAME'''

    print 'analyze| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE , ' params=',params
    trial = True
    ppid = str(os.getppid())

    try:
        #construct_correction(dict['OBJNAME'],dict['FILTER'],dict['PPRUN'])
        #imstats(SUPA,FLAT_TYPE)

        #if string.find(str(params['CRPIX1ZERO']),'None') != -1:
        #    length_swarp(SUPA,FLAT_TYPE)
        if string.find(str(params['fwhm']),'None') != -1 or str(params['fwhm'])=='0.3':
            print 'analyze| running find_seeing(SUPA,FLAT_TYPE)'
            find_seeing(SUPA,FLAT_TYPE)
        print 'analyze| running sextract(SUPA,FLAT_TYPE)'
        sextract(SUPA,FLAT_TYPE)
        #match_simple(SUPA,FLAT_TYPE)
        #phot(SUPA,FLAT_TYPE)
        #get_sdss_obj(SUPA,FLAT_TYPE)
        #apply_photometric_calibration(SUPA,FLAT_TYPE)
        print 'analyze| finished'
    except:
        ppid_loc = str(os.getppid())
        print 'analyze| traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)
        if ppid_loc != ppid: os._exit(0)
        if trial: raise
    #except:
    #    ppid_loc = str(os.getppid())
    #    print sys.exc_info()
    #    print 'something else failed',ppid, ppid_loc
    #    if ppid_loc != ppid: os._exit(0)
    #     os.system('rm -rf /scratch/' + ppid)
    print 'analyze| DONE with func'

def get_astrom_run_sextract(OBJNAME,PPRUNs): #main #step2_sextract
    '''inputs:OBJNAME,PPRUNs
    returns:
    purpose: runs sextractor on all of the data for this OBJNAME AND PPRUN. Intermediate func fix_radec calls sextract func, which does the bulk of the computing
    calls: connect_except,fix_radec
    called_by: '''

    try:
	    print "get_astrom_run_sextract| START the func. inputs:" , "OBJNAME=", OBJNAME ,  "PPRUNs=", PPRUNs
	    db2,c = connect_except()
	    keys=describe_db(c,[illum_db])
	    #command = "SELECT * from ' + test + 'fit_db where color1_star > 0.2 and OBJNAME!='HDFN' limit 2"
	    results=[] #adam-watch# i think i deleted something here. hopw it wasnt needed
	    for PPRUN in PPRUNs:
		print 'get_astrom_run_sextract| start: PPRUN=',PPRUN
		first = True
		while len(results) > 0 or first:
		    first = False
		    #command= "SELECT * from "+illum_db+" where (OBJNAME like 'A%' or OBJNAME like 'MACS%') and (pasted_cat is null or pasted_cat like '%None%') and CORRECTED='True' " # and PPRUN='2003-04-04_W-C-IC'"
		    #command= "SELECT * from ' + test + 'try_db where sdssstatus='fitfinished' and OBJNAME like 'MACS2129%' ORDER BY RAND()" # and PPRUN='2003-04-04_W-C-IC'"
		    #command = 'SELECT * from '+illum_db+' where SUPA="SUPA0118300" and OBJNAME like "MACS1226%"' #  order by rand()' #fwhm!=-999 and objname not like "%ki06%" order by rand()'
		    #command = 'SELECT * from '+illum_db+' where  pasted_cat is null and OBJNAME like "MACS1226%" and PPRUN="W-C-RC_2006-03-04"' #  order by rand()' #fwhm!=-999 and objname not like "%ki06%" order by rand()'

		    command = 'SELECT * from '+illum_db+' where  pasted_cat is null and OBJNAME like "'+OBJNAME+'%" and PPRUN="'+PPRUN+'"' #  order by rand()' #fwhm!=-999 and objname not like "%ki06%" order by rand()'
		    print 'get_astrom_run_sextract| command=',command
		    c.execute(command)
		    results = c.fetchall()
		    print 'get_astrom_run_sextract| len(results)=',len(results)
		    print 'get_astrom_run_sextract| results[0]=',results[0]

		    dict_astrom = {}
		    for i in xrange(len(results[0])): dict_astrom[keys[i]] = results[0][i]

		    print 'get_astrom_run_sextract| dict_astrom["SUPA"]=',dict_astrom["SUPA"] , 'dict_astrom["FLAT_TYPE"]=',dict_astrom["FLAT_TYPE"]
		    #fix_radec uses the SCAMP solution
		    fix_radec(dict_astrom['SUPA'],dict_astrom['FLAT_TYPE'])

		    c.execute(command)
		    results = c.fetchall()
		    ### used to run construct_correction here before, will have to run this in some other function later on
		print 'done: PPRUN=',PPRUN
	    print "get_astrom_run_sextract| DONE with func"
    except:
	    ns.update(locals())
	    raise
#adam-fragments_removed# get_astrom_run_sextract-end

''' search for images of a specific object in the data directory '''
def gather_exposures(OBJNAME,filters=None): #main #step1_add_database
    '''inputs: OBJNAME,filters=None
    returns:  exposures
    purpose: search for images of a specific object in the data directory and enter all exposures into the database
    calls: initialize,save_exposure
    called_by: '''

    print "gather_exposures| START the func. inputs:", ' OBJNAME=',OBJNAME , ' filters=',filters
    ''' setting Corrected to false here since I don't think there is any superflat correction '''
    Corrected =False
    if Corrected: pattern = 'I.fits'
    else: pattern = ''

    if not filters:
        filters =  ['B','W-J-B','W-J-V','W-C-RC','W-C-IC','I','W-S-Z+']
    for filter_name in filters:
        search_params = initialize(filter_name,OBJNAME)
        searchstr = "/%(path)s/%(FILTER)s/SCIENCE/*.fits" % search_params
        print "gather_exposures| ",'searching here:', searchstr
        files = glob(searchstr)

        ''' filter_name out corrected or not corrected files '''
        if Corrected:
            files = filter(lambda x:string.find(x,'I.fits')!=-1,files)
        elif not Corrected:
            files = filter(lambda x:string.find(x,'I.fits')==-1,files)
        print "gather_exposures| ",'files=',files

        files.sort()
        exposures =  {}
        db2,c = connect_except()

        for file in files:
            print "gather_exposures| ",'file=', file
            if string.find(file,'wcs') == -1 and string.find(file,'.sub.fits') == -1:
                res = re.split('_',re.split('/',file)[-1])
                exp_name = res[0]
                if not exposures.has_key(exp_name): exposures[exp_name] = {'images':[],'keywords':{}}
                exposures[exp_name]['images'].append(file) # exp_name is the root of the image name

                print "gather_exposures| ",'exposures[exp_name]["keywords"]=',exposures[exp_name]["keywords"]
                if len(exposures[exp_name]['keywords'].keys()) == 0: #not exposures[exp_name]['keywords'].has_key('ROTATION'): #if exposure does not have keywords yet, then get them
                    exposures[exp_name]['keywords']['FILTER'] = filter_name
                    exposures[exp_name]['keywords']['file'] = file
                    res2 = re.split('/',file)
                    for r in res2:
                        if string.find(r,filter_name) != -1:
                            print "gather_exposures| r=",r
                            exposures[exp_name]['keywords']['date'] = r.replace(filter_name + '_','')
                            exposures[exp_name]['keywords']['fil_directory'] = r
                            search_params['fil_directory'] = r
                    kws = utilities.get_header_kw(file,['CRVAL1','CRVAL2','ROTATION','OBJECT','GABODSID','CONFIG','EXPTIME','AIRMASS','INSTRUM','PPRUN','BADCCD']) # return KEY/NA if not SUBARU

                    ''' figure out a way to break into SKYFLAT, DOMEFLAT '''

                    ppid = str(os.getppid())
                    command_dfits = progs_path['p_dfits']+' ' + file + ' > ' + search_params['TEMPDIR'] + '/header'
                    ooo=utilities.run(command_dfits)
                    if ooo!=0: raise Exception("the line utilities.run(command_dfits) failed\ncommand_dfits="+command_dfits)
                    file = open('' + search_params['TEMPDIR'] + '/header','r').read()
                    if string.find(file,'SKYFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'SKYFLAT'
                    elif string.find(file,'DOMEFLAT') != -1: exposures[exp_name]['keywords']['FLAT_TYPE'] = 'DOMEFLAT'
                    #print "gather_exposures| ",file, exposures[exp_name]['keywords']['FLAT_TYPE']

                    file = open('' + search_params['TEMPDIR'] + '/header','r').readlines()

                    for line in file:
                        print "gather_exposures| ",'line=',line
                        if string.find(line,'Flat frame:') != -1 and string.find(line,'illum') != -1:
                            res = re.split('SET',line)
                            if len(res) > 1:
                                res = re.split('_',res[1])
                                set = res[0]
                                exposures[exp_name]['keywords']['FLAT_SET'] = set

                                res = re.split('illum',line)
                                res = re.split('\.',res[1])
                                smooth = res[0]
                                exposures[exp_name]['keywords']['SMOOTH'] = smooth
                            break

                    for kw in kws.keys():
                        exposures[exp_name]['keywords'][kw] = kws[kw]
                    if Corrected:
                        exposures[exp_name]['keywords']['SUPA'] = exp_name+'I'
                    if not Corrected:
                        exposures[exp_name]['keywords']['SUPA'] = exp_name
                    exposures[exp_name]['keywords']['OBJNAME'] = OBJNAME
                    exposures[exp_name]['keywords']['CORRECTED'] = str(Corrected)
                    print "gather_exposures| ",'exposures[exp_name]["keywords"]=',exposures[exp_name]["keywords"]
                    save_exposure(exposures[exp_name]['keywords'])

    print "gather_exposures| DONE with func"
    return exposures

def initialize(FILTER,OBJNAME): #simple #database
    '''inputs: FILTER,OBJNAME
    returns:  search_params={'path':data_path, 'OBJNAME':OBJNAME, 'FILTER':FILTER, 'PHOTCONF':PHOTCONF, 'DATACONF':os.environ['DATACONF'], 'TEMPDIR':TEMPDIR}
    purpose: returns a dictionary of paths to data/temp files/config files/ etc. corresponding to this OBJECT and FILTER
    calls:
    called_by: sextract,sextract,length_swarp,gather_exposures,find_seeing,fix_radec,fix_radec,sdss_coverage'''

    print "initialize| START the func. inputs:",' FILTER=',FILTER , ' OBJNAME=',OBJNAME
    for key in progs_path.keys():
        os.environ[key] = str(progs_path[key])
    ppid = str(os.getppid())
    PHOTCONF = os.environ['bonn'] + '/photconf/'
    if not os.path.isdir(PHOTCONF): raise Exception("The PHOTCONF directory %s isn't there" % (PHOTCONF))
    TEMPDIR = tmpdir
    if not os.path.isdir(tmpdir):os.system('mkdir ' + TEMPDIR)
    search_params = {'path':data_path, 'OBJNAME':OBJNAME, 'FILTER':FILTER, 'PHOTCONF':PHOTCONF, 'DATACONF':progs_path['dataconf'], 'TEMPDIR':TEMPDIR}
    print "initialize| DONE with func"
    return search_params

def save_exposure(dict_save,SUPA=None,FLAT_TYPE=None): #simple #database
    '''inputs: dict_save,SUPA=None,FLAT_TYPE=None
    returns:
    purpose: add (key,value) pairs in input dict_save to the illumination_db under (SUPA,FLAT_TYPE), if (SUPA,FLAT_TYPE) does not exist, then add it to the table
    calls: connect_except
    called_by: sextract,sextract,length_swarp,gather_exposures,find_seeing,fix_radec,fix_radec,fix_radec,sdss_coverage'''
    print 'save_exposure| START the func. inputs: dict_save=',dict_save , ' SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE
    if SUPA != None and FLAT_TYPE != None:
        dict_save['SUPA'] = SUPA
        dict_save['FLAT_TYPE'] = FLAT_TYPE

    db2,c = connect_except()

    #command = "CREATE TABLE IF NOT EXISTS "+illum_db+" ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    #c.execute("DROP TABLE IF EXISTS "+illum_db+"")
    #c.execute(command)

    floatvars = {}
    stringvars = {}
    #copy array but exclude lists
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-' + ','
    for ele in dict_save.keys():
        type = 'float'
        for l in letters:
            if string.find(str(dict_save[ele]),l) != -1:
                type = 'string'
        if type == 'float':
            floatvars[ele] = str(float(dict_save[ele]))
        elif type == 'string':
            stringvars[ele] = dict_save[ele]

    # make database if it doesn't exist
    print 'save_exposure| ','floatvars=', floatvars
    print 'save_exposure| ','stringvars=', stringvars

    for column in stringvars:
        try:
            command = 'ALTER TABLE '+illum_db+' ADD ' + column + ' varchar(240)'
            c.execute(command)
        except: nope = 1

    for column in floatvars:
        try:
            command = 'ALTER TABLE '+illum_db+' ADD ' + column + ' float(30)'
            c.execute(command)
        except: nope = 1

    # insert new observation

    SUPA = dict_save['SUPA']
    flat = dict_save['FLAT_TYPE']
    c.execute("SELECT SUPA from "+illum_db+" where SUPA = '" + SUPA + "' and flat_type = '" + flat + "'")
    results = c.fetchall()
    print 'save_exposure| results=',results
    if len(results) > 0:
        print 'save_exposure| ','already added'
    else:
        command = "INSERT INTO "+illum_db+" (SUPA,FLAT_TYPE) VALUES ('" + dict_save['SUPA'] + "','" + dict_save['FLAT_TYPE'] + "')"
        print 'save_exposure| command=',command
        c.execute(command)

    vals = ''
    for key in stringvars.keys():
        print 'save_exposure| key=',key , ' stringvars[key]=',stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"

    for key in floatvars.keys():
        print 'save_exposure| key=',key , ' floatvars[key]=',floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    command = "UPDATE "+illum_db+" set " + vals + " WHERE SUPA='" + dict_save['SUPA'] + "' AND FLAT_TYPE='" + dict_save['FLAT_TYPE'] + "'"
    print 'save_exposure| command=',command
    c.execute(command)

    print 'save_exposure| vals=',vals

    #names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
    #values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])
    #names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
    #values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])

    #command = "INSERT INTO "+illum_db+" (" + names + ") VALUES (" + values + ")"
    #os.system(command)

    db2.close()
    print "save_exposure| DONE with func"

def connect_except(): #simple #database
    '''inputs:
    returns:  db2,c
    purpose: connect to the SQL database
    calls:
    called_by: get_astrom_run_sextract,save_exposure,get_files,save_fit,get_fits'''

    #print 'connect_except| START the func'
    notConnect = True
    tried = 0
    while notConnect:
        tried += 1
        try:
            db2 = MySQLdb.connect(db=mysqldb_params["db"], user=mysqldb_params["user"], passwd=mysqldb_params["passwd"], host=mysqldb_params["host"])
            c = db2.cursor()
            notConnect = False
        except:
            print 'connect_except| traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)
            randwait = int(random.random()*30)
            if randwait < 10: randwait=10
            print 'connect_except| rand wait!', randwait
            time.sleep(randwait)
            if tried > 15:
                print 'connect_except| too many failures'
                os._exit(0)
    #print "connect_except| DONE with func"
    return db2,c

''' find full set of files corresponding to all '''
def get_files(SUPA,FLAT_TYPE=None): #simple #database
    '''inputs: SUPA,FLAT_TYPE=None
    returns:  dict_files
    purpose: find the full set of files for all keys in illumination_db corresponding to this SUPA###
    calls: connect_except
    called_by: sextract,sextract,sextract,length_swarp,find_seeing,fix_radec,fix_radec,match_OBJNAME,match_OBJNAME,sdss_coverage,sdss_coverage,linear_fit'''

    #print 'get_files| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE
    db2,c = connect_except()
    keys=describe_db(c,[illum_db])

    command = "SELECT * from "+illum_db+" where SUPA='" + SUPA + "'" # AND FLAT_TYPE='" + FLAT_TYPE + "'"
    c.execute(command)
    results = c.fetchall()
    dict_files = {}
    for i in xrange(len(results[0])): dict_files[keys[i]] = results[0][i]
    file_pat = dict_files['file']
    #print 'get_files| searching for files for all chips in the exposure', file_pat

    res = re.split('_\d+O',file_pat)
    pattern = res[0] + '_*O' + res[1]
    files = glob(pattern)
    dict_files['files'] = files

    if not files:
        print 'get_files| no image files found', file_pat
        raise Exception("get_files: no image files found!")

    db2.close()
    #print "get_files| DONE with func"
    return dict_files

def combine_cats(cats,outfile,search_params):
    '''inputs: cats,outfile,search_params
    returns:
    calls:
    called_by: sextract'''
    #cats = [{'im_type': 'DOMEFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.DOMEFLAT.fixwcs.rawconv'}, {'im_type': 'SKYFLAT', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.SKYFLAT.fixwcs.rawconv'}, {'im_type': 'OCIMAGE', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.OCIMAGE.fixwcs.rawconv'}]
    #outfile = '' + search_params['TEMPDIR'] + 'stub'
    #cats = [{'im_type': 'MAIN', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS..fixwcs.rawconv'}, {'im_type': 'D', 'cat': '' + search_params['TEMPDIR'] + '/SUPA0005188_3OCFS.D.fixwcs.rawconv'}]
    try:
	    print 'combine_cats| START the func. inputs: cats=',cats , ' outfile=',outfile , ' search_params=',search_params
	    ppid = str(os.getppid())
	    tables = {}
	    colset = 0
	    cols = []
	    for catalog in cats:
		file = catalog['cat']
		os.system('mkdir ' + search_params['TEMPDIR'] )
		aper = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
		command_ldactoasc = progs_path['p_ldactoasc'] + ' -i ' + catalog['cat'] + ' -b -s -k MAG_APER MAGERR_APER MAG_APER MAGERR_APER -t OBJECTS > ' + aper
		print 'combine_cats| command_ldactoasc=',command_ldactoasc
		ooo=os.system(command_ldactoasc)
		if ooo!=0: raise Exception("the line os.system(command_ldactoasc) failed\ncommand_ldactoasc="+command_ldactoasc)
		cat1 = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
		command_asctoldac = progs_path['p_asctoldac']+' -i ' + aper + ' -o ' + cat1 + ' -t OBJECTS -c ' + os.environ['bonn'] + '/photconf/MAG_APER.conf'
		print 'combine_cats| command_asctoldac=',command_asctoldac
		ooo=os.system(command_asctoldac)
		if ooo!=0: raise Exception("the line os.system(command_asctoldac) failed\ncommand_asctoldac="+command_asctoldac)
		allconv = tempfile.NamedTemporaryFile(dir=search_params['TEMPDIR']).name
		#adam-watch# hmm, this doesn't have a -t input, does it need one?
		command_ldacjoinkey = progs_path['p_ldacjoinkey']+' -i ' + catalog['cat'] + ' -p ' + cat1 + ' -o ' + allconv + '  -k MAG_APER1 MAG_APER2 MAGERR_APER1 MAGERR_APER2'
		print 'combine_cats| adam-look (no -t input) command_ldacjoinkey=',command_ldacjoinkey
		ooo=os.system(command_ldacjoinkey)
		if ooo!=0: raise Exception("the line os.system(command_ldacjoinkey) failed\ncommand_ldacjoinkey="+command_ldacjoinkey)

		tables[catalog['im_type']] = pyfits.open(allconv)
		#if filter == filters[0]:
		#    tables['notag'] = pyfits.open('' + search_params['TEMPDIR'] + 'all.conv' )

	    for catalog in cats:
		for i in xrange(len(tables[catalog['im_type']][1].columns)):
		    print 'combine_cats| catalog["im_type"]=',catalog["im_type"] , ' catalog["cat"]=',catalog["cat"]
		    if catalog['im_type'] != '':
			tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name + catalog['im_type']
		    else:
			tables[catalog['im_type']][1].columns[i].name = tables[catalog['im_type']][1].columns[i].name
		    cols.append(tables[catalog['im_type']][1].columns[i])

	    print 'combine_cats| cols=',cols
	    print 'combine_cats| len(cols)=',len(cols)
	    hdu = pyfits.PrimaryHDU()
	    hduIMHEAD = pyfits.BinTableHDU.from_columns(tables[catalog['im_type']][2].columns)
	    hduOBJECTS = pyfits.BinTableHDU.from_columns(cols)
	    hdulist = pyfits.HDUList([hdu])
	    hdulist.append(hduIMHEAD)
	    hdulist.append(hduOBJECTS)
            hdulist[1].header.update(EXTNAME='FIELDS')
            hdulist[2].header.update(EXTNAME='OBJECTS')
	    print 'combine_cats| file=',file
	    res = re.split('/',outfile)
	    ooo=os.system('mkdir -p ' + reduce(lambda x,y: x + '/' + y,res[:-1]))
	    if ooo!=0: raise Exception("the line os.system('mkdir -p ' + reduce(lambda x,y: x + '/' + y,res[:-1])) failed\nreduce(lambda x,y: x + '/' + y,res[:-1])="+reduce(lambda x,y: x + '/' + y,res[:-1]))
	    hdulist.writeto(outfile,overwrite=True)
	    print 'combine_cats| outfile=',outfile , '$#######$'
	    print "combine_cats| DONE with func"
    except:
	    ns.update(locals())
	    raise

def paste_cats(cats,outfile,index=2): #simple #step2_sextract
    '''inputs: cats,outfile,index=1 or 2 (depending on whether you want just an OBJECTS table, or a FIELDS and OBJECTS table)
    returns:
    purpose: concatenates all of the ldac catalogs in `cats` and saves them to `outfile`
    calls:
    called_by: sextract'''
    print 'paste_cats| START the func. inputs: cats=',cats , ' outfile=',outfile , ' index=',index
    ppid = str(os.getppid())
    tables = {}
    colset = 0
    cols = []

    table = pyfits.open(cats[0])

    data = []
    nrows = 0

    good_cats = []
    ''' get rid of empty tables '''
    for catalog in cats:
        cattab = pyfits.open(catalog)
        if not str(type(cattab[index].data)) == "<type 'NoneType'>":
            good_cats.append(catalog)
    cats = good_cats

    for catalog in cats:
        cattab = pyfits.open(catalog)
        nrows += cattab[index].data.shape[0]

    hduOBJECTS = pyfits.BinTableHDU.from_columns(table[index].columns, nrows=nrows)

    rowstart = 0
    rowend = 0
    for catalog in cats:
        cattab = pyfits.open(catalog)
        rowend += cattab[index].data.shape[0]
        for i in xrange(len(cattab[index].columns)):
            hduOBJECTS.data.field(i)[rowstart:rowend]=cattab[index].data.field(i)
        rowstart = rowend

    # update SeqNr
    print 'paste_cats| rowend=',rowend , ' len(hduOBJECTS.data.field("SeqNr"))=',len(hduOBJECTS.data.field("SeqNr")) , ' len(range(1,rowend+1))=',len(range(1 ,rowend+1))
    hduOBJECTS.data.field('SeqNr')[0:rowend]=range(1,rowend+1)

    hduIMHEAD = pyfits.BinTableHDU.from_columns(table[1])

    print 'paste_cats| cols=',cols
    print 'paste_cats| len(cols)=',len(cols)
    if index == 2:
        hdu = pyfits.PrimaryHDU()
        hdulist = pyfits.HDUList([hdu])
        hdulist.append(hduIMHEAD)
        hdulist.append(hduOBJECTS)
        hdulist[1].header.update(EXTNAME='FIELDS')
        hdulist[2].header.update(EXTNAME='OBJECTS')
    elif index == 1:
        hdu = pyfits.PrimaryHDU()
        hdulist = pyfits.HDUList([hdu])
        hdulist.append(hduOBJECTS)
        hdulist[1].header.update(EXTNAME='OBJECTS')

    print 'paste_cats| file=',file

    hdulist.writeto(outfile,overwrite=True)
    print 'paste_cats| outfile=',outfile
    print 'paste_cats| done', '$#######$'
    print "paste_cats| DONE with func"

#adam-watch# I wonder if find_seeing and calc_seeing would be more accurate if it just used MYSEEING in the file header
def find_seeing(SUPA,FLAT_TYPE):
    '''inputs: SUPA,FLAT_TYPE
    returns:
    calls: get_files,initialize,calc_seeing,save_exposure
    called_by: analyze,fix_radec'''

    print 'find_seeing| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE
    dict_files = get_files(SUPA,FLAT_TYPE)
    print 'find_seeing| dict_files["file"]=',dict_files["file"]
    search_params = initialize(dict_files['FILTER'],dict_files['OBJNAME'])
    search_params.update(dict_files)
    print 'find_seeing| dict_files["files"]=',dict_files["files"]

    trial = True #adam-tmp: this implies DONT FORK!
    #if __name__ == '__main__':
    #    trial = False #adam-tmp

    ''' quick run through for seeing '''
    children = []
    for image in search_params['files'][:]:

        child = False

        if not trial:
            child = os.fork()
            if child:
                children.append(child)


        if trial or not child:
            params = copy(search_params)

            ROOT = re.split('\.',re.split('\/',image)[-1])[0]
            params['ROOT'] = ROOT
            params['ROOT_WEIGHT'] = ROOT.replace('I','')
            NUM = re.split('O',re.split('\_',ROOT)[1])[0]
            params['NUM'] = NUM
            print 'find_seeing| ROOT=',ROOT

            weightim = params['file'].replace('.fits','.weight.fits')
            #weightim = "/%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT)s.weight.fits" % params
            #flagim = "/%(path)s/%(fil_directory)s/WEIGHTS/globalflag_%(NUM)s.fits" % params
            #finalflagim = TEMPDIR + "flag_%(ROOT)s.fits" % params
            os.system('mkdir -p ' + params['TEMPDIR'])

            params['finalflagim'] = weightim
            #os.system('rm ' + finalflagim)
            #command_ic = "ic -p 16 '1 %2 %1 0 == ?' " + weightim + " " + flagim + " > " + finalflagim
            #utilities.run(command_ic)

            # -WEIGHT_IMAGE /%(path)s/%(fil_directory)s/WEIGHTS/%(ROOT_WEIGHT)s.weight.fits\
            # -WEIGHT_TYPE MAP_WEIGHT\

            params['p_sex']=progs_path['p_sex']
            command_sex = "nice %(p_sex)s %(file)s -c %(PHOTCONF)s/singleastrom.conf.sex \
                        -FLAG_IMAGE ''\
                        -FLAG_TYPE MAX \
                        -CATALOG_NAME %(TEMPDIR)s/seeing_%(ROOT)s.cat \
                        -FILTER_NAME %(PHOTCONF)s/default.conv\
                        -CATALOG_TYPE 'ASCII' \
                        -DETECT_MINAREA 8 -DETECT_THRESH 8.\
                        -ANALYSIS_THRESH 8 \
                        -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.flag.sex" %  params

            print 'find_seeing| command_sex=',command_sex
            ooo=os.system(command_sex)
            if ooo!=0: raise Exception("the line os.system(command_sex) failed\ncommand_sex="+command_sex)
            if not trial:
                os._exit(0)

    for child in children:
        os.waitpid(child,0)

    command_cat = 'cat ' + search_params['TEMPDIR'] + '/seeing_' +  SUPA.replace('I','*I') + '*cat > ' + search_params['TEMPDIR'] + '/paste_seeing_' + SUPA.replace('I','*I') + '.cat'
    ooo=utilities.run(command_cat)
    if ooo!=0: raise Exception("the line utilities.run(command_cat) failed\ncommand_cat="+command_cat)

    file_seeing = search_params['TEMPDIR'] + '/paste_seeing_' + SUPA.replace('I','*I') + '.cat'
    PIXSCALE = float(search_params['PIXSCALE'])
    print 'find_seeing| running calc_seeing(file_seeing,PIXSCALE)'
    fwhm = calc_seeing(file_seeing,PIXSCALE)

    save_exposure({'fwhm':fwhm},SUPA,FLAT_TYPE)

    print 'find_seeing| file_seeing=',file_seeing , ' SUPA=',SUPA , ' PIXSCALE=',PIXSCALE , ' fwhm=',fwhm
    print 'find_seeing| DONE with func'

def calc_seeing(infile,PIXSCALE):
    '''inputs: infile,PIXSCALE
    returns:  fwhm
    calls:
    called_by: find_seeing'''

    print 'calc_seeing| START the func. inputs: infile=',infile , ' PIXSCALE=',PIXSCALE
    #set up bins
    binsize = 0.03
    nbins = int((3.0-0.3)/binsize+0.5)
    bin = scipy.zeros(nbins)

    # for each line get fwhm
    for line in open(infile,'r').readlines():
        tokens = line.split()
        fwhm_obj = float(tokens[2])
        flag = float(tokens[3])


        # make sure flag is zero and the seeing is reasonable
        if 3.0 > fwhm_obj*PIXSCALE > 0.3 and flag == 0:

            actubin = int((fwhm_obj * PIXSCALE - 0.3)/binsize)
            bin[actubin] += 1
    # find max
    max = 0
    k = 0
    nobjs = 0
    for i in range(nbins):
        nobjs += bin[i]
        if bin[i]>max:
            k=i
            max = bin[i]

    # set the fwhm
    fwhm = 0.3 + k*binsize

    # check that its ok
    if nobjs < 100:
        fwhm = -999

    print 'calc_seeing| DONE with func'
    return fwhm

def fix_radec(SUPA,FLAT_TYPE): #intermediate #step2_sextract
    '''inputs: SUPA,FLAT_TYPE
    returns:  1 (if func runs properly), -1 (if no SDSS/2MASS headers found), -2 (if SDSS/2MASS headers have no OBJECTS in them)
    purpose: Run sextractor to get stars and their (x,y) positions at the chip-level. Then get the (x,y) positions at the SUPA-level and finally fix the RA/DEC coords of OBJECTS in the SDSS/2MASS headers
    calls: get_files,initialize,length_swarp,find_seeing,sextract,get_files,initialize,save_exposure,save_exposure,save_exposure
    called_by: get_astrom_run_sextract,match_OBJNAME'''

    print 'fix_radec| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE
    ppid = str(os.getppid())

    #chips = length(SUPA,FLAT_TYPE)

    dict_radec = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_radec['FILTER'],dict_radec['OBJNAME'])
    search_params.update(dict_radec)

    chips = {}
    NUMS = []
    at_least_one = False

    print 'fix_radec| files:', dict_radec['files']

    for image in dict_radec['files']:
        params = copy(search_params)
        ROOT = re.split('\.',re.split('\/',image)[-1])[0]
        params['ROOT'] = ROOT
        BASE = re.split('O',ROOT)[0]
        params['BASE'] = BASE
        NUM = re.split('O',re.split('\_',ROOT)[1])[0]
        params['NUM'] = NUM
        print 'fix_radec| NUM=',NUM , 'BASE=',BASE , 'ROOT=',ROOT , 'image=',image

        ## get the correct gain for the configuration
        dd=utilities.get_header_kw(image,['CONFIG'])
        config=dd['CONFIG']
        params['GAIN'] = config_dict['GAIN'][config]
        print "fix_radec| (adam-look) config=",config," params['GAIN']=",params['GAIN']

        finalflagim = "%(TEMPDIR)sflag_%(ROOT)s.fits" % params
        res = re.split('SCIENCE',image)
        print 'fix_radec| res=',res
        res = re.split('/',res[0])
        if res[-1]=='':res = res[:-1]
        print 'fix_radec| res=',res
        params['path'] = reduce(lambda x,y:x+'/'+y,res[:-1])
        params['fil_directory'] = res[-1]
        print 'fix_radec| params["fil_directory"]=',params["fil_directory"]
        res = re.split('_',res[-1])

        ''' if three second exposure, use the headers in the directory '''
        print 'fix_radec| dict_radec["fil_directory"]=',dict_radec["fil_directory"]
        if string.find(params['fil_directory'],'CALIB') != -1:
            params['directory'] = params['fil_directory']
        else:
            params['directory'] = res[0]


        print 'fix_radec| params["directory"]=',params["directory"]
        print 'fix_radec| BASE=',BASE
        SDSS_R6 = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_SDSS-R6/%(BASE)s.head" % params   # it's not a ZERO!!!
        SDSS_R9 = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_SDSS-R9/%(BASE)s.head" % params   # it's not a ZERO!!!
        TWOMASS = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_2MASS/%(BASE)s.head" % params
        NOMAD = "/%(path)s/%(directory)s/SCIENCE/headers_scamp_NOMAD*/%(BASE)s.head" % params

        SDSS_R6 = SDSS_R6.replace('I_','_').replace('I.','.')
        SDSS_R9 = SDSS_R9.replace('I_','_').replace('I.','.')

        print 'fix_radec| looking for SCAMP header'

        print 'fix_radec| SDSS_R6=',SDSS_R6, 'TWOMASS=',TWOMASS, 'NOMAD=',NOMAD
        print 'fix_radec| SDSS_R9=',SDSS_R9
        print 'fix_radec| glob(SDSS_R6)=',glob(SDSS_R6) , ' glob(TWOMASS)=',glob(TWOMASS) , ' glob(NOMAD)=',glob(NOMAD)
        print 'fix_radec| glob(SDSS_R9)=',glob(SDSS_R9)
        head = None
        heads = []
        if len(glob(TWOMASS)) > 0:
            heads.append(glob(TWOMASS)[0])
        if len(glob(TWOMASS.replace('.head','O*.head'))) > 0:
            heads.append(glob(TWOMASS.replace('.head','O*.head'))[0])
        if len(glob(NOMAD)) > 0:
            heads.append(glob(NOMAD)[0])
        if len(glob(NOMAD.replace('.head','O*.head'))) > 0:
            heads.append(glob(NOMAD.replace('.head','O*.head'))[0])

        print 'fix_radec| heads=',heads


        ''' pick out latest SCAMP solution not SDSS_R6 '''
        if len(heads) > 0:
            a = [[os.stat(f).st_mtime,f] for f in heads ]
            a.sort()
            print 'fix_radec| a=',a
            head = a[-1][1]
            print 'fix_radec| head=',head

        ''' if SDSS_R9 exists, use that '''
        if len(glob(SDSS_R9)) > 0:
            head = glob(SDSS_R9)[0]
        if len(glob(SDSS_R9.replace('.head','O*.head'))) > 0:
            head = glob(SDSS_R9.replace('.head','O*.head'))[0]

        ''' if SDSS_R6 exists, use that '''
        if len(glob(SDSS_R6)) > 0:
            head = glob(SDSS_R6)[0]
        if len(glob(SDSS_R6.replace('.head','O*.head'))) > 0:
            head = glob(SDSS_R6.replace('.head','O*.head'))[0]

        print 'fix_radec| head=',head , ' SDSS_R9=',SDSS_R9 , ' glob(SDSS_R9)=',glob(SDSS_R9), ' SDSS_R6=',SDSS_R6 , ' glob(SDSS_R6)=',glob(SDSS_R6)

        w = {}

        if head is not None:
            keys = []
            hf = open(head,'r').readlines()
            print 'fix_radec| head=',head
            for line in hf:
                at_least_one = True
                if string.find(line,'=') != -1:
                    res = re.split('=',line)
                    name = res[0].replace(' ','')
                    res = re.split('/',res[1])
                    value = res[0].replace(' ','')
                    print 'fix_radec| name=',name , ' value=',value
                    if string.find(name,'CD')!=-1 or string.find(name,'PV')!=-1 or string.find(name,'CR')!=-1 or string.find(name,'NAXIS') != -1:
                        w[name] = float(value)
                        print 'fix_radec| line=',line , ' w[name]=',w[name]
                        keys.append(name)
        chips[NUM] = copy(w)
        print 'fix_radec| w=',w
        NUMS.append(NUM)

    if at_least_one:

        chip_dict = length_swarp(SUPA,FLAT_TYPE,chips)
        vecs = {}
        for key in keys:
            vecs[key] = []
        vecs['good_scamp'] = []

        ''' if it can't find the catalog it needs, it runs SExtractor to make catalog '''
        print 'fix_radec| trying to open SExtractor catalog for: ', dict_radec['file']
        try:
            hdu= pyfits.open(search_params['pasted_cat'])
            print 'fix_radec| search_params["pasted_cat"]=',search_params["pasted_cat"]
            table = hdu['OBJECTS'].data
            print 'fix_radec| SExtractor catalog found'
        except:
            print 'fix_radec| SExtractor catalog not found. So go ahead and run sextractor'
            if string.find(str(params['fwhm']),'None') != -1 or str(params['fwhm'])=='0.3':
                find_seeing(search_params['SUPA'],search_params['FLAT_TYPE'])

            sextract(search_params['SUPA'],search_params['FLAT_TYPE'])
            dict_radec = get_files(SUPA,FLAT_TYPE)
            search_params = initialize(dict_radec['FILTER'],dict_radec['OBJNAME'])
            search_params.update(dict_radec)

            ''' problem is here !!! '''
            print 'fix_radec| search_params["pasted_cat"]=',search_params["pasted_cat"]
            hdu= pyfits.open(search_params['pasted_cat'])
            table = hdu['OBJECTS'].data

        print 'fix_radec| type(table)=',type(table)
        if str(type(table)) == "<type 'NoneType'>":
            save_exposure({'fixradecCR':-2},SUPA,FLAT_TYPE)
            print "fix_radec| DONE with func (return -2)"
            return -2
        else:
            CHIP = table.field('CHIP')
            print 'fix_radec| keys=',keys
            print 'fix_radec| chips.keys()=',chips.keys()
            #for k in chips.keys():
            #    print chips[k].has_key('CRVAL1'), k
            for i in xrange(len(CHIP)):
                NUM = str(int(CHIP[i]))
                good = False
                for key in keys:
                    if chips[NUM].has_key(key):
                        good = True
                        vecs[key].append(float(chips[NUM][key]))
                    else:
                        vecs[key].append(-1.)
                if good:
                    vecs['good_scamp'].append(1)
                else:
                    vecs['good_scamp'].append(0)

            print 'fix_radec| vecs["good_scamp"]=',vecs["good_scamp"]
            print 'fix_radec| vecs.keys()=',vecs.keys()
            for key in vecs.keys():
                vecs[key] = scipy.array(vecs[key])
                print 'fix_radec| vecs[key][0:20]=',vecs[key][0:20] , ' key=',key

            ra_cat = table.field('ALPHA_J2000')
            dec_cat = table.field('DELTA_J2000')

            x0 = (table.field('Xpos') - vecs['CRPIX1'])
            y0 = (table.field('Ypos') - vecs['CRPIX2'])

            x0_ABS = (table.field('Xpos') + chip_dict['CRPIX1ZERO'] - vecs['CRPIX1'])
            y0_ABS = (table.field('Ypos') + chip_dict['CRPIX2ZERO'] - vecs['CRPIX2'])

            x = x0*vecs['CD1_1'] + y0*vecs['CD1_2']
            y = x0*vecs['CD2_1'] + y0*vecs['CD2_2']

            r = (x**2. + y**2.)**0.5

            xi_terms = {'PV1_0':scipy.ones(len(x)),'PV1_1':x,'PV1_2':y,'PV1_3':r,'PV1_4':x**2.,'PV1_5':x*y,'PV1_6':y**2.,'PV1_7':x**3.,'PV1_8':x**2.*y,'PV1_9':x*y**2.,'PV1_10':y**3.}

            pv1_keys = filter(lambda x: string.find(x,'PV1') != -1, vecs.keys())
            print 'fix_radec| pv1_keys=', pv1_keys
            xi = reduce(lambda x,y: x + y, [xi_terms[k]*vecs[k] for k in pv1_keys])

            eta_terms = {'PV2_0':scipy.ones(len(x)),'PV2_1':y,'PV2_2':x,'PV2_3':r,'PV2_4':y**2.,'PV2_5':y*x,'PV2_6':x**2.,'PV2_7':y**3.,'PV2_8':y**2.*x,'PV2_9':y*x**2.,'PV2_10':x**3.}

            pv2_keys = filter(lambda x: string.find(x,'PV2') != -1, vecs.keys())
            print 'fix_radec| pv2_keys=', pv2_keys
            eta = reduce(lambda x,y: x + y, [eta_terms[k]*vecs[k] for k in pv2_keys])

            print 'fix_radec| xi[0:10]=',xi[0:10] , ' eta[0:10]=',eta[0:10] , ' len(eta)=',len(eta)
            print 'fix_radec| vecs.keys()=',vecs.keys() , ' vecs["CD1_1"][0]=',vecs["CD1_1"][0] , ' vecs["CD1_2"][0]=',vecs["CD1_2"][0] , ' vecs["CD2_2"][0]=',vecs["CD2_2"][0] , ' vecs["CD2_1"][0]=',vecs["CD2_1"][0]

            ra_out = []
            dec_out = []
            cat = open(tmpdir + '/' + BASE + 'cat','w')
            for i in xrange(len(xi)):
                XI = xi[i] / 180.0   * math.pi
                ETA = eta[i] / 180.0 * math.pi
                CRVAL1 = vecs['CRVAL1'][i]/180.0* math.pi
                CRVAL2 = vecs['CRVAL2'][i]/180.0 * math.pi
                p = math.sqrt(XI**2. + ETA**2.)
                c = math.atan(p)

                a = CRVAL1 + math.atan((XI*math.sin(c))/(p*math.cos(CRVAL2)*math.cos(c) - ETA*math.sin(CRVAL2)*math.sin(c)))
                d = math.asin(math.cos(c)*math.sin(CRVAL2) + ETA*math.sin(c)*math.cos(CRVAL2)/p)

                ra = a*180.0/math.pi
                dec = d*180.0/math.pi
                if i % 100== 0:
                    print 'fix_radec| ra_cat','dec_cat',ra,ra_cat[i], dec, dec_cat[i]
                    print 'fix_radec| (ra-ra_cat[i])*3600.=',(ra-ra_cat[i])*3600. , ' (dec-dec_cat[i])*3600.=',(dec-dec_cat[i])*3600.
                ''' if no solution, give a -999 value '''
                if vecs['good_scamp'][i] != 1:
                    ra = -999  - 200*random.random()
                    dec = -999  - 200*random.random()
                ra_out.append(ra)
                dec_out.append(dec)
                cat.write(str(ra) + ' ' + str(dec) + '\n')
                #cat.write(str(ra[i]) + ' ' + str(dec[i]) + '\n')
            cat.close()
            #index = int(random.random()*4)
            #colour = ['red','blue','green','yellow'][index]
            #rad = [1,2,3,4][index]
            #os.system(' mkreg.pl -xcol 0 -ycol 1 -c -rad ' + str(rad) + ' -wcs -colour ' + colour + ' ' + BASE + 'cat')

            hdu[2].data.field('Xpos_ABS')[:] = scipy.array(x0_ABS)
            hdu[2].data.field('Ypos_ABS')[:] = scipy.array(y0_ABS)
            hdu[2].data.field('ALPHA_J2000')[:] = scipy.array(ra_out)
            hdu[2].data.field('DELTA_J2000')[:] = scipy.array(dec_out)
            table = hdu[2].data

            print 'fix_radec| BREAK'
            print 'fix_radec| ra_out[0:10]=',ra_out[0:10] , ' table.field("ALPHA_J2000")[0:10]=',table.field("ALPHA_J2000")[0:10]
            print 'fix_radec| dec_out[0:10]=',dec_out[0:10] , ' table.field("DELTA_J2000")[0:10]=',table.field("DELTA_J2000")[0:10]
            print 'fix_radec| SUPA=',SUPA , ' search_params["pasted_cat"]=',search_params["pasted_cat"]

            hdu.writeto(search_params['pasted_cat'],overwrite=True)

            print "fix_radec| DONE with func (return 1)"
            save_exposure({'fixradecCR':1},SUPA,FLAT_TYPE)
            return 1

    else:
        save_exposure({'fixradecCR':-1},SUPA,FLAT_TYPE)
        print "fix_radec| DONE with func (return -1)"
        return -1

def test_1226():
    '''inputs:
    returns:
    purpose: runs match_OBJNAME on MACS1226
    calls: match_OBJNAME
    called_by: '''
    OBJNAME, FILTER, PPRUN = 'MACS1226+21', 'W-C-RC', 'W-C-RC_2006-03-04'
    match_OBJNAME( OBJNAME, FILTER, PPRUN )

def match_OBJNAME(OBJNAME=None,FILTER=None,PPRUN=None,todo=None): #main #step3_run_fit
    '''inputs: OBJNAME=None,FILTER=None,PPRUN=None,todo=None
    returns:
    calls: describe_db,describe_db,describe_db,save_fit,describe_db,describe_db,analyze,fix_radec,sdss_coverage,get_files,match_many,getTableInfo,get_files,find_config,selectGoodStars,starStats,save_fit,find_config,linear_fit,save_fit,save_fit
    called_by: test_1226'''
    print 'match_OBJNAME| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' todo=',todo
    #match_many,getTableInfo,get_files,find_config,selectGoodStars,starStats,save_fit,find_config,linear_fit
    if OBJNAME is None:
        batchmode = True
    else: batchmode = False

    ppid = str(os.getppid())
    trial = True #adam-tmp: this implies DONT FORK!
    #if __name__ == '__main__':
    #    trial = False #adam-tmp

    start = 1
    loop = False
    go = True

    while go:
        db2,c = connect_except()
        illum_db_keys = describe_db(c,[illum_db])

        if loop or OBJNAME is None: # or start == 0:
            loop=True

            try_db_keys = describe_db(c,['' + test + 'try_db'])
            illum_db_keys = describe_db(c,[illum_db])

            command = "select * from " + test + "try_db t where t.sdssstatus is null and t.Nonestatus is null and (config='8.0' or config='9.0') group by t.objname, t.pprun order by rand()"
            print 'match_OBJNAME| command=',command
            c.execute(command)
            results=c.fetchall()

            if len(results) > 0:
                for line in results:
                    dtop = {}
                    for i in xrange(len(try_db_keys)):
                        dtop[try_db_keys[i]] = str(line[i])
                    command = "select i.* from "+illum_db+" i where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.PPRUN = '" + dtop['PPRUN'] + "' and i.pasted_cat is not null  GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND() limit 1 " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
                    c.execute(command)
                    results_b=c.fetchall()
                    print 'match_OBJNAME| results_b=',results_b
                    if len(results_b) > 0:
                        for i in xrange(len(illum_db_keys)):
                            dtop[illum_db_keys[i]] = str(results_b[0][i])
                        print 'match_OBJNAME| dtop["PPRUN"]=',dtop["PPRUN"] , ' dtop["OBJNAME"]=',dtop["OBJNAME"]
                        break
                else:
                    dtop= {}

        else:
            go = False
            command=" drop temporary table if exists temp  "
            c.execute(command)
            command = "create temporary table temp as select * from "+illum_db+" group by objname, pprun "
            print 'match_OBJNAME| command=',command
            c.execute(command)

            #command="SELECT * from temp i left join " + test + "fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.SUPA not like '%I' and i.objname='"+OBJNAME+"' and i.pprun='"+PPRUN+"' and i.filter='" + FILTER + "' GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND() " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
            command="SELECT * from "+illum_db+" where  file not like '%CALIB%' and  PPRUN !='KEY_N/A'  and OBJNAME like '" + OBJNAME + "' and FILTER like '" + FILTER + "' and PPRUN='" + PPRUN + "' GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"

            start = 0
            print 'match_OBJNAME| command=',command
            c.execute(command)
            results=c.fetchall()
            print 'match_OBJNAME| len(results)=',len(results)
            print 'match_OBJNAME| results[0]=',results[0]
            ppid = str(os.getppid())

            print 'match_OBJNAME| hey'
            if len(results) == 0:
                print 'match_OBJNAME| breaking!'
                break

            if len(results) > 0:
                print 'match_OBJNAME| start next'
                line = results[0]
                dtop = {}
                for i in xrange(len(illum_db_keys)):
                    dtop[illum_db_keys[i]] = str(line[i])

        if len(results) ==0: return
        if len(results) > 0:
            FILTER = dtop['FILTER']
            PPRUN = dtop['PPRUN']
            OBJNAME = dtop['OBJNAME']

            print 'match_OBJNAME| now running save_fit',({"PPRUN":PPRUN,"OBJNAME":OBJNAME,"FILTER":FILTER,"sample":"record","sample_size":"record"},"db="+""+test+"try_db")
            save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'sample':'record','sample_size':'record'},db='' + test + 'try_db')
            illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/'
	    os.system('mkdir -p ' + illum_dir+'/other_runs_plots/')
            logfile  = open(illum_dir + 'logfile','w')
            print 'match_OBJNAME| illum_dir+"logfile"=',illum_dir+"logfile"
            print 'match_OBJNAME| dtop["FILTER"]=',dtop["FILTER"] , 'dtop["PPRUN"]=',dtop["PPRUN"] , 'dtop["OBJNAME"]=',dtop["OBJNAME"]
            #keys = ['SUPA','OBJNAME','ROTATION','PPRUN','pasted_cat','FILTER','ROTATION','files']

            try_db_keys = describe_db(c,['' + test + 'try_db'])
            #command="SELECT * from "+illum_db+" where  OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and filter like '" + dtop['FILTER'] + "' and pasted_cat is not NULL"
            command="SELECT * from " + test + "try_db f  where f.OBJNAME='" + dtop['OBJNAME'] + "' and f.PPRUN='" + dtop['PPRUN'] + "' limit 1"
            print 'match_OBJNAME| command=',command
            c.execute(command)
            results2=c.fetchall()
            #sort_results(results,try_db_keys)

            for line in results2:
                dict_temp = {}
                for i in xrange(len(try_db_keys)):
                    dict_temp[try_db_keys[i]] = str(line[i])

            primary = dict_temp['primary_filt']
            primary_catalog = dict_temp['primary_catalog']
            secondary = dict_temp['secondary_filt']
            secondary_catalog = dict_temp['secondary_catalog']
            if todo is None:
                match = dict_temp['todo']
            else: match= todo

            print 'match_OBJNAME| primary=',primary , ' secondary=',secondary

            ''' now run with PPRUN '''
            command_supa="SELECT * from "+illum_db+" i left join " + test + "fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and i.PPRUN='" + dtop['PPRUN'] + "' and badccd!=1 group by i.supa"

            print 'match_OBJNAME| command_supa=',command_supa
            c.execute(command_supa)
            results_supa=c.fetchall()
            print 'match_OBJNAME| matching len(results_supa)=', len(results_supa)

            field = []
            info = []
            if len(results_supa) > 0: #  and (len(results_try) == 0 or trial):
                ''' only redirect stdout if actually running on a pprun '''
                if not trial:
                    print "match_OBJNAME| not trial"
                    stderr_orig = sys.stderr
                    stdout_orig = sys.stdout
                    sys.stdout = logfile
                    sys.stderr = logfile
                try:

                    for line in results_supa:
                        print 'match_OBJNAME| line=', line
                        d = {}
                        for i in xrange(len(illum_db_keys)):
                            d[illum_db_keys[i]] = str(line[i])
                        #ana = '' #raw_input('analyze ' + d['SUPA'] + '?')
                        #if len(ana) > 0:
                        #    if ana[0] == 'y':
                        #        analyze(d['SUPA'],d['FLAT_TYPE'])
                        ''' use SCAMP CRVAL, etc. '''

                        a=1
                        print 'match_OBJNAME| d["CHIPS"]=',d["CHIPS"] , ' d["fixradecCR"]=',d["fixradecCR"]
                        ooo=os.system('cd ' + tmpdir)
                        if ooo!=0: raise xception("the line os.system('cd ' + tmpdir) failed\n'cd ' + tmpdir="+'cd ' + tmpdir)
                        print 'match_OBJNAME| tmpdir=',tmpdir
                        if str(d['CHIPS'])=='None' or str(d['fixradecCR']) != str(1.0): # or str(d['fixradecCR']) == '-1':
                            a = fix_radec(d['SUPA'],d['FLAT_TYPE'])

                        if a==1:
                            key = str(int(float(d['ROTATION']))) + '$' + d['SUPA'] + '$'
                            field.append({'key':key,'pasted_cat':d['pasted_cat'],'ROT':d['ROTATION'],'file':d['file']})
                            info.append([d['ROTATION'],d['SUPA'],d['OBJNAME']])
                            print 'match_OBJNAME| d["file"]=',d["file"]
                        if d['CRVAL1'] == 'None':
                            length(d['SUPA'],d['FLAT_TYPE'])
                        print 'match_OBJNAME| d["SUPA"]=',d["SUPA"]

                    #The output catalogs are named in a confusing way. Each PPRUN is supposed to have a sdssmatch*.cat.assoc1 file, but it's only run on the last SUPA, because it assumes you'll get the same things from all of the SUPAs. So this stuff doesn't need to be indented, it's not supposed to be part of the loop over the results_supa (line)
                    #adam-watch# maybe it's best to pick the image with the best image quality instead of just the last one in the list?

                    #adam-note# match == 'bootstrap': then you apply the catalog from a previous successful fit (from a different filter )
                    if match == 'bootstrap':
                        print 'match_OBJNAME| primary=', primary, ' secondary=', secondary
                        ''' match images '''
                        finalcat = match_many_multi_band([[dict_temp['primary_catalog'],'primary'],[dict_temp['secondary_catalog'],'secondary']])
                        print 'match_OBJNAME| finalcat=',finalcat
                    else:
                        ''' now check to see if there is SDSS '''
                        sdss_cov,galaxycat,starcat = sdss_coverage(d['SUPA'],d['FLAT_TYPE'])
                        ''' get SDSS matched stars, use photometric calibration to remove color term '''
                        #adam-watch# make sure the rest of this code actually uses `sdss_coverage` output and `get_cats_ready` output, rather than just appearing to use it. Remember that at first it was claiming to use SDSS info even when there weren't any SDSS catalogs
                        if sdss_cov:
                            ''' retrieve SDSS catalog '''
                            match = 'sdss'
                            sdssmatch = get_cats_ready(d['SUPA'],d['FLAT_TYPE'],galaxycat,starcat)
                            print 'match_OBJNAME| d["SUPA"]=',d["SUPA"] , ' d["FLAT_TYPE"]=',d["FLAT_TYPE"] , ' d["OBJECT"]=',d["OBJECT"] , ' d["CRVAL1"]=',d["CRVAL1"] , ' d["CRVAL2"]=',d["CRVAL2"]
                            print 'match_OBJNAME| d["pasted_cat"]=',d["pasted_cat"] , ' sdss_cov=',sdss_cov
                            print 'match_OBJNAME| calibration done'
                        else:
                            match=None

                    print 'match_OBJNAME| match=',match

                    #save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'logfile':illum_dir+'logfile','sample':'record','sample_size':'record','status':'started','time':str(time.localtime())},db='' + test + 'try_db')

                    d = get_files(d['SUPA'],d['FLAT_TYPE'])
                    print 'match_OBJNAME| field=',field
                    input = [[x['pasted_cat'],x['key'],x['ROT']] for x in field]
                    #input_files = [[x['pasted_cat']] for x in field]
                    #print 'match_OBJNAME| input_files=',input_files

                    input_filt = []
                    print 'match_OBJNAME| input=',input
                    for f in input:
                        ''' may need fainter objects for bootstrap '''
                        if match=='bootstrap':
                            Ns = ['MAGERR_AUTO < 0.1)','Flag = 0)']
                        else:
                            Ns = ['MAGERR_AUTO < 0.05)','Flag = 0)']
                        filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',Ns)
                        print 'match_OBJNAME| filt=',filt , ' f=',f
                        filtered = f[0].replace('.cat','.filt.cat')
                        print 'match_OBJNAME| filtered=',filtered
                        command_ldacfilter = progs_path['p_ldacfilter']+' -i ' + f[0] + ' -t OBJECTS -o ' + filtered + ' -c "' + filt + ';" '
                        print 'match_OBJNAME| command_ldacfilter=',command_ldacfilter
                        ooo=utilities.run(command_ldacfilter,[filtered])
                        if ooo!=0: raise Exception("the line utilities.run(command_ldacfilter,[filtered]) failed\ncommand_ldacfilter="+command_ldacfilter)
                        input_filt.append([filtered,f[1],f[2]])

                    if 0: #len(input) > 8:
                        input_short = []
                        i = 0
                        while len(input_short) < 6 and len(input_short)<len(input):
                            i += 1
                            rot0 = filter(lambda x:float(x[1][0])==0,input)[0:i]
                            rot1 = filter(lambda x:float(x[1][0])==1,input)[0:i]
                            rot2 = filter(lambda x:float(x[1][0])==2,input)[0:i]
                            rot3 = filter(lambda x:float(x[1][0])==2,input)[0:i]
                            input_short = rot0 + rot1 + rot2 + rot3
                        input = input_short
                        print 'match_OBJNAME| new input=', input
                    print 'match_OBJNAME| input=',input
                    input = input_filt
                    print 'match_OBJNAME| input_filt=',input_filt

                    if match=='sdss':
                        input.append([sdssmatch,'SDSS',None])
                    elif match=='bootstrap':
                        input.append([finalcat,'SDSS',None])

                    if len(input) < 3:
                        raise TryDb('too few images')

                    print 'match_OBJNAME| input=',input
                    print 'match_OBJNAME| now running match_many(input)'
                    match_many(input)

                    start_EXPS = getTableInfo()
                    print 'match_OBJNAME| start_EXPS=',start_EXPS

                    dt = get_files(start_EXPS[start_EXPS.keys()[0]][0])
                    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
                    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']
                    CONFIG = find_config(dt['GABODSID'])
                    print 'match_OBJNAME| CONFIG=',CONFIG , ' dt["PPRUN"]=',dt["PPRUN"] , ' dt["OBJNAME"]=',dt["OBJNAME"]

                    EXPS, star_good,supas, totalstars, mdn_background = selectGoodStars(start_EXPS,match,LENGTH1,LENGTH2,CONFIG)
                    info = starStats(supas)
                    print 'match_OBJNAME| info=',info
                    print 'match_OBJNAME| match=',match
                    print 'match_OBJNAME| mdn_background=',mdn_background , ' len(supas)=',len(supas)

                    if len(supas) < 300 and mdn_background > 26000:
                        raise TryDb('high background:'+ str(mdn_background))

                    start_ims = (reduce(lambda x,y: x + y, [len(start_EXPS[x]) for x in start_EXPS.keys()]))
                    final_ims = (reduce(lambda x,y: x + y, [len(EXPS[x]) for x in EXPS.keys()]))
                    print 'match_OBJNAME| start_ims=', start_ims
                    print 'match_OBJNAME| final_ims=', final_ims
                    if final_ims < 3:
                        raise TryDb('start:'+str(start_ims)+',end:'+str(final_ims))

                    uu = open(tmpdir + '/selectGoodStars','w')
                    pickle.dump({'info':info,'EXPS':EXPS,'star_good':star_good,'supas':supas,'totalstars':totalstars},uu)
                    uu.close()

                    ''' if there are too few matches with SDSS stars, dont use them '''
                    if match == 'sdss' and info['match'] < 100:
                        match = None

                    save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'logfile':illum_dir+'logfile','sample':'record','sample_size':'record',str(match)+'status':'started','fit_time':str(time.localtime())},db='' + test + 'try_db')
                    print 'match_OBJNAME| ',{'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'logfile':illum_dir+'logfile','sample':'record','sample_size':'record',str(match)+'status':'started','fit_time':str(time.localtime())}

                    if match == 'bootstrap' and info['match'] < 200:
                        print 'match_OBJNAME| info["match"]=',info["match"]
                        raise TryDb('too few objects/bootstrap:' + str(info['match']))

                    print 'match_OBJNAME| match=',match , ' info=',info
                    command="SELECT * from " + test + "fit_db i  where i.OBJNAME='" + dtop['OBJNAME'] + "' and (i.sample_size='all' and i.sample='" + str(match) + "' and i.positioncolumns is not null) and i.PPRUN='" + dtop['PPRUN'] + "'"
                    print 'match_OBJNAME| command=',command
                    c.execute(command)
                    results_try=c.fetchall()
                    print 'match_OBJNAME| len(results_try)=',len(results_try)
                    print 'match_OBJNAME| OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' match=',match

                    print 'match_OBJNAME| matched'
		    run_these=["all","rand1","rand2","rand3","rand4","rand5","rand6","rand7","rand8","rand9","rand10"]
                    #adam-no_more# run_these=["all"] 
                    linear_fit(OBJNAME,FILTER,PPRUN,run_these,match,CONFIG,primary=primary,secondary=secondary)
                    ''' now records the current sample used in the fit '''
                    save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'logfile':str(illum_dir)+'logfile','sample':str('record'),'sample_size':'record',str(match)+'status':'fitfinished','test_check':'yes','sample_current':str(match),'fit_time':str(time.localtime())},db='' + str(test) + 'try_db')
                    #save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'sample_size':'record','sample':'record','sample_current':str(match)},db='' + test + 'try_db')

                    ### used to run construct_correction here before, now I run this separate from any other function (could be run in run_correction later  )
                    print 'match_OBJNAME| ','DONE '*100
                    if batchmode:
                        os.system('rm -rf ' + tmpdir +"/*")
                except KeyboardInterrupt:
                    print 'match_OBJNAME| HIT EXCEPTION!'
                    raise
                except:
                    print 'match_OBJNAME| HIT EXCEPTION!'
                    ppid_loc = str(os.getppid())
                    print 'match_OBJNAME| traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)
                    ''' if a child process fails, just exit '''
                    if ppid_loc != ppid: sys.exit(0)
                    print 'match_OBJNAME| fail'
                    print 'match_OBJNAME| trial=', trial
                    save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'logfile':illum_dir+'logfile','sample':'record','sample_size':'record',str(match)+'status':'failed','fit_time':str(time.localtime()),'exception':'no information'},db='' + test + 'try_db')
                    if batchmode:
                        os.system('rm -rf ' + tmpdir +"/*")
                    if trial:
                        print 'match_OBJNAME| raising exception'
                        raise
                    raise
                if not trial:
                    sys.stderr = stderr_orig
                    sys.stdout = stdout_orig
                    logfile.close()
    print "match_OBJNAME| DONE with func"

def describe_db(c,db=[illum_db]):
    '''inputs: c,db=[illum_db]
    returns:  keys
    calls:
    called_by: match_OBJNAME,match_OBJNAME,match_OBJNAME,match_OBJNAME,match_OBJNAME,save_fit,linear_fit,get_fits'''
    if type(db) != type([]):
        db = [db]
    keys = []
    for d in db:
        command = "DESCRIBE " + d
        #print command
        c.execute(command)
        results = c.fetchall()
        for line in results:
            keys.append(line[0])
    return keys

def save_fit(dict_fit,OBJNAME=None,FILTER=None,PPRUN=None,db=test + 'fit_db'):
    '''inputs: dict_fit,OBJNAME=None,FILTER=None,PPRUN=None,db=test + 'fit_db'
    returns:
    calls: connect_except,describe_db
    called_by: match_OBJNAME,match_OBJNAME,match_OBJNAME,match_OBJNAME,linear_fit,linear_fit,linear_fit,linear_fit,linear_fit,linear_fit,linear_fit,linear_fit'''
    print '\nsave_fit| START the func. inputs: dict_fit=',dict_fit , ' OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' db=',db
    if OBJNAME!= None and FILTER!= None and  PPRUN!=None:
        dict_fit['OBJNAME'] = OBJNAME
        dict_fit['FILTER'] = FILTER
        dict_fit['PPRUN'] = PPRUN

    db2,c = connect_except()

    command = "CREATE TABLE IF NOT EXISTS " + db + " ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    c.execute(command)

    db_keys = describe_db(c,db)

    floatvars = {}
    stringvars = {}
    #copy array but exclude lists
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-' + ','
    for ele in dict_fit.keys():

            type = 'float'
            for l in letters:
                if string.find(str(dict_fit[ele]),l) != -1:
                    type = 'string'
            if type == 'float':
                floatvars[ele] = str(float(dict_fit[ele]))
            elif type == 'string':
                stringvars[ele] = dict_fit[ele]

    # make database if it doesn't exist
    #print 'save_fit| floatvars', floatvars
    #print 'save_fit| stringvars', stringvars
    for column in stringvars:
        stop = False
        for key in db_keys:
            if key.lower() == column.lower(): stop = True
        if not stop:
            try:
                if string.find(column,'reject_plot') != -1 or string.find(column,'im') != -1 or string.find(column,'positioncolumns') != -1:
                    command = 'ALTER TABLE ' + db + ' ADD ' + column + ' varchar(1000)'
                elif string.find(column,'zp_image') != -1:
                    command = 'ALTER TABLE ' + db + ' ADD ' + column + ' varchar(3000)'
                else:
                    command = 'ALTER TABLE ' + db + ' ADD ' + column + ' varchar(100)'
                print "save_fit| command=",command
                c.execute(command)
            except:
                print 'save_fit|  traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)

    for column in floatvars:
        stop = False
        for key in db_keys:
            if key.lower() == column.lower(): stop = True
        if not stop:
            try:
                command = 'ALTER TABLE ' + db + ' ADD ' + column + ' float(15)'
                print "save_fit| command=",command
                c.execute(command)
            except:
                print 'save_fit|  traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)

    # insert new observation
    #print 'save_fit|  db_keys=',db_keys

    OBJNAME = dict_fit['OBJNAME']
    FILTER = dict_fit['FILTER']
    PPRUN = dict_fit['PPRUN']
    sample = dict_fit['sample']
    sample_size = dict_fit['sample_size']

    command = "SELECT OBJNAME from " + db + " where OBJNAME = '" + OBJNAME + "' and FILTER = '" + FILTER + "' and PPRUN='" + PPRUN + "' and sample='" + str(sample) + "' and sample_size='" + str(sample_size) + "'"
    #print 'save_fit|  command=',command
    c.execute(command)
    #print 'save_fit|  OBJNAME,=',OBJNAME, FILTER, PPRUN
    results = c.fetchall()
    #print 'save_fit|  results=',results
    if len(results) > 0:
        print 'save_fit| already added'
    else:
        command = "INSERT INTO " + db + " (OBJNAME,FILTER,PPRUN,sample,sample_size) VALUES ('" + dict_fit['OBJNAME'] + "','" + dict_fit['FILTER'] + "','" + dict_fit['PPRUN'] + "','" + dict_fit['sample'] + "','" + dict_fit['sample_size'] + "')"
        #print 'save_fit| ',command
        c.execute(command)

    vals = ''
    for key in stringvars.keys():
        #print 'save_fit|  key,=',key, stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"

    for key in floatvars.keys():
        #print 'save_fit|  key,=',key, floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    if len(vals) > 1:
        command = "UPDATE " + db + " set " + vals + " WHERE OBJNAME='" + dict_fit['OBJNAME'] + "' AND FILTER='" + dict_fit['FILTER'] + "' AND PPRUN='"  + dict_fit['PPRUN'] + "' and sample='" + str(sample) + "' and sample_size='" + str(sample_size) + "'"
        print 'save_fit|  command=',command
        c.execute(command)

    print 'save_fit|  vals=',vals
    #names = reduce(lambda x,y: x + ',' + y, [x for x in floatvars.keys()])
    #values = reduce(lambda x,y: str(x) + ',' + str(y), [floatvars[x] for x in floatvars.keys()])
    #names += ',' + reduce(lambda x,y: x + ',' + y, [x for x in stringvars.keys()])
    #values += ',' + reduce(lambda x,y: x + ',' + y, ["'" + str(stringvars[x]) + "'" for x in stringvars.keys()])
    #command = "INSERT INTO "+illum_db+" (" + names + ") VALUES (" + values + ")"
    #print 'save_fit| ',command
    #os.system(command)
    print 'save_fit| DONE with func\n'

def sdss_coverage(SUPA,FLAT_TYPE):  #intermediate #step3_run_fit
    '''inputs: SUPA,FLAT_TYPE
    returns:  cov, galaxycat, starcat
    purpose: Determines if the SUPA is in the SDSS field (cov=True if it is, else cov=False). Returns `cov` and path to galaxy/star SDSS catalogs
    calls: get_files,initialize,get_files,save_exposure
    called_by: match_OBJNAME'''

    print 'sdss_coverage| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE
    dict_sdss = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_sdss['FILTER'],dict_sdss['OBJNAME'])
    search_params.update(dict_sdss)

    if search_params['CRVAL1'] is None:
        length(search_params['SUPA'],search_params['FLAT_TYPE'])

    dict_sdss = get_files(SUPA,FLAT_TYPE)
    search_params.update(dict_sdss)
    print "sdss_coverage| search_params['CRVAL1']=",search_params['CRVAL1']
    crval1 = float(search_params['CRVAL1'])
    crval2 = float(search_params['CRVAL2'])
    query = 'select ra, dec from star where ra between ' + str(crval1-0.1) + ' and ' + str(crval1+0.1) + ' and dec between ' + str(crval2-0.1) + ' and ' + str(crval2+0.1)
    print 'sdss_coverage| query=',query

    import sqlcl
    lines = sqlcl.query(query).readlines()
    print 'sdss_coverage| lines=',lines
    if len(lines) > 1: sdss_coverage=True
    else: sdss_coverage=False
    save_exposure({'sdss_coverage':sdss_coverage},SUPA,FLAT_TYPE)

    db2,c = connect_except()
    command = "select cov from sdss_db where OBJNAME='" + dict_sdss['OBJNAME'] + "'"
    c.execute(command)
    results=c.fetchall()
    print 'sdss_coverage| results=',results

    if len(results) == 0:
	#adam-del# import calc_tmpsave; calc_tmpsave.get_sdss_cats(dict_sdss['OBJNAME'])
        get_sdss_cats(dict_sdss['OBJNAME'])
        command = "select cov from sdss_db where OBJNAME='" + dict_sdss['OBJNAME'] + "'"
        c.execute(command)
        results=c.fetchall()
        print 'sdss_coverage| results=',results

    sdss_coverage = results[0][0]

    if string.find(sdss_coverage,'True') != -1:
        cov = True
    else: cov=False

    starcat=data_path+'PHOTOMETRY/sdssstar.cat'
    galaxycat=data_path+'PHOTOMETRY/sdssgalaxy.cat'
    print "sdss_coverage| DONE with func"
    return cov, galaxycat, starcat

#adam-watch# checkout what's going on with `match_many` func and associate command
def match_many(input_list,color=False):
    '''inputs: input_list,color=False
    returns:
    calls: make_ssc_config_few
    called_by: match_OBJNAME'''

    print 'match_many| START the func. inputs: input_list=',input_list , ' color=',color
    if color:
        make_ssc_config_colors(input_list)
        print 'match_many| color=',color
    else:
        make_ssc_config_few(input_list)

    os.system('rm -rf ' + tmpdir + '/assoc/')
    os.system('mkdir -p ' + tmpdir + '/assoc/')

    files = []
    i=0
    for file,prefix,rot in input_list:
        print 'match_many| file=',file
        res = re.split('\/',file)
        #os.system(progs_path['p_ldactoasc']+' -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  os.environ['bonn'] +  res[-1] )
        #os.system('mkreg.pl -c -rad 3 -xcol 0 -ycol 1 -wcs ' +  os.environ['bonn'] + res[-1])

        i += 1
        colour = 'blue'
        if i%2 ==0: colour = 'red'
        if i%3 ==0: colour = 'green'
        res = re.split('\/',file)
        #os.system(progs_path['p_ldactoasc']+' -i ' + file + ' -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > ' +  os.environ['bonn'] +  res[-1] )
        #os.system('mkreg.pl -c -rad ' + str(i) + ' -xcol 0 -ycol 1 -colour ' + colour + ' -wcs ' +  os.environ['bonn'] + res[-1])
        command_ldacaddkey = '%(p_ldacaddkey)s -i %(inputcat)s -t OBJECTS -o %(outputcat)s -k A_WCS_assoc 0.0003 FLOAT "" \
                                        B_WCS_assoc 0.0003 FLOAT "" \
                                        Theta_assoc 0.0 FLOAT "" \
                                        Flag_assoc 0 SHORT "" ' % {'p_ldacaddkey':progs_path['p_ldacaddkey'],'inputcat':file,'outputcat':file + '.assoc1'}
        print 'match_many| command_ldacaddkey=',command_ldacaddkey
        ooo=os.system(command_ldacaddkey)
        if ooo!=0: raise Exception("the line os.system(command_ldacaddkey) failed\ncommand_ldacaddkey="+command_ldacaddkey)

        #command = 'ldacrenkey -i %(inputcat)s -o %(outputcat)s -k ALPHA_J2000 Ra DELTA_J2000 Dec' % {'inputcat':file + '.assoc1','outputcat':file+'.assoc2'}
        #os.system(command)
        files.append(file+'.assoc1')
    files_input = reduce(lambda x,y:x + ' ' + y,files)
    files_output = reduce(lambda x,y:x + ' ' + y,[tmpdir + '/assoc/'+re.split('\/',z)[-1] +'.assd' for z in files])

    print 'match_many| files=',files
    print 'match_many| files_input=',files_input,' files_output=', files_output

    command_associate = progs_path['p_associate']+' -i %(inputcats)s -o %(outputcats)s -t OBJECTS -c %(bonn)s/photconf/fullphotom.alpha.associate' % {'inputcats':files_input,'outputcats':files_output, 'bonn':os.environ['bonn']}
    print 'match_many| command_associate=',command_associate
    ooo=os.system(command_associate)
    if ooo!=0: raise Exception("the line os.system(command_associate) failed\ncommand_associate="+command_associate)
    print 'match_many| associated'

    outputcat = tmpdir + '/final.cat'
    command_make_ssc = '%(p_make_ssc)s -i %(inputcats)s -o %(outputcat)s -t OBJECTS -c %(tmpdir)s/tmp.ssc ' % {'p_make_ssc':progs_path['p_makessc'],'tmpdir': tmpdir, 'inputcats':files_output,'outputcat':outputcat}
    print 'match_many| command_make_ssc=',command_make_ssc
    ooo=os.system(command_make_ssc)
    if ooo!=0: raise Exception("the line os.system(command_make_ssc) failed\ncommand_make_ssc="+command_make_ssc)
    print 'match_many| DONE with func'

#adam-watch# checkout what's going on with `make_ssc_config_few` func and make_ssc  command
def make_ssc_config_few(input_list):
    '''inputs: input_list
    returns:
    calls:
    called_by: match_many'''

    print 'make_ssc_config_few| START the func. inputs: input_list=',input_list
    ofile = tmpdir + '/tmp.cat'
    out = open(tmpdir + '/tmp.ssc','w')

    key_list = ['CHIP','Flag','MAG_AUTO','MAGERR_AUTO','MAG_APER2','MAGERR_APER2','Xpos','Ypos','Xpos_ABS','Ypos_ABS','CLASS_STAR','MaxVal','BackGr','stdMag_corr','stdMagErr_corr','stdMagColor_corr','stdMagClean_corr','stdMagStar_corr','Star_corr','ALPHA_J2000','DELTA_J2000']
    keys = []
    i = -1
    for file_name,prefix,rot in input_list:
        i += 1
        print 'make_ssc_config_few| file_name=',file_name
        print 'make_ssc_config_few| RUNNING: ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile
        os.system('ldacdesc -t OBJECTS -i ' + file_name + ' > ' + ofile)
        file = open(ofile,'r').readlines()
        for line in file:
            if string.find(line,"Key name") != -1 :
                red = re.split('\.+',line)
                key = red[1].replace(' ','').replace('\n','')
                out_key = prefix + key
                if reduce(lambda x,y: x+ y, [string.find(out_key,k)!=-1 for k in key_list]):
                    out.write("COL_NAME = " + out_key + '\nCOL_INPUT = ' + key + '\nCOL_MERGE = AVE_REG\nCOL_CHAN = ' + str(i) + "\n#\n")
                #print ' key=',key
                keys.append(key)

    out.close()
    print "make_ssc_config_few| DONE with func"

def getTableInfo(): #simple #step3
    '''inputs:
    returns:  ROTS
    calls:
    called_by: match_OBJNAME,linear_fit'''

    print '\ngetTableInfo| START the func. No inputs for this func!'
    p = pyfits.open(tmpdir + '/final.cat') #final.cat is the output from match_many func
    #tbdata = p[1].data ; types = [] ; KEYS = {}
    ROTS = {}
    for column in p[1].columns:
        if string.find(column.name,'$') != -1:
            #print 'getTableInfo| column=',column
            res = re.split('\$',column.name)
            ROT = res[0]
            IMAGE = res[1]
            #KEY = res[2]
            if not ROTS.has_key(ROT):
                ROTS[ROT] = []
            if not len(filter(lambda x:x==IMAGE,ROTS[ROT])):
                ROTS[ROT].append(IMAGE)
    print "getTableInfo| DONE with func\n"
    return ROTS

def find_config(GID): #simple
    '''inputs: GID
    returns:  CONFIG_IM
    purpose: based on GABODSID, figure out which configuration the images are from
    calls:
    called_by: match_OBJNAME,match_OBJNAME'''
    #print 'find_config| START the func. inputs: GID=',GID
    config_list = [[575,691,'8'],[691,871,'9'],[817,1309,'10_1'],[1309,3470,'10_2'],[3470,5000,'10_3']]
    CONFIG_IM = None
    for config in config_list:
        if config[0] < GID < config[1]:
            CONFIG_IM = config[2]
            break

    if config is None:
            raise Exception('find_config: no configuration found for GID=%s, may need to define a new configuration for your data' % (GID) )
    #print "find_config| DONE with func"
    return CONFIG_IM

def selectGoodStars(EXPS,match,LENGTH1,LENGTH2,CONFIG): #intermediate #step3
    '''inputs: EXPS,match,LENGTH1,LENGTH2,CONFIG
    returns:  EXPS, star_good(=list of indicies of "good stars"), supas(=list of "good star" info dicts), totalstars(=# of "good stars"), mdn_background(=median background of exposures)
    purpose: find the quality detections in "final.cat". I exclude exposures with <300 good stars and ROTations with <2 exposures. calculate the "mag"(mag=zp-magnitude ; w/ zp=median({magnitudes in exposure}) for each star. quality stars identified by:
    (1) in at least two exposures w/ consistent magnitudes
    (2) in proper flux/magnitude range
    (3) within the center of the RADIAL ring portion of the image and without any flags at that point
    (4) with fairly certain magnitudes (Mag_err<.1)
    if match==True: see if there is an SDSS match and if it's a good match (i.e. match_good==1 if:CLASS_STAR>.65 and SDSSstdMagClean_corr==1 and 40>SDSSstdMag_corr>0 and 5>SDSSstdMagColor_corr>-5)
    calls:
    called_by: match_OBJNAME,linear_fit'''

    print '\nselectGoodStars| START the func. inputs: EXPS=',EXPS , ' match=',match , ' LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2 , ' CONFIG=',CONFIG
    ''' the top two most star-like objects have CLASS_STAR>0.9 and, for each rotation, their magnitudes differ by less than 0.01 '''

    ''' remove a rotation if it has no or one exposure '''
    EXPS_new = {}
    for ROT in EXPS.keys():
        if len(EXPS[ROT]) > 1: EXPS_new[ROT] = EXPS[ROT]
        else: print "Dropped ROT=",ROT, " because len(EXPS[ROT]) <= 1"

    print 'selectGoodStars| EXPS=',EXPS
    if EXPS != EXPS_new:
        print 'selectGoodStars| EXPS_new=',EXPS_new
    EXPS = EXPS_new

    p = pyfits.open(tmpdir + '/final.cat') #final.cat is the output from match_many func
    print 'selectGoodStars| tmpdir+"/final.cat"=',tmpdir+"/final.cat"
    #print 'selectGoodStars| p[1].columns=',p[1].columns
    table = p[1].data
    star_good = []
    supas = []

    totalstars = 0
    #adam-ask# I made this cut consistent with the deeper potential well of the 10_3 config. This makes sense to me because it's more consistent. Is this ok with pat/anja?
    SATURATION=config_dict["SATURATION"][CONFIG]
    flux_cut1=SATURATION-1000
    flux_cut2=SATURATION-2000

    ''' if there is an image with <300 good stars, throw it out '''
    Finished = False
    while not Finished:
        temp = copy(table)
        tlist = []
        for ROT in EXPS.keys():
            for y in EXPS[ROT]:
                tlist.append([y,ROT])
        print 'selectGoodStars| tlist=',tlist

        for y,ROT in tlist:
            mask = temp.field(ROT+'$'+y+'$MAG_AUTO') != 0.0
            good_entries = temp[mask] ; temp = good_entries
            print 'selectGoodStars| ',len(good_entries.field(ROT+'$'+y+'$MAG_AUTO')), ' | not 0.0'
            mask = temp.field(ROT+'$'+y+'$MAG_AUTO') < 30
            good_entries = temp[mask] ; temp = good_entries
            print 'selectGoodStars| ',len(good_entries.field(ROT+'$'+y+'$MAG_AUTO')), ' | less than 30'
            mask = 0 < temp.field(ROT+'$'+y+'$MAG_AUTO')
            good_entries = temp[mask] ; temp = good_entries
            print 'selectGoodStars| ',len(good_entries.field(ROT+'$'+y+'$MAG_AUTO')), ' | greater than 0'
            mask = (temp.field(ROT+'$'+y+'$MaxVal') + temp.field(ROT+'$'+y+'$BackGr')) < flux_cut1
            good_entries = temp[mask] ; temp = good_entries
            good_number = len(good_entries.field(ROT+'$'+y+'$MAG_AUTO'))
            print 'selectGoodStars| ROT=',ROT , ' y=',y , ' good_number=',good_number, ' | flux<flux_cut1=',flux_cut1
            if good_number < 300:
                print 'selectGoodStars| DROPPING!'
                TEMP = {}
                for ROTTEMP in EXPS.keys():
                    TEMP[ROTTEMP] = []
                    for z in EXPS[ROTTEMP]:
                        if y!=z:
                            TEMP[ROTTEMP].append(z)
                EXPS = TEMP
                Finished = False
                break
        if good_number > 0:
            Finished = True
        print 'selectGoodStars| Finished=',Finished
    print 'selectGoodStars| len(temp)=',len(temp)

    '''now get the zp of each of the different exposures: eventually I'm after "mag"(mag=zp-magnitude ; w/ zp=median({magnitudes in exposure}) for each star.'''
    zps = {}
    print 'selectGoodStars| EXPS.keys()=',EXPS.keys() , ' EXPS=',EXPS
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            s = good_entries.field(ROT+'$'+y+'$MAG_AUTO').sum()
            print 'selectGoodStars| s=',s
            print 'selectGoodStars| zp=s/len(good_entries)=',s/len(good_entries)
            zps[y] = s/len(good_entries)
    print 'selectGoodStars| zps=',zps

    tab = {}
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
            if match:
                keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag' ,'SDSSstdMag_corr','SDSSstdMagErr_corr','SDSSstdMagColor_corr','SDSSstdMagClean_corr','SDSSStar_corr',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
                #print 'SDSS', table.field('SDSSstdMag_corr')[-1000:]
            for key in keys:
                tab[key] = copy(table.field(key))
    print 'selectGoodStars| len(table)=',len(table)
    backgrounds = []
    for i in xrange(len(table)):
        class_star_array = [] ; include_star = []  ; name = [] ; mags_diff_array = [] ; mags_good_array = [] ; mags_array = [] #; in_box = []
        for ROT in EXPS.keys():
            mags_array += [tab[ROT+'$'+y+'$MAG_AUTO'][i] for y in EXPS[ROT]]
            mags_diff_array += [zps[y] - tab[ROT+'$'+y+'$MAG_AUTO'][i] for y in EXPS[ROT]]
            mags_good_array += [tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 for y in EXPS[ROT]]
            #in_box += [1000<tab[ROT+'$'+y+'$Xpos_ABS'][i]<9000 and 1000<tab[ROT+'$'+y+'$Ypos_ABS'][i]<7000  for y in EXPS[ROT]]
            #include_star += [( tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0  ) for y in EXPS[ROT]] # and
            backgrounds += filter(lambda x: x!=0, [tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i] for y in EXPS[ROT]])
            if string.find(str(CONFIG),'8') != -1:
                ''' config 8 keep outer ring stars and throw out chips 1 and 5 '''
                include_star += [(tab[ROT+'$'+y+'$CHIP'][i]!=1 and tab[ROT+'$'+y+'$CHIP'][i]!=5) and ( 0<(tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<flux_cut2  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.1 )  for y in EXPS[ROT]]
            elif string.find(str(CONFIG),'9') != -1:
                ''' config 9 throw out chips 1,5,6,10 '''
                include_star += [(tab[ROT+'$'+y+'$CHIP'][i]!=1 and tab[ROT+'$'+y+'$CHIP'][i]!=5 and tab[ROT+'$'+y+'$CHIP'][i]!=6 and tab[ROT+'$'+y+'$CHIP'][i]!=10) and ( 0<(tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<flux_cut2  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.1 and ((tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.)**2.+(tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2.)**2.)<(LENGTH1/2.)**2  )  for y in EXPS[ROT]]
            else: include_star += [( 0<(tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<flux_cut2  and  tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.1 and ((tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.)**2.+(tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2.)**2.)<(LENGTH1/2.)**2  )  for y in EXPS[ROT]]

            #include_star += [( 0<(tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<25000 and tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05) for y in EXPS[ROT]]
            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<25000 and tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05) for y in EXPS[ROT]]
            #in_circ = lambda x,y,r: (x**2.+y**2.)<r**2.
            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i] + tab[ROT+'$'+y+'$BackGr'][i])<25000 and tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05 and in_circ(tab[ROT+'$'+y+'$Xpos_ABS'][i]-LENGTH1/2.,tab[ROT+'$'+y+'$Ypos_ABS'][i]-LENGTH2/2,LENGTH) for y in EXPS[ROT]]
            #include_star += [((tab[ROT+'$'+y+'$MaxVal'][i]+tab[ROT+'$'+y+'$BackGr'][i])<25000 and tab[ROT+'$'+y+'$Flag'][i]==0 and tab[ROT+'$'+y+'$MAG_AUTO'][i]<30 and tab[ROT+'$'+y+'$MAG_AUTO'][i]!=0.0 and tab[ROT+'$'+y+'$MAGERR_AUTO'][i]<0.05) for y in EXPS[ROT]]
            name += [{'name':EXPS[ROT][z],'rotation':ROT} for z in xrange(len(EXPS[ROT]))]
            class_star_array += [tab[ROT+'$'+y+'$CLASS_STAR'][i] for y in EXPS[ROT]]
        class_star_max=scipy.nanmax(class_star_array)

        good_mags_diff_list = []
        for k in xrange(len(mags_good_array)):
            if mags_good_array[k]:
                good_mags_diff_list.append(mags_diff_array[k])
        if len(good_mags_diff_list) > 1:
            median_mag_diff = scipy.median(good_mags_diff_list)
            file_list=[];mag_list=[] #adam-watch# I'm adding in the mag_list object because I'm changing "mag" so that it isn't a random thing anymore, but it really shouldn't matter anyway.
            for j in xrange(len(include_star)):
                if include_star[j] and abs(mags_diff_array[j] - median_mag_diff) < 1.:  # MAIN PARAMETER!
                    file_list.append(name[j])
                    mag = mags_diff_array[j] #adam-watch# I was assigning a random `mag` of the ones within 1 mag of the median, but now I'm making a list of these and picking the median of that list. That seems less arbitrary
                    mag_list.append(mag) #adam-watch# I'm adding in the mag_list object because I'm changing "mag" so that it isn't a random thing anymore, but it really shouldn't matter anyway.
            if match:
                ''' if match object exists '''
                if tab['SDSSstdMag_corr'][i] != 0.0: match_exists = 1
                else: match_exists = 0
                ''' if match object is good -- throw out galaxies for this '''
                if float(tab['SDSSstdMagClean_corr'][i]) == 1 and abs(class_star_max) > 0.65 and 40. > tab['SDSSstdMag_corr'][i] > 0.0 and 5 > tab['SDSSstdMagColor_corr'][i] > -5: match_good = 1
                else: match_good = 0
            else:
                match_good = 0
                match_exists = 0
            if len(file_list) > 1:
                totalstars += len(file_list)
                star_good.append(i)
                mag=scipy.median(mag_list) #adam-watch# I'm changing "mag" so that it isn't a random thing anymore, but it really shouldn't matter anyway.
                supas.append({'mag':mag,'table index':i,'supa files':file_list, 'match':match_good, 'match_exists':match_exists, 'std':scipy.std(good_mags_diff_list)})
        if i%2000==0: print 'selectGoodStars|  star number i=',i

    supas.sort(sort_supas)
    mdn_background = scipy.median(scipy.array(backgrounds))
    print "selectGoodStars| DONE with func\n"
    return EXPS, star_good, supas, totalstars, mdn_background

def sort_supas(x,y): #simple
    '''inputs: x,y
    returns:  -1
    calls:
    called_by: '''

    if x['mag'] > y['mag']:
        return 1
    else: return -1

def starStats(supas): #simple #step3
    '''inputs: supas
    returns:  stats
    purpose: print stats based on how many SDSS matches, good SDSS matches, rotations, and stars in each supa you have in this `supas` dict
    calls:
    called_by: match_OBJNAME,linear_fit,linear_fit'''

    print '\nstarStats| START the func. inputs: len(supas)=',len(supas)
    stats = {}
    stats_ims = {}
    stats['rot'] = 0
    stats['match'] = 0
    stats['match_exists'] = 0
    for s in supas:
        if s['match']: stats['match'] += 1
        if s['match_exists']: stats['match_exists'] += 1
        s = s['supa files']
        rots = []
        for ele in s:
            if not stats.has_key(ele['name']):
                stats[ele['name']] = 0
                stats_ims[ele['name']] = 0
            stats[ele['name']] += 1
            stats_ims[ele['name']] += 1
            rot =ele['rotation']
            if rot not in rots:
                rots.append(rot)
        if len(rots) > 1:
            stats['rot'] += 1

    for key in stats.keys():
        print 'starStats| # with ',key ,': ',stats[key]
    stats['ims'] = stats_ims
    print "starStats| DONE with func\n"
    return stats

def linear_fit(OBJNAME,FILTER,PPRUN,run_these,match=None,CONFIG=None,primary=None,secondary=None): #intermediate #step3_run_fit
    '''inputs: OBJNAME,FILTER,PPRUN,run_these,match=None,CONFIG=None,primary=None,secondary=None
    returns: it runs the IC fit and saves the fit to the SQL database
    purpose: creates the matricies and performs a sparse fit. Does some diagnostic plotting. Writes out the catalogs: data_path + 'PHOTOMETRY/ILLUMINATION/' + 'catalog_' + PPRUN + '.cat'
    calls: getTableInfo,get_files,selectGoodStars,starStats,describe_db,save_fit,starStats,calcDataIllum,save_fit,save_fit,save_fit,save_fit,get_fits,save_fit,save_fit,calcDataIllum,calcDataIllum,calcDataIllum,save_fit
    called_by: match_OBJNAME'''

    print '\nlinear_fit| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' run_these=',run_these , ' match=',match , ' CONFIG=',CONFIG , ' primary=',primary , ' secondary=',secondary
    redoselect = False #if True will redo selectGoodStars and starStats. `redoselect = False` is appropriate since match_OBJNAME already takes care of making these catalogs

    ''' create chebychev polynomials '''
    if CONFIG == '10_3' or string.find(CONFIG,'8')!=-1 or string.find(CONFIG,'9')!=-1:
        cheby_x = [{'n':'0x','f':lambda x,y:1.,'order':0},{'n':'1x','f':lambda x,y:x,'order':1},{'n':'2x','f':lambda x,y:2*x**2-1,'order':2}] #,{'n':'3x','f':lambda x,y:4*x**3.-3*x,'order':3},{'n':'4x','f':lambda x,y:8*x**4.-8*x**2.+1,'order':4}]#,{'n':'5x','f':lambda x,y:16*x**5.-20*x**3.+5*x,'order':5}]
        cheby_y = [{'n':'0y','f':lambda x,y:1.,'order':0},{'n':'1y','f':lambda x,y:y,'order':1},{'n':'2y','f':lambda x,y:2*y**2-1,'order':2}] #,{'n':'3y','f':lambda x,y:4*y**3.-3*y,'order':3},{'n':'4y','f':lambda x,y:8*y**4.-8*y**2.+1,'order':4}] #,{'n':'5y','f':lambda x,y:16*y**5.-20*y**3.+5*y,'order':5}]
    else:
        cheby_x = [{'n':'0x','f':lambda x,y:1.,'order':0},{'n':'1x','f':lambda x,y:x,'order':1},{'n':'2x','f':lambda x,y:2*x**2-1,'order':2},{'n':'3x','f':lambda x,y:4*x**3.-3*x,'order':3}] #,{'n':'4x','f':lambda x,y:8*x**4.-8*x**2.+1,'order':4},{'n':'5x','f':lambda x,y:16*x**5.-20*x**3.+5*x,'order':5}]
        cheby_y = [{'n':'0y','f':lambda x,y:1.,'order':0},{'n':'1y','f':lambda x,y:y,'order':1},{'n':'2y','f':lambda x,y:2*y**2-1,'order':2},{'n':'3y','f':lambda x,y:4*y**3.-3*y,'order':3}] #,{'n':'4y','f':lambda x,y:8*y**4.-8*y**2.+1,'order':4},{'n':'5y','f':lambda x,y:16*y**5.-20*y**3.+5*y,'order':5}]
    cheby_terms = []
    cheby_terms_no_linear = []
    for tx in cheby_x:
        for ty in cheby_y:
            if 1: #tx['order'] + ty['order'] <=3:
                if not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
                if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
    print 'linear_fit| cheby_terms=',cheby_terms , ' CONFIG=',CONFIG , ' cheby_terms_no_linear=',cheby_terms_no_linear
    #adam-fragments_removed# linear_fit-store_and_model

    ''' EXPS has all of the image information for different rotations '''
    start_EXPS = getTableInfo()
    print 'linear_fit| start_EXPS=',start_EXPS

    dt = get_files(start_EXPS[start_EXPS.keys()[0]][0])
    print 'linear_fit| dt["CHIPS"]=',dt["CHIPS"]
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    if string.find(CONFIG,'8')!=-1:
        CHIPS = [2,3,4,6,7,8]
    elif string.find(CONFIG,'9')!=-1:
        CHIPS = [2,3,4,7,8,9]

    #''' see if linear or not '''
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']
    print 'linear_fit| LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2

    ''' get stars from the selectGoodStars func '''
    if redoselect:
        EXPS, star_good,supas, totalstars, mdn_background = selectGoodStars(start_EXPS,match,LENGTH1,LENGTH2,CONFIG)
        uu = open(tmpdir + '/selectGoodStars','w')
        info = starStats(supas)
        pickle.dump({'info':info,'EXPS':EXPS,'star_good':star_good,'supas':supas,'totalstars':totalstars},uu)
        uu.close()
    f=open(tmpdir + '/selectGoodStars','r')
    m=pickle.Unpickler(f)
    d=m.load()

    ''' if early chip configuration, use chip color terms '''
    if (CONFIG=='8' or CONFIG=='9'): relative_colors = True
    else: relative_colors = False

    ''' read out of pickled dictionary '''
    info = d['info'];EXPS = d['EXPS'];star_good = d['star_good'];supas = d['supas'];totalstars = d['totalstars']
    print 'linear_fit| EXPS=',EXPS
    print 'linear_fit| len(star_good)=',len(star_good)

    #fitvars_fiducial = False
    p = pyfits.open(tmpdir + '/final.cat') #final.cat is the output from match_many func
    table = p[1].data
    p.close()

    #adam-note# `table` and `supas` have closely related data. supas[#]['table index'] will give you the index of `table` that this "#" in `supas` corresponds to
    tab = {}
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos',ROT+'$'+y+'$Ypos',ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
            if match:
                keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos',ROT+'$'+y+'$Ypos',ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag' ,'SDSSstdMag_corr','SDSSstdMagErr_corr','SDSSstdMagColor_corr','SDSSstdMagClean_corr','SDSSStar_corr',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
            for key in keys:
                tab[key] = copy(table.field(key))
    del table

    supas_copy = copy(supas)
    coord_conv_x = lambda x:((2.*x)-LENGTH1)/LENGTH1
    coord_conv_y = lambda x:((2.*x)-LENGTH2)/LENGTH2
    #adam-fragments_removed# linear_fit-find_the_color_term

    sample = str(match)
    sample_copy = copy(sample)
    print 'linear_fit| sample=',sample
    db2,c = connect_except()

    ## back to using run_these from input!
    #run_these=["all","rand1","rand2","rand3","rand4","rand5","rand6","rand7","rand8","rand9","rand10"] #,"rand11","rand12","rand13","rand14","rand15","rand16","rand17","rand18","rand19","rand20"]
    #adam-fragments_removed# linear_fit-rands_and_run_these (RERPLACED)
    for original_sample_size in run_these:
        print 'linear_fit| loop0: for original_sample_size in run_these: (run_these=["all","rand1","rand2","rand3","rand4","rand5","rand6","rand7","rand8","rand9","rand10"])'
        print 'linear_fit| loop0: original_sample_size='+original_sample_size

        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':original_sample_size,'primary_filt':primary,'secondary_filt':secondary,'coverage':str(match),'relative_colors':relative_colors,'catalog':str(match),'CONFIG':CONFIG,'supas':len(supas),'match_stars':len(filter(lambda x:x['match'],supas))})
        print 'linear_fit| totalstars=',totalstars , ' len(supas)=',len(supas)
	if original_sample_size == 'all':
            #adam-ask# Is this shortening of `supas` if there are more than 30000 stars just to make it so that the fit runs quickly? If that's the case I can probably just continue to leave this out.
            if totalstars > 30000:
                ''' shorten star_good, supas '''
                supas = []
                ''' include bright stars and matched stars '''
                for supa in supas_copy:
                    if len(supas) < int(float(30000)/float(totalstars)*len(supas_copy))  or supa['match']:
                        supas.append(supa)
            else:
                supas = copy(supas_copy)
            ''' if sdss comparison exists, run twice to see how statistics are improved '''
            if sample == 'sdss':
                ''' first all info, then w/o sdss, then fit for zps w/ sdss but not position terms, then run fit for zps w/o position terms '''
                runs = [[original_sample_size,True,supas,'sdss',True],[original_sample_size + 'None',True,supas,'None', False],[original_sample_size + 'sdsscorr',False,supas,'sdss',False],[original_sample_size + 'sdssuncorr',False,supas,'sdss',False]]
                #adam-no_more# adding another run to `runs`, the first one will be like the original first, but with try_linear=False, just to see if I get a better fit that way
                #adam-no_more# runs = [[original_sample_size,True,supas,'sdss',False],[original_sample_size,True,supas,'sdss',True],[original_sample_size + 'None',True,supas,'None', False],[original_sample_size + 'sdsscorr',False,supas,'sdss',False],[original_sample_size + 'sdssuncorr',False,supas,'sdss',False]]
            else:
                runs = [[original_sample_size,True,supas,sample_copy,True],[original_sample_size + 'corr',False,supas,sample_copy,True],[original_sample_size + 'uncorr',False,supas,sample_copy,True]]
        else:
            if totalstars > 60000:
                ''' shorten star_good, supas '''
                supas_short = copy(supas_copy[0:int(float(60000)/float(totalstars)*len(supas_copy))])
            else:
                supas_short = copy(supas_copy)

            ''' take a random sample of half '''
            ## changing the CLASS_STAR criterion upwards helps as does increasing the sigma on the SDSS stars
            print 'linear_fit| len(supas_short)=',len(supas_short)
            star_nums = range(len(supas_short))
	    random.shuffle(star_nums) #this shuffles star_nums in place
	    star_nums_sample = star_nums[:len(supas_short)/2]
	    star_nums_complement = star_nums[len(supas_short)/2:]

            ''' shorten star_good, supas '''
            supas = [supas_short[i] for i in star_nums_sample]
            supas_complement = [supas_short[i] for i in star_nums_complement]
            ''' make the complement '''
            runs = [[original_sample_size,True,supas,sample_copy,True],[original_sample_size + 'corr',False,supas_complement,sample_copy,True],[original_sample_size + 'uncorr',False,supas_complement,sample_copy,True]]

        print 'linear_fit| len(supas)=',len(supas), ' info["rot"]=',info["rot"]
        print 'linear_fit| original_sample_size=',original_sample_size , ' match=',match , ' sample=',sample,' info["match"]=',info["match"]

        '''
        first all info                                  : sample_size= "all"            calc_illum= True  sample= "sdss"  try_linear= True
        then w/o sdss                                   : sample_size= "allNone"        calc_illum= True  sample= "None"  try_linear= False
        then fit for zps w/ sdss but not position terms : sample_size= "allsdsscorr"    calc_illum= False sample= "sdss"  try_linear= False
        then run fit for zps w/o position terms         : sample_size= "allsdssuncorr"  calc_illum= False sample= "sdss"  try_linear= False
        '''
        # sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True             : first w/ sdss, fit for position, sdss, & exp terms
        # sample_size-is-allNone__calc_illum-is-True__sample-is-None__try_linear-is-False        : then w/o sdss, fit for position & exp terms (*lone_position_corr*)
        # sample_size-is-allsdsscorr__calc_illum-is-False__sample-is-sdss__try_linear-is-False   : then  w/ sdss, fit for sdss, & exp terms (but not position terms) using data pre-corrected by *lone_position_corr*
        # sample_size-is-allsdssuncorr__calc_illum-is-False__sample-is-sdss__try_linear-is-False : then  w/ sdss, fit for sdss, & exp terms (but not position terms) using normal data
        fitvars_runs={}
        run_goodness_info={};run_infos=[]
        run_goodness_info["stars"]='\n# stars detected: total=%s , found match in SDSS =%s found in both rotations=%s ' % (len(supas), info['match'],info['rot'])+'\n# mag^exp_star values totalstars='+str(totalstars)
        print run_goodness_info["stars"]
        for sample_size, calc_illum, supas,  sample , try_linear in runs:
            print '\nlinear_fit| loop1-(1/1) loops over `runs` to do different types of fits | for sample_size, calc_illum, supas,  sample , try_linear in runs: (runs = [[sample_size,True,supas,"sdss",True],[sample_size + "None",True,supas,"None", False],[sample_size + "sdsscorr",False,supas,"sdss",False],[sample_size + "sdssuncorr",False,supas,"sdss",False]]) since (sample == "sdss" and sample_size == "all")'
            print 'linear_fit| loop1-(1/1) loops over `runs` to do different types of fits | sample_size=',sample_size , ' calc_illum=',calc_illum , 'sample=', sample , ' try_linear=',try_linear

            run_info=extra_nametag+'__sample_size-is-'+str(sample_size)+'__calc_illum-is-'+str(calc_illum)+'__sample-is-'+str(sample)+'__try_linear-is-'+str(try_linear)
            print "linear_fit| run_info=",run_info
            run_goodness_info[run_info]= '';run_infos.append(run_info)

            '''### MAIN1-START ### SETUP THE MATRIX place all free parameters in columns for this particular run.'''
            print 'linear_fit| ....determine matrix structure/setup....'
            #adam-note#(in wtg2 paper) we only include the linear terms in the fit if there are a sufficient number of stars (600 here, but it's 400 in the paper)
            if try_linear and info['match'] > 600: #adam-ask# 600 here, but it's 400 in the paper!
                print 'linear_fit| try_linear and info["match"] > 600  ==> use all cheby terms in fit'
                cheby_terms_use = cheby_terms
            else:
                print 'linear_fit| dont use linear cheby terms in fit'
                cheby_terms_use = cheby_terms_no_linear
            #adam-fragments_removed# linear_fit-loop_over_samples

            #adam-note#(in wtg2 paper) `columns` contains all of the entries that will be included in the fit
            #adam-note#(in wtg2 paper) columns= position_columns + zp_columns + color_columns + mag_columns
            #adam-note#(in wtg2 paper) position_columns: f(x,y)_rot [ {'name':name,'fx':term['fx'],'fy':term['fy'],'rotation':ROT,'index':index} ]
            #adam-note#(in wtg2 paper) zp_columns: O_chip, ZP_exp and O_cat [ {'name':'zp_'+str(chip)} and {'name':'zp_image_'+exp} and {'name':'zp_SDSS','image':'match','index':index} ]
            #adam-note#(in wtg2 paper) color_columns: handles S_cat*c^cat_star [ color_columns=[{'name':'SDSS_color','image':'match_color_term','index':index, 'chip_group':[]}]]
            #adam-note#(in wtg2 paper) mag_columns:m^model_star [ mag_columns=[{'name':'mag_' + str(star['table index'])} for star in supas]]
            ''' if random, run first with one half, then the other half, applying the correction '''
            columns = []
            ''' position-dependent terms in design matrix '''
            position_columns = []
            index = -1
            if calc_illum:
                for ROT in EXPS.keys():
                    for term in cheby_terms_use:
                        index += 1
                        name = str(ROT) + '$' + term['n'] # + reduce(lambda x,y: x + 'T' + y,term)
                        position_columns.append({'name':name,'fx':term['fx'],'fy':term['fy'],'rotation':ROT,'index':index})
                columns += position_columns

            ''' zero point terms in design matrix '''
            #adam-ask: It seems to me that `per_chip` and `same_chips` need not be options, but that the code should be written as if these things were set in stone, leaving no option for future users to make worse fits
            per_chip = False  # have a different zp for each chip on each exposures
            same_chips =True  # have a different zp for each chip but constant across exposures

            print 'linear_fit| T/F of these determine "columns" structure: calc_illum=',calc_illum , ' per_chip=',per_chip , ' same_chips=',same_chips , ' match=',match , ' relative_colors=',relative_colors,' try_linear=',try_linear
            zp_columns = []
            if not per_chip:
                for ROT in EXPS.keys():
                    for exp in EXPS[ROT]:
                        index += 1
                        zp_columns.append({'name':'zp_image_'+exp,'image':exp,'im_rotation':ROT,'index':index})
            else:
                for ROT in EXPS.keys():
                    for exp in EXPS[ROT]:
                        for chip in CHIPS:
                            index += 1
                            zp_columns.append({'name':'zp_image_'+exp + '_' + chip,'image':exp,'im_rotation':ROT, 'chip':chip,'index':index})

            if calc_illum and not per_chip and same_chips:
                for chip in CHIPS:
                    index += 1
                    zp_columns.append({'name':'zp_'+str(chip),'image':'chip_zp','chip':chip,'index':index})

            if match:
                index += 1
                zp_columns.append({'name':'zp_SDSS','image':'match','index':index})
            columns += zp_columns

            color_columns = []
            if match:
                if relative_colors:# CONFIG == '10_3' => relative_colors==False
                    ''' add chip dependent color terms'''
                    for group in config_bonn.chip_groups[str(CONFIG)].keys():
                        ''' this is the relative color term, so leave out the first group '''
                        if float(group) != 1:
                            index += 1
                            color_columns.append({'name':'color_group_'+str(group),'image':'chip_color','chip_group':group,'index':index})
                ''' add a color term for the catalog '''
                index += 1
                color_columns+=[{'name':'SDSS_color','image':'match_color_term','index':index, 'chip_group':[]}]
            columns += color_columns
            print 'linear_fit| color_columns=',color_columns

            mag_columns = []
            for star in supas:
                mag_columns.append({'name':'mag_' + str(star['table index'])})
            columns += mag_columns

            column_names = [x['name'] for x in columns] #reduce(lambda x,y: x+y,columns)]
            print 'linear_fit| column_names[0:20]=',column_names[0:20]

            print 'linear_fit| len(position_columns)=',len(position_columns) , ' len(zp_columns)=',len(zp_columns) , ' len(color_columns)=',len(color_columns) , ' len(mag_columns)=',len(mag_columns)
            run_goodness_info[run_info]+= '\nlen(position_columns)='+str(len(position_columns))+' len(zp_columns)='+str(len(zp_columns))+' len(color_columns)='+str(len(color_columns))+' len(mag_columns)='+str(len(mag_columns))
            for col,colname in zip([position_columns , zp_columns , color_columns , mag_columns], ["position_columns","zp_columns","color_columns","mag_columns"]):
                print 'linear_fit| ',colname,': ',scipy.array([c['name'] for c in col])
            x_length = len(position_columns) + len(zp_columns) + len(color_columns) + len(mag_columns)
            if not len(columns)==x_length: raise Exception('linear_fit: COLUMN LENGTH DISAGREEMENT: len(columns)='+str(len(columns))+' != x_length='+str(x_length))
            #adam-old# x_length = len(columns)
            #adam-watch# what if it's not sdss? then not multiply by 2 in y_length? I think it won't effect the solution that you get, but I'm not too sure.
            y_length = reduce(lambda x,y: x + y,[len(star['supa files'])*2 for star in supas]) # double number of rows for SDSS
            print 'linear_fit| x_length=',x_length , ' y_length=',y_length
            '''### MAIN1-END ### SETUP THE MATRIX place all free parameters in columns for this particular run.'''

            '''### MAIN2-START ### FILL THE MATRIX WITH INFORMATION'''
            #adam-note# let M = # of mag^exp_star and mag^sdss_star values (M=y_length, this is the number of equations, except not all of the elements of "star['supa files'] for star in supas" will have an sdss match, so these ones will get a row of zeros)
            #adam-note# let N = # of free parameters in the fit. (N=x_length == len(columns), this is the number of unknowns )
            #adam-note# we're going to solve A * x = B ; where A is (M,N) matrix, B is (M,1) vector, we solve for the (N,1) vector of free parameters x
            #adam-note# so we loop over the M star mags (exp and sdss):
            #adam-note#    loop over the N values corresponding to free parameter things: (ex. for cheby poly coeffs, we put the value of cheby_nth_degree(x,y) into A, in order to fit for the coefficient in x)
            #adam-note#        star_A.append([row_num,col_num+supa_num,value]) #happens multiple times. goes through each of the "columns" for each row
            #adam-note#    star_B.append([row_num,value]) #happens once. value = MAG_AUTO for exposures and SDSSstdMag_corr for SDSS match
            #adam-note#    sigmas.append([row_num,sigma]) #happens once (unrelated to fit)

            print 'linear_fit| ....creating matrix....'
            #adam-del# Bstr = ''
            row_num = -1;supa_num = -1
            ''' each star '''
            inst = [];data = {} ; magErr = {} ; whichimage = {} ; X = {} ; Y = {} ; color = {} ; chipnums = {} ; Star = {} ; catalog_values = {}
            for ROT in EXPS.keys():
                data[ROT] = [] ; magErr[ROT] = [] ; X[ROT] = [] ; Y[ROT] = [] ; color[ROT] = [] ; whichimage[ROT] = [] ; chipnums[ROT] = [] ; Star[ROT] = []
            x_positions = {} ; y_positions = {}
            #adam-del#chip_dict = {}
            '''### MAIN2a-START ### put M^exp_star info in MATRIX'''
            print "linear_fit| loop2-(1/3) sets up the matrix | for star in supas: NOT GOING TO PRINT DURRING EVERY LOOP THIS TIME"
            for star in supas:
                supa_num += 1
                ''' each exp of each star '''
                #adam-del# star_A = [] ; star_B = [] ; star_B_cat = [] ; sigmas = []
                star_A = [] ; star_B = [] ; sigmas = []
                for exp in star['supa files']:
                    row_num += 1
                    col_num = -1
                    rotation = exp['rotation']
                    chip = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                    x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                    y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                    #adam-del# x_rel = tab[str(rotation) + '$' + exp['name'] + '$Xpos'][star['table index']]
                    #adam-del# y_rel = tab[str(rotation) + '$' + exp['name'] + '$Ypos'][star['table index']]
                    x_positions[row_num] = x
                    y_positions[row_num] = y
                    x = coord_conv_x(x)
                    y = coord_conv_y(y)

                    #adam-fragments_removed# linear_fit-10_3_subchips
                    sigma = tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']]
		    if sigma < 0.001: sigma = 0.001 #adam-ask# sigma lower limit: here if sigma < 0.001: sigma = 0.001 (MAGERR_AUTO)

                    #adam-START#UNCERTAINTY_CHANGE# weight by 1/sigma**2, not 1/sigma
                    if calc_illum:
                        for c in position_columns:
                            col_num += 1
                            if c['rotation'] == rotation:
                                #adam-tmp# value = c['fx'](x,y)*c['fy'](x,y)/sigma**2 #UNCERTAINTY_CHANGE#
                                value = c['fx'](x,y)*c['fy'](x,y)/sigma
                                star_A.append([row_num,col_num,value])

                    first_exposure = True
                    for c in zp_columns:
                        col_num += 1
                        #if not degeneracy_break[c['im_rotation']] and c['image'] == exp['name']:
                        if not per_chip:
                            if (first_exposure is not True  and c['image'] == exp['name']):
                                #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                                value = 1./sigma
                                star_A.append([row_num,col_num,value])
                            if calc_illum and same_chips and c.has_key('chip'):
                                if (c['chip'] == chip) and chip != CHIPS[0]:
                                    #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                                    value = 1./sigma
                                    star_A.append([row_num,col_num,value])
                            first_exposure = False
                        #if per_chip:
                        #    if (first_column is not True and c['image'] == exp['name'] and c['chip'] == chip):
                        #        #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                        #        value = 1./sigma
                        #        star_A.append([row_num,col_num,value])


                    ''' fit for the color term dependence for SDSS comparison '''
                    if match:
                        ''' this is if there are different color terms for EACH CHIP!'''
                        if relative_colors:
                            for c in color_columns:
                                col_num += 1
                                for chip_num in c['chip_group']:
                                    if float(chip_num) == float(chip):
                                        #adam-tmp# value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma**2 #UNCERTAINTY_CHANGE#
                                        value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                                        star_A.append([row_num,col_num,value])
                        else:
                            col_num += 1 #adam-watch# this seems a little strange. Is it ever appropriate to have `col_num+=1` lines back-to-back without ever adding something to the table in between?

                    ''' magnitude column -- include the correct/common magnitude '''
                    col_num += 1 #adam-watch# this seems a little strange. Is it ever appropriate to have `col_num+=1` lines back-to-back without ever adding something to the table in between?
                    #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                    value = 1./sigma
                    star_A.append([row_num,col_num+supa_num,value])
                    ra = tab[str(rotation) + '$' + exp['name'] + '$ALPHA_J2000'][star['table index']]
                    dec = tab[str(rotation) + '$' + exp['name'] + '$DELTA_J2000'][star['table index']]

                    if calc_illum or string.find(sample_size,'uncorr') != -1: #if calc_illum or if 'uncorr' in sample_size
                        #adam-tmp# value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]/sigma**2 #UNCERTAINTY_CHANGE#
                        value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]/sigma
                    elif not calc_illum: #only hit this for run=sample_size-is-allsdsscorr__calc_illum-is-False__sample-is-sdss__try_linear-is-False
                        ''' correct the input magnitudes using the previously fitted correction '''
                        epsilon_cheby_chip=0 #(epsilon_cheby_chip=C(x,y,chip,rot) in paper)
                        #adam-watch# fitvars_use= fitvars_runs["sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True"]
                        #adam-watch# instead it's using the fitvars from sample_size-is-allNone__calc_illum-is-True__sample-is-None__try_linear-is-False right now, which is maybe not ideal, but at least the try_linear is consistent, which is necessary!
                        for term in cheby_terms_use:
                            epsilon_cheby_chip += fitvars[str(rotation)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                        epsilon_cheby_chip += float(fitvars['zp_' + str(chip)])
                        #adam-tmp# value = (tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']] - epsilon_cheby_chip)/sigma**2 #UNCERTAINTY_CHANGE#
                        value = (tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']] - epsilon_cheby_chip)/sigma
                        #print 'linear_fit| epsilon_cheby_chip=',epsilon_cheby_chip , ' value=',value

                    star_B.append([row_num,value])
                    sigmas.append([row_num,sigma])
		    #adam: 1/sigma -> 1/sigma**2 requires value*sigma -> value*sigma**2 below
                    catalog_values[col_num+supa_num] = {'inst_value':value*sigma,'ra':ra,'dec':dec,'sigma':sigma} # these values are written into 'catalog_' + PPRUN + '.cat'
                    #adam-tmp# catalog_values[col_num+supa_num] = {'inst_value':value*sigma**2,'ra':ra,'dec':dec,'sigma':sigma} #UNCERTAINTY_CHANGE#

                    #x_long = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                    #y_long = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                    #x = coord_conv_x(x_long)
                    #y = coord_conv_y(y_long)
                    #if fitvars_fiducial:
                    #    value += add_single_correction(x,y,fitvars_fiducial)

                '''end loop over exposures that the star was found in'''
                inst.append({'type':'match','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})
                #'''### MAIN2a-END ### put M^exp_star info in MATRIX'''

                ''' only include one SDSS observation per star '''
                #print sample , star["match"] , star["match"] and (sample=="all" or sample=="sdss" or sample=="bootstrap") # and tab["SDSSStar_corr"][star["table index"]] == 1
                if star['match'] and (sample=='sdss' or sample=='bootstrap'): # and tab['SDSSStar_corr'][star['table index']] == 1:
                    '''### MAIN2b-START ### put SDSS match information in MATRIX (if sample=='sdss' or sample=='bootstrap')'''

                    star_A = [] ; star_B = [] ; sigmas = []
                    ''' need to filter out bad colored-stars '''
                    row_num += 1;col_num = -1
                    sigma = tab['SDSSstdMagErr_corr'][star['table index']]
		    if sigma < 0.03: sigma = 0.03 #adam-ask# sigma lower limit: here if sigma < 0.03: sigma = 0.03 (SDSSstdMagErr_corr)

                    for c in position_columns:
                        col_num += 1
                    #adam-del# first_column = True
                    for c in zp_columns:
                        col_num += 1
                        ''' remember that the good magnitude does not have any zp dependence!!! '''
                        if c['image'] == 'match':
                            #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                            value = 1./sigma
                            star_A.append([row_num,col_num,value])
                            x_positions[row_num] = x
                            y_positions[row_num] = y
                        #adam-del# first_column = False

                    ''' fit for the color term dependence for SDSS comparison -- '''
                    if relative_colors:
                        ''' this is if there are different color terms for EACH CHIP!'''
                        for c in color_columns:
                            col_num += 1
                            if c['name'] == 'SDSS_color':
                                #adam-tmp# value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma**2 #UNCERTAINTY_CHANGE#
                                value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                                star_A.append([row_num,col_num,value])
                    else:
                        col_num += 1
                        #adam-tmp# value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma**2 #UNCERTAINTY_CHANGE#
                        value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                        star_A.append([row_num,col_num,value])

                    #adam-watch# I don't understand why this part is necessary!
                    col_num += 1
                    ''' magnitude column -- include the correct/common magnitude '''
                    #adam-tmp# value = 1./sigma**2 #UNCERTAINTY_CHANGE#
                    value = 1./sigma
                    star_A.append([row_num,col_num+supa_num,value])

                    #adam-tmp# value = tab['SDSSstdMag_corr'][star['table index']]/sigma**2 #UNCERTAINTY_CHANGE# 
                    value = tab['SDSSstdMag_corr'][star['table index']]/sigma
                    star_B.append([row_num,value])
                    sigmas.append([row_num,sigma])
                    inst.append({'type':'sdss','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})

                    ''' record star MAG_SDSS-MAG_EXP offsets for each star matched in multiple exposures and in SDSS '''
                    for exp in star['supa files']:
                        rotation = exp['rotation']
                        x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                        x = coord_conv_x(x)
                        y = coord_conv_y(y)
                        if calc_illum or string.find(sample_size,'uncorr') != -1: #if calc_illum or if 'uncorr' in sample_size
                            value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]
                        elif not calc_illum: #only hit this for run=sample_size-is-allsdsscorr__calc_illum-is-False__sample-is-sdss__try_linear-is-False
                            ''' correct the input magnitudes using the previously fitted correction '''
                            epsilon_cheby_chip=0  #(epsilon_cheby_chip=C(x,y,chip,rot) in paper)
                            #adam-watch# fitvars_use= fitvars_runs["sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True"]
                            #adam-watch# instead it's using the fitvars from sample_size-is-allNone__calc_illum-is-True__sample-is-None__try_linear-is-False right now, which is maybe not ideal, but at least the try_linear is consistent, which is necessary!
                            for term in cheby_terms_use:
                                epsilon_cheby_chip += fitvars[str(rotation)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                            epsilon_cheby_chip += float(fitvars['zp_' + str(chip)])
                            value = (tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']] - epsilon_cheby_chip)
                        data[str(rotation)].append(value - tab['SDSSstdMag_corr'][star['table index']])
                        Star[str(rotation)].append(tab['SDSSStar_corr'][star['table index']])
                        magErr[str(rotation)].append(tab['SDSSstdMagErr_corr'][star['table index']])
                        whichimage[str(rotation)].append(exp['name'])
                        X[str(rotation)].append(tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']])
                        Y[str(rotation)].append(tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']])
                        color[str(rotation)].append(tab['SDSSstdMagColor_corr'][star['table index']])
                        chipnums[str(rotation)].append(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']])
                    '''### MAIN2b-END ### put SDSS match information in MATRIX (if sample=='sdss' or sample=='bootstrap')'''
            '''end loop over stars'''
            '''### MAIN2-END ### FILL THE MATRIX WITH INFORMATION'''

            ''' save the SDSS matches '''
            matches = {'data':data,'magErr':magErr,'whichimage':whichimage,'X':X,'Y':Y,'color':color ,'chipnums':chipnums ,'Star':Star}
            uu = open(tmpdir + '/sdss','w')
            pickle.dump(matches,uu)
            uu.close()
            #print 'linear_fit| EXPS=',EXPS
            for rot in EXPS.keys():
                if run_info==run_infos[0]:
                    run_goodness_info["stars"]+='\n# mag^exp_star values with SDSS match for rot='+str(rot)+ ': '+str(len(data[str(rot)]))
                    print 'linear_fit| rot=',rot , ' len(data[str(rot)])=',len(data[str(rot)])

            '''### MAIN3-START ### DO FITTING'''
            ''' do fitting '''#not quick!
            for attempt in ['first','rejected']:
                print "linear_fit| loop2-(2/3) performs the fit | for attempt in ['first','rejected']:"
                print 'linear_fit| loop2-(2/3) performs the fit | attempt=',attempt
                ''' make matrices/vectors '''
                Ainst_expand = []; Binst_expand = [];sigmas_expand = []
                for z in inst: #this is just adding in the previous values
                    for y in z['A_array']:Ainst_expand.append(y)
                    for y in z['B_array']:Binst_expand.append(y)
                    for y in z['sigma_array']:sigmas_expand.append(y)
                ''' this gives the total number of rows added '''
                print 'linear_fit| len(Ainst_expand)=',len(Ainst_expand) , ' len(Binst_expand)=',len(Binst_expand), 'len(sigmas_expand)=',len(sigmas_expand)

                #adam-old# ylength = len(Binst_expand)
                print 'linear_fit| x_length=',x_length , ' y_length=',y_length
                A = scipy.zeros([y_length,x_length])
                B = scipy.zeros(y_length)
                S = scipy.zeros(y_length)

                if attempt == 'first': rejectlist = 0*copy(B)

                Af = open('A','w')
                Bf = open('b','w')

                rejected_x = [] ; rejected_y = [] ; all_x = [] ; all_y = [] ; all_resids = []
                if attempt == 'rejected':
                    for ele in Ainst_expand:
                        if rejectlist[ele[0]] == 0:
                            if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]):
                                all_x.append(float(str(x_positions[ele[0]])))
                                all_y.append(float(str(y_positions[ele[0]])))
                                all_resids.append(float(str(resids_sign[ele[0]])))
                            Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n')
                            A[ele[0],ele[1]] = ele[2]
                        else:
                            if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]):
                                rejected_x.append(float(str(x_positions[ele[0]])))
                                rejected_y.append(float(str(y_positions[ele[0]])))
                else:
                    for ele in Ainst_expand:
                        Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n')
                        A[ele[0],ele[1]] = ele[2]

                for ele in Binst_expand:
                    if rejectlist[ele[0]] == 0:
                        B[ele[0]] = ele[1]

                for ele in sigmas_expand:
                    if rejectlist[ele[0]] == 0:
                        S[ele[0]] = ele[1]

                if attempt == 'rejected':
                    print 'linear_fit| num_rejected=',num_rejected
                    illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/'
                    print 'linear_fit| all_resids[0:20]=',all_resids[0:20]
                    os.system('mkdir -p ' + illum_dir+'/other_runs_plots/')
                    #adam-old# calcDataIllum(sample + 'reducedchi'+str(ROT)+FILTER,LENGTH1,LENGTH2,scipy.array(all_resids),scipy.ones(len(all_resids)),scipy.array(all_x),scipy.array(all_y),pth=illum_dir,rot=0,limits=[-10,10],ylab='Residual/Error')
                    plot_name='_'.join(['reducedchi',run_info,PPRUN])
                    print 'linear_fit| running calcDataIllum plot_name=',plot_name
                    fit_redchisq_clipped=calcDataIllum(plot_name,LENGTH1,LENGTH2,scipy.array(all_resids),scipy.ones(len(all_resids)),scipy.array(all_x),scipy.array(all_y),pth=illum_dir,limits=[-5,5],data_label='Fit Residual/Error') #magErr is ones here. that just ignores the errors (fine)
                    run_goodness_info[run_info]+='\nattempt='+str(attempt)+': redchisq=%.3f' % fit_redchisq_clipped
                    if num_rejected > 0:
                        dtmp = {}
                        if "try_linear-is-False" in run_info:
                            reject_plot =illum_dir + "other_runs_plots/" + '_'.join(['rejects',run_info,"pos",test.replace('_','')])+ '.png'
                        else:
                            reject_plot =illum_dir + '_'.join(['rejects',run_info,"pos",test.replace('_','')])+ '.png'
                        print "linear_fit| reject_plot=",reject_plot
                        dtmp['reject_plot']=reject_plot
                        dtmp['rejected']=num_rejected
                        dtmp['totalmeasurements']=num_rejected
                        dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,'linearfit':'1'})
                        save_fit(dtmp)

                        x_p = scipy.array(rejected_x)
                        y_p = scipy.array(rejected_y)
                        pylab.figure(figsize=(22,13.625))
                        pylab.title('Location of all of the rejected stars. Of a possible '+str(len(rejectlist))+' only '+str(num_rejected)+ ' were rejected.\n'+r'(rejected if $m_{exp}$ and $m_{model}$ differ by $>5 \sigma$ after initial starflat fit)')
                        pylab.scatter(x_p,y_p,linewidth=None)
                        pylab.xlabel('X axis')
                        pylab.ylabel('Y axis')     # label the plot
                        pylab.ylim(y_p.min(),y_p.max())
                        pylab.xlim(x_p.min(),x_p.max())
                        pylab.savefig(reject_plot)
                        pylab.clf()

                Bstr = reduce(lambda x,y:x+' '+y,[str(z[1]) for z in Binst_expand])
                Bf.write(Bstr)
                Bf.close()
                Af.close()

                print 'linear_fit| ...finished matrix...'
                print 'linear_fit| len(position_columns)=',len(position_columns) , ' len(zp_columns)=',len(zp_columns)
                print 'linear_fit|  B[0:10]=',B[0:10] , ' scipy.shape(A)=',scipy.shape(A) , ' scipy.shape(B)=',scipy.shape(B)
                print 'linear_fit|  A[0,0:10]=',A[0,0:10] , ' A[1,0:10]=',A[1,0:10]

                Bf = open(tmpdir + '/B','w')
                for i in xrange(len(B)):
                    Bf.write(str(B[i]) + '\n')
                Bf.close()

                print 'linear_fit| ...solving matrix...'
                os.system('rm -f x')
                ooo=os.system('./sparse < A')
                if ooo!=0: raise Exception("the line os.system('./sparse < A') failed\n'./sparse < A'="+'./sparse < A')

                read_x_soln = open('x','r').read()
                print 'linear_fit| len(read_x_soln)=',len(read_x_soln),' x_length=',x_length
                res_x_soln = re.split('\s+',read_x_soln[:-1])
                Traw = [float(x) for x in res_x_soln][:x_length]
                res_x_soln = re.split('\s+',read_x_soln[:-1].replace('nan','0').replace('inf','0'))
                T = [float(x) for x in res_x_soln][:x_length]
                for i in xrange(len(T)):
                    if i < len(column_names):
                        if string.find(column_names[i],'mag') == -1:
                            print 'linear_fit| column_names[i]=',column_names[i] , ' T[i]=',T[i], ' Traw[i]=',Traw[i]
                        if T[i] == -99:
                           print 'linear_fit| column_names[i]=',column_names[i] , ' T[i]=',T[i]
                    if catalog_values.has_key(i): # these values are written into 'catalog_' + PPRUN + '.cat'
                        catalog_values[i]['mag'] = T[i] # these values are written into 'catalog_' + PPRUN + '.cat'
                x_soln = scipy.array([float(x) for x in res_x_soln][:x_length])

                print 'linear_fit| ...finished solving...'

                ''' calculate reduced chi-squared value'''
                print 'linear_fit| scipy.shape(A)=',scipy.shape(A) , ' len(x_soln)=',len(x_soln) , ' x_length=',x_length , ' len(res_x_soln)=',len(res_x_soln)
                Bprime = scipy.dot(A,x_soln)
                print 'linear_fit| scipy.shape(Bprime)=',scipy.shape(Bprime) , ' scipy.shape(B)=',scipy.shape(B)

                ''' number of free parameters is the length of x_soln , number of data points is B '''
                #adam-tmp# resids_sign = (B-Bprime)*S #UNCERTAINTY_CHANGE#
                resids_sign = B-Bprime
		#adam: 1/S -> 1/S**2 requires resids in units of sigmas to change: (B-Bprime) -> (B-Bprime)*S
                resids = abs(resids_sign)
                chisq = (resids**2.).sum()
                parameters = len(B) - len(x_soln)
                reducedchi = chisq/parameters
                difference = (resids*S).sum()/len(B)

                if attempt == 'first': #rejectlist = zeros already
                    sig5_outliers= resids > 5
                    rejectlist[sig5_outliers]=1
                    num_rejected = rejectlist.sum()

                fit_str='\nSTART attempt='+attempt+' run_info='+run_info+' FIT INFO '
                fit_str+='\n'+attempt+' FIT INFO: x_soln = [float(x) for x in res_x_soln][:x_length] || Bprime = scipy.dot(A,x_soln) || resids = abs(B-Bprime)'
                fit_str+='\n'+attempt+' FIT INFO: (resids==0).sum()=%s' % ((resids==0).sum())
                fit_str+='\n'+attempt+' FIT INFO: (resids!=0).sum()=%s' % ((resids!=0).sum())
                fit_str+='\n'+attempt+' FIT INFO: resids.mean()=%.3f' % (resids.mean())
                fit_str+='\n'+attempt+' FIT INFO: len(resids)=%s num_rejected=%s' % (len(resids),num_rejected)
                fit_str+='\n'+attempt+' FIT INFO: sample_size=%s try_linear=%s' % (sample_size , try_linear)
                fit_str+='\n'+attempt+' FIT INFO: (B-Bprime)[:20]=%s' % (resids_sign[:20])
                fit_str+='\n'+attempt+' FIT INFO: x_soln[0:20]=%s' % (x_soln[0:20])
                fit_str+='\n'+attempt+' FIT INFO: read_x_soln[0:20]=%s' % (read_x_soln[0:20])
                fit_str+='\n'+attempt+' FIT INFO: chisq=%s %s' % (chisq,' (= ((B-Bprime)**2.).sum() )')
                fit_str+='\n'+attempt+' FIT INFO: parameters=%s %s' % (parameters , " (= len(B) - len(x_soln) )")
                fit_str+='\n'+attempt+' FIT INFO: difference=%s %s' % (difference," (= abs((B-Bprime)*S).sum()/len(B)")#adam: 1/S -> 1/S**2 requires resids*S -> resids*S**2 below
                fit_str+='\n'+attempt+' FIT INFO: reducedchi=%s %s' % ( reducedchi, ' (= ((B-Bprime)**2.).sum()/(len(B) - len(x_soln)) = reduced chi-squared)')
                fit_str+='\nEND   attempt='+attempt+' run_info=%s' % (run_info,)+' FIT INFO '
                print fit_str
                if attempt!='first':
                        run_goodness_info[run_info]+='\n'+attempt+' FIT INFO: (resids==0).sum()=%s' % ((resids==0).sum()) +' len(resids)=%s num_rejected=%s' % (len(resids),num_rejected)
                        run_goodness_info[run_info]+='\n'+attempt+' FIT INFO: resids.mean()=%.3f' % (resids.mean())
                        run_goodness_info[run_info]+='\n'+attempt+' FIT INFO: reducedchi=%s %s' % ( reducedchi, ' (= ((B-Bprime)**2.).sum()/(len(B) - len(x_soln)) = reduced chi-squared)')
                        run_goodness_info[run_info]+='\n'+attempt+' FIT INFO: parameters=%s %s' % (parameters , " (= len(B) - len(x_soln) )")
                #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'reducedchi$'+sample+'$'+sample_size:reducedchi})
                #adam-END#UNCERTAINTY_CHANGE# weight by 1/sigma**2, not 1/sigma

                #adam-del#position_fit = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
                ''' save fit information '''
                if match: save_columns = position_columns + zp_columns + color_columns
                else: save_columns = position_columns + zp_columns

                fitvars = {} ;dtmp = {}
                zp_images = ''
                zp_images_names = ''
                for ele in save_columns:
                    #adam-del# res = re.split('$',ele['name'])
                    ''' save to own column if not an image zeropoint '''
                    if string.find(ele['name'],'zp_image') == -1:
                        fitvars[ele['name']] = x_soln[ele['index']]
                        term_name = ele['name']
                        dtmp[term_name]=fitvars[ele['name']]
                    else:
                        zp_images += str(x_soln[ele['index']]) + ','
                        zp_images_names += ele['name'] + ','

                zp_images = zp_images[:-1] ; zp_images_names = zp_images_names[:-1]
                dtmp["zp_images"]=zp_images
                dtmp["zp_images_names"]=zp_images_names
                print 'linear_fit| save_columns=', save_columns,
                print 'linear_fit| zp_columns=', zp_columns
                print 'linear_fit| dtmp[zp_images]=',dtmp["zp_images"]
                print 'linear_fit| dtmp[zp_images_names]=',dtmp["zp_images_names"]
                use_columns = filter(lambda x: string.find(x,'zp_image') == -1,[z['name'] for z in save_columns] ) + ['zp_images','zp_images_names']

                positioncolumns = reduce(lambda x,y: x+','+y,use_columns)
                print 'linear_fit| positioncolumns=',positioncolumns
                #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$positioncolumns':positioncolumns})
                dtmp['positioncolumns'] = positioncolumns
                dtmp[attempt + 'reducedchi']=reducedchi
                dtmp[attempt + 'difference']=difference
                dtmp[attempt + 'chisq']= chisq
                dtmp[attempt + 'parameters']= parameters
                #adam-fragments_removed# linear_fit-term_name (this was commented out to begin with)

                print 'linear_fit| dtmp.keys()=',dtmp.keys()
                print 'linear_fit| PPRUN=',PPRUN , ' FILTER=',FILTER , ' OBJNAME=',OBJNAME , ' dtmp["positioncolumns"]=',dtmp["positioncolumns"]
                dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,'linearfit':'1'})
                save_fit(dtmp)
                print 'linear_fit| ...done with attempt=',attempt,'...'
            ''' end loop over attempt=['first','reject'] '''
            '''### MAIN3-END ### DO FITTING'''

            '''### MAIN4-START ### SAVE CATALOGS/FITS/PLOTS'''
            ''' save the corrected catalog '''
            cols = [] ; stdMag_corr = [] ; stdMagErr_corr = [] ; stdMagColor_corr = [] ; stdMagClean_corr = [] ; ALPHA_J2000 = [] ; DELTA_J2000 = [] ; SeqNr = [] ; Star_corr = []
            sn = -1
            for i in catalog_values.keys():
                entr = catalog_values[i]
                sn += 1
                SeqNr.append(sn)
                stdMag_corr.append(entr['mag'])
                ALPHA_J2000.append(entr['ra'])
                DELTA_J2000.append(entr['dec'])
                stdMagErr_corr.append(entr['sigma'])
                stdMagColor_corr.append(0)
                stdMagClean_corr.append(1)
                Star_corr.append(1)

            cols.append(pyfits.Column(name='stdMag_corr', format='D',array=scipy.array(stdMag_corr)))
            cols.append(pyfits.Column(name='stdMagErr_corr', format='D',array=scipy.array(stdMagErr_corr)))
            cols.append(pyfits.Column(name='stdMagColor_corr', format='D',array=scipy.array(stdMagColor_corr)))
            cols.append(pyfits.Column(name='stdMagClean_corr', format='D',array=scipy.array(stdMagClean_corr)))
            cols.append(pyfits.Column(name='ALPHA_J2000', format='D',array=scipy.array(ALPHA_J2000)))
            cols.append(pyfits.Column(name='DELTA_J2000', format='D',array=scipy.array(DELTA_J2000)))
            cols.append(pyfits.Column(name='SeqNr', format='E',array=scipy.array(SeqNr)))
            cols.append(pyfits.Column(name='Star_corr', format='E',array=scipy.array(Star_corr)))

            outcat = data_path + 'PHOTOMETRY/ILLUMINATION/' + 'catalog_' + PPRUN + '.cat'
            #adam-watch# do these catalogs get used anywhere else?
            hdu = pyfits.PrimaryHDU()
            hdulist = pyfits.HDUList([hdu])
            tbhu = pyfits.BinTableHDU.from_columns(cols)
            hdulist.append(tbhu)
            hdulist[1].header.update(EXTNAME='OBJECTS')
            hdulist.writeto( outcat ,overwrite=True)
            catalog_save_name=data_path + 'PHOTOMETRY/ILLUMINATION/'+'_'.join(['catalog',run_info,PPRUN]) + '.cat'
            os.system('cp %s %s' % ( outcat , catalog_save_name))
            print 'linear_fit| wrote out new cat! outcat=',outcat
            print 'linear_fit| wrote out new cat! catalog_save_name=',catalog_save_name

            save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'format':'good','sample':'record','sample_size':'record'},db='' + test + 'try_db')

            save_fit({'FILTER':FILTER,'OBJNAME':OBJNAME,'PPRUN':PPRUN,'sample':sample,'sample_size':sample_size,'catalog':outcat})

            ''' make diagnostic IC fits images'''
            if string.find(sample_size,'rand') == -1:
                d = get_fits(OBJNAME,FILTER,PPRUN, sample, sample_size)
                print 'linear_fit| d.keys()=',d.keys()
                column_prefix = '' #sample+'$'+sample_size+'$'
                position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns'])
                print 'linear_fit| position_columns_names=',position_columns_names
                fitvars = {}
                #adam-ask# why is there a need to mess with the cheby_terms_use dict here? Is it to keep a consistent match btwn what goes in fitvars and is used for calc_illum=False runs?
                cheby_terms_dict = {}
                for ele in position_columns_names:
                    if type(ele) != type({}):
                        ele = {'name':ele}
                    #adam-del#res = re.split('$',ele['name'])
                    if string.find(ele['name'],'zp_image') == -1:
                        fitvars[ele['name']] = float(d[ele['name']])
                        for term in cheby_terms:
                            if term['n'] == ele['name'][2:]:
                                cheby_terms_dict[term['n']] = term

                zp_images = re.split(',',d['zp_images'])
                zp_images_names = re.split(',',d['zp_images_names'])

                for i in xrange(len(zp_images)): fitvars[zp_images_names[i]] = float(zp_images[i])

                print 'linear_fit| fitvars=',fitvars
                fitvars_runs[run_info]=fitvars

                cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]
                print 'linear_fit| cheby_terms_use=',cheby_terms_use

                ''' make images of illumination corrections '''
                if calc_illum:
                    '''### MAIN4a-START ### MAKE FITS FILES of IC and IC_no_chip_zp and save fits (if calc_illum and "rand" not in sample_size)'''
                    size_x=LENGTH1;size_y=LENGTH2
                    bin=100
                    xA,yA = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin),indexing='ij')
                    xA = coord_conv_x(xA);yA = coord_conv_y(yA)
                    for ROT in EXPS.keys():
                        print "linear_fit| loop2-(3/3) plots the fit | for ROT =",ROT, " in EXPS.keys()=",EXPS.keys()
                        illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT) + '/'
		        os.system('mkdir -p ' + illum_dir+'/other_runs_plots/')

                        epsilonA = 0
                        for term in cheby_terms_use:
                            print 'linear_fit| ROT=',ROT , ' term["n"]=',term["n"] , ' fitvars[str(ROT)+"$"+term["n"]]=',fitvars[str(ROT)+"$"+term["n"]]
                            epsilonA += fitvars[str(ROT)+'$'+term['n']]*term['fx'](xA,yA)*term['fy'](xA,yA) #this part makes `epsilonA` a grid

                        ''' save pattern w/o chip zps '''
                        #adam-old#im = illum_dir + '/nochipzps' + sample + sample_size +  test + '.fits'
                        im = illum_dir + '_'.join([ '/nochipzps' , run_info,'ROT'+str(ROT),  test.replace('_','')]) + '.fits'
                        print "linear_fit| ...writing...im=",im
                        hdu = pyfits.PrimaryHDU(epsilonA.T)
                        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,str(ROT)+'$im':im})
                        hdu.writeto(im,overwrite=True)

                        print 'linear_fit| scipy.shape(epsilonA)=',scipy.shape(epsilonA), ' bin=',bin
                        ''' save pattern w/ chip zps '''
                        if per_chip or same_chips:
                            print 'linear_fit| CHIPS=',CHIPS
                            for CHIP in CHIPS:
                                if str(dt['CRPIX1_' + str(CHIP)]) != 'None':
                                    #adam-fragments_removed# linear_fit-fit_readout_ports #this would be usefull if you wanted to have the IC treat each individual readout port in each CCD (unnecessary)
                                    #pp='CRPIX1ZERO'+'=%s\t'+'CRPIX1_'+str(CHIP)+'=%s\t'+'NAXIS1_'+str(CHIP)+'=%s\t'+'CRPIX2ZERO'+'=%s\t'+'CRPIX2_'+str(CHIP)+'=%s\t'+'NAXIS2_'+str(CHIP)+'=%s'
                                    #print pp % (float(dt['CRPIX1ZERO']) , float(dt['CRPIX1_' + str(CHIP)]) ,float(dt['NAXIS1_' + str(CHIP)]) , float(dt['CRPIX2ZERO']) , float(dt['CRPIX2_' + str(CHIP)]) ,float(dt['NAXIS2_' + str(CHIP)]))
                                    xmin = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)])
                                    xmax = xmin + float(dt['NAXIS1_' + str(CHIP)])
                                    ymin = float(dt['CRPIX2ZERO']) - float(dt['CRPIX2_' + str(CHIP)])
                                    ymax = ymin + float(dt['NAXIS2_' + str(CHIP)])
                                    X0,X1,Y0,Y1=int(xmin/bin),int(xmax/bin) ,int(ymin/bin) ,int(ymax/bin)
                                    print 'linear_fit|CHIP=',CHIP,' xmin=',xmin , ' xmax=',xmax , ' ymin=',ymin , ' ymax=',ymax
                                    print 'linear_fit|CHIP=%s [X0:X1,Y0:Y1]=[%s:%s,%s:%s] epsilonA[X0:X1,Y0:Y1].shape=%s' % (CHIP,X0,X1,Y0,Y1,epsilonA[X0:X1,Y0:Y1].shape)
				    print 'linear_fit|CHIP=',CHIP,' zp:', fitvars['zp_' + str(CHIP)]
                                    epsilonA[X0:X1,Y0:Y1]+= float(fitvars['zp_' + str(CHIP)])

                        #adam-old#im = illum_dir + '/correction' + sample + sample_size +  test + '.fits'
                        im = illum_dir + '_'.join([ '/correction' , run_info,'ROT'+str(ROT),  test.replace('_','')]) + '.fits'
                        print 'linear_fit| ...writing...im=',im
                        hdu = pyfits.PrimaryHDU(epsilonA.T) #the transpose makes it consistent with the old versions shape, but I prefer this way of indexing so that you don't have to flip X and Y around and other confusing stuff
                        save_fit({'linearplot':1,'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,str(ROT)+'$im':im})
                        hdu.writeto(im,overwrite=True)
                        print 'linear_fit| done'
                    '''### MAIN4a-END ### MAKE FITS FILES of IC and IC_no_chip_zp and save fits (if calc_illum and "rand" not in sample_size)'''

            ''' don't make these plots if it's a random run '''
            if match and sample != 'None' and string.find(sample_size,'rand') == -1:
                '''### MAIN4b-START ### MAKE nocorrected_data PLOTS with calcDataIllum (if sample != 'None' and "rand" not in sample_size)'''
                ''' calculate matched plot differences, before and after '''
                for ROT in EXPS.keys():
                    data[ROT] = scipy.array(data[ROT]) # value - tab['SDSSstdMag_corr'] (  if calc_illum or ('uncorr' in sample_size): value = MAG_AUTO     elif not calc_illum: value = MAG_AUTO - epsilon_cheby_chip  )
                    Star[ROT] = scipy.array(Star[ROT]) # tab['SDSSStar_corr']
                    magErr[ROT] = scipy.array(magErr[ROT]) # tab['SDSSstdMagErr_corr']
                    X[ROT] = scipy.array(X[ROT]) # tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS']
                    Y[ROT] = scipy.array(Y[ROT]) # tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS']
                    color[ROT] = scipy.array(color[ROT]) # tab['SDSSstdMagColor_corr']
                    print 'linear_fit| ROT=',ROT, ' data[ROT]=',data[ROT]

                    #adam-note# Properly apply corrections with: diff_Pcat_Pcolor_Mexp_Mchip_Mcheby
                    ''' apply the color term measured from the data '''
                    print 'linear_fit| fitvars["SDSS_color"]=',fitvars["SDSS_color"] , ' color[ROT]=',color[ROT]
                    #adam-old# data1 = data[ROT] + fitvars['SDSS_color']*color[ROT] - zp_image_correction # Definitely Pcolor that's right!

                    ''' correct using the SDSS magnitudes from SDSS_color and zp_SDSS '''
                    data1 = data[ROT] + fitvars['SDSS_color']*color[ROT] # Definitely Pcolor that's right!
                    if fitvars.has_key('zp_SDSS'):
                            data1+=fitvars['zp_SDSS']

                    print 'linear_fit| len(data1)=',len(data1) , ' len(data[ROT])=',len(data[ROT]) , ' match=',match , ' sample=',sample
                    illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT) + '/'
                    for kind,keyvalue in [['star',1]]: #['galaxy',0],

                        #adam-old# data2 = data1 - scipy.median(data1)
                        #adam-old#calcim=sample + kind + 'nocorr'+str(ROT)+FILTER
                        calcim = '_'.join([sample,kind,'nocorrected_data','ROT'+str(ROT),FILTER,run_info])
                        #adam-ask# WHY aren't we using the true values of LENGTH1 and LENGTH2 here instead of 10000,8000? (p.s. I changed how the array is setup (x_val and y_val) in calcDataIllum! I think this is right now, shouldn't hit that except anymore)
                        #adam-old# calcDataIllum(calcim,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=ROT,good=[Star[ROT],keyvalue])
                        #adam-watch#if not calc_illum:                        data1 = MAG_AUTO + fitvars['SDSS_color']*color[ROT] - tab['SDSSstdMag_corr'] - epsilon_cheby_chip  #(epsilon_cheby_chip=C(x,y,chip,rot) in paper)
                        #adam-watch#if not calc_illum: (maybe should be:      data1 = MAG_AUTO + fitvars['SDSS_color']*color[ROT] - zp_image_correction - tab['SDSSstdMag_corr'] - epsilon_cheby_chip ) #(epsilon_cheby_chip=C(x,y,chip,rot) in paper)
                        calcDataIllum(calcim,LENGTH1,LENGTH2,data1,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,good=[Star[ROT],keyvalue],limits=[-0.5,0.5],data_label="(Raw Measured Mag) - (Corrected SDSS Mag)" )
                        #adam-note# Mexp: subtract the zp_exp for each exposure
                        zp_image_correction = scipy.array([float(fitvars['zp_image_'+thisimage]) for thisimage in whichimage[ROT]])
                        data2=data1-zp_image_correction
                        calcim = '_'.join([sample,kind,'no_pos-corrected_data','ROT'+str(ROT),FILTER,run_info])
                        calcDataIllum(calcim,LENGTH1,LENGTH2,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,good=[Star[ROT],keyvalue],limits=[-0.5,0.5],data_label="(Raw Measured Mag) - (Corrected SDSS Mag)" )
                        dtmp = {}
                        var = variance(data2,magErr[ROT])
                        print 'linear_fit| var=',var
                        dtmp[sample + 'stdnocorr$' + str(ROT)] = var[1]**0.5
                        dtmp[sample + 'redchinocorr$' + str(ROT)] = var[2]
                        dtmp[sample + 'pointsnocorr$' + str(ROT)] = len(data2)
                        print 'linear_fit| sample+"redchinocorr$"+str(ROT)=',sample+"redchinocorr$"+str(ROT)

                        if calc_illum:
                            '''### MAIN4c-START ### MAKE corrected_data AND correction PLOTS with calcDataIllum (if calcIllum and sample != 'None' and "rand" not in sample_size)'''
                            #plot_color(color[ROT], data2)
                            x = coord_conv_x(X[ROT])
                            y = coord_conv_y(Y[ROT])

                            epsilonB=scipy.zeros(data1.shape) #adam-note# epsilonB is the Mexp_Mchip_Mcheby part
                            epsilonB += zp_image_correction

                            #adam-note# Mchip: subtract the zp_chip for the proper chip number that each star was identified with
                            zp_chip_correction = []
                            for chip in chipnums[ROT]:
                                zp_chip_correction.append(fitvars['zp_' + str(int(float(chip)))])
                            zp_chip_correction = scipy.array(zp_chip_correction)
                            epsilonB += zp_chip_correction

                            #adam-note# Mcheby: subtract the f(x,y)_rot poly based on the (x,y) position where each star was located
                            for term in cheby_terms_use:
                                epsilonB += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

                            #adam-fragments_removed# try_linear-config_based_zp_chip_correct

                            data1 -= epsilonB
                            #adam-note# data1 = MAG_AUTO - tab['SDSSstdMag_corr'] + fitvars['SDSS_color']*color[ROT] + fitvars['zp_SDSS'] - zp_image_correction - zp_chip_correction - fitvars[str(ROT)+'$'+cheby_term['n']]*cheby_term['fx'](x,y)*cheby_term['fy'](x,y)

                            '''plot the epsilonB=Mexp_Mchip_Mcheby correction'''
                            #adam-old#calcim = sample+kind+'correction'+str(ROT)+FILTER
                            calcim1 = '_'.join([sample,kind,'correction','ROT'+str(ROT),FILTER,run_info]) #adam-possible problem
                            #adam-old# WHY aren't we using the true values of LENGTH1 and LENGTH2 here instead of 10000,8000? (p.s. I changed how the array is setup (x_val and y_val) in calcDataIllum! I think this is right now, shouldn't hit that except anymore)
                            #adam-old# calcDataIllum(calcim1,10000,8000,epsilonB,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=ROT,good=[Star[ROT],keyvalue])
                            calcDataIllum(calcim1,LENGTH1,LENGTH2,epsilonB,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,good=[Star[ROT],keyvalue],limits=[-0.5,0.5],data_label="epsilon: (IC-corrected Measured Mag) - (Measured Mag)" )

                            #adam-old# #plot_color(color[ROT], data2)
                            #adam-old#data2 -= epsilonB

                            '''plot the corrected magnitudes data1=diff_Pcat_Pcolor_Mexp_Mchip_Mcheby correction'''
                            #adam-old#calcim = sample+kind+'rot'+str(ROT)+FILTER
                            calcim2 = '_'.join([sample,kind,'corrected_data','ROT'+str(ROT),FILTER,run_info])
                            #adam-old# WHY aren't we using the true values of LENGTH1 and LENGTH2 here instead of 10000,8000? (p.s. I changed how the array is setup (x_val and y_val) in calcDataIllum! I think this is right now, shouldn't hit that except anymore)
                            #adam-old# calcDataIllum(calcim2,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=ROT,good=[Star[ROT],keyvalue])
                            fit_redchisq_clipped=calcDataIllum(calcim2,LENGTH1,LENGTH2,data1,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,good=[Star[ROT],keyvalue],limits=[-0.5,0.5],data_label="(IC-corrected Measured Mag) - (SDSS Mag)" )
                            run_goodness_info[run_info]+='\nROT='+str(ROT)+': redchisq=%.3f' % fit_redchisq_clipped

                            var = variance(data1,magErr[ROT])
                            print 'linear_fit| second: var=' , var
                            dtmp[sample + 'stdcorr$' + str(ROT)] = var[1]**0.5
                            dtmp[sample + 'redchicorr$' + str(ROT)] = var[2]
                            dtmp[sample + 'pointsnocorr$' + str(ROT)] = len(data1)
                            #adam-no_more# ns.update(locals())
                            #adam-no_more# adam_tmp_plots(*ns)
                            run_goodness_info[run_info]+= '\nROT='+str(ROT)+': variance=%.2f weight_variance=%.2f redchi=%.3f' % var
                            '''### MAIN4c-END   ### MAKE corrected_data AND correction PLOTS with calcDataIllum (if calcIllum and sample != 'None' and "rand" not in sample_size)'''

                        dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size})
                        save_fit(dtmp)
                '''### MAIN4b-END  ### MAKE nocorrected_data PLOTS with calcDataIllum (if sample != 'None' and "rand" not in sample_size)'''

            '''### MAIN4-END ### SAVE CATALOGS/FITS/PLOTS'''
            #run_goodness_info[run_info]= run_goodness_info[run_info].replace('\n',' (adam-look)\nlinear_fit| run_info=%86s ' % (run_info))+ " (adam-look)"
            #run_goodness_info[run_info]= run_goodness_info[run_info].replace('\n',' (adam-look)\n%86s : ' % (run_info))+ " (adam-look)"
            run_goodness_info[run_info]= run_goodness_info[run_info].replace('\n',' \n%86s : ' % (run_info))+ " "

            #adam-no_more# ns.update(locals())
            #adam-no_more# break
	if original_sample_size=="all":
            #for run_info in run_infos: print '\n\n'+run_goodness_info[run_info]
            goodness_runs_info_str='\n\n### How good are the stars and the matching with SDSS/rotations? ### PPRUN: %s\n\n' % (PPRUN)
            goodness_runs_info_str+=run_goodness_info["stars"]
            goodness_runs_info_str+='\n\n### How good did the fits perform? How was the chi-squared for each run? ### PPRUN: %s\n\n' % (PPRUN)
            for run_info in run_infos: goodness_runs_info_str+='\n\n'+run_goodness_info[run_info]
            adam_str=adam_fit_goodness(fitvars_runs,run_infos,data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/',PPRUN,goodness_runs_info_str)
            adam_str= adam_str.replace('\n',' (adam-look)\n')+ " (adam-look)\n"
            print adam_str

    #adam-no_more# ns.update(locals())
    print "linear_fit| DONE with func\n"
    return

table_zps_runs_new=1
def adam_fit_goodness(fitvars_runs,run_infos,illum_dir,PPRUN,extra_str=''):
    chip_keys=['zp_1','zp_2','zp_3','zp_4','zp_5','zp_6','zp_7','zp_8','zp_9','zp_10']
    ss=set()
    run_maxlen=0
    for run_info in run_infos:
        ss.update(set(fitvars_runs[run_info].keys()))
        if len(run_info)>run_maxlen:run_maxlen=len(run_info)

    zp_keys=numpy.array(list(ss))
    cheby0_zps=zp_keys[numpy.array(map(lambda x: x.startswith('0'),zp_keys))]
    cheby1_zps=zp_keys[numpy.array(map(lambda x: x.startswith('1'),zp_keys))]
    sdss_zps=zp_keys[numpy.array(map(lambda x: 'SDSS' in x,zp_keys))]
    image_zps=zp_keys[numpy.array(map(lambda x: 'image' in x,zp_keys))]
    chip_zps=zp_keys[numpy.array(map(lambda x: x in chip_keys,zp_keys))]
    sdss_zps.sort();image_zps.sort();chip_zps.sort();cheby1_zps.sort();cheby0_zps.sort()
    header_keys=sdss_zps.tolist()+image_zps.tolist()+chip_zps.tolist()+cheby1_zps.tolist()+cheby0_zps.tolist()
    header_lengths=numpy.array([len(k)+1 for k in header_keys])
    lt9=header_lengths<9
    header_lengths[lt9]=9

    header_str=''
    for length,key in zip(header_lengths,header_keys):
        header_str+=("%"+str(length)+"s") % (key)

    total_str=[header_str]+[""]*len(run_infos)
    for i,run_info in enumerate(run_infos):
        for length,key in zip(header_lengths,header_keys):
            fv=fitvars_runs[run_info]
            if fv.has_key(key):
                total_str[i+1]+= ("%"+str(length)+"s") % ("%.5f" % (fv[key]))
            else:
                total_str[i+1]+= ("%"+str(length)+"s") % ("NaN")

    table_str= '\n### best-fit ZP values ### PPRUN: %s\n\n' % (PPRUN)
    table_str+='columns correspond to the following runs:\n'+'\n'.join(run_infos)+'\n'+'\n'.join(total_str)
    table_str+=extra_str
    #print table_str
    global table_zps_runs_new
    if table_zps_runs_new==1:
        fl_table_zps_runs=open('table_zps_runs.txt','w')
        fl_table_zps_runs.write(table_str)
        table_zps_runs_new=0
        fl_table_zps_runs.close()
    else:
        fl_table_zps_runs=open('table_zps_runs.txt','a+')
        fl_table_zps_runs.write('\n##### NEW PPRUN ##### PPRUN=%s ##### NEW PPRUN #####\n')
        fl_table_zps_runs.write(table_str)
        fl_table_zps_runs.close()
    fl=open(illum_dir+'table_zps_runs.txt','w')
    fl.write(table_str)
    fl.close()
    return table_str

'''adam: just coppied from calc_test_save. #adam-Warning#: it has the comment "this is not quite right" in it'''
def variance(data,err): #simple #step3_run_fit
    d = 0
    w = 0
    for i in xrange(len(data)):
        w += 1/err[i]**2.
        d += data[i]/err[i]**2.
    mean = d/w

    w = 0
    d = 0
    for i in xrange(len(data)):
        w += 1/err[i]**2.
        d += 1/err[i]**2.*(data[i] - mean)**2.

    weight_variance = d/w
    variance = scipy.var(data)

    n = 0
    d = 0
    for i in xrange(len(data)):
        n += 1.
        d += ((data[i] - mean)/err[i])**2.

    ''' this is not quite right '''
    redchi = d/n
    print 'variance| variance=',variance , ' weight_variance=',weight_variance , ' redchi=',redchi
    return variance, weight_variance, redchi

#adam-fragments_removed# calcDataIllum-old
def calcDataIllum(output_files_nametag, LENGTH1, LENGTH2, data,magErr, X, Y, pth, good=None, limits=[-0.4,0.4], data_label='SUBARU-SDSS', make_pickle=False):
    '''inputs: output_files_nametag, LENGTH1, LENGTH2, data,magErr, X, Y, pth, good=None, limits=[-0.4,0.4], data_label='SUBARU-SDSS'
    parameters: pth: path to dir where plots will be placed
    returns:
    calls:
    called_by: linear_fit,linear_fit,linear_fit,linear_fit'''

    #output_files_nametag+="_8bins" #adam-no_more#8bins
    output_files_nametag+="_15bins"
    print '\ncalcDataIllum| START the func. inputs: output_files_nametag=',output_files_nametag , ' LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2 , ' data=',data , ' magErr=',magErr , ' X=',X , ' Y=',Y , ' pth=',pth , ' good=',good , ' limits=',limits , ' data_label=',data_label

    if "try_linear-is-False" in output_files_nametag:
	    pth+="/other_runs_plots/"
    f = pth + output_files_nametag + '.pickle'
    if make_pickle:
	    calcDataIllum_info = {'file':output_files_nametag, 'LENGTH1':LENGTH1, 'LENGTH2': LENGTH2, 'data': data, 'magErr':magErr, 'X':X, 'Y':Y, 'pth':pth, 'good':good, 'limits':limits, 'data_label':data_label}
	    output = open(f,'wb')
	    pickle.dump(calcDataIllum_info,output)
	    output.close()

    nbin1 =15 ; nbin2 =15
    #nbin1 =8 ; nbin2 =8 #adam-no_more#8bins
    bin1 = LENGTH1/float(nbin1) ; bin2 = LENGTH2/float(nbin2) #adam-watch# changed this! I think this is right now, shouldn't hit that except anymore
    diff_weightsum = -9999*numpy.ones([nbin1,nbin2]) ; diff_invvar = -9999*numpy.ones([nbin1,nbin2]) ; diff_X = -9999*numpy.ones([nbin1,nbin2]) ; diff_Y = -9999*numpy.ones([nbin1,nbin2])
    X_cen = [];Y_cen = [];data_cen = []#;zerr_cen = []

    chisq = 0
    clipped_chisq = 0
    for i in xrange(len(data)):
        if good is not None:
            use = good[0][i] == good[1]
        else:
            use = True
        if use:
            #if 1: # LENGTH1*0.3 < X[i] < LENGTH1*0.6:
            X_cen.append(X[i]) ; Y_cen.append(Y[i]) ; data_cen.append(data[i]) #; zerr_cen.append(magErr[i])
            chisq += data[i]**2./magErr[i]**2.
            err = magErr[i]
            ''' lower limit on error '''
	    if err < 0.04: err = 0.04 #adam-ask# sigma lower limit: here if err < 0.04: err = 0.04
            clipped_chisq += data[i]**2./err**2.
            weightsum = data[i]/err**2.
            weightX = X[i]/err**2.
            weightY = Y[i]/err**2.
            invvar = 1/err**2.

            x_val = int(X[i]/bin1);y_val = int(Y[i]/bin2) #adam-watch# changed this! I think this is right now, shouldn't hit that except anymore
            #if 1: #0 <= x_val and x_val < int(nbin1) and y_val >= 0 and y_val < int(nbin2):  #0 < x_val < size_x/bin and 0 < y_val < size_y/bin:
            try:
                if diff_weightsum[x_val][y_val] == -9999:
                    diff_weightsum[x_val][y_val] = weightsum
                    diff_invvar[x_val][y_val] = invvar
                    diff_X[x_val][y_val] = weightX
                    diff_Y[x_val][y_val] = weightY
                else:
                    diff_weightsum[x_val][y_val] += weightsum
                    diff_invvar[x_val][y_val] += invvar
                    diff_X[x_val][y_val] += weightX
                    diff_Y[x_val][y_val] += weightY
            except:
                    print 'calcDataIllum| (adam-look) failure where diff_weightsum[x_val][y_val] is an index error: i=',i , ' x_val=',x_val , ' y_val=',y_val

    redchisq = numpy.sqrt(chisq) / len(data)
    clipped_redchisq  = numpy.sqrt(clipped_chisq) / len(data)
    print 'calcDataIllum| redchisq=', redchisq,' clipped_redchisq=', clipped_redchisq

    x_p = scipy.array(X_cen)
    y_p = scipy.array(Y_cen)
    data_p = scipy.array(data_cen)
    #data_err_p = scipy.array(zerr_cen)
    x_extrema = (x_p.min(),x_p.max()) ;y_extrema = (y_p.min(),y_p.max())

    #diff_invvar=sum(1/err[1]**2 + 1/err[2]**2 + ... + 1/err[N]**2)
    #diff_weightsum=sum(data[1]/err[1]**2 + data[2]/err[2]**2 + ... + data[N]/err[N]**2)
    #diff_X=sum(X[1]/err[1]**2 + X[2]/err[2]**2 + ... + X[N]/err[N]**2)
    #diff_Y=sum(Y[1]/err[1]**2 + Y[2]/err[2]**2 + ... + Y[N]/err[N]**2)
    mean = diff_weightsum/diff_invvar # mean = (data[1]/err[1]**2 + data[2]/err[2]**2 + ... + data[N]/err[N]**2) / (1/err[1]**2 + 1/err[2]**2 + ... + 1/err[N]**2)
    err = 1/diff_invvar**0.5 # err = 1 / sqrt(1/err[1]**2 + 1/err[2]**2 + ... + 1/err[N]**2)

    f = pth + output_files_nametag
    print 'calcDataIllum| ...writing...'
    print 'calcDataIllum| f=',f
    hdu = pyfits.PrimaryHDU(mean)
    diffmap_fits_name= f + '_diff_mean.fits'
    hdu.writeto(diffmap_fits_name,overwrite=True)
    hdu = pyfits.PrimaryHDU(err)
    diffinvvar_fits_name= f + '_diff_err.fits'
    hdu.writeto(diffinvvar_fits_name,overwrite=True)

    ''' now make cuts with binned data '''
    mean_flat = scipy.array(mean.flatten(1))
    err_flat = scipy.array(err.flatten(1))
    mean_X = scipy.array((diff_X/diff_invvar).flatten(1))
    mean_Y = scipy.array((diff_Y/diff_invvar).flatten(1))

    '''set pylab parameters'''
    params = {'backend' : 'ps', 'text.usetex' : True, 'ps.usedistiller' : 'xpdf', 'ps.distiller.res' : 6000}
    pylab.rcParams.update(params)
    fig_size = [20,13]
    params = {'axes.labelsize' : 16, 'text.fontsize' : 16, 'legend.fontsize' : 16, 'xtick.labelsize' : 12, 'ytick.labelsize' : 12, 'figure.figsize' : fig_size}
    pylab.rcParams.update(params)

    diffbinned_png_name= f + '_diffbinned_' + test.replace('_','') + '.png'
    pylab.clf()
    pylab.subplot(211)
    pylab.title(r'$\chi^{2}_{clipped}/dof=%.3f$ $\chi^{2}_{clipped}=%.1f$' % (clipped_redchisq,clipped_chisq))
    pylab.xlabel('X axis')
    pylab.ylabel(data_label)
    #pylab.scatter(mean_X,mean_flat,linewidth=0)
    pylab.scatter(x_p,data_p,linewidth=0,marker='.',color='k')
    pylab.errorbar(mean_X,mean_flat,err_flat,marker='o',lw=0.0,elinewidth=0.5,color='r')
    pylab.ylim(limits)
    pylab.xlim(x_extrema[0],x_extrema[-1])
    pylab.grid(axis='y')
    pylab.subplot(212)
    #pylab.scatter(mean_Y,mean_flat,linewidth=0)
    pylab.scatter(y_p,data_p,linewidth=0,marker='.',color='k')
    pylab.errorbar(mean_Y,mean_flat,err_flat,lw=0.0,elinewidth=0.5,marker='o',color='r')
    pylab.ylim(limits)
    pylab.xlim(y_extrema[0],y_extrema[-1])
    pylab.xlabel('Y axis')
    pylab.ylabel(data_label)     # label the plot
    pylab.grid(axis='y')
    pylab.suptitle(r'diffbinned: the data (%s) has been binned up in X and Y with appropriate mean and uncertainty for each bin plotted here' % (data_label))
    pylab.savefig(diffbinned_png_name)
    pylab.clf()
    print 'calcDataIllum| finished: diffbinned_png_name=',diffbinned_png_name

    pos_png_name= f + '_pos_' + test.replace('_','') + '.png'
    pylab.scatter(x_p,y_p,linewidth=0)
    pylab.xlabel('X axis')
    pylab.ylabel('Y axis')     # label the plot
    pylab.ylim(y_extrema[0],y_extrema[-1])
    pylab.xlim(x_extrema[0],x_extrema[-1])
    pylab.grid(axis='both')
    pylab.suptitle(r'pos: the positions of the image/SDSS matched detections are shown here')
    pylab.savefig(pos_png_name)
    pylab.clf()
    print 'calcDataIllum| finished: pos_png_name=',pos_png_name

    #adam-fragments_removed# calcDataIllum-diff_png
    print "calcDataIllum| DONE with func\n"
    return clipped_redchisq

def get_fits(OBJNAME,FILTER,PPRUN,sample, sample_size):
    '''inputs: OBJNAME,FILTER,PPRUN,sample, sample_size
    returns:  dtop
    calls: connect_except,describe_db
    called_by: linear_fit'''

    #print 'get_fits| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' sample=',sample , ' sample_size=',sample_size
    db2,c = connect_except()

    command="SELECT * from " + test + "fit_db where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and sample='" + str(sample) + "' and sample_size='" + str(sample_size) + "'"
    #print 'get_fits| command=',command
    c.execute(command)
    results=c.fetchall()
    db_keys = describe_db(c,'' + test + 'fit_db')
    dtop = {}
    for line in results:
        for i in xrange(len(db_keys)):
            dtop[db_keys[i]] = str(line[i])

    db2.close()
    #print "get_fits| DONE with func"
    return dtop

#adam-note# modified from calc_test_save
''' read in the photometric calibration and apply it to the data '''
def get_cats_ready(SUPA,FLAT_TYPE,galaxycat,starcat): #step3_run_fit
    '''inputs:SUPA,FLAT_TYPE,galaxycat=data_path+'PHOTOMETRY/sdssgalaxy.cat', starcat=data_path+'PHOTOMETRY/sdssstar.cat'
    purpose: this gets the information from sdssstar.cat relevant to this specific SUPA, saves it in starsdssmatch__SUPA0121585_star.txt, and then corrects it ( starts the seqNr at 2 instead of 1 ) sdssmatch__SUPA0121585_star.txt
    '''
    print 'get_cats_ready| START the func. inputs: SUPA=',SUPA , ' FLAT_TYPE=',FLAT_TYPE , ' galaxycat=',galaxycat , ' starcat=',starcat

    dict_cats = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_cats['FILTER'],dict_cats['OBJNAME'])
    search_params.update(dict_cats)

    ''' figure out the correct color and magnitudes for the filter '''

    tmp = {}
    #adam-ask# do we need the galaxy catalogs as well?
    # galaxycat=data_path+'PHOTOMETRY/sdssgalaxy.cat' starcat=data_path+'PHOTOMETRY/sdssstar.cat'
    for type_stargal,cat in [['star',starcat]]: #['galaxy',galaxycat],
        hdulist1 = pyfits.open(cat)
        #print 'get_cats_ready| ',hdulist1["STDTAB"].columns
        table = hdulist1["STDTAB"].data
        #adam-ask# Is there a good place to get this info for W-S-G+? Or should I just use the fit from another filter, since W-S-G+ doesn't have rotations anyway
        other_info = config_bonn.info[dict_cats['FILTER']] #adam-Warning: add W-S-G+ info
        filters_info = utilities.make_filters_info([dict_cats['FILTER']]) #adam-Warning: add W-S-G+ info
        compband = filters_info[0][1] ## use the SDSS/other comparison band
        color1which = other_info['color1']
        print 'get_cats_ready|  filters_info=',filters_info , ' compband=',compband
        #adam-no_more# try:
        #adam-no_more#         other_info = config_bonn.info[dict_cats['FILTER']]
        #adam-no_more#         filters_info = utilities.make_filters_info([dict_cats['FILTER']])
        #adam-no_more#         compband = filters_info[0][1] ## use the SDSS/other comparison band
        #adam-no_more#         color1which = other_info['color1']
        #adam-no_more#         print 'get_cats_ready|  filters_info=',filters_info , ' compband=',compband
        #adam-no_more# except KeyError:
        #adam-no_more#         if dict_cats['FILTER']=="W-S-G+":
        #adam-no_more#                 print "get_cats_ready| making stuff up for W-S-G+!!!"
        #adam-no_more#                 compband = 'g'
        #adam-no_more#                 color1which = 'gmr'
        #adam-no_more#         else:
        #adam-no_more#                 raise
        for key in dict_cats.keys():
            if string.find(key,'color') != -1:
                print 'get_cats_ready| key=',key
        #calib = get_calibrations_threesecond(dict_cats['OBJNAME'],filters_info)
        #print 'get_cats_ready| calib', calib
        #model = utilities.convert_modelname_to_array('zpPcolor1') #dict_cats['model_name%'+dict_cats['FILTER']])
        cols = [] #pyfits.Column(name=column.name, format=column.format,array=scipy.array(0 + hdulist1["STDTAB"].data.field(column.name))) for column in hdulist1["STDTAB"].columns]
        print 'get_cats_ready| data start'
        #data = utilities.color_std_correct(model,dict_cats,table,dict_cats['FILTER'],compband+'mag',color1which) # correct standard magnitude into instrumntal system -- at least get rid of the color term
        data = copy(table.field(compband+'mag'))
        print 'get_cats_ready|  data=',data
        cols.append(pyfits.Column(name='stdMag_corr', format='D',array=data))
        cols.append(pyfits.Column(name='stdMagErr_corr', format='D',array=scipy.array(0 + hdulist1["STDTAB"].data.field(compband+'err'))))
        cols.append(pyfits.Column(name='stdMagColor_corr', format='D',array=scipy.array(0 + hdulist1["STDTAB"].data.field(color1which))))
        cols.append(pyfits.Column(name='stdMagClean_corr', format='D',array=scipy.array(0 + hdulist1["STDTAB"].data.field('Clean'))))
        cols.append(pyfits.Column(name='ALPHA_J2000', format='D',array=scipy.array(0 + hdulist1["STDTAB"].data.field('Ra'))))
        cols.append(pyfits.Column(name='DELTA_J2000', format='D',array=scipy.array(0 + hdulist1["STDTAB"].data.field('Dec'))))
        cols.append(pyfits.Column(name='SeqNr', format='E',array=scipy.array(0 + hdulist1["STDTAB"].data.field('SeqNr'))))
        length = len(hdulist1["STDTAB"].data.field('SeqNr'))
        if type_stargal == 'star':
            cols.append(pyfits.Column(name='Star_corr', format='E',array=scipy.ones(length)))
        else:
            cols.append(pyfits.Column(name='Star_corr', format='E',array=scipy.zeros(length)))

        hdu = pyfits.PrimaryHDU()
        print 'get_cats_ready| hdulist'
        hdulist = pyfits.HDUList([hdu])
        print 'get_cats_ready| tbhu'
        tbhu = pyfits.BinTableHDU.from_columns(cols)
        hdulist.append(tbhu)
        print 'get_cats_ready| headers'
        hdulist[1].header.update(EXTNAME='OBJECTS')
        #this outcat is like: starsdssmatch__SUPA0121585_star.txt (not sdssmatch__SUPA0121585_star.txt)
        outcat = data_path + 'PHOTOMETRY/ILLUMINATION/' + type_stargal + 'sdssmatch__' + search_params['SUPA'] + '_' +  type_stargal + '.cat'
        hdulist.writeto( outcat ,overwrite=True)
        print 'get_cats_ready| wrote out new cat. outcat=',outcat
        save_exposure({type_stargal + 'sdssmatch':outcat},SUPA,FLAT_TYPE)
        tmp[type_stargal + 'sdssmatch'] = outcat

        #this outcat2 is like: sdssmatch__SUPA0121585_star.txt (not starsdssmatch__SUPA0121585_star.txt) like in the loop
        outcat2 = data_path + 'PHOTOMETRY/ILLUMINATION/sdssmatch__' + search_params['SUPA'] + '_' +  type_stargal + '.cat'
        os.system('rm ' + outcat2)
        #this saves the stuff in starsdssmatch__SUPA0121585_star.txt to the name sdssmatch__SUPA0121585_star.txt starting the seqNr at 2 instead of 1
        paste_cats([tmp[type_stargal + 'sdssmatch']],outcat2,index=1)

    print 'get_cats_ready| added outcat2=', outcat2
    print "get_cats_ready| DONE with func"
    return outcat2

#adam-note# modified from calc_tmpsave
def get_sdss_cats(OBJNAME=None): #step3_run_fit
    '''
    purpose: update the sdss_db and run get_sdss_obj for each of the SUPAs
    '''
    print 'get_sdss_cats| START the func. inputs: OBJNAME=',OBJNAME
    db2,c = connect_except()
    db_keys = describe_db(c)

    if OBJNAME is not None:
        command="SELECT * from "+illum_db+" LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".SUPA like 'SUPA%' and "+illum_db+".OBJNAME like '%" + OBJNAME + "%' and "+illum_db+".pasted_cat is not null GROUP BY "+illum_db+".OBJNAME" # LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".OBJNAME is not null  GROUP BY "+illum_db+".OBJNAME" #and sdss_db.cov is not NULL
    else:
        command="SELECT * from "+illum_db+" LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".SUPA like 'SUPA%' and "+illum_db+".pasted_cat is not null GROUP BY "+illum_db+".OBJNAME" # LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".OBJNAME is not null  GROUP BY "+illum_db+".OBJNAME" #and sdss_db.cov is not NULL

    #command="SELECT * from "+illum_db+" LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME GROUP BY "+illum_db+".OBJNAME" # LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".OBJNAME is not null  GROUP BY "+illum_db+".OBJNAME" #and sdss_db.cov is not NULL
    print 'get_sdss_cats| command=',command
    c.execute(command)
    results=c.fetchall()
    for line in results:
        try:
            dtop = {}
            for i in xrange(len(db_keys)): dtop[db_keys[i]] = str(line[i])
            print 'get_sdss_cats| dtop["CRVAL1"]=',dtop["CRVAL1"] , ' dtop["CRVAL2"]=',dtop["CRVAL2"] , ' dtop["OBJNAME"]=',dtop["OBJNAME"]
            print 'get_sdss_cats| dtop["SUPA"]=',dtop["SUPA"] , ' dtop["FLAT_TYPE"]=',dtop["FLAT_TYPE"]
            #dict_cats = run_telarchive(float(dtop['CRVAL1']),dtop['CRVAL2'],dtop['OBJNAME'])
            OBJNAME = dtop['OBJNAME']
            SUPA = dtop['SUPA']
            FLAT_TYPE = dtop['FLAT_TYPE']

            #cov = sdss_coverage(SUPA, FLAT_TYPE)
            #starcat = None
            #if cov:
            cov, starcat, galaxycat = get_sdss_obj(SUPA, FLAT_TYPE)
            print 'get_sdss_cats| cov=',cov , ' starcat=',starcat , ' galaxycat=',galaxycat

            dict_sdss = {}
            dict_sdss['cov'] = cov
            if cov:
                dict_sdss['starcat_sdss'] = starcat
                dict_sdss['galaxycat_sdss'] = galaxycat

            dict_sdss['OBJNAME'] = OBJNAME
            floatvars = {}
            stringvars = {}
            #copy array but exclude lists
            letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-'
            for ele in dict_sdss.keys():
                print 'get_sdss_cats| ele=',ele , ' dict_sdss[ele]=',dict_sdss[ele]
                type = 'float'
                for l in letters:
                    if string.find(str(dict_sdss[ele]),l) != -1 or dict_sdss[ele] == ' ':
                        type = 'string'
                if type == 'float':
                    floatvars[ele] = str(float(dict_sdss[ele]))
                elif type == 'string':
                    stringvars[ele] = dict_sdss[ele]

            # make database if it doesn't exist
            print 'get_sdss_cats| floatvars=', floatvars
            print 'get_sdss_cats| stringvars=', stringvars

            for column in stringvars:
                try:
                    command = 'ALTER TABLE sdss_db ADD ' + column + ' varchar(240)'
                    c.execute(command)
                except: nope = 1
            for column in floatvars:
                try:
                    command = 'ALTER TABLE sdss_db ADD ' + column + ' float(30)'
                    c.execute(command)
                except: nope = 1

            c.execute("SELECT OBJNAME from sdss_db where OBJNAME = '" + OBJNAME + "'")
            results = c.fetchall()
            print 'get_sdss_cats| len(results)=',len(results)
            print 'get_sdss_cats| results=',results
            if len(results) > 0:
                print 'get_sdss_cats| already added'
            else:
                command = "INSERT INTO sdss_db (OBJNAME) VALUES ('" + OBJNAME + "')"
                print 'get_sdss_cats| command=',command
                c.execute(command)

            vals = ''
            for key in stringvars.keys():
                print 'get_sdss_cats| key=',key , ' stringvars[key]=',stringvars[key]
                vals += ' ' + key + "='" + str(stringvars[key]) + "',"

            for key in floatvars.keys():
                print 'get_sdss_cats| key=',key , ' floatvars[key]=',floatvars[key]
                vals += ' ' + key + "='" + floatvars[key] + "',"
            vals = vals[:-1]

            command = "UPDATE sdss_db set " + vals + " WHERE OBJNAME='" + OBJNAME + "'"
            print 'get_sdss_cats| command=',command
            c.execute(command)
        except:
            print 'get_sdss_cats| traceback.print_exc(file=sys.stdout)=',traceback.print_exc(file=sys.stdout)
            print "HIT EXCEPTION in get_sdss_cats"
            raise
    print "get_sdss_cats| DONE with func"

#adam-note# modified from calc_tmpsave
def get_sdss_obj(SUPA, FLAT_TYPE): #step3_run_fit
    '''Note: despite having SUPA,FLAT_TYPE as inputs, this only needs to be run once per cluster
    purpose: create the sdss catalog (sdssstar.cat and sdssgalaxy.cat)
    '''
    print 'get_sdss_obj| START the func. inputs: SUPA=', SUPA,  "FLAT_TYPE=", FLAT_TYPE
    dict_sdss_obj = get_files(SUPA,FLAT_TYPE)
    search_params = initialize(dict_sdss_obj['FILTER'],dict_sdss_obj['OBJNAME'])
    search_params.update(dict_sdss_obj)
    starcat=data_path+'PHOTOMETRY/sdssstar.cat'
    galaxycat=data_path+'PHOTOMETRY/sdssgalaxy.cat'
    print 'get_sdss_obj| starcat=',starcat

    catalog = search_params['pasted_cat'] #exposures[exposure]['pasted_cat']
    ramin,ramax, decmin, decmax = coordinate_limits(catalog)
    limits = {'ramin':ramin-0.2,'ramax':ramax+0.2,'decmin':decmin-0.2,'decmax':decmax+0.2}
    print 'get_sdss_obj| ramin=',ramin , ' ramax=',ramax , ' decmin=',decmin , ' decmax=',decmax

    image = search_params['files'][0]
    print 'get_sdss_obj| image=',image
    import retrieve_test
    for type_stargal,cat in [['galaxy',galaxycat],['star',starcat]]:
        cov, outcat = retrieve_test.run(image,cat,type_stargal,limits)
        save_exposure({type_stargal + 'cat':outcat},SUPA,FLAT_TYPE)

    print "get_sdss_obj| DONE with func"
    return cov, starcat, galaxycat

#adam-note# modified from calc_tmpsave
def coordinate_limits(cat): #step3_run_fit
    '''purpose: get the edges of the FOV of this catalog'''

    print 'coordinate_limits| START the func. inputs: cat=',cat
    p = pyfits.open(cat)
    good_entries = p[2].data

    print 'coordinate_limits| len(good_entries)=',len(good_entries)
    mask = abs(good_entries.field('ALPHA_J2000')) > 0.0001
    good_entries = good_entries[mask]

    print 'coordinate_limits| len(good_entries)=',len(good_entries)
    mask = abs(good_entries.field('ALPHA_J2000')) <  400
    good_entries = good_entries[mask]

    print 'coordinate_limits| len(good_entries)=',len(good_entries)
    mask = abs(good_entries.field('DELTA_J2000')) > 0.0001
    good_entries = good_entries[mask]

    print 'coordinate_limits| len(good_entries)=',len(good_entries)
    mask = abs(good_entries.field('DELTA_J2000')) < 300
    good_entries = good_entries[mask]

    print 'coordinate_limits| len(good_entries)=',len(good_entries)

    ra = good_entries.field('ALPHA_J2000')
    ra.sort()
    dec = good_entries.field('DELTA_J2000')
    dec.sort()
    print 'coordinate_limits| cat=',cat

    print "coordinate_limits| DONE with func"
    return ra[0],ra[-1],dec[0],dec[-1]

#adam-note# step4: below here is my attempt to take the stuff from calc_test_save.py related to calculating sigma_jack and testing the goodness of fit, and make it work here
def get_a_file(OBJNAME,FILTER,PPRUN):
    ''' get a single file w/ OBJNAME FILTER PPRUN'''

    db2,c = connect_except()
    keys=describe_db(c,[illum_db])

    command="SELECT * from "+illum_db+" where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and CHIPS is not null limit 1"
    print 'get_a_file| command=',command
    c.execute(command)
    results = c.fetchall()
    dict_a_file = {}
    print 'get_a_file| len(results)=',len(results)
    for i in range(len(results[0])):
        dict_a_file[keys[i]] = results[0][i]

    #adam: get "files" matching this one, if they exist
    file_pat = dict_a_file['file']
    res = re.split('_\d+O',file_pat)
    pattern = res[0] + '_*O' + res[1]
    files = glob(pattern)
    dict_a_file['files'] = files
    print 'get_a_file| len(files)=',len(files)

    #db2.close()
    return dict_a_file

def testgood(OBJNAME,FILTER,PPRUN): #step4_test_fit #main
    '''inputs:
    returns:
    calls: describe_db,save_fit,save_fit,describe_db,sort_results
    called_by: '''

    db2,c = connect_except()
    db_keys_t = describe_db(c,['' + test + 'try_db'])
    command_testgood1="SELECT * from ' + test + 'try_db where todo='good' and var_correction > 0.08 order by rand()"
    command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null and (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
    command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null order by rand()' # and (i.objname like "A68%" and i.pprun like "2007-07-18_W-J-B")' # or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
    #command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null order by rand()' #and objname="MACS0018+16" and pprun="2003-09-25_W-J-V"' # i.todo="bootstrap" and (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and bootstrapstatus="fitfinished" and objname="MACS1824+43" and PPRUN="2000-08-06_W-C-IC"'
    #command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null and (i.sdssstatus like "%finished" or i.Nonestatus like "%finished")  order by rand()'
    #command_testgood1='SELECT * from ' + test + 'try_db i where (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and (i.objname like "MACS0717%")  order by rand()'

    command_testgood1="select * from " + test + "try_db where OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and  FILTER='" + FILTER + "'"
    #command_testgood1='select * from ' + test + 'try_db where objname="CL1226" and pprun="2000-12-27_W-C-IC"' # and pprun="2007-07-18_W-C-IC"'
    print 'testgood| command_testgood1=',command_testgood1
    c.execute(command_testgood1)
    results_testgood1=c.fetchall()
    print 'testgood| len(results_testgood1)=',len(results_testgood1)
    for line in results_testgood1:
        dtop = {}
        for i in range(len(db_keys_t)):
            dtop[db_keys_t[i]] = str(line[i])

        ''' if not fit has been attempted, set todo '''
        print 'testgood| dtop["sdssstatus"]=',dtop["sdssstatus"] , ' dtop["Nonestatus"]=',dtop["Nonestatus"] , ' dtop["PPRUN"]=',dtop["PPRUN"] , ' dtop["OBJNAME"]=',dtop["OBJNAME"]
        if dtop['sdssstatus'] == None and dtop['Nonestatus'] == None:
            print "testgood| (adam-look ERROR) if dtop['sdssstatus'] == None and dtop['Nonestatus'] == None: TRUE"
            save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'sample':'record','sample_size':'record','todo': 'no fit'},db='' + test + 'try_db')

        elif dtop['sdssstatus']=='failed' or dtop['Nonestatus']=='failed':
            print "testgood| (adam-look ERROR) if dtop['sdssstatus'] == 'failed' and dtop['Nonestatus'] == 'failed': TRUE"
            save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'sample':'record','sample_size':'record','todo': 'failed fit'},db='' + test + 'try_db')

        else:
            print "testgood| (GOOD!) dtop['sdssstatus'] or dtop['Nonestatus'] are SUCCESSFUL"
            db_keys = describe_db(c,[illum_db,test + 'try_db'])
            #command_testgood2="SELECT * from "+illum_db+" where  OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and filter like '" + dtop['FILTER'] + "' and pasted_cat is not NULL"
            #command_testgood2="SELECT * from "+illum_db+" i left join ' + test + 'try_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and f.std is not null and f.mean is not null and f.rots is not null and f.var_correction is not null group by f.pprun"
            #command_testgood2="SELECT * from "+illum_db+" i left join " + test + "try_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and (f.sdssstatus is not null or f.Nonestatus is not null) and ((f.sdssstatus!='failed' or f.sdssstatus is null) and (f.Nonestatus is null or f.Nonestatus!='failed')) and f.config=9.0 group by f.pprun"
            command_testgood2="SELECT * from "+illum_db+" i left join " + test + "try_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and (f.sdssstatus is not null or f.Nonestatus is not null) and ((f.sdssstatus!='failed' or f.sdssstatus is null) and (f.Nonestatus is null or f.Nonestatus!='failed')) group by f.pprun"
            #and (f.bootstrapstatus like '%finished' or f.sdssstatus like '%finished' or f.Nonestatus like '%finished')
            print 'testgood| command_testgood2=',command_testgood2
            c.execute(command_testgood2)
            results_testgood2=c.fetchall() #adam-ask# is this resetting the earlier `results` intentionally?
            print 'testgood| len(results_testgood2)=',len(results_testgood2)
            sorted_results=sort_results(results_testgood2,db_keys)
    return sorted_results #adam-added#

def sort_results(results2,db_keys): #step4_test_fit #intermediate
    '''inputs: results2,db_keys
    returns:  all_list
    calls: find_config,describe_db,calc_good,save_fit,save_fit,save_fit,save_fit
    called_by: testgood'''
    try:
        rotation_runs = {}
        for line in results2:
            dict_sort_results = {}
            for i in range(len(db_keys)):
                dict_sort_results[db_keys[i]] = str(line[i])
            GID = float(dict_sort_results['GABODSID'])
            CONFIG_IM = find_config(GID)
            FILTER_NUM =  None

            for i in range(len(config_bonn.wavelength_groups)):
                for filt in config_bonn.wavelength_groups[i]:
                    if filt == dict_sort_results['FILTER']:
                        FILTER_NUM = i
                        dict_sort_results['FILTER_NUM'] = FILTER_NUM

            if FILTER_NUM is None:
                print 'sort_results| dict_sort_results["FILTER"]=',dict_sort_results["FILTER"]
                raise NoFilterMatch

            if True: #float(dict_sort_results['EXPTIME']) > 10.0:
                if not dict_sort_results['PPRUN'] in rotation_runs:
                    rotation_runs[dict_sort_results['PPRUN']] = copy(dict_sort_results)
                    #{'ROTATION':{dict_sort_results['ROTATION']:'yes'},'FILTER':dict_sort_results['FILTER'],'CONFIG_IM':CONFIG_IM,'EXPTIME':dict_sort_results['EXPTIME'],'file':dict_sort_results['file'],'linearfit':dict_sort_results['linearfit'],'OBJNAME':dict_sort_results['OBJNAME'],'catalog':dict_sort_results['catalog'],'FILTER_NUM':FILTER_NUM,}
                #rotation_runs[dict_sort_results['PPRUN']]['ROTATION'][dict_sort_results['ROTATION']] = 'yes'
        #print rotation_runs

        help_list = {}
        good_list = {}
        print 'sort_results| (adam-look) stats: PPRUN',"var_correction" , "mean" , "std" , "sdss_imp_all" , "match_stars" , "sdss_imp"
        for y in rotation_runs.keys():

	    db2,c = connect_except()

            ''' figure out what the sample is '''
            command_sort_results1="SELECT todo from " + test + "try_db where OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and PPRUN='" + rotation_runs[y]['PPRUN'] + "'"
            print 'sort_results| command_sort_results1=',command_sort_results1
            c.execute(command_sort_results1)
            results=c.fetchall()
            todo = results[0][0]

            command_sort_results2="SELECT sample from " + test + "fit_db where OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and PPRUN='" + rotation_runs[y]['PPRUN'] + "' and sample_size='all'  group by sample"
            print 'sort_results| command_sort_results2=',command_sort_results2
            c.execute(command_sort_results2)
            results=c.fetchall()
            samples = {}
            for line in results:
                samples[line[0]] = 'yes'

            if samples.has_key('sdss'):
                s = 'sdss'
            else: s = 'None'
            #s = 'None'

            db_keys_t = describe_db(c,['' + test + 'fit_db'])
            command_sort_results3="SELECT * from " + test + "fit_db where PPRUN='" + rotation_runs[y]['PPRUN'] + "' and OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and sample_size='all'" # and sample='sdss'"
            print 'sort_results| command_sort_results3=',command_sort_results3
            c.execute(command_sort_results3)
            results=c.fetchall()
            for line in results:
                dtop = {}
                for i in range(len(db_keys_t)):
                    dtop[db_keys_t[i]] = str(line[i])

            print 'sort_results| results=',results
            print 'sort_results| dtop=',dtop

            #if (rotation_runs[y]['sdss$good'] == 'y' or rotation_runs[y]['None$good'] =='y') and rotation_runs[y]['CONFIG_IM'] != '8' and  rotation_runs[y]['CONFIG_IM'] != '9' and  rotation_runs[y]['CONFIG_IM'] != '10_3' and len(rotation_runs[y]['ROTATION'].keys()) > 1:
            #print y, rotation_runs[y]['EXPTIME'], rotation_runs[y]['file'],  (float(rotation_runs[y]['mean']) - 1*float(rotation_runs[y]['std']) > 1.005) , (rotation_runs[y]['rots'] > 1 or dtop['sample']=='sdss'),  float(rotation_runs[y]['EXPTIME']) > 10

            #print float(rotation_runs[y]['mean']) , float(rotation_runs[y]['std']) , rotation_runs[y][s + '_var_correction'] , rotation_runs[y]['rots'] , dtop['sample']=='sdss' , float(rotation_runs[y]['EXPTIME'])
            #print (float(rotation_runs[y]['mean']) - 1*float(rotation_runs[y]['std']) > 1.005) , float(rotation_runs[y]['var_correction']) < 0.08 , (rotation_runs[y]['rots'] > 1 or dtop['sample']=='sdss') , float(rotation_runs[y]['EXPTIME']) > 10

            sl = s + '_'

            print 'sort_results| y=',y , ' rotation_runs[y]["OBJNAME"]=',rotation_runs[y]["OBJNAME"] , ' s+"status"=',s+"status" , ' rotation_runs[y][s+"status"]=',rotation_runs[y][s+"status"]
            if string.find(rotation_runs[y][s + 'status'],'finished')!= -1:

                ''' if not stats, then calculate them!!! '''
                if str(rotation_runs[y]['stats']) == 'None' or (str(rotation_runs[y][sl + 'var_correction']) == 'None' or str(rotation_runs[y][sl + 'mean']) == 'None' or str(rotation_runs[y][sl+'std'])): calc_good(rotation_runs[y]['OBJNAME'],rotation_runs[y]['FILTER'],rotation_runs[y]['PPRUN'])
                print 'sort_results| rotation_runs[y]["CONFIG"]=',rotation_runs[y]["CONFIG"]
                if rotation_runs[y]['sdss_imp_all'] != 'None':
                    if rotation_runs[y]['CONFIG'] == str(8.0) or rotation_runs[y]['CONFIG'] == str(9.0) :
                        good = float(rotation_runs[y][sl + 'var_correction']) < 0.03 and (float(rotation_runs[y][sl+ 'mean']) - 1.*float(rotation_runs[y][sl + 'std']) > 0.995) and ( (float(rotation_runs[y]['sdss_imp_all'])>1.00 and float(rotation_runs[y]['match_stars'])>400) or float(rotation_runs[y]['match_stars'])<400)
                    else:
                        good = float(rotation_runs[y][sl + 'var_correction']) < 0.01 and (float(rotation_runs[y][sl+ 'mean']) - 1.5*float(rotation_runs[y][sl + 'std']) > 1.00) and ( (float(rotation_runs[y]['sdss_imp_all'])>1.00 and float(rotation_runs[y]['match_stars'])>400) or float(rotation_runs[y]['match_stars'])<400)
                else:
                    if rotation_runs[y]['CONFIG'] == str(8.0) or rotation_runs[y]['CONFIG'] == str(9.0):
                        good = float(rotation_runs[y][sl + 'var_correction']) < 0.03 and (float(rotation_runs[y][sl + 'mean']) - 1.*float(rotation_runs[y][sl + 'std']) > 0.99)
                    else:
                        print 'sort_results| sl=',sl
                        good = float(rotation_runs[y][sl + 'var_correction']) < 0.01 and (float(rotation_runs[y][sl + 'mean']) - 1.5*float(rotation_runs[y][sl + 'std']) > 1.00)
            else: good = False

            print 'sort_results| (rotation_runs[y][sl=',(rotation_runs[y][sl + "var_correction"]) , ' (rotation_runs[y][sl=',(rotation_runs[y][sl + "mean"]) , ' (rotation_runs[y][sl=',(rotation_runs[y][sl + "std"]) , ' rotation_runs[y]["sdss_imp_all"]=',rotation_runs[y]["sdss_imp_all"]
            print 'sort_results| string.find(rotation_runs[y][s+"status"],"finished")=',string.find(rotation_runs[y][s+"status"],"finished")
            print 'sort_results| s+"status"=',s+"status"

            print 'sort_results| sl=',sl
            if str(rotation_runs[y][sl + 'var_correction']) == 'None': sl = ''
            print 'sort_results| sl=',sl
            print 'sort_results| stats:  rotation_runs[y][sl+"var_correction"]=',rotation_runs[y][sl+"var_correction"] , ' rotation_runs[y][sl+"mean"]=',rotation_runs[y][sl+"mean"] , ' rotation_runs[y][sl+"std"]=',rotation_runs[y][sl+"std"] , ' rotation_runs[y]["sdss_imp_all"]=',rotation_runs[y]["sdss_imp_all"] , ' rotation_runs[y]["match_stars"]=',rotation_runs[y]["match_stars"] , ' rotation_runs[y]["sdss_imp"]=',rotation_runs[y]["sdss_imp"]
            print 'sort_results| (adam-look) stats: ',y,rotation_runs[y][sl+"var_correction"] , rotation_runs[y][sl+"mean"] , rotation_runs[y][sl+"std"] , rotation_runs[y]["sdss_imp_all"] , rotation_runs[y]["match_stars"] , rotation_runs[y]["sdss_imp"]

            ''' look to see if bootstrap was tried and failed or if the regular fit failed because of too few objects, set boostrap_good to use for applying the correction '''
            if str(rotation_runs[y]['bootstrapstatus']) == 'failed' or (str(rotation_runs[y]['bootstrapstatus']) == 'None' and   (string.find(rotation_runs[y]['exception'],'end')!=-1 or string.find(rotation_runs[y]['exception'],'few')!=-1)): bootstrap_good = 'failed'
            elif str(rotation_runs[y]['bootstrap_var_correction']) != 'None' and str(rotation_runs[y]['bootstrap_mean']) != 'None' and str(rotation_runs[y]['bootstrap_std']) != 'None':
                bootstrap_good = float(rotation_runs[y]['bootstrap_var_correction']) < 0.01 and (float(rotation_runs[y]['bootstrap_mean']) - 1.5*float(rotation_runs[y]['bootstrap_std']) > 1.00)
            else: bootstrap_good = 'no input measurements'
            save_fit({'PPRUN':rotation_runs[y]['PPRUN'],'OBJNAME':rotation_runs[y]['OBJNAME'],'FILTER':rotation_runs[y]['FILTER'],'sample':'record','sample_size':'record','bootstrap_good': bootstrap_good},db='' + test + 'try_db')

            print 'sort_results| good=',good , ' y=',y
            print 'sort_results| good?'
            print 'sort_results| y=',y , ' bootstrap_good=',bootstrap_good , ' rotation_runs[y]["bootstrapstatus"]=',rotation_runs[y]["bootstrapstatus"]

            if good:
                print 'sort_results| GOOD'
                good_list[y] = {}
                good_list[y]['FILTER_NUM'] = rotation_runs[y]['FILTER_NUM']
                good_list[y]['FILTER'] = rotation_runs[y]['FILTER']
                good_list[y]['OBJNAME'] = rotation_runs[y]['OBJNAME']
                good_list[y]['catalog'] = dtop['catalog']
                good_list[y]['EXPTIME'] = rotation_runs[y]['EXPTIME']
                good_list[y]['PPRUN'] = rotation_runs[y]['PPRUN']
                good_list[y]['file'] = rotation_runs[y]['file']
                good_list[y]['todo'] = rotation_runs[y]['todo']
                good_list[y]['status'] = 'good'
                good_list[y]['primary'] = None
                good_list[y]['secondary'] = None
                good_list[y]['bootstrap_good'] = bootstrap_good
                save_fit({'PPRUN':rotation_runs[y]['PPRUN'],'OBJNAME':rotation_runs[y]['OBJNAME'],'FILTER':rotation_runs[y]['FILTER'],'sample':'record','sample_size':'record','todo': 'good'},db='' + test + 'try_db')
                print 'sort_results| good_list=',good_list
            else:
                print 'sort_results| HELP'
                help_list[y] = {}
                help_list[y]['FILTER_NUM'] = rotation_runs[y]['FILTER_NUM']
                help_list[y]['FILTER'] = rotation_runs[y]['FILTER']
                help_list[y]['OBJNAME'] = rotation_runs[y]['OBJNAME']
                #help_list[y]['file'] = rotation_runs[y]['file']
                help_list[y]['EXPTIME'] = rotation_runs[y]['EXPTIME']
                help_list[y]['PPRUN'] = rotation_runs[y]['PPRUN']
                help_list[y]['todo'] = rotation_runs[y]['todo']
                help_list[y]['catalog'] = dtop['catalog']
                help_list[y]['status'] = 'help'
                help_list[y]['primary'] = None
                help_list[y]['secondary'] = None
                help_list[y]['bootstrap_good'] = bootstrap_good

        orphan_list = {}
        matched_list = {}
        for y in help_list.keys():
            ''' use rules to assign comparison cats'''
            ''' first determine the closest filter '''
            primaries = []
            for x in good_list.keys():
                if good_list[x]['catalog'] != 'None':
                    ''' if same filter, use that '''
                    if good_list[x]['FILTER'] == help_list[y]['FILTER']:
                        primaries.append([-1,x,good_list[x]['FILTER'],good_list[x]['catalog']])
                    else:
                        primaries.append([abs(help_list[y]['FILTER_NUM'] - good_list[x]['FILTER_NUM']),x,good_list[x]['FILTER'],good_list[x]['catalog']])
            primaries.sort()
            if len(primaries) > 0:
                if primaries[0][0] < 3:
                    primary = primaries[0][1]
                    primary_filter = primaries[0][2]
                    help_list[y]['primary'] = primary
                    help_list[y]['primary_catalog'] = primaries[0][3]
                else:
                    primary = None
                    primary_filter = None
                    help_list[y]['primary'] = None
                    help_list[y]['primary_catalog'] = None
            else:
                primary = None
                primary_filter = None
                help_list[y]['primary'] = None
                help_list[y]['primary_catalog'] = None

            print 'sort_results| primary: ',  "primaries=", primaries,  "primary=", primary,  "y=" , y

            secondaries = []
            for x in good_list.keys():
                if good_list[x]['FILTER'] != primary_filter and x != primary and help_list[y]['FILTER_NUM'] != good_list[x]['FILTER_NUM']:
                    secondaries.append([abs(help_list[y]['FILTER_NUM'] - good_list[x]['FILTER_NUM']),x,good_list[x]['FILTER'],good_list[x]['catalog']])
            #''' if no calibrated secondary, use the same catalog '''
            #if len(secondaries) == 0:
            #    for x in help_list.keys():
            #        secondaries.append([abs(help_list[y]['FILTER_NUM'] - help_list[x]['FILTER_NUM']),x])
            #''' guaranteed to be a secondary '''
            if len(secondaries)>0:
                secondaries.sort()
                secondary = secondaries[0][1]
                help_list[y]['secondary'] = secondary
                help_list[y]['secondary_catalog'] = secondaries[0][3]
            else:
                secondary = None
                help_list[y]['secondary'] = None
                help_list[y]['secondary_catalog'] = None

            print 'sort_results| secondary: ',  "secondaries=",secondaries,  "secondary=",secondary,  "y=" , y
            print 'sort_results| help_list=',help_list

            if help_list[y]['primary']!=None and help_list[y]['secondary']!=None:
                save_fit({'PPRUN':help_list[y]['PPRUN'],'OBJNAME':help_list[y]['OBJNAME'],'FILTER':help_list[y]['FILTER'],'sample':'record','sample_size':'record','todo': 'bootstrap', 'primary_catalog':help_list[y]['primary_catalog'],'primary_filt':str(help_list[y]['primary']), 'secondary_catalog':help_list[y]['secondary_catalog'], 'secondary_filt':str(help_list[y]['secondary'])},db='' + test + 'try_db')
            else:
                print 'sort_results| primaries', primaries,'\n'
                print 'sort_results| secondaries', secondaries
                print 'sort_results| help_list[y]["primary"]=',help_list[y]["primary"] , ' help_list[y]["secondary"]=',help_list[y]["secondary"]
                print 'sort_results| help_list[y]["PPRUN"]=',help_list[y]["PPRUN"]
                print 'sort_results| good_list.keys()=',good_list.keys()
                print 'sort_results| help_list.keys()=',help_list.keys()
                save_fit({'PPRUN':help_list[y]['PPRUN'],'OBJNAME':help_list[y]['OBJNAME'],'FILTER':help_list[y]['FILTER'],'sample':'record','sample_size':'record','todo': 'orphaned', 'primary_catalog':help_list[y]['primary_catalog'],'primary_filt':str(help_list[y]['primary']), 'secondary_catalog':help_list[y]['secondary_catalog'], 'secondary_filt':str(help_list[y]['secondary'])},db='' + test + 'try_db')

                #save_fit({'PPRUN':help_list[y]['PPRUN'],'OBJNAME':help_list[y]['OBJNAME'],'FILTER':help_list[y]['FILTER'],'sample':'record','sample_size':'record','todo': 'bootstrap', 'primary_catalog':help_list[y]['primary_catalog'],'primary_filt':str(help_list[y]['primary']), 'secondary_catalog':help_list[y]['secondary_catalog'], 'secondary_filt':str(help_list[y]['secondary'])},db='' + test + 'try_db')

        print 'sort_results| good_list=',good_list
        print 'sort_results| help_list=',help_list

        for g in good_list.keys(): print 'sort_results| g=',g , ' good_list[g]=',good_list[g]
        for h in help_list.keys(): print 'sort_results| h=',h , ' help_list[h]=',help_list[h]

        for key in sorted(good_list.keys()):   print 'sort_results| good: ',key, good_list[key]['EXPTIME'], #good_list[key]['file']
        for key in sorted(help_list.keys()):   print 'sort_results| help: ',key, help_list[key]['EXPTIME'],#help_list[key]['file']
        for key in sorted(matched_list.keys()):print 'sort_results| matched: ',key, matched_list[key]['EXPTIME'],#matched_list[key]['file']
        for key in sorted(orphan_list.keys()): print 'sort_results| orphaned: ',key, orphan_list[key]['EXPTIME'],#orphan_list[key]['file']
        all_list = copy(good_list)
        all_list.update(help_list)
    except:
        ns.update(locals())
        raise
    print 'sort_results| all_list=',all_list
    return all_list

def calc_good(OBJNAME=None,FILTER=None,PPRUN=None): #step4_test_fit #main
    '''inputs: OBJNAME=None,FILTER=None,PPRUN=None
    returns:
    calls: describe_db,save_fit,save_fit,describe_db,save_fit,describe_db,save_fit,describe_db,test_correction,save_fit,describe_db,save_fit,save_fit,describe_db,save_fit,save_fit
    called_by: sort_results'''
    try:
        db2,c = connect_except()
        db_keys_try = describe_db(c,['' + test + 'try_db'])
        db_keys_fit = describe_db(c,['' + test + 'fit_db'])

        #command_calc_good1='SELECT * from ' + test + 'try_db i where (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and stats is null order by rand()' # and (i.objname like "MACS0744%")' # and i.pprun="2001-12-11_W-C-IC" order by rand()'
        #command_calc_good1='SELECT * from ' + test + 'try_db i where i.bootstrapstatus="fitfinished" and bootstrap_mean is null and i.stats is null ' #and (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
        # and (i.objname like "MACS0744%")' # and i.pprun="2001-12-11_W-C-IC" order by rand()'

        '''PART1| get basic PPRUN/OBJNAME stuff in try_db'''
        if OBJNAME is not None:
            command_calc_good1='SELECT * from ' + test + 'try_db i where PPRUN="' + PPRUN + '" and OBJNAME="' + OBJNAME + '"'
        #adam-maybe# else: command_calc_good1='SELECT * from ' + test + 'try_db i where i.stats is null order by rand()'
        print 'calc_good| command_calc_good1=',command_calc_good1
        c.execute(command_calc_good1)
        results1=c.fetchall()
        print "calc_good| len(results1)=",len(results1)

	### LOOP0: loop over try_db matches with this PPRUN (should only be one)
        for line in results1:
            dtop = {}
            for i in range(len(db_keys_try)):
                dtop[db_keys_try[i]] = str(line[i])

            save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'stats':'start', 'sample':'record','sample_size':'record',},db='' + test + 'try_db')

            '''PART2| get "todo" from try_db. (this is never used for anything later) '''
            command_calc_good2="SELECT todo from " + test + "try_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'"
            print 'calc_good| command_calc_good2=',command_calc_good2
            c.execute(command_calc_good2)
            results2=c.fetchall()
            print "calc_good| len(results2)=",len(results2)
            todo = results2[0][0]
            print "calc_good| (adam-look) todo=",todo

            '''PART3| get sdss/None/bootstrap fits from try_db'''
            command_calc_good3="SELECT sdssstatus, Nonestatus, bootstrapstatus from " + test + "try_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'" # and sample_size='all'  group by sample"
            print 'calc_good| command_calc_good3=',command_calc_good3
            c.execute(command_calc_good3)
            results3=c.fetchall()
            print "calc_good| len(results3)=",len(results3)
            fit_samples = []
            sdssstatus = results3[0][0]
            if string.find(str(sdssstatus),'finished')!=-1: fit_samples.append('sdss')
            Nonestatus = results3[0][1]
            if string.find(str(Nonestatus),'finished')!=-1: fit_samples.append('None')
            bootstrapstatus = results3[0][2]
            if string.find(str(bootstrapstatus),'finished')!=-1: fit_samples.append('bootstrap')

            if len(fit_samples) == 0:
                print 'calc_good| no fits'
                save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'stats':'no fits', 'sample':'record','sample_size':'record',},db='' + test + 'try_db')
            print 'calc_good| fit_samples=',fit_samples

	    ### LOOP1: loop over sdss/None/bootstrap fits
            for sample in fit_samples:
                '''PART4| get 1 sample_size="all" fits in fit_db and CALCULATE/SAVE zpstd = std(zp_images) (for this type of sample in ["sdss","None","bootstrap"])'''
                command_calc_good4="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size='all' and sample='" + sample + "' limit 1"
                print 'calc_good| command_calc_good4=',command_calc_good4
                c.execute(command_calc_good4)
                results4=c.fetchall()
                print "calc_good| len(results4)=",len(results4)

                for line in results4:
                    drand = {}
                    for i in range(len(db_keys_fit)):
                        drand[db_keys_fit[i]] = str(line[i])
                    print 'calc_good| sample=',sample
                    zp_images = re.split(',',drand['zp_images'])
                    zpstd = scipy.std([float(zp) for zp in zp_images])
                    save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],sample + '_zpstd':zpstd, 'zp_images': drand['zp_images'], 'sample':'record','sample_size':'record',},db='' + test + 'try_db')

                '''PART5| get 1 sample_size="rand%" fit in fit_db CALCULATE/SAVE len(rots) (for this type of sample in ["sdss","None","bootstrap"])'''
                command_calc_good5="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'rand%'  and sample='" + sample + "' limit 1"
                print 'calc_good| command_calc_good5=',command_calc_good5
                c.execute(command_calc_good5)
                results5=c.fetchall()
                print "calc_good| len(results5)=",len(results5)
                for line in results5:
                    drand = {}
                    for i in range(len(db_keys_fit)):
                        drand[db_keys_fit[i]] = str(line[i])
                    rots = []
                    for rot in ['0','1','2','3','40']:
                        print 'calc_good| rot=',rot , ' drand[rot+"$1x1y"]=',drand[rot+"$1x1y"]
                        if drand[rot + '$2x2y'] != 'None':
                            rots.append(rot)
                    save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'rots': int(len(rots)), 'sample':'record','sample_size':'record',},db='' + test + 'try_db')
                '''PART6| get collection of sample_size="rand%" fits in fit_db CALCULATE/SAVE: (for this type of sample in ["sdss","None","bootstrap"])
			corr/uncorr: rejectedreducedchi
			original: var_correction (from test_correction results), mean(chi_diffs), and std(chi_diffs) | chi_diffs=reducedchi_uncorr/reducedchi_corr'''
                command_calc_good6="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'rand%' and positioncolumns is not null  and sample='" + sample + "'" # and CHIPS is not null"
                print 'calc_good| command_calc_good6=',command_calc_good6
                c.execute(command_calc_good6)
                results6=c.fetchall()
                print "calc_good| len(results6)=",len(results6)
                random_dict = {}
                epsilons = []
                for line in results6:
                    drand = {}
                    for i in range(len(db_keys_fit)):
                        drand[db_keys_fit[i]] = str(line[i])
                    name = drand['sample_size'].replace('corr','').replace('un','')
                    if not name in random_dict: random_dict[name] = {}
                    if string.find(drand['sample_size'],'corr') != -1 and string.find(drand['sample_size'],'uncorr') == -1:
                        random_dict[name]['corr'] = drand['rejectedreducedchi']
                    if string.find(drand['sample_size'],'uncorr') != -1:
                        random_dict[name]['uncorr'] = drand['rejectedreducedchi']
                    if string.find(drand['sample_size'],'orr') == -1:
                        print 'calc_good| dtop["OBJNAME"]=',dtop["OBJNAME"] , ' dtop["FILTER"]=',dtop["FILTER"] , ' dtop["PPRUN"]=',dtop["PPRUN"] , ' drand["sample"]=',drand["sample"] , ' drand["sample_size"]=',drand["sample_size"]
                        epsilon, diff_bool = test_correction(dtop['OBJNAME'],dtop['FILTER'],dtop['PPRUN'],drand['sample'],drand['sample_size'])
                        epsilons.append(epsilon)

                print 'calc_good| epsilons=',epsilons
                if len(epsilons) > 0:
                    #surfs = numpy.array(epsilons)
                    stds = numpy.std(epsilons,axis=0)
                    var_correction = numpy.median(stds.flatten().compress(diff_bool.flatten())) #sigma_jack
                    print 'calc_good| var_correction=',var_correction

                    chi_diffs = []
                    print 'calc_good| random_dict=',random_dict
                    for key in random_dict.keys():
                        print 'calc_good| key=',key,': random_dict[key].has_key("corr")=',random_dict[key].has_key("corr") , ' random_dict[key].has_key("uncorr")=',random_dict[key].has_key("uncorr")
                        print 'calc_good| BETTER BE TRUE: random_dict[key].has_key("corr") and random_dict[key].has_key("uncorr") = ', random_dict[key].has_key('corr') and random_dict[key].has_key('uncorr')
                        if random_dict[key].has_key('corr') and random_dict[key].has_key('uncorr'):
                            if random_dict[key]['corr'] != 'None' and random_dict[key]['uncorr'] != 'None' and float(random_dict[key]['corr'])!=0:
                                print 'calc_good| dtop["OBJNAME"]=',dtop["OBJNAME"] , ' dtop["PPRUN"]=',dtop["PPRUN"]
                                random_dict[key]['chi_diff'] = float(random_dict[key]['uncorr'])/float(random_dict[key]['corr'])
                                #print float(random_dict[key]['uncorr']),float(random_dict[key]['corr'])
                                #print random_dict[key]['chi_diff']
                                chi_diffs.append(random_dict[key]['chi_diff'])

                    print 'calc_good| chi_diffs=',chi_diffs
                    mean = scipy.mean(chi_diffs)
                    print 'calc_good| mean(chi_diffs)=', mean
                    std = scipy.std(chi_diffs)
                    print 'calc_good|  std(chi_diffs)=', std
                    save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],sample + '_mean':mean, sample + '_std':std, sample + '_var_correction': var_correction, 'sample':'record','sample_size':'record',},db='' + test + 'try_db')

                '''PART7| get sample_size="all" fit in fit_db and CALCULATE/SAVE sdss_imp_all=mean(sdssredchinocorr/sdssredchicorr) and match_stars (for this type of sample in ["sdss","None","bootstrap"])'''
                command_calc_good7="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size='all' and sample='sdss' "
                print 'calc_good| command_calc_good7=',command_calc_good7
                c.execute(command_calc_good7)
                results7=c.fetchall()
                print 'calc_good| len(results7)=',len(results7)
                o = {}
                if len(results7) > 0:
                    line = results7[0]
                    drand = {}
                    for i in range(len(db_keys_fit)):
                        drand[db_keys_fit[i]] = str(line[i])

                    save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],sample + '_match_stars':drand['match_stars'],'sample':'record','sample_size':'record',},db='' + test + 'try_db')
                    name = drand['sample_size'].replace('corr','').replace('un','')

                    for rot in ['0','1','2','3']:
                        if not o.has_key(rot):
                            o[rot] = {}
                        if drand['sdssredchinocorr$' + rot] != 'None':
                            o[rot]['corr'] = drand['sdssredchicorr$' + rot]
                            o[rot]['uncorr'] = drand['sdssredchinocorr$' + rot]
                    num = 0;factor = 0
                    for rot in ['0','1','2','3']:
                        #adam-old# if 'corr' in o[rot] and 'uncorr' in o[rot]:
                        if o[rot].has_key('uncorr') and o[rot].has_key('corr'):
                            if float(o[rot]['corr']) != 0:
                                factor += float(o[rot]['uncorr'])/float(o[rot]['corr'])
                                num += 1.
                    if num!=0:
                        save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'match_stars':drand['match_stars'],'sdss_imp_all':factor/num, 'sample':'record','sample_size':'record',},db='' + test + 'try_db')

                '''PART8| get sample_size="all" fit in fit_db and CALCULATE/SAVE sdss_imp=mean(sdssredchinocorr/sdssredchicorr) (for this type of sample in ["sdss","None","bootstrap"])'''
                command_calc_good8="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'allsdss%corr' "
                print 'calc_good| command_calc_good8=',command_calc_good8
                c.execute(command_calc_good8)
                results8=c.fetchall()
                print 'calc_good| len(results8)=',len(results8)
                o = {}
                if len(results8) > 0:
                    for line in results8:
                        drand = {}
                        for i in range(len(db_keys_fit)):
                            drand[db_keys_fit[i]] = str(line[i])
                        name = drand['sample_size'].replace('corr','').replace('un','')

                        for rot in ['0','1','2','3']:
                            if not o.has_key(rot):
                                o[rot] = {}
                            if drand['sdssredchinocorr$' + rot] != 'None':
                                #print 'calc_good| drand["sample_size"]=',drand["sample_size"] , ' string.find(drand["sample_size"],"uncorr")!=-1=',string.find(drand["sample_size"],"uncorr")!=-1
                                if string.find(drand['sample_size'],'corr') != -1 and string.find(drand['sample_size'],'uncorr') == -1:
                                    #if drand['sdssredchinocorr$' + rot]
                                    o[rot]['corr'] = drand['sdssredchinocorr$' + rot]
                                if string.find(drand['sample_size'],'uncorr') != -1:
                                    o[rot]['uncorr'] = drand['sdssredchinocorr$' + rot]
                    num = 0;factor = 0
                    for rot in ['0','1','2','3']:
                        #adam-old# if 'corr' in o[rot] and 'uncorr' in o[rot]:
                        if o[rot].has_key('uncorr') and o[rot].has_key('corr'):
                            if float(o[rot]['corr']) != 0:
                                factor += float(o[rot]['uncorr'])/float(o[rot]['corr'])
                                num += 1.

                    if num!=0:
                        save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'sdss_imp':factor/num, 'sample':'record','sample_size':'record',},db='' + test + 'try_db')

                ''' calculate the mean and std of the reduced chi sq improvement '''

                ''' calculate the variance in the best fit '''

                ''' retrieve all sdss tests '''

                ''' decide if good '''

                save_fit({'PPRUN':dtop['PPRUN'],'OBJNAME':dtop['OBJNAME'],'FILTER':dtop['FILTER'],'stats':'yes', 'sample':'record','sample_size':'record',},db='' + test + 'try_db')
    except:
        ns.update(locals())
        raise
    return

def test_correction(OBJNAME,FILTER,PPRUN,sample,sample_size,paper_stat=False): #step4_test_fit #intermediate
    '''inputs: OBJNAME,FILTER,PPRUN,sample,sample_size,paper_stat=False
    returns:  epsilon, diff_bool
    calls: get_a_file,get_fits
    called_by: calc_good'''

    sample = str(sample)
    sample_size = str(sample_size)

    ''' create chebychev polynomials '''
    cheby_x = [{'n':'0x','f':lambda x,y:1.},{'n':'1x','f':lambda x,y:x},{'n':'2x','f':lambda x,y:2*x**2-1},{'n':'3x','f':lambda x,y:4*x**3.-3*x}]
    cheby_y = [{'n':'0y','f':lambda x,y:1.},{'n':'1y','f':lambda x,y:y},{'n':'2y','f':lambda x,y:2*y**2-1},{'n':'3y','f':lambda x,y:4*y**3.-3*y}]
    cheby_terms = []
    cheby_terms_no_linear = []
    for tx in cheby_x:
        for ty in cheby_y:
            if not ((tx['n'] == '0x' and ty['n'] == '0y')):
                cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
            if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})

    dt = get_a_file(OBJNAME,FILTER,PPRUN)
    d = get_fits(OBJNAME,FILTER,PPRUN, sample, sample_size)

    column_prefix = ''
    position_columns_names = re.split('\,',d['positioncolumns'])
    print 'test_correction| column_prefix=',column_prefix , ' position_columns_names=',position_columns_names
    fitvars = {} ; cheby_terms_dict = {} ; ROTS_dict = {}
    for ele in position_columns_names:
        #print ele
        if type(ele) != type({}):
            ele = {'name':ele}
        res = re.split('\$',ele['name'])
        if len(res) > 1:
            ROTS_dict[res[0]] = ''
            #print res
        if string.find(ele['name'],'zp_image') == -1:
            #print sample, sample_size, ele['name']
            fitvars[ele['name']] = float(d[ele['name']])
            for term in cheby_terms:
                if len(res) > 1:
                    if term['n'] == res[1]:
                        cheby_terms_dict[term['n']] = term

    ROTS = ROTS_dict.keys()
    print 'test_correction| ROTS=',ROTS

    zp_images = re.split(',',d['zp_images'])
    zp_images_names = re.split(',',d['zp_images_names'])
    for i in range(len(zp_images)):
        fitvars[zp_images_names[i]] = float(zp_images[i])

    cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']
    coord_conv_x = lambda x:(2.*x-0-LENGTH1)/(LENGTH1-0)
    coord_conv_y = lambda x:(2.*x-0-LENGTH2)/(LENGTH2-0)

    print 'test_correction| cheby_terms_use=',cheby_terms_use , ' fitvars=',fitvars
    print 'test_correction| dt["CHIPS"]=',dt["CHIPS"]
    print 'test_correction| CHIPS=',CHIPS

    if not paper_stat: bin = 100
    else: bin = 10

    x,y = numpy.meshgrid(numpy.arange(0,LENGTH1,bin),numpy.arange(0,LENGTH2,bin))
    x_conv = coord_conv_x(x)
    y_conv = coord_conv_y(y)

    epsilon = 0
    index = 0
    ROT=ROTS[0]
    for term in cheby_terms_use:
        index += 1
        #print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
        epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x_conv,y_conv)*term['fy'](x_conv,y_conv)

    diff = ((x-LENGTH1/2.)**2.+(y-LENGTH2/2.)**2.) - (LENGTH1/2.)**2.
    diff_bool = diff[diff<0]
    diff[diff>0] = 0
    diff[diff<0] = 1
    diff2 = copy(diff)
    diff2[diff2==0] = -999 #adam-watch# somehow I get arrays that are almost entirely epsilon=[...,-999,...]
    diff2[diff2==1] = 0
    #hdu = pyfits.PrimaryHDU(diff)
    #im = '/scratch/pkelly/diff.fits'
    #os.system('rm ' + im)
    #hdu.writeto(im)
    #print 'test_correction| im =',im, '...finished...'

    if not paper_stat: epsilon = epsilon * diff + diff2
    else: pass

    flat = epsilon.flatten().compress(epsilon.flatten()[epsilon.flatten()!=0])
    print 'test_correction| numpy.median(flat)=',numpy.median(flat) , ' len(epsilon.flatten())=',len(epsilon.flatten()) , ' len(flat)=',len(flat)
    epsilon = epsilon - numpy.median(flat)
    if False:
        print 'test_correction| ...writing...'
        hdu = pyfits.PrimaryHDU(epsilon)
        #os.system('rm ' + tmpdir + 'correction' + ROT + filter + sample_size + '.fits')
        #hdu.writeto(tmpdir + '/correction' + ROT + filter + sample_size + '.fits')
        im = '/scratch/pkelly/test.fits'
        os.system('rm ' + im)
        hdu.writeto(im)
        print 'test_correction| im =',im, 'finished'
    return epsilon, diff_bool

#adam-note# step5: below here is my attempt to apply the correction and make *I.fits files!
def run_correction(OBJNAME=None,FILTER=None,PPRUN=None,r_ext=True): #step5_correct_ims #main
    '''inputs: OBJNAME=None,FILTER=None,PPRUN=None,r_ext=True (r_ext=True if you've already done the stellar halo rings, otherwise r_ext=False)
    returns: apply the correction and make *I.fits files (basically a wrapper around construct_correction, which does this:save starflat fits files
    calls: describe_db,find_nearby,construct_correction,save_fit'''

    print '\nrun_correction| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' r_ext=',r_ext
    loop = True
    while loop:

        db2,c = connect_except()
        db_keys_try = describe_db(c,['' + test + 'try_db'])

        command='SELECT * from ' + test + 'try_db where todo="good" and var_correction > 0.08 order by rand()'
        command='SELECT * from ' + test + 'try_db i where i.todo="good" and i.correction_applied!="yes" and (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
        command='SELECT * from ' + test + 'try_db i where i.correction_applied is null and not (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand() limit 1'
        command='SELECT * from ' + test + 'try_db where correction_applied="redo" group by objname order by rand()'
        command='SELECT * from ' + test + 'try_db where correction_applied is null and fix="yes" order by rand()'
        command='SELECT * from ' + test + 'try_db where correction_applied is null and (config=8 or config=9) order by rand()'
        command='SELECT * from ' + test + 'try_db where correction_applied is null and OBJNAME="HDFN" order by rand()'

        if OBJNAME is not None:
            command='SELECT * from ' + test + 'try_db i where OBJNAME="' + OBJNAME + '" and PPRUN="' + PPRUN + '" limit 1'
            loop = False
        #command='SELECT * from ' + test + 'try_db i where (i.objname like "MACS0018%") and i.pprun like "%2009%" order by rand()'
        #command='SELECT * from ' + test + 'try_db i where (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and (i.objname like "A2219%") order by rand()'
        print ' command=',command
        c.execute(command)
        results=c.fetchall()
        line = results[0]

        dtop2 = {}
        for i in range(len(db_keys_try)):
            dtop2[db_keys_try[i]] = str(line[i])

        print ' dtop2["OBJNAME"]=',dtop2["OBJNAME"] , ' dtop2["correction_applied"]=',dtop2["correction_applied"]

        illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + dtop2['FILTER'] + '/' + dtop2['PPRUN'] + '/'
        #logfile  = open(illum_dir + 'logfile','w')

        OBJNAME_use, FILTER_use, PPRUN_use = dtop2['OBJNAME'], dtop2['FILTER'], dtop2['PPRUN']

        sample = 'notselected'

        ''' if no bootstrap use good fit '''
        if dtop2['todo'] == 'good' and (string.find(dtop2['sdssstatus'],'finished') != -1 or string.find(dtop2['Nonestatus'],'finished')):
            if string.find(dtop2['sdssstatus'],'finished') != -1:
                sample = 'sdss'
            if string.find(dtop2['Nonestatus'],'finished') != -1:
                sample = 'None'
        elif dtop2['todo'] == 'bootstrap' and str(dtop2['todo']) == 'True'  :
            sample = 'bootstrap'

        print ' sample=',sample
        if sample == 'notselected':
            OBJNAME_use, FILTER_use, PPRUN_use, sample = find_nearby(dtop2['OBJNAME'],dtop2['FILTER'],dtop2['PPRUN'])
            print 'find'

        print ' parameters: sample=',sample , ' dtop2["sdssstatus"]=',dtop2["sdssstatus"] , ' dtop2["Nonestatus"]=',dtop2["Nonestatus"] , ' dtop2["bootstrapstatus"]=',dtop2["bootstrapstatus"] , ' dtop2["todo"]=',dtop2["todo"] , ' sample=',sample , ' OBJNAME_use=',OBJNAME_use , ' FILTER_use=',FILTER_use , ' PPRUN_use=',PPRUN_use , ' dtop2["OBJNAME"]=',dtop2["OBJNAME"] , ' dtop2["FILTER"]=',dtop2["FILTER"] , ' dtop2["PPRUN"]=',dtop2["PPRUN"]
        if sample!='notselected' and sample!=None:

            #stderr_orig = sys.stderr
            #stdout_orig = sys.stdout
            #sys.stdout = logfile
            #sys.stderr = logfile

            print ' dtop2["OBJNAME"]=',dtop2["OBJNAME"] , ' dtop2["FILTER"]=',dtop2["FILTER"] , ' dtop2["PPRUN"]=',dtop2["PPRUN"] , ' sample=',sample , "all" , ' OBJNAME_use=',OBJNAME_use , ' FILTER_use=',FILTER_use , ' PPRUN_use=',PPRUN_use
            construct_correction(dtop2['OBJNAME'],dtop2['FILTER'],dtop2['PPRUN'],sample,'all',OBJNAME_use,FILTER_use,PPRUN_use,r_ext=r_ext)

            #sys.stderr = stderr_orig
            #sys.stdout = stdout_orig
            #logfile.close()

        else:
            save_fit({'PPRUN':dtop2['PPRUN'],'OBJNAME':dtop2['OBJNAME'],'FILTER':dtop2['FILTER'],'sample':'record','sample_size':'record','correction_applied':'no match'},db='' + test + 'try_db')

    #if 0: #help_list[y]['primary']==None or help_list[y]['secondary']==None:
    print "run_correction| DONE with func\n"

def find_nearby(OBJNAME,FILTER,PPRUN): #step5_correct_ims #intermediate
    '''inputs: OBJNAME,FILTER,PPRUN
    returns: (use[0]['OBJNAME'],use[0]['FILTER'],use[0]['PPRUN'],sample)
    purpose: figure out the right (closest) correction to apply
    calls: describe_db,describe_db,describe_db
    called_by: run_correction'''
    print '\nfind_nearby| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN
    db2,c = connect_except()

    db_keys_illum = describe_db(c,[illum_db])
    command="SELECT * from "+illum_db+" where PPRUN='" + PPRUN + "' and OBJNAME='" + OBJNAME + "'" # and sample_size='all'" # and sample='sdss'"
    print command
    c.execute(command)
    results=c.fetchall()
    print len(results)
    for line in results:
        dtop = {}
        for i in range(len(db_keys_illum)):
            dtop[db_keys_illum[i]] = str(line[i])

    db_keys = describe_db(c,['' + test + 'fit_db','' + test + 'try_db'])
    ''' select runs with little cloud cover '''
    #command="SELECT * from ' + test + 'fit_db f left join ' + test + 'try_db t on (t.pprun=f.pprun and t.OBJNAME=f.OBJNAME) where t.zpstd<0.01 and (t.mean - 1.5*t.std) > 1.005 and t.var_correction < 0.08 and f.sample_size='all' and f.sample='sdss' and f.CONFIG='" + dtop['CONFIG'] + "' and f.FILTER='" + dtop['FILTER'] + "'"

    ''' pick runs with good statistics and no zp variations '''

    if dtop['CONFIG'] == '10_3':  # or (dtop['CONFIG'] == '9.0' and dtop['FILTER'] == 'W-J-B'):

        ''' '''

        for i in range(len(config_bonn.wavelength_groups)):
            for filt in config_bonn.wavelength_groups[i]:
                if filt == dtop['FILTER']:
                    FILTER_NUM_ZERO = i
                    break

        command="SELECT * from " + test + "fit_db f left join " + test + "try_db t on (t.pprun=f.pprun and t.OBJNAME=f.OBJNAME) where f.CONFIG='" + dtop['CONFIG'] + "'"
        print command
        c.execute(command)
        results=c.fetchall()
        use = []
        print len(results), ' # of results '
        for line in results:
            dp = {}
            for i in range(len(db_keys)):
                dp[db_keys[i]] = str(line[i])

            for i in range(len(config_bonn.wavelength_groups)):
                for filt in config_bonn.wavelength_groups[i]:
                    if filt == dp['FILTER']:
                        FILTER_NUM = i
                        break

            use.append([abs(FILTER_NUM - FILTER_NUM_ZERO),dp])

        use.sort()

        use = [x[1] for x in use]

        print use[0]['OBJNAME'], use[0]['PPRUN'], PPRUN
    else:
        ''' use B filter if U '''
        if dtop['FILTER'] == 'W-J-U': filter = 'W-J-B'
        else: filter = dtop['FILTER']

        ''' use 10_2 if 10_1 and W-J-B '''
        if dtop['CONFIG'] == '10_1' and filter == 'W-J-B':
            dtop['CONFIG'] = '10_2'

        db_keys = describe_db(c,['' + test + 'try_db'])

        if (dtop['CONFIG'] == '9.0' and dtop['FILTER'] == 'W-J-B'):
            command="SELECT * from " + test + "try_db t where sample_current is not null and (t.todo='good' or (t.todo='bootstrap' and t.bootstrap_good='True')) and t.CONFIG='" + dtop['CONFIG'] + "' and t.objname!='HDFN' order by todo desc"

        else:
            command="SELECT * from " + test + "try_db t where sample_current is not null and (t.todo='good' or (t.todo='bootstrap' and t.bootstrap_good='True')) and t.CONFIG='" + dtop['CONFIG'] + "' and t.FILTER='" + filter + "' and t.objname!='HDFN' order by todo desc"
        print command
        c.execute(command)
        results=c.fetchall()
        use = []
        print len(results), ' # of results '
        for line in results:
            dp = {}
            for i in range(len(db_keys)):
                dp[db_keys[i]] = str(line[i])
            use.append(dp)

        def use_comp(x,y):
            date = [float(q) for q in re.split('-',re.split('_',PPRUN)[0])]
            date_x = [float(q) for q in re.split('-',re.split('_',x['PPRUN'])[0])]
            date_y = [float(q) for q in re.split('-',re.split('_',y['PPRUN'])[0])]

            #print date, date_x, date_y,

            diff = lambda a,b: abs((a[0]-b[0])*365 + (a[1]-b[1])*30 + a[2]-b[2])
            diff_x = diff(date_x,date)
            diff_y = diff(date_y,date)

            if diff_x < diff_y:
                return -1
            elif diff_x == diff_y:
                return 0
            else:
                return 1

        use.sort(use_comp)

    #for k in use:
    #        print k['objname'],k['pprun'], PPRUN
    if len(use) > 0:
        print use[0]['OBJNAME'], use[0]['PPRUN'], PPRUN

        sample = 'not set'

        ''' make sure that the illumination correction is in place '''


        #if float(use[0]['bootstrap_zpstd']) < 0.01 and string.find(use[0]['bootstrapstatus'],'finished') != -1:
        #    sample = 'bootstrap'
        if False:
            if str(use[0]['None_zpstd']) != 'None':
                if float(use[0]['None_zpstd']) < 0.01 and string.find(use[0]['Nonestatus'],'finished') != -1:
                    sample = 'None'
            if str(use[0]['sdss_zpstd']) != 'None':
                if float(use[0]['sdss_zpstd']) < 0.01 and string.find(use[0]['sdssstatus'],'finished') != -1:
                    sample = 'sdss'

        sample = use[0]['sample_current']

        #print use[0]['sdssstatus'], use[0]['Nonestatus'], use[0]['bootstrapstatus']

        #print use[0:2]
        if sample != 'not set':
            return (use[0]['OBJNAME'],use[0]['FILTER'],use[0]['PPRUN'],sample)
        else: return(None,None,None,None)
    else: return(None,None,None,None)
    print "find_nearby| DONE with func\n"

def construct_correction(OBJNAME,FILTER,PPRUN,sample,sample_size,OBJNAME_use=None,FILTER_use=None,PPRUN_use=None,r_ext=True): #step5_correct_ims #main (will be #intermediate if run_correction and find_nearby are fixed)
    '''inputs: OBJNAME,FILTER,PPRUN,sample,sample_size,OBJNAME_use=None,FILTER_use=None,PPRUN_use=None,r_ext=True
    returns: save starflat fits files
    calls: save_fit,get_a_file,get_fits,save_fit,connect_except,describe_db,save_exposure,save_fit,save_fit,save_fit,save_fit
    called_by: run_correction,select_analyze'''

    print '\nconstruct_correction| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' sample=',sample , ' sample_size=',sample_size,' OBJNAME_use=',OBJNAME_use , ' FILTER_use=',FILTER_use , ' PPRUN_use=',PPRUN_use , ' r_ext=',r_ext

    if OBJNAME_use is None:
        OBJNAME_use, FILTER_use, PPRUN_use = OBJNAME, FILTER, PPRUN

    save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'sample':'record','sample_size':'record','correction_applied':'corrstarted','OBJNAME_use':OBJNAME_use,'FILTER_use':FILTER_use,'PPRUN_use':PPRUN_use,'sample_use':sample,'time':str(time.localtime())},db='' + test + 'try_db')

    try:
        #adam-needed?#sample = str(sample)
        #adam-needed?#sample_size = str(sample_size)

        ''' create chebychev polynomials '''
        cheby_x = [{'n':'0x','f':lambda x,y:1.},{'n':'1x','f':lambda x,y:x},{'n':'2x','f':lambda x,y:2*x**2-1},{'n':'3x','f':lambda x,y:4*x**3.-3*x}]
        cheby_y = [{'n':'0y','f':lambda x,y:1.},{'n':'1y','f':lambda x,y:y},{'n':'2y','f':lambda x,y:2*y**2-1},{'n':'3y','f':lambda x,y:4*y**3.-3*y}]
        cheby_terms = []
        cheby_terms_no_linear = []
        for tx in cheby_x:
            for ty in cheby_y:
                if not ((tx['n'] == '0x' and ty['n'] == '0y')): # or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})
                if not ((tx['n'] == '0x' and ty['n'] == '0y') or (tx['n'] == '0x' and ty['n'] == '1y') or (tx['n'] == '1x' and ty['n'] == '0y')) :
                    cheby_terms_no_linear.append({'n':tx['n'] + ty['n'],'fx':tx['f'],'fy':ty['f']})

        #if cov:
        #    samples = [['sdss',cheby_terms,True]] #,['None',cheby_terms_no_linear,False]] #[['None',cheby_terms_no_linear],['sdss',cheby_terms]]
        #else:
        #    samples = [['None',cheby_terms_no_linear,False]]

        samples = [['sdss',cheby_terms,True],['None',cheby_terms_no_linear,False]] #[['None',cheby_terms_no_linear],['sdss',cheby_terms]]

        dt = get_a_file(OBJNAME,FILTER,PPRUN)
        d = get_fits(OBJNAME_use,FILTER_use,PPRUN_use, sample, sample_size)

        #if d['sdss$good'] == 'y':
        #    sample = 'sdss'
        #if d['None$good'] == 'y':
        #    sample = 'None'
        #if d['bootstrap$good'] == 'y':
        #    sample = 'bootstrap'

        column_prefix = '' #sample+'$'+sample_size+'$'
        position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns'])
        fitvars = {}
        cheby_terms_dict = {}
        print 'construct_correction| column_prefix=',column_prefix , ' position_columns_names=',position_columns_names
        ROTS_dict = {}
        for ele in position_columns_names:
            print 'construct_correction| ele=',ele
            if type(ele) != type({}):
                ele = {'name':ele}
            res = re.split('\$',ele['name'])
            if len(res) > 1:
                ROTS_dict[res[0]] = ''
                print 'construct_correction| res=',res
            if string.find(ele['name'],'zp_image') == -1:
                print 'construct_correction| sample=',sample , ' sample_size=',sample_size , ' ele["name"]=',ele["name"]
                fitvars[ele['name']] = float(d[ele['name']])
                for term in cheby_terms:
                    if len(res) > 1:
                        if term['n'] == res[1]:
                            cheby_terms_dict[term['n']] = term

        ROTS = ROTS_dict.keys()
        print 'construct_correction| ROTS=',ROTS

        zp_images = re.split(',',d['zp_images'])
        zp_images_names = re.split(',',d['zp_images_names'])

        for i in range(len(zp_images)):
            fitvars[zp_images_names[i]] = float(zp_images[i])

        cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]

        CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
        print 'construct_correction| cheby_terms_use=',cheby_terms_use , ' fitvars=',fitvars
        print 'construct_correction| CHIPS=',CHIPS
        print 'construct_correction| dt.keys()=',dt.keys()
        LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']

	#adam-watch# had `per_chip = True` here before. I hope this isn't setup to run that way, since `per_chip=False` in linear_fit

        coord_conv_x = lambda x:((2.*x)-LENGTH1)/LENGTH1
        coord_conv_y = lambda x:((2.*x)-LENGTH2)/LENGTH2

        ''' make images of illumination corrections '''

        for ROT in ROTS:
	    print 'construct_correction| for ROT in ROTS: ROT=', ROT
            size_x=LENGTH1
            size_y=LENGTH2
            bin=100
            x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
            print 'construct_correction| ...calculating'
            x = coord_conv_x(x)
            y = coord_conv_y(y)

            illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT)

            epsilon = 0
            index = 0
            for term in cheby_terms_use:
                index += 1
                print 'construct_correction| index=',index , ' ROT=',ROT , ' term=',term , ' fitvars[str(ROT)+"$"+term["n"]]=',fitvars[str(ROT)+"$"+term["n"]]
                epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

            ''' save pattern w/o chip zps '''

            im = illum_dir + '/apply_nochipzps' + sample + sample_size +  test + '.fits'
            hdu = pyfits.PrimaryHDU(epsilon)

            print 'construct_correction| ...writing'
            print 'construct_correction| epsilon=',epsilon
            print 'construct_correction| im=',im
            print 'construct_correction| ...before save'
            save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,sample+'$'+sample_size+'$'+str(ROT)+'$im':im})
            print 'construct_correction| ...after save'
            hdu.writeto(im,overwrite=True)

            ''' save pattern w/ chip zps '''

	    #adam-note# I'm going to simplify this whole process a lot and shorten this code by a few hundred lines by perminantly setting trial = True. If I want the whole thing with forking/etc. then I can get it from calc_test_save.py's version of construct_correction
            for CHIP in CHIPS:

                if str(dt['CRPIX1_' + str(CHIP)]) != 'None' and fitvars.has_key('zp_' + str(CHIP)):
                    xmin = int(float(dt['CRPIX1ZERO'])) - int(float(dt['CRPIX1_' + str(CHIP)]))
                    ymin = int(float(dt['CRPIX2ZERO'])) - int(float(dt['CRPIX2_' + str(CHIP)]))
                    xmax = xmin + int(dt['NAXIS1_' + str(CHIP)])
                    ymax = ymin + int(dt['NAXIS2_' + str(CHIP)])

                    print 'construct_correction| xmin=',xmin , ' xmax=',xmax , ' xmax=',xmax - xmin , ' ymin=',ymin , ' ymax=',ymax , ' ymax-ymin=',ymax-ymin
                    print 'construct_correction| int(xmin/bin)=',int(xmin/bin) , ' int(xmax/bin)=',int(xmax/bin) , ' int(ymin/bin)=',int(ymin/bin) , ' int(ymax/bin)=',int(ymax/bin) , ' CHIP=',CHIP , ' bin=',bin , ' scipy.shape(epsilon)=',scipy.shape(epsilon)
                    print 'construct_correction| epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]=',epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                    print 'construct_correction| fitvars.keys()=',fitvars.keys()
                    print 'construct_correction| fitvars["zp_"=',fitvars["zp_" + str(CHIP)]
                    epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP)])
                    x,y = numpy.meshgrid(numpy.arange(xmin,xmax,1),numpy.arange(ymin,ymax,1))

                    x = coord_conv_x(x)
                    y = coord_conv_y(y)

                    ''' correct w/ polynomial '''
                    epsilonC = 0
                    index = 0

                    for term in cheby_terms_use:
                        index += 1
                        print 'construct_correction| index=',index , ' ROT=',ROT , ' term=',term , ' fitvars[str(ROT)+"$"+term["n"]]=',fitvars[str(ROT)+"$"+term["n"]]

                        epsilonC += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

                    ''' add the zeropoint '''
                    epsilonC += float(fitvars['zp_' + str(CHIP)])

                    ''' save pattern w/o chip zps '''

                    print 'construct_correction| ...writing/converting to linear flux units'
                    hdu = pyfits.PrimaryHDU(10.**(epsilonC/2.5))
                    im = tmpdir + '/' + str(ROT) + '_' + str(CHIP) + '.fits'
                    print 'construct_correction| im=',im
                    hdu.writeto(im,overwrite=True)

            print 'construct_correction| ...finished writing'
            ''' apply the corrections to the images '''
            db2,c = connect_except()
            command_get_files  ="select file, ROTATION from "+illum_db+" where SUPA not like '%I' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "'" # and file like '%004007%' " # and ROTATION='" + str(ROT) + "'"

            print 'construct_correction| command_get_files=',command_get_files
            c.execute(command_get_files)
            results=c.fetchall()
            files = []
            for line in results:
                files.append([float(line[1]),str(line[0])])
            db2.close()
            for rot_dat,file in files:
                print 'construct_correction| rot_dat=',rot_dat , ' file=',file
                for CHIP in CHIPS:

                    if fitvars.has_key('zp_' + str(CHIP)): hasCHIP = True
                    else: hasCHIP = False

                    RUN = re.split('\_',PPRUN)[0] #adam-watch#
                    print 'construct_correction| (adam-look) RUN=',RUN
                    p = re.compile('\_\d+O')
                    file_chip_1 = p.sub('_' + str(CHIP) + 'O',file)#.replace('.fits','.sub.fits')

                    if r_ext:
                        g = glob(file_chip_1.replace('.fits','*R*.fits'))
                    else:
                        g = glob(file_chip_1.replace('.fits','*.fits'))

                    print 'construct_correction| g=',g
                    file_chips = []
                    for l in g:
                        test_f = l.replace('.fits','.weight.fits').replace('SCIENCE','WEIGHTS').replace('.sub','').replace('III.','.').replace('II.','.').replace('IIII.','.')
                        print 'construct_correction| l=',l
                        print 'construct_correction| test_f=', test_f, ' glob(test_f)=', glob(test_f)
                        if string.find(l,'I.')== -1 and len(glob(test_f)) > 0:
                            f = l.replace('.sub','').replace('III.','.').replace('II.','.').replace('IIII.','.')
                            file_chips.append([len(f),f])
                    file_chips.sort()

                    print 'construct_correction| file_chips=',file_chips
                    file_chip = file_chips[-1][1]

                    print 'construct_correction| file_chip=',file_chip

                    if len(g) == 0:
                            raise TryDb('missing file ')

                    ooo,info = commands.getstatusoutput('dfits ' + file_chip + ' | fitsort -d ROTATION')
		    if ooo!=0: raise Exception('ERROR WITH: dfits ' + file_chip + ' | fitsort -d ROTATION')
                    print 'construct_correction| info=',info , ' file_chip=',file_chip
                    #CHIP_ROT = str(int(re.split('\s+',info)[1]))

                    file_short = re.split('\/',file_chip)[-1]
                    run_dir = re.split('\/',file_chip)[-3]

                    SUPA = re.split('\_',file_short)[0]
                    print 'construct_correction| SUPA=',SUPA

                    ''' if a calibration exposure, put in the CALIB directory '''
                    if string.find(run_dir,'CALIB') == -1:
                        use_run_dir = FILTER
                    else:
                        use_run_dir = run_dir

                    os.system('rm ' + data_root + '/' + OBJNAME + '/' + use_run_dir + '/SCIENCE/*II.fits')
                    os.system('rm ' + data_root + '/' + OBJNAME + '/' + use_run_dir + '/WEIGHTS/*II.weight.fits')

                    ''' get rid of zero-size files '''
                    print 'construct_correction| use_run_dir=',use_run_dir , ' run_dir=',run_dir , ' string.find(run_dir,"CALIB")=',string.find(run_dir,"CALIB")
                    if string.find(run_dir,'CALIB') != -1:
                        out_file =  data_root + '/' + OBJNAME + '/' + FILTER + '/SCIENCE/' +  file_short.replace('.fits','I.fits')
                        os.system('rm ' + out_file)
                        out_weight_file =  data_root + '/' + OBJNAME + '/' + FILTER + '/WEIGHTS/' +  file_short.replace('.fits','I.weight.fits')
                        os.system('rm ' + out_weight_file)
                    ''' see if there are different extensions '''
                    out_file =  data_root + '/' + OBJNAME + '/' + use_run_dir + '/SCIENCE/' +  file_short.replace('.fits','I.fits')
                    print 'construct_correction| out_file=',out_file

                    BADCCD = False
                    if glob(out_file):
                        command_dfits = 'dfits ' + file_chip + ' | fitsort BADCCD'
                        print 'construct_correction| command_dfits=',command_dfits
                        ooo,info = commands.getstatusoutput(command_dfits)
                        if ooo!=0: raise Exception( 'ERROR WITH: dfits ' + file_chip + ' | fitsort BADCCD')
                        res = re.split('\s+',info)
                        if res[3] == '1':
                            BADCCD = True
                        print 'construct_correction| BADCCD=',BADCCD

                    out_weight_file = data_root + '/' + OBJNAME + '/' + use_run_dir + '/WEIGHTS/' +  file_short.replace('.fits','I.weight.fits')
                    bad_out_weight_file =  data_root + '/' + OBJNAME + '/' + use_run_dir + '/SCIENCE/' +  file_short.replace('.fits','I.weight.fits')
                    print 'construct_correction| out_weight_file=' ,out_weight_file
                    print 'construct_correction| bad_out_weight_file=' ,bad_out_weight_file

                    flag_file = file_chip.replace('SCIENCE','WEIGHTS').replace('.fits','.flag.fits')
                    out_flag_file = data_root + '/' + OBJNAME + '/' + use_run_dir + '/WEIGHTS/' +  file_short.replace('.fits','I.flag.fits')
                    bad_out_weight_file =  data_root + '/' + OBJNAME + '/' + use_run_dir + '/SCIENCE/' +  file_short.replace('.fits','I.weight.fits')
                    os.system('rm ' + out_flag_file)
                    command_ln = 'ln -s  ' + flag_file + ' ' + out_flag_file
                    print 'construct_correction| command_ln=',command_ln
                    ooo=os.system(command_ln)
                    if ooo!=0: raise Exception("os.system==0")

                    if str(dt['CRPIX1_' + str(CHIP)]) == 'None':
                        os.system('rm ' + out_file)
                        os.system('rm ' + out_weight_file)
                    else:
                        CHIP_ROT = int(rot_dat)
                        print 'construct_correction| CHIP_ROT=',CHIP_ROT , ' ROT=',ROT,' int(CHIP_ROT)==int(ROT)=',int(CHIP_ROT) == int(ROT)
                        print 'construct_correction| filter(lambda x: int(x)==int(CHIP_ROT),ROTS)=', filter(lambda x: int(x)==int(CHIP_ROT),ROTS)
                        if not filter(lambda x: int(x)==int(CHIP_ROT),ROTS): CHIP_ROT = ROT

                        if int(CHIP_ROT) == int(ROT):
                            im = tmpdir + '/' + str(CHIP_ROT) + '_' + str(CHIP) + '.fits'
                            print 'construct_correction| im=',im
                            weight_file = file_chip.replace('SCIENCE','WEIGHTS').replace('.fits','.weight.fits')
                            flag_file = file_chip.replace('SCIENCE','WEIGHTS').replace('.fits','.flag.fits')
                            print 'construct_correction| file_chip=',file_chip, 'weight_file=',weight_file,'flag_file=',flag_file

                            directory = reduce(lambda x,y: x + '/' + y, re.split('\/',file_chip)[:-1])
                            print 'construct_correction| directory=',directory , ' file=',file

                            filter_dir = directory.replace(FILTER+'_'+RUN,FILTER)

                            print 'construct_correction| glob(out_file)=',glob(out_file) , ' out_file=',out_file

                            go = False
                            if not len(glob(out_file)): go = True
                            elif os.path.getsize(out_file) == 0: go = True
                            elif 0.98 < os.path.getsize(file_chip) / os.path.getsize(out_file) < 1.02: go = True
                            go = True
                            if go:
                                os.system('rm ' + out_file)

                                tried = 0
                                while 1:
                                    if hasCHIP:
                                        command_ic = "ic '%1 %2 *' " + file_chip + " " + im + "> " + out_file
                                    else:
                                        command_ic = "ic '%1 0 *' " + file_chip + " > " + out_file
                                    print 'construct_correction| command_ic=',command_ic
                                    code = os.system(command_ic)
                                    tried += 1
                                    if os.path.getsize(file_chip) == os.path.getsize(out_file) or tried > 4: break

                                print 'construct_correction| code=', code
                                if code != 0:
                                    raise TryDb('failed ic' + file_chip)

                                command_sethead1 = 'sethead ' + out_file + ' PPRUN_USE=' + PPRUN_use
                                print 'construct_correction| command_sethead1=',command_sethead1
                                ooo=os.system(command_sethead1)
                                if ooo!=0: raise Exception("os.system==0")
                                command_sethead2 = 'sethead ' + out_file + ' OBJNAME_USE=' + OBJNAME_use
                                print 'construct_correction| command_sethead2=',command_sethead2
                                ooo=os.system(command_sethead2)
                                if ooo!=0: raise Exception("os.system==0")

                                if BADCCD:
                                    command_sethead3 = 'sethead ' + out_file + ' BADCCD=1'
                                    print 'construct_correction| command_sethead3=',command_sethead3
                                    ooo=os.system(command_sethead3)
                                    if ooo!=0: raise Exception("os.system==0")
                                else:
                                    command_delhead = 'delhead ' + out_file + ' BADCCD'
                                    print 'construct_correction| command_delhead=',command_delhead
                                    ooo=os.system(command_delhead)
                                    if ooo!=0: raise Exception("os.system==0")
                                print 'construct_correction| BADCCD=',BADCCD

                                save_exposure({'illumination_match':sample,'time':str(time.localtime())},dt['SUPA'],dt['FLAT_TYPE'])

                            #os.system('rm ' + bad_out_weight_file) # remove this file which was accidently put there:w

                            go = False
                            print 'construct_correction| len(glob(out_weight_file))=',len(glob(out_weight_file)) , ' outweightfile'
                            if not len(glob(out_weight_file)) : go = True
                            elif os.path.getsize(out_weight_file) == 0: go = True
                            elif 0.98 < os.path.getsize(out_weight_file) / os.path.getsize(weight_file) < 1.02: go = True
                            go = True
                            if go:
                                os.system('rm ' + out_weight_file)
                                tried = 0
                                while True:
                                    if hasCHIP:
                                        command_ic = "ic '%1 %2 /' " + weight_file + " " + im + "> " + out_weight_file
                                    else:
                                        command_ic = "ic '%1 0 *' " + weight_file + " > " + out_weight_file

                                    print 'construct_correction| command_ic=',command_ic
                                    print 'construct_correction| glob(weight_file)=',glob(weight_file) , ' weight_file=',weight_file
                                    print 'construct_correction| glob(im)=',glob(im) , ' im=',im
                                    code = os.system(command_ic)

                                    tried += 1
                                    if os.path.getsize(file_chip) == os.path.getsize(out_file) or tried > 4: break

                                if code != 0:
                                    raise TryDb('failed ic' + weight_file)
                                command_sethead1wt = 'sethead ' + out_weight_file + ' PPRUN_USE=' + PPRUN_use
                                print 'construct_correction| command_sethead1wt=',command_sethead1wt
                                ooo=os.system(command_sethead1wt)
                                if ooo!=0: raise Exception("os.system==0")
                                command_sethead2wt = 'sethead ' + out_weight_file + ' OBJNAME_USE=' + OBJNAME_use
                                print 'construct_correction| command_sethead2wt=',command_sethead2wt
                                ooo=os.system(command_sethead2wt)
                                if ooo!=0: raise Exception("os.system==0")

                                if BADCCD:
                                    command_sethead3wt = 'sethead ' + out_file + ' BADCCD=1'
                                    print 'construct_correction| command_sethead3wt=',command_sethead3wt
                                    ooo=os.system(command_sethead3wt)
                                    if ooo!=0: raise Exception("os.system==0")
                                print 'construct_correction| BADCCD=',BADCCD

                            ''' now do a file integrity check '''
                            if len(glob(weight_file)):
                                if 0.98 < os.path.getsize(weight_file) - os.path.getsize(out_weight_file) < 1.02:
                                    print 'construct_correction| os.path.getsize(weight_file)=',os.path.getsize(weight_file) , ' weight_file=',weight_file , ' os.path.getsize(out_weight_file)=',os.path.getsize(out_weight_file) , ' out_weight_file=',out_weight_file
                                    raise TryDb('weight file' + str(weight_file))
        save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'sample':'record','sample_size':'record','correction_applied':'finished','OBJNAME_use':OBJNAME_use,'FILTER_use':FILTER_use,'PPRUN_use':PPRUN_use,'sample_use':sample,'time':str(time.localtime())},db='' + test + 'try_db')
    except:
        ns.update(locals()) 
	raise

    print "construct_correction| DONE with func\n"
    return

#adam-fragments_removed#
#r29:def calcBinStats(output_files_nametag, LENGTH1, LENGTH2, data,magErr, X, Y, pth,  limits=[-0.4,0.4], data_label='SUBARU-SDSS'):
#r29:adam_tmp_plots(*args):

if __name__=="__main__" and username=="awright":
	#FILTERs=["W-J-B","W-J-V","W-C-RC","W-C-IC","W-S-Z+"] #adam-Warning#
	#PPRUNs=["W-C-IC_2010-02-12", "W-C-IC_2011-01-06","W-C-RC_2010-02-12", "W-J-B_2010-02-12", "W-J-V_2010-02-12", "W-S-Z+_2011-01-06"] #adam-Warning#
	#FILTERs_matching_PPRUNs=["W-C-IC", "W-C-IC","W-C-RC", "W-J-B", "W-J-V", "W-S-Z+"] #adam-Warning#
	FILTERs=["W-J-B","W-C-RC","W-S-Z+"] #adam-Warning#
	PPRUNs=["W-S-Z+_2009-04-29","W-J-B_2009-04-29","W-J-B_2010-03-12","W-S-Z+_2010-03-12","W-C-RC_2010-03-12"]
	FILTERs_matching_PPRUNs=["W-S-Z+","W-J-B","W-J-B","W-S-Z+","W-C-RC"]
	OBJNAME=cluster #adam-Warning#

	#adam-Warning# either handle SQL tables here or at the beginning!
        #This will drop tables and re-run everything. just comment out anything above here and run :%s///g
	db2,c = connect_except()
	c.execute(" DROP TABLE adam_illumination_db ; ")
	c.execute(" DROP TABLE adam_try_db ; ")
	c.execute(" DROP TABLE adam_fit_db ; ")
	c.execute(" CREATE TABLE adam_illumination_db LIKE illumination_db; ")
	c.execute(" CREATE TABLE adam_try_db LIKE test_try_db; ")
	c.execute(" CREATE TABLE adam_fit_db LIKE test_fit_db; ")

	print "adam-look: gather_exposures(cluster,filters=FILTERs)"
	gather_exposures(cluster,filters=FILTERs)
	print "adam-look: get_astrom_run_sextract(cluster,PPRUNs=PPRUNs)"
	get_astrom_run_sextract(cluster,PPRUNs=PPRUNs)
	print "adam-look: get_sdss_cats(OBJNAME)"
	get_sdss_cats(OBJNAME)

	extra_nametag=""
	for FILTER,PPRUN in zip(FILTERs_matching_PPRUNs,PPRUNs):
	 	print "\n\nadam-look: match_OBJNAME starting on FILTER=%s PPRUN=%s\n" % (FILTER,PPRUN)
	 	match_OBJNAME(OBJNAME,FILTER,PPRUN)
		print "\n\nadam-look: calc_good starting on FILTER=%s PPRUN=%s\n" % (FILTER,PPRUN)
		calc_good(OBJNAME,FILTER,PPRUN)
	for FILTER,PPRUN in zip(FILTERs_matching_PPRUNs,PPRUNs):
		print "\n\nadam-look: testgood starting on FILTER=%s PPRUN=%s\n" % (FILTER,PPRUN)
		testgood(OBJNAME,FILTER,PPRUN)
	for FILTER,PPRUN in zip(FILTERs_matching_PPRUNs,PPRUNs):
		print "\n\nadam-look: construct_correction starting on FILTER=%s PPRUN=%s\n" % (FILTER,PPRUN)
		#adam-Warning# r_ext=True if you've already done the stellar halo rings, otherwise r_ext=False. So for MACS0416 I'll sure r_ext=True
		r_ext=False
		construct_correction(OBJNAME,FILTER,PPRUN,"sdss","all",OBJNAME,FILTER,PPRUN,r_ext=False)
	#print "\n\nadam-look: run_correction starting on FILTER=%s PPRUN=%s\n" % (FILTER,PPRUN)
	#run_correction(OBJNAME,FILTER,PPRUN)
	#Note: run_correction and find_nearby are not necessary if you know which OBJECT/PPRUN you want to fit, the fit was successful, it's in sdss, and you don't want to bootstrap/etc.
	#adam-Warning# run_correction and find_nearby will need to be fixed in order to work properly under the conditions described above 
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning
#ADVICE: ## before running simple_ic.py, I need to have OBJNAME in all images (and consistent in all images). Might as well do the same for OBJECT and MYOBJ too.  I also should rename PPRUN to PPRUN0 and have filter_run be the pattern for PPRUN
