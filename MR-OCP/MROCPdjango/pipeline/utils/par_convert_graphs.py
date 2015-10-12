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

# par_convert_graphs.py
# Created by Disa Mhembere on 2015-10-11.
# Email: disa@jhu.edu

import argparse
import multiprocessing as mp 
import os, sys
from glob import glob

from paths import include
include()
from mrcap.utils import igraph_io

def read_and_convert(inouttup):
  assert isinstance(inouttup, tuple), "arg1 of read_and_convert takes a len = 4 tuple!"
  assert len(inouttup) == 4, "arg1 of read_and_convert takes a len = 4 tuple!" 
  inname, infmt, outname, outfmt  = inouttup

  print "Reading graph {}".format(inname)
  g = igraph_io.read_arbitrary(inname, infmt)
  print "Writing graph {}".format(outname)
  g.write(outname, format=outfmt)


def get_outname(inname, outdir, outfmt):
  return os.path.join(outdir, os.path.splitext(os.path.basename(inname))[0]+"."+outfmt)

def run_on_dir(indir, infmt, outdir, outfmt, num_procs):
  if not os.path.isdir(outdir):
    print "Making the output directory"
    os.makedirs(outdir)

  innames = glob(os.path.join(indir, "*"))
  outnames = []
  for name in innames:
    outnames.append(get_outname(name, outdir, outfmt))

  assert len(innames) == len(outnames), \
      "Should be a direct mapping from innames to outnames that are same len"

  #"""
  print "Making a process pool with {} processes ...".format(num_procs)
  procpool = mp.Pool(num_procs)
  procpool.map(read_and_convert, zip(innames, [infmt]*len(innames), outnames, [outfmt]*len(outnames)))

  """
  #Test
  print "Testing with regular map!"
  map(read_and_convert, zip(innames, [infmt]*len(innames), outnames, [outfmt]*len(outnames)))
  """

def main():
  parser = argparse.ArgumentParser(description="Convert graph files from one format to another")
  parser.add_argument("indir", action="store", help="Input directory")
  parser.add_argument("infmt", action="store", help="Input format")
  parser.add_argument("outdir", action="store", help="Output directory")
  parser.add_argument("outfmt", action="store", help="Output format")
  parser.add_argument("num_procs", action="store", type=int, help="The number of processing units")
  result = parser.parse_args()

  run_on_dir(result.indir, result.infmt, result.outdir, result.outfmt, result.num_procs)

if __name__ == "__main__":
  main()
