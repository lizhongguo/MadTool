import sys
import os.path
import markdown
import mimetypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *

from Control_MainWindow import Control_MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = Control_MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
