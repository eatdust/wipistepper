import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
from setuptools import setup, find_packages

setup(
    name="wipistepper",
    version="0.1.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    scripts=['steppertest.py'],

    install_requires=['wiringpi'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata to display on PyPI
    author="Chris Ringeval",
    author_email="eatdirt@mageia.org",
    description="High level controls for serious steppers",
    license="GPLv3",
    keywords="stepper driver motor wiringpi arm raspberry pi",
    url="https://github.com/eatdust/wipistepper",
)
