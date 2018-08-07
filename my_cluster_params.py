#! /usr/bin/env python
# for fgas ppruns only
# see lensing_coadd_type_filter.list for lensing filter/mag/coadd_type info
ppruns=[ "2009-03-28_W-S-I+" ,"2009-09-19_W-J-V" ,"2009-04-29_W-S-Z+" ,"2009-04-29_W-J-B" ,"2010-03-12_W-J-B" ,"2010-03-12_W-S-Z+" ,"2010-03-12_W-C-RC" ,"2010-11-04_W-J-B" ,"2010-11-04_W-S-Z+" ,"2012-07-23_W-C-RC" ,"2013-06-10_W-S-Z+" ,"2007-02-13_W-S-I+" ,"2007-02-13_W-J-V" ,"2010-03-12_W-J-V" ,"2010-03-12_W-S-I+" ,"2010-12-05_W-J-V" ,"2015-12-15_W-J-B" ,"2015-12-15_W-C-RC" ,"2015-12-15_W-S-Z+"]
ppruns_MACS1115=[ "2009-04-29_W-S-Z+" ,"2009-04-29_W-J-B" ,"2010-03-12_W-J-B" ,"2010-03-12_W-S-Z+" ,"2010-03-12_W-C-RC"]
ppruns_preH=[ "2010-03-12_W-S-I+" ,"2010-12-05_W-J-V" ,"2007-02-13_W-J-V" ,"2007-02-13_W-S-I+" ,"2009-03-28_W-S-I+" ,"2010-03-12_W-J-V"]
ppruns_10_3= ['2009-03-28_W-S-I+', '2009-09-19_W-J-V', '2009-04-29_W-S-Z+', '2009-04-29_W-J-B', '2010-03-12_W-J-B', '2010-03-12_W-S-Z+', '2010-03-12_W-C-RC', '2010-11-04_W-J-B', '2010-11-04_W-S-Z+', '2012-07-23_W-C-RC', '2013-06-10_W-S-Z+', '2010-03-12_W-J-V', '2010-03-12_W-S-I+', '2010-12-05_W-J-V', '2015-12-15_W-J-B', '2015-12-15_W-C-RC', '2015-12-15_W-S-Z+']
ppruns_10_2= ['2007-02-13_W-S-I+', '2007-02-13_W-J-V']
ppruns_postH= ['2009-09-19_W-J-V', '2009-04-29_W-S-Z+', '2009-04-29_W-J-B', '2010-03-12_W-J-B', '2010-03-12_W-S-Z+', '2010-03-12_W-C-RC', '2010-11-04_W-J-B', '2010-11-04_W-S-Z+', '2012-07-23_W-C-RC', '2013-06-10_W-S-Z+', '2015-12-15_W-J-B', '2015-12-15_W-C-RC', '2015-12-15_W-S-Z+']
ppruns_nonMACS1115= ['2009-03-28_W-S-I+', '2009-09-19_W-J-V', '2010-11-04_W-J-B', '2010-11-04_W-S-Z+', '2012-07-23_W-C-RC', '2013-06-10_W-S-Z+', '2007-02-13_W-S-I+', '2007-02-13_W-J-V', '2010-03-12_W-J-V', '2010-03-12_W-S-I+', '2010-12-05_W-J-V', '2015-12-15_W-J-B', '2015-12-15_W-C-RC', '2015-12-15_W-S-Z+']
ppruns_dec= ['2009-03-28_W-S-I+', '2009-09-19_W-J-V', '2010-11-04_W-J-B', '2010-11-04_W-S-Z+', '2012-07-23_W-C-RC', '2013-06-10_W-S-Z+', '2010-03-12_W-J-V', '2010-03-12_W-S-I+', '2010-12-05_W-J-V', '2015-12-15_W-J-B', '2015-12-15_W-C-RC', '2015-12-15_W-S-Z+']

ic_cldata={'MACS0429-02':{},'MACS1226+21':{},'RXJ2129':{},'MACS1115+01':{},"MACS0416-24":{},'MACS0159-08':{}, 'Zw2089':{}, 'Zw2701':{}, 'A2204':{}}
ic_cldata['MACS1226+21']['FILTERs']=["W-J-B","W-J-V","W-C-RC","W-C-IC","W-S-Z+"]
ic_cldata['MACS1226+21']['PPRUNs']=["W-C-IC_2010-02-12", "W-C-IC_2011-01-06","W-C-RC_2010-02-12", "W-J-B_2010-02-12", "W-J-V_2010-02-12", "W-S-Z+_2011-01-06"]
ic_cldata['MACS1226+21']['FILTERs_matching_PPRUNs']=["W-C-IC", "W-C-IC","W-C-RC", "W-J-B", "W-J-V", "W-S-Z+"] 
ic_cldata['MACS0429-02']['FILTERs']=["W-J-B","W-S-Z+"]
ic_cldata['MACS0429-02']['FILTERs_matching_PPRUNs']=["W-J-B","W-S-Z+"]
ic_cldata['MACS0429-02']['PPRUNs']=["W-J-B_2015-12-15","W-S-Z+_2015-12-15"]
ic_cldata['RXJ2129']['FILTERs']=["W-J-B","W-C-RC","W-S-Z+"]
ic_cldata['RXJ2129']['FILTERs_matching_PPRUNs']=["W-J-B","W-C-RC","W-S-Z+"]
ic_cldata['RXJ2129']['PPRUNs']=["W-J-B_2010-11-04","W-C-RC_2012-07-23","W-S-Z+_2010-11-04"]
ic_cldata['MACS1115+01']['FILTERs']=["W-J-B","W-C-RC","W-S-Z+"] 
ic_cldata['MACS1115+01']['FILTERs_matching_PPRUNs']=["W-S-Z+","W-J-B","W-J-B","W-S-Z+","W-C-RC"]
ic_cldata['MACS1115+01']['PPRUNs']=["W-S-Z+_2009-04-29","W-J-B_2009-04-29","W-J-B_2010-03-12","W-S-Z+_2010-03-12","W-C-RC_2010-03-12"]
ic_cldata['MACS0416-24']['FILTERs']=["W-J-B","W-C-RC","W-S-Z+"] 
ic_cldata['MACS0416-24']['FILTERs_matching_PPRUNs']=["W-J-B","W-C-RC","W-S-Z+"] 
ic_cldata['MACS0416-24']['PPRUNs']=["W-J-B_2010-11-04","W-C-RC_2010-11-04","W-S-Z+_2010-11-04"] 
ic_cldata['MACS0159-08']['FILTERs']=["W-J-B"]
ic_cldata['MACS0159-08']['FILTERs_matching_PPRUNs']=["W-J-B"]
ic_cldata['MACS0159-08']['PPRUNs']=["W-J-B_2015-12-15"]
ic_cldata['Zw2089']['FILTERs']=['W-J-B','W-J-V','W-C-RC','W-S-I+','W-S-Z+']
ic_cldata['Zw2089']['FILTERs_matching_PPRUNs']=['W-C-RC','W-J-B','W-J-V','W-S-I+','W-S-I+','W-S-Z+']
ic_cldata['Zw2089']['PPRUNs']=['W-C-RC_2015-12-15','W-J-B_2015-12-15','W-J-V_2010-12-05','W-S-I+_2007-02-13','W-S-I+_2009-03-28','W-S-Z+_2015-12-15']
ic_cldata['Zw2701']['FILTERs']=['W-J-B','W-J-V','W-C-RC','W-S-I+']
ic_cldata['Zw2701']['FILTERs_matching_PPRUNs']=['W-C-RC','W-J-B','W-J-V','W-J-V','W-S-I+']
ic_cldata['Zw2701']['PPRUNs']=['W-C-RC_2015-12-15','W-J-B_2015-12-15','W-J-V_2010-03-12','W-J-V_2010-12-05','W-S-I+_2010-03-12']
ic_cldata['A2204']['FILTERs']=['W-J-V','W-S-I+']
ic_cldata['A2204']['FILTERs_matching_PPRUNs']=['W-J-V','W-S-I+']
ic_cldata['A2204']['PPRUNs']=['W-J-V_2009-09-19','W-S-I+_2009-03-28']
ra_cluster={}
dec_cluster={}
ra_cluster['MACS0429-02']=67.40041667 ; dec_cluster['MACS0429-02']=-2.88555556
ra_cluster['RXJ2129']=322.41625000 ; dec_cluster['RXJ2129']=0.08888889
ra_cluster['MACS1226+21']=186.71268; dec_cluster['MACS1226+21']=21.831938
ra_cluster['A2204']=248.19666667; dec_cluster['A2204']=5.57555556
ra_cluster['MACS0159-08']=29.9579;dec_cluster['MACS0159-08']=-8.83028
#MACSJ0429.6-0253	67.4	-2.88375
#RXJ2129.6+0005	322.408	0.094
ra_cluster['Zw2089']=135.158;dec_cluster['Z2089']=20.916
ra_cluster['Zw2701']=148.198;dec_cluster['Z2701']=51.891
ra_cluster['MACS1115+01']=168.972;dec_cluster['MACS1115+01']=1.49639
ra_cluster['MACS0416-24']=64.0413;dec_cluster['MACS0416-24']=6-24.0662


clusters =['MACS0429-02','MACS1226+21','RXJ2129','MACS1115+01',"MACS0416-24",'MACS0159-08', 'Zw2089', 'Zw2701', 'A2204']
fgas_clusters =['MACS0429-02','RXJ2129','MACS1115+01','MACS0159-08', 'Zw2089', 'Zw2701', 'A2204']
clusters_refcats={}
clusters_refcats['MACS0429-02']='PANSTARRS'
clusters_refcats['RXJ2129']='SDSS'
clusters_refcats['MACS1226+21']='SDSS'
clusters_refcats['A2204']='PANSTARRS'
clusters_refcats['MACS0159-08']='SDSS'
clusters_refcats['Zw2089']='SDSS'
clusters_refcats['Zw2701']='SDSS'
clusters_refcats['MACS1115+01']='SDSS'
clusters_refcats['MACS0416-24']='PANSTARRS'

if __name__=='__main__':
	import adam_quicktools_ArgCleaner
	import sys
	argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
	if len(argv)>1:
		cluster = argv[0]
		property = argv[1]
		if property=='PPRUN' or property=='PPRUNs':
			print ' '.join(ic_cldata[cluster]['PPRUNs'])
		if property=='FILTER' or property=='FILTERs':
			print ' '.join(ic_cldata[cluster]['FILTERs'])

