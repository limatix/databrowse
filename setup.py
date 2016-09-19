#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2013 Iowa State University                             ##
##                                                                           ##
## This program is free software: you can redistribute it and/or modify      ##
## it under the terms of the GNU General Public License as published by      ##
## the Free Software Foundation, either version 3 of the License, or         ##
## (at your option) any later version.                                       ##
##                                                                           ##
## This program is distributed in the hope that it will be useful,           ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of            ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             ##
## GNU General Public License for more details.                              ##
##                                                                           ##
## You should have received a copy of the GNU General Public License         ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>.     ##
###############################################################################
""" setup.py - Main Install Script """

import os
from setuptools import setup, find_packages


def readfile(filename):
    """ Utility Function to Read the Readme File """
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name="databrowse",
    author="Tyler Lesthaeghe",
    author_email="tylerl@iastate.edu",
    description="An Extensible Data Management Platform",
    keywords="databrowse data management",
    url="http://thermal.cnde.iastate.edu",
    version='0.7.1',
    packages=find_packages(exclude=['databrowse_wsgi']),
    package_data = {'':['*.conf', '*.xml']},
    license="BSD-3",
    long_description=readfile('README'),
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: JavaScript",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ]
)
