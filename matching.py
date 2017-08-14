#################
# utility functions
###############

from math import sqrt
from numpy import *

###############################

class Catalog(object):

    def __init__(self, x, y, id):

        self.nentries = len(x)
        self.pos = vstack([x,y]).transpose()
        self.id = id

    def filter(self, filt):

        return Catalog(self.pos[:,0][filt], self.pos[:,1][filt], self.id[filt])

    def __len__(self):
        return self.nentries

#########################

class MagCatalog(Catalog):

    def __init__(self, x, y, id, mag):
        Catalog.__init__(self, x, y, id)
        self.mag = mag

    def filter(self, filt):

        cat = Catalog.filter(self, filt)

        return MagCatalog(cat.pos[:,0], cat.pos[:,1], cat.id, self.mag[filt])


#########################

EuclideanDist = lambda p1, p2: sqrt(((p1 - p2)**2).sum(axis=1))

##########################

def SphereDist(p1, p2):
    '''assumes already in radians, first coord is RA, second is dec'''
    dTheta = p1 - p2
    dLat = dTheta[:,1] #dec
    dLong = dTheta[:,0] #ra

    dist = 2*arcsin(sqrt(sin(dLat/2)**2 + cos(p1[:,1])*cos(p2[1])*sin(dLong/2)**2))

    return dist
    
##########################

SPLIT=1000

def buildTrie(cat):
    if len(cat) > SPLIT:
        return Node(cat)
    else:
        return Leaf(cat)

########################

class Trie(object):

    def __init__(self, cat):
        self.range = ((min(cat.pos[:,0]), max(cat.pos[:,0])),
            (min(cat.pos[:,1]), max(cat.pos[:,1])))

    def findNeighbors(self, coord, within, 
                      distFunc = EuclideanDist):
        
        for pos, dim in zip(coord, self.range):
            if (pos + within) < dim[0] or \
                    (pos - within) > dim[1]:
                return []
            return self._findNeighbors(coord, within, 
                                       distFunc)
        
##########################



class Leaf(Trie):

    def __init__(self, cat):
        Trie.__init__(self, cat)
        self.cat = cat

    def _findNeighbors(self, coord, within, 
                       distFunc = EuclideanDist):

        dist = distFunc(self.cat.pos, coord)

        return self.cat.id[dist < within].tolist()


############################
        

class Node(Trie):

    def __init__(self,cat):

        Trie.__init__(self, cat)
        self.left = None
        self.right = None

        if (self.range[0][1] - self.range[0][0]) > \
                (self.range[1][1] - self.range[1][0]):
            splitaxis = cat.pos[:,0]
        else:
            splitaxis = cat.pos[:,1]

        split = median(splitaxis)

        self.left = buildTrie(cat.filter(splitaxis <= split))
        self.right = buildTrie(cat.filter(splitaxis > split))


    def _findNeighbors(self, coord, within, 
                       distFunc = EuclideanDist):

        neighbors = self.left.findNeighbors(coord, within, distFunc)
        neighbors.extend(self.right.findNeighbors(coord, within, distFunc))
        
        return neighbors
        
################################



def matchCatalogs(cat1,cat2,tolerance, distFunc = EuclideanDist):
    #lists of entry objects

    cat1Index = {}
    cat2Index = {}

    trie = buildTrie(cat2)
    
    for i in xrange(len(cat2)):
        cat2Index[cat2.id[i]] = []
    
    total = len(cat1)
    for i in xrange(total):
        if (i % 500 == 0):
            print '%d of %d complete' % (i, total)
        curId = cat1.id[i]
        neighbors = trie.findNeighbors(cat1.pos[i], tolerance, distFunc)
#        print len(neighbors)
        cat1Index[curId] = neighbors
        for id in neighbors:
            cat2Index[id].append(curId)

    return (cat1Index, cat2Index)
        




#################################

