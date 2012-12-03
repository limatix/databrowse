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
""" support/handler_support.py - Class to encapsulate handler plugin management """

import os
import os.path
import sys
import magic


if not hasattr(magic,"Magic"): 
    # old magic api
    magicstore = magic.open(magic.MAGIC_NONE)
    magicstore.load()


class handler_support:
    """ Class to encapsulate handler plugin management """

    _handlers = []

    def __init__(self, handlerpath):
        """ Load up all of the handler plugins """
        handlerlist = os.listdir(handlerpath)
        handlerlist.sort()
        sys.path.append(handlerpath)
        for filename in handlerlist:
            if filename.endswith(".py"):
                modulename = filename[:-3]
                functions = None
                try:
                    exec "import %s" % modulename
                    exec "functions = dir(%s)" % modulename
                    for function in functions:
                        if function.startswith("_"):
                            pass
                        else:
                            exec "self._handlers.append(%s.%s)" % (modulename, function)
                            pass
                        pass
                    pass
                except:
                    pass
                pass
            pass

        pass

    def GetHandler(self, fullpath):
        """ Return the handler given a full path """
        if hasattr(magic,"Magic"): 
            # new python-magic API
            mime = magic.Magic(mime=True)
            contenttype = mime.from_file(fullpath)
            pass
        else :
            contenttype =  magicstore.file(fullpath)            

            pass

        #logf=file("/tmp/junk","w")
        #logf.write("fullpath=%s contenttype=%s\n" % (fullpath,contenttype))
        #logf.close()

        extension = os.path.splitext(fullpath)[1][1:]
        handler = False
        for function in self._handlers:
            temp = function(fullpath, contenttype, extension)
            handler = temp if temp else handler
            pass
        return handler

    pass
