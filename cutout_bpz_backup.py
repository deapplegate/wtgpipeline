import math, re, sys
import pylab  # matplotlib

#def mkstellarcolorplot():


def filt_num(x):
    filter_order = ['u','B','g','V','r','R','i','I','z','Z','J','H','K']
                                                                                                                  
    x = x.replace('SUBARU','').replace('SPECIAL','').replace('WIRCAM','').replace('MEGAPRIME','').replace('-J-','')
                                                                                                                  
    from copy import copy
    import string
    for e in range(len(filter_order)):
        if string.find(x,filter_order[e]) != -1:  
            x_num = copy(e)            

    return x_num

def sort_filters(x,y):
    ''' sort filter list to make color-color plots '''

    x_num = filt_num(x)
    y_num = filt_num(y)

    print x_num, y_num
    if x_num > y_num: return 1     
    elif x_num <= y_num: return -1     
        

def mkcolorcolor(filt,catalog,starcatalog,cluster):

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
        
    for i in range(len(list)-2):
        for filter in list[i]:
            plot = True 
            while plot:
                for filtcomp1 in list[i+1]:                                                                       
                    for filtcomp2 in list[i+2]:
                        #s = sorted(random.sample(range(len(filt)),3),reverse=True)                              
                        print s
                        import astropy.io.fits as pyfits, scipy
                        pickles = pyfits.open('Pickles.cat')                                                   
                        pickles = pickles['PICKLES'].data
                                                                                                                
                        a =  filter
                        b =  filtcomp1 
                        c =  filtcomp2 

                        print a, b, c
                        
                        import string
                                                                                                                 
                        def fix(q): 
                                                                                                                 
                            if string.find(q,'MEGA') != -1:             
                                import re
                                res = re.split('-',q)
                                q = 'MEGAPRIME-0-1-' + res[-1]
                            print q
                            return q
                                                                                                                 
                            
                        
                                                                                                                 
                                                                                                                 
                                                                                                                 
                                                                                                                 
                        print a
                                                                                                                
                        print catalog , starcatalog
                        px = pickles.field(fix(a)) - pickles.field(fix(b))
                        py = pickles.field(fix(b)) - pickles.field(fix(c))
                        print px,py
                                                                                                                
                        import pylab
                                                                                                                
                        pylab.clf()
                                                                                                                
                        
                        pylab.xlabel(a + ' - ' + b)
                        pylab.ylabel(b + ' - ' + c)
                        
                        #pylab.savefig(outbase + '/RedshiftErrors.png')
                                                                                                                
                                                                                                                
                        
                        table = p
                                                                                                                
                        print 'MAG_APER-' + a
                        print a,b,c
                        print table.field('MAG_APER-' + a)    
                        at = table.field('MAG_APER-' + a)[:,1]
                        bt = table.field('MAG_APER-' + b)[:,1]
                        ct = table.field('MAG_APER-' + c)[:,1]
                                                                                                                
                        bt = bt[at!=-99]
                        ct = ct[at!=-99]
                        at = at[at!=-99]
                                                                                                                
                        at = at[bt!=-99]
                        ct = ct[bt!=-99]
                        bt = bt[bt!=-99]
                                                                                                                
                        at = at[ct!=-99]
                        bt = bt[ct!=-99]
                        ct = ct[ct!=-99]
                                                                                                                
                        if len(at) and len(bt) and len(ct):
                            x = at - bt                      
                            y = bt -ct 
                                                             
                            x = x[:1000]
                            y = y[:1000]
                                                             
                            print x, y
                            pylab.scatter(x,y,s=1)
                                                             
                            pylab.scatter(px,py,color='red')

                            pylab.axis([sorted(x)[5],sorted(x)[-5],sorted(y)[5],sorted(y)[-5]])
                            file = filter + filtcomp1 + filtcomp2 + '.png'                                                             
                            pylab.savefig(base + file)
                            pylab.clf()

                            f.write('<img src=' + file + '>\n')
                        plot = False 






    f.close()



def plot_res(file_name,outbase):
    import MySQLdb                                                  
    import os, sys, anydbm, time
    import lib, scipy, pylab 
    from scipy import arange
   
    print file_name 
    
    file = open(file_name,'r').readlines()
    results = []
    for line in file:
        if line[0] != '#':
            import re                                     
            res = re.split('\s+',line)
            if float(res[5]) > 0.95:
                #for i in range(len(res)):
                #    print res[i],i
                results.append([float(res[1]),float(res[9])])
    
    diff = []
    z = []
    z_spec = []
    for line in results:
        diff_val = (line[0] - line[1])/(1 + line[1])
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])
    
    list = diff[:]  
    import pylab   
    varps = [] 
    a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016))
    print a,b,varp
    varps.append(varp[0])
    
    diffB = []
    for d in diff:
        if abs(d) < 0.08:
            diffB.append(d)
    diff = diffB
    list = scipy.array(diff)
    mu = list.mean()
    sigma = list.std()
    
    print 'mu', mu
    print 'sigma', sigma
    
    from scipy import stats
    pdf = scipy.stats.norm.pdf(b, mu, sigma)
    print 'pdf', pdf
    
    height = scipy.array(a).max()
    
    pylab.plot(b,len(diff)*pdf/pdf.sum(),'r')

    print b,len(diff)*pdf/pdf.sum()
    
    pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
    pylab.ylabel("Number of Galaxies")
    pylab.title(['mu ' + str(mu),'sigma ' + str(sigma)])
    print outbase
    pylab.savefig(outbase + '/RedshiftErrors.png')
    pylab.clf()
    
    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,4]),scipy.array([0,4]),color='red')
    pylab.xlim(0,4)
    pylab.ylim(0,4)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/RedshiftScatter04.png')
    pylab.clf()

    pylab.scatter(z_spec,z)
    pylab.plot(scipy.array([0,1]),scipy.array([0,1]),color='red')
    pylab.xlim(0,1)
    pylab.ylim(0,1)
    pylab.ylabel("PhotZ")
    pylab.xlabel("SpecZ")
    pylab.savefig(outbase + '/RedshiftScatter01.png')
    pylab.clf()

def scale(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val+48.60))
    

def scaleerr(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val))

def plot(file,outfile):
    #    for file in files:
    print file
    f=open(file,'r')
    lines=f.readlines()
    
    mag=[]
    magerr=[]
    lambdamean=[]
    lambdawidth=[]
    
    specmag=[]
    speclambda=[]
    specmag1=[]
    speclambda1=[]

    oldval=9999999.
    flag=0
    
    gal1info={}
    
    gal2info={}
    
    for line in lines:
        entries=re.split('\s+',line)
        if entries[0]=='GAL-1':
            gal1info['Model'] = entries[2]
            gal1info['Library'] = entries[3]
            

            
        if entries[0]=='GAL-2':
            gal2info['Model'] = entries[2]
            gal2info['Library'] = entries[3]
            


        if entries[0]!='':
            continue

        length=len(entries)

        
        
        if length > 4:
            # filter part
            if float(entries[1]) < 90:
                mag.append(scale(float(entries[1])))
                magerr.append(scaleerr(float(entries[2])))
                # magerr.append(0)
                lambdamean.append(float(entries[3]))
                lambdawidth.append(float(entries[4])/2)
        elif entries[1]>100 :
            if (oldval > entries[1]) and (float(oldval)/float(entries[1]) > 10) :
                flag=1

            if not flag:                                
                if float(entries[1]) < 12000 and float(entries[2]) < 25 and \
                   float(entries[1]) > 2000 and float(entries[2]) > 10:
                    speclambda.append(float(entries[1]))
                    specmag.append(scale(float(entries[2])))
                    oldval=entries[1]
            else :
                if float(entries[1]) < 12000 and float(entries[2]) < 25 and \
                   float(entries[1]) > 2000 and float(entries[2]) > 10:
                    speclambda1.append(float(entries[1]))
                    specmag1.append(scale(float(entries[2])))
                    oldval=entries[1]
                    
    pylab.xlabel("Lambda; Gal1 Model"+ gal1info['Model']+", lib:"+gal1info['Library']+\
                 ", Gal2: Model"+ gal2info['Model']+", lib:"+gal2info['Library'])
    
    pylab.ylabel("Log10(Flux)")
    pylab.plot(speclambda,specmag,'b-')
    #pylab.plot(speclambda1,specmag1,'g-')
    pylab.errorbar(lambdamean,mag,xerr=lambdawidth,yerr=magerr,fmt='ro')
    

    print "showing"
    pylab.savefig(outfile)
    pylab.clf()
    #pylab.show()

def plot_bpz_probs(id,file,outfile):    
    import re, scipy
    a = re.split('\(',file[0])
    b = re.split('\)',a[-1])
    r = [float(x) for x in re.split('\,',b[0])]
    x_axis = scipy.arange(r[0],r[1],r[2])

    for l in file:
        res = re.split('\s+',l)
        if l[0] != '#':
            if int(res[0]) == int(id):        
                arr = scipy.array([float(x) for x in res[1:-1]])
                import copy
                x_axis = x_axis[arr>0]
                x_axis = scipy.array([x_axis[0]-0.01] + list(x_axis) + [x_axis[-1]+0.01])
                arr = arr[arr>0]
                arr = scipy.array([0] + list(arr) + [0])
                
                pylab.fill(x_axis, arr,'b')
                pylab.xlabel('z')
                pylab.ylabel('P')
                pylab.savefig(outfile)
                pylab.clf()
    

def run(cluster):
    import astropy.io.fits as pyfits
    import os
    import os, sys, bashreader, commands
    from utilities import *
    from config_bonn import appendix, tag, arc, filters, filter_root, appendix_root

    print cluster
    
    path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster
    
    type='all'
    
    filecommand = open('record.analysis','w')
    
    BASE="coadd"
    image = BASE + '.fits'

    from glob import glob
    
    images = []
    filters.reverse()
    print filters
    ims = {}
    ims_seg = {}

    params = {'path':path, 
              'filter_root': filter_root, 
              'cluster':cluster, 
              'appendix':appendix, }


    catalog = '%(path)s/PHOTOMETRY/%(cluster)s.slr.cat' %params           
    starcatalog = '%(path)s/PHOTOMETRY/%(cluster)s.stars.calibrated.cat' %params           
    import do_multiple_photoz
    filterlist = do_multiple_photoz.get_filters(catalog,'OBJECTS')
    print filterlist
    mkcolorcolor(filterlist,catalog,starcatalog,cluster)





    ffile = os.environ['sne'] + '/photoz/' + cluster + '/all.tif'
    if not glob(ffile):
        for filter in filters[0:3]:                                                                 
            params = {'path':path, 
                      'filter_root': filter_root, 
                      'cluster':cluster, 
                      'filter':filter,
                      'appendix':appendix, }
            print params
            # now run sextractor to determine the seeing:              
            image = '%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits' %params 
            images.append(image)
            print 'reading in ' + image        
            seg_image = '/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits' % params
            ims[filter] = pyfits.open(image)[0].data
            print 'read in ' + image        
            #ims_seg[filter] = pyfits.open(seg_image)[0].data
        
        os.system('mkdir ' + os.environ['sne'] + '/photoz/' + cluster + '/')
        os.system('chmod o+rx ' + os.environ['sne'] + '/photoz/' + cluster + '/')
        
        from glob import glob
        os.system('stiff ' + reduce(lambda x,y:x + ' ' + y,images) + ' -OUTFILE_NAME ' + ffile + ' -BINNING 1 -GAMMA_FAC 1.6')
        os.system('convert ' + os.environ['sne'] + '/photoz/' + cluster + '/all.tif ' + os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')
    
    print ffile
    
    import Image
    im = Image.open(os.environ['sne'] + '/photoz/' + cluster + '/fix.tif')
    
    
    
    
    
    
    

    print catalog
    p_cat = pyfits.open(catalog)[1].data
    
    outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.spec.bpz.tab' % params 
    
    #outputcat = '%(path)s/PHOTOMETRY/all_bpz1_' % params 
    
    if glob(outputcat.replace('.tab','')):
        plot_res(outputcat.replace('.tab',''),os.environ['sne'] + '/photoz/' + cluster + '/')
    print outputcat
    
    
    spec = True 
    
    if not spec:
        outputcat = '%(path)s/PHOTOMETRY/%(cluster)s.1.all.bpz.tab' % params 
    
    print outputcat
    bpz_cat = pyfits.open(outputcat)[1].data
    
   
    print outputcat
 
    gals = [] 
    
    for i in range(len(bpz_cat)): #[75227,45311,53658, 52685, 64726]:
        print i
        line = bpz_cat[i]
        print line
        text = ''
    
    #for x,y,side,index in [[4800,4900,200,1],[5500,5500,100,2],[4500,5500,300,2]]:
    
        text += '<tr>\n'
        SeqNr = int(line['SeqNr'])
        fileNumber = str(int(line['BPZ_NUMBER']))
        params['fileNumber'] = str(fileNumber)
    
        if spec: 
            base = '%(path)s/PHOTOMETRY/%(cluster)s.1.spec' % params
            probs =  '%(path)s/PHOTOMETRY/all.spec.cat.bpz1.probs' % params
    
            #base = '%(path)s/PHOTOMETRY/specsave.cat' % params
            #probs =  '%(path)s/PHOTOMETRY/all.spec.cat.bpz1.probs' % params
    
        else:
            base = '%(path)s/PHOTOMETRY/all_bpz1_%(fileNumber)s' % params
            probs =  '%(path)s/PHOTOMETRY/all_bpz1_%(fileNumber)s.probs' % params
        print probs
        probs_f = open(probs,'r').readlines()
    
        resid = line['BPZ_Z_B'] - line['BPZ_Z_S']
    
        ODDS = line['BPZ_ODDS']
    
        if True: #0.38 < line['BPZ_Z_B'] < 0.42: #abs(resid) > 0.15: # and ODDS > 0.95:        
    
            mask = p_cat.field('SeqNr') == SeqNr                                                                                                   
            temp = p_cat[mask]
            x = int(temp.field('Xpos')[0])
            y = 10000 - int(temp.field('Ypos')[0])
    
            x_fits = int(temp.field('Xpos')[0])
            y_fits = int(temp.field('Ypos')[0])
    
            import pyraf
            from pyraf import iraf
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    
            
    
            
    
    
    
           
            if line['BPZ_Z_S'] != 0: 
                resid = line['BPZ_Z_B'] - line['BPZ_Z_S']
                if resid > 0: 
                    color='green'
                    resid_str = ' <font color=' + color + '>+' + str(resid) + '</font> '
                else: 
                    color='red'        
                    resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '
            else:
                resid = 'no spec z' 
                color = 'black'
                resid_str = ' <font color=' + color + '>' + str(resid) + '</font> '
    
            
            t = ['BPZ_Z_B','BPZ_ODDS','BPZ_CHI-SQUARED']
            text += '<td colspan=10>' + str(SeqNr) + ' z=' + str(line['BPZ_Z_B']) + resid_str  + ' ODDS=' + str(line['BPZ_ODDS']) + ' TYPE=' + str(line['BPZ_T_B']) + ' CHISQ=' + str(line['BPZ_CHI-SQUARED']) + ' x=' + str(x) + ' y=' + str(y) + '</td></tr><tr>\n'
            
            print x,y
                                                                                                                                                   
            index = SeqNr
                                                                                                                                                   
            outfile = os.environ['sne'] + '/photoz/' + cluster + '/' + str(index) + '.png' 
            plot_bpz_probs(index, probs_f, outfile)
                                                                                                                                                   
            #file = 'Id%09.f.spec' % index
            #outfile = os.environ['sne'] + '/photoz/' + str(index) + '.png' 
            #print outfile
            #plot(file,outfile)
            
            text += '<td align=left><img height=400px src=' + str(index)  + '.png></img>\n'
            text += '<img height=400px src=' + str(index)  + 'spec.png></img>\n'
            images = []
    
            file = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  str(SeqNr) + 'spec.png' #print 'SAVING', outdir + outimg
            command = 'python ' + os.environ['BPZPATH'] + '/plots/sedplot.py ' + base + ' ' + str(SeqNr) + ' ' + file
            print command
    
            import sedplot
    
            sys.argv = ['',base,str(SeqNr),file]
            filt_info = sedplot.run()
            print filt_info 
    
            
            #print command
            #os.system(command)

            try:
                p = im.crop([x-side,y-side,x+side,y+side])
                image = os.environ['sne'] + '/photoz/' + cluster + '/' + str(index) + '.jpg'  
                os.system('rm ' + image)
                p.save(image,'JPEG')
            except: print 'fail'
            text += '<img src=' + str(index)  + '.jpg></img></td><td colspan=20></td>\n'
            text += '</tr>\n'
            keys = ['name','wavelength','observed','flux','fluxerror','expectedflux','chioffset']
            text += '<tr><td colspan=10><table><tr>' + reduce(lambda x,y: x + y,['<td>'+n+'</td>' for n in keys]) + "</tr>"
            for f in filt_info:
                text += '<tr>' + reduce(lambda x,y: x + y,['<td>'+str(f[n])+'</td>' for n in keys]) + "</tr>"
            text += "</table></td></tr>"
    
            side = 100 #x = temp.field('Xpos')[0]
            bounds = '[' + str(int(x_fits-side)) + ':' + str(int(x_fits+side)) + ',' + str(int(y_fits-side)) + ':' + str(int(y_fits+side)) + ']'
            text += '<td colspan=20><table>\n'
            textim = ''
            textlabel = ''
    
            import string
    
            filters_b = []
    
            name_t = None
            for f in filt_info:
                print f['name']
                if string.find(f['name'],'MEGAPRIME') != -1:
                    n = f['name'][-1]
                if string.find(f['name'],'SUBARU') != -1:
                    import re
                    res = re.split('-W',f['name'])
                    print res, f['name']
                    n = 'W' + res[1]
                if n != name_t:
                    filters_b.append(n)
                    name_t = n
    
    
            for filter in filters_b[1:]:
                fitsfile = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  str(SeqNr) + 'cutout' + filter + '.fits' #print 'SAVING', outdir + outimg  
                jpg = '/nfs/slac/g/ki/ki04/pkelly/photoz/' + cluster + '/' +  str(SeqNr) + 'cutout' + filter + '.jpg' #print 'SAVING', outdir + outimg
                os.system('rm ' + fitsfile)
                os.system('rm ' + jpg)
                bigfile = '/a/wain023/g.ki.ki05/anja/SUBARU/' + cluster + '/' + filter + '/SCIENCE/coadd_' + cluster + '_all/coadd.fits'
                iraf.imcopy(bigfile + bounds,fitsfile)
                import commands
                seeing = commands.getoutput('gethead ' + bigfile + ' SEEING')
                print 'seeing', seeing 


                import os
                #os.system("ds9 " + fitsfile + " -view info no -view panner no -view magnifier no -view buttons no -view colorbar yes -view horzgraph no -view wcs no -view detector no -view amplifier no -view physical no -zoom to fit -minmax -histequ  -invert -zoom to fit -saveas jpeg " + jpg ) # -quit >& /dev/null &")        
                #os.system("xpaset -p ds9 " + fitsfile + "  -zoom to fit -view colorbar no -minmax -histequ  -invert -zoom to fit -saveas jpeg " + jpg  + " ") # -quit >& /dev/null &")        
    
                com = ['file ' + fitsfile, 'zoom to fit', 'view colorbar no', 'minmax', 'scale histequ' , 'cmap invert', 'saveimage jpeg ' + jpg] # -quit >& /dev/null &")        
                for c in com:
                    z = 'xpaset -p ds9 ' + c
                    print z
                    os.system(z)
                print jpg
                text += '<td><img height=200px src=' + str(SeqNr)  + 'cutout' + filter + '.jpg></img></td>\n'
                textlabel += '<td>' + filter + ' seeing ' + seeing + '</td>\n'
                                                                                                                                                                                                                                                                                                                                         
            text += '<tr>' + textim +  '</tr><tr>' +  textlabel + '</tr></table></td></tr><tr>'
    
    
    
    
    
    
    
    
    
    
    
            #os.system('stiff ' + image_seg + ' -OUTFILE_NAME ' + image_seg.replace('fits','tif'))
            gals.append([line['BPZ_T_B'],text])
            page = open(os.environ['sne'] + '/photoz/' + cluster + '/index.html','w')
            t = '<head><link href="http://www.slac.stanford.edu/~pkelly/photoz/table.css" rel="stylesheet" type="text/css"></head>' 
            t += '<table align=left><tr><td colspan=5 class="dark"><h1>' + cluster + '</h1></td></tr><tr><td colspan=5><a href=stars.html>Stellar Color-Color Plots</a><td></tr>\n'
            t += '<tr><td colspan=10 align=left><img height=400px src=RedshiftErrors.png></img>\n'
            t += '<img height=400px src=RedshiftScatter04.png></img>\n'
            t += '<img height=400px src=RedshiftScatter01.png></img></td></tr>\n'
            page.write(t)
            gals.sort()
            for gal in gals:
                page.write(gal[1])
            page.write('<table>\n')
            page.close()
    
            if len(gals) > 100:
                break
    
    
    
    ''' make SED plots '''

if __name__ == '__main__':    
    import sys
    cluster = sys.argv[1] #'MACS0717+37'
    run(cluster)
