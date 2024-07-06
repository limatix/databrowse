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
##                                                                           ##
## This material is based on work supported by NASA under Contract           ##
## NNX16CL31C and performed by Iowa State University as a subcontractor      ##
## to TRI Austin.                                                            ##
##                                                                           ##
## Approved for public release by TRI Austin: distribution unlimited;        ##
## 01 June 2018; by Carl W. Magnuson (NDE Division Director).                ##
###############################################################################
""" plugins/renderers/db_directory.py - Basic Output for Any Folder """

import sys
import os
import os.path
import random
import string
from difflib import get_close_matches
if sys.version_info >= (3, 0):
    import urllib.request as urllib 
else:
    import urllib
    pass
from importlib import import_module
from lxml import etree
from lxml import objectify
from databrowse.support.renderer_support import renderer_class


class db_directory(renderer_class):
    """ Default Folder Renderer - Basic Output for Any Folder """

    _xml = None
    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/dir"
    _namespace_local = "dir"
    _default_content_mode = "title"
    _default_style_mode = "list"
    _default_recursion_depth = 1

    def specimen_search(self, rootpath, fileexts):
        filelist = []
        dirlist = self.getDirectoryList(rootpath)
        for item in dirlist:
            itemfullpath = os.path.join(rootpath, item).replace("\\", "/")
            if not os.path.isdir(itemfullpath):
                ext = os.path.splitext(itemfullpath)[1]
                if ext in fileexts:
                    filelist.append(itemfullpath)
        return filelist

    def recursiveloop(self, dirname, chxlist):
        chxpath = os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + dirname)
        if os.path.exists(chxpath):
            chxdirlist = self.getDirectoryList(chxpath)
            for item in chxdirlist:
                if item.endswith(".chx"):
                    itemurl = self.getURL(
                        os.path.normpath(self._web_support.checklistpath + '/' + dirname + '/' + item).replace("\\", "/"),
                        handler=None)
                    etree.SubElement(chxlist, '{%s}chxfile' % (self._namespace_uri), nsmap=self.nsmap, url=itemurl, name=item)
                    pass
                if os.path.isdir(os.path.abspath(
                        self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + dirname + '/' + item)):
                    if len([x for x in self.getDirectoryList(os.path.abspath(
                            self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + os.path.normpath(
                                    dirname + '/' + item))) if (x.endswith('.chx') or os.path.isdir(os.path.abspath(
                            self._web_support.dataroot + '/' + self._web_support.checklistpath + '/' + os.path.normpath(
                                    dirname + '/' + item + '/' + x))))]) > 0:
                        subchxlist = etree.SubElement(chxlist, '{%s}chxdir' % (self._namespace_uri), nsmap=self.nsmap,
                                                      url=self.getURL(os.path.normpath(
                                                          self._web_support.checklistpath + '/' + dirname + '/' + item),
                                                                      handler=None), name=item)
                        self.recursiveloop(os.path.normpath(dirname + '/' + item), subchxlist)
                    pass

    def __init__(self, relpath, fullpath, web_support, handler_support, caller, handlers,
                 content_mode=_default_content_mode, style_mode=_default_style_mode,
                 recursion_depth=_default_recursion_depth):
        """ Load all of the values provided by initialization """
        super(db_directory, self).__init__(relpath, fullpath, web_support, handler_support, caller, handlers, content_mode,
                                           style_mode)
        if caller == "databrowse":
            uphref = self.getURLToParent(self._relpath)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, nsmap=self.nsmap, path=self._fullpath,
                                    relpath=self._relpath, dataroot=self._web_support.dataroot, uphref=uphref,
                                    resurl=self._web_support.resurl, siteurl=self._web_support.siteurl, root="True")
            topmenu = etree.Element('{http://thermal.cnde.iastate.edu/databrowse}navbar', nsmap=self.nsmap,
                                    xmlns="http://www.w3.org/1999/xhtml")
            navelem = etree.SubElement(topmenu, "{http://thermal.cnde.iastate.edu/databrowse}navelem", nsmap=self.nsmap)
            title = etree.SubElement(navelem, "{http://www.w3.org/1999/xhtml}a", nsmap=self.nsmap)
            title.text = "View Options"
            navitems = etree.SubElement(navelem, "{http://thermal.cnde.iastate.edu/databrowse}navdir", alwaysopen="true",
                                        nsmap=self.nsmap)
            if not "showhiddenfiles" in self._web_support.req.form:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem',
                                            nsmap=self.nsmap)
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a',
                                            href=self.getURL(self._relpath, showhiddenfiles=""), nsmap=self.nsmap)
                menulink.text = "Show Hidden Files"
            else:
                menuitem = etree.SubElement(navitems, '{http://thermal.cnde.iastate.edu/databrowse}navelem',
                                            nsmap=self.nsmap)
                menulink = etree.SubElement(menuitem, '{http://www.w3.org/1999/xhtml}a',
                                            href=self.getURL(self._relpath, showhiddenfiles=None), nsmap=self.nsmap)
                menulink.text = "Hide Hidden Files"
            self._web_support.menu.AddMenu(topmenu)
            pass
        else:
            link = self.getURL(self._relpath, handler=None)
            xmlroot = etree.Element('{%s}dir' % self._namespace_uri, nsmap=self.nsmap, name=os.path.basename(self._relpath),
                                    path=self._fullpath, relpath=self._relpath, dataroot=self._web_support.dataroot,
                                    href=link, resurl=self._web_support.resurl)
            pass
        if "ajax" in self._web_support.req.form:
            xmlroot.set("ajaxreq", "True")
            pass
        if recursion_depth != 0:
            caller = self.__class__.__name__
            dirlist = self.getDirectoryList(self._fullpath)
            for item in dirlist:
                itemrelpath = os.path.join(self._relpath, item).replace("\\", "/")
                itemfullpath = os.path.join(self._fullpath, item).replace("\\", "/")
                (handlers, icon) = self._handler_support.GetHandlerAndIcon(itemfullpath)
                handler = handlers[-1]
                if handler in self._handler_support.directoryplugins:
                    icon = self._handler_support.directoryplugins[handler]
                if handler in self._handler_support.directoryplugins:
                    renderer = self.__class__(itemrelpath, itemfullpath, self._web_support, self._handler_support, caller,
                                              handlers, content_mode=content_mode, style_mode=style_mode,
                                              recursion_depth=recursion_depth - 1)
                else:
                    renderer = getattr(import_module("databrowse.plugins.%s.%s" % (handler, handler)), handler)(
                        itemrelpath, 
                        itemfullpath,
                        self._web_support, 
                        self._handler_support, 
                        caller, 
                        handlers,
                        content_mode=content_mode,
                        style_mode=style_mode,
                        recursion_depth=recursion_depth - 1
                    )
                content = renderer.getContent()
                if os.path.islink(itemfullpath):
                    overlay = "link"
                elif not os.access(itemfullpath, os.W_OK):
                    overlay = "readonly"
                elif not os.access(itemfullpath, os.R_OK):
                    overlay = "unreadable"
                else:
                    overlay = "none"
                if content is not None and content.tag.startswith("{%s}" % self._namespace_uri):
                    content.set('icon', icon)
                    content.set('overlay', overlay)
                    xmlroot.append(content)
                else:
                    xmlchild = etree.SubElement(xmlroot, '{%s}file' % (self._namespace_uri), nsmap=self.nsmap,
                                                fullpath=itemfullpath, relpath=itemrelpath,
                                                basename=os.path.basename(itemfullpath),
                                                link=self.getURL(itemrelpath, handler=None), icon=icon, overlay=overlay)
                    if content is not None:
                        xmlchild.append(content)
                        pass
                pass
            pass
        else:
            # ajax url and what not
            xmlroot.set("ajax", "True")
            xmlroot.set("ajaxurl",
                        self.getURL(self._relpath, recursion_depth=1, nopagestyle=True, content_mode=self._content_mode,
                                    style_mode=self._style_mode))
            pass
        if self._caller == "databrowse" and self._web_support.checklistpath is not None:
            chxlist = etree.SubElement(xmlroot, '{%s}chxlist' % (self._namespace_uri), nsmap=self.nsmap)
            # chxdirlist = self.getDirectoryList(os.path.abspath(self._web_support.dataroot + '/' + self._web_support.checklistpath))

            self.recursiveloop('/', chxlist)

            # for item in [item for item in chxdirlist if item.endswith(".chx")]:
            #    itemurl = self.getURL(os.path.join(self._web_support.checklistpath, item), handler=None)
            #    etree.SubElement(chxlist, '{%s}chxfile' % (self._namespace_uri), nsmap=self.nsmap, url=itemurl, name=item)
            #    pass
            pass
        if self._style_mode in ['fusion']:
            if self._caller == "databrowse":
                sens = 0.85
                try:
                    search_terms = self._web_support.req.form['search'].value
                except KeyError:
                    search_terms = None

                if not self.CacheFileExists(tag='searches', extension='txt'):
                    ft = self.getCacheFileHandler('wb', "searches", "txt")
                    ft.close()

                ft = self.getCacheFileHandler('rb', "searches", "txt")
                prevsearches = ft.read().split(",")
                ft.close()

                if prevsearches == ['']:
                    prevsearches = []

                if search_terms:
                    if search_terms in prevsearches:
                        if prevsearches[-1] != search_terms:
                            prevsearches.remove(search_terms)
                            prevsearches.append(search_terms)
                    else:
                        if search_terms:
                            prevsearches.append(search_terms)

                if len(prevsearches) > 5:
                    prevsearches = prevsearches[-5:]

                ft = self.getCacheFileHandler('wb', "searches", "txt")
                ft.write(",".join(prevsearches))
                ft.close()

                p = etree.XMLParser(huge_tree=True, remove_blank_text=True)
                specimen_file_types = ['.xlg', '.xlp']

                filelist = self.specimen_search(self._fullpath, specimen_file_types)
                if len(filelist) > 0:
                    xmllogs = etree.Element('{%s}logs' % self._namespace_uri, nsmap=self.nsmap)

                    for specfile in filelist:
                        specxml = etree.parse(specfile, parser=p).getroot()
                        self.nsmap.update(dict(set(specxml.xpath('//namespace::*'))))
                        xmllogs.append(specxml)

                    specimens = xmllogs.xpath('//dc:specimen[not(preceding::dc:specimen/text() = text())]/text()',
                                              namespaces=self.nsmap)

                    xmlsearch = etree.Element('{%s}search' % self._namespace_uri,
                                              resurl=self._web_support.resurl,
                                              path=self.getURL(self._relpath, style_mode="fusion"),
                                              nsmap=self.nsmap)

                    xmlspecimens = etree.SubElement(xmlsearch, "{%s}specimens" % self._namespace_uri, nsmap=self.nsmap)

                    xmlsearchterm = etree.SubElement(xmlspecimens, '{%s}searchterm' % self._namespace_uri, nsmap=self.nsmap)
                    xmlsearchterm.text = search_terms

                    if prevsearches:
                        xmlprevsearchterms = etree.SubElement(xmlspecimens, '{%s}prevsearches' % self._namespace_uri, nsmap=self.nsmap)
                        for searchterm in list(reversed(prevsearches)):
                            xmlprevsearchterm = etree.SubElement(xmlprevsearchterms, '{%s}prevsearch' % self._namespace_uri, nsmap=self.nsmap)
                            xmlprevsearchterm.text = searchterm

                    for specimen in specimens:
                        xmlspecimen = etree.SubElement(xmlspecimens, '{%s}specimen' % self._namespace_uri, nsmap=self.nsmap)
                        xmlspecimen.text = specimen

                    xmlcontent = etree.SubElement(xmlsearch, "{%s}content" % self._namespace_uri, nsmap=self.nsmap)
                    if search_terms:
                        all_elements = list(xmllogs.iter())[1:]
                        for search_term in search_terms.split(" "):
                            for child in xmlcontent:
                                xmlcontent.remove(child)

                            for element in all_elements:
                                res = []

                                tag = element.tag

                                attributes = element.attrib
                                attrib_keys = attributes.keys()
                                attrib_values = attributes.values()

                                text = element.text

                                if tag:
                                    res += get_close_matches(search_term, [tag.split("}")[1]], cutoff=sens, n=1)

                                if attrib_keys:
                                    res += get_close_matches(search_term, attrib_keys, cutoff=sens, n=1)

                                if attrib_values:
                                    res += get_close_matches(search_term, attrib_values, cutoff=sens, n=1)

                                if text:
                                    res += get_close_matches(search_term, text.split(" "), cutoff=sens, n=1)

                                res = list(set(res))

                                if res:
                                    parent = element
                                    while True:
                                        if parent.text and parent != xmllogs:
                                            parent = parent.getparent()
                                        else:
                                            break

                                    if not xmlcontent.xpath("//dir:_[@title = '%s']" % parent.tag.split("}")[1],
                                                            namespaces=self.nsmap):
                                        grandparent = etree.SubElement(xmlcontent, "{%s}_" % self._namespace_uri, nsmap=self.nsmap)
                                        grandparent.attrib['title'] = parent.tag.split("}")[1]

                                    grandparent = xmlcontent.xpath("//dir:_[@title = '%s']" % parent.tag.split("}")[1],
                                                                   namespaces=self.nsmap)[0]
                                    if parent not in grandparent:
                                        grandparent.append(parent)
                            all_elements = list(xmlcontent.iter())[1:]
                    xmlroot = xmlsearch
                    fusions = xmlroot.xpath('//dc:fusion', namespaces={'dc': 'http://limatix.org/datacollect'})
                    for fusion in fusions:
                        fusionmodellist = fusion.xpath('dc:greensinversion_3d', namespaces={'dc': 'http://limatix.org/datacollect'})
                        for model in fusionmodellist:
                            try:
                                xlink = model.get('{http://www.w3.org/1999/xlink}href')
                                if xlink:
                                    path = os.path.join(self._fullpath, xlink)
                                    if path.startswith(os.path.normpath(self._web_support.dataroot)) and os.access(path, os.R_OK) and os.path.exists(path):
                                        relpath = path.replace(self._web_support.dataroot, '')
                                        url = self.getURL(relpath, content_mode="raw", model="true").replace("\\", "/")
                                        model.attrib['url'] = url
                            except Exception:
                                pass
                    xlinks = xmlroot.xpath('//*[@xlink:href]', namespaces={'xlink': 'http://www.w3.org/1999/xlink'})
                    for xlink in xlinks:
                        path = os.path.join(self._fullpath, xlink.attrib['{http://www.w3.org/1999/xlink}href'])
                        if path.startswith(os.path.normpath(self._web_support.dataroot)) and os.access(path, os.R_OK) and os.path.exists(path):
                            relpath = path.replace(self._web_support.dataroot, '')
                            url = self.getURL(relpath).replace("\\", "/")
                            xlink.attrib['{http://www.w3.org/1999/xlink}href'] = url
                # print(etree.tostring(xmlroot, pretty_print=True))
        self._xml = xmlroot
        pass

    def getContent(self):
        if self._content_mode == "detailed" or self._content_mode == "summary" or self._content_mode == "title":
            return self._xml
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

    def loadStyleFunction(self):
        """ Override Load Style Function to Replace URL """

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

        stylestring = stylestring.replace('/usr/local/limatix-qautils/checklist/datacollect2.xsl', urllib.pathname2url(os.path.join(self._web_support.limatix_qautils, "checklist/datacollect2.xsl")).replace("///", ""))

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


pass
