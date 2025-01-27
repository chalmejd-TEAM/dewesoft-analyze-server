from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "weightedMean",
        ["weightedMean.cpp"],  # Path to your C++ file
    ),
]

setup(
    name="weightedMean",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)

# Run the following to build the python dependency
# python setup.py build_ext --inplace