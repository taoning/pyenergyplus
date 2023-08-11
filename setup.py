from setuptools import setup
import platform
import os

# Determine the platform and Python version
package = 'pyenergyplus'
plat = platform.system().lower()
machine = platform.machine().lower()
py_version = platform.python_version_tuple()
py_version_str = f"{py_version[0]}{py_version[1]}"
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
            "build_tool": "Visual Studio 16 2019",
        },
        "amd64": {
            "wheel": "win_amd64",
            "zip_tag": "Windows",
            "arch": "x64",
            "build_tool": "Visual Studio 16 2019",
        },
    },
}

wheel = wheels[plat][machine]['wheel']
# Define the URL template for the wheels
url = f"https://github.com/taoning/pyenergyplus/raw/main/wheels/{plat}/{package}-23.1.0-py3-none-{wheel}.whl"

setup(
    name='pyenergyplus',
    version='23.1.0',
    install_requires=['pyenergyplus'],
    dependency_links=[url],
)

