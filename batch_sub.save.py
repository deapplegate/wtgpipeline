import os, sys, random, time
trial = False 
#outputfile = sys.argv[1]
os.system('which python2.5')
import MySQLdb
import commands
tmpdir = commands.getoutput('mktemp -d /scratch/' + os.environ['LSB_JOBID']) + '/'

stdout = sys.argv[1]
#stderr = sys.argv[2]
#save_stdout = sys.stdout 
#f_stdout = open(tmpdir + 'stdout',"w")
#sys.stdout = f_stdout
#save_stderr = sys.stderr
#f_stderr = open(tmpdir + 'stderr',"w")
#sys.stderr = f_stderr

print 'hi!!!!'

randwait = int(random.random()*0)
print 'rand wait', randwait
time.sleep(randwait)
os.environ['OUTPUTFILE'] = tmpdir + '/lsfout'
os.system('mkdir ' + tmpdir + '/data/')
os.system('cp -rp /nfs/slac/g/ki/ki04/pkelly/astrometry/ ' + tmpdir + '/astrometry/')
os.system('ls -lt ' + tmpdir)
astrom = tmpdir + '/astrometry/bin/solve-field'
#astrom_tmp = tmpdir + '/tmp/'
os.system(astrom)
os.system('du -H ' + tmpdir + '/astrometry/data/')
os.system('du -H ' + tmpdir + '/astrometry/data/*')

#import calc_tmpsave
#calc_tmpsave.astrom = astrom
#calc_tmpsave.select_analyze()
if 1:
    if 0: #not trial:
        import commands
        op = commands.getoutput('/afs/slac/g/ki/software/python/bin/python ' + os.environ['bonn'] + '/calc_resam.py ' + tmpdir + ' ' + astrom) 
        f = open(stdout,'w')
        f.write(op)
        f.close()
    else: 
        os.system('/afs/slac/g/ki/software/python/bin/python ' + os.environ['bonn'] + '/calc_resam.py ' + tmpdir + ' ' + astrom) 


''' redirect stdout to usual, close log files '''
#sys.stdout=save_stdout
#sys.stderr=save_stderr
#f_stdout.close()
#f_stderr.close()

''' copy output file to the output file from the command line -o '''
#os.system('cp -p ' + tmpdir + 'stdout ' + stdout)
#os.system('cp -p ' + tmpdir + 'stderr ' + stderr)

''' remove original '''
os.system('rm -R ' + tmpdir)
#os.system('rm -R /tmp/*')
