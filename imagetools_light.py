#! /usr/bin/env python
#adam-does# this has most of the generalized useful functions I've written since the start of grad school
#adam-use# use with anything and everything
#import pyfits
import astropy, astropy.io.fits as pyfits
from matplotlib.pyplot import *
from numpy import *
import itertools
import os
import sys
import shutil
import time
from glob import glob
import copy
from copy import deepcopy
import scipy
import scipy.stats
import scipy.ndimage
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
conn8=ones((3,3),dtype=bool)
namespace=globals()
fullsize=(24,13.625)
fullscreen=(24,13.625)
#adam-use# use tags like this `def func(inputs): #tag`. Here are the ones I'm currently using:
#	command: this function returns the output of a linux command
#	non-image: this function does non-image related stuff, and might be better off in UsefulTools
#	plotting: this function's main concern is plotting
#	potential: this function has the potential to be better/generalized/more useful
#	re-write: this function should be re-written (tools to use in it) or just generalized
#	short: this function is super short
#	use: I need to use this function more
#	useless: I'm not sure that this is useful at all!

import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def slices_cover_both(sl1,sl2): #non-image
	'''take two slices and return a slice that is big enough to encompass both of them'''
	stop1_1=int(sl1[1].stop)
	stop1_0=int(sl1[0].stop)
	start1_1=int(sl1[1].start)
	start1_0=int(sl1[0].start)
	stop2_1=int(sl2[1].stop)
	stop2_0=int(sl2[0].stop)
	start2_1=int(sl2[1].start)
	start2_0=int(sl2[0].start)
	#get final position
	start_1=min(start1_1,start2_1)
	start_0=min(start1_0,start2_0)
	stop_1=max(stop1_1,stop2_1)
	stop_0=max(stop1_0,stop2_0)
	return (slice(start_0,stop_0,None),slice(start_1,stop_1,None))

def slice_center_size(sl): #non-image
	stop1=int(sl[1].stop)
	stop0=int(sl[0].stop)
	start1=int(sl[1].start)
	start0=int(sl[0].start)
	size2=stop1-start1
	size1=stop0-start0
	middle2=(stop1+start1)/2
	middle1=(stop0+start0)/2
	size=(size1,size2)
	center=(middle1,middle2)
	return center,size

def slice_center(sl): #non-image
	stop1=int(sl[1].stop)
	stop0=int(sl[0].stop)
	start1=int(sl[1].start)
	start0=int(sl[0].start)
	middle2=(stop1+start1)/2
	middle1=(stop0+start0)/2
	center=(middle1,middle2)
	return center

def slice_size(sl): #non-image
	stop1=int(sl[1].stop)
	stop0=int(sl[0].stop)
	start1=int(sl[1].start)
	start0=int(sl[0].start)
	size2=stop1-start1
	size1=stop0-start0
	size=(size1,size2)
	return size

def slice_expand(sl,widen): #non-image
	stop1=int(sl[1].stop)+widen
	stop0=int(sl[0].stop)+widen
	start1=int(sl[1].start)-widen
	start0=int(sl[0].start)-widen
	if start1<0:start1=0
	if start0<0:start0=0
	return (slice(start0,stop0,None),slice(start1,stop1,None))

def slice_square(sl):
	width1=int(sl[1].stop)-int(sl[1].start)
	width0=int(sl[0].stop)-int(sl[0].start)
	width=max(width0,width1)
	return (slice(int(sl[0].start),int(sl[0].start)+width,None),slice(int(sl[1].start),int(sl[1].start)+width,None))

def GetCCD(fl):
	'''get the CCD #:
		input = files name
		output = int(CCDnum)'''
	if fl[-5:]=='.fits':
		flname=os.path.basename(fl)
		if flname.count('_')==1:
			flend=flname[flname.index('_')+1:-5]
			strnum=''
			for i in flend:
				try:
					strnum+=str(int(i))
				except ValueError:
					pass
			return int(strnum)
		elif flname.count('_')==0:
			#use pyfits to get CCD num from header file?
			#raise Exception("Need to generalize GetCCD to work with this file")
			print ("Need to generalize GetCCD to work with this file")
		else:
			#use pyfits to get CCD num from header file?
			#raise Exception("Need to generalize GetCCD to work with this file")
			print ("Need to generalize GetCCD to work with this file")
		print "returning meaningless CCDnum value"
		return nan
	else:
		raise Exception("Need to generalize GetCCD to work with this file")

def Nsub_to_Npy(Nsub):
	'''takes a CCD number and returns the value of the subplot number needed to plot the focal plane in matplotlib'''
	if Nsub>5:
		return Nsub-5
	elif Nsub<=5:
		return Nsub+5
	else:
		raise Exception("Nsub_to_Npy given bad Nsub")

def GetReads(image):
	'''Split the image into it's readout ports:
		input = image array
		output = 4 image arrays'''
	if image.shape==(4152,2016):
		read1=image[:,0:496]
		read2=image[:,496:1008]
		read3=image[:,1008:1520]
		read4=image[:,1520:2016]
		return (read1,read2,read3,read4)
	########elif image.shape==(4080,2000):
	########	print "10-2 configuration only has 1 readout per CCD, but we'll split it up as if it has 4 readout ports"
	########	read1=image[:,0:500]
	########	read2=image[:,500:1000]
	########	read3=image[:,1000:1500]
	########	read4=image[:,1500:2000]
	########	return (read1,read2,read3,read4)
	elif image.shape==(4080,2000):
		print "10-2 configuration only has 1 readout per CCD, and that's how I'm going to treat this"
		return [image]
	else:
		raise Exception("Need to change readout setup in order to work with this file")

def NthEntry2Pos(imageshape,N):
	'''takes the index number of an element of ar.flatten() and returns it's position in ar[(x,y)]''' 
	#if image.ndim!=2, then this won't work!!
	Nx,Ny=imageshape
	xx=N/Ny
	yy=N%Ny
	return (xx,yy)
		
def around(image,pt,levels):
	'''get region(s) a certain # of pixels (levels) around a given pt
	around(foo,pt,N) will return an array of size (2N+1,2N+1) and the pts corresponding to those corners'''
	return_list=[]
	try:
		for level in levels:
			pts=array([[-level+pt[0],level+1+pt[0]],[-level+pt[1],level+1+pt[1]]])
			x_up,y_up=image.shape
			if pts[0,0]<0:pts[0,0]=0
			if pts[0,1]>x_up:pts[0,1]=x_up
			if pts[1,0]<0:pts[1,0]=0
			if pts[1,1]>y_up:pts[1,1]=y_up
			patch=image[pts[0,0]:pts[0,1],pts[1,0]:pts[1,1]]
			return_list.append((patch,pts))
	except TypeError:
		pts=array([[-levels+pt[0],levels+1+pt[0]],[-levels+pt[1],levels+1+pt[1]]])
		x_up,y_up=image.shape
		if pts[0,0]<0:pts[0,0]=0
		if pts[0,1]>x_up:pts[0,1]=x_up
		if pts[1,0]<0:pts[1,0]=0
		if pts[1,1]>y_up:pts[1,1]=y_up
		patch=image[pts[0,0]:pts[0,1],pts[1,0]:pts[1,1]]
		return_list=(patch,pts)
	return return_list

#plot this using:
#imshow(r,vmin=CCDextrema[0],vmax=CCDextrema[1],interpolation='nearest',origin='lower left')
#plot([grid_pts[1,0],grid_pts[1,0],grid_pts[1,1],grid_pts[1,1],grid_pts[1,0]],[grid_pts[0,0],grid_pts[0,1],grid_pts[0,1],grid_pts[0,0],grid_pts[0,0]],'k-')
#scatter(GSpairs[:,1],GSpairs[:,0],c='k',marker='o',facecolor='none')

def points_around(imageshape,pt,level):
	'''similar to around(image,pt,level), but gives you all the pts around pt in a list'''
	pts=array([[-level+pt[0],level+1+pt[0]],[-level+pt[1],level+1+pt[1]]])
	x_up,y_up=imageshape
	if pts[0,0]<0:pts[0,0]=0
	if pts[0,1]>x_up:pts[0,1]=x_up
	if pts[1,0]<0:pts[1,0]=0
	if pts[1,1]>y_up:pts[1,1]=y_up
	xxx=range(pts[0][0],pts[0][1])
	yyy=range(pts[1][0],pts[1][1])
	return_list=list(itertools.product(xxx,yyy))
	return return_list

def totuple(ar):
	'''convert mutable object filled with mutable objects to tuples of tuples'''
	return tuple(tuple(i) for i in ar)

def listtuple(ar):
	'''convert mutable object filled with mutable objects to a list of tuples'''
	return [tuple(i) for i in ar]

def equalequal(A,B):
	'''how similar are the two arrays?'''
	A=GetImage(A)
	B=GetImage(B)
	if A is B:
		print "A is B"
		return True
	elif type(A)!=type(B):
		print "the types aren't event the same"
		print "type(A)=",type(A)
		print "type(B)=",type(B)
		try:
			A_ar=array(A)
			B_ar=array(B)
			if (A_ar==B_ar).all():
				print "try again after converting to an array!"
		except:pass
		return False	
	elif A.shape != B.shape:
		print "the shapes aren't event the same"
		print "A.shape=",A.shape
		print "B.shape=",B.shape
		return False
	else: print "they have the same shape"
	if isnan(A).all() or isnan(B).all():
		print "one or the other is all nans!"
		return "all nan arrays are stupid"
	eq=A==B
	A_eq=A[eq]
	B_eq=B[eq]
	A_not=A[logical_not(eq)]
	B_not=B[logical_not(eq)]
	Aflat=A.flatten()
	Bflat=B.flatten()
	if eq.all():
		print "(A==B).all()"
		return True
	elif (nan_to_num(A)==nan_to_num(B)).all():
		print "(nan_to_num(A)==nan_to_num(B)).all()"
		if (isnan(A)==isnan(B)).all():
			print "they are identical"
		else:
			print "isnan(A) is not equal to isnan(B), so you probably have 0's in one where there are nans in the other"
		return True
	elif isnan(A_not).all() or isnan(B_not).all():
		print "All the same except for the nans & at least one array has all nan values where the two are not equal (that is equal or nan)"
		print "sum(A)=",sum(A)
		print "sum(B)=",sum(B)
		return True
	elif (logical_or(isnan(Aflat),isnan(Bflat))+(Aflat==Bflat)).all():
		print "All the same except for the nans & BOTH have nan values & One has nan values where the other doesn't (kinda wierd)" 
		return "probably same image with different cuts"
	elif not eq.any():
		print "yeah, they are totally different"
		print "A=",A
		print "B=",B
		return False
	elif (A.T==B).all():
		print "A.T==B"
		return False
	elif (nan_to_num(A.T)==nan_to_num(B)).all():
		print "(nan_to_num(A.T)==nan_to_num(B)).all()"
		return False
	elif mean(eq)>.9:
		print "yeah, they are 90% the same, but still somehow different"
		print "A=",A
		print "B=",B
		return False
	else:
		print "They are at least 10% different\nnot A=B, not nonnan(A)=nonnan(B), not A.T=B, not nonnan(A.T)=nonnan(B)"
		return False

def get_center(imageshape):
	'''given an image shape, it gives the location of the images center pixel'''
	Nx,Ny=imageshape
	if Nx%2==0:
		XX=[Nx/2,Nx/2-1]
	else:
		XX=[Nx/2]
	if Ny%2==0:
		YY=[Ny/2,Ny/2-1]
	else:
		YY=[Ny/2]
	return XX,YY

def get_centerX(imageshape):
	'''given an image shape, it gives the X location of the images center column'''
	Nx,Ny=imageshape
	if Nx%2==0:
		XX=[Nx/2,Nx/2-1]
	else:
		XX=[Nx/2]
	return XX

def get_centerY(imageshape):
	'''given an image shape, it gives the Y location of the images center row'''
	Nx,Ny=imageshape
	if Ny%2==0:
		YY=[Ny/2,Ny/2-1]
	else:
		YY=[Ny/2]
	return YY


##############################splitter.py##################################
#splitter.py functions: factors(n) and splitter(ar,Vpieces,Hpieces)
def PickMiddle(fl,Vpieces,Hpieces):
	'''this takes the number of Vslices and Hslices you want to slice an image up into and returns the middle portion of the image chosen so that the array can be divided up evenly without any excess!'''
	ar=GetImage(fl)
	Xstart,Ystart=ar.shape
	coord_skip1=(Xstart % Vpieces)/2
	coord_skip2=(Ystart % Hpieces)/2
	return ar[coord_skip1:Xstart-coord_skip1,coord_skip2:Ystart-coord_skip2]

def factors(n): #non-image
	'''returns all of the factors of a number'''
	return set(reduce(list.__add__, 
		([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

def splitter(fl,Vpieces,Hpieces,PickMiddleOk=False):
	'''splits ar into NbyM pieces
	returns an array of split pieces and the indicies that match up with those positions in the origonal array.
	The corner values will give you the spots in your input array where the split pieces come from. For example:
		ar1=arange(4152*496).reshape(4152,496)
		x=ar1[:-2,:]
		#split this into 400 pieces i.e. 50 vertical cuts and 8 horizontal cuts
		splits,Xcorn,Ycorn=splitter(x,50,8)
		#now splits contains the 400 split pieces
		#say you find something in piece #390 that you want to change in the origonal array
		#you can find piece 390 within x by
		piece390=x[Xcorn[390][0]:Xcorn[390][1]+1,Ycorn[390][0]:Ycorn[390][1]+1]
		#changing piece390 won't change x and v.v.'''
	ar=GetImage(fl)
	Xstart,Ystart=ar.shape
	total_pieces=Hpieces*Vpieces
	try:
		Var=array(vsplit(ar,Vpieces))
	except ValueError:
		if PickMiddleOk:
			return splitter(PickMiddle(fl,Vpieces,Hpieces),Vpieces,Hpieces)
		raise ValueError,"sorry, but input # of vertical pieces (Vpieces="+str(Vpieces)+") isn't a factor of the input array's # of rows (ar.shape[0]="+str(Xstart)+")\nThis number leaves "+str(Xstart%Vpieces)+" remaining pieces\nconsider using one of the following factors:"+str(sort(list(factors(Xstart)))) 
	try:
		VHar=asarray(dsplit(Var,Hpieces))
	except ValueError:
		if PickMiddleOk:
			return splitter(PickMiddle(fl,Vpieces,Hpieces),Vpieces,Hpieces)
		raise ValueError,"sorry, but input # of vertical pieces (Hpieces="+str(Hpieces)+") isn't a factor of the input array's # of rows (ar.shape[1]="+str(Ystart)+")\nThis number leaves "+str(Ystart%Hpieces)+" remaining pieces\nconsider using one of the following factors:"+str(sort(list(factors(Ystart))))
	arX,arY=mgrid[:Xstart,:Ystart]
	VarX=array(vsplit(arX,Vpieces))
	VarY=array(vsplit(arY,Vpieces))
	VHar=VHar.reshape(total_pieces,Xstart/Vpieces,Ystart/Hpieces)
	VHarX=asarray(dsplit(VarX,Hpieces)).reshape(total_pieces,Xstart/Vpieces,Ystart/Hpieces)
	VHarY=asarray(dsplit(VarY,Hpieces)).reshape(total_pieces,Xstart/Vpieces,Ystart/Hpieces)
	Xmaxs=VHarX[:,-1,0]
	Xmins=VHarX[:,0,0]
	Ymaxs=VHarY[:,0,-1]
	Ymins=VHarY[:,0,0]
	Xcorners=zip(Xmins,Xmaxs)
	Ycorners=zip(Ymins,Ymaxs)
	return VHar,Xcorners,Ycorners

##############################RegionMaker.py##################################
#RegionMaker1pt1.py functions: HCcorner(im)
#	returns the array in the images hot and cold corner
#get hot and cold corners with HCcorner
xy=200
sizetotal=xy*xy
ar2couple=[(0,0),(0,1),(1,0),(1,1)]
spot2=array([[(0,1),(0,0)],[(1,1),(1,0)]],dtype=None)
cornernums496={(0,0):((-xy+4152,0+4152),(0,xy)),(0,1):((-xy+4152,0+4152),(-xy+496,0+496)),(1,0):((0,xy),(0,xy)),(1,1):((0,xy),(-xy+496,0+496))}
cornernums512={(0,0):((-xy+4152,0+4152),(0,xy)),(0,1):((-xy+4152,0+4152),(-xy+512,0+512)),(1,0):((0,xy),(0,xy)),(1,1):((0,xy),(-xy+512,0+512))}
cornernums10_2_split={(0,0):((-xy+4080,0+4080),(0,xy)),(0,1):((-xy+4080,0+4080),(-xy+500,0+500)),(1,0):((0,xy),(0,xy)),(1,1):((0,xy),(-xy+500,0+500))}
cornernums10_2={(0,0):((-xy+4080,0+4080),(0,xy)),(0,1):((-xy+4080,0+4080),(-xy+2000,0+2000)),(1,0):((0,xy),(0,xy)),(1,1):((0,xy),(-xy+2000,0+2000))}
cornernums={(4152, 496):cornernums496,(4152, 512):cornernums512,(4080, 500):cornernums10_2_split,(4080, 2000):cornernums10_2}
def HCcorner(read):
	corner=zeros((2, 2, xy, xy))
	cornerpairs=cornernums[read.shape]
	corner[0,0]=read[-xy:,:xy]
	corner[0,1]=read[-xy:,-xy:]
	corner[1,0]=read[:xy,:xy]
	corner[1,1]=read[:xy,-xy:]
	hc,cc=zeros((2,2)),zeros((2,2))
	# this is where the error was, I needed the copy in the next line!
	flatcorner=deepcopy(corner.reshape((2,2,sizetotal)))
	flatcorner.sort(axis=2)
	for couple in [(0,0),(1,0),(0,1),(1,1)]:
		hc[couple]=((flatcorner[couple])[(flatcorner[couple]>0.1)*(flatcorner[couple]<2.0)])[-(sizetotal)/8:-4].mean()
		cc[couple]=((flatcorner[couple])[(flatcorner[couple]>0.1)*(flatcorner[couple]<2.0)])[4:(sizetotal)/8].mean()
	hot1=ar2couple[hc.argmax()]
	cold1=ar2couple[cc.argmin()]
	hotmax=hc.max()
	coldmin=cc.min()
	Ccorner=corner[cold1]
	Hcorner=corner[hot1]
	return (cornerpairs[hot1],cornerpairs[cold1])
	##priority #2: if second hotest/coldest corner is close to the true hottest/coldest one, then define the corner to stretch all the way across the readout
	#hot2=tuple(spot2[hot1])
	#cold2=tuple(spot2[cold1])
	#hotnext=hc[hot2]
	#coldnext=cc[cold2]
	#if coldnext-coldmin<.005:
	#if hotmax-hotnext<.005:
	##priority #1: if there is something stupidly cold/hot in the cold/hot corner, then cut it out
	##sp=.1 #set separation parameter
	##toocold=(Ccorner<coldmin-sp)*(isnan(Ccorner)==False)
	##toohot=(Hcorner>hotmax+sp)*(isnan(Hcorner)==False)
	##if toocold.any():
	##      print "\ttoocold.sum()= ",toocold.sum()," for separation param sp=",sp
	##if toohot.any():
	##      print "\ttoohot.sum()= ",toohot.sum()," for separation param sp=",sp
	#return (Hcorner,cornerstrings[hot1]),(Ccorner,cornerstrings[cold1])

##############################PLC.py##################################
#PLC.py functions: get_PLClims(files,tolerance=(-0.01,.03)) and mask_compare_more_less(mm_files,lm_files,level=5)
def get_PLClims(files,tolerance=(-0.01,.03)): #re-write
	'''get's limits the way that Plot_Light_Cutter.py does'''
	sorted_files=range(10)
	for fl in files:
	    if "-i" in fl: continue
	    CCDnum=GetCCD(fl)
	    sorted_files[CCDnum-1]=fl
	files=sorted_files
	for fl in files:
		fit=pyfits.open(fl)
		data=fit[0].data
		CCDnum=GetCCD(fl)
		light=data.reshape((-1,))
		x,bins=histogram(light,bins=linspace(0,2,201)) ##may need limits changed (DARK=-15,15)
		countup=cumsum(x<10)
		counter=bincount(countup)
		start_spot=sum(counter[:counter.argmax()])+1
		end_spot=sum(counter[:counter.argmax()+1])
		lowlim=bins[start_spot]+tolerance[0]#add on tolenence
		uplim=bins[end_spot]+tolerance[1]
		uplims[CCDnum-1]=uplim
		lowlims[CCDnum-1]=lowlim
		Ncut=sum((light<lowlim)+(light>uplim))
		print '%cut='+str(round(100*Ncut/float(light.size),6))
	return zip(lowlims, uplims)

def mask_compare_more_less(mm_files,lm_files,level=5): #potential
	'''compares the masks of two different images, returns an array of regions around pts where things are masked in the more masked array and not masked in the less masked array'''
	mm_mask_spots={}
	lm_mask_spots={}
	mm_data={}
	lm_data={}
	for fl in mm_files:
		fit=pyfits.open(fl)
		data=fit[0].data
		CCDnum=GetCCD(fl)
		mm_data[CCDnum]=data
		masked=data==0
		mask_spots=transpose(nonzero(masked))
		mm_mask_spots[CCDnum]=set([tuple(pair) for pair in mask_spots])
		fit.close()
	for fl in lm_files:
		fit=pyfits.open(fl)
		data=fit[0].data
		CCDnum=GetCCD(fl)
		lm_data[CCDnum]=data
		masked=data==0
		mask_spots=transpose(nonzero(masked))
		lm_mask_spots[CCDnum]=set([tuple(pair) for pair in mask_spots])
		fit.close()
	MnotL={}
	LnotM={}
	for i in range(1,11):
		MnotL[i]=list(mm_mask_spots[i]-lm_mask_spots[i])
		LnotM[i]=list(lm_mask_spots[i]-mm_mask_spots[i])
	Nlnm=0
	Nmnl=0
	return_mm={}
	return_lm={}
	for i in range(1,11):
		Nlnm+=len(LnotM[i])
		Nmnl+=len(MnotL[i])
		#if MnotL[i]:
		return_mm[i]=[around(mm_data[i],mnl,level)[0] for mnl in MnotL[i]]
		return_lm[i]=[around(lm_data[i],mnl,level)[0] for mnl in MnotL[i]]
	print "Not Returned: There are "+str(Nlnm)+" pixels masked out in the images expected to have less masks that are not masked out in the images expected to have more masks (here high numbers are bad, can investigate this by flipping input order)"
	print "\nReturning: There are "+str(Nmnl)+" pixels masked out in the images expected to have more masks that are not masked out in the images expected to have less masks (here higher numbers are OK)"
	return return_mm,return_lm

##############################CompareTool.py##################################
#CompareTool.py functions: CompareTool(dir/file/file list) and ImageWithSpots(image)
def CompareTool(comp1,comp2,form="globalweight_",name1='Old',name2='New'): #potential
	''' This function takes two lists of files (or images) that you want to compare, and makes many side-by-side image plots comparing them using imagetools.ImageWithSpots'''
	if type(comp1) != type(comp2):
		print "input1 = ",comp1
		print "input2 = ",comp2
		raise Exception("Problem with input types not matching")
	if ('.' in comp1) != ('.' in comp2):
		print "input1 = ",comp1
		print "input2 = ",comp2
		raise Exception("Problem with one input having a . & one not")
	if type(comp1)==str and '.' not in comp1: #it's a dir
		if not os.path.isdir(comp1) or not os.path.isdir(comp2):
			print "input1 = ",comp1
			print "input2 = ",comp2
			raise Exception("These directories don't exist!")
		files1 = glob(comp1+form+'*.fits')
		files2 = glob(comp2+form+'*.fits')
		if len(files1)==10 and len(files2)==10:
			figs=[]
			for fl1,fl2 in zip(files1,files2):
				figs.append(ImageWithSpots([fl1,fl2],name1=name1,name2=name2))
			return figs
		else:
			print "input1 = ",comp1
			print "input2 = ",comp2
			raise Exception("Problem with not enough files or files not matching in glob()")
	elif type(comp1)==str and '.' in comp1: #it's a file
		if not os.path.isfile(comp1) or not os.path.isfile(comp2):
			print "input1 = ",comp1
			print "input2 = ",comp2
			raise Exception("These files don't exist!")
		return ImageWithSpots([comp1,comp2],name1=name1,name2=name2)
	elif type(comp1)==list: #it's a list of files
		for fl1,fl2 in zip(comp1,comp2):
			if not os.path.isfile(fl1) or not os.path.isfile(fl2):
				print "either one of the files, or both files don't exist"
				print "input1 problem element = ",fl1
				print "input2 problem element = ",fl2
				raise Exception("These files don't exist!")
		figs=[]
		for fl1,fl2 in zip(comp1,comp2):
			figs.append(ImageWithSpots([fl1,fl2],name1=name1,name2=name2))
		return figs

def ImageWithSpots(fls,Xspots=None,name1='image1',name2='image2',nameX='selected spots',mode='alpha',plotlim=None,window=None,ZeroToNan=0,ignore_scale=False,cutinfo=None):
	''' this function shows an image in locked step with a collection of boolian spots to mark certain pixels that should be paid attention to
		(1) if fls=image & Xspots=spots, then this function takes an image and some spots and plots them in locked mode
		(2) if fls=[image1,image2] & Xspots=spots, then this function takes both images and plots them in locked mode with the spots in the middle
		(3) if fls=[image1,image2] & Xspots=None, then this function takes both images and plots them in locked mode with Xspots marking the difference
		NOTE: (3) is totally equivalent to the old CompareImage function!
		mode is 'alpha', 'box', or 'o'
		window=((X low lim,X up lim),(Y low lim, Y up lim))
		ZeroToNan=(BOOL1,BOOL2) where BOOL determines if you want to plot it with 0 set to white'''
	#PlotImage(fl,Xspots=None,ax=None,plotlim=None,name='Input Image',mode='alpha',window=None,ZeroToNan=True,cbar=True):
	if plotlim:
		CCDextrema=plotlim
	elif ignore_scale:
		CCDextrema=None
	else:
		CCDextrema=FilesLimits([fls])
	two_fls_bool= type(fls)==list
	if two_fls_bool:
		fl1=fls[0]
		fl2=fls[1]
		#this should give the exact same behavior as CompareImage(fls[0],fls[1])
		if Xspots==None:
			print "Now in compare mode"
			im1=GetImage(fl1)
			im2=GetImage(fl2)
			Xspots=im1!=im2
			if not Xspots.any():
				print "Exactly the same!"
				return 0
			diffs=nonzero((im1!=im2))
			spot=diffs[0][0],diffs[1][0]
			print "im1[",spot,"]=",im1[spot]
			print "im2[",spot,"]=",im2[spot]
	else:
		fl1=fls
	NXs=sum(Xspots)
	print "there are",NXs,"# of pixels in Xspots"
	if NXs>50000:
		if mode in ['rect','Rectangle','rectangle','box','boxes']:
			print 'setting mode="o" since there are so many different points'
			mode='o'
	#do  stuff for file#1
	im1=GetImage(fl1)
	if window:
		xx,yy=window
		im1=im1[yy[0]:yy[1],xx[0]:xx[1]]
	image1=im1.copy()
	if ZeroToNan==True:
		try:
			image1[image1==0]=nan
		except ValueError:
			image1=asarray(image1,dtype=float32)
			image1[image1==0]=nan
	#do  stuff for file#2
	if two_fls_bool:
		im2=GetImage(fl2)
		if window:
			xx,yy=window
			im2=im2[yy[0]:yy[2],xx[0]:xx[2]]
			if (im1==im2).all():
				print "Globally different, but exactly the same within this window!"
				#return 0
		image2=im2.copy()
		if ZeroToNan==True:
			try:
				image2[image2==0]=nan
			except ValueError:
				image2=asarray(image2,dtype=float32)
				image2[image2==0]=nan
	if cutinfo:
		name1=name1+' fraction cut='+str(round(sum(isnan(image1))/float(image1.size),7))+'\n'+str(isnan(image1).sum())+' total pixels cut'
		name2=name2+' fraction cut='+str(round(sum(isnan(image2))/float(image2.size),7))+'\n'+str(isnan(image2).sum())+' total pixels cut'
	imshape=im1.shape
	fig=figure(figsize=(22,13.625))
	if two_fls_bool:
		ax1=fig.add_subplot(121)
		ax2=fig.add_subplot(122,sharex=ax1,sharey=ax1)
		fig=PlotImage(image2,Xspots=Xspots,ax=ax2,plotlim=CCDextrema,name=name2,ZeroToNan=0,cbar=False,mode=mode)
	else:
		ax1=fig.add_subplot(111)
	fig=PlotImage(image1,Xspots=Xspots,ax=ax1,plotlim=CCDextrema,name=name1,ZeroToNan=0,cbar=False,mode=mode)
	ax1.set_adjustable('box-forced')
	ax1.set_ylim(-.5,imshape[0]+.5);ax1.set_xlim(-.5,imshape[1]+.5)
	fig.tight_layout()
	fig.canvas.draw()
	box1=ax1.get_position()
	ax1.set_position(box1.translated(-.05,0))
	box1=ax1.get_position()
	axnew=fig.add_axes(box1.shrunk(.53,.6).translated(.4,.2),sharex=ax1,sharey=ax1)
	Xx,Xy=nonzero(Xspots)
	axnew.scatter(Xy,Xx,marker='o',facecolors='none',edgecolors='k')
	axnew.set_adjustable('box-forced')
	axnew.set_ylim(-.5,imshape[0]+.5);axnew.set_xlim(-.5,imshape[1]+.5)
	axnew.set_title(nameX)
	if two_fls_bool:
		ax2.set_adjustable('box-forced')
		ax2.set_ylim(-.5,imshape[0]+.5);ax2.set_xlim(-.5,imshape[1]+.5)
		box2=ax2.get_position()
		ax2.set_position(box2.translated(.07,0))
	fig.canvas.draw()
	#namespace.update(locals())
	return fig

def CompareImage(fl1,fl2,name1='Old',name2='New',mode='alpha',plotlim=None,window=None,ZeroToNan=(1,1),cutinfo=False):
	'''CompareImage isn't a function anymore! You should instead run ImageWithSpots'''
	print "CompareImage isn't a function anymore! You should instead run ImageWithSpots"
	fig=ImageWithSpots([fl1,fl2],name1=name1,name2=name2,mode=mode,plotlim=plotlim,window=window,ZeroToNan=ZeroToNan[0],cutinfo=cutinfo)
	return fig

def PlotLockedImages(fl1,fl2,name1='Old',name2='New',colorbar_same=False):
	'''plot these two files side-by-side and lock them so that when you zoom it'll zoom on both windows'''
	im1=GetImage(fl1)
	im2=GetImage(fl2)
	imshape=im1.shape
	vmin1=scipy.stats.scoreatpercentile(im1.flatten(),.1)
	vmin2=scipy.stats.scoreatpercentile(im2.flatten(),.1)
	vmax1=scipy.stats.scoreatpercentile(im1.flatten(),99.5)
	vmax2=scipy.stats.scoreatpercentile(im2.flatten(),99.5)
	if colorbar_same:
		vmin=min(vmin1,vmin2)
		vmax=max(vmax1,vmax2)
		(vmin1,vmin2)=(vmin,vmin)
		(vmax1,vmax2)=(vmax,vmax)
	fig=figure(figsize=(16,12))
	ax1=fig.add_subplot(1,2,1)
	title(name1)
	imshowed=ax1.imshow(im1,vmin=vmin1,vmax=vmax1,interpolation='nearest',origin='lower left')
	colbar=colorbar(imshowed,ax=ax1)
	ax1.set_adjustable('box-forced')
	ax1.set_ylim(-.5,imshape[0]+.5);ax1.set_xlim(-.5,imshape[1]+.5)
	fig.tight_layout()
	fig.canvas.draw()
	box1=ax1.get_position()
	ax1.set_position(box1.translated(-.05,0))
	box1=ax1.get_position()
	#plot next image                                                                                                                                                                                                                                                                                                                     
	ax2=fig.add_subplot(1,2,2,sharex=ax1,sharey=ax1)
	title(name2)
	imshowed=ax2.imshow(im2,vmin=vmin2,vmax=vmax2,interpolation='nearest',origin='lower left')
	colbar=colorbar(imshowed,ax=ax2)
	ax2.set_adjustable('box-forced')
	ax2.set_ylim(-.5,imshape[0]+.5);ax2.set_xlim(-.5,imshape[1]+.5)
	box2=ax2.get_position()
	ax2.set_position(box2.translated(.07,0))
	return fig,ax1,ax2

def PlotImage(fl,Xspots=None,ax=None,plotlim=None,name='Input Image',mode='alpha',window=None,ZeroToNan=True,cbar=True):
	''' This function takes a file or image and plots it with either boxes or alpha differences over the points in Xspots
		mode is 'alpha', 'box', or 'o'
		window=((X low lim,X up lim),(Y low lim, Y up lim))
		ZeroToNan=BOOL #determines if you want to plot it with 0 set to white'''
	im=GetImage(fl)
	if not plotlim:
		plotlim=ImageLimits(fl,delta=.001)
		print "Set Plot Limits to Extrema: ",plotlim
	if window:
		xx,yy=window
		im=im[yy[0]:yy[1],xx[0]:xx[1]]
	if not ax:
		fig=figure(figsize=(10,15))
		ax=fig.add_subplot(1,1,1)
	else:
		fig=ax.figure
	image=im.copy()
	if ZeroToNan:image[image==0]=nan
	ax.set_title(name+'\nfraction cut='+str(round(sum(isnan(image))/float(image.size),7))+' of '+str(isnan(image).sum())+' total pixels cut ')
	#SIMPLE_RECTS: if this isn't working well enough, then consider trying to get BETTER_RECTS to work (below)
	if not (Xspots is None):
		if mode in ['circles','o','circle']:
			Xx,Xy=nonzero(Xspots)
			ax.scatter(Xy,Xx,edgecolors='k',facecolors='None')
			imshowed=ax.imshow(image,vmin=plotlim[0],vmax=plotlim[1],interpolation='nearest',origin='lower left')
		if mode in ['rect','Rectangle','rectangle','box','boxes']:
			Xx,Xy=nonzero(Xspots)
			for x,y in zip(Xx,Xy):
				#txt=ax.text(y,x,'X',color='w',alpha=.5)
				rect=Rectangle((y-.5,x-.5),1,1,axes=ax,color='k',fill=False,ec='k')
				ax.add_patch(rect)
			imshowed=ax.imshow(image,vmin=plotlim[0],vmax=plotlim[1],interpolation='nearest',origin='lower left')
		if mode in ['alpha','Alpha']:
			my_norm = matplotlib.colors.Normalize(vmin=plotlim[0],vmax=plotlim[1])
			my_cmap = copy.copy(cm.get_cmap('jet'))
			c_data= my_cmap(my_norm(image)) #RGBA
			c_data[:, :, 3] = .8 # make everything half alpha
			c_data[Xspots, 3] = 1 # reset the marked pixels as full opacity
			#plot them
			extent=[0,image.shape[1],0,image.shape[0]]
			imshowed=ax.imshow(c_data,extent=extent, interpolation='nearest',origin='lower left',norm=my_norm)
			#imshowed=ax.imshow(image,vmin=plotlim[0],vmax=plotlim[1],interpolation='nearest',origin='lower left')
		if cbar: colbar=colorbar(imshowed,ax=ax)
	else:
		imshowed=ax.imshow(image,vmin=plotlim[0],vmax=plotlim[1],interpolation='nearest',origin='lower left')
		if cbar: colbar=colorbar(imshowed,ax=ax)
	return fig
	#BETTER_RECTS
	#if 0<Xspots.sum()<1000:
	#	Xx,Xy=nonzero(Xspots)
	#	for x,y in zip(Xx,Xy):
	#		print x,y
	#		rect=Rectangle((y-.5,x-.5),1,1,color='w',ec='w',fill=False)
	#		ax1.add_patch(rect)
	#		ax2.add_patch(rect)
	#elif 1000<Xspots.sum():
	#	xs=Xspots.copy()
	#	labels,Nlabel=scipy.ndimage.label(Xspots)
	#	slices = scipy.ndimage.find_objects(labels)
	#	for lab in range(1,Nlabel+1):
	#		sl=slices[lab-1]
	#		FracInSlice=(labels[sl]==lab).mean()
	#		if FracInSlice>.75:
	#			Center,Size=slice_center_size(sl)
	#			x,y=int(sl[0].start),int(sl[1].start)
	#			rect=Rectangle((y-.5,x-.5),Size[1],Size[0],color='w',fill=False,ec='w')
	#			ax1.add_patch(rect)
	#			ax2.add_patch(rect)
	#			Xspots[sl]=False
	#	Xx,Xy=nonzero(Xspots)
	#	for x,y in zip(Xx,Xy):
	#		rect=Rectangle((y-.5,x-.5),1,1,color='w',fill=False,ec='w')
	#		ax1.add_patch(rect)
	#		ax2.add_patch(rect)

##################post-RegionMaker era (July 2013 or later)################################
def ImageLimits(flOar,delta=0.001):
	''' this takes a file (or an array), and returns the limiting values in the image'''
	im=GetImage(flOar)
	MASKED=(im[isfinite(im)]>=0.0).all()
	if MASKED:
		#if lower bound of the image is 0, then assume 0 indicates a WEIGHT=0 (masked pixel)
		CCDextrema=[im[im>0.0].min()*(1-delta),im[isfinite(im)].max()*(1+delta)]
	else: 
		#if there are negative values, we assume there are no weights
		CCDextrema=[im[isfinite(im)].min()*(1-delta),im[isfinite(im)].max()*(1+delta)]
	if isnan(im).any():
		print "there are "+str(sum(isnan(im)))+" nans in image which are ignored"
	if CCDextrema[0]<0:
		CCDextrema[0]*=(1+delta)/(1-delta)
	return CCDextrema

def OrderFiles(files): #re-write #useless
	'''orders files in increasing order of CCD number'''
	sorted_files=range(10)
	for fl in files:
		if (not '.fits' in fl) and (not '.reg' in fl):
			raise Exception("Input "+fl+" isn't a fits file or a region file!")
		elif fl=="-i":continue
		else:
			CCDnum=GetCCD(fl)
			sorted_files[CCDnum-1]=fl
	return sorted_files

def MaskMiddles(image,corners=1):
	self_ar=array([[0,0,0],[0,1,0],[0,0,0]],dtype=bool)
	image_nans=isnan(image)
	hom=zeros(image_nans.shape,dtype=bool)
	if corners:
		for corner in [(0,0),(0,-1),(-1,0),(-1,-1)]:
			hit_corner=zeros((3,3),dtype=bool)
			hit_corner[corner]=1
			hit=scipy.ndimage.morphology.binary_dilation(hit_corner,conn4)
			hom+=scipy.ndimage.morphology.binary_hit_or_miss(image_nans, structure1=hit, structure2=self_ar)
	LandR=array([[0,0,0],[1,0,1],[0,0,0]],dtype=bool)
	UandD=LandR.T
	hom+=scipy.ndimage.morphology.binary_hit_or_miss(image_nans, structure1=LandR, structure2=logical_not(LandR))
	hom+=scipy.ndimage.morphology.binary_hit_or_miss(image_nans, structure1=UandD, structure2=logical_not(UandD))
	image[hom]=nan
	return image

def FilesLimits(files,delta=.001):
	'''This takes a list of files, and gives you the limits to use for vmin and vmax in plotting those files together'''
	mins,maxs=[],[]
	for fl in files:
		minmin,maxmax=ImageLimits(fl,delta=delta)
		mins.append(minmin)
		maxs.append(maxmax)
	#try:
	#	for fl in files:
	#		minmin,maxmax=ImageLimits(fl,delta=delta)
	#		mins.append(minmin)
	#		maxs.append(maxmax)
	#except Exception:
	#	#it was given a file, not a list of files!
	#	print "WARNING: Don't Use imagetools.FilesLimits for this! Use imagetools.ImageLimits"
	#	fl=files
	#	minmin,maxmax=ImageLimits(fl,delta=delta)
	#	mins.append(minmin)
	#	maxs.append(maxmax)
	return (min(mins),max(maxs))

def FilesHists(files,shape=(4,4),title=None,lims=None,Nbins=201): #use #re-write (ImageHist, generalize) #potential
	'''This takes a list of files, and plots histograms of those files together'''
	if not lims:
		lims=FilesLimits(files)
	bins=linspace(lims[0],lims[1],Nbins)
	fig=figure(figsize=(20,15))
	fig.subplots_adjust(hspace=.2,wspace=.2,right=.97,top=.97, bottom=.03, left=.03)
	if title: fig.suptitle(title)
	size=shape[0]*shape[1]
	if size>len(files):
		print "more files than plotting size alotted, so I'm taking only ",size," of possible ",len(files)
	files=files[:size]
	for num,fl in enumerate(files):
		fit=pyfits.open(fl)
		data=fit[0].data
		#CCDnum=GetCCD(fl)
		light=data.reshape((-1,))
		ax=fig.add_subplot(shape[0],shape[1],num+1)
		x,bins,patches=hist(light,bins=bins,log=True)
		ax.set_xlim(lims[0],lims[1])
	return fig

def GetImage(flOar):
	'''This takes a file, and returns the image from the fits file. If you give it an array, it assumes that is the image and just returns the argument'''
	#if type(flOar)==str and os.path.isfile(flOar):
	try:
		fitfl=pyfits.open(flOar)
		im=fitfl[0].data
		fitfl.close()
	except:
		if type(flOar)==ndarray:
			im=flOar	
		elif type(flOar)==ma.core.MaskedArray:
			im=flOar	
		elif type(flOar)==list:
			im=array(flOar)	
		else:
			print "input = ",flOar
			raise Exception("Cannot get an image from this input!")
	return im

def variance_estimate(data,err,mean=None,nfitpars=0): #simple #step3_run_fit
    if mean==None:
	    d = 0
	    w = 0
	    for i in xrange(len(data)):
		w += 1/err[i]**2.
		d += data[i]/err[i]**2.
	    mean = d/w

    w = 0
    d = 0
    for i in xrange(len(data)):
        w += 1/err[i]**2.
        d += 1/err[i]**2.*(data[i] - mean)**2.

    weight_variance = d/w
    variance = scipy.var(data)

    n = 0
    d = 0
    for i in xrange(len(data)):
        n += 1.
        d += ((data[i] - mean)/err[i])**2.

    ''' this is not quite right '''
    redchi = d/(n-nfitpars)
    print 'variance_estimate| variance=',variance , ' weight_variance=',weight_variance , ' redchi=',redchi
    return variance, weight_variance, redchi


def Hist_Overflow(data,bins,ax=None,**kwargs):
	'''this will plot a histogram with a hatched overflow bin'''
	if not bins[-1]==inf:
		bins=append(bins,[inf])
	if not ax:
		f=figure(**kwargs)
		ax=f.add_subplot(111)
	x,bins,patches=ax.hist(data,bins=bins,**kwargs)
	ax.bar(left=bins[-2],height=x[-1],width=bins[2]-bins[1],fc='b',ec='w',hatch='\\\\\\\\\\',label='overflow')
	ax.set_xlim(bins[0],bins[-2]+(bins[2]-bins[1]))
	yd,yu=ax.get_ylim()
	xd,xu=ax.get_xlim()
	if kwargs.has_key('log'):
		ytxt=.7*(log10(yd)+log10(yu))
	else:
		ytxt=.7*(yd+yu)
	width=(bins[2]-bins[1])
	over=x[-1]
	meanmean=data.mean()
	minmin=data.min()
	maxmax=data.max()
	if type(minmin)==float: printit='min/max = '+str(round(minmin,2))+'/'+str(round(maxmax,2))+'\nmean = '+str(round(meanmean,2))
	else: printit='min/max = '+str(minmin)+'/'+str(maxmax)+'\nmean = '+str(meanmean)
	#if over>0 and over<5:
	#	overpts=data[data>bins[-2]]
	#	printit+='\n'+str(over)+' overflow points:'
	#	for overpt in overpts: printit+='\n'+str(overpt)
	#	ax.text(bins[0]+width,ytxt,printit)
	#else:
	#	ax.text(bins[0]+width,ytxt,printit)
	ax.text(xd+(xu-xd)*.2,ytxt,printit)
	return ax

def AxesCompact(fig,compact=.1): #plotting
	''' take fig and divide it up into a bunch of axes, then return the figure and the list of axes.
	Ex: fig,axes = imagetools.AxesList(fig=fig,shape=(2,5))'''
	small=compact
	big=1-compact
	fig.subplots_adjust(left=small,bottom=small,top=big,right=big)
	fig.canvas.draw()
	return fig

def AxesList(fig,shape,compact=False,**kwargs): #plotting
	''' take fig and divide it up into a bunch of axes, then return the figure and the list of axes.
	Ex: fig,axes = imagetools.AxesList(fig=fig,shape=(2,5))'''
	if compact != False:
		small=compact
		big=1-compact
		fig.subplots_adjust(left=small,bottom=small,top=big,right=big)
	for key in kwargs.keys():
		if key in 'left bottom right top wspace hspace':
			exec "fig.subplots_adjust("+key+"=kwargs[key])"
	size=shape[0]*shape[1]
	axes=[]
	for i in range(size):
		axes.append(fig.add_subplot(shape[0],shape[1],i+1))
	return fig,axes

def AxesSameLims(fig,axes=False,compact=False,**kwargs): #plotting
	'''take fig and make axes limits match'''
	fig.canvas.draw()
	if not axes:
		axes=fig.get_axes()
	for key in kwargs.keys():
		if key in 'left bottom right top wspace hspace':
			fig.subplots_adjust(key=kwargs[key])
	yUPlims=[]
	yDNlims=[]
	xUPlims=[]
	xDNlims=[]
	for ax in axes:
		xd,xu=ax.get_xlim()
		yd,yu=ax.get_ylim()
		xUPlims.append(xu)
		yUPlims.append(yu)
		xDNlims.append(xd)
		yDNlims.append(yd)
	xDN=min(xDNlims)
	yDN=min(yDNlims)
	xUP=max(xUPlims)
	yUP=max(yUPlims)
	for ax in axes:
		ax.set_xlim(xDN,xUP)
		ax.set_ylim(yDN,yUP)
	if compact != False:
		fig.canvas.draw()
		small=compact
		big=1-compact
		fig.subplots_adjust(left=small,bottom=small,top=big,right=big)
		fig.subplots_adjust(hspace=small,wspace=small)
		(xN,yN,N) = axes[0].get_geometry()
		N=xN*yN
		xx=zeros((xN,yN),dtype=bool)
		yy=zeros((xN,yN),dtype=bool)
		yy[:,0]=1
		xx[-1,:]=1
		axesN = arange(N).reshape(xN,yN)
		noYlabel=axesN[logical_not(yy)]
		noXlabel=axesN[logical_not(xx)]
		for yn in noYlabel:
			axes[yn].set_yticklabels([])
		for xn in noXlabel:
			axes[xn].set_xticklabels([])
		Ylabel=axesN[yy]
		Xlabel=axesN[xx]
		for yn in Ylabel:
			#axes[yn].set_yticklabels(axes[yn].get_yticklabels()[:-1])
			ax=axes[yn]
			ytl = ax.get_yticklabels()
			labels=[yt.get_text() for yt in ytl]
			labels[-1]=''
			ax.set_yticklabels(labels)
		for xn in Xlabel:
			#axes[xn].set_xticklabels(axes[xn].get_yticklabels()[:-1])
			ax=axes[xn]
			xtl = ax.get_xticklabels()
			labels=[xt.get_text() for xt in xtl]
			labels[-1]=''
			ax.set_xticklabels(labels)
	fig.canvas.draw()
	return fig

def AxesSameColors(fig,axes=None,lims=None,cbar_ax_pos=[0.96, 0.05, 0.01, 0.9],**kwargs): #plotting
	'''take fig and make color axes limits match. This will change the **colors** and the **colorbars**, so that the colors and colorbars will both be correct!
		if set `lims=(down,up)` in the inputs, then you specify limits, otherwise the limits are chosen from the extrema of the existing colorbars
		cbar_ax_pos=[*left*, *bottom*, *width*,*height*]
		if you don't want a colorbar, then cbar_ax_pos=False'''
	fig.canvas.draw()
	try:
		if not axes:
			axes=fig.get_axes()
		if not lims:
			UPlims=[]
			DNlims=[]
			for ax in axes:
				for im in ax.get_images():
					d,u=im.get_clim()
					UPlims.append(u)
					DNlims.append(d)
			DN=min(DNlims)
			UP=max(UPlims)
		else:
			DN,UP=lims
		for ax in axes:
			for im in ax.get_images():
				im.set_clim(DN,UP)
		if cbar_ax_pos:
			make_room=cbar_ax_pos[0]
			fig.subplots_adjust(right=make_room+.005)
			cbar_ax=fig.add_axes(cbar_ax_pos)
			fig.colorbar(im,cax=cbar_ax)
		fig.canvas.draw()
		return fig
	except:
		namespace.update(locals())
		raise

def AxesStripText(fig,axes=False,labels=True,titles=True,allticks=True,alllabels=False,alltitles=False,**kwargs): #plotting
	fig.canvas.draw()
	if not axes:
		axes=fig.get_axes()
	for ax in axes:
		#ax.set_title('')
		if allticks:
			numXL=len(ax.get_xticklabels())
			ax.set_xticklabels(['']*numXL)
			numyL=len(ax.get_yticklabels())
			ax.set_yticklabels(['']*numyL)
		if alllabels:
			try:
				ax.set_xlabel('')
			except AttributeError:pass
			try:
				ax.set_ylabel('')
			except AttributeError:pass
		elif labels:
			try:
				if ax.is_last_row(): pass
				else:ax.set_xlabel('')
			except AttributeError:pass
			try:
				if ax.is_first_col(): pass
				else:ax.set_ylabel('')
			except AttributeError:pass
		if alltitles:
			ax.set_title('')
		elif titles:
			try:
				if ax.is_first_row(): pass
				else:ax.set_title('')
			except AttributeError:pass
	fig.canvas.draw()
	return fig

def AxesRowColumn(fig,rows,columns,axes=False,**kwargs): #plotting
	'''take fig and make color axes limits match. This will change the **colors** and the **colorbars**, so that the colors and colorbars will both be correct!'''
	fig.canvas.draw()
	if not axes:
		axes=fig.get_axes()
	try:
		rcount=0
		ccount=0
		for ax in axes:
			if ax.is_first_row(): #col
				title=ax.get_title()
				if title: ax.set_title(columns[ccount]+'\n'+title)
				else: ax.set_title(columns[ccount])
				ccount+=1
			if ax.is_first_col(): #row
				yl=ax.get_ylabel()
				ax.set_ylabel(rows[rcount]+'\n'+yl)
				if yl: ax.set_ylabel(rows[rcount]+'\n'+yl)
				else: ax.set_ylabel(rows[rcount])
				rcount+=1
		##fig.text(x,y,s)
		fig.canvas.draw()
		return fig
	except:
		namespace.update(locals())
		raise

def imstats_params(fl,dictout=False): #command
	'''this function returns the statistics given by the `imstats` command
	i.e. the mode, lquartile, median, uquartile, mean, sigma
	it is totally equivalent to the following BASH command:
	imstats  ${fl} | tail -1 | awk {print $2, $3, $4, $5, $6, $7}'''
	p1=Popen(["imstats",fl],stdout=PIPE)
	p2=Popen(["tail","-1"],stdin=p1.stdout,stdout=PIPE)
	p1.stdout.close()
	p3=Popen(["awk", "{print $2, $3, $4, $5, $6, $7}"],stdin=p2.stdout,stdout=PIPE)
	p2.stdout.close()
	output=p3.communicate()[0]
	outputs=output.split(' ')
	mode, lquartile, median, uquartile, mean, sigma = (float(param) for param in outputs)
	if dictout:
		imstats={}
		imstats['mode']=mode
		imstats['lquartile']=lquartile
		imstats['median']=median
		imstats['uquartile']=uquartile
		imstats['mean']=mean
		imstats['sigma']=sigma
		return imstats
	return mode, lquartile, median, uquartile, mean, sigma

def sextractor_RMS(fl,getback=False):#command
	'''this function returns the statistics given by the `sextractor` command
	i.e. the background and the RMS.'''
	tmpfl="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/"+os.path.basename(fl)[:-5]+".log"
	cosmic_fl="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/cosmic%s.cat" % (id_generator(10),)
	print "**REMINDER** for now I'm using the theli version of sextractor (2.2.2) rather than the default (2.8.6) since it gives sensible values of FWHM!"
	sex_command="/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/sex_theli"
	os.system( sex_command+" -c /u/ki/awright/InstallingSoftware/pythons/sextractimtools/config-sex.imagetools %s -CATALOG_NAME %s > %s 2>&1" % (fl,cosmic_fl,tmpfl))
	os.system("rm "+cosmic_fl)
	flstr=open(tmpfl,'r').readlines()
	for line in flstr:
		if 'RMS' in line:
			rmsline = line
			break
	vals=rmsline.split(' ')
	rmsind=1+vals.index('RMS:')
	RMS=float(vals[rmsind])
	backind=1+vals.index('Background:')
	back=float(vals[backind])
	os.system( "rm -r "+tmpfl)
	if getback:
		backind=1+vals.index('Background:')
		back=float(vals[backind])
		return RMS,back
	return RMS

def get_seeing(fl):#command
	'''uses ~/bonnpipeline/get_seeing.sh to get the seeing of the image'''
	p1 = Popen(['/u/ki/awright/bonnpipeline/get_seeing.sh',fl], stdout=PIPE)
	out,err= p1.communicate()
	splitout=out.split('\n')
	seeing=float(splitout[-2])
	return seeing

def ftstat_params(fl,dictout=False):#command
	'''this function returns the statistics given by the `ftstat` command
	i.e. the mean, median, mode, sigma (and also lquartile & uquartile if dictout=True)'''
	p1 = Popen(['ftstat',fl,'centroid=NO','clip=YES'], stdout=PIPE)
	out,err=p1.communicate()
	pieces=out.split('\n')
	params=[]
	for piece in pieces[2:-1]:
		params.append([p for p in piece.split('  ') if len(p)>0])
	ftstatdict={}
	for i,(key,val) in enumerate(params):
		if key.startswith(' '): key=key[1:-1]
		else: key=key[:-1]
		if 'minimum' in key:
			mainkey='minimum'
			ftstatdict[mainkey]={}
			ftstatdict[mainkey]['value']=float(val)
		elif 'maximum' in key:
			mainkey='maximum'
			ftstatdict[mainkey]={}
			ftstatdict[mainkey]['value']=float(val)
		elif 'coord' in key:
			x,y=val[1:-1].split(',')
			ftstatdict[mainkey][key]=(float(x),float(y))
		else:
			try:
				ftstatdict[key]=float(val)
			except ValueError:
				ftstatdict[key]=val
	if not ftstatdict['cnvrgd']=='YES':
		print "WARNING: ftstat didn't converge!\n"*100
		print "ftstatdict['cnvrgd'] is ",ftstatdict['cnvrgd']
	if dictout:
		return ftstatdict
	else:
		return ftstatdict['mean'],ftstatdict['median'],ftstatdict['mode'],ftstatdict['sigma']

def Array2Bins(fl,Nbins=False,use_iterbins=False): #plotting
	'''Takes an array/file/image and gives the bins you would want to use to make a histogram of it
		default is to use max/min values as the limits
		it's probably most useful if I use mode with use_iterbins=True'''
	ar=GetImage(fl)
	if use_iterbins:
		minmin,maxmax=iterbins(ar)
	else:
		minmin=ar.min()
		maxmax=ar.max()
	if Nbins:
		bins=linspace(minmin,maxmax,Nbins)
	elif ar.dtype==int:
		#bins go from minmin-.5 to maxmax+.5 in increments of 1
		bins=arange(minmin,maxmax+2)-.5
	return bins
		
def percent2index(sortedarray, per): #short
	return int(len(sortedarray)*per/100.0)

def iterbins(fl,fraction_include_thresh=.000005,saturated=55000):
	'''this function takes in a file/image and iteratively determines which bins would be appropriate so that when you plot a histogram of the light, you can see **almost** the whole range. It excludes only the obvious fliers
		Side-By-Side Comparison Showing How Much Better iterbins are!
		Old Way (for image with notable flyers) is totally biased based on the # of bins
		# sigma Nbins=8001  :  292.942701113
		# sigma Nbins=10001  :  243.869131599
		# sigma Nbins=20001  :  193.104727249
		# sigma Nbins=100001  :  49.7097924538
		# sigma Nbins=300001  :  42.9327726654
		iterative Way doesn't change with the # of bins! (and it works with 500 bins, Old way needs 16x that!)
		# sigma iterbins Nbins=501  :  41.9149462622
		# sigma iterbins Nbins=1001  :  41.7465894109
		# sigma iterbins Nbins=3001  :  41.6943142403
		# sigma iterbins Nbins=10001  :  41.6885617137
		# sigma iterbins Nbins=100001  :  41.6880926952'''
	data=GetImage(fl)
	light=data.flatten()
	#if I don't want a saturation cut, then set saturation=inf (setting saturation=False is interpreted as saturation=0)
	light = light[light<saturated] #saturated = 55000 for 10_3 config, for 10_2 it's either 27000 or 30000
	light.sort()
	#percent2index = lambda arlen,per: int(arlen*per/100.0)
	#start out cutting 1%
	percent_clip=1
	cliplight = light[percent2index(light,percent_clip):percent2index(light,100-percent_clip)]
	cliplow = light[:percent2index(light,percent_clip)]
	cliphigh = light[percent2index(light,100-percent_clip):]
	lowscore=scipy.stats.scoreatpercentile(light,percent_clip)
	highscore=scipy.stats.scoreatpercentile(light,100-percent_clip)
	try:
		gauss_mean,gauss_sigma = ImageMeanSigma(cliplight,Nbins=501,use_iterbins=False,use_iterbins_if_needed=False)
	except IndexError:
		print "**   iterbins   ** iterbins tried and failed to run ImageMeanSigma now we're going to try again with finer bins. "
		gauss_mean,gauss_sigma = ImageMeanSigma(cliplight,Nbins=10001,use_iterbins=False,use_iterbins_if_needed=False)
	except TypeError:
		print "**   iterbins   ** iterbins tried and failed to run ImageMeanSigma now we're going to try again clipping off an extra 1%"
		percent_clip+=1
		cliplight = light[percent2index(light,percent_clip):percent2index(light,100-percent_clip)]
		cliplow = light[:percent2index(light,percent_clip)]
		cliphigh = light[percent2index(light,100-percent_clip):]
		lowscore=scipy.stats.scoreatpercentile(light,percent_clip)
		highscore=scipy.stats.scoreatpercentile(light,100-percent_clip)
		gauss_mean,gauss_sigma = ImageMeanSigma(cliplight,Nbins=501,use_iterbins=False,use_iterbins_if_needed=False)
	# get # of more datapoints that i include from using bins wider by a given # of sigmas
	Nadded_lower=asarray([(cliplow>lowscore-gauss_sigma*i).sum() for i in range(500)],dtype=int)
	Nadded_higher=asarray([(cliphigh<highscore+gauss_sigma*i).sum() for i in range(500)],dtype=int)
	raise_more = Nadded_higher[1:]-Nadded_higher[:-1]
	raise_less = Nadded_lower[1:]-Nadded_lower[:-1]
	binthresh = len(light)*fraction_include_thresh
	#iterate to get upper limit
	UPthenums=cumsum(raise_more<binthresh)
	UPbcnums = bincount(UPthenums)
	for i in range(len(UPbcnums)):
		if (UPbcnums[i:i+10]==1).all():
			UPstop=sum(UPbcnums[:i])
			break
	UPnewlim=highscore+UPstop*gauss_sigma  
	#iterate to get lower limit
	DOWNthenums=cumsum(raise_less<binthresh)
	DOWNbcnums = bincount(DOWNthenums)
	for i in range(len(DOWNbcnums)):
		if (DOWNbcnums[i:i+10]==1).all():
			DOWNstop=sum(DOWNbcnums[:i])
			break
	DOWNnewlim=lowscore-DOWNstop*gauss_sigma
	return DOWNnewlim,UPnewlim

def AxesBinNum2BinVal(ax,xbins,ybins=None,shape=None): #plotting
	'''takes axes with x and y ticklabels set as bin numbers and sets them to the actual values of those bins. Useful when using imshow to plot the result of an array which is the result of a 2dhist function (w/ some operations done on it, etc.). Use shape as a safety valve so that you can't screw up which bins are from the x axis and which are from the y axis.'''
	if not (shape is None) and not (ybins is None):
		axshape=(len(xbins)-1,len(ybins)-1)
		if not axshape==shape:
			if (axshape[1],axshape[0])==shape:
				print "flipping given axes bins around to match shape.\nMight want to plot imshow(array.T) rather than imshow(array)!"
				xbins,ybins=ybins,xbins
			else:
				print "bins shape is ",axshape," which doesn't match input shape ",shape," at all!\nshould have bins shape (N,M) => input shape (N-1,M-1)"
				raise Exception(" Shapes don't agree! (See above) "*10)
	xt=ax.get_xticks()
	xd,xu=ax.get_xlim()
	ticks_showing = xt[(xt>=xd) * (xt<=xu)]
	ax.set_xticks(ticks_showing)
	binvals = xbins[asarray(ticks_showing,dtype=int)]
	ax.set_xticklabels(binvals)
	if not ybins is None:
		yt=ax.get_yticks()
		yd,yu=ax.get_ylim()
		ticks_showing = yt[(yt>=yd) * (yt<=yu)]
		ax.set_yticks(ticks_showing)
		binvals = ybins[asarray(ticks_showing,dtype=int)]
		ax.set_yticklabels(binvals)
	return ax
		
def savefig_NameFileDate(f,NameString,FileString,DateString,size=10):
	f.text(.003,.003,"Made By:"+os.path.basename(FileString),size=size)
	f.text(.303,.003,"Date:"+DateString,size=size)
	f.text(.503,.003,"Named:"+os.path.basename(NameString),size=size)
	f.savefig(NameString)
	return f	

def NameFileDate(f,NameString,FileString,DateString,size=10):
	f.text(.003,.003,"Made By:"+os.path.basename(FileString),size=size)
	f.text(.303,.003,"Date:"+DateString,size=size)
	f.text(.503,.003,"Named:"+os.path.basename(NameString),size=size)
	return f	

def print_name2val(title='',blocklen=50,order=None,update_dict=None,**kwargs):
	try:
		maxblock=237
		max2linelen=210
		if blocklen>maxblock:blocklen=maxblock
		if len(title)>blocklen-14:
			blocklen=len(title)+14
			if blocklen<maxblock: return print_name2val(title=title,blocklen=blocklen,**kwargs)
			else: 
				blocklen=maxblock
				Nmaxlen=len(title)/max2linelen
				strs=[title[n*max2linelen:(n+1)*max2linelen] for n in range(Nmaxlen)]
				ending=title[(Nmaxlen*max2linelen):]
				strout=''
				for stri in strs:
					strout+='#START~~~~~~~~'+stri+'...~~~~START#'+'\n'
				strout+='#START~~~~~~~~'+ending+'~'*(210-len(ending))+'~~~~~~~START#'+'\n'
		else:strout='#START'+title.center(blocklen-12,'~')+'START#'+'\n'
		beginstr=strout
		if order:
			o=set(order)
			k=set(kwargs.keys())
			for elem in k.difference(o):
				order.append(elem)
			loopover=order
		else:
			loopover=kwargs.keys()
		if update_dict:
			for name in loopover:
				update_dict[name].append(kwargs[name])
		for name in loopover:
			#strout+='='.join([arg,globals().get(arg)])+'\n'
			nstr=(' '+name+' = {'+name+'} ').format(**kwargs)
			if len(nstr)>blocklen-2:
				if blocklen<maxblock:
					blocklen=len(nstr)+2
					return print_name2val(title=title,blocklen=blocklen,**kwargs)
				else:
					Nmaxlen=len(nstr)/max2linelen
					strs=[nstr[n*max2linelen:(n+1)*max2linelen] for n in range(Nmaxlen)]
					ending=nstr[(Nmaxlen*max2linelen):]
					for num,stri in enumerate(strs):
						if num==0:strout+='######    '+stri+'...	######'+'\n'
						else:strout+='######	...'+stri+'... ######'+'\n'
					strout+='######	...'+ending+' '*(210-len(ending))+'    ######'+'\n'
			else:strout+='######    '+nstr.ljust(blocklen-16,' ')+'######\n'
	except:
		namespace.update(locals())
		raise
	#namespace.update(locals())
	endstr=beginstr.replace('START','ENDED').replace('~','^')[:-1]
	strout+=endstr
	return strout


def SpotCutter(cutspots_list):
	'''this function takes a list of cut spots from successive cuts and returns the spots corresponding to all original values which passed all cuts. Example:
	nums= [-10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6 7 8 9 10]
	In [34]: even_spots=nums%2==0
	In [35]: evens=nums[even_spots]
	evens= [-10 -8 -6 -4 -2 0 2 4 6 8 10]
	In [37]: mid_even_spots=evens.__abs__()<9
	In [38]: mid_evens=evens[mid_even_spots]
	mid_evens= [-8 -6 -4 -2 0 2 4 6 8]
	In [40]: mid_even_PN_fib_spots=array([me in fibs_pn for me in mid_evens])
	In [41]: mid_even_PN_fibs=mid_evens[mid_even_PN_fib_spots]
	mid_even_PN_fibs= [-8 -2 0 2 8]
	In [43]: pos_mid_even_PN_fib_spots=mid_even_PN_fibs>0
	In [44]: pos_mid_even_PN_fibs=mid_even_PN_fibs[pos_mid_even_PN_fib_spots]
	pos_mid_even_PN_fibs= [2 8]
	In [46]: cutspots_list=[even_spots, mid_even_spots, mid_even_PN_fib_spots, pos_mid_even_PN_fib_spots]
	In [47]: pass_all_cuts_spots=SpotCutter(cutspots_list)
	pass_all_cuts_spots=[False False False False False False False False False False False False True False False False False False True False False]
	nums[pass_all_cuts_spots]= [2 8]'''
	Ncuts=len(cutspots_list)
	lens=[]
	sums=[]
	for cutspots in cutspots_list:
		lens.append(cutspots.__len__())
		sums.append(cutspots.sum())
	if not lens[1:]==sums[:-1]:
		print "lens=",lens
		print "sums=",sums
		raise Exception('These Shapes dont agree!')
	cut1spots=cutspots_list[0]
	finalspots=cut1spots.copy()
	for i in range(Ncuts-1):
		pass_cut_i_inds=nonzero(finalspots)[0]
		#finalspots already has been adjusted so that you know it satisfies cut i, now make it satisfy cut i+1
		not_pass_cut_iplus1_inds=pass_cut_i_inds[logical_not(cutspots_list[i+1])]
		finalspots[not_pass_cut_iplus1_inds]=False
	if finalspots.__len__()==lens[0] and finalspots.sum()==sums[-1]:
		return finalspots
	else:
		print "supposted to have len=",lens[0]
		print "and sum=",sums[-1]
		print "but got len=",finalspots.__len__()," and sum=",finalspots.sum()
		raise Exception('something wrong with finalspots shape and sum!')

def parallel_manager(sysargv,inlist=[0,1,2,3]):
	'''maps from parallel manager inputs to items in a list!
	meant to be called like imagetools.parallel_manager(sys.argv,inlist=['foo','bar','bazz','packers'])'''
	choices={' 3 7':0, ' 4 8':1, ' 2 6 10':2, ' 1 5 9':3}
	for key in choices.keys():
		if key in sysargv:
			ind2pick=choices[key]
	select=inlist[ind2pick]
	if select==None:
		sys.exit()
	else:
		return select

def getRegex(ss):
	control_chars=['(','+','?','.','*','^','$','(',')','[',']','{','}','|',')']
	esc_chars=['\(','\+','\?','\.','\*','\^','\$','\(','\)','\[','\]','\{','\}','\|','\)']
	num_cc=len(control_chars)
	for i in range(num_cc):
		ss=ss.replace(control_chars[i],esc_chars[i])
	return ss

def py_list_to_bash_array(l,l_name):
	'''example: >>> overscan_clips_x1=[1,569,1138,1705]
	>>>print py_list_to_bash_array(overscan_clips_x1,"overscan_clips_x1")
	<<<overscan_clips_x1=( [1]=1 [2]=1 [3]=1 [4]=1 [5]=1 [6]=1 [7]=1 [8]=1 [9]=1 [10]=1 \ 
	[11]=569 [12]=569 [13]=569 [14]=569 [15]=569 [16]=569 [17]=569 [18]=569 [19]=569 [20]=569 \ 
	[21]=1138 [22]=1138 [23]=1138 [24]=1138 [25]=1138 [26]=1138 [27]=1138 [28]=1138 [29]=1138 [30]=1138 \ 
	[31]=1705 [32]=1705 [33]=1705 [34]=1705 [35]=1705 [36]=1705 [37]=1705 [38]=1705 [39]=1705 [40]=1705 )'''
	s=l_name+"=( "
	for i in range(4):
		nums=arange(i*10,i*10+10)+1
		vals=[l[i]]*10
		nvs=array(zip(nums,vals)).flatten()
		s+="[%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i [%i]=%i \\ \n" % tuple(nvs)
	s_final=s[:-3]+")"
	return s_final

def ArgCleaner(allargs=sys.argv,FileString=None,pythons_remove=True): #re-write (generalize) 
	'''takes command line inputs and cleans out the garbage and picks out the useful stuff'''
	args=[]
	for arg in allargs:
		if arg.endswith(".py"):continue
		if arg.startswith("-"):continue
		if arg=='python':continue
		else:
			args.append(arg)
	if FileString:
		if FileString in args[0]:
			args.pop(0)
	#if pythons_remove:
	#	for arg in args:
	#		if arg.endswith(".py"):
	#			args.remove(arg)
	return args

def PlotFlags(fl):
	'''plot the flag file showing individual flags and flags as a whole'''
	import itertools
	from matplotlib.colors import LogNorm
	import matplotlib.cm as cm
	flag_nums=[1,2,4,8,16,32,64,128]
	many_flags={}
	for flag in flag_nums:
		many_flags[flag]=[flag]

	multiples={}
	for Ntup in range(2,len(flag_nums)+1):
		multiples[Ntup]={}
		multiples[Ntup]['nums']=array(list(itertools.combinations(flag_nums,Ntup)))
		multiples[Ntup]['sums']=array([P.sum() for P in multiples[Ntup]['nums']])
		for flag in flag_nums:
			flag_in_mult=(multiples[Ntup]['nums']==flag).any(axis=1)
			flag_nums_Ntup=multiples[Ntup]['sums'][flag_in_mult]
			many_flags[flag]+=list(flag_nums_Ntup)

	fl_basename=os.path.basename(fl)
	im=pyfits.open(fl)[0].data
	im_size=im.size
																				    
	f=figure(figsize=(16,13.75))
	ax=f.add_subplot(3,3,1)
	ax.set_title(fl_basename)
	imshow(im,origin='lower left', interpolation='nearest',norm=LogNorm(vmin=1,vmax=128))
	colorbar()
	for i,flag in enumerate(flag_nums):
		ax=f.add_subplot(3,3,i+2)
		flag_match=EqualsAny(im,many_flags[flag])
		ax.set_title('flag==%i (total=%i of %i)' % (flag,flag_match.sum(),im_size))
		ax.set_xticklabels([])
		ax.set_yticklabels([])
		imshow(flag_match,vmin=0,vmax=1,origin='lower left', interpolation='nearest',cmap=cm.binary)
	f.tight_layout()
	return f

def read_external_header(fl,return_enigmas=False):
	fo=open(fl,'r')
	enigmas=[]
	fheader={}
	for l in fo.xreadlines():
	    lsplit=l.split()
	    if lsplit[0].endswith("="):lsplit=[lsplit[0][:-1],"="]+lsplit[1:]
	    if len(lsplit)<3:continue
	    elif len(lsplit)==3 and split[1]=="=":
		fheader[lsplit[0]]=lsplit[2]
	    elif lsplit[1]=="=" and lsplit[3]=="/":
		fheader[lsplit[0]]=lsplit[2]
	    else:
		print "don't know if this helps or not:",l
		enigmas.append(l)
	## make ints and floats where appropriate
	for k,v in fheader.items():
	    try:
		vnew=int(v)
	    except:
		try:
		    vnew=float(v)
		except:
		    continue
	    fheader[k]=vnew
	## return headers or not
	if return_enigmas==True:
		return fheader,enigmas
	else:
		return fheader

# Filter properties of the instrument.
filter_names= {'W-J-B'    : 'JohnsonB',
               'W-S-G+'   : 'SloanG',
               'W-J-V'    : 'JohnsonV',
               'W-C-RC'   : 'CousinsR',
               'W-S-I+'   : 'SloanI',
               'W-C-IC'   : 'CousinsI',
               'W-S-Z+'   : 'SloanZ'}
#filter's central wavelength (cwl) [angstroms]
#purple~3800 and red~7800
# in order of increasing wavelength: W-J-B W-S-G+ W-J-V W-C-RC W-S-I+ W-C-IC W-S-Z+
filter_cwl  = { 'W-J-B'    : 4478.0,
                'W-S-G+'   : 4809.0,
                'W-J-V'    : 5493.0,
                'W-C-RC'   : 6550.0,
                'W-S-I+'   : 7709.0,
                'W-C-IC'   : 7996.0,
                'W-S-Z+'   : 9054.0}
filter_color  = { 'W-J-B'  : 'purple',
                'W-S-G+'   : 'blue',
                'W-J-V'    : 'green',
                'W-C-RC'   : 'yellow',
                'W-S-I+'   : 'orange',
                'W-C-IC'   : 'red',
                'W-S-Z+'   : 'black'}
filters = [ 'W-J-B', 'W-S-G+' , 'W-J-V'  , 'W-C-RC' , 'W-S-I+' , 'W-C-IC' , 'W-S-Z+' ]
band2color=filter_color
