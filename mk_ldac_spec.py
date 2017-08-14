    
def run(cluster, detect):
    import os
    import MySQLdb
    import os, sys, anydbm, time
    #from config import datb, dataloc
    #from config_bonn import cluster
    #cluster = sys.argv[1]
    #detect = sys.argv[2]
    SUBARUDIR = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
    output = SUBARUDIR + cluster + '/PHOTOMETRY_' + detect + '_aper/'  + cluster + 'spec.cat'
    #print datb + cluster
    
    import lib 
    
    os.system("mkdir " + cluster)
    
    import string
    
    #if string.find(cluster,'MACS') != -1:
    #    name = cluster[4:8]
    #else: 
    #    name = cluster
    
    from glob import glob
    file = './spec/' + cluster + '.zcat'
    if glob(file):
        zcat_harald = open(file,'r').readlines()
    else: zcat_harald = []    
    
    
    file = './nedspec/' + cluster + '.zcat'
    if glob(file):
        zcat_ned = open(file,'r').readlines()
    else:
        zcat_ned = []
   
    if len(zcat_harald) or len(zcat_ned):
 
        if len(zcat_harald) > len(zcat_ned):                                                                                                                
            zcat = zcat_harald
        else:
            zcat = zcat_ned
        
        
        import re
        op = open('op','w')
        import os
        
        SeqNr = 0
        for line in zcat:
            import re
            ll = re.split('\s+',line)       
            if ll[0] == '': ll = ll[1:]     
        
            import string
            if string.find(ll[0],':') != 0:
                ll = [''] + ll
            temp = ['','temp']
            #print len(ll), 'length'        
            print ll
            if string.find(ll[1],':') != -1:
                for ele in ll[1:]:
                    temp.append(ele) 
                ll = temp
        
            #print ll
        
            print ll
            id = ll[1] #line[0:6]
        
            agalra     = ll[2] #line[8:20]
            agaldec    = ll[3] #line[22:34]
            z = ll[4] #line[37:43]                                                                                                                      
            if string.find(agalra,':') != -1:
                #print id, agalra, agaldec, z
                rlist = ['','',''] 
                dlist = ['','',''] 
                rlist[0] = agalra[0:2] 
                rlist[1] = agalra[3:5] 
                rlist[2] = agalra[6:] 
                dsign = agaldec[0]
                dmul = float(dsign + '1')
                dlist[0] = agaldec[1:3] 
                dlist[1] = agaldec[4:6] 
                dlist[2] = agaldec[7:] 
                import string
                #print rlist, dlist, dsign
                radeg = (360/24.0)*string.atof(rlist[0]) + (360.0/(24.0*60))*string.atof(rlist[1]) + (360.0/(24.0*60.0*60.0))*string.atof(rlist[2])
                spectrara = radeg
                decdeg = dmul * (string.atof(dlist[0]) + (1/60.0)*string.atof(dlist[1]) + string.atof(dlist[2])*(1/(60.0*60.0))                           )
            else:
                radeg = float(agalra)
                decdeg = float(agaldec)
        
        
        
            spectradec = decdeg
            spectraz = z
            label = id
            #decdiff =decdeg - 24.0695846901 
            #radiff = radeg - 215.925761617995
            #print decdiff, radiff
            #op.write(str(radiff) + " " + str(decdiff)+ "\n")
            p = re.compile('\S')
            m = p.findall(label)
            if len(m) == 0: label = 'nolab'
            SeqNr += 1
            if string.find(spectraz,'?') == -1 and spectraz != '' and spectraz != '-1' and 0 < float(spectraz) < 3:
                print radeg, decdeg, spectraz
                op.write(str(SeqNr) + ' ' + str(radeg) + " " + str(decdeg)+ " " + str(spectraz) + "\n")
        
        op.close()
        os.system('asctoldac -i op -o ' + output + ' -c ./photconf/zspec.conf')

        return True
    else: return False
