#! /usr/bin/env python
#adam-example# ./adam_make_cosmos_sims_finalplots.py ${datadir} ${filterset}
## you may have to raise the limit on the number of allowed connections like this:
## By default resource.RLIMIT_NOFILE is set to 1024 (at least on the slac machines).
## It wouldn't let me set it to 65536, so there are limits, but you can raise it to 8196
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (8196, 8196))

import process_cosmos_sims as pcs
import process_cosmos_sims_plots as pcsp
import pylab, sys
import adam_quicktools_ArgCleaner
argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
datadir = argv[0]
filterset = argv[1]
filtersetdir=datadir+'/'+filterset+'/'
from adam_cosmos_options import zchoice_switch, cat_switch

## gather the results
results = pcs.consolidate(pcs.processPklDir(filtersetdir+"/nocontam/maxlike", "out2"))

## now do the plotting
bias_plt=pcsp.publicationBias(results,None)
pylab.savefig('plt_publicationBias-CAT%s-Z%s-%s' % (cat_switch, zchoice_switch,filterset) )
zcompact_plt=pcsp.plotZCompact(results)
pylab.savefig('plt_plotZCompact-CAT%s-Z%s-%s' % (cat_switch, zchoice_switch,filterset) )
pylab.show()

