#adam-fragments_removed# linear_fit-term_name (this was commented out to begin with)
                #term_name = sample+'$'+sample_size+'$0x1y'
                #term_name = sample+'$'+sample_size+'$0x1y'
                #print term_name, '!!!!!'
                #if 0:
                #    print fitvars['1$0x1y'], '1$0x1y'
                #    term_name = sample+'$'+sample_size+'$1$0x1y'
                #    dtmp[term_name] = 1.
                #    term_name = sample+'$'+sample_size+'$0$1x0y'
                #    dtmp[term_name] = 1.
                #    fitvars['1$0x1y'] = 1.
                #    fitvars['0$1x0y'] = 1.
                #    print fitvars

#adam-fragments_removed# calcDataIllum-diff_png
    diff_png_name= f + '_diff_' + test.replace('_','') + '.png'
    pylab.subplot(211)
    pylab.scatter(x_p,data_p,linewidth=0)
    pylab.ylim(limits)
    pylab.xlim(x_extrema[0],x_extrema[-1])
    pylab.xlabel('X axis')
    pylab.ylabel(data_label)     # label the plot
    pylab.subplot(212)
    pylab.scatter(y_p,data_p,linewidth=0)
    pylab.ylim(limits)
    pylab.xlim(y_extrema[0],y_extrema[-1])
    pylab.xlabel('Y axis')
    pylab.ylabel(data_label)     # label the plot
    pylab.suptitle('diff: the data (%s) is shown in a scatter plot projected vs. the X-axis and Y-axis' % (data_label))
    pylab.savefig(diff_png_name)
    pylab.clf()
    print 'calcDataIllum| finished: diff_png_name=',diff_png_name

#adam-fragments_removed# try_linear-config_based_zp_chip_correct
                        if CONFIG != '10_3':
                            zp_chip_correction = []
                            for chip in chipnums[ROT]:
                                zp_chip_correction.append(fitvars['zp_' + str(int(float(chip)))])
                            zp_chip_correction = scipy.array(zp_chip_correction)
                            epsilonB += zp_chip_correction



#adam-fragments_removed# get_astrom_run_sextract-end
## from the end of get_astrom_run_sextract (all parts after running fix_radec are removed)

            #raw_input('FINISHED')


            trial = True
            ppid = str(os.getppid())
            try:
                construct_correction(dict['OBJNAME'],dict['FILTER'],dict['PPRUN'])
                print 'finished'
            except:
                ppid_loc = str(os.getppid())
                print traceback.print_exc(file=sys.stdout)
                if ppid_loc != ppid: os._exit(0)
                print 'exiting here'
                #if trial: raise Exception

            print dict['OBJNAME'], dict['PPRUN']

        ''' not sure what following code does '''
        #if 0:
        #    #print dict['SUPA'], dict['file'], dict['OBJNAME'], dict['pasted_cat'], dict['matched_cat_star']
        #    d_update = get_files(dict['SUPA'],dict['FLAT_TYPE'])
        #    go = 0
        #    if d_update.has_key('TRIED'):
        #        if d_update['TRIED'] != 'YES':
        #            go = 1
        #    else: go = 1
#
#            if string.find(str(dict['TIME']),'N') == -1:
#                #print dict['TIME']
#                if time.time() - float(dict['TIME']) > 600:
#                    go = 1
#                else: go = 0
#            else: go = 1
#            if 0: # go:
#                #print str(time.time())
#                save_exposure({'ACTIVE':'YES','TIME':str(time.time())},dict['SUPA'],dict['FLAT_TYPE'])
#                os.system('rm -R ' + tmpdir)
#                analyze(dict['SUPA'],dict['FLAT_TYPE'],dict)
#                save_exposure({'ACTIVE':'FINISHED'},dict['SUPA'],dict['FLAT_TYPE'])
#


## now fragments I've picked out from the linear_fit function in simplifying it (check the func above to see exactly where it fits in)

#adam-fragments_removed# linear_fit-fit_readout_ports
# from linear_fit: few lines after (''' save pattern w/ chip zps '''), right after (if str(dt['CRPIX1_' + str(CHIP)]) != 'None':)
#this would be usefull if you wanted to have the IC treat each individual readout port in each CCD (unnecessary)
#kept the stuff after (else:)
                                        if False: #CONFIG == '10_3':
                                            for sub_chip in ['1','2','3','4']:                                                                                                                                                                          
                                                xmin = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)]) + config_bonn.chip_divide_10_3[sub_chip][0]
                                                xmax = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)]) + config_bonn.chip_divide_10_3[sub_chip][1]
                                                ymin = float(dt['CRPIX2ZERO']) - float(dt['CRPIX2_' + str(CHIP)])
                                                ymax = ymin + float(dt['NAXIS2_' + str(CHIP)])
                                                print 'linear_fit| xmin=',xmin , ' xmax=',xmax , ' ymin=',ymin , ' ymax=',ymax , ' CHIP=',CHIP
                                                print 'linear_fit| int(xmin/bin)=',int(xmin/bin) , ' int(xmax/bin)=',int(xmax/bin) , ' int(ymin/bin)=',int(ymin/bin) , ' int(ymax/bin)=',int(ymax/bin) , ' CHIP=',CHIP , ' bin=',bin , ' scipy.shape(epsilon)=',scipy.shape(epsilon)
                                                print 'linear_fit| epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]=',epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                                                print 'linear_fit| fitvars.keys()=',fitvars.keys()
                                                if fitvars.has_key('zp_' + str(CHIP) + '_' + sub_chip):
                                                    print 'linear_fit| zp', fitvars['zp_' + str(CHIP) + '_' + sub_chip]
                                                    epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP) + '_' + sub_chip])
                                        else:
                                            xmin = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)])
                                            xmax = xmin + float(dt['NAXIS1_' + str(CHIP)])
                                            ymin = float(dt['CRPIX2ZERO']) - float(dt['CRPIX2_' + str(CHIP)])
                                            ymax = ymin + float(dt['NAXIS2_' + str(CHIP)])

                                            print 'linear_fit| xmin=',xmin , ' xmax=',xmax , ' ymin=',ymin , ' ymax=',ymax , ' CHIP=',CHIP
                                            print 'linear_fit| int(xmin/bin),=',int(xmin/bin), int(xmax/bin), int(ymin/bin), int(ymax/bin), CHIP, bin, scipy.shape(epsilon)
                                            print 'linear_fit| epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]=',epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                                            print 'linear_fit| fitvars.keys()=',fitvars.keys()
                                            print 'linear_fit| zp', fitvars['zp_' + str(CHIP)]
                                            epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP)])

#adam-fragments_removed# linear_fit-find_the_color_term
    ''' find the color term '''                                                                                                                                                                                                                         
    if  False:
        data = []
        magErr = []
        color = []
        for star in supas:
            ''' each exp of each star '''
            if star['match'] and (sample=='sdss' or sample=='bootstrap'):
                for exp in star['supa files']:
                    if 2 > tab['SDSSstdMagColor_corr'][star['table index']] > -2:
                        rotation = exp['rotation']
                        sigma = tab['SDSSstdMagErr_corr'][star['table index']]
                        data.append(tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])
                        magErr.append(tab['SDSSstdMagErr_corr'][star['table index']])
                        color.append(tab['SDSSstdMagColor_corr'][star['table index']])
        color.sort()


#adam-fragments_removed# linear_fit-store_and_model
    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open(tmpdir + '/store','w')                                                                                                                                                                                                                   
    #pickle.dump(save,uu)
    #uu.close()

    #''' make model '''
    #fit = make_model(EXPS)
    #position_fit = make_position_model(EXPS)
    #print fit

#adam-fragments_removed# linear_fit-rands_and_run_these (RERPLACED)
    rands = ['rand1'] #,'rand1','rand2','rand3','rand4','rand5','rand6','rand7','rand8','rand9','rand10'] #,'rand11','rand12','rand13','rand14','rand15','rand16','rand17','rand18','rand19','rand20']
    #rands = ['rand11','rand12','rand13','rand14','rand15','rand16','rand17','rand18','rand19','rand20']

    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    if run_these is None:
        run_these = []
        for k in rands:
            db_keys_t = describe_db(c,['' + test + 'fit_db'])
            command="SELECT * from " + test + "fit_db where PPRUN='" + PPRUN + "' and OBJNAME='" + OBJNAME + "' and sample_size like '" + k +  "%' and sample='" + sample + "'"
            print 'linear_fit| command=',command
            c.execute(command)
            results=c.fetchall()
            if len(results) == 0:
                run_these.append(k)
        print 'linear_fit| run_these=',run_these , ' sample=',sample

    print 'linear_fit| run_these=',run_these
    run_these = ['all'] #adam-Warning# why go to the trouble of inputting run_these, then looping and adding things to it, then redoing it?
    #run_these = ['all','rand1','rand2','rand3','rand4','rand5','rand6','rand7','rand8','rand9','rand10']
    #adam-Warning# run_these can only have 'all' in it for now since `random_cmp` isn't defined

    for original_sample_size in run_these:
        print 'linear_fit| adam-loop1: for original_sample_size in run_these: (run_these=["all"])'
        print 'linear_fit| adam-loop1: original_sample_size=',original_sample_size
        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':original_sample_size,'primary_filt':primary,'secondary_filt':secondary,'coverage':str(match),'relative_colors':relative_colors,'catalog':str(match),'CONFIG':CONFIG,'supas':len(supas),'match_stars':len(filter(lambda x:x['match'],supas))})
        if original_sample_size == 'all':
            if totalstars > 30000:
                print 'linear_fit| len(supas)=',len(supas)
                ''' shorten star_good, supas '''
                print 'linear_fit| totalstars=',totalstars , ' len(supas)=',len(supas)
		#l = range(len(supas_copy))
                #supas = [supas_copy[i] for i in l[0:int(float(30000)/float(totalstars)*len(supas))]]
                supas = []
                ''' include bright stars and matched stars '''
                for supa in supas_copy:
                    if len(supas) < int(float(30000)/float(totalstars)*len(supas_copy))  or supa['match']:
                        supas.append(supa)
                #    print 'supa', supa['mag']
                #supas = copy(supas_copy[0:int(float(30000)/float(totalstars)*len(supas_copy))])
            else:
                supas = copy(supas_copy)
            print 'linear_fit| starStats(supas)=',starStats(supas)
            ''' if sdss comparison exists, run twice to see how statistics are improved '''
            #adam: elements of `runs` contain: [original_sample_size, calc_illum, supas,  sample , try_linear]
            if sample == 'sdss':
                ''' first all info, then w/o sdss, then fit for zps w/ sdss but not position terms, then run fit for zps w/o position terms '''
		#runs = [[original_sample_size,True,supas,'sdss'],[original_sample_size + 'None',True,supas,'None'],[original_sample_size + 'sdsscorr',False,supas,'sdss'],[original_sample_size + 'sdssuncorr',False,supas,'sdss']]
		#runs = [[original_sample_size,True,supas,'sdss',True],[original_sample_size + 'None',True,supas,'None', False],[original_sample_size + 'sdsscorr',False,supas,'sdss',False],[original_sample_size + 'sdssuncorr',False,supas,'sdss',False]]
                runs = [[original_sample_size,True,supas,'sdss',True],[original_sample_size + 'None',True,supas,'None', False],[original_sample_size + 'sdsscorr',False,supas,'sdss',False],[original_sample_size + 'sdssuncorr',False,supas,'sdss',False]]
                #runs = [[original_sample_size,True,supas,'sdss',True]]
            else:
                #runs = [[original_sample_size,True,supas,sample_copy,False]]
                runs = [[original_sample_size,True,supas,sample_copy,True],[original_sample_size + 'corr',False,supas,sample_copy,True],[original_sample_size + 'uncorr',False,supas,sample_copy,True]]

        elif original_sample_size != 'all':
            if totalstars > 60000:
                print 'linear_fit| len(supas)=',len(supas)
                ''' shorten star_good, supas '''
                print 'linear_fit| totalstars=',totalstars , ' len(supas)=',len(supas)
                #l = range(len(supas_copy))
                #supas = [supas_copy[i] for i in l[0:int(float(30000)/float(totalstars)*len(supas))]]
                supas_short = copy(supas_copy[0:int(float(60000)/float(totalstars)*len(supas_copy))])
            else:
                supas_short = copy(supas_copy)

            ''' take a random sample of half '''
            ## changing the CLASS_STAR criterion upwards helps as does increasing the sigma on the SDSS stars
            print 'linear_fit| len(supas_short)=',len(supas_short)
            l = range(len(supas_short))
            print 'linear_fit| l[0:10]=',l[0:10]

            l.sort(random_cmp) #adam-Warning# random_cmp isn't defined
            print 'linear_fit| l[0:10]=',l[0:10]
            ''' shorten star_good, supas '''
            print 'linear_fit| len(supas_short)=',len(supas_short)
            supas = [supas_short[i] for i in l[0:len(supas_short)/2]]
            ''' make the complement '''
            supas_complement = [supas_short[i] for i in l[len(supas_short)/2:]]
            runs = [[original_sample_size,True,supas,sample_copy,True],[original_sample_size + 'corr',False,supas_complement,sample_copy,True],[original_sample_size + 'uncorr',False,supas_complement,sample_copy,True]]

#adam-fragments_removed# linear_fit-loop_over_samples
        if try_linear:
            if info['match'] > 600:
                print 'linear_fit| info["match"]>600 => samples = [["match","cheby_terms",True]]'
                samples = [["match","cheby_terms",True]]
                print 'linear_fit| all terms'
            else:
                print 'linear_fit| info["match"]<=600 => samples = [["match","cheby_terms_no_linear",True]]'
                samples = [["match","cheby_terms_no_linear",True]]
                print 'linear_fit| no linear terms'
        else:
            samples = [['nomatch','cheby_terms_no_linear',False]]

        for hold_sample,which_terms,sample2 in samples:

#adam-fragments_removed# linear_fit-10_3_subchips
                if False: #CONFIG == '10_3':
                    chip_num = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                    for div in config_bonn.chip_divide_10_3.keys():
                        if config_bonn.chip_divide_10_3[div][0] < x_rel <= config_bonn.chip_divide_10_3[div][1]:
                            sub_chip = div
                    chip = str(chip_num) + '_' + str(sub_chip)
                else:
                    chip = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                    if not chip_dict.has_key(str(chip)):
                        chip_dict[str(chip)] = ''
                    #adam-del#if not chip_dict.has_key(str(chip)):
                    #adam-del#    chip_dict[str(chip)] = ''
                    #adam-del#    print 'linear_fit| chip_dict.keys()=',chip_dict.keys() , ' CHIPS=',CHIPS
                    #adam-del#n = str(rotation) + '$' + exp['name'] + '$Xpos_ABS'

## can't handle this function, which is over 1000 lines long now. I'm going to change things so that the first big loop is gone. It will save a whole bunch of headaches later. the run_these=['all'] thing is now a given
def linear_fit(OBJNAME,FILTER,PPRUN,run_these=None,match=None,CONFIG=None,primary=None,secondary=None): #intermediate #step3_run_fit
    '''inputs: OBJNAME,FILTER,PPRUN,run_these=None,match=None,CONFIG=None,primary=None,secondary=None
    returns:
    purpose: creates the matricies and performs a sparse fit. Does some diagnostic plotting. Writes out the catalogs: data_path + 'PHOTOMETRY/ILLUMINATION/' + 'catalog_' + PPRUN + '.cat'
    calls: getTableInfo,get_files,selectGoodStars,starStats,describe_db,save_fit,starStats,calcDataIllum,save_fit,save_fit,save_fit,save_fit,get_fits,save_fit,save_fit,calcDataIllum,calcDataIllum,calcDataIllum,save_fit
    called_by: match_OBJNAME'''

    print 'linear_fit| START the func. inputs: OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' run_these=',run_these , ' match=',match , ' CONFIG=',CONFIG , ' primary=',primary , ' secondary=',secondary
    redoselect = False #if True will redo selectGoodStars and starStats

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

    #ROTS, data, err, X, Y, maxVal, classStar = diffCalcNew()
    #save = {'ROTS': ROTS, 'data':data,'err':err,'X':X,'Y':Y,'maxVal':maxVal,'classStar':classStar}
    #uu = open(tmpdir + '/store','w')
    #pickle.dump(save,uu)
    #uu.close()

    #''' make model '''
    #fit = make_model(EXPS)
    #position_fit = make_position_model(EXPS)
    #print fit

    ''' EXPS has all of the image information for different rotations '''
    start_EXPS = getTableInfo()
    print 'linear_fit| start_EXPS=',start_EXPS

    for ROT in start_EXPS.keys():
        print 'linear_fit| start_EXPS[ROT]=',start_EXPS[ROT]
        #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,str(ROT)+'images':len(EXPS[ROT]),str(ROT)+'supas':reduce(lambda x,y:x+','+y,EXPS[ROT])})
    print 'linear_fit| start_EXPS=',start_EXPS

    dt = get_files(start_EXPS[start_EXPS.keys()[0]][0])
    print 'linear_fit| dt["CHIPS"]=',dt["CHIPS"]
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    if string.find(CONFIG,'8')!=-1:
        CHIPS = [2,3,4,6,7,8]
    elif string.find(CONFIG,'9')!=-1:
        CHIPS = [2,3,4,7,8,9]

    ''' see if linear or not '''
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']
    print 'linear_fit| LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2

    if redoselect:
        EXPS, star_good,supas, totalstars, mdn_background = selectGoodStars(start_EXPS,match,LENGTH1,LENGTH2,CONFIG)
        uu = open(tmpdir + '/selectGoodStars','w')
        info = starStats(supas)
        print 'linear_fit| info=',info
        pickle.dump({'info':info,'EXPS':EXPS,'star_good':star_good,'supas':supas,'totalstars':totalstars},uu)
        uu.close()

    ''' if early chip configuration, use chip color terms '''
    if (CONFIG=='8' or CONFIG=='9'):
        relative_colors = True
    else: relative_colors = False
    print 'linear_fit| relative_colors=',relative_colors

    f=open(tmpdir + '/selectGoodStars','r')
    m=pickle.Unpickler(f)
    d=m.load()

    ''' read out of pickled dictionary '''
    info = d['info']
    EXPS = d['EXPS']
    star_good = d['star_good']
    supas = d['supas']
    totalstars = d['totalstars']
    print 'linear_fit| EXPS=',EXPS
    print "linear_fit| calc_test_save.linear_fit('" + OBJNAME + "','" + FILTER + "','" + PPRUN + "'," + str(match) + ",'" + CONFIG +  str(primary) + "',secondary='" + str(secondary) + "',star_good='" + str(len(star_good)) + "')"
    print 'linear_fit| len(star_good)=',len(star_good)

    #fitvars_fiducial = False
    p = pyfits.open(tmpdir + '/final.cat')
    table = p[1].data

    tab = {}
    for ROT in EXPS.keys():
        for y in EXPS[ROT]:
            keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos',ROT+'$'+y+'$Ypos',ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']
            if match:
                keys = [ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos',ROT+'$'+y+'$Ypos',ROT+'$'+y+'$CHIP',ROT+'$'+y+'$Xpos_ABS',ROT+'$'+y+'$Ypos_ABS',ROT+'$'+y+'$MAG_AUTO',ROT+'$'+y+'$MAGERR_AUTO',ROT+'$'+y+'$MaxVal',ROT+'$'+y+'$BackGr',ROT+'$'+y+'$CLASS_STAR',ROT+'$'+y+'$Flag' ,'SDSSstdMag_corr','SDSSstdMagErr_corr','SDSSstdMagColor_corr','SDSSstdMagClean_corr','SDSSStar_corr',ROT+'$'+y+'$ALPHA_J2000',ROT+'$'+y+'$DELTA_J2000']

            for key in keys:
                tab[key] = copy(table.field(key))

    tab_copy = copy(tab)
    supas_copy = copy(supas)
    coord_conv_x = lambda x:(2.*x-(LENGTH1))/((LENGTH1))
    coord_conv_y = lambda x:(2.*x-(LENGTH2))/((LENGTH2))

    ''' find the color term '''
    if  False:
        data = []
        magErr = []
        color = []
        for star in supas:
            ''' each exp of each star '''
            if star['match'] and (sample=='sdss' or sample=='bootstrap'):
                for exp in star['supa files']:
                    if 2 > tab['SDSSstdMagColor_corr'][star['table index']] > -2:
                        rotation = exp['rotation']
                        sigma = tab['SDSSstdMagErr_corr'][star['table index']]
                        data.append(tab[str(rotation)+'$'+exp['name']+'$MAG_AUTO'][star['table index']] - tab['SDSSstdMag_corr'][star['table index']])
                        magErr.append(tab['SDSSstdMagErr_corr'][star['table index']])
                        color.append(tab['SDSSstdMagColor_corr'][star['table index']])
        color.sort()

    sample = str(match)
    sample_copy = copy(sample)
    print 'linear_fit| sample=',sample

    rands = ['rand1'] #,'rand1','rand2','rand3','rand4','rand5','rand6','rand7','rand8','rand9','rand10'] #,'rand11','rand12','rand13','rand14','rand15','rand16','rand17','rand18','rand19','rand20']
    #rands = ['rand11','rand12','rand13','rand14','rand15','rand16','rand17','rand18','rand19','rand20']

    db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
    c = db2.cursor()

    if run_these is None:
        run_these = []
        for k in rands:
            db_keys_t = describe_db(c,['' + test + 'fit_db'])
            command="SELECT * from " + test + "fit_db where PPRUN='" + PPRUN + "' and OBJNAME='" + OBJNAME + "' and sample_size like '" + k +  "%' and sample='" + sample + "'"
            print 'linear_fit| command=',command
            c.execute(command)
            results=c.fetchall()
            if len(results) == 0:
                run_these.append(k)
        print 'linear_fit| run_these=',run_these , ' sample=',sample

    print 'linear_fit| run_these=',run_these
    run_these = ['all'] #adam-Warning# why go to the trouble of inputting run_these, then looping and adding things to it, then redoing it?
    #run_these = ['all','rand1','rand2','rand3','rand4','rand5','rand6','rand7','rand8','rand9','rand10']
    #adam-Warning# run_these can only have 'all' in it for now since `random_cmp` isn't defined

    for sample_size in run_these:
        print 'linear_fit| adam-loop1: for sample_size in run_these: (run_these=["all"])'
        print 'linear_fit| adam-loop1: sample_size=',sample_size
        save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,'primary_filt':primary,'secondary_filt':secondary,'coverage':str(match),'relative_colors':relative_colors,'catalog':str(match),'CONFIG':CONFIG,'supas':len(supas),'match_stars':len(filter(lambda x:x['match'],supas))})
        if sample_size == 'all':
            if totalstars > 30000:
                print 'linear_fit| len(supas)=',len(supas)
                ''' shorten star_good, supas '''
                print 'linear_fit| totalstars=',totalstars , ' len(supas)=',len(supas)
		#l = range(len(supas_copy))
                #supas = [supas_copy[i] for i in l[0:int(float(30000)/float(totalstars)*len(supas))]]
                supas = []
                ''' include bright stars and matched stars '''
                for supa in supas_copy:
                    if len(supas) < int(float(30000)/float(totalstars)*len(supas_copy))  or supa['match']:
                        supas.append(supa)
                #    print 'supa', supa['mag']
                #supas = copy(supas_copy[0:int(float(30000)/float(totalstars)*len(supas_copy))])
            else:
                supas = copy(supas_copy)
            print 'linear_fit| starStats(supas)=',starStats(supas)
            ''' if sdss comparison exists, run twice to see how statistics are improved '''
            #adam: elements of `runs` contain: [sample_size, calc_illum, supas,  sample , try_linear]
            if sample == 'sdss':
                ''' first all info, then w/o sdss, then fit for zps w/ sdss but not position terms, then run fit for zps w/o position terms '''
		#runs = [[sample_size,True,supas,'sdss'],[sample_size + 'None',True,supas,'None'],[sample_size + 'sdsscorr',False,supas,'sdss'],[sample_size + 'sdssuncorr',False,supas,'sdss']]
		#runs = [[sample_size,True,supas,'sdss',True],[sample_size + 'None',True,supas,'None', False],[sample_size + 'sdsscorr',False,supas,'sdss',False],[sample_size + 'sdssuncorr',False,supas,'sdss',False]]
                runs = [[sample_size,True,supas,'sdss',True],[sample_size + 'None',True,supas,'None', False],[sample_size + 'sdsscorr',False,supas,'sdss',False],[sample_size + 'sdssuncorr',False,supas,'sdss',False]]
                #runs = [[sample_size,True,supas,'sdss',True]]
            else:
                #runs = [[sample_size,True,supas,sample_copy,False]]
                runs = [[sample_size,True,supas,sample_copy,True],[sample_size + 'corr',False,supas,sample_copy,True],[sample_size + 'uncorr',False,supas,sample_copy,True]]

        elif sample_size != 'all':
            if totalstars > 60000:
                print 'linear_fit| len(supas)=',len(supas)
                ''' shorten star_good, supas '''
                print 'linear_fit| totalstars=',totalstars , ' len(supas)=',len(supas)
                #l = range(len(supas_copy))
                #supas = [supas_copy[i] for i in l[0:int(float(30000)/float(totalstars)*len(supas))]]
                supas_short = copy(supas_copy[0:int(float(60000)/float(totalstars)*len(supas_copy))])
            else:
                supas_short = copy(supas_copy)

            ''' take a random sample of half '''
            ## changing the CLASS_STAR criterion upwards helps as does increasing the sigma on the SDSS stars
            print 'linear_fit| len(supas_short)=',len(supas_short)
            l = range(len(supas_short))
            print 'linear_fit| l[0:10]=',l[0:10]

            l.sort(random_cmp) #adam-Warning# random_cmp isn't defined
            print 'linear_fit| l[0:10]=',l[0:10]
            ''' shorten star_good, supas '''
            print 'linear_fit| len(supas_short)=',len(supas_short)
            supas = [supas_short[i] for i in l[0:len(supas_short)/2]]
            ''' make the complement '''
            supas_complement = [supas_short[i] for i in l[len(supas_short)/2:]]
            runs = [[sample_size,True,supas,sample_copy,True],[sample_size + 'corr',False,supas_complement,sample_copy,True],[sample_size + 'uncorr',False,supas_complement,sample_copy,True]]

        print 'linear_fit| len(supas)=',len(supas) , ' supas[0]=',supas[0] , ' totalstars=',totalstars
        print 'linear_fit| sample_size=',sample_size , ' match=',match , ' sample=',sample
        print 'linear_fit| len(supas_copy)=',len(supas_copy) , ' len(supas)=',len(supas)
        print 'linear_fit| supas[0:10]=',supas[0:10]

        for sample_size, calc_illum, supas,  sample , try_linear in runs:
            print 'linear_fit| adam-loop2: for sample_size, calc_illum, supas,  sample , try_linear in runs: (runs = [[sample_size,True,supas,"sdss",True],[sample_size + "None",True,supas,"None", False],[sample_size + "sdsscorr",False,supas,"sdss",False],[sample_size + "sdssuncorr",False,supas,"sdss",False]]) since (sample == "sdss" and sample_size == "all")'
            print 'linear_fit| adam-loop2: sample_size=',sample_size , ' calc_illum=',calc_illum , ' supas=',supas , 'sample=', sample , ' try_linear=',try_linear
            #tab = copy(tab_copy )
            print 'linear_fit| info["match"]=',info["match"]
            if try_linear:
                if info['match'] > 600:
                    print 'linear_fit| info["match"]>600 => samples = [["match","cheby_terms",True]]'
                    samples = [["match","cheby_terms",True]]
                    print 'linear_fit| all terms'
                else:
                    print 'linear_fit| info["match"]<=600 => samples = [["match","cheby_terms_no_linear",True]]'
                    samples = [["match","cheby_terms_no_linear",True]]
                    print 'linear_fit| no linear terms'
            else:
                samples = [['nomatch','cheby_terms_no_linear',False]]

            for hold_sample,which_terms,sample2 in samples:
                print 'linear_fit| adam-loop3: for hold_sample,which_terms,sample2 in samples: (since try_linear==True always)(if info["match"] > 600: samples = [["match","cheby_terms",True]]) (else: samples = [["match","cheby_terms_no_linear",True]])'
                print 'linear_fit| adam-loop3: hold_sample=',hold_sample , ' which_terms=',which_terms , ' sample2=',sample2

                cheby_terms_use = locals()[which_terms] 
                print 'linear_fit| sample=', sample #sample="sdss" or "None"
		#sample2 never used: print 'linear_fit| sample2=', sample2 #sample2=True (or False if not try_linear)
		#adam-SHNT# trying to get this all understood. Start here!

                ''' if random, run first with one half, then the other half, applying the correction '''
                columns = []
                column_dict = {}

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
                per_chip = False # have a different zp for each chip on each exposures
                same_chips =   True# have a different zp for each chip but constant across exposures

                if not per_chip:
                    zp_columns = []
                    for ROT in EXPS.keys():
                        for exp in EXPS[ROT]:
                            index += 1
                            zp_columns.append({'name':'zp_image_'+exp,'image':exp,'im_rotation':ROT,'index':index})
		else:
                    zp_columns = []
                    for ROT in EXPS.keys():
                        for exp in EXPS[ROT]:
                            for chip in CHIPS:
                                index += 1
                                zp_columns.append({'name':'zp_image_'+exp + '_' + chip,'image':exp,'im_rotation':ROT, 'chip':chip,'index':index})

                #if False: # CONFIG == '10_3':
                #    first_empty = 0
                #    for chip in CHIPS:
                #        for sub_chip in [1,2,3,4]:
                #            if first_empty != 0:
                #                index += 1
                #                zp_columns.append({'name':'zp_'+str(chip)+'_'+str(sub_chip),'image':'chip_zp','chip':str(chip)+'_'+str(sub_chip),'index':index})
                #            else: first_empty = 1
                #else:
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
                else: color_columns = []
                columns += color_columns
                print 'linear_fit| color_columns=',color_columns , ' match=',match

                mag_columns = []
                for star in supas:
                    mag_columns.append({'name':'mag_' + str(star['table index'])})
                columns += mag_columns
                print 'linear_fit| len(columns)=',len(columns)

                column_names = [x['name'] for x in columns] #reduce(lambda x,y: x+y,columns)]
                print 'linear_fit| column_names[0:100]=',column_names[0:100]

                #adam-del# ''' total number of fit parameters summed over each rotation + total number of images of all rotations + total number of stars to fit '''
                #adam-del# tot_exp = 0
                #adam-del# for ROT in EXPS.keys():
                #adam-del#     for ele in EXPS[ROT]:
                #adam-del#         tot_exp += 1

                x_length = len(position_columns) + len(zp_columns) + len(color_columns) + len(mag_columns)
                print 'linear_fit| len(columns)=',len(columns) , ' x_length=',x_length
                x_length = len(columns)
                y_length = reduce(lambda x,y: x + y,[len(star['supa files'])*2 for star in supas]) # double number of rows for SDSS
                print 'linear_fit| x_length=',x_length , ' y_length=',y_length
                print 'linear_fit| star["supa files"]=', star["supa files"]
                Bstr = ''
                row_num = -1
                supa_num = -1
                ''' each star '''
                print 'linear_fit| creating matrix....'
                sigmas = [] ;inst = []
                data = {} ; magErr = {} ; whichimage = {} ; X = {} ; Y = {} ; color = {} ; chipnums = {} ; Star = {} ; catalog_values = {}
                for ROT in EXPS.keys():
                    data[ROT] = [] ; magErr[ROT] = [] ; X[ROT] = [] ; Y[ROT] = [] ; color[ROT] = [] ; whichimage[ROT] = [] ; chipnums[ROT] = [] ; Star[ROT] = []
                chip_dict = {} ; x_positions = {} ; y_positions = {}
                for star in supas:
                    print 'linear_fit| adam-loop4-make_matrix: for star in supas'
                    print 'linear_fit| adam-loop4-make_matrix: star=',star
                    #print star['match']
                    supa_num += 1
                    ''' each exp of each star '''
                    star_A = []
                    star_B = []
                    star_B_cat = []
                    sigmas = []
                    for exp in star['supa files']:
                        row_num += 1
                        col_num = -1
                        rotation = exp['rotation']
                        x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]

                        x_rel = tab[str(rotation) + '$' + exp['name'] + '$Xpos'][star['table index']]
                        y_rel = tab[str(rotation) + '$' + exp['name'] + '$Ypos'][star['table index']]

                        if False: #CONFIG == '10_3':
                            chip_num = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                            for div in config_bonn.chip_divide_10_3.keys():
                                if config_bonn.chip_divide_10_3[div][0] < x_rel <= config_bonn.chip_divide_10_3[div][1]:
                                    sub_chip = div
                            chip = str(chip_num) + '_' + str(sub_chip)
                        else:
                            chip = int(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] )
                            if not chip_dict.has_key(str(chip)):
                                chip_dict[str(chip)] = ''
                                print 'linear_fit| chip_dict.keys()=',chip_dict.keys() , ' CHIPS=',CHIPS

                        #if x < 2000 or y < 2000 or abs(LENGTH1 - x) < 2000 or abs(LENGTH2 - y) < 2000:
                        #    sigma = 1.5 * tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']]
                        #else:
                        sigma = tab[str(rotation) + '$' + exp['name'] + '$MAGERR_AUTO'][star['table index']]

                        if sigma < 0.001: sigma = 0.001
                        sigma = sigma # * 1000.
                        #sigma = 1

                        n = str(rotation) + '$' + exp['name'] + '$Xpos_ABS'
                        x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                        x_positions[row_num] = x
                        y_positions[row_num] = y
                        x = coord_conv_x(x)
                        y = coord_conv_y(y)

                        if calc_illum:
                            for c in position_columns:
                                col_num += 1
                                if c['rotation'] == rotation:
                                    value = c['fx'](x,y)*c['fy'](x,y)/sigma
                                    star_A.append([row_num,col_num,value])

                        first_exposure = True
                        for c in zp_columns:
                            col_num += 1
                            #if not degeneracy_break[c['im_rotation']] and c['image'] == exp['name']:
                            if not per_chip:
                                if (first_exposure is not True  and c['image'] == exp['name']):
                                    value = 1./sigma
                                    star_A.append([row_num,col_num,value])
                                if calc_illum and same_chips and c.has_key('chip'):
                                    if (c['chip'] == chip) and chip != CHIPS[0]:
                                        value = 1./sigma
                                        star_A.append([row_num,col_num,value])
                                first_exposure = False
                            #if per_chip:
                            #    if (first_column is not True and c['image'] == exp['name'] and c['chip'] == chip):
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
                                            value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                                            star_A.append([row_num,col_num,value])
                            else:
                                col_num += 1


                        ''' magnitude column -- include the correct/common magnitude '''
                        col_num += 1
                        value = 1./sigma
                        star_A.append([row_num,col_num+supa_num,value])
                        ra = tab[str(rotation) + '$' + exp['name'] + '$ALPHA_J2000'][star['table index']]
                        dec = tab[str(rotation) + '$' + exp['name'] + '$DELTA_J2000'][star['table index']]

                        if calc_illum or string.find(sample_size,'uncorr') != -1:
                            value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]/sigma
                        elif not calc_illum:
                            ''' correct the input magnitudes using the previously fitted correction '''
                            epsilon=0
                            for term in cheby_terms_use:
                                epsilon += fitvars[str(rotation)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                            epsilon += float(fitvars['zp_' + str(chip)])
                            value = (tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']] - epsilon)/sigma
                            #print 'linear_fit| epsilon=',epsilon , ' value=',value

                        star_B.append([row_num,value])
                        sigmas.append([row_num,sigma])


                        catalog_values[col_num+supa_num] = {'inst_value':value*sigma,'ra':ra,'dec':dec,'sigma':sigma} # write into catalog
                        #print 'linear_fit| catalog_values=',catalog_values , ' col_num+supa_num=',col_num+supa_num

                        #x_long = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                        #y_long = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]
                        #x = coord_conv_x(x_long)
                        #y = coord_conv_y(y_long)
                        #if fitvars_fiducial:
                        #    value += add_single_correction(x,y,fitvars_fiducial)

                    inst.append({'type':'match','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})

                    ''' only include one SDSS observation per star '''
                    #print sample , star["match"] , star["match"] and (sample=="all" or sample=="sdss" or sample=="bootstrap") # and tab["SDSSStar_corr"][star["table index"]] == 1
                    if star['match'] and (sample=='sdss' or sample=='bootstrap'): # and tab['SDSSStar_corr'][star['table index']] == 1:

                        star_A = [] ; star_B = [] ; sigmas = []
                        ''' need to filter out bad colored-stars '''
                        row_num += 1
                        col_num = -1
                        exp = star['supa files'][0]
                        rotation = exp['rotation']
                        sigma = tab['SDSSstdMagErr_corr'][star['table index']]
                        if sigma < 0.03: sigma = 0.03

                        for c in position_columns:
                            col_num += 1
                        first_column = True
                        for c in zp_columns:
                            col_num += 1
                            ''' remember that the good magnitude does not have any zp dependence!!! '''
                            if c['image'] == 'match':
                                value = 1./sigma
                                star_A.append([row_num,col_num,value])
                                x_positions[row_num] = x
                                y_positions[row_num] = y

                            first_column = False

                        ''' fit for the color term dependence for SDSS comparison -- '''
                        if relative_colors:
                            ''' this is if there are different color terms for EACH CHIP!'''
                            for c in color_columns:
                                col_num += 1
                                if c['name'] == 'SDSS_color':
                                    value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                                    star_A.append([row_num,col_num,value])
                        else:
                            col_num += 1
                            value = tab['SDSSstdMagColor_corr'][star['table index']]/sigma
                            star_A.append([row_num,col_num,value])

                        col_num += 1
                        ''' magnitude column -- include the correct/common magnitude '''
                        value = 1./sigma
                        star_A.append([row_num,col_num+supa_num,value])

                        value = tab['SDSSstdMag_corr'][star['table index']]/sigma
                        star_B.append([row_num,value])
                        sigmas.append([row_num,sigma])

                        inst.append({'type':'sdss','A_array':star_A, 'B_array':star_B, 'sigma_array': sigmas})

                        ''' record star information '''
                        for exp in star['supa files']:

                            rotation = exp['rotation']
                            x = tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']]
                            y = tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']]

                            x = coord_conv_x(x)
                            y = coord_conv_y(y)

                            if calc_illum or string.find(sample_size,'uncorr') != -1:
                                value = tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']]
                            elif not calc_illum:
                                ''' correct the input magnitudes using the previously fitted correction '''
                                epsilon=0
                                for term in cheby_terms_use:
                                    epsilon += fitvars[str(rotation)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
                                epsilon += float(fitvars['zp_' + str(chip)])
                                value = (tab[str(rotation) + '$' + exp['name'] + '$MAG_AUTO'][star['table index']] - epsilon)







                            rotation = str(exp['rotation'])
                            data[rotation].append(value - tab['SDSSstdMag_corr'][star['table index']])
                            Star[rotation].append(tab['SDSSStar_corr'][star['table index']])
                            magErr[rotation].append(tab['SDSSstdMagErr_corr'][star['table index']])
                            whichimage[rotation].append(exp['name'])
                            X[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Xpos_ABS'][star['table index']])
                            Y[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$Ypos_ABS'][star['table index']])
                            color[rotation].append(tab['SDSSstdMagColor_corr'][star['table index']])
                            chipnums[rotation].append(tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']])
                            #if tab[str(rotation) + '$' + exp['name'] + '$CHIP'][star['table index']] == 1:
                            #    print str(rotation) + '$' + exp['name'] + '$CHIP'
                        #print 'linear_fit| star_A=',star_A , ' star_B=',star_B , ' sigmas=',sigmas , ' sigma=',sigma
                print 'linear_fit| data.keys()=',data.keys()
                print 'linear_fit| EXPS=',EXPS
                for rot in EXPS.keys():
                    print 'linear_fit| rot=',rot , ' len(data[str(rot)])=',len(data[str(rot)])

                ''' save the SDSS matches '''
                matches = {'data':data,'magErr':magErr,'whichimage':whichimage,'X':X,'Y':Y,'color':color}
                uu = open(tmpdir + '/sdss','w')
                pickle.dump(matches,uu)
                uu.close()

                ''' do fitting '''
                #not quick!
                for attempt in ['first','rejected']:
                    print "linear_fit| adam-loop4-do_fitting: for attempt in ['first','rejected']:"
                    print 'linear_fit| adam-loop4-do_fitting: attempt=',attempt
                    ''' make matrices/vectors '''
                    Ainst_expand = []
                    for z in inst:
                        for y in z['A_array']:
                            Ainst_expand.append(y)

                    Binst_expand = []
                    for z in inst:
                        for y in z['B_array']:
                            Binst_expand.append(y)
                    print 'linear_fit| len(Binst_expand)=',len(Binst_expand)
                    ''' this gives the total number of rows added '''

                    sigmas_expand = []
                    for z in inst:
                        for y in z['sigma_array']:
                            sigmas_expand.append(y)
                    print 'linear_fit| len(sigmas_expand)=',len(sigmas_expand)

                    ylength = len(Binst_expand)
                    print 'linear_fit| y_length=',y_length , ' x_length=',x_length
                    print 'linear_fit| len(Ainst_expand)=',len(Ainst_expand) , ' len(Binst_expand)=',len(Binst_expand)
                    A = scipy.zeros([y_length,x_length])
                    B = scipy.zeros(y_length)
                    S = scipy.zeros(y_length)

                    if attempt == 'first': rejectlist = 0*copy(B)

                    Af = open('A','w')
                    Bf = open('b','w')

                    rejected = 0
                    rejected_x = [] ; rejected_y = [] ; all_x = [] ; all_y = [] ; all_resids = []
                    if attempt == 'rejected':
                        for ele in Ainst_expand:
                            if rejectlist[ele[0]] == 0:
                                if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]):
                                    all_x.append(float(str(x_positions[ele[0]])))
                                    all_y.append(float(str(y_positions[ele[0]])))
                                    all_resids.append(float(str(resids_sign[ele[0]])))
                            if rejectlist[ele[0]] == 0:
                                Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n')
                                #print ele, y_length, x_length
                                A[ele[0],ele[1]] = ele[2]
                            else:
                                rejected += 1
                                if x_positions.has_key(ele[0]) and y_positions.has_key(ele[0]):
                                    rejected_x.append(float(str(x_positions[ele[0]])))
                                    rejected_y.append(float(str(y_positions[ele[0]])))
                    else:
                        for ele in Ainst_expand:
                            Af.write(str(ele[0]) + ' ' + str(ele[1]) + ' ' + str(ele[2]) + '\n')
                            #print ele, y_length, x_length
                            A[ele[0],ele[1]] = ele[2]

                    for ele in Binst_expand:
                        if rejectlist[ele[0]] == 0:
                            B[ele[0]] = ele[1]

                    for ele in sigmas_expand:
                        if rejectlist[ele[0]] == 0:
                            S[ele[0]] = ele[1]

                    if attempt == 'rejected' and rejected > 0:
                        print 'linear_fit| rejected=',rejected

                        illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/'
                        print 'linear_fit| all_resids[0:100]=',all_resids[0:100]
                        print 'linear_fit| all_x[0:100]=',all_x[0:100]
                        print 'linear_fit| all_y[0:100]=',all_y[0:100]
                        print 'linear_fit| check'

                        os.system('mkdir -p ' + illum_dir)
                        print 'linear_fit| running calcDataIllum'
                        calcDataIllum(sample + 'reducedchi'+str(ROT)+FILTER,LENGTH1,LENGTH2,scipy.array(all_resids),scipy.ones(len(all_resids)),scipy.array(all_x),scipy.array(all_y),pth=illum_dir,rot=0,limits=[-10,10],ylab='Residual/Error')
                        print 'linear_fit| finished calcDataIllum'

                        dtmp = {}
                        dtmp['rejected']=rejected
                        dtmp['totalmeasurements']=rejected

                        #import ppgplot
                        #print rejected_x, rejected
                        x_p = scipy.array(rejected_x)
                        y_p = scipy.array(rejected_y)
                        x = sorted(copy(x_p))
                        y = sorted(copy(y_p))

                        reject_plot = illum_dir + sample + sample_size + 'rejects' + test + '.png'
                        dtmp['reject_plot']=reject_plot
                        dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,'linearfit':'1'})
                        save_fit(dtmp)

                        #file = f + 'pos' + test.replace('_','') + '.png'
                        pylab.scatter(x_p,y_p,linewidth=None)
                        pylab.xlabel('X axis')
                        pylab.ylabel('Y axis')     # label the plot
                        pylab.ylim(y_p[0],y_p[-1])
                        pylab.xlim(x_p[0],x_p[-1])
                        print 'linear_fit| file=',file
                        pylab.savefig(reject_plot)
                        pylab.clf()





                    Bstr = reduce(lambda x,y:x+' '+y,[str(z[1]) for z in Binst_expand])
                    Bf.write(Bstr)
                    Bf.close()
                    Af.close()

                    print 'linear_fit| finished matrix....'
                    print 'linear_fit| len(position_columns)=',len(position_columns) , ' len(zp_columns)=',len(zp_columns)
                    print A[0,0:30], B[0:10], scipy.shape(A), scipy.shape(B)
                    print A[1,0:30], B[0:10], scipy.shape(A), scipy.shape(B)
                    print 'linear_fit| hi!'

                    Af = open(tmpdir + '/B','w')
                    for i in range(len(B)):
                        Af.write(str(B[i]) + '\n')
                    Af.close()

                    print 'linear_fit| solving matrix...'
                    os.system('rm x')
                    ooo=os.system('./sparse < A') 
		    if ooo!=0: raise Exception("the line os.system('./sparse < A') failed\n'./sparse < A'="+'./sparse < A')
                    bout = open('x','r').read()

                    res = re.split('\s+',bout[:-1])
                    Traw = [float(x) for x in res][:x_length]

                    res = re.split('\s+',bout[:-1].replace('nan','0').replace('inf','0'))
                    T = [float(x) for x in res][:x_length]

                    params = {}
                    for i in range(len(T)):
                        if i < len(column_names):
                            params[column_names[i]] = T[i]
                            if string.find(column_names[i],'mag') == -1:
                                print 'linear_fit| column_names[i]=',column_names[i] , ' T[i]=',T[i], ' Traw[i]=',Traw[i]
                            if T[i] == -99:
                                print 'linear_fit| column_names[i]=',column_names[i] , ' T[i]=',T[i]
                        if catalog_values.has_key(i):
                            catalog_values[i]['mag'] = T[i]


                    U = [float(x) for x in res][:x_length]

                    print 'linear_fit| finished solving...'

                    #print 'linear_fit| doing linear algebra'
                    #U = scipy.linalg.lstsq(A,B)
                    #print U[0][0:30]

                    ''' calculate reduced chi-squared value'''
                    print 'linear_fit| scipy.shape(A)=',scipy.shape(A) , ' len(U)=',len(U) , ' x_length=',x_length , ' len(res)=',len(res)
                    Bprime = scipy.dot(A,U)
                    print 'linear_fit| scipy.shape(Bprime)=',scipy.shape(Bprime) , ' scipy.shape(B)=',scipy.shape(B)

                    ''' number of free parameters is the length of U '''
                    Bdiff = (abs((B-Bprime)**2.)).sum()/(len(B) - len(U))
                    parameters = len(B) - len(U)
                    chi_squared_sum = (abs((B-Bprime)**2.)).sum()
                    number_of_datapoints = len(B)
                    number_of_parameters = len(U)

                    resids = abs(B-Bprime)
                    resids_sign = B-Bprime
                    rejectlist = []
                    rejectnums = 0
		    #for u in resids: print 'linear_fit| u=',u
		    print 'linear_fit| (resids==0).sum()=',(resids==0).sum()
		    print 'linear_fit| (resids!=0).sum()=',(resids!=0).sum()
		    print 'linear_fit| resids.mean()=',resids.mean()
                    print 'linear_fit| len(resids)=',len(resids)
                    print 'linear_fit| attempt=',attempt
                    print 'linear_fit| sample_size=',sample_size , ' try_linear=',try_linear
                    #print [z for z in resids*S]
                    for i in range(len(resids)):
                        if resids[i] > 5: #*S[i] > 0.1: # or resids[i]==0:
                            rejectlist.append(1)
                            rejectnums += 1
                        else: rejectlist.append(0)
                    print 'linear_fit| (B-Bprime)[:20]=',(B-Bprime)[:20]
                    print 'linear_fit| len(resids)=',len(resids) , ' rejectnums=',rejectnums
                    print 'linear_fit| U[0:20]=',U[0:20]
                    print 'linear_fit| x[0:20]=',x[0:20]
                    reducedchi = Bdiff

                    ''' number of free parameters is the length of U , number of data points is B '''
                    difference = (abs(abs((B-Bprime)*S))).sum()/len(B)
                    chisq = (abs((B-Bprime)**2.)).sum()
                    print 'linear_fit| chisq=',chisq
                    print 'linear_fit| parameters=',parameters
                    print 'linear_fit| difference=',difference
                    print  "reducedchi=", reducedchi, ' (reduced chi-squared)'
                    #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'reducedchi$'+sample+'$'+sample_size:Bdiff})
		    #adam-needed?#data_directory = '/nfs/slac/g/ki/ki04/pkelly/illumination/'

                    position_fit = [['Xpos_ABS','Xpos_ABS'],['Xpos_ABS','Ypos_ABS'],['Ypos_ABS','Ypos_ABS'],['Xpos_ABS'],['Ypos_ABS']]
                    ''' save fit information '''
                    #print  sample+'$'+sample_size+'$' + str(ROT) + '$positioncolumns',reduce(lambda x,y: x+','+y,[z['name'] for z in position_columns])

                    if match:
                        save_columns = position_columns + zp_columns + color_columns
                    else:
                        save_columns = position_columns + zp_columns

                    dtmp = {}
                    #for ROT in EXPS.keys():
                    #   dtmp['zp_' + ROT] = params['zp_' + ROT]
                    fitvars = {}
                    zp_images = ''
                    zp_images_names = ''
                    for ele in save_columns:
                        print 'linear_fit| ele=',ele
                        res = re.split('$',ele['name'])
                        ''' save to own column if not an image zeropoint '''
                        if string.find(ele['name'],'zp_image') == -1:
                            fitvars[ele['name']] = U[ele['index']]
                            term_name = ele['name']
                            print 'linear_fit| term_name=',term_name
                            dtmp[term_name]=fitvars[ele['name']]
                            print 'linear_fit| ele["name"]=',ele["name"] , ' fitvars[ele["name"]]=',fitvars[ele["name"]]
                        else:
                            zp_images += str(U[ele['index']]) + ','
                            zp_images_names += ele['name'] + ','

                    print 'linear_fit| save_columns=', save_columns,
                    print 'linear_fit| zp_columns=', zp_columns
                    zp_images = zp_images[:-1]
                    zp_images_names = zp_images_names[:-1]
                    term_name = 'zp_images'
                    print 'linear_fit| term_name=',term_name
                    dtmp[term_name]=zp_images
                    print 'linear_fit| dtmp[term_name]=',dtmp[term_name]

                    term_name = 'zp_images_names'
                    print 'linear_fit| term_name=',term_name
                    dtmp[term_name]=zp_images_names
                    print 'linear_fit| dtmp[term_name]=',dtmp[term_name]


                    print 'linear_fit| dtmp.keys()=',dtmp.keys()
                    use_columns = filter(lambda x: string.find(x,'zp_image') == -1,[z['name'] for z in save_columns] ) + ['zp_images','zp_images_names']

                    positioncolumns = reduce(lambda x,y: x+','+y,use_columns)

                    print 'linear_fit| positioncolumns=',positioncolumns
                    #save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,sample+'$'+sample_size+'$positioncolumns':positioncolumns})
                    dtmp['positioncolumns'] = positioncolumns
                    dtmp[attempt + 'reducedchi']=reducedchi
                    dtmp[attempt + 'difference']=difference
                    dtmp[attempt + 'chisq']= chisq
                    dtmp[attempt + 'parameters']= parameters
                    print 'linear_fit| chisq=', chisq
                    print 'linear_fit| parameters=', parameters



                    #term_name = sample+'$'+sample_size+'$0x1y'
                    #print term_name, '!!!!!'
                    #if 0:
                    #    print fitvars['1$0x1y'], '1$0x1y'
                    #    term_name = sample+'$'+sample_size+'$1$0x1y'
                    #    dtmp[term_name] = 1.
                    #    term_name = sample+'$'+sample_size+'$0$1x0y'
                    #    dtmp[term_name] = 1.
                    #    fitvars['1$0x1y'] = 1.
                    #    fitvars['0$1x0y'] = 1.
                    #    print fitvars

                    print 'linear_fit| dtmp.keys()=',dtmp.keys()
                    print 'linear_fit| stop'
                    print 'linear_fit| dtmp["positioncolumns"]=',dtmp["positioncolumns"] , ' PPRUN=',PPRUN , ' FILTER=',FILTER , ' OBJNAME=',OBJNAME
                    dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,'linearfit':'1'})
                    save_fit(dtmp)

                ''' save the corrected catalog '''

                tmp = {}
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

                print 'linear_fit| data start'
                cols.append(pyfits.Column(name='stdMag_corr', format='D',array=scipy.array(stdMag_corr)))
                cols.append(pyfits.Column(name='stdMagErr_corr', format='D',array=scipy.array(stdMagErr_corr)))
                cols.append(pyfits.Column(name='stdMagColor_corr', format='D',array=scipy.array(stdMagColor_corr)))
                cols.append(pyfits.Column(name='stdMagClean_corr', format='D',array=scipy.array(stdMagClean_corr)))
                cols.append(pyfits.Column(name='ALPHA_J2000', format='D',array=scipy.array(ALPHA_J2000)))
                cols.append(pyfits.Column(name='DELTA_J2000', format='D',array=scipy.array(DELTA_J2000)))
                cols.append(pyfits.Column(name='SeqNr', format='E',array=scipy.array(SeqNr)))
                cols.append(pyfits.Column(name='Star_corr', format='E',array=scipy.array(Star_corr)))

                outcat = data_path + 'PHOTOMETRY/ILLUMINATION/' + 'catalog_' + PPRUN + '.cat'
                print 'linear_fit| cols=',cols
                hdu = pyfits.PrimaryHDU()
                hdulist = pyfits.HDUList([hdu])
                tbhu = pyfits.new_table(cols)
                hdulist.append(tbhu)
                hdulist[1].header.update('EXTNAME','OBJECTS')
                #adam-del# os.system('rm ' + outcat)
                hdulist.writeto( outcat ,clobber=True)
                print 'linear_fit| wrote out new cat'
                print 'linear_fit| outcat=',outcat

                save_fit({'PPRUN':PPRUN,'OBJNAME':OBJNAME,'FILTER':FILTER,'format':'good','sample':'record','sample_size':'record'},db='' + test + 'try_db')

                save_fit({'FILTER':FILTER,'OBJNAME':OBJNAME,'PPRUN':PPRUN,'sample':sample,'sample_size':sample_size,'catalog':outcat})
                #save_exposure({type + 'atch':outcat},SUPA,FLAT_TYPE)
                #tmp[type + 'sdssmatch'] = outcat

                ''' make diagnostic plots '''
                if string.find(sample_size,'rand') == -1:
                    d = get_fits(OBJNAME,FILTER,PPRUN, sample, sample_size)
                    print 'linear_fit| d.keys()=',d.keys()
                    column_prefix = '' #sample+'$'+sample_size+'$'
                    position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns'])
                    print 'linear_fit| position_columns_names=',position_columns_names
                    fitvars = {}
                    cheby_terms_dict = {}
                    print 'linear_fit| column_prefix=',column_prefix , ' position_columns_names=',position_columns_names
                    for ele in position_columns_names:
                        print 'linear_fit| ele=',ele
                        if type(ele) != type({}):
                            ele = {'name':ele}
                        res = re.split('$',ele['name'])
                        if string.find(ele['name'],'zp_image') == -1:
                            fitvars[ele['name']] = float(d[ele['name']])
                            for term in cheby_terms:
                                if term['n'] == ele['name'][2:]:
                                    cheby_terms_dict[term['n']] = term

                    zp_images = re.split(',',d['zp_images'])
                    zp_images_names = re.split(',',d['zp_images_names'])

                    for i in range(len(zp_images)):
                        fitvars[zp_images_names[i]] = float(zp_images[i])

                    print 'linear_fit| fitvars=',fitvars




                    cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]

                    print 'linear_fit| cheby_terms_use=',cheby_terms_use

                    ''' make images of illumination corrections '''
                    if calc_illum:
                        for ROT in EXPS.keys():
                            size_x=LENGTH1
                            size_y=LENGTH2
                            bin=100
                            x,y = numpy.meshgrid(numpy.arange(0,size_x,bin),numpy.arange(0,size_y,bin))
                            F=0.1
                            print 'linear_fit| calculating'
                            x = coord_conv_x(x)
                            y = coord_conv_y(y)

                            illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT) + '/'
                            os.system('mkdir -p ' + illum_dir)

                            epsilon = 0
                            index = 0
                            for term in cheby_terms_use:
                                index += 1
                                print 'linear_fit| index=',index , ' ROT=',ROT , ' term=',term , ' fitvars[str(ROT)+"$"+term["n"]]=',fitvars[str(ROT)+"$"+term["n"]]
                                epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

                            ''' save pattern w/o chip zps '''
                            #im = illum_dir + '/nochipzps' + sample + sample_size +  test + '.fits' #adam-namefix
                            im = illum_dir + '_'.join([ '/nochipzps' , sample , sample_size ,  test]) + '.fits'
                            print "linear_fit| ...writing...im=",im
                            hdu = pyfits.PrimaryHDU(epsilon)
                            save_fit({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,str(ROT)+'$im':im})
                            hdu.writeto(im,clobber=True)

                            ''' save pattern w/ chip zps '''
                            if per_chip or same_chips:
                                print 'linear_fit| CHIPS=',CHIPS
                                for CHIP in CHIPS:
                                    if str(dt['CRPIX1_' + str(CHIP)]) != 'None':
                                        #fragments_removed: #this would be usefull if you wanted to have the IC treat each individual readout port in each CCD (unnecessary)
                                        xmin = float(dt['CRPIX1ZERO']) - float(dt['CRPIX1_' + str(CHIP)])
                                        xmax = xmin + float(dt['NAXIS1_' + str(CHIP)])
                                        ymin = float(dt['CRPIX2ZERO']) - float(dt['CRPIX2_' + str(CHIP)])
                                        ymax = ymin + float(dt['NAXIS2_' + str(CHIP)])

                                        print 'linear_fit| xmin=',xmin , ' xmax=',xmax , ' ymin=',ymin , ' ymax=',ymax , ' CHIP=',CHIP
                                        print 'linear_fit| int(xmin/bin),=',int(xmin/bin), int(xmax/bin), int(ymin/bin), int(ymax/bin), CHIP, bin, scipy.shape(epsilon)
                                        print 'linear_fit| epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]=',epsilon[int(xmin/bin):int(xmax/bin)][int(ymin/bin):int(ymax/bin)]
                                        print 'linear_fit| fitvars.keys()=',fitvars.keys()
                                        print 'linear_fit| zp', fitvars['zp_' + str(CHIP)]
                                        epsilon[int(ymin/bin):int(ymax/bin),int(xmin/bin):int(xmax/bin)] += float(fitvars['zp_' + str(CHIP)])

                            #im = illum_dir + '/correction' + sample + sample_size +  test + '.fits' #adam-namefix
                            im = illum_dir + '_'.join([ '/correction' , sample , sample_size ,  test]) + '.fits'
                            print 'linear_fit| ...writing...im=',im
                            hdu = pyfits.PrimaryHDU(epsilon)
                            save_fit({'linearplot':1,'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size,str(ROT)+'$im':im})
                            hdu.writeto(im,clobber=True)
                            print 'linear_fit| done'

                ''' don't make these plots if it's a random run '''
                if match and sample != 'None' and string.find(sample_size,'rand') == -1:
                    ''' calculate matched plot differences, before and after '''
                    for ROT in EXPS.keys():
                        data[ROT] = scipy.array(data[ROT])
                        print 'linear_fit| scipy.array(data[ROT])=',scipy.array(data[ROT]) , ' ROT=',ROT
                        print 'linear_fit| EXPS=',EXPS

                        color[ROT] = scipy.array(color[ROT])

                        ''' apply the color term measured from the data '''
                        zp_correction = scipy.array([float(fitvars['zp_image_'+x]) for x in whichimage[ROT]])
                        #data1 = data[ROT] - fitvars['SDSS_color']*color[ROT]  - zp_correction
                        data1 = data[ROT] + fitvars['SDSS_color']*color[ROT] - zp_correction
                        #print data1, data[ROT], fitvars['SDSS_color'], color[ROT], zp_correction
                        print 'linear_fit| len(data1)=',len(data1) , ' len(data[ROT])=',len(data[ROT]) , ' match=',match , ' sample=',sample

                        ''' it looks like I am subtracting the median magnitude for each star?? '''
                        data2 = data1 - (data1/data1*scipy.median(data1))
                        illum_dir = data_path + 'PHOTOMETRY/ILLUMINATION/' + FILTER + '/' + PPRUN + '/' + str(ROT) + '/'
                        for kind,keyvalue in [['star',1]]: #['galaxy',0],

                            calcDataIllum(sample + kind + 'nocorr'+str(ROT)+FILTER,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue])
                            dtmp = {}
                            var = variance(data2,magErr[ROT])
                            print 'linear_fit| var=',var
                            dtmp[sample + 'stdnocorr$' + str(ROT)] = var[1]**0.5
                            dtmp[sample + 'redchinocorr$' + str(ROT)] = var[2]
                            dtmp[sample + 'pointsnocorr$' + str(ROT)] = len(data2)
                            print 'linear_fit| sample+"redchinocorr$"+str(ROT)=',sample+"redchinocorr$"+str(ROT)

                            if calc_illum:
                                #plot_color(color[ROT], data2)
                                #print X[ROT]
                                x = coord_conv_x(scipy.array(X[ROT]))
                                y = coord_conv_y(scipy.array(Y[ROT]))

                                #epsilon = 0
                                #for term in cheby_terms:
                                #    data += fitvars[term[str(ROT)+'$'+'n']]*term['fx'](x,y)*term['fy'](x,y)

                                epsilon=0
                                for term in cheby_terms_use:
                                    epsilon += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)

                                chipcorrect = []
                                #print chipnums
                                if CONFIG != '10_3':
                                    for chip in chipnums[ROT]:
                                        chipcorrect.append(fitvars['zp_' + str(int(float(chip)))])
                                    chipcorrect = scipy.array(chipcorrect)
                                    epsilon += chipcorrect


                                calcim = sample+kind+'correction'+str(ROT)+FILTER
                                calcDataIllum(calcim,10000,8000,epsilon,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue])

                                data2 -= epsilon

                                #print whichimage[ROT][0:100]
                                #data1 = data[ROT] - zp_correction
                                #data2 = data1 - (data1/data1*scipy.median(data1))
                                #plot_color(color[ROT], data2)

                                #print magErr[ROT][0:20]
                                calcim = sample+kind+'rot'+str(ROT)+FILTER
                                #print illum_dir
                                calcDataIllum(calcim,10000,8000,data2,magErr[ROT],X[ROT],Y[ROT],pth=illum_dir,rot=0,good=[Star[ROT],keyvalue])

                                var = variance(data2,magErr[ROT])
				print 'linear_fit| second: var=' , var
                                dtmp[sample + 'stdcorr$' + str(ROT)] = var[1]**0.5
                                dtmp[sample + 'redchicorr$' + str(ROT)] = var[2]
                                dtmp[sample + 'pointsnocorr$' + str(ROT)] = len(data2)

				print 'linear_fit| calcDataIllum: im=', im,  "calcim=",calcim, " len(data[ROT])=",len(data[ROT])

                            dtmp.update({'PPRUN':PPRUN,'FILTER':FILTER,'OBJNAME':OBJNAME,'sample':sample,'sample_size':sample_size})
                            save_fit(dtmp)

                            #print params['SDSS_color'], 'SDSS_color'
                            print 'linear_fit| OBJNAME=',OBJNAME , ' FILTER=',FILTER , ' PPRUN=',PPRUN , ' tmpdir=',tmpdir

    print "linear_fit| DONE with func"
    return


#adam-fragments_removed# calcDataIllum-old
def calcDataIllum(file, LENGTH1, LENGTH2, data,magErr, X, Y, pth, rot=0, good=None, limits=[-0.4,0.4], ylab='SUBARU-SDSS'):
    '''inputs: file, LENGTH1, LENGTH2, data,magErr, X, Y, pth, rot=0, good=None, limits=[-0.4,0.4], ylab='SUBARU-SDSS'
    parameters: pth: path to dir where plots will be placed
    returns:
    calls:
    called_by: linear_fit,linear_fit,linear_fit,linear_fit'''

    print 'calcDataIllum: START the func. inputs: file=',file , ' LENGTH1=',LENGTH1 , ' LENGTH2=',LENGTH2 , ' data=',data , ' magErr=',magErr , ' X=',X , ' Y=',Y , ' pth=',pth , ' rot=',rot , ' good=',good , ' limits=',limits , ' ylab=',ylab
    #from ppgplot import *

    f = pth + file + '.pickle'
    calcDataIllum_info = {'file':file, 'LENGTH1':LENGTH1, 'LENGTH2': LENGTH2, 'data': data, 'magErr':magErr, 'X':X, 'Y':Y, 'pth':pth, 'rot':rot, 'good':good, 'limits':limits, 'ylab':ylab}
    output = open(f,'wb')
    pickle.dump(calcDataIllum_info,output)
    output.close()

    X_sort = copy(X) ; Y_sort = copy(Y)
    X_sort = numpy.sort(X_sort) ; Y_sort = numpy.sort(Y_sort)
    X_min = X_sort[0] ; Y_min = Y_sort[0]
    X_max = X_sort[-1] ; Y_max = Y_sort[-1]
    X_width = abs(X_max - X_min) ; Y_width = abs(Y_max - Y_min)

    nbin1 =15 ; nbin2 =15
    bin1 = int(LENGTH1/nbin1) ; bin2 = int(LENGTH2/nbin2)
    diff_weightsum = -9999*numpy.ones([nbin1,nbin2]) ; diff_invvar = -9999*numpy.ones([nbin1,nbin2]) ; diff_X = -9999*numpy.ones([nbin1,nbin2]) ; diff_Y = -9999*numpy.ones([nbin1,nbin2])
    X_cen = [];Y_cen = [];data_cen = [];zerr_cen = []

    chisq = 0
    for i in range(len(data)):
        if good is not None:
            use = good[0][i] == good[1]
        else:
            use = True
        if use:
	    #if 1: # LENGTH1*0.3 < X[i] < LENGTH1*0.6:
            X_cen.append(X[i])
            Y_cen.append(Y[i])
            data_cen.append(data[i])
            zerr_cen.append(magErr[i])

            chisq += data[i]**2./magErr[i]**2.

            x_val = int((X[i])/float(bin1))  # + size_x/(2*bin)
            y_val = int((Y[i])/float(bin2))  #+ size_y/(2*bin)
            err = magErr[i]
            ''' lower limit on error '''
            if err < 0.04: err = 0.04
            weightsum = data[i]/err**2.
            weightX = X[i]/err**2.
            weightY = Y[i]/err**2.
            invvar = 1/err**2.

	    #if 1: #0 <= x_val and x_val < int(nbin1) and y_val >= 0 and y_val < int(nbin2):  #0 < x_val < size_x/bin and 0 < y_val < size_y/bin:
	    #print x_val, y_val
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
		    print 'calcDataIllum: failure where diff_weightsum[x_val][y_val] is an index error: i=',i , ' x_val=',x_val , ' y_val=',y_val

    redchisq = chisq**0.5 / len(data)
    print 'calcDataIllum: redchisq=', redchisq

    x_p = scipy.array(X_cen)
    y_p = scipy.array(Y_cen)
    z_p = scipy.array(data_cen)
    zerr_p = scipy.array(zerr_cen)

    mean = diff_weightsum/diff_invvar
    err = 1/diff_invvar**0.5
    print 'calcDataIllum: mean=',mean
    print 'calcDataIllum: err=',err

    f = pth + file
    print 'calcDataIllum: ...writing...'
    print 'calcDataIllum: f=',f
    hdu = pyfits.PrimaryHDU(mean)
    diffmap_fits_name= f + '_diffmap.fits'
    hdu.writeto(diffmap_fits_name,clobber=True)
    hdu = pyfits.PrimaryHDU(err)
    diffinvvar_fits_name= f + '_diffinvvar.fits'
    hdu.writeto(diffinvvar_fits_name,clobber=True)

    ''' now make cuts with binned data '''
    mean_flat = scipy.array(mean.flatten(1))
    print 'calcDataIllum: mean_flat=',mean_flat
    err_flat = scipy.array(err.flatten(1))
    print 'calcDataIllum: err_flat=',err_flat
    mean_X = scipy.array((diff_X/diff_invvar).flatten(1))
    print 'calcDataIllum: mean_X=',mean_X
    mean_Y = scipy.array((diff_Y/diff_invvar).flatten(1))
    print 'calcDataIllum: mean_Y=',mean_Y

    '''set pylab parameters'''
    params = {'backend' : 'ps',
         'text.usetex' : True,
          'ps.usedistiller' : 'xpdf',
          'ps.distiller.res' : 6000}
    pylab.rcParams.update(params)
    fig_size = [6,4]
    params = {'axes.labelsize' : 16,
              'text.fontsize' : 16,
              'legend.fontsize' : 16,
              'xtick.labelsize' : 12,
              'ytick.labelsize' : 12,
              'figure.figsize' : fig_size}
    pylab.rcParams.update(params)

    diffp_png_name= f + '_diffp_' + test.replace('_','') + '.png'
    pylab.clf()
    pylab.subplot(211)
    pylab.xlabel('X axis')
    pylab.ylabel('SDSS-SUBARU')     # label the plot
    pylab.scatter(mean_X,mean_flat,linewidth=0)
    pylab.errorbar(mean_X,mean_flat,err_flat,lw=0.)
    pylab.ylim(limits)
    pylab.xlim(x[0],x[-1])
    pylab.subplot(212)
    pylab.scatter(mean_Y,mean_flat,linewidth=0)
    pylab.errorbar(mean_Y,mean_flat,err_flat,lw=0)
    pylab.ylim(limits)
    pylab.xlim(y[0],y[-1])
    pylab.xlabel('Y axis')
    pylab.ylabel(ylab)     # label the plot
    pylab.savefig(diffp_png_name)
    pylab.clf()
    print 'calcDataIllum: finished: diffp_png_name=',diffp_png_name

    #x_p = x_p[z_p>0.2]
    #y_p = y_p[z_p>0.2]
    #z_p = z_p[z_p>0.2]

    pos_png_name= f + '_pos_' + test.replace('_','') + '.png'
    pylab.scatter(x_p,y_p,linewidth=None)
    pylab.xlabel('X axis')
    pylab.ylabel('Y axis')     # label the plot
    pylab.ylim(y[0],y[-1])
    pylab.xlim(x[0],x[-1])
    pylab.savefig(pos_png_name)
    pylab.clf()
    print 'calcDataIllum: finished: pos_png_name=',pos_png_name

    diff_png_name= f + '_diff_' + test.replace('_','') + '.png'
    pylab.subplot(211)
    pylab.scatter(x_p,z_p,linewidth=0)
    pylab.ylim(limits)
    pylab.xlim(x[0],x[-1])
    pylab.xlabel('X axis')
    pylab.ylabel(ylab)     # label the plot
    pylab.subplot(212)
    pylab.scatter(y_p,z_p)
    pylab.ylim(limits)
    pylab.xlim(y[0],y[-1])
    pylab.xlabel('Y axis')
    pylab.ylabel(ylab)     # label the plot
    pylab.savefig(diff_png_name)
    pylab.clf()
    print 'calcDataIllum: finished: diff_png_name=',diff_png_name

    print "calcDataIllum: DONE with func"
    return
