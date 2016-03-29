
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

# asyn_inv_compute.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import os

from run_invariants import run_invariants

def invariant_compute(invariants, graph_fn, invariants_path, in_graph_format):
  try:
    invariant_fns = run_invariants(invariants, graph_fn,
                invariants_path, 
                graph_format=in_graph_format)

    if isinstance(invariant_fns, str):
      raise Exception(invariant_fns)
    else:
      print 'Invariants for annoymous project %s complete...' % graph_fn

  except Exception, msg:
    msg = "[ERROR]: - File: '%s'\n failure: - '%s'.\n\n" % (os.path.basename(graph_fn), msg)
    return msg

  return 0 # C-style return with 0 as success
