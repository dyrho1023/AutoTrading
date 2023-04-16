from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import time
import pandas as pd
import numpy as np
import sys
import sqlite3
# from ListUpByFssFind import *



# UISubWindow = uic.loadUiType("Stock_UI.ui")[0]
# UISubWindow = uic.loadUiType("untitled.ui")[0]
sub_class =  uic.loadUiType(r"miniFssShow.ui")[0]
# sub_class =  uic.loadUiType(r"C:\Users\com\python\python_v_test\PyqtWithUic2.ui")[0]
# UISubWindow = uic.loadUiType("FssView_UI.ui")[0]


class miniFssShow(QDialog, QWidget, sub_class):           ## 'EOL 테이블 입력' 버튼을 눌렀을때의 서브 WINDOW 클래스

    def __init__(self):
        super(miniFssShow, self).__init__()
        self.setupUi(self)
        self.show()


        # self.comboBoxRatioSum1.addItem('Apple')
        # self.comboBoxRatioSum1.addItem('Banana')


        with sqlite3.connect('Dart.db') as conn:
            self.totalFssDataFrame = pd.read_sql("SELECT * FROM Totalinfo", con=conn,  index_col=None)


        # self.PushButtonAction()
        self.settingAction()


    def settingAction(self):
        """
        ComboBox 선택 액션
        """

        comboList = list(self.totalFssDataFrame.columns)

        self.comboBoxRatioSum1.addItems(comboList)
        self.comboBoxRatioSum2.addItems(comboList)
        self.comboBoxRatioSum3.addItems(comboList)
        self.comboBoxRatioSum4.addItems(comboList)
        self.comboBoxRatioSum5.addItems(comboList)
        self.comboBoxRatioSum6.addItems(comboList)


        # self.comboBoxRatioSumSet1 = self.comboBoxRatioSum1.currentData()
        # self.comboBoxRatioSumSet2 = self.comboBoxRatioSum2.currentData()
        # self.comboBoxRatioSumSet3 = self.comboBoxRatioSum3.currentData()
        # self.comboBoxRatioSumSet4 = self.comboBoxRatioSum4.currentData()
        # self.comboBoxRatioSumSet5 = self.comboBoxRatioSum5.currentData()
        # self.comboBoxRatioSumSet6 = self.comboBoxRatioSum6.currentData()

        self.lineEditRatioSum1.text()
        self.lineEditRatioSum2.text()
        self.lineEditRatioSum3.text()
        self.lineEditRatioSum4.text()
        self.lineEditRatioSum5.text()
        self.lineEditRatioSum6.text()

        # self.currentYear = self.dateEditSetYear.text().split('-')[0]
        # print(self.currentYear)

        # self.lineEditNYearInput

        # finvizLike.receiveInput(self.totalFssDataFrame, self.currentYear, self.lineEditNYearInput)
        # view1 = finvizLike()
        # print('2')

        self.pushButtonShow.clicked.connect(self.receiveInput)



        # self.comboBoxRatioSum1.currentIndexChanged.connect(self.comboBoxRatioSum1.setCurrentIndex)  ## 콤보 항목이 변경될때 이벤트 발생시키는 코드


    def receiveInput(self):

    ## 기본 필터 : n개년치 뽑아내기 ##
        # with sqlite3.connect('Dart.db') as conn:
        #     corpGroupByUpcodeDataFrame = pd.read_sql("SELECT * FROM Totalinfo", con=conn, index_col=None)
        # print(corpGroupByUpcodeDataFrame)
        corpGroupByUpcodeDataFrame = self.totalFssDataFrame

        # currentYear = "2021"   ## input
        currentYear = self.dateEditSetYear.text().split('-')[0]

        # nYears = 3  ## input
        if self.lineEditNYearInput.text() == '':
            nYears = 3
        else:
            nYears = int(self.lineEditNYearInput.text())

        listYears = []
        for i in range(0, nYears):
            shittTime = str(int(currentYear) - i) + "/12(Y)"
            listYears.append(shittTime)
        print(listYears)


        ## 기본 필터 : 12(Y)만 뽑아내기 ##
        # a = corpGroupByUpcodeDataFrame[corpGroupByUpcodeDataFrame["시점"].str.contains(pat = "12\(Y\)")]
        # print(a)

        c = corpGroupByUpcodeDataFrame[corpGroupByUpcodeDataFrame["시점"].isin(listYears)]





        ## 조건부 필터 ##


        ## 부채는 어떻게 활용?
        # inputFilterSeries = pd.Series({ 'PBR' : 0.05, 'EV/EBITDA' : 0.03, 'ROA': None, 'ROIC': 0.03, 'ROE' : 0.05, '세전계속사업이익': 0.03, '매출총이익': 0.05})

        inputFilterSeries= pd.Series({'매출총이익' : self.lineEdit_1.text(),  '매출액' : self.lineEdit_2.text(),
                                      '영업이익' : self.lineEdit_3.text(), 'EPS': self.lineEdit_4.text(),
                                      'BPS': self.lineEdit_5.text(), 'CPS' :self.lineEdit_6.text(),
                                      'SPS': self.lineEdit_7.text(), 'PER': self.lineEdit_8.text(),
                                      'PBR' : self.lineEdit_9.text(),  'PCR' : self.lineEdit_10.text(),
                                      'PSR' : self.lineEdit_11.text(),  '현금DPS' : self.lineEdit_12.text(),
                                      '주식DPS' : self.lineEdit_13.text(),  '현금배당수익률' : self.lineEdit_14.text(),
                                      '현금배당성향%' : self.lineEdit_15.text(),  'ROE' : self.lineEdit_16.text(),
                                      'ROA' : self.lineEdit_17.text(),  'ROIC' : self.lineEdit_18.text(),
                                      '세전사업이익' : self.lineEdit_19.text(),  '당기순이익' : self.lineEdit_20.text()})

        inputFilterSeries = inputFilterSeries.str.strip().replace('', np.nan).replace('N/A', np.nan).dropna()
        d = c.copy()

        for i in inputFilterSeries.index:
            filterPassList = []
            for k in set(c['종목코드']):
                # print( inputFilterSeries[i] , i)
                if d.loc[(d['시점'] == listYears[0]) & (d['종목코드'] == k), i].values >=  d.loc[(d['시점'] == listYears[-1]) & (d['종목코드'] == k), i].values * (1 + float(inputFilterSeries[i])/100 )**(nYears-1):
                    filterPassList.append(k)
            d = d[d["종목코드"].isin(filterPassList)]

        print('##############################################')
        # print(d["종목코드"])
        # d.to_excel('test_d.xlsx')

        # f = pd.pivot_table(d, index="종목코드", values= ["EV/EBITDA", "ROIC"]).sort_values(by = ["EV/EBITDA", "ROIC"], ascending= False)
        ## 이렇게 하면 첫번째 컬럼 정렬 이후 두번째 컬럼을 기준으로 정렬함 (동일 우선순위 아님)
        # print(f)


        print('12')
        # pivotUsedList = list(d.columns).remove('종목코드')  #.remove('시점').remove('크롤링_시간')
        # feature1 = "EV/EBITDA"      ## input
        # feature2 = "ROIC"           ## input
        # feature3 = "ROE"            ## input
        # # ratio1 = 0.5            ## input
        # # ratio2 = 0.5            ## input
        # # ratio3 = 0.5            ## input

        feature1 = self.comboBoxRatioSum1.currentText()
        feature2 = self.comboBoxRatioSum2.currentText()
        feature3 = self.comboBoxRatioSum3.currentText()
        feature4 = self.comboBoxRatioSum4.currentText()
        feature5 = self.comboBoxRatioSum5.currentText()
        feature6 = self.comboBoxRatioSum6.currentText()
        print(self.comboBoxRatioSum1.currentText(), type(self.comboBoxRatioSum1.currentText()))
        ratio1 = self.lineEditRatioSum1.text()
        ratio2 = self.lineEditRatioSum2.text()
        ratio3 = self.lineEditRatioSum3.text()
        ratio4 = self.lineEditRatioSum4.text()
        ratio5 = self.lineEditRatioSum5.text()
        ratio6 = self.lineEditRatioSum6.text()

        userInputRatio = {feature1 : ratio1, feature2 : ratio2,  feature3 : ratio3, feature4 : ratio4, feature5 : ratio5, feature6 : ratio6 }

        del (userInputRatio['시점'])  ## 콤보 박스에서 '시점'이 선택된 것은 미선택한것으로 취급하여, 삭제함

        print('11')




        dNew = d.select_dtypes(include = ['float', 'int'])
        normalization_d = (dNew - dNew.mean())/dNew.std()
        print(normalization_d)

        normalization_d['종목코드'] = d['종목코드'].copy()
        normalization_d['시점'] = d['시점'].copy()
        normalization_d['크롤링_시간'] = d['크롤링_시간'].copy()

        print(normalization_d)


        g = pd.pivot_table(normalization_d, index="종목코드", values= None)

        g['mix'] = 0

        for key, value in userInputRatio.items():
            g['mix'] += g[key]*float(value)
            print(g[key]*float(value), g[key], value)


        # g['mix']= g[feature1]*ratio1+ g[feature2]*ratio2 + g[feature3]*ratio3
        # g = g.sort_values(by = 'mix' , ascending=False)

        h = pd.pivot_table(d, index="종목코드", values= None)

        h['mix'] = g['mix'].copy()

        h = h.sort_values(by='mix', ascending=False)

        self.tableWidgetView.setColumnCount(len(h.columns))
        self.tableWidgetView.setRowCount(len(h.columns))
        self.tableWidgetView.setHorizontalHeaderLabels(list(h.columns))
        self.tableWidgetView.setVerticalHeaderLabels(list(h.index))


        for i in range(len(h.index)):
            for j in range(len(h.columns)):
                self.tableWidgetView.setItem(i, j, QTableWidgetItem(str(h.iloc[i, j])))

        self.viewDataFrame = h
        self.pushButtonToExcel.clicked.connect(self.ToExcel)

    def ToExcel(self):
        self.viewDataFrame.to_excel('viewDataFrame.xlsx')
#

#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mywindow = miniFssShow()
#     mywindow.show()
#     app.exec_()