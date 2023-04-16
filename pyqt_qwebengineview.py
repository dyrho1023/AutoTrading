# https://stackoverflow.com/questions/52098156/launch-javascript-function-from-pyqt-qwebengineview


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEnginePage


class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)


class FormWidget(QWidget):
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.__controls()
        self.__layout()

    def __controls(self):
        html = open('pyqt_qwebengineview.html', 'r').read()
        self.browser = QWebEngineView()
        self.browser.setHtml(html)
        self.browser.loadFinished.connect(self.onLoadFinished)
        # self.browse = QWebEngineView()
        # self.browser.setPage(WebEnginePage(self.browser))

    def onLoadFinished(self, ok):
        print('11')
        if ok:
            self.browser.page().runJavaScript("helloWorld(1, \"2\")", self.ready)


    def __layout(self):
        self.vbox = QVBoxLayout()
        self.hBox = QVBoxLayout()
        self.hBox.addWidget(self.browser)
        self.vbox.addLayout(self.hBox)
        self.setLayout(self.vbox)

    def ready(self, returnValue):
        print(returnValue)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())