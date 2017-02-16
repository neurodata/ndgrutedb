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

# raw_upload.py
# Created by Disa Mhembere on 2015-05-28.
# Email: disa@jhu.edu

import argparse
import os
from time import strftime, localtime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings

from pipeline.forms import RawUploadForm
from pipeline.models import RawUploadModel
from pipeline.utils.util import saveFileToDisk, sendEmail
from pipeline.tasks import task_runc4

from pipeline.utils.util import get_script_prefix

def raw_upload(request):

  if request.method == "POST":
    form = RawUploadForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():

      data_dir = os.path.join(settings.MEDIA_ROOT, "c4",
                strftime("%a%d%b%Y_%H.%M.%S/", localtime()))
      inp = 'raw'
      out = 'ndmg'

      dti = form.cleaned_data["dwi"]
      mprage = form.cleaned_data["t1w"]
      bvalue = form.cleaned_data["bval"]
      bvector = form.cleaned_data["bvec"]

      ext = ".".join(mprage.name.split('.')[1:]) # gets double exts for im files
      mprage_fn = os.path.join(data_dir, inp, 'sub-1', 'ses-1', 'anat', 'sub-1_ses-1_T1w.%s' % ext)

      ext = ".".join(dti.name.split('.')[1:]) # gets double exts for im files
      dti_fn = os.path.join(data_dir, inp, 'sub-1', 'ses-1', 'dwi', 'sub-1_ses-1_dwi.%s' % ext)

      bvalue_fn = os.path.join(data_dir, inp, 'sub-1', 'ses-1', 'dwi', 'sub-1_ses-1_dwi.bval')
      bvector_fn = os.path.join(data_dir, inp, 'sub-1', 'ses-1', 'dwi', 'sub-1_ses-1_dwi.bvec')

      saveFileToDisk(mprage, mprage_fn)
      saveFileToDisk(dti, dti_fn)
      saveFileToDisk(bvalue, bvalue_fn)
      saveFileToDisk(bvector, bvector_fn)

      ru_model = RawUploadModel()
      ru_model.dtipath = dti_fn
      ru_model.mpragepath = mprage_fn
      ru_model.bvectorpath = bvector_fn
      ru_model.bvaluepath = bvalue_fn

      ru_model.email = form.cleaned_data["email"]
      ru_model.save() # Sync to Db

      task_runc4.delay(data_dir, inp, out, form.cleaned_data["email"])

      request.session["success_msg"] =\
"""
Your job successfully launched. You should receive an email to confirm launch
and another when it upon job completion. <br/> The process can take <i>several hours</i> in some cases.
"""
      return HttpResponseRedirect(get_script_prefix()+"success")

  else:
    form = RawUploadForm() # An empty, unbound form

  return render_to_response(
    "c4.html",
    {"RawUploadForm": form},
    context_instance=RequestContext(request)
    )
