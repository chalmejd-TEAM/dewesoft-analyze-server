from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "fast_calculations",
        ["fast_calculations.cpp"],  # Path to your C++ file
    ),
]

setup(
    name="fast_calculations",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
