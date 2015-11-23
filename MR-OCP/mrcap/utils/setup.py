from distutils.core import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

import numpy

setup(
  ext_modules = cythonize("*.pyx")
    )

"""
ext_modules=[
      Extension("cy_downsample", ["cy_downsample.pyx"], include_dirs=[numpy.get_include()]),
      Extension("cy_downsample_atlas", ["cy_downsample_atlas.pyx"]),
]

for e in ext_modules:
    e.pyrex_directives = {"boundscheck": False}

setup(
    name = 'Down Sampler',
    cmdclass = {'build_ext': build_ext},
        ext_modules = ext_modules,
)
"""
