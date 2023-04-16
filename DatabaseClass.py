import sqlite3

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import pandas as pd
from pandas import Series, DataFrame

# https://blog.naver.com/edison0106/221797102417 중복데이터 넣지 않는 방법 : INSERT OR IGNORE -> 넣는 데이터가 PK일때 가능

class Database():

    """
    StockList
    """
        #종목리스트 insert
    def AddStockList(self, data):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        # data 형식 예시 - 이 순서로 저장 부탁드립니다 (shcode, hname, gubun, etfgubun)
        # data = (
        #     ('001100', '가상회사1', 2, 0),
        #     ('001200', '가상회사2', 2, 0),
        #     ('001300', '가상회사3', 2, 0)
        # )
        sql = "INSERT OR IGNORE INTO StockList(shcode, hname, gubun, etfgubun, recprice) values (?, ?, ?, ?, ?)"
        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    def AddStockListTotal(self, data):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "UPDATE StockList SET total = ? WHERE shcode = ?"
        cur.execute(sql, data)
        conn.commit()
        conn.close()


    # 종목리스트 delete
    def DeleteStockList(self, shcode):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM StockList WHERE shcode = ?"
        cur.executemany(sql, shcode)
        conn.commit()
        conn.close()

        # StockList 전체삭제
        # https://ybworld.tistory.com/22 UPDATE 코드 참고
    def DeleteStockListAll(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM StockList"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0")
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    # StockList 종목 불러오는 코드
    # StockList에서 시총 낮은애들 삭제할때 사용 예정
    def CallStockList(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT shcode FROM StockList"
        cur.execute(sql)

        StockList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return StockList

    # StockList 종목 불러오는 코드
    # StockList에서 시총 낮은애들 삭제할때 사용 예정
    def CallStockListLowTotal(self, totalprice):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        cur.execute("SELECT shcode FROM StockList WHERE total < %s" % totalprice)

        StockList = cur.fetchall()

        print(type(StockList))
        print('저가주식 리스트 : {}'.format(StockList))

        cur.close()
        conn.commit()
        conn.close()
        return StockList

    def StockListFilter(self, marketcap):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        # sql = "DELETE FROM StockList WHERE etfgubun <> 0 OR total < %s"
        # # etfgubun : 0-stock, 1-etf, 2-etn
        # cur.execute(sql, marketcap)
        cur.execute("DELETE FROM StockList WHERE etfgubun <> 0 OR total < %s" % marketcap)

        conn.commit()
        conn.close()

    """
    StockVolume
    """
    # 중복입력 문제있음, DeleteStockVolumeAll과 함께 사용 필요함
    # https://m.blog.naver.com/browniz1004/220987203139
    # https://www.sqlitetutorial.net/sqlite-python/insert/
    def AddStockVolume(self, data):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "INSERT INTO StockVolume(shcode, date, volume, close) values (?, ?, ?, ?)"
        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    # shcode 입력 -> date, volume, close 리턴
    def CallStockVolume(self, shcode):
        conn = sqlite3.connect("TradingDB.db")
        cur = conn.cursor()
        sql = "SELECT date, volume, close FROM StockVolume WHERE shcode = ?"
        cur.execute(sql, shcode)

        VolumeList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return VolumeList

    # 어제(전일) 거래량 호출
    def CallStockVolumeLastday(self, shcode):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1") # 원래없던건데 리스트로 불러와서 내가만듬
        cur = conn.cursor()
        sql = "SELECT volume, close FROM StockVolume WHERE shcode = (?) ORDER BY date desc limit 1"
        cur.execute(sql, shcode)
        # select volume from StockVolume where shcode = "000020" order by date desc limit 1
        LastDayVolume = cur.fetchall()
        LastDayVolume = LastDayVolume[0][0]

        cur.close()
        conn.commit()
        conn.close()
        return LastDayVolume

    # StockVolume - 거래량 정보를 삭제하는 코드, 거래량 정보를 받기전에 1회 실행 필요함
    def DeleteStockVolumeAll(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM StockVolume"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = '%s'" % ('StockVolume'))
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    ## R DB상의 shcode만 불러와서 어디까지 저장되었는지 확인하는데 사용
    def CallStockVolumeList(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT shcode FROM StockVolume"
        cur.execute(sql)

        stockVolumeList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return stockVolumeList

    """
    MinData
    """

    # MinData - 분봉 정보를 삭제하는 코드
    # ☆★☆★☆분봉 정보를 받기전에 반드시 1회 실행 필요함☆★☆★☆
    def DeleteMinDataAll(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "DELETE FROM MinData"
        cur.execute(sql)
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = '%s'" % ('MinData'))
        conn.commit()
        conn.execute("VACUUM")
        conn.close()

    # 3분봉 데이터를 받아 저장하는 SQL 쿼리
    def AddMinData(self, data):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 0")
        cur = conn.cursor()
        sql = "REPLACE INTO MinData(shcode, chetime, volume, close, diff) values (?, ?, ?, ?, ?)"
        cur.executemany(sql, data)
        conn.commit()
        conn.close()

    # 3분봉 데이터를 불러오는 쿼리
    def CallMinData(self, shcode):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT chetime, volume, close, diff FROM MinData WHERE shcode = (?) order by chetime ASC"
        cur.execute(sql, shcode)

        MinData = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return MinData

    # "SELECT chetime, volume, close, diff FROM MinData WHERE shcode = (?) order by chetime ASC"
    # "SELECT volume FROM StockVolume WHERE shcode = (?) ORDER BY date desc limit 1"


    """
    StockPick
    """

    # StockPick 종목 리스트에 shcode 하나 추가하는 코드
    def AddStockPick(self, shcode):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "INSERT OR IGNORE INTO StockPick (shcode) VALUES(?)"
        cur.executemany(sql, shcode)
        conn.commit()
        conn.close()

    # StockPick 종목을 튜플 - 리스트 형식으로 저장하는 코드
    def CallStockPick(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT shcode FROM StockPick"
        cur.execute(sql)

        PickList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        return PickList
    """
    1404, 1405 Warning
    """
    def Call1404WarnList(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT 종목코드 FROM '1404WarningList'"
        cur.execute(sql)

        PickList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        # print(PickList)
        return PickList

    def Call1405WarnList(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("PRAGMA foreign_keys = 1")
        cur = conn.cursor()
        sql = "SELECT 종목코드 FROM '1405WarningList'"
        cur.execute(sql)

        PickList = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()
        # print(PickList)
        return PickList

    """
    기타
    """

    # DB 용량확보 코드
    def Vaccum(self):
        conn = sqlite3.connect("TradingDB.db")
        conn.execute("VACUUM")
        conn.close()