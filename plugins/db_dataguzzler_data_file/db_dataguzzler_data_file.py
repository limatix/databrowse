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
""" plugins/renderers/db_dataguzzler.py - Default Renderer - Basic Output for Any Dataguzzler File """

import os
import os.path
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic
import dg_file as dgf
import dg_eval as dge
import dg_metadata as dgm
import struct
import numpy
from PIL import Image
import matplotlib as mpl
mpl.use('Agg')
import pylab
import images2gif

# These definitions should be synchronized with dg_dumpfile within dataguzzler
dgf_nestedchunks = set(["DATAGUZZ", "GUZZNWFM", "GUZZWFMD", "METADATA", "METDATUM", "SNAPSHOT", "SNAPSHTS", "VIBRDATA", "VIBFCETS", "VIBFACET"])
dgf_stringchunks = set(["WAVENAME", "METDNAME", "METDSTRV"])
dgf_int64chunks = set(["METDINTV", "WFMDIMNS"])
dgf_float64chunks = set(["METDDBLV"])


class db_dataguzzler_data_file(renderer_class):
    """ Default Renderer - Basic Output for Any Dataguzzler File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/dataguzzler"
    _namespace_local = "dg"
    _default_content_mode = "full"
    _default_style_mode = "examine_file_contents"
    _default_recursion_depth = 2

    def dumpxmlchunk(self, dgfh, nestdepth=-1):
        ellist = []

        Chunk = dgf.nextchunk(dgfh)
        while Chunk:
            newel = etree.Element("{%s}%s" % (self._namespace_uri, Chunk.Name))
            if (Chunk.Name in dgf_nestedchunks):
                if nestdepth > 0:
                    nestedchunks = self.dumpxmlchunk(dgfh, nestdepth-1)
                    for nestedchunk in nestedchunks:
                        newel.append(nestedchunk)
                        pass
                    pass
                else:
                    nestedchunks = self.dumpxmlchunk(dgfh, -1)
                    for nestedchunk in nestedchunks:
                        newel.append(nestedchunk)
                        pass
                    pass
                pass
            elif Chunk.Name in dgf_stringchunks:
                newel.text = dgf.readdata(dgfh, Chunk.ChunkLen)
                pass
            elif Chunk.Name in dgf_int64chunks:
                textdata = ""
                for cnt in range(Chunk.ChunkLen/8):
                    textdata += "%d\n" % (struct.unpack("@Q", dgf.readdata(dgfh, 8)))
                    pass
                newel.text = textdata
                pass
            elif Chunk.Name in dgf_float64chunks:
                textdata = ""
                for cnt in range(Chunk.ChunkLen/8):
                    textdata += "%.10g\n" % (struct.unpack("@d", dgf.readdata(dgfh, 8)))
                    pass
                newel.text = textdata
                pass
            else:
                newel.text = "%s\n" % (self.ConvertUserFriendlySize(Chunk.ChunkLen))
                pass
            dgf.chunkdone(dgfh, None)
            Chunk = dgf.nextchunk(dgfh)
            ellist.append(newel)
            pass
        return ellist

    def CreateImageFromWaveform(self, waveform, wfmdict, waveformname, filename, dgfh):
        if "ProcExpr" in waveform.MetaData:
            (ndim, dimlen, inival, step, bases) = dge.geom(waveform)
            inivalstepdimlen = []
            for i in range(ndim):
                inivalstepdimlen.append(inival[i])
                inivalstepdimlen.append(step[i])
                inivalstepdimlen.append(dimlen[i])
            waveform = dge.eval(waveform, wfmdict, ndim, *inivalstepdimlen, rgba=False)
        rgbawaveform = None
        if "ProcRGBA" in wfmdict[waveformname].MetaData:
            (ndim, dimlen, inival, step, bases) = dge.geom(wfmdict[waveformname])
            inivalstepdimlen = []
            for i in range(ndim):
                inivalstepdimlen.append(inival[i])
                inivalstepdimlen.append(step[i])
                inivalstepdimlen.append(dimlen[i])
            rgbawaveform = dge.eval(wfmdict[waveformname], wfmdict, ndim, *inivalstepdimlen, rgba=True)

        (ndim, dimlen, inival, step, bases) = dge.geom(waveform)
        coord = []
        units = []
        for i in range(ndim):
            try:
                coord.append(waveform.MetaData['ProcCoord' + str(i+1)].Value if ("ProcCoord" + str(i+1)) in waveform.MetaData else waveform.MetaData['Coord' + str(i+1)].Value)
                units.append(waveform.MetaData['ProcUnits' + str(i+1)].Value if ("ProcUnits" + str(i+1)) in waveform.MetaData else waveform.MetaData['Units' + str(i+1)].Value)
            except:
                pass
        coord.append(waveform.MetaData['ProcAmplCoord'].Value if "ProcAmplCoord" in waveform.MetaData else waveform.MetaData['AmplCoord'].Value)
        units.append(waveform.MetaData['ProcAmplUnits'].Value if "ProcAmplUnits" in waveform.MetaData else waveform.MetaData['AmplUnits'].Value)

        if all(k in waveform.MetaData for k in ("Coord1", "Coord2", "Coord3")):  # Time Dependant Images
            if len(waveform.data.shape) == 2:
                xmin = inival[0]
                xmax = waveform.data.shape[0] * step[0] + inival[0]
                ymin = inival[1]
                ymax = waveform.data.shape[1] * step[1] + inival[1]
                pylab.imshow(waveform.data[:, :].T, cmap='hot', origin='lower', extent=[xmin, xmax, ymin, ymax])
                cb = pylab.colorbar()
                cb.set_label(coord[-1] + " (" + units[-1] + ")")
                if rgbawaveform is not None:
                        RGBAdat = rgbawaveform.data[:, :].transpose().tostring()
                        sz = len(RGBAdat)
                        RGBAmat = numpy.fromstring(RGBAdat, 'B').reshape(sz/4, 4)
                        RGBAmat2 = RGBAmat.copy()
                        RGBAmat2[:, 0] = RGBAmat[:, 3]
                        RGBAmat2[:, 1] = RGBAmat[:, 2]
                        RGBAmat2[:, 2] = RGBAmat[:, 1]
                        RGBAmat2[:, 3] = RGBAmat[:, 0]
                        #newsize = (waveform.data.shape[0], waveform.data.shape[1], 4)
                        #img = Image.fromstring("RGBA", (DimLen[0], DimLen[1]), RGBAmat2.tostring())
                        pylab.imshow(Image.fromstring("RGBA", (rgbawaveform.data.shape[0], rgbawaveform.data.shape[1]), RGBAmat2.tostring()), origin='lower', extent=[xmin, xmax, ymin, ymax])
                pylab.title(waveformname)
                pylab.xlabel(coord[0] + " (" + units[0] + ")")
                pylab.ylabel(coord[1] + " (" + units[1] + ")")
                f = self.getCacheFileHandler('w', filename, 'png')
                pylab.savefig(f)
                f.close()
                pylab.clf()
                dgf.close(dgfh)
                size = os.path.getsize(self.getCacheFileName(filename, 'png'))
                return (self.getCacheFileHandler('r', filename, 'png'), size, 'image/png')
            elif len(waveform.data.shape) == 3:
                xmin = inival[0]
                xmax = waveform.data.shape[0] * step[0] + inival[0]
                ymin = inival[1]
                ymax = waveform.data.shape[1] * step[1] + inival[1]
                t = numpy.arange(0, waveform.data.shape[2], dtype='d') * step[2] + inival[2]
                images = []
                for i in range(0, waveform.data.shape[2] - 1):
                    fig = pylab.figure()
                    fig.set_facecolor((1, 1, 1, 1))
                    pylab.imshow(waveform.data[:, :, i].T, cmap='hot', origin='lower', extent=[xmin, xmax, ymin, ymax])
                    cb = pylab.colorbar()
                    cb.set_label(coord[-1] + " (" + units[-1] + ")")
                    if rgbawaveform is not None:
                        RGBAdat = rgbawaveform.data[:, :, i].transpose().tostring()
                        sz = len(RGBAdat)
                        RGBAmat = numpy.fromstring(RGBAdat, 'B').reshape(sz/4, 4)
                        RGBAmat2 = RGBAmat.copy()
                        RGBAmat2[:, 0] = RGBAmat[:, 3]
                        RGBAmat2[:, 1] = RGBAmat[:, 2]
                        RGBAmat2[:, 2] = RGBAmat[:, 1]
                        RGBAmat2[:, 3] = RGBAmat[:, 0]
                        #newsize = (waveform.data.shape[0], waveform.data.shape[1], 4)
                        #img = Image.fromstring("RGBA", (DimLen[0], DimLen[1]), RGBAmat2.tostring())
                        pylab.imshow(Image.fromstring("RGBA", (rgbawaveform.data.shape[0], rgbawaveform.data.shape[1]), RGBAmat2.tostring()), origin='lower', extent=[xmin, xmax, ymin, ymax])
                    pylab.title(waveformname + " (" + coord[2] + ": " + str(t[i]) + " " + units[2] + ")")
                    pylab.xlabel(coord[0] + " (" + units[0] + ")")
                    pylab.ylabel(coord[1] + " (" + units[1] + ")")
                    fig.canvas.draw()
                    w, h = fig.canvas.get_width_height()
                    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
                    buf.shape = (w, h, 4)
                    buf = numpy.roll(buf, 3, axis=2)
                    images.append(Image.fromstring("RGBA", (w, h), buf.tostring()))
                    pylab.clf()
                if len(images) < 20:
                    duration = 1
                else:
                    duration = 0.01
                images2gif.writeGif(self.getCacheFileHandler('w', filename, 'gif'), images, duration=duration)
                dgf.close(dgfh)
                size = os.path.getsize(self.getCacheFileName(filename, 'gif'))
                return (self.getCacheFileHandler('r', filename, 'gif'), size, 'image/gif')
                pass
            pass
        elif all(k in waveform.MetaData for k in ("Coord1", "Coord2")):  # Static Images
            if len(waveform.data.shape) == 3:
                xmin = inival[0]
                xmax = waveform.data.shape[0] * step[0] + inival[0]
                ymin = inival[1]
                ymax = waveform.data.shape[1] * step[1] + inival[1]
                images = []
                for i in range(0, waveform.data.shape[2] - 1):
                    fig = pylab.figure()
                    fig.set_facecolor((1, 1, 1, 1))
                    pylab.imshow(waveform.data[:, :, i].T, cmap='hot', origin='lower', extent=[xmin, xmax, ymin, ymax])
                    cb = pylab.colorbar()
                    cb.set_label(coord[-1] + " (" + units[-1] + ")")
                    if rgbawaveform is not None:
                        RGBAdat = rgbawaveform.data[:, :, i].transpose().tostring()
                        sz = len(RGBAdat)
                        RGBAmat = numpy.fromstring(RGBAdat, 'B').reshape(sz/4, 4)
                        RGBAmat2 = RGBAmat.copy()
                        RGBAmat2[:, 0] = RGBAmat[:, 3]
                        RGBAmat2[:, 1] = RGBAmat[:, 2]
                        RGBAmat2[:, 2] = RGBAmat[:, 1]
                        RGBAmat2[:, 3] = RGBAmat[:, 0]
                        #newsize = (waveform.data.shape[0], waveform.data.shape[1], 4)
                        #img = Image.fromstring("RGBA", (DimLen[0], DimLen[1]), RGBAmat2.tostring())
                        pylab.imshow(Image.fromstring("RGBA", (rgbawaveform.data.shape[0], rgbawaveform.data.shape[1]), RGBAmat2.tostring()), origin='lower', extent=[xmin, xmax, ymin, ymax])
                    pylab.title(waveformname + " (Frame " + str(i+1) + ")")
                    pylab.xlabel(coord[0] + " (" + units[0] + ")")
                    pylab.ylabel(coord[1] + " (" + units[1] + ")")
                    fig.canvas.draw()
                    w, h = fig.canvas.get_width_height()
                    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
                    buf.shape = (w, h, 4)
                    buf = numpy.roll(buf, 3, axis=2)
                    images.append(Image.fromstring("RGBA", (w, h), buf.tostring()))
                    pylab.clf()
                if len(images) < 20:
                    duration = 1
                else:
                    duration = 0.01
                images2gif.writeGif(self.getCacheFileHandler('w', filename, 'gif'), images, duration=duration)
                dgf.close(dgfh)
                size = os.path.getsize(self.getCacheFileName(filename, 'gif'))
                return (self.getCacheFileHandler('r', filename, 'gif'), size, 'image/gif')
            elif len(waveform.data.shape) == 2:
                xmin = inival[0]
                xmax = waveform.data.shape[0] * step[0] + inival[0]
                ymin = inival[1]
                ymax = waveform.data.shape[1] * step[1] + inival[1]
                pylab.imshow(waveform.data[:, :].T, cmap='hot', origin='lower', extent=[xmin, xmax, ymin, ymax])
                cb = pylab.colorbar()
                cb.set_label(coord[-1] + " (" + units[-1] + ")")
                pylab.title(waveformname)
                pylab.xlabel(coord[0] + " (" + units[0] + ")")
                pylab.ylabel(coord[1] + " (" + units[1] + ")")
                f = self.getCacheFileHandler('w', filename, 'png')
                pylab.savefig(f)
                f.close()
                pylab.clf()
                dgf.close(dgfh)
                size = os.path.getsize(self.getCacheFileName(filename, 'png'))
                return (self.getCacheFileHandler('r', filename, 'png'), size, 'image/png')
            else:
                pass
        elif "Coord1" in waveform.MetaData and waveform.data.shape[0] != 1:  # Plain Waveforms
            n = waveform.data.shape[0]
            x = pylab.arange(0, n, dtype='d') * step[0] + inival[0]
            y = waveform.data
            if n > 10000:
                chunksize = 1000
                numchunks = y.size // chunksize
                ychunks = y[:chunksize*numchunks].reshape((-1, chunksize))
                xchunks = x[:chunksize*numchunks].reshape((-1, chunksize))
                max_env = ychunks.max(axis=1)
                min_env = ychunks.min(axis=1)
                ycenters = ychunks.mean(axis=1)
                xcenters = xchunks.mean(axis=1)
                pylab.fill_between(xcenters, min_env, max_env, edgecolor='none')
                #color='gray', edgecolor='none', alpha=0.5
                pylab.plot(xcenters, ycenters)
            else:
                pylab.plot(x, y)
            pylab.title(waveformname)
            pylab.xlabel(coord[0] + " (" + units[0] + ")")
            pylab.ylabel(coord[-1] + " (" + units[-1] + ")")
            pylab.grid(True)
            f = self.getCacheFileHandler('w', filename, 'png')
            pylab.savefig(f)
            f.close()
            pylab.clf()
            dgf.close(dgfh)
            size = os.path.getsize(self.getCacheFileName(filename, 'png'))
            return (self.getCacheFileHandler('r', filename, 'png'), size, 'image/png')
            pass
        elif waveform.data.shape[0] == 1:
            pylab.plot(waveform.data, marker='o', color='b')
            pylab.title(waveformname)
            if "Coord1" in waveform.MetaData:
                pylab.xlabel(coord[0] + " (" + units[0] + ")")
            pylab.ylabel(coord[-1] + " (" + units[-1] + ")")
            pylab.grid(True)
            f = self.getCacheFileHandler('w', filename, 'png')
            pylab.savefig(f)
            f.close()
            pylab.clf()
            dgf.close(dgfh)
            size = os.path.getsize(self.getCacheFileName(filename, 'png'))
            return (self.getCacheFileHandler('r', filename, 'png'), size, 'image/png')
        else:
            raise self.RendererException("Unrecognized Waveform Data")

    def getSnapshotImage(self, snapshotnumber, waveformname):
        dgfh = dgf.open(self._fullpath)
        chunk = dgf.nextchunk(dgfh)

        if chunk.Name == "SNAPSHTS":
            count = 0
            while count != snapshotnumber:
                chunk = dgf.nextchunk(dgfh)
                if chunk.Name == "SNAPSHOT":
                    count = count + 1
                if count == snapshotnumber:
                    break
                else:
                    dgf.chunkdone(dgfh, chunk)
                pass
            pass
        elif chunk.Name == "SNAPSHOT":
            if snapshotnumber != 1:
                raise self.RendererException("Looking for SNAPSHTS but found SNAPSHOT")
            pass
        else:
            raise self.RendererException("Unexpected " + chunk.Name + " Chunk Found")

        mdata, wfms, wfmdict = dgf.procSNAPSHOT(dgfh)
        if waveformname == "DiffStack":
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(1)))
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(296.5)))
        elif waveformname == "VibroFit":
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(296.5)))
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(1)))
            dgm.AddMetaDatumWI(wfmdict['VibroFit'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['VibroFit'], dgm.CreateMetaDatumDbl("ScopeOffset", float(1)))
        elif waveformname == "VibroFitImg":
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(296.5)))
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['DiffStack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(1)))
            dgm.AddMetaDatumWI(wfmdict['VibroFit'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['VibroFit'], dgm.CreateMetaDatumDbl("ScopeOffset", float(1)))
        elif waveformname == "IRstack":
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeUnitsPerDiv", float(2)))
            dgm.AddMetaDatumWI(wfmdict['IRstack'], dgm.CreateMetaDatumDbl("ScopeOffset", float(296.5)))
        waveform = wfmdict[waveformname]
        filename = "SNAPSHOT"+str(snapshotnumber)+"_"+waveformname

        return self.CreateImageFromWaveform(waveform, wfmdict, waveformname, filename, dgfh)

    def getWaveformImage(self, waveformnumber=1):
        dgfh = dgf.open(self._fullpath)
        chunk = dgf.nextchunk(dgfh)

        if chunk.Name == "GUZZWFMD":
            count = 1
            if count != waveformnumber:
                dgf.chunkdone(dgfh, chunk)
            while count != waveformnumber:
                chunk = dgf.nextchunk(dgfh)
                if chunk.Name == "GUZZWFMD":
                    count = count + 1
                if count == waveformnumber:
                    break
                else:
                    dgf.chunkdone(dgfh, chunk)
                pass
            pass
        else:
            raise self.RendererException("Unexpected " + chunk.Name + " Chunk Found")

        waveform = dgf.procGUZZWFMD(dgfh, None)
        filename = "WAVEFORM"+str(waveformnumber)

        return self.CreateImageFromWaveform(waveform, None, "Unnamed Waveform " + str(waveformnumber), filename, dgfh)

    def getContent(self):
        if self._caller != "databrowse":
            return None
        else:
            if self._content_mode is "full" or self._content_mode is "summary":
                nestdepth = -1
                if self._content_mode is "summary":
                    nestdepth = 3
                    pass

                dgfh = dgf.open(self._fullpath)
                if dgfh:
                    xmlchunk = self.dumpxmlchunk(dgfh, nestdepth=nestdepth)
                    dgf.close(dgfh)
                    pass
                if len(xmlchunk) > 1:
                    xmlcontent = etree.Element('{http://thermal.cnde.iastate.edu/dataguzzler}DATAGUZZ')
                    for x in xmlchunk:
                        xmlcontent.append(x)
                elif len(xmlchunk) == 1:
                    if xmlchunk[0].xpath("local-name()") == "GUZZWFMD":
                        xmlcontent = etree.Element('{http://thermal.cnde.iastate.edu/dataguzzler}DATAGUZZ')
                        xmlcontent.append(xmlchunk[0])
                    else:
                        xmlcontent = xmlchunk[0]
                else:
                    raise self.RendererException("Empty Dataguzzler File")

                extension = os.path.splitext(self._fullpath)[1][1:]
                icon = self._handler_support.GetIcon('application/octet-stream', extension)

                downlink = self.getURL(self._relpath, content_mode="raw", download="true")
                imagelink = self.getURL(self._relpath, content_mode="raw", image="true")

                etree.register_namespace("dbdg", "http://thermal.cnde.iastate.edu/databrowse/dataguzzler")

                xmlroot = etree.Element('{%s}dbdg' % "http://thermal.cnde.iastate.edu/databrowse/dataguzzler", name=os.path.basename(self._relpath), resurl=self._web_support.resurl, downlink=downlink, icon=icon, imagelink=imagelink)
                xmlroot.append(xmlcontent)

                return xmlroot

            elif self._content_mode == "raw":
                if "image" in self._web_support.req.form:
                    if "snapshot" in self._web_support.req.form and "waveform" in self._web_support.req.form:
                        if self.CacheFileExists("SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'png'):
                            size = os.path.getsize(self.getCacheFileName("SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'png'))
                            f = self.getCacheFileHandler('r', "SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'png')
                            contenttype = 'image/png'
                        elif self.CacheFileExists("SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'gif'):
                            size = os.path.getsize(self.getCacheFileName("SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'gif'))
                            f = self.getCacheFileHandler('r', "SNAPSHOT"+str(self._web_support.req.form['snapshot'].value)+"_"+self._web_support.req.form["waveform"].value, 'gif')
                            contenttype = 'image/gif'
                        else:
                            (f, size, contenttype) = self.getSnapshotImage(int(self._web_support.req.form['snapshot'].value), str(self._web_support.req.form["waveform"].value))
                        self._web_support.req.response_headers['Content-Type'] = contenttype
                        self._web_support.req.response_headers['Content-Length'] = str(size)
                        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                        self._web_support.req.output_done = True
                        if 'wsgi.file_wrapper' in self._web_support.req.environ:
                            return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                        else:
                            return iter(lambda: f.read(1024))
                    elif "waveform" in self._web_support.req.form:
                        if self.CacheFileExists("WAVEFORM"+self._web_support.req.form["waveform"].value, 'png'):
                            size = os.path.getsize(self.getCacheFileName("WAVEFORM"+self._web_support.req.form["waveform"].value, 'png'))
                            f = self.getCacheFileHandler('r', "WAVEFORM"+self._web_support.req.form["waveform"].value, 'png')
                            contenttype = 'image/png'
                        elif self.CacheFileExists("WAVEFORM"+self._web_support.req.form["waveform"].value, 'gif'):
                            size = os.path.getsize(self.getCacheFileName("WAVEFORM"+self._web_support.req.form["waveform"].value, 'gif'))
                            f = self.getCacheFileHandler('r', "WAVEFORM"+self._web_support.req.form["waveform"].value, 'gif')
                            contenttype = 'image/gif'
                        else:
                            (f, size, contenttype) = self.getWaveformImage(int(self._web_support.req.form["waveform"].value))
                        self._web_support.req.response_headers['Content-Type'] = contenttype
                        self._web_support.req.response_headers['Content-Length'] = str(size)
                        self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                        self._web_support.req.output_done = True
                        if 'wsgi.file_wrapper' in self._web_support.req.environ:
                            return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                        else:
                            return iter(lambda: f.read(1024))
                    else:
                        raise self.RendererException("No Image Requested")
                else:
                    size = os.path.getsize(self._fullpath)
                    magicstore = magic.open(magic.MAGIC_NONE)
                    magicstore.load()
                    contenttype = magicstore.file(self._fullpath)
                    f = open(self._fullpath, "rb")
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
            else:
                raise self.RendererException("Invalid Content Mode")
            pass

    pass
