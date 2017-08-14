#include <iostream>
#include <cstring>
#include <cstdlib>
#include <fitsio.h>
#include <fitsio2.h>
#include <longnam.h>
#include <cmath>
#include <stddef.h>
#include "leastsq.h"


/*
  Shadowfinder is designed to find and produce a mask to cover
  the shadow caused by the autotracker for the Subaru telescope.
  It assumes that the filename given includes the chip-number
  defined by:
  6 7 8 9 10
  1 2 3 4 5

  and that the chip number is identified in the filename as
  blah_2blah.fits.  It may become confused otherwise.

  -mta
  12-10-08
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
  double **imagearray = new double*[NaxisX];// the image fed in
  double **maskarray = new double*[NaxisX];// an intermediate mask
  double **maskarray2 = new double*[NaxisX];// the final mask
  
  for(int iter = 0; iter < NaxisX ; iter++) {// initialize...
    imagearray[iter] = new double [NaxisY];
    maskarray [iter] = new double [NaxisY];
    maskarray2[iter] = new double [NaxisY];
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
  
  //more initialization
  for(int i=0; i<NaxisX; i++) {
    for(int j=0; j<NaxisY; j++) {
      maskarray[i][j]=imagearray[i][j];
      maskarray2[i][j]=1.;
    }
  }
  
  
  // As mentioned above,  this assumes the chip 10 configuration.  If
  // it is chip 1-5, ignore and return an empy mask.
  
  if(strstr(filename,"_6")||strstr(filename,"_7")||strstr(filename,"_8")||
     strstr(filename,"_9")||strstr(filename,"_10")) {
    
    // First thing, expand the blank regions...  
    int bval = 20;// a value of 20 is aggressive, but it probably dosn't matter too much.
  
    if(v) cout<<" Expanding..."<<endl;
    for(int jcol = 0; jcol<NaxisX; jcol++) {
      for(int jrow = 0; jrow<NaxisY; jrow++) {
	float val = imagearray[jcol][jrow];
	if(val > 0) continue; // Nothin doin
	else {
	  for(int localx = jcol-bval; localx <= jcol+bval; localx++) {
	    for(int localy = jrow-bval; localy <= jrow+bval; localy++) {
	      // Make sure we're still on the image!
	      if( (localx-jcol)*(localx-jcol) +  (localy-jrow)*(localy-jrow) > bval*bval) continue;
	      if(!(localx<0 || localx>=NaxisX  || localy<0 || localy>=NaxisY))  {
		maskarray[localx][localy] = 0;
	      }
	    }
	  }
	}
      }
    }
  
    //maskarray is now fully "object-subtracted"
  
    // Next define bottom 2/3, get average...
    int toprow = floor(NaxisY*2./3.);
  
    long double avg_counter = 0;
    long double rms_counter = 0;
    int count = 0;
  
  
    for(int jcol = 0; jcol<NaxisX; jcol++) {
      for(int jrow = 0; jrow<=toprow; jrow++) {
	float val = maskarray[jcol][jrow];
	if(val<=0) continue;
	count++;
	avg_counter+= val;
	rms_counter+=val*val;
      }
    }	
    double avg = avg_counter / (1.*count);
    double rms = sqrt(rms_counter/(1.*count) - avg*avg);
    // Naturally this rms value assumes a 
    // flat inherent distribution, which 
    // is almost certainly not true.
    cout<< "Comparing to "<<avg<<"  "<<rms/sqrt(1.*count)<<endl;
  


    /* 
       We're grouping the rest of the image into a 4 x 10 grid
    */

    long double avg_bin[4][10];
    long double rms_bin[4][10];
    count=0;
  
    int Yrange = NaxisY - toprow;
    /*  ibin goes horizontally (0 on left), and jbin goes 
	vertically (0 on bottom) */
    for(int ibin=0; ibin < 4; ibin++) {
      for(int jbin=0; jbin < 10; jbin++) {
	avg_bin[ibin][jbin]=0;
	rms_bin[ibin][jbin]=0;
	// calculate averages in all of the "bricks"
	for(int xpix = floor(ibin*NaxisX/4.); xpix < floor((ibin+1)*NaxisX/4.);xpix++) {
	  for(int ypix = floor(jbin*Yrange/10.+toprow); ypix < floor((jbin+1)*Yrange/10.+toprow);ypix++) {
	    double val = maskarray[xpix][ypix];
	    if(val<=0) continue; // ignore objects...
	    avg_bin[ibin][jbin] += val;
	    rms_bin[ibin][jbin] += val* val;
	    count++;
	  }	
	}

	if(count>10){ // if there are enough good background pixels....  
	  avg_bin[ibin][jbin] =  avg_bin[ibin][jbin]/(count*1.);
	  rms_bin[ibin][jbin] =  (sqrt(rms_bin[ibin][jbin]/(count*1.) -  
				       avg_bin[ibin][jbin]* avg_bin[ibin][jbin]))/sqrt(1.*count);      
	}
	else{ // otherwise...
	  avg_bin[ibin][jbin] =-1;
	  rms_bin[ibin][jbin] = -1;
	}
	count=0; // reset
      }
    }	

    // these correspond to the bricks...
    int grid[4][10];
    int grid2[4][10];
  
    // initialize all bricks to 1;
    for( int jbin=0; jbin < 10; jbin++) {
      for( int ibin=0; ibin < 4; ibin++) {
	cout <<"For "<<ibin<<" "<<jbin<<": "<<avg_bin[ibin][jbin]<<" +/- "<<rms_bin[ibin][jbin]<<"    ";
	grid[ibin][jbin]=1;
	grid2[ibin][jbin]=1;
      }
      cout<<endl;
    }

    // if(strstr(filename,"_6")) is6 = 1;
  
    for( int jbin=9; jbin >= 0; jbin--){
      for( int ibin=3; ibin >=0; ibin--){
	if(avg_bin[ibin][jbin]<0){ continue;}  // ignore bricks with no good pix.
	if(avg_bin[ibin][jbin]<avg - 80){ // 80 is as good a number as any...	
	  if( jbin<9 ){
	    if(grid[ibin][jbin+1]>0){
	      cout<<"WARNING: DETECT A SIGNIFICANT DECREASE IN THE BACKGROUND, BUT"<<endl;
	      cout<<"NOT IN THE LAYER ABOVE: "<<ibin<<" "<<jbin<<" IGNORING "<<endl;
	      continue;
	    }
	  }
	  grid[ibin][jbin]=0;  // mask the bin
	  cout<<"masking "<<ibin<<", "<<jbin<<endl;
	  if(jbin>0) grid[ibin][jbin-1]=0; // mask bin below...
	
	  // if on the left, expand left...
	  if(ibin>0&&(strstr(filename,"_6")||strstr(filename,"_7")||strstr(filename,"_8"))) {
	    grid[ibin-1][jbin]=0;
	    if(jbin>0) grid[ibin-1][jbin-1]=0;
	  }	  
	  // if on the right, expand right...
	  if(ibin<3&&(strstr(filename,"_9")||strstr(filename,"_10")||strstr(filename,"_8"))) {
	    grid[ibin+1][jbin]=0;
	    if(jbin>0) grid[ibin+1][jbin-1]=0;
	  }
	}
      }
    }	
   
    // now we've got what we want, just make the final mask...
    
    for(int ibin=0; ibin < 4; ibin++) {
      for(int jbin=0; jbin < 10; jbin++) {
	if(grid[ibin][jbin]==0) {
	for(int xpix = floor(ibin*NaxisX/4.); xpix < floor((ibin+1)*NaxisX/4.);xpix++) {
	  for(int ypix = floor(jbin*Yrange/10.+toprow); ypix < floor((jbin+1)*Yrange/10.+toprow);ypix++) {
	      maskarray2[xpix][ypix]=0;
	    }	
	  }
	}
      }
    }	

    // and we're done!

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
      array[jj][ii] = maskarray2[ii][jj];  
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


