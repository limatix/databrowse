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
""" plugins/handlers/dbh_dataguzzler.py - Generic dataguzzler file Handler """


def dbh_dataguzzler(path, contenttype, extension):
    """ Generic Dataguzzler Handler - Returns db_dataguzzler for all dataguzzler files """
    if extension.lower() == "dgs" or extension.lower() == "dgz" or extension.lower() == "dga" or extension.lower() == "dgd":
        return "db_dataguzzler"
    else:
        return False
