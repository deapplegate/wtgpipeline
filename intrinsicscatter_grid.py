####################################
# Run a grid search to constrain the ratio
#  and intrinsic scatter between two measures
####################################

import numpy as np
import stats



sqrt2pi = np.sqrt(2*np.pi)
def gauss(x, mu, std):

    result = np.zeros_like(x)

    expr = 'result = exp(-0.5*(x-mu)**2/std**2)/(sqrt2pi*std)'
    weave.blitz(expr)

    return result


def intrinsicScatter(x, y, 
                     means = np.arange(0.85, 1.15, 0.001), 
                     scatters = np.arange(0.005, 0.2, 0.0025)):
    #x and y are dictionaries with common keys.
    # the dictionary values are numpy arrays of the values for x[key] and y[key]
    # (for example, x[key] is the lensing mass and y[key] is the SZ mass for cluser "key"

              
#    return (Meangrid, Scattergrid, prob), (means, meanprob), (scatters, scatterprob)
#            2D array's                         1d arrays           1d arrays
    
    
    logprob = np.zeros((len(means), len(scatters)))

    R = {}
    logR = {}
    for item in x.keys():
        
        R[item] = y[item] / x[item]
        logR[item] = np.log(R[item])

    for i, mean in enumerate(means):
        logmean = np.log(mean)

        for j, scatter in enumerate(scatters):

            for item in logR.keys():

                
                logprob[i,j] = logprob[i,j] + stats.LogSumLogNormal(  \
                    R[item],
                    logR[item], 
                    logmean, 
                    scatter)

            
            

    prob = np.exp(logprob - np.max(logprob))
    prob = prob / np.sum(prob)
    
    meanprob = np.sum(prob, axis=-1)
    scatterprob = np.sum(prob, axis=0)

    Scattergrid, Meangrid = np.meshgrid(scatters, means)


    return (Meangrid, Scattergrid, prob), (means, meanprob), (scatters, scatterprob)


########################


#pass either means, meanprob or scatters, scatterprob as x, probs
def getdist_1d_hist(x, probs, levels = [0.68]):

    probs = probs.astype(np.float64) / np.sum(probs)

    mode = x[probs == np.max(probs)]
    
    sort_order = np.argsort(probs)[::-1]

    cumprob = np.cumsum(probs[sort_order])

    if not isinstance(levels, list):
        levels = [levels]

    level_ranges = []


    for level in levels:

        marked = np.zeros_like(x) == 1.
        stop_index = np.arange(len(sort_order))[cumprob <= level][-1] + 2
        for index in sort_order[:stop_index]:
            marked[index] = True

        ranges = []
        curRange = None
        for i in range(len(x)):

            if curRange is None and marked[i]:
                curRange = x[i]

            if curRange is not None and not marked[i]:
                ranges.append((curRange, x[i-1]))
                curRange = None

        if curRange is not None and marked[-1]:
            ranges.append((curRange, x[-1]))

        level_ranges.append(ranges)

    if len(level_ranges) == 0:
        level_ranges = level_ranges[0]

    return mode, level_ranges



########################

#pass meangrid, scattergrid, and prob here
def getdist_2d_hist(X, Y, probs, level = 0.68):


    probs = (probs.astype(np.float64) / np.sum(probs)).flatten()

    mode = (X.flatten()[probs == np.max(probs)], Y.flatten()[probs == np.max(probs)])

    marked = np.zeros_like(probs)

    sort_order = np.argsort(probs)[::-1]

    cumprob = np.cumsum(probs[sort_order])

    stop_index = np.arange(len(sort_order))[cumprob <= level][-1] + 2
    for index in sort_order[:stop_index]:
        marked[index] = 1.

    marked = np.reshape(marked, X.shape)


    return mode, marked

    



    
    

    

#########################


def test_1d_dist():

    x = np.arange(100).astype(np.float64)
    probs = (32./68.)*np.ones_like(x)

    probs[10:27] = 2.
    probs[23] += 0.01
    probs[24] -= 0.01
    probs[83:] = 2.
    


    mode, ranges = getdist_1d_hist(x, probs)

    print mode
    print ranges

    assert(mode == 23)
    assert(len(ranges) == 2)
    assert(ranges[0][0] == 10)
    assert(ranges[0][1] == 26)
    assert(ranges[1][0] == 83)
    assert(ranges[1][1] == 99)




################################


def test_isg1():

    true_ratio = 3.4
    intrinsic_scatter = 0.9
    ratio_samples = np.exp(np.log(true_ratio) + intrinsic_scatter*np.random.standard_normal(size=10000))

    y = {}
    x = {}
    for i in range(10000):
        x[i] = np.ones(1)
        y[i] = np.ones(1)*ratio_samples[i]

    grid, means, scatters = intrinsicScatter(x, y, means = np.arange(3.3, 3.5, 0.002), scatters = np.arange(0.88, 0.921, 0.005))

    return ratio_samples, grid, means, scatters
