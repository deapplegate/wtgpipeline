#########################
# Utilities to deal with BPZ pdz file ops
#########################

import sys, re, cPickle
import numpy as np, astropy, astropy.io.fits as pyfits
import ldac


##########################

__cvs_id__ = "$Id$"

##########################


class PDZManager(object):

    def __init__(self, pdzcat):

        self.pdzcat = pdzcat
        self.pdzrange = None
        self.index = None

        self._buildPDZRange()
        self._buildIndex()

    #################


    def __getitem__(self, key):
        #key is the object ID
        #returns pdz array
        #index maps ID to element number

        if self.index is None or key not in self.index:
            raise IndexError

        return self.pdzcat[self.index[key]][1]
    
    ####################

    def _buildIndex(self):

        self.index = {}
        for i, id in enumerate(self.pdzcat['SeqNr']):
            self.index[id] = i

    #####################

    def _buildPDZRange(self):
        
        self.pdzrange = np.arange(self.pdzcat.hdu.header['MINPDZ'], 
                                  self.pdzcat.hdu.header['MAXPDZ'], 
                                  self.pdzcat.hdu.header['PDZSTEP'])

    ######################

    def save(self, outfile):

        self.pdzcat.saveas(outfile, overwrite=True)


    ######################


    def associatePDZ(self, z_ids):

        arrangedPDZ = []
        for id in z_ids:
            arrangedPDZ.append(self[id])

        finalPDZs = np.column_stack(arrangedPDZ).transpose()

        return self.pdzrange, finalPDZs


    ######################


    @classmethod
    def parsePDZ(cls, pdzfile):
        '''parses text output from BPZ'''


        input = open(pdzfile)

        headerline = input.readline()
        match = re.search('z=arange\((.+)\)', headerline)
        assert(match is not None)
        minPDZ, maxPDZ, pdzstep = map(float, match.group(1).split(','))

        ids = []
        pdzs = []
        for line in input.readlines():
            if re.match('^#', line):
                continue
            tokens = line.split()
            id = int(tokens[0])
            pdz = map(float, tokens[1:])

            ids.append(id)
            pdzs.append(pdz)

        nobjects = len(pdzs)
        npdzs = len(np.arange(minPDZ, maxPDZ, pdzstep))

        cols = [pyfits.Column(name = 'SeqNr', format = 'J', array = np.array(ids)),
                pyfits.Column(name = 'pdz', format = '%dE' % npdzs, array = np.array(pdzs))]

        pdzs = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        pdzs.hdu.header['MINPDZ']= minPDZ
        pdzs.hdu.header['MAXPDZ']= maxPDZ
        pdzs.hdu.header['PDZSTEP']= pdzstep

        
        return cls(pdzs)


    ##########################
    
    @classmethod
    def open(cls, pdzfile):
        '''opens a pdzfile saved by PDZManager'''

        pdz = ldac.openObjectFile(pdzfile)

        return cls(pdz)


############################################

class ZebraManager(PDZManager):

    @classmethod
    def parsePDZ(cls, pdzfile, sourcefile):
        '''parses text output from ZEBRA'''

        input = open(pdzfile)

        source = ldac.openObjectFile(sourcefile)

        minPDZ, maxPDZ, pdzstep = 0.0, 4.005, 0.005

        pdzs = []
        for line in input.readlines():
            if re.match('^#', line):
                continue
            tokens = line.split()
            pdz = map(float, tokens)

            pdzs.append(pdz)

        nobjects = len(pdzs)
        npdzs = len(np.arange(minPDZ, maxPDZ, pdzstep))

        ids = source['SeqNr']

        cols = [pyfits.Column(name = 'SeqNr', format = 'J', array = ids),
                pyfits.Column(name = 'pdz', format = '%dE' % npdzs, array = np.array(pdzs))]

        pdzs = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        pdzs.hdu.header['MINPDZ']= minPDZ
        pdzs.hdu.header['MAXPDZ']= maxPDZ
        pdzs.hdu.header['PDZSTEP']= pdzstep

        
        return cls(pdzs)


        
    

############################################


def parseRawPDZ(infile, outfile, filetype = 'bpz', sourcefile = None):

    if filetype == 'zebra':
        pdzmanager = ZebraManager.parsePDZ(infile, sourcefile)
        
    else:
        pdzmanager = PDZManager.parsePDZ(infile)

    pdzmanager.save(outfile)


##############################################

if __name__ == '__main__':

    infile = sys.argv[1]
    outfile = sys.argv[2]

    photoztype = 'bpz'
    if len(sys.argv) > 3:
        photoztype = sys.argv[3]
        
    sourcefile = None
    if photoztype == 'zebra':
        sourcefile = sys.argv[4]

    parseRawPDZ(infile, outfile, photoztype, sourcefile)
