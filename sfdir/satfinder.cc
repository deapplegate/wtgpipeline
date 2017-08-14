#include <iostream>
#include <cstring>
#include <cstdlib>
#include <fitsio.h>
#include <fitsio2.h>
#include <longnam.h>
 /*  
      The method here is just to scan the outside of an image.  We
      keep the pixel coordinates that have an object.  Then for each 
      pair we draw a ray across, and see if there is an "object" 
      across the whole line.  If there is, we mask it.  We ignore
      rows/columns of hot pixels.  Or at least we try to.  

  --mta
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


// Given an X position, and the end points, calculates 
// the Y pixel...
int getypixel(int xval, int x1, int x2, int y1, int y2) {
  double X1 = x1+0.5;
  double X2 = x2+0.5;
  double Y1 = y1+0.5;
  double Y2 = y2+0.5;
  double Xval = xval+0.5;

  if(x1==x2){ return y2;}

  double m = (Y2-Y1)/(X2-X1);
  
  double b = Y1 - m * X1;

  return   (int)(( m*Xval + b)/1);


}

// Given an Y position, and the end points, calculates 
// the X pixel...
int getxpixel(int yval, int x1, int x2, int y1, int y2) {
  double X1 = x1+0.5;
  double X2 = x2+0.5;
  double Y1 = y1+0.5;
  double Y2 = y2+0.5;
  double Yval = yval+0.5;

  if(X1==X2){ return x2;}
  if(Y1==Y2){ return x2;}

  double m = (Y2-Y1)/(X2-X1);
  
  double b = Y1 - m * X1;

  return   (int)(((Yval - b)/m)/1);

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
  if(open_file_flag) {	printf("Error: Cannot open file\n"); return 0;}
  
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
  double **maskarray2 = new double*[NaxisX]; // final mask
  
  for(int iter = 0; iter < NaxisX ; iter++){
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
  
  //mask arrays are   
  for(int i=0; i<NaxisX; i++) {
    for(int j=0; j<NaxisY; j++) {
      maskarray[i][j]=1.;
      maskarray2[i][j]=1.;
    }
  }
  
  if(v) cout<<"start the scan.... "<<endl;

  int ix1;
  int ix2;
  int iy1;
  int iy2;
  
  int jx1;
  int jx2;
  int jy1;
  int jy2;
  int jxpixel;    
  int jypixel;    
  
  //  These store the pix coordinates with 
  //  "objects" in them.
  int xset[2*NaxisX+2*NaxisY - 4];
  int yset[2*NaxisX+2*NaxisY - 4];

  int count = 0;

  // go across the left edge..
  ix1 = 0;
  for(iy1 = 0; iy1<NaxisY; iy1++) {
    if(imagearray[ix1][iy1]==0) continue;
    else {
      xset[count] = ix1;
      yset[count] = iy1;
      count++;
    }
  }

  // go across the bottom...
  iy1 =0;
  for(int ix1 = 1; ix1< NaxisX; ix1++) {
    if(imagearray[ix1][iy1]==0) continue;
    else {
      xset[count] = ix1;
      yset[count] = iy1;
      count++;
    }
  }

  // go across the top...
  iy1 = NaxisY-1;
  for(int ix1 = 1; ix1 < NaxisX; ix1++) {
    if(imagearray[ix1][iy1]==0) continue;
    else {
      xset[count] = ix1;
      yset[count] = iy1;
      count++;
    } 
  }

  // go across the left edge...
  ix1 = NaxisX-1;
  for(int iy1 = 1; iy1 < NaxisY-1; iy1++) {
    if(imagearray[ix1][iy1]==0) continue;
    else {
      xset[count] = ix1;
      yset[count] = iy1;
      count++;
    } 
  }


  cout<<"Done scanning, let's test"<<endl;
  
  int x1set = 0;
  int y1set = 0;
  int x2set = 0;
  int y2set = 0;

  //  now we go pairwise, and see if they qualify...  
  for(int iset = 0; iset<count; iset++) {
    for(int jset = 0; jset<iset; jset++) { 
      // here we ignore hot rows/columns
      if(xset[iset]==xset[jset] || yset[iset]==yset[jset]) continue;
      

      // this is annoying, there's surely a better way...
      //  here I just order them.  x1<x2, buy y2<y1 or y1<y2
      if(xset[iset]<=xset[jset]) {
        x1set = xset[iset];  x2set = xset[jset];   y1set = yset[iset];  y2set = yset[jset];  
      }
      else if(xset[iset]>xset[jset]) {
        x1set = xset[jset];  x2set = xset[iset];   y1set = yset[jset];  y2set = yset[iset];  
      }
      
      
      int ison = 1;    // just a flag   
      // scan along the xpixels...
      for(jxpixel = x1set; jxpixel<=x2set; jxpixel++) {
	// for each value of x, get the y...
	jypixel = (int) getypixel(jxpixel, x1set, x2set, y1set, y2set);
	if(imagearray[jxpixel][jypixel]==0){
	  // not here, get out.
	  ison = 0; 
	  jxpixel = x2set+1;
	} 
      }
      // if it passed the x pixel scan, do the same along the y dir...
      if(ison &&  (y1set < y2set)) {
	for(jypixel = y1set; jypixel<=y2set; jypixel++) {
	  jxpixel = (int) getxpixel(jypixel, x1set, x2set, y1set, y2set);
	  if(imagearray[jxpixel][jypixel]==0){
	    ison = 0;
	    jypixel = y2set+1;
	  }
	}
      } 
      else if(ison &&  (y1set > y2set)){
	for(jypixel = y1set; jypixel>=y2set; jypixel--) {
	  jxpixel = (int) getxpixel(jypixel, x1set, x2set, y1set, y2set);
	  if(imagearray[jxpixel][jypixel]==0){
	    ison = 0;
	    jypixel = y2set-1;
	  }
	}
      } 
      
      
      if(ison){// still there?  must be a sat?
	if(v) cout<<"SAT found!!! from "<<x1set<<","<<y1set<<"  "<<x2set<<","<<y2set<<endl;
	for(jxpixel = x1set; jxpixel<=x2set; jxpixel++) {	
	  jypixel = (int) getypixel(jxpixel, x1set, x2set, y1set, y2set);
	  maskarray[jxpixel][jypixel] = 0;  // record the mask...
	}
	for(jypixel = y1set; jypixel<=y2set; jypixel++) {
	  jxpixel = (int) getxpixel(jypixel, x1set, x2set, y1set, y2set);
	  maskarray[jxpixel][jypixel] = 0; // record the mask...
	}
      }
    }
  }
  
      

  // And that's it!  
  // Let's boxcar this thing, and go home.
  int bval = 30;
  
  if(v) cout<<" Expanding..."<<endl;
  for(int jcol = 0; jcol<NaxisX; jcol++) {
    for(int jrow = 0; jrow<NaxisY; jrow++) {
      float val = maskarray[jcol][jrow];
      if(val > 0.5) continue; // Nothin doin
      else {
	for(int localx = jcol-bval; localx <= jcol+bval; localx++) {
	  for(int localy = jrow-bval; localy <= jrow+bval; localy++) {
	    // Make sure we're still on the image!
	    if(!(localx<0 || localx>=NaxisX  || localy<0 || localy>=NaxisY))  {
	      maskarray2[localx][localy] = 0; // final mask.
	    }
	  } 
	}
      }
    }
  }
  

  
  
  cout<<"Writing file to "<<outfilename<<endl;
   
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



   




