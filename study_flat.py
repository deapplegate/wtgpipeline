import numpy, sys, re, astropy.io.fits as pyfits,  glob,pylab, math
import subarucorr
#import fitstuff as fs
from ROOT import TCanvas, TF1, TGraph, TAxis, gStyle, TH2F,gROOT, gPad, TLine, TLatex

gROOT.SetStyle("Plain");
gStyle.SetPalette(1)
##FILE                	EXPTIME	
##SUPA0002627_2OC.fits	15.00  	
##SUPA0002628_2OC.fits	15.00  	
##SUPA0002629_2OC.fits	15.00  	
##SUPA0002631_2OC.fits	10.00  	
##SUPA0002632_2OC.fits	15.00  	
##SUPA0002633_2OC.fits	30.00  	
##SUPA0002634_2OC.fits	45.00  	
##SUPA0002635_2OC.fits	60.00  	


def polyn(x,pars):
    y=x[0]
    total=0
    for i in range(len(pars)):
        total+=pars[i]*math.pow(y,i+1)
    return total
def polyn_all(x,pars):
    y=x[0]
    total=0
    for i in range(len(pars)):
        total+=pars[i]*math.pow(y,i+1)
    return total






l=sys.argv[1]

l= int(l)

chipcodes=['','w93c2','w9c2','si005s','si001s','w4c5','w67c1','w6c1','si006s','si002s','w7c3']

if l != -1:
    start = l
    stop = l+1
else:
    start = 2
    stop = 11
b_list=[0,0,[],[],[],[],[],[],[],[],[]]
m_list=[0,0,[],[],[],[],[],[],[],[],[]]



for ichip in range(start,stop):
    
    fitrange=[0,0,[7000,10000],[4500,6000],[4500,6000],[3000,8000],[4000,9000],\
              [7000,10000],[6000,7000],[4000,6300],[3500,8500]]
    
    fitrange=[0,0,[1000,10000],[1000,10000],[1000,10000],[1000,10000],[1000,10000],\
              [1000,10000],[1000,10000],[1000,10000],[1000,10000]]
      
    ic = ichip
    ichip = str(ichip)


    # 31 is the 10 sec

    flatlist=[#'/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002631_'+ichip+'OC.fits']
              '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002628_'+ichip+'OC.fits',
              '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002629_'+ichip+'OC.fits' ]


    complist=[
        #'/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002627_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002628_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002629_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002631_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/SUPA0002632_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/BADMODE/SUPA0002633_'+ichip+'OC.fits',
        '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/BADMODE/SUPA0002634_'+ichip+'OC.fits'#,
        #       '/nfs/slac/g/ki/ki05/anja/SUBARU//2000-11-22_W-J-V/DOMEFLAT/BADMODE/SUPA0002635_'+ichip+'OC.fits'
        ]
    

  

    hdulist = pyfits.open(flatlist[0])
    scidata = hdulist[0].data[:,:]
    
    flatarray = numpy.ndarray((len(scidata[:,0]),len(scidata[0,:]),len(flatlist)))
    
    hdulist.close()
    
    count=0

    for f in flatlist :
        hdulist = pyfits.open(f)
        thisexptime=hdulist[0].header['EXPTIME']
        print ' for flat: expt ime is', thisexptime, f
        
        scidata = hdulist[0].data[:,:]
        flatarray[:,:,count] = scidata/thisexptime
        count+=1
    # 
    print 'Making flat'
    flat = numpy.average(flatarray,2)

    print len(flat[:,0]),  len(flat[0,:])  

    fullarray=numpy.ndarray(0)
    fullprojarray=numpy.ndarray(0)
    fullarraytime = numpy.ndarray(0)
    count=0
    x=[1,2,3]
    y=[]
    rms=[]

    grlist=[]

    #c = TCanvas('c','c',800,400)
    
    shorttimearray=[]
    shortratearray=[]
    
    for f in complist :
        count+=1
        hdulist = pyfits.open(f)
        thisexptime=hdulist[0].header['EXPTIME']
        print ' for comp: exp time is', thisexptime, f
        #fullarray=numpy.ndarray(0)
        #fullprojarray=numpy.ndarray(0)
       
        scidata = hdulist[0].data[:,:]
        
        projecteddata = flat * thisexptime

        #hist=TH2F('hist','hist',len(scidata[:,1]),0,len(scidata[:,1]),\
         #         len(scidata[1,:]),0, len(scidata[1,:]))
        
        #    thisarray=scidata[0,:]
    
        for i in range(0,len(scidata[:,0]),100):
            #print i
            # for i in range(1000, 1050,1):
            thisarray=scidata[i,:]
            thisprojarray=projecteddata[i,:]
            # thisarray=scidata[i,1000:1050]
            # thisprojarray=projecteddata[i,1000:1050]
            # fullarray=numpy.ndarray(fullarray,thisarray)

            #thisfilter=numpy.abs((thisarray-thisprojarray) /thisprojarray )<0.2
            # thisfilter=numpy.logical_and(thisfilter,thisarray<6200)
            # thisfilter=numpy.logical_and(thisfilter,thisprojarray<6200)
            # thisfilter2=numpy.logical_and(thisarray>7000,thisprojarray>7000 )
            # thisfilter=numpy.logical_or(thisfilter,thisfilter2)
             
            # thisfilter=numpy.logical_and(thisfilter,thisprojarray>8000)
            #for j in range(len(scidata[0,:])):
            #    hist.Fill(i,j,(scidata[i,j]-projecteddata[i,j])/projecteddata[i,j])
                
            #thisarray = thisarray*thisfilter
            #thisprojarray = thisprojarray*thisfilter
            
            fullarray=numpy.hstack((fullarray,thisarray))
            fullprojarray = numpy.hstack((fullprojarray,thisprojarray))
            fullarraytime = numpy.hstack((fullarraytime,numpy.ones(len(thisprojarray))*thisexptime))
            shorttimearray.append(thisexptime)
            shortratearray.append(numpy.average(thisprojarray)/thisexptime)
            #pylab.errorbar( fullprojarray,fullarray-fullprojarray,fmt='.')
            #pylab.errorbar( fullprojarray,fullarray,fmt='.')
            
            ##grlist.append(TGraph(len(fullarray),fullprojarray,fullarray-fullprojarray ))
##            grlist[count-1].SetName('gr'+str(count))
##            grlist[count-1].SetMarkerColor(count)
##            grlist[count-1].SetMaximum(2000)
##            grlist[count-1].SetMinimum(-2000)
##            grlist[count-1].GetXaxis().SetLimits(0,40000)
            #if count==1:
            #    grlist[0].Draw('AP')
            #else :
            #    grlist[count-1].Draw('APsame')

    gr= TGraph(len(fullarray),fullarray,(fullarray-fullprojarray)/ fullarray)
    #gr= TGraph(len(fullarray),fullprojarray,fullarray)
    #gr= TGraph(len(fullarray),fullarray,fullprojarray)
    


    fcn = TF1('fcn','pol7(0)',10,28000)
    fcn.FixParameter(0,0.)
    fcn.SetLineColor(4)

    gr.Fit(fcn,'r')
    parset=[]
    for i in range(1,8):
        parset.append(fcn.GetParameter(i))
        
    print parset
    print chipcodes[int(ichip)]
    
    NORMPOINT = 10000
    scale = NORMPOINT/subarucorr.mypoly_char(chipcodes[int(ichip)], NORMPOINT)
    corrarray = subarucorr.mypoly_char(chipcodes[int(ichip)],fullarray)*scale
    gr2= TGraph(len(fullarray),fullarray,(corrarray-fullprojarray)/ fullarray)
    
    # NORMPOINT2 = 10000
    # scale2 = NORMPOINT2/subarucorr.mypoly_new_char(chipcodes[int(ichip)], NORMPOINT2)

    corrarray2 =   fullarray*(1. - subarucorr.mypoly_mult(parset,fullarray))
    
    plotcorrarray2=(corrarray2-fullprojarray)/ fullarray
    gr3= TGraph(len(fullarray),fullarray,plotcorrarray2)


    print subarucorr.mypoly_mult(parset,fullarray)

    #flatarray=numpy.array(range(0,20000,10),dtype=float)
    #corrflatarray =   subarucorr.mypoly_new_char(chipcodes[int(ichip)],flatarray)*scale2
    #gr4= TGraph(len(fullarray),flatarray,(corrflatarray-flatarray)/ flatarray)
    

    #gr2= TGraph(len(fullarray),fullprojarray,corrarray)
    #gr2= TGraph(len(fullarray),corrarray,fullprojarray)
    


#    mycorr = polyn(,parset)
#    gr3= TGraph(len(fullarray),fullprojarray,(corrarray-fullprojarray)/ fullprojarray)
    
 
    c = TCanvas('c','c',800,400)

    #c.Divide(2)
##    grlist[0].Draw('AP')
##    grlist[1].Draw('APsame')
##    grlist[2].Draw('APsame')
##    grlist[3].Draw('APsame')
##    grlist[4].Draw('APsame')
##    grlist[5].Draw('APsame')
    #c.cd(1)
    gr.SetMaximum(0.15)
    gr.SetMinimum(-0.15)
    pad = c.GetPad(0)
    pad.SetGridx(1)
    pad.SetGridy(1)
    gStyle.SetOptTitle(0)
    
    #  gr= TGraph(len(fullarray),fullarray,(fullarray-fullprojarray)/ fullarray)

    gr.GetXaxis().SetTitle('Pixel Count')
    gr.GetYaxis().SetTitle('1 - #frac{Expected Count}{Count} ')
    gr.Draw('AP')
    

    fcn.Draw('same')
    gr2.SetMarkerColor(2)
    gr3.SetMarkerColor(4)
    #gr4.SetMarkerColor(3)
    
    # gr2.Draw('Psame')
    #gr3.Draw('Psame')
    #gr4.Draw('Psame')
    #c.cd(2)
    #c2 = TCanvas('c2','c2',800,400)
    #hist.Draw('colz')


    
    c2 = TCanvas('c2','c2',800,400)
    #lingr= TGraph(len(fullarray),fullarray,(fullprojarray)) #  -fullarray ))
    print len(shorttimearray), len(shortratearray)

    lingr=TGraph(len(fullarray), fullarray , fullarray/ fullprojarray)
    fit1=subarucorr.mypoly_char(chipcodes[int(ichip)],numpy.arange(0,27000,10))*scale
    print fit1
    
    xvals=numpy.arange(0,27000,1000)
    yvals=[]
    for v in xvals:
        yvals.append(fcn.Eval(v)+1)
        print v,fcn.Eval(v)+1
    print xvals,yvals
    lingr2=TGraph(len(xvals), xvals, numpy.array(yvals))
    
    
    #lingr= TGraph(len(shorttimearray), numpy.array(shorttimearray), numpy.array(shortratearray))
    lingr.SetMaximum(1.15)
    lingr.SetMinimum(0.85)
    lingr.GetXaxis().SetTitle('Pixel Count')
    lingr.GetYaxis().SetTitle('Count / Expected Count')
    pad = c2.GetPad(0)
    pad.SetGridx(1)
    pad.SetGridy(1)
    gStyle.SetOptTitle(0)
    #lingr.GetXaxis().SetRange(0,30000)
    #lingr.GetYaxis().SetRange(0,30000)    
    lingr.Draw('AP')
    lingr2.SetMarkerStyle(20)
    lingr2.SetMarkerColor(2)
    
    lingr2.Draw('Psame')
    
    #lingr.Fit(fcn,'r')
    ten=TLatex(3000,0.01,'10 s')
    fifteen=TLatex(8000,0.05,'15 s')
    thirty=TLatex(18000,0.03,'30 s')
    forty5=TLatex(25000,0.01,'45 s')

    ten.SetTextColor(4)
    fifteen.SetTextColor(4)
    thirty.SetTextColor(4)
    forty5.SetTextColor(4)
    
    c.cd()
    ten.Draw('same')
    fifteen.Draw('same')
    thirty.Draw('same')
    forty5.Draw('same')
    
    oneline=TLine(0,0,30000,30000)
    oneline.SetLineWidth(2)
    oneline.SetLineColor(2)
    #oneline.Draw("same")
     
    c.Print('c.png')
    c.Print('nonlinear.eps')
    c2.Print('c2.png')
    print 'pausing...'

    gStyle.SetOptStat(0)
    
    c3=TCanvas('c3','c3',800,400)
    hist2d = TH2F('hist2d','hist2d',200,0,30000,200,-0.15,0.15)
    for i in range(len(fullarray)):
        hist2d.Fill(fullarray[i],(fullarray[i]-fullprojarray[i])/ fullarray[i])

    hist2d.GetXaxis().SetTitle('Pixel Count')
    hist2d.GetYaxis().SetTitle('1 - #frac{Expected Count}{Count} ')

    hist2d.SetMaximum(2500)
    hist2d.Draw('colz')
    fcn.SetLineColor(1)
    
    ten.SetTextColor(1)
    fifteen.SetTextColor(1)
    thirty.SetTextColor(1)
    forty5.SetTextColor(1)
    
    ten.Draw('same')
    fifteen.Draw('same')
    thirty.Draw('same')
    forty5.Draw('same')
    
    fcn.Draw('same')
    
    c3.Print('c3.png')
    raw_input()
    
        #f = TF1('f','[0]+[1]*x',fitrange[ic][0],fitrange[ic][1])
        #f.SetParameters(0,1)
        
        #f.SetParLimits(1,1.0,1.0)
        
        #c = TCanvas()
        #gr=TGraph(len(fullarray),fullprojarray,fullarray) 
        #f.SetRange(1000,20000)
        #gr.Fit(f,'rLL')
        
        #gr.SetMaximum(1200)
        #gr.SetMinimum(-1200)
        
        #gr.Draw('AP')
        #f.SetLineColor(4)
        # f.Draw('same')

        # print 'appending '+str(f.GetParameter(0)) +' to ic='+str(ic) 
        #b_list[ic].append(f.GetParameter(0))
        #m_list[ic].append(f.GetParameter(1))
        # print b_list

        #raw_input()

        
        #def f(x): return m()*x + b()
        #fs.fit(f, [m, b],fullarray-fullprojarray, fullprojarray)

        
        # pylab.plot(fs.fit(f, [m, b],fullarray-fullprojarray, fullprojarray))
        # pylab.hist( (fullprojarray,fullarray-fullprojarray))
        # print m()
        # print b()
        #
        # pylab.axis([0,30000,0 ,30000])
    #pylab.show()
    #pylab.clf()
    # print y
    #    print rms/y

    


    




sys.exit(0)

x=[2.,3.,4.,5.,6.,7.,8.,9.,10.]
#print x
#print b_list

b_y=[[],[],[],[],[],[]]
m_y=[[],[],[],[],[],[]]

for j in range(3):
    for i in range(2,11):
        b_y[j].append(float(b_list[i][j]))
        m_y[j].append(float(m_list[i][j]))

print x
print b_y[0]
#print len(b_list[1])

pylab.errorbar(x,b_y[0],fmt='.')
pylab.errorbar(x,b_y[1],fmt='.')
pylab.errorbar(x,b_y[2],fmt='.')
pylab.axis([1,11,-1000,1000])
pylab.show()
pylab.clf()
pylab.errorbar(x,m_y[0],fmt='.')
pylab.errorbar(x,m_y[1],fmt='.')
pylab.errorbar(x,m_y[2],fmt='.')
pylab.axis([1,11,-0.2,0.2])
pylab.show()


##z=b_y[0]
##b_plot0=TGraph(9,x,z)
##b_plot1=TGraph(9,x,b_y[1])
##b_plot2=TGraph(9,x,b_y[2])
##m_plot0=TGraph(9,x,m_y[0])
##m_plot1=TGraph(9,x,m_y[1])
##m_plot2=TGraph(9,x,m_y[2])
##can = TCanvas('can','can',900,450)
##can.Divide(2)
##can.cd(1)
##b_plot0.Draw('AP')
##b_plot1.Draw('same')
##b_plot2.Draw('same')
##can.cd(2)
##m_plot0.Draw('AP')
##m_plot1.Draw('same')
##m_plot2.Draw('same')
    
raw_input()
        
    #pylab.errorbar(x, y  ,fmt='.')    

##    #pylab.clf()
##    #pylab.plot([0,40000],[0,40000])
##    #pylab.errorbar(fullprojarray,fullarray ,fmt='b.')
   
##    NORMPOINT = 10000
##    #scale = NORMPOINT/subarucorr.mypoly_char(chipcodes[int(ichip)], NORMPOINT)
    
##    # pylab.errorbar(fullprojarray,subarucorr.mypoly_char(chipcodes[int(ichip)],fullarray)*scale ,fmt='g.')
##    #pylab.axis([0,40000,0,40000])
##    pylab.axis([0,40000,0.9,1.1])
##    print l
##    pylab.xlabel('Expected pix count:'+chipcodes[int(ichip)])
##    pylab.ylabel('Measured pix count')
    
    
##    #pylab.show()
    
    # pylab.savefig("Chip"+str(ichip)+"_Config9_nonlin.png")
