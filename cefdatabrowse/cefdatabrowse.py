# Copyright (c) 2012 The CEF Python authors - see the Authors file.
# All rights reserved. Licensed under the BSD 3-clause license.
# See project website: https://github.com/cztomczak/cefpython
#
# This product includes the following third party libraries:
# * Chromium Embedded Framework licensed under the BSD 3-clause
#   license. Website: https://bitbucket.org/chromiumembedded/cef
#
# Redistribution and use in source and binary forms, with
# or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above
#   copyright notice, this list of conditions and the
#   following disclaimer.
#
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the
#   following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#
# * Neither the name of Google Inc. nor the name Chromium
#   Embedded Framework nor the name of CEF Python nor the
#   names of its contributors may be used to endorse or
#   promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

WIDTH, HEIGHT, POS_X, POS_Y, dataroot, dataguzzlerlib = (800, 600, 0, 0, "/", None)

from cefpython3 import cefpython as cef
import ctypes
import os
import platform
import sys
import ConfigParser
from urlparse import urlparse
from urlparse import unquote
import cefdatabrowse_support as dbp


def load_settings():
    global WIDTH, HEIGHT, dataroot, POS_X, POS_Y, dataguzzlerlib
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"))
    WIDTH = config.getint("databrowse", "WIDTH")
    HEIGHT = config.getint("databrowse", "HEIGHT")
    POS_X = config.getint("databrowse", "X")
    POS_Y = config.getint("databrowse", "Y")
    dataroot = config.get("databrowse", "dataroot")
    dataguzzlerlib = config.get("databrowse", "dataguzzlerlib")


def save_settings():
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"))
    config.set("databrowse", "WIDTH", WIDTH)
    config.set("databrowse", "HEIGHT", HEIGHT)
    config.set("databrowse", "X", POS_X)
    config.set("databrowse", "Y", POS_Y)
    with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"), 'wb') as configfile:
        config.write(configfile)


def update_dataroot(newdataroot):
    global dataroot
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"))
    config.set("databrowse", "dataroot", newdataroot)
    with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"), 'wb') as configfile:
        config.write(configfile)
    dataroot = newdataroot


load_settings()

usr_path = ""
try:
    if sys.argv[1] is not None:
        if sys.argv[1] == "-s":
            try:
                if sys.argv[2] is not None:
                    if os.path.exists(sys.argv[2]):
                        update_dataroot(sys.argv[2])
                        print("Updated dataroot to: %s" % dataroot)
                        sys.exit(0)
            except IndexError:
                print("Dataroot is currently: %s" % dataroot)
                sys.exit(0)
        elif sys.argv[1] == "-e":
            if platform.system() == "Linux":
                status = os.system('%s %s' % (os.getenv('EDITOR'), os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse")))
                if status != 0:
                    if status == 32512:
                        raise Exception("%s: EDITOR not set" % status)
                    else:
                        raise Exception("%s: Could not open config file." % status)
            elif platform.system() == "Windows":
                status = os.system(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"))
                if status != 0:
                    raise Exception("%s: Could not open config file." % status)
            else:
                print(open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), "databrowse_app/.databrowse"), "rb").read())
            sys.exit(0)
        else:
            if os.path.exists(sys.argv[1]):
                usr_path = os.path.splitdrive(sys.argv[1])[1]
            else:
                usr_path = dataroot
except IndexError:
    pass

if usr_path == "":
    usr_path = os.path.splitdrive(os.getcwd())[1]

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
except Exception:
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
    except Exception:
        try:
            # noinspection PyUnresolvedReferences
            from PyQt5.QtGui import *
            # noinspection PyUnresolvedReferences
            from PyQt5.QtCore import *
            # noinspection PyUnresolvedReferences
            from PyQt5.QtWidgets import *

            PYQT5 = True
        except Exception:
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

# Configuration
scheme = "file://127.0.0.1"

# OS differences
CefWidgetParent = QWidget
if LINUX and (PYQT4 or PYSIDE):
    install = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
    sys.path.insert(0, install)
    # noinspection PyUnresolvedReferences
    CefWidgetParent = QX11EmbedContainer

if WINDOWS:
    install = os.path.splitdrive(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[1]
    sys.path.insert(0, install)
sys.path.insert(0, dataguzzlerlib)


class ClientHandler:

    # RequestHandler.GetResourceHandler()
    def GetResourceHandler(self, browser, frame, request):
        # Called on the IO thread before a resource is loaded.
        # To allow the resource to load normally return None.
        # print("GetResourceHandler(): url = %s" % request.GetUrl())
        parsedurl = urlparse(request.GetUrl())

        if parsedurl.netloc != urlparse(scheme).netloc:
            return None

        if LINUX:
            relpath = os.path.relpath(parsedurl.path)
            fullpath = os.path.abspath(parsedurl.path)
        elif WINDOWS:
            relpath = os.path.relpath(parsedurl.path)
            fullpath = os.path.splitdrive(os.path.abspath(parsedurl.path))[1]
        else:
            relpath = None
            fullpath = None

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
        # Handle editing of text files here
        if type(fs) == list:
            text = fs[0].split("\r\n")
            text = text[3:-2]
            text = "\r\n".join(text)
            urlparams.update({'extra': fs[0], 'file': text})
        else:
            urlparams.update({"extra": ""})
            urlparams.update(fs)

        if "databrowse_wsgi" not in fullpath:
            resHandler = DatabrowseHandler()
            resHandler._clientHandler = self
            resHandler._browser = browser
            resHandler._frame = frame
            resHandler._request = request
            resHandler._fullpath = fullpath
            resHandler._relpath = relpath
            resHandler._params = urlparams
            self._AddStrongReference(resHandler)
            return resHandler
        else:
            resHandler = ResourceHandler()
            resHandler._clientHandler = self
            resHandler._browser = browser
            resHandler._frame = frame
            resHandler._request = request
            resHandler._fullpath = fullpath
            resHandler._relpath = relpath
            self._AddStrongReference(resHandler)
            return resHandler

    def _OnResourceResponse(self, handler, browser, fullpath, frame, request, requestStatus,
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
        if handler is "cefdatabrowse":
            databrowsepaths = {'dataroot': dataroot, 'install': install, 'path': fullpath}
            params = databrowsepaths.copy()
            params.update(urlparams)
            html = dbp.application(fullpath, params)
            # print("STATUS: %s" % html[2])
            data = "".join(html[0])
            urlparams.update({'headers': html[1], "status": html[2]})
            # print("HTML Ouput: %s" % data)
            if "operation" in urlparams:
                browser.Reload()
        else:
            try:
                html = open(fullpath, "rb")
            except IOError:
                if not os.path.exists(fullpath):
                    import pdb
                    pdb.set_trace()
                    raise IOError("Install location needs to be updated")
                else:
                    print("Different problem")
                    raise IOError
            mime = response.GetMimeType()
            urlparams.update({'headers': {'Content-Type': mime}})
            data = "".join(html)

        # print("HTML Ouput: %s" % data)
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


class ResourceHandler:

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
    _params = {}
    _fullpath = None
    _relpath = None
    _offsetRead = 0

    def ProcessRequest(self, request, callback):
        # print("Resource called")
        # print("ProcessRequest()")
        # 1. Start the request using WebRequest
        # 2. Return True to handle the request
        # 3. Once response headers are ready call
        #    callback.Continue()
        self._responseHeadersReadyCallback = callback
        self._webRequestClient = WebRequestClient()
        self._webRequestClient._resourceHandler = self
        self._webRequestClient._filetype = "resource"
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
        response.SetStatus(wrcResponse.GetStatus())
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
    _relpath = None
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
        self._webRequestClient._filetype = "cefdatabrowse"
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
        # print("Mimetype: %s" % response.GetMimeType())
        # print("Headers: %s" % response.GetHeaderMultimap())
        # print("Details: %s" % self._params)
        response.SetMimeType(self._params["headers"]["Content-Type"])
        response.SetStatus(self._params["status"][0])
        response.SetStatusText(wrcResponse.GetStatusText())
        response.SetHeaderMap(self._params["headers"])
        # response.SetHeaderMap({"": self._params["params"]["extra"]})
        # print("HEADERS####: %s" % self._params["headers"])
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


class WebRequestClient:

    _resourceHandler = None
    _filetype = None
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
        # print("status = %s" % statusText)
        # print("error code = %s" % web_request.GetRequestError())
        # Emulate OnResourceResponse() in ClientHandler:
        self._response = web_request.GetResponse()
        # Are web_request.GetRequest() and
        # self._resourceHandler._request the same? What if
        # there was a redirect, what will GetUrl() return
        # for both of them?
        self._data = self._resourceHandler._clientHandler._OnResourceResponse(
                self._filetype,
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


def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
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


def check_versions():
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
    assert cef.__version__ >= "55.4", "CEF Python v55.4+ required to run this"


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.cef_widget = None
        self.navigation_bar = None
        self.setWindowTitle("Databrowse")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setupLayout()

    def setupLayout(self):
        self.resize(WIDTH, HEIGHT)
        self.cef_widget = CefWidget(self)
        self.navigation_bar = NavigationBar(self.cef_widget)
        layout = QGridLayout()
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

    def closeEvent(self, event):
        # Close browser (force=True) and free CEF reference
        if self.cef_widget.browser:
            self.cef_widget.browser.CloseBrowser(True)
            self.clear_browser_references()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.cef_widget.browser = None


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
        global WIDTH, HEIGHT
        size = event.size()
        WIDTH = self.window().size().width()
        HEIGHT = self.window().size().height()
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
        icon_file = os.path.join(install + "/databrowse_app/resources", "{0}.png".format("pyside"))
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
                print("[qt.py] LoadHandler.OnLoadStart:"
                      " keyboard focus fix no. 2 (Issue #284)")
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
            print("[qt.py] FocusHandler.OnGotFocus:"
                  " keyboard focus fix no. 1 (Issue #284)")
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
            if url.startswith("/"):
                parse_text = urlparse(url)

                if parse_text.scheme == "":
                    self.url.setText(scheme + url)
                else:
                    self.url.setText(url)
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
        resources = install + "/databrowse_app/resources"
        pixmap = QPixmap(os.path.join(resources, "{0}.png".format(name)))
        icon = QIcon(pixmap)
        button = QPushButton()
        button.setIcon(icon)
        button.setIconSize(pixmap.rect().size())
        return button


if __name__ == '__main__':
    main()
