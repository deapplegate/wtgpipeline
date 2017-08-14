/**
 * @file FitsObj
 * @author Mark Allen
 * @date 5/28/08
 *
 * @brief Implementation of FitsObj
 */

//CVSID $Id: FitsObj.cxx,v 1.1 2008-06-25 22:26:22 mallen Exp $
#include <iostream>
#include <stddef.h>
#include <fitsio.h>
#include <fitsio2.h> 
#include <longnam.h> 
#include <cmath>
#include "FitsObj.h"


using namespace std;

FitsObj::FitsObj(char* filename){
  
  int v = 0;
  fitsfile *fptr;   /* FITS file pointer, defined in fitsio.h */
  int status = 0;   /* CFITSIO status value MUST be initialized to zero! */
  int bitpix; // not important
  int naxis;// number of axes.  Better be 2.
  int ii;//  iterator       , anynul;
  long naxes[2] = {1,1};// number of pixels in axis
  long fpixel[2] = {1,1};// effectively iterator
  //  double *pixels; // actually hlds the pixel vals
  //  char format[20], hdformat[20];
  

  // Open FITS file:
  if (fits_open_file(&fptr, filename, READONLY, &status)) {return;}
    
  if(v) cout<<"FileOpen"<<endl;

  // Get Parameters: NpixelsX & NpixelsY from header
  if (fits_get_img_param(fptr, 2, &bitpix, &naxis, naxes, &status) )  {
    cout<<"Cant get parameters"<<endl;
  }
  NaxisX = naxes[0];
  NaxisY = naxes[1];
  Npixels = NaxisX * NaxisY; 
  if (v) cout<<"Got Axes "<<NaxisX<<" "<<NaxisY<<endl; 
  fitsarray = new double*[NaxisX];
  //  if(v) cout<<"made fits array 1"<<endl;
  for(int iter = 0; iter < NaxisX ; iter++) {
    fitsarray[iter] = new double [NaxisY];
    //if(v) cout<<"made fits array 1."<<iter<<endl;
  }
  //  if(v) cout<<"made fits array 2"<<endl;

 if (naxis > 2 || naxis == 0)  printf("Error: only 1D or 2D images are supported\n");

  else  {
    /* get memory for 1 row */
    //  pixels = (double *) malloc(naxes[0] * sizeof(double));
    pixels = new double(NaxisX);
    
    if (pixels == NULL) {
      printf("Memory allocation error\n");
      return;
    }
        
    if(v) cout<<"Starting Loop"<<endl;
    
    /* loop over all the rows in the image, top to bottom */
    for (fpixel[1] = naxes[1]; fpixel[1] >= 1; fpixel[1]--) {
      //cout<<"1 fpixel[1]-1 = "<<fpixel[1]-1<<endl;
      /* read row of pixels */
      if (fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0], NULL,
                        pixels, NULL, &status) ) {break;}  /* jump out of loop on error */
      
      for (ii = 0; ii < naxes[0]; ii++) {
        fitsarray[ii][fpixel[1]-1] = pixels[ii];
      }
      
    }
    
    //free(pixels);
  }

 if(v) cout<<"Done with loop"<<endl;
 fits_close_file(fptr, &status);

}


FitsObj::~FitsObj(){

  // delete [] fitsarray;
  //  _parameters = NULL;
  //  cout<<"clearing fits arrays"<<endl;
  for(int i=0; i < NaxisX; i++){
    delete [] fitsarray[i];
  }
  //cout<<"clearing and the last one"<<endl;
  delete [] fitsarray;
  fitsarray = NULL;
  //  cout<<"clearing pixels"<<endl;
  delete [] pixels;
  pixels = NULL;
};

////////////////////////////////////////
    

double FitsObj::AvgRow(int irow) {

  double average = 0;
  int counter =0; 
  for(int i = 0; i< NaxisX; i++){
    if(fitsarray[i][irow]<20 &&fitsarray[i][irow]>-20){ 
      average += fitsarray[i][irow];
      counter++;
    }
  }
  
  if(counter==0) return 0;
  average = average/(1.*counter);
  
  return average;

}    

double FitsObj::AvgCol(int icol) {

  double average = 0;
  int counter =0; 
  for(int i = 0; i< NaxisY; i++){
    if(fitsarray[icol][i]<20 &&fitsarray[icol][i]>-20){ 
      average += fitsarray[icol][i];
      counter++;
    }
  }

  
  if(counter==0) return 0;
  average = average/(1.*counter);
  
  return average;

}
double FitsObj::FracBadPixels(){
  
  int count = 0;
  
  for(int i = 0; i< NaxisX; i++) {
    for(int j = 0; j<NaxisY; j++) {
      if(fabs(fitsarray[i][j]) > 20. )count++;
    }
  }

  return (1.0*count)/(1.0*NaxisX*NaxisY);


}
