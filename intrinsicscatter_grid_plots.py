###########################
# Plots that go along with the intrinsic scatter measured distributions
###########################

import numpy as np, pylab
import intrinsicscatter_grid as isg

############################


def plotdist_1d_hist(x, probs, mode = None, ranges = None):

    if mode is None or ranges is None:

        mode, ranges = isg.getdist_1d_hist(x, probs, [0.68, 0.95])

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95-0.12, 0.95 - 0.12])

    ax.plot(x, probs, 'b-')

    print '!!!!!!!!!'
    print ranges

    ax.axvline(mode, c='r', linewidth=1.5)

    s68, s95 = ranges
    if isinstance(s68[0], float):
        s68 = [s68]
    if isinstance(s95[0], float):
        s95 = [s95]
    for range in s68:
        ax.axvline(range[0], c='m', linewidth=1.2, linestyle='--')
        ax.axvline(range[1], c='m', linewidth=1.2, linestyle='--')
    for range in s95:
        ax.axvline(range[0], c='c', linewidth=1.2, linestyle=':')
        ax.axvline(range[1], c='c', linewidth=1.2, linestyle=':')


    return fig
        
        
