
import pandas as pd
import sys
import time
from datetime import datetime
import sqlite3
import math
import traceback

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

from XASession import *
from XAQueries import *



from Dart import *
from FssByNaver import *
# from FindRiskList import *

class selectWholeFfs():
    def do(self):
        wholeTableFssDataFrame = pd.DataFrame()

        with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1 ;")

            for i in cursor:
                stockTRDataFrame = pd.read_sql('SELECT * FROM "{}" '.format(i[0]), conn, index_col=None)
                wholeTableFssDataFrame = pd.concat([wholeTableFssDataFrame, stockTRDataFrame], axis=0, ignore_index=True)

        with sqlite3.connect('Dart.db') as conn:
            wholeTableFssDataFrame.to_sql('Totalinfo', con=conn, if_exists='replace', index=False)

        return wholeTableFssDataFrame


class selectWholeFfsThread(QThread):
    def __init__(self, parent=None):  # parent는 WndowClass에서 전달하는 self이다.(WidnowClass의 인스턴스)
        super().__init__(parent)
        self.parent = parent  # self.parent를 사용하여 WindowClass 위젯을 제어할 수 있다.

    def stop(self):
        print('view 생성완료')
        self.quit()

    def __del__(self):
        print(self.__class__, '삭제')

    def run(self):  ## FssByNaverStart 대체
        print('view 생성시작')
        wholeTableFssDataFrame = pd.DataFrame()

        with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1 ;")

            for i in cursor:
                stockTRDataFrame = pd.read_sql('SELECT * FROM "{}" '.format(i[0]), conn, index_col=None)
                wholeTableFssDataFrame = pd.concat([wholeTableFssDataFrame, stockTRDataFrame], axis=0, ignore_index=True)

        with sqlite3.connect('Dart.db') as conn:
            wholeTableFssDataFrame.to_sql('Totalinfo', con=conn, if_exists='replace', index=False)

        self.stop()






class ListUpByFssFind(XAQuery):


    def t1404start(self):
        # a = t1404().Query("0", '1')
        self.gett1404 = t1404(parent=self)

        self.gett1404.Query(구분='0', 종목체크='1', 종목체크_CTS=' ', 연속조회=False)
        self.t1404df = pd.DataFrame()


    def t1404receive(self, 구분, 종목체크, Re종목체크_CTS, 연속조회, t1404df):
        # print(Re종목체크_CTS, 종목체크)

        delay_2s = 2000
        self.t1404df = pd.concat([self.t1404df, t1404df], axis= 0)

        # print(Re종목체크_CTS, 종목체크)
        if len(Re종목체크_CTS) < 1:
            if int(종목체크) == 4:
                self.t1404df = self.t1404df.reset_index(drop = True)
                self.t1404df.to_excel('t1404.xlsx')

                with sqlite3.connect('TradingDB.db') as conn:
                    self.t1404df.to_sql('1404WarningList', con=conn, if_exists='replace', index=False)

                # print('종료', self.t1404df, sep='\n')

            else :
                종목체크 = int(종목체크) + 1
                연속조회 = False
                QTimer.singleShot(delay_2s,lambda: self.gett1404.Query(구분=구분, 종목체크=str(종목체크), 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회))

        else:
            연속조회 = True
            # self.gett1404.Query(구분=구분, 종목체크=종목체크, 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회)
            QTimer.singleShot(delay_2s, lambda: self.gett1404.Query(구분=구분, 종목체크=종목체크, 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회))


    def t1405start(self):
        # a = t1404().Query("0", '1')
        self.gett1405 = t1405(parent=self)

        self.gett1405.Query(구분='0', 종목체크='1', 종목체크_CTS=' ', 연속조회=False)
        self.t1405df = pd.DataFrame()


    def t1405receive(self, 구분, 종목체크, Re종목체크_CTS, 연속조회, t1405df):
        # print(Re종목체크_CTS, 종목체크)
        delay_2s = 2000
        self.t1405df = pd.concat([self.t1405df, t1405df], axis= 0)

        # print(Re종목체크_CTS, 종목체크)
        if len(Re종목체크_CTS) < 1:

            if int(종목체크) == 9:

                self.t1405df = self.t1405df.reset_index(drop = True)
                self.t1405df.to_excel('t1405.xlsx')
                currenttime = datetime.datetime.today().strftime("%Y%m%d")
                self.parent.RiskCorpUpdateLastDate = currenttime

                with sqlite3.connect('TradingDB.db') as conn:
                    self.t1405df.to_sql('1405WarningList', con=conn, if_exists='replace', index=False)

                return None
                # print('종료', self.t1405df, sep='\n')

            else :
                if int(종목체크) == 7:
                    종목체크 = int(종목체크) + 2
                else:
                    종목체크 = int(종목체크) + 1
                연속조회 = False
                QTimer.singleShot(delay_2s,lambda: self.gett1405.Query(구분=구분, 종목체크=str(종목체크), 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회))

        else:
            연속조회 = True
            # self.gett1404.Query(구분=구분, 종목체크=종목체크, 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회)
            QTimer.singleShot(delay_2s, lambda: self.gett1405.Query(구분=구분, 종목체크=종목체크, 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회))


    def t8424start(self, baton=0):   ## baton : 이어받기, 0은 새로받기    1은 이어받기
        self.t8424t1516Baton = baton
        self.gett8424 = t8424(parent=self)
        self.gett8424.Query("0")
        # return upcodeTotalDataFrame

    def t8424receive(self, upcodeTotalDataFrame):

        currentTime = datetime.datetime.today().strftime("%Y%m%d")
        with sqlite3.connect('upcodeData.db') as conn:
            upcodeTotalDataFrame.to_sql('upcodeTotalList', con=conn, if_exists='replace', index=False)
        with sqlite3.connect('upcodeData.db') as conn:
            upcodeTotalDataFrame.to_sql('{}_upcodeTotalList'.format(currentTime), con=conn, if_exists='replace', index=False)

        print('t8424 완료')
        self.t1516start()


    def t1516start(self):
        self.t1516Stop = 0   ## stop 여부 체크  (0: 계속, 1: 중지)

        with sqlite3.connect('upcodeData.db') as conn:
            self.upcodeTotalDataFrame = pd.read_sql("SELECT * FROM upcodeTotalList", con=conn,  index_col=None)

        if self.t8424t1516Baton == 0:  ## 새로 받기

            ### 새로 받기시, 기존 테이블의 테이블명을 바꿀때, 덮어쓰기가 가능하도록 할지 말지를 결정하는 코드 필요  ###
            try:  ### 새로 받기시, 기존 테이블이 존재할경우 테이블명에 날짜 추가하여 테이블 복사해놓는 코드
                with sqlite3.connect('upcodeData.db') as conn:
                    self.corpGroupByUpcodeDataFrame = pd.read_sql("SELECT * FROM corpGroupByUpcodeList", con=conn,  index_col=None)
            except:
                print('에러 발생!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            else:
                date = self.corpGroupByUpcodeDataFrame['TR조회일'][0]
                with sqlite3.connect('upcodeData.db') as conn:
                    self.corpGroupByUpcodeDataFrame.to_sql('{}_corpGroupByUpcodeList'.format(date), con=conn, if_exists='replace', index=False)

            self.upcodeIndex = 1  ## 업종명이 '종합'인 것은 제외하기 위해 0이 아니라 1부터 시작 (개수가 너무 많음)
            self.upcodeStartIndex = 1
            self.upcodePercentPrev = 0
            self.gett1516 = t1516(parent=self)
            self.gett1516.Query(업종코드=self.upcodeTotalDataFrame['업종코드'][self.upcodeIndex], 구분='', 종목코드='',연속조회=False)  ## 업종명이 '종합'인 것은 제외하기 위해 001이 아니라 002부터 시작 (개수가 너무 많음)
            self.t1516df = pd.DataFrame()

        else:   ## 이어받기
            with sqlite3.connect('upcodeData.db') as conn:
                self.corpGroupByUpcodeDataFrame = pd.read_sql("SELECT * FROM corpGroupByUpcodeList", con=conn,  index_col=None)

            self.t1516df = self.corpGroupByUpcodeDataFrame.copy()

            if self.corpGroupByUpcodeDataFrame.iloc[-1][1] == self.upcodeTotalDataFrame.iloc[-1][1] :   ## 두개의 데이터프레임의 마지막 업종코드가 동일한 상태 -> 이어받기가 필요없이 새로 받기 실행
                self.upcodeIndex = 1  ## 업종명이 '종합'인 것은 제외하기 위해 0이 아니라 1부터 시작 (개수가 너무 많음)
                self.upcodeStartIndex = 1

            else:
                self.upcodeIndex = 1 + self.upcodeTotalDataFrame.index[self.upcodeTotalDataFrame['업종코드'] == self.corpGroupByUpcodeDataFrame.iloc[-1][0]][0]
                self.upcodeStartIndex = self.upcodeIndex


            self.gett1516 = t1516(parent=self)
            self.gett1516.Query(업종코드=self.upcodeTotalDataFrame['업종코드'][self.upcodeIndex], 구분='', 종목코드='',연속조회=False)  ## 업종명이 '종합'인 것은 제외하기 위해 001이 아니라 002부터 시작 (개수가 너무 많음)

        self.upcodePercentPrev = math.ceil(self.upcodeIndex / (len(self.upcodeTotalDataFrame['업종코드']) - self.upcodeStartIndex))


    def t1516receive(self, 업종코드, 구분, Re종목코드, 연속조회, t1516df):


        if self.parent.checkBox_UpCodeUpdateStop1.isChecked() is True:
            QTimer.singleShot(50, lambda: self.parent.checkBox_UpCodeUpdateStop1.setChecked(False))

            with sqlite3.connect('upcodeData.db') as conn:
                self.corpGroupByUpcodeDataFrame = pd.read_sql("SELECT * FROM corpGroupByUpcodeList ORDER BY TR조회일 DESC", con=conn,  index_col=None)
            self.parent.UpCodeUpdateLastDate = self.corpGroupByUpcodeDataFrame['TR조회일'][0]



            return None
            # raise ValueError

        delay_3s = 3000
        self.t1516df = pd.concat([self.t1516df, t1516df], axis=0)


        if (len(Re종목코드) < 1) :

            currentTime = datetime.datetime.today().strftime("%Y%m%d")
            self.t1516df['TR조회일'] = currentTime
            print(self.t1516df)

            with sqlite3.connect('upcodeData.db') as conn:
                self.t1516df.to_sql('corpGroupByUpcodeList', con=conn, if_exists='replace', index=False)

            self.upcodePercent = math.ceil( (100 * self.upcodeIndex) / (len(self.upcodeTotalDataFrame['업종코드'])))

            if self.upcodePercent >= self.upcodePercentPrev + 1:   # 1% 업데이트 증가 완료시마다 사용자에게 보여줌

                self.parent.UpcodeUpdateStatusChange(self.upcodePercent)

            if self.upcodeIndex  == len(self.upcodeTotalDataFrame['업종코드'])-1:  ## index값이므로, 길이에서 1을 뺀다.
                print('t1516 완료')
                return None

            else:
                self.upcodeIndex += 1
                업종코드 = self.upcodeTotalDataFrame.iloc[self.upcodeIndex][1]

                연속조회 = False
                QTimer.singleShot(delay_3s, lambda: self.gett1516.Query(업종코드 = 업종코드, 구분= 구분, 종목코드=Re종목코드,연속조회=연속조회))

        else:
            연속조회 = True
            # self.gett1404.Query(구분=구분, 종목체크=종목체크, 종목체크_CTS=Re종목체크_CTS, 연속조회=연속조회)
            QTimer.singleShot(delay_3s, lambda: self.gett1516.Query(업종코드 = 업종코드, 구분= 구분, 종목코드=Re종목코드,연속조회=연속조회))

        # except ValueError:
        #     print('11')
        #     pass




######## QThread 활용하기 전의 코드 #############
    # def FssByNaverStart(self, baton):
    #     self.fssByNaverStop = 0
    #     self.fssByNaverBaton = baton
    #     # try:
    #     #     with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
    #     #         self.errorDataFrame = pd.read_sql('SELECT * FROM errorFssNaver', conn, index_col=None)
    #     # except Exception:  ## DB에 없으면 생성
    #     #     self.errorDataFrame = pd.DataFrame( columns=['shcode'])
    #
    #
    #     with sqlite3.connect('Dart.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
    #         self.corpDartDataFrame = pd.read_sql('SELECT * FROM currentCorpList', conn, index_col=None)
    #
    #
    #     with sqlite3.connect('TradingDB.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
    #         self.stockTRDataFrame = pd.read_sql('SELECT * FROM StockList ORDER BY shcode ASC', conn, index_col=None)
    #
    #     print(self.stockTRDataFrame)
    #
    #     ## 새로 받기일때
    #     if self.fssByNaverBaton == 0:
    #         # currentTime = datetime.datetime.today().strftime("%Y%m%d")
    #         self.fssByNaverStartIndex = 0
    #
    #
    #     ## 이어 받기일때
    #     else:
    #
    #         con = sqlite3.connect('FssData.db')
    #         cursor = con.cursor()
    #         # cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'FssData.db'")  ## sqlite3는 information_schema.tables를 지원하지 않음
    #         cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1 ;")
    #         a = []
    #
    #         for i in cursor:
    #             a.append(i)
    #
    #         if len(a) == 0 : ## 이어받기를 실행했으나 DB에 데이터가 없을때
    #             self.fssByNaverStartIndex = 0  ## 새로받기로 실행
    #         else :
    #             self.fssByNaverStartIndex = self.stockTRDataFrame[self.stockTRDataFrame['shcode'] == a[-1][0]].index[0] + 1
    #             print('가장 최근에 받은 자료(shcode)',a[-1][0],self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex])
    #
    #     self.FssByNaver()
    #
    #
    # def FssByNaver(self):
    #
    #     try:
    #         if self.corpDartDataFrame['종목코드'].isin([self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]]).sum() == 1:
    #             print(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex], self.fssByNaverStartIndex,'\n')
    #             a = FssByNaver().Get(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex])
    #     except Exception:
    #         w = traceback.format_exc().splitlines()
    #         w.append(str(datetime.datetime.now()))
    #         k = w[1].split(',')
    #         print('error trace:' , k)
    #         self.errorDataFrame = self.errorDataFrame.append({'shcode': self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]}, ignore_index=True)
    #         with sqlite3.connect('Dart.db') as conn:
    #             self.errorDataFrame.to_sql('error_FssNaver', con=conn, if_exists='replace', index=False)
    #         with open("error_at_{}_{}.txt".format(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex], k[1]), "w") as f:
    #             for v in w:  # w라는 list에서 1개의 원소씩 꺼내어 write함
    #                 v += '\n'
    #                 f.writelines(v)
    #     else:
    #         self.fssUpdatePercent = math.ceil(100 * self.fssByNaverStartIndex / len(self.stockTRDataFrame['shcode']))
    #         self.parent.FssStatusChange(self.fssUpdatePercent)
    #
    #     finally:
    #         if self.parent.checkBox_FssUpdateStop1.isChecked() is True:
    #             QTimer.singleShot(50, lambda: self.parent.checkBox_FssUpdateStop1.setChecked(False))
    #             return None
    #
    #         if self.fssByNaverStartIndex > len(self.stockTRDataFrame['shcode']):
    #             print('Fss 업데이트 완료')
    #             return None
    #
    #         self.fssByNaverStartIndex += 1  ## 에러가 생겼을때 다음 단계 호출
    #         self.FssByNaver()



### FSS 이어받기 실행 클래스 (QTread 적용)
class FssByNaverRetry(QThread):

    def __init__(self, parent=None):  # parent는 WndowClass에서 전달하는 self이다.(WidnowClass의 인스턴스)
        super().__init__(parent)
        self.parent = parent  # self.parent를 사용하여 WindowClass 위젯을 제어할 수 있다.

    def stop(self):
        print('stop')
        self.quit()

    def __del__(self):
        print(self.__class__, '삭제')


    def run(self):   ## FssByNaverStart 대체
        # self.fssByNaverStop = 0
        self.fssByNaverBaton = 1  ## 이어받기 일때 1로 지정
        # try:
        #     with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
        #         self.errorDataFrame = pd.read_sql('SELECT * FROM errorFssNaver', conn, index_col=None)
        # except Exception:  ## DB에 없으면 생성
        #     self.errorDataFrame = pd.DataFrame( columns=['shcode'])

        with sqlite3.connect('Dart.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            self.corpDartDataFrame = pd.read_sql('SELECT * FROM currentCorpList', conn, index_col=None)

        with sqlite3.connect('TradingDB.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            self.stockTRDataFrame = pd.read_sql('SELECT * FROM StockList ORDER BY shcode ASC', conn, index_col=None)

        print(self.stockTRDataFrame)


        ## 이어 받기일때

        con = sqlite3.connect('FssData.db')
        cursor = con.cursor()
        # cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'FssData.db'")  ## sqlite3는 information_schema.tables를 지원하지 않음
        cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1 ;")
        a = []

        for i in cursor:
            a.append(i)

        if len(a) == 0:  ## 이어받기를 실행했으나 DB에 데이터가 없을때
            self.fssByNaverStartIndex = 0  ## 새로받기로 실행
        else:
            self.fssByNaverStartIndex = self.stockTRDataFrame[self.stockTRDataFrame['shcode'] == a[-1][0]].index[0] + 1
            print('가장 최근에 받은 자료(shcode):',a[-1][0])

        self.FssByNaver()


    def FssByNaver(self):
        print(self.parent.checkBox_FssUpdateStop1.isChecked())

        while not ((self.parent.checkBox_FssUpdateStop1.isChecked()) | (self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']))):     ## 중지 체크박스에 체크가 되기 전까지 무한 루프 실행됨 (while은 조건문이 True이면 계속 실행)

            try:
                if self.corpDartDataFrame['종목코드'].isin([self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]]).sum() == 1:
                    print(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex], self.fssByNaverStartIndex)
                    a = FssByNaver().Get(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex])
            except Exception:
                w = traceback.format_exc().splitlines()
                w.append(str(datetime.datetime.now()))
                k = w[1].split(',')
                print('error trace:', k)
                self.errorDataFrame = self.errorDataFrame.append({'shcode': self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]}, ignore_index=True)
                with sqlite3.connect('Dart.db') as conn:
                    self.errorDataFrame.to_sql('error_FssNaver', con=conn, if_exists='replace', index=False)
                with open("error_at_{}_{}.txt".format(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex], k[1]), "w") as f:
                    for v in w:  # w라는 list에서 1개의 원소씩 꺼내어 write함
                        v += '\n'
                        f.writelines(v)
            else:
                self.fssUpdatePercent = math.ceil(100 * self.fssByNaverStartIndex / len(self.stockTRDataFrame['shcode']))
                self.parent.FssStatusChange(self.fssUpdatePercent)

            finally:
                # if self.parent.checkBox_FssUpdateStop1.isChecked() is True:
                #     QTimer.singleShot(50, lambda: self.parent.checkBox_FssUpdateStop1.setChecked(False))
                #     return None

                # if self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']):
                #     print('Fss 업데이트 완료')
                #     break
                    # return None

                # else:
                self.fssByNaverStartIndex += 1  ## 에러가 생겼을때 다음 단계 호출

        if self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']):
            print('Fss 업데이트 완료')

        print('중지 check')
        self.parent.checkBox_FssUpdateStop1.setChecked(False)

        wholeTableFssDataFrame = selectWholeFfs().do()
        sorted_wholeTableFssDataFrame = wholeTableFssDataFrame.sort_values(by=['크롤링_시간'], axis=0)

        a = sorted_wholeTableFssDataFrame['크롤링_시간'][len(sorted_wholeTableFssDataFrame['크롤링_시간']) - 1].split(' ')
        b = a[0].split('-')
        self.parent.FssUpdateLastDate[0] = ''.join(b)

        a = sorted_wholeTableFssDataFrame['크롤링_시간'][0].split(' ')
        b = a[0].split('-')
        self.parent.FssUpdateLastDate[1] = ''.join(b)

        time.sleep(5)
        self.stop()
        # QTimer.singleShot(3000, lambda: self.stop())
        # self.stop()
        # print('123')
        # return None



### FSS 새로받기 실행 클래스 (QTread 적용)
class FssByNaverNew(QThread):

    def __init__(self, parent=None):  # parent는 WndowClass에서 전달하는 self이다.(WidnowClass의 인스턴스)
        super().__init__(parent)
        self.parent = parent  # self.parent를 사용하여 WindowClass 위젯을 제어할 수 있다.

    def stop(self):
        print('stop')
        self.quit()

    def __del__(self):
        print(self.__class__, '삭제')

    def run(self):  ## FssByNaverStart 대체
        # self.fssByNaverStop = 0
        self.fssByNaverBaton = 0  ## 이어받기 일때 1로 지정
        # try:
        #     with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
        #         self.errorDataFrame = pd.read_sql('SELECT * FROM errorFssNaver', conn, index_col=None)
        # except Exception:  ## DB에 없으면 생성
        #     self.errorDataFrame = pd.DataFrame( columns=['shcode'])

        with sqlite3.connect('Dart.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            self.corpDartDataFrame = pd.read_sql('SELECT * FROM currentCorpList', conn, index_col=None)

        with sqlite3.connect('TradingDB.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
            self.stockTRDataFrame = pd.read_sql('SELECT * FROM StockList ORDER BY shcode ASC', conn, index_col=None)


        # try:
        #     with sqlite3.connect('FssData.db') as conn:
        #         conn.execute('DROP TABLE Totalinfo')
        #
        # except:
        #     pass

        self.fssByNaverStartIndex = 0

        print('처음부터 새로받기를 시작합니다')

        self.FssByNaver()

    def FssByNaver(self):
        print(self.parent.checkBox_FssUpdateStop1.isChecked())

        while not((self.parent.checkBox_FssUpdateStop1.isChecked()) | (self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']))):  ## 중지 체크박스에 체크가 되기 전까지 무한 루프 실행됨 (while은 조건문이 True이면 계속 실행)
            try:
                if self.corpDartDataFrame['종목코드'].isin([self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]]).sum() == 1:
                    print(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex], self.fssByNaverStartIndex)
                    ffsDataFrame = FssByNaver().Get(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex])


            except Exception:
                w = traceback.format_exc().splitlines()
                w.append(str(datetime.datetime.now()))
                k = w[1].split(',')
                print('error trace:', k)
                self.errorDataFrame = self.errorDataFrame.append(
                    {'shcode': self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex]}, ignore_index=True)
                with sqlite3.connect('Dart.db') as conn:
                    self.errorDataFrame.to_sql('error_FssNaver', con=conn, if_exists='replace', index=False)
                with open(
                        "error_at_{}_{}.txt".format(self.stockTRDataFrame['shcode'].iloc[self.fssByNaverStartIndex],
                                                    k[1]), "w") as f:
                    for v in w:  # w라는 list에서 1개의 원소씩 꺼내어 write함
                        v += '\n'
                        f.writelines(v)
            else:
                self.fssUpdatePercent = math.floor(100 * self.fssByNaverStartIndex / len(self.stockTRDataFrame['shcode']))
                self.parent.FssStatusChange(self.fssUpdatePercent)

            finally:
                # if self.parent.checkBox_FssUpdateStop1.isChecked() is True:
                #     QTimer.singleShot(50, lambda: self.parent.checkBox_FssUpdateStop1.setChecked(False))
                #     return None

                # if self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']):
                #     print('Fss 업데이트 완료')
                    # return None

                self.fssByNaverStartIndex += 1  ## 에러가 생겼을때 다음 단계 호출
                # self.FssByNaver()

        if self.fssByNaverStartIndex == len(self.stockTRDataFrame['shcode']):
            print('Fss 업데이트 완료')

        # QTimer.singleShot(50, lambda: self.parent.checkBox_FssUpdateStop1.setChecked(False))
        print('중지 check')
        self.parent.checkBox_FssUpdateStop1.setChecked(False)

        wholeTableFssDataFrame = selectWholeFfs().do()
        sorted_wholeTableFssDataFrame = wholeTableFssDataFrame.sort_values(by=['크롤링_시간'], axis=0)
        # wholeTableFssDataFrame = pd.DataFrame()
        # with sqlite3.connect('FssData.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
        #     cursor = conn.cursor()
        #     cursor.execute(
        #         "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1 ;")
        #     a = []
        #
        #     for i in cursor:
        #         stockTRDataFrame = pd.read_sql('SELECT * FROM "{}" '.format(i[0]), conn, index_col=None)
        #         wholeTableFssDataFrame = pd.concat([wholeTableFssDataFrame, stockTRDataFrame], axis=0, ignore_index=True)
        #
        #     wholeTableFssDataFrame.to_sql('Totalinfo', con=conn, if_exists='replace', index=False)
        #     sorted_wholeTableFssDataFrame = wholeTableFssDataFrame.sort_values(by=['크롤링_시간'], axis=0)



        a = sorted_wholeTableFssDataFrame['크롤링_시간'][len(sorted_wholeTableFssDataFrame['크롤링_시간']) - 1].split(' ')
        b = a[0].split('-')
        self.parent.FssUpdateLastDate[0] = ''.join(b)

        a = sorted_wholeTableFssDataFrame['크롤링_시간'][0].split(' ')
        b = a[0].split('-')
        self.parent.FssUpdateLastDate[1] = ''.join(b)

        time.sleep(5)
        self.stop()





