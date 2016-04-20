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

# disk_graph.py
# Created by Disa Mhembere on 2015-11-23.
# Email: disa@jhu.edu

#TODO: GK add fields & possibly debug

import os

class DiskGraph(object):
  def __init__(self, path):
    """
    @param path: The path to the graph on disk

    """
    assert os.path.exists(path), "Path '%s' broken" % path
    self.graph_path = os.path.abspath(path)

  def add_dataset(self, dataset):
    assert isinstance(dataset, str) , "Dataset should be a string"
    self.dataset = dataset

  def add_atlas(self, atlas):
    assert isinstance(atlas, str) , "Atlas should be a string"
    self.atlas = atlas

  def add_raw_path(self, path):
    assert os.path.exists(path), "Path '%s' broken" % path
    self.raw_path = os.path.abspath(path)

  def add_deriv_path(self, path):
    assert os.path.exists(path), "Path '%s' broken" % path
    self.deriv_path = os.path.abspath(path)

  def get_dataset(self,):
    return self.dataset

  def get_atlas(self,):
    return self.atlas

  def get_raw_path(self,):
    return self.raw_path

  def get_deriv_path(self,):
    return self.deriv_path

  def get_graph_path(self):
    return self.graph_path
  
  def __repr__(self):
    return "Graph path: {}\nDataset:{}\nAtlas: {}\nRaw path: {}\nDeriv path: {}"\
        .format(self.get_graph_path(), self.get_dataset(),
            self.get_atlas(), self.get_raw_path(), self.get_deriv_path())


def test():
  try:
    d = DiskGraph(1)
  except Exception, msg:
    print "Correct error: %s" % msg 
    d = DiskGraph("/")

    try:
      d.add_dataset(1)
    except Exception, msg:
      print "Correct error: %s" % msg
      d.add_dataset("test dataset")

      try:
        d.add_atlas(True)
      
      except Exception, msg:
        print "Correct error: %s" % msg
        d.add_atlas("test atlas")

        try:
          d.add_deriv_path(0)

        except Exception, msg:
          print "Correct error: %s" % msg
          d.add_deriv_path(".")

          try:
            d.add_raw_path(1)
          except Exception, msg:
            print "Correct error: %s" %msg
            d.add_raw_path(".")
          
            print "\nIf you got here you succeeded:\n{}".format(d)

if __name__ == "__main__":
  test()
