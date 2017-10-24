#!/usr/bin/env python
import ldac, getopt, sys, os, glob

def make_eazy_filter_file(filterlist):


    f = open('test.RES','w')
    f_info = open('test.RES.info','w')
    f_translate = open('zphot.translate','w')
    line_c = 1
    i = 0
    for filter_name in filterlist:
        i += 1
        f_translate.write('f_' + filter_name + ' F' + str(i) + '\n')
        f_translate.write('e_' + filter_name + ' E' + str(i) + '\n')
        o = open(os.environ['BPZPATH'] + '/FILTER/' + filter_name + '.res','r').readlines()
        f_info.write(str(i) + ' ' + str(line_c) + ': ' + str(len(o)) + ' ' + filter_name + '\n') 
        line_c += (1 + len(o))
        f.write(str(len(o)) + ' ' + filter_name + ' total system response (should be!)\n')
        f.write(reduce(lambda x,y: x + y,['   ' + str(q[0]) + ' ' + str(q[1]) for q in zip(range(1,len(o)+1),o)]))
    f.close()
    f_info.close()
    f_translate.close()

def run(command,to_delete=[]):
    for file in to_delete: 
        if glob.glob(file):
            os.system('rm ' + file)
    print command
    os.system(command)


def conditions(object,filterlist):
    for filter_name in filterlist:
        if object['Flag_'+filter_name + '_data'] !=0:
            return 0
        elif object['IMAFLAGS_ISO_'+filter_name + '_data'] !=0: 
            return 0

    return 1


class file_iter:
    def __init__(self,name):
        self.name = name
        self.suffix = 1
        self.file = self.name + str(self.suffix) 
    def next(self):
        self.suffix += 1    
        self.file = self.name + str(self.suffix) 
        return self.file
    def __iter__(self):
        self.file = self.name + str(self.suffix) 








''' select a random subsample of objects to adjust training band zeropoints '''
def select_random(filterlist, fulltable,train_filters, magtype):
    print len(fulltable)

    ''' first need to keep only galaxies with decent S/N '''
                                                                                            
    import scipy, random

    #print fulltable.columns#.has_key('MAGERR_ISO-'+train_filters[1]+'_data')

    ''' removed this b/c HDFN has two B-band which don't always overlap -- if just training on u-band OK '''
    ''' hopefully have fixed this problem -- union not intersection '''
    
    if True:
        length = len(fulltable.field('SeqNr'))
        randvec = scipy.array([random.random() for ww in range(length)])
        has_a_good_measurement = scipy.zeros(len(fulltable),dtype=int)
        for f in filterlist:  
            for f2 in train_filters:
                if f == f2:
                    backup_array = fulltable.field('MAGERR_' + magtype + '-'+f2+'')[:]              
                    mask = backup_array < 0.1
                    temptable = fulltable[mask]
                    goodnum = len(temptable)

                    masktot = (backup_array < 0.1) * (randvec < 10000./goodnum)

                    print f2, masktot.sum(), goodnum
                    
                    has_a_good_measurement[masktot] = 1

    fulltable = fulltable[has_a_good_measurement==1]
    #length = len(fulltable.field('SeqNr'))
    #randvec = scipy.array([random.random() for ww in range(length)])
    #mask = randvec < (10000./length) 
    #fulltable = fulltable[mask]
                                                                                            
    print len(fulltable)


    
    return fulltable

def doit(cluster,DETECT_FILTER,filterlist,inputcat,speccat,outspeccat,outfullcat,spec,varname,errvarname,magtype,train_filters=[],correction_dict={},randsample=False, magflux='MAG',quickHDFN=True,inputcat_zlist=None):


    make_eazy_filter_file(filterlist,)

    print filterlist,inputcat,speccat,outspeccat,outfullcat,varname,errvarname
    matchedcat = "tmp_matched.cat" + cluster
    scale=3631.0e-23
    
    import os 
    import astropy.io.fits as pyfits
    print inputcat
    core = pyfits.open(inputcat)['OBJECTS'] # ???
    fulltable = core.data        

    print len(core.data)        

    print spec    

    run_list = [['all',core,outfullcat,'',inputcat]]

    print run_list

    print inputcat
    
    #spec = False

    if spec:
        print speccat
        specfile = file_iter(speccat+'spec')                                                                                       
        from glob import glob
        if not glob(speccat): 
            print 'NO SPECTRA FILE'
            raise Exception

        os.system('rm ' + specfile.file[:-1] + '*')
        os.system('cp '+ speccat +' '+specfile.file)
        
        run("ldacrentab -i " + specfile.file + " -t OBJECTS STDTAB FIELDS NULL -o " + specfile.next(),[specfile.file])
        run("ldacrenkey -i " + specfile.file  + " -t STDTAB -k Ra ALPHA_J2000 Dec DELTA_J2000 Z z -o " + specfile.next(),[specfile.file])
        run("ldaccalc -i " + specfile.file + " -t STDTAB -c '(Nr);'  -k LONG -n SeqNr '' -o " + specfile.next(),[specfile.file] )
                                                                                                                                   
        print specfile.file
                                                                                                                                   
        #    inputtable = ldac.openObjectFile(inputcat)
                                                                                                                                   
        run("ldacrentab -i " + inputcat + " -t OBJECTS STDTAB  -o " + inputcat+str(1),\
            [inputcat+str(1)])

        if os.environ['USER'] == 'dapple':            
            os.chdir('/a/wain001/g.ki.ki02/dapple/pipeline/wtgpipeline/')
            print os.environ['USER'], os.system('pwd')
            command = "./match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + inputcat+str(1)  + " data "                                                                                                                       
        else: 
            os.chdir('/u/ki/pkelly/pipeline/wtgpipeline/')
            print os.environ['USER'], os.system('pwd')

            command = "/u/ki/pkelly/pipeline/wtgpipeline//match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + inputcat+str(1)  + " data "                                                                                                                       
        print command
        os.system('pwd')
        run(command, [matchedcat])


        print matchedcat, specfile.file            
                                                                                                                                   
        import astropy.io.fits as pyfits
                                                                                                                                   
        spectable = pyfits.open(matchedcat)['STDTAB']
        print "looking at "+varname+'-'+filterlist[0]+'_data'
        print spectable
        print matchedcat
        

        run_list.append(['spectra',spectable,outspeccat,'_data',matchedcat])





    #print pyfits.open(inputcat)['STDTAB'].columns# ???


    naper=len(fulltable.field(magflux + '_' + magtype + '-'+filterlist[0]+''))
    print naper

    print inputcat+str(1)
  
    eazy_write=True 
    bpz_write=True 
    bpz_cols_info = open(outspeccat + '.columns','w')
    eazy_cols = ''

    import scipy

    #for type,table,file,appendix in [['spectra',spectable,outspeccat,'_data'],['all',fulltable,outfullcat,'']]:

    for type,alltable,file,appendix,tablefile in run_list:
        table = alltable.data

        print file, appendix, type

        print len(table)

        ''' select subsample '''
        if randsample:
            table = select_random(filterlist, table, train_filters, magtype)


        #if quickHDFN:
            
            
            
            
            
            
            
            
            
            
            
            

            
            
            

            

        

        for i in [1]: #range(naper):                                                                                           


            prior_cols = []
            bpz_cols = [] 
            eazy_cols = []
            eazy_head = ''
            cols = []
            colnum = 1

            name = 'SeqNr'+appendix 

            #prior_cols.append(pyfits.Column(name='SeqNr', format='D', array=table.field('SeqNr'))) 
            #cols.append(pyfits.Column(name=name, format='D', array=table.field(name))) 
            ID_COL = pyfits.Column(name=name, format='D', array=table.field(name)) 
            #eazy_cols.append(pyfits.Column(name=name, format='D', array=table.field(name))) 

            eazy_head += ('# id ')

            print filterlist

            from glob import glob

            file2 = os.environ['subdir'] + '/' + cluster + '/PHOTOMETRY/pat_slr.calib.pickle'   
            if glob(file2):
                import pickle            
                f2 = open(file2,'r')
                m = pickle.Unpickler(f2)
                a2 = m.load()
                results = a2['results']
                zpcorr = results['full']
                print zpcorr

            def short_filter(f2):
                a_short = f2.replace('+','').replace('C','')[-1]        
                print filt, a_short
                                                                       
                import string
                                                                        
                ok = True                                           
                if string.find(f2,'MEGAPRIME') != -1:
                    a_short = 'MP' + a_short.upper() + 'SUBARU'
                elif string.find(f2,'SUBARU') != -1:
                    if string.find(f2,"W-S-") != -1:
                        a_short = 'WS' + a_short.upper() + 'SUBARU'
                    else:
                        a_short = a_short.upper() + 'JOHN'
                                                                        
                    if string.find(f2,"-1-") == -1:
                        ok = False
                return a_short

            good_filts = scipy.zeros(len(table))

            cols_names = [x.name for x in alltable.columns] 

            import string as stringlib
            coaddlist = filter(lambda x: stringlib.find(x,'COADD') != -1 and stringlib.find(x,'APER1') != -1, cols_names)

            import re
            coadd_filts = list(set([re.split('APER1',x)[1] for x in coaddlist]))

            print coaddlist
            print coadd_filts 

            ''' need to check that these filters are also in filterlist '''
            ''' place filters into GROUPS based on coadd column '''

            use_filts = []
            for filt in coadd_filts:
                coadd_filt_list = []
                for filt_good in filterlist:
                    if stringlib.find(filt_good, filt.split('COADD')[-1][2:]) != -1:
                        coadd_filt_list.append(filt_good)

                if coadd_filt_list:
                    use_filts.append(coadd_filt_list)
                    

            print use_filts, 'use_filts'                
            print filterlist, 'filterlist'


            for filts in use_filts:

                good_filt = scipy.zeros(len(table))

                for filt in filts: 

                    fluxmag_name = magflux + '_' + magtype + '-' + filt          
                    error_name = magflux + 'ERR_' + magtype + '-' + filt
                    
                    error_cat = table.field(error_name)[:] 
                    fluxmag_cat = table.field(fluxmag_name)[:] 
                                                                                
                                                                                
                    print len(good_filt)
                                                                                 
                    if magflux == 'FLUX':
                                                                                 
                        fluxmag = scipy.array(fluxmag_cat) #*scale) 
                        error = scipy.array(error_cat) #*scale) 
                        fluxmag[fluxmag_cat==-99]=0
                        error[fluxmag_cat==-99]=0
                                                                                 
                        good_filt[error!=0]=1
                    
                    elif magflux == 'MAG':
                                                                                 
                                                                                 
                        fluxmag = scipy.array(fluxmag_cat) 
                        error = scipy.array(error_cat) 

                        good_filt[(fluxmag!=-99)*(error!=99)] = 1


                good_filts += good_filt


            print good_filts[:1000]



            print filterlist, len(filterlist)
            for filt in filterlist:

                if bpz_write:
                    colnum += 1                                                                        
                    import string
                    fix = filter(lambda x:x is True, [filt==f for f in train_filters])
                    print fix, correction_dict.has_key(filt), len(fix), filt
                    if correction_dict.has_key(filt) and len(fix) > 0:
                        bpz_cols_info.write(filt + '\t' + str(colnum) + ',' + str(colnum+1) + '\tAB\t0.02\t' + str(correction_dict[filt]) + '\n')
                        #print correction_dict[filt], filt, 'fixed'
                    else:
                        #print zpcorr.keys(), short_filter(filt), filt                            
                        if False: #zpcorr.has_key(short_filter(filt)):
                            bpz_cols_info.write(filt + '\t' + str(colnum) + ',' + str(colnum+1) + '\tAB\t0.02\t' + str(zpcorr[short_filter(filt)]) + '\n')
                        else:
                            bpz_cols_info.write(filt + '\t' + str(colnum) + ',' + str(colnum+1) + '\tAB\t0.02\t0.0\n')
                    colnum += 1
                    print fix, len(fix) > 0
                    print [filt==f for f in train_filters]
                    print train_filters
                
                if eazy_write:
                    eazy_head += ('f_' + filt + ' e_' + filt + ' ')

                fluxmag_name = magflux + '_' + magtype + '-'+filt+appendix
                error_name = magflux + 'ERR_' + magtype + '-'+filt+appendix
                
                error_cat = table.field(error_name)[:] 
                fluxmag_cat = table.field(fluxmag_name)[:] 



                if magflux == 'FLUX':
                    #flag_name = 'Flags_' + magtype + '-'+filt+appendix
                    #flag_cat = table.field(flag_name)[:] 

                    #imaflags_name = 'IMAFLAGS_ISO_' + magtype + '-'+filt+appendix
                    #imaflags_cat = table.field(fluxmag_name)[:] 

                    fluxmag = scipy.array(fluxmag_cat) #*scale) 
                    fluxmag_eazy = scipy.array(fluxmag_cat) #*scale) 
                    error = scipy.array(error_cat) #*scale) 
                    fluxmag[fluxmag_cat==-99]=0
                    fluxmag_eazy[fluxmag_cat==-99]=-100
                    fluxmag_eazy[fluxmag_cat==0]=-100
                    error[fluxmag_cat==-99]=0

                    ''' mark bad measurements '''
                    #fluxmag[flag_cat!=0]=0
                    #error[flag_cat!=0]=0
                    #fluxmag[imaflags_cat!=0]=0
                    #error[imaflags_cat!=0]=0
                    #good_filt[error==0]=0

                    ''' expand errors for training bands '''                            
                    for e in train_filters:
                        if string.find(filt,e) != -1 and randsample:
                            error[(error/fluxmag<0.15)*(error>0)*(fluxmag!=0)] = 0.15 * abs(fluxmag)
                            #print error
                    
                elif magflux == 'MAG':
                    fluxmag = scipy.array(fluxmag_cat) 
                    fluxmag_eazy = scipy.array(fluxmag_cat) #*scale) 

                    fluxmag_eazy[fluxmag_cat==-99]=-100
                    fluxmag_eazy[fluxmag_cat==0]=-100

                    error = scipy.array(error_cat) 

                    ''' for the COSMOS catalog '''
                    flag_dict = {'SUBARU-10_2-1-W-J-B':'B_mask',
                        'SUBARU-10_2-1-W-J-V':'V_mask',
                        'SUBARU-10_2-1-W-S-I+':'I_mask',
                        'SUBARU-10_2-1-W-S-Z+':'z_mask'}          
    
                    if filt in flag_dict: 
                        flag_cat = table.field(flag_dict[filt])[:] 
                        fluxmag[flag_cat!=0]=-99
                        error[flag_cat!=0]=-99

                    ''' expand errors for training bands '''                            
                    for e in train_filters:
                        if string.find(filt,e) != -1 and randsample:
                            error[(error<0.15)*(error>0)] = 0.15 

                    ''' remember that not all columns have a mask (i.e. R-band) '''
                    #good_filt[fluxmag==-99]=0
                    #good_filt[error==99]=0

                ''' BPZ: If an object is not detected in a filter, write m=99. and  its error as m_lim, where m_lim is the 1-sigma detection limit.
                For fluxes, write flux=0 and an error equal to the 1-sigma detection limit.
                If an object is not observed in a filter, write m=-99., error=0. For fluxes, just write both flux and error as 0. 
                http://acs.pha.jhu.edu/~txitxo/bpzdoc.html

                COSMOS CATALOG: A magnitude of -99 indicates a photometric measurement was not possible due to lack of data, a large number of bad pixels, or saturation. A magnitude of 99.0 indicates no detection. In the case of no detection the error given for the object is the 1 sigma limiting magnitude at the position of the souce. 
                http://irsa.ipac.caltech.edu/data/COSMOS/gator_docs/cosmos_photom_colDescriptions.html#masks
                '''


                from copy import copy
                bpz_cols.append(pyfits.Column(name=fluxmag_name, format='D', array=copy(fluxmag))) 
                bpz_cols.append(pyfits.Column(name=error_name, format='D', array=copy(error))) 
                eazy_cols.append(pyfits.Column(name=fluxmag_name, format='D', array=copy(fluxmag_eazy))) 
                eazy_cols.append(pyfits.Column(name=error_name, format='D', array=copy(error))) 

                #good_filts += good_filt



            if cluster == 'COSMOS_PHOTOZ':
                filterprior = 'SUBARU-10_2-1-W-S-R+' 
            else:
                filterprior = 'SUBARU-COADD-1-W-C-RC'                                                                     
                import itertools
                import scipy
                truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                truth = truth[truth]
                print 'truth', truth, filterprior, filterlist
                
                
                
                
                if len(truth) == 0: 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    filterprior = 'SUBARU-10_1-1-W-C-RC' 
                    truth = truth[truth]
                if len(truth) == 0: 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    filterprior = 'SUBARU-10_2-1-W-C-RC' 
                    truth = truth[truth]
                if len(truth) == 0: 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    truth =  scipy.array([x == filterprior for x in filterlist])
                    truth = truth[truth]
                if len(truth) == 0: 
                    filterprior = 'SUBARU-COADD-1-W-S-R+' 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    truth = truth[truth]
                if len(truth) == 0: 
                    filterprior = 'MEGAPRIME-COADD-1-r' 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    truth = truth[truth]

                if len(truth) == 0:   
                    filterprior = 'SUBARU-10_2-1-W-S-R+' 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])
                    truth = truth[truth]

                if len(truth) == 0:   
                    filterprior = 'SUBARU-10_2-1-W-S-I+' 
                    truth =  scipy.array([x.name == magflux + '_' + magtype + '-'+filterprior for x in alltable.columns])                                                                                                          
                    truth = truth[truth]                                                                                                                                                                                           
                                                                                                                          
                print truth, filterprior

            filter_name = filterprior

            print filter_name



            #print table.field('FLUX_ISO-'+filter+appendix)[:,1], scale
            #print -2.5 * scipy.log10(table.field('FLUX_ISO-'+filter+appendix)[:,1])
            #print len(table.field('FLUX_ISO-'+filter+appendix)[:,1])

            ''' need to make a prior magnitude column that does not have only negative values?? '''
            prior_array = table.field(magflux + '_' + magtype + '-'+filter_name+appendix)[:]

            print len(prior_array[prior_array!=-99])

            import string
            if string.find(filter_name,'-1-') != -1:
                backfilter = filter_name.replace('-1-','-2-')
                truth =  scipy.array([x == backfilter for x in filterlist])
                truth = truth[truth]
                if len(truth) != 0: 
                    backup_array = table.field(magflux + '_' + magtype + '-'+backfilter+appendix)[:]
                    prior_array[prior_array == -99] = backup_array[prior_array == -99]            
            if string.find(filter_name,'-2-') != -1:
                backfilter = filter_name.replace('-2-','-1-')
                truth =  scipy.array([x == backfilter for x in filterlist])
                truth = truth[truth]
                if len(truth) != 0: 
                    backup_array = table.field(magflux + '_' + magtype + '-'+backfilter+appendix)[:]              
                    prior_array[prior_array == -99] = backup_array[prior_array == -99]            
            
            print len(prior_array[prior_array!=-99])

            print prior_array

            bpz_cols = [ID_COL] + bpz_cols
            eazy_cols = [ID_COL] + eazy_cols
            
            ''' Add up number of good filter measurements for each object NFILT '''


            if type=='spectra':
                print type
                cols.append(pyfits.Column(name='PatID', format='D', array=table.field('z_spec')*0)) 

                cols.append(pyfits.Column(name='zspec', format='D', array=table.field('z_spec'))) 
                cols.append(pyfits.Column(name='priormag', format='D', array=prior_array) )

                a = scipy.arange(1,len(table)+1)

                bpz_cols.append(pyfits.Column(name='PatID', format='D', array=a)) 
                bpz_cols.append(pyfits.Column(name='zspec', format='D', array=table.field('z_spec'))) 
                #bpz_cols.append(pyfits.Column(name='priormag', format='D', array=table.field('FLUX_ISO-'+filter+appendix)[:,1])) 

                if magflux == 'FLUX': 
                    bpz_cols.append(pyfits.Column(name='priormag', format='D', array=-2.5*scipy.log10(prior_array)) )
                else: 
                    bpz_cols.append(pyfits.Column(name='priormag', format='D', array=prior_array)) 

                bpz_cols.append(pyfits.Column(name='NFILT', format='D', array=copy(good_filts))) 
                #bpz_cols.append(pyfits.Column(name='randsample', format='D', array=scipy.array([random.random() for ww in range(len(prior_array))])) )
                #bpz_cols.append(pyfits.Column(name='RA', format='D', array=(table.field('ALPHA_J2000')))) 
                #bpz_cols.append(pyfits.Column(name='DEC', format='D', array=(table.field('DELTA_J2000')))) 
                prior_cols.append(pyfits.Column(name='priorflux', format='D', array=prior_array)) 
                prior_cols.append(pyfits.Column(name='priormag', format='D', array=-2.5*scipy.log10(prior_array)) )
                eazy_cols.append(pyfits.Column(name='zspec', format='D', array=table.field('z_spec'))) 

            else:
                #bpz_cols.append(pyfits.Column(name='0', format='D', array=table.field('SeqNr')*0)) 
                a = scipy.arange(1,len(table)+1)
    
                bpz_cols.append(pyfits.Column(name='PatID', format='D', array=a)) 
                if inputcat_zlist:
                    f = open(inputcat_zlist,'r').readlines()
                    zs_array = scipy.array(f)
                    bpz_cols.append(pyfits.Column(name='zspec', format='D', array=zs_array))
                else:
                    bpz_cols.append(pyfits.Column(name='zspec', format='D', array=table.field('SeqNr')*0))

                if magflux == 'FLUX': 
                    bpz_cols.append(pyfits.Column(name='priormag', format='D', array=-2.5*scipy.log10(prior_array))) 
                else: 
                    bpz_cols.append(pyfits.Column(name='priormag', format='D', array=prior_array)) 
                bpz_cols.append(pyfits.Column(name='NFILT', format='D', array=copy(good_filts))) 
                #bpz_cols.append(pyfits.Column(name='randsample', format='D', array=scipy.array([random.random() for ww in range(len(prior_array))]))) 
                #bpz_cols.append(pyfits.Column(name='RA', format='D', array=(table.field('ALPHA_J2000')))) 
                #bpz_cols.append(pyfits.Column(name='DEC', format='D', array=(table.field('DELTA_J2000')))) 
                prior_cols.append(pyfits.Column(name='priorflux', format='D', array=prior_array)) 
                prior_cols.append(pyfits.Column(name='priormag', format='D', array=-2.5*scipy.log10(prior_array)) )
                eazy_cols.append(pyfits.Column(name='zspec', format='D', array=-1.*scipy.ones(len(table.field('SeqNr'))))) 

            if bpz_write:
                bpz_cols_info.write('ID\t' + str(1) + '\n')
                colnum += 2                                  
                bpz_cols_info.write('Z_S\t' + str(colnum) + '\n')
                colnum += 1                                  
                bpz_cols_info.write('M_0\t' + str(colnum) + '\n')
                #colnum += 1                                  
                #bpz_cols_info.write('NFILT\t' + str(colnum) + '\n')
                #colnum += 1                                  
                #bpz_cols_info.write('RANDOM\t' + str(colnum) + '\n')
                #colnum += 1                                  
                #bpz_cols_info.write('RA\t' + str(colnum) + '\n')
                #colnum += 1                                  
                #bpz_cols_info.write('DEC\t' + str(colnum) + '\n')

                bpz_write = False
                bpz_cols_info.close()
            print outspeccat + '.columns'

            if eazy_write: 
                eazy_head += 'z_spec\n# id ' + reduce(lambda x,y: x + ' ' + y, ['F' + str(g) + ' E' + str(g) for g in range(1,len(filterlist)+1)]) + ' z_spec\n'

            print eazy_head

            lphfile = file+'.lph'+str(i)
            bpzfile = file+'.bpz'+str(i)
            eazyfile = file+'.eazy'+str(i)
            print eazyfile

            eazyheader= file+'.eazyheader'

            f = open(eazyheader,'w')
            f.write(eazy_head)
            f.close()

            ''' write out prior columns ''' 
            f = file+'.prior'+str(i)
            hdu = pyfits.PrimaryHDU()                                                  
            hdulist = pyfits.HDUList([hdu])
            print cols
            tbhu = pyfits.BinTableHDU.from_columns(prior_cols)
            hdulist.append(tbhu)
            hdulist[1].header['EXTNAME']='STDTAB'
            outcat = '/tmp/test' #path + 'PHOTOMETRY/' + type + '.cat'                
            os.system('rm ' + f + '.tab')
            hdulist.writeto(f + '.tab')

            for c,f in [[bpz_cols,bpzfile],[eazy_cols,eazyfile]]: #[cols,lphfile],
                
                hdu = pyfits.PrimaryHDU()                                                  
                hdulist = pyfits.HDUList([hdu])
                print cols
                tbhu = pyfits.BinTableHDU.from_columns(c)
                hdulist.append(tbhu)
                hdulist[1].header['EXTNAME']='STDTAB'
                outcat = '/tmp/test' #path + 'PHOTOMETRY/' + type + '.cat'                
                os.system('rm ' + f + '.tab')
                hdulist.writeto(f + '.tab')


               
                os.system('rm test')
                print 'writing'
                #pyfits.tdump(outcat,datafile='test',ext=1)
                os.system('ldactoasc -b -i ' + f + '.tab -t STDTAB > ' + f)
                print 'finished'
                print f
                                                                                                                         
            print "Finished aper "+str(i)
            print "Type " + type




if __name__ == "__main__":

    import sys
    usage = '''./make_lephare_cats.py -i,--inputcat=STRING # full calibrated cat
                                      -s,--speccat=STRING  # spectra catalog
                                      -o,--outspeccat=STRING # spectra catalog for lph
                                      -c,--outfullcat=STRING # full cat for lph
                                      -f,--filterlist=STRING # filterlist
                                      '''
    
    try: 
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "i:s:o:c:f:", 
                                   ["inputcat=", "speccat=", "outspeccat=",\
                                    "outfullcat=","filterlist="])
        
    except getopt.GetoptError: 
        print usage 
        sys.exit(2) 

    filterlist=''
    inputcat=''
    speccat=''
    outspeccat=''
    outfullcat=''
    varname=''
    errvarname=''
    for o, a in opts:
        if o in ("-i", "--inputcat"):
            inputcat = a
        elif o in ("-s","--speccat"):
            speccat = a
        elif o in ("-o", "--outspeccat"):
            outspeccat = a
        elif o in ("-c", "--outfullcat"):
            outfullcat = a
        elif o in ("-f","--filterlist"):
            print a
            a=a.replace(","," ")
            filterlist = a.split() 
        else:
            print "option:", o, " unknown"
            print usage
            sys.exit(2)
    counter = 0
    for item in filterlist,inputcat,speccat,outspeccat,outfullcat:
        counter = counter +1
        if item == '':
            print str(counter) +"unknown: need all options"
            print usage
            sys.exit(2)
 
    #doit(cluster,DETECT_FILTER,filterlist,inputcat,speccat,outspeccat,outfullcat,varname,errvarname)
