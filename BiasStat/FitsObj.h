/*****************
 * @file FitsObj.h
 * @date 4/1/08
 * @author Douglas Applegate
 *
 * @brief Provides a wrapper around the GSL libraries for fitting functions
 *****************/

//CVSID $Id: FitsObj.h,v 1.1 2008-06-25 22:26:22 mallen Exp $

////////////////////////////////////////////////////

#ifndef FITSOBJ_H
#define FITSOBJ_H
#include <iostream>
#include <stddef.h>
#include <fitsio.h>
#include <fitsio2.h> 
#include <longnam.h>
#include <cmath>


/**
 *
 */
class FitsObj {

 public:
  
  /**
   * Initializes object with basic fit information
   */
  FitsObj(char* filename);

  
  /**
   * Default constructor
   */
  virtual ~FitsObj();


  double AvgRow(int irow);
  double AvgCol(int icol);
  double FracBadPixels();

  int NaxisX;
  int NaxisY;
  int Npixels;

private:

  double** fitsarray;
  
  double *pixels;
  

};


#endif 
