def add_correction_new(cat_list,OBJNAME,FILTER,PPRUN):

    import scipy, re, string, os

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
   
    cov = 1

    if cov:
        samples = [['sdss',cheby_terms,True]] #,['nosdss',cheby_terms_no_linear,False]] #[['nosdss',cheby_terms_no_linear],['sdss',cheby_terms]]
    else: 
        samples = [['nosdss',cheby_terms_no_linear,False]]

    sample = 'sdss'
    sample_size = 'all'
    import re, time                                                                                                                
    dt = get_a_file(OBJNAME,FILTER,PPRUN)                
    d = get_fits(OBJNAME,FILTER,PPRUN)                
    print d.keys()
    column_prefix = sample+'$'+sample_size+'$'
    position_columns_names = re.split('\,',d[column_prefix + 'positioncolumns']) 
    print position_columns_names, 'position_columns_names'
    fitvars = {}
    cheby_terms_dict = {}
    print column_prefix, position_columns_names
    for ele in position_columns_names:                      
        print ele
        if type(ele) != type({}):
            ele = {'name':ele}
        res = re.split('$',ele['name'])
        fitvars[ele['name']] = float(d[sample+'$'+sample_size+'$'+ele['name']])
        for term in cheby_terms:
            if term['n'] == ele['name'][2:]:
                cheby_terms_dict[term['n']] = term 
    cheby_terms_use =  [cheby_terms_dict[k] for k in cheby_terms_dict.keys()]
    
    print cheby_terms_use, fitvars
    
    CHIPS = [int(x) for x in re.split(',',dt['CHIPS'])]
    LENGTH1, LENGTH2 = dt['LENGTH1'], dt['LENGTH2']

    per_chip = True

    coord_conv_x = lambda x:(2.*x-0-LENGTH1)/(LENGTH1-0) 
    coord_conv_y = lambda x:(2.*x-0-LENGTH2)/(LENGTH2-0) 

    ''' make images of illumination corrections '''                                                                  
    for cat in cat_list:
        for ROT in EXPS.keys():
            for SUPA in EXPS[ROT]:
                import re
                print SUPA, cat
                res = re.split('$',cat[1])
                file = res[1]
                print file, cat 
                if file == SUPA: rotation = ROT

        print cat
        p = pyfits.open(cat[0])
        tab = p["OBJECTS"].data
        print tab.field('MAG_AUTO')[0:10] 
                                                
        x = coord_conv_x(tab.field('Xpos_ABS'))
        y = coord_conv_y(tab.field('Ypos_ABS'))

        CHIPS = tab.field('CHIP')

        chip_zps = []
        for i in range(len(CHIPS)):
            chip_zps.append(float(fitvars['zp_' + str(CHIPS[i])]))

        chip_zps = scipy.array(chip_zps)

        ''' save pattern w/ chip zps '''

        trial = False 
        children = []
        
        x = coord_conv_x(x)
        y = coord_conv_y(y)
        
        ''' correct w/ polynomial '''
        epsilonC = 0
        index = 0                                                                                                                
        for term in cheby_terms_use:
            index += 1
            print index, ROT, term, fitvars[str(ROT)+'$'+term['n']]
            
            epsilonC += fitvars[str(ROT)+'$'+term['n']]*term['fx'](x,y)*term['fy'](x,y)
        ''' add the zeropoint '''
        epsilonC += chip_zps 
        ''' save pattern w/o chip zps '''

        print epsilon[0:20]
        tab.field('MAG_AUTO')[:] = tab.field('MAG_AUTO')[:] - epsilonC
        print tab.field('MAG_AUTO')[0:20]
        new_name = cat[0].replace('.cat','.gradient.cat')
        os.system('rm ' + new_name)
        p.writeto(new_name)
        cat_grads.append([new_name,cat[1]])
    return cat_grads 
