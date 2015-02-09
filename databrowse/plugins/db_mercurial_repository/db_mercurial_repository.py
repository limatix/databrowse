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
""" plugins/renderers/db_directory_image.py - Basic Output for Any Folder """

import databrowse.plugins.db_directory.db_directory as db_directory_module
import subprocess
import os


class db_mercurial_repository(db_directory_module.db_directory):
    """ Image Directory Renderer """

    _default_content_mode = "title"
    _default_style_mode = "view_repository"
    _default_recursion_depth = 1

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=_default_content_mode, style_mode=_default_style_mode, recursion_depth=_default_recursion_depth):
        if caller == "databrowse":
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/hgdir"
            self._namespace_local = "hgdir"
        else:
            self._namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
            self._namespace_local = "dir"
            self._disable_load_style = True

        # Call Directory Plugin To Parse The Directory And Build The XML Representation
        super(db_mercurial_repository, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode, style_mode)

        # Check for uncommitted changes - only if at top level - the only place we'd display this
        if caller == "databrowse":
            uncommitted = [(item[0], item[2:]) for item in (subprocess.check_output(['/usr/bin/hg', '--cwd', fullpath, 'status'], stderr=open(os.devnull))).split('\n') if len(item)>2]
            if len(uncommitted) > 0:
                self._xml.set('uncommitted', '%s' % len(uncommitted))
                pass
            pass
        pass

    pass
