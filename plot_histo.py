def run(command,to_delete=[]):
    import os
    for file in to_delete: 
        os.system('rm ' + file)
    print command
    #raw_input()
    os.system(command)

from config_bonn import cluster 

for error in [0.2,0.3,0.5,1]: #,1,1.5]:
    run("ldaccalc -i /tmp/" + cluster + "final.cat -t STDTAB -c '(Z_BEST68_HIGH - Z_BEST68_LOW);' -k FLOAT -n Z_BESTERR '' -o /tmp/" + cluster + "final.calc") 
    #'CLASS_STAR_W-J-V < 0.9)','Z_BEST > 0)',
    listcond = ['Z_BESTERR < ' + str(error) + ')'] #,'Xpos > 5500)','Xpos < 7000)','Ypos > 5500)','Ypos < 6500)'] 
    filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',listcond)

    #run("ldacfilter -i /tmp/final.calc -t STDTAB -c '(((CLASS_STAR_W-J-V < 0.9) AND  (Z_BEST > 0)) AND (Z_BESTERR<" + str(error) + "));' -o /tmp/final.filt")

    run("ldacfilter -i /tmp/" + cluster + "final.calc -t STDTAB -c '" + filt + ";' -o /tmp/" + cluster + "final.filt")
    
    #run("ldacfilter -i /tmp/final.cat -t STDTAB -c '(Z_BEST > 0);' -o /tmp/final.filt")
    run("ldactoasc -b -q -i /tmp/" + cluster + "final.filt  -t STDTAB -k Z_BEST > /tmp/histo")
    
    import pylab
    from numpy import *
    zs_list = []
    zs = open('/tmp/histo','r').readlines()
    for z in zs:
        if z[0] != '#':
            if 1==1: #0.3 < float(z[:-1]) < 0.6:
                zs_list.append(float(z[:-1]))
        
    _, _, varp = pylab.hist(zs_list,bins=arange(0.0,3,0.1))
    #varps.append(varp[0])
    
    #pylab.legend(varps,legendlist)
    	
    pylab.xlabel("PhotZ")
    pylab.ylabel("Number of Galaxies")
    pylab.savefig('RedshiftHistogram' + str(error) + '.ps')
    print len(zs_list)
    pylab.show()
