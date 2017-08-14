/*****************
 * @file leastsq.h
 * @date 4/1/08
 * @author Douglas Applegate
 *
 * @brief Provides a wrapper around the GSL libraries for fitting functions
 *****************/

//CVSID $Id: leastsq.h,v 1.1 2008-04-04 01:43:12 mallen Exp $

////////////////////////////////////////////////////

#ifndef LEASTSQ_H
#define LEASTSQ_H

#include <gsl/gsl_vector.h>
#include <gsl/gsl_matrix.h>


/**
 * Function prototype for fitting function and its derivative
 * @param double x position at which to evaluate function
 * @param const double* parameter values to use in evaluation
 */
typedef double (*FitFunction_t)(double, const double*);



/**
 * Provides non-linear fitting functionality
 */
class Leastsq {

 public:
  
  /**
   * Initializes object with basic fit information
   * @param fitFunc function to fit to data
   * @param dfitFunc array of fit function derivatives, one for each param
   * @param nparams number of parameters that fitFunc and dfitFunc accept
   */
  Leastsq(FitFunction_t fitFunc,
	  FitFunction_t* dfitFunc,
	  int nparams);
  
  /**
   * Default constructor
   */
  virtual ~Leastsq();
  
  /**
   * Fits function to the given data, starting at initial guess
   * @param x x values of data
   * @param y y values of data
   * @param ndata number of data points
   * @param guess initial parameter values for fit
   *
   * @returns status status code for fit. 1 == fit ran fine
   */
  int doFit(const double* x, const double* y, int ndata, double* guess);
  
  /////GETTERS
  
  double numParams() const {return _nparams;};
  
  const double** covarMatrix() const {
    return const_cast<const double**>(_covar);
  };
  
  double chisq() const {return _chisq;};
  
  const double* parameters() const {
    return const_cast<const double*>(_parameters);
  };

  
 protected:

  /////INSTANCE METHODS

  int gslFitFunction(const gsl_vector* x, 
		     void* params, 
		     gsl_vector* result);
  
  int gslDFitFunction(const gsl_vector* x, 
		      void* params, 
		      gsl_matrix* J);
  

  /////Instance Variables
  
  FitFunction_t _fitFunc; ///< Function to fit to data
  FitFunction_t* _dfitFunc; ///< Analytical derivative of fitFunc
  int _nparams; ///< Number of parameters in fitFunc and dfitFunc
  double** _covar; ///< Covariance Matrix
  double _chisq; ///< Chisq or residual from fit
  double* _parameters; ///< Best fit parameters
  const double* _x; ///< x values of data
  const double* _y; ///< y values of data
  int _ndata; ///< number of data
};


#endif 
