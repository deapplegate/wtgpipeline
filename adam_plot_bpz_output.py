#adam-does# plots some helpful stuff from convert_to_mags func in adam_do_multiple_photoz.py
# The catalog that you will use for the CC analysis is cut_lensing.cat . It still needs the shear calibration applied, which happens at the beginning of cc_masses_1p5Mpc.sh .
#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning#
#adam-Warning#
import astropy.io.fits as pyfits
from matplotlib.pylab import *
import numpy
import ldac

import sys,os
purepath=sys.path
addpath=[os.environ['BPZPATH']]+purepath
sys.path=addpath
from useful import ejecuta,get_header,put_header,get_str,put_str,get_data,get_2Darray,put_2Darray,params_file,params_commandline,view_keys,match_resol,overlap,match_objects,match_min,match_min2
from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig
sys.path=purepath+['/u/ki/awright/InstallingSoftware/pythons/']
import imagetools

#adam-Warning# names to put on plots
cluster=os.environ['cluster']
ztrue=0.355
z95width_cut=2.5 #adam-default#

#for z95width_cut in [1.75, 2.0, 2.25,2.5]: #293<<
z95width_cut_str= str(z95width_cut).replace('.','pt')
bpzmode="PureStarCalib-lens_RS_and_pdz%s_cuts" % (z95width_cut_str)
nametag="-%s-%s" % (cluster,bpzmode)


## open lensing catalog
lens_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cut_lensing.cat"
lens_fo = pyfits.open(lens_fl)[4]
SeqNr_lens_b4=lens_fo.data.field('SeqNr')

## open RS catalog
rs_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/MACS1115+01_redsequence.cat"
rs_fo = pyfits.open(rs_fl)[4]
SeqNr_rs_b4=rs_fo.data.field('SeqNr')

## get bpz info
run_name="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.APER1.1.CWWSB_capak.list.all"
bpz_fl= run_name + '.bpz'
zs_all=get_2Darray(bpz_fl)


## open photometry catalog
mag_fl = "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.alter.cat"
mag_fo = pyfits.open(mag_fl)[1]
SeqNr_all_b4=mag_fo.data.field('SeqNr')

## let's get the cuts arranged properly
passed_pdz_cut=zeros(SeqNr_all_b4.shape,dtype=bool)
passed_lens_cut=zeros(SeqNr_all_b4.shape,dtype=bool)
passed_rs_cut=zeros(SeqNr_all_b4.shape,dtype=bool)
passed_rs_cut[SeqNr_rs_b4-1]=True
passed_lens_cut[SeqNr_lens_b4-1]=True

## now get the pdzs!
import pdzfile_utils
pdzmanager = pdzfile_utils.PDZManager.parsePDZ('/nfs/slac/g/ki/ki18/anja/SUBARU//MACS1115+01/PHOTOMETRY_W-C-RC_aper//MACS1115+01.APER1.1.CWWSB_capak.list.all.probs')
zrange=arange(.01,4.01,.01)
zbins=zrange-.005
pdz_all=pdzmanager.pdzcat['pdz']
assert((pdzmanager.pdzcat['SeqNr']==SeqNr_all_b4).all())
assert(len(pdz_all)==len(SeqNr_all_b4))
assert((SeqNr_all_b4==zs_all[:,0]).all())

## make pdz quality cut
#paper says: rejecting galaxies with very wide P(z),: z95% >= 2.5
top=0.975
bottom=0.025
#adam-SHNT# make the p(z) quality cut from here:
# /nfs/slac/kipac/fs1/u/rherbonn/photoz/WtG/scripts/cut_bpzcat.py
cumpdz_all=np.cumsum(pdz_all,axis=1)
SeqNr_pass_pdz_cut=[]
SeqNr_fail_pdz_cut=[]
z95widths=[]
for SeqNr,cumpdz in zip(SeqNr_all_b4,cumpdz_all):
	#adam: this is correct, remember that cumpdz is a monotonically increasing function
	z95width=zrange[cumpdz>=top][0] - zrange[cumpdz>=bottom][0]
	z95widths.append( z95width)
	#adam-old# z90width=zrange[cumpdz >= 0.95][0] - zrange[cumpdz >= 0.05][0]
	if z95width<z95width_cut:
		passed_pdz_cut[SeqNr-1]=True
		SeqNr_pass_pdz_cut.append(SeqNr)
	else:
		passed_pdz_cut[SeqNr-1]=False
		SeqNr_fail_pdz_cut.append(SeqNr)

## save for compare script
import pickle
fo=open('SeqNr_fail_pdz_cut.pkl','wb')
pickle.dump(SeqNr_fail_pdz_cut,fo)
fo.close()

## plot the z95width stuff
z95widths=array( z95widths )
f=figure()
ax=f.add_subplot(1,1,1)
ax.axvline(2.5,color='red',ls=':',label='cut value')
xlabel(u'$\Delta_Z$ = Z(2.5%)-Z(97.5%)')
title(u'$\Delta_Z$: 95% width in redshift space')
hist(z95widths,arange(0,3.80,.05),label='all',log=True)
z95_lens=z95widths[passed_lens_cut]
z95_rs=z95widths[passed_rs_cut]
hist(z95_lens,arange(0,3.80,.05),histtype='step',label='lens',color='green',log=True)
hist(z95_rs,arange(0,3.80,.05),histtype='step',label='RS',color='red',log=True)
legend()
f.savefig('plt_DeltaZ_z95width_distribution')

## make combined cuts
passed_lens_and_pdz_cut=passed_pdz_cut*passed_lens_cut
passed_rs_and_pdz_cut=passed_pdz_cut*passed_rs_cut
print ' passed_pdz_cut.sum()=',passed_pdz_cut.sum() , ' passed_rs_cut.sum()=',passed_rs_cut.sum() , ' passed_lens_cut.sum()=',passed_lens_cut.sum() , ' passed_lens_and_pdz_cut.sum()=',passed_lens_and_pdz_cut.sum() , ' passed_rs_and_pdz_cut.sum()=',passed_rs_and_pdz_cut.sum()
print ' passed_pdz_cut.__len__()=',passed_pdz_cut.__len__() , ' passed_rs_cut.__len__()=',passed_rs_cut.__len__() , ' passed_lens_cut.__len__()=',passed_lens_cut.__len__() , ' passed_lens_and_pdz_cut.__len__()=',passed_lens_and_pdz_cut.__len__() , ' passed_rs_and_pdz_cut.__len__()=',passed_rs_and_pdz_cut.__len__()

# Make NFILT calculation count 10_3 and 10_2 mags from the same filter as one 
# apply the NFILT cuts, and put the resulting catalog somewhere for @Ricardo Herbonnet to find

zs_pdz=zs_all[passed_pdz_cut]
zs_rs=zs_all[passed_rs_and_pdz_cut]
zs_lens=zs_all[passed_lens_and_pdz_cut]
Z_B_lens=zs_lens[:,1]
Z_B_rs=zs_rs[:,1]
Z_B_WOpdz_rs=zs_all[passed_rs_cut][:,1]
Z_B_WOpdz_lens=zs_all[passed_lens_cut][:,1]


SeqNr_lens=SeqNr_all_b4[passed_lens_and_pdz_cut]
SeqNr_rs=SeqNr_all_b4[passed_rs_and_pdz_cut]
pdzrange,pdz_lens=pdzmanager.associatePDZ(SeqNr_lens)
pdzrange,pdz_rs=pdzmanager.associatePDZ(SeqNr_rs)
SeqNr_WOpdz_lens=SeqNr_all_b4[passed_lens_cut]
SeqNr_WOpdz_rs=SeqNr_all_b4[passed_rs_cut]
pdzrange,pdz_WOpdz_lens=pdzmanager.associatePDZ(SeqNr_WOpdz_lens)
pdzrange,pdz_WOpdz_rs=pdzmanager.associatePDZ(SeqNr_WOpdz_rs)


## get NFILT info and quantify cuts
NFILT_all=mag_fo.data.field('NFILT')
NFILT_pdz=mag_fo.data.field('NFILT')[passed_pdz_cut]
NFILT_lens=mag_fo.data.field('NFILT')[passed_lens_cut]
NFILT_rs=mag_fo.data.field('NFILT')[passed_rs_cut]
NFILT_lens_and_pdz=mag_fo.data.field('NFILT')[passed_lens_and_pdz_cut]
NFILT_rs_and_pdz=mag_fo.data.field('NFILT')[passed_rs_and_pdz_cut]
print_num_pdz = "# passed  pdz     cuts: %s" % (len(NFILT_pdz))
print_num_lens= "# passed lensing  cuts: %s" % (len(NFILT_lens))
print_num_rs =  "# passed   RS     cuts: %s" % (len(NFILT_rs))
print_num_lens_and_pdz= "# passed lens+pdz cuts: %s" % (len(NFILT_lens_and_pdz))
print_num_rs_and_pdz =  "# passed  RS+pdz  cuts: %s" % (len(NFILT_rs_and_pdz))
print_per_lens= "%" +" passed lensing  cuts: %.2f" % (len(NFILT_lens)*100.0/float(len(mag_fo.data.field('NFILT'))))
print_per_rs =  "%" + " passed   RS     cuts: %.2f" % (len(NFILT_rs)*100.0/float(len(mag_fo.data.field('NFILT'))))
print_per_lens_and_pdz= "%" +" passed lens+pdz cuts: %.2f" % (len(NFILT_lens_and_pdz)*100.0/float(len(mag_fo.data.field('NFILT'))))
print_per_rs_and_pdz =  "%" + " passed  RS+pdz  cuts: %.2f" % (len(NFILT_rs_and_pdz)*100.0/float(len(mag_fo.data.field('NFILT'))))
lens_info=print_per_lens+'\n'+print_num_lens
rs_info=print_per_rs+'\n'+print_num_rs
print lens_info
print rs_info
lens_and_pdz_info=print_per_lens_and_pdz+'\n'+print_num_lens_and_pdz
rs_and_pdz_info=print_per_rs_and_pdz+'\n'+print_num_rs_and_pdz
print lens_and_pdz_info
print rs_and_pdz_info


## now get the pdz peaks
pdz_stack_WOpdz_lens=pdz_WOpdz_lens.sum(axis=0)
pdz_stack_WOpdz_rs=pdz_WOpdz_rs.sum(axis=0)
pdz_stack_lens=pdz_lens.sum(axis=0)
pdz_stack_rs=pdz_rs.sum(axis=0)
pdzbins=np.array(pdzrange-pdzrange[0]/2)
# (pdzbins==zbins).all() is True
pdz_peak_lens=pdzbins[pdz_stack_lens.argmax()]
pdz_peak_rs=pdzbins[pdz_stack_rs.argmax()]
#adam-SHNT# I'm not so sure about the binning, if it's supposed to start at 0.00 or 0.01
pdz_peak_str_lens='pdz lens peak: %.3f True Z: %.3f (difference: %.3f)' % (pdz_peak_lens,ztrue, pdz_peak_lens-ztrue)
pdz_peak_str_rs='pdz RS peak: %.3f True Z: %.3f (difference: %.3f)' % (pdz_peak_rs,ztrue, pdz_peak_rs-ztrue)

## plotting bpz output
ulim=3.0
f=figure(figsize=(13,9))
f.suptitle("plt_bpz_pdz_stack"+nametag)
ax=f.add_subplot(2,1,1)
ax.set_title('P(z) stack and Z_BEST histogram for all galaxies that pass the lensing cuts')
ax.plot(zbins,pdz_stack_WOpdz_lens,'k--',label='P(z) stack lens cuts, not pdz cuts')
ax.plot(zbins,pdz_stack_lens,'k-',label='P(z) stack lens cuts & pdz cuts')
ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')

Z_B_stack_WOpdz_lens,bins,patch=ax.hist(Z_B_WOpdz_lens,bins=zbins,label='lens cuts, not pdz cuts')
Z_B_stack_lens,bins,patch=ax.hist(Z_B_lens,bins=zbins,label='lens cuts & pdz cuts')
Z_B_peak_lens=zbins[Z_B_stack_lens.argmax()]
Z_B_peak_str_lens='Z_B peak: %.3f True Z: %.3f (difference: %.3f)' % (Z_B_peak_lens,ztrue, Z_B_peak_lens-ztrue)
ax.set_xlim(0,ulim)
ax.text(1,135,lens_and_pdz_info+'\n\n'+lens_info,size=12)
legend()

ax=f.add_subplot(2,1,2)
ax.set_title('P(z) stack and Z_BEST histogram for Red Sequence galaxies ')
ax.plot(zbins,pdz_stack_WOpdz_rs,'k--',label='P(z) stack rs cuts, not pdz cuts')
ax.plot(zbins,pdz_stack_rs,'k-',label='P(z) stack rs cuts & pdz cuts')
ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
ax.set_xlabel('Redshift',size=12)

Z_B_stack_WOpdz_rs,bins,patch=ax.hist(Z_B_WOpdz_rs,bins=zbins,label='rs cuts, not pdz cuts')
Z_B_stack_rs,bins,patch=ax.hist(Z_B_rs,bins=zbins,label='rs cuts & pdz cuts')
Z_B_peak_rs=zbins[Z_B_stack_rs.argmax()]
Z_B_peak_str_rs='Z_B peak: %.3f True Z: %.3f (difference: %.3f)' % (Z_B_peak_rs,ztrue, Z_B_peak_rs-ztrue)
ax.text(1,20,rs_and_pdz_info+'\n\n'+rs_info+'\n\n'+Z_B_peak_str_rs+'\n\n'+pdz_peak_str_rs,size=12)
ax.set_xlim(0,ulim)
f.tight_layout()
legend()
f.subplots_adjust(top=.93)
f.savefig("plt_bpz_pdz_stack"+nametag)


f=figure(figsize=(13,9))
ax=f.add_subplot(1,1,1)
ax.set_title('Z_BEST histogram and P(z) stack for Red Sequence galaxies ',size=15)
ax.plot(zbins,pdz_stack_rs,'r-',label='P(z) stack')
ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
ax.set_xlabel(pdz_peak_str_rs)
Z_B_stack_rs,bins,patch=ax.hist(Z_B_rs,bins=zbins,label='Z_BEST histogram')
Z_B_peak_rs=zbins[Z_B_stack_rs.argmax()]
Z_B_peak_str_rs='Z_B peak: %.3f True Z: %.3f (difference: %.3f)' % (Z_B_peak_rs,ztrue, Z_B_peak_rs-ztrue)
ax.set_xlabel('Redshift',size=14)
ax.text(.7,35,lens_info+'\n\n'+rs_info+'\n\n'+Z_B_peak_str_rs+'\n\n'+pdz_peak_str_rs,size=14)
f.tight_layout()
f.subplots_adjust(top=.94)
ax.set_xlim(0,1.65)
legend()
f.savefig("plt_bpz_RS_hist_and_pdz_stack"+nametag)


tbins=arange(1,6.2,.111)-.01
obins=arange(0,1,.005)
chibins=arange(-3,3,.05)
m0bins=arange(18,35,.1)
bins_list_master=[zbins,zbins,zbins,tbins, obins, zbins, tbins, chibins, m0bins]

## use new hist2d func
keys=["Z_B","Z_B_MIN","Z_B_MAX","T_B","ODDS","Z_ML","T_ML","CHI_SQUARED","M_0"]
keys2use=np.array([0,0,3,4,5,7,8],dtype=int)
bins_list=[bins_list_master[i] for i in keys2use]
NFILTs=[NFILT_all,NFILT_pdz,NFILT_rs_and_pdz,NFILT_lens_and_pdz]
pdzmode="pdz%s_cut" % (z95width_cut_str)
nametags=['-MACS1115+01-PureStarCalib-all','-MACS1115+01-PureStarCalib-'+pdzmode,'-MACS1115+01-PureStarCalib-RScut_and_'+pdzmode,'-MACS1115+01-PureStarCalib-lens_cut_and_'+pdzmode]
zs_types=[zs_all.copy(),zs_pdz.copy(),zs_rs.copy(),zs_lens.copy()]
for (zs,NFILT,nametag) in zip(zs_types,NFILTs,nametags):
	Z_B=zs[:,1]
	T_B=zs[:,4]
	ODDS=zs[:,5]
	Z_ML=zs[:,6]
	T_ML=zs[:,7]
	M_0=zs[:,9]
	CHI_finite=isfinite(numpy.log10(zs[:,8]))
	CHI_SQUARED=numpy.log10(zs[:,8])[isfinite(numpy.log10(zs[:,8]))]
	Z_B_cut=where(ODDS>.5,Z_B,-1)

	f=figure(figsize=(13,9))
	title('Z_B '+nametag)
	hist(Z_B,bins=zbins,label='normal')
	hist(Z_B[NFILT==6],bins=zbins,label='normal')
	hist(where(CHI_finite,Z_B,-1),bins=zbins,label='Z_B where CHI_SQUARED is finite'+nametag)

	f=figure(figsize=(13,9))
	f,axes = imagetools.AxesList(fig=f,shape=(3,4))
	i=0; axes[i].hist(Z_B,bins=zbins) ; axes[i].set_title("Z_B")
	yup,ydn=axes[i].get_ylim()
	axes[i].axvline(ztrue,color='red',ls=':',label='Z spec')
	i=1; axes[i].hist(Z_B_cut,bins=zbins) ; axes[i].set_title("Z_B where ODDS>.5")
	axes[i].set_ylim(yup,ydn)
	axes[i].axvline(ztrue,color='red',ls=':',label='Z spec')
	i=2; axes[i].hist(T_B,bins=tbins) ; axes[i].set_title("T_B")
	i=3; axes[i].hist(ODDS,bins=obins) ; axes[i].set_title("ODDS")
	i=4; axes[i].hist(Z_ML,bins=zbins) ; axes[i].set_title("Z_ML")
	axes[i].set_ylim(yup,ydn)
	axes[i].axvline(ztrue,color='red',ls=':',label='Z spec')
	i=5; axes[i].hist(CHI_SQUARED,bins=chibins) ; axes[i].set_title("log10(CHI_SQUARED)")
	i=6; axes[i].hist(M_0,bins=m0bins) ; axes[i].set_title("M_0")
	i=7;ax=axes[i]
	ax.hist(NFILT,bins=arange(8)-.5,log=True)
	ax.set_title("NFILT histogram")
	i=8; ax=axes[i]
	ax.set_title("Z_ML & ODDS HIST")
	axplt1=ax.hist2d(ODDS,Z_ML,bins=(20,20))
	colorbar(axplt1[3],ax=ax)
	i=9; ax=axes[i]
	ax.set_title("T_B & Z_B HIST")
	axplt=ax.hist2d(Z_B,T_B,bins=(20,20))
	colorbar(axplt[3],ax=ax)
	i=10; ax=axes[i]
	ax.set_title("M_0 & Z_B HIST")
	axplt=ax.hist2d(Z_B,M_0,bins=(20,20))
	colorbar(axplt[3],ax=ax)
	i=11; ax=axes[i]
	ax.set_title("Z_ML & Z_B HIST")
	axplt=ax.hist2d(Z_B,Z_ML,bins=(20,20))
	colorbar(axplt[3],ax=ax)
	f.tight_layout()
	f.subplots_adjust(top=.93)
	f.suptitle("plt_bpz_many_properties_"+nametag)
	f.savefig("plt_bpz_many_properties_"+nametag)

	##first I'll have to update pandas or something
	########import pandas as pd
	########df = pd.DataFrame(zs_pick,columns=keys_pick)
	#########plot_pick=scatter_matrix(df, alpha=0.2, figsize=(12, 10), diagonal='hist')
	########import adam_plot_mva
	########hist2d_pick=adam_plot_mva.hist2d_matrix(df, bins=bins_list, figsize=(12, 10), diagonal='hist')
	print ' Z_B.shape=',Z_B.shape , ' ODDS.shape=',ODDS.shape

	f=figure(figsize=(13,9))
	f.suptitle(nametag+": BPZ Z_BEST for objects detected in all 5 filters")
	ax=f.add_subplot(1,1,1)
	ax.set_title("bpz Z_B hist for multiple ODDs cut values")
	ax.hist(Z_B,bins=zbins,histtype='stepfilled',color='k',label='no ODDS cut')
	ax.hist(Z_B[ODDS>.2],bins=zbins,histtype='stepfilled',color='blue',label='ODDS>.2')
	ax.hist(Z_B[ODDS>.4],bins=zbins,histtype='stepfilled',color='green',label='ODDS>.4')
	ax.hist(Z_B[ODDS>.6],bins=zbins,histtype='stepfilled',color='magenta',label='ODDS>.6')
	ax.hist(Z_B[ODDS>.8],bins=zbins,histtype='stepfilled',color='orange',label='ODDS>.8')
	ax.axvline(ztrue,color='red',ls=':',label='Z spec')
	ax.legend()
	ax.set_xlim(0,2.5)
	f.tight_layout()
	f.subplots_adjust(top=.93)
	f.savefig("plt_bpz_Z_B_hist-cut_ODDS_many_vals"+nametag)


sys.exit()


ID=zs_lens[:,0]
ID=array(ID,dtype=int)
Z_B=zs_lens[:,1]
Z_B_MIN=zs_lens[:,2]
Z_B_MAX=zs_lens[:,3]

ID_rs=zs_rs[:,0]
ID_rs=array(ID_rs,dtype=int)
Z_B_rs=zs_rs[:,1]
Z_B_MIN_rs=zs_rs[:,2]
Z_B_MAX_rs=zs_rs[:,3]
T_B_rs=zs_rs[:,4]
ODDS_rs=zs_rs[:,5]
Z_ML_rs=zs_rs[:,6]
T_ML_rs=zs_rs[:,7]
CHI_SQUARED_rs=zs_rs[:,8]
M_0_rs=zs_rs[:,9]

f=figure(figsize=(13,9))
f.suptitle("plt_bpz_hist1"+nametag)
ax=f.add_subplot(2,2,1)
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax.hist(Z_B,bins=zbins)
ax.set_title("bpz Z_B hist ")
ax=f.add_subplot(2,2,2)
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax.set_title("bpz Z_B hist (ODDS>.5)")
ax.hist(Z_B[(ODDS>.5)],bins=zbins)
ax=f.add_subplot(2,2,3)
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax.hist(Z_ML,bins=zbins)
ax.set_title("bpz Z_ML hist ")
ax=f.add_subplot(2,2,4)
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax.set_title("bpz Z_ML hist (ODDS>.5)")
ax.hist(Z_ML[(ODDS>.5)],bins=zbins)
f.tight_layout()
f.subplots_adjust(top=.94)
f.savefig("plt_bpz_hist1"+nametag)


f=figure(figsize=(13,9))
f.suptitle(nametag+": All quantities restricted to objects that passed the lensing cuts")
ax=f.add_subplot(2,3,1)
## new cuts on M_0 and NFILT
ax=f.add_subplot(2,3,4)
ax.hist(Z_ML,bins=zbins)
ax.set_title("bpz Z_ML hist")
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax=f.add_subplot(2,3,5)
ax.set_title("bpz Z_B hist")
ax.hist(Z_B,bins=zbins)
ax.axvline(ztrue,color='red',ls=':',label='Z spec')
ax=f.add_subplot(2,3,6)
ax.hist(NFILT,bins=arange(8)-.5)
ax.set_title("NFILT histogram")
f.tight_layout()
f.subplots_adjust(top=.94)
f.savefig("plt_bpz_hist2"+nametag)

if 0:
	f=figure(figsize=(13,9))
	f.suptitle("plt_bpz_pdz_stack"+nametag)
	ax=f.add_subplot(2,2,1)
	ax.set_title('P(z) stack for all galaxies that pass the lensing cuts')
	ax.plot(zbins,pdz_stack_WOpdz_lens,'k--',label='P(z) stack lens cuts, not pdz cuts')
	ax.plot(zbins,pdz_stack_lens,'k-',label='P(z) stack lens cuts & pdz cuts')
	ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
	ax.set_xlabel(pdz_peak_str_lens)
	legend()

	ax=f.add_subplot(2,2,2)
	ax.set_title('Z_BEST histogram for all galaxies that pass the lensing cuts')
	Z_B_stack_WOpdz_lens,bins,patch=ax.hist(Z_B_WOpdz_lens,bins=zbins,label='lens cuts, not pdz cuts')
	Z_B_stack_lens,bins,patch=ax.hist(Z_B_lens,bins=zbins,label='lens cuts & pdz cuts')
	Z_B_peak_lens=zbins[Z_B_stack_lens.argmax()]
	Z_B_peak_str_lens='Z_B peak: %.3f True Z: %.3f (difference: %.3f)' % (Z_B_peak_lens,ztrue, Z_B_peak_lens-ztrue)
	ax.set_xlabel(Z_B_peak_str_lens)
	ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
	legend()

	ax=f.add_subplot(2,2,3)
	ax.set_title('P(z) stack for Red Sequence galaxies ')
	ax.plot(zbins,pdz_stack_WOpdz_rs,'k--',label='P(z) stack rs cuts, not pdz cuts')
	ax.plot(zbins,pdz_stack_rs,'k-',label='P(z) stack rs cuts & pdz cuts')
	ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
	legend()
	ax.set_xlabel(pdz_peak_str_rs)

	ax=f.add_subplot(2,2,4)
	ax.set_title('Z_BEST histogram for Red Sequence galaxies')
	Z_B_stack_WOpdz_rs,bins,patch=ax.hist(Z_B_WOpdz_rs,bins=zbins,label='rs cuts, not pdz cuts')
	Z_B_stack_rs,bins,patch=ax.hist(Z_B_rs,bins=zbins,label='rs cuts & pdz cuts')
	Z_B_peak_rs=zbins[Z_B_stack_rs.argmax()]
	Z_B_peak_str_rs='Z_B peak: %.3f True Z: %.3f (difference: %.3f)' % (Z_B_peak_rs,ztrue, Z_B_peak_rs-ztrue)
	ax.set_xlabel(Z_B_peak_str_rs)
	ax.axvline(ztrue,color='red',ls=':',label='cluster spec-z')
	f.tight_layout()
	legend()
	f.subplots_adjust(top=.94)
	f.savefig("plt_bpz_pdz_stack"+nametag)

