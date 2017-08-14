
import scipy
import scipy.interpolate.interpolate as interp

response = scipy.loadtxt('')
    
sdssSpline = interp.interp1d(specSDSS[:,0], specSDSS[:,1], 
                    bounds_error = False, 
                    fill_value = 0.)

