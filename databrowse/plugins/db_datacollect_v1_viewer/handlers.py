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
""" plugins/handlers/dbh_old_DC_viewer.py - Datacollect v1 Handler """


def dbh_old_DC_viewer(path, contenttype, extension, roottag, nsurl):
    """ Datacollect v1 Handler - Returns old_DC_viewer for all DC run files """
    if extension == "xml":
        f = open(path, 'r')
        f.readline()
        test = f.readline()
        if(test.startswith("<run")):
            return "db_datacollect_v1_viewer"
        else:
            return False
    else:
        return False
