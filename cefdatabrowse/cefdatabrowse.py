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
## This material is based on work supported by NASA under Contract           ##
## NNX16CL31C and performed by Iowa State University as a subcontractor      ##
## to TRI Austin.                                                            ##
##                                                                           ##
## Approved for public release by TRI Austin: distribution unlimited;        ##
## 01 June 2018; by Carl W. Magnuson (NDE Division Director).                ##
###############################################################################
""" Main script for the standalone CEFPython based Databrowse Application"""

'''
Usage: cefdatabrowse.py [-h] [-s path] [-e] [-g [path]]

    Databrowse: An Extensible Data Management Platform

    optional arguments:
      -h, --help                    show this help message and exit
      -s path, --setdataroot path   path to set new dataroot
      -e, --openconfig              open cefdatabrowse config file
      -g [path], --go [path]        open cefdatabrowse in a directory
'''

configdict = {}
partydict = {}

from cefpython3 import cefpython as cef
from shutil import copyfile
import pkg_resources
import ctypes
import os
import platform
import sys
import argparse
import subprocess
from re import search
import ConfigParser
from urlparse import urlparse
from urlparse import unquote
import cefdatabrowse_support as dbp


# Load saved cef application settings
def load_settings():
    global configdict, partydict
    config = ConfigParser.ConfigParser()
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse")):
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"))
        configdict.update(dict(config.items('databrowse')))
        partydict.update(dict(config.items('3rdparty')))
    else:
        print("### Alert ###")
        print("### Settings need to be set ###")
        print("### %s ###" % os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"))
        copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse-example"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"))
        subprocess.call(["databrowse", "-e"])
        load_settings()


def save_settings():
    global configdict
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(configdict['install'], "cefdatabrowse/.databrowse"))
    config.set("databrowse", "WIDTH", configdict['width'])
    config.set("databrowse", "HEIGHT", configdict['height'])
    config.set("databrowse", "X", POS_X)
    config.set("databrowse", "Y", POS_Y)
    with open(os.path.join(configdict['install'], "cefdatabrowse/.databrowse"), 'wb') as configfile:
        config.write(configfile)


def update_dataroot(newdataroot):
    global configdict
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"))
    config.set("databrowse", "dataroot", newdataroot)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"), 'wb') as configfile:
        config.write(configfile)
    configdict['dataroot'] = newdataroot


load_settings()

# Handle command line variables
parser = argparse.ArgumentParser(description='Databrowse: An Extensible Data Management Platform')
parser.add_argument('-s', '--setdataroot', metavar='path', help='path to set new dataroot')
parser.add_argument('-e', '--openconfig', action='store_true', help='open cefdatabrowse config file')
parser.add_argument('-g', '--go', metavar='path', const="here", nargs="?", help='open cefdatabrowse in a directory')
args = parser.parse_args()

usr_path = ""
if args.setdataroot:
    try:
        if os.path.exists(args.setdataroot):
            update_dataroot(args.setdataroot)
            print("Updated dataroot to: %s" % configdict['dataroot'])
            sys.exit(0)
    except IndexError:
        print("Dataroot is currently: %s" % configdict['dataroot'])
        sys.exit(0)
elif args.openconfig:
    if platform.system() == "Linux":
        status = os.system('%s %s' % (os.getenv('EDITOR'), os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse")))
        if status != 0:
            if status == 32512:
                raise Exception("%s: EDITOR not set. You need to set the EDITOR environment variable." % status)
            else:
                raise Exception("%s: Could not open config file." % status)
    elif platform.system() == "Windows":
        status = os.system(os.path.join(os.path.dirname(os.path.abspath(__file__)),  ".databrowse"))
        if status != 0:
            raise Exception("%s: Could not open config file." % status)
    else:
        print(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"), "rb").read())
    sys.exit(0)
elif args.go:
    if args.go != "here":
        if os.path.exists(args.go):
            usr_path = args.go
        else:
            raise argparse.ArgumentTypeError('Path does not exist.')
    else:
        usr_path = os.getcwd()
else:
    usr_path = configdict['dataroot']

# GLOBALS
PYQT4 = False
PYQT5 = False
PYSIDE = False

try:
    # noinspection PyUnresolvedReferences
    from PyQt4.QtGui import *
    # noinspection PyUnresolvedReferences
    from PyQt4.QtCore import *

    PYQT4 = True
except ImportError:
    try:
        # noinspection PyUnresolvedReferences
        import PySide
        # noinspection PyUnresolvedReferences
        from PySide import QtCore
        # noinspection PyUnresolvedReferences
        from PySide.QtGui import *
        # noinspection PyUnresolvedReferences
        from PySide.QtCore import *

        PYSIDE = True
    except ImportError:
        try:
            # noinspection PyUnresolvedReferences
            from PyQt5.QtGui import *
            # noinspection PyUnresolvedReferences
            from PyQt5.QtCore import *
            # noinspection PyUnresolvedReferences
            from PyQt5.QtWidgets import *

            PYQT5 = True
        except ImportError:
            print("You need to install one of the following:")
            print("pyqt4")
            print("pyside")
            print("pyqt5")
            sys.exit(1)

# Fix for PyCharm hints warnings when using static methods
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# OS differences
CefWidgetParent = QWidget
configdict['install'] = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
sys.path.insert(0, configdict['install'])
if LINUX and (PYQT4 or PYSIDE):
    # noinspection PyUnresolvedReferences
    CefWidgetParent = QX11EmbedContainer

if WINDOWS:
    myappid = u'limatix.org.databrowse'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    scheme = "http://0.0.0.0/"
elif LINUX:
    scheme = "http://databrowse/"

# Append external libraries to path
for item in partydict.keys():
    sys.path.insert(0, partydict[item])


# Modified client handler from cefpython31/cefpython/cef3/linux/binaries_32bit/wxpython-response.py
# Differentiates between resources and files that databrowse can analyze.
# Parses web payloads and loads them into a python dictionary (replaces environ)
class ClientHandler:
    # RequestHandler.GetResourceHandler()
    def GetResourceHandler(self, browser, frame, request):
        # Called on the IO thread before a resource is loaded.
        # To allow the resource to load normally return None.
        # print("GetResourceHandler(): url = %s" % request.GetUrl())
        parsedurl = urlparse(request.GetUrl())

        if parsedurl.netloc != urlparse(scheme).netloc:
            return None

        fullpath = unquote(parsedurl.path[1:])

        urlparams = {}
        if parsedurl.query != "":
            # print("Parsed params: %s" % parsedurl.query.split("&"))
            paramdata = parsedurl.query.split("&")
            for paramone in paramdata:
                if '=' in paramone:
                    key, value = paramone.split('=')
                    urlparams[key] = value
                else:
                    urlparams[paramone] = paramone

        fs = request.GetPostData()
        # Especially uploaded files because of this:
        # [0608/110311.456:ERROR:request_impl.cc(785)] NOT IMPLEMENTED multi-part form data is not supported
        if len(fs) > 0:
            if type(fs) is list:
                if len(fs) == 1:
                    form = fs[0]
                    form_dict = {}
                    boundary = search(r".+?(?=\r\n)", form).group(0)
                    splitform = form.split(boundary)
                    for frag in splitform:
                        try:
                            name = search(r"(?<= name=)\"([^\"]*)\"", frag).group(0).strip('\"')
                            content = search(r"\r\n\r\n((.|\r\n)*)\r\n", frag).group(1)
                            form_dict[name] = content
                        except AttributeError:
                            pass
                    urlparams.update(form_dict)
                else:
                    form = fs[0]
                    form_dict = {}
                    name = search(r"(?<= name=)\"([^\"]*)\"", form).group(0).strip('\"')
                    form_dict[name] = {}
                    form_dict[name]['name'] = name
                    form_dict[name]['filename'] = search(r"(?<= filename=)\"([^\"]*)\"", form).group(0).strip('\"')
                    form_dict[name]['type'] = "multipart/form-data"
                    upfile = open(fs[1][1:], 'rb')
                    form_dict[name]['file'] = upfile
                    form_dict[name]['value'] = upfile.read()
                    form_dict[name]['boundary'] = search(r"-([^\"]*)(?=\--)", fs[-1]).group(0)
                    urlparams.update(form_dict)
            else:
                urlparams.update(fs)

        # Any resource files must be located in the databrowse_wsgi directory in the databrowse root source directory
        resHandler = DatabrowseHandler()
        resHandler._clientHandler = self
        resHandler._browser = browser
        resHandler._frame = frame
        resHandler._request = request
        resHandler._fullpath = fullpath
        resHandler._params = urlparams
        self._AddStrongReference(resHandler)
        return resHandler

    def _OnResourceResponse(self, browser, fullpath, frame, request, requestStatus,
            requestError, response, urlparams, data):
        # This callback is emulated through ResourceHandler
        # and WebRequest. Real "OnResourceResponse" is not yet
        # available in CEF 3 (as of CEF revision 1450). See
        # issue 515 in the CEF Issue Tracker:
        # https://code.google.com/p/chromiumembedded/issues/detail?id=515
        # ----
        # requestStatus => cefpython.WebRequest.Status
        #     {"Unknown", "Success", "Pending", "Canceled", "Failed"}
        # For "file://" requests the status will be "Unknown".
        # requestError => see the NetworkError wiki page
        # response.GetStatus() => http status code
        # print("_OnResourceResponse()")
        # print("data length = %s" % len(data))
        # Return the new data - you can modify it.

        # Call the databrowse library and return the generated html
        if "databrowse_wsgi" not in fullpath:
            databrowsepaths = {'install': configdict['install'], 'path': fullpath, 'scheme': scheme}
            databrowsepaths.update(configdict)
            params = databrowsepaths.copy()
            params.update(urlparams)
            html = dbp.application(fullpath, params)
            data = "".join(html[0])
            urlparams.update({'headers': html[1], "status": html[2]})
            # if "operation" in urlparams:
            #     browser.Reload()
        else:
            try:
                html = open(unquote(fullpath), "rb")
            except IOError:
                if not os.path.exists(unquote(fullpath)):
                    raise IOError("Invalid path: %s" % unquote(fullpath))
                else:
                    if os.path.isdir(unquote(fullpath)):
                        html = ""
                    else:
                        raise IOError("Unknown problem")
            mime = response.GetMimeType()
            urlparams.update({'headers': {'Content-Type': mime}, "status": 200})
            data = "".join(html)

        return data

    # A strong reference to ResourceHandler must be kept
    # during the request. Some helper functions for that.
    # 1. Add reference in GetResourceHandler()
    # 2. Release reference in ResourceHandler.ReadResponse()
    #    after request is completed.

    _resourceHandlers = {}
    _resourceHandlerMaxId = 0

    def _AddStrongReference(self, resHandler):
        self._resourceHandlerMaxId += 1
        resHandler._resourceHandlerId = self._resourceHandlerMaxId
        self._resourceHandlers[resHandler._resourceHandlerId] = resHandler

    def _ReleaseStrongReference(self, resHandler):
        if resHandler._resourceHandlerId in self._resourceHandlers:
            del self._resourceHandlers[resHandler._resourceHandlerId]
        else:
            print("_ReleaseStrongReference() FAILED: resource handler not found, id = %s" % (resHandler._resourceHandlerId))


# Adapted resource handler to deal with the returned start resposne variables from databrowse
# Based on the resource handler in cefpython31/cefpython/cef3/linux/binaries_32bit/wxpython-response.py
class DatabrowseHandler:

    # The methods of this class will always be called
    # on the IO thread.

    _resourceHandlerId = None
    _clientHandler = None
    _browser = None
    _frame = None
    _request = None
    _responseHeadersReadyCallback = None
    _web_request = None
    _webRequestClient = None
    _params = None
    _fullpath = None
    _offsetRead = 0

    def ProcessRequest(self, request, callback):
        # print("Databrowse called")
        # print("ProcessRequest()")
        # 1. Start the request using WebRequest
        # 2. Return True to handle the request
        # 3. Once response headers are ready call
        #    callback.Continue()
        self._responseHeadersReadyCallback = callback
        self._webRequestClient = WebRequestClient()
        self._webRequestClient._resourceHandler = self
        # Need to set AllowCacheCredentials and AllowCookies for
        # the cookies to work during POST requests (Issue 127).
        # To skip cache set the SkipCache request flag.
        request.SetFlags(cef.Request.Flags["AllowCachedCredentials"]\
                | cef.Request.Flags["AllowCookies"])
        # A strong reference to the WebRequest object must kept.
        self._web_request = cef.WebRequest.Create(
                request, self._webRequestClient)
        return True

    def GetResponseHeaders(self, response, responseLengthOut, redirectUrlOut):
        # print("GetResponseHeaders()")
        # 1. If the response length is not known set
        #    responseLengthOut[0] to -1 and ReadResponse()
        #    will be called until it returns False.
        # 2. If the response length is known set
        #    responseLengthOut[0] to a positive value
        #    and ReadResponse() will be called until it
        #    returns False or the specified number of bytes
        #    have been read.
        # 3. Use the |response| object to set the mime type,
        #    http status code and other optional header values.
        # 4. To redirect the request to a new URL set
        #    redirectUrlOut[0] to the new url.
        assert self._webRequestClient._response, "Response object empty"
        wrcResponse = self._webRequestClient._response
        response.SetMimeType(self._params["headers"]["Content-Type"])
        response.SetStatus(200)
        response.SetStatusText(wrcResponse.GetStatusText())
        response.SetHeaderMap(self._params["headers"])
        if wrcResponse.GetHeaderMultimap():
            response.SetHeaderMultimap(wrcResponse.GetHeaderMultimap())
        responseLengthOut[0] = self._webRequestClient._dataLength
        if not responseLengthOut[0]:
            # Probably a cached page? Or a redirect?
            pass

    def ReadResponse(self, data_out, bytes_to_read, bytes_read_out, callback):
        # print("ReadResponse()")
        # 1. If data is available immediately copy up to
        #    bytes_to_read bytes into data_out[0], set
        #    bytes_read_out[0] to the number of bytes copied,
        #    and return true.
        # 2. To read the data at a later time set
        #    bytes_read_out[0] to 0, return true and call
        #    callback.Continue() when the data is available.
        # 3. To indicate response completion return false.
        if self._offsetRead < self._webRequestClient._dataLength:
            dataChunk = self._webRequestClient._data[\
                    self._offsetRead:(self._offsetRead + bytes_to_read)]
            self._offsetRead += len(dataChunk)
            data_out[0] = dataChunk
            bytes_read_out[0] = len(dataChunk)
            return True
        self._clientHandler._ReleaseStrongReference(self)
        print("no more data, return False")
        return False

    def CanGetCookie(self, cookie):
        # Return true if the specified cookie can be sent
        # with the request or false otherwise. If false
        # is returned for any cookie then no cookies will
        # be sent with the request.
        return True

    def CanSetCookie(self, cookie):
        # Return true if the specified cookie returned
        # with the response can be set or false otherwise.
        return True

    def Cancel(self):
        # Request processing has been canceled.
        pass


# Web request client as described in cefpython31/cefpython/cef3/linux/binaries_32bit/wxpython-response.py
class WebRequestClient:

    _resourceHandler = None
    _data = ""
    _dataLength = -1
    _response = None

    def OnUploadProgress(self, web_request, current, total):
        pass

    def OnDownloadProgress(self, web_request, current, total):
        pass

    def OnDownloadData(self, web_request, data):
        # print("OnDownloadData()")
        self._data += data

    def OnRequestComplete(self, web_request):
        # print("OnRequestComplete()")
        cef.WebRequest.Status = {"Unknown", "Success",
                 "Pending", "Canceled", "Failed"}
        statusText = "Unknown"
        if web_request.GetRequestStatus() in cef.WebRequest.Status:
            statusText = cef.WebRequest.Status[web_request.GetRequestStatus()]
        # Emulate OnResourceResponse() in ClientHandler:
        self._response = web_request.GetResponse()
        # Are web_request.GetRequest() and
        # self._resourceHandler._request the same? What if
        # there was a redirect, what will GetUrl() return
        # for both of them?
        self._data = self._resourceHandler._clientHandler._OnResourceResponse(
                self._resourceHandler._browser,
                self._resourceHandler._fullpath,
                self._resourceHandler._frame,
                web_request.GetRequest(),
                web_request.GetRequestStatus(),
                web_request.GetRequestError(),
                web_request.GetResponse(),
                self._resourceHandler._params,
                self._data)
        self._dataLength = len(self._data)
        # ResourceHandler.GetResponseHeaders() will get called
        # after _responseHeadersReadyCallback.Continue() is called.
        self._resourceHandler._responseHeadersReadyCallback.Continue()


# Main CEF function to initialize run and shutdown the CEF application
def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # Required chromium commandline arguments:
    # Needed to allow local file operations and access
    commandlineargs = {'allow-file-access-from-files': '', 'disable-web-security': ''}
    cef.Initialize(None, commandlineargs)
    app = CefApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.activateWindow()
    main_window.raise_()
    main_window.setAttribute(Qt.WA_DeleteOnClose, True)
    app.exec_()
    app.stopTimer()
    del main_window  # Just to be safe, similarly to "del app"
    del app  # Must destroy app object before calling Shutdown
    save_settings()
    cef.Shutdown()


# Check graphical framework version and CEFPython version
def check_versions():
    # print("[qt.py] Databrowse {ver}".format(ver=pkg_resources.require("databrowse")[0].version))
    print("[qt.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[qt.py] Python {ver} {arch}".format(
            ver=platform.python_version(), arch=platform.architecture()[0]))
    if PYQT4 or PYQT5:
        print("[qt.py] PyQt {v1} (qt {v2})".format(
              v1=PYQT_VERSION_STR, v2=qVersion()))
    elif PYSIDE:
        print("PyQt4 or PyQt5 is preferred.")
        print("[qt.py] PySide {v1} (qt {v2})".format(
              v1=PySide.__version__, v2=QtCore.__version__))
    # CEF Python version requirement
    assert cef.__version__ >= "57.0", "CEF Python v55.4+ required to run this"


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.cef_widget = None
        self.navigation_bar = None
        self.setWindowTitle("Databrowse")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setupLayout()

    def setupLayout(self):
        self.resize(int(configdict['width']), int(configdict['height']))
        self.cef_widget = CefWidget(self)
        self.navigation_bar = NavigationBar(self.cef_widget)
        layout = QGridLayout()

        openAction = QAction("&Open", self)
        openAction.setStatusTip('Open file')
        openAction.triggered.connect(self.openfile)

        settingsAction = QAction("&Settings", self)
        settingsAction.setStatusTip('Open settings file')
        settingsAction.triggered.connect(self.settings)

        helpAction = QAction("&Help", self)
        helpAction.setStatusTip('Open Manual')
        helpAction.triggered.connect(self.opendoc)

        closeAction = QAction("&Close", self)
        closeAction.setStatusTip('Close Databrowse')
        closeAction.triggered.connect(self.closeapp)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(helpAction)
        fileMenu.addAction(closeAction)

        layout.addWidget(self.navigation_bar, 0, 0)
        layout.addWidget(self.cef_widget, 1, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        frame = QFrame()
        frame.setLayout(layout)
        self.setCentralWidget(frame)

        if PYQT5 and WINDOWS:
            # On Windows with PyQt5 main window must be shown first
            # before CEF browser is embedded, otherwise window is
            # not resized and application hangs during resize.
            self.show()

        # Browser can be embedded only after layout was set up
        self.cef_widget.embedBrowser()

        if PYQT5 and LINUX:
            # On Linux with PyQt5 the QX11EmbedContainer widget is
            # no more available. An equivalent in Qt5 is to create
            # a hidden window, embed CEF browser in it and then
            # create a container for that hidden window and replace
            # cef widget in the layout with the container.
            # noinspection PyUnresolvedReferences, PyArgumentList
            self.container = QWidget.createWindowContainer(
                    self.cef_widget.hidden_window, parent=self)
            # noinspection PyArgumentList
            layout.addWidget(self.container, 1, 0)

    def closeapp(self):
        # Close browser (force=True) and free CEF reference
        if self.cef_widget.browser:
            self.cef_widget.browser.CloseBrowser(True)
            self.clear_browser_references()
            self.close()

    def closeEvent(self, event):
        # Close browser (force=True) and free CEF reference
        if self.cef_widget.browser:
            self.cef_widget.browser.CloseBrowser(True)
            self.clear_browser_references()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.cef_widget.browser = None

    def opendoc(self):
        subprocess.Popen(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + '/resources/Manual.pdf', shell=True)

    def openfile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", configdict['dataroot'],
                                                  "All Files (*)", options=options)
        if fileName:
            self.cef_widget.browser.LoadUrl(scheme + fileName)

    def settings(self):
        status = -1
        if platform.system() == "Linux":
            status = os.system('%s %s' % (
                os.getenv('EDITOR'), os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse")))
            if status != 0:
                if status == 32512:
                    print("%s: EDITOR not set. You need to set the EDITOR environment variable." % status)
                else:
                    print("%s: Could not open config file." % status)
        elif platform.system() == "Windows":
            status = os.system(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"))
            if status != 0:
                print("%s: Could not open config file." % status)
        else:
            print(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".databrowse"), "rb").read())
        if status == 0:
            load_settings()
            for item in partydict.keys():
                sys.path.insert(0, partydict[item])
            self.cef_widget.browser.LoadUrl(scheme + configdict['dataroot'])


class CefWidget(CefWidgetParent):
    def __init__(self, parent=None):
        super(CefWidget, self).__init__(parent)
        self.parent = parent
        self.browser = None
        self.hidden_window = None  # Required for PyQt5 on Linux
        self.show()

    def focusInEvent(self, event):
        # This event seems to never get called on Linux, as CEF is
        # stealing all focus due to Issue #284
        # https://github.com/cztomczak/cefpython/issues/284.
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSetFocus(self.getHandle(), 0, 0, 0)
            self.browser.SetFocus(True)

    def focusOutEvent(self, event):
        # This event seems to never get called on Linux, as CEF is
        # stealing all focus due to Issue #284
        # https://github.com/cztomczak/cefpython/issues/284.
        if self.browser:
            self.browser.SetFocus(False)

    def embedBrowser(self):
        if PYQT5 and LINUX:
            # noinspection PyUnresolvedReferences
            self.hidden_window = QWindow()
        window_info = cef.WindowInfo()
        rect = [0, 0, self.width(), self.height()]
        window_info.SetAsChild(self.getHandle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=scheme + usr_path)
        self.browser.SetClientHandler(ClientHandler())
        self.browser.SetClientHandler(LoadHandler(self.parent.navigation_bar))
        self.browser.SetClientHandler(FocusHandler(self))

    def getHandle(self):
        if self.hidden_window:
            # PyQt5 on Linux
            return int(self.hidden_window.winId())
        try:
            # PyQt4 and PyQt5
            return int(self.winId())
        except:
            # PySide:
            # | QWidget.winId() returns <PyCObject object at 0x02FD8788>
            # | Converting it to int using ctypes.
            if sys.version_info[0] == 2:
                # Python 2
                ctypes.pythonapi.PyCObject_AsVoidPtr.restype = (
                        ctypes.c_void_p)
                ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = (
                        [ctypes.py_object])
                return ctypes.pythonapi.PyCObject_AsVoidPtr(self.winId())
            else:
                # Python 3
                ctypes.pythonapi.PyCapsule_GetPointer.restype = (
                        ctypes.c_void_p)
                ctypes.pythonapi.PyCapsule_GetPointer.argtypes = (
                        [ctypes.py_object])
                return ctypes.pythonapi.PyCapsule_GetPointer(
                        self.winId(), None)

    def moveEvent(self, event):
        global POS_X, POS_Y
        self.x = 0
        self.y = 0
        POS_X = self.x
        POS_Y = self.y
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(self.x, self.y,
                                       self.width(), self.height())
            self.browser.NotifyMoveOrResizeStarted()

    def resizeEvent(self, event):
        global configdict
        size = event.size()
        configdict['width'] = self.window().size().width()
        configdict['height'] = self.window().size().height()
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(self.x, self.y,
                                       size.width(), size.height())
            self.browser.NotifyMoveOrResizeStarted()


class CefApplication(QApplication):
    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.timer = self.createTimer()
        self.setupIcon()

    def createTimer(self):
        timer = QTimer()
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.onTimer)
        timer.start(10)
        return timer

    def onTimer(self):
        cef.MessageLoopWork()

    def stopTimer(self):
        # Stop the timer after Qt's message loop has ended
        self.timer.stop()

    def setupIcon(self):
        icon_file = os.path.join(configdict['install'] + "/cefdatabrowse/resources/", "{0}.png".format("icon256"))
        if os.path.exists(icon_file):
            self.setWindowIcon(QIcon(icon_file))


class LoadHandler(object):
    def __init__(self, navigation_bar):
        self.initial_app_loading = True
        self.navigation_bar = navigation_bar

    def OnLoadingStateChange(self, **_):
        self.navigation_bar.updateState()

    def OnLoadStart(self, browser, **_):
        self.navigation_bar.url.setText(unquote(browser.GetUrl().replace(scheme, "")))
        if self.initial_app_loading:
            self.navigation_bar.cef_widget.setFocus()
            # Temporary fix no. 2 for focus issue on Linux (Issue #284)
            if LINUX:
                pass
                # print("[qt.py] LoadHandler.OnLoadStart:"
                #       " keyboard focus fix no. 2 (Issue #284)")
                # browser.SetFocus(True)        -- Seems like this isn't necessary
            self.initial_app_loading = False


class FocusHandler(object):
    def __init__(self, cef_widget):
        self.cef_widget = cef_widget

    def OnSetFocus(self, **_):
        pass

    def OnGotFocus(self, browser, **_):
        # Temporary fix no. 1 for focus issues on Linux (Issue #284)
        if LINUX:
            # print("[qt.py] FocusHandler.OnGotFocus:"
            #       " keyboard focus fix no. 1 (Issue #284)")
            browser.SetFocus(True)


class NavigationBar(QFrame):
    def __init__(self, cef_widget):
        super(NavigationBar, self).__init__()
        self.cef_widget = cef_widget

        # Init layout
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Back button
        self.back = self.createButton("back")
        # noinspection PyUnresolvedReferences
        self.back.clicked.connect(self.onBack)
        layout.addWidget(self.back, 0, 0)

        # Forward button
        self.forward = self.createButton("forward")
        # noinspection PyUnresolvedReferences
        self.forward.clicked.connect(self.onForward)
        layout.addWidget(self.forward, 0, 1)

        # Reload button
        self.reload = self.createButton("reload")
        # noinspection PyUnresolvedReferences
        self.reload.clicked.connect(self.onReload)
        layout.addWidget(self.reload, 0, 2)

        # Url input
        self.url = QLineEdit("")
        # noinspection PyUnresolvedReferences
        self.url.returnPressed.connect(self.onGoUrl)
        layout.addWidget(self.url, 0, 3)

        # Layout
        self.setLayout(layout)
        self.updateState()

    def onBack(self):
        if self.cef_widget.browser:
            self.cef_widget.browser.GoBack()

    def onForward(self):
        if self.cef_widget.browser:
            self.cef_widget.browser.GoForward()

    def onReload(self):
        if self.cef_widget.browser:
            self.cef_widget.browser.Reload()

    def onGoUrl(self):
        if self.cef_widget.browser:
            url = str(self.url.text())
            parse_text = urlparse(url)
            if parse_text.netloc == "":
                self.url.setText(scheme + url)
            self.cef_widget.browser.LoadUrl(str(self.url.text()))

    def updateState(self):
        browser = self.cef_widget.browser
        if not browser:
            self.back.setEnabled(False)
            self.forward.setEnabled(False)
            self.reload.setEnabled(False)
            self.url.setEnabled(False)
            return
        self.back.setEnabled(browser.CanGoBack())
        self.forward.setEnabled(browser.CanGoForward())
        self.reload.setEnabled(True)
        self.url.setEnabled(True)
        self.url.setText(unquote(browser.GetUrl().replace(scheme, "")))

    def createButton(self, name):
        resources = configdict['install'] + "/cefdatabrowse/resources"
        pixmap = QPixmap(os.path.join(resources, "{0}.png".format(name)))
        icon = QIcon(pixmap)
        button = QPushButton()
        button.setIcon(icon)
        button.setIconSize(pixmap.rect().size())
        return button


if __name__ == '__main__':
    main()
