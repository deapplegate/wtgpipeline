def mk_saturation_all(files,titles,filter,all_objects=None):                                                                                               
    import sys, re
    from ppgplot   import *
    from glob import glob

    pgbeg("/XTERM",3,2)

    pgiden()
    positions = [[1,1],[1,2],[2,1],[2,2],[3,1],[3,2]]
    for i in range(len(files)):
        file = files[i]
        position = positions[i]
        title = titles[i]

        pgpanl(position[0],position[1]) 

        lines = open(file,'r').readlines()
        x = []
        y = []
        z = []
        err = []
        
        #file = outfile+".ps"
        #pgbeg(file+"/cps",1, 1)
                                 
        from Numeric import *
        
        for line in lines:
            spt = re.split('\s+',line)
            if spt[0] != '':
                spt = [''] + spt
            aptmag = float(spt[1])
            catmag = float(spt[2])
            radius = float(spt[3])
            star_class = float(spt[4])
            sdss_error = float(spt[5])
            color = float(spt[6])
            #print color
            #print aptmag, catmag, radius, star_class, sdss_error, color
            if -10 <catmag-aptmag < 10: #aptmag != 0 and catmag < 40 and catmag > 10: # and color > 0.5: # and radius < 3.3 and aptmag>-1.5:
                
                #print spt
                x.append(aptmag)
        
                y.append(catmag - aptmag)
        
                z.append(radius)
        
                err.append(sdss_error)
        
        #print 'x',x
        #print 'y',y
        import copy 
        plotx = copy.copy(x)
        ploty = copy.copy(y)
        x.sort()    
        y.sort()
        #print plotx
        #print x[0], x[-1], y[0], y[-1]
        if i==0:
            lowx=x[2]
            highx=x[-2]
            lowy=y[2]
            highy=y[-2]

        pgswin(lowx,highx,lowy,highy)
        plotx = array(plotx)
        ploty = array(ploty)
        #pylab.scatter(z,x)
        pglab('Mag','Mag - Mag(Inst)',title)
        #print plotx, ploty
        pgpt(plotx,ploty,3)
        
        pgbox()
    pgend()
        
       
def mk_saturation(file,filter,all_objects=None): 
    import sys, re
    
    from ppgplot   import *
    
    from glob import glob
    if 1==1: #len(glob('box' + filter)) == 0:
        lines = open(file,'r').readlines()
        x = []
        y = []
        z = []
        err = []
        
        #file = outfile+".ps"
        #pgbeg(file+"/cps",1, 1)
        pgbeg("/XTERM",1,1)
                                 
        pgiden()
        from Numeric import *
        
        for line in lines:
            spt = re.split('\s+',line)
            if spt[0] != '':
                spt = [''] + spt
            aptmag = float(spt[1])
            catmag = float(spt[2])
            radius = float(spt[3])
            #print color
            #print aptmag, catmag, radius, star_class, sdss_error, color
            if -10 <catmag-aptmag < 10: #aptmag != 0 and catmag < 40 and catmag > 10: # and color > 0.5: # and radius < 3.3 and aptmag>-1.5:
                
                #print spt
                x.append(radius)
        
                y.append(catmag - aptmag)
        
                z.append(radius)
        
        
        #print 'x',x
        #print 'y',y
        import copy 
        plotx = copy.copy(x)
        ploty = copy.copy(y)
        x.sort()    
        y.sort()
        #print plotx
        #print x[0], x[-1], y[0], y[-1]
        pgswin(x[2],x[-2],y[2],y[-2])
        plotx = array(plotx)
        ploty = array(ploty)
        #pylab.scatter(z,x)
        pglab('Mag','Mag - Mag(Inst)','')
        #print plotx, ploty
        pgpt(plotx,ploty,3)
        
        pgbox()
        pgend()
        
       
	yn = raw_input('Adjust box?') 
       	
	if len(yn) > 0: 
		if yn[0] == 'y' or yn[0] == 'Y': 
       			#pylab.errorbar(x,y,err,fmt='o',markersize=0.01)                                                       
                        #pylab.show()   
                        lower_mag = -99
                        upper_mag = 99
                        lower_magdiff = -99
                        upper_magdiff = 99
                        print '\n\n\n'
                        print '\n'
                        print "Lower Mag? (-99)"
                        b = raw_input()
                        if b is not '':
                            lower_mag = b
                        print "Upper Mag? (-99)"
                        b = raw_input()
                        if b is not '':
                            upper_mag = b
                        
                        print "Lower Mag Diff? (-99)"
                        b = raw_input()
                        if b is not '':
                            lower_magdiff = b
                        
                        print "Upper Mag Diff? (-99)"
                        b = raw_input()
                        if b is not '':
                            upper_magdiff = b
                        
                        out = open('box' + filter,'w')
                        out.write(str(lower_mag) + ' ' + str(upper_mag) + ' ' + str(lower_magdiff) + ' ' + str(upper_magdiff))
                        out.close()
   
if __name__ == '__main__': 

    import sys

    file = sys.argv[1]
    filter = sys.argv[2]

    mk_saturation(file,filter)
    
