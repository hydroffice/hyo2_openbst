import codecs
import os
import re

from setuptools import setup, find_packages

# ------------------------------------------------------------------
#                         HELPER FUNCTIONS

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M, )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


# ------------------------------------------------------------------
#                          POPULATE SETUP

setup(
    name="hyo2.openbst",
    version=find_version("hyo2", "openbst", "__init__.py"),
    license="LGPLv3 license",

    namespace_packages=[
        "hyo2"
    ],
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "*.test*",
    ]),
    package_data={
        "": [
            'openbst/app/media/*.*',
            'openbst/app/dialogs/array_explorer/media/*.*',
            'openbst/notebooks/*.ipynb',
            'openbst/notebooks/images/*.*',
        ],
    },
    zip_safe=False,
    ext_modules=None,
    setup_requires=[
        "setuptools",
        "wheel"
    ],
    install_requires=[
        "hyo2.abc",
    ],
    python_requires='>=3.5',
    entry_points={
        "gui_scripts": [
            "OpenBST = hyo2.openbst.app:main",
        ],
        "console_scripts": [

        ],
    },
    test_suite="tests",

    description="Library and Application for the Open BackScatter Toolchain Project.",
    long_description=read(os.path.join(here, "README.rst")),
    url="https://www.hydroffice.org/openbst/main",
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="hydrography ocean mapping acoustic backscatter mosaic reflectivity",
    author="Giuseppe Masetti, Jean-Marie Augustin, Cyrille Poncelet",
    author_email="gmasetti@ccom.unh.edu, jean.marie.augustin@ifremer.fr, cyrille.poncelet@ifremer.fr",
)
