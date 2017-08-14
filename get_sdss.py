#!/usr/bin/env python

def get_corr(image):
        psftotalpath = image.replace('corr','objcs').replace('fpC','psField').replace('-r','-').replace('-g','-').replace('-u','-').replace('-i','-').replace('-z','-')
        print psftotalpath	
        if psftotalpath[-1] == 'i': psftotalpath = psftotalpath + 't'
        #psfpath = reduce(lambda x,y: x + '/' + y,bones)
        #spath = bones[-1].replace('r','')
        #spath = spath.replace('fpC','tsField')
        #psfpath = spath.replace('tsField','psField').replace('-r','-').replace('-g','-').replace('-u','-').replace('-i','-').replace('-z','-')
        #if psfpath[-1] == 'i': psfpath = psfpath + 't'

        return psftotalpath

# Develeoped by Min-Su Shin (Princeton University)
# It requires xml2obj function.
# http://code.activestate.com/recipes/534109/

import getopt, sys
import time
import urllib
import xml2obj
import string
from config import datb, prog, path


# objname='SDSSJ001027.3-104341'
# ra="2.6141316" # deg
# dec="-10.728253" # deg
# size="4.0" # arcmin

def isfilegood(file):
    import os
    from glob import glob
    files = glob(file.replace('.gz','') + '*')
    good = 1
    if len(files) > 0: 
        print file
        print os.stat(files[0])
        print str(os.stat(files[0])[6])
        if str(os.stat(files[0])[6]) == '0':
            good = 0
    else: good = 0
    return good


def single_download(sn, ra, dec, size, gh):

    reget = False 
    import anydbm        
    dict_names = ['mustart','stripe','run','rerun','camcol','field']                                                                                                                                                                                                                                                                         
    #query = "select distinct dbo.fGetUrlFitsCFrame(fieldId,'" + filter + "'), run, rerun, camcol, field from Field where " + str(ra) + " > (raMin - 0.0211) and " + str(ra) + " < (raMax + 0.0211) and " + str(dec) + " > (decMin - 0.0211) and " + str(dec) + " < (decMax + 0.0211) and (raMax - raMin) < 1"  
                                                                                                                                                                                                                                                                                                                 
    query = "select distinct s.startMu, s.stripe, f.run, f.rerun, f.camcol, f.field from Field f JOIN segment AS s on s.segmentid=f.segmentid where " + str(ra) + " > (f.raMin - 0.0211) and " + str(ra) + " < (f.raMax + 0.0211) and " + str(dec) + " > (f.decMin - 0.0211) and " + str(dec) + " < (f.decMax + 0.0211) and (f.raMax - f.raMin) < 1"  

    query = "select distinct s.startMu, s.stripe, f.run, f.rerun, f.camcol, f.field from Field f JOIN segment AS s on s.segmentid=f.segmentid where " + str(ra) + " > (f.raMin - 0.0211) and " + str(ra) + " < (f.raMax + 0.0211) and " + str(dec) + " > (f.decMin - 0.0211) and " + str(dec) + " < (f.decMax + 0.0211) and (f.raMax - f.raMin) < 1"  

    query = "select distinct s.startMu, s.stripe, f.run, f.rerun, f.camcol, f.field from Field f JOIN segment AS s on s.segmentid=f.segmentid where " + str(ra) + " > (f.raMin - 0.04) and " + str(ra) + " < (f.raMax + 0.04) and " + str(dec) + " > (f.decMin - 0.04) and " + str(dec) + " < (f.decMax + 0.04 ) and (f.raMax - f.raMin) < 1"  

#    query = "select distinct run, rerun, camcol, field from Field mentid=f.fieldid where " + str(ra) + " > (f.raMin - 0.0211) and " + str(ra) + " < (f.raMax + 0.0211) and " + str(dec) + " > (f.decMin - 0.0211) and " + str(dec) + " < (f.decMax + 0.0211) and (f.raMax - f.raMin) < 1"  
                                                                                                                                                                                                                                                                                                                 
    #query = "select dbo.fGetUrlFitsCFrame(fieldId,'" + filter + "'),raMin,raMax,decMin,decMax from Field where " + str(ra) + " > (raMin) and " + str(ra) + " < (raMax) and " + str(dec) + " > (decMin) and " + str(dec) + " < (decMax)"  
    import sqlcl
    import time, os
    #time.sleep(1.1)
    lines = sqlcl.query(query).readlines()

    print query
    print lines
    dicts = []     
    for line in lines[1:]:
        dict = {}
        line = line.replace('\n','')
        import re
        res = re.split(',',line)
        print res
        for i in range(len(res)): 
            if dict_names[i] != 'image':
                dict[dict_names[i]] = int(res[i])
        print dict
        dicts.append(dict)

    downlpsf = 0
    downldff = 0

    for filter in ['i','u','g','r','z']:
        os.system('mkdir ' + path + sn )
        os.system('mkdir ' + path + sn + '/SDSS/')
        os.system('mkdir ' + path + sn + '/SDSS/' + filter)

        import os , re                                                     
        #os.system('rm ' + path + sn + '/SDSS/' + filter + '/*')
        psFields = []
        fpCs = []
        for dict in dicts:
            print dict
            psField = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/objcs/%(camcol)d/psField-%(run)06d-%(camcol)d-%(field)04d.fit" % dict      

            ps_destination = path + 'imaging/inchunk_best/new/psField-%(run)06d-%(camcol)d-%(field)04d.fit' % dict

            #tsField = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/calibChunks/%(camcol)d/tsField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit" % dict 

            drField = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/dr/%(camcol)d/drField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit" % dict 
            dr_destination = path + 'imaging/inchunk_best/new/drField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit' % dict
            dr_directory = path + 'imaging/%(run)d/%(rerun)d/dr/%(camcol)d/' % dict
            os.system('mkdir -p ' + dr_directory)



            #nfCalib = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/nfcalib/%(camcol)d/nfCalib-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit" % dict 

            #nfCalib = 'http://das.sdss.org/imaging/%(run)d/%(rerun)d/nfcalib/fcPCalib-%(run)06d-%(camcol)d.fit' % dict

            #nf_destination = path + 'imaging/inchunk_best/new/fcPCalib-%(run)06d-%(camcol)d.fit' % dict
            #nf_directory = path + 'imaging/%(run)d/%(rerun)d/nfcalib/%(camcol)d/' % dict
            #os.system('mkdir -p ' + nf_directory)


            tsField = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/calibChunks/%(camcol)d/tsField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit" % dict 

            ts_destination = path + "/imaging/inchunk_best/stripe%(stripe)d_mu%(mustart)d_1/%(camcol)d/tsField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit" % dict 

            ts_directory = path + "/imaging/inchunk_best/stripe%(stripe)d_mu%(mustart)d_1/%(camcol)d/" % dict 

            os.system('mkdir -p ' + ts_directory)


            dict['filter'] = filter 
            fpC = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/corr/%(camcol)d/fpC-%(run)06d-%(filter)s%(camcol)d-%(field)04d.fit.gz" % dict
            local_fpC = "fpC-%(run)06d-%(filter)s%(camcol)d-%(field)04d.fit" % dict

            print psField, fpC, local_fpC 
            fpCs.append({'tsField':tsField,'fpC':fpC,'psField':psField,'local_fpC':local_fpC,'ts_destination':ts_destination,'ps_destination':ps_destination,'dr_destination':dr_destination,'drField':drField})

        for image in fpCs: 
            print image
            #print get_corr(image) 
            from glob import glob                                                      
                                                                            
            #fits_url = fields[dict['url']].data[i] 
            #print fits_url
            out_fn_fits = path + sn + '/SDSS/' + filter + '/' + image['local_fpC'] + '.gz'

            os.system('rm ' + path + sn + '/SDSS')
            os.system('mkdir -p ' + path + sn + '/SDSS/' + filter + '/')
           
            #time.sleep(1.1)
            if not isfilegood(out_fn_fits.replace('.gz','') + '*') or reget:
                os.system('rm ' + out_fn_fits )
                os.system('rm ' + out_fn_fits[:-3] )
                print "downloading..."+out_fn_fits                  
                command = 'wget "' + image['fpC'] + '" -x -O '  + out_fn_fits
                print command
                os.system(command)
                print 'done'
                os.system('gunzip ' + out_fn_fits )

                
            if isfilegood(out_fn_fits.replace('.gz','') + '*'):

                #os.system('mkdir ' + image['destination'] )                                                                                                   

                print isfilegood(image['ps_destination']+ '*')
                if not isfilegood(image['ps_destination']+ '*') or reget:
                    command = 'wget "' + image['psField'] + '" -x -O '  + image['ps_destination']  
                    print command
                    os.system(command)
                    downlpsf = 1


                if not isfilegood(image['ts_destination']+ '*') or reget:
                    command = 'wget "' + image['tsField'] + '" -x -O '  + image['ts_destination']  
                    print command
                    os.system(command)
                    downlpsf = 1

                                                                                                                                                               
                
                if not isfilegood(image['dr_destination'] + '*') or reget:
                    command = 'wget "' + image['drField'] + '" -x -O '  + image['dr_destination']  
                    print command
                    os.system(command)
                    downldff = 1
                                                                                                                                                               
                if isfilegood(image['dr_destination']):                                                                                                             
                    command = 'sethead ' + out_fn_fits.replace('.gz','') + ' SNAM="' + image['dr_destination'].replace('.gz','') + '"' 
                else: 
                    command = 'sethead ' + out_fn_fits.replace('.gz','') + ' SNAM="' + image['ts_destination'].replace('.gz','') + '"' 
                print command
                os.system(command)
                                                                                                                                        
                for key in dict.keys():                                                                            
                    command = 'sethead ' + out_fn_fits.replace('.gz','') + ' ' + key + '="' + str(dict[key]) + '"'
                    print command
                    os.system(command)
                os.system('gunzip ' + out_fn_fits )
                import commands
                dateobs = commands.getoutput('gethead ' + out_fn_fits.replace('.gz','') + ' DATE-OBS')
                print dateobs
                import testdateper
                gh = anydbm.open(datb + sn,'c')
                if gh.has_key('mlcs17'):                        
                        status = testdateper.assigncodemal(sn,gh,6.6,1,img=out_fn_fits.replace('.gz',''))
                else:                        
                        status = testdateper.assigncodemal(sn,gh,12,3,img=out_fn_fits.replace('.gz',''))
                                                                                                                                        
                if status == 'bad': 
                    gh['onebadimage'] = 'yes' 
                if status == 'good':
                    gh['onegoodimage'] = 'yes' 
                gh.close()
                                                                                                                                                               
                print image
                print len(glob(image['ts_destination']+ '*'))



def run():
    import anydbm
    from config import datb
    import os
    os.chdir(os.environ['util'])
    infn="snert"
    infp=open(infn, 'r')
    while 1:
        oneline = infp.readline()
        if not oneline: break
        parts = string.split(oneline)
        sn = parts[0]
        import colorlib
        gh = anydbm.open(datb + sn,'c')
        ra = gh['galradeg']
        dec = gh['galdecdeg'] 
        size = "0.01"
        gh['SDSS_downloaded'] = 'try'
        result = single_download(sn, ra, dec, size, gh)
        gh['SDSS_downloaded'] = 'yes'
        gh.close()
    infp.close()
    return result

def run_single(sn,gh):
    import anydbm
    from config import datb
    import os, sys
    os.chdir(os.environ['util'])
    import colorlib
    colorlib.galaxyposition(sn,gh)
    ra = gh['galradeg']
    dec = gh['galdecdeg'] 
    size = "0.01"
    result = single_download(sn, ra, dec, size, gh)
    gh['2MASS_downloaded'] = 'yes'




if __name__ == '__main__':
    import anydbm
    from config import datb
    import os, sys
    os.chdir(os.environ['util'])
    sn = sys.argv[1] 
    import colorlib
    colorlib.asiago(sn)

    os.system('mkdir -p ' + os.environ['sdss'] + '/' + sn + '/')
    SDSS_dir = os.environ['sdss'] + '/' + sn + '/SDSS'
    os.system('rm -rf ' + SDSS_dir)
    os.system('mkdir -p ' + SDSS_dir.replace('mosquitocoast','Big') )
    command = 'ln -s ' + SDSS_dir.replace('mosquitocoast','Big') + ' ' + SDSS_dir        
    print command
    os.system(command)
    #os.system(' -r ' + SDSS_dir.replace('mosquitocoast','Big') + ' ' + SDSS_dir)
    import colorlib
    colorlib.asiago(sn)
    colorlib.galaxyposition(sn)
    gh = anydbm.open(datb + sn,'c')
    if not gh.has_key('snradeg'):
        colorlib.snposition(sn)
        ra = gh['snradeg']                        
        dec = gh['sndecdeg'] 
        size = "0.01"
        print ra,dec,gh['sndecdeg'],gh['snradeg']
    else:
        ra = gh['galradeg']                        
        dec = gh['galdecdeg'] 
        size = "0.01"

    gh['SDSS_downloaded'] = 'try'
    result = single_download(sn, ra, float(dec), size, gh)
    gh['SDSS_downloaded'] = 'yes'
    gh.close()
    os.chdir(os.environ['util']) 
    os.system('python coadd_SDSS.py '  + sn)
    ''' erase input files '''
    #os.system('mv ' + SDSS_dir + ' ' + SDSS_dir.replace('mosquitocoast','Big'))

