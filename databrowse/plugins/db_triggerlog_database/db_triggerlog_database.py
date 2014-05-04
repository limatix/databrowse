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
""" plugins/renderers/db_triggerlog_database.py - Basic Output for Any Folder """

import databrowse.plugins.db_directory.db_directory as db_directory_module
from lxml import etree
import os


class db_triggerlog_database(db_directory_module.db_directory):
    """ Image Directory Renderer """

    _default_content_mode = "title"
    _default_style_mode = "view_trigger_log"
    _default_recursion_depth = 1

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        if caller == "databrowse":
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/triggerlogdb"
            self._namespace_local = "tgldb"
        else:
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
            self._namespace_local = "dir"
            self._disable_load_style = True

        tmpref = self.getDirectoryList
        self.getDirectoryList = self.getTriggerlogDatabaseDirectoryList
        super(db_triggerlog_database, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)
        self.getDirectoryList = tmpref

        pass

    def getTriggerlogDatabaseDirectoryList(self, fullpath, sort=None, order="asc"):
        """ Build a Sorted List of Files with Appropriate Files Removed """
        #print "getDirectoryList being called"
        reallist = os.listdir(fullpath)
        returnlist = [n for n in reallist if n.endswith('.tgl')]
        exec "returnlist.sort(%s%s)" % ("reverse=True" if order == "desc" else "reverse=False", ",key=%s" % sort if sort is not None else ",key=str.lower")
        return returnlist

    def getContent(self):
        return super(db_triggerlog_database, self).getContent()
    pass
