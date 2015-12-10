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

# downsample.pyx
# Created by Disa Mhembere on 2015-11-20.
# Email: disa@jhu.edu

import argparse
from glob import glob
from collections import defaultdict
import os, sys
from time import time
import zipfile

import numpy as np
import igraph
import nibabel as nib

from zindex import MortonXYZ
import downsample_atlas
#cimport numpy as np # TODO
from cpython.string cimport PyString_AsString

from libc.stdlib cimport malloc, free
from libcpp.string cimport string
from libcpp.vector cimport vector

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
  start = time()
  edge_dict = defaultdict(int) # key=(v1, v2), value=weight # TODO: c++: map Or vector of tuples

  if factor >= 0:
    print "Generating downsampled atlas ..."
    # TODO: Accelerate this call my makeing create a c function
    ds_atlas = downsample_atlas.create(start=factor) # Create ds atlas and an atlas map for the original atlas
  
  print "Getting atlas data ..."
  ds_atlas = ds_atlas.get_data() # don't care about other atlas data

  print "Malloc-ing spatial map ..."
  cdef vector[string] spatial_map;
  spatial_map.resize(long(ds_atlas.max())+1)

  if not spatial_map.size() == long(ds_atlas.max())+1:
    raise MemoryError()

  cdef long src_spatial_id, tgt_spatial_id
  cdef long src_x, src_y, src_z, tgt_x, tgt_y, tgt_z
  cdef long src, tgt

  # This takes O(m)
  print "Getting edge and vertex data ..."
  edges = g.es # TODO: Could type these but requires materialization :/
  vertices = g.vs # TODO: This too

  print "Iterating through edges ..."
  for idx in xrange(len(edges)): # TODO: check xrange vs range
    src_spatial_id = long(vertices[long(edges[idx].source)]["spatial_id"])
    tgt_spatial_id = long(vertices[long(edges[idx].target)]["spatial_id"])

    src_x, src_y, src_z = MortonXYZ(src_spatial_id)
    tgt_x, tgt_y, tgt_z = MortonXYZ(tgt_spatial_id)

    src = int(ds_atlas[src_x, src_y, src_z])
    tgt = int(ds_atlas[tgt_x, tgt_y, tgt_z])

    # FIXME GK: We will skip all region zeros for all atlases which is not really true!
    if ignore_zero:
      if (src and tgt) and (src != tgt):
        if not len(spatial_map[src]):
          spatial_map[src] = `src_spatial_id`

        if not len(spatial_map[tgt]):
          spatial_map[tgt] = `tgt_spatial_id`

        edge_dict[(src, tgt)] += edges[idx]["weight"]
    else:
      print "Never should get here"
      if not len(spatial_map[src]): spatial_map[src] = `src_spatial_id`
      if not len(spatial_map[tgt]): spatial_map[tgt] = `tgt_spatial_id`

      edge_dict[(src, tgt)] += edges[idx]["weight"]

  del g # free me

  print "Build edge list .."
  # TODO: Make this conversion faster or use a better container
  py_spatial_map = list(spatial_map)
  print "Pre-graph build in %.3f sec ... " % (time() - start)

  new_graph = igraph.Graph(n=spatial_map.size(), directed=False) # len spatial_map is the # of vertices
  new_graph.vs["spatial_id"] = spatial_map
  
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
