import sys, re

from ppgplot   import *

from glob import glob
if 1==1: #len(glob('box' + filter)) == 0:
    lines = open('Id000000001.spec','r').readlines()
    x = []
    y = []
    z = []
    err = []
    
    file = "brightarc.ps"
    pgbeg(file+"/cps",1, 1)
    #pgbeg("/XWINDOW",1,1)
                             
    pgiden()
    from Numeric import *
    
    for line in lines[8:]:
        spt = re.split('\s+',line)
        print spt
        lda = float(spt[7])
        mag = float(spt[8])
        #print color
        #print aptmag, catmag, radius, star_class, sdss_error, color
           #print spt
        if 50 > mag > 0:
            x.append(lda) 
            y.append(mag)
    
    #print 'x',x
    #print 'y',y
    import copy 
    plotx = copy.copy(x)
    ploty = copy.copy(y)
    x.sort()    
    y.sort()
    #print plotx
    #print x[0], x[-1], y[0], y[-1]
    pgswin(x[0],x[-1],y[0]-1,y[-1]+2)
    plotx = array(plotx)
    ploty = array(ploty)
    #pylab.scatter(z,x)
    pglab('Lambda','Mag','')
    #print plotx, ploty
    pgsci(3)
    pgpt(plotx,ploty,5)

    x = []
    y = []
    z = []
    err = []
    
    for line in lines[1:6]:
        spt = re.split('\s+',line)
        print spt
        lda = float(spt[3])
        mag = float(spt[1])
        magerr = float(spt[2])
        #print color
        #print aptmag, catmag, radius, star_class, sdss_error, color
           #print spt
        x.append(lda)
        y.append(mag)
        err.append(magerr)
    
    #print 'x',x
    #print 'y',y
    import copy 
    plotx = copy.copy(x)
    ploty = copy.copy(y)
    x.sort()    
    y.sort()
    #print plotx
    #print x[0], x[-1], y[0], y[-1]
    #pgswin(x[0],x[-1],y[0],y[-1])
    plotx = array(plotx)
    ploty = array(ploty)
    ploterr = array(err)
    #pylab.scatter(z,x)
    pgsci(2)
    pgpt(plotx,ploty,3)
    print plotx, ploty, err
    pgerrb(6,plotx,ploty,ploterr,8)
   
    pgsci(1)
    pgbox()
pgend()
