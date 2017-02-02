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

# tasks.py
# Created by Disa Mhembere on 2015-09-06.
# Email: disa@jhu.edu

from __future__ import absolute_import
import os

from celery import task, group
from django.conf import settings
from pipeline.utils.util import sendJobFailureEmail, sendJobCompleteEmail, sendEmail
from pipeline.utils.util import get_genus, get_equiv_fn
from pipeline.procs.scale_convert import TempGraph
from pipeline.utils.zipper import zipfiles
from pipeline.utils.util import get_download_path

#import logging
#logger = logging.getLogger("mrocp")

@task(queue="mrocp")
def mrocp(param):
  print "The param was {0}!!!".format(param)
  return "EXITED CORRECTLY"

@task(queue="mrocp")
def task_convert(upload_fn, convert_file_save_loc, input_format, output_format):
  print "Entering convert task ..."
  from computation.utils import convertTo

  outfn, err_msg = convertTo.convert_graph(upload_fn, input_format, convert_file_save_loc, *output_format)
  if (err_msg):
    res = "- File: '{}'\n- '{}'\n\n".format(outfn, err_msg)
  else: res = 0

  print "Exiting convert task ..."
  return res

@task(queue="mrocp")
def task_mp_convert(upload_fns, convert_file_save_loc, input_format, output_format, to_email):
  print "Entering mp_convert task ..."
  # Send begin job email
  content = "Hello,\n\n You requested the following files be converted:"
  for fn in upload_fns:
    content += "\n- " + os.path.basename(fn)
  content += "\n\nTo the following formats:"
  for fmt in output_format:
    content += "\n- " + fmt

  sendEmail(to_email, "Job launch Notification", content+"\n\n")
  # End Email junk

  print "Entering multiprocess convert ..."

  #"""
  funcs = map((lambda fn: task_convert.s(fn, convert_file_save_loc, input_format, output_format)), upload_fns)
  callback = group(funcs)()
  result = callback.get()

  """
  # For minimal testing
  task_convert(upload_fns[0], convert_file_save_loc, input_format, output_format)
  """
  dwnld_loc = get_download_path(convert_file_save_loc)

  err_msg = ""

  for msg in result:
    if msg:
     ## There's an error of some kind so accumulate errors
      err_msg += msg

  if not err_msg:
    sendJobCompleteEmail(to_email, dwnld_loc)
  else:
    err_msg = "Hello,\n\nYour most recent job a had failure." +\
    "\n\n You may have some partially completed data at {}." +\
    "\nHere's an error list:\n".format(dwnld_loc) + err_msg +\
    "Please check these and try again.\n\n"

    sendJobFailureEmail(to_email, err_msg, dwnld_loc)

@task(queue="mrocp")
def task_invariant_compute(invariants, graph_fn, invariants_path, in_graph_format):
  print "Entering invariant task ..."
  from pipeline.procs.inv_compute import invariant_compute
  res = invariant_compute(invariants, graph_fn, invariants_path, in_graph_format)
  print "Exiting invariant task ..."
  return res

@task(queue="mrocp")
def task_mp_invariant_compute(invariants, graph_fns, invariants_path,
    data_dir, in_graph_format, to_email):
  print "Entering multiprocess invariant compute task ..."

  dwnld_loc = get_download_path(data_dir)
  funcs = map((lambda fn: task_invariant_compute.s(invariants, fn, invariants_path,
      in_graph_format)), graph_fns)

  callback = group(funcs)()
  result = callback.get()

  err_msg = ""
  for msg in result:
    if msg:
     ## There's an error of some kind so accumulate errors
      err_msg += msg

  if not err_msg:
    sendJobCompleteEmail(to_email, dwnld_loc)
  else:
    err_msg = "Hello,\n\nYour most recent job a had failure." +\
    "\n\n You may have some partially completed data at {}." +\
    "\n\n".format(dwnld_loc) + err_msg +\
    "Please check these and try again.\n\n"

    sendJobFailureEmail(to_email, err_msg, dwnld_loc)

@task(queue="mrocp")
def task_runc4(data_dir, inp, out, email):
  print "Entering c4 task ..."
  content = "Congratulations,\n\nYour c4 job has started. " +\
  "You will receive a notification when it completes."
  sendEmail(email, "Job launch Notification", content+"\n\n")

  print "Making output dir '{}'...".format(os.path.join(data_dir, out))
  os.makedirs(os.path.join(data_dir, out))
  dwnld_loc = get_download_path(os.path.join(data_dir, out))

  from pipeline.procs.runc4 import runc4
  retcode = runc4(data_dir, inp, out)

  if retcode:
    err_msg = "Hello,\n\nUnfortunately, your most recent job failed "+\
	"with exit code '{}'. Please check your data and retry.".format(retcode)
    sendJobFailureEmail(email, err_msg, dwnld_loc)
  else:
    print "Emailing job completion to '{}' with dwnld_loc '{}'...".format(email, dwnld_loc)
    sendJobCompleteEmail(email, dwnld_loc)

  print "Exiting c4 task ..."

@task(queue="mrocp")
def task_build(derivatives, graph_loc, graphsize, invariants,
                        proj_dir, to_email):
  print "Entering build task ..."
  from pipeline.procs.process_ip_data import process_input_data
  process_input_data(derivatives, graph_loc, graphsize, invariants,
                        proj_dir, to_email)
  print "Exiting build task ..."

@task(queue="mrocp")
def task_scale(_file, dl_format, ds_factor, ATLASES):
  from pipeline.procs.scale_convert import scale_convert
  print "Entering download/scale task ..."
  out = scale_convert(_file, dl_format, ds_factor, ATLASES)
  print "Exiting download/scale task ..."
  return out.__dict__

# Multiprocessed scaling
@task(queue="mrocp")
def task_mp_scale(selected_files, dl_format, ds_factor, ATLASES, email=None, dwnld_loc=None, zip_fn=None):
  print "Entering multiprocess download/scale task ..."

  err_msg = ""

  if dl_format == "graphml" and ds_factor == 0:
    zipfiles(selected_files, use_genus=True, zip_out_fn=zip_fn)
  elif get_genus(selected_files[0]) == "human" and dl_format == "ncol" and ds_factor == 0:
    zipfiles(map(get_equiv_fn, selected_files), use_genus=True, zip_out_fn=zip_fn)

  else:
    # Create the list of task
    #"""
    funcs = map((lambda fn: task_scale.s(fn, dl_format, ds_factor, ATLASES)), selected_files)
    callback = group(funcs)()
    result = callback.get()
    """
    task_scale(selected_files[0], dl_format, ds_factor, ATLASES)
    """

    # Zip any results if present and Check for errors
    files_to_zip = {}

    for _dict in result:
      obj = TempGraph(_dict["orig_fn"], _dict["temp_fn"], _dict["err_msg"])
      if (obj.has_error()):
        err_msg += "\n- " + obj.get_error()
      if (obj.has_temp_fn()):
        print "Adding {}:{} to zips".format(obj.get_temp_fn(), obj.get_orig_fn())
        files_to_zip[obj.get_temp_fn()] = obj.get_orig_fn()

    print "Attempting zip ..."
    zipfiles(files_to_zip, use_genus=True, zip_out_fn=zip_fn, gformat=dl_format)

  if err_msg:
    msg = "Hello,\n\nYour most recent job failed to fully complete." \
          "\nYou may have some partially completed data at {}. The " \
          "error messages received are: {}\n\n".format(dwnld_loc, err_msg)

    sendJobFailureEmail(email, msg, dwnld_loc)
  else:
    sendJobCompleteEmail(email, dwnld_loc)
    print "Exiting multiprocess download/scale task ..."
