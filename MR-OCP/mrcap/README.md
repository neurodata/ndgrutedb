#Several utilities, written in python, to manipulate MR fiber data.#

This code now generates small `(70x70)` graphs that are consistent with 
the output of the MRCAP pipeline.  It also generates large graphs that
have anywhere from `400K-1M+` non-zero entries.

##Requirements##
  - Python packages:
    - numpy
    - scipy
    - igraph
    - cython
    - nibabel

  - If you want to handle large files...
    - lots of ram (> 8GB)
    - 64-bit python

### Files ###
- `fiber.py`
  - Module for reading MRI Studio-format fiber files

- `fibgergraph.py`
- `fibgergraph_sm.py`
  - Module to represent the graph derived from an MRI studio file

- `gengraph.py`
  - Script to generate a graph on a single MRI studio file

- `zindex.pyx`
  - The Morton-order space filling curve.  To get the coordinates of a large
    graph identifier call zindex.MortonXYZ ( id ) which returns [ x, y, z ].
    This is a cython optimized version of the code and needs to be installed
    into your python distribution by calling 'python setup.py install'

- `setup.py`
 - Install the zindex package into your python distribution
