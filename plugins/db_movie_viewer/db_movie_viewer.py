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
""" plugins/renderers/db_movie_generic.py - Default Image Renderer """

import os
import os.path
import time
import pwd
import grp
from stat import *
from lxml import etree
from renderer_support import renderer_class
import magic
import Image
import StringIO
from subprocess import Popen, PIPE
import re


class db_movie_viewer(renderer_class):
    """ Default Renderer - Basic Output for Any File """

    _namespace_uri = "http://thermal.cnde.iastate.edu/databrowse/movie"
    _namespace_local = "movie"
    _default_content_mode = "full"
    _default_style_mode = "view_movie"
    _default_recursion_depth = 2

    def stream_generator(self):
        f = open(self._fullpath, 'rb')
        while True:
            block = f.read(1024)
            if not block:
                f.close()
                break
            yield block

    def getContent(self):
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

                src = self.getURL(self._relpath, content_mode="raw", thumbnail="medium")
                href = self.getURL(self._relpath, content_mode="raw")
                downlink = self.getURL(self._relpath, content_mode="raw", download="true")

                xmlroot = etree.Element('{%s}movie' % self._namespace_uri, name=os.path.basename(self._relpath), src=src, href=href, resurl=self._web_support.resurl, downlink=downlink)

                xmlchild = etree.SubElement(xmlroot, "filename")
                xmlchild.text = os.path.basename(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "path")
                xmlchild.text = os.path.dirname(self._fullpath)

                xmlchild = etree.SubElement(xmlroot, "filesize")
                xmlchild.text = self.ConvertUserFriendlySize(file_size)

                xmlchild = etree.SubElement(xmlroot, "mtime")
                xmlchild.text = file_mtime

                xmlchild = etree.SubElement(xmlroot, "ctime")
                xmlchild.text = file_ctime

                xmlchild = etree.SubElement(xmlroot, "atime")
                xmlchild.text = file_atime

                # File Permissions
                xmlchild = etree.SubElement(xmlroot, "permissions")
                xmlchild.text = self.ConvertUserFriendlyPermissions(st[ST_MODE])

                # User and Group
                username = pwd.getpwuid(st[ST_UID])[0]
                groupname = grp.getgrgid(st[ST_GID])[0]
                xmlchild = etree.SubElement(xmlroot, "owner")
                xmlchild.text = "%s:%s" % (username, groupname)

                magicstore = magic.open(magic.MAGIC_MIME)
                magicstore.load()
                contenttype = magicstore.file(self._fullpath)
                xmlchild = etree.SubElement(xmlroot, "contenttype")
                xmlchild.text = contenttype

                probe = Popen(("mplayer", "-identify", "-frames", "0", "-ao", "null", self._fullpath), stdout=PIPE, stderr=PIPE).communicate()[0]
                video_codec = re.search('ID_VIDEO_CODEC=(.+?)\n', probe)
                video_bitrate = re.search('ID_VIDEO_BITRATE=(.+?)\n', probe)
                video_width = re.search('ID_VIDEO_WIDTH=(.+?)\n', probe)
                video_height = re.search('ID_VIDEO_HEIGHT=(.+?)\n', probe)
                video_fps = re.search('ID_VIDEO_FPS=(.+?)\n', probe)
                video_aspect = re.search('ID_VIDEO_ASPECT=(.+?)\n', probe)
                length = re.search('ID_LENGTH=(.+?)\n', probe)
                audio_codec = re.search('ID_AUDIO_CODEC=(.+?)\n', probe)
                audio_rate = re.findall('ID_AUDIO_RATE=(.+?)\n', probe)
                audio_bitrate = re.findall('ID_AUDIO_BITRATE=(.+?)\n', probe)
                audio_nch = re.findall('ID_AUDIO_NCH=(.+?)\n', probe)
                if length:
                    xmlchild = etree.SubElement(xmlroot, "length")
                    xmlchild.text = self.ConvertUserFriendlySize(float(length.group(1)), "time")
                if re.search('Video stream found', probe):
                    videochild = etree.SubElement(xmlroot, "video", video="True")
                    if video_codec:
                        xmlchild = etree.SubElement(videochild, "attr", name="Codec")
                        xmlchild.text = video_codec.group(1)
                    if video_bitrate:
                        xmlchild = etree.SubElement(videochild, "attr", name="Bitrate")
                        xmlchild.text = self.ConvertUserFriendlySize(float(video_bitrate.group(1)), "bitrate", rounding=2)
                    if video_width:
                        xmlchild = etree.SubElement(videochild, "attr", name="Width")
                        xmlchild.text = video_width.group(1)
                    if video_height:
                        xmlchild = etree.SubElement(videochild, "attr", name="Height")
                        xmlchild.text = video_height.group(1)
                    if video_fps:
                        xmlchild = etree.SubElement(videochild, "attr", name="FPS")
                        xmlchild.text = video_fps.group(1)
                    if video_aspect:
                        xmlchild = etree.SubElement(videochild, "attr", name="Aspect Ratio")
                        xmlchild.text = video_aspect.group(1)
                else:
                    videochild = etree.SubElement(xmlroot, "video", video="False")
                if re.search('Audio stream found', probe):
                    audiochild = etree.SubElement(xmlroot, "audio", audio="True")
                    if audio_codec:
                        xmlchild = etree.SubElement(audiochild, "codec")
                        xmlchild.text = audio_codec.group(1)
                    if audio_rate:
                        xmlchild = etree.SubElement(audiochild, "attr", name="Frequency")
                        xmlchild.text = self.ConvertUserFriendlySize(float(audio_rate[-1]), "frequency", rounding=2)
                    if audio_bitrate:
                        xmlchild = etree.SubElement(audiochild, "attr", name="Bitrate")
                        xmlchild.text = self.ConvertUserFriendlySize(float(audio_bitrate[-1]), "bitrate", rounding=2)
                    if audio_nch:
                        xmlchild = etree.SubElement(audiochild, "attr", name="# of Channels")
                        xmlchild.text = audio_nch[-1]
                else:
                    audiochild = etree.SubElement(xmlroot, "audio", audio="False")

                return xmlroot
        elif self._content_mode == "summary" or self._content_mode == "title":
            link = self.getURL(self._relpath)
            src = self.getURL(self._relpath, content_mode="raw", thumbnail="gallery")
            href = self.getURL(self._relpath, content_mode="raw")
            downlink = self.getURL(self._relpath, content_mode="raw", download="true")
            xmlroot = etree.Element('{%s}movie' % self._namespace_uri, name=os.path.basename(self._relpath), link=link, src=src, href=href, downlink=downlink)
            return xmlroot
        elif self._content_mode == "raw":
            magicstore = magic.open(magic.MAGIC_MIME)
            magicstore.load()
            contenttype = magicstore.file(self._fullpath)
            if "thumbnail" in self._web_support.req.form:
                basename = os.path.splitext(os.path.basename(self._fullpath))
                cachedir = os.path.abspath(os.path.dirname(self._fullpath) + "/.databrowse/cache/")
                if self._web_support.req.form['thumbnail'].value == "small":
                    cachefilename = basename[0] + "_small" + basename[1]
                    newsize = (150, 150)
                elif self._web_support.req.form['thumbnail'].value == "medium":
                    cachefilename = basename[0] + "_medium" + basename[1]
                    newsize = (300, 300)
                elif self._web_support.req.form['thumbnail'].value == "large":
                    cachefilename = basename[0] + "_large" + basename[1]
                    newsize = (500, 500)
                elif self._web_support.req.form['thumbnail'].value == "gallery":
                    cachefilename = basename[0] + "_gallery" + basename[1]
                    newsize = (201, 201)
                else:
                    cachefilename = basename[0] + "_small" + basename[1]
                    newsize = (150, 150)
                cachefullpath = os.path.join(cachedir, cachefilename)
                if os.access(cachefullpath, os.R_OK) and os.path.exists(cachefullpath):
                    size = os.path.getsize(cachefullpath)
                    f = open(cachefullpath, "rb")
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.response_headers['Content-Length'] = str(size)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    img = Image.open(self._fullpath)
                    format = img.format
                    img.thumbnail(newsize, Image.ANTIALIAS)
                    output = StringIO.StringIO()
                    img.save(output, format=format)
                    if not os.path.exists(cachedir):
                        os.makedirs(cachedir)
                    f = open(cachefullpath, "wb")
                    img.save(f, format=format)
                    f.close()
                    self._web_support.req.response_headers['Content-Type'] = contenttype
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    return [output.getvalue()]
            else:
                size = os.path.getsize(self._fullpath)
                self._web_support.req.response_headers['Content-Type'] = contenttype
                self._web_support.req.response_headers['Content-Length'] = str(size)
                if "download" in self._web_support.req.form:
                    f = open(self._fullpath, "rb")
                    self._web_support.req.response_headers['Content-Disposition'] = "attachment; filename=" + os.path.basename(self._fullpath)
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    if 'wsgi.file_wrapper' in self._web_support.req.environ:
                        return self._web_support.req.environ['wsgi.file_wrapper'](f, 1024)
                    else:
                        return iter(lambda: f.read(1024))
                else:
                    self._web_support.req.start_response(self._web_support.req.status, self._web_support.req.response_headers.items())
                    self._web_support.req.output_done = True
                    return self.stream_generator()
        else:
            raise self.RendererException("Invalid Content Mode")
        pass

    pass
