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
## Portions of this software are adapted from hurry.filesize-0.9:            ##
## Copyright (C) 2009 Martijn Faassen, Startifact                            ##
## CHANGE LOG:                                                               ##
##     2013-03-30 - filesize.py condensed and adapted for use in the         ##
##                  ConvertUserFriendlySize function                         ##
###############################################################################
""" support/renderer_support.py - Encapsulation Class for Renderer Plugins """

from lxml import etree
from stat import *
import os.path
import string
import random
import os
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

        # Try to Load Style
        if not self._disable_load_style:
            #print "About to call self.loadStyle()"
            self.loadStyle()
            #print "About to call etree.register_namespace"
            etree.register_namespace(self._namespace_local, self._namespace_uri)
            pass

        pass

    def getSize(self, fullpath=None):
        """ Get Size of A File - Returns size of current file if none specified """

        if fullpath is None:
            fullpath = self._fullpath
            pass

        st = os.stat(fullpath)
        return st[ST_SIZE]

    def getUserFriendlySize(self, fullpath=None, mode="alternative", custom=None):
        return self.ConvertUserFriendlySize(self.getSize(fullpath), mode, custom)

    def ConvertUserFriendlySize(self, bytes, mode="alternative", custom=None):
        """Human-readable file size. """

        if custom is not None:
            formatstrings = custom
            pass
        elif mode is "traditional":
            formatstrings = [
                (1024 ** 5, 'P'),
                (1024 ** 4, 'T'),
                (1024 ** 3, 'G'),
                (1024 ** 2, 'M'),
                (1024 ** 1, 'K'),
                (1024 ** 0, 'B'),
            ]
        elif mode is "alternative":
            formatstrings = [
                (1024 ** 5, ' PB'),
                (1024 ** 4, ' TB'),
                (1024 ** 3, ' GB'),
                (1024 ** 2, ' MB'),
                (1024 ** 1, ' KB'),
                (1024 ** 0, (' byte', ' bytes')),
            ]
        elif mode is "verbose":
            formatstrings = [
                (1024 ** 5, (' petabyte', ' petabytes')),
                (1024 ** 4, (' terabyte', ' terabytes')),
                (1024 ** 3, (' gigabyte', ' gigabytes')),
                (1024 ** 2, (' megabyte', ' megabytes')),
                (1024 ** 1, (' kilobyte', ' kilobytes')),
                (1024 ** 0, (' byte', ' bytes')),
            ]
        elif mode is "iec":
            formatstrings = [
                (1024 ** 5, 'Pi'),
                (1024 ** 4, 'Ti'),
                (1024 ** 3, 'Gi'),
                (1024 ** 2, 'Mi'),
                (1024 ** 1, 'Ki'),
                (1024 ** 0, ''),
            ]
        elif mode is "si":
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
        if self._content_mode is "raw":
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
        if self._handlers[-1] is not self.__class__.__name__ and "handler" not in kwargs:
            kwargs["handler"] = self.__class__.__name__
            pass
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
        removelist = copy.copy(reallist)
        for item in hiddenlist:
            removelist = [n for n in removelist if not fnmatch.fnmatch(n, item[1])]
            pass
        addlist = []
        for item in shownlist:
            addlist = [n for n in reallist if fnmatch.fnmatch(n, item[1])]
            pass
        returnlist = list(set(removelist + addlist))
        exec "returnlist.sort(%s%s)" % ("reverse=True" if order is "desc" else "reverse=False", ",key=%s" % sort if sort is not None else ",key=str.lower")
        return returnlist

        pass

    def loadMenu(self):
        """ Load Menu Items for all current handlers """
        for handler in reversed(self._handlers):
            dirlist = [os.path.splitext(item)[0] for item in os.listdir(os.path.abspath(self._web_support.rendererpath + '/stylesheets/' + handler + '/')) if item.lower().endswith(".xml")]
            newmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar')
            navelem = etree.SubElement(newmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a")
            title.text = handler[4:].title().replace("_", " ")
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true")
            for item in dirlist:
                link = self.getURL(self._relpath, handler=handler, style_mode=item)
                if self._style_mode == item and self.__class__.__name__ == handler:
                    itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem", selected="true")
                else:
                    itemelem = etree.SubElement(navitems, "{http://thermal.cnde.iastate.edu/databrowse}navelem")
                menuitem = etree.SubElement(itemelem, "{http://www.w3.org/1999/xhtml}a", href=link)
                menuitem.text = item.title().replace("_", " ")
                pass
            self._web_support.menu.AddMenu(newmenu)
            pass
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
            if self._style_mode == self._default_style_mode:
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
        custompath = os.path.abspath((self._fullpath if os.path.isdir(self._fullpath) else os.path.dirname(self._fullpath)) + \
            '/.databrowse/stylesheets/' + self.__class__.__name__ + '/' + self._style_mode + '.xml')
        defaultpath = os.path.abspath(self._web_support.rendererpath + '/stylesheets/' + self.__class__.__name__ + '/' + self._style_mode + '.xml')
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
            if self._web_support.style.IsStyleLoaded(self._namespace_uri) and override is not True:
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
                raise self.RendererException("Unable To Locate Stylesheet")
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
