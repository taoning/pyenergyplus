from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import json
import os
import shutil
import platform
from pathlib import Path
import subprocess as sp
import sys

from wheel.bdist_wheel import bdist_wheel


def _remove_empty_string_enums(schema):
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "enum" and isinstance(value, list):
                schema[key] = [item for item in value if item != ""]
            else:
                _remove_empty_string_enums(value)
    elif isinstance(schema, list):
        for item in schema:
            _remove_empty_string_enums(item)


def _replace_enum_with_ref(obj):
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if key == "enum" and "No" in value and "Yes" in value:
                obj.clear()
                obj["$ref"] = "#/definitions/EPBoolean"
            else:
                _replace_enum_with_ref(value)
    elif isinstance(obj, list):
        for item in obj:
            _replace_enum_with_ref(item)


def generate_epjson_schema(ep_dir):
    """Generate Energy+.schema.epJSON from the EnergyPlus IDD source."""
    idd_dir = Path(ep_dir) / "idd"
    schema_script = idd_dir / "schema" / "generate_epJSON_schema.py"
    sp.check_call([sys.executable, str(schema_script), str(idd_dir)])
    return idd_dir / "Energy+.schema.epJSON"


def _strip_numeric_constraints_in_anyof(schema):
    """Strip numeric constraints from anyOf branches that coexist with a string branch.

    When a field accepts either a number or a sentinel string like "Autosize",
    datamodel-code-generator would normally generate a constrained RootModel[float]
    for the numeric branch (e.g. RootModel[float] with gt=0.0).  With reuse_model=True
    that same class can end up with a string default ("Autocalculate"), which breaks
    pydantic's default_factory at runtime.  Dropping the numeric constraints here keeps
    the numeric branch as a plain float so the union float | Literal["Autosize"] is
    generated correctly and the string default is valid.
    """
    if isinstance(schema, dict):
        if "anyOf" in schema:
            variants = schema["anyOf"]
            has_number = any(
                isinstance(v, dict) and v.get("type") == "number" for v in variants
            )
            has_string = any(
                isinstance(v, dict) and v.get("type") == "string" for v in variants
            )
            if has_number and has_string:
                for v in variants:
                    if isinstance(v, dict) and v.get("type") == "number":
                        for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"):
                            v.pop(key, None)
        for v in schema.values():
            _strip_numeric_constraints_in_anyof(v)
    elif isinstance(schema, list):
        for item in schema:
            _strip_numeric_constraints_in_anyof(item)


def generate_model(schema_path, output_path):
    """Generate pydantic model from the epJSON schema."""
    from datamodel_code_generator import (
        DataModelType,
        InputFileType,
        LiteralType,
        PythonVersion,
        generate,
    )

    schema = json.loads(Path(schema_path).read_text())

    _replace_enum_with_ref(schema)
    _remove_empty_string_enums(schema)
    _strip_numeric_constraints_in_anyof(schema)

    schema.setdefault("definitions", {})["EPBoolean"] = {
        "type": "string",
        "enum": ["No", "Yes"],
        "default": "No",
    }

    generate(
        json.dumps(schema),
        input_file_type=InputFileType.JsonSchema,
        output=Path(output_path),
        output_model_type=DataModelType.PydanticV2BaseModel,
        snake_case_field=True,
        use_double_quotes=True,
        enum_field_as_literal=LiteralType.One,
        reuse_model=True,
        field_constraints=True,
        use_annotated=True,
        set_default_enum_member=True,
        target_python_version=PythonVersion.PY_310,
        class_name="EnergyPlusModel",
    )


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

        cmake_build_cmd = ["cmake", "--build", ".", f"-j{os.cpu_count()}"]
        if arch:
            cmake_cmd += ["-A", arch]
        cmake_cmd.append("-DBUILD_FORTRAN=ON")
        if platform.system().lower() == "darwin":
            cmake_cmd.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=12.1")
        if platform.system().lower() != "windows":
            cmake_cmd.append("-DCMAKE_BUILD_TYPE=Release")
        else:
            cmake_cmd.append("-DLINK_WITH_PYTHON:BOOL=ON")
            py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
            cmake_cmd.append(f"-DPython_REQUIRED_VERSION:STRING={py_ver}")
            cmake_cmd.append(f"-DPython_ROOT_DIR:PATH={os.path.dirname(pypath)}")
            mingw_gfortran = os.environ.get(
                "CMAKE_Fortran_COMPILER",
                "C:/msys64/mingw64/bin/gfortran.exe"
            )
            cmake_cmd.append(f"-DMINGW_GFORTRAN={mingw_gfortran}")
            cmake_build_cmd += ["--config", "Release"]
            pdir = Path("Products") / "Release"
        exe_dir = Path("Products")
        cmake_cmd.append(ext.cmake_source_dir)
        sp.check_call(cmake_cmd)
        sp.check_call(cmake_build_cmd)
        output_dir = os.path.join(build_lib, ext.name)
        os.makedirs(output_dir, exist_ok=True)
        file_extension = platform_file_extension[platform.system()]
        lib_files = pdir.glob(f"*.{file_extension['lib']}*")
        for file in lib_files:
            shutil.move(str(file), build_lib)
        # ExpandObjects
        expandobject_path = exe_dir / ("ExpandObjects" + file_extension["exe"])
        if expandobject_path.exists():
            shutil.move(str(expandobject_path), build_lib)
        # ReadVarsESO
        readvars_path = exe_dir / ("ReadVarsESO" + file_extension["exe"])
        if readvars_path.exists():
            shutil.move(str(readvars_path), build_lib)
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
        model_src = Path(cwd) / "src" / "model"
        model_dst = Path(build_lib) / "pyenergyplus" / "model"
        model_dst.mkdir(parents=True, exist_ok=True)
        for fname in ("__init__.py", "builder.py"):
            shutil.copy(str(model_src / fname), str(model_dst / fname))
        schema_path = generate_epjson_schema(Path(cwd) / "EnergyPlus")
        generate_model(schema_path, model_dst / "model.py")
        os.chdir(cwd)


setup(
    name="pyenergyplus_lbnl",
    version="25.2.0",
    packages=[],
    setup_requires=["datamodel-code-generator>=0.55.0"],
    install_requires=["pydantic>=2.3.0"],
    license="LICENSE.txt",
    author="LBNL",
    author_email="taoningwang@lbl.gov",
    url="https://github.com/taoning/pyenergyplus",
    description="Direct port of pyenergyplus that comes with EnergyPlus into a standalone Python package",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension("pyenergyplus", "EnergyPlus", "EnergyPlus")],
    cmdclass={
        "build_ext": CMakeBuild,
        "bdist_wheel": PyenergyplusBDistWheel,
    },
)
