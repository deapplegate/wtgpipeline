
import os, sys, commands, re
from glob import glob

def compare(x, y):
	if x['OBJECT'] > y['OBJECT']:
		return 1	
	
	elif x['OBJECT'] == y['OBJECT']:
		return 0
	else:
		return -1

def find_files(path,zero='no'):
	from glob import glob
	if zero == 'no': 
		gl = glob(path + '*fits')
	else:
		gl = glob(path + '*0.fits')
	ll = []
	for im in gl:
		splted = re.split('\/',im)[-1]     	
		if zero == 'no': 
	        	SUPA = re.split('\.fits',splted)[0]
			output = commands.getoutput('dfits -x 1 ' + im + ' | fitsort DATE-OBS OBJECT')
		else:
	        	SUPA = re.split('0\.fits',splted)[0]
			output = commands.getoutput('dfits ' + im + ' | fitsort DATE-OBS OBJECT')
        	outputre = re.split('\s+',re.split('\n',output)[1])
                if outputre[0] == '': outputre = outputre[1:]
                DATE_OBS = outputre[1].replace(' ','')
                OBJECT= outputre[2].replace(' ','')

		ll.append({'file':SUPA,'fullfile':im,'zero':zero,'DATE-OBS':DATE_OBS,'OBJECT':OBJECT} )
	return ll

def collect_files(run):
	datadir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
        path = datadir + run + '/SCIENCE/ORIGINALS/'
        pathdownload = path + 'SMOKA/'

        pathaux = datadir + '/auxiliary/' + run  + '/'
        pathnobackup = datadir + 'nobackup/' + run  + '/SCIENCE/ORIGINALS/'
        pathnobackupstan = datadir + 'nobackup/' + run  + '/STANDARD/ORIGINALS/'
       
	kill_delete = 0 
        if not (glob(pathnobackup) or glob(pathnobackupstan)):
        	print 'no backup!'
		kill_delete = 1
        	raw_input()
        
        os.system('mkdir ' + pathdownload)
        
        glorig = find_files(path,'no')
        glaux = find_files(pathaux,'yes') 
	print pathnobackup
        glnobackup = find_files(pathnobackup,'no') 
	print glnobackup
        
        gl = glorig + glaux
        gluniq = []	
        
        #make unique list
        for item in gl:
        	yes = 1
        	for itemin in gluniq:
        		if item['file'] == itemin['file']:
        			yes = 0	
        	if yes: gluniq.append(item)
        
        print 'gl', len(gl), 'gluniq', len(gluniq), 'glorig', len(glorig), 'glaux', len(glaux)

	return (gluniq, glnobackup, kill_delete)

def retrieve_images(gluniq,run):
	datadir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
        path = datadir + run + '/SCIENCE/ORIGINALS/'
        pathdownload = path + 'SMOKA/'

	for im in gluniq:
        	command = 'wget "http://smoka.nao.ac.jp/qlis/ImagePNG?frameid=' + im['file'] + '0&dateobs=' + im['DATE-OBS'] + '&grayscale=log&mosaic=true" -O ' + pathdownload + im['file'] + '.png'
        	#command = 'wget "http://smoka.nao.ac.jp/qlis/ImagePNG?frameid=' + im + '0&grayscale=log" -O ' + pathdownload + im + '.png'
        	print command
        	os.system(command)
        	command = 'convert ' + pathdownload + im['file'] + '.png ' + pathdownload + im['file'] + '.fits'
        	print command
        	os.system(command)
        	os.system('rm ' + pathdownload + im['file'] + '.png')
       
if __name__ ==  '__main__':
        run = sys.argv[1]
	gluniq,glnobackup,kill_delete = collect_files(run)
	retrieve_images(gluniq,run)
	
