#include <iostream>
#include <stddef.h>
#include "leastsq.h"
#include <cstring>
#include <cstdlib>
#include <fitsio.h>
#include <fitsio2.h>
#include <longnam.h>
#include <cmath>

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
 
  if( argc<3 || argc > 5) {
    
    std::cerr <<"Usage: " << argv[0] << " <inputfile> <outputfile>  <filter> (verboseflag)"<< std::endl;
    ::exit(1);
  }

  int v =0;
  if(argc==5) v =1;


  char* filename = argv[1];
  char* outfilename = argv[2]; 
  
  char* filter="";
  int chipnum=1;
  if(argc > 3){
    filter = argv[3];
  }

  //  filter depenant extra masking...
  // first, is this chip 6?
  // adam: nope, not treating ccd6 differently anymore, it's normal in 10_3 config
  int is6 =0;
  int whichfilter=0;
  if(strstr(filename,"_6")) is6 = 0;
  if(strstr(filter,"B")) whichfilter = 1;
  else if(strstr(filter,"V")) whichfilter = 2;
  else if(strstr(filter,"R")) whichfilter = 3;
  else if(strstr(filter,"I")) whichfilter = 4;
  else if(strstr(filter,"Z")) whichfilter = 5;
  else { 
    whichfilter = 3;
    cout<<"filter not recognized.  Assuming...R"<<endl;
  }


 
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
   double **imagearray = new double*[NaxisX];
   double **maskarray = new double*[NaxisX];
   double **maskarray2 = new double*[NaxisX];
   double **maskarray3 = new double*[NaxisX];
   
   for(int iter = 0; iter < NaxisX ; iter++){
     imagearray[iter] = new double [NaxisY];
     maskarray [iter] = new double [NaxisY];
     maskarray2[iter] = new double [NaxisY];
     maskarray3[iter] = new double [NaxisY];     
   }
  
   
   /* get memory for 1 row */
   double *pixels = new double[NaxisX];
   
   if(v) cout<<"Starting Reading Loop"<<endl;
  
   /* loop over all the rows in the image, top to bottom */
   for (fpixel[1] = naxes[1]; fpixel[1] >= 1; fpixel[1]--) {
     
     /* read row of pixels */
     if (fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0], NULL,
		       pixels, NULL, &status) ) { break;}  /* jump out of loop on error */
     for (ii = 0; ii < naxes[0]; ii++) {
       imagearray[ii][fpixel[1]-1] = pixels[ii];
       total = total + pixels[ii];
     }
   }
   
   free(pixels);
   
   /* Close the file*/
   fits_close_file(fptr, &status);
   if(v) cout<<"Closed infile"<<endl;
  
   if (status) fits_report_error(stderr, status); /* print any error message */
   else {  // find the average
     average = total/(1.0*  naxes[0]*  naxes[1]);
   }
   
   // Initialize mask-array, also calculate mean background value and rms:
   double lrms=0;
   double lavg=0;
   
   for(int i=0; i<NaxisX; i++) {
     for(int j=0; j<NaxisY; j++) {
       maskarray[i][j]=1.;
       if(imagearray[i][j] < 2.* average) {
	 lavg =lavg + imagearray[i][j];
       }
     }
   }

   lavg = lavg / (1.*Npixels);
   cout<<"Find RMS"<<endl;
   //Find the rms/ typical width of distribution
   for(int i=0; i<NaxisX; i++) {
     for(int j=0; j<NaxisY; j++) {
       if(imagearray[i][j] < 1.5* lavg &&imagearray[i][j] > 0.5 ) {
	 lrms = lrms + ((imagearray[i][j]-lavg)*(imagearray[i][j]-lavg));
       }
     }
   }
   lrms = lrms/(1.0*NaxisX*NaxisY);
   lrms = sqrt(lrms)/2.;
   
  
   
   double thresh = lavg + 8*lrms;   // We look outside of this range
   double negthresh = lavg - 5*lrms;// for the diff. spikes.
  
   if(v) {
     cout<<"Statistics: Average: "<<average<<endl;
     cout<<"  Local Average: "<<lavg<<endl;
     cout<<"  Local RMS: "<<lrms<<endl;
     cout<<"  Pos threshold "<<thresh<<endl;
     cout<<"  Neg threshold "<<negthresh<<endl;
   }
  
   if(v)cout<<"Finding spikes..."<<endl;
   // First we look for the spikes:  
   for(int icol = 0; icol<NaxisX; icol++) {
     
     int setstart = -1,setstop = -1;
     int flag = 0;  // keeps track of when we are in a spike
     for(int irow = 0; irow<NaxisY; irow++) {
      
      // True if the pixel is above/below thresholds 
      // and the previous pixel was ok.
       if((imagearray[icol][irow] > thresh 
	   || imagearray[icol][irow] < negthresh) 
	  && setstart == -1 ) {// found start	
	 setstart = irow;
       }
      
      //True if pixel is above/below thresholds 
      //and the previous pixel was bad too.
      else if((imagearray[icol][irow] > thresh ||
	       imagearray[icol][irow] < negthresh) && 
	      setstart != -1 && (irow!=NaxisY-1) ) { // still in
	continue; 
      }
      
      //True if pixel is ok, ending a strech 
      //with bad pixels. Or reached end of chip
      else if( setstart != -1 && 
	       ((imagearray[icol][irow] < thresh && 
		 imagearray[icol][irow] > negthresh  )|| 
		irow==NaxisY-1  ) ) {// we're done...  
	setstop = irow;
	
	if(setstop - setstart > 40 ) {
	  //if the strip is less than 100 pixels, ignore it
	  //otherwise, mask it out.
	  for(int k = setstart; k<= setstop; k++) { 
	    maskarray[icol][k] = 0;
	  }
	}
	// reset
	setstop = -1;
	setstart = -1;
      }
    }
  }


  // now lets get rid of columns of bad pixels, and 
  // remove areas where we've masked while stars
  // reading left to right...
  if(v) cout<<"removing  bad column pixels"<<endl;

  int startmask = -1, stopmask = -1;
  for(int jrow = 0 ; jrow<NaxisY; jrow++) {
    int flag = 0;
    for(int jcol = 0; jcol<NaxisX; jcol++) {
      float val = maskarray[jcol][jrow];
      
      // Nothin' goin' on.
      if(val > 0.5 && !flag ) continue; 
      
      // End of a strip of masked pixels 
      else if((val >0.5 && flag) ||(jcol==NaxisX-1 && flag)) { // time to stop;
	// This designed to remove one pixel anomalies
	// in the middle of stars.  	
	if( jcol < NaxisX-3 &&
	    maskarray[jcol+1][jrow] <0.5 &&
	    maskarray[jcol+2][jrow] <0.5 ){
	  //	  if(v) cout<<"Fake stop: "<<jcol<<" "<<jrow<<endl; 
	  continue;
	}
	stopmask = jcol;
	int size = stopmask - startmask;
	//This it to get unmask bad pixels columns
	// but it also chops off the end of strips..
	//if(v) cout<<"Row "<<jrow<< "width = "<<size<<endl;
	if(size <= 1) {
	  for(int iundo = startmask; iundo <stopmask; iundo++){
	    maskarray[iundo][jrow] = 1;
	  }
	}
	//Diffraction spikes aren't that wide...
	// this removes the masking of whole stars
	if(size > 25) {
	  for(int iundo = startmask; iundo <stopmask; iundo++){
	    maskarray[iundo][jrow] = 1;
	  }
	}
       
	startmask = -1; stopmask = -1; 
	flag = 0;
      }
      else if(val < 0.5 && !flag) { //time to start;
	startmask = jcol;
	flag = 1;
      }

      else if(val < 0.5 && flag) {//in a masked region, do nothing
	continue;
      }

    }
  }
  

  // now we've removed most of the masking of stars, 
  // but lets just clean up a little:
  // and make sure our "spikes" have some length...
  for(int jcol = 0; jcol<NaxisX; jcol++) {
    int flag = 0;
    for(int jrow = 0; jrow<NaxisY; jrow++) {
      float val = maskarray[jcol][jrow];

      if(val > 0.5 && !flag ) continue; // Nothin doin
      
      else if((val >0.5 && flag) ||  (flag && jrow==NaxisY-1)) { // time to stop;
	stopmask = jrow;
	int size = stopmask - startmask;
	//we've cut some spikes in half,
	// so the minimum length has to be shortened too
	if(size <=10) {
	  for(int iundo = startmask; iundo <stopmask; iundo++){
	    maskarray[jcol][iundo] = 1;
	  }
	}
	startmask = -1; stopmask = -1; 
	flag = 0;
      }
      else if(val < 0.5 && !flag){ //time to start;
	startmask = jrow;
	flag = 1;
      }

      else if(val < 0.5 && flag) {//in a masked region, do nothing
	continue;
      }

    }
  }


  /* Now we've got entirely (largly) "spikes".  Lets enlarge the masked region 
     by 2 pixel in all directions. This will remove headaches that'll come 
     later, and we won't lose much*/ 
  
  if(v) cout<<" expanding masked area"<<endl;

  for(int i=0; i<NaxisX; i++){
    for(int j=0; j<NaxisY; j++){
      maskarray2[i][j]=1;
    }
  }

  if(v) cout<<" Boxcar..."<<endl;
  for(int jcol = 0; jcol<NaxisX; jcol++) {
    for(int jrow = 0; jrow<NaxisY; jrow++) {
      float val = maskarray[jcol][jrow];
      if(val > 0.5) continue; // Nothin doin
      else {
	for(int localx = jcol-2; localx <= jcol+2; localx++) {
	  for(int localy = jrow-2; localy <= jrow+2; localy++) {
	    // Make sure we're still on the image!
	    if(!(localx<0 || localx>=NaxisX  || localy<0 || localy>=NaxisY))  {
	      maskarray2[localx][localy] = 0;
	    }
	  }
	}
      }
    }
  }

  /* Now we're going to expand the masked region,  
     by looking for an excess in pixel values over 
     the backgreound level.  */
  // copy the masking array....
  for(int i=0; i < NaxisX; i++) {
    for(int j=0; j < NaxisY; j++) {
      maskarray3[i][j] = maskarray2[i][j];
    }
  }
  
  if(v) cout<<"Expanding Horizontally..."<<endl;
  for(int jrow = 0; jrow<NaxisY; jrow++) {
    int getout = 0;
    int flag = 0;
    int thiscol;
    int counter;
    int Nbelowthresh ;

    for(int jcol = 0; jcol<NaxisX; jcol++) {
      float val = maskarray2[jcol][jrow];
      if(val > 0.5 && !flag ) {
	continue; // Nothin doin
      }
      else if(val < 0.5 && flag) {//in a masked region, do nothing
	continue;
      }
      else if(val > 0.5 && flag) { // right egde of region
	// Try going out to the fifth pixel below some cut
	if(jcol==NaxisX-1) continue;
	thiscol = jcol;
	counter = 0;
	getout = 0;
	Nbelowthresh = 0;
	while((!getout) && (counter < 25) && (thiscol < NaxisX) ) {
	  //If its too low, we mask it.
	  // if its really high, it may be an object
	  // mask it if its high, but not too high.
	  if(((imagearray[thiscol][jrow]> (lavg + 1.*lrms)) || 
	     (imagearray[thiscol][jrow] < (lavg - 1.*lrms))) &&
	    (jrow <=40 || NaxisY-40 <=jrow) ) {
	    /*
	      This is an attempt to get the horizontal pixel bleeding near the 
	      chip boundarys 
	     */
	    maskarray3[thiscol][jrow] = 0;
	    // counter++;
	    thiscol++;
	    continue;
	  }
	  else if(((imagearray[thiscol][jrow]> (lavg + 2.*lrms)) &&
	      (imagearray[thiscol][jrow]< (lavg + 8.*lrms))) || 
	     (imagearray[thiscol][jrow] < (lavg - 1.*lrms))) {
	    maskarray3[thiscol][jrow] = 0;
	    counter++;
	    thiscol++;
	    continue;
	  }

	  // Normal range, lets count 5 of these before we're done 
	  else if(imagearray[thiscol][jrow] < (lavg + 2.*lrms)){
	    maskarray3[thiscol][jrow] = 0;
	    counter++;
	    thiscol++;
	    Nbelowthresh++;
	    if(Nbelowthresh>5) { getout = 1; }
	    continue;
	  }

	  // if its too high, it might be an object, 
	  // and let's leave those alone...
	  //  This could just be an "else"...
	  else if( imagearray[thiscol][jrow] > (lavg + 4.*lrms)){ 
	    getout = 1;
	    continue;
	  }
	}
	flag = 0;
      }

      else if(val < 0.5 && !flag) { // left egde of region
	if(jcol==0) {
	  flag = 1;
	  continue;
	}
	thiscol = jcol;
	counter = 0;
	getout = 0;
	Nbelowthresh = 0;
	// same logic here as above:
	while((!getout) && (counter < 25) && (thiscol > 0)) {
	  //If its too low, we mask it.
	  // if its really high, it may be an object
	  // mask it if its high, but not too high.
	  if(((imagearray[thiscol][jrow]> (lavg + 1.*lrms)) || 
	     (imagearray[thiscol][jrow] < (lavg - 1.*lrms))) &&
	    (jrow <=40 || NaxisY-40 <=jrow) ) {
	    /*
	      This is an attempt to get the horizontal pixel bleeding near the 
	      chip boundarys 
	     */
	    maskarray3[thiscol-1][jrow] = 0;
	    // counter++;
	    thiscol--;
	    continue;
	  }
	  else if((imagearray[thiscol-1][jrow]> (lavg + 2.*lrms)  && 
	      (imagearray[thiscol-1][jrow]< (lavg + 8.*lrms))) ||
	     (imagearray[thiscol-1][jrow]< (lavg - 1.*lrms))) {
	    maskarray3[thiscol-1][jrow] = 0;
	    counter++;
	    thiscol--;
	    continue;
	  }
	  else if(imagearray[thiscol-1][jrow]< (lavg + 2.*lrms)) {
	    maskarray3[thiscol-1][jrow] =0;
	    counter++;
	    thiscol--;
	    Nbelowthresh++;
	    if(Nbelowthresh>5) { getout = 1; }
	    continue; 
	  }
	  else if( imagearray[thiscol-1][jrow]> (lavg + 6.*lrms)) { 
	    getout = 1;
	    continue;
	  }
	}
	flag = 1;
      }
    } 
  } 
 

  // Now check for spread vertically
  if(v) cout<<"Expanding vertically"<<endl;
  //Set up Fit vars
  int nparams = 3;
  double parameters[3] = {0,0,0}; 
  double chisq = -1;
  double** covar;
  int isgood = 0;
  double *xFitval;// = new double[nPts];
  double *yFitval;// = new double[nPts];
	
  if(v) cout<<"Set stuff up for the fit below"<<endl;

  for(int jcol = 0; jcol<NaxisX; jcol++) {

    int getout = 0;
    int flag = 0;
    int thisrow; 
    int counter;
    int Nbelowthresh ;
    int colcount=0;// keep track of how long these masks are...
    int maskstartfinal= 0; // keep track of where the mask starts...

    for(int jrow = 0; jrow< NaxisY; jrow++) {
      float val = maskarray2[jcol][jrow];

      if(val > 0.5 && !flag ) {
	continue; // Nothin doin
      }
      else if(val < 0.5 && flag) {//in a masked region, do nothing
	colcount++;
	continue;
      }
      else if(val > 0.5 && flag) { // top egde of region

	if(jrow==NaxisY-1)continue;
	colcount++;
	thisrow = jrow;
	counter = 0;
	getout = 0;
	Nbelowthresh = 0;
	

	// same as above
	while((!getout) && (counter < 500) && (thisrow < NaxisY) ) {
	  /* I don't have quite the same logic here, if we cover an object,
	     /* so be it. */  
	  if(((imagearray[jcol][thisrow] > (lavg + 2.*lrms)) ||
	     (imagearray[jcol][thisrow] < (lavg - 1.*lrms)))) {
	    maskarray3[jcol][thisrow] = 0;
	    counter++;
	    thisrow++;
	    colcount++;
	    if(thisrow >= NaxisY) getout = 1;
 	    continue; 
	  }
	  else if(imagearray[jcol][thisrow] < (lavg + 2.*lrms)) {
	    maskarray3[jcol][thisrow] = 0;
	    counter++;
	    thisrow++;
	    colcount++;
	    Nbelowthresh++;
	    if(Nbelowthresh>5) { getout = 1; }
	    if(thisrow >= NaxisY) getout = 1;
	    continue;
	  }
	  else if( imagearray[jcol][thisrow] > (lavg + 4.*lrms)) { 
	    getout = 1;
	    continue;
	  }
	}

	
	if(whichfilter>0) {
	  // filter dependant masking!!!!  This'll be fun.
	  double high_frac;
	  double low_frac;
	  // these are set by hand.  Sorry.  Maybe later, I'll add them as options 
	  if(whichfilter==1)      {cout<<"Using B Mask"<<endl;  high_frac= 0.8; low_frac= 0.3;}//B
	  else if(whichfilter==2) {cout<<"Using V Mask"<<endl; high_frac= 0.25; low_frac= 0.25;}//V
	  else if(whichfilter==3) {cout<<"Using R Mask"<<endl; high_frac= 0.5; low_frac= 0.3;}//R
	  else if(whichfilter==4) {cout<<"Using I Mask"<<endl; high_frac= 0.3; low_frac= 0.3;}//I
	  else if(whichfilter==5) {cout<<"Using Z Mask"<<endl; high_frac= 0.5; low_frac= 0.5;}//Z

	  if(is6) {low_frac=5; cout<<"Is Chip 6: Extending lower mask"<<endl;}
	  
	  int extramasks_high = (int) (high_frac * 1.*colcount);
	  int extramasks_low =  (int) (low_frac * 1.*colcount);
	  
	  cout<<"Extra Masks: "<< maskstartfinal - extramasks_low<<"-"<<maskstartfinal<<"   "<<
	    thisrow <<"-"<<thisrow+extramasks_high<<" col "<<jcol<<
	    "  colcount "<<colcount<<endl;
	  for(int rowmaskiter = maskstartfinal - extramasks_low; rowmaskiter<=maskstartfinal; rowmaskiter++) { 
	    // cout<< rowmaskiter<<endl;
	    if(!(rowmaskiter<0 || rowmaskiter> NaxisY-1)) {
	      //cout<<"Masking "<<jcol<<","<<rowmaskiter<<endl;
	      maskarray3[jcol][rowmaskiter] = 0;}
	  }
	  
	  for(int rowmaskiter = thisrow; rowmaskiter<=thisrow + extramasks_high; rowmaskiter++) { 
	    // cout<< rowmaskiter<<endl;
	    if(rowmaskiter<0 || rowmaskiter> NaxisY-1) continue;
	    maskarray3[jcol][rowmaskiter] = 0;
	  }
	}
	colcount = 0;
	flag = 0;
      }
      else if(val < 0.5 && !flag) { // bottom egde of region	
	if(jrow <5){
	  for(int irow = 0; irow<=5; irow++) {
	    maskarray3[jcol][irow] = 0;
	  }
	  continue;
	}
	thisrow = jrow;
	counter = 0;
	getout = 0;
	Nbelowthresh = 0;

	//Because the spread below the spikes is so bad, 
	// we have a different scheme.  We fit for the 
	// long tail, and cut at some point there.
	
	// place to start fitting
	int fitstart = 0;  
	if(jrow>250) fitstart = jrow-250;  
	else fitstart = 0;  

	// place to stop fitting
	int fitstop = jrow;  
	//number of fit points
	int nPts = fitstop - fitstart +1;  
	
	// make data arrays
	double *xFitval = new double[nPts];   
	double *yFitval = new double[nPts];  
	
	// fill the arrays
	for(int ipt = fitstart; ipt <= fitstop; ipt++) {  
	  xFitval[ipt-fitstart] = ipt;  
	  yFitval[ipt-fitstart] = imagearray[jcol][ipt];  
	}  
	// reasonable guesses
	double guess[3] = {lavg, 0.03, fitstart}; 
	//	if(v) cout<<"Guessing  ("<<lavg<<","<<0.03<<","<<fitstart<<") for col "<<jcol<<"row "<<jrow<<endl;
	int iter = 0; isgood = 0;  
	// The fitter is touchy, so I'll try to fit it 5 times with different 
	//  parameters.  If it failes it fails

	// in fact, its so bad... I've removed it.

	while((!getout) && (counter < 500)) {
	    if((imagearray[jcol][thisrow-1] > (lavg + 2.*lrms) ||
		imagearray[jcol][thisrow-1] < (lavg - 2.*lrms))) {
	      maskarray3[jcol][thisrow-1] = 0;
	      counter++;
	      thisrow--;
	      colcount++;
	      if(thisrow<=0) getout = 1;
	      continue;
	    }
	    else if(imagearray[jcol][thisrow-1] < (lavg + 2.*lrms)){
	      maskarray3[jcol][thisrow-1] = 0;
	      counter++;
	      thisrow--;
	      colcount++;
	      Nbelowthresh++;
	      if(Nbelowthresh>5) { getout = 1; }
	      if(thisrow<=0) getout = 1;
	      continue;
	    }
	    // This, I think is wholly unnecessary
	    else if( imagearray[jcol][thisrow-1] > (lavg + 6.*lrms)){ 
	      getout = 1;
	      continue;	      
	    }
	    

	  }
	
	cout<<"thisrow = "<<thisrow<<endl;
	maskstartfinal = thisrow;

	flag = 1;	

	
	delete [] xFitval;
	delete [] yFitval;

      }
    }
  }
  

  if(is6){
    // here we will mae a second pass in an attempt to
    // get more of those nasty pixel bleeding buggers.  

    int Nmasks = 250;
    for(int i=0; i<NaxisX; i++) {
      for(int j=0; j<NaxisY; j++) {
	if(imagearray[i][j] > 35000 ) {
	  for(int thisj = j; thisj>=j-Nmasks; thisj--) { 	    
	    if(thisj>=0){
	      maskarray3[i][thisj]=0;
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
      array[jj][ii] = maskarray3[ii][jj];  
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
