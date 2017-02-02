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

# runc4.py
# Created by Disa Mhembere, Greg Kiar on 2015-05-28.
# Email: disa@jhu.edu, gkiar07@gmail.com

import argparse
from django.core.mail import send_mail
from django.conf import settings
import ndmg.scripts.ndmg_pipeline as mgp
import os

def runc4(data_dir, inp, outp):
    """
    Job launched by webservice to execute ndmg pipeline and graph generation.
    """
    print "Running c4. data_dir: {}, inp: {}, outp:{}".format(data_dir, inp,
            outp)

    return os.system('docker run -t -v %s:/data bids/ndmg:latest /data/%s /data/%s participant' % (data_dir, inp, outp) )
