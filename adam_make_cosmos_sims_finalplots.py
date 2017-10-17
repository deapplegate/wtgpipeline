#! /usr/bin/env python

## you may have to raise the limit on the number of allowed connections like this:
## By default resource.RLIMIT_NOFILE is set to 1024 (at least on the slac machines).
## It wouldn't let me set it to 65536, so there are limits, but you can raise it to 8196
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (8196, 8196))

import process_cosmos_sims as pcs
results = pcs.consolidate(pcs.processPklDir("/u/ki/dapple/nfs22/cosmossims2017/UGRIZ/nocontam/maxlike", "out2"))
import process_cosmos_sims_plots as pcsp
#pcsp.publicationBias(results,None)
#pcsp.plotZCompact(results)

import pylab
bias_plt=pcsp.publicationBias(results,None)
pylab.savefig('plt_publicationBias')
zcompact_plt=pcsp.plotZCompact(results)
pylab.savefig('plt_plotZCompact')
pylab.show()
