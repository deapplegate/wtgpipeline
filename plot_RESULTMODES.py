#! /usr/bin/env python
import numpy
set8=numpy.array([1806.6,1800.84,1797.29,1798.16,1792.06,1793.85,1791.16,1800.4,1808.31,1801.3])
set5=numpy.array([ 1822.4,1801.52,1797.29,1799.47,1795.78,1796.09,1791.93,1800.4,1809.61,1806.68])

f=figure()
xx=arange(10)+1
plot(xx,set8,'bo',label='set8')
plot(xx,set5,'ro',label='set5')
xlabel("CCD chip #")
ylabel("RESULTMODE")
xlim((.5,10.5))
legend()
savefig("plt_RESULTMODE_diffs")
