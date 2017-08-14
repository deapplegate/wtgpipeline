from ftplib import FTP
import popen2, time, sys
directory = sys.argv[1]
filename = sys.argv[2]
download_dir = sys.argv[3]
host = sys.argv[4]
size_ftp = sys.argv[5]
path_to_cvs = sys.argv[6]

'''this commands needs to be redirected to /dev/null or it won't work, also can't read out from this for debugging b/c process will wait'''
command = "python " + path_to_cvs + "/download_remote.py " + directory + " " + filename + " " + download_dir + " " + host + " >& /dev/null"
print command
e = popen2.Popen4(command,1)

#output = e.fromchild.readlines()	
#errors = e.childerr.read()
#print output
#print errors

downloaded = 'no'

import time
for j in range(600):
	time.sleep(1)
	print e.poll(), e.pid, j
	#break time cycle if completed
	from glob import glob	
	file_there = glob(download_dir + "/" + directory + "/" + filename)
	print file_there
        downloaded = 'not' 	
        downloading = 'not'
	if len(file_there) > 0:
		import os
        	stats = os.stat(download_dir + "/" + directory + "/" + filename)
                last_time = stats[-1]
                size = stats[6]	
                #print int(size_ftp), int(size), filename
        	if int(size_ftp) == int(size):  
			import os
                        import signal
                        os.kill(e.pid,signal.SIGKILL)		
                        os.system("kill -9 " + str(e.pid))
                        downloaded = 'yes'

	if e.poll() != -1:
		import os
		os.system("mv " + download_dir + "/" + directory + "/tmp" + host + filename + " " +  download_dir + "/" + directory + "/" + filename)
		break
        if e.poll() != -1:
                import os
		os.system("rm " + download_dir + directory + "/tmp" + host + filename) 
                break
	#kill if download times out and delete image
	if j == 598: 
		import os
		import signal
		os.kill(e.pid,signal.SIGKILL)		
		os.system("kill -9 " + str(e.pid))
		os.system("rm " + download_dir + directory + "/tmp" + host + filename) 
