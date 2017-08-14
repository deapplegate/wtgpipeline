/**
 * @file leastsq
 * @author Douglas Applegate
 * @date 4/1/08
 *
 * @brief Implementation of Leastsq
 */

//CVSID $Id: leastsq.cxx,v 1.2 2008-04-11 22:27:22 mallen Exp $

#include "leastsq.h"
#include <gsl/gsl_multifit_nlin.h>

using namespace std;

typedef int (Leastsq::*GSLVectorMemberFunc)(const gsl_vector*, void*, 
					    gsl_vector*);
typedef int (Leastsq::*GSLMatrixMemberFunc)(const gsl_vector*, void*,
					   gsl_matrix*);

//////////////////////////////////////
//HELPER STRUCTS
//////////////////////////////////////

typedef struct gslfunctor {

  Leastsq* leastsq;
  GSLVectorMemberFunc f;
  GSLMatrixMemberFunc df;

} GSLFunctor;

///////////////////////////////////////
//HELPER FUNCTIONS
///////////////////////////////////////

double* convertGSLVector(const gsl_vector* gslvector){
  
  double* target = new double[gslvector->size];
  for (int i=0; i < gslvector->size; i++){
    target[i] = gsl_vector_get(gslvector, i);
  }

  return target;
};

///////////////////

int gslF(const gsl_vector* params, void* functor, gsl_vector* result){
  
  GSLFunctor* gslfunctor = 
    static_cast<GSLFunctor*>(functor);

  Leastsq* obj  = gslfunctor->leastsq;
  GSLVectorMemberFunc func = gslfunctor->f;

  return (obj->*func)(params, NULL, result);

};

/////////////////////

int gslDF(const gsl_vector* params, void* functor, gsl_matrix* jacobian){
  GSLFunctor* gslfunctor = 
    static_cast<GSLFunctor*>(functor);

  Leastsq* obj  = gslfunctor->leastsq;
  GSLMatrixMemberFunc func = gslfunctor->df;

  return (obj->*func)(params, NULL, jacobian);

}

/////////////////////

int gslFDF(const gsl_vector* params, 
	       void* data, 
	       gsl_vector* result,
	       gsl_matrix* jacobian){

  gslF(params, data, result);
  gslDF(params, data, jacobian);
  return GSL_SUCCESS;

}


////////////////////////////////////////
//Leastsq Implementation
/////////////////////////////////////

Leastsq::Leastsq(FitFunction_t fitFunc, FitFunction_t* dfitFunc, int nparams){

  _fitFunc = fitFunc;
  _dfitFunc = dfitFunc;
  _nparams = nparams;
  _chisq = -1;

  _parameters = new double [nparams];
  
  _covar = new double* [nparams];
  for (int i=0; i < nparams; i++){
    _covar[i] = new double [nparams];
  }

};

///////////////////////////////////////

Leastsq::~Leastsq(){

  delete [] _parameters;
  _parameters = NULL;

  for(int i=0; i < _nparams; i++){
    delete [] _covar[i];
  }
  delete [] _covar;
  _covar = NULL;

};

////////////////////////////////////////
    
int Leastsq::doFit(const double* x, const double* y, int ndata, double* guess){

  //init data structures
  _x = x;
  _y = y;
  _ndata = ndata;

  int stat;

  gsl_multifit_fdfsolver* fdfSolver = 
    gsl_multifit_fdfsolver_alloc(gsl_multifit_fdfsolver_lmsder,
				 ndata,
				 _nparams);
  if (fdfSolver == NULL){
    return 0;
  }

  gsl_vector_view gslGuess_view = gsl_vector_view_array(guess, _nparams);
  gsl_vector* gslGuess = &gslGuess_view.vector;

  GSLFunctor functor;
  functor.leastsq = this;
  functor.f = &Leastsq::gslFitFunction;
  functor.df = &Leastsq::gslDFitFunction;
  
  gsl_multifit_function_fdf gslFunctions;
  gslFunctions.f = &gslF;
  gslFunctions.df = &gslDF;
  gslFunctions.fdf = &gslFDF;
  gslFunctions.n = ndata;
  gslFunctions.p = _nparams;
  gslFunctions.params = &functor;

  stat = gsl_multifit_fdfsolver_set(fdfSolver, 
				    &gslFunctions,
				    gslGuess);


  //main iteration
  stat = GSL_CONTINUE;
  int iter = 0;
  while (stat == GSL_CONTINUE && iter < 500){
    stat = gsl_multifit_fdfsolver_iterate(fdfSolver);
   
    if (stat)
      break;

    stat = gsl_multifit_test_delta(fdfSolver->dx,
				     fdfSolver->x,
				     1e-4, 1e-4);
  }

  if (stat == GSL_SUCCESS){

    //extract params
    gsl_vector* gslParams = fdfSolver->x;
    for (int i=0; i < _nparams; i++){
      _parameters[i] = gsl_vector_get(gslParams, i);
    }

    //calc residuals
    gsl_vector* funcVals = fdfSolver->f;
    _chisq = 0.;
    for (int i=0; i < _ndata; i++){
      _chisq += pow(gsl_vector_get(funcVals, i), 2);
    }


    //read covar matrix
    gsl_matrix* covar = gsl_matrix_alloc(_nparams, _nparams);
    gsl_multifit_covar(fdfSolver->J, 0.0, covar);
  
    for (int i=0; i < _nparams; i++){
      for (int j=0; j < _nparams; j++){
	_covar[i][j] = gsl_matrix_get(covar,i,j);
      }
    }
    gsl_matrix_free(covar);
  }
  
  gsl_multifit_fdfsolver_free(fdfSolver);

  return (stat == GSL_SUCCESS) ? 1 : 0;

  

};

////////////////////////////////////////

int Leastsq::gslFitFunction(const gsl_vector* gslParams, 
			    void* gslData, 
			    gsl_vector* result){
  
  double* params = convertGSLVector(gslParams);

  for(int i = 0; i < _ndata; i++){
   double val  = _fitFunc(_x[i], params) - _y[i];
   gsl_vector_set(result, i, val);
  }

  delete [] params;

  return GSL_SUCCESS;

};

///////////////////////////////////////////

int Leastsq::gslDFitFunction(const gsl_vector* gslParams,
			     void* gslData,
			     gsl_matrix* Jacobian){

  double* params = convertGSLVector(gslParams);

  for(int curdata = 0; curdata < _ndata; curdata++){

    for (int curparam = 0; curparam < _nparams; curparam++){
      
      double val = _dfitFunc[curparam](_x[curdata], params);
      gsl_matrix_set(Jacobian, curdata, curparam, val);

    }

  }

  

  delete [] params;

  return GSL_SUCCESS;

};

