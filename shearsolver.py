###########################
# Solve for lensing signal for a non-spherically symmetric mass distribution
###########################

import numpy as np

##########################


def calcTangG(kappamap, scaling = (1./3600.)*(np.pi/180)):

    shear1 = np.zeros_like(kappamap)
    shear2 = np.zeros_like(kappamap)

    Y,X = np.meshgrid(scaling*np.arange(shear1.shape[1]), 
                      scaling*np.arange(shear1.shape[0]))

    D1 = lambda dx, dy: (dy**2 - dx**2) / (dx**2 + dy**2)**2
    D2 = lambda dx, dy: -2*dx*dy / (dx**2 + dy**2)**2

    for i in range(shear1.shape[0]):
        for j in range(shear1.shape[1]):
            dX = X - X[i,j]
            dY = Y - Y[i,j]
            D1s = D1(dX, dY)
            D2s = D2(dX, dY)

            keep = np.isfinite(D1s)

            shear1[i,j] = np.sum((D1s*kappamap*scaling**2)[keep])/np.pi
            shear2[i,j] = np.sum((D2s*kappamap*scaling**2)[keep])/np.pi

    g1 = shear1 / (1 - kappamap)
    g2 = shear2 / (1 - kappamap)

    g = g1 + complex(0,1)*g2
    
    center = scaling*np.array([float(shear1.shape[0])/2., float(shear1.shape[1])/2.])

    dX = X - center[0]
    dY = Y - center[1]
    phi = np.arctan2(dY, dX)

    gtan = -np.real(g*np.exp(complex(0, -2)*phi))
    gcross = -np.imag(g*np.exp(complex(0, -2)*phi))

    return (shear1, shear2), (g1, g2), phi, (gtan, gcross)


def kappa(xsize, ysize, sigx, sigy, amp, phi = 0.):

    Y,X = np.meshgrid(np.arange(ysize), np.arange(xsize))

    kappa = np.zeros((xsize, ysize))
    
    dX = X - float(xsize)/2.
    dY = Y - float(ysize)/2.
    
    cov = np.array([[sigx, 0], [0, sigy]])
    invcov = np.linalg.inv(cov)

    rot = np.array([[np.cos(phi),-np.sin(phi)], [np.sin(phi),np.cos(phi)]])

    invcovp = np.dot(rot.T, np.dot(invcov, rot))
    
    for i in range(xsize):
        for j in range(ysize):
            dR = np.array([dX[i,j], dY[i,j]])
            kappa[i,j] = amp*np.exp(-0.5*np.dot(dR, np.dot(invcovp, dR)))

    return kappa
