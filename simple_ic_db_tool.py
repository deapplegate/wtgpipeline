#! /usr/bin/env python
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning
import pickle, sys, os, re, time, string, math
import random, tempfile, traceback, commands
import MySQLdb

from copy import copy
from glob import glob
import astropy, astropy.io.fits as pyfits, scipy, pylab, numpy
from astropy.table import Table
import config_bonn #only need "wavelength_groups"
import utilities
import bashreader #only need "parseFile"
global data_path, tmpdir, test
username = os.environ['USER']
if username=="awright":
        ## get/set env variables
        data_root = '/gpfs/slac/kipac/fs1/u/awright/SUBARU/' #Warning#
        if 'SUBARUDIR' in os.environ.keys():
                if "pat" in os.environ['SUBARUDIR']: raise Exception("You have /nfs/slac/g/ki/ki18/anja/SUBARU/pat/ as your SUBARUDIR, this is a mistake right?")
        else:
                os.environ['SUBARUDIR']=data_root
        if 'cluster' in os.environ.keys():
                cluster=os.environ['cluster']
	#cluster="MACS0429-02"
	cluster="RXJ2129"
        cluster = 'MACS1226+21'

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
        os.environ['bonn']='/u/ki/awright/wtgpipeline/' #adam-Warning#

elif username=="pkelly":
        data_root = '/nfs/slac/g/ki/ki18/anja/SUBARU/pat/'
        data_path = data_root + 'MACS1226+21/' #adam-Warning#
        test = 'test_'
        illum_db="illumination_db"

#adam-note# the program paths used in simple_ic.py should be taken from progs.ini for the sake of consistency, since os.system kinda uses whatever paths it wants!
#adam-note# program paths in progs.ini used in this code: "p_sex","p_ldacconv","p_ldactoasc","p_ldaccalc","p_dfits","p_asctoldac","p_ldacjoinkey","p_ldacfilter","p_ldacaddkey","p_associate","p_makessc"
#adam-note# programs used in simple_ic.py: progs=["sex","ldacconv","ldactoasc","ldaccalc","dfits","asctoldac","ldacjoinkey","ldacfilter","ldacaddkey","associate","make_ssc"]
progs_path= bashreader.parseFile(os.environ['bonn']+'/progs.ini') #adam-Warning# both use my progs.ini file so that we have a consistent set of catalogs/files


#adam-Warning# If you're not working at SLAC you're probably going to use a different mysqldb
mysqldb_params = {'db' : 'subaru',
                  'user' : 'weaklensing',
                  'passwd' : 'darkmatter',
                  'host' : 'ki-sr01'}

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

db2,c = connect_except()
def get_db_obj(db,cluster):
	'''dbs=["adam_illumination_db","adam_try_db","adam_fit_db","sdss_db","adamPAN_illumination_db","adamPAN_try_db","adamPAN_fit_db","panstarrs_db","illumination_db","test_try_db","test_fit_db","try_db","fit_db"]
	clusters=["MACS0429-02","RXJ2129","MACS1226+21"]'''
	command='SELECT * from ' +  db  + " where OBJNAME='" +cluster + "'"
	Nresults=c.execute(command)
	results =c.fetchall()
	#c.execute("SELECT OBJNAME from sdss_db where OBJNAME = '" + OBJNAME + "'")
	print cluster,db,Nresults
	keys=describe_db(c,[db])
	db_results = {}
	for k in keys:
		db_results[k]=[]
	for line in results:
		for i in range(len(keys)):
			db_results[keys[i]].append(line[i])
	print ' db_results.values()=',db_results.values()
	print ' db_results.keys()=',db_results.keys()
	dbtab=Table(db_results.values(),names=db_results.keys())
	return dbtab

#def get_dbs_objs(dbs=["adam_illumination_db","adam_try_db","adam_fit_db","sdss_db","adamPAN_illumination_db","adamPAN_try_db","adamPAN_fit_db","panstarrs_db","illumination_db","test_try_db","test_fit_db","try_db","fit_db"], clusters=["MACS0429-02","RXJ2129","MACS1226+21"])
#        if type(dbs)==list:

#FILTERs=["W-J-B","W-J-V","W-C-RC","W-C-IC","W-S-Z+"]
#PPRUNs=["W-C-IC_2010-02-12", "W-C-IC_2011-01-06","W-C-RC_2010-02-12", "W-J-B_2010-02-12", "W-J-V_2010-02-12", "W-S-Z+_2011-01-06"]
#FILTERs_matching_PPRUNs=["W-C-IC", "W-C-IC","W-C-RC", "W-J-B", "W-J-V", "W-S-Z+"] 
#FILTERs=["W-J-B","W-C-RC","W-S-Z+"] 
#PPRUNs=["W-S-Z+_2009-04-29","W-J-B_2009-04-29","W-J-B_2010-03-12","W-S-Z+_2010-03-12","W-C-RC_2010-03-12"]
#FILTERs_matching_PPRUNs=["W-S-Z+","W-J-B","W-J-B","W-S-Z+","W-C-RC"]
FILTERs=["W-J-B","W-C-RC","W-S-Z+"] #adam-Warning#
FILTERs_matching_PPRUNs=["W-J-B","W-C-RC","W-S-Z+"]
PPRUNs=["W-J-B_2010-11-04","W-C-RC_2012-07-23","W-S-Z+_2010-11-04"]
OBJNAME=cluster #adam-Warning#

good_tracker={}
#for FILTER,PPRUN in zip(FILTERs_matching_PPRUNs,PPRUNs):
#	good_tracker[FILTER]=testgood(OBJNAME,FILTER,PPRUN)
#command='SELECT * from '+illum_db+' where  pasted_cat is null and OBJNAME like "'+OBJNAME+'%" and PPRUN="'+PPRUN+'"' #  order by rand()' #fwhm!=-999 and objname not like "%ki06%" order by rand()'
#command='ALTER TABLE '+illum_db+' ADD ' + column + ' varchar(240)'
#command='ALTER TABLE '+illum_db+' ADD ' + column + ' float(30)'
#command="INSERT INTO "+illum_db+" (SUPA,FLAT_TYPE) VALUES ('" + dict_save['SUPA'] + "','" + dict_save['FLAT_TYPE'] + "')"
#command="UPDATE "+illum_db+" set " + vals + " WHERE SUPA='" + dict_save['SUPA'] + "' AND FLAT_TYPE='" + dict_save['FLAT_TYPE'] + "'"
#command="SELECT * from "+illum_db+" where SUPA='" + SUPA + "'" # AND FLAT_TYPE='" + FLAT_TYPE + "'"
#command="select * from " + test + "try_db t where t.sdssstatus is null and t.Nonestatus is null and (config='8.0' or config='9.0') group by t.objname, t.pprun order by rand()"
#command="select i.* from "+illum_db+" i where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.PPRUN='" + dtop['PPRUN'] + "' and i.pasted_cat is not null  GROUP BY i.pprun,i.filter,i.OBJNAME ORDER BY RAND() limit 1 " # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
#command="create temporary table temp as select * from "+illum_db+" group by objname, pprun "
#command="SELECT * from "+illum_db+" where  file not like '%CALIB%' and  PPRUN !='KEY_N/A'  and OBJNAME like '" + OBJNAME + "' and FILTER like '" + FILTER + "' and PPRUN='" + PPRUN + "' GROUP BY pprun,filter,OBJNAME" # ORDER BY RAND()" # and PPRUN='2006-12-21_W-J-B' GROUP BY OBJNAME,pprun,filter"
#command="SELECT * from " + test + "try_db f  where f.OBJNAME='" + dtop['OBJNAME'] + "' and f.PPRUN='" + dtop['PPRUN'] + "' limit 1"
#command_supa="SELECT * from "+illum_db+" i left join " + test + "fit_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and i.PPRUN='" + dtop['PPRUN'] + "' and badccd!=1 group by i.supa"
#command="SELECT * from " + test + "fit_db i  where i.OBJNAME='" + dtop['OBJNAME'] + "' and (i.sample_size='all' and i.sample='" + str(match) + "' and i.positioncolumns is not null) and i.PPRUN='" + dtop['PPRUN'] + "'"
#command="select cov from sdss_db where OBJNAME='" + dict_sdss['OBJNAME'] + "'"
#command="select cov from sdss_db where OBJNAME='" + dict_sdss['OBJNAME'] + "'"
#command="SELECT * from " + test + "fit_db where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and sample='" + str(sample) + "' and sample_size='" + str(sample_size) + "'"
#command="SELECT * from "+illum_db+" LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".SUPA like 'SUPA%' and "+illum_db+".OBJNAME like '%" + OBJNAME + "%' and "+illum_db+".pasted_cat is not null GROUP BY "+illum_db+".OBJNAME" # LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".OBJNAME is not null  GROUP BY "+illum_db+".OBJNAME" #and sdss_db.cov is not NULL
#command="SELECT * from "+illum_db+" LEFT OUTER JOIN sdss_db on sdss_db.OBJNAME="+illum_db+".OBJNAME where "+illum_db+".SUPA like 'SUPA%' and "+illum_db+".pasted_cat is not null GROUP BY "+illum_db+".OBJNAME" 
#command='ALTER TABLE sdss_db ADD ' + column + ' varchar(240)'
#command='ALTER TABLE sdss_db ADD ' + column + ' float(30)'
#command="INSERT INTO sdss_db (OBJNAME) VALUES ('" + OBJNAME + "')"
#command="UPDATE sdss_db set " + vals + " WHERE OBJNAME='" + OBJNAME + "'"
#command="SELECT * from "+illum_db+" where FILTER='" + FILTER + "' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and CHIPS is not null limit 1"
#command_testgood1="SELECT * from ' + test + 'try_db where todo='good' and var_correction > 0.08 order by rand()"
#command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null and (i.sdssstatus like "%finished" or i.Nonestatus like "%finished") and (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
#command_testgood1='SELECT * from ' + test + 'try_db i where i.todo is null order by rand()' # and (i.objname like "A68%" and i.pprun like "2007-07-18_W-J-B")' # or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
#command_testgood1="select * from " + test + "try_db where OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "' and  FILTER='" + FILTER + "'"
#command_testgood2="SELECT * from "+illum_db+" i left join " + test + "try_db f on (i.pprun=f.pprun and i.OBJNAME=f.OBJNAME) where i.OBJNAME='" + dtop['OBJNAME'] + "' and i.pasted_cat is not NULL and (f.sdssstatus is not null or f.Nonestatus is not null) and ((f.sdssstatus!='failed' or f.sdssstatus is null) and (f.Nonestatus is null or f.Nonestatus!='failed')) group by f.pprun"
#command_sort_results1="SELECT todo from " + test + "try_db where OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and PPRUN='" + rotation_runs[y]['PPRUN'] + "'"
#command_sort_results2="SELECT sample from " + test + "fit_db where OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and PPRUN='" + rotation_runs[y]['PPRUN'] + "' and sample_size='all'  group by sample"
#command_sort_results3="SELECT * from " + test + "fit_db where PPRUN='" + rotation_runs[y]['PPRUN'] + "' and OBJNAME='" + rotation_runs[y]['OBJNAME'] + "' and sample_size='all'" # and sample='sdss'"
#command_calc_good1='SELECT * from ' + test + 'try_db i where PPRUN="' + PPRUN + '" and OBJNAME="' + OBJNAME + '"'
#command_calc_good2="SELECT todo from " + test + "try_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'"
#command_calc_good3="SELECT sdssstatus, Nonestatus, bootstrapstatus from " + test + "try_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "'" # and sample_size='all'  group by sample"
#command_calc_good4="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size='all' and sample='" + sample + "' limit 1"
#command_calc_good5="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'rand%'  and sample='" + sample + "' limit 1"
#command_calc_good6="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'rand%' and positioncolumns is not null  and sample='" + sample + "'" # and CHIPS is not null"
#command_calc_good7="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size='all' and sample='sdss' "
#command_calc_good8="SELECT * from " + test + "fit_db where OBJNAME='" + dtop['OBJNAME'] + "' and PPRUN='" + dtop['PPRUN'] + "' and sample_size like 'allsdss%corr' "
#command='SELECT * from ' + test + 'try_db where todo="good" and var_correction > 0.08 order by rand()'
#command='SELECT * from ' + test + 'try_db i where i.todo="good" and i.correction_applied!="yes" and (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand()'
#command='SELECT * from ' + test + 'try_db i where i.correction_applied is null and not (i.objname like "MACS0018%" or i.objname like "MACS0025%" or i.objname like "MACS0257%" or i.objname like "MACS0454%" or i.objname like "MACS0647%" or i.objname like "MACS0717%" or i.objname like "MACS0744%" or i.objname like "MACS0911%" or i.objname like "MACS1149%" or i.objname like "MACS1423%" or i.objname like "MACS2129%" or i.objname like "MACS2214%" or i.objname like "MACS2243%" or i.objname like "A2219" or i.objname like "A2390") order by rand() limit 1'
#command='SELECT * from ' + test + 'try_db where correction_applied="redo" group by objname order by rand()'
#command='SELECT * from ' + test + 'try_db where correction_applied is null and fix="yes" order by rand()'
#command='SELECT * from ' + test + 'try_db where correction_applied is null and (config=8 or config=9) order by rand()'
#command='SELECT * from ' + test + 'try_db where correction_applied is null and OBJNAME="HDFN" order by rand()'
#command='SELECT * from ' + test + 'try_db i where OBJNAME="' + OBJNAME + '" and PPRUN="' + PPRUN + '" limit 1'
#command="SELECT * from "+illum_db+" where PPRUN='" + PPRUN + "' and OBJNAME='" + OBJNAME + "'" # and sample_size='all'" # and sample='sdss'"
#command="SELECT * from " + test + "fit_db f left join " + test + "try_db t on (t.pprun=f.pprun and t.OBJNAME=f.OBJNAME) where f.CONFIG='" + dtop['CONFIG'] + "'"
#command="SELECT * from " + test + "try_db t where sample_current is not null and (t.todo='good' or (t.todo='bootstrap' and t.bootstrap_good='True')) and t.CONFIG='" + dtop['CONFIG'] + "' and t.objname!='HDFN' order by todo desc"
#command="SELECT * from " + test + "try_db t where sample_current is not null and (t.todo='good' or (t.todo='bootstrap' and t.bootstrap_good='True')) and t.CONFIG='" + dtop['CONFIG'] + "' and t.FILTER='" + filter + "' and t.objname!='HDFN' order by todo desc"
#command_get_files ="select file, ROTATION from "+illum_db+" where SUPA not like '%I' and OBJNAME='" + OBJNAME + "' and PPRUN='" + PPRUN + "'" # and file like '%004007%' " # and ROTATION='" + str(ROT) + "'"
#c.execute("SELECT OBJNAME from sdss_db where OBJNAME = '" + OBJNAME + "'")

#c.execute(" DROP TABLE adam_illumination_db ; ")
#c.execute(" DROP TABLE adam_try_db ; ")
#c.execute(" DROP TABLE adam_fit_db ; ")
#c.execute(" CREATE TABLE adam_illumination_db LIKE illumination_db; ")
#c.execute(" CREATE TABLE adam_try_db LIKE test_try_db; ")
#c.execute(" CREATE TABLE adam_fit_db LIKE test_fit_db; ")

## mess with SQL databases
#sql databases used by pat: illumination_db, test_try_db, test_fit_db, sdss_db
#sql databases used by adam: adam_illumination_db, adam_try_db, adam_fit_db, sdss_db

dbs=["adam_illumination_db","adam_try_db","adam_fit_db","sdss_db","adamPAN_illumination_db","adamPAN_try_db","adamPAN_fit_db","panstarrs_db","illumination_db","test_try_db","test_fit_db","try_db","fit_db"]
dbs=["adam_illumination_db","adam_try_db","adam_fit_db","sdss_db","adamPAN_illumination_db","adamPAN_try_db","adamPAN_fit_db","panstarrs_db","illumination_db","test_try_db","test_fit_db","try_db","fit_db"]
clusters=["MACS0429-02","RXJ2129","MACS1226+21"]
db_keys={}
for db in dbs:
	db_keys[db]=describe_db(c,[db])

keys=describe_db(c,[illum_db])
for cluster in clusters:
	for db in dbs:
		#command='SELECT * from ' +  db  + ' where todo="good"'+ " and OBJNAME='" +cluster + "'"
		command="SELECT OBJNAME from " +  db  + " where OBJNAME='" +cluster + "'"
		try:
			results=c.execute(command)
		except:
			continue
		#results = c.fetchall()
		#c.execute("SELECT OBJNAME from sdss_db where OBJNAME = '" + OBJNAME + "'")
		print cluster,db,results

def db_cluster_logfile(db=test+'try_db',cluster='RXJ2129'):
	trytab=get_db_obj(db,cluster)
	allnames=trytab.colnames
	t=trytab.copy()
	tfl=trytab['logfile'][0].split('ILLUMINATION')[0]+'logfile'
	keepnames=['OBJNAME',"PPRUN","var_correction","mean","std","match_stars","sdss_imp","sdss_imp_all","panstarrs_imp","panstarrs_imp_all","todo"]
	for name in allnames:
	    if not name in keepnames:
		t.remove_column(name)
	t.write(tfl+'_'+db,format='ascii.fixed_width')

	#t.write(data_path+'/PHOTOMETRY/ILLUMINATION/fit_quality_check.txt',format='ascii.fixed_width')
