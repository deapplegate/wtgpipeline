file = open('bscript2','w')
import os
os.chdir(os.environ['sne'] + '/work/')
import time
trial = True 
#if trial: queue = 'short'
#else: queue = 'long'
for num in range(1,30):
    output_me = os.environ['sne'] + '/batch/ob' + str(num)
    output = os.environ['sne'] + '/batch/o' + str(num)
    error = os.environ['sne'] + '/batch/e' + str(num)
    os.system('rm ' + output_me )
    os.system('rm ' + output )
    os.system('rm ' + error )
    #command = 'bsub -R "scratch > 8 && rhel50" -q   long -o ' + output + ' -e ' + error + '  /afs/slac/g/ki/software/python/bin/python ' + os.environ['bonn'] + '/batch_sub.py ' + output_me + ''

    command = 'bsub -R "rhel50" -q   xlong -o ' + output + ' -e ' + error + '  /afs/slac/g/ki/software/python/bin/python ' + os.environ['bonn'] + '/batch_sub.py ' + output_me + ''
	#command = 'bsub -R "!bali && linux64 && rhel40" -q xlong -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} ${ending} ${modes}
    print command
    os.system(command)
    time.sleep(1)

    #file.write('bsub -R rhel40 -q medium -e ' + os.environ['sne'] + '/batch/e' + str(num) + ' -o ' + os.environ['sne'] + '/batch/o' + str(num) + ' python batch_sub.py\n')
    #file.write('bsub -R rhel40 -q long -e ' + os.environ['sne'] + '/batch/e' + str(num) + ' -o /dev/null python batch_sub.py\n')
file.close()
