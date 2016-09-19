#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.   ##
## All rights reserved.                                                      ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##   1. Redistributions of source code must retain the above copyright       ##
##      notice, this list of conditions and the following disclaimer.        ##
##   2. Redistributions in binary form must reproduce the above copyright    ##
##      notice, this list of conditions and the following disclaimer in the  ##
##      documentation and/or other materials provided with the distribution. ##
##   3. Neither the name of the copyright holder nor the names of its        ##
##      contributors may be used to endorse or promote products derived from ##
##      this software without specific prior written permission.             ##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS       ##
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED ##
## TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A           ##
## PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER ##
## OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,  ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ## 
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## This material is based on work supported by the Air Force Research        ##
## Laboratory under Contract #FA8650-10-D-5210, Task Order #023 and          ##
## performed at Iowa State University.                                       ##
##                                                                           ##
## DISTRIBUTION A.  Approved for public release:  distribution unlimited;    ##
## 19 Aug 2016; 88ABW-2016-4051.                                             ##
###############################################################################
""" support/handler_support.py - Class to encapsulate handler plugin management """

import os
import os.path
import magic
import ConfigParser
import pkgutil
import databrowse.plugins
import re


class handler_support:
    """ Class to encapsulate handler plugin management """

    _handlers = {}
    _icondb = None
    _hiddenfiledb = None
    directoryplugins = {}
    directorystylesheets = []
    hiddenstylesheets = []

    def __init__(self, icondbpath, hiddenfiledbpath, directorypluginpath):
        """ Load up all of the handler plugins and icon database """
        # Reset Handler List
        self._handlers = {}
        # Parse Handlers
        #pluginlist = os.listdir(pluginpath)  # Removed 8/6/13 - Transition to Installed Modules
        pkgpath = os.path.dirname(databrowse.plugins.__file__)   # Added 8/6/13 - Transition to Installed Modules
        pluginlist = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]  # Added 8/6/13 - Transition to Installed Modules
        pluginlist.sort()
        for filename in pluginlist:
            if filename.startswith("db_"):
                modulename = filename
                functions = None
                try:
                    exec "import databrowse.plugins.%s.handlers" % modulename  # Added 8/6/13 - Transition to Installed Modules
                    exec "functions = dir(databrowse.plugins.%s.handlers)" % modulename  # Added 8/6/13 - Transition to Installed Modules
                    for function in functions:
                        if not function.startswith("dbh_"):    # Ignore all functions not starting with dbh_
                            pass
                        else:
                            exec "self._handlers['%s']=(databrowse.plugins.%s.handlers.%s)" % (function, modulename, function)  # Added 8/6/13 - Transition to Installed Modules
                            pass
                        pass
                    pass
                except:
                    pass
                pass
            pass

        # Load Icon Database
        self._icondb = None
        self._icondb = ConfigParser.ConfigParser()
        self._icondb.read(icondbpath)

        # Load Hidden File Database
        self._hiddenfiledb = None
        self._hiddenfiledb = ConfigParser.ConfigParser()
        self._hiddenfiledb.read(hiddenfiledbpath)

        # Get Directory Plugin list
        self.directoryplugins = {}
        self.directorystylesheets = []
        directorypluginconfig = ConfigParser.ConfigParser()
        directorypluginconfig.read(directorypluginpath)
        for item in directorypluginconfig.items("directory_plugins"):
            self.directoryplugins[item[0]] = item[1]
        for item in directorypluginconfig.items("directory_plugin_stylesheets"):
            self.directorystylesheets.append(item[0])
        for item in directorypluginconfig.items("hidden_plugin_stylesheets"):
            self.hiddenstylesheets.append(item[0])

        pass

    def GetHandler(self, fullpath):
        """ Return the handler given a full path """
        magicstore = magic.open(magic.MAGIC_MIME)
        magicstore.load()
        contenttype = magicstore.file(os.path.realpath(fullpath))   # real path to resolve symbolic links outside of dataroot
        extension = os.path.splitext(fullpath)[1][1:]
        if contenttype.startswith('application/xml'):
            (roottag, nsurl) = self.GetXMLRootAndNamespace(fullpath)
        else:
            (roottag, nsurl) = ('','')
        handler = []
        for function in sorted(self._handlers):
            temp = self._handlers[function](fullpath, contenttype, extension, roottag, nsurl)
            if temp:
                handler.append(temp)
            pass
        return handler

    def GetHandlerAndIcon(self, fullpath):
        """ Return the handler given a full path """
        magicstore = magic.open(magic.MAGIC_MIME)
        magicstore.load()
        contenttype = magicstore.file(os.path.realpath(fullpath))    # real path to resolve symbolic links outside of dataroot
        extension = os.path.splitext(fullpath)[1][1:]
        if contenttype.startswith('application/xml'):
            (roottag, nsurl) = self.GetXMLRootAndNamespace(fullpath)
        else:
            (roottag, nsurl) = ('','')
        handler = []
        for function in sorted(self._handlers):
            temp = self._handlers[function](fullpath, contenttype, extension, roottag, nsurl)
            if temp:
                handler.append(temp)
            pass
        try:
            iconname = self._icondb.get("Content-Type", contenttype.split(';')[0])
            pass
        except ConfigParser.NoOptionError:
            try:
                iconname = self._icondb.get("Extension", extension)
                pass
            except:
                iconname = "unknown.png"
                pass
            pass
        #print "Returning Handler Name:  %s" % handler
        return (handler, iconname)

    def GetIcon(self, contenttype, extension):
        """ Return the icon for a contenttype or extension """
        try:
            iconname = self._icondb.get("Content-Type", contenttype.split(';')[0])
            pass
        except ConfigParser.NoOptionError:
            try:
                iconname = self._icondb.get("Extension", extension)
                pass
            except:
                iconname = "unknown.png"
                pass
            pass

        return iconname

    def GetHiddenFileList(self):
        """ Return the list of files marked to be hidden """
        return (self._hiddenfiledb.items("Hidden"), self._hiddenfiledb.items("Shown"))

    def GetXMLRootAndNamespace(self, filename):
        """ Extract the root node name and namespace from an XML file without parsing the entire file """
        f = open(filename)
        flag = True
        while flag:
            while True:
                c = f.read(1)
                if c == '<':
                    buf = c
                    # Read Next Characters To Figure Out How To Proceed
                    c = f.read(1)
                    buf = buf + c
                    if c == '!':
                        # We Found A Comment - Warning!  This doesn't consider the possiblility of <![CDATA[]]>
                        while buf[-3:] != '-->':
                            c = f.read(1)
                            buf = buf + c
                            pass
                    elif c == '?':
                        # We Found a XML Declaration
                        while buf[-2:] != '?>':
                            c = f.read(1)
                            buf = buf + c
                            pass
                    else:
                        # We found the root tag... let's read in the rest
                        # This also doesn't consider > that may appear in quotes or other weird situations
                        while buf[-1] != '>':
                            c = f.read(1)
                            buf = buf + c
                            pass
                        flag = False
                        break
            pass
        
        # Let's parse the buffer
        fullroot = buf[1:buf.find(' ')]
        colonidx = fullroot.find(':')
        if colonidx < 0:
            roottag = fullroot
            localns = ''
        else:
            roottag = fullroot[colonidx+1:]
            localns = fullroot[:colonidx]
        if localns == '':
            t = re.search('xmlns=[\'"](.*?)[\'"]', buf)
            if t is not None:
                nsurl = t.groups()[0]
            else:
                nsurl = ''
        else:
            t = re.findall('xmlns:(.*?)=[\'"](.*?)[\'"]', buf)
            nsurl = [x[1] for x in t if x[0] == localns][0]
        return (roottag, nsurl)

    pass
