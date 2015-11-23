#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# downsample.py
# Created by Disa Mhembere on 2014-07-08.
# Email: disa@jhu.edu

import argparse
from glob import glob
from collections import defaultdict
import os, sys
import igraph
from mrcap.atlas import Atlas 
from mrcap.utils import igraph_io
from time import time
import cy_downsample_atlas
import nibabel as nib
import zipfile
from zindex import MortonXYZ
import numpy as np
#cimport numpy as np # TODO
import cPickle as pickle

from libc.stdlib cimport malloc, free

DEBUG = False
def downsample(g, factor=-1, ds_atlas=None, bint ignore_zero=True):
  """
	Downsample a graph by a scale factor.

	Downsamples by collapsing regions using an dynamically generated downsampled atlas. Rebuilding the graph takes on the order of a few minutes on a standard desktop computer with more than 4GB of RAM.
	
	**Positional Arguments**

			g: [.graphml; XML file]
					- A full sized big graph.
			factor: [int] (default = 1)
					- The downsampling factor.
			ds_atlas: [.nii; nifti image] (default = MNI152)
					- A prebuilt downsampled nifti atlas with which to downsample.
			ignore_zero: [boolean] (default = True)
					- We assume the zeroth label is outside the brain.
	
	**Returns**
	
			new graph: [.graphml; XML file]
					- The input graph downsampled to the scale of the input atlas.
  """

  #ctypedef unsigned long long
  start = time()
  edge_dict = defaultdict(int) # key=(v1, v2), value=weight # TODO: c++: map Or vector of tuples

  if factor >= 0:
    print "Generating downsampled atlas ..."
    # TODO: Accelerate this call my makeing create a c function
    ds_atlas = cy_downsample_atlas.create(start=factor) # Create ds atlas and an atlas map for the original atlas
  
  ds_atlas = ds_atlas.get_data() # don't care about other atlas data

  #spatial_map = [0]*(int(ds_atlas.max())+1) 
  cdef long *spatial_map = <long *>malloc((long(ds_atlas.max())+1) * sizeof(long)) #TODO: Numpy/vector
  if not spatial_map:
    raise MemoryError()

  cdef long src_spatial_id, tgt_spatial_id
  cdef long src_x, src_y, src_z, tgt_x, tgt_y, tgt_z
  cdef long src, tgt

  # This takes O(m)
  edges = g.es # TODO: Could type these but requires materialization :/
  vertices = g.vs # TODO: This too
  for idx in xrange(len(edges)): # TODO: check xrange vs range
    src_spatial_id = long(vertices[edges[idx].source]["spatial_id"])
    tgt_spatial_id = long(vertices[edges[idx].target]["spatial_id"])

    src_x, src_y, src_z = MortonXYZ(src_spatial_id)
    tgt_x, tgt_y, tgt_z = MortonXYZ(tgt_spatial_id)

    src = ds_atlas[src_x, src_y, src_z]
    tgt = ds_atlas[tgt_x, tgt_y, tgt_z]

    # FIXME GK: We will skip all region zeros for all atlases which is not really true!
    if ignore_zero:
      if (src and tgt) and (src != tgt):
        if not spatial_map[src]: spatial_map[src] = `src_spatial_id` 
        if not spatial_map[tgt]: spatial_map[tgt] = `tgt_spatial_id` 

        edge_dict[(src, tgt)] += edges[idx]["weight"]
    else:
      print "Never should get here"
      if not spatial_map[src]: spatial_map[src] = `src_spatial_id`
      if not spatial_map[tgt]: spatial_map[tgt] = `tgt_spatial_id` 

      edge_dict[(src, tgt)] += edges[idx]["weight"]

  del g # free me

  # TODO: Make this conversion faster or use a better container
  py_spatial_map = []
  for idx in xrange((long(ds_atlas.max())+1)):
    py_spatial_map.append(spatial_map[idx])
  new_graph = igraph.Graph(n=len(py_spatial_map), directed=False) # len spatial_map is the # of vertices
  new_graph.vs["spatial_id"] = py_spatial_map

  free(spatial_map)
  
  print "Adding edges to graph ..."
  new_graph += edge_dict.keys()

  print "Adding edge weight to graph ..."
  new_graph.es["weight"] = edge_dict.values()

  print "Deleting zero-degree nodes..."
  zero_deg_nodes = np.where(np.array(new_graph.degree()) == 0 )[0]
  new_graph.delete_vertices(zero_deg_nodes)

  print "Completed building graph in %.3f sec ... " % (time() - start)
  print new_graph.summary()
  return new_graph
