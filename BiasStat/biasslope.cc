#include <iostream>
#include <stddef.h>
#include "FitsObj.h"
#include <fitsio.h>
#include <fitsio2.h>
#include <longnam.h>
//#include "/afs/slac/g/ki/include/fitsio.h"
//#include "/afs/slac/g/ki/include/fitsio2.h"
//#include "/afs/slac/g/ki/include/longnam.h"
#include <cmath>
//#include <gsl/gsl_fit.h>

using namespace std;

int main( int argc, char** argv ) {
 
  // if( argc!=3 && argc!=2 ) {
    
  //    std::cerr <<"Usage: " << argv[0] << " <inputfile> (verboseflag)"<< std::endl;
  // ::exit(1);
  //  }

  int v = 0;
  if(argc==4) v = 1;


  //for(int j = 1; j < argc; j++) {
  int j=1;
    char* filename = argv[j];
    FitsObj img(filename);
    
    //make array for slope 

    double* biasvalsX = new double[img.NaxisX];
    double* biasvalsY = new double[img.NaxisY];
    
    for(int i=0; i<img.NaxisX; i++){
      biasvalsX[i]=img.AvgCol(i);
    }
    
    for(int i=0; i<img.NaxisY; i++){
      biasvalsY[i]=img.AvgRow(i);
    }
  
    //Getting parameters:
    double y_i =0;
    double sum_xi2 =0;
    double sum_yi = 0;
    double sum_xi  = 0;
    double sum_xy = 0;
    
    
    for(int i=0; i<img.NaxisX; i++){
      y_i = biasvalsX[i];
      
      sum_xi += i;
      sum_xi2 += i*i;
      sum_yi += y_i;
      sum_xy += i*y_i;
    }
    

    double rowpars[2] = { ((sum_xi2 * sum_yi - sum_xi * sum_xy) / 
			   (img.NaxisX * sum_xi2 - sum_xi * sum_xi)),
			  ((img.NaxisX * sum_xy - sum_xi * sum_yi) / 
			   (img.NaxisX * sum_xi2 - sum_xi * sum_xi)) };
    
    
    y_i =0;
    sum_xi2 =0;
    sum_yi = 0;
    sum_xi  = 0;
    sum_xy = 0;
    

    for(int i=0; i<img.NaxisY; i++) {
      y_i = biasvalsY[i];
      
      sum_xi += i;
      sum_xi2 += i*i;
      sum_yi += y_i;
      sum_xy += i*y_i;
    }
    
    
    double colpars[2] = { ((sum_xi2 * sum_yi - sum_xi * sum_xy) / 
			   (img.NaxisY * sum_xi2 - sum_xi * sum_xi)),
			  ((img.NaxisY * sum_xy - sum_xi * sum_yi) / 
			   (img.NaxisY * sum_xi2 - sum_xi * sum_xi)) };
    
    //For chisquare stat, I'm assuming a sigma of 4.75, 
    // a typical value of the 
    // bias frames I've seen.  
    
    // take error on avg to be 4.75/sqrt(N) ~ 0.2-0.4
    
    double chi2x = 0;
    int Ndofx = img.NaxisX;
    double chi2y = 0;
    int Ndofy = img.NaxisY;
  
    double sigmax2 = 1;//(4.75/sqrt(img.NaxisX)) * (4.75/sqrt(img.NaxisX));
    double sigmay2 = 1;//(4.75/sqrt(img.NaxisY)) * (4.75/sqrt(img.NaxisY));
    


    for(int i=0; i<img.NaxisX; i++){
      chi2x += (biasvalsX[i] - (rowpars[0] + rowpars[1]* i)) * (biasvalsX[i] - (rowpars[0] + rowpars[1]* i)) /sigmax2   ;      
      
  }
    
    for(int i=0; i<img.NaxisY; i++){
      chi2y += (biasvalsY[i] - (colpars[0] + colpars[1]* i)) * (biasvalsY[i] - (colpars[0] + colpars[1]* i) ) /sigmay2    ;      
    }
    
    cout<<"#   Filename   Xdir:  Slope     intercept     Residual    Ydir: Slope     intercept     Residual     Bad Fraction"<<endl;
    
    cout<<"In: "<< filename<<" ";

    cout << rowpars[1]*img.NaxisX<<"   "<< rowpars[0] << 
      "   "<< chi2x/Ndofx<<"   ";
    
    cout<< colpars[1]*img.NaxisY << 
      "   "<< colpars[0]<<
      "   "<< chi2y/Ndofy <<"  "<<img.FracBadPixels()  <<endl;
     
    // }
  
  //  if(v) cout<<"{";
  //for(int i = 0; i< img.NaxisY; i++){
  //if(v) cout<<biasvalsY[i]<<",";
  //}
  //if(v) cout<<"}"<<endl;

 
} 
