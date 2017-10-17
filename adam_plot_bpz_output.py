#adam-does# plots some helpful stuff from convert_to_mags func in adam_do_multiple_photoz.py
# convert_to_mags("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.alter.cat" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat")
run_name,mag_cat=("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.alter.cat")

mag = pyfits.open(mag_cat)[1]
cat = run_name + '.bpz'
zs=get_2Darray(cat)

ID=zs[:,0]
Z_B=zs[:,1]
Z_B_MIN=zs[:,2]
Z_B_MAX=zs[:,3]
T_B=zs[:,4]
ODDS=zs[:,5]
Z_ML=zs[:,6]
T_ML=zs[:,7]
CHI_SQUARED=zs[:,8]
M_0=zs[:,9]
NFILT=mag.data.field('NFILT')

f=figure()
ax=f.add_subplot(2,2,1)
ax.hist(NFILT,bins=arange(7)-.5)
ax.set_title("NFILT histogram")
ax=f.add_subplot(2,2,2)
ax.set_title("CHI_SQUARED vs ODDS (where M_0 defined)")
ax.hist2d(ODDS[M_0>0],CHI_SQUARED[M_0>0]) #logscale?
ax=f.add_subplot(2,2,3)
ax.set_title("T_B vs Z_B (where M_0 defined)")
ax.hist2d(Z_B[M_0>0],T_B[M_0>0]) #logscale?
ax=f.add_subplot(2,2,4)
ax.set_title("M_0 vs Z_B (where M_0 defined)")
ax.hist2d(Z_B[M_0>0],M_0[M_0>0]) #logscale?
show()

f=figure()
ax=f.add_subplot(2,2,1)
ax.hist(Z_B[M_0>0],bins=zbins)
ax.set_title("bpz Z_B hist (where M_0 defined)")
ax=f.add_subplot(2,2,2)
ax.set_title("bpz Z_B hist (where M_0 defined and ODDS>.95)")
ax.hist(Z_B[(M_0>0)*(ODDS>.95)],bins=zbins)
ax=f.add_subplot(2,2,3)
ax.hist(Z_B[(M_0>0)*(ODDS>.85)],bins=zbins)
ax.set_title("bpz Z_B hist (where M_0 defined and ODDS>.85)")
ax=f.add_subplot(2,2,4)
ax.set_title("bpz Z_B hist (where M_0 defined and NFILT==5)")
ax.hist(Z_B[(M_0>0)*(NFILT==5)],bins=zbins)
show()


## now get just the ones where M_0>0
acceptable=(M_0>0)*(NFILT==5)
id=zs[:,0][acceptable]
zb=zs[:,1][acceptable]
zb_min=zs[:,2][acceptable]
zb_max=zs[:,3][acceptable]
tb=zs[:,4][acceptable]
odds=zs[:,5][acceptable]
zml=zs[:,6][acceptable]
tml=zs[:,7][acceptable]
chi_squared=zs[:,8][acceptable]
m0=zs[:,9][acceptable]

## plotting bpz output
nfilt=NFILT[acceptable]
zrange=arange(.01,4,.01)
zz=numpy.around(Z_B[acceptable],2)
zbins=zrange-.005

f=figure(figsize=(12,10))
ax=f.add_subplot(2,2,1)
ax.set_title("NFILT histogram")
ax.hist(nfilt,bins=arange(7)-.5)
ax=f.add_subplot(2,2,2)
ax.set_title("CHI_SQUARED vs ODDS (where M_0 defined)")
ax.hist2d(odds,chi_squared) #logscale?
ax=f.add_subplot(2,2,3)
ax.set_title("T_B vs Z_B (where M_0 defined)")
ax.hist2d(zb,tb) #logscale?
ax=f.add_subplot(2,2,4)
ax.set_title("M_0 vs Z_B (where M_0 defined)")
ax.hist2d(zb,m0) #logscale?
f.tight_layout()
f.savefig("plt_bpz_hist1")

## new cuts on M_0 and NFILT
f=figure(figsize=(12,10))
f.suptitle("All datapoints are where M_0 is defined and NFILT=5")
ax=f.add_subplot(2,2,1)
ax.hist(zb,bins=zbins)
ax.set_title("bpz Z_B hist (where M_0 defined)")
ax=f.add_subplot(2,2,2)
ax.set_title("bpz Z_B hist (where M_0 defined and ODDS>.95)")
ax.hist(zb[odds>.95],bins=zbins)
ax=f.add_subplot(2,2,3)
ax.hist(zb[odds>.85],bins=zbins)
ax.set_title("bpz Z_B hist (where M_0 defined and ODDS>.85)")
ax=f.add_subplot(2,2,4)
ax.set_title("bpz Z_B hist (where M_0 defined and NFILT==5)")
ax.hist(zb[nfilt==5],bins=zbins)
f.tight_layout()
f.savefig("plt_bpz_hist2")
show()

## pca plots
plotit={}; keys=[]
plotit["zb"]=zb ; keys.append("zb")
plotit["zb_min"]=zb_min ; keys.append("zb_min")
plotit["zb_max"]=zb_max ; keys.append("zb_max")
plotit["tb"]=tb ; keys.append("tb")
plotit["odds"]=odds ; keys.append("odds")
plotit["zml"]=zml ; keys.append("zml")
plotit["tml"]=tml ; keys.append("tml")
plotit["chi_squared"]=chi_squared ; keys.append("chi_squared")
plotit["m0"]=m0 ; keys.append("m0")


zbins2=arange(.01,4,.02)-.01
tbins=arange(1,6.2,.111)-.01
obins=arange(0,1,.01)
chibins=arange(-3,3,.05)
m0bins=arange(18,35,.1)
f=figure(figsize=(12,10))
f,axes = imagetools.AxesList(fig=f,shape=(3,2))
bins_list=[zbins2,tbins, obins, zbins2, chibins, m0bins]
for bl in bins_list: print len(bl)
i=0; axes[i].hist(zs_pick[:,i],bins=zbins2) ; axes[i].set_title(keys_pick[i])
i=1; axes[i].hist(zs_pick[:,i],bins=tbins) ; axes[i].set_title(keys_pick[i])
i=2; axes[i].hist(zs_pick[:,i],bins=obins) ; axes[i].set_title(keys_pick[i])
i=3; axes[i].hist(zs_pick[:,i],bins=zbins2) ; axes[i].set_title(keys_pick[i])
i=4; axes[i].hist(zs_pick[:,i],bins=chibins) ; axes[i].set_title(keys_pick[i])
i=5; axes[i].hist(zs_pick[:,i],bins=m0bins) ; axes[i].set_title(keys_pick[i])
f.tight_layout()
f.savefig("plt_bpz_hist2")
show()

## use new hist2d func
zs_pick=zs[acceptable][:,1:][:,(0,3,4,5,7,8)].copy()
zs_pick[:,4]=numpy.log10(zs_pick[:,4])
df = pd.DataFrame(zs_pick,columns=keys_pick)
#plot_pick=scatter_matrix(df, alpha=0.2, figsize=(12, 10), diagonal='hist')
reload(adam_plot_mva)
import adam_plot_mva
hist2d_pick=adam_plot_mva.hist2d_matrix(df, bins=bins_list, figsize=(12, 10), diagonal='hist')



## new cuts on M_0 and NFILT
f=figure(figsize=(12,10))
f.suptitle("All datapoints are where M_0 is defined and NFILT=5")
ax=f.add_subplot(2,2,1)
ax.set_title("bpz Z_B hist")
ax.hist(zb,bins=zbins)
ax=f.add_subplot(2,2,2)
ax.set_title("bpz Z_B hist (where ODDS>.95)")
ax.hist(zb[odds>.95],bins=zbins)
ax=f.add_subplot(2,2,3)
ax.set_title("bpz Z_B hist (where ODDS>.85)")
ax.hist(zb[odds>.85],bins=zbins)
ax=f.add_subplot(2,2,4)
ax.set_title("bpz Z_B hist (where ODDS>.5)")
ax.hist(zb[odds>.5],bins=zbins)
f.tight_layout()
f.savefig("plt_bpz_Z_B_hist-cut_ODDS")


## new cuts on M_0 and NFILT
f=figure(figsize=(12,10))
f.suptitle("All datapoints are where M_0 is defined and NFILT=5")
ax=f.add_subplot(2,3,1)
ax.set_title("bpz Z_B hist (where M_0<29)")
ax.hist(zb[m0<29.],bins=zbins)
ax=f.add_subplot(2,3,2)
ax.set_title("bpz Z_B hist (where M_0<27)")
ax.hist(zb[m0<27.],bins=zbins)
ax=f.add_subplot(2,3,3)
ax.set_title("bpz Z_B hist (where M_0<25)")
ax.hist(zb[m0<25.],bins=zbins)
ax=f.add_subplot(2,3,4)
ax.set_title("bpz Z_B hist (where M_0<29 and ODDS>.85)")
ax.hist(zb[(m0<29)*(odds>.85)],bins=zbins)
ax=f.add_subplot(2,3,5)
ax.set_title("bpz Z_B hist (where M_0<27 and ODDS>.85)")
ax.hist(zb[(m0<27)*(odds>.85)],bins=zbins)
ax=f.add_subplot(2,3,6)
ax.set_title("bpz Z_B hist (where M_0<25 and ODDS>.85)")
ax.hist(zb[(m0<25)*(odds>.85)],bins=zbins)
f.tight_layout()
f.savefig("plt_bpz_Z_B_hist-cut_M_0")
