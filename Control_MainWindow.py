import sys
import os.path
import markdown
import mimetypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *

from Ui_MainWindow import Ui_MainWindow
from MarkdownSyntaxHighlighter import MarkdownSyntaxHighlighter as MSH

class Control_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.textEdit.textChanged.connect(self.updateMd)
        self.md2html = markdown.Markdown(extensions=['pymdownx.extra','pymdownx.tasklist','attr_list','sane_lists'])
        self.webView.setZoomFactor(2.0)
        self.highlighter = MSH(self.textEdit.document())

    def updateMd(self):
        text = self.textEdit.toPlainText()
        htmlContent = self.md2html.convert(text)
        self.webView.setHtml(htmlContent)
    