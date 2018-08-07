#! /usr/bin/env python
from __future__ import division #3/2=1.5 and 3//2=1
#adam-does# blends cosmics and blocks them from being blended into stars
#adam-use # use with CRNitschke cosmics masking pipeline
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
import astropy
from astropy.io import ascii
from copy import deepcopy as cp
import os
import pymorph
import skimage
from skimage import measure
from skimage import morphology
import mahotas
from matplotlib.pyplot import *
import numpy
from numpy import histogram
import time
ns=globals()
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
connS=array([[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]],dtype=bool)
plotdir='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/plot_SCIENCE_compare/'

#START: RING FUNCTIONS define commands for fixing rings
slope_flat_cut=.04
ring_rr_cut=2.8 #new
def track2ring(track_spots,ring_spots):
	'''this is designed to extend tracks through objects they are near. it is called within `ringer`. this fits a line to `track_spots` and stretches the mask along the line through the ring'''
	try:
		#fill ring then get ring pairs
		ring_spots_all=scipy.ndimage.binary_fill_holes(ring_spots)
		ayy,axx=nonzero(ring_spots_all)
		#get track pairs and fit line to track spots
		oyy,oxx=nonzero(track_spots)
		rr,poly,polytype=polyfitter(track_spots,1)
		#get spots in filled ring that are co-linear with the track
		try:
			m,b=poly.coeffs #for line y=m*x+b or x=m*y+b
			print "track2ring poly.coeffs runs fine"
		except ValueError:
			print "track2ring poly.coeffs ValueError"
			return track_spots,0,rr
		except AttributeError:
			print "track2ring poly.coeffs AttributeError"
			return track_spots,0,rr
		if rr>ring_rr_cut or isnan(rr):
			return track_spots,0,rr
		if polytype=='x_of_y':
			aX=poly(ayy)
			aOffsets=(axx-aX).__abs__()
			oX=poly(oyy)
			oOffsets=(oxx-oX).__abs__()
		elif polytype=='y_of_x':
			aY=poly(axx)
			aOffsets=(ayy-aY).__abs__()
			oY=poly(oxx)
			oOffsets=(oyy-oY).__abs__()
		else:
			return track_spots,0,rr
		extend_track_spots=aOffsets<1.3
		xmin=oxx.min();xmax=oxx.max();ymin=oyy.min();ymax=oyy.max()
		#make sure they are extending along the main axis of the track
		ur=(axx>=xmax)*(ayy>=ymax)
		ul=(axx<=xmin)*(ayy>=ymax)
		lr=(axx>=xmax)*(ayy<=ymin)
		ll=(axx<=xmin)*(ayy<=ymin)
		if math.fabs(m)<slope_flat_cut:
			if polytype=='x_of_y':
				Rxxyy_spots=extend_track_spots*(ayy>=ymax) #upper
				Lxxyy_spots=extend_track_spots*(ayy<=ymin) #lower
			elif polytype=='y_of_x':
				Rxxyy_spots=extend_track_spots*(axx>=xmax) #right
				Lxxyy_spots=extend_track_spots*(axx<=xmin) #left
		elif math.fabs(m)>slope_flat_cut**(-1):
			if polytype=='x_of_y':
				Rxxyy_spots=extend_track_spots*(axx>=xmax) #right
				Lxxyy_spots=extend_track_spots*(axx<=xmin) #left
			elif polytype=='y_of_x':
				Rxxyy_spots=extend_track_spots*(ayy>=ymax) #upper
				Lxxyy_spots=extend_track_spots*(ayy<=ymin) #lower
		elif m>0:
		    Rxxyy_spots=extend_track_spots*ur
		    Lxxyy_spots=extend_track_spots*ll
		elif m<0:
		    Rxxyy_spots=extend_track_spots*lr
		    Lxxyy_spots=extend_track_spots*ul
		Rxx,Ryy=axx[Rxxyy_spots],ayy[Rxxyy_spots]
		Lxx,Lyy=axx[Lxxyy_spots],ayy[Lxxyy_spots]
		#now change the final mask if the edgepoints are above the threshold
		track_spots_final=track_spots.copy()
		Rpts=zip(Ryy,Rxx)
		Lpts=zip(Lyy,Lxx)
		included=0
		for o in Rpts+Lpts:
			included+=1
			track_spots_final[o]=True
		# now include a co-linear connector (intra-track/inter-track connector)
		track_spots_final=connector(track_spots_final)
		return track_spots_final,included,rr
	except:
		ns.update(locals())
		raise

def ringable(ra_object):
	'''this takes an "almost ring" and makes it a true ring. it is called within `ringer`.'''
	ra_spots=asarray(ra_object.copy(),dtype=bool)
	ra_insides=scipy.ndimage.binary_fill_holes(ra_spots)* logical_not(ra_spots)
	hom=zeros(ra_spots.shape)
	for corner in [(0,0),(0,-1),(-1,0),(-1,-1)]:
		miss=zeros((3,3),dtype=bool)
		miss[corner]=1
		hit=scipy.ndimage.morphology.binary_dilation(miss,conn4)*logical_not(miss)
		hom+=scipy.ndimage.morphology.binary_hit_or_miss(ra_spots, structure1=hit, structure2=miss)
	hom=asarray(hom,dtype=bool)
	fill_them=ra_insides*hom
	ra_spots[fill_them]=1
	#new to accomodate count_hole_filled_pixels
	ra_skel=pymorph.thin(ra_spots)
	ra_ring=pymorph.thin(ra_skel,pymorph.endpoints())
	if not ra_ring.any(): #fill in the tiny gaps that ruin the ring!
		ra4_spots=scipy.ndimage.binary_dilation(ra_spots,conn4)
		ra4_skel=pymorph.thin(ra4_spots)
		ra4_ring=pymorph.thin(ra4_skel,pymorph.endpoints())
		if ra4_ring.any(): #fill in the tiny gaps that ruin the ring!
			print "ringable 4\n"
			ra_insides=scipy.ndimage.binary_fill_holes(ra4_ring)
			fill_them=ra_insides*ra4_spots
			ra_spots[fill_them]=1
			return ra_spots
		ra8_spots=scipy.ndimage.binary_dilation(ra_spots,conn8)
		ra8_skel=pymorph.thin(ra8_spots)
		ra8_ring=pymorph.thin(ra8_skel,pymorph.endpoints())
		if ra8_ring.any(): #fill in the tiny gaps that ruin the ring!
			print "ringable 8\n"
			ra_insides=scipy.ndimage.binary_fill_holes(ra8_ring)
			fill_them=ra_insides*ra8_spots
			ra_spots[fill_them]=1
	return ra_spots

def ringer_noplot(spots_ringer,l_ringer,filtstamp_ringer,imstamp_ringer,seg0stamp_ringer,star_stamp):
        '''input the detection stamp with a ring in it and output the detection stamp if you remove the ring and extend the outside tracks through the ring'''
        try:
                fl_label_str='file=%s label=%.4i' % (OFB,l_ringer)
                #DONT CONTINUE: if saturation spike
                sl2_height,sl2_width=imstamp_ringer.shape
                sl2_height,sl2_width=float(sl2_height-6),float(sl2_width-6)
                if sl2_height>300 and (sl2_height/sl2_width)>25:
                        return spots_ringer, "saturation spike"
                #DONT CONTINUE: if really long and skinny ring
                inside4_b4=scipy.ndimage.binary_opening(scipy.ndimage.binary_fill_holes(spots_ringer)* logical_not(spots_ringer),array([[1,1],[1,1]],dtype=bool)).any()

                #START: what was `getring_track(spots_ringer)`
                #input object mask and output the pixels separated into a ring pixels and track pixels
                ringer_skel=pymorph.thin(spots_ringer)
                ring=pymorph.thin(ringer_skel,pymorph.endpoints())
                if not ring.any(): #fill in the tiny gaps that ruin the ring!
                        spots_ringer2=ringable(spots_ringer)
                        ringer_skel=pymorph.thin(spots_ringer2)
                        ring=pymorph.thin(ringer_skel,pymorph.endpoints())
                        if not ring.any():
                                print (fl_label_str+": RINGABLE didnt work!\n")
                                return spots_ringer, "Un-ringable holes"
                        else:
                                spots_ringer=spots_ringer2
                #DONT CONTINUE: if really long and skinny ring
                inside4_after=scipy.ndimage.binary_opening(scipy.ndimage.binary_fill_holes(spots_ringer)* logical_not(spots_ringer),array([[1,1],[1,1]],dtype=bool)).sum()
                if not inside4_b4 and not inside4_after>5:
                        return spots_ringer, "none in square pattern" #might as well put this at beginning, if it fails (and I want it to pass) it'll probably pass after the thresh is raised
                #now if there are gaps in the ring, then take only the inner portion surrounding them
                insides=scipy.ndimage.binary_fill_holes(ring)* logical_not(ring)
                newinsides=skimage.morphology.remove_small_objects(insides,2,connectivity=1) #conn4
                if (insides!=newinsides).any():
                        newinsides_seg,Nnewinsides_segs= scipy.ndimage.label(newinsides,conn8)
                        if Nnewinsides_segs<=1:
                                ring2=scipy.ndimage.binary_dilation(newinsides,conn8,mask=ring)-newinsides
                                ring=ring2
                                insides=newinsides
                #skel_outside_ring=ringer_skel*logical_not(scipy.ndimage.binary_fill_holes(scipy.ndimage.binary_dilation(ring,conn4)))
                ring_and_insides=insides+ring
                outsides=logical_not(ring_and_insides)
                skel_outside_ring=ringer_skel*outsides
                ringer_track_portions=skimage.morphology.remove_small_objects(skel_outside_ring,3,connectivity=2) #conn8
                ringer_track_spots=spots_ringer*scipy.ndimage.binary_dilation(ringer_track_portions,conn8,mask=outsides)
                Rgetring_ring,Rgetring_track=asarray(ring,dtype=bool),asarray(ringer_track_spots,dtype=bool)
                #END: end of what was previously getring_track

                #DONT CONTINUE: if it's a circle of cosmics
                #tree_ring=ring.copy()
                ring_and_outer_layer=scipy.ndimage.binary_dilation(ring,conn4,mask=outsides)
                image_ring,image_ring_widen=imstamp_ringer[ring],imstamp_ringer[ring_and_outer_layer]
                image_ring.sort();image_ring_widen.sort()
                image_ring,image_ring_widen=image_ring[:-3],image_ring_widen[:-3]
                image_ring_mean=max(image_ring.mean(),image_ring_widen.mean())
                image_ring_filled_mean=(imstamp_ringer[insides].mean())
                if image_ring_mean>image_ring_filled_mean: #if the mean value of the edge is greater than the middle, then it isn't an object at all
                        print (fl_label_str+": circle of cosmics!\n")
                        return spots_ringer, "Circle of Cosmics"
                #get original mask
                ringer_mask0=seg0stamp_ringer>0
                ringer0=ringer_mask0*spots_ringer
                yy0,xx0=nonzero(ringer0)
                Pts0=zip(yy0,xx0)
                for pt0 in Pts0:
                        if not Rgetring_track[pt0]:
                                if skel_outside_ring[pt0]:
                                        skel_outside_seg,Nskelsegs=scipy.ndimage.label(skel_outside_ring,conn8)
                                        pt0_l=skel_outside_seg[pt0]
                                        pt0_spots=skel_outside_seg==pt0_l
                                        Rgetring_track[pt0_spots]=True
                                else:
                                        Rgetring_track[pt0]=True
                if not Rgetring_track.any():#Now if it was all ring
                        #reset to the original mask
                        return spots_ringer, "Entire thing was a ring"
                #SIMPLE LINE: BEGIN try seeing if everything fits in a simple line really easily
                max_within=scipy.stats.scoreatpercentile(filtstamp_ringer[ring_and_insides],95)
                cosmics_lintry=(filtstamp_ringer>max_within*2)*spots_ringer
                yy_lin,xx_lin=nonzero(cosmics_lintry)
                try:
                        track_length=sqrt((xx_lin.max()-xx_lin.min())**2+(yy_lin.max()-yy_lin.min())**2)
                        if cosmics_lintry.sum()>4 and track_length>7:
                                track_spots_final,included,rr=track2ring(cosmics_lintry,Rgetring_ring)
                                if (rr<.75) or (cosmics_lintry.sum()>9 and rr<1.03):
                                        print (fl_label_str+": SIMPLE LINE!\n")
                                        track_spots_final,stretch_count=iter_track_stretch(track_spots_final, filtstamp_ringer,dt_times_pt01,BASE,l_ringer,star_stamp,ts_rr_cut=ring_rr_cut,rr_per_step=.25)
                                        #now include tracks that overlap with the mask
                                        ring_seg,Nring_track_labels=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layer),conn8)
                                        track_seg_include=ring_seg[cosmics_lintry]
                                        track_seg_include_labels=unique(track_seg_include).tolist()
                                        try:track_seg_include_labels.remove(0)
                                        except ValueError:pass
                                        if track_seg_include_labels:
                                                spots_yy_all,spots_xx_all=array([],dtype=int),array([],dtype=int)
                                                for l_track in track_seg_include_labels:
                                                        spots=ring_seg==l_track
                                                        track_spots_final+=spots
                                                        spots_yy,spots_xx=nonzero(spots)
                                                        spots_yy_all=append(spots_yy_all,spots_yy)
                                                        spots_xx_all=append(spots_xx_all,spots_xx)
                                        ringer_yy,ringer_xx=nonzero(track_spots_final)
                                        return track_spots_final, 0 #ringstat==0 implies all is well with ringer
                except ValueError:
                        if cosmics_lintry.any(): raise
                        else: pass
                #SIMPLE LINE: END try seeing if everything fits in a simple line really easily
                # first doing ring segments with 1 layer outside the ring excluded (gets closer to the ring), then doing it with 2 layers excluded (has advantage of not mixing detections near the ring). then if the 1layer and 2layer thing disagree I ta
                ring_seg,Nring_track_labels=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layer),conn8)
                ringer_track_labels=range(1,1+Nring_track_labels)
                ring_slices=scipy.ndimage.find_objects(ring_seg)
                ring_and_outer_layers2=scipy.ndimage.binary_dilation(ring_and_outer_layer,conn8,mask=outsides)
                ring_seg_layers2,Nring_track_labels_layers2=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layers2),conn8)
                #if there are a ton of track pieces, then I'll go with the original mask thing
                ringer_track_labels_loop=copy(ringer_track_labels)
                xx_seg,yy_seg=array([]),array([])
                for l_bit in ringer_track_labels_loop:
                        sl=ring_slices[l_bit-1]
                        track_spots=ring_seg[sl]==l_bit
                        ringer0_here=ringer0[sl][track_spots].any()
                        if track_spots.sum()<7:
                                continue
                        layers2_stamp=ring_seg_layers2[sl]
                        layers2_at_track=layers2_stamp[track_spots]
                        layers2_at_track_labels=unique(layers2_at_track).tolist()
                        try:layers2_at_track_labels.remove(0)
                        except ValueError:pass
                        Nl2s_possible=len(layers2_at_track_labels)
                        if Nl2s_possible>1:
                                l2_sizes=[]
                                l2_in_orig=[]
                                for l2_l in layers2_at_track_labels:
                                        l2_spots=layers2_stamp==l2_l
                                        l2_in_orig.append(ringer0[sl][l2_spots].any())
                                        l2_sizes.append(l2_spots.sum())
                                l2_sizes=array(l2_sizes)
                                l2_size_cut=l2_sizes>2
                                Nl2s=sum(l2_size_cut)
                                if Nl2s>=2:
                                        if ringer0_here and not array(l2_in_orig).any(): continue
                                        ringer_track_labels_add=max(ringer_track_labels)+1+arange(Nl2s_possible)
                                        ringer_track_labels=ringer_track_labels+ringer_track_labels_add.tolist()
                                        ring_seg[sl][track_spots]=0
                                        ringer_track_labels.remove(l_bit)
                                        for l2_l,ring_seg_l in zip(layers2_at_track_labels,ringer_track_labels_add):
                                                l2_spots=layers2_stamp==l2_l
                                                l2yy,l2xx=nonzero(l2_spots)
                                                xx_seg=append(xx_seg,l2xx)
                                                yy_seg=append(yy_seg,l2yy)
                                                ring_seg[sl][l2_spots]=ring_seg_l
                                        print (fl_label_str+": thing with 1layer and 2layer masks actually matters!\n")
                ringer_track_labels=asarray(ringer_track_labels)
                ring_seg_in_orig=[]
                ring_seg_maxvals=[]
                ring_seg_areas=[]
                for l_bit in ringer_track_labels:
                        track_spots=ring_seg==l_bit
                        ring_seg_in_orig.append(ringer0[track_spots].any())
                        ring_seg_maxvals.append(filtstamp_ringer[track_spots].max())
                        ring_seg_areas.append(track_spots.sum())
                ring_seg_in_orig=asarray(ring_seg_in_orig)
                ring_seg_maxvals=asarray(ring_seg_maxvals)
                ring_seg_areas=asarray(ring_seg_areas)
                #keep anything that's above twice the highest ring value or was an original masked pixel
                ring_seg_keep=(ring_seg_maxvals>max_within*2) + ring_seg_in_orig
                if ring_seg_keep.sum()>0:ringer_track_labels=ringer_track_labels[ring_seg_keep]
                else:
                        print (fl_label_str+': if none are the originals, then take the largest and the brightest\n')
                        try:
                                max_label=ringer_track_labels[ring_seg_maxvals.argmax()]
                                area_label=ringer_track_labels[ring_seg_areas.argmax()]
                                ringer_track_labels=[max_label]
                                if area_label!=max_label and ring_seg_areas.max()>5: ringer_track_labels.append(area_label)
                        except ValueError:
                                return spots_ringer, "Un-ringable holes"#if there is no max valued/max area thing, then they're all super small and
                newring=ringer0.copy() #at the very least, use the original track pixels
                Nringworms=0
                for bit_i,l_bit in enumerate(ringer_track_labels):
                        track_spots=ring_seg==l_bit
                        track_spots_final,included,rr=track2ring(track_spots,Rgetring_ring)
                        #now extend track?!
                        if not isnan(rr):track_spots_final,stretch_count=iter_track_stretch(track_spots_final, filtstamp_ringer,dt_times_pt01,BASE,l_ringer,star_stamp,ts_rr_cut=ring_rr_cut,name_extras=('ring_rr%.2f' % (rr,)).replace('.','pt'),rr_per_step=.2)
                        else:track_spots_final=scipy.ndimage.binary_dilation(track_spots_final,conn8)
                        newring+=track_spots_final
                        ringer_yy,ringer_xx=nonzero(track_spots_final)
                        try:
                                if rr>ring_rr_cut or isnan(rr):
                                        Nringworms+=1
                        except IndexError: pass
                #if there are 2 worms, then mask entire thing!
                if Nringworms>1:
                        newring+=ring_and_insides
                ringer_Fyy,ringer_Fxx=nonzero(newring)
                return newring, 0 #ringstat==0 implies all is well with ringer
        except:
                ns.update(locals())
                raise 

#RINGER
def ringer(spots_ringer,l_ringer,filtstamp_ringer,imstamp_ringer,seg0stamp_ringer,star_stamp):
	'''input the detection stamp with a ring in it and output the detection stamp if you remove the ring and extend the outside tracks through the ring'''
	try:
		pltstr='pltRevise%s_holes_ringer-label%.4i' % (OFB,l_ringer)
		pltextras=''
		fl_label_str='file=%s label=%.4i' % (OFB,l_ringer)
		#DONT CONTINUE: if saturation spike
		sl2_height,sl2_width=imstamp_ringer.shape
		sl2_height,sl2_width=float(sl2_height-6),float(sl2_width-6)
		if sl2_height>300 and (sl2_height/sl2_width)>25:
			return spots_ringer, "saturation spike"
		#DONT CONTINUE: if really long and skinny ring
		inside4_b4=scipy.ndimage.binary_opening(scipy.ndimage.binary_fill_holes(spots_ringer)* logical_not(spots_ringer),array([[1,1],[1,1]],dtype=bool)).any()
		#START: what was `getring_track(spots_ringer)`
		#input object mask and output the pixels separated into a ring pixels and track pixels
		ringer_skel=pymorph.thin(spots_ringer)
		ring=pymorph.thin(ringer_skel,pymorph.endpoints())
		if not ring.any(): #fill in the tiny gaps that ruin the ring!
			spots_ringer2=ringable(spots_ringer)
			ringer_skel=pymorph.thin(spots_ringer2)
			ring=pymorph.thin(ringer_skel,pymorph.endpoints())
			if not ring.any():
				print (fl_label_str+": RINGABLE didnt work!\n")
				f=figure(figsize=(20,10))
				yy,xx=nonzero(spots_ringer)
				imshow(imstamp_ringer,interpolation='nearest',origin='lower left')
				scatter(xx,yy,edgecolors='k',facecolors='None')
				title('Holes there, but not ringable')
				pltextras+='-NoChange_UnRingable'
				f.suptitle(fl_label_str+pltextras)
				f.savefig(plotdir+pltstr+pltextras)
				close(f);del f
				return spots_ringer, "Un-ringable holes"
			else:
				spots_ringer=spots_ringer2
		#DONT CONTINUE: if really long and skinny ring
		inside4_after=scipy.ndimage.binary_opening(scipy.ndimage.binary_fill_holes(spots_ringer)* logical_not(spots_ringer),array([[1,1],[1,1]],dtype=bool)).sum()
		if not inside4_b4 and not inside4_after>5:
			return spots_ringer, "none in square pattern" #might as well put this at beginning, if it fails (and I want it to pass) it'll probably pass after the thresh is raised
		#now if there are gaps in the ring, then take only the inner portion surrounding them
		insides=scipy.ndimage.binary_fill_holes(ring)* logical_not(ring)
		newinsides=skimage.morphology.remove_small_objects(insides,2,connectivity=1) #conn4
		if (insides!=newinsides).any():
			newinsides_seg,Nnewinsides_segs= scipy.ndimage.label(newinsides,conn8)
			if Nnewinsides_segs<=1:
				ring2=scipy.ndimage.binary_dilation(newinsides,conn8,mask=ring)-newinsides
				f=figure()
				ax=f.add_subplot(2,2,1);imshow(ring,interpolation='nearest',origin='lower left');title('ring')
				ax=f.add_subplot(2,2,2);imshow(insides,interpolation='nearest',origin='lower left');title('insides')
				ax=f.add_subplot(2,2,3);imshow(newinsides,interpolation='nearest',origin='lower left');title('newinsides')
				ax=f.add_subplot(2,2,4);imshow(ring2,interpolation='nearest',origin='lower left');title('ring2')
				pltextras+='-reringing'
				f.suptitle(fl_label_str+pltextras+'NewRing')
				f.savefig(plotdir+pltstr+pltextras)
				close(f);del f
				ring=ring2
				insides=newinsides
		#skel_outside_ring=ringer_skel*logical_not(scipy.ndimage.binary_fill_holes(scipy.ndimage.binary_dilation(ring,conn4)))
		ring_and_insides=insides+ring
		outsides=logical_not(ring_and_insides)
		skel_outside_ring=ringer_skel*outsides
		ringer_track_portions=skimage.morphology.remove_small_objects(skel_outside_ring,3,connectivity=2) #conn8
		ringer_track_spots=spots_ringer*scipy.ndimage.binary_dilation(ringer_track_portions,conn8,mask=outsides)
		Rgetring_ring,Rgetring_track=asarray(ring,dtype=bool),asarray(ringer_track_spots,dtype=bool)
		#END: end of what was previously getring_track

		#DONT CONTINUE: if it's a circle of cosmics
		#tree_ring=ring.copy()
		ring_and_outer_layer=scipy.ndimage.binary_dilation(ring,conn4,mask=outsides)
		image_ring,image_ring_widen=imstamp_ringer[ring],imstamp_ringer[ring_and_outer_layer]
		image_ring.sort();image_ring_widen.sort()
		image_ring,image_ring_widen=image_ring[:-3],image_ring_widen[:-3]
		image_ring_mean=max(image_ring.mean(),image_ring_widen.mean())
		image_ring_filled_mean=(imstamp_ringer[insides].mean())
		if image_ring_mean>image_ring_filled_mean: #if the mean value of the edge is greater than the middle, then it isn't an object at all
			print (fl_label_str+": circle of cosmics!\n")
			f=figure(figsize=(20,10))
			yy,xx=nonzero(spots_ringer)
			imshow(imstamp_ringer,interpolation='nearest',origin='lower left')
			scatter(xx,yy,edgecolors='k',facecolors='None')
			title('circle of cosmics')
			pltextras+='-NoChange_CircleOfCosmics'
			f.suptitle('file=%s label=%.4i image_ring_mean=%.4f>image_ring_filled_mean=%.4f' % (OFB,l_ringer,image_ring_mean,image_ring_filled_mean) + pltextras)
			f.savefig(plotdir+pltstr+pltextras)
			close(f);del f
			return spots_ringer, "Circle of Cosmics"

		#get original mask
		ringer_mask0=seg0stamp_ringer>0
		ringer0=ringer_mask0*spots_ringer
		yy0,xx0=nonzero(ringer0)
		Pts0=zip(yy0,xx0)
		for pt0 in Pts0:
			if not Rgetring_track[pt0]:
				if skel_outside_ring[pt0]:
					skel_outside_seg,Nskelsegs=scipy.ndimage.label(skel_outside_ring,conn8)
					pt0_l=skel_outside_seg[pt0]
					pt0_spots=skel_outside_seg==pt0_l
					Rgetring_track[pt0_spots]=True
				else:
					Rgetring_track[pt0]=True
		f=figure(figsize=(20,10))
		f.subplots_adjust(left=.03, bottom=.03, right=.97, top=.93)
		if not Rgetring_track.any():#Now if it was all ring
			#reset to the original mask
			ax=f.add_subplot(111)
			yy,xx=nonzero(spots_ringer)
			imshow(filtstamp_ringer,interpolation='nearest',origin='lower left')
			scatter(xx,yy,edgecolors='k',facecolors='None')
			scatter(xx0,yy0,edgecolors='w',marker='x')
			ax.set_title('No track found around the ring. Un-doing the blend so the original mask (the white "x"s) will be used!')
			pltextras+='-NoChange_NoTrack'
			f.suptitle(fl_label_str+pltextras)
			f.savefig(plotdir+pltstr+pltextras)
			close(f);del f
			return spots_ringer, "Entire thing was a ring"
		#SIMPLE LINE: BEGIN try seeing if everything fits in a simple line really easily
		max_within=scipy.stats.scoreatpercentile(filtstamp_ringer[ring_and_insides],95)
		cosmics_lintry=(filtstamp_ringer>max_within*2)*spots_ringer
		yy_lin,xx_lin=nonzero(cosmics_lintry)
		try:
			track_length=sqrt((xx_lin.max()-xx_lin.min())**2+(yy_lin.max()-yy_lin.min())**2)
			if cosmics_lintry.sum()>4 and track_length>7:
				track_spots_final,included,rr=track2ring(cosmics_lintry,Rgetring_ring)
				if (rr<.75) or (cosmics_lintry.sum()>9 and rr<1.03):
					print (fl_label_str+": SIMPLE LINE!\n")
					track_spots_final,stretch_count=iter_track_stretch(track_spots_final, filtstamp_ringer,dt_times_pt01,BASE,l_ringer,star_stamp,ts_rr_cut=ring_rr_cut,rr_per_step=.25)
					#now include tracks that overlap with the mask
					ring_seg,Nring_track_labels=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layer),conn8)
					track_seg_include=ring_seg[cosmics_lintry]
					track_seg_include_labels=unique(track_seg_include).tolist()
					try:track_seg_include_labels.remove(0)
					except ValueError:pass
					if track_seg_include_labels:
						spots_yy_all,spots_xx_all=array([],dtype=int),array([],dtype=int)
						for l_track in track_seg_include_labels:
							spots=ring_seg==l_track
							track_spots_final+=spots
							spots_yy,spots_xx=nonzero(spots)
							spots_yy_all=append(spots_yy_all,spots_yy)
							spots_xx_all=append(spots_xx_all,spots_xx)
					ringer_yy,ringer_xx=nonzero(track_spots_final)
					imshow(filtstamp_ringer,interpolation='nearest',origin='lower left')
					scatter(ringer_xx,ringer_yy,marker='o',edgecolors='k',facecolors='None',s=50)
					scatter(xx_lin,yy_lin,marker='x',edgecolors='w',facecolors='None')
					pltextras+='-simple_line_interupt'
					try:
						scatter(spots_xx_all,spots_yy_all,marker='s',edgecolors='purple',facecolors='None',s=50)
						f.suptitle('SIMPLE LINE: file=%s label=%.4i rr=%.4f' % (OFB,l_ringer,rr) +pltextras+'\nwhite "x"=spots that formed simple line, black "o"=final mask, purple \t=overlapping tracks included')
					except:
						f.suptitle('SIMPLE LINE: file=%s label=%.4i rr=%.4f' % (OFB,l_ringer,rr) +pltextras+'\nwhite "x"=spots that formed simple line, black "o"=final mask')
					f.savefig(plotdir+pltstr+pltextras)
					close(f);del f
					return track_spots_final, 0 #ringstat==0 implies all is well with ringer
		except ValueError:
			if cosmics_lintry.any(): raise
			else: pass
		#SIMPLE LINE: END try seeing if everything fits in a simple line really easily
		ax=f.add_subplot(2,6,1);ax.set_title('spots_ringer="o"\n& original mask ="x"');yy,xx=nonzero(spots_ringer);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		scatter(xx0,yy0,edgecolors='w',marker='x')
		ax=f.add_subplot(2,6,2);ax.set_title('ringer_skel');yy,xx=nonzero(ringer_skel);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		ax=f.add_subplot(2,6,3);ax.set_title('Rgetring_ring\n& ring');yy,xx=nonzero(ring);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		ax=f.add_subplot(2,6,4);ax.set_title('skel_outside_ring');yy,xx=nonzero(skel_outside_ring);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		ax=f.add_subplot(2,6,5);ax.set_title('ringer_track_portions');yy,xx=nonzero(ringer_track_portions);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		ax=f.add_subplot(2,6,6);ax.set_title('Rgetring_track\n& ringer_track_spots');yy,xx=nonzero(ringer_track_spots);imshow(filtstamp_ringer,interpolation='nearest',origin='lower left');scatter(xx,yy,edgecolors='k',facecolors='None')
		# first doing ring segments with 1 layer outside the ring excluded (gets closer to the ring), then doing it with 2 layers excluded (has advantage of not mixing detections near the ring). then if the 1layer and 2layer thing disagree I take the 2layer results (as long as they fit certain criteria)
		ring_seg,Nring_track_labels=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layer),conn8)
		ringer_track_labels=range(1,1+Nring_track_labels)
		ring_slices=scipy.ndimage.find_objects(ring_seg)
		ring_and_outer_layers2=scipy.ndimage.binary_dilation(ring_and_outer_layer,conn8,mask=outsides)
		ring_seg_layers2,Nring_track_labels_layers2=scipy.ndimage.label(Rgetring_track*logical_not(ring_and_outer_layers2),conn8)
		#if there are a ton of track pieces, then I'll go with the original mask thing
		ringer_track_labels_loop=copy(ringer_track_labels)
		xx_seg,yy_seg=array([]),array([])
		for l_bit in ringer_track_labels_loop:
			sl=ring_slices[l_bit-1]
			track_spots=ring_seg[sl]==l_bit
			ringer0_here=ringer0[sl][track_spots].any()
			if track_spots.sum()<7:
				continue
			layers2_stamp=ring_seg_layers2[sl]
			layers2_at_track=layers2_stamp[track_spots]
			layers2_at_track_labels=unique(layers2_at_track).tolist()
			try:layers2_at_track_labels.remove(0)
			except ValueError:pass
			Nl2s_possible=len(layers2_at_track_labels)
			if Nl2s_possible>1:
				l2_sizes=[]
				l2_in_orig=[]
				for l2_l in layers2_at_track_labels:
					l2_spots=layers2_stamp==l2_l
					l2_in_orig.append(ringer0[sl][l2_spots].any())
					l2_sizes.append(l2_spots.sum())
				l2_sizes=array(l2_sizes)
				l2_size_cut=l2_sizes>2
				Nl2s=sum(l2_size_cut)
				if Nl2s>=2:
					if ringer0_here and not array(l2_in_orig).any(): continue
					ringer_track_labels_add=max(ringer_track_labels)+1+arange(Nl2s_possible)
					ringer_track_labels=ringer_track_labels+ringer_track_labels_add.tolist()
					ring_seg[sl][track_spots]=0
					ringer_track_labels.remove(l_bit)
					for l2_l,ring_seg_l in zip(layers2_at_track_labels,ringer_track_labels_add):
						l2_spots=layers2_stamp==l2_l
						l2yy,l2xx=nonzero(l2_spots)
						xx_seg=append(xx_seg,l2xx)
						yy_seg=append(yy_seg,l2yy)
						ring_seg[sl][l2_spots]=ring_seg_l
					print (fl_label_str+": thing with 1layer and 2layer masks actually matters!\n")
					pltextras+='-2layer_masks'
		ringer_track_labels=asarray(ringer_track_labels)
		ring_seg_in_orig=[]
		ring_seg_maxvals=[]
		ring_seg_areas=[]
		for l_bit in ringer_track_labels:
			track_spots=ring_seg==l_bit
			ring_seg_in_orig.append(ringer0[track_spots].any())
			ring_seg_maxvals.append(filtstamp_ringer[track_spots].max())
			ring_seg_areas.append(track_spots.sum())

		ax=f.add_subplot(2,6,7)
		ax.set_title('ring_seg')
		imshow(ring_seg,interpolation='nearest',origin='lower left')
		if len(xx_seg):scatter(xx_seg,yy_seg,edgecolors='k',facecolors='None')
		ring_seg_in_orig=asarray(ring_seg_in_orig)
		ring_seg_maxvals=asarray(ring_seg_maxvals)
		ring_seg_areas=asarray(ring_seg_areas)
		#keep anything that's above twice the highest ring value or was an original masked pixel
		ring_seg_keep=(ring_seg_maxvals>max_within*2) + ring_seg_in_orig
		if ring_seg_keep.sum()>0:
			ringer_track_labels=ringer_track_labels[ring_seg_keep]
		else:
			print (fl_label_str+': if none are the originals, then take the largest and the brightest\n')
			pltextras+='-largest_and_brightest'
			try:
				max_label=ringer_track_labels[ring_seg_maxvals.argmax()]
				area_label=ringer_track_labels[ring_seg_areas.argmax()]
				ringer_track_labels=[max_label]
				if area_label!=max_label and ring_seg_areas.max()>5: ringer_track_labels.append(area_label)
			except ValueError:
				close(f);del f
				return spots_ringer, "Un-ringable holes"#if there is no max valued/max area thing, then they're all super small and
		newring=ringer0.copy() #at the very least, use the original track pixels
		Nringworms=0
		for bit_i,l_bit in enumerate(ringer_track_labels):
			track_spots=ring_seg==l_bit
			track_spots_final,included,rr=track2ring(track_spots,Rgetring_ring)
			#now extend track?!
			if not isnan(rr):
				track_spots_final,stretch_count=iter_track_stretch(track_spots_final, filtstamp_ringer,dt_times_pt01,BASE,l_ringer,star_stamp,ts_rr_cut=ring_rr_cut,name_extras=('ring_rr%.2f' % (rr,)).replace('.','pt'),rr_per_step=.2)
			else:
				track_spots_final=scipy.ndimage.binary_dilation(track_spots_final,conn8)
			newring+=track_spots_final
			ringer_yy,ringer_xx=nonzero(track_spots_final)
			try:
				ax=f.add_subplot(2,6,bit_i+8)
				ax.set_title('ringer track extension\niter='+str(bit_i))
				imshow(filtstamp_ringer,interpolation='nearest',origin='lower left')
				scatter(ringer_xx,ringer_yy,marker='o',edgecolors='k',facecolors='None',s=50)
				if rr>ring_rr_cut or isnan(rr):
					Nringworms+=1
					pltextras+='-ringworms%s' % (Nringworms)
					ax.set_title(ax.get_title()+"  (rr=%.3f>rr_cut=%.3f)" % (rr,ring_rr_cut))
			except IndexError: #if there are a lot of track pieces
				if not 'TrackPiecesEQ' in pltextras:
					pltextras+='-TrackPiecesEQ%s' % (len(ringer_track_labels))
		#if there are 2 worms, then mask entire thing!
		if Nringworms>1:
			newring+=ring_and_insides
		ringer_Fyy,ringer_Fxx=nonzero(newring)
		ax=f.add_subplot(2,6,11)
		ax.set_title('ringer track extension\nFINAL')
		imshow(filtstamp_ringer,interpolation='nearest',origin='lower left')
		scatter(ringer_Fxx,ringer_Fyy,marker='o',edgecolors='k',facecolors='None',s=50)
		ax=f.add_subplot(2,6,12)
		ax.set_title('unfiltered image')
		imshow(imstamp_ringer,interpolation='nearest',origin='lower left')
		scatter(ringer_Fxx,ringer_Fyy,marker='o',edgecolors='k',facecolors='None',s=50)
		pltextras+='-Changed'
		f.suptitle(fl_label_str+pltextras)
		f.savefig(plotdir+pltstr+pltextras)
		close(f);del f
		return newring, 0 #ringstat==0 implies all is well with ringer
	except:
		ns.update(locals())
		show();raise
#END: RING FUNCTIONS define commands for fixing rings

#START: HOLE FUNCTIONS define command for counting holes in objects
def count_hole_filled_pixels(spots):
	'''count the number of holes in the spots, and if there is a ring that isn't quite filled, then fill it and count the holes'''
	holefilledpixels=(mahotas.close_holes(spots)!=spots).sum()
	if holefilledpixels>9:
		return holefilledpixels
	spots4=mahotas.dilate(spots,conn4)
	holefilledpixels4=(mahotas.close_holes(spots4)!=spots4).sum()
	if holefilledpixels4>holefilledpixels:
		return holefilledpixels4
	spots8=mahotas.dilate(spots,conn8)
	holefilledpixels8=(mahotas.close_holes(spots8)!=spots8).sum()
	if holefilledpixels8>holefilledpixels:
		return holefilledpixels8
	holefilledpixels_options=array([holefilledpixels,holefilledpixels4,holefilledpixels8])
	return holefilledpixels_options.max()
#END: HOLE FUNCTIONS define command for counting holes in objects

#START: POLYNOMIAL FUNCTIONS define command for fitting lines and polynomials to objects
def polyfitter_specific(cosmics,polytype,degree=1):
	'''This fits a polynomial (of a specific polytype, i.e. x_of_y or y_of_x) to the True elements in cosmics.
	call it like: rr,poly,polytype=polyfitter_specific(cosmics,'x_of_y',1)'''
	try:
		yy,xx=nonzero(cosmics)
		if polytype=='y_of_x': #XY
			pXY, residualsXY, rankXY, singular_valuesXY, rcondXY = polyfit(xx,yy,degree,full=True)
			try:
				rXY=residualsXY.min()
			except ValueError:
				rXY=nan
			if isnan(rXY):
				return nan,None,None
			rr=rXY/len(xx)
			y_of_x = poly1d(pXY)
			return rr,y_of_x,'y_of_x'
		if polytype=='x_of_y': #YX
			pYX, residualsYX, rankYX, singular_valuesYX, rcondYX = polyfit(yy,xx,degree,full=True)
			try:
				rYX=residualsYX.min()
			except ValueError:
				rYX=nan
			if isnan(rYX):
				return nan,None,None
			rr=rYX/len(xx)
			x_of_y = poly1d(pYX)
			return rr,x_of_y,'x_of_y'
	except:
		ns.update(locals())
		show();raise

def polyfitter(cosmics,degree=1):
	'''This fits a polynomial to the True elements in cosmics.
	call it like: rr,poly,polytype=polyfitter(cosmics,1)'''
	try:
		yy,xx=nonzero(cosmics)
		#if cosmics is small enough, then see how oblong it is and if it's super oblong then fit with the dependent variable being the one we have more of
		if len(xx)<100:
			Yextent,Xextent=len(unique(yy)),len(unique(xx))
			Y2Xratio=Yextent/float(Xextent)
			if Y2Xratio>2.0:
				return polyfitter_specific(cosmics,'x_of_y',degree=degree)
			elif Y2Xratio<.5:
				return polyfitter_specific(cosmics,'y_of_x',degree=degree)
			#else continue with the fit
		#if cosmics is big or not oblong it continues with the usual fit here
		pXY, residualsXY, rankXY, singular_valuesXY, rcondXY = polyfit(xx,yy,degree,full=True)
		pYX, residualsYX, rankYX, singular_valuesYX, rcondYX = polyfit(yy,xx,degree,full=True)
		try:
			rXY=residualsXY.min()
		except ValueError:
			rXY=nan
		try:
			rYX=residualsYX.min()
		except ValueError:
			rYX=nan
		residual=nanmin([rXY,rYX])
		if isnan(residual):
			return nan,None,None
		rr=residual/len(xx)
		if rXY<=rYX:
			y_of_x = poly1d(pXY)
			return rr,y_of_x,'y_of_x'
		else:
			x_of_y = poly1d(pYX)
			return rr,x_of_y,'x_of_y'
	except:
		ns.update(locals())
		raise

def cosmicpoly(l,cosmics,stamp,ax,**kwargs):
	'''cosmicpoly is like polyfitter(cosmics,degree=5)'''
	try:
		yy,xx=nonzero(cosmics)
		pXY, residualsXY, rankXY, singular_valuesXY, rcondXY = polyfit(xx,yy,5,full=True)
		pYX, residualsYX, rankYX, singular_valuesYX, rcondYX = polyfit(yy,xx,5,full=True)
		try:
			rXY=residualsXY.min()
		except ValueError:
			rXY=nan
		try:
			rYX=residualsYX.min()
		except ValueError:
			rYX=nan
		residual=nanmin([rXY,rYX])
		if isnan(residual):
			return ax,nan
		rr=residual/len(xx)
		y_of_x = poly1d(pXY)
		x_of_y = poly1d(pYX)
		X=arange(xx.min(),xx.max(),.1)
		Y=arange(yy.min(),yy.max(),.1)
		ax.imshow(stamp,interpolation='nearest',origin='lower left')
		if not 'marker' in kwargs:
			kwargs['marker']='o'
		ax.scatter(xx,yy,edgecolors='k',facecolors='None',label='points',**kwargs)
		if rXY<rYX:
			ax.plot(X,y_of_x(X),'y')
			ax.plot(x_of_y(Y),Y,'r--')
		else:
			ax.plot(X,y_of_x(X),'y--')
			ax.plot(x_of_y(Y),Y,'r')
		yd,yu=yy.min()-4,yy.max()+4
		xd,xu=xx.min()-4,xx.max()+4
		ywidth=yu-yd
		xwidth=xu-xd
		if xwidth>ywidth:
			ax.set_ylim(yd,yd+xwidth)
			ax.set_xlim(xd,xu)
		elif ywidth>xwidth:
			ax.set_xlim(xd,xd+ywidth)
			ax.set_ylim(yd,yu)
		ax.set_title('label %s: residual/#points=%.3f' % (l,rr),size=12)
		return ax,rr
	except:
		ns.update(locals())
		show();raise
#END: POLYNOMIAL FUNCTIONS define command for fitting lines and polynomials to objects

#START: TRACK STRETCHING and CONNECTING
ts_count=0
def track_stretcher(cosmics,CRfiltstamp,thresh,star_stamp,stretchL_total,stretchR_total,ts_rr_cut,name_extras,rr_per_step):
	'''this fits a line to `cosmics` and stretches the mask along the line, then it determines if any of the pixels included from the stretching have counts in `CRfiltstamp` above `thresh`. If they do, then those pixels are included in the final mask and it returns `cosmics_final,1`, else it returns `cosmics,0`. It is mean to be called from within iter_track_stretch'''
	try:
		rr,poly,polytype=polyfitter(cosmics,1)
		#get spots along the line
		if rr>ts_rr_cut:
			return cosmics,0,0,rr
		#get cosmic endpoints
		cosmic_ends=cosmics*logical_not(pymorph.thin(cosmics,pymorph.endpoints(option='homotopic'),1))
		around_cosmics=scipy.ndimage.binary_dilation(cosmic_ends,structure=conn8, iterations=2) * logical_not(cosmics+star_stamp) #this way stars aren't included in pts at all!
		ayy,axx=nonzero(around_cosmics)
		if polytype=='x_of_y':
			aX=poly(ayy)
			aOffsets=(axx-aX).__abs__()
		elif polytype=='y_of_x':
			aY=poly(axx)
			aOffsets=(ayy-aY).__abs__()
		else:
			return cosmics,0,0,rr
		close_cutL=1.2+stretchL_total*rr_per_step
		close_cutR=1.2+stretchR_total*rr_per_step
		extend_track_spotsL=aOffsets<close_cutL
		extend_track_spotsR=aOffsets<close_cutR
		if not extend_track_spotsL.any() or not extend_track_spotsR.any():
			return cosmics,0,0,rr
		#get the corner spots!
		end_yy,end_xx=nonzero(cosmic_ends)
		if polytype=='x_of_y':
			end_X=poly(end_yy)
			endpts_off=(end_xx-end_X).__abs__()
		elif polytype=='y_of_x':
			end_Y=poly(end_xx)
			endpts_off=(end_yy-end_Y).__abs__()
		endpts=zip(end_yy,end_xx)
		UR=array([end[0]+end[1] for end in endpts])
		UL=array([end[0]-end[1] for end in endpts])
		LL=array([-end[0]-end[1] for end in endpts])
		LR=array([-end[0]+end[1] for end in endpts])
		close_enoughL=endpts_off<close_cutL+.5 #give it an extra 1/2 pixel so it has a chance of picking up neighbors
		close_enoughR=endpts_off<close_cutR+.5 #give it an extra 1/2 pixel so it has a chance of picking up neighbors
		Lce=close_enoughL.any()
		Rce=close_enoughR.any()
		if not Lce and not Rce:
			return cosmics,0,0,rr
		if Lce:
			endpts_Lstandard=[endpt for i,endpt in enumerate(endpts) if close_enoughL[i]]
			UR_Lstandard=UR[close_enoughL]
			UL_Lstandard=UL[close_enoughL]
			LL_Lstandard=LL[close_enoughL]
			LR_Lstandard=LR[close_enoughL]
			URpt_Lstandard=endpts_Lstandard[UR_Lstandard.argmax()]
			ULpt_Lstandard=endpts_Lstandard[UL_Lstandard.argmax()]
			LLpt_Lstandard=endpts_Lstandard[LL_Lstandard.argmax()]
			LRpt_Lstandard=endpts_Lstandard[LR_Lstandard.argmax()]
		if Rce:
			endpts_Rstandard=[endpt for i,endpt in enumerate(endpts) if close_enoughR[i]]
			UR_Rstandard=UR[close_enoughR]
			UL_Rstandard=UL[close_enoughR]
			LL_Rstandard=LL[close_enoughR]
			LR_Rstandard=LR[close_enoughR]
			URpt_Rstandard=endpts_Rstandard[UR_Rstandard.argmax()]
			ULpt_Rstandard=endpts_Rstandard[UL_Rstandard.argmax()]
			LLpt_Rstandard=endpts_Rstandard[LL_Rstandard.argmax()]
			LRpt_Rstandard=endpts_Rstandard[LR_Rstandard.argmax()]
		#make sure they are extending along the main axis of the track
		try:
			m,b=poly.coeffs #for line y=m*x+b or x=m*y+b
			if math.fabs(m)<slope_flat_cut:
				if polytype=='x_of_y':
					title_extras=' ***|srt8 UP and DOWN|*** '
					Ltype=1
					if Rce:
						UR_pt=URpt_Rstandard;UL_pt=ULpt_Rstandard
						Ux_midpt=(UR_pt[1]+UL_pt[1])/2.0
						Rxxyy_spots=extend_track_spotsR*(ayy>=max(UR_pt[0],UL_pt[0])-1)*((axx<=Ux_midpt+1)*(axx>=Ux_midpt-1)) #upper restricted
					if Lce:
						LR_pt=LRpt_Lstandard;LL_pt=LLpt_Lstandard
						Lx_midpt=(LR_pt[1]+LL_pt[1])/2.0
						Lxxyy_spots=extend_track_spotsL*(ayy<=min(LR_pt[0],LL_pt[0])+1)*((axx<=Lx_midpt+1)*(axx>=Lx_midpt-1)) #lower restricted
				elif polytype=='y_of_x':
					title_extras=' ***_srt8 RIGHT and LEFT_*** '
					Ltype=2
					if Rce:
						UR_pt=URpt_Rstandard;LR_pt=LRpt_Rstandard
						Ry_midpt=(UR_pt[0]+LR_pt[0])/2.0
						Rxxyy_spots=extend_track_spotsR*(axx>=max(UR_pt[1],LR_pt[1])-1)*((ayy<=Ry_midpt+1)*(ayy>=Ry_midpt-1)) #right restricted
					if Lce:
						UL_pt=ULpt_Lstandard;LL_pt=LLpt_Lstandard
						Ly_midpt=(UL_pt[0]+LL_pt[0])/2.0
						Lxxyy_spots=extend_track_spotsL*(axx<=min(UL_pt[1],LL_pt[1])+1)*((ayy<=Ly_midpt+1)*(ayy>=Ly_midpt-1)) #left restricted
			elif math.fabs(m)>slope_flat_cut**(-1):
				if polytype=='x_of_y':
					title_extras=' ***_srt8 RIGHT and LEFT_*** '
					Ltype=3
					if Rce:
						UR_pt=URpt_Rstandard;LR_pt=LRpt_Rstandard
						Ry_midpt=(UR_pt[0]+LR_pt[0])/2.0
						Rxxyy_spots=extend_track_spotsR*(axx>=max(UR_pt[1],LR_pt[1])-1)*((ayy<=Ry_midpt+1)*(ayy>=Ry_midpt-1)) #right restricted
					if Lce:
						UL_pt=ULpt_Lstandard;LL_pt=LLpt_Lstandard
						Ly_midpt=(UL_pt[0]+LL_pt[0])/2.0
						Lxxyy_spots=extend_track_spotsL*(axx<=min(UL_pt[1],LL_pt[1])+1)*((ayy<=Ly_midpt+1)*(ayy>=Ly_midpt-1)) #left restricted
				elif polytype=='y_of_x':
					title_extras=' ***|srt8 UP and DOWN|*** '
					Ltype=4
					if Rce:
						UR_pt=URpt_Rstandard;UL_pt=ULpt_Rstandard
						Ux_midpt=(UR_pt[1]+UL_pt[1])/2.0
						Rxxyy_spots=extend_track_spotsR*(ayy>=max(UR_pt[0],UL_pt[0])-1)*((axx<=Ux_midpt+1)+(axx>=Ux_midpt-1)) #upper restricted
					if Lce:
						LR_pt=LRpt_Lstandard;LL_pt=LLpt_Lstandard
						Lx_midpt=(LR_pt[1]+LL_pt[1])/2.0
						Lxxyy_spots=extend_track_spotsL*(ayy<=min(LR_pt[0],LL_pt[0])+1)*((axx<=Lx_midpt+1)+(axx>=Lx_midpt-1)) #lower restricted
			elif m>0:
				title_extras=' ***/UPPER RIGHT and LOWER LEFT/*** '
				Ltype=5
				if Rce:
					ur=(axx>=URpt_Rstandard[1]-1)*(ayy>=URpt_Rstandard[0]-1)
					Rxxyy_spots=extend_track_spotsR*ur
				if Lce:
					ll=(axx<=LLpt_Lstandard[1]+1)*(ayy<=LLpt_Lstandard[0]+1)
					Lxxyy_spots=extend_track_spotsL*ll
			elif m<0:
				title_extras=' ***\\UPPER LEFT and LOWER RIGHT\\*** '
				Ltype=6
				if Rce:
					lr=(axx>=LRpt_Rstandard[1]-1)*(ayy<=LRpt_Rstandard[0]+1)
					Rxxyy_spots=extend_track_spotsR*lr
				if Lce:
					ul=(axx<=ULpt_Lstandard[1]+1)*(ayy>=ULpt_Lstandard[0]-1)
					Lxxyy_spots=extend_track_spotsL*ul
		except ValueError:
			return cosmics,0,0,rr
		except AttributeError:
			return cosmics,0,0,rr
		#pick the things from Rxxyy_spots and Lxxyy_spots which have the highest value
		if Rce:
			Rxx,Ryy=axx[Rxxyy_spots],ayy[Rxxyy_spots]
			Rpts=zip(Ryy,Rxx)
			Rpts_vals=array([CRfiltstamp[o] for o in Rpts])
			Rabove_thresh=Rpts_vals>thresh
			Rinclude=(Rabove_thresh).any()
		else: Rinclude=False
		if Lce:
			Lxx,Lyy=axx[Lxxyy_spots],ayy[Lxxyy_spots]
			Lpts=zip(Lyy,Lxx)
			Lpts_vals=array([CRfiltstamp[o] for o in Lpts])
			Labove_thresh=Lpts_vals>thresh
			Linclude=(Labove_thresh).any()
		else: Linclude=False
		if not Rinclude and not Linclude:
			return cosmics,0,0,rr
		#now get edges
		cosmics_final=cosmics.copy()
		cosmics_expanded1=scipy.ndimage.binary_dilation(cosmic_ends,structure=conn8, iterations=1)
		if Rinclude:
			R_Tedge_or_Fouter=array([cosmics_expanded1[o] for o in Rpts])
			outer_above_thresh=Rabove_thresh[logical_not(R_Tedge_or_Fouter)].any()
			inner_above_thresh=Rabove_thresh[(R_Tedge_or_Fouter)].any()
			Rpts2include=set([])
			if outer_above_thresh: #then take the max outer thing and it's edges above the thresh
				out_pt=Rpts[Rpts_vals.argmax()]
				outer_surrounding=set([(out_pt[0]+mx,out_pt[1]+my) for mx,my in itertools.product([-1,0,1],[-1,0,1])])
				outer_above_thresh=set([pt for i,pt in enumerate(Rpts) if Rabove_thresh[i]])
				Rpts2include=Rpts2include.union(set.intersection(outer_above_thresh,outer_surrounding))
				outer_inner_connection=set([pt for i,pt in enumerate(Rpts) if R_Tedge_or_Fouter[i]])
				Rpts2include=Rpts2include.union(set.intersection(outer_inner_connection,outer_surrounding))
			if inner_above_thresh: #then take the max inner thing and it's edges above the thresh
				in_pt=Rpts[Rpts_vals.argmax()]
				inner_above_thresh=set([pt for i,pt in enumerate(Rpts) if Rabove_thresh[i]])
				inner_surrounding=set([(in_pt[0]+mx,in_pt[1]+my) for mx,my in itertools.product([-1,0,1],[-1,0,1])])
				Rpts2include=Rpts2include.union(set.intersection(inner_above_thresh,inner_surrounding))
			for o in Rpts2include:
				cosmics_final[o]=True
		if Linclude:
			L_Tedge_or_Fouter=array([cosmics_expanded1[o] for o in Lpts])
			outer_above_thresh=Labove_thresh[logical_not(L_Tedge_or_Fouter)].any()
			inner_above_thresh=Labove_thresh[(L_Tedge_or_Fouter)].any()
			Lpts2include=set([])
			if outer_above_thresh: #then take the max outer thing and it's edges above the thresh
				out_pt=Lpts[Lpts_vals.argmax()]
				outer_above_thresh=set([pt for i,pt in enumerate(Lpts) if Labove_thresh[i]])
				outer_surrounding=set([(out_pt[0]+mx,out_pt[1]+my) for mx,my in itertools.product([-1,0,1],[-1,0,1])])
				Lpts2include=Lpts2include.union(set.intersection(outer_above_thresh,outer_surrounding))
				outer_inner_connection=set([pt for i,pt in enumerate(Lpts) if L_Tedge_or_Fouter[i]])
				Lpts2include=Lpts2include.union(set.intersection(outer_inner_connection,outer_surrounding))
			if inner_above_thresh: #then take the max inner thing and it's edges above the thresh
				in_pt=Lpts[Lpts_vals.argmax()]
				inner_above_thresh=set([pt for i,pt in enumerate(Lpts) if Labove_thresh[i]])
				inner_surrounding=set([(in_pt[0]+mx,in_pt[1]+my) for mx,my in itertools.product([-1,0,1],[-1,0,1])])
				Lpts2include=Lpts2include.union(set.intersection(inner_above_thresh,inner_surrounding))
			for o in Lpts2include:
				cosmics_final[o]=True
		########f=figure(figsize=(11,10))
		########ax2=f.add_subplot(1,2,2)
		########ax1=f.add_subplot(10,2,19)
		########yy1,xx1=nonzero(cosmics)
		########yy2,xx2=nonzero(cosmics_final*logical_not(cosmics))
		########ax2.imshow(CRfiltstamp,interpolation='nearest',origin='lower left')
		########ax2.scatter(xx1,yy1,marker='o',edgecolors='k',facecolors='None',s=40)
		########ax2.scatter(xx2,yy2,s=35,alpha=.5,marker='x',edgecolors='w',facecolors='None')
		########xx_ends_plot=[]
		########yy_ends_plot=[]
		########if Rce:
		########	ULLRxx_Rends_plot=[pt[1] for pt in [ULpt_Rstandard,LRpt_Rstandard]]
		########	ULLRyy_Rends_plot=[pt[0] for pt in [ULpt_Rstandard,LRpt_Rstandard]]
		########	URLLxx_Rends_plot=[pt[1] for pt in [URpt_Rstandard,LLpt_Rstandard]]
		########	URLLyy_Rends_plot=[pt[0] for pt in [URpt_Rstandard,LLpt_Rstandard]]
		########	ax2.scatter(URLLxx_Rends_plot,URLLyy_Rends_plot,s=60,marker='>',edgecolors='yellow',facecolors='None',label='UR/LL')
		########	ax2.scatter(ULLRxx_Rends_plot,ULLRyy_Rends_plot,s=60,marker='>',edgecolors='purple',facecolors='None',label='UL/LR')
		########	xx_ends_plot+=ULLRxx_Rends_plot;xx_ends_plot+=URLLxx_Rends_plot
		########	yy_ends_plot+=ULLRyy_Rends_plot;yy_ends_plot+=URLLyy_Rends_plot
		########if Lce:
		########	ULLRxx_Lends_plot=[pt[1] for pt in [ULpt_Lstandard,LRpt_Lstandard]]
		########	ULLRyy_Lends_plot=[pt[0] for pt in [ULpt_Lstandard,LRpt_Lstandard]]
		########	URLLxx_Lends_plot=[pt[1] for pt in [URpt_Lstandard,LLpt_Lstandard]]
		########	URLLyy_Lends_plot=[pt[0] for pt in [URpt_Lstandard,LLpt_Lstandard]]
		########	ax2.scatter(URLLxx_Lends_plot,URLLyy_Lends_plot,s=60,marker='<',edgecolors='yellow',facecolors='None',label='UR/LL')
		########	ax2.scatter(ULLRxx_Lends_plot,ULLRyy_Lends_plot,s=60,marker='<',edgecolors='purple',facecolors='None',label='UL/LR')
		########	xx_ends_plot+=ULLRxx_Lends_plot;xx_ends_plot+=URLLxx_Lends_plot
		########	yy_ends_plot+=ULLRyy_Lends_plot;yy_ends_plot+=URLLyy_Lends_plot
		########f.suptitle('white "x"=added by stretching  ,  black "o"=there before  \n  yellow ">"=UR/LL_Rstandard , purple ">"=UL/LR_Rstandard || yellow "<"=UR/LL_Lstandard ,  purple "<"=UL/LR_Lstandard\n'+title_extras)
		########ax1.set_frame_on(False)
		########f=imagetools.AxesStripText(f,axes=[ax1],allticks=True,titles=False)
		########ax1.set_title('stretchL_total=%s\nstretchR_total=%s\nrr=%.3f\npolytype=%s\nLtype=%s\nm=%.3f\nLce=%s Linclude=%s\nRce=%s Rinclude=%s' % (stretchL_total,stretchR_total,rr,polytype,Ltype,m,Lce,Linclude,Rce,Rinclude))
		########ax2.set_xlim(min(xx_ends_plot)-5,max(xx_ends_plot)+5)
		########ax2.set_ylim(min(yy_ends_plot)-5,max(yy_ends_plot)+5)
		########NameString='pltRevise%s_stretch-TS%.4i-iter%s' % (OFB,ts_count,name_extras)
		########f=imagetools.NameFileDate(f,NameString,FileString,DateString)
		########f.savefig(plotdir+NameString)
		########close(f);del f
		global ts_count
		ts_count+=1
		return cosmics_final,Linclude,Rinclude,rr
	except:
		ns.update(locals())
		show();raise

def iter_track_stretch(cosmics, CRfiltstamp,bthresh,BASE,l,star_stamp,name_extras='',ts_rr_cut=1.8,rr_per_step=.07,track_len_cut=4):
	'''run track_stretcher over and over until it converges'''
	yy_lin,xx_lin=nonzero(cosmics)
	track_length=sqrt((xx_lin.max()-xx_lin.min())**2+(yy_lin.max()-yy_lin.min())**2)
	if track_length<track_len_cut:
		return cosmics,0
	stretch_countL=0
	stretch_countR=0
	stretch=1
	########cosmics_no_stretch=cosmics.copy() #noplot
	while stretch:
		cosmics,stretchL,stretchR,rr=track_stretcher(cosmics,CRfiltstamp,bthresh,star_stamp,stretch_countL,stretch_countR,ts_rr_cut,name_extras,rr_per_step)
		stretch_countL+=stretchL
		stretch_countR+=stretchR
		stretch=stretchL or stretchR
	stretch_count=stretch_countL+stretch_countR
	########global ts_count
	########ts_count+=1
	########if stretch_count:
	########	f=figure(figsize=(11,10))
	########	ax=f.add_subplot(1,1,1)
	########	yy1,xx1=nonzero(cosmics_no_stretch)
	########	yy2,xx2=nonzero(cosmics*logical_not(cosmics_no_stretch))
	########	ax.imshow(CRfiltstamp,interpolation='nearest',origin='lower left')
	########	ax.scatter(xx1,yy1,marker='o',edgecolors='k',facecolors='None',s=40)
	########	ax.scatter(xx2,yy2,marker='x',edgecolors='w',facecolors='None')
	########	bthresh_tag=('bthresh%.3i' % (bthresh))
	########	NameString='pltRevise%s_stretch-TS%.4i-%s-label%.4i%s' % (OFB,ts_count,bthresh_tag,l,name_extras)
	########	ax.set_title('white "x" = added by stretching\n# stretch iterations Left=%s Right=%s\nstretch threshold=%s (label=%s) rr=%.3f' % (stretch_countL,stretch_countR,bthresh_tag,l,rr))
	########	f=imagetools.NameFileDate(f,NameString,FileString,DateString)
	########	if cosmics.size>100:
	########		ax.set_xlim(min(xx1.min(),xx2.min())-3,max(xx1.max(),xx2.max())+3)
	########		ax.set_ylim(min(yy1.min(),yy2.min())-3,max(yy1.max(),yy2.max())+3)
	########	f.savefig(plotdir+NameString)
	########	close(f);del f
	########else:
	########	f=figure(figsize=(11,10))
	########	ax=f.add_subplot(1,1,1)
	########	yy1,xx1=nonzero(cosmics_no_stretch)
	########	ax.imshow(CRfiltstamp,interpolation='nearest',origin='lower left')
	########	ax.scatter(xx1,yy1,marker='o',edgecolors='k',facecolors='None',s=40)
	########	bthresh_tag=('bthresh%.3i' % (bthresh))
	########	NameString='pltRevise%s_stretch-TS%.4i-unstretchable-%s-label%.4i%s' % (OFB,ts_count,bthresh_tag,l,name_extras)
	########	ax.set_title('UNSTRETCHABLE (label=%s) rr=%.3f' % (l,rr))
	########	f=imagetools.NameFileDate(f,NameString,FileString,DateString)
	########	f.savefig(plotdir+NameString)
	########	close(f);del f
	return cosmics,stretch_count

def connector(cosmics):
	'take non-connected cosmics (that are almost connected) and connect them'
	contig_checkseg,Npieces=scipy.ndimage.label(cosmics,conn8)
	del contig_checkseg
	if Npieces<=1:
		return cosmics
	rr,poly,polytype=polyfitter(cosmics,1)
	if rr>3.0:
		return cosmics
	hull_final=skimage.morphology.convex_hull_image(cosmics) * logical_not(cosmics)
	hyy,hxx=nonzero(hull_final)
	if polytype=='x_of_y':
		hX=poly(hyy)
		hOffsets=(hxx-hX).__abs__()
	elif polytype=='y_of_x':
		hY=poly(hxx)
		hOffsets=(hyy-hY).__abs__()
	else:
		return cosmics
	if rr<.6:hull_rr=.6
	elif rr>1.2:hull_rr=1.2
	else: hull_rr=rr
	hull_extend_cosmics=hOffsets<hull_rr
	Hxx,Hyy=hxx[hull_extend_cosmics],hyy[hull_extend_cosmics]
	Hpts=zip(Hyy,Hxx)
	for o in Hpts:
		cosmics[o]=True
	return cosmics
#END: TRACK STRETCHING and CONNECTING

#START: BLENDING FUNCTIONS
def ExpandMaskAbove(image,mask,EdgeThresh):
	'''take the input mask and add in edges that are above some threshold'''
	expand_mask=scipy.ndimage.binary_dilation(mask,structure=conn8, iterations=1) #we use conn4 in step5_make_inputs_and_outputs.2.1.py
	edge_mask=expand_mask*logical_not(mask)
	edgepixels=ma.array(image,mask=logical_not(edge_mask)) #mask all non-edges
	edgeout=edgepixels>EdgeThresh #edges > bthresh = True & edges < bthresh = False
	add2mask=ma.filled(edgeout,False) #non-edges=False and edges<bthresh=False
	maskEGbthresh=mask+add2mask #maskEGbthresh=size thresholded mask OR mask edge above the EdgeThresh
	return maskEGbthresh

#set cutting parameters
blend_raise_bthresh_amount=70.0
blend_rr_cut=3.0
blend_sizediff_1vs2_cut=60
blend_slope_off_cut=.06
blend_holefilledpixels_cut=21
#SHNT: make it plot/not plot based on value of PLOT_ON_OFF
def blocked_blender(bthresh,CRfiltimage,CRll,CRslices,starbools,CRseg):
	'''take input CR detections and output a detections that have been blblend_ended (surroundings have been included in the mask if they were above bthresh) and blocked (meaning they are blocked from hitting a detected object'''
	try:
		print '\n############# START BLEND: bthresh = '+str(bthresh)+" ###################"
		blend_Niters=[];blend_ended=[]
		blended_CRseg=CRseg.copy()
		bthresh2=bthresh+blend_raise_bthresh_amount
		bthresh_raise_tag=('bthresh%.i_to_%.i' % (bthresh,bthresh+blend_raise_bthresh_amount))
		for l in CRll:
			sl=CRslices[l-1]
			sle=imagetools.slice_expand(sl,100)
			CRfiltstamp=CRfiltimage[sle]
			SBstamp=starbools[sle]
			cosmics1=blended_CRseg[sle]==l
			cosmics2=cosmics1.copy()
			#iterate a max of 100 times to expand to neighboring pixels above bthresh
			for i in range(100): #limit to 100 iterations
				cosmicsb4=cosmics1.copy()
				cosmics1=ExpandMaskAbove(CRfiltstamp,cosmicsb4,bthresh)
				if (cosmics1==cosmicsb4).all():
					blend_ended.append(0)
					break
				if SBstamp[cosmics1].any():
					blend_ended.append(1)
					break
			else:
				blend_ended.append(2)
			blend_Niters.append(i+1)
			#do this iteration again at a higher threshold
			for i in range(100): #limit to 100 iterations
				cosmics2b4=cosmics2.copy()
				cosmics2=ExpandMaskAbove(CRfiltstamp,cosmics2b4,bthresh2)
				if (cosmics2==cosmics2b4).all():
					break
				if SBstamp[cosmics2].any():
					break
			# if the higher threshold result is way smaller, then consider returning the 2nd one
			size_diff12=cosmics1.sum()-cosmics2.sum()
			if size_diff12>blend_sizediff_1vs2_cut:
				#START: now make sure sum(8)>9 just to make sure
				open8_cosmics=scipy.ndimage.binary_opening(cosmics1,conn8)
				open8_Nspots= float(open8_cosmics.sum())
				open8_frac=open8_Nspots/cosmics1.sum()
				if open8_frac<.03: #if less than 3% of the pixels in cosmics1 are open8 pixels, then cosmics1 isn't a blob, so stick with cosmics1 (rather than switching to cosmics2)
					if PLOT_ON_OFF:
						f=figure(figsize=(12,9));f.add_subplot(121);title('FINAL: cosmics1');yy,xx=nonzero(cosmics1);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
						f.add_subplot(122);title('cosmics2');yy,xx=nonzero(cosmics2);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
						f.suptitle('Stick with cosmics1\nfailed: open8_frac=%.3f < .03' % (open8_frac,))
						f.savefig(plotdir+'pltRevise%s_failed_raise_thresh_%s-No_Open8-label%.4i' % (OFB,bthresh_raise_tag,l))
						close(f);del f
					#END: now make sure sum(8)>9 just to make sure
				else:
					rr2,poly2,polytype2=polyfitter(cosmics2,1)
					if isnan(rr2) or rr2>blend_rr_cut: #if the linefit looks like crap for cosmics2, then it probably will for cosmics1, so we assume it's not a line and take 2nd mask
						if open8_frac>.2: #if greater than 20% of the image is open8, then use cosmics2:
							#stretch cosmics2 if it's linear
							if rr2<1.2:
								cosmics2_addons,count_stretch2=iter_track_stretch(cosmics2, CRfiltstamp,bthresh*.4,BASE,l,SBstamp,name_extras='_InBlender2',ts_rr_cut=2.0,rr_per_step=.04)
								cosmics2[cosmics2_addons*cosmics1]=True
								cosmics2=connector(cosmics2)
							else:
								count_stretch2=0
							#make sure picking cosmics2 doesn't mean that we're breaking the track into smaller pieces
							contig_checkseg,Npieces2=scipy.ndimage.label(cosmics2,conn8)
							contig_checkseg,Npieces1=scipy.ndimage.label(cosmics1,conn8)
							if Npieces2<=Npieces1: #if picking cosmics2 doesn't break the track up into smaller pieces, then continue
								if PLOT_ON_OFF:
									f=figure(figsize=(12,9));f.add_subplot(121);title('cosmics1');yy,xx=nonzero(cosmics1);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
									f.add_subplot(122);title('FINAL: cosmics2');yy,xx=nonzero(cosmics2);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
									f.suptitle('Going from cosmics1 to cosmics2 (count_stretch2=%s)!\npassed: open8_frac=%.3f < .03\npassed: rr2=%.3f>blend_rr_cut=%.3f\npassed: open8_frac=%.3f >.2' % (count_stretch2,open8_frac,rr2,blend_rr_cut,open8_frac))
									f.savefig(plotdir+'pltRevise%s_passed_raise_thresh_%s-simple-label%.4i' % (OFB,bthresh_raise_tag,l))
									close(f);del f
								cosmics1=cosmics2
						else:
							if PLOT_ON_OFF:
								f=figure(figsize=(12,9));f.add_subplot(121);title('FINAL: cosmics1');yy,xx=nonzero(cosmics1);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
								f.add_subplot(122);title('cosmics2');yy,xx=nonzero(cosmics2);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
								f.suptitle('Stick with cosmics1!\npassed: open8_frac=%.3f < .03\npassed: rr2=%.3f>blend_rr_cut=%.3f\nfailed open8_frac=%.3f >.2' % (open8_frac,rr2,blend_rr_cut,open8_frac))
								f.savefig(plotdir+'pltRevise%s_failed_raise_thresh_%s-simple-label%.4i' % (OFB,bthresh_raise_tag,l))
								close(f);del f
					else: #if the line fit is decent for cosmics2, try the line fit for cosmics1
						yy2,xx2=nonzero(cosmics2)
						slope2=poly2.coeffs[0]
						#try:
						#	slope2=poly2.coeffs[0]
						#except ValueError:
						#	pass
						#except AttributeError:
						#	pass
						yy1,xx1=nonzero(cosmics1*logical_not(cosmics2))
						yy3,xx3=nonzero(cosmics1)
						if polytype2=='y_of_x': #if rXY2<rYX2:
							pXY1, residualsXY1, rankXY1, singular_valuesXY1, rcondXY1 = polyfit(xx1,yy1,1,full=True)
							slope1=pXY1[0]
							slope_off=abs(slope2-slope1)
							rr1=residualsXY1[0]/len(xx1)
							poly1 = poly1d(pXY1)
							X3=arange(xx3.min(),xx3.max(),.1)
							pltxx1,pltyy1=X3,poly1(X3)
							pltxx2,pltyy2=X3,poly2(X3)
						else: #if polytype2=='x_of_y': #if rYX2<rXY2:
							pYX1, residualsYX1, rankYX1, singular_valuesYX1, rcondYX1 = polyfit(yy1,xx1,1,full=True)
							slope1=pYX1[0]
							slope_off=abs(slope2-slope1)
							rr1=residualsYX1[0]/len(xx1)
							poly1 = poly1d(pYX1)
							Y3=arange(yy3.min(),yy3.max(),.1)
							pltxx1,pltyy1=poly1(Y3),Y3
							pltxx2,pltyy2=poly2(Y3),Y3
						if isnan(rr1) or rr1>(blend_rr_cut+1.0) or slope_off>blend_slope_off_cut:#if the linefit looks like crap for cosmics1, then we assume it's not a line and take 2nd mask
							#stretch cosmics2 if it's linear
							if rr2<1.2:
								cosmics2_addons,count_stretch2=iter_track_stretch(cosmics2, CRfiltstamp,bthresh*.4,BASE,l,SBstamp,name_extras='_InBlender2',ts_rr_cut=2.0,rr_per_step=.04)
								cosmics2[cosmics2_addons*cosmics1]=True
								cosmics2=connector(cosmics2)
							else:
								count_stretch2=0
							#make sure picking cosmics2 doesn't mean that we're breaking the track into smaller pieces
							contig_checkseg,Npieces2=scipy.ndimage.label(cosmics2,conn8)
							contig_checkseg,Npieces1=scipy.ndimage.label(cosmics1,conn8)
							if Npieces2<=Npieces1: #if picking cosmics2 doesn't break the track up into smaller pieces, then continue
								if PLOT_ON_OFF:
									f=figure(figsize=(12,9));f.add_subplot(121);title('cosmics1');yy,xx=nonzero(cosmics1);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
									f.add_subplot(122);title('FINAL: cosmics2');yy,xx=nonzero(cosmics2);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
									f.suptitle('Going from cosmics1 to cosmics2! (count_stretch2=%s)\npassed: open8_frac=%.3f < .03\npassed: rr2=%.3f>blend_rr_cut=%.3f\npassed: rr1=%.3f>blend_rr_cut+1=%.3f or slope_off=%.3f>blend_slope_off_cut=%.3f' % (count_stretch2,open8_frac,rr2,blend_rr_cut,rr1,blend_rr_cut+1.0,slope_off,blend_slope_off_cut))
									f.savefig(plotdir+'pltRevise%s_passed_raise_thresh_%s-higher_thresh_much_smaller-label%.4i' % (OFB,bthresh_raise_tag,l))
									close(f);del f
								cosmics1=cosmics2
						elif PLOT_ON_OFF: #else cosmics1 stays the same because I determine that they are both lines along the same trajectory!
							f=figure()
							f.suptitle('Stick with cosmics1!\npassed: open8_frac=%.3f < .03\npassed: rr2=%.3f>blend_rr_cut=%.3f\nfailed: rr1=%.3f>blend_rr_cut=%.3f and slope_off=%.3f>blend_slope_off_cut=%.3f' % (open8_frac,rr2,blend_rr_cut,rr1,blend_rr_cut,slope_off,blend_slope_off_cut))
							ax=f.add_subplot(1,1,1)
							ax.imshow(CRfiltstamp,interpolation='nearest',origin='lower left')
							ax.scatter(xx1,yy1,marker='o',edgecolors='k',facecolors='None',label='cosmics1')
							ax.scatter(xx2,yy2,marker='x',edgecolors='w',facecolors='None',label='cosmics2')
							ax.plot(pltxx2,pltyy2,'w')
							ax.plot(pltxx1,pltyy1,'k--')
							ax.set_ylim(yy3.min()-3,yy3.max()+3)
							ax.set_xlim(xx3.min()-3,xx3.max()+3)
							f.savefig(plotdir+'pltRevise%s_failed_raise_thresh_%s-SameTrajectory-label%.4i' % (OFB,bthresh_raise_tag,l))
							close(f);del f
			#get the number hole pixels using the simple way of doing it rather than using `holefilledpixels=count_hole_filled_pixels(cosmics1)`
			if bthresh==bthresh1: #only do the holefilled cut raise if it's the first time using blender
				holefilledpixels=(scipy.ndimage.binary_fill_holes(cosmics1)!=cosmics1).sum()
				if holefilledpixels>blend_holefilledpixels_cut:
					if PLOT_ON_OFF:
						f=figure(figsize=(12,9));f.add_subplot(121);title('cosmics1');yy,xx=nonzero(cosmics1);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
						f.add_subplot(122);title('FINAL: cosmics2');yy,xx=nonzero(cosmics2);imshow(CRfiltstamp,interpolation='nearest',origin='lower left');scatter(xx,yy,marker='o',edgecolors='k',facecolors='None')
						f.suptitle('Go from cosmics1 to cosmics2!')
						f.savefig(plotdir+'pltRevise%s_passed_raise_thresh_%s-holefilledpixels-label%.4i' % (OFB,bthresh_raise_tag,l))
						close(f);del f
					print "holefilledpixels: ",holefilledpixels
					cosmics1=cosmics2
			blended_CRseg[sle][cosmics1]=l
		#loop ends if mask (1) converges, (2) hits a star, or (3) hits 100 iterations
		blend_ended=array(blend_ended)
		print "times converged: ",(blend_ended==0).sum()
		print "times hit star : ",(blend_ended==1).sum()
		print "times 100 iters: ",(blend_ended==2).sum()
		print "at bthresh %.3i it converges after a mean of %.3f iterations" % (bthresh,mean(blend_Niters))
		print "# iterations=",blend_Niters
		print '############# END BLEND: bthresh = '+str(bthresh)+" ###################\n"
		return blended_CRseg
	except:
		ns.update(locals())
		show();raise
#END: BLENDING FUNCTIONS

#START: LABEL FUNCTIONS
def plotlabels(ll,segments=None,slices=None,params=None,background=None):
	'''plot stamps of all of the masks in the label list `ll`.'''
	try:
		if segments==None:segments=BBCRseg
		if slices==None: slices=BBCRslices
		if params==None: params=ll
		if background==None: background=image
		patches=[]
		for l in ll:
			patches.append(imagetools.slice_expand(tuple(slices[l-1]),3))
		fig=figure(figsize=(22,13.625))
		Nlabels=len(ll)
		if Nlabels<=4:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(2,2))
			textsize=14
		elif Nlabels<=9:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(3,3))
			textsize=13
		elif Nlabels<=16:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(4,4))
			textsize=12
		elif Nlabels<=25:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(5,5))
			textsize=11
		elif Nlabels<=6*7:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(6,7))
			textsize=10
		elif Nlabels<=6*8:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(6,8))
			textsize=10
		elif Nlabels<=7*8:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(7,8))
			textsize=9
		elif Nlabels<=7*9:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(7,9))
			textsize=9
		else:
			fig,axes = imagetools.AxesList(fig=fig,compact=.02,shape=(8,10))
			fig.subplots_adjust(top=.95)
			textsize=8
		if len(params)==Nlabels:
			for ax,sl,title,l in zip(axes,patches,params,ll):
				##spots=segments[sl]>0
				spots=segments[sl]==l
				yy,xx=nonzero(spots)
				stamp=background[sl]
				ax.imshow(stamp,interpolation='nearest',origin='lower left')
				ax.scatter(xx,yy,marker='o',edgecolors='k',facecolors='None',label='points')
				ax.set_title(str(title),size=10)
		elif len(params)==len(slices):
			for ax,sl,l in zip(axes,patches,ll):
				title=params[l-1]
				##spots=segments[sl]>0
				spots=segments[sl]==l
				yy,xx=nonzero(spots)
				stamp=background[sl]
				ax.imshow(stamp,interpolation='nearest',origin='lower left')
				ax.scatter(xx,yy,marker='o',edgecolors='k',facecolors='None',label='points')
				ax.set_title(str(title),size=10)
		else:
			raise Exception('gotta have len(params)==len(slices) or len(params)==len(ll)')
		return fig
	except:
		ns.update(locals())
		show();raise

def reset_labels(prob_labels,segs2reset):
	'''take in a current image and an older image and reset the masks in `prob_labels` to how they were in the older image'''
	CRsegX=segs2reset.copy()
	for l in prob_labels:
		spots=segs2reset==l
		CRsegX[spots]=0 #reset the problem labels to zero
		newspots=spots*detections0
		CRsegX[newspots]=l #reset the problem labels to their original value
	return CRsegX
#END: LABEL FUNCTIONS

PLOT_ON_OFF=0 #0=plotting off 1=plotting on

if __name__ == "__main__":
	if len(sys.argv)<2:
		sys.exit()
	if not os.path.isfile(sys.argv[1]):
		print "sys.argv[1]=",sys.argv[1]
		raise Exception(sys.argv[1]+" is not a file!")
	else:
		fl=sys.argv[1]
	print "starting file=",fl
	try:
		PLOT_ON_OFF=sys.argv[2]
	except:
		pass

	#START: iter0
	t0=time.time()
	#get the image for `fl`
	image=imagetools.GetImage(fl)
	back_im=scipy.stats.scoreatpercentile(image,48)
        CRfl=pyfits.open(fl)
        header=CRfl[0].header
        OBJECT=header['MYOBJ']
        FILTER=header['FILTER']
	CCDnum=header['IMAGEID']
	if CCDnum==7: PLOT_ON_OFF=1

	#iter0: take the original files2check and prepare them for blending
	files2check=[]
	flname=os.path.basename(fl).split('.')[0]
	BASE=os.path.basename(fl).split('OCF.')[0]
	#get cosmics images
	OFB='%s_%s_%s' % (OBJECT,FILTER,BASE,)
	CR_segfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE,)
	CR_filtfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE,)
	CRfitsfl=pyfits.open(CR_filtfl)
	rms=CRfitsfl[0].header['MYRMS']
	rms_bins=arange(15,90,5)
	bthresh1_bin=digitize([rms],rms_bins)[0] #no "-1" here because I want the top-edge of the bin, not the bottom edge
	bthresh1=rms_bins[bthresh1_bin]
	dt=CRfitsfl[0].header['CRN_DT']*rms#; ft=CRfitsfl[0].header['CRN_FT']*rms
	dt_times_pt01=int(dt*.01+1) #this is like a ceiling function
	CRfiltimage=CRfitsfl[0].data
	CRfiltheader=CRfitsfl[0].header
	CRfitsfl.close()
	#get stars images
	star_segfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_stars/SEGMENTATION_CRN-stars_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,flname,)
	starseg0=asarray(imagetools.GetImage(star_segfl),dtype=int)
	star0_slices=scipy.ndimage.find_objects(starseg0 )
	Nstars=starseg0.max()
	#remove stars that don't at least have a square in them
	for i in range(1,Nstars+1):
		sl=star0_slices[i-1]
		spots=starseg0[sl]==i
		openspots=scipy.ndimage.binary_opening(spots,array([[1,1],[1,1]]))
		if not openspots.any():
			starseg0[sl][spots]=0
	#now add in things with 100 pixels above saturation level (in case they aren't there yet)
	sat=image>28000
	sat_big=skimage.morphology.remove_small_objects(sat,80,connectivity=2) #conn8
	sat_seg,Nsat_labels=mahotas.label(sat_big,conn8)
	sat_slices=scipy.ndimage.find_objects(sat_seg)
	s2=skimage.morphology.star(2)
	#add very large regions near saturation that have an s2 shape in them
	for i,sl in enumerate(sat_slices):
		l=i+1
		spots=sat_seg[sl]==l
		if mahotas.open(spots,s2).any():
			starseg0[sl][spots]=Nstars+l
	#setup final star position array
	starbools=mahotas.dilate(starseg0>Nstars,conn4)#dilate only those large saturation areas
	starbools+=starseg0>0
	#get cosmics and remove the ones that overlap with the stars (these will be replaced later, but I don't want them to be blended!)
	CRseg0=asarray(imagetools.GetImage(CR_segfl),dtype=int)
	CRll_for_loop=arange(CRseg0.max())+1
	CRll=CRll_for_loop.tolist()
	CRslices=scipy.ndimage.find_objects(CRseg0)
	CRoverlapSTAR=zeros(CRseg0.shape,dtype=bool) #these are almost entirely saturation spikes!
	CRoverlapSTAR_Ncosmics_mask_at_end=0
	CRoverlapSTAR_Npixels_mask_at_end=0
	for l in CRll_for_loop:
		CRsl=CRslices[l-1]
		CRspots=CRseg0[CRsl]==l
		CR_on_star_frac=starbools[CRsl][CRspots].mean()
		if CR_on_star_frac>0:
			#test if it is a major hit or a minor hit
			if CR_on_star_frac<0.5:
				CRsl2=imagetools.slice_expand(CRsl,1)
				STARspots=starbools[CRsl2]
				STARspots2=scipy.ndimage.binary_dilation(STARspots,conn8)
				CRspots2=CRseg0[CRsl2]==l
				CR_on_dilated_star_frac=STARspots2[CRspots2].mean()
				if CR_on_dilated_star_frac<0.5: #if it's a minor hit, then remove the overlap and continue
					overlap=CRspots2*STARspots2
					CRseg0[CRsl2][overlap]=0
					continue
			#always remove a major hit from list of CRs
			CRll.remove(l)
			CRseg0[CRsl][CRspots]=0
			if CRspots.sum()>9: #if big enough, then remove it later
				CRoverlapSTAR_Ncosmics_mask_at_end+=1
				CRoverlapSTAR_Npixels_mask_at_end+=CRspots.sum()
				CRoverlapSTAR[CRsl][CRspots]=1

	CRll=asarray(CRll)
	#get the info needed to define the blender function
	#start saving output
	compare_dir='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/'
	detections0=CRseg0>0
	WOblendCRfiltimage=CRfiltimage.copy()
	WOblendCRfiltimage[detections0]=-2000
	#save original file
	hdu=pyfits.PrimaryHDU(image)
	hdu.header=CRfiltheader
	fl_original=compare_dir+'BBout_ORIGINAL_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE)
	hdu.writeto(fl_original,clobber=True)
	files2check.append(fl_original)
	#save old CR mask file
	hdu=pyfits.PrimaryHDU(WOblendCRfiltimage)
	hdu.header=CRfiltheader
	fl_woblend=compare_dir+'BBout_WOblend_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE)
	hdu.writeto(fl_woblend,clobber=True)
	files2check.append(fl_woblend)
	#END: iter0

	#START: iter1
	t1=time.time()
	#iter1: run the blender!
	bthresh1_tag=('bthresh%.3i' % (bthresh1))
	CRblended1=blocked_blender(bthresh1,CRfiltimage,CRll,CRslices,starbools,CRseg0.copy())
	BBCRmask=CRblended1>0
	print "Masked",float((BBCRmask).sum())/detections0.sum(),"times the number of original pixels"

	BBCRseg,BBCR_Nlabels=scipy.ndimage.label(BBCRmask,conn8)
	BBCRslices_b4=scipy.ndimage.find_objects(BBCRseg)
	BBCRlabels=arange(BBCR_Nlabels)+1
	#get the number of holes in each detection
	BBCRslices=[]
	Nholefilledpixels=[]
	for l,sl in zip(BBCRlabels,BBCRslices_b4):
		spots=BBCRseg[sl]==l
		Nholefilledpixels.append(count_hole_filled_pixels(spots))
		sl3=imagetools.slice_expand(sl,3)
		BBCRslices.append(sl3)
	Nholefilledpixels=asarray(Nholefilledpixels)
	BBCRregs=skimage.measure.regionprops(BBCRseg)
	area=array([BBCRregs[i].area for i in range(BBCR_Nlabels)])

	#select cut parameters
	rr_iterN_cut=3.1 #masks with poly residual/#pts>=this will have their threshold raised
	holefilledpixels_cut=5 #masks with >this pixels will be sent to the ringer function
	open_cut=11;open_rr_cut=.8

	#iter1: select the masks big enough to be able to fail cuts
	big_enough=area>8
	area2polyfit=area[big_enough]
	BBCRlabels2polyfit=BBCRlabels[big_enough]
	#iter1: find detections from iter1 that fail the polynomial fit cut (add to list of bad labels if poly doesn't fit well)
	cut_labels2=[];cut_details2=[]
	########count=0
	for i,(k,size_k) in enumerate(zip(BBCRlabels2polyfit,area2polyfit)):
		########Nax= i % 9 + 1
		########if Nax==1:
		########	count+=1
		########	if i!=0:
		########		f=imagetools.AxesStripText(f,allticks=True,titles=False)
		########		f.savefig(plotdir+'pltRevise%s_bad_labels-polyfit_num%.3i' % (OFB,count))
		########		close(f);del f
		########	f=figure(figsize=(14,14))
		########ax=f.add_subplot(3,3,Nax)
		sl=BBCRslices[k-1]
		cosmics=BBCRseg[sl]==k
		########stamp=image[sl]
		########ax,rr_k=cosmicpoly(k,cosmics,stamp,ax)
		rr_k,poly_k,polytype_k=polyfitter(cosmics,degree=5)
		open8_cosmics=scipy.ndimage.binary_opening(cosmics,conn8)
		open8_Nspots=open8_cosmics.sum()
		open8_frac=float(open8_Nspots)/size_k
		if rr_k>rr_iterN_cut and open8_frac>.03:
			cut_labels2.append(k)
			cut_details2.append("rr=%.2f>%.2f and open8_frac=%.3f>.03" % (rr_k,rr_iterN_cut,open8_frac))
		elif open8_Nspots>open_cut:
			openS_cosmics=scipy.ndimage.binary_opening(cosmics,connS)
			openS_Nspots=openS_cosmics.sum()
			if openS_Nspots>open_cut and rr_k>open_rr_cut:
				cut_labels2.append(k)
				cut_details2.append("sum(S)=%s>%s sum(8)=%s>%s & rr=%.2f>%.2f" % (openS_Nspots,open_cut,open8_Nspots,open_cut,rr_k,open_rr_cut))
				########ax.set_title(ax.get_title().replace('residual/#points','rr')+'\nsum(S)=%s sum(8)=%s' % (openS_Nspots,open8_Nspots),size=10.5)
	########else:
	########	f=imagetools.AxesStripText(f,allticks=True,titles=False)
	########	f.savefig(plotdir+'pltRevise%s_bad_labels-polyfit_num%.3i' % (OFB,count))
	########	close(f);del f
	#iter1: find detections from iter1 that fail the number of filled pixels cut
	hole_cuts=Nholefilledpixels>holefilledpixels_cut
	fillLL=BBCRlabels[hole_cuts]
	for l in fillLL:
		##yy,xx=nonzero(spots)
		##track_length=sqrt((xx.max()-xx.min())**2+(yy.max()-yy.min())**2)
		##if track_length>150
		if l in cut_labels2:
			ind=cut_labels2.index(l)
			cut_labels2.pop(ind)
			cut_details2.pop(ind)
	params=['label=%s #holes=%s' % (hole_l, hole_N) for hole_l,hole_N in zip(fillLL,Nholefilledpixels[hole_cuts])]
	if PLOT_ON_OFF:
		f=plotlabels(fillLL,params=params)
		f.savefig(plotdir+'pltRevise%s_bad_labels-holes_1before-unfiltered' % (OFB,))
		close(f);del f
		f=plotlabels(fillLL,params=params,background=CRfiltimage)
		f.savefig(plotdir+'pltRevise%s_bad_labels-holes_1before-filtered' % (OFB,))
		close(f);del f
	#iter1: END

	#BEGIN: RING
	Nring_fixed1=0
	for l in fillLL:
		sl2=BBCRslices[l-1]
		spots_ring=BBCRseg[sl2]==l
		if PLOT_ON_OFF: newring,ringstat=ringer(spots_ringer=spots_ring.copy(),l_ringer=l,filtstamp_ringer=CRfiltimage[sl2],imstamp_ringer=image[sl2],seg0stamp_ringer=CRseg0[sl2],star_stamp=starbools[sl2])
		else: newring,ringstat=ringer_noplot(spots_ringer=spots_ring.copy(),l_ringer=l,filtstamp_ringer=CRfiltimage[sl2],imstamp_ringer=image[sl2],seg0stamp_ringer=CRseg0[sl2],star_stamp=starbools[sl2])
		if ringstat==0:
			Nring_fixed1+=1
			BBCRseg[sl2][spots_ring]=0
			BBCRseg[sl2][newring]=l
		else:
			cut_labels2.append(l)
			cut_details2.append(ringstat)
	#moved the "after" plot to the end
	#END: RING

	#START: iter2
	cut_labels={2:cut_labels2}
	cut_details={2:cut_details2}
	CRblendeds={1:BBCRseg.copy()}
	bthreshs={2:60.0,3:80.0,4:100.0,5:120.0,6:140.0,7:160.0,8:180.0}
	iterN_final=max(bthreshs.keys())
	star_ERASE=zeros(CRseg0.shape,dtype=bool)
	antidrop_extras=''
	iterN_stats={}
	for iterN in range(2,iterN_final+1):
		exec "t%s=time.time()" % (iterN)
		iterN_stats[iterN]={'DONE-swallowed':0,'DONE-PREVsplit':0,'DONE-Multiple Ringers':0,'NEXT-rr':0,'NEXT-ring failed':0,'NEXT-open':0,'NEXT-rr=nan size>9 open8=0':0,'REMOVED-ERASE':0,'DONE-ERASE FAILED':0,'DONE-PASSED ALL':0}
		rr_iterN_cut+=.1
		#iter2: take detections from iter1 that fail the cuts and reset them to the way they were at iter0
		CRsegN=reset_labels(cut_labels[iterN],CRblendeds[iterN-1]) #reset cut_labels2 from CRblendeds[iterN-1] to CRseg0
		bthresh_tag=('bthresh%.3i' % (bthreshs[iterN]))
		#iter2: take cut detections from iter1 (which have been reset to iter0) and reblend them at a higher thresh
		CRblendeds[iterN]=blocked_blender(bthreshs[iterN],CRfiltimage,cut_labels[iterN],BBCRslices,starbools,CRsegN)
		CRblendeds_slices=scipy.ndimage.find_objects(CRblendeds[iterN])
		del CRsegN
		print "had in iter1: ",(CRblendeds[1]>0).sum()
		print "now have in iter"+str(iterN)+": ", (CRblendeds[iterN]>0).sum()
		#iter2: plot detections from iter2 and determine if they pass the iter3 cuts or not
		count=1;cut_labels[iterN+1]=[];cut_details[iterN+1]=[]
		if PLOT_ON_OFF: f=figure(figsize=(22,13.625))
		for i,probl in enumerate(cut_labels[iterN]):
			title_extras=''
			Nax= i % 9 + 1
			if Nax==1:
				if i!=0:
					if PLOT_ON_OFF:
						f.suptitle('orange "X" = original masked spots \t white "X" = masked spots when blending at bthresh=%.3i\nblack "o" = masked spots after raising non-poly cuts to bthresh=%.3f' % (bthresh1,bthreshs[iterN],))
						f=imagetools.AxesStripText(f,allticks=True,titles=False)
						f=imagetools.AxesCompact(f,.1)
						f.savefig(plotdir+'pltRevise%s_anti-drop_%s-%slabel_group_num%.3i' % (OFB,bthresh_tag,antidrop_extras,count))
						close(f);del f
						f=figure(figsize=(22,13.625))
					antidrop_extras=''
					count+=1
			sl=CRblendeds_slices[probl-1]
			if sl==None: #if this label was swallowed by another label, then skip it!
				iterN_stats[iterN]['DONE-swallowed']+=1
				continue
			#iter2: RING now do the ringer thing!
			sl2=imagetools.slice_expand(sl,3)
			iterNmask=CRblendeds[iterN][sl2]==probl #change this so plot looks right
			if not iterNmask.any(): #if this label was swallowed by another label, then skip it!
				iterN_stats[iterN]['DONE-swallowed']+=1
				continue
			holefilledpixels=count_hole_filled_pixels(iterNmask)
			run_ring_bool= holefilledpixels>holefilledpixels_cut
			if run_ring_bool:
				if PLOT_ON_OFF: newring,ringstat=ringer(spots_ringer=iterNmask.copy(),l_ringer=probl,filtstamp_ringer=CRfiltimage[sl2],imstamp_ringer=image[sl2],seg0stamp_ringer=CRseg0[sl2],star_stamp=starbools[sl2])
				else: newring,ringstat=ringer_noplot(spots_ringer=iterNmask.copy(),l_ringer=probl,filtstamp_ringer=CRfiltimage[sl2],imstamp_ringer=image[sl2],seg0stamp_ringer=CRseg0[sl2],star_stamp=starbools[sl2])
				if ringstat==0:
					CRblendeds[iterN][sl2][iterNmask]=0
					CRblendeds[iterN][sl2][newring]=probl
					title_extras+=" Used Ring(stat=0)"
					iterNmask=newring
					holefilledpixels=count_hole_filled_pixels(iterNmask)
				else:
					title_extras+=" Used Ring(stat!=0)"
			else:ringstat=0
			#iter2: get needed info for the BLOB cut!
			blended_only_spots= iterNmask.copy()
			open8_blended_only_spots=scipy.ndimage.binary_opening(blended_only_spots,conn8)
			openS_blended_only_spots=scipy.ndimage.binary_opening(blended_only_spots,connS)
			open8_Nspots= open8_blended_only_spots.sum();openS_Nspots=openS_blended_only_spots.sum()
			del open8_blended_only_spots,openS_blended_only_spots
			#iter2: STRETCH now do the iter_track_stretch thing!
			slE=imagetools.slice_expand(sl,100)
			if bthreshs[iterN]>=80:
				iterNmaskE=CRblendeds[iterN][slE]==probl
				cosmics,stretch_count=iter_track_stretch(iterNmaskE.copy(),CRfiltimage[slE] ,bthreshs[iterN]-20,BASE,probl,starbools[slE],name_extras="_ADloop",rr_per_step=.1,ts_rr_cut=1.0,track_len_cut=13)
				if stretch_count:
					stretch_pixels=cosmics*logical_not(iterNmaskE)
					stretch_unnecessary=(CRblendeds[iterN][slE].copy()>0) * stretch_pixels
					print "number of stretched pixels already covered=",stretch_unnecessary.sum()," of total ",stretch_pixels.sum()
					stretch_necessary=stretch_pixels * logical_not(stretch_unnecessary)
					CRblendeds[iterN][slE][stretch_necessary]=probl
					title_extras+=" Used Stretch"
			#iter2: do the plotting by using a square slice within the slE slice!
			slsq=imagetools.slice_square(scipy.ndimage.find_objects(asarray(CRblendeds[iterN][slE]==probl,dtype=int))[0])
			slsq3=imagetools.slice_expand(slsq,3)
			stamp=image[slE][slsq3]
			iter1mask=BBCRseg[slE][slsq3]==probl
			iterNmask_slsq3=CRblendeds[iterN][slE][slsq3]==probl #this is iterNmask, but in the slsq3 form
			iter0mask=iterNmask_slsq3*(CRseg0[slE][slsq3]>0)
			yy0,xx0=nonzero(iter0mask)
			masksize0=len(xx0)
			#iter2: determine if iter2 detections pass the iter3 cuts or not
			masksize=iterNmask_slsq3.sum()
			open8_frac=float(open8_Nspots)/masksize
			if PLOT_ON_OFF:
				ax=f.add_subplot(3,3,Nax)
				yy1,xx1=nonzero(iter1mask)
				ax.scatter(xx1,yy1,marker='x',color='w',lw=.5,alpha=.5)
				ax,rr_i=cosmicpoly(probl,iterNmask_slsq3,stamp,ax,marker='s',s=40)
				if isnan(rr_i):
					ax.set_title('label %s: rr=nan' % (probl,))
					yyN,xxN=nonzero(iterNmask_slsq3)
					ax.imshow(stamp,interpolation='nearest',origin='lower left')
					ax.scatter(xxN,yyN,marker='o',edgecolors='k',facecolors='None')
				ax.scatter(xx0,yy0,marker='x',color='orange',s=50)
				ax.set_ylim(0,slsq3[0].stop-slsq3[0].start);ax.set_xlim(0,slsq3[1].stop-slsq3[1].start)
			else:
				rr_i,poly_i,polytype_i=polyfitter(iterNmask_slsq3,degree=5)
			#START: PREVsplit
			autopass=False
			if not (run_ring_bool and ringstat==0): #if we didn't successfully run the ringer function
				#check if the mask has been split into 2 pieces
				iterPREVmask_slsq3=CRblendeds[iterN-1][slE][slsq3]==probl #this is iterNmask, but for the N-1 iteration
				contig_checkseg,contig_check_NlabelsN=scipy.ndimage.label(iterNmask_slsq3,conn8)
				contig_checkseg,contig_check_NlabelsPREV=scipy.ndimage.label(iterPREVmask_slsq3,conn8)
				names="iterN=",iterN,"probl=",probl,"contig_check_NlabelsN=",contig_check_NlabelsN,"contig_check_NlabelsPREV=",contig_check_NlabelsPREV
				del contig_checkseg
				if contig_check_NlabelsN>contig_check_NlabelsPREV: #if label has been split-up take the last one
					Nopen8_iterPREVmask_slsq3=scipy.ndimage.binary_opening(iterPREVmask_slsq3,conn8).sum()
					Ntotal_iterPREVmask_slsq3=iterPREVmask_slsq3.sum()
					open8_frac_PREV=float(Nopen8_iterPREVmask_slsq3)/Ntotal_iterPREVmask_slsq3
					if open8_frac<=.3 and open8_frac_PREV<open8_frac+.2:
						#open8_iterPREVmask_slsq3=scipy.ndimage.binary_opening(iterPREVmask_slsq3,conn8)
						#iterPREV_8less=iterPREVmask_slsq3-open8_iterPREVmask_slsq3
						#contig_checkseg,contig_check_NlabelsPREV_8less=scipy.ndimage.label(iterPREV_8less,conn8)
						#if contig_check_NlabelsN>contig_check_NlabelsPREV_8less: #if label has been split-up take the last one
						iterN_stats[iterN]['DONE-PREVsplit']+=1
						CRblendeds[iterN][slE][slsq3][iterPREVmask_slsq3]=probl
						iterNmask_slsq3=iterPREVmask_slsq3
						if PLOT_ON_OFF:ax.set_title('label=%s DONE!!! PREV declared iterN-1 better!\nI dont want to break this up into more pieces!' % (probl))
						print ('label=%s DONE!!! PREV declared iterN-1 better!\nI dont want to break this up into more pieces!' % (probl))
						antidrop_extras+='PREVsplit-'
						autopass=True
			#END: PREVsplit
			if not autopass and ((ringstat=="Circle of Cosmics" or ringstat=="none in square pattern") and iterN>=3 and open8_frac<.2):
				iterN_stats[iterN]['DONE-Multiple Ringers']+=1
				more_title_extras="DONE!!! Circle of Cosmics rr=%.2f size=%s sum(8)=%s sum(S)=%s open8_frac=%.2f<.2" % (rr_i, iterNmask_slsq3.sum(), open8_Nspots, openS_Nspots,open8_frac)
				antidrop_extras+='CosmicCircle-'
			elif not autopass and (open8_frac>.03 and rr_i>rr_iterN_cut): #if not autopass and (more than 3% of the pixels in cosmics are open8 pixels, then cosmics is a blob, so raise the thresh
				iterN_stats[iterN]['NEXT-rr']+=1
				cut_labels[iterN+1].append(probl)
				cut_details[iterN+1].append("rr=%.2f>%.2f open8_frac=%.2f>.03" % (rr_i,rr_iterN_cut,open8_frac))
				more_title_extras=('this iter (%s of %s) details: ' % (iterN+1,iterN_final))+cut_details[iterN+1][-1]
			elif not autopass and (ringstat!=0 and holefilledpixels>holefilledpixels_cut):
				iterN_stats[iterN]['NEXT-ring failed']+=1
				cut_labels[iterN+1].append(probl)
				cut_details[iterN+1].append(ringstat)
				more_title_extras=('this iter (%s of %s) details: ' % (iterN+1,iterN_final))+cut_details[iterN+1][-1]
			elif not autopass and (open8_Nspots>open_cut and openS_Nspots>open_cut and rr_i>open_rr_cut):
				iterN_stats[iterN]['NEXT-open']+=1
				cut_labels[iterN+1].append(probl)
				cut_details[iterN+1].append("sum(S)=%s>%s sum(8)=%s>%s rr=%.2f>%.2f" % (openS_Nspots,open_cut,open8_Nspots,open_cut,rr_i,open_rr_cut))
				more_title_extras=('this iter (%s of %s) details: ' % (iterN+1,iterN_final))+cut_details[iterN+1][-1]
			elif not autopass and (isnan(rr_i) and masksize>9 and not open8_Nspots):
				iterN_stats[iterN]['NEXT-rr=nan size>9 open8=0']+=1
				cut_labels[iterN+1].append(probl)
				cut_details[iterN+1].append("rr=nan size>9 open8_Nspots=0")
				more_title_extras=('this iter (%s of %s) details: ' % (iterN+1,iterN_final))+cut_details[iterN+1][-1]
			elif not autopass and (isnan(rr_i) and masksize>9 and masksize0<3 and open8_frac>.6): #if not autopass and (this is true then it might be a star!
				#make sure that the original mask pixels are all 4-connected and that the mask isn't in 2 pieces
				contig_checkseg,contig_check_NlabelsN=scipy.ndimage.label(iterNmask_slsq3,conn8)
				contig_checkseg,contig_check_Nlabels0=scipy.ndimage.label(iter0mask,conn8)
				del contig_checkseg
				contig_check_Nlabels=max(contig_check_NlabelsN,contig_check_Nlabels0)
				#make sure that the hottest pixel and the 2nd hottest are next to one another and both are 8 connected with the 3rd hottest
				stampmax=stamp[iterNmask_slsq3].max()
				maxspot=stamp==stampmax
				stamp_no_max=stamp.copy();stamp_no_max[maxspot]=0;stamp_no_max[logical_not(iterNmask_slsq3)]=0
				maxspot2=stamp_no_max==stamp_no_max.max()
				max_and_2nd_next=sum(maxspot2*binary_dilation(maxspot))>0
				max_or_2=maxspot2+maxspot
				stamp_no_max_or_2=stamp.copy();stamp_no_max_or_2[max_or_2]=0;stamp_no_max_or_2[logical_not(iterNmask_slsq3)]=0
				maxspot3=stamp_no_max_or_2==stamp_no_max_or_2.max()
				max_and_2nd_next_to_3rd=sum(max_or_2*binary_dilation(maxspot3,conn8))>1
				if max_and_2nd_next and max_and_2nd_next_to_3rd and contig_check_Nlabels==1: #if this is true then it might be a star! (this should drastically reduce the "pac-man effect"!)
					iterN_stats[iterN]['REMOVED-ERASE']+=1
					more_title_extras="ERASED!!! (should be star) rr=nan open8_frac=%.2f>.6 Nlabels=1" % (open8_frac,)
					more_title_extras+="\nPASSED all OF: max_and_2nd_next=%s max_and_2nd_next_to_3rd=%s" % (max_and_2nd_next,max_and_2nd_next_to_3rd ) #if this is true then it might be a star! (this should drastically reduce the "pac-man effect"!)
					star_ERASE[slE][slsq3][iterNmask_slsq3]=1
				else:
					iterN_stats[iterN]['DONE-ERASE FAILED']+=1
					more_title_extras="DONE!!! Didn't Pass ERASE (not star) rr=nan open8_frac=%.2f>.6" % (open8_frac,)
					more_title_extras+="\nFAILED one OF:Nlabels=%s>1 max_and_2nd_next=%s max_and_2nd_next_to_3rd=%s" % (contig_check_Nlabels,max_and_2nd_next,max_and_2nd_next_to_3rd )
			else:
				iterN_stats[iterN]['DONE-PASSED ALL']+=1
				more_title_extras="DONE!!! rr=%.2f iterNmask.sum()=%s sum(8)=%s sum(S)=%s open8_frac=%.2f" % (rr_i, iterNmask_slsq3.sum(), open8_Nspots, openS_Nspots,open8_frac)
				#START: PREV
				#PREV: check how the mask compares to the old mask!
				########	else:
				########		#check and see if the deleted part was clean (not conn8,etc.)!
				########		PREV_removed=iterPREVmask_slsq3-iterNmask_slsq3
				########		PREV_important=PREV_removed-(PREV_removed*mahotas.sobel(iterNmask_slsq3))
				########		open8_PREV_important=scipy.ndimage.binary_opening(PREV_important,conn8)
				########		N_PREV_important=float(PREV_important.sum())
				########		N8_PREV_important=float(open8_PREV_important.sum())
				########		open8_frac_PREV=N8_PREV_important/N_PREV_important
				########		if open8_frac_PREV<.5 and (N_PREV_important-N8_PREV_important)>3:
				########			PREV_good_removal=scipy.ndimage.binary_opening(PREV_important,conn8)+scipy.ndimage.binary_opening(PREV_important,connS)
				########			PREV_putback=PREV_important-PREV_good_removal
				########			skimage.morphology.remove_small_objects(PREV_putback,3,connectivity=2,in_place=True) #conn8
				########			if PREV_putback.sum()>3:
				########				PREV_seg,N_PREV_segs=scipy.ndimage.label(PREV_putback,conn8)
				########				around_iterN=scipy.ndimage.binary_dilation(iterNmask_slsq3,conn8)
				########				PREV_segs_nearby=unique(PREV_seg[around_iterN]).tolist()
				########				try:PREV_segs_nearby.remove(0)
				########				except ValueError:pass
				########				if PREV_segs_nearby:
				########					Nmask_old=iterNmask_slsq3.copy()
				########					add_xx,add_yy=[],[]
				########					for PREV_l in PREV_segs_nearby:
				########						add_l=PREV_seg==PREV_l
				########						l_yy,l_xx=nonzero(add_l)
				########						add_xx+=l_xx.tolist()
				########						add_yy+=l_yy.tolist()
				########						iterNmask_slsq3[add_l]=True
				########						print "added %s to label=%s" % (add_l.sum(),probl)
				########					#now add the labels from #PREV_segs_nearby to the mask
				########					f_PREV=figure(figsize=(10,12))
				########					ax_PREV=f_PREV.add_subplot(111)
				########					ax_PREV.imshow(stamp,interpolation='nearest',origin='lower left')
				########					yy_PREV,xx_PREV=nonzero(Nmask_old)
				########					ax_PREV.scatter(xx_PREV,yy_PREV,marker='x',s=60,edgecolors='w',facecolors='none',label='Nmask_old')
				########					ax_PREV.scatter(add_xx,add_yy,s=70,marker='x',edgecolors='purple',facecolors='none',label='actually put back')
				########					#yy_PREV,xx_PREV=nonzero(PREV_important)
				########					#scatter(xx_PREV,yy_PREV,marker='x',edgecolors='w',facecolors='none',label='PREV_important')
				########					yy_PREV,xx_PREV=nonzero(PREV_good_removal)
				########					ax_PREV.scatter(xx_PREV,yy_PREV,marker='o',edgecolors='k',facecolors='k',label='PREV_good_removal')
				########					yy_PREV,xx_PREV=nonzero(PREV_putback)
				########					ax_PREV.scatter(xx_PREV,yy_PREV,s=70,marker='s',edgecolors='purple',facecolors='none',label='PREV_putback')
				########					legend()
				########					f_PREV.suptitle('pltRevise%s_PREV-%s-label%.4i' % (OFB,bthresh_tag,probl))
				########					f_PREV=imagetools.AxesCompact(f_PREV,.1)
				########					f_PREV.savefig(plotdir+'pltRevise%s_PREV-%s-label%.4i' % (OFB,bthresh_tag,probl))
				########					antidrop_extras+='PREVputback-'
				#END: PREV
			if PLOT_ON_OFF: ax.set_title(ax.get_title()+'\n'+more_title_extras+title_extras+('\nlast iter (%s of %s) details: ' % (iterN,iterN_final))+cut_details[iterN][i],size=10)
		if PLOT_ON_OFF:
			f.suptitle('orange "X" = original masked spots \t white "X" = masked spots when blending at bthresh=%.3i\nblack "o" = masked spots after raising non-poly cuts to bthresh=%.3f' % (bthresh1,bthreshs[iterN],))
			f=imagetools.AxesStripText(f,allticks=True,titles=False)
			f=imagetools.AxesCompact(f,.1)
			f.savefig(plotdir+'pltRevise%s_anti-drop_%s-%slabel_group_num%.3i' % (OFB,bthresh_tag,antidrop_extras,count))
			antidrop_extras=''
			close(f);del f
	#ERASE the removed stars
	CRblendeds[iterN_final][star_ERASE]=0
	#iter2: this is it, all I need to do is to reset anything that's filled. Just to be safe
	BBCRblend_comparable=CRblendeds[iterN_final].copy()
	BBCRblend_comparable=asarray(BBCRblend_comparable,dtype=int)
	#Save Erased Stars
	hdu=pyfits.PrimaryHDU(asarray(star_ERASE,dtype=int))
	hdu.header=CRfiltheader
	fl_erase=compare_dir+'BB_ERASED_'+bthresh1_tag+'_BBCR_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE)
	hdu.writeto(fl_erase,clobber=True)
	files2check.append(fl_erase)

	#RING: plot rings, the "after" version
	if PLOT_ON_OFF:
		f=plotlabels(fillLL,segments=BBCRblend_comparable,slices=BBCRslices,params=params)
		f.savefig(plotdir+'pltRevise%s_bad_labels-holes_2after' % (OFB,))
		close(f);del f
	#END: iter2

	#START: LastStretch
	tLS=time.time()
	#last step should be to fit a line for each cosmic and connect any close co-linear tracks
	LastStretchmask=CRblendeds[iterN_final].copy()>0
	LastStretchseg,LastStretch_Nlabels=scipy.ndimage.label(LastStretchmask,conn8)
	LastStretchslices=scipy.ndimage.find_objects(LastStretchseg)
	LastStretchregs=skimage.measure.regionprops(LastStretchseg)
	LastStretcharea=array([LastStretchregs[i].area for i in range(LastStretch_Nlabels)])
	LastStretchlabels=arange(1,LastStretch_Nlabels+1)
	BIGll=LastStretchlabels[LastStretcharea>6]
	LastStretch_rr_cut=1.8
	LastStretch_Ncosmics_added=0
	LastStretch_Npixels_added=[]
	for l in BIGll:
		sl_l=imagetools.slice_expand(LastStretchslices[l-1],20)
		seg_l=LastStretchseg[sl_l]
		spots=seg_l==l
		yy_lin,xx_lin=nonzero(spots)
		track_length=sqrt((xx_lin.max()-xx_lin.min())**2+(yy_lin.max()-yy_lin.min())**2)
		xx_plot=arange(xx_lin.min(),xx_lin.max(),.1)
		yy_plot=arange(yy_lin.min(),yy_lin.max(),.1)
		rr,poly,polytype=polyfitter(spots,1)
		if rr<LastStretch_rr_cut and track_length>5:
			ayy,axx=nonzero((seg_l>0)*logical_not(spots))
			if polytype=='x_of_y':
				aX=poly(ayy)
				aOffsets=(axx-aX).__abs__()
			elif polytype=='y_of_x':
				aY=poly(axx)
				aOffsets=(ayy-aY).__abs__()
			extend_track_spots=aOffsets<LastStretch_rr_cut
			Npixels=extend_track_spots.sum()
			if Npixels:
				LastStretch_Ncosmics_added+=1
				LastStretch_Npixels_added.append(Npixels)
				star_stamp=starbools[sl_l]
				stretched_spots,stretch_count=iter_track_stretch(spots.copy(),CRfiltimage[sl_l] ,dt_times_pt01,BASE,l,star_stamp,name_extras='_LastStretch',ts_rr_cut=1.8,rr_per_step=.2)
				fill_these=LastStretchseg[sl_l][stretched_spots]==0
				LastStretchseg[sl_l][stretched_spots][fill_these]=l
	LastStretch_Npixels_added=asarray(LastStretch_Npixels_added)
	#END: LastStretch

	#START: CR/star overlap
	tOverlap=time.time()
	#setup final masks which include the CR/star overlap
	BBCRmask_final=LastStretchseg>0
	BBCRmask_final[CRoverlapSTAR]=True #put spots where CRseg0 and starseg overlap back into final mask (this will mainly include more saturation spikes)
	BBCRimage_final=image.copy()
	BBCRimage_final[BBCRmask_final]=0 #CRs=0 and CRseg0/starseg overlap=0 too
	#plot this to make sure I'm not making an aweful mistake
	BBCRimage_plot_comp=image.copy()
	BBCRimage_plot_comp[LastStretchseg>0]=0 #just the CRs=0
	if PLOT_ON_OFF:
		f=imagetools.ImageWithSpots([BBCRimage_plot_comp,BBCRimage_final],name1='image with masks from before the CR-star overlap was replaced', name2='image with CR-star overlap masked',mode='alpha')
		f.savefig(plotdir+'pltRevise%s_CR-star_overlap' % (OFB,))
		close(f);del f
	#END: CR/star overlap

	#START: 400
	t400=time.time()
	#now add on the stuff that you only pick-up with a very low threshold (mainly for the low seeing objects)
	CR_filtfl_ft400=CR_filtfl.replace('_CRN-cosmics','_FT400_CRN-cosmics')
	CRfilt_ft400=imagetools.GetImage(CR_filtfl_ft400)
	BBCRmask_final_copy=BBCRmask_final.copy()
	CR400=CRfilt_ft400>400
	CRseg_400_start,CR_400_Nlabels=scipy.ndimage.label(CR400,conn8)
	CRslices_400=scipy.ndimage.find_objects(CRseg_400_start)
	CRregs_400=skimage.measure.regionprops(CRseg_400_start,intensity_image=CRfilt_ft400)
	maxval_400=array([CRregs_400[i].max_intensity for i in range(CR_400_Nlabels)])
	eccentricity_400=array([CRregs_400[i].eccentricity for i in range(CR_400_Nlabels)])
	area_400=array([CRregs_400[i].area for i in range(CR_400_Nlabels)])
	CRll_400=arange(CR_400_Nlabels)+1
	ok_label_400=[]
	s2t_400=[]
	BBCR_frac_400=[]
	for l,size_l in zip(CRll_400,area_400):
		sl=imagetools.slice_expand(CRslices_400[l-1],2)
		spots=CRseg_400_start[sl]==l
		sl2_height,sl2_width=spots.shape
		yy,xx=nonzero(spots)
		spots_beside_track=scipy.ndimage.binary_dilation(spots,conn4)*logical_not(spots)
		beside_track_mean=(image[sl][spots_beside_track]-back_im).mean()
		track_mean=(image[sl][spots]-back_im).mean()
		side2track_ratio=beside_track_mean/track_mean
		s2t_400.append(side2track_ratio)
		BBCR_frac_400.append(BBCRmask_final_copy[sl][spots].mean())
		if sl2_width<6 and sl2_height>200 and (sl2_height/sl2_width)>25:ok_label_400.append(False) #get rid of saturation spikes
		elif starbools[sl][spots].any():ok_label_400.append(False)
		elif (xx==xx[0]).all():ok_label_400.append(False)#get rid of str8 up and down stuff!
		else:ok_label_400.append(True)
	BBCR_frac_400=array(BBCR_frac_400)
	s2t_400=array(s2t_400)
	ok_label_400=array(ok_label_400)
	s2t_400_cutval=.33
	eccentricity_400_cutval=.88
	area_400_cutval=5
	maxval_400_cutval=2000.0
	standard_cut_400=ok_label_400*(s2t_400<s2t_400_cutval)*(eccentricity_400>eccentricity_400_cutval)*(area_400>area_400_cutval)*(maxval_400>maxval_400_cutval)
	fives_cut_400=ok_label_400*(eccentricity_400>.91)*(area_400==5)*(maxval_400>3500)*(s2t_400<s2t_400_cutval)
	fours_cut_400=ok_label_400*(eccentricity_400>.95)*(area_400==4)*(maxval_400>3500)*(s2t_400<s2t_400_cutval)
	all_cut_400=standard_cut_400+fives_cut_400+fours_cut_400#+brighter_circular_cut_400
	CRseg_400_final=CRseg_400_start.copy()
        for l in CRll_400[logical_not(all_cut_400)]:
                sl=CRslices_400[l-1]
                spots=CRseg_400_final[sl]==l
                CRseg_400_final[sl][spots]=0
        for l in CRll_400[all_cut_400]:
                sl=CRslices_400[l-1]
                sl_l=imagetools.slice_expand(sl,25)
                spots=CRseg_400_final[sl_l]==l
                star_stamp=starbools[sl_l]
		try:stretched_spots,stretch_count=iter_track_stretch(spots.copy(),CRfilt_ft400[sl_l] ,dt_times_pt01*2,BASE,l,star_stamp,name_extras='_400',rr_per_step=.25)
		except ValueError:continue
                if stretch_count:
			BBCR_frac_l=BBCRmask_final_copy[sl_l][stretched_spots].mean()
			if BBCR_frac_l<BBCR_frac_400[l-1]: #only update things if it's better
				BBCR_frac_400[l-1]=BBCR_frac_l
				CRseg_400_final[sl_l][stretched_spots]=l
				CRslices_400[l-1]=sl_l
        #params=["e=%.2f max=%.1f frac_done=%.2f\ns2t=%.2f (.35 cut)" % (ecc,maxval,fc,s2t) for ecc, maxval,fc,s2t in zip(eccentricity_400,maxval_400,BBCR_frac_400,s2t_400)]
        params=["e=%.2f max=%.1f\ns2t=%.2f (<.33)" % (ecc,maxval,s2t) for ecc,maxval,s2t in zip(eccentricity_400,maxval_400,s2t_400)]
	tryitllS=CRll_400[standard_cut_400*(BBCR_frac_400<.9)]
	if len(tryitllS) and PLOT_ON_OFF:
		f=plotlabels(tryitllS,segments=CRseg_400_final,slices=CRslices_400,params=params,background=image)
		f=imagetools.AxesStripText(f,allticks=True,titles=False)
		f.savefig(plotdir+'pltRevise%s_extras_standard_cut_400' % (OFB,))
		close(f);del f
	#GalFix# does the s2t cut do anything?
	standard_cut_400_NOT_s2t=ok_label_400*(s2t_400>s2t_400_cutval)*(eccentricity_400>eccentricity_400_cutval)*(area_400>area_400_cutval)*(maxval_400>maxval_400_cutval)
	tryitllS_NOT_s2t=CRll_400[standard_cut_400_NOT_s2t*(BBCR_frac_400<.9)]
	if len(tryitllS_NOT_s2t) and PLOT_ON_OFF:
		f=plotlabels(tryitllS_NOT_s2t,segments=CRseg_400_final,slices=CRslices_400,params=params,background=image)
		f=imagetools.AxesStripText(f,allticks=True,titles=False)
		f.savefig(plotdir+'pltRevise%s_extras_standard_cut_400_NOT_s2t' % (OFB,))
		close(f);del f
	tryit=fives_cut_400*logical_not(standard_cut_400)*(BBCR_frac_400<.9)
	tryitll5=CRll_400[tryit]
	if len(tryitll5) and PLOT_ON_OFF:
		f=plotlabels(tryitll5,segments=CRseg_400_final,slices=CRslices_400,params=params,background=image)
		f=imagetools.AxesStripText(f,allticks=True,titles=False)
		f.savefig(plotdir+'pltRevise%s_extras_fives_cut_400' % (OFB,))
		close(f);del f
	tryit=fours_cut_400*logical_not(standard_cut_400)*(BBCR_frac_400<.9)
	tryitll4=CRll_400[tryit]
	if len(tryitll4) and PLOT_ON_OFF:
		f=plotlabels(tryitll4,segments=CRseg_400_final,slices=CRslices_400,params=params,background=image)
		f=imagetools.AxesStripText(f,allticks=True,titles=False)
		f.savefig(plotdir+'pltRevise%s_extras_fours_cut_400' % (OFB,))
		close(f);del f

	ll_400_final=tryitll4.tolist()+tryitll5.tolist()+tryitllS.tolist()
	totally_new_400=0
	for l in ll_400_final:
		fc=BBCR_frac_400[l-1]
		if fc==0.0: totally_new_400+=1
	#END: 400

	#START: save results
	tsave=time.time()
	FINALmask=BBCRmask_final.copy()
        for l in ll_400_final:
                sl=CRslices_400[l-1]
                spots=CRseg_400_final[sl]==l
                FINALmask[sl][spots]=True
	FINALimage=image.copy()
	FINALimage[FINALmask]=0 #CRs=0 and CRseg0/starseg overlap=0 too
	FINALseg,FINAL_Nlabels=scipy.ndimage.label(FINALmask,conn8)
	hdu=pyfits.PrimaryHDU(FINALimage)
	hdu.header=CRfiltheader
	fl_revised=compare_dir+'BBrevised_'+bthresh1_tag+'_BBCR_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE)
	hdu.writeto(fl_revised,clobber=True)
	files2check.append(fl_revised)
	#files2check.append(compare_dir+'BBrevised_bfrac0pt0100_BBCR_%s_%s.%s_wjb-170.fits' % (OBJECT,FILTER,BASE))
	#save output mask for bonnpipeline code
	CR_newsegfl=CR_segfl.replace('SEGMENTATION_CRN-cosmics','SEGMENTATION_BB_CRN-cosmics')
	hdu=pyfits.PrimaryHDU(FINALseg)
	hdu.header=CRfiltheader
	hdu.writeto(CR_newsegfl ,clobber=True)
	tend=time.time()
	#END: save results

	#START: print stats!
	times_start=asarray([t0, t1, t2, t3, t4, t5, t6, t7, t8, tLS, tOverlap, t400, tsave, tend])
	things=['iter0','iter1','iter2','iter3','iter4','iter5','iter6','iter7','iter8','LastStretch','CRonSTAR','FT400','SAVE']
	times_took=(times_start[1:]-times_start[:-1])/60.0
	time_total=(tend-t0)/60.0
	time_percent=times_took/time_total*100
	thing_times=[str(round(tt,2)) for tt in times_took]
	thing_time_percent=["("+str(round(tt,0))+"%)" for tt in time_percent]
	end_str_print=''
	#**set PLOT_ON_OFF=1**
	BBstat_str="|***$$$~~~: "+"BB stats for the file="+fl+" :***$$$~~~|"
	BBstat_len=len(BBstat_str)-2
	BBstat_details="|***$$$~~~: MYSEEING=%.2f EXPTIME=%i RMS=%.2f " % (header['MYSEEING'],header['EXPTIME'],rms)
	nl= BBstat_details+" %"+str(BBstat_len-len(BBstat_details)-10)+"s"
	detections1=BBCRseg>0
	end_str_print+= "\n"+"|"+"-"*BBstat_len+"|"+"\n"+BBstat_str+"\n"+nl % (" ")+":***$$$~~~|"+"\n|"+"-"*BBstat_len+"|"
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| iter0| # cosmics before blending :"+ str(CRseg0.max())
	end_str_print+= "\n"+"| iter0| # masked pixels before blending :"+ str(detections0.sum())+ " %="+ str(detections0.mean())
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| iter1| # cosmics after blending #1 :"+ str(BBCRseg.max())
	end_str_print+= "\n"+"| iter1| # masked pixels after blending #1 :"+ str(detections1.sum())+" %="+ str(detections1.mean())
	end_str_print+= "\n"+"| iter1| # that are big enough (area>8) to be considered in raise thresh cut:"+ str(big_enough.sum())+" %="+ str( big_enough.mean())
	end_str_print+= "\n"+"| iter1| # with large holes that will be sent to raise thresh cut:"+ str(hole_cuts.sum())+ " of those this many were fixed:"+ str(Nring_fixed1)
	end_str_print+= "\n"+"| iter1| # with bad rr+ str( or not great rr and open8 and openS+ str( or ringer failed (i.e. masks considered in iterN):"+ str(len(cut_labels2))
	end_str_print+= "\n|\n| iterN| iterations 2 thru 8 "
	done_keys=asarray(["DONE-Multiple Ringers", "DONE-swallowed", "DONE-PASSED ALL", "DONE-PREVsplit", "DONE-ERASE FAILED"])
	next_keys=asarray([ "NEXT-open", "NEXT-ring failed", "NEXT-rr", "NEXT-rr=nan size>9 open8=0"])
	iterN_stats_all={"DONE-swallowed":0,"DONE-PREVsplit":0,"DONE-Multiple Ringers":0,"NEXT-rr":0,"NEXT-ring failed":0,"NEXT-open":0,"NEXT-rr=nan size>9 open8=0":0,"REMOVED-ERASE":0,"DONE-ERASE FAILED":0,"DONE-PASSED ALL":0}
	done_all=0; next_all=0
	for iterN in range(2,iterN_final+1):
		next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
		done=0; next=0
		for key in sort(iterN_stats[iterN].keys()):
			iterN_stats_all[key]+=iterN_stats[iterN][key]
			if 'DONE' in key: done+=iterN_stats[iterN][key]
			if 'NEXT' in key: next+=iterN_stats[iterN][key]
		done_all+=done;next_all+=next
		done_str_total="| iter%s| %s DONE: " % (iterN,done)
		removed_str_total="| iter%s| %s REMOVED-ERASED STAR CANDIDATES " % (iterN,iterN_stats[iterN]['REMOVED-ERASE'])
		next_str_total="| iter%s| %s NEXT: " % (iterN,next)
		done_vals=asarray([iterN_stats[iterN][key] for key in done_keys])
		next_vals=asarray([iterN_stats[iterN][key] for key in next_keys])
		done_str_pieces=["("+str(i+1)+": "+dk.replace("DONE-","")+") == "+str(iterN_stats[iterN][dk]) for i,dk in enumerate(done_keys[done_vals.argsort()[::-1]])]
		done_str=done_str_total+" ".join(done_str_pieces)
		next_str_pieces=["("+str(i+1)+": "+dk.replace("NEXT-","")+") == "+str(iterN_stats[iterN][dk]) for i,dk in enumerate(next_keys[next_vals.argsort()[::-1]])]
		next_str=next_str_total+" ".join(next_str_pieces)
		end_str_print+= "\n|"+next_time_line+"|\n"+done_str
		end_str_print+= "\n"+next_str
		end_str_print+= "\n"+removed_str_total
	else: 
		end_str_print+= "\n|\n| iterN| iterations 2 thru 8 totals (NEXT stats aren't all that meaningful here)"
		done_str_total="| iter%s| %s DONE: " % ("N",done_all)
		removed_str_total="| iter%s| %s REMOVED-ERASED STAR CANDIDATES " % ("N",iterN_stats_all["REMOVED-ERASE"])
		next_str_total="| iter%s| %s NEXT: " % ("N",next_all)
		done_vals=asarray([iterN_stats_all[key] for key in done_keys])
		next_vals=asarray([iterN_stats_all[key] for key in next_keys])
		done_str_pieces=["("+str(i+1)+": "+dk.replace("DONE-","")+") == "+str(iterN_stats_all[dk]) for i,dk in enumerate(done_keys[done_vals.argsort()[::-1]])]
		done_str=done_str_total+' '.join(done_str_pieces)
		next_str_pieces=["("+str(i+1)+": "+dk.replace("NEXT-","")+") == "+str(iterN_stats_all[dk]) for i,dk in enumerate(next_keys[next_vals.argsort()[::-1]])]
		next_str=next_str_total+" ".join(next_str_pieces)
		end_str_print+= "\n"+done_str
		end_str_print+= "\n"+next_str
		end_str_print+= "\n"+removed_str_total
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| LastStretch| Masked a total of this many cosmics: "+ str(LastStretch_Ncosmics_added)
	end_str_print+= "\n"+"| LastStretch| of which an average of this # of pixels was added on: "+ str(LastStretch_Npixels_added.mean())
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| CRonSTAR| Masked a total of this many cosmics: "+ str(CRoverlapSTAR_Ncosmics_mask_at_end)
	end_str_print+= "\n"+"| CRonSTAR| of which an average of this # of pixels was added on: "+ str(CRoverlapSTAR_Npixels_mask_at_end/CRoverlapSTAR_Ncosmics_mask_at_end)
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| FT400| Masked a total of this many cosmics: "+ str(len(ll_400_final))
	end_str_print+= "\n"+"| FT400| of which these many were totally new: "+ str(totally_new_400)
	next_time_line = (' '.join([things.pop(0),'took',thing_times.pop(0),'minutes',thing_time_percent.pop(0)])).rjust(BBstat_len)
	end_str_print+= "\n|"+next_time_line+"|\n| FINAL| Total cosmics+sat spikes masked: "+ str(FINAL_Nlabels)
	TOTAL_BBCR=FINAL_Nlabels-CRoverlapSTAR_Ncosmics_mask_at_end
	RATE_BBCR=TOTAL_BBCR/header["EXPTIME"]
	end_str_print+= "\n"+"| FINAL| Total cosmics masked: "+str(TOTAL_BBCR)
	end_str_print+= "\n"+"| FINAL| cosmics masked per second exposed: "+str(RATE_BBCR)
	end_str_print+= "\n"+"|"+"-"*BBstat_len+"|"
	#asciiable data
	end_str_print+= "\n"+"BBCR_stats %s %s %.2f %.2f %s %i %.2f %i %i %i %i %i" % (BASE,header["FILTER"],header["MYSEEING"],RATE_BBCR,TOTAL_BBCR,header["EXPTIME"],rms,iterN_stats_all["REMOVED-ERASE"],FINAL_Nlabels,CRoverlapSTAR_Ncosmics_mask_at_end,totally_new_400, LastStretch_Ncosmics_added)
	#ascii_names=["BASE","FILTER","SEEING","RATE_BBCR","TOTAL_BBCR","EXPTIME","RMS","ERASED","TOTAL","CRonSTAR","FT400_new","LastStretch"]
	#ascii_vals= (BASE,header["FILTER"],header["MYSEEING"],RATE_BBCR,TOTAL_BBCR,header["EXPTIME"],rms,iterN_stats_all["REMOVED-ERASE"],FINAL_Nlabels,CRoverlapSTAR_Ncosmics_mask_at_end,totally_new_400, LastStretch_Ncosmics_added)
	#end_str_print+= "\n"+"ascii %s\t%s\t%.2f\t%.2f\t%s\t%i\t%.2f\t%i\t%i\t%i\t%i\t%i" % (BASE,header["FILTER"],header["MYSEEING"],RATE_BBCR,TOTAL_BBCR,header["EXPTIME"],rms,iterN_stats_all["REMOVED-ERASE"],FINAL_Nlabels,CRoverlapSTAR_Ncosmics_mask_at_end,totally_new_400, LastStretch_Ncosmics_added)
	#end_str_print+= "\n"+"\nascii_BB", BASE,header["FILTER"],header["MYSEEING"],RATE_BBCR,TOTAL_BBCR,header["EXPTIME"],rms,iterN_stats_all["REMOVED-ERASE"],FINAL_Nlabels,CRoverlapSTAR_Ncosmics_mask_at_end,totally_new_400, LastStretch_Ncosmics_added
	end_str_print+= "\n"+"\nds9 -zscale -tile mode column "+" ".join(files2check)+" -zscale -lock frame image -lock crosshair image -geometry 2000x2000 &"
	end_str_print+= "\n"+"\ndone with file="+fl
	#END: end_str_print+= "\n"+stats!
	print end_str_print

