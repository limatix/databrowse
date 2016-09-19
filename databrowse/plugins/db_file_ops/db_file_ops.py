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
## 19 Aug 2016; 88ABW-2016-4051.											 ##
###############################################################################
""" plugins/renderers/db_file_ops.py - File Operations Utility Plugin """

import os
import os.path
from databrowse.support.renderer_support import renderer_class
import re
import json
import shutil
import databrowse.support.zipstream as zipstream


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
        elif operation == "download":
            def zipdir(path, ziph):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        ziph.write(os.path.join(root, f))
                        pass
                    pass
                pass
            z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED, allowZip64=True)
            if os.path.isdir(self._fullpath):
                zipdir(self._fullpath, z)
            else:
                z.write(self._fullpath)
            #s = sum(e.compress_size for e in z.infolist())
            #self._web_support.req.response_headers['Content-Length'] = str(s)
            self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath) + ".zip"
            self._web_support.req.response_headers['Content-Type'] = 'application/zip'
            self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
            self._web_support.req.output_done = True
            return z
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
