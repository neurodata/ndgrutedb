
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

#!/usr/bin/env python

# scale_convert.py
# Created by Disa Mhembere on 2015-03-15.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import tempfile
import os

from pipeline.utils.util import get_genus, get_equiv_fn
from mrcap.utils.downsample import downsample
from mrcap.utils import igraph_io

class TempGraph(object):
  """
  Helper class used to organize the result of a downsample operations
  Has 3 attrs an orginal file (calee), a tempfile (result) and a possible
  error message
  """
  def __init__(self, orig_fn, temp_fn="", err_msg=""):
    self.orig_fn = orig_fn
    self.temp_fn = temp_fn
    self.err_msg = err_msg

  def _make_fn(self):
    print "Creating temp file ..."
    tmpfile = tempfile.NamedTemporaryFile("w", delete=False, dir="/data/pytmp")
    print "Temp file %s created ..." % tmpfile.name
    tmpfile.close()

    self.temp_fn = tmpfile.name

  def _add_error(self, msg):
    self.err_msg = msg
  
  def get_error(self):
    return self.err_msg

  def has_error(self):
    return len(self.err_msg) > 0

  def has_temp_fn(self):
    return len(self.temp_fn) > 0

  def get_temp_fn(self):
    return self.temp_fn

  def get_orig_fn(self):
    return self.orig_fn

  def free(self):
    if os.path.exists(self.get_temp_fn()):
      print "Deleting %s ..." % self.get_temp_fn()
      os.remove(self.get_temp_fn())

  def __repr__(self):
    return "Orig: '{}', Temp: '{}', Error: '{}'".format(self.orig_fn, self.temp_fn, self.err_msg)

def scale_convert(fn, dl_format, ds_factor, ATLASES):
  print "Entering scale function with file '{}'...".format(fn)
  ret = TempGraph(fn)
  try:
    # Downsample only valid for *BIG* human brains!
    # *NOTE: If smallgraphs are ingested this will break

    if ds_factor and get_genus(fn) == "human":
      if isinstance(ds_factor, int): # Downsample by a factor
        print "downsampling to factor %d" % ds_factor
        g = downsample(igraph_io.read_arbitrary(fn, "graphml"), ds_factor)
        print "downsample complete"
      else: # Or downsample by an atlas
        g = downsample(igraph_io.read_arbitrary(fn, "graphml"), atlas=nib_load(ATLASES[ds_factor]))
    else: # No downsample at all
      fn = get_equiv_fn(fn)
      g = igraph_io.read_arbitrary(fn, os.path.splitext(fn)[1][1:])
    
    # We are able to read the i/p fn so create rest of object
    ret._make_fn()
    
    # Write to `some` format
    if dl_format == "mm":
      igraph_io.write_mm(g, ret.get_temp_fn())
    else:
      g.write(ret.get_temp_fn(), format=dl_format)

  except Exception, msg:
    print "An exception was thrown and caught with message %s!" % msg
    ret._add_error(msg)

  return ret
