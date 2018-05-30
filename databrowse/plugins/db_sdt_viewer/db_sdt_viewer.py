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
## This material is based on work supported by the                           ##
##                                                                           ##
##                                                                           ##
## DISTRIBUTION A.  Approved for public release:  distribution unlimited;    ##
## 19 Aug 2016; 88ABW-2016-4051.				             ##
###############################################################################
""" db_sdt_viewer.py - SDT File Viewer """

import os
import os.path
import time
import platform
if platform.system() == "Linux":
    import pwd
    import grp
from stat import *
from lxml import etree
from databrowse.support.renderer_support import renderer_class
import magic
import numpy as np
import collections
from PIL import Image
import matplotlib.pyplot as plt

import pdb


class db_sdt_viewer(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/sdtfile"
    _namespace_local = "dbsdt"
    _default_content_mode = "full"
    _default_style_mode = "examine_datasets"
    _default_recursion_depth = 2


    # Used to read in data
    dtype_lookup = {'INTEGER 12': np.int16,
                    'INTEGER 16': np.int16,
                    'FLOAT 32': np.float32,
                    'CHAR 8': np.int8}


    def check_units(self, param):
        # Check whether the provided string is an integer, float, or a value with units

        try:
            intval = int(param)
            return intval, None
        except ValueError:
            try:
                floatval = float(param)
                return floatval, None
            except ValueError:
                try:
                    val, units = param.split(' ')
                    return float(val), units
                except IndexError:
                    return param, None

    def parse_sdt(self, fstream, verbose=False):
        # Open file, read in header information, read in and scale datasets, and read xml tree
        # Contents are read by streaming so it must be done in this order

        if verbose:
            print "Reading in header information"
        paramdict = self.read_params(fstream, verbose)

        if verbose:
            print "Reading in data chunk"
        datasets = self.read_data(fstream, paramdict, verbose)

        if verbose:
            print "Extracting XML formatted chunk"
        xmltree = self.read_xml(fstream, verbose)

        return paramdict, datasets, xmltree

    def read_data(self, fstream, paramdict, verbose):
        # Loop through header information to get axis and dataset information
        # read in each dataset, reshape, and scale

        datasets = {}
        minvals = []
        resolution = []
        maxvals = []

        # Default values
        nx = 1
        ny = 1
        nt = 1
        x = [0]
        y = [0]
        t = [0]

        for key, value in paramdict.items():
            if key.find('First Axis') > 0:
                if verbose:
                    print "Found first axis header information"

                nx = int(value['Number of Sample Points'])

                minval, minunits = self.check_units(value['Minimum Sample Position'])
                resval, resunits = self.check_units(value['Sample Resolution'])
                maxval = minval+nx*resval

                x = np.arange(minval, maxval, resval)
                if len(x)>nx:
                    x = x[0:nx]

            if key.find('Second Axis') > 0:
                if verbose:
                    print "Found second axis header information"

                ny = int(value['Number of Sample Points'])

                minval, minunits = self.check_units(value['Minimum Sample Position'])
                resval, resunits = self.check_units(value['Sample Resolution'])
                maxval = minval+ny*resval

                y = np.arange(minval, maxval, resval)
                if len(y)>ny:
                    y = y[0:ny]

        for key, value in paramdict.items():
            if key.find('Data Subset') > 0 and isinstance(value, dict):
                if verbose:
                    print "Starting data extraction for dataset {v}".format(v=value['Subset Label'])

                element_size = int(value['Element Size (bytes)'])
                nt = int(value['Number of Sample Points'])

                if verbose:
                    print "Number of sample points: {n}".format(n=nx*ny*nt)

                minval, minunits = self.check_units(value['Minimum Sample Position'])
                resval, resunits = self.check_units(value['Sample Resolution'])
                maxval = minval+nt*resval

                t = np.arange(minval, maxval, resval)
                if len(t)>nt:
                    t = t[0:nt]

                data_type = self.dtype_lookup[value['Element Representation']]
                data_range = [float(i) for i in value['Measurement Range'].split()[0:2]]
                data_range[1] = data_range[0]+data_range[1]

                if verbose:
                    print "Data type found to be {d}".format(d=data_type)

                #data = np.fromfile(fstream, dtype=data_type, count=nx*ny*nt)
                #data = np.reshape(data,(len(y),len(x),len(t)), order='C') # [index axis, scan axis, time axis]]
                curpos = fstream.tell()
                data = np.memmap(fstream, data_type, 'r', curpos, (len(y), len(x), len(t)), 'C')
                fstream.seek(curpos + (len(y)*len(x)*len(t)*np.dtype(data_type).itemsize))

                if value['Undefineds Permitted'] == 'YES':
                    undef_value = float(value['Undefined Element'])
                else:
                    undef_value = None

                if verbose:
                    print "Reshaping and scaling data to match header information"

                scaled_data = self.scale_data(data, value['Element Representation'], data_range, undef_value)
                datasets.update({value['Subset Label']: {'y': x, 'x': y, 't':t, 'v': scaled_data}})

        return datasets

    def scale_data(self, data, dtype, drange, undef_value=None):
        # Scale data based on the data type given
        if dtype == 'CHAR 8':
            scaled_data = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**8)))*data
            undef_value = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**8)))*undef_value
            scaled_data[scaled_data == undef_value] = np.nan
            return scaled_data

        elif dtype == 'INTEGER 12':
            scaled_data = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**12)))*data
            undef_value = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**12)))*undef_value
            scaled_data[scaled_data == undef_value] = np.nan
            return scaled_data

        elif dtype == 'INTEGER 16':
            scaled_data = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**16)))*data
            undef_value = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**16)))*undef_value
            scaled_data[scaled_data == undef_value] = np.nan
            return scaled_data

        elif dtype == 'FLOAT 32':
            scaled_data = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**32)))*data
            undef_value = (((2*drange[0]+drange[1])/2.0) + (float(drange[1])/(2.0**32)))*undef_value
            scaled_data[scaled_data == undef_value] = np.nan
            return scaled_data

        else:
            raise Exception('Data type {t} not recognized'.format(t=dtype))

    def read_params(self, fstream, verbose):
        # Create dictionary of header information
        # Sub dictionaries are created for axes and subsets

        paramdict = collections.OrderedDict()

        def stream_and_update(main_dict, path_to_subdict):
            inheader = True

            while inheader:
                line = fstream.readline()
                if len(line.split(':')) > 1:
                    key = line.split(':')[0].strip()
                    value = line.split(':')[1].strip()
                    if key == '|^AS Header^|':
                        continue
                    reduce(lambda d, k: d[k], path_to_subdict, main_dict).update({key:value})

                elif len(line.split(':')) == 1:
                    key = line.strip()
                    if key == '|^Data Set^|':
                        inheader = False
                        continue
                    main_dict.update({key: {}})
                    stream_and_update(main_dict, [key])
                    inheader = False
                    continue
            return

        stream_and_update(paramdict, [])

        return paramdict

    def read_xml(self, fobject, verbose):
        # Read in xml tree at the end of the file

        xmldata = fobject.read()
        xmltree = etree.fromstring(xmldata)
        return xmltree

    def getContent(self):
        if self._caller != "databrowse" and self._caller != "cefdatabrowse":
            return None
        else:
            if self._content_mode == "full":
                try:
                    st = os.stat(self._fullpath)
                except IOError:
                    return "Failed To Get File Information: %s" % (self._fullpath)
                else:
                    file_size = st[ST_SIZE]
                    file_mtime = time.asctime(time.localtime(st[ST_MTIME]))
                    file_ctime = time.asctime(time.localtime(st[ST_CTIME]))
                    file_atime = time.asctime(time.localtime(st[ST_ATIME]))
                    try:
                        magicstore = magic.open(magic.MAGIC_MIME)
                        magicstore.load()
                        contenttype = magicstore.file(
                            os.path.realpath(self._fullpath))  # real path to resolve symbolic links outside of dataroot
                    except AttributeError:
                        contenttype = magic.from_file(os.path.realpath(self._fullpath), mime=True)
                    if contenttype is None:
                        contenttype = "text/plain"
                    extension = os.path.splitext(self._fullpath)[1][1:]
                    icon = self._handler_support.GetIcon(contenttype, extension)

                    downlink = self.getURL(self._relpath, content_mode="raw", download="true")
                    imagelink = self.getURL(self._relpath, content_mode="raw", image="true")

                    xmlroot = etree.Element('{%s}sdtfile' %
                                            self._namespace_uri,
                                            nsmap=self.nsmap,
                                            name=os.path.basename(self._relpath),
                                            resurl=self._web_support.resurl,
                                            downlink=downlink, icon=icon,
                                            imagelink=imagelink)

                    xmlchild = etree.SubElement(xmlroot, "filename", nsmap=self.nsmap)
                    xmlchild.text = os.path.basename(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "path", nsmap=self.nsmap)
                    xmlchild.text = os.path.dirname(self._fullpath)

                    xmlchild = etree.SubElement(xmlroot, "size", nsmap=self.nsmap)
                    xmlchild.text = self.ConvertUserFriendlySize(file_size)

                    xmlchild = etree.SubElement(xmlroot, "mtime", nsmap=self.nsmap)
                    xmlchild.text = file_mtime

                    xmlchild = etree.SubElement(xmlroot, "ctime", nsmap=self.nsmap)
                    xmlchild.text = file_ctime

                    xmlchild = etree.SubElement(xmlroot, "atime", nsmap=self.nsmap)
                    xmlchild.text = file_atime

                    # Content Type
                    xmlchild = etree.SubElement(xmlroot, "contenttype", nsmap=self.nsmap)
                    xmlchild.text = contenttype

                    # File Permissions
                    xmlchild = etree.SubElement(xmlroot, "permissions", nsmap=self.nsmap)
                    xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                    # User and Group
                    if platform.system() == "Linux":
                        username = pwd.getpwuid(st[ST_UID])[0]
                        groupname = grp.getgrgid(st[ST_GID])[0]
                        xmlchild = etree.SubElement(xmlroot, "owner", nsmap=self.nsmap)
                        xmlchild.text = "%s:%s" % (username, groupname)

                    # XML Contents
                    f = open(self._fullpath)
                    paramdict, datasets, xmltree = self.parse_sdt(f)
                    f.close()
                    xmlcontent = etree.SubElement(xmlroot, "xmlcontent",nsmap=self.nsmap)
                    xmlcontent.append(xmltree)

                    # Parameters
                    def parsedict(self, root, d):
                        for n in d:
                            v = d[n]
                            node = etree.SubElement(root, "node", nsmap=self.nsmap)
                            node.set("name", n)
                            if isinstance(v, dict):
                                parsedict(self, node, v)
                            else:
                                node.text = v
                            pass
                        pass

                    paramcontent = etree.SubElement(xmlroot, "parameters", nsmap=self.nsmap)
                    parsedict(self, paramcontent, paramdict)

                    # Datasets
                    dsetcontent = etree.SubElement(xmlroot, "datasets", nsmap=self.nsmap)
                    for item in datasets:
                        node = etree.SubElement(dsetcontent, "dataset", nsmap=self.nsmap)
                        node.set("name", item)
                        node.set("shape",repr(datasets[item]['v'].shape))

                    return xmlroot
            elif self._content_mode == "raw" and "download" in self._web_support.req.form:
                size = os.path.getsize(self._fullpath)
                try:
                    magicstore = magic.open(magic.MAGIC_MIME)
                    magicstore.load()
                    contenttype = magicstore.file(os.path.realpath(self._fullpath))  # real path to resolve symbolic links outside of dataroot
                except AttributeError:
                    contenttype = magic.from_file(os.path.realpath(self._fullpath), mime=True)
                if contenttype is None:
                    contenttype = "text/plain"
                f = open(self._fullpath, "rb")
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')
            elif self._content_mode == "raw" and "image" in self._web_support.req.form:
                if "dataset" not in self._web_support.req.form:
                    raise self.RendererException("Dataset Must Be Selected")

                f = None

                if "frame" in self._web_support.req.form:
                    fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)+"_Frame"+str(self._web_support.req.form['frame'].value)
                    if self.CacheFileExists(fprefix,'png'):
                        f = self.getCacheFileHandler('rb', fprefix, 'png')
                        contenttype='image/png'
                        size = os.path.getsize(self.getCacheFileName(fprefix,'png'))
                        pass
                    pass
                else:
                    fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)
                    if self.CacheFileExists(fprefix, 'png'):
                        f = self.getCacheFileHandler('rb', fprefix, 'png')
                        contenttype='image/png'
                        size = os.path.getsize(self.getCacheFileName(fprefix,'png'))
                        pass
                    pass
                if f is None:
                    g = open(self._fullpath)
                    paramdict, datasets, xmltree = self.parse_sdt(g)
                    g.close()

                    dsetname = self._web_support.req.form['dataset'].value

                    if dsetname not in datasets:
                        raise self.RendererException("Dataset '%s' Not Found" % dsetname)

                    ds = datasets[dsetname]

                    shp = ds['v'].shape

                    pd = None

                    for i in paramdict:
                        if i.startswith('-- Data Subset'):
                            if paramdict[i]['Subset Label'] == dsetname:
                                pd = paramdict[i]
                                pass
                            pass
                        pass

                    if pd is None:
                        raise self.RendererException("Unable to locate '%s' in Parameter List" % dsetname)

                    vmin = float(pd['Measurement Range'].split()[0])
                    vmax = float(pd['Measurement Range'].split()[1])+vmin
                    try:
                        vunits = pd['Measurement Range'].split()[2]
                    except:
                        vunits = "unitless"

                    # Ascan
                    if shp[0] == 1 and shp[1] == 1 and shp[2] > 1:
                        plt.plot(ds['t'], ds['v'][0,0,:])
                        plt.xlabel('Time, t (%s)' % (self.check_units(pd['Sample Resolution'])[1]))
                        plt.ylabel('Amplitude (%s)' % (vunits))
                        #pylab.ylim([vmin, vmax])
                        fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)
                    # Bscan
                    elif shp[0] > 1 and shp[1] == 1 and shp[2] > 1:
                        # Beware - this one probably doesn't work
                        # Also, this situation probably doesn't actually happen
                        plt.imshow(ds['v'][:,0,:], cmap='jet',
                                     origin='lower', extent=[ds['x'][0],
                                                             ds['x'][-1],
                                                             ds['t'][0],
                                                             ds['t'][-1]])#vmin=vmin, vmax=vmax)
                        axis = 'Axis 1'
                        aunits = 'None'
                        for i in paramdict:
                            if i.startswith('--- First Axis ---'):
                                axis = i[i.find('(')+1:i.find(')')]
                                aunits = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            pass
                        plt.xlabel('Position, %s (%s)' % (axis, aunits))
                        plt.ylabel('Time, t (%s)' % (self.check_units(pd['Sample Resolution'])[1]))
                        cb = plt.colorbar()
                        cb.set_label('Amplitude (%s)' % vunits)
                        fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)
                    # Bscan
                    elif shp[1] > 1 and shp[0] == 1 and shp[2] > 1:
                        plt.imshow(ds['v'][0,:,:], cmap='jet',
                                     origin='lower', extent=[ds['y'][0],
                                                             ds['y'][-1],
                                                             ds['t'][0],
                                                             ds['t'][-1]])#vmin=vmin, vmax=vmax)
                        axis = 'Axis 2'
                        aunits = 'None'
                        for i in paramdict:
                            if i.startswith('--- Second Axis ---'):
                                axis = i[i.find('(')+1:i.find(')')]
                                aunits = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            pass
                        plt.xlabel('Position, %s (%s)' % (axis, aunits))
                        plt.ylabel('Time, t (%s)' % (self.check_units(pd['Sample Resolution'])[1]))
                        cb = plt.colorbar()
                        cb.set_label('Amplitude (%s)' % vunits)
                        fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)
                    # Gated CScan Output - i.e. Both Positions And No Time
                    elif shp[0] > 1 and shp[1] > 1 and shp[2] == 1:
                        plt.imshow(ds['v'][:,:,0], cmap='jet',
                                     origin='lower', extent=[ds['x'][0],
                                                             ds['x'][-1],
                                                             ds['y'][0],
                                                             ds['y'][-1]],
                                    vmin=ds['v'].min(), vmax=ds['v'].max())
                        axis1 = 'Axis 1'
                        a1units = 'None'
                        axis2 = 'Axis 2'
                        a2units = 'None'
                        for i in paramdict:
                            if i.startswith('--- First Axis ---'):
                                axis1 = i[i.find('(')+1:i.find(')')]
                                a1units = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            elif i.startswith('--- Second Axis ---'):
                                axis2 = i[i.find('(')+1:i.find(')')]
                                a2units = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            pass
                        plt.xlabel('Position, %s (%s)' % (axis1, a1units))
                        plt.ylabel('Position, %s (%s)' % (axis2, a2units))
                        cb = plt.colorbar()
                        cb.set_label('Amplitude, (%s)' % vunits)
                        fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value)
                    # CScan
                    elif shp[0] > 1 and shp[1] > 1 and shp[2] > 1:
                        if "frame" not in self._web_support.req.form:
                            frame = ds['v'].max(0).max(0).argmax()
                        else:
                            frame = int(self._web_support.req.form['frame'].value)
                        plt.imshow(ds['v'][:,:,frame], cmap='jet',
                                     origin='lower', extent=[ds['x'][0],
                                                             ds['x'][-1],
                                                             ds['y'][0],
                                                             ds['y'][-1]],
                                     vmin=ds['v'].min(), vmax=ds['v'].max())
                        axis1 = 'Axis 1'
                        a1units = 'None'
                        axis2 = 'Axis 2'
                        a2units = 'None'
                        for i in paramdict:
                            if i.startswith('--- First Axis ---'):
                                axis1 = i[i.find('(')+1:i.find(')')]
                                a1units = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            elif i.startswith('--- Second Axis ---'):
                                axis2 = i[i.find('(')+1:i.find(')')]
                                a2units = self.check_units(paramdict[i]['Sample Resolution'])[1]
                                pass
                            pass
                        plt.xlabel('Position, %s (%s)' % (axis1, a1units))
                        plt.ylabel('Position, %s (%s)' % (axis2, a2units))
                        cb = plt.colorbar()
                        cb.set_label('Amplitude (%s)' % vunits)
                        plt.title('Time, t=%0.2f %s' % (ds['t'][frame],
                                                              self.check_units(pd['Sample Resolution'])[1]))
                        fprefix = "Dataset_"+str(self._web_support.req.form['dataset'].value+"_Frame%d"%frame)

                    f = self.getCacheFileHandler('wb', fprefix, 'png')
                    plt.savefig(f)
                    f.close()
                    plt.clf()
                    size = os.path.getsize(self.getCacheFileName(fprefix, 'png'))
                    contenttype='image/png'
                    f = self.getCacheFileHandler('rb', fprefix, 'png')

                self._web_support.req.response_headers['Content-Disposition'] = "filename=" + os.path.basename(f.name)
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                self._web_support.req.output_done = True
                if 'wsgi.file_wrapper' in self._web_support.req.environ:
                    return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                else:
                    return iter(lambda: f.read(1024), '')

            else:
                raise self.RendererException("Invalid Content Mode")
        pass

    pass
