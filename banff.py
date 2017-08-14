##############

import pymc, numpy as np
import banff_tools

##############

def computeDeltas(querypoints):

    cleaned_xpoints = []
    for x in querypoints:
        if x not in cleaned_xpoints:
            cleaned_xpoints.append(x)

    xpoints = np.sort(np.array(cleaned_xpoints))

    edges = [0.]
    for i in range(len(xpoints) - 1):
        curx = xpoints[i]
        nextx = xpoints[i+1]
        edges.append( (curx + nextx)/2. )
    edges.append(1.)
    edges = np.array(edges)

    deltas =  (np.roll(edges, -1) - edges)[:-1]

    delta_cat = {}
    for x, delta in zip(xpoints, deltas):
        delta_cat[x] = delta

    return np.array([delta_cat[x] for x in querypoints])


##################



##############

def BanffModel(background1, background2, signal, data, nbootstraps = 1000, free_ks = True):

    print 'sorting'

    background1 = np.sort(background1)
    background2 = np.sort(background2)
    signal = np.sort(signal)
    data = np.sort(data)
    
    print len(data)

    nevents = len(data)

    print 'deltas'

    deltas = computeDeltas(data)

    print 'bootstraps'
    
    background1_pdfs = \
        np.array([banff_tools.computePDF(np.sort(background1[np.random.randint(0, 
                                                           len(background1), 
                                                           len(background1))]), 
                             data, deltas) \
                      for i in range(nbootstraps)])

    background2_pdfs = \
        np.array([banff_tools.computePDF(np.sort(background2[np.random.randint(0, 
                                                           len(background2), 
                                                           len(background2))]), 
                             data, deltas) \
                      for i in range(nbootstraps)])

    signal_pdfs = \
        np.array([banff_tools.computePDF(np.sort(signal[np.random.randint(0, 
                                                      len(signal), 
                                                      len(signal))]), 
                             data, deltas)
                  for i in range(nbootstraps)])

    print 'end bootstraps'

    
    ################
    
    
    kb1 = pymc.Uniform('kb1', 0., 1.)

    ###

    if free_ks:
    
        @pymc.stochastic
        def ks(value =0.0, kb1 = kb1):
            if value >= 0. and value + kb1 <= 1:
                return 0
            return -np.infty
    else:
        ks = 0.

    ###

    @pymc.deterministic
    def kb2(kb1 = kb1, ks = ks):
        return 1 - kb1 - ks

    
    #################

    @pymc.stochastic(observed = True)
    def likelihood(value = data, kb1 = kb1, kb2 = kb2, ks = ks):

#        logprob_b1rate = pymc.truncnorm_like(kb1*nevents, 900, 90, 0, 100000)        
#        logprob_b2rate = pymc.truncnorm_like(kb2*nevents, 100, 100, 0, 100000)

        logprob_b1rate = 0
        logprob_b2rate = 0

        
        log_dataprob = np.sum(np.log(np.sum(kb1 * background1_pdfs + \
                                                kb2*background2_pdfs + \
                                                ks*signal_pdfs, axis=0)))
        
        return logprob_b1rate + logprob_b2rate + log_dataprob


    
    return locals()
