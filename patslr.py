def mkcolorcolor(filt,catalog,starcatalog,cluster):
    locus_c = locus()
    import os
    base = os.environ['sne'] + '/photoz/' + cluster + '/'
    f = open(base + 'stars.html','w')
    print filt
    filt.sort(sort_filters)
    print filt

    ''' group filters '''
    groups = {}
    for filter in filt:
        num = filt_num(filter)
        if not num in groups:
            groups[num] = []
        groups[num].append(filter)

    print groups
    print catalog

    import random, pyfits

    p = pyfits.open(catalog)['OBJECTS'].data

    s = pyfits.open(starcatalog)
    indices = s['OBJECTS'].data.field('SeqNr')
    dict = {}
    for index in indices:
        p.field('CLASS_STAR')[index-1] = -99 

    mask = p.field('CLASS_STAR') == -99 
    p = p[mask]


    #while not plot:

    list = []
    for g in sorted(groups.keys()):
        list.append(groups[g])

    print list

    l_new = []
    l_fs = {}

    locus_dict = {}
    for filt in list:
        a_short = filt[0].replace('+','').replace('C','')[-1]
        print filt, a_short

        import string
                                       
        if a_short == a_short.upper() and string.find(filt[0],'Z') == -1 and string.find(filt[0],'SUBARU') != -1:
            a_short = a_short + 'JOHN'
        elif a_short == a_short.upper() and string.find(filt[0],'Z') != -1 and string.find(filt[0],'SUBARU') != -1:
            a_short = a_short + 'SUBARU'
        elif a_short != a_short.upper() and string.find(filt[0],'MEGA') != -1:
            a_short = a_short.upper() + 'CFHT'


        l_new.append([filt,a_short])
        l_fs[a_short] = 'yes'
        #print a_short, filt
        locus_dict[a_short] = filt[0] 


    print l_fs

    import re
    good_fs = []
    for k1 in locus_c.keys():
        res = re.split('_',k1)
        print res
        if l_fs.has_key(res[0]) and l_fs.has_key(res[1]):
            good_fs.append([res[0],res[1]])

    print good_fs
    print l_fs
    raw_input()

    for f1A,f1B in good_fs:         
        for f2A,f2B in good_fs:         
            if f1A!=f1B: # and f2A!=f2B:
                a = locus_dict[f1A] 
                b = locus_dict[f1B]
                c = locus_dict[f2A]
                d = locus_dict[f2B]
                
                
                
                
                import string                                                                                                   
                def fix(q): 
                    if string.find(q,'MEGA') != -1:         
                        import re                           
                        res = re.split('-',q)               
                        q = 'MEGAPRIME-0-1-' + res[-1]      
                    print q                                 
                    return q                                
                                                                                                                                                
                                                                                                                                                
                #print catalog , starcatalog                            
                #px = pickles.field(fix(a)) - pickles.field(fix(b))    
                #py = pickles.field(fix(b)) - pickles.field(fix(c))    
                #print px,py                                           
                                                                       
                import pylab                                           
                                                                       
                pylab.clf()                                            

                
                if 0: #a==b or ==f2B:                                
                    print a,b,c,d
                    print f1A,f1B,f2A,f2B
                    raw_input()
                                                                       
                pylab.xlabel(a + ' - ' + b)                            
                pylab.ylabel(c + ' - ' + d)                            
                                                                       
                #pylab.savefig(outbase + '/RedshiftErrors.png')        
                                                                       
                                                                      
                                                                      
                table = p                                             
                                                                      
                print 'MAG_APER-' + a                                 
                print a,b,c                                           
                #print table.field('MAG_APER-' + a)                    
                at = table.field('MAG_APER-' + a)[:,1]                
                bt = table.field('MAG_APER-' + b)[:,1]                
                ct = table.field('MAG_APER-' + c)[:,1]                
                dt = table.field('MAG_APER-' + d)[:,1]                
                                                                      
                bt = bt[at!=-99]                                      
                ct = ct[at!=-99]                                      
                dt = dt[at!=-99]                                      
                at = at[at!=-99]                                      
                                                                      
                at = at[bt!=-99]                                      
                ct = ct[bt!=-99]                                      
                dt = dt[bt!=-99]                                      
                bt = bt[bt!=-99]                                      
                                                                      
                at = at[ct!=-99]                                      
                bt = bt[ct!=-99]                                      
                dt = dt[ct!=-99]                                      
                ct = ct[ct!=-99]                                      

                at = at[dt!=-99]                                      
                bt = bt[dt!=-99]                                      
                ct = ct[dt!=-99]                                      
                dt = dt[dt!=-99]                                      
                                                                      
                if len(at) and len(bt) and len(ct) and len(dt) and len(locus_c[f1A + '_' + f1B])==len(locus_c[f2A + '_' + f2B]):                   
                    x = at - bt                                       
                    y = ct -dt                                        
                                                                      
                    x = x[:1000]                                      
                    y = y[:1000]                                      
                                                                      
                    #print x, y                                        
                    pylab.scatter(x,y,s=1)                            
                                                                      
                    pylab.scatter(locus_c[f1A + '_' + f1B],locus_c[f2A + '_' + f2B],color='red',s=1.)                  

 

                                                                      
                    #pylab.axis([sorted(x)[5],sorted(x)[-5],sorted(y)[5
                    file = a+ b+ c+ d + '.png'    
                    pylab.savefig(base + file)                        
                    pylab.clf()                                       
                                                                      
                    f.write('<img src=' + file + '>\n')               
                plot = False                                          
                            
    f.close()
