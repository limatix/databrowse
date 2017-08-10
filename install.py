# Import PySide classes
import sys
import os
import urllib
import zipfile
from PySide.QtCore import *
from PySide.QtGui import *

# Configuration
WIDTH = 800
HEIGHT = 600

# Create the QApplication object
qt_app = QApplication(sys.argv)


class Install(QWidget):
    """  """
    def __init__(self):
        # Initialize the object as a QLabel
        self.main = QWidget.__init__(self)

        # Set the size, alignment, and title
        # self.setFixedSize(QSize(WIDTH, HEIGHT))
        self.setWindowTitle('Databrowse Install GUI')

        self.title = QLabel("Databrowse - Iowa State University")
        self.title.setAlignment(Qt.AlignHCenter)

        self.select_path = QPushButton("Install Location", self)
        self.select_path.setFixedWidth(145)
        self.select_path.clicked.connect(self.opendirdialog)

        self.path_text = QLabel("Select an install directory")
        self.path = None

        self.install = QPushButton("Install", self)
        self.install.setFixedWidth(145)
        self.install.clicked.connect(self.confirm_install)

        self.cancel = QPushButton("Cancel", self)
        self.cancel.setFixedWidth(145)
        self.cancel.clicked.connect(self.cancel_app)

        self.license = QPushButton("License", self)
        self.license.setFixedWidth(145)
        self.license.clicked.connect(self.license_app)

        self.output_area = QScrollArea(self)
        self.output_area.setFixedSize(self.size().width(), 100)
        self.output_text = QLabel("")
        self.output_text.setFixedSize(self.output_area.size())
        self.output_area.setWidget(self.output_text)

        self.layout_menu = QFormLayout(self)

        self.layout_menu.addRow(self.title)
        self.layout_menu.addRow(self.select_path, self.path_text)
        self.layout_menu.addRow(self.install, self.cancel)
        self.layout_menu.addRow(self.license)
        self.layout_menu.addRow(self.output_area)

        # Initialize license window
        self.license_window = QWidget()
        self.license_window.setWindowTitle("GPL Pyside License")

        self.scrollarea = QScrollArea(self.license_window)
        self.license_text = QLabel(open("COPYING").read(), self.license_window)
        self.scrollarea.setWidget(self.license_text)

        # Initialize confirmation window
        self.conf_window = QWidget()
        self.conf_window.setWindowTitle("Confirm")

        self.confirm_message = QLabel("Are you sure you want to install here:", self.conf_window)

        self.path_text_conf = QLabel("")

        self.conf_pos = QPushButton("Confirm", self.conf_window)
        self.conf_pos.clicked.connect(self.installdatabrowse)
        self.conf_pos.setFixedWidth(70)

        self.conf_neg = QPushButton("Cancel", self.conf_window)
        self.conf_neg.clicked.connect(self.cancel_app)
        self.conf_neg.setFixedWidth(70)

        self.conf_layout = QFormLayout(self.conf_window)
        self.conf_layout.addRow(self.confirm_message)
        self.conf_layout.addRow(self.path_text_conf)
        self.conf_layout.addRow(self.conf_pos, self.conf_neg)

    def opendirdialog(self):
        """ Opens a dialog to allow user to choose a directory """
        flags = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        self.path = directory = QFileDialog.getExistingDirectory(self, "Open Directory", os.getcwd(), flags)
        self.path_text.setText(self.path)
        self.path_text_conf.setText(self.path)

    def installdatabrowse(self):
        self.conf_window.close()
        self.output_text.resize(self.output_area.size())

        self.output_text.setText(self.output_text.text() + ">Gathering files from Github\r\n")
        self.output_text.repaint()
        qt_app.processEvents()
        filename = os.path.join(self.path, "databrowse_install.zip")

        call_github(filename).run()

        if call_github.isFinished:
            self.output_text.setText(self.output_text.text() + ">Done\r\n")
            self.output_text.repaint()
            self.output_text.setText(self.output_text.text() + ">Unzipping files\r\n")
            self.output_text.repaint()
            qt_app.processEvents()

            unzip(filename, self.path).run()

            if unzip.isFinished:
                self.output_text.setText(self.output_text.text() + ">Done\r\n")
                self.output_text.repaint()
                self.output_text.setText(self.output_text.text() + ">Running setup.py\r\n")

                os.chdir(self.path + "/databrowse-feature-cefdatabrowse")
                f = open(os.getcwd() + "/cefdatabrowse/config.py", "w")
                f.write("location = '" + os.getcwd() + "'")
                f.close()

                qt_app.processEvents()

                if f.closed:
                    setup(self.path).run()

                if setup.isFinished:
                    self.output_text.setText(self.output_text.text() + ">Done\r\n")
                    self.output_text.repaint()
                    qt_app.processEvents()

    def cancel_app(self):
        qt_app.quit()

    def confirm_install(self):
        if self.path is not None:
            if os.path.exists(self.path):
                self.conf_window.resize(self.conf_layout.sizeHint())
                self.conf_window.show()
            else:
                self.path_text.setText("Path does not exist.")
        else:
            self.path_text.setText("Path must be set.")

    def license_app(self):
        """ Read and display GPL licence. """
        self.license_window.resize(self.scrollarea.sizeHint().width(), 300)
        self.license_window.show()

    def run(self):
        """ Show the application window and start the main event loop """
        self.show()
        qt_app.exec_()


# Inherit from QThread
class call_github(QThread):
    # You can do any extra things in this init you need, but for this example
    # nothing else needs to be done expect call the super's init
    def __init__(self, filename):
        QThread.__init__(self)
        self.filename = filename

    # A QThread is run by calling it's start() function, which calls this run()
    # function in it's own "thread".
    def run(self):
        urllib.urlretrieve("https://github.com/limatix/databrowse/archive/feature-cefdatabrowse.zip",
                           filename=self.filename)


# Inherit from QThread
class unzip(QThread):
    # You can do any extra things in this init you need, but for this example
    # nothing else needs to be done expect call the super's init
    def __init__(self, filename, path):
        QThread.__init__(self)
        self.filename = filename
        self.path = path

    # A QThread is run by calling it's start() function, which calls this run()
    # function in it's own "thread".
    def run(self):
        zip_ref = zipfile.ZipFile(self.filename, 'r')
        zip_ref.extractall(self.path)
        zip_ref.close()


class setup(QThread):
    def __init__(self, path):
        QThread.__init__(self)
        self.path = path

    def run(self):
        import subprocess
        subprocess.call(['python', 'setup.py', 'install'])

# Create an instance of the application and run it
Install().run()
