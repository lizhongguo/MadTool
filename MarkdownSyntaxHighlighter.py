from PyQt5.QtCore import (QEvent, QFile, QFileInfo, QRegExp, QTextStream, Qt)

from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMessageBox, QTextEdit)

from PyQt5.QtGui import QCursor, QFont,QIcon,QColor,QKeySequence,QSyntaxHighlighter,QTextCharFormat,QTextCursor, QTextDocument

import sys

class MarkdownSyntaxHighlighter(QSyntaxHighlighter):
    Rules = []
    Formats = {}

    def __init__(self, parent:QTextDocument = None):
        super(MarkdownSyntaxHighlighter, self).__init__(parent)
        self.initializeFormats()
        KEYWORDS = ["and", "as", "assert", "break", "class",
                "continue", "def", "del", "elif", "else", "except",
                "exec", "finally", "for", "from", "global", "if",
                "import", "in", "is", "lambda", "not", "or", "pass",
                "print", "raise", "return", "try", "while", "with",
                "yield"]
        BUILTINS = ["abs", "all", "any", "basestring", "bool",
                "callable", "chr", "classmethod", "cmp", "compile",
                "complex", "delattr", "dict", "dir", "divmod",
                "enumerate", "eval", "execfile", "exit", "file",
                "filter", "float", "frozenset", "getattr", "globals",
                "hasattr", "hex", "id", "int", "isinstance",
                "issubclass", "iter", "len", "list", "locals", "map",
                "max", "min", "object", "oct", "open", "ord", "pow",
                "property", "range", "reduce", "repr", "reversed",
                "round", "set", "setattr", "slice", "sorted",
                "staticmethod", "str", "sum", "super", "tuple", "type",
                "vars", "zip"] 
        CONSTANTS = ["False", "True", "None", "NotImplemented",
                     "Ellipsis"]

        MarkdownSyntaxHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % keyword for keyword in KEYWORDS])),
                "keyword"))
        MarkdownSyntaxHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % builtin for builtin in BUILTINS])),
                "builtin"))
        MarkdownSyntaxHighlighter.Rules.append((QRegExp(
                "|".join([r"\b%s\b" % constant
                for constant in CONSTANTS])), "constant"))
        MarkdownSyntaxHighlighter.Rules.append((QRegExp(
                r"\b[+-]?[0-9]+[lL]?\b"
                r"|\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"
                r"|\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
                "number"))
        MarkdownSyntaxHighlighter.Rules.append((QRegExp(
                r"\bPyQt4\b|\bQt?[A-Z][a-z]\w+\b"), "pyqt"))
        MarkdownSyntaxHighlighter.Rules.append((QRegExp(r"\b@\w+\b"),
                "decorator"))
        stringRe = QRegExp(r"""(?:'[^']*'|"[^"]*")""")
        stringRe.setMinimal(True)
        MarkdownSyntaxHighlighter.Rules.append((stringRe, "string"))
        self.stringRe = QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
        self.stringRe.setMinimal(True)
        MarkdownSyntaxHighlighter.Rules.append((self.stringRe, "string"))
        self.tripleSingleRe = QRegExp(r"""'''(?!")""")
        self.tripleDoubleRe = QRegExp(r'''"""(?!')''')

    @staticmethod
    def initializeFormats():
        baseFormat = QTextCharFormat()
        baseFormat.setFontFamily("courier")
        baseFormat.setFontPointSize(12)
        for name, color in (("normal", Qt.black),
                ("keyword", Qt.darkBlue), ("builtin", Qt.darkRed),
                ("constant", Qt.darkGreen),
                ("decorator", Qt.darkBlue), ("comment", Qt.darkGreen),
                ("string", Qt.darkYellow), ("number", Qt.darkMagenta),
                ("error", Qt.darkRed), ("pyqt", Qt.darkCyan)):
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            if name in ("keyword", "decorator"):
                format.setFontWeight(QFont.Bold)
            if name == "comment":
                format.setFontItalic(True)
            MarkdownSyntaxHighlighter.Formats[name] = format

    def highlightBlock(self, text: str) -> None:
        # core function 
        # setFormat for each char in block
        NORMAL, TRIPLESINGLE, TRIPLEDOUBLE,ERROR = range(4)
        textLength = len(text)
        prevState = self.previousBlockState()
        self.setFormat(0,textLength, MarkdownSyntaxHighlighter.Formats["normal"])

        if text.startswith("Traceback") or text.startswith("Error: "):
            self.setFormat(0,textLength,MarkdownSyntaxHighlighter.Formats("error"))
            self.setCurrentBlockState(ERROR)
            return
        
        if (prevState==ERROR and not(text.startswith(sys.ps1) or text.startswith("#"))):
            self.setCurrentBlockState(ERROR)
            self.setFormat(0, textLength, MarkdownSyntaxHighlighter.Formats["error"])

        for regex,format in MarkdownSyntaxHighlighter.Rules:
            i = regex.indexIn(text)
            while i>=0:
                length = regex.matchedLength()
                self.setFormat(i,length,MarkdownSyntaxHighlighter.Formats[format])
                i = regex.indexIn(text, i+length)
        if not text:
            pass
        elif text[0] == "#":
            self.setFormat(0, len(text),MarkdownSyntaxHighlighter.Formats["comment"])
        else:
            stack = []
            for i,c in enumerate(text):
                if c in ('"', "'"):
                    if stack and stack[-1] == c:
                        stack.pop()
                    else:
                        stack.append(c)
                elif c=="#" and len(stack)==0:
                    self.setFormat(i,len(text),MarkdownSyntaxHighlighter.Formats["comment"])
                    break
        self.setCurrentBlockState(NORMAL)

    def rehighlight(self) -> None:
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QSyntaxHighlighter.rehighlight(self)
        QApplication.restoreOverrideCursor()
