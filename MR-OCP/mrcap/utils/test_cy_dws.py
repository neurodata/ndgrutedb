import downsample_atlas, downsample
import import mrcap.utils.downsample_atlas, mrcap.utils.downsample
import sys
from mrcap.utils.igraph_io import read_arbitrary

if (len(sys.argv) < 2):
  sys.stderr.write("ERROR: usage => python test_cy_dws big_graph_file")
  
print "Running vanilla python create atlas...."
%timeit atl = mrcap.utils.downsample_atlas.create()

print "Running accelerated cython crate atlas...."
%timeit atl2 = downsample_atlas.create()

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
