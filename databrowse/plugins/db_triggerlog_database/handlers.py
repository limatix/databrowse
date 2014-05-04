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
""" plugins/handlers/dbh_multimedia_directory.py - Image Directory Handler """

import os


def dbh_directory_triggerlog(path, contenttype, extension):
    """ Generic Image Directory Handler - Returns directory_image for all directories with more than 50 percent images """
    if contenttype.startswith("inode/directory") or contenttype.startswith("application/x-directory") or contenttype.startswith("directory"):
        dirlist = os.listdir(path)
        count = 0
        for item in dirlist:
            if (os.path.splitext(item)[1].lower() in [".tgl"]):
                count = count + 1
        if count > (len(dirlist) * 0.25):
            return "db_triggerlog_database"
        else:
            return False
    else:
        return False
