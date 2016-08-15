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
            t = re.findall('xmlns:(.*?)=[\'"](.*?)[\'"]', buf)
            nsurl = [x[1] for x in t if x[0] == localns][0]
        return (roottag, nsurl)

    pass
