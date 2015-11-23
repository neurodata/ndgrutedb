import cy_downsample_atlas, cy_downsample
import import mrcap.utils.downsample_atlas, mrcap.utils.downsample
import sys
from mrcap.utils.igraph_io import read_arbitrary

print "Running vanilla python create atlas...."
%timeit atl = mrcap.utils.downsample_atlas.create()

print "Running accelerated cython crate atlas...."
%timeit atl2 = cy_downsample_atlas.create()

print "Testing equality"
assert np.equal(atl.get_data(), atl2.get_data()), "Atlases, Cython and python not equal!"

del atl, atl2
# Run actual downsample
gfile = sys.argv[1]
g = read_arbitrary(gfile)

print "Running vanilla python downsample ...."
dsg = mrcap.utils.downsample.downsample(g, 2)

print "Running accelerated cython downsample ...."
dsg2 = cy_downsample(g, 2)

assert dsg.isomorphic(dsg2), "Graphs, cython and python not equal!"
