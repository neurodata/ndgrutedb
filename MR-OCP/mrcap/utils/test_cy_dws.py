import downsample_atlas, downsample
import mrcap.utils.downsample_atlas, mrcap.utils.downsample
import sys
from mrcap.utils.igraph_io import read_arbitrary
from time import time
import numpy as np

if (len(sys.argv) < 2):
  sys.stderr.write("ERROR: usage => python test_cy_dws big_graph_file\n")
  exit(1)
  
print "Running vanilla python create atlas...."
start = time()
atl = mrcap.utils.downsample_atlas.create()
print "Time to create vanilla atlas: {} sec ...".format(time() - start)

print "Running accelerated cython crate atlas...."
start = time()
atl2 = downsample_atlas.create()
print "Time to create accelerated atlas: {} sec ...".format(time() - start)

print "Testing equality"
assert np.equal(atl.get_data(), atl2.get_data()), "Atlases, Cython and python not equal!"

del atl, atl2
# Run actual downsample
gfile = sys.argv[1]
g = read_arbitrary(gfile)

print "Running vanilla python downsample ...."
dsg = mrcap.utils.downsample.downsample(g, 2)

print "Running accelerated cython downsample ...."
dsg2 = downsample(g, 2)

assert dsg.isomorphic(dsg2), "Graphs, cython and python not equal!"
