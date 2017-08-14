#include <iostream>
#include <stddef.h> 
#include <fitsio.h>
#include <fitsio2.h>
#include <longnam.h>
#include "leastsq.h"
#include <cmath>

 /*  
   

 */

using namespace std;

// error handling
void printerror( int status)
{
  /*****************************************************/
  /* Print out cfitsio error messages and exit program */
  /*****************************************************/
  if (status)
    {
      fits_report_error(stderr, status); /* print error report */

      exit( status );    /* terminate the program, returning error status */
    }
  return;
}
int main( int argc, char** argv ) {

  if( argc!=3 && argc!=4 ) {
    
    std::cerr <<"Usage: " << argv[0] << " <inputfile> <outputfile>  (verboseflag)"<< std::endl;
    std::cerr <<"Input image must be image with background pixels set to -1, objects > 0."<<std::endl;
    ::exit(1);
  }

  int v =0;
  if(argc==4) v =1;

  char* filename = argv[1];
  char* outfilename = argv[2]; 
  
 
  /* Most of the code to load the fits file, 
     I have brazenly stolen from the cfitsio manual examples*/

  if(v) cout<<"Start reading FITS file"<<endl;
  fitsfile *fptr;   /* FITS file pointer, defined in fitsio.h */
  int status = 0;   /* CFITSIO status value MUST be initialized to zero! */
  int bitpix; // not important
  int naxis;// number of axes.  Better be 2.
  int ii;//  iterator    
  long naxes[2] = {1,1};// number of pixels in axis{x,y}
  long fpixel[2] = {1,1};// effectively an iterator
  int NaxisX=0;
  int NaxisY=0;
  int Npixels=0;
  
  int max = 0;  //minimum val 
  int min = 99999;
  double average=0;
  double total=0;
  int open_file_flag=0,img_param_flag=0;
  
  

  // Open FITS file:
  open_file_flag = fits_open_file(&fptr, filename, READONLY, &status);
  if(open_file_flag) {  printf("Error: Cannot open file\n"); return 0;}
  
  if(v) cout<<"FileOpen"<<endl;

  // Get Parameters: NaxisX & NaxisY from header  
  img_param_flag = fits_get_img_param(fptr, 2, &bitpix, &naxis, naxes, &status);
  if (img_param_flag )  {printf("Error: Cannot find image dimensions\n");return 0; }
  
  
  NaxisX = naxes[0];
  NaxisY = naxes[1];
  Npixels = NaxisX * NaxisY; 
  if(v) cout<<"Nx = "<< NaxisX<<"; Ny = "<< NaxisY<<endl;
  
  if (naxis > 2 || naxis == 0)  {
    printf("Error: only 1D or 2D images are supported\n");

    return 0;
  }
  
  // Define Masks
  double **imagearray = new double*[NaxisX]; // the input image 
  double **maskarray = new double*[NaxisX];  // intermediate mask.

   for(int iter = 0; iter < NaxisX ; iter++){
    imagearray[iter] = new double [NaxisY];
    maskarray [iter] = new double [NaxisY];

  }
  
  
  /* get memory for 1 row */
  double *pixels = new double[NaxisX];
  
  if(v) cout<<"Starting Reading File"<<endl;  
  /* loop over all the rows in the image, top to bottom */
  for (fpixel[1] = naxes[1]; fpixel[1] >= 1; fpixel[1]--) {
    
    /* read row of pixels */
    if (fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0], NULL,
                      pixels, NULL, &status) ) { break;}  /* jump out of loop on error */
    for (ii = 0; ii < naxes[0]; ii++) {
      imagearray[ii][fpixel[1]-1] = pixels[ii]; // Fill array
    }
  }
   
  free(pixels);
  
  /* Close the file*/
  fits_close_file(fptr, &status);
  if(v) cout<<"Closed infile"<<endl;
  
 if (status) fits_report_error(stderr, status); /* print any error message */
  
  //mask arrays are   
  for(int i=0; i<NaxisX; i++) {
    for(int j=0; j<NaxisY; j++) {
      maskarray[i][j]=0;
    }
  }



  for(int jcol = 0; jcol<NaxisX; jcol++) {
    for(int jrow = 0; jrow<NaxisY; jrow++) {
      float val = imagearray[jcol][jrow];
      if(val < 0.5) continue; // Nothin doin
      else {
        for(int localx = jcol-1; localx <= jcol+1; localx++) {
          for(int localy = jrow-1; localy <= jrow+1; localy++) {
            // Make sure we're still on the image!
            if(!(localx<0 || localx>=NaxisX  || localy<0 || localy>=NaxisY))  {
              maskarray[localx][localy] = 1;
            }
          }
        }
      }
    }
  }



  /******************************************************/
  /* Create a FITS primary array containing a 2-D image */
  /*  ...  Again, stolen from the cfitsio doc           */
  /******************************************************/
  fitsfile *fptrout;       /* pointer to the FITS file, defined in fitsio.h */
  int statusout;
  long  fpixelout, nelements;
  unsigned short *array[NaxisY];
   
  
  /* initialize FITS image parameters */
  bitpix   =  -32; /* 16-bit unsigned short pixel values       */
   
  /* allocate memory for the whole image */ 
  array[0] = (unsigned short *)malloc( naxes[0] * naxes[1]
                                       * sizeof( unsigned short ) );
  /* initialize pointers to the start of each row of the image */
  for( ii=1; ii<naxes[1]; ii++ ) {
    array[ii] = array[ii-1] + naxes[0];
  }
  remove(outfilename);               /* Delete old file if it already exists */
  statusout = 0;         /* initialize statusout before calling fitsio routines */
   
  if (fits_create_file(&fptrout, outfilename, &statusout)) /* create new FITS file */
    printerror( statusout );           /* call printerror if error occurs */
 if ( fits_create_img(fptrout,  bitpix, naxis, naxes, &statusout) )
    printerror( statusout );          
   
  /* set the values in the image with the mask values  */
  for (int jj = 0; jj < naxes[1]; jj++) {
    for (ii = 0; ii < naxes[0]; ii++) {
      array[jj][ii] = maskarray[ii][jj];  
    }
  }
   
  fpixelout = 1;                               /* first pixel to write      */
  nelements = naxes[0] * naxes[1];          /* number of pixels to write */
   
  if ( fits_write_img(fptrout, TUSHORT, fpixelout, nelements, array[0], &statusout) )
    printerror( statusout );
   
  free( array[0] );  /* free previously allocated memory */
   
  if ( fits_close_file(fptrout, &statusout) )                /* close the file */
    printerror( statusout );           
   

  if(v) cout<<"Done."<<endl;
  return 0;
   
   
} 
