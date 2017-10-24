import threading

class MyThread ( threading.Thread ):
	def __init__ ( self, host, directory, download_dir, path_to_cvs , c):
		self.host = host 
		self.directory = directory
		self.download_dir = download_dir
		self.path_to_cvs = path_to_cvs
		self.c =c 
		threading.Thread.__init__(self)	

	def run ( self ):
		run_download(self.host,self.directory,self.download_dir, self.path_to_cvs, self.c)
	        return 
        	

''' record the list of files in the remote directory ''' 
def run_download(host,directory, download_dir, path_to_cvs, c):
	directory = directory.replace(' ','') # replace spaces in directory name
	file_download = 'default' # make sure script find new file to download
	failed = 0 # number of times thread has filed in a row
	timeout_update = 20. # number of seconds since file has been updated
	timeout_start = 120. # number of seconds since new download process has started
	import os
	import MySQLdb

	from ftplib import FTP                                               
        import string, re
     
	print 'trying ' + host 
	''' make sure there's a new file to download and the thread hasn't failed four times ''' 
	while (failed < 20 and file_download is not None): 
       		ftp = FTP('smokaftp.nao.ac.jp')                                                                                                                                                          
                ftp.login('smokaftp','02YoS04')
		
                ftp.cwd(directory)
                dirfiles = []
                ftp.retrlines('LIST',dirfiles.append)
	        ftp.close()
                                                                                                                                                                                                         
	        ftp_files = []	
	        for file in dirfiles[1:]:
	        	pp = re.split('\s+',file)
	        	size = pp[4]
	        	name = pp[8]
	        	date = pp[7]
	        	ftp_files.append([name,size,date])

	        	
                list = [[re.split('\s+',x)[-1],0] for x in dirfiles]
                #for list in [list[0:2],list[2:4]]: 
                #	split_download(list)
	        ''' open downloading/downloaded files to see which are finished/dead/alive '''
	        from glob import glob	
	        import os, time
	        #filelist = glob(download_dir + "/" + directory)
	        #for file in filelist:
	        	#stats = os.stat(download_dir + "/" + directory + "/" + file)		
	        	#last_time = stats[-1]
	        	#size = stats[6]	
	        	#downloaded_files.append([file,size,last_time])
	        	#''' figure out the last time the file was modified '''	
                                                                                                                                                                                                         
	        file_download = None
	        for file in ftp_files:
			file_found = None
	        	file_there = glob(download_dir + "/" + directory + "/" + file[0])
	        	downloaded = 'not' 	
	        	downloading = 'not'
			size_ftp = file[1]
			if len(file_there) > 0:
	        		stats = os.stat(download_dir + "/" + directory + "/" + file[0])
	        	        last_time = stats[-1]
	        	        size = stats[6]	
	        		if int(size_ftp) == int(size):  
	        			downloaded = 'yes'
	        		#elif time.time() - file_comp[3] < timeout_update: 
	        			#downloading = 'yes'
			''' make sure that another process hasn't just started downloading file '''
			command = "SELECT start_time,number_downloads FROM download_db  WHERE directory = '" + directory + "' AND file = '" + file[0] + "' and download_dir = '" + download_dir + "'"	
			
			c.execute(command)
                        results = c.fetchall()
			#print results
			
                        if len(results) > 0:	
	
				#print results[0][0]
				#print results[0][1]


				number_downloads = results[0][1]
				time_run = results[0][0]
				diff = time.time() - float(time_run)
				#print diff
                        	if diff < timeout_start: # or number_downloads  > 2: 
					downloading = 'yes'
	        			
       	        	if downloaded is 'not' and downloading is 'not': 
	        		file_download = file[0]
	        		break
		print file_download
	        if file_download is not None:	
	        	from popen2 import * 
                        
                        command = "SELECT start_time, number_downloads FROM download_db  WHERE directory = '" + directory + "' AND file = '" + file_download + "' and download_dir = '" + download_dir + "'"
                        c.execute(command)
                        results = c.fetchall()
                        results_length = len(results)
                        
                        if results_length == 0:
                        	c.execute("INSERT INTO download_db (directory, file, download_dir, start_time, number_downloads) VALUES ('" + directory + "','" + file_download + "','" + download_dir + "'," + str(time.time()) + ",1)")	
                        else: 
                        	command = "UPDATE download_db SET start_time=" + str(time.time()) + ", number_downloads = number_downloads + 1 WHERE directory='" + directory + "' AND file='" + file_download	+ "'"
                        	c.execute(command)


			print "about to run: " + str(failed) + " failures so far on this machine"
			command = "ssh " + host + " /usr/local/bin/python " + path_to_cvs + "download_manager.py " + directory + " " + file_download + " " + download_dir + " " + host + " " + str(size_ftp) + " " + path_to_cvs
			print command
                        proc = Popen3(command	,1)
                        #proc = Popen3(	"ls -lt ",1)
                        output = proc.fromchild.readlines()	
                        errors = proc.childerr.read()
			print output
			print errors

                                                                                                                                                                                                         
	        	''' test if the file is downloaded and the right size '''	
	        	location = download_dir + "/" + directory + "/" + file_download
	        	if len(glob(location)) > 0:
	        		stats = os.stat(location)			
	        	        last_time_stat = stats[-1]
	        	        size_stat = stats[6]	
	        		if size_stat != size: 
	        			failed += 1
	        		else: 
	        			failed = 0
	        	else: failed += 1	
	
		
# yakut 01-12
# ki-ls 01-06
# noric 01-16 
# run one file retrieval at a time to avoid conflicts


import MySQLdb, os, sys
if len(sys.argv) < 3 or sys.argv[1] == '-h':
	print "INSTRUCTIONS:\n    python fastftp.py file_with_directories_to_download download_to_this_directory path_to_your_cvs_directory  \n"
	print "EXAMPLE:\n    python fastftp.py directory_file $xoc/TEST/ ~/pipeline/wtgpipeline \n"
	print "     python fastftp.py todownload ~/nfs03/tmpdownload/ ~dapple/nfs/pipeline/wtgpipeline\n"
	print " YOU NEED TO PUT IN A FULL PATH THAT CAN BE ACCESSED ON OTHER MACHINES \n"
	print "EXAMPLE file_with_directories_to_download:\nkhata0801153717\nkhata0801150346\nmihara0801124538\n"
else:
        #c.execute("DROP TABLE IF EXISTS download_db ") 
        #c.execute("CREATE TABLE download_db (directory varchar(200), file varchar(80), download_dir varchar(200), start_time float(30), number_downloads int(11) )" )
        download_dir = sys.argv[2] #'/nfs/slac/g/ki/ki03/xoc/pkelly/TEST/'
	if download_dir[-1] != '/': download_dir = download_dir + '/'
        directory_file = sys.argv[1] #'khata0801130746' 
        path_to_cvs = sys.argv[3] #'/nfs/slac/g/ki/ki03/xoc/pkelly/TEST/'
	if path_to_cvs[-1] != '/': path_to_cvs = path_to_cvs + '/'

	directories = open(directory_file,'r').readlines()
	
	db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
        c = db2.cursor()
	for directory in directories:
		directory = directory[:-1]	
       		command = "UPDATE download_db SET number_downloads=0 WHERE directory='" + directory + "'" 

                c.execute(command)

                os.system("mkdir " + download_dir + directory)
                
                hosts = []
                for host in [['yakut',12],['noric',12],['ki-ls',6]]:
                	for num in xrange(host[1]):	
                		snum = '%(blah)02d' % {'blah':num + 1}
                		hosts.append(host[0] + snum)
                	
                print hosts	
                import time
                for host in hosts: 
                	time.sleep(1)
                	MyThread( host,directory,download_dir, path_to_cvs, c ).start()
