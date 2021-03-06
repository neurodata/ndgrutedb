
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
# Created by Disa Mhembere
# Email: disa@jhu.edu
#import matplotlib
#matplotlib.use("Agg")

#import matplotlib.pyplot as plt

import numpy as np
import os
import sys
from glob import glob
import argparse
import scipy
from scipy import interpolate

from plotHelpers import *
import pylab as pl
import scipy.io as sio

# Issues: Done nothing with MAD

def plotInvDist(invDir, pngName, numBins =100, char = 'class', big = False):
  subj_types, zero_type, one_type, two_type = csvtodict(char = char) # load up subject types

  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen/values"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]
  #invDirs = []
  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=3, ncols=2)
  #fig_gl.tight_layout()

  maleLabelAdded = False
  femaleLabelAdded = False

  x_to_disk = []
  interp_to_disk = []

  for idx, drcty in enumerate (invDirs):
    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        #arr = np.log(arr)
        arr = np.log(arr[arr.nonzero()])
        print "Processing %s..." % arrfn
      except:
        print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.5)

      ax = pl.subplot(3,2,idx+1)

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      x = np.arange(bins[0],bins[-1],0.03) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      plot_color = pickprintcolor(subj_types, arrfn)

      if (idx == 1 and plot_color == 'black' and not maleLabelAdded):
        pl.plot(x, interp*100, color = plot_color, linewidth=1, label = 'male')
        plt.legend(bbox_to_anchor=(0.7, 1.3), loc=2, prop={'size':8}, borderaxespad=0.)
        maleLabelAdded = True

      if (idx == 1 and plot_color == 'red' and not femaleLabelAdded):
        pl.plot(x, interp*100, color = plot_color, linewidth=1, label = 'female')
        plt.legend(bbox_to_anchor=(0.7, 1.3), loc=2, prop={'size':8}, borderaxespad=0.)
        femaleLabelAdded = True
      else:
        pl.plot(x, interp*100, color = plot_color, linewidth=1)

      x_to_disk.append(x)
      interp_to_disk.append(interp)

    if idx == 0:
      pl.ylabel('Percent')
      pl.xlabel('Log Number of Local Triangles')
      ax.set_yticks(scipy.arange(0,13,4))

    if idx == 1:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Local Clustering Coefficient')
      ax.set_yticks(scipy.arange(0,13,4))

      if big and char == 'class':
        ax.set_yticks(scipy.arange(0,3,1))

    if idx == 2:
      pl.ylabel('Percent')
      pl.xlabel('Log scan statistic-1')

      if big:
        ax.set_yticks(scipy.arange(0,17,4))
      else:
        ax.set_yticks(scipy.arange(0,12,2))

    if idx == 3:
      pl.xlabel('Log Degree')

      if big:
        ax.set_yticks(scipy.arange(0,17,4))

      else:
        ax.set_yticks(scipy.arange(0,15,3))
        ax.set_xticks(scipy.arange(0,5,1))

    print "Saving for drcty: %s..." % drcty
    sio.savemat( drcty+"x_data", {"data": x_to_disk} )
    sio.savemat( drcty+"interp_data", {"data": interp_to_disk} )
    x_to_disk = []
    interp_to_disk = []

  ''' Eigenvalues '''
  # For disk saving
  eig_to_disk = []
  eig_range_to_disk = []

  ax = pl.subplot(3,2,5)
  for eigValInstance in glob(os.path.join(invDir, EigDir,"*.npy")):
    try:
      eigv = np.load(eigValInstance)
    except:
      print "Eigenvalue array"

    n = len(eigv)
    sa = (np.sort(eigv)[::-1])

    plot_color = pickprintcolor(subj_types, eigValInstance)

    pl.plot(range(1,n+1), sa/10000, color=plot_color)

    # Save
    eig_to_disk.append(sa/10000)
    eig_range_to_disk.append(range(1,n+1))

    pl.ylabel('Magnitude x $10^4$')
    pl.xlabel('Eigenvalue rank')

    if big:
      ax.set_yticks(scipy.arange(0,18,4))

  # save
  print "Saving eigs!"
  sio.savemat("eigs_data", {"data":eig_to_disk} )
  sio.savemat("eigs_range_data", {"data":eig_range_to_disk} )

  ''' Global Edges '''
  arrfn = os.path.join(invDir, 'Globals/numEdgesDict.npy')
  ax = pl.subplot(3,2,6)

  gle_to_disk = []
  glex_to_disk = []

  try:
    ass_ray = np.load(arrfn).item() # associative array
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

  zeros = []
  ones = []
  twos = []

  for key in ass_ray.keys():
    if subj_types[key] == '0':
      zeros.append(ass_ray[key])
    if subj_types[key] == '1':
      ones.append(ass_ray[key])
    if subj_types[key] == '2':
      twos.append(ass_ray[key])

  for cnt, arr in enumerate ([zeros, ones]): #, twos, ass_ray.values()
    pl.figure(1)

    arr = np.log(np.array(arr)[np.array(arr).nonzero()]) # NOTE THIS CHANGE

    n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)
    fig = pl.figure(2)

    if big:
      pass
      #ax.set_xticks(scipy.arange(17.2,18.2,.2))

    f = interpolate.interp1d(bins, n, kind='cubic')
    x = np.arange(bins[0],bins[-1],0.01) # vary linspc

    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0

    if cnt == 0: # zeros
      plot_color = 'black'#'grey'
    if cnt == 1: # ones
      plot_color = 'red'
    if cnt == 2:# twos
      plot_color = 'green'
    if cnt == 3: # ALL
      plot_color = 'red'

    pl.plot(x, interp,color = plot_color ,linewidth=1)

    ax.set_yticks(scipy.arange(0,16,4))
    ax.set_xticks(scipy.arange(17.2, 18.2, .3))
    
    print "Saving global edges!"
    sio.savemat( "Global_edges_data_%d"%cnt, {"data":interp} )
    sio.savemat( "Globalx_edges_data%d"%cnt, {"data":x} )

  pl.ylabel('Frequency')
  pl.xlabel('Log Global Edge Number')

  ax = pl.subplot(3,2,6)

  font = {'family' : 'monospace',
        'weight' : 'bold',
        'size'   : '10'}

  matplotlib.rc('font', **font)  # pass in the font dict as kwargs

  #pl.savefig(pngName+'.pdf')
  pl.savefig(pngName+'.pdf', dpi=160)
  print '~**** FIN ****~'

#########################################
#########################################

def main():
  parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
  parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
  parser.add_argument('pngName', action='store', help='Full path of directory of resulting png file')
  parser.add_argument('numBins', type = int, action='store', help='Number of bins')
  parser.add_argument('char', action='store', help='Characteristic on which to partition data: gender or class')

  parser.add_argument('-b', '--big', action="store_true", help='if working on big graphs pass in numLCCVertices.npy full with this param')

  result = parser.parse_args()

  if result.big:
    plotInvDist(result.invDir, result.pngName, result.numBins, result.char, result.big)

if __name__ == '__main__':
  main()