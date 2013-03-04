#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012 Iowa State University                                  ##
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
""" plugins/handlers/dbh_xml_monthlyrpt.py - Monthly Report XML Handler """

import os.path
import fnmatch


def dbh_xml_monthlyrpt(path, contenttype, extension):
    """ Monthly Report XML Handler - Returns xml_monthly_rpt for Monthly Report """
    if fnmatch.fnmatch(os.path.basename(path), "monthlyrpt_*-*.xml"):
        return "dbr_xml_monthly_rpt"
    else:
        return False
