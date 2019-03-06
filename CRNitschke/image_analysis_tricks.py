#! /usr/bin/env python
import sys
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
connS=array([[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]],dtype=bool)
import astropy
from astropy.io import ascii
from copy import deepcopy as cp
from numpy import histogram
import os
#import new image tools
import pymorph
import skimage
from skimage import measure
import mahotas

#########import simplecv
########import statsmodels
########from random import random
########import statsmodels.api as smapi
########from statsmodels.formula.api import ols
########import statsmodels.graphics as smgraphics
########import cv2
########import cv

#######get transform stuff########
import skimage.transform
from skimage.transform import warp
tform_left= skimage.transform.SimilarityTransform(translation=(1, 0))
tform_right = skimage.transform.SimilarityTransform(translation=(-1, 0))
tform_up = skimage.transform.SimilarityTransform(translation=(0, 1))
tform_down = skimage.transform.SimilarityTransform(translation=(0, -1))
#spots_up=warp(spots,tform_up)
#spots_down=warp(spots,tform_down)
#spots_left=warp(spots,tform_left)
#spots_right=warp(spots,tform_right)

######others##########
#pymorph.binary faster than seg>0?
#from skimage import measure
#from skimage import morphology
#pymorph.#thick(s,pymorph.endpoints(option='homotopic'),1)
#pymorph.dist(spots) this gives exactly the thing anja was talking about (dist to non-track)
#mahotas.labeled_sum(array, labeled) = Labeled sum. sum will be an array of size labeled.max() + 1, where sum[i] is equal to np.sum(array[labeled == i]).

#check out ~/thiswork/eyes/CRNitschke/blocked_blender.2.2.py for best image analysis examples
