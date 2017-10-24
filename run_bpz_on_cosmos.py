#! /usr/bin/env python
oldcat = '/u/ki/dapple/nfs12/cosmos/cosmos.cat'
newcat="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat"
M_0_filt="rp"

ns=globals()
import os,sys
env_vars=os.environ.keys()
vars_ok=True
if not os.environ['BPZPATH']: 
	print "BPZPATH isn't defined!"
	vars_ok=False
subarudir = os.environ['subdir']

import re, string, numpy,scipy
from glob import glob
import astropy.io.fits as pyfits
import ldac
from astropy.io import ascii

newcatobj=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat")
#cat=newcatobj.hdu
#keys=newcatobj.keys()
#for k in keys:
#    dkey='d'+k
#    if dkey in keys:
#        print k

##all keys in this cat: 'gp      ' 'dIB484  ' 'F814W   ' 'i_max   ' 'dIB527  ' 'dH1     ' 'K_uv    ' 'NB816   ' 'z_s     ' 'IB738   ' 'ID_2006 ' 'i_auto  ' 'dH_uv   ' 'i_star  ' 'H       ' 'du_s    ' 'F814W_star' 'J_uv    ' 'dch3    ' 'dIB738  ' 'du      ' 'dIB827  ' 'IB427   ' 'dJ      ' 'dH      ' 'dB      ' 'H_uv    ' 'IB505   ' 'J3      ' 'dch2    ' 'dV      ' 'x       ' 'dip     ' 'IB624   ' 'FUV     ' 'dIB505  ' 'dJ3     ' 'dJ2     ' 'dKs     ' 'di_s    ' 'Eb-v    ' 'J2      ' 'g_s     ' 'J1      ' 'dIB624  ' 'dK_uv   ' 'dKc     ' 'di_c    ' 'zp      ' 'rp      ' 'dKnf    ' 'dH2     ' 'appflag ' 'ra      ' 'photflag' 'dF814W  ' 'dNUV    ' 'auto_offset' 'ID_2008 ' 'acs_mask' 'dNB816  ' 'di_auto ' 'H2      ' 'drp     ' 'H1      ' 'dIB427  ' 'dzp     ' 'dFUV    ' 'deep_mask' 'V_mask  ' 'dJ1     ' 'dIB767  ' 'z_mask  ' 'dg_s    ' 'i_mask  ' 'IB574   ' 'dzpp    ' 'NUV     ' 'zpp     ' 'blendflag' 'mask_NUV' 'IB679   ' 'Kc      ' 'B       ' 'J       ' 'F814W_fwhm' 'Ks      ' 'dIB574  ' 'det_fwhm' 'dIB679  ' 'V       ' 'i_fwhm  ' 'IB709   ' 'ch1     ' 'ch2     ' 'ch3     ' 'ch4     ' 'IB767   ' 'mask_FUV' 'dec     ' 'IRAC2_mask' 'ip      ' 'i_c     ' 'i_s     ' 'dIB709  ' 'dz_s    ' 'dJ_uv   ' 'r_s     ' 'dY_uv   ' 'u_s     ' 'Kc_mask ' 'B_mask  ' 'auto_flag' 'tile    ' 'flags   ' 'dch1    ' 'IRAC1_mask' 'dch4    ' 'acsdata_mask' 'dNB711  ' 'Knf     ' 'y       ' 'dgp     ' 'IB827   ' 'ID      ' 'NB711   ' 'IB464   ' 'Y_uv    ' 'IB527   ' 'u       ' 'objID   ' 'dr_s    ' 'IB484   ' 'dIB464  '
##'gp''dIB484''F814W''i_max''dIB527''dH1''K_uv''NB816''z_s''IB738''ID_2006''i_auto''dH_uv''i_star''H''du_s''F814W_star''J_uv''dch3''dIB738''du''dIB827''IB427''dJ''dH''dB''H_uv''IB505''J3''dch2''dV''x''dip''IB624''FUV''dIB505''dJ3''dJ2''dKs''di_s''Eb-v''J2''g_s''J1''dIB624''dK_uv''dKc''di_c''zp''rp''dKnf''dH2''appflag''ra''photflag''dF814W''dNUV''auto_offset''ID_2008''acs_mask''dNB816''di_auto''H2''drp''H1''dIB427''dzp''dFUV''deep_mask''V_mask''dJ1''dIB767''z_mask''dg_s''i_mask''IB574''dzpp''NUV''zpp''blendflag''mask_NUV''IB679''Kc''B''J''F814W_fwhm''Ks''dIB574''det_fwhm''dIB679''V''i_fwhm''IB709''ch1''ch2''ch3''ch4''IB767''mask_FUV''dec''IRAC2_mask''ip''i_c''i_s''dIB709''dz_s''dJ_uv''r_s''dY_uv''u_s''Kc_mask''B_mask''auto_flag''tile''flags''dch1''IRAC1_mask''dch4''acsdata_mask''dNB711''Knf''y''dgp''IB827''ID''NB711''IB464''Y_uv''IB527''u''objID''dr_s''IB484''dIB464'
## BVRIZ or ugriz or ugrizY
#u u_s
#i_c and i_s
## alloptical=["B","H","H1","H2","J","J1","J2","J3","Kc","Knf","Ks","V","g_s","gp","i_auto","i_c","i_s","ip","r_s","rp","u","u_s","z_s","zp","zpp"]
master_filterlist=["B","V","g_s","gp","i_auto","i_c","i_s","ip","r_s","rp","u","u_s","z_s","zp","zpp","Y_uv"]
BVRIZ_filterlists = [['B','V','r_s','i_c','z_s'], ['B','V','rp','i_c','z_s'], ['B','V','r_s','i_s','z_s'], ['B','V','rp','i_s','z_s'], ['B','V','r_s','ip','z_s'], ['B','V','rp','ip','z_s']]
BVRIZ_filterlists += [['B','V','r_s','i_c','zp'], ['B','V','rp','i_c','zp'], ['B','V','r_s','i_s','zp'], ['B','V','rp','i_s','zp'], ['B','V','r_s','ip','zp'], ['B','V','rp','ip','zp']]
BVRIZ_filterlists += [['B','V','r_s','i_c','zpp'], ['B','V','rp','i_c','zpp'], ['B','V','r_s','i_s','zpp'], ['B','V','rp','i_s','zpp'], ['B','V','r_s','ip','zpp'], ['B','V','rp','ip','zpp']]
## README_UVISTA_v4.1.txt says:
# This catalog contains aperture fluxes with an AB magnitude zeropoint of 25.  Magnitudes can be determined with 
# m_filter = -2.5*log10(flux_filter) + 25.  The catalog has been put through many quality tests (zphot vs. zspec, number counts, 
# looking for unusual objects, comparison of some SEDs with NMBS) and is a science-grade catalog; however, be aware that there are 
# many many objects and error checking is not completely fool proof.  The catalog is just entering larger consumption so it is likely 
# this will reveal issues that were not discovered in the initial error checking.  If you are using the catalog and find issues, 
# please contact me (muzzin@strw.leidenuniv.nl) so that I can address these in future catalogs.

## put filter curves in place
filter_curves={'B':'B_subaru.res', 'V':'V_subaru.res',
"g_s":"g_SDSS.res", "i_s":"i_SDSS.res", "r_s":"r_SDSS.res", "u_s":"u_SDSS.res", "z_s":"z_SDSS.res",
"gp":"g_subaru.res", "ip":"i_subaru.res", "rp":"r_subaru.res", "zp":"z_subaru.res",
"zpp":"suprime_FDCCD_z.res", "u":"u_megaprime_sagem.res","Y_uv":"Y_uv.res"}
for z in filter_curves.keys():
    f = '' + z + '.res'
    #print ' os.environ["BPZPATH"]+"/FILTER/"+f=',os.environ["BPZPATH"]+"/FILTER/"+f
    existing_curves=glob(os.environ["BPZPATH"]+"/FILTER/"+f)

    if len(existing_curves) != 0:
        print f + " exists!!!"
    else:
	linkstr='ln -s %s/transmission_curves/%s /nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/bpz-1.99.3/FILTER/%s' % (runbpzdir,filter_curves[z],f)
	print linkstr
        ooo=os.system(linkstr)
        if ooo!=0: raise Exception("os.system failed!!!")

print "setting up BVRIZ run on new cosmos field"
cluster="cosmos_ultravista"
## make the bpz columns and bpz input file
runbpzdir="/u/ki/awright/COSMOS_2017/run_bpz_on_COSMOS/"
photdir="/u/ki/awright/COSMOS_2017/run_bpz_on_COSMOS/BVRIZ_inputs/"
BVRIZ_filterlists = [['B','V','rp','ip','zpp']]
for filterlist in BVRIZ_filterlists:
	signature='-'.join(filterlist)
	columns_fl= photdir + cluster+'_'+signature + '.bpz.columns'
	cat_fl= photdir + cluster+'_'+signature+".bpz_input.txt"

	## write columns file
	columns_fo= open(columns_fl,'w')
	columns_num=2
	ascii_cat_keys=["ID"]
	for filt in filterlist:
		filt_col=[filt,'%i,%i' % (columns_num,1+columns_num),'AB','0.02','0.0\n']
		columns_fo.write('\t'.join(filt_col))
		ascii_cat_keys.append(filt)
		ascii_cat_keys.append('d'+filt)
		columns_num+=2

	if M_0_filt==None:
		raise Exception("the filter %s used for M_0 didn't show up in filterlist" % (M_0_filt))
	else:
		ascii_cat_keys.append(M_0_filt)
	columns_fo.write('\t'.join(['ID','1\n']))
	columns_fo.write('\t'.join(['M_0',str(columns_num)+'\n']))
	columns_fo.close()

	datas=[];formats={};names=[]
	## add ID
	datas.append(newcatobj['ID'])
	names.append('ID')
	formats={'ID':'%i'}
	## add each filter
	for k in filterlist:
	    mag=clip(newcatobj[k],-99.0,99.0)
	    dmag=clip(newcatobj['d'+k],-99.0,99.0)
	    datas.append(mag)
	    datas.append(dmag)
	    names.append(k)
	    names.append('d'+k)
	    formats[k]='%.2f'
	    formats['d'+k]='%.2f'
	## add M_0
	datas.append(clip(newcatobj[M_0_filt],-99.0,99.0))
	names.append('M_0')
	formats={'M_0':'%.2f'}
	ascii.write(table=datas, output=cat_fl, formats=formats,names=names,Writer=astropy.io.ascii.NoHeader)
	#ascii.write(table,'ultravista_cosmos.txt',formats=formats)
	#OR#ascii.write([newcatobj['r_s'],newcatobj['dr_s']],'test.txt',formats={'r_s':'%.2f','dr_s':'%.2f'},names=['r_s','dr_s'])
	print "wrote catalog: %s with columns: %s " % (cat_fl,columns_fl)

#cat_fl="cosmos_ultravista_B-V-rp-ip-zpp.bpz_input.txt"
#columns_fl="cosmos_ultravista_B-V-rp-ip-zpp.bpz.columns"

dict = { 'runbpzdir':runbpzdir,
    'PHOTOMETRYDIR': signature+'_output',
    'ONLY_TYPE': 'no',
    'M_0_filt':M_0_filt,
    'cluster':cluster,
    'BPZPATH':os.environ['BPZPATH'],
    'signature':signature,
    'SPECTRA':'CWWSB_capak.list' }

basedir = '%(runbpzdir)s/%(PHOTOMETRYDIR)s/' % dict
if not os.path.exists(basedir):
    os.mkdir(basedir)

base = '%(runbpzdir)s/%(PHOTOMETRYDIR)s/%(cluster)s.%(signature)s.%(SPECTRA)s.%(M_0_filt)s' % dict
dict['columns'] = base + '.columns'
dict['flux'] = base + '.flux_comparison'
dict['catalog'] = base + '.bpz'
dict['incat'] = base + '.cat'
dict['prob'] = base + '.probs'
dict['INTERP'] = '8'
dict['magvar'] = 'yes' #used MAGs not FLUXes

for z in filterlist:
    f = '' + z + '.res'
    #print ' os.environ["BPZPATH"]+"/FILTER/"+f=',os.environ["BPZPATH"]+"/FILTER/"+f
    existing_curves=glob(os.environ["BPZPATH"]+"/FILTER/"+f)
    if len(existing_curves) == 0:
        raise Exception("NO CURVE FOR THIS FILTER!")

incat = base + '.cat'
command_cp_cat=' '.join(["cp",cat_fl,incat])
print "command_cp_cat=",command_cp_cat
ooo=os.system(command_cp_cat)
if ooo!=0: raise Exception("os.system failed!!!")
command_cp_columns=' '.join(["cp",columns_fl,dict['columns']])
print "command_cp_columns=",command_cp_columns
ooo=os.system(command_cp_columns)
if ooo!=0: raise Exception("os.system failed!!!")


#if pars.d['ONLY_TYPE']=='yes': #Use only the redshift information, no priors
# probably have to run it with pars.d['ONLY_TYPE']=='yes' and 'no' to see impact

command = 'python %(BPZPATH)s/bpz.py %(incat)s \
-COLUMNS %(columns)s \
-MAG %(magvar)s \
-SPECTRA %(SPECTRA)s \
-ONLY_TYPE %(ONLY_TYPE)s \
-PRIOR hdfn_SB \
-CHECK yes \
-PLOTS yes \
-VERBOSE yes \
-ZMAX 4.0 \
-INTERP %(INTERP)s \
-INTERACTIVE no \
-PROBS_LITE %(prob)s \
-OUTPUT %(catalog)s' % dict
#adam-changed# -NEW_AB yes 

print ' command=',command
ooo=os.system(command)
if ooo!=0: 
    raise Exception("os.system failed!!!")

#print "adam-look: running parsebpz(catalog=",catalog,")"
#parsebpz(catalog) #outputs ldac cat named catalog+".tab"
#adam-comment# parsebpz takes catalog and makes catalog+".tab", which is in ldac format

#''' join the tables '''
#output = base + '.input_and_bpz.tab'
#join_cats([catalog+'.tab',(inputcat_alter_ldac,"OBJECTS")],output)
#convert_to_mags(base,output,base+'.EVERY.cat')
