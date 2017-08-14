import re, sys


# usage eg: python choosepoly.py $SUBARUDIR/MACS0025-12//LENSING_W-J-V_W-J-V_aper/good/star_chi2_even.txt

thefilename = sys.argv[1]

theint = -1
isset_flag=False


thefile = open(thefilename)
linelist=thefile.readlines()


for line in linelist:
    entries=re.split('\s+',line)
    #print entries
    
    if len(entries) > 10:
        #print 'thisline',entries[1], entries[-2]
        if entries[-2].find('notok')>=0:
            #   print 'in notok'
            isset_flag=False
            
            
        elif entries[-2].find('ok')>=0:
            # print 'in ok'
            if isset_flag:  #isset_flag=True
                continue
            else: # isset == false
                theint = entries[1][4:]
                isset_flag=True
            #
    #else:
        #print 'skipping shortline'
    #print 'theint=',theint, 'isset_flag=',isset_flag


outfile = open(thefilename[:-3]+'poly','w')
outfile.write(str(theint))
outfile.close()
print theint
