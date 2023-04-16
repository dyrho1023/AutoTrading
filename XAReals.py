import sys
import os
import datetime
import time
import win32com.client
import pythoncom
import inspect
import pathlib

# import pandas as pd
# from pandas import DataFrame, Series


class XARealEvents(object):
    def __init__(self):
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def OnReceiveMessage(self, systemError, messageCode, message):
        if self.parent != None:
            self.parent.OnReceiveMessage(systemError, messageCode, message)

    def OnReceiveData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveData(szTrCode)

    def OnReceiveRealData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveRealData(szTrCode)

    def OnReceiveChartRealData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveChartRealData(szTrCode)

    def OnRecieveLinkData(self, szLinkName, szData, szFiller):
        if self.parent != None:
            self.parent.OnRecieveLinkData(szLinkName, szData, szFiller)


class XAReal(object):
    def __init__(self, parent=None, classification='classification'):
        self.parent = parent
        self.classification = classification

        self.ActiveX = win32com.client.DispatchWithEvents("XA_DataSet.XAReal", XARealEvents)
        self.ActiveX.set_parent(parent=self)

        userInfo = []
        path = pathlib.Path(__file__).parent.absolute().parent
        path = path.joinpath('User_Environment.txt')

        with open(path, encoding='utf8') as userFile:
            for line in userFile:
                userInfo.append(line.splitlines())
        userFile.close()

        self.RESDIR = "".join(userInfo[1])
        self.MYNAME = self.__class__.__name__
        self.INBLOCK = "InBlock"
        self.OUTBLOCK = "OutBlock"
        self.RESFILE = "%s\\Res\\%s.res" % (self.RESDIR, self.MYNAME)

    def OnReceiveMessage(self, systemError, messageCode, message):
        className = self.__class__.__name__
        functionName = inspect.currentframe().f_code.co_name
        print("%s-%s " % (className, functionName), systemError, messageCode, message)

    # 용도 미파악
    def AdviseLinkFromHTS(self):
        self.ActiveX.AdviseLinkFromHTS()

    # 용도 미파악
    def UnAdviseLinkFromHTS(self):
        self.ActiveX.UnAdviseLinkFromHTS()

    # 용도 미파악
    def OnRecieveLinkData(self, szLinkName, szData, szFiller):
        print(szLinkName, szData, szFiller)


class SC1(XAReal):
    """
    주식 주문 체결
    """
    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.ActiveX.LoadFromResFile(self.RESFILE)

    def AdviseRealData(self):
        self.ActiveX.AdviseRealData()

    def UnadviseRealData(self):
        self.ActiveX.UnadviseRealData()

    def OnReceiveRealData(self, szTrCode):
        result = []
        # '라인일련번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "lineseq")
        # '계좌번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "accno")
        # '조작자ID' = self.ActiveX.GetFieldData(self.OUTBLOCK, "user")
        # '헤더길이' = self.ActiveX.GetFieldData(self.OUTBLOCK, "len")
        # '헤더구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "gubun")
        # '압축구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "compress")
        # '암호구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "encrypt")
        # '공통시작지점' = self.ActiveX.GetFieldData(self.OUTBLOCK, "offset")
        # 'TRCODE' = self.ActiveX.GetFieldData(self.OUTBLOCK, "trcode")
        # '이용사번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "comid")
        # '사용자ID' = self.ActiveX.GetFieldData(self.OUTBLOCK, "userid")
        # '접속매체' = self.ActiveX.GetFieldData(self.OUTBLOCK, "media")
        # 'IF일련번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "ifid")
        # '전문일련번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "seq")
        # 'TR추적ID' = self.ActiveX.GetFieldData(self.OUTBLOCK, "trid")
        # '공인IP' = self.ActiveX.GetFieldData(self.OUTBLOCK, "pubip")
        # '사설IP' = self.ActiveX.GetFieldData(self.OUTBLOCK, "prvip")
        # '처리지점번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "pcbpno")
        # '지점번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "bpno")
        # '단말번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "termno")
        # '언어구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "lang")
        # 'AP처리시간' = self.ActiveX.GetFieldData(self.OUTBLOCK, "proctm")
        # '메세지코드' = self.ActiveX.GetFieldData(self.OUTBLOCK, "msgcode")
        # '메세지출력구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "outgu")
        # '압축요청구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "compreq")
        # '기능키' = self.ActiveX.GetFieldData(self.OUTBLOCK, "funckey")
        # '요청레코드개수' = self.ActiveX.GetFieldData(self.OUTBLOCK, "reqcnt")
        # '예비영역' = self.ActiveX.GetFieldData(self.OUTBLOCK, "filler")
        # '연속구분' = self.ActiveX.GetFieldData(self.OUTBLOCK, "cont")
        # '연속키값' = self.ActiveX.GetFieldData(self.OUTBLOCK, "contkey")
        # '가변시스템길이' = self.ActiveX.GetFieldData(self.OUTBLOCK, "varlen")
        # '가변해더길이' = self.ActiveX.GetFieldData(self.OUTBLOCK, "varhdlen")
        # '가변메시지길이' = self.ActiveX.GetFieldData(self.OUTBLOCK, "varmsglen")
        # '조회발원지' = self.ActiveX.GetFieldData(self.OUTBLOCK, "trsrc")
        # 'IF이벤트ID' = self.ActiveX.GetFieldData(self.OUTBLOCK, "eventid")
        # 'IF정보' = self.ActiveX.GetFieldData(self.OUTBLOCK, "ifinfo")
        # '예비영역' = self.ActiveX.GetFieldData(self.OUTBLOCK, "filler1")
        # '주문체결유형코드' = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordxctptncode")
        # '주문시장코드' = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordmktcode")
        # '주문유형코드' = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordptncode")
        # '관리지점번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "mgmtbrnno")
        # '계좌번호1' = self.ActiveX.GetFieldData(self.OUTBLOCK, "accno1")
        # '계좌번호2' = self.ActiveX.GetFieldData(self.OUTBLOCK, "accno2")
        # '계좌명' = self.ActiveX.GetFieldData(self.OUTBLOCK, "acntnm")
        # '종목번호' = self.ActiveX.GetFieldData(self.OUTBLOCK, "Isuno")
        종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "Isunm")
        주문번호 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordno")
        # result['원주문번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "orgordno")
        체결번호 = self.ActiveX.GetFieldData(self.OUTBLOCK, "execno")
        주문수량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordqty")
        주문가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordprc")
        체결수량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "execqty")
        체결가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "execprc")
        # result['정정확인수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mdfycnfqty")
        # result['정정확인가격'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mdfycnfprc")
        # result['취소확인수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "canccnfqty")
        # result['거부수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "rjtqty")
        # result['주문처리유형코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordtrxptncode")
        # result['복수주문일련번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mtiordseqno")
        # result['주문조건'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordcndi")
        # result['호가유형코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordprcptncode")
        # result['비저축체결수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "nsavtrdqty")
        단축종목번호 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shtnIsuno")
        # result['운용지시번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "opdrtnno")
        # result['반대매매주문구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "cvrgordtp")
        # result['미체결수량_주문'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "unercqty")
        # result['원주문미체결수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "orgordunercqty")
        # result['원주문정정수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "orgordmdfyqty")
        # result['원주문취소수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "orgordcancqty")
        주문평균체결가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordavrexecprc")
        # result['주문금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordamt")
        # result['표준종목번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "stdIsuno")
        # result['전표준종목번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfstdIsuno")
        매매구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bnstp")
        # result['주문거래유형코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordtrdptncode")
        # result['신용거래코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mgntrncode")
        # result['수수료합산코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "adduptp")
        # result['통신매체코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "commdacode")
        # result['대출일'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "Loandt")
        # result['회원_비회원사번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mbrnmbrno")
        주문계좌번호 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordacntno")
        # result['집계지점번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "agrgbrnno")
        # result['관리사원번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mgempno")
        # result['선물연계지점번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "futsLnkbrnno")
        # result['선물연계계좌번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "futsLnkacntno")
        # result['선물시장구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "futsmkttp")
        # result['등록시장코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "regmktcode")
        # result['현금증거금률'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mnymgnrat")
        # result['대용증거금률'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "substmgnrat")
        # result['현금체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "mnyexecamt")
        # result['대용체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ubstexecamt")
        # result['수수료체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "cmsnamtexecamt")
        # result['신용담보체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "crdtpldgexecamt")
        # result['신용체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "crdtexecamt")
        # result['전일재사용체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "prdayruseexecval")
        # result['금일재사용체결금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "crdayruseexecval")
        # result['실물체결수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "spotexecqty")
        # result['공매도체결수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "stslexecqty")
        # result['전략코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "strtgcode")
        # result['그룹Id'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "grpId")
        # result['주문회차'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordseqno")
        # result['포트폴리오번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ptflno")
        # result['바스켓번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bskno")
        # result['트렌치번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "trchno")
        # result['아이템번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "itemno")
        # result['주문자ID'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "orduserId")
        # result['차입관리여부'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "brwmgmtYn")
        # result['외국인고유번호'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "frgrunqno")
        # result['거래세징수구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "trtzxLevytp")
        # result['유동성공급자구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "lptp")
        체결시각 = self.ActiveX.GetFieldData(self.OUTBLOCK, "exectime")
        # result['거래소수신체결시각'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "rcptexectime")
        # result['잔여대출금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "rmndLoanamt")
        # result['잔고수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "secbalqty")
        # result['실물가능수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "spotordableqty")
        # result['재사용가능수량_매도'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordableruseqty")
        # result['변동수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "flctqty")
        # result['잔고수량_D2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "secbalqtyd2")
        # result['매도주문가능수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sellableqty")
        # result['미체결매도주문수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "unercsellordqty")
        # result['평균매입가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "avrpchsprc")
        # result['매입금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "pchsant")
        # result['예수금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "deposit")
        # result['대용금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "substamt")
        # result['위탁증거금현금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "csgnmnymgn")
        # result['위탁증거금대용'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "csgnsubstmgn")
        # result['신용담보재사용금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "crdtpldgruseamt")
        # result['주문가능현금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordablemny")
        # result['주문가능대용'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordablesubstamt")
        # result['재사용가능금액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ruseableamt")

        if(self.parent.mainCall == True):
            self.parent.QtableWidgetShowing(분류='체결', 주문번호=주문번호, 종목명=종목명, 매매구분=매매구분, 수량=체결수량,
                                        체결가격=체결가격, 시각=체결시각, 체결번호=체결번호)
        else:
            self.parent.parent.QtableWidgetShowing(분류='체결', 주문번호=주문번호, 종목명=종목명, 매매구분=매매구분, 수량=체결수량,
                                            체결가격=체결가격, 시각=체결시각, 체결번호=체결번호)
            outblockList = [체결가격]
            result.append(outblockList)

            self.parent.resultSC1 = result
            self.parent.flagSC1 = 1
