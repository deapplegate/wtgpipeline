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
from adam_cosmos_options import zchoice_switch, cat_switch, dirtag

## gather the results
#RH: jest tust second plots; results = pcs.consolidate(pcs.processPklDir(filtersetdir+"/*/nocontam/maxlike", "out2"))

## now do the plotting
#RH: just test second plots; bias_plt=pcsp.publicationBias(results,None)
#RH: test just second plots; pylab.savefig('plt_publicationBias-%s-%s' % ( dirtag , filterset ) )
## these plots only make sense if you're using idealized fake-sim-clusters well spaced out in z and M
#adam-old# zcompact_plt=pcsp.plotZCompact(results)
#adam-old# pylab.savefig('plt_plotZCompact-%s-%s' % ( dirtag , filterset ) )

#note that scatter_sims_plots.PointEstPzScript is the plot in Weighing the Giants - III figure 8
#import scatter_sims_plots
#pointest=scatter_sims_plots.PointEstPzScript()


#adam-SHNT# GOTTA GET PointEstPzScript working!
# I tried to get this to work by using copying it over to pcsp and hacking away at it, but no luck so far.
# you could start fixing it by working on either pcsp.PointEstPzScript or the original scatter_sims_plots.PointEstPzScript
pointest=pcsp.PointEstPzScript(filtersetdir)
pointest.savefig('plt_pointEstPzScript-%s-%s' % ( dirtag , filterset ) )
pylab.show()
