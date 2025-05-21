from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import shutil
import platform
from pathlib import Path
import subprocess as sp
import sys

from wheel.bdist_wheel import bdist_wheel


wheels = {
    "darwin": {
        "x86_64": {
            "wheel": "macosx_10_13_x86_64",
            "zip_tag": "OSX",
            "build_tool": "Ninja",
        },
        "arm64": {
            "wheel": "macosx_11_0_arm64",
            "zip_tag": "OSX_arm64",
            "build_tool": "Ninja",
            "cxx": "/opt/homebrew/bin/c++-14",
            "cc": "/opt/homebrew/bin/gcc-14",
            "cmake": "/opt/homebrew/bin/cmake",
        },
    },
    "linux": {
        "x86_64": {
            "wheel": "manylinux1_x86_64",
            "zip_tag": "Linux",
            "build_tool": "Ninja",
        }
    },
    "windows": {
        "i386": {
            "wheel": "win32",
            "zip_tag": "Windows",
            "arch": "x64",
            "build_tool": "Visual Studio 17 2022",
        },
        "amd64": {
            "wheel": "win_amd64",
            "zip_tag": "Windows",
            "arch": "x64",
            "build_tool": "Visual Studio 17 2022",
        },
    },
}
platform_file_extension = {
    "Darwin": {
        "lib": "dylib",
        "exe": "",
    },
    "Linux": {
        "lib": "so",
        "exe": "",
    },
    "Windows": {
        "lib": "dll",
        "exe": ".exe",
    }
}
libdir = list(Path("build").glob("lib*"))
if len(libdir) > 0:
    shutil.rmtree(libdir[0], ignore_errors=True)
wheel = wheels[platform.system().lower()][platform.machine().lower()]

# Model files
ref_files = [
    "RefBldgFullServiceRestaurantNew2004_Chicago.idf",
    "RefBldgHospitalNew2004_Chicago.idf",
    "RefBldgLargeHotelNew2004_Chicago.idf",
    "RefBldgLargeOfficeNew2004_Chicago.idf",
    "RefBldgMediumOfficeNew2004_Chicago.idf",
    "RefBldgMidriseApartmentNew2004_Chicago.idf",
    "RefBldgOutPatientNew2004_Chicago.idf",
    "RefBldgPrimarySchoolNew2004_Chicago.idf",
    "RefBldgQuickServiceRestaurantNew2004_Chicago.idf",
    "RefBldgSecondarySchoolNew2004_Chicago.idf",
    "RefBldgSmallHotelNew2004_Chicago.idf",
    "RefBldgSmallOfficeNew2004_Chicago.idf",
    "RefBldgStand-aloneRetailNew2004_Chicago.idf",
    "RefBldgStripMallNew2004_Chicago.idf",
    "RefBldgSuperMarketNew2004_Chicago.idf",
    "RefBldgWarehouseNew2004_Chicago.idf",
    "ASHRAE901_ApartmentHighRise_STD2019_Denver.idf",
    "ASHRAE901_ApartmentMidRise_STD2019_Denver.idf",
    "ASHRAE901_Hospital_STD2019_Denver.idf",
    "ASHRAE901_HotelLarge_STD2019_Denver.idf",
    "ASHRAE901_HotelSmall_STD2019_Denver.idf",
    "ASHRAE901_OfficeLarge_STD2019_Denver.idf",
    "ASHRAE901_OfficeMedium_STD2019_Denver.idf",
    "ASHRAE901_OfficeSmall_STD2019_Denver.idf",
    "ASHRAE901_OutPatientHealthCare_STD2019_Denver.idf",
    "ASHRAE901_RestaurantFastFood_STD2019_Denver.idf",
    "ASHRAE901_RestaurantSitDown_STD2019_Denver.idf",
    "ASHRAE901_RetailStandalone_STD2019_Denver.idf",
    "ASHRAE901_RetailStripmall_STD2019_Denver.idf",
    "ASHRAE901_SchoolPrimary_STD2019_Denver.idf",
    "ASHRAE901_SchoolSecondary_STD2019_Denver.idf",
    "ASHRAE901_Warehouse_STD2019_Denver.idf",
]

weather_files = [
    "USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780_TMY3.epw",
    "USA_CA_Fresno.Air.Terminal.723890_TMY3.epw",
    "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw",
    "USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw",
    "USA_CO_Colorado.Springs-Peterson.Field.724660_TMY3.epw",
    "USA_CO_Denver-Aurora-Buckley.AFB.724695_TMY3.epw",
    "USA_CO_Golden-NREL.724666_TMY3.epw",
    "USA_FL_Miami.Intl.AP.722020_TMY3.epw",
    "USA_FL_Orlando.Intl.AP.722050_TMY3.epw",
    "USA_FL_Tampa.Intl.AP.722110_TMY3.epw",
    "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw",
    "USA_IL_University.of.Illinois-Willard.AP.725315_TMY3.epw",
    "USA_NJ_Newark.Intl.AP.725020_TMY3.epw",
    "USA_NV_Las.Vegas-McCarran.Intl.AP.723860_TMY3.epw",
    "USA_OK_Oklahoma.City-Will.Rogers.World.AP.723530_TMY3.epw",
    "USA_VA_Sterling-Washington.Dulles.Intl.AP.724030_TMY3.epw",
]

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

        ep_dir = Path("EnergyPlus")
        model_dir = (ep_dir / "testfiles").resolve()
        weather_dir = (ep_dir / "weather").resolve()
        build_temp = os.path.abspath(self.build_temp)
        build_lib = os.path.abspath(self.build_lib)

        os.makedirs(build_temp, exist_ok=True)
        os.chdir(build_temp)

        cfg = wheels[platform.system().lower()][platform.machine().lower()]
        if "arch" in cfg:
            arch = cfg['arch']
        else:
            arch = None

        # call cmake to configure the build
        pdir = Path("Products")

        cmake_cmd = [
            "cmake",
            "-G",
            cfg["build_tool"]
        ]
        pypath = sys.executable

        num_cores = os.cpu_count()
        cmake_build_cmd = ["cmake", "--build", ".", f"-j{num_cores}"]

        if arch:
            cmake_cmd += ["-A", arch]

        cmake_cmd.append("-DBUILD_FORTRAN=OFF")

        if platform.system().lower() == "darwin":
            cmake_cmd.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=12.1")
            cmake_cmd.append(f"-DCMAKE_CXX_COMPILER={cfg["cxx"]}")
            cmake_cmd.append(f"-DCMAKE_C_COMPILER={cfg["cc"]}")

        if platform.system().lower() != "windows":
            cmake_cmd.append("-DCMAKE_BUILD_TYPE=Release")

        else:
            cmake_cmd.append("-DLINK_WITH_PYTHON:BOOL=ON")
            cmake_cmd.append("-DPython_REQUIRED_VERSION:STRING=3.10")
            cmake_cmd.append(f"-DPython_ROOT_DIR:PATH={os.path.dirname(pypath)}")
            cmake_build_cmd += ["--config", "Release"]
            pdir = Path("Products") / "Release"
        cmake_cmd.append(ext.cmake_source_dir)
        sp.check_call(cmake_cmd)
        sp.check_call(cmake_build_cmd)
        output_dir = os.path.join(build_lib, ext.name)
        os.makedirs(output_dir, exist_ok=True)
        file_extension = platform_file_extension[platform.system()]
        lib_files = pdir.glob(f"*.{file_extension['lib']}*")
        for file in lib_files:
            shutil.move(str(file), build_lib)
        # ExpandObject
        expandobject_path = pdir / ("ExpandObjects" + file_extension["exe"])
        if expandobject_path.exists():
            shutil.move(str(expandobject_path), build_lib)
        sdir = pdir / "pyenergyplus"
        for file in sdir.glob("*.py"):
            shutil.move(str(file), os.path.join(build_lib, "pyenergyplus"))
        pyepdir = Path(build_lib) / "pyenergyplus"
        mdir = pyepdir / "data" / "model"
        wdir = pyepdir / "data" / "weather"
        mdir.mkdir(parents=True, exist_ok=True)
        wdir.mkdir(parents=True, exist_ok=True)
        for mfile in ref_files:
            shutil.copy(str(model_dir / mfile), mdir)
        for wfile in weather_files:
            shutil.copy(str(weather_dir / wfile), wdir)
        shutil.copy(os.path.join(cwd, "src", "dataset.py"), os.path.join(build_lib, "pyenergyplus"))
        os.chdir(cwd)


setup(
    name="pyenergyplus_lbnl",
    version="23.2.0",
    packages=[],
    license="LICENSE.txt",
    author="LBNL",
    author_email="taoningwang@lbl.gov",
    url="https://github.com/taoning/pyenergyplus",
    description="Direct port of pyenergyplus that comes with EnergyPlus into a standalone Python package",
    long_description=Path("README.md").read_text(),
    ext_modules=[CMakeExtension("pyenergyplus", "EnergyPlus", "EnergyPlus")],
    cmdclass={
        "build_ext": CMakeBuild,
        "bdist_wheel": PyenergyplusBDistWheel,
    },
)
