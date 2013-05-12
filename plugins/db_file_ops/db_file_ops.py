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
""" plugins/renderers/db_file_ops.py - File Operations Utility Plugin """

import os
import os.path
from renderer_support import renderer_class
import re
import json
import shutil


class db_file_ops(renderer_class):
    """ File Operations Utility Plugin """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/fileops"
    _namespace_local = "fileops"
    _default_content_mode = "raw"
    _default_style_mode = "list"
    _default_recursion_depth = 2

    def get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def getContent(self):
        if not "operation" in self._web_support.req.form:
            raise self.RendererException("Operation Must Be Specified")
        else:
            operation = self._web_support.req.form['operation'].value

        if operation == "upload":
            if not os.path.isdir(self._fullpath):
                raise self.RendererException("Uploads Must Be in Folder")
            elif not "files[]" in self._web_support.req.form:
                raise self.RendererException("No Uploads Found")
            fieldStorage = self._web_support.req.form["files[]"]
            fullfilename = os.path.abspath(self._fullpath + "/" + fieldStorage.filename)
            if not fullfilename.startswith(self._web_support.dataroot):
                raise self.RendererException("Attempt to Save File Outside of Dataroot")
            # Let's check on the directory and make sure its writable and it exists
            if not os.access(self._fullpath, os.W_OK) and os.path.exists(self._fullpath):
                raise self.RendererException("Save Directory Not Writable")
            else:
                #Let's check on the file and make sure its writable and doesn't exist
                if os.path.exists(fullfilename):
                    # rename old version into .1 .2. .3 etc.
                    filenum = 1
                    while os.path.exists("%s.%.2d%s" % (os.path.splitext(fullfilename)[0], filenum, os.path.splitext(fullfilename)[1])):
                        filenum += 1
                        pass
                    os.rename(fullfilename, "%s.%.2d%s" % (os.path.splitext(fullfilename)[0], filenum, os.path.splitext(fullfilename)[1]))
                    pass
                f = open(fullfilename, "w")
                f.write(fieldStorage.value)
                f.close
            results = []
            result = {}
            result['name'] = re.sub(r'^.*\\', '', fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            #result['delete_type'] = 'DELETE'
            #result['delete_url'] = self.getURL(os.path.join(self._relpath, fieldStorage.filename), handler=None)
            result['url'] = self.getURL(os.path.join(self._relpath, fieldStorage.filename), handler=None)
            if os.path.splitext(fieldStorage.filename)[1][1:] in ["png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff"]:
                result['thumbnail_url'] = self.getURL(os.path.join(self._relpath, fieldStorage.filename), content_mode="raw", thumbnail="small", handler=None)
            results.append(result)
            resultwrapper = {'files': results}
            s = json.dumps(resultwrapper, separators=(',', ':'))
            #if 'HTTP_ACCEPT' in self._web_support.req.environ and 'application/json' in self._web_support.req.environ['HTTP_ACCEPT']:
            #    self._web_support.req.response_headers['Content-Type'] = 'application/json'
            #else:
            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            return [s]
        elif operation == "newdir":
            outputmsg = ""
            if not os.path.isdir(self._fullpath):
                outputmsg = "ERROR:  Directories Must Be Created Inside Directories"
            elif not "dirname" in self._web_support.req.form or self._web_support.req.form["dirname"].value == "":
                outputmsg = "ERROR:  No Directory Name Supplied"
            elif not os.access(self._fullpath, os.W_OK) and not os.path.exists(self._fullpath):
                outputmsg = "ERROR: Directory '" + self._fullpath + "' Not Writable"
            else:
                newdirpath = os.path.abspath(os.path.join(self._fullpath, self._web_support.req.form["dirname"].value))
                if not newdirpath.startswith(self._web_support.dataroot):
                    outputmsg = "ERROR: Cannot Write Outside Of Dataroot"
                elif os.path.exists(newdirpath):
                    outputmsg = "ERROR: Directory Already Exists"
                else:
                    try:
                        os.makedirs(newdirpath)
                        pass
                    except Exception as err:
                        outputmsg = "ERROR: " + repr(err)
                        pass
                    else:
                        outputmsg = "Directory Created Successfully"
                        pass
                    pass
                pass
            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            return [outputmsg]
        elif operation == "rename":
            outputmsg = ""
            if not "newname" in self._web_support.req.form or self._web_support.req.form["newname"].value == "":
                outputmsg = "ERROR:  Name Must Be Specified"
            elif not os.access(self._fullpath, os.W_OK) and not os.path.exists(self._fullpath):
                outputmsg = "ERROR: Directory '" + self._fullpath + "' Not Writable"
            else:
                newpath = os.path.abspath(os.path.join(os.path.dirname(self._fullpath), self._web_support.req.form["newname"].value))
                if not newpath.startswith(self._web_support.dataroot):
                    outputmsg = "ERROR: Cannot Write Outside Of Dataroot"
                elif os.path.exists(newpath):
                    outputmsg = "ERROR: File or Directory Already Exists"
                else:
                    try:
                        os.renames(self._fullpath, newpath)
                        pass
                    except Exception as err:
                        outputmsg = "ERROR: " + repr(err)
                        pass
                    else:
                        outputmsg = "Item Renamed Successfully"
                        pass
                    pass
                pass
            pass
            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            return [outputmsg]
        elif operation == "delete":
            outputmsg = ""
            if not os.access(self._fullpath, os.W_OK) and not os.path.exists(self._fullpath):
                outputmsg = "ERROR: Directory '" + self._fullpath + "' Not Writable"
            elif self._fullpath == self._web_support.dataroot:
                outputmsg = "ERROR: Databrowse Data Root Directory '" + self._fullpath + "' Cannot Be Deleted"
            else:
                trashdir = os.path.abspath(os.path.dirname(self._fullpath) + "/.databrowse/trash/")
                if not os.path.exists(trashdir):
                    try:
                        os.makedirs(trashdir)
                    except Exception as err:
                        outputmsg = "ERROR:  Unable to Create Trash Directory - Check File Permissions"
                if outputmsg == "":
                    try:
                        shutil.move(self._fullpath, trashdir)
                        pass
                    except Exception as err:
                        outputmsg = "ERROR: " + repr(err)
                        pass
                    else:
                        outputmsg = "Item Moved To Trash Successfully"
                        pass
                    pass
                pass
            pass
            self._web_support.req.response_headers['Content-Type'] = 'text/plain'
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            return [outputmsg]
        else:
            raise self.RendererException("Invalid Operation Specificed")

    pass
