
import math, re, sys
import pylab  # matplotlib

def scale(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val+48.60))
    

def scaleerr(val):
    #    return 10**(-0.4*(val+48.60))
    return (-0.4*(val))
    



def doit(file):
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
    pylab.plot(speclambda1,specmag1,'g-')
    pylab.errorbar(lambdamean,mag,xerr=lambdawidth,yerr=magerr,fmt='ro')
    

    print "showing"
#    pylab.savefig(file+'.png')
    pylab.show()
    

doit(sys.argv[1])
