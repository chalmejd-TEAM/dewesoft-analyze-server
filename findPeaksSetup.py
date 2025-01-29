from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11

ext_modules = [
    Extension(
        "findPeaks",
        ["findPeaks.cpp"],
        include_dirs=[pybind11.get_include()],
        extra_compile_args=["/O2", "/openmp"],  # Use MSVC-compatible flags
        extra_link_args=["/openmp"]
    ),
]

setup(
    name="findPeaks",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
