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
""" plugins/renderers/db_git.py - Basic Output for Any Folder """
import pdb

import os
import os.path
import git
import magic
import datetime
from shutil import copyfile
from lxml import etree
from databrowse.support.renderer_support import renderer_class


class db_git(renderer_class):
    """ GIT Repository Renderer """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/git"
    _namespace_local = "git"
    _default_content_mode = "full"
    _default_style_mode = "repository"
    _default_recursion_depth = 1

    def recursive_search(self, xmlcontents, rootpath, root="", relroot=""):
        dirlist = self.getDirectoryList(rootpath)
        for item in dirlist:
            itemfullpath = os.path.join(rootpath, item).replace("\\", "/")
            itemrelpath = os.path.join(relroot, item).replace("\\", "/")
            if os.path.isdir(itemfullpath):
                xmldir = etree.SubElement(xmlcontents, "dir", nsmap=self.nsmap)
                xmldir.attrib["name"] = os.path.basename(itemfullpath)
                xmldir.attrib['url'] = self.getURL(itemrelpath)
                self.recursive_search(xmldir, itemfullpath,
                                      root=os.path.join(root, os.path.basename(itemfullpath)).replace("\\", "/"),
                                      relroot=os.path.join(relroot, os.path.basename(itemrelpath)).replace("\\", "/"))
            else:
                xmlitem = etree.SubElement(xmlcontents, "item", nsmap=self.nsmap)
                xmlitem.text = item

                itemsubpath = os.path.join(root, item).replace("\\", "/")

                try:
                    magicstore = magic.open(magic.MAGIC_MIME)
                    magicstore.load()
                    contenttype = magicstore.file(
                        os.path.realpath(itemfullpath))  # real path to resolve symbolic links outside of dataroot
                except AttributeError:
                    contenttype = magic.from_file(os.path.realpath(itemfullpath), mime=True)
                if contenttype is None:
                    contenttype = "text/plain"

                extension = os.path.splitext(itemfullpath)[1][1:]
                icon = self._handler_support.GetIcon(contenttype, extension)

                xmlitem.attrib['icon'] = icon
                xmlitem.attrib['url'] = self.getURL(itemrelpath)

                if itemsubpath in self.changedfiles:
                    xmlitem.attrib['changed'] = "True"
                if itemsubpath in self.untracked:
                    xmlitem.attrib['untracked'] = "True"

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self.isGit():
                repo_path = self._fullpath.split('.git')[0]

                owd = os.getcwd()
                os.chdir(repo_path)
                g = git.Git()
                g.execute(["git", "update-server-info"])
                update_path = os.path.join(repo_path, ".git", "hooks", "post-update")
                if not os.path.exists(update_path):
                    copyfile(update_path+".sample", update_path)
                os.chdir(owd)

                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Type'] = "text/plain"
                self._web_support.req.response_headers['Content-Length'] = str(os.fstat(f.fileno()).st_size)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(f.name)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            elif self._content_mode == "full":
                repo = git.Repo(self._fullpath)

                self.changedfiles = [item.a_path for item in repo.index.diff(None)]

                if "branch" in self._web_support.req.form:
                    repo.git.checkout(self._web_support.req.form["branch"].value)

                repo = git.Repo(self._fullpath)

                downlink = self.getURL(self._relpath, content_mode="raw", download="true", branch=repo.active_branch)

                xmlroot = etree.Element('{%s}git' %
                                        self._namespace_uri,
                                        nsmap=self.nsmap,
                                        name=os.path.basename(self._relpath),
                                        resurl=self._web_support.resurl,
                                        downlink=downlink)

                xmlchild = etree.SubElement(xmlroot, "giturl", self.nsmap)
                xmlchild.text = self.getURL(self._relpath) + "/.git"

                xmlchild = etree.SubElement(xmlroot, "branches", nsmap=self.nsmap)
                for branch in repo.branches:
                    xmlbranch = etree.SubElement(xmlchild, "branch", nsmap=self.nsmap)
                    xmlbranch.attrib['url'] = self.getURL(self._relpath, branch=branch.name)

                    xmlname = etree.SubElement(xmlbranch, "name", nsmap=self.nsmap)
                    xmlname.text = branch.name

                    xmllog = etree.SubElement(xmlbranch, "log", nsmap=self.nsmap)
                    for log in branch.log():
                        xmlentry = etree.SubElement(xmllog, "log_entry", nsmap=self.nsmap)
                        xmlentry.text = log.format()

                self.untracked = repo.untracked_files
                if repo.untracked_files:
                    xmlunfiles = etree.SubElement(xmlroot, "untracked_files", nsmap=self.nsmap)
                    for unfile in repo.untracked_files:
                        xmlunfile = etree.SubElement(xmlunfiles, "file", nsmap=self.nsmap)
                        xmlunfile.text = unfile

                if self.changedfiles:
                    xmlchfiles = etree.SubElement(xmlroot, "changed_files", nsmap=self.nsmap)
                    for chfile in self.changedfiles:
                        xmlchfile = etree.SubElement(xmlchfiles, "file", nsmap=self.nsmap)
                        xmlchfile.text = chfile

                xmlchild = etree.SubElement(xmlroot, "active_branch", nsmap=self.nsmap)
                xmlchild.text = str(repo.active_branch)

                xmlcontents = etree.SubElement(xmlroot, "repo_contents", nsmap=self.nsmap)

                xmldir = etree.SubElement(xmlcontents, "dir", nsmap=self.nsmap)
                xmldir.attrib["name"] = os.path.basename(self._fullpath)

                self.recursive_search(xmldir, self._fullpath, relroot=self._relpath)

                return xmlroot
            elif self._content_mode == "raw" and "download" in self._web_support.req.form:
                requested_branch = None
                if "branch" in self._web_support.req.form:
                    requested_branch = self._web_support.req.form["branch"].value

                repo = git.Repo(self._fullpath)

                timestamp = datetime.datetime.now()
                timestamp = timestamp.strftime("%b-%d-%Y-%I-%M%p")

                f = self.getCacheFileHandler('wb', timestamp + "_" + requested_branch, "tar")
                repo.archive(f)
                f.close()

                f = self.getCacheFileHandler('rb', timestamp + "_" + requested_branch, "tar")
                self._web_support.req.response_headers['Content-Type'] = "application/gzip"
                self._web_support.req.response_headers['Content-Length'] = str(os.fstat(f.fileno()).st_size)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(f.name)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            else:
                raise self.RendererException("Invalid Content Mode")
            pass
