from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import pandas
import sys
# from ListUpByFssFind import *


# https://stackoverflow.com/questions/52098156/launch-javascript-function-from-pyqt-qwebengineview


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineScript
from PyQt5.QtCore import *


class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)


class WebMainWindow(QMainWindow):
    print('11')
    def __init__(self, parent=None):
        print('12')
        super(WebMainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)
        print('13')


class FormWidget(QWidget):
    def __init__(self, parent):
        print('14')
        super(FormWidget, self).__init__(parent)
        self.__controls()
        self.__layout()

    def __controls(self):
        print('15')
        html = open('pyqt_qwebengineview2.html', 'r').read()
        self.browser = QWebEngineView()
        self.browser.setHtml(html)  ## 또는 self.browser.setHtml(HTML, QtCore.QUrl("pyqt_qwebengineview2.html"))
        self.loadCSS(self.browser, "css/style.css", "script1")  ## javascript를 통해 css를 실행함.
        # self.script_ex(self.browser)
        self.script_ex2(self.browser)
        print('16')

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

    def loadCSS(self, view, path, name):  ## pyqt내 html 직접 css를 리딩할수 없다.
        print('17')
        path = QFile(path)  ## 따라서 javascript를 통해 css를 실행해줘야한다.
        # https://stackoverflow.com/questions/51388443/css-doesnt-work-in-qwebengineview-sethtml
        if not path.open(QFile.ReadOnly | QFile.Text):
            # print('111')
            return
        print('21')
        css = path.readAll().data().decode("utf-8")
        print('20')
        SCRIPT = """
        (function() {
        css = document.createElement('style');
        css.type = 'text/css';
        css.id = "%s";
        document.head.appendChild(css);
        css.innerText = `%s`;
        })()
        """ % (name, css)
        print('18')
        script = QWebEngineScript()
        view.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
        script.setName(name)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        view.page().scripts().insert(script)
        print('19')
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
            """ % (a, b, c, d)

        script = QWebEngineScript()
        browser.page().runJavaScript(SCRIPT, QWebEngineScript.ApplicationWorld)
        script.setSourceCode(SCRIPT)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        browser.page().scripts().insert(script)


def main():
    app = QApplication(sys.argv)
    win = WebMainWindow()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())


#
# kospi_top5 = {
#     'code': ['005930', '015760', '005380', '090430', '012330'],
#     'name': ['삼성전자', '한국전력', '현대차', '아모레퍼시픽', '현대모비스'],
#     'cprice': ['1,269,000', '60,100', '132,000', '414,500', '243,500']
# }
# column_idx_lookup = {'code': 0, 'name': 1, 'cprice': 2}
#
#
#
#
#
# class ListUpByFssShow(QDialog):           ## 'EOL 테이블 입력' 버튼을 눌렀을때의 서브 WINDOW 클래스
#
#     def __init__(self):
#         super().__init__()
#         self.setupUI()
#
#
#
#     def setupUI(self):
#
#         # kospiTop100 = ListUp_By_Fss_Find().t1404()
#         # kospiTop100 = ListUp_By_Fss_Find().t1405()
#         # kospiTop100 = ListUp_By_Fss_Find().t8430()
#
#         # a = ListUp_By_Fss_Find().FssByNAVER()
#
#         # kospiTop100 = ListUp_By_Fss_Find().t1444()
#         # kospiTop100 = ListUp_By_Fss_Find().t3320()
#         # kospiTop100 = ListUp_By_Fss_Find().FssByNAVERAndt1444()
#
#         self.setGeometry(800, 200, 500, 500)
#         # a = t8430().Query(1)
#
#         self.tableAWidget = QTableWidget(self)
#         self.tableAWidget.resize(290, 290)
#         self.tableAWidget.setRowCount(5)
#         self.tableAWidget.setColumnCount(3)
#         self.tableAWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
#
#         self.tableBWidget = QTableWidget(self)
#         self.tableBWidget.resize(290, 290)
#         self.tableBWidget.setRowCount(40)
#         self.tableBWidget.setColumnCount(4)
#         self.tableBWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
#
#         self.setTableWidgetData()
#
#         Tablelayout = QHBoxLayout()
#         Tablelayout.addWidget(self.tableAWidget)
#         Tablelayout.addWidget(self.tableBWidget)
#         self.setLayout(Tablelayout)
#
#
#     def setTableWidgetData(self):
#         column_headers = ['종목코드', '종목명', '종가']
#         self.tableAWidget.setHorizontalHeaderLabels(column_headers)
#         # self.tableBWidget.setHorizontalHeaderLabels(column_headers)
#
#         for k, v in kospi_top5.items():
#             col = column_idx_lookup[k]
#             for row, val in enumerate(v):
#                 item = QTableWidgetItem(val)
#                 if col == 2:
#                     item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
#
#                 self.tableAWidget.setItem(row, col, item)
#                 # self.tableBWidget.setItem(row, col, item)
#
#         self.tableAWidget.resizeColumnsToContents()
#         self.tableAWidget.resizeRowsToContents()
#         # self.tableBWidget.resizeColumnsToContents()
#         # self.tableBWidget.resizeRowsToContents()
#
#         # self.tableCWidget.resizeColumnsToContents()
#         # self.tableCWidget.resizeRowsToContents()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mywindow = ListUpByFssShow()
#     mywindow.show()
#     app.exec_()