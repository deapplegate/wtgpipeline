import kdtree

sarray = kdtree.tree(0,100000)
#print sarray

class Node:pass

vec = [] 


def kdtree_func(pointList, depth=0, volume=10):

    lim = 500
 
    k = len(pointList[0]) # assumes all points have the same dimension

    # Select axis based on depth so that axis cycles through all valid values
    axis = depth % k
 
    # Sort point list and choose median as pivot element
    pointList.sort(key=lambda point: point[axis])
    median = len(pointList)/2 # choose median
 
    # Create node and construct subtrees
    node = Node()
    from copy import copy
    node.axis = copy(axis)
    node.location = pointList[median]
    left = [x for x in pointList if x[node.axis] < node.location[node.axis]]
    right = [x for x in pointList if x[node.axis] >= node.location[node.axis]]
    if len(left) < lim  or len(right) < lim: 
        vec.append(len(pointList)) 
        return
    node.left = kdtree_func(left, depth+1)
    node.right = kdtree_func(right, depth+1)
    return node

pointList = sarray #[(1,1.1),(2.1,2),(2,3),(30,20)] 


print len(pointList[0]) 


tree = kdtree_func(pointList)

print vec[0:10]

vec_test = []


def traverse_kdtree(node, pointList, combined_lim_mag=[1000,1000,1000,1000,1000,1000,1000]):
    if node is not None: #.__dict__.has_key('left'):
        #print node.location, node.axis            
        try:
            pointListLeft = [x for x in pointList if (x[node.axis] < combined_lim_mag[node.axis]) and (x[node.axis] < node.location[node.axis] + zps[node.axis])]
        except: 
            print len(pointList), node.location, zps, node.axis
            raise Exception
        #print pointListLeft, pointList, node.location
        #print len(pointListLeft), len(pointList)
        pointListRight = [x for x in pointList if (x[node.axis] < combined_lim_mag[node.axis]) and (x[node.axis] >= node.location[node.axis] + zps[node.axis])]
        traverse_kdtree(node.left,pointListLeft)
        traverse_kdtree(node.right,pointListRight)
    else:
        vec_test.append(len(pointList))
        return 

sarray2 = kdtree.tree(200000,300000)

vec_test = []        
zps = [0.,0.,0.,0.,0.,0.,0.]
traverse_kdtree(tree,sarray2)
from copy import copy
vec1 = copy([float(x) for x in vec_test])
print vec_test


vec_test = []        
#zps = [0.02,0.02,0.02,0.02,0.02,0.02,0.02]
traverse_kdtree(tree,pointList)
print vec_test
vec2 = copy([float(x) for x in vec_test])

import pylab, scipy
a = sorted(scipy.array(vec1)/scipy.array(vec2))
print scipy.std(a[3:-3])

raw_input()


a,b,varp = pylab.hist(scipy.array(vec1)/scipy.array(vec2),bins=scipy.arange(0.8,1.2,0.02))
pylab.xlabel('Ratio')
pylab.ylabel('Number of Galaxies')
pylab.show()




