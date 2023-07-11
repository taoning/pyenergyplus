from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import shutil
import platform
from pathlib import Path
import subprocess as sp

from wheel.bdist_wheel import bdist_wheel

wheels = {
    "darwin": {
        "x86_64": {
            "wheel": "macosx_10_13_x86_64",
            "zip_tag": "OSX",
        },
        "arm64": {
            "wheel": "macosx_11_0_arm64",
            "zip_tag": "OSX_arm64",
        },
    },
    "linux": {
        "x86_64": {
            "wheel": "manylinux1_x86_64",
            "zip_tag": "Linux",
        }
    },
    "windows": {
        "i386": {
            "wheel": "win32",
            "zip_tag": "Windows",
        },
        "amd64": {
            "wheel": "win_amd64",
            "zip_tag": "Windows",
        },
    },
}
platform_file_extension = {"Darwin": "dylib", "Linux": "so", "Windows": "dll"}
libdir = list(Path("build").glob("lib*"))
if len(libdir) > 0:
    shutil.rmtree(libdir[0], ignore_errors=True)
wheel = wheels[platform.system().lower()][platform.machine().lower()]


class PyenergyplusBDistWheel(bdist_wheel):
    def get_tag(self):
        return "py3", "none", wheel["wheel"]


# This class handles the CMake build
class CMakeExtension(Extension):
    def __init__(self, name, cmake_source_dir="", sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.cmake_source_dir = os.path.abspath(cmake_source_dir)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        cwd = os.getcwd()

        build_temp = os.path.abspath(self.build_temp)
        build_lib = os.path.abspath(self.build_lib)

        os.makedirs(build_temp, exist_ok=True)
        os.chdir(build_temp)

        # call cmake to configure the build
        sp.check_call(
            [
                "cmake",
                # "-G",
                # "Ninja",
                "-DBUILD_FORTRAN=ON",
                "-DCMAKE_BUILD_TYPE=Release",
                ext.cmake_source_dir,
            ]
        )

        # call cmake to build the sources
        sp.check_call(["cmake", "--build", "."])

        output_dir = os.path.join(build_lib, ext.name)
        os.makedirs(output_dir, exist_ok=True)
        pdir = Path("Products")
        file_extension = platform_file_extension[platform.system()]
        lib_files = pdir.glob(f"*.{file_extension}")
        for file in lib_files:
            shutil.move(file, build_lib)
        shutil.move(pdir / "ReadVarsESO", build_lib)
        sdir = pdir / "pyenergyplus"
        for file in sdir.glob("*.py"):
            shutil.move(file, os.path.join(build_lib, "pyenergyplus"))
        os.chdir(cwd)


setup(
    name="pyenergyplus",
    version="23.1.0",
    packages=[],
    ext_modules=[CMakeExtension("pyenergyplus", "EnergyPlus", "EnergyPlus")],
    cmdclass={
        "build_ext": CMakeBuild,
        "bdist_wheel": PyenergyplusBDistWheel,
    },
)
