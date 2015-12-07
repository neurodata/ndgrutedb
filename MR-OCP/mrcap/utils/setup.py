from distutils.core import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

import numpy

"""
setup(
  name = "Downsample utilities",
  cmdclass = {"build_ext": build_ext},
  ext_modules = cythonize("*.pyx")
    )
"""

ext_modules=[
      Extension("downsample", ["downsample.pyx"]),
      Extension("downsample_atlas", ["downsample_atlas.pyx"]),
]

for e in ext_modules:
    e.pyrex_directives = {"boundscheck": False}

setup(
    name = 'Downsample utilities',
    cmdclass = {'build_ext': build_ext},
        ext_modules = ext_modules,
)
