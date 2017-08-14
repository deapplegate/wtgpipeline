import sys
directory = sys.argv[1]
filename = sys.argv[2]
download_dir = sys.argv[3]
host = sys.argv[4]
from ftplib import FTP
import string, re
def handleDownload(block):
	file.write(block)
	print ".",
ftp = FTP('smokaftp.nao.ac.jp')
print ftp.login('smokaftp','02YoS04')
ftp.cwd(directory)
file = open(download_dir + "/" + directory + "/tmp" + host + filename, 'wb')
ftp.retrbinary('RETR ' + filename, handleDownload)
file.close()
ftp.close()
sys.exit(0)

