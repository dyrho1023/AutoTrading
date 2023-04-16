import win32com.client
import inspect
import datetime
# from pandas import DataFrame, Series
import pathlib
from DatabaseClass import *


class XAQueryEvents(object):
    """
    XAQuery를 호출하기 전에, File 구조를 정리하는 부분
    parent로 호칭되는 상위 호출자가 존재하는 경우,
    XING API Server로부터 수신한 데이터를 처리하는 부분
    """

    def __init__(self):
        self.parent = None

    def SetParent(self, parent):
        self.parent = parent

    def OnReceiveMessage(self, system_error, message_code, message):
        if self.parent is not None:
            self.parent.OnReceiveMessage(system_error, message_code, message)

    def OnReceiveData(self, szTrCode):
        if self.parent is not None:
            self.parent.OnReceiveData(szTrCode)

    def OnReceiveChartRealData(self, szTrCode):
        if self.parent is not None:
            self.parent.OnReceiveChartRealData(szTrCode)

    def OnReceiveSearchRealData(self, szTrCode):
        if self.parent is not None:
            self.parent.OnReceiveSearchRealData(szTrCode)


class XAQuery(object):
    """
    XAQuery 형태의 API를 사용하기 위한 구조체 선언
    """

    def __init__(self, parent=None, classification='classification'):
        self.parent = parent
        self.classification = classification

        self.ActiveX = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
        self.ActiveX.SetParent(parent=self)

        userInfo = []
        path = pathlib.Path(__file__).parent.absolute().parent
        path = path.joinpath('User_Environment.txt')
        with open(path, encoding='utf8') as userFile:
            for line in userFile:
                userInfo.append(line.splitlines())
        userFile.close()

        self.RESDIR = "".join(userInfo[1])
        self.MYNAME = self.__class__.__name__
        self.INBLOCK = "%sInBlock" % self.MYNAME
        self.INBLOCK1 = "%sInBlock1" % self.MYNAME
        self.OUTBLOCK = "%sOutBlock" % self.MYNAME
        self.OUTBLOCK1 = "%sOutBlock1" % self.MYNAME
        self.OUTBLOCK2 = "%sOutBlock2" % self.MYNAME
        self.OUTBLOCK3 = "%sOutBlock3" % self.MYNAME
        self.RESFILE = "%s\\Res\\%s.res" % (self.RESDIR, self.MYNAME)

    # int type 으로 casting 해주고, 숫자가 아닌 경우 '0' 값으로 바꿔주는 부분
    def toint(self, s):
        temp = s.strip()
        result = 0

        if temp not in ['-']:
            result = int(temp)
        else:
            result = 0

        return result

    # float type으로 casting 해주고, 숫자가 아닌 경우 '0' 값으로 바꿔주는 부분
    def tofloat(self, s):
        temp = s.strip()
        result = 0

        if temp not in ['-']:
            result = float(temp)
        else:
            result = 0.0

        return result

    # 용도 미파악
    def OnReceiveMessage(self, system_error, message_code, message):
        if self.parent is not None:
            self.parent.OnReceiveMessage(system_error, message_code, message)

    # 용도 미파악
    def OnReceiveData(self, szTrCode):
        pass

    # 용도 미파악
    def OnReceiveChartRealData(self, szTrCode):
        pass

    # 용도 미파악
    def RequestLinkToHTS(self, szLinkName, szData, szFiller):
        return self.ActiveX.RequestLinkToHTS(szLinkName, szData, szFiller)


""" =RDY=========================================================================================================== """


class t8430(XAQuery):
    """
    주식종목코드조회
    """

    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.dataControl = Database()

    def Query(self, 구분='0'):
        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)

        err_code = self.ActiveX.Request(False)  # 연속조회가 아닌 경우 False로 Request 요청

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            단축코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip()
            # 확장코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "expcode", i).strip()
            ETF구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "etfgubun", i).strip())
            # 상한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "uplmtprice", i).strip())
            # 하한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "dnlmtprice", i).strip())
            # 전일가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "jnilclose", i).strip())
            # 주문수량단위 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "memedan", i).strip())
            기준가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "recprice", i).strip())
            구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "gubun", i).strip())

            outblockList = [단축코드, 종목명, 구분, ETF구분, 기준가]
            result.append(outblockList)

        ## 하나의 tr이 종료되면 수행해야 하는 코드
        self.dataControl.AddStockList(result)
        self.parent.companyNumber = len(result)

        ## Main UI에 표기
        self.parent.lastListUpdateTime = datetime.datetime.today().strftime("%Y-%m-%d")
        self.parent.label_ListUpdate.setText(" 마지막 업데이트 날짜 : " + self.parent.lastListUpdateTime)
        self.parent.statusBar.showMessage("상장된 국내 회사의 정보가 업데이트 되었습니다.")
        self.parent.label_VolumeUpdate2.setText(" 업데이트 된 기업 수 / 총 기업 : " + str(self.parent.lastVolumeUpdateNumber)
                                                + "/" + str(self.parent.companyNumber))


class t1305(XAQuery):
    """
    기간별주가
    """
    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.dataControl = Database()
        self.건수 = None

    def Query(self, 단축코드='', 일주월구분='1', 날짜='', IDX='', 건수='', 연속조회=False):
        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 단축코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "dwmcode", 0, 일주월구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "date", 0, 날짜)
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)
            self.ActiveX.SetFieldData(self.INBLOCK, "cnt", 0, 건수)

            err_code = self.ActiveX.Request(False)  # 연속조회가 아닌 경우 False로 Request 요청

        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "date", 0, 날짜)
            self.ActiveX.SetFieldData(self.INBLOCK, "cnt", 0, 건수)

            err_code = self.ActiveX.Request(True)  # 연속조회인 경우 True로 Request 요청

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))

        self.건수 = 건수  # 이전에 입력된 건수가 얼만큼 남았는지 Check 하기 위함

    def OnReceiveData(self, szTrCode):
        Out날짜 = None
        Out건수 = None
        종목코드 = None

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            Out건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "cnt", i).strip())
            Out날짜 = self.ActiveX.GetFieldData(self.OUTBLOCK, "date", i).strip()

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            날짜 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            # 시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            # 고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            # 저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            # 전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            # 전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            # 등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            # 거래증가율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff_vol", i).strip())
            # 체결강도 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "chdegree", i).strip())
            # 소진율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "sojinrate", i).strip())
            # 회전율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "changerate", i).strip())
            # 외인순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "fpvolume", i).strip())
            # 기관순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "covolume", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            # 누적거래대금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i).strip())
            # 개인순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "ppvolume", i).strip())
            # 시가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_sign", i).strip()
            # 시가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_change", i).strip())
            # 시가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_diff", i).strip())
            # 고가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_sign", i).strip()
            # 고가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_change", i).strip())
            # 고가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_diff", i).strip())
            # 저가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_sign", i).strip()
            # 저가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_change", i).strip())
            # 저가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_diff", i).strip())
            # 시가총액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "marketcap", i).strip())

            outblockList = [종목코드, 날짜, 누적거래량, 종가]
            result.append(outblockList)

        ## 하나의 tr이 종료되면 수행해야 하는 코드

        if len(Out날짜) > 0:  # 거래량 데이터가 80개 이상 있는 경우 여기의 값이 1 이상
            self.dataControl.AddStockVolume(result)
            self.parent.VolumeUpdateFunction2([종목코드, Out날짜, Out건수, self.건수])
        else:                 # 거래량 데이터가 80개가 안되는 경우 여기의 값이 0
            Out날짜 = 0
            Out건수 = self.건수  # 다음 종목 조회를 하도록 Re건수 조절 (값이 틀어지므로, 보정)
            self.parent.VolumeUpdateFunction2([종목코드, Out날짜, Out건수, self.건수])

        ## Main UI에 표기


class CSPAT00600(XAQuery):
    """
    현물정상주문
    """
    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.주문결과코드 = ''
        self.주문결과메세지 = ''
        self.주문수량 = ''
        self.매매구분 = ''
        self.종목명 = ''
        self.주문시각 = ''
        self.주문번호 = ''
        self.주문금액 = ''

        # 호가유형코드 : 00 - 지정가, 03 - 시장가, 우린 시장가로 단숨에 체결하는 방법으로 간다
    def Query(self, 계좌번호='', 입력비밀번호='', 종목번호='', 주문수량='', 주문가='', 매매구분='2', 호가유형코드='03',
              신용거래코드='000', 대출일='', 주문조건구분='0'):

        print(계좌번호, 입력비밀번호, 종목번호, 주문수량, 주문가, 매매구분, 호가유형코드,
              신용거래코드, 대출일, 주문조건구분)
        if 호가유형코드 == '03':
            주문가 = ''

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK1, "AcntNo", 0, 계좌번호)
        self.ActiveX.SetFieldData(self.INBLOCK1, "InptPwd", 0, 입력비밀번호)
        self.ActiveX.SetFieldData(self.INBLOCK1, "IsuNo", 0, 종목번호)
        self.ActiveX.SetFieldData(self.INBLOCK1, "OrdQty", 0, 주문수량)
        self.ActiveX.SetFieldData(self.INBLOCK1, "OrdPrc", 0, 주문가)
        self.ActiveX.SetFieldData(self.INBLOCK1, "BnsTpCode", 0, 매매구분)
        self.ActiveX.SetFieldData(self.INBLOCK1, "OrdprcPtnCode", 0, 호가유형코드)
        self.ActiveX.SetFieldData(self.INBLOCK1, "MgntrnCode", 0, 신용거래코드)
        self.ActiveX.SetFieldData(self.INBLOCK1, "LoanDt", 0, 대출일)
        self.ActiveX.SetFieldData(self.INBLOCK1, "OrdCndiTpCode", 0, 주문조건구분)

        err_code = self.ActiveX.Request(False)  # 연속조회가 아닌 경우 False로 Request 요청

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            레코드갯수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "RecCnt", i).strip())
            계좌번호 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "AcntNo", i).strip()
            입력비밀번호 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "InptPwd", i).strip()
            종목번호 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "IsuNo", i).strip()
            주문수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "OrdQty", i).strip())
            주문가 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "OrdPrc", i).strip()
            매매구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "BnsTpCode", i).strip()
            호가유형코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "OrdprcPtnCode", i).strip()
            프로그램호가유형코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "PrgmOrdprcPtnCode", i).strip()
            공매도가능여부 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "StslAbleYn", i).strip()
            공매도호가구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "StslOrdprcTpCode", i).strip()
            통신매체코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "CommdaCode", i).strip()
            신용거래코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "MgntrnCode", i).strip()
            대출일 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "LoanDt", i).strip()
            회원번호 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "MbrNo", i).strip()
            주문조건구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "OrdCndiTpCode", i).strip()
            전략코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "StrtgCode", i).strip()
            그룹ID = self.ActiveX.GetFieldData(self.OUTBLOCK1, "GrpId", i).strip()
            주문회차 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "OrdSeqNo", i).strip())
            포트폴리오번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "PtflNo", i).strip())
            바스켓번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "BskNo", i).strip())
            트렌치번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "TrchNo", i).strip())
            아이템번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "ItemNo", i).strip())
            운용지시번호 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "OpDrtnNo", i).strip()
            유동성공급자여부 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "LpYn", i).strip()
            반대매매구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "CvrgTpCode", i).strip()

            outblockList = [레코드갯수, 계좌번호, 입력비밀번호, 종목번호, 주문수량, 주문가, 매매구분, 호가유형코드, 프로그램호가유형코드, 공매도가능여부, 공매도호가구분, 통신매체코드,
                            신용거래코드,
                            대출일, 회원번호, 주문조건구분, 전략코드, 그룹ID, 주문회차, 포트폴리오번호, 바스켓번호, 트렌치번호, 아이템번호, 운용지시번호, 유동성공급자여부, 반대매매구분]
            result.append(outblockList)

            self.주문수량 = str(주문수량)
            self.매매구분 = str(매매구분)

        result1 = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK2)
        for i in range(nCount):
            레코드갯수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "RecCnt", i).strip())
            주문번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "OrdNo", i).strip())
            주문시각 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "OrdTime", i).strip()
            주문시장코드 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "OrdMktCode", i).strip()
            주문유형코드 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "OrdPtnCode", i).strip()
            단축종목번호 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "ShtnIsuNo", i).strip()
            관리사원번호 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "MgempNo", i).strip()
            주문금액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "OrdAmt", i).strip())
            예비주문번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "SpareOrdNo", i).strip())
            반대매매일련번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "CvrgSeqno", i).strip())
            예약주문번호 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "RsvOrdNo", i).strip())
            실물주문수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "SpotOrdQty", i).strip())
            재사용주문수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "RuseOrdQty", i).strip())
            현금주문금액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "MnyOrdAmt", i).strip())
            대용주문금액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "SubstOrdAmt", i).strip())
            재사용주문금액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK2, "RuseOrdAmt", i).strip())
            계좌명 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "AcntNm", i).strip()
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK2, "IsuNm", i).strip()

            outblockList = [레코드갯수, 주문번호, 주문시각, 주문시장코드, 주문유형코드, 단축종목번호, 관리사원번호, 주문금액, 예비주문번호, 반대매매일련번호, 예약주문번호, 실물주문수량,
                            재사용주문수량,
                            현금주문금액, 대용주문금액, 재사용주문금액, 계좌명, 종목명]
            result1.append(outblockList)

            self.종목명 = str(종목명)
            self.주문시각 = str(주문시각)
            self.주문번호 = str(주문번호)
            self.주문금액 = str(주문금액)

        if(self.parent.mainCall == True):
            self.parent.QtableWidgetShowing(분류='주문', 주문번호=self.주문번호, 종목명=self.종목명, 매매구분=self.매매구분,
                                        수량=self.주문수량, 체결가격=self.주문금액, 시각=self.주문시각, 체결번호='-')
        else:
            self.parent.parent.QtableWidgetShowing(분류='주문', 주문번호=self.주문번호, 종목명=self.종목명, 매매구분=self.매매구분,
                                            수량=self.주문수량, 체결가격=self.주문금액, 시각=self.주문시각, 체결번호='-')


class t1302(XAQuery):
    """
    주식분별주가조회
    """

    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.dataControl = Database()

    def Query(self, 단축코드='', 작업구분='', 시간='', 건수='', 연속조회=False):
        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 단축코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 작업구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "time", 0, 시간)
            self.ActiveX.SetFieldData(self.INBLOCK, "cnt", 0, 건수)

            err_code = self.ActiveX.Request(False)  # 연속조회가 아닌 경우 False로 Request 요청
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "cts_time", 0, 시간)

            err_code = self.ActiveX.Request(True)  # 연속조회인 경우 True로 Request 요청

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            시간CTS = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_time", i).strip()

        result = []
        result_update = []

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            시간 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "chetime", i).strip()
            종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            체결강도 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "chdegree", i).strip())
            매도체결수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdvolume", i).strip())
            매수체결수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "msvolume", i).strip())
            순매수체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "revolume", i).strip())
            매도체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdchecnt", i).strip())
            매수체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mschecnt", i).strip())
            순체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "rechecnt", i).strip())
            거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "cvolume", i).strip())
            매도체결건수시간 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdchecnttm", i).strip())
            매수체결건수시간 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mschecnttm", i).strip())
            매도잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "totofferrem", i).strip())
            매수잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "totbidrem", i).strip())
            시간별매도체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdvolumetm", i).strip())
            시간별매수체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "msvolumetm", i).strip())

            outblockList = [시간, 종가, 전일대비구분, 전일대비, 등락율, 체결강도, 매도체결수량, 매수체결수량, 순매수체결량, 매도체결건수, 매수체결건수, 순체결건수, 거래량, 시가, 고가,
                            저가, 체결량,
                            매도체결건수시간, 매수체결건수시간, 매도잔량, 매수잔량, 시간별매도체결량, 시간별매수체결량]
            # 내 편의상 하나 추가 => 이래도 될지???
            outblockList_update = [시간, 거래량, 종가, 등락율]
            result.append(outblockList)
            result_update.append(outblockList_update)
            # shcode, chetime, close, diff =

        ## 하나의 tr이 종료되면 수행해야 하는 코드
        self.parent.resultt1302 = result
        self.parent.resultt1302_update = result_update
        self.parent.flagt1302 = 1
        ## Main UI에 표기

        # 작동확인
        # print("print(result)")
        # print(result)
        # print("print(self.parent.resultt1302)")
        # print(self.parent.resultt1302)
        # print("print(self.parent.resultt1302_update)")
        # print(self.parent.resultt1302_update)

class t1101(XAQuery):
    """
    주식 현재가 호가 조회
    """

    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.현재가격 = 0
        self.종목명 = []

    def Query(self, 단축코드=None):
        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 단축코드)

        err_code = self.ActiveX.Request(False)  # 연속조회가 아닌 경우 False로 Request 요청

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            현재가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "price", i).strip()
            # 전일대비구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "sign", i).strip())
            # 전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "change", i).strip())
            # 등락율 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "diff", i).strip())
            # 누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "volume", i).strip())
            # 전일종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "jnilclose", i).strip())
            # 매도호가1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho1", i).strip())
            # 매수호가1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho1", i).strip())
            # 매도호가수량1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem1", i).strip())
            # 매수호가수량1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem1", i).strip())
            # 직전매도대비수량1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha1", i).strip())
            # 직전매수대비수량1 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha1", i).strip())
            # 매도호가2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho2", i).strip())
            # 매수호가2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho2", i).strip())
            # 매도호가수량2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem2", i).strip())
            # 매수호가수량2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem2", i).strip())
            # 직전매도대비수량2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha2", i).strip())
            # 직전매수대비수량2 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha2", i).strip())
            # 매도호가3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho3", i).strip())
            # 매수호가3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho3", i).strip())
            # 매도호가수량3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem3", i).strip())
            # 매수호가수량3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem3", i).strip())
            # 직전매도대비수량3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha3", i).strip())
            # 직전매수대비수량3 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha3", i).strip())
            # 매도호가4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho4", i).strip())
            # 매수호가4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho4", i).strip())
            # 매도호가수량4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem4", i).strip())
            # 매수호가수량4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem4", i).strip())
            # 직전매도대비수량4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha4", i).strip())
            # 직전매수대비수량4 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha4", i).strip())
            # 매도호가5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho5", i).strip())
            # 매수호가5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho5", i).strip())
            # 매도호가수량5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem5", i).strip())
            # 매수호가수량5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem5", i).strip())
            # 직전매도대비수량5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha5", i).strip())
            # 직전매수대비수량5 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha5", i).strip())
            # 매도호가6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho6", i).strip())
            # 매수호가6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho6", i).strip())
            # 매도호가수량6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem6", i).strip())
            # 매수호가수량6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem6", i).strip())
            # 직전매도대비수량6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha6", i).strip())
            # 직전매수대비수량6 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha6", i).strip())
            # 매도호가7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho7", i).strip())
            # 매수호가7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho7", i).strip())
            # 매도호가수량7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem7", i).strip())
            # 매수호가수량7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem7", i).strip())
            # 직전매도대비수량7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha7", i).strip())
            # 직전매수대비수량7 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha7", i).strip())
            # 매도호가8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho8", i).strip())
            # 매수호가8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho8", i).strip())
            # 매도호가수량8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem8", i).strip())
            # 매수호가수량8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem8", i).strip())
            # 직전매도대비수량8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha8", i).strip())
            # 직전매수대비수량8 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha8", i).strip())
            # 매도호가9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho9", i).strip())
            # 매수호가9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho9", i).strip())
            # 매도호가수량9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem9", i).strip())
            # 매수호가수량9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem9", i).strip())
            # 직전매도대비수량9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha9", i).strip())
            # 직전매수대비수량9 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha9", i).strip())
            # 매도호가10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerho10", i).strip())
            # 매수호가10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidho10", i).strip())
            # 매도호가수량10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offerrem10", i).strip())
            # 매수호가수량10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bidrem10", i).strip())
            # 직전매도대비수량10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha10", i).strip())
            # 직전매수대비수량10 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha10", i).strip())
            # 매도호가수량합 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "offer", i).strip())
            # 매수호가수량합 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "bid", i).strip())
            # 직전매도대비수량합 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "preoffercha", i).strip())
            # 직전매수대비수량합 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "prebidcha", i).strip())
            # 수신시간 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "hotime", i).strip())
            # 예상체결가격 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "yeprice", i).strip())
            # 예상체결수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "yevolume", i).strip())
            # 예상체결전일구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "yesign", i).strip())
            # 예상체결전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "yechange", i).strip())
            # 예상체결등락율 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "yediff", i).strip())
            # 시간외매도잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tmoffer", i).strip())
            # 시간외매수잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tmbid", i).strip())
            # 동시구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "ho_status", i).strip())
            # 단축코드 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip())
            # 상한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "uplmtprice", i).strip())
            # 하한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "dnlmtprice", i).strip())
            # 시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "open", i).strip())
            # 고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "high", i).strip())
            # 저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "low", i).strip())

            # outblockList = [종목명, 현재가, 전일대비구분, 전일대비, 등락율, 누적거래량, 전일종가, 매도호가1, 매수호가1, 매도호가수량1,
            #                 매수호가수량1, 직전매도대비수량1, 직전매수대비수량1, 매도호가2, 매수호가2, 매도호가수량2, 매수호가수량2,
            #                 직전매도대비수량2, 직전매수대비수량2, 매도호가3, 매수호가3, 매도호가수량3, 매수호가수량3, 직전매도대비수량3,
            #                 직전매수대비수량3, 매도호가4, 매수호가4, 매도호가수량4, 매수호가수량4, 직전매도대비수량4, 직전매수대비수량4,
            #                 매도호가5, 매수호가5, 매도호가수량5, 매수호가수량5, 직전매도대비수량5, 직전매수대비수량5, 매도호가6,
            #                 매수호가6, 매도호가수량6, 매수호가수량6, 직전매도대비수량6, 직전매수대비수량6, 매도호가7, 매수호가7,
            #                 매도호가수량7, 매수호가수량7, 직전매도대비수량7, 직전매수대비수량7, 매도호가8, 매수호가8, 매도호가수량8,
            #                 매수호가수량8, 직전매도대비수량8, 직전매수대비수량8, 매도호가9, 매수호가9, 매도호가수량9, 매수호가수량9,
            #                 직전매도대비수량9, 직전매수대비수량9, 매도호가10, 매수호가10, 매도호가수량10, 매수호가수량10,
            #                 직전매도대비수량10, 직전매수대비수량10, 매도호가수량합, 매수호가수량합, 직전매도대비수량합,
            #                 직전매수대비수량합, 수신시간, 예상체결가격, 예상체결수량, 예상체결전일구분, 예상체결전일대비, 예상체결등락율,
            #                 시간외매도잔량, 시간외매수잔량, 동시구분, 단축코드, 상한가, 하한가, 시가, 고가, 저가]
            outblockList = [종목명, 현재가격]
            result.append(outblockList)

        ## 하나의 tr이 종료되면 수행해야 하는 코드
        self.parent.result1101 = result
        self.parent.flagt1101 = 1

        ## Main UI에 표기


""" =PKB=========================================================================================================== """


class t1102(XAQuery):
    """
    주식현재가(시세)조회
    """
    def Query(self, 종목코드):
        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
        self.ActiveX.Request(0)

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)

        for i in range(nCount):
            한글명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            현재가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "price", i).strip()
            # 전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sign", i).strip()
            # 전일대비 = self.ActiveX.GetFieldData(self.OUTBLOCK, "change", i).strip()
            # 등락율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "diff", i).strip()
            # 누적거래량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "volume", i).strip()
            # 기준가_평가가격= self.ActiveX.GetFieldData(self.OUTBLOCK, "recprice", i).strip()
            # 가중평균 = self.ActiveX.GetFieldData(self.OUTBLOCK, "avg", i).strip()
            # 상한가_최고호가가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "uplmtprice", i).strip()
            # 하한가_최저호가가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dnlmtprice", i).strip()
            # 전일거래량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "jnilvolume", i).strip()
            # 거래량차 = self.ActiveX.GetFieldData(self.OUTBLOCK, "volumediff", i).strip()
            # 시가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "open", i).strip()
            # 시가시간 = self.ActiveX.GetFieldData(self.OUTBLOCK, "opentime", i).strip()
            # 고가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "high", i).strip()
            # 고가시간 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hightime", i).strip()
            # 저가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "low", i).strip()
            # 저가시간 = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowtime", i).strip()
            # 최고가_52 = self.ActiveX.GetFieldData(self.OUTBLOCK, "high52w", i).strip()
            # 최고가일_52 = self.ActiveX.GetFieldData(self.OUTBLOCK, "high52wdate", i).strip()
            # 최저가_52 = self.ActiveX.GetFieldData(self.OUTBLOCK, "low52w", i).strip()
            # 최저가일_52 = self.ActiveX.GetFieldData(self.OUTBLOCK, "low52wdate", i).strip()
            # 소진율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "exhratio", i).strip()
            # PER = self.ActiveX.GetFieldData(self.OUTBLOCK, "per", i).strip()
            # PBRX = self.ActiveX.GetFieldData(self.OUTBLOCK, "pbrx", i).strip()
            # 상장주식수_천 = self.ActiveX.GetFieldData(self.OUTBLOCK, "listing", i).strip()
            # 증거금율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "jkrate", i).strip()
            # 수량단위 = self.ActiveX.GetFieldData(self.OUTBLOCK, "memedan", i).strip()
            # 매도증권사코드1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd1", i).strip()
            # 매수증권사코드1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd1", i).strip()
            # 매도증권사명1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno1", i).strip()
            # 매수증권사명1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno1", i).strip()
            # 총매도수량1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol1", i).strip()
            # 총매수수량1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol1", i).strip()
            # 매도증감1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha1", i).strip()
            # 매수증감1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha1", i).strip()
            # 매도비율1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff1", i).strip()
            # 매수비율1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff1", i).strip()
            # 매도증권사코드2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd2", i).strip()
            # 매수증권사코드2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd2", i).strip()
            # 매도증권사명2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno2", i).strip()
            # 매수증권사명2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno2", i).strip()
            # 총매도수량2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol2", i).strip()
            # 총매수수량2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol2", i).strip()
            # 매도증감2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha2", i).strip()
            # 매수증감2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha2", i).strip()
            # 매도비율2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff2", i).strip()
            # 매수비율2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff2", i).strip()
            # 매도증권사코드3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd3", i).strip()
            # 매수증권사코드3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd3", i).strip()
            # 매도증권사명3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno3", i).strip()
            # 매수증권사명3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno3", i).strip()
            # 총매도수량3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol3", i).strip()
            # 총매수수량3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol3", i).strip()
            # 매도증감3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha3", i).strip()
            # 매수증감3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha3", i).strip()
            # 매도비율3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff3", i).strip()
            # 매수비율3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff3", i).strip()
            # 매도증권사코드4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd4", i).strip()
            # 매수증권사코드4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd4", i).strip()
            # 매도증권사명4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno4", i).strip()
            # 매수증권사명4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno4", i).strip()
            # 총매도수량4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol4", i).strip()
            # 총매수수량4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol4", i).strip()
            # 매도증감4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha4", i).strip()
            # 매수증감4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha4", i).strip()
            # 매도비율4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff4", i).strip()
            # 매수비율4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff4", i).strip()
            # 매도증권사코드5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd5", i).strip()
            # 매수증권사코드5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd5", i).strip()
            # 매도증권사명5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno5", i).strip()
            # 매수증권사명5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno5", i).strip()
            # 총매도수량5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol5", i).strip()
            # 총매수수량5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol5", i).strip()
            # 매도증감5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha5", i).strip()
            # 매수증감5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha5", i).strip()
            # 매도비율5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff5", i).strip()
            # 매수비율5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff5", i).strip()
            # 외국계매도합계수량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "fwdvl", i).strip()
            # 외국계매도직전대비 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdcha", i).strip()
            # 외국계매도비율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmddiff", i).strip()
            # 외국계매수합계수량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "fwsvl", i).strip()
            # 외국계매수직전대비 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmscha", i).strip()
            # 외국계매수비율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsdiff", i).strip()
            # 회전율 = self.ActiveX.GetFieldData(self.OUTBLOCK, "vol", i).strip()
            단축코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip()
            # 누적거래대금 = self.ActiveX.GetFieldData(self.OUTBLOCK, "value", i).strip()
            # 전일동시간거래량 = self.ActiveX.GetFieldData(self.OUTBLOCK, "jvolume", i).strip()
            # 연중최고가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "highyear", i).strip()
            # 연중최고일자 = self.ActiveX.GetFieldData(self.OUTBLOCK, "highyeardate", i).strip()
            # 연중최저가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowyear", i).strip()
            # 연중최저일자 = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowyeardate", i).strip()
            # 목표가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "target", i).strip()
            # 자본금 = self.ActiveX.GetFieldData(self.OUTBLOCK, "capital", i).strip()
            # 유동주식수 = self.ActiveX.GetFieldData(self.OUTBLOCK, "abscnt", i).strip()
            # 액면가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "parprice", i).strip()
            # 결산월 = self.ActiveX.GetFieldData(self.OUTBLOCK, "gsmm", i).strip()
            # 대용가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "subprice", i).strip()
            시가총액 = self.ActiveX.GetFieldData(self.OUTBLOCK, "total", i).strip()
            # 상장일 = self.ActiveX.GetFieldData(self.OUTBLOCK, "listdate", i).strip()
            # 전분기명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "name", i).strip()
            # 전분기매출액 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfsales", i).strip()
            # 전분기영업이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfoperatingincome", i).strip()
            # 전분기경상이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfordinaryincome", i).strip()
            # 전분기순이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfnetincome", i).strip()
            # 전분기EPS = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfeps", i).strip()
            # 전전분기명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "name2", i).strip()
            # 전전분기매출액 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfsales2", i).strip()
            # 전전분기영업이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfoperatingincome2", i).strip()
            # 전전분기경상이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfordinaryincome2", i).strip()
            # 전전분기순이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfnetincome2", i).strip()
            # 전전분기EPS = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfeps2", i).strip()
            # 전년대비매출액 = self.ActiveX.GetFieldData(self.OUTBLOCK, "salert", i).strip()
            # 전년대비영업이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "opert", i).strip()
            # 전년대비경상이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordrt", i).strip()
            # 전년대비순이익 = self.ActiveX.GetFieldData(self.OUTBLOCK, "netrt", i).strip()
            # 전년대비EPS = self.ActiveX.GetFieldData(self.OUTBLOCK, "epsrt", i).strip()
            # 락구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "info1", i).strip()
            # 관리_급등구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "info2", i).strip()
            # 정지_연장구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "info3", i).strip()
            # 투자_불성실구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "info4", i).strip()
            # 장구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "janginfo", i).strip()
            # TPER = self.ActiveX.GetFieldData(self.OUTBLOCK, "t_per", i).strip()
            # 통화ISO코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "tonghwa", i).strip()
            # 총매도대금1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval1", i).strip()
            # 총매수대금1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval1", i).strip()
            # 총매도대금2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval2", i).strip()
            # 총매수대금2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval2", i).strip()
            # 총매도대금3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval3", i).strip()
            # 총매수대금3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval3", i).strip()
            # 총매도대금4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval4", i).strip()
            # 총매수대금4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval4", i).strip()
            # 총매도대금5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval5", i).strip()
            # 총매수대금5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval5", i).strip()
            # 총매도평단가1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg1", i).strip()
            # 총매수평단가1 = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg1", i).strip()
            # 총매도평단가2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg2", i).strip()
            # 총매수평단가2 = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg2", i).strip()
            # 총매도평단가3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg3", i).strip()
            # 총매수평단가3 = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg3", i).strip()
            # 총매도평단가4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg4", i).strip()
            # 총매수평단가4 = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg4", i).strip()
            # 총매도평단가5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg5", i).strip()
            # 총매수평단가5 = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg5", i).strip()
            # 외국계매도대금 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdval", i).strip()
            # 외국계매수대금 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsval", i).strip()
            # 외국계매도평단가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdvag", i).strip()
            # 외국계매수평단가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsvag", i).strip()
            # 투자주의환기 = self.ActiveX.GetFieldData(self.OUTBLOCK, "info5", i).strip()
            # 기업인수목적회사여부 = self.ActiveX.GetFieldData(self.OUTBLOCK, "spac_gubun", i).strip()
            # 발행가격 = self.ActiveX.GetFieldData(self.OUTBLOCK, "issueprice", i).strip()
            # 배분적용구분코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "alloc_gubun", i).strip()
            # 배분적용구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "alloc_text", i).strip()
            # 단기과열_VI발동 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shterm_text", i).strip()
            # 정적VI상한가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svi_uplmtprice", i).strip()
            # 정적VI하한가 = self.ActiveX.GetFieldData(self.OUTBLOCK, "svi_dnlmtprice", i).strip()
            # 저유동성종목여부 = self.ActiveX.GetFieldData(self.OUTBLOCK, "low_lqdt_gu", i).strip()
            # 이상급등종목여부 = self.ActiveX.GetFieldData(self.OUTBLOCK, "abnormal_rise_gu", i).strip()
            # 대차불가표시 = self.ActiveX.GetFieldData(self.OUTBLOCK, "lend_text", i).strip()

        if(self.parent.mainCall == True):
            print('리시브성공 : {} {} , {} / {}'.format(단축코드, 시가총액, self.parent.countStockList1+1, self.parent.StockListLen))
            list = [시가총액, 단축코드]

            if self.parent.countStockList1 == (self.parent.StockListLen-1):
                self.dataControl = Database()
                self.dataControl.AddStockListTotal(list)
                self.parent.statusBar.showMessage("시총 업데이트 완료!")
            else:
                self.dataControl = Database()
                self.dataControl.AddStockListTotal(list)
                self.parent.MarketCapFunction2()

        else:
            outblockList = [한글명, 현재가]
            result.append(outblockList)
            print(result)
            self.parent.resultt1102 = result
            print(self.parent.resultt1102)
            self.parent.flagt1102 = 1


class t1452(XAQuery):
    """
    거래량 상위
    """
    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.dataControl = Database()

    def Query(self, 구분='1',전일구분='2',시작등락율='',종료등락율='',대상제외='',시작가격='',종료가격='',거래량='',IDX='',연속조회=False):
        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "jnilgubun", 0, 전일구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "sdiff", 0, 시작등락율)
            self.ActiveX.SetFieldData(self.INBLOCK, "ediff", 0, 종료등락율)
            self.ActiveX.SetFieldData(self.INBLOCK, "jc_num", 0, 대상제외)
            self.ActiveX.SetFieldData(self.INBLOCK, "sprice", 0, 시작가격)
            self.ActiveX.SetFieldData(self.INBLOCK, "eprice", 0, 종료가격)
            self.ActiveX.SetFieldData(self.INBLOCK, "volume", 0, 거래량)
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)
            self.ActiveX.Request(0)
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)

            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            if err_code < 0:
                클래스이름 = self.__class__.__name__
                함수이름 = inspect.currentframe().f_code.co_name
                print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            IDX = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "idx", i).strip())

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            # 종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            # 현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            # 전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            # 전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            # 등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            # 누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            # 회전율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "vol", i).strip())
            # 전일거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "jnilvolume", i).strip())
            # 전일비 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "bef_diff", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()

            lst = [종목코드]
            result.append(lst)

        self.dataControl.AddStockPick(result)
        #
        # columns = ['종목코드']
        # df = DataFrame(data=result, columns=columns)

        # print(result)


        # if self.parent != None:
        #     self.parent.OnReceiveData(szTrCode, [IDX, df])


class t1463(XAQuery):
    """
    거래량 상위
    """
    def __init__(self, parent=None, classification='classification'):
        super().__init__(parent=parent, classification='classification')
        self.dataControl = Database()

    def Query(self, 구분='1',전일구분='2',대상제외='',시작가격='',종료가격='',거래량='',IDX='',대상제외2='',연속조회=False):
        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "jnilgubun", 0, 전일구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "jc_num", 0, 대상제외)
            self.ActiveX.SetFieldData(self.INBLOCK, "sprice", 0, 시작가격)
            self.ActiveX.SetFieldData(self.INBLOCK, "eprice", 0, 종료가격)
            self.ActiveX.SetFieldData(self.INBLOCK, "volume", 0, 거래량)
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)
            self.ActiveX.SetFieldData(self.INBLOCK, "jc_num2", 0, 대상제외2)
            self.ActiveX.Request(0)
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)

            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            if err_code < 0:
                클래스이름 = self.__class__.__name__
                함수이름 = inspect.currentframe().f_code.co_name
                print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            IDX = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "idx", i).strip())

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            # 한글명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            # 현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            # 전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            # 전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            # 등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            # 누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            # 거래대금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i).strip())
            # 전일거래대금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "jnilvalue", i).strip())
            # 전일비 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "bef_diff", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            # filler = self.ActiveX.GetFieldData(self.OUTBLOCK1, "filler", i).strip()
            # 전일거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "jnilvolume", i).strip())

            lst = [종목코드]
            result.append(lst)

        self.dataControl.AddStockPick(result)

        # if self.parent != None:
        #     self.parent.OnReceiveData(szTrCode, [IDX, df])


""" =LKH=========================================================================================================== """


class t8424(XAQuery):
    """
    전체 업종 코드 리스트를 조회한다. ex) 0000 대형주, 0015 운수중비, 0018 건설업
    t1516과 한 세트로 움직이게 구성함
    """

    def Query(self, 구분='0'):
        self.구분 = 구분

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun1", 0, self.구분)

        err_code = self.ActiveX.Request(False)  # 연속조회인경우만 True
        # print(err_code)

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))  # Error Code 출력

    def OnReceiveData(self, szTrCode):
        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            업종명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            업종코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "upcode", i).strip()

            outblockList = [업종명, 업종코드]

            result.append(outblockList)
            # print(outblockList)

        # print('tr출력값:', result)

        columns = ['업종명', '업종코드']
        t8424df = DataFrame(data=result, columns=columns)

        # if self.parent is not None:
        #     self.parent.InsolventListUpdateFunction2(Re종목체크_CTS)

        self.parent.t8424receive(t8424df)


class t1516(XAQuery):
    """
    업종 코드에 해당하는 기업 리스트를 조회한다. ex) 0018 건설업 : 현대걸선, sk건설, GS건설 등
    t8424과 한 세트로 움직이게 구성함
    """

    def Query(self, 업종코드='001', 구분='0', 종목코드='', 연속조회=False):
        self.업종코드 = 업종코드
        self.구분 = 구분
        self.종목코드 = 종목코드
        self.연속조회 = 연속조회

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "upcode", 0, self.업종코드)
        # self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, self.구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, self.종목코드)

        if self.연속조회 is False:
            err_code = self.ActiveX.Request(False)
        else:
            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True

        if err_code < 0:
            className = self.__class__.__name__
            functionName = inspect.currentframe().f_code.co_name
            print("%s-%s " % (className, functionName), "error... {0}".format(err_code))  # Error Code 출력

    def OnReceiveData(self, szTrCode):
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)

        for i in range(nCount):
            Re종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip()

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            시가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            소진율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "sojinrate", i).strip())
            베타계수 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "beta", i).strip())
            거래증가율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff_vol", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            거래대금 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i).strip()

            outblockList = [self.업종코드, 종목명, 현재가, 전일대비구분, 전일대비, 등락율, 누적거래량, 시가, 고가, 저가, 소진율, 베타계수, 거래증가율, 종목코드, 거래대금]

            result.append(outblockList)
            # print(outblockList)
        # print('tr출력값:',result)

        columns = ['업종코드', '종목명', '현재가', '전일대비구분', '전일대비', '등락율', '누적거래량', '시가', '고가', '저가', '소진율', '베타계수', '거래증가율',
                   '종목코드', '거래대금']

        if len(result) >= 1:
            t1516df = DataFrame(data=result, columns=columns)

        elif (self.연속조회 == False) & (len(result) == 0):  ## 첫 조회때, 조회된 데이터가 없는 경우
            # print('결과값 없음')
            columns = ['업종코드']
            result = [self.업종코드]
            t1516df = DataFrame(data=result, columns=columns)

        else:    ## 연속조회시, 조회된 데이터가 없는 경우
            t1516df = DataFrame()

        # if self.parent is not None:
        #     self.parent.InsolventListUpdateFunction2(Re종목체크_CTS)

        self.parent.t1516receive(self.업종코드, self.구분, Re종목코드, self.연속조회, t1516df)


class t1404(XAQuery):
    """
    관리/불성실/투자유의조회
    """

    def Query(self, 구분='0', 종목체크=None, 종목체크_CTS='', 연속조회=False):
        self.구분 = 구분
        self.종목체크 = 종목체크
        self.연속조회 = 연속조회

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "jongchk", 0, 종목체크)
        self.ActiveX.SetFieldData(self.INBLOCK, "cts_shcode", 0, 종목체크_CTS)

        if 연속조회 is False:
            err_code = self.ActiveX.Request(False)


        else:
            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True


        if err_code < 0:
            클래스이름 = self.__class__.__name__
            함수이름 = inspect.currentframe().f_code.co_name
            print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))  # Error Code 출력

    def OnReceiveData(self, szTrCode):

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)

        for i in range(nCount):

            Re종목체크_CTS = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_shcode", i).strip()

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)

        for i in range(nCount):
            한글명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            지정일 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            지정일주가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "tprice", i).strip())
            지정일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "tchange", i).strip())
            대비율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "tdiff", i).strip())
            사유 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "reason", i).strip()
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            해제일 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "edate", i).strip()
            종목체크 = self.종목체크

            list = [한글명, 현재가, 전일대비구분, 전일대비, 등락율, 누적거래량, 지정일, 지정일주가, 지정일대비, 대비율,
                    사유, 종목코드, 해제일, 종목체크]

            result.append(list)
            # print(list)
        # print('tr출력값:',result)

        columns = ['한글명', '현재가', '전일대비구분', '전일대비', '등락율', '누적거래량', '지정일', '지정일주가', '지정일대비', '대비율', '사유', '종목코드', '해제일', '종목체크']

        if len(result) >= 1:
            t1404df = DataFrame(data=result, columns=columns)
        else:
            # print('결과값 없음')
            t1404df = DataFrame()

        # if self.parent is not None:
        #     self.parent.InsolventListUpdateFunction2(Re종목체크_CTS)

        self.parent.t1404receive(self.구분, self.종목체크, Re종목체크_CTS, self.연속조회, t1404df)


class t1405(XAQuery):
    """
    관리/불성실/투자유의조회
    """

    def Query(self, 구분='0', 종목체크=None, 종목체크_CTS='', 연속조회=False):
        self.구분 = 구분
        self.종목체크 = 종목체크
        self.연속조회 = 연속조회

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "jongchk", 0, 종목체크)
        self.ActiveX.SetFieldData(self.INBLOCK, "cts_shcode", 0, 종목체크_CTS)

        if 연속조회 is False:
            err_code = self.ActiveX.Request(False)

        else:
            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True

        if err_code < 0:
            클래스이름 = self.__class__.__name__
            함수이름 = inspect.currentframe().f_code.co_name
            print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))  # Error Code 출력

    def OnReceiveData(self, szTrCode):
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            Re종목체크_CTS = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_shcode", i).strip()
            # print(Re종목체크_CTS, 'RE종목체크')

        result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            한글명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            지정일 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            해제일 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "edate", i).strip()
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            종목체크 = self.종목체크

            list = [한글명, 현재가, 전일대비구분, 전일대비, 등락율, 누적거래량, 지정일, 해제일, 종목코드, 종목체크]

            result.append(list)
            # print(list)
        # print('tr출력값:',result)

        columns = ['한글명', '현재가', '전일대비구분', '전일대비', '등락율', '누적거래량', '지정일', '해제일', '종목코드', '종목체크']

        if len(result) >= 1:
            t1405df = DataFrame(data=result, columns=columns)
        else:
            # print('결과값 없음')
            t1405df = DataFrame()

        # if self.parent is not None:
        #     self.parent.InsolventListUpdateFunction2(Re종목체크_CTS)

        self.parent.t1405receive(self.구분, self.종목체크, Re종목체크_CTS, self.연속조회, t1405df)
