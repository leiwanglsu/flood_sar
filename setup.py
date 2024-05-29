
from setuptools import setup, Extension
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "region_grow",
        ["region_grow.cpp"],
        include_dirs=[pybind11.get_include()],
    ),
]

setup(
    name="region_grow",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
