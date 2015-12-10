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
#

# downsample_atlas.pyx
# Created by Disa Mhembere on 2015-11-10.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# This simply takes a (182, 218, 182) atlas and creates
# a ~30-non-zero k region atlas by relabelling each
#   3x3x3 region with a new label then masking
# using a base atlas

import os, sys
from math import ceil
from time import time

import nibabel as nib
import numpy as np # TODO: cimport

from packages.utils.setup import get_files

# cpdef cy_create(char* roifn=os.path.join(os.environ["M2G_HOME"],"data","Atlas", 
# TODO: cdef
def create(roifn=os.path.join(os.environ["M2G_HOME"],"data","Atlas",
  "MNI152_T1_1mm_brain.nii"), int start=2):

  """
  cimport numpy as np
  DTYPE = np.int
  """
  start_time = time()

  print "Loading rois as base ..."
  if not os.path.exists(roifn):
    get_files()

  img = nib.load(roifn)
  base = img.get_data() # TODO: cdef np.ndarray base = img.get_data()
  # cdef int* true_dim; true_dim[0] = base.shape[0]; true_dim[1] = base.shape[1]; true_dim[2] = base.shape[2]
  true_dim = base.shape

  # Labelling new 
  cdef bint label_used = False
  cdef int region_num = 1

  cdef int step = 1 + (start * 2)
  cdef int mstart = (-start)
  cdef int mend = start + 1
  cdef int xdim, ydim, zdim

  # Align new to scale factor
  """
  cdef np.ndarray tmp = np.zeros([xmax, ymax], dtype=DTYPE)
  cdef np.ndarray resized_base = np.zeros((xdim*step, ydim*step, zdim*step), dtype=int)
  """
  xdim, ydim, zdim = map(ceil, np.array(base.shape)/float(step))
  if step == 1:
    assert xdim == base.shape[0] and ydim == base.shape[1] and zdim == base.shape[2]
  resized_base = np.zeros((xdim*step, ydim*step, zdim*step), dtype=int)
  resized_base[:base.shape[0], :base.shape[1], :base.shape[2]] = base

  base = resized_base
  del resized_base

  print "Labeling new ..."
  # Create new matrix
  new = np.zeros_like(base, dtype=np.int) # poke my finger in the eye of bjarne

  for z in xrange(start, base.shape[2]-start, step):
    for y in xrange(start, base.shape[1]-start, step):
      for x in xrange(start, base.shape[0]-start, step):

        if label_used: 
          region_num += 1 # only increase counter when a label was used
          label_used = False

        # set other (step*step)-1 around me to same region
        for zz in xrange(mstart,mend):
          for yy in xrange(mstart,mend):
            for xx in xrange(mstart,mend):
              if (base[x+xx,y+yy,z+zz]): # Masking # TODO: could be base[x+xx][]
                label_used = True
                new[x+xx,y+yy,z+zz] = region_num
  
  new = new[:true_dim[0], :true_dim[1], :true_dim[2]] # shrink new to correct size
  print "Your atlas has %d regions ..." % len(np.unique(new))

  img = nib.Nifti1Image(new, affine=img.get_affine(), header=img.get_header(), file_map=img.file_map)
  
  del new
  print "Building atlas took %.3f sec ..." % (time()-start_time)

  return img
