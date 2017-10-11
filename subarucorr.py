import astropy, astropy.io.fits as pyfits, numpy, scipy, sys, re,pylab

def mypoly(a, x):
    #n = n terms in fit
    # float *a = poly terms,
    # x; = val array
    
    y = [1.]
    t = [x]
    print 'printing x'
    print x

    z=y[0]*t[0]

    #NORMPOINT = 10000
    
    for i in range(1,len(a)+1):
        t.append(t[i-1]*x)
        y.append(a[i-1])
        print 'i='+str(i) + ' a = '+str(a[i-1])

    for i in range(1,len(a)+1):
        print t[i]
        print y[i] 
        
        z+=t[i]*y[i]
        # for (i=0; i<n; i++) {


        # y += a[i]*t
        # t *= x
        #print y
    #     
    # y *= x
    #NORMPOINT = 10000
    #scale = NORMPOINT/mypoly(a, NORMPOINT)
    
    return z



def mypoly_mult(a, x):
    #n = n terms in fit
    # float *a = poly terms,
    # x; = val array
    
    y = [1.]
    t = [1.]
    print 'printing x'
    print x

    #z=y[0]*t[0]
    z=0
    #NORMPOINT = 10000
    
    for i in range(1,len(a)+1):
        t.append(t[i-1]*x)
        y.append(a[i-1])
        print 'i='+str(i) + ' a = '+str(a[i-1])

    for i in range(1,len(a)+1):
        print t[i]
        print y[i] 
        
        z+=t[i]*y[i]
        # for (i=0; i<n; i++) {


        # y += a[i]*t
        # t *= x
        #print y
    #     
    # y *= x
    #NORMPOINT = 10000
    #scale = NORMPOINT/mypoly(a, NORMPOINT)
    
    return z



def mypoly_char(txt,x):
    # here txt must be the early chip name.
    params={}
    params['w9c2']=[-6.85636e-05,
                    7.34159e-09,
                    -3.49597e-13,
                    6.25578e-18]
    
    params['w4c5']=[-0.000229013,
                    4.99811e-08,
                    -5.86075e-12,
                    3.40795e-16,
                    -5.24326e-21,
                    -3.25813e-25,
                    1.12422e-29]
    
    params['w6c1']= [-7.02288e-05,
                     7.6895e-09,
                     -3.75244e-13,
                     6.88234e-18]
    
    params['w7c3']= [-0.000218723,
                     4.55178e-08,
                     -5.06917e-12,
                     2.77035e-16,
                     -3.58369e-21,
                     -2.74045e-25,
                     8.65118e-30]
    if txt in ['w9c2', 'w4c5','w6c1','w7c3']:
        return mypoly(params[txt],x)
    else:
        print 'no correction for :', txt
        return x



def mypoly_new_char(txt,x):
    # here txt must be the early chip name.
    params={}
    params['w9c2']=[ 1.17970e+00,
                     -3.76728e-05,
                     1.53093e-09,
                     1.56436e-13,
                     -1.63457e-17,
                     5.45417e-22,
                     -6.33405e-27]
    
    params['w4c5']=[ -0.000229013,
                     4.99811e-08,
                    -5.86075e-12,
                    3.40795e-16,
                    -5.24326e-21,
                    -3.25813e-25,
                    1.12422e-29]
    
    params['w6c1']= [9.64368e-01,
                     5.96304e-05,
                     -1.55794e-08,
                     1.65423e-12,
                     -8.58425e-17,
                     2.17863e-21,
                     -2.16169e-26]
    
    
    params['w7c3']= [-0.000218723,
                     4.55178e-08,
                     -5.06917e-12,
                     2.77035e-16,
                     -3.58369e-21,
                     -2.74045e-25,
                     8.65118e-30]

    params['si005s']=[9.45486e-01,
                      3.06580e-05,
                      -7.32848e-09,
                      9.19088e-13,
                      -5.99454e-17,
                      1.95305e-21,
                      -2.51130e-26]
    
    params['si001s']=[8.89229e-01,
                      8.05488e-05,
                      -2.45696e-08,
                      3.87417e-12,
                      -3.24538e-16,
                      1.37049e-20,
                      -2.28946e-25]

    params['si006s']=[4.27821e-01,
                     3.67858e-04,
                     -9.41304e-08,
                     1.21898e-11,
                     -8.40626e-16,
                     2.93915e-20,
                     -4.09096e-25]
    params['si002s']=[7.13973e-01,
                      2.04011e-04,
                      -5.89538e-08,
                      8.69446e-12,
                      -6.83755e-16,
                      2.73065e-20,
                      -4.34803e-25]

    
    if txt in ['w9c2', 'w4c5','w6c1','w7c3','si001s','si002s','si005s','si006s']:
        tot = 0
        y=[x]
        for i in range(1,len(params[txt])):  
            y.append(x*y[i-1])
        for i in range(len(params[txt])):            
            tot+= params[txt][i]*y[i]

        return tot
        #return mypoly(params[txt],x)
    else:
        print 'no correction for :', txt
        return x
