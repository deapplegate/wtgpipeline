
# entry point for the input form to pass values back to this script
def setValues(tH0,tWM,tWV,tz,tmnue,tmnumu,tmnutau,tw,twp,tT0):
  H0 = tH0
  h = H0/100
  WM = tWM
  WV = tWV
  z = tz
  WR = 2.477E-5/(h*h)	# does not include neutrinos, T0 = 2.72528
  WK = 1-WM-WR-WV
  mnue = tmnue
  mnumu = tmnumu
  mnutau = tmnutau
  w = tw
  wp = twp
  T0 = tT0
  compute()

# tangential comoving distance
def DCMT(WK,DCMR):
  import math
  ratio = 1.00
  x = math.sqrt(abs(WK))*DCMR
  # document.writeln("DCMR = " + DCMR + "<BR>")
  # document.writeln("x = " + x + "<BR>")
  if (x > 0.1): 
    if (WK > 0) : ratio = 0.5*(math.exp(x)-math.exp(-x))/x 
    else: ratio = math.sin(x)/x
    # document.writeln("ratio = " + ratio + "<BR>")
    y = ratio*DCMR
    return y
  y = x*x
# statement below fixed 13-Aug-03 to correct sign error in expansion
  if (WK < 0): y = -y
  ratio = 1 + y/6 + y*y/120
  # document.writeln("ratio = " + ratio + "<BR>")
  y= ratio*DCMR
  return y

# comoving volume computation
def VCM(WK,DCMR):
  import math
  ratio = 1.00
  x = math.sqrt(abs(WK))*DCMR
  if (x > 0.1) :
    if (WK > 0) : ratio = (0.125*(math.exp(2*x)-math.exp(-2*x))-x/2)/(x*x*x/3) 
    else: ratio =(x/2 - math.sin(2*x)/4)/(x*x*x/3) 
    y = ratio*DCMR*DCMR*DCMR/3
    return y
  y = x*x
# statement below fixed 13-Aug-03 to correct sign error in expansion
  if (WK < 0): y = -y
  ratio = 1 + y/5 + (2/105)*y*y
  y = ratio*DCMR*DCMR*DCMR/3
  return y

# function to give neutrino density over rest mass density
def nurho(mnurel,mnu):
  import math
  y = math.pow(1+math.pow(mnurel/mnu,1.842),1.0/1.842)
  return y

# calculate the actual results
def compute(z,w,WM=0.27,WV=0.73):
  i=0	# index
  n=1000	# number of points in integrals
  nda = 1	# number of digits in angular size distance
  H0 = 71.	# Hubble constant
  #WM = 0.27	# Omega(matter)
  #WV = 0.73	# Omega(vacuum) or lambda
  WR = 0.	# Omega(radiation)
  WK = 0.	# Omega curvaturve = 1-Omega(total)
  Wnu = 0.    # Omega from massive neutrinos
  #z = 3.0	# redshift of the object
  h = 0.71	# H0/100
  mnue = 0.001     # mass of electron neutrino in eV
  mnumu = 0.009    # mass of muon neutrino in eV
  mnutau = 0.049   # mass of tau neutrino in eV
  we = mnue/93.     # Omega(nu(e))h^2
  wmu = mnumu/93.   # Omega(nu(mu))h^2
  wtau = mnutau/93. # Omega(nu(tau))h^2
  mnurel = 0.0005  # mass of neutrino that is just now relativistic in eV
  T0 = 2.72528     # CMB temperature in K
  c = 299792.458 # velocity of light in km/sec
  Tyr = 977.8 # coefficent for converting 1/H into Gyr
  DTT = 0.5	# time from z to now in units of 1/H0
  DTT_Gyr = 0.0	# value of DTT in Gyr
  age = 0.5	# age of Universe in units of 1/H0
  age_Gyr = 0.0	# value of age in Gyr
  zage = 0.1	# age of Universe at redshift z in units of 1/H0
  zage_Gyr = 0.0	# value of zage in Gyr
  DCMR = 0.0	# comoving radial distance in units of c/H0
  DCMR_Mpc = 0.0
  DCMR_Gyr = 0.0
  DA = 0.0	# angular size distance
  DA_Mpc = 0.0
  DA_Gyr = 0.0
  kpc_DA = 0.0
  DL = 0.0	# luminosity distance
  DL_Mpc = 0.0
  DL_Gyr = 0.0	# DL in units of billions of light years
  V_Gpc = 0.0
  a = 1.0	# 1/(1+z), the scale factor of the Universe
  az = 0.5	# 1/(1+z(object))
  #w = -1.     # equation of state, w = P/(rno*c^2)
  wp = 0.     # rate of change of equation of state, w(a) = w+2*wp*(1-a)
  #	following Linder, astro-ph/040250

  import math
  h = H0/100.
  WR = 2.477E-5*math.pow(T0/2.72528,4)/(h*h)	# no neutrinos
# avoid dividing by zero neutrino mass
  if (mnue < 0.00001): mnue = 0.00001
  if (mnumu < 0.00001): mnumu = 0.00001
  if (mnutau < 0.00001): mnutau = 0.00001
# rest mass omega*h^2 for the three neutrino types
  we = (mnue/93.64)*math.pow(T0/2.72528,3)
  wmu = (mnumu/93.90)*math.pow(T0/2.72528,3)
  wtau = (mnutau/93.90)*math.pow(T0/2.72528,3)
# mass of nu that is just now relativistic
# evaluates at 3.151*kT with T = (4/11)^(1/3)*To and To=2.72528
# This is 6.13 K, and 1 eV is 11604.5 K
  mnurel = 6.13*(T0/2.72528)/11604.5
  Wnu = (we*nurho(mnurel,mnue)+wmu*nurho(mnurel,mnumu)+wtau*nurho(mnurel,mnutau))/(h*h)
  WK = 1-WM-WR-WV
  WM = WM-Wnu
  az = 1.0/(1+1.0*z)
  age = 0
# do integral over a=1/(1+z) from 0 to az in n steps, midpoint rule
  for i in range(n): #(i = 0 i != n i++) {
    a = az*(i+0.5)/n
#    rho(DE) = a^{-3-3*w_o-6*w'}*exp(6*w'*(a-1))*rho_o(DE)
#    based on w = w_o+w_a*(1-a) with w_a = 2*w': Linder astro-ph/0402503
    rhoV = WV*math.pow(a,-3-3*w-6*wp)*math.exp(6*wp*(a-1))
# get neutrino density corrected for kT/mc^2 by using lower mass
# instead of higher T:
    Wnu = (we*nurho(mnurel,mnue*a)+wmu*nurho(mnurel,mnumu*a)+wtau*nurho(mnurel,mnutau*a))/(h*h)
    adot = math.sqrt(WK+((WM+Wnu)/a)+(WR/(a*a))+(rhoV*a*a))
    age = age + 1/adot
  zage = az*age/n
# correction for annihilations of particles not present now like e+/e-
# added 13-Aug-03 based on T_vs_t.f
  lpz = math.log((1+1.0*z))/math.log(10.0)
  dzage = 0
  if (lpz >  7.500): dzage = 0.002 * (lpz -  7.500)
  if (lpz >  8.000): dzage = 0.014 * (lpz -  8.000) +  0.001
  if (lpz >  8.500): dzage = 0.040 * (lpz -  8.500) +  0.008
  if (lpz >  9.000): dzage = 0.020 * (lpz -  9.000) +  0.028
  if (lpz >  9.500): dzage = 0.019 * (lpz -  9.500) +  0.039
  if (lpz > 10.000): dzage = 0.048
  if (lpz > 10.775): dzage = 0.035 * (lpz - 10.775) +  0.048
  if (lpz > 11.851): dzage = 0.069 * (lpz - 11.851) +  0.086
  if (lpz > 12.258): dzage = 0.461 * (lpz - 12.258) +  0.114
  if (lpz > 12.382): dzage = 0.024 * (lpz - 12.382) +  0.171
  if (lpz > 13.055): dzage = 0.013 * (lpz - 13.055) +  0.188
  if (lpz > 14.081): dzage = 0.013 * (lpz - 14.081) +  0.201
  if (lpz > 15.107): dzage = 0.214
  zage = zage*10.0**dzage
#
  zage_Gyr = (Tyr/H0)*zage
  DTT = 0.0
  DCMR = 0.0
# do integral over a=1/(1+z) from az to 1 in n steps, midpoint rule
  for i in range(n):
    a = az+(1-az)*(i+0.5)/n
    rhoV = WV*math.pow(a,-3-3*w-6*wp)*math.exp(6*wp*(a-1))
    Wnu = (we*nurho(mnurel,mnue*a)+wmu*nurho(mnurel,mnumu*a)+wtau*nurho(mnurel,mnutau*a))/(h*h)
    adot = math.sqrt(WK+((WM+Wnu)/a)+(WR/(a*a))+(rhoV*a*a))
    DTT = DTT + 1/adot
    DCMR = DCMR + 1/(a*adot)

  #print az    

  DTT = (1-az)*DTT/n
  DCMR = (1-az)*DCMR/n
  age = DTT+zage
  age_Gyr = age*(Tyr/H0)
  DTT_Gyr = (Tyr/H0)*DTT
  DCMR_Gyr = (Tyr/H0)*DCMR
  DCMR_Mpc = (c/H0)*DCMR
  DA = az*DCMT(WK,DCMR)
  DA_Mpc = (c/H0)*DA
  kpc_DA = DA_Mpc/206.264806
  DA_Gyr = (Tyr/H0)*DA
  DL = DA/(az*az)
  DL_Mpc = (c/H0)*DL
  DL_Gyr = (Tyr/H0)*DL
  V_Gpc = 4*math.pi*math.pow(0.001*c/H0,3)*VCM(WK,DCMR)

  #print 'z',z,'DA_Mpc',DA_Mpc

  return DCMR













if __name__ == '__main__':

  import pylab

  cluster_z_low = 0.2
  cluster_z_high = 0.6           

  for cluster_z in [0.2,0.3,0.55]: #,1.2]:

    for w in [-1]: #.5,-1,-0.5,]:                                   
      d_cluster_low = compute(cluster_z_low,w)
      d_cluster_high = compute(cluster_z_high,w)
        
      d_cluster = compute(cluster_z,w)
      refer = (compute(0.8,w) - d_cluster)/compute(0.8,w)    

      import scipy                                             
      ratios_save = []
      zs = []
      for z in scipy.arange(cluster_z,3.,0.1):
        zs.append(z)
        s = compute(z,w) 
        #ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
        ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
        #nprint ratio, s, d_cluster, z
        #ratios.append(ratio)
        ratios_save.append((compute(z,w) - d_cluster)/compute(z,w)/refer)

    for w in [-1.5,-1,-0.5,]:                                   
      d_cluster_low = compute(cluster_z_low,w)
      d_cluster_high = compute(cluster_z_high,w)
        
      d_cluster = compute(cluster_z,w)
      refer = (compute(0.8,w) - d_cluster)/compute(0.8,w)    
                                                                                                                                
      import scipy                                             
      ratios = []
      zs = []
      i = 0
      for z in scipy.arange(cluster_z,3.,0.1):
        zs.append(z)
        s = compute(z,w) 
        #ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
        ratio = (d_cluster_high/(1+cluster_z_high))/(d_cluster_low/(1+cluster_z_low))*(s - d_cluster_high)/(s - d_cluster_low)
        #print ratio, s, d_cluster, z
        #ratios.append(ratio)
        ratios.append((compute(z,w) - d_cluster)/compute(z,w)/refer/ratios_save[i])
        i += 1

                                                               
      pylab.plot(scipy.array(zs), scipy.array(ratios))
  pylab.savefig('shearratio.pdf')
  pylab.show()


def compute_cube():
    import scipy
    dict = {}
    for w in [-1]: #scipy.arange(-2,2,0.1):                                   
        for WM in [0.3]: #scipy.arange(0,1,0.1#):                                   
            WV = 1 - WM
            for z in scipy.arange(0,2.5,0.01):                    
                d = compute(z,w,WM,WV)
                dict['%.2f' % z + '_' + '%.2f' % w + '_' + '%.2f' % WM] = d #str(z) + '_' + str(w) + '_' + str(WM)] = d                  
                print d, z, w, WM, WV

            print dict.keys()

    import pickle 
    f = open('DA.pickle','w')
    m = pickle.Pickler(f)
    pickle.dump(dict,m)
    f.close()


def dist_ratio(zs,cluster_z=0.55,w=-1.,omega_m=0.27,omega_lambda=0.73):                
  import pylab                                                                         
  #cluster_z = 0.55                                                                    
  ratios = []                                                                          
  for z in zs:                                                                         
    d_cluster = compute(cluster_z,w,omega_m,omega_lambda)                              
    ratios.append((compute(z,w) - d_cluster)/compute(z,w,omega_m,omega_lambda))        
                                                                                       
  import scipy                                                                         
  return scipy.array(ratios)                                                           
