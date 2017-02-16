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

# graph_ingest.py
# Created by Greg Kiar on 2016-04-20.
# Email: gkiar@jhu.edu

import os
import glob
from disk_graph import DiskGraph
from argparse import ArgumentParser


def get_file_list(basePath):
    graphTypes = list(('*.graphml', '*.gpickle'))
    graphFiles = [y for x in os.walk(basePath) for z in graphTypes
                  for y in glob.glob(os.path.join(x[0], z))]
    return graphFiles

def populate(graphs):
    dgs = list()
    for idx, graph in enumerate(graphs):
        dgs.append(DiskGraph(graph))
        dgs[idx].add_atlas(extract_atlas(graph))
        dgs[idx].add_dataset(extract_dataset(graph))
        dgs[idx].add_raw_path("/brainstore/MR/data/"+extract_dataset(graph)+"/raw/")
        dgs[idx].add_deriv_path("/brainstore/MR/data/"+extract_dataset(graph)+"/ndmg_v0011/")
        print dgs[idx]
    return dgs

def extract_dataset(graph):
    return str.split(os.path.basename(graph), '_')[0]

def extract_atlas(graph):
    return str.split(str.split(os.path.basename(graph), '_')[-1], '.')[0]

def main():
    parser = ArgumentParser(description="")
    parser.add_argument("basepath", action="store")
    result = parser.parse_args()
    graphs = get_file_list(result.basepath)
    dgs = populate(graphs)

if __name__ == "__main__":
    main()
