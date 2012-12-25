import scipy.io as sio
import numpy as np
import os
import csv
from time import time

def convertLCCNpyToMat(lcc_fn):
  '''
  Convert a npy largest connected components file to an equivalent .mat file
  lcc_fn - largest connected components full file name which should be a .npy
  '''
  start  = time()
  lcc = np.load(lcc_fn).item().toarray()
  sio.savemat(os.path.splitext(lcc_fn)[0],{'lcc': lcc}, appendmat = True)
  print ('Lcc sucessfully converted from .npy to .mat in  %.2f secs') % (time()-start)


def convertAndSave(fn, toFormat, saveLoc, fileType):
  '''
  * Big graphs
  Covert an array between .npy, .csv, .mat
  fn - the filename of the file to be converted
  fileType - the fileType is the type of invariant ('cc','ss1' etc) or 'fg'|'fibergraph'
  '''

  fnExt = os.path.splitext(fn)[1]
  fnBase = os.path.splitext(fn.split('/')[-1])[0] # eg. M854656235_degree

  start = time()

  theFile = loadFile(fn, fileType)
  # Fix this

  #if (fnExt == '.npy' and toFormat == '.mat'):
  #  arr = np.load(fn)
  #  sio.savemat(os.path.join(saveLoc, fnBase), {fileType ,arr}, appendmat = True)
  #
  #elif (fnExt == '.mat' and toFormat == '.npy'):
  #
  #  arr = sio.loadmat(fn) # Temp dict with headers etc + data
  #  dataMemberName = (set(arr.keys()) - set(['__version__', '__header__', '__globals__'])).pop() # extract data member from .mat
  #  arr = arr[dataMemberName]
  #  np.save(os.path.join(saveLoc, fnBase), arr)
  #
  #elif ((fnExt == '.mat' or fnExt == '.npy') and toFormat == '.csv'):
  #  pass # TODO DM: Convert to csv
  #
  #else:
  #  print "[ERROR] in convertArray Invalid file format! Only .csv, .npy & .mat"
  #  sys.exit(-1)

  print ('%s sucessfully converted from .npy to .mat in  %.2f secs') % (fileType, fnExt, toFormat ,(time()-start))


def convertGraph(G_fn, toFormat):
  '''
  Convert a graph from mat format to npy format
  G_fn - the graph name
  '''
  fnExt = os.path.splitext(fn)[1]

  if (fnExt == '.mat' and toFormat == '.npy'):
    start  = time()
    G = sio.loadmat(G_fn)['fibergraph']
    np.save(os.path.splitext(G_fn)[0],G)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif (fnExt == '.npy' and toFormat == '.mat'):
    start  = time()
    sio.savemat(os.path.splitext(G_fn)[0], {'fibergraph':np.load(G_fn)} , appendmat=True)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif ((fnExt == '.npy' or fnExt == '.npy')  and toFormat == '.csv'):
    convertGraphToCSV(G_fn)

  else:
    print "[ERROR] in convertGraph Invalid file format! Only .csv, .npy & .mat"
    sys.exit(-1)

def convertSVDNpyToMat(svd_fn):
  '''
  Convert a npy sigular value decomposition file to an equivalent .mat file
  svd_fn - sigular value decomposition full file name which should be a .npy
  '''
  sio.savemat(os.path.splitext(svd_fn)[0],{'svd': np.load(svd_fn)}, appendmat = True)

def convertGraphToCSV(G_fn, G=None):
  '''
  * Infesible for big graphs ~9T space & 62 Days!
  Convert a graph .mat format to a dense comma separated value file (.csv)
  graph_fn - the full file name of the graph.
  '''
  fnExt = os.path.splitext(G_fn)[1]
  if not G:
    if (fnExt == '.mat'):
      G = sio.loadmat(G_fn)['fibergraph']
    if (fnExt == '.npy'):
      G = np.load(G_fn)

  if (G.shape[0] > 500):
    start = time()
    with open(os.path.splitext(G_fn)[0]+'.csv', 'wb') as csvfile:
      writer = csv.writer(csvfile, dialect='excel')
      for vertex in G.shape[0]:
        denseRow = np.array(G[vertex,:].todense())[0].tolist()
      writer.writerow(denseRow)
    print ('Graph successfully converted from %s to .csv in  %.2f secs') % (fnExt , (time()-start))

  else:
    print ('Sorry your graph is too big. Max size = 500 X 500')

def loadFile(file_fn, fileType):
    '''
    @param file_fn the filename of the file to be loaded
    @param fileType the fileType to loaded.
    @return the loaded file

    The following are valid fileTypes:
    1.'cc'|'clustCoeff' is the clustering coefficient
    2.'deg'|'degree' is the local vertex degree
    3.'eig'|'eigen' is the eigenvalues
    4.'mad'|'maxAvgDeg'
    5.'ss1'| 'scanStat1'
    6.'tri'|'triangle',
    7.'fg'|'fibergraph'
    '''
    fn, ext  = os.path.splitext(file_fn)
    if (ext == '.mat' and  fileType in settings.EQUIV_NP_ARRAYS.keys()):
      theFile = sio.loadmat(result.fileToConvert)[fileType]

    elif (ext == '.mat'and fileType in settings.EQUIV_NP_ARRAYS.values()):  # All currently available
      theFile = sio.loadmat(result.fileToConvert)[settings.EQUIV_NP_ARRAYS[fileType]]

    elif (ext == '.mat'and (fileType == 'fibergraph' or fileType == 'fg')):  # fibergraph
      theFile = sio.loadmat(result.fileToConvert)['fibergraph']

    elif (ext == '.mat'and (fileType == 'maxAvgDeg' or fileType == 'mad')): # MAD
      theFile = sio.loadmat(result.fileToConvert)['mad']

    elif (ext == '.npy'):
      theFile = np.load(result.fileToConvert)
    return theFile