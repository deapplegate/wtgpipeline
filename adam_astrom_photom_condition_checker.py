#! /usr/bin/env python
#astref=starcat astref_wt=1  stability_type=exp
#astref=starcat astref_wt=1  stability_type=instrum
#astref=starcat astref_wt=10 stability_type=exp
#astref=starcat astref_wt=10 stability_type=instrum
#astref=refcat  astref_wt=1  stability_type=exp
#astref=refcat  astref_wt=1  stability_type=instrum
#astref=refcat  astref_wt=10 stability_type=exp
#astref=refcat  astref_wt=10 stability_type=instrum


tags=['refcat_wt10','exp_wt10','instrum_wt1','instrum_wt10']
import itertools
for tag1,tag2 in itertools.combinations(tags,2):
    print "ic '%1 %2 -' "+"coadd_%s.fits coadd_%s.fits > coadd_%s-%s.fits" % (tag1,tag2,tag1,tag2)

astref=['starcat','refcat']
astref_wt=[1,10]
stability_type=['exp','instrum']
for cond1 in astref:
    for cond2 in astref_wt:
        for cond3 in stability_type:
            print "astref=%s astref_wt=%s stability_type=%s" % (cond1,cond2,cond3)
astref=['starcat','refcat ']
astref_wt=['1 ','10']
for cond1 in astref:
    for cond2 in astref_wt:
        for cond3 in stability_type:
            print "astref=%s astref_wt=%s stability_type=%s" % (cond1,cond2,cond3)

