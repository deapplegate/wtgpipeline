#! /usr/bin/env python
#adam-example#ipython -i Plot_Light_Cutter.py /nfs/slac/g/ki/ki18/anja/SUBARU/10_2_DARK/DARK/DARK_*.fits
import pyfits
from matplotlib.pylab import *
import sys
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from fitter import Gauss
from UsefulTools import names, FromPick_data_true, FromPick_data_spots, GetMiddle, GetSpots_bins_values, ShortFileString
import imagetools
GetCCD=imagetools.GetCCD
Nsub_to_Npy=imagetools.Nsub_to_Npy
from mpl_toolkits.axes_grid1 import ImageGrid

files=imagetools.ArgCleaner()

# files in /u/ki/awright/data/2010-02-12_W-C-IC/DARK
files=imagetools.OrderFiles(files)
fl=files[0]
if 'DARK' in fl:
	lightbins=linspace(-15,15,150)
	xlims=-9,16
	darkmode=True
else:
	lightbins=linspace(0,2,200)
	xlims=.3,1.3
	darkmode=False

#set values
count_thresh=100
widen=0.0
#widen=.5
#####tag='10_2_DARK'
tag='10_3_DARK_newlims'

f=figure(figsize=(13,8.5))
uplims=zeros((10,))
lowlims=zeros((10,))
for fl in files:
	fit=pyfits.open(fl)
	data=fit[0].data
	CCDnum=GetCCD(fl)	
	npy=Nsub_to_Npy(CCDnum)
	ax=f.add_subplot(2,5,npy)
	light=data.reshape((-1,))
	x,bins,patch=hist(light,bins=lightbins,log=True)
	fitinst=Gauss(GetMiddle(bins),x,threshold=.001)
	xx,yy=fitinst.getfitline()
	plot(xx,yy,'green')
	sigma=fitinst.sigma
	mean=fitinst.mean
	title('CCD '+str(CCDnum)+' mean='+str(round(mean,2)))
	#lowlim=mean-5*sigma
	#uplim=mean+5*sigma
	#plot([lowlim,lowlim],[1,max(x)],'green')
	#plot([uplim,uplim],[1,max(x)],'green')
	countup=cumsum(x<count_thresh)
	counter=bincount(countup)
	start_spot=sum(counter[:counter.argmax()])+1
	end_spot=sum(counter[:counter.argmax()+1])
	lowlim=bins[start_spot]
	uplim=bins[end_spot]
	#compare uplim to 4 sigma
	sig5=mean+5*sigma
	plot([sig5,sig5],[1,max(x)],'orange')
	lowlims[CCDnum-1]=lowlim
	#uplims[CCDnum-1]=min(uplim,sig5) #this is for 10_2_DARK and 10_3_DARKestablished
	uplims[CCDnum-1]=max(uplim,sig5) #this is for 10_2_DARK_newlims
	if sig5 < uplim:
		text( sig5, max(x),'5sigma<uplim')
	plot([lowlim,lowlim],[1,max(x)],'r')
	plot([uplim,uplim],[1,max(x)],'r')
	Ncut=sum((light<lowlim)+(light>uplim))
	xlim(xlims[0],xlims[1])
	ylim(1,10**7)
	text(xlim()[0],10**6.7,'%cut='+str(round(100*Ncut/float(light.size),6)))
	fit.close()
	#now pick the spots for each one (see if there are flyers too)

line1and2='./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT '
middle=' DARK '

savefig('plt'+tag+'_ImageFitLimit_Hists')

#Plot the things to get an idea of limits
lims=zip(lowlims, uplims)
f=figure(figsize=(13,8.5))
suptitle('The BASE_WEIGHT Images')
for lim,fl in zip(lims,files):
	CCDnum=GetCCD(fl)
	npy=Nsub_to_Npy(CCDnum)
	fit=pyfits.open(fl)
	data=fit[0].data
	ax=f.add_subplot(2,5,npy)
	title('CCD '+str(CCDnum)+'\nlims: '+str(round(lim[0],2))+' '+str(round(lim[1],2)))
	bins=linspace(lim[0],lim[1],50) #append([-inf],linspace(lim[0],lim[1],50))
	hister=asarray(digitize(data.flatten(),bins=bins)-1,dtype='float32')
	hister[hister==-1]=nan
	hister[hister==len(bins)-1]=nan
	imshow(hister.reshape(data.shape),interpolation='nearest',origin='lower left')
	cbar=colorbar()
	cdn,cup=int(cbar.get_clim()[0]),int(cbar.get_clim()[1])
	if cdn<0:cdn=0
	cbar.set_ticks(range(cdn,cup+1,5))
	cbar.set_ticklabels([round(bins[i],2) for i in range(cdn,cup+1,5)])
	ax.set_yticklabels([]);ax.set_xticklabels([]);ax.set_xticks([]);ax.set_yticks([])
	fit.close()

savefig('plt'+tag+'_ImageFitLimit_CCDs')
#Now plot the limits
#lims=[(, ),
#(, ),
#(, ),
#(, ),
#(, ),
#(, ),
#(, ),
#(, ),
#(, ),
#(, )]
lims={}
#below are lims for 2011-01-06_W-S-Z+
lims['2011-01-06_W-S-Z+']=[(.585,.91 ),(.78,1.01 ),(.86,1.042 ),(.8,1.025 ),(.425, .95),(.405, .985),(.795, 1.05),(.86,1.07 ),(.63, .94),(.34, .93)]
#below are the limits for 2011-01-06_W-C-IC 
lims['2011-01-06_W-C-IC']=[(.58,.96),(.78,1.0),(.86,1.04 ),(.78,1.01 ),(.36,.94 ),(.55,1.03 ),(.85,1.05 ),(.90,1.07 ),(.65,.95 ),(.38,.92 )]
#below are the limits for 2010-04-15_W-S-I+
lims['2010-04-15_W-S-I+']=[(.5,.93),(.83,1.01),(.87, 1.05),(.82, 1.0),(.46, .97),(.45, 1.0),(.84, 1.04),(.89, 1.07),(.69, .95),(.49, .95)]
#below are the limits for 2010-04-15_W-S-G+
lims['2010-04-15_W-S-G+']=[(.46,.94 ), (.81,1.01 ), (.83, 1.06), (.8,1.03 ), (.43, .99), (.42, 1.01), (.82, 1.05), (.9, 1.1), (.68, .98), (.47, .98)]
#below are the limits for 2010-02-12_W-C-IC
lims['2010-02-12_W-C-IC']=[(.48,.91),(.82, 1.01),(.87, 1.05),(.82, 1.02),(.48, .97),(.43, .99),(.83, 1.05),(.89, 1.08),(.70, .99),(.5, .95)]
#below are the limits for 2010-02-12_W-C-RC
lims['2010-02-12_W-C-RC']=[(0.48, 0.91), (0.82, 1.01), (0.86, 1.06), (0.81, 1.022), (0.47, 1.01), (0.42, .99), (0.8, 1.05), (0.9, 1.09), (0.71, .97), (0.5, 0.95)]
#below are the limits for 2010-02-12_W-J-B
lims['2010-02-12_W-J-B']=[(0.47, 0.93), (0.81, 1.03), (0.84, 1.07), (0.73, 1.04), (0.45, 1.02), (0.41, 1.03), (0.78, 1.06), (0.85, 1.11), (0.69, 1.01),(0.5, 0.99)]
#below are the limits for 2010-02-12_W-J-V
lims['2010-02-12_W-J-V']=[(.49,.91),(.82, 1.02),(.85, 1.06),(.81, 1.02),(.47, .98),(.44, .99),(.85, 1.05), (.90, 1.10), (.72, 1.00), (.51, .97)]
#these are the uniform wide limits used for the 10_3 config
lims['WideLims']=zip(-.04+array([ 0.46 ,  0.78 ,  0.83 ,  0.73 ,  0.36 ,  0.405,  0.78 ,  0.85 ,0.63 ,  0.34 ]),.08+array([ 0.96,  1.03,  1.07,  1.04,  1.02,  1.03,  1.06,  1.11,  1.01,  0.99]))

if darkmode:
	dark_lims=zip(-widen+lowlims,widen+uplims)
	base_weight_lims=zip(-.04+array([ 0.46 ,  0.78 ,  0.83 ,  0.73 ,  0.36 ,  0.405,  0.78 ,  0.85 ,0.63 ,  0.34 ]),.08+array([ 0.96,  1.03,  1.07,  1.04,  1.02,  1.03,  1.06,  1.11,  1.01,  0.99])) #these are the uniform wide limits used for the 10_3 config
	base_weight_lims=zip(-.24+array([ 0.46 ,  0.78 ,  0.83 ,  0.73 ,  0.36 ,  0.405,  0.78 ,  0.85 ,0.63 ,  0.34 ]),.28+array([ 0.96,  1.03,  1.07,  1.04,  1.02,  1.03,  1.06,  1.11,  1.01,  0.99])) #going extra wide for 10_2 because this only matters if the cuts are too tight, and I don't feel like really caring about this
else:
	dark_lims=[(-1.73, 4.15), (-1.88, 4.6), (-1.88 ,4.9), (-1.88, 5.35), (-2.94, 5.95), (-1.88, 5.5), (-1.73, 4.75), (-2.04, 4.75), (-1.43, 4.6), (-1.58, 4.75)] #this is dark lims for 10_3
	base_weight_lims=zip(lowlims, uplims)

print 'lowlim highlim ccd#'
scalecheck=''
f=figure(figsize=(13,8.5))
#suptitle('Chips Cut Out Shown In Black')
for bwlim,fl,darklim in zip(base_weight_lims,files,dark_lims):
	if darkmode: lim=darklim 
	else: lim=bwlim
	CCDnum=GetCCD(fl)	
	npy=Nsub_to_Npy(CCDnum)
	fit=pyfits.open(fl)
	data=fit[0].data
	#ar=zeros(data.shape)
	endline3 = str(round(bwlim[0],2))+' '+str(round(bwlim[1],2))
	dark = str(round(darklim[0],2))+' '+str(round(darklim[1],2))
	end=' '+str(CCDnum)
	dn,up=lim[0],lim[1]
	toolow=data<dn
	toohigh=data>up
	cutout=toohigh+toolow
	ax=f.add_subplot(2,5,npy)
	imshow(cutout,cmap='Greys',interpolation='nearest',origin='lower left')
	ax.set_yticklabels([]);ax.set_xticklabels([]);ax.set_xticks([]);ax.set_yticks([])
	print line1and2+endline3+middle+dark+end
	scalecheck+= 'ds9 '+fl+' -scale limits '+str(round(lim[0],2))+' '+str(round(lim[0],2))+' -view layout vertical -geometry 650x1600 -zoom to fit &\n'
	scalecheck+= 'ds9 '+fl+' -scale limits '+str(round(lim[1],2))+' '+str(round(lim[1],2))+' -view layout vertical -geometry 650x1600 -zoom to fit &\n'
	fit.close()

print scalecheck

f.subplots_adjust(hspace=0, top=.99, right=.99, left=.01, bottom=.01)
f.subplots_adjust(wspace=-.2)

savefig('plt'+tag+'_FinalLimit_ds9')

f=figure(figsize=(13,8.5))
for bwlim,fl,darklim in zip(base_weight_lims,files,dark_lims):
	if darkmode: lim=darklim 
	else: lim=bwlim
	CCDnum=GetCCD(fl)	
	npy=Nsub_to_Npy(CCDnum)
	fit=pyfits.open(fl)
        data=fit[0].data
        lowlim,uplim=lim
        npy=Nsub_to_Npy(CCDnum)
        ax=f.add_subplot(2,5,npy)
        light=data.reshape((-1,))
        x,bins,patch=hist(light,bins=lightbins,log=True) ##may need limits changed (DARK=-15,15)
        title('CCD '+str(CCDnum))
        plot([lowlim,lowlim],[1,max(x)],'r')
        plot([uplim,uplim],[1,max(x)],'r')
        Ncut=sum((light<lowlim)+(light>uplim))
        xlim(xlims[0],xlims[1])
        ylim(1,10**7)
        text(xlim()[0],10**6.7,'%cut='+str(round(100*Ncut/float(light.size),6)))
	fit.close()
        #now pick the spots for each one (see if there are flyers too)

#f.subplots_adjust(hspace=0, top=.99, right=.99, left=.01, bottom=.01)
savefig('plt'+tag+'_FinalLimit_Hists')
