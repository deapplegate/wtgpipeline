#!/usr/bin/env python

# The script estimates a gaussian convolution kernel
# to degrade an image from its original to a worse
# target seeing. The width of the kernel is determined
# with the assumption that stellar objects can be
# described by Gaussian profiles. This turned out
# to be valid if the two seeings are not too different
# from each other (about 0.3 arcsec).

# HISTORY INFORMATION:
#
# 24.07.2008:
# I adapted kernel size and fudge factors to give good
# results on the first 37 sq. degrees of CARS data

from math import *
import string
import sys

# This romberg integration formula is specialised to integrate
# a one dimensional gaussian with width sigma from a to b:
def gauss_romberg(a, b, sigma, eps = 1E-8):

   def gauss(x, sigma=1):
       f = exp(-x**2/(2*(sigma)**2))
       return f

   """Approximate the definite integral of f from a to b by Romberg's method.
   eps is the desired accuracy."""
   R = [[0.5 * (b - a) * (gauss(a, sigma) + gauss(b, sigma))]]  # R[0][0]
   n = 1
   while True:
       h = float(b-a)/2**n
       R.append((n+1)*[None])  # Add an empty row.
       R[n][0] = 0.5*R[n-1][0] + h*sum(gauss(a+(2*k-1)*h, sigma) for k in range(1, 2**(n-1)+1)) # for proper limits
       for m in range(1, n+1):
           R[n][m] = R[n][m-1] + (R[n][m-1] - R[n-1][m-1]) / (4**m - 1)
       if abs(R[n][n-1] - R[n][n]) < eps:
           return R[n][n]
       n += 1

# gauss_int gives the intagral of the product of two
# one-dimensional gaussians; integration boundaries
# are from x1 to x2 and from y1 to y2:
def gauss_int(x1,x2,y1,y2,sigma):
   result=(gauss_romberg(x1,x2,sigma))*(gauss_romberg(y1,y2,sigma))
   return result

# Here the main program starts:
if __name__ == "__main__":

   # check validity of command line arguments:
   if len(sys.argv) != 5:
       print "SYNOPSIS:"
       print "   %s orig_seeing new_seeing pix_scale output_file.\n" \
             % ( sys.argv[0] )
       print "DESCRIPTION:"
       print "   The script calculates a Gaussian smoothing kernel to degrade"
       print "   an image from seeing 'orig_seeing' to 'new seeing'. Your"
       print "   CCD data has pixel scale 'pixel_scale' and the resulting"
       print "   kernel is written into 'output.'. Seeing and pixel"
       print "   have to be given in arcsec.\n"
       print "EXAMPLE:"
       print "   create_gausssmoothing_kernel.py 0.5 0.8 0.186 ."
       sys.exit(1)

   seeing_orig = string.atof(sys.argv[1])
   seeing_new  = string.atof(sys.argv[2])
   pixel_scale = string.atof(sys.argv[3])
   output  = sys.argv[4]

   filter_size = 5 # must be an odd number!
   fudge = 1.0     # to have some more control on the width
                   # of the Gaussian smoothing kernel

   # adapt filter size and fudge factor if necessary:
   if (seeing_new - seeing_orig > 0.25) and \
       (seeing_new - seeing_orig <= 0.35):
       filter_size = 7
       fudge = 1.2

   if (seeing_new - seeing_orig > 0.35) and \
       (seeing_new - seeing_orig <= 0.5):
       filter_size = 7
       fudge = 1.1

   if (seeing_new - seeing_orig > 0.5):
       filter_size = 9
       fudge = 1.2

   # variance of the smoothing kernel:
   #
   # In the following formula the '2.35' (2*sqrt(2*ln(2))) accounts
   # for the difference between seeing which is full-width at half
   # maximum and the variance which appears in the formula for a
   # Gaussian.
   if seeing_orig < seeing_new:
       sigma_smooth = (sqrt(seeing_new**2 - seeing_orig**2) \
                       / pixel_scale / fudge ) / 2.35
   else:
       sigma_smooth = 0

   # create output file:
   filename = output
#   filename = output_dir + "/gauss.conv" #% ( filter_size, \
                                                         #filter_size, \
                                                         #sys.argv[1], \
                                                         #sys.argv[2])

   fout = open(filename, "w")

   # print out a zero filter in case the requested seeing
   # is smaller than the original one:
   if seeing_orig > seeing_new:

       fout.write("CONV NORM\n")
       for i in range(filter_size):
           line = ""
           for j in range(filter_size):
               line = line + "%1.6f " % 0.000000
           fout.write(line + "\n")
   else:
       fout.write("CONV NORM\n")
       line = "# %dx%d gaussian convolution with sigma %1.6f\n" \
              % (filter_size, \
                 filter_size,\
                 sigma_smooth)

       fout.write(line)

       for i in range(filter_size):
           line = ""
           for j in range(filter_size):
               line = line + "%1.6f " % gauss_int(-(filter_size / 2.) + j,
                                                  -(filter_size / 2.) + j + 1,
                                                   (filter_size / 2.) - 1 - i,
                                                   (filter_size / 2.) - i,
                                                    sigma_smooth)
           fout.write(line + "\n")

   fout.close()

sys.exit(0)
# end of script
