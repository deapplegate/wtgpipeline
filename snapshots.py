
from config import path, cluster, filters, magnitude_err, path, appendix
from utilities import *
import re 

#run("ldacfilter -i /tmp/final.cat -t STDTAB -c '((CLASS_STAR_W-J-V < 0.9) AND  (Z_BEST < 0));' -o /tmp/final.bad")

run("ldacfilter -i /tmp/final.cat -t STDTAB -c '((CLASS_STAR_W-J-V < 0.9) AND  (Z_BEST > 1.98));' -o /tmp/final.bad")


keys = ['Z_BEST','Z_BEST68_LOW','Z_BEST68_HIGH','ALPHA_J2000','DELTA_J2000','Xpos','Ypos','SeqNr']
keys += ['MAG_ABS_' + x for x in filters]
keys += ['MAG_OBS_' + x for x in filters]
keys += ['ERR_MAG_OBS_' + x for x in filters]
keys_str = reduce(lambda x,y: x + ' ' + y, keys)

run("ldactoasc -b -q -i /tmp/final.bad  -t STDTAB -k " + keys_str + "  > /tmp/histo")



outdir = "/%(path)s/PHOTOMETRY/snaps/" % {'path':path, 'cluster':cluster, 'appendix':appendix}
run("mkdir " + outdir)


zs_list = []
zs = open('/tmp/histo','r').readlines()
for z in zs[len(zs)/2:len(zs)/2+100]:
    res = re.split('\s+',z)
    print res, keys
    tmp = {}  
    for i in range(len(res[1:])):
        tmp[keys[i]] = res[i]
        print keys[i], res[i]





    for filter in filters:
        for type in ['','.weight','.flag']:
            image = "/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd%(type)s.fits" % {'type': type, 'path':path, 'filter':filter, 'cluster':cluster, 'appendix':appendix}        
            outimage = "/%(path)s/PHOTOMETRY/snaps/%(SeqNr)s%(filter)s%(type)s.fits" % {'type': type, 'path':path, 'filter':filter, 'cluster':cluster, 'appendix':appendix, 'SeqNr':tmp['SeqNr']}
            print outimage
            run("makesubimage " + str(int(float(tmp['Xpos'])) - 25) + " " + str(int(float(tmp['Ypos'])) - 25) + ' 50 50 < ' + image + ' > ' + outimage,[outimage])

    raw_input()


    

