# https://stackoverflow.com/questions/52098156/launch-javascript-function-from-pyqt-qwebengineview


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineScript
from PyQt5.QtCore import*

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
        html = open('pyqt_qwebengineview2.html', 'r').read()
        self.browser = QWebEngineView()
        self.browser.setHtml(html)   ## 또는 self.browser.setHtml(HTML, QtCore.QUrl("pyqt_qwebengineview2.html"))
        self.loadCSS(self.browser, "css/style.css", "script1")   ## javascript를 통해 css를 실행함.
        # self.script_ex(self.browser)
        self.script_ex2(self.browser)

        # self.browser.loadFinished.connect(self.onLoadFinished)
        # self.browse = QWebEngineView()
        # self.browse.setPage(WebEnginePage(self.browser))

    def onLoadFinished(self, ok):
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

    def loadCSS(self, view, path, name):    ## pyqt내 html 직접 css를 리딩할수 없다.
        path = QFile(path)                  ## 따라서 javascript를 통해 css를 실행해줘야한다.
                                            # https://stackoverflow.com/questions/51388443/css-doesnt-work-in-qwebengineview-sethtml
        if not path.open(QFile.ReadOnly | QFile.Text):
            print('111')
            return
        css = path.readAll().data().decode("utf-8")
        SCRIPT = """
        (function() {
        css = document.createElement('style');
        css.type = 'text/css';
        css.id = "%s";
        document.head.appendChild(css);
        css.innerText = `%s`;
        })()
        """ % (name, css)

        script =QWebEngineScript()
        view.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
        script.setName(name)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        view.page().scripts().insert(script)


    # def script_ex(self , browser):
    #     a = '1'
    #     SCRIPT = """
    #
    #             const items = document.getElementById('test')
    #             items.addEventListener('click', openCloseMenu)
    #
    #                 function openCloseMenu(event){
    #                     let menuId = event.target
    #                     menuId.textContent += "%s";
    #                     }
    #             """  %(a)
    #
    #     script = QWebEngineScript()
    #     browser.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
    #     script.setSourceCode(SCRIPT)
    #     script.setInjectionPoint(QWebEngineScript.DocumentReady)
    #     script.setRunsOnSubFrames(True)
    #     script.setWorldId(QWebEngineScript.ApplicationWorld)
    #     browser.page().scripts().insert(script)

    def script_ex2(self, browser):
        a = '2'
        b = '1'
        c = "['1', '2', '1','1','1','1','1','1','1','1', '1', '1', '1']"
        d = "[1, 2, 3, 4, 5]"

        SCRIPT = """

            const items2 = document.getElementById('test2')
            items2.addEventListener('click', openCloseMenu2)
            
            function openCloseMenu2(event){
                let menuId = event.target
                menuId.textContent += %s;
            }
                    
            const items1 = document.getElementById('test')
            items1.addEventListener('click', openCloseMenu1)
            
            function openCloseMenu1(event){
                let menuId = event.target
                menuId.textContent += %s;
             }
            
            const tableitems = document.getElementById('test3')
            tableitems.addEventListener('click', openCloseMenu3)
            
            function openCloseMenu3(event){
                let table = document.getElementById('weight-table')
                var data = %s;
                a = table.getElementsByClassName('tbody')
                var newRow =""
                for (let i=0; i<data.length; i++) {
                newRow +=   "<td>" + data[i] + "</td>";  
                }
    
                a[0].innerHTML +=  "<tr>" + newRow + "</tr>";
             }
                
                
            tableitems.addEventListener('click', openCloseMenu4)
            function openCloseMenu4(event){
                let selform = document.getElementsByName('sel_num')
                var data = %s;
                for (let i=0; i<data.length; i++) {
                    selform.options
                }
    
                a[0].innerHTML +=  "<tr>" + newRow + "</tr>";
             }            
            """ % (a,b,c,d)

        script = QWebEngineScript()
        browser.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        browser.page().scripts().insert(script)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())