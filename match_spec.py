class file_iter:
    def __init__(self,name):
        self.name = name
        self.suffix = 1
        self.file = self.name + str(self.suffix) 
    def next(self):
        self.suffix += 1    
        self.file = self.name + str(self.suffix) 
        return self.file
    def __iter__(self):
        self.file = self.name + str(self.suffix) 










from utilities import *

matchedcat = 'test.fits'

speccat = '/nfs/slac/g/ki/ki05/anja/SUBARU/A68/PHOTOMETRY_W-C-RC_aper/pat3_A68_ned.dat.tab'
inputcat = '/nfs/slac/g/ki/ki05/anja/SUBARU/A68/PHOTOMETRY_W-C-RC_aper/A68.APER1.1.CWWSB_capak.list.all.bpz.tab'

print speccat
specfile = file_iter(speccat+'spec')                                                                                       
from glob import glob
if not glob(speccat): 
    print 'NO SPECTRA FILE'
    raise Exception

os.system('rm ' + specfile.file[:-1] + '*')
os.system('cp '+ speccat +' '+specfile.file)

run("ldacrentab -i " + specfile.file + " -t OBJECTS STDTAB FIELDS NULL -o " + specfile.next(),[specfile.file])
run("ldacrenkey -i " + specfile.file  + " -t STDTAB -k Ra ALPHA_J2000 Dec DELTA_J2000 Z z -o " + specfile.next(),[specfile.file])
run("ldaccalc -i " + specfile.file + " -t STDTAB -c '(Nr);'  -k LONG -n SeqNr '' -o " + specfile.next(),[specfile.file] )
                                                                                                                           
print specfile.file
                                                                                                                           
#    inputtable = ldac.openObjectFile(inputcat)
                                                                                                                           
run("ldacrentab -i " + inputcat + " -t OBJECTS STDTAB  -o " + inputcat+str(1),\
    [inputcat+str(1)])

raw_input()

if os.environ['USER'] == 'dapple':            
    os.chdir('/a/wain001/g.ki.ki02/dapple/pipeline/wtgpipeline/')
    print os.environ['USER'], os.system('pwd')
    command = "./match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + inputcat+str(1)  + " data "                                                                                                                       
else: 
    os.chdir('/u/ki/pkelly/pipeline/wtgpipeline/')
    print os.environ['USER'], os.system('pwd')
    command = "/u/ki/pkelly/pipeline/wtgpipeline//match_neighbor.sh " + matchedcat + " STDTAB " + specfile.file + " spec " + inputcat+str(1)  + " data "                                                                                                                       
print command
os.system('pwd')
run(command, [matchedcat])
print matchedcat, specfile.file            
import astropy, astropy.io.fits as pyfits
spectable = pyfits.open(matchedcat)['STDTAB']
print "looking at "+varname+'-'+filterlist[0]+'_data'
print spectable
print matchedcat
