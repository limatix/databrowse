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
## Portions of this software are adapted from hurry.filesize-0.9:            ##
## Copyright (C) 2009 Martijn Faassen, Startifact                            ##
## CHANGE LOG:                                                               ##
##     2013-03-30 - filesize.py condensed and adapted for use in the         ##
##                  ConvertUserFriendlySize function                         ##
###############################################################################
""" support/renderer_support.py - Encapsulation Class for Renderer Plugins """

from lxml import etree
from errno import EEXIST
from stat import *
import sys
import os
import string
import random
import copy
import fnmatch


class renderer_class(object):
    """ Renderer Plugin Support - Encapsulation Class for Renderer Plugins """

    _relpath = None
    _fullpath = None
    _web_support = None
    _handler_support = None
    _caller = None
    _handlers = None
    _content_mode = None
    _style_mode = None
    _dynamic_style = None
    _default_content_mode = "title"
    _default_style_mode = "list"
    _default_recursion_depth = 2
    _disable_load_style = False
    nsmap = {}

    class RendererException(Exception):
        pass

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers, content_mode=None, style_mode=None, recursion_depth=None):
        """ Default Initialization Function """

        # Set all of our argument variables
        #print "In RendererException.__init__".center(100, '=')
        #print "Setting Class Variables"
        self._relpath = relpath
        self._fullpath = fullpath
        self._web_support = web_support
        self._handler_support = handler_support
        self._caller = caller
        self._handlers = handlers
        if content_mode is None:
            self._content_mode = self._default_content_mode
            pass
        else:
            self._content_mode = content_mode
            pass
        if style_mode is None:
            self._style_mode = self._default_style_mode
            pass
        else:
            self._style_mode = style_mode
            pass
        if recursion_depth is None:
            self._recursion_depth = self._default_recursion_depth
            pass
        else:
            self._recursion_depth = recursion_depth
            pass

        #print "Class Variables Set - Here's a Summary"
        #print "self._relpath = " + repr(self._relpath)
        #print "self._fullpath = " + repr(self._fullpath)
        #print "self._web_support = " + repr(self._web_support)
        #print "self._web_support.req.filename = " + repr(self._web_support.req.filename)
        #print "self._web_support.req.dirname = " + repr(self._web_support.req.dirname)
        #print "self._web_support.req.unparsed_uri = " + repr(self._web_support.req.unparsed_uri)
        #print "self._handler_support = " + repr(self._handler_support)
        #print "self._caller = " + repr(self._caller)
        #print "self._content_mode = " + repr(self._content_mode)
        #print "self._style_mode = " + repr(self._style_mode)
        #print "self._recursion_depth = " + repr(self._recursion_depth)
        self.nsmap = {}
        self.nsmap['db'] = 'http://thermal.cnde.iastate.edu/databrowse'

        # Try to Load Style
        if not self._disable_load_style:
            #print "About to call self.loadStyle()"
            self.loadStyle()
            #print "About to call etree.register_namespace"
            self.nsmap[self._namespace_local] = self._namespace_uri
            #etree.register_namespace(self._namespace_local, self._namespace_uri)
            pass

        pass

    def getContent(self):
        ''' Default getContent '''
        return None

    def getSize(self, fullpath=None):
        """ Get Size of A File - Returns size of current file if none specified """

        if fullpath is None:
            fullpath = self._fullpath
            pass

        st = os.stat(fullpath)
        return st[ST_SIZE]

    def getUserFriendlySize(self, fullpath=None, mode="alternative", custom=None):
        return self.ConvertUserFriendlySize(self.getSize(fullpath), mode, custom)

    def ConvertUserFriendlySize(self, bytes, mode="alternative", custom=None, rounding=None):
        """Human-readable file size. """

        if custom is not None:
            formatstrings = custom
            pass
        elif mode == "traditional":
            formatstrings = [
                (1024 ** 5, 'P'),
                (1024 ** 4, 'T'),
                (1024 ** 3, 'G'),
                (1024 ** 2, 'M'),
                (1024 ** 1, 'K'),
                (1024 ** 0, 'B'),
            ]
        elif mode == "alternative":
            formatstrings = [
                (1024 ** 5, ' PB'),
                (1024 ** 4, ' TB'),
                (1024 ** 3, ' GB'),
                (1024 ** 2, ' MB'),
                (1024 ** 1, ' KB'),
                (1024 ** 0, (' byte', ' bytes')),
            ]
        elif mode == "bitrate":
            formatstrings = [
                (1024 ** 5, ' Pbps'),
                (1024 ** 4, ' Tbps'),
                (1024 ** 3, ' Gbps'),
                (1024 ** 2, ' Mbps'),
                (1024 ** 1, ' Kbps'),
                (1024 ** 0, ' bps'),
            ]
        elif mode == "frequency":
            formatstrings = [
                (1000 ** 5, ' PHz'),
                (1000 ** 4, ' THz'),
                (1000 ** 3, ' GHz'),
                (1000 ** 2, ' MHz'),
                (1000 ** 1, ' KHz'),
                (1000 ** 0, ' Hz'),
            ]
        elif mode == "time":
            formatstrings = [
                (4 ** 4, (' week', ' weeks')),
                (7 ** 3, (' day', ' days')),
                (24 ** 2, (' hr', ' hrs')),
                (60 ** 1, ' min'),
                (60 ** 0, ' sec'),
            ]
        elif mode == "verbose":
            formatstrings = [
                (1024 ** 5, (' petabyte', ' petabytes')),
                (1024 ** 4, (' terabyte', ' terabytes')),
                (1024 ** 3, (' gigabyte', ' gigabytes')),
                (1024 ** 2, (' megabyte', ' megabytes')),
                (1024 ** 1, (' kilobyte', ' kilobytes')),
                (1024 ** 0, (' byte', ' bytes')),
            ]
        elif mode == "iec":
            formatstrings = [
                (1024 ** 5, 'Pi'),
                (1024 ** 4, 'Ti'),
                (1024 ** 3, 'Gi'),
                (1024 ** 2, 'Mi'),
                (1024 ** 1, 'Ki'),
                (1024 ** 0, ''),
            ]
        elif mode == "si":
            formatstrings = [
                (1000 ** 5, 'P'),
                (1000 ** 4, 'T'),
                (1000 ** 3, 'G'),
                (1000 ** 2, 'M'),
                (1000 ** 1, 'K'),
                (1000 ** 0, 'B'),
            ]
        else:
            formatstrings = [
                (1024 ** 5, ' PB'),
                (1024 ** 4, ' TB'),
                (1024 ** 3, ' GB'),
                (1024 ** 2, ' MB'),
                (1024 ** 1, ' KB'),
                (1024 ** 0, (' byte', ' bytes')),
            ]

        for factor, suffix in formatstrings:
            if bytes >= factor:
                break
        amount = float(bytes/factor)
        if isinstance(suffix, tuple):
            singular, multiple = suffix
            if amount == 1:
                suffix = singular
            else:
                suffix = multiple
        if rounding is not None:
            amount = round(amount, rounding)
        return str(amount) + suffix

    def ConvertUserFriendlyPermissions(self, p):
        ts = {
            0140000: 'ssocket',
            0120000: 'llink',
            0100000: '-file',
            0060000: 'bblock',
            0040000: 'ddir',
            0020000: 'cchar',
            0010000: 'pfifo'
        }

        t = p & 0170000

        permstr = ts[t][0] if t in ts else 'u'
        permstr += 'r' if p & 0x0100 else '-'
        permstr += 'w' if p & 0x0080 else '-'
        permstr += 's' if p & 0x0800 else 'x' if p & 0x0040 else 'S' if p & 0x0800 else '-'
        permstr += 'r' if p & 0x0020 else '-'
        permstr += 'w' if p & 0x0010 else '-'
        permstr += 's' if p & 0x0400 else 'x' if p & 0x0008 else 'S' if p & 0x0400 else '-'
        permstr += 'r' if p & 0x0004 else '-'
        permstr += 'w' if p & 0x0002 else '-'
        permstr += 's' if p & 0x0200 else 'x' if p & 0x0001 else 'S' if p & 0x0200 else '-'

        return permstr

    def isRaw(self):
        #print "isRaw being called"
        if self._content_mode == "raw":
            return True
        else:
            return False

    def getStyleMode(self):
        #print "getStyleMode being called"
        return self._style_mode

    def getContentMode(self):
        #print "getContentMode being called"
        return self._content_mode

    def getURL(self, relpath, **kwargs):
        """ Return Full URL to a Relative Path """
        #print "getURL being called"
        # We need to tack in handler if handler is overridden
        if self._handlers[-1] != self.__class__.__name__ and "handler" not in kwargs:
            kwargs["handler"] = self.__class__.__name__
            pass
        elif "handler" in kwargs and kwargs["handler"] is None:
            del kwargs["handler"]
            pass
        # Add flag for hidden files if needed
        if "showhiddenfiles" in self._web_support.req.form and "showhiddenfiles" not in kwargs:
            kwargs["showhiddenfiles"] = ""
        elif "showhiddenfiles" in kwargs and kwargs["showhiddenfiles"] is None:
            del kwargs["showhiddenfiles"]
        # Build the URL
        if self._web_support.seo_urls is True:
            url = self._web_support.siteurl + relpath
            if len(kwargs) > 0:
                url = url + '?'
                z = 1
                pass
            for i in kwargs:
                if z == 1:
                    url = url + i + '=' + str(kwargs[i])
                    z = 2
                    pass
                else:
                    url = url + '&' + i + '=' + str(kwargs[i])
                    pass
                pass
            pass
        else:
            url = self._web_support.siteurl + '/?path=' + relpath
            for i in kwargs:
                url = url + '&' + i + '=' + str(kwargs[i])
                pass
            pass
        return url

    def getURLToParent(self, relpath, **kwargs):
        #print "getURLToParent being called"
        if relpath == "/":
            return self.getURL(relpath, **kwargs)
            pass
        else:
            relpath = os.path.abspath(relpath + '/../')
            return self.getURL(relpath, **kwargs)
            pass
        pass

    def getDirectoryList(self, fullpath, sort=None, order="asc"):
        """ Build a Sorted List of Files with Appropriate Files Removed """
        #print "getDirectoryList being called"
        (hiddenlist, shownlist) = self._handler_support.GetHiddenFileList()
        reallist = os.listdir(fullpath)
        if "showhiddenfiles" in self._web_support.req.form:
            returnlist = reallist
        else:
            removelist = copy.copy(reallist)
            for item in hiddenlist:
                removelist = [n for n in removelist if not fnmatch.fnmatch(n, item[1])]
                pass
            addlist = []
            for item in shownlist:
                addlist = [n for n in reallist if fnmatch.fnmatch(n, item[1])]
                pass
            returnlist = list(set(removelist + addlist))
        exec "returnlist.sort(%s%s)" % ("reverse=True" if order == "desc" else "reverse=False", ",key=%s" % sort if sort is not None else ",key=str.lower")

        returndirlist = [f for f in returnlist if os.path.isdir(os.path.join(fullpath, f))]
        returnfilelist = [f for f in returnlist if os.path.isfile(os.path.join(fullpath, f))]
        returnlist = returndirlist
        returnlist.extend(returnfilelist)

        return returnlist

        pass

    class CacheFileHandler(file):
        """ Overrride File Close Class to Reassign Timestamp """

        timestamp = None

        def __init__(self, filename, mode='r', timestamp=None):
            self.timestamp = timestamp
            super(renderer_class.CacheFileHandler, self).__init__(filename, mode)

        def close(self):
            super(renderer_class.CacheFileHandler, self).close()
            if self.mode not in ['r', 'rb'] and self.timestamp is not None:
                st = os.stat(self.name)
                atime = st[ST_ATIME]
                os.utime(self.name, (atime, self.timestamp))
            else:
                pass

        pass

    def getCacheFileHandler(self, mode='r', tag=None, extension=None):
        """ Return File Handler For Cache File """
        filename = self.getCacheFileName(tag, extension)
        st = os.stat(self._fullpath)
        timestamp = st[ST_MTIME]
        if mode not in ['r', 'rb']:
            self.PrepareCacheDir()
            if not os.access(filename, os.W_OK) and os.path.exists(filename):
                raise self.RendererException("Unable to Open Cache File for Writing: " + filename)
        else:
            if not os.access(filename, os.R_OK):
                raise self.RendererException("Unable to Open Cache File for Reading: " + filename)
        return self.CacheFileHandler(filename, mode, timestamp)

    def PrepareCacheDir(self):
        cachedirname = self.getCacheDirName()
        if not os.path.exists(cachedirname):
            try:
                os.makedirs(cachedirname)
            except OSError as err:
                if err.errno == EEXIST:  # Handle the Race Condition
                    pass
                else:
                    raise
        pass

    def CacheFileExists(self, tag=None, extension=None):
        """ Return Boolean after Verifying the Existance of a Cache File """
        if "ignorecache" in self._web_support.req.form:
            return False
        filename = self.getCacheFileName(tag, extension)
        if os.access(filename, os.R_OK) and os.path.exists(filename):
            basestat = os.stat(self._fullpath)
            cachestat = os.stat(filename)
            if basestat[ST_MTIME] != cachestat[ST_MTIME]:
                return False
            else:
                return True
        else:
            return False

    def getCacheDirName(self):
        return os.path.abspath(os.path.dirname(self._fullpath) + "/.databrowse/cache/" + self.__class__.__name__ + "/")

    def getCacheFileName(self, tag=None, extension=None):
        """ Get the Name of a Cache File Given a Tag and Extension """
        basefilename = os.path.splitext(os.path.basename(self._fullpath))
        basedirname = self.getCacheDirName()
        filename = basefilename[0]
        if tag is not None:
            filename = filename + "_" + tag
        if extension is not None:
            filename = filename + "." + extension
        else:
            filename = filename + basefilename[1]
        return os.path.join(basedirname, filename)

    def loadMenu(self):
        """ Load Menu Items for all current handlers """
        newmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar')
        isDirectory = os.path.isdir(self._fullpath)
        for handler in reversed(self._handlers):
            dirlist = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.abspath(os.path.dirname(sys.modules['databrowse.plugins.' + handler].__file__) + '/')) if item.lower().startswith("dbs_")]
            additionalitems = []
            if isDirectory:
                if os.path.exists(os.path.join(self._fullpath, '.databrowse', 'stylesheets', handler)):
                    additionalitems = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.join(self._fullpath, '.databrowse', 'stylesheets', handler)) if item.lower().startswith("dbs_")]
            else:
                if os.path.exists(os.path.join(os.path.dirname(self._fullpath), '.databrowse', 'stylesheets', handler)):
                    additionalitems = [os.path.splitext(item)[0][4:] for item in os.listdir(os.path.join(os.path.dirname(self._fullpath), '.databrowse', 'stylesheets', handler)) if item.lower().startswith("dbs_")]
            dirlist = dirlist + additionalitems
            navelem = etree.SubElement(newmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a")
            title.text = " ".join([i[0].title()+i[1:] for i in handler[3:].split("_")])
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true")
            for item in dirlist:
                if item not in self._handler_support.hiddenstylesheets:
                    if not isDirectory and item not in self._handler_support.directorystylesheets:
                        link = self.getURL(self._relpath, handler=handler, style_mode=item)
                        if self._style_mode == item and self.__class__.__name__ == handler:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
                        else:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
                        menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
                        menuitem.text = " ".join([i[0].title()+i[1:] for i in item.split("_")])
                        pass
                    elif isDirectory:
                        link = self.getURL(self._relpath, handler=handler, style_mode=item)
                        if self._style_mode == item and self.__class__.__name__ == handler:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
                        else:
                            itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
                        menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
                        menuitem.text = " ".join([i[0].title()+i[1:] for i in item.split("_")])
                        pass
                    else:
                        pass
            pass
        self._web_support.menu.AddMenu(newmenu)
        pass

    def loadStyle(self):
        """ Safe Function Wrapper To Prevent Errors When Stylesheet Doesn't Exist """
        #print "loadStyle being called"
        try:
            #print "About to call loadStyleFunction"
            self.loadStyleFunction()
            pass
        except self.RendererException:
            #print "loadStyleFunction failed with error"
            if self._caller in self._handler_support.directoryplugins:
                pass
            elif self._style_mode == self._default_style_mode:
                raise
            else:
                self._style_mode = self._default_style_mode
                self.loadStyleFunction()
                pass
        pass

    def loadStyleFunction(self):
        """ Look In Standard Places For the Appropriate Static Stylesheet """

        # Get Variables Containing Search Locations Ready
        #print "In loadStyleFunction"
        #print "Path = " + self._fullpath
        #print "Plugin = " + self.__class__.__name__
        custompath = os.path.abspath((self._fullpath if os.path.isdir(self._fullpath) else os.path.dirname(self._fullpath)) +
                                     '/.databrowse/stylesheets/' + self.__class__.__name__ + '/dbs_' + self._style_mode + '.xml')
        defaultpath = os.path.abspath(os.path.dirname(sys.modules['databrowse.plugins.' + self.__class__.__name__].__file__) + '/dbs_' + self._style_mode + '.xml')
        #print "Custom Search Path = " + custompath
        #print "Default Search Path = " + defaultpath

        # Look for Custom Stylesheets in a .databrowse folder relative to the current path
        filename = custompath if os.path.exists(custompath) else None
        #print "Looking For Custom File === Filename is now " + repr(filename)

        # If we find one, see if its overriding the standard stylesheet and set a flag to remind us later
        override = False
        if filename is not None:
            override = True if (os.path.exists(defaultpath) or hasattr(self, '_style_' + self._style_mode)) else False
            pass
        #print "Checking for Default Stylesheets === Override is now " + repr(override)

        # Let's first check if we have already loaded the standard stylesheets
        if filename is None:
            #print "Filename is still empty so let's see if we have loaded the default already"
            if self._web_support.style.IsStyleLoaded(self._namespace_uri) and override != True:
                #print "We have loaded already === IsStyleLoaded is %s and override is %s" % (repr(self._web_support.style.IsStyleLoaded(self._namespace_uri)), repr(override))
                return
            else:
                # If not, let's look for normal stylesheets
                #print "Not loaded already === IsStyleLoaded is %s and override is %s" % (repr(self._web_support.style.IsStyleLoaded(self._namespace_uri)), repr(override))
                filename = defaultpath if os.path.exists(defaultpath) else None
                pass

        # Let's check for a stylesheet in the current file
        if filename is None:
            #print "Filename is still none = looking for variable"
            if hasattr(self, '_style_' + self._style_mode):
                stylestring = getattr(self, '_style_' + self._style_mode)
                pass
            else:
                # Unable to Find Stylesheet Anywhere - Return Error
                #print "Unable to find stylesheet"
                raise self.RendererException("Unable To Locate Stylesheet for Style Mode %s in %s" % (self._style_mode, self.__class__.__name__))
        else:
            # Lets load up whatever stylesheet we found
            f = open(filename, 'r')
            stylestring = f.read()
            f.close()
            pass

        #print "Stylesheet Loaded Successfully:"
        #print stylestring

        # If we set the flag earlier, we need to change the namespace
        if override is True:
            #print "Override is True = Lets Modify Our Stylesheet"
            randomid = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
            #print "Random ID is " + randomid
            newnamespace = self._namespace_uri + randomid
            newlocalns = self._namespace_local + randomid
            #print "New namespace is " + newnamespace
            newnamedtemplates = self.__class__.__name__ + '-' + randomid + '-'
            #print "Named templates are now prefixed " + newnamedtemplates
            stylestring = stylestring.replace(self._namespace_uri, newnamespace)
            stylestring = stylestring.replace(self._namespace_local + ":", newlocalns + ":")
            stylestring = stylestring.replace("xmlns:" + self._namespace_local, "xmlns:" + newlocalns)
            #print "Namespace Changed:"
            #print stylestring
            stylestring = stylestring.replace(self.__class__.__name__ + '-', newnamedtemplates)
            #print "Named Templates Updated:"
            #print stylestring
            self._namespace_uri = newnamespace
            self._namespace_local = newlocalns
            pass

        #print "Adding Style"
        self._web_support.style.AddStyle(self._namespace_uri, stylestring)

        pass
