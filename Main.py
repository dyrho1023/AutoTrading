## User Python File
from XAQueries import *
from XASession import *
from XAReals import *
from SetEnvironment import *
from DatabaseClass import *
from DayTrading import *
from ListUpByFssFind import *  # LKH
from ListUpByFssShow import *  # LKH
from Dart import DartCorpListGet  # LKH
from multiprocessing import *
from msvcrt import *
from miniFssShow import *

## Python Module
import pythoncom
import inspect
## import sqlite3
import sys
import os
import PyQt5
import time
import atexit
import datetime

## UI용 Python Module
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

## 전역 변수
Delay3s = 3000  # ms 단위 // TR 제한 10분 200개
delay_0_2s = 205  # TR 제한 1초 5개
VolumeDuration = 80  # 거래량 80일 분
TotalLimit = 100000000000  # 시총 제한 금액 - 추후 UI에서 구현

UIMainWindow = uic.loadUiType("Stock_UI.ui")[0]
# UISampleWindow = uic.loadUiType("Sample_UI.ui")[0]

PushButton_Style = '''
            QPushButton { background-color : rgb(204, 230, 255); }
            QPushButton::hover { background-color : rgb(128, 193, 255); } '''

PushButton_Style_Stop = '''
            QPushButton { background-color : rgb(255, 149, 149); }
            QPushButton::hover { background-color : rgb(255, 102, 102); } '''

PushButton_Style_Restart = '''
            QPushButton { background-color : rgb(156, 226, 156); }
            QPushButton::hover { background-color : rgb(97, 209, 97); } '''

PushButton_Style_Green = '''
            QPushButton { background-color : rgb(156, 226, 156); }
            QPushButton::hover { background-color : rgb(97, 209, 97); } '''

ProgressBar_Style = '''
            QProgressBar { text-align : right;
                           margin-right : 40 px }
            QProgressBar::chunk { background-color : rgb(70, 130, 180); 
                                  boarder-color : black;
                                  margin : 1px ; } '''

Label_Style = ''' QLabel { background-color : rgb(204, 204, 204); } '''

GroupBox_Style1 = ''' 
            QGroupBox { background-color: rgb(231, 231, 231);
                        border-style : outset;
                        border-width : 1px;
                        border-color : rgb(140, 140, 140); } '''

GroupBox_Style2 = ''' 
            QGroupBox { background-color: rgb(216, 216, 216);
                        border-style : outset;
                        border-width : 1px;
                        border-color : rgb(140, 140, 140); } '''

ComboBox_Style1 = ''' 
            QComboBox { background-color : rgb(204, 204, 204); }
            QListView::item { background-color : rgb(204, 204, 204); 
                              height : 18px; }'''

ComboBox_Style2 = ''' 
            QListView::item { height : 18px; }'''


class SampleWindow(QDialog):
    def __init__(self):
        super().__init__()
        QDialog.__init__(self)
        # UISampleWindow.__init__(self)
        self.setupUi(self)

        self.work = Worker()

        self.pushButton_StartPrint.setStyleSheet(PushButton_Style_Restart)
        self.pushButton_StopPrint.setStyleSheet(PushButton_Style_Stop)

        self.pushButton_StartPrint.clicked.connect(self.startPrint)
        self.pushButton_StopPrint.clicked.connect(self.stopPrint)

    def startPrint(self):
        self.work.start()
        print("진입")

    def stopPrint(self):
        self.work.stop()
        print("종료")


class Worker(QThread):
    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            print("안녕하세요")
            self.sleep(1)

    def stop(self):
        self.running = False
        self.quit()


class MainWindow(QMainWindow, QWidget, UIMainWindow):
    def __init__(self):
        super().__init__()
        QMainWindow.__init__(self)
        UIMainWindow.__init__(self)
        self.setupUi(self)

        ## 초기 UI 실행 위치 설정
        self.frameGeo = self.frameGeometry()
        self.centerPoint = QDesktopWidget().availableGeometry().center()
        self.frameGeo.moveCenter(self.centerPoint)
        self.move(self.frameGeo.topLeft())

        ## SetEnvironment에서 값 불러오는 부분
        programSet = SystemSetting()
        programSet.LoadSystemSetting(parent=self)

        self.autoLogInCheck = "".join(programSet.systemInfo[1])
        self.autoUpdateCheck = "".join(programSet.systemInfo[3])
        self.lastListUpdateTime = "".join(programSet.systemInfo[5])
        self.lastVolumeUpdateTime1 = "".join(programSet.systemInfo[7])
        self.UpCodeUpdateLastDate = "".join(programSet.systemInfo[9])   ### LKH
        self.FssUpdateLastDate = "".join(programSet.systemInfo[11])     ### LKH
        self.RiskCorpUpdateLastDate = "".join(programSet.systemInfo[13])  ### LKH
        self.UpCodeUpdateLastDate = "".join(programSet.systemInfo[9])   ### LKH
        self.FssUpdateLastDate = "".join(programSet.systemInfo[11]).split(',')     ### LKH
        self.RiskCorpUpdateLastDate = "".join(programSet.systemInfo[13])  ### LKH

        ## 다른 python file의  Class 할당
        self.dataControl = Database()
        self.stockPickUpdate = StockPick(parent=self)
        self.logInOut = MyLogInOut(parent=self)
        self.sampleTrading = StockTrading(parent=self)

        self.DayTrading = StockTrading() # DayTrading 함수 테스트용

        ## UI용 함수 호출 부분 및 초기 설정 부분
        self.statusBarMsg = "Program Initialized"
        self.statusBar.showMessage(self.statusBarMsg)

        self.InitProgramSetting()

        self.AutoUpdate()
        self.MenuAction()
        self.PushButtonAction()
        self.ComboBoxAction()
        self.TableViewAction()
        self.SpinboxAction()

        # 전역 변수 설정

        # Local 변수 - 기업 종목 수 관련

        # Local 변수 - 종목 필터 관련
        self.MarketCap = 0

        # Local 변수 - 거래량 업데이트 관련
        self.progressbarSet = 0
        self.shcodeStockList = []
        self.lenStockList = 0
        self.countStockList = 0
        self.lastVolumeUpdateNumber = 0
        self.retryCount = 0
        self.lastStockVolumeShcode = 0
        self.companyNumber = 0
        self.tempCompanyNumber = 0

        # Local 변수 - 매매 관련
        self.mainCall = True        # 매매 관련 함수를 main에서 호출함
        self.countCurrentRow = 0
        self.orderingList = []
        self.stockAccount = 0
        self.stockPassword = 0
        self.stockShcode = 0
        self.stockPrice = 0
        self.stockVolume = 0
        self.stockLoanDate = 0
        self.stockMargin = 0
        self.stockSellBuy = 0
        self.stockBidAsk = 0
        self.stockOption = 0
        self.tableLabels = []

        # tr 할당
        self.gett8430 = t8430(parent=self)
        self.gett1404 = t1404(parent=self)
        self.gett1305 = t1305(parent=self)
        self.gett1102 = t1102(parent=self)
        self.gett1452 = t1452(parent=self)
        self.gett1463 = t1463(parent=self)
        self.getCSPAT00600 = CSPAT00600(parent=self)
        self.getSC1 = SC1(parent=self)

        # GroupBox Style
        self.groupBox_Update.setStyleSheet(GroupBox_Style1)
        self.groupBox_BasicSetting.setStyleSheet(GroupBox_Style1)
        self.groupBox_VolumeRetry.setStyleSheet(GroupBox_Style2)
        self.groupBox_Algorithm1.setStyleSheet(GroupBox_Style2)
        self.groupBox_StockOrder1.setStyleSheet(GroupBox_Style2)

        # PushButton Style
        self.pushButton_AllStop.setStyleSheet(PushButton_Style_Stop)
        self.pushButton_TempStop.setStyleSheet(PushButton_Style_Stop)
        self.pushButton_ListUpdate.setStyleSheet(PushButton_Style)
        self.pushButton_StockListFilter.setStyleSheet(PushButton_Style_Green)
        self.pushButton_VolumeUpdate1.setStyleSheet(PushButton_Style)
        self.pushButton_StockPick.setStyleSheet(PushButton_Style)
        self.pushButton_VolumeRetry1.setStyleSheet(PushButton_Style)
        self.pushButton_StockOrder.setStyleSheet(PushButton_Style)
        self.pushButton_MarketCap.setStyleSheet(PushButton_Style)
        self.pushButton_FssUpdate1.setStyleSheet(PushButton_Style)
        self.pushButton_UpCodeUpdate1.setStyleSheet(PushButton_Style)  ## LKH
        self.pushButton_UpCodeUpdateRetry1.setStyleSheet(PushButton_Style)  ## LKH
        self.pushButton_FssUpdate1.setStyleSheet(PushButton_Style)  ## LKH
        self.pushButton_FssUpdateRetry1.setStyleSheet(PushButton_Style)  ## LKH
        self.pushButton_RiskCorpUpdate1.setStyleSheet(PushButton_Style)  ## LKH
        self.pushButton_SelectWholeFfs.setStyleSheet(PushButton_Style)  ## LKH

        # ProgressBar Style
        self.progressBar_VolumeUpdate.setStyleSheet(ProgressBar_Style)
        self.progressBar_StockPick.setStyleSheet(ProgressBar_Style)
        self.progressBar_VolumeRetry.setStyleSheet(ProgressBar_Style)

        # Label Style
        self.label_UpcodeUpdateStatus1.setStyleSheet(Label_Style)  ## LKH
        self.label_FssUpdateStatus1.setStyleSheet(Label_Style)  ## LKH

        # ComboBox Style
        self.comboStyle1 = QListView()
        self.comboStyle1.setStyleSheet(ComboBox_Style1)
        self.comboStyle1.setFont(QFont("a뉴굴림2", 8))

        self.comboStyle20 = QListView()
        self.comboStyle20.setStyleSheet(ComboBox_Style2)
        self.comboStyle20.setFont(QFont("a뉴굴림2", 8))

        self.comboStyle21 = QListView()
        self.comboStyle21.setStyleSheet(ComboBox_Style2)
        self.comboStyle21.setFont(QFont("a뉴굴림2", 8))

        self.comboStyle22 = QListView()
        self.comboStyle22.setStyleSheet(ComboBox_Style2)
        self.comboStyle21.setFont(QFont("a뉴굴림2", 8))

        self.comboBox_StockOrder3.setView(self.comboStyle1)
        self.comboBox_StockOrder3.resize(111, 20)

        self.comboBox_StockOrder7.setView(self.comboStyle20)
        self.comboBox_StockOrder7.resize(111, 20)

        self.comboBox_StockOrder8.setView(self.comboStyle21)
        self.comboBox_StockOrder8.resize(111, 20)

        self.comboBox_StockOrder9.setView(self.comboStyle22)
        self.comboBox_StockOrder9.resize(111, 20)

    def InitProgramSetting(self):
        """
        프로그램 실행 후 초기 UI 설정 및 자동 실행 부분 호출
        """
        if self.autoLogInCheck == '1':  # 자동 로그인 UI Setting
            self.checkBox_AutoLogIn.setChecked(True)
            self.logInOut.MyLogIn()
        else:
            self.checkBox_AutoLogIn.setChecked(False)

        if self.autoUpdateCheck == '1':  # 자동 상장 기업 종목 업데이트 UI Setting
            self.checkBox_AutoUpdate.setChecked(True)
        else:
            self.checkBox_AutoUpdate.setChecked(False)

        ## UI 기본 설정 부분
        self.tempCompanyNumber = self.dataControl.CallStockList()  # StockList에서 shcode 불러옴
        self.companyNumber = len(self.tempCompanyNumber)

        if len(self.dataControl.CallStockVolumeList()) == 0:
            self.lastVolumeUpdateNumber = 0
        else:
            self.lastStockVolumeShcode = max(self.dataControl.CallStockVolumeList())
            self.lastVolumeUpdateNumber = self.tempCompanyNumber.index(self.lastStockVolumeShcode) + 1

        self.label_ListUpdate.setText(" 마지막 업데이트 날짜 : " + self.lastListUpdateTime)
        self.label_VolumeUpdate1.setText(" 마지막 업데이트 날짜 : " + self.lastVolumeUpdateTime1)
        self.label_VolumeUpdate2.setText(" 업데이트 된 기업 수 / 총 기업 수 : " + str(self.lastVolumeUpdateNumber) + "/" +
                                         str(self.companyNumber))
        self.label_StockPick1.setText(" 마지막 업데이트 날짜 : ")
        self.label_UpCodeUpdateLastDate.setText(" 마지막 업데이트 날짜 : " + self.UpCodeUpdateLastDate)  ### LKH
        # self.label_FssUpdateLastDate.setText(" 마지막 업데이트 날짜 : " + self.FssUpdateLastDate) ### LKH
        self.label_RiskCorpUpdateLastDate.setText(" 마지막 업데이트 날짜 : " + self.RiskCorpUpdateLastDate)  ### LKH
        self.label_UpCodeUpdateLastDate.setText(" 마지막 업데이트 날짜 : " + self.UpCodeUpdateLastDate)  ### LKH
        self.label_FssUpdateLastDate.setText(" 마지막 업데이트 날짜 : ( " + self.FssUpdateLastDate[0] + ',' + self.FssUpdateLastDate[1]+ ' )') ### LKH
        self.label_RiskCorpUpdateLastDate.setText(" 마지막 업데이트 날짜 : " + self.RiskCorpUpdateLastDate)  ### LKH

        ## 수동 매매 UI Setting
        self.lineEdit_StockOrder1.setText(self.logInOut.accountNum)
        self.lineEdit_StockOrder2.setText(self.logInOut.tradingPwd)

    def PushButtonAction(self):
        """
        PushButton으로 실행하는 기능
        """
        self.pushButton_SamplePart2.clicked.connect(self.sampleTrading.TradingPart2)

        self.pushButton_AllStop.clicked.connect(self.AllStopFunction)
        self.pushButton_TempStop.clicked.connect(self.TempStopFunction)
        self.pushButton_ListUpdate.clicked.connect(self.ListUpdateFunction)
        self.pushButton_VolumeUpdate1.clicked.connect(self.VolumeUpdateFunction)
        self.pushButton_StockPick.clicked.connect(self.StockPickFunction)
        self.pushButton_VolumeRetry1.clicked.connect(self.VolumeRetryFunction)
        self.pushButton_StockOrder.clicked.connect(self.StockOrderFunction)
        self.pushButton_MarketCap.clicked.connect(self.MarketCapFunction)
        self.pushButton_StockListFilter.clicked.connect(self.StockListFilterFunction)
        self.pushButton_UpCodeUpdate1.clicked.connect(self.UpcodeUpdateFunction)  ## LKH
        self.pushButton_UpCodeUpdateRetry1.clicked.connect(self.UpcodeUpdateRetryFunction)  ## LKH
        self.pushButton_FssUpdate1.clicked.connect(self.FssUpdateFunction)  ## LKH
        self.pushButton_FssUpdateRetry1.clicked.connect(self.FssUpdateRetryFunction)  ## LKH
        self.pushButton_RiskCorpUpdate1.clicked.connect(self.RiskCorpUpdateFunction)  ## LKH
        self.pushButton_SelectWholeFfs.clicked.connect(self.connectselectWholeFfs)   ## LKH

        self.pushButton_PKB_TEST.clicked.connect(self.DayTrading.CheckBuySignal)
        # self.pushButton_PKB_TEST.clicked.connect(lambda:self.DayTrading.CheckBuySignal())

    def ComboBoxAction(self):
        """
        ComboBox 선택 액션
        """
        self.comboBox_StockOrder3.addItem("보통", '000')
        self.comboBox_StockOrder3.addItem("유통/자기융자신규", '003')
        self.comboBox_StockOrder3.addItem("유통대주신규", '005')
        self.comboBox_StockOrder3.addItem("자기대주신규", '007')
        self.comboBox_StockOrder3.addItem("유통융자상환", '101')
        self.comboBox_StockOrder3.addItem("자기융자상환", '103')
        self.comboBox_StockOrder3.addItem("유통대주상환", '105')
        self.comboBox_StockOrder3.addItem("자기대주상환", '107')
        self.comboBox_StockOrder3.addItem("예탁담보대출상환", '180')

        self.comboBox_StockOrder7.addItem("매도", '1')
        self.comboBox_StockOrder7.addItem("매수", '2')

        self.comboBox_StockOrder8.addItem("지정가", '00')
        self.comboBox_StockOrder8.addItem("시장가", '03')
        self.comboBox_StockOrder8.addItem("조건부지정가", '05')
        self.comboBox_StockOrder8.addItem("최유리지정가", '06')
        self.comboBox_StockOrder8.addItem("최우선지정가", '07')
        self.comboBox_StockOrder8.addItem("장개시전시간외종가", '61')
        self.comboBox_StockOrder8.addItem("시간외종가", '81')
        self.comboBox_StockOrder8.addItem("시간외단일가", '82')

        self.comboBox_StockOrder9.addItem("없음", '0')
        self.comboBox_StockOrder9.addItem("ICO", '1')
        self.comboBox_StockOrder9.addItem("FOK", '2')

    def TableViewAction(self):
        """
        TableView로 주문/체결의 상태를 보여줌
        """
        self.tableLabels = ['분류', '주문번호', '종목명', '매매구분', '수량', '체결가격', '시각', '체결번호']
        self.tableWidget_StockOrder1.setColumnCount(7)
        self.tableWidget_StockOrder1.verticalHeader().setDefaultSectionSize(22)
        self.tableWidget_StockOrder1.setHorizontalHeaderLabels(self.tableLabels)
        self.tableWidget_StockOrder1.setColumnWidth(0, 80)
        self.tableWidget_StockOrder1.setColumnWidth(1, 80)
        self.tableWidget_StockOrder1.setColumnWidth(2, 80)
        self.tableWidget_StockOrder1.setColumnWidth(3, 80)
        self.tableWidget_StockOrder1.setColumnWidth(4, 80)
        self.tableWidget_StockOrder1.setColumnWidth(5, 80)
        self.tableWidget_StockOrder1.setColumnWidth(6, 80)
        self.tableWidget_StockOrder1.setColumnWidth(7, 80)

    def SpinboxAction(self):
        """
        SpinBox에서 선택 가능한 값의 상한/하한/간격/초기값 설정
        """
        self.spinBox_VolumeRetry1.setMinimum(1)
        self.spinBox_VolumeRetry1.setMaximum(self.companyNumber)
        self.spinBox_VolumeRetry1.setSingleStep(1)
        if self.lastVolumeUpdateNumber == self.companyNumber:
            self.spinBox_VolumeRetry1.setValue(1)
        else:
            self.spinBox_VolumeRetry1.setValue(self.lastVolumeUpdateNumber + 1)

    def MenuAction(self):
        """
        상단 Menu에 들어 가는 기능
        """
        actionLogIn = QAction('&Log In', self)  # 첫 번째 Menubar
        actionLogIn.triggered.connect(lambda: self.logInOut.MyLogIn())

        actionLogOut = QAction('&Log Out', self)
        actionLogOut.triggered.connect(lambda: self.logInOut.MyLogOut())

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&프로그램')
        fileMenu.setStyleSheet("background-color : rgb(178, 209, 230)")
        fileMenu.addAction(actionLogIn)
        fileMenu.addAction(actionLogOut)

        actionListUpByFss = QAction('&기업 리스트(재무제표 기반) DB 다운로드', self)  # 두 번째 Menubar
        actionListUpByFss.triggered.connect(self.ActionListUpByFss)

        actionListUpByFssShowUp = QAction('&기업 리스트 UI 조회', self)
        actionListUpByFssShowUp.triggered.connect(self.ActionListUpByFssShowUp)

        extraMenuBar = self.menuBar()
        extraMenu = extraMenuBar.addMenu('부가기능')
        extraMenu.setStyleSheet("background-color : rgb(178, 209, 230)")
        extraMenu.addAction(actionListUpByFss)
        extraMenu.addAction(actionListUpByFssShowUp)

    def TempStopFunction(self):
        """
        프로그램 일시 정지
        """
        print("프로그램 일시 정지")
        input("계속 하기 위해서 Consol 창에 Enter를 치세요")

    def AllStopFunction(self):
        """
        프로그램 전체 중지
        """
        print("프로그램 중지")
        input("아직 미구현...")

    def ListUpdateFunction(self):
        """
        상장된 국내 회사 전체 종목 업데이트
        """
        self.dataControl.DeleteStockListAll()
        self.statusBar.showMessage("상장된 국내 회사의 정보를 업데이트하고 있습니다.")
        self.gett8430.Query(구분='0')

    def VolumeUpdateFunction(self):
        """
        StockList에 있는 회사의 거래량을 업데이트
        연속 조회 형태 = 함수 2개 추가로 필요
        VolumeUpdateFunction1
        VolumeUpdateFunction2
        """

        ## Main UI에 표기 및 함수 진입시 변수값 설정
        self.statusBar.showMessage("상장된 국내 회사의 거래량 정보를 업데이트 시작합니다.")
        self.progressBar_VolumeUpdate.setValue(0)

        self.progressbarSet = 0  # 거래량 업데이트 첫번째 시도

        self.dataControl.DeleteStockVolumeAll()  # DB에서 기존 거래량 삭제

        tempShcode = self.dataControl.CallStockList()  # StockList에서 shcode 불러옴

        for temp in tempShcode:
            listShcode = list(temp)
            self.shcodeStockList = self.shcodeStockList + listShcode

        self.lenStockList = len(self.shcodeStockList)

        self.countStockList = 0

        self.VolumeUpdateFunction1(self.shcodeStockList[self.countStockList], request=[])

    def VolumeUpdateFunction1(self, 단축코드=None, request=None):
        if request is None:
            request = []

        if len(request) > 0:  # 연속조회
            날짜, 잔여건수 = request

            QTimer.singleShot(Delay3s, lambda: self.gett1305.Query(단축코드=단축코드, 일주월구분='1', 날짜=날짜, IDX='',
                                                                   건수=잔여건수, 연속조회=True))
        else:  # 첫 조회
            QTimer.singleShot(Delay3s, lambda: self.gett1305.Query(단축코드=단축코드, 일주월구분='1', 날짜='', IDX='',
                                                                   건수=VolumeDuration, 연속조회=False))

    def VolumeUpdateFunction2(self, result=None):
        if result is None:
            result = []

        단축코드, Out날짜, Out건수, 건수 = result
        if (Out건수 - 건수) >= 0:  # 연속 조회가 필요 없을 때
            self.statusBar.showMessage("거래량 업데이트 중 : " + str(self.shcodeStockList[self.countStockList]) + " - " +
                                       str(self.countStockList + 1) + " 번째 기업 업데이트")

            if self.countStockList != (self.lenStockList - 1):  # 거래량 업데이트 할 종목이 더 남았을 때
                self.countStockList = self.countStockList + 1

                if self.progressbarSet == 0:  # 종목 업데이트 최초 시도 시
                    self.progressBar_VolumeUpdate.setValue(int(self.countStockList * (100 / self.lenStockList)))
                else:  # 종목 업데이트 재 시도 시
                    self.progressBar_VolumeRetry.setValue(int((self.countStockList - self.retryCount) *
                                                              (100 / (self.lenStockList - self.retryCount))))

                self.VolumeUpdateFunction1(self.shcodeStockList[self.countStockList], request=[])  # 다음 종목 호출
            else:  # 모든 종목의 거래량 업데이트 완료 시
                self.statusBar.showMessage("상장된 국내 회사의 거래량 정보가 업데이트 되었습니다.")

                if self.progressbarSet == 0:
                    self.progressBar_VolumeUpdate.setValue(100)
                    self.lastVolumeUpdateTime1 = datetime.datetime.today().strftime("%Y-%m-%d")
                    self.label_VolumeUpdate1.setText(" 마지막 업데이트 날짜 : " + self.lastVolumeUpdateTime1)
                else:
                    self.progressBar_VolumeRetry.setValue(100)
                    self.lastVolumeUpdateTime1 = datetime.datetime.today().strftime("%Y-%m-%d")
                    self.label_VolumeUpdate1.setText(" 마지막 업데이트 날짜 : " + self.lastVolumeUpdateTime1)
        else:  # 연속 조회가 필요 할 때
            잔여건수 = 건수 - Out건수
            self.VolumeUpdateFunction1(단축코드, request=[Out날짜, 잔여건수])

    def VolumeRetryFunction(self):
        """
        VolumeUpdateFunction이 도중에 중단 될 때,
        DB에 저장된 값 기준으로 종목의 거래량 업데이트 재 시작
        """
        self.retryCount = self.spinBox_VolumeRetry1.value()

        self.statusBar.showMessage("상장된 국내 회사의 거래량 정보를 업데이트 시작합니다.")
        self.progressBar_VolumeRetry.setValue(0)
        self.progressbarSet = 1

        tempShcode = self.dataControl.CallStockList()  # StockList에서 shcode 불러옴

        for temp in tempShcode:
            listShcode = list(temp)
            self.shcodeStockList = self.shcodeStockList + listShcode

        self.lenStockList = len(self.shcodeStockList)

        self.countStockList = self.retryCount - 1

        self.VolumeUpdateFunction1(self.shcodeStockList[self.countStockList], request=[])  # 거래량 Update 이어서 실행

    def StockPickFunction(self):
        """
        실시간 매매 알고리즘을 동작시킬 대상 기업을 선정
        """
        self.stockPickUpdate.StockPickAlgorithm()

        # self.gett1452.Query()
        # self.gett1463.Query()
        # 현재 동작안됨 - 불량주식 삭제했는데, 해당 종목이 1452/1463에 포함되서 들어가기때문!!
        # 여기에 하나 더, 거래량 서서히 증가중인 종목두 체크해야함

    def StockOrderFunction(self):
        """
        수동 주식 주문 기능
        """
        self.statusBar.showMessage("주식을 주문합니다.")
        self.orderingList = []
        self.mainCall = True

        self.stockAccount = self.lineEdit_StockOrder1.text()
        self.stockPassword = self.lineEdit_StockOrder2.text()
        self.stockShcode = self.lineEdit_StockOrder4.text()
        self.stockPrice = self.lineEdit_StockOrder5.text()
        self.stockVolume = self.lineEdit_StockOrder6.text()
        self.stockLoanDate = self.lineEdit_StockOrder10.text()
        self.stockMargin = self.comboBox_StockOrder3.currentData()
        self.stockSellBuy = self.comboBox_StockOrder7.currentData()
        self.stockBidAsk = self.comboBox_StockOrder8.currentData()
        self.stockOption = self.comboBox_StockOrder9.currentData()

        self.getCSPAT00600.Query(계좌번호=self.stockAccount, 입력비밀번호=self.stockPassword, 종목번호=self.stockShcode,
                                 주문수량=self.stockVolume, 주문가=self.stockPrice, 매매구분=self.stockSellBuy,
                                 호가유형코드=self.stockBidAsk, 신용거래코드=self.stockMargin, 대출일=self.stockLoanDate,
                                 주문조건구분=self.stockOption)

        self.getSC1.AdviseRealData()

    def QtableWidgetShowing(self, 분류='', 주문번호='', 종목명='', 매매구분='', 수량='', 체결가격='', 시각='', 체결번호=''):
        """
        주문 전송 및 체결 수신 관련 데이터를 사용자에게 제공
        """
        if 매매구분 == '1':
            매매구분 = '매도'
        elif 매매구분 == '2':
            매매구분 = '매수'

        self.countCurrentRow = self.tableWidget_StockOrder1.rowCount()
        self.tableWidget_StockOrder1.insertRow(self.countCurrentRow)

        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 0, QTableWidgetItem(분류))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 1, QTableWidgetItem(주문번호))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 2, QTableWidgetItem(종목명))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 3, QTableWidgetItem(매매구분))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 4, QTableWidgetItem(수량))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 5, QTableWidgetItem(체결가격))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 6, QTableWidgetItem(시각))
        self.tableWidget_StockOrder1.setItem(self.countCurrentRow, 7, QTableWidgetItem(체결번호))

    def AutoUpdate(self):
        """
        자동 업데이트 관련 함수 호출
        """
        self.checkBox_AutoUpdate.stateChanged.connect(self.AutoUpdateFunction)

    def AutoUpdateFunction(self):
        """
        자동 업데이트 상태일 때, 호출되는 함수 및 호출 주기 설정
        """
        if self.checkBox_AutoUpdate.isChecked() is True:
            today = datetime.today().strftime("%Y-%m-%d")
            date = int(today[8:10])
            if date == 1:
                self.ListUpdateFunction()
        else:
            pass

    def OnReceiveMessage(self, systemError, messageCode, message):
        print(systemError, messageCode, message)

    """ =LKH======================================================================================================== """

    def ActionListUpByFss(self):
        a = ListUpByFssFind().t1404start()
        b = ListUpByFssFind().t1405start()
        dartCorpCodeDataFrame = DartCorpListGet.Get()
        # upcodeTotalDataFrame = ListUpByFssFind().t8424start()  ## t8424후 t1516 자동 실행
        # c = ListUp_By_Fss_Find().FssByNAVERtoDB()

    def UpcodeUpdateFunction(self):
        self.upcodeTotalDataFrame = ListUpByFssFind(parent=self)
        self.upcodeTotalDataFrame.t8424start(baton=0)    ## t8424후 t1516 자동 실행
        self.statusBar.showMessage("업종별 기업 정보 새로 다운받기를 시작합니다.")

    def UpcodeUpdateRetryFunction(self):
        self.upcodeTotalDataFrame = ListUpByFssFind(parent=self)
        self.upcodeTotalDataFrame.t8424start(baton=1)
        self.statusBar.showMessage("업종별 기업 정보 이어받기를 시작합니다.")

    def FssUpdateFunction(self):
        print('FssUpdateFunction')
        self.statusBar.showMessage("재무제표 정보 새로 다운받기를 시작합니다.")
        self.getDartCorpList =  DartCorpListGet.Get()
        self.gett8430.Query(구분='0')

        # self.fssByNaver = ListUpByFssFind(parent=self)
        # QTimer.singleShot(100, lambda: self.fssByNaver.FssByNaverStart(0))

        self.fssByNaverNew = FssByNaverNew(parent=self)
        self.fssByNaverNew.start()

    def FssUpdateRetryFunction(self):
        print('FssRetryFunction')
        self.statusBar.showMessage("재무제표 정보 이어받기를 시작합니다.")
        self.getDartCorpList = DartCorpListGet.Get()
        self.gett8430.Query(구분='0')

        # self.fssByNaver = ListUpByFssFind(parent=self)
        # QTimer.singleShot(100, lambda: self.fssByNaver.FssByNaverStart(1))

        self.fssByNaverRetry = FssByNaverRetry(parent=self)
        self.fssByNaverRetry.start()

    def ActionListUpByFssShowUp(self):
        print('test ok')
        # listUpByFss = WebMainWindow(parent=self)  # 버튼을 눌렀을때의 서브 WINDOW 클래스
        listUpByFss = miniFssShow()
        listUpByFss.exec_()
        # EOLdlg = EOL_dialog()
        # EOLdlg.exec_()

    def UpcodeUpdateStatusChange(self, percent):
        self.upcodeUpdatePercent = str(percent)
        self.label_UpcodeUpdateStatus1.setText(self.upcodeUpdatePercent + '%')

    def FssStatusChange(self, percent):
        self.fssUpdatePercent = str(percent)
        self.label_FssUpdateStatus1.setText(self.fssUpdatePercent + '%')

    def RiskCorpUpdateFunction(self):
        a = ListUpByFssFind(parent=self).t1404start()
        b = ListUpByFssFind(parent=self).t1405start()

    def connectselectWholeFfs(self):
        c = selectWholeFfsThread(parent=self).start()


    """ =PKB======================================================================================================== """

    # 시총이 작은 회사들을 제거하는 함수
    # def SmallCapRemoveFunction(self):
    #     self.statusBar.showMessage("시총이 작은 회사들을 삭제하고 있습니다.")
    #     # 종목코드 리스트를 불러와서 저장
    #     StockList = self.dataControl.CallStockList()
    #
    #     print(StockList)  # 테스트 해보려 하는데 잘 안되네요 .....
    #
    #     # for shcode in StockList:
    #     #     self.gett1102.Query(shcode)
    #
    #     # self.gett1102.Query(StockList[0])
    #     self.gett1102.Query(StockList[1])
    #     # self.gett1102.Query(StockList[2])
    #     # self.gett1102.Query(StockList[3])
    #     # self.gett1102.Query(StockList[4])
    #
    ## 국내 회사 List Update 함수
    def t1102Function(self):
        self.mainCall = True
        self.gett1102 = t1102(parent=self)
        self.gett1102.Query(종목코드='005930')

    # 시총이 작은 회사들을 제거하는 함수
    def StockListFilterFunction(self):
        # 삭제하고싶은 시총 금액을 입력받음
        self.MarketCap = self.lineEdit_MarketCap.text()
        # 시총 X억 이하 종목을 삭제
        self.dataControl.StockListFilter(self.MarketCap)
        # 1404, 1405 종목을 삭제
        self.dataControl.DeleteStockList(self.dataControl.Call1404WarnList())
        self.dataControl.DeleteStockList(self.dataControl.Call1405WarnList())

    def MarketCapFunction(self):
        self.statusBar.showMessage("시총 정보를 불러오고 있습니다.")
        # 종목코드 리스트를 불러와서 저장
        StockListTuple = self.dataControl.CallStockList()
        # StockList에 list 형식으로 저장
        self.StockList = []
        for temp in StockListTuple:
            listValue = list(temp)  # 튜플을 리스트로 변환
            self.StockList = self.StockList + listValue  # 리스트 합침
        # 루프에 필요한 파라미터 생성
        self.StockListLen = len(self.StockList)
        self.countStockList1 = 0

        print('self.StockList : {}'.format(self.StockList))
        print('총 갯수 : {}'.format(self.StockList))

        self.MarketCapFunction1(self.StockList[self.countStockList1])

    def MarketCapFunction1(self, 종목코드=None):
        QTimer.singleShot(delay_0_2s, lambda: self.gett1102.Query(종목코드=종목코드))

    def MarketCapFunction2(self):
        if (self.countStockList1 != self.StockListLen + 1):
            self.countStockList1 += 1
            self.MarketCapFunction1(self.StockList[self.countStockList1])
        else:
            self.statusBar.showMessage("시총 업뎃완")
            print('시총 업뎃완')



if __name__ == '__main__':
    def MainExitFunction(parent='None'):
        programSet = SystemSetting()
        programSet.SaveSystemSetting(parent=parent)


    app = QApplication(sys.argv)
    windowMain = MainWindow()
    windowMain.show()

    # windowSample = SampleWindow()
    # windowSample.show()
    # Process(name="SubProcess", target=windowSample)

    atexit.register(MainExitFunction, parent=windowMain)
    app.exec_()
