import os
from setuptools import setup

import pygrid

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "PyGrid",
    version = pygrid.__version__,
    author = "Felix Brockherde",
    author_email = "fbrockherde@gmail.com",
    description = ("PyGrid provides a map-like interface for job submissions "
                   "to gridengine clusters."),
    license = "BSD",
    keywords = "gridengine, sungrid, sge, cluster, parallel, distributed",
    url = "http://packages.python.org/pygrid",
    packages=['pygrid'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: System :: Distributed Computing"
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Science/Research"
    ],
)
