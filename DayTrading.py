from DatabaseClass import *
from XAQueries import *
from XAReals import *
from XASession import *
from DatabaseClass import *

import pathlib
import pythoncom
import win32com.client
import schedule
import time
import PyQt5

## UI용 Python Module
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

## 전역 변수
Delay3m = 180000   #msec 단위

## 상태 상수
AlgorithmReStart = 1
AlgorithmStop = 0


class StockPick:
    """
    t1452먼저 하고, 해당 값에 대하여 일봉 DB 대상으로 두 번째 Filtering
    (두 번째 작업이 3개월치 데이터 이용)
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.dataControl = Database()
        self.volumeCloseDB = []
        self.closePricePick = []
        self.stockPickList = []
        self.tempStockList = None
        self.shcodeStockList = None


    def StockPickAlgorithm(self):
        self.tempStockList = self.dataControl.CallStockList()  # StockList에서 shcode 불러옴

        self.shcodeStockList = []
        i = 0
        listTypeValue = []

        for temp in self.tempStockList:
            listTypeValue = list(temp)          # Tuple 형태로 호출되기 때문에 List 형태로 바꿔주기 위한 부분
            self.shcodeStockList = self.shcodeStockList + listTypeValue

            ## 거래량 DB 호출                    # 기업의 코드 shcode에 해당하는 Volume 정보가 80개씩 올라옴
            self.volumeCloseDB.append(self.dataControl.CallStockVolume(listTypeValue))

            ## 종가 비교 부분
            if len(self.volumeCloseDB[i]) > 0:
                if int(self.volumeCloseDB[i][0][2]) > int(self.volumeCloseDB[i][1][2]):  # 가장 마지막날의 종가가
                    self.closePricePick.append(listTypeValue)                            # 그 전전날의 종가보다 높을때
                    ## 거래량 비교 부분
                    volumeSum = 0
                    for j in range(80):
                        volumeSum = volumeSum + float(self.volumeCloseDB[i][j][1])
                    volumeMean = (volumeSum / 80)
                    if float(self.volumeCloseDB[i][0][1]) > (volumeMean * 3):
                        self.stockPickList.append(listTypeValue)
                        print(listTypeValue)
                        print("당일값", float(self.volumeCloseDB[i][0][1]))
                        print("평균값*3", volumeMean * 3)
                    else:
                        pass
                else:
                    pass
            else:
                pass
            print(i)
            i = i + 1

            self.parent.progressBar_StockPick.setValue(int(i * (100 / len(self.tempStockList))))

        self.parent.progressBar_StockPick.setValue(100)
        print(self.closePricePick)
        print(self.stockPickList)

        self.dataControl.AddStockPick(self.stockPickList)


class StockTrading():
    ## 주식 실제 익절 부분
    def __init__(self, parent=None):
        self.parent = parent

        self.dataControl = Database()

        self.tradingpart1Start = 0          # 매수 프로그램 시작 Flag
        self.tradingPart1Finish = 0         # 매수 프로그램 종료 Flag
        self.tradingPart2Start = 0          # 매도 프로그램 시작 Flag
        self.tradingPart2Finish = 0         # 매도 프로그램 종료 Flag

        self.stockName = "005930"           # 대상 short code 임시로 - 삼성전자 선정
        self.averageBuyPrice = 0            # 매수 가격
        self.initBuyStock = 20              # 초기 매수 주식 수
        self.averageSellPrice = 0           # 매도 가격

        self.stopLossPrice = 0              # StopLoss 가격
        self.stopLossPercentage = 0.95      # 매수가 대비, StopLoss 가격의 비율
        self.profitTakingFlag = 0           # 익절 체크
        self.currentPrice = 0               # 현재가
        self.prior3MinPrice = 0             # 이전 3분봉 종가
        self.minProfitPrice = 0             # 최소 이익 가격
        self.minProfitPercentage = 0        # 매수가 대비, 최소 이익 가격의 비율

        self.gett1101 = t1101(parent=self)
        self.resultt1101 = []               # t1101의 값을 받아오는 부분
        self.flagt1101 = 0                  # t1101의 값을 받아왔음을 확인하는 부분

        self.gett1302 = t1302(parent=self)
        self.resultt1302 = []               # t1302의 값을 받아오는 부분
        self.resultt1302_update = []        # 3분봉 업뎃을 위해 저장, 사용할 공간
        self.flagt1302 = 0                  # t1302의 값을 받아왔음을 확인하는 부분


        self.gett1102 = t1102(parent=self)
        self.resultt1102 = []               # t1101의 값을 받아오는 부분
        self.flagt1102 = 0                  # t1101의 값을 받아왔음을 확인하는 부분

        self.getCSPAT00600 = CSPAT00600(parent=self)
        self.sampleCSPAT00600 = CSPAT00600(parent=self) # 임시
        self.sampleSC1 = SC1(parent=self)               # 임시

        self.mainCall = False                           # 주식매매 함수 호출이 Main에서 이루어지지 않을때
        self.sellCSPAT00600 = CSPAT00600(parent=self)   # Buy를 위한 Class 상속
        self.sellSC1 = SC1(parent=self)                 # 주식 주문이 체결되면 그 결과를 받는 부분
        self.resultSC1 = []
        self.flagSC1 = 0

        self.upwardCheck1 = False
        self.upwardCheck2 = False
        self.streamCheck1 = False
        self.trailingCheck1 = False
        self.profitCheck1 = False

        self.accountNum = ''
        self.id = ''
        self.pwd = ''
        self.cert = ''
        self.tradingPwd = ''
        self.url = ''

        """ 계좌정보를 불러오는 곳 """
        userInfo = []
        path = pathlib.Path(__file__).parent.absolute().parent
        path = path.joinpath('User_Environment.txt')

        with open(path, encoding='utf8') as userFile:
            for line in userFile:
                userInfo.append(line.splitlines())
        userFile.close()

        if ("".join(userInfo[15]) == 'Trading') is True:
            self.accountNum = "".join(userInfo[3])
            self.id = "".join(userInfo[5])
            self.pwd = "".join(userInfo[7])
            self.cert = "".join(userInfo[9])
            self.tradingPwd = "".join(userInfo[11])
            self.url = "".join(userInfo[13])

    def OnReceiveMessage(self, systemError, messageCode, message):
        print(systemError, messageCode, message)

    def ProcessCheck(self):
        """
        Part1이 완료되었을 떄, Part2를 시작하는 부분
       """

        self.TradingPart2()

    def Check3Min(self):  # 이름은 편할대로 바꾸어도 무방
        """
        StockPick에 있는 주식들에 대한 3분봉을 MinData에 저장하는 부분
        """
        # stockPick = self.dataControl.CallStockPick() # 모니터링할 주식 리스트로 저장 ex.[('000100',), ('001820',), ('001880',)]
        # self.dataControl.DeleteMinDataAll() # 데이터 오류 없게 깔끔하게 정리
        # 위 방식은 못씀. 이 함수는 딱 1개 설정해서 입력하는 것으로 만들어야 함. 전체 삭제 후 1개씩 추가해야하기 때문임.

        # stockpick => shcode로 decomposition, 나눠서 1초씩 gap 두고 나눠서 실행되도록 코드 작성
        self.dataControl.DeleteMinDataAll()
        stockpicklist = self.dataControl.CallStockPick()

        for stocks in stockpicklist:
            shcode = "".join(stocks)
            time.sleep(1.001) # 1초당 1건, 10분당 200건 ~ 1분당 20건
            self.gett1302.Query(단축코드=shcode, 작업구분='2', 시간='', 건수='128', 연속조회=False)
            # 홀드중
            while (self.flagt1302 != 1):
                pythoncom.PumpWaitingMessages()
                if (self.flagt1302 == 1):
                    self.flagt1302 = 0
                    break

            list_temp = []
            for i in self.resultt1302_update:
                list_temp.append([shcode]+i)

            self.dataControl.AddMinData(list_temp)
            # 여기서 시간데이터만 제대로 구현되면 됨
        # 분봉 업뎃하면 BuySignal 분석 자동실행
        CheckBuySignal()

    def CheckBuySignal(self):
        """
        Check3Min으로 업뎃된 분봉데이터를 보고 사고 팔 지 판단, Signal을 보내는 부분
        """

        stockpicklist = self.dataControl.CallStockPick()
        # shcode = ['000100'] # 완성 전 임시변수 - 나중에 for문으로 stockpicklist 돌릴꺼임

        for stocks in stockpicklist:
            # shcode = "".join(stocks)
            shcode = stocks

            stockMinData = self.dataControl.CallMinData(shcode)
            stockVolumeLastday = self.dataControl.CallStockVolumeLastday(shcode)


            # cl = checklist 축약어
            # [*][0] : 시간 / [*][1] : 거래량 / [*][2] : 종가 / [*][3] : 전날종가대비 지금가격의 % 변화량
            """
            조회 시 최신 데이터는 3분을 꽉 채운 데이터가 아니라 X초 동안의 데이터임.
            때문에, 아래에서 '현' 이라고 해도 실제 받아쓰는 데이터는 직전 데이터임
            """
            cl1 = (stockMinData[-2][1]*(1.1) > stockMinData[-3][1]) # 해석 : 현  3분봉 거래량이   이전   3분봉보다 1.1배 이상 높음
            cl2 = (stockMinData[-3][1]*(1.1) > stockMinData[-4][1]) # 해석 : 이전 3분봉 거래량이  이전x2  3분봉보다 1.1배 이상 높음

            cl3 = (stockMinData[-2][1] * (4) > stockMinData[-3][1]+stockMinData[-4][1]+stockMinData[-5][1]+stockMinData[-6][1])
            # 해석 : 현 3분봉이 이전 4개 3분봉 거래량 평균보다 거래량이 높음
            cl4 = (stockMinData[-2][1]*(1.5) > (stockVolumeLastday / 130))    # 해석 : 현 3분봉 거래량이 전날 3분봉 거래량보다 2.0배 이상 높음

            cl5 = (stockMinData[-2][2]*(1.0) > stockMinData[-3][2]) # 해석 : 현  3분봉 종가가     이전   3분봉보다 1.0배 이상 높음
            cl6 = (stockMinData[-3][2]*(1.0) > stockMinData[-4][2]) # 해석 : 이전  3분봉 종가가   이전x2  3분봉보다 1.0배 이상 높음

            # 다양한 buySignal들을 만들어서 응용 코드를 만들 수 있다
            buySignal1 = cl1 & cl2 & cl3 & cl4 & cl5 & cl6
            buySignal2 = cl1 & cl2 & cl3 & cl5 & cl6

            print(shcode, "종목 체크리스트 결과 : ", cl1, cl2, cl3, cl4, cl5, cl6, "최종 시그널 해석 : ", buySignal1, buySignal2)


            if buySignal1:
                print(shcode, "구매들어감")
                self.BuyStock(shcode, 1)
                break

            if buySignal2:
                print(shcode, "구매들어감")
                self.BuyStock(shcode, 1)
                break

    def CheckBuySignal_Fast(self):
        """
        t1302 조회속도의 한계(10분에 200회)로, 1분간격으로 조회X 3분간격으로 조회해야함(종목수가많을시 조회 반복 어려움 - 분당 20회로 제한)
        만약 위 문제가 해결되면 이 함수 사용하면 된다
        """

        stockpicklist = self.dataControl.CallStockPick()
        shcode = ['000100'] # 완성 전 임시변수 - 나중에 for문으로 stockpicklist 돌릴꺼임

        stockMinData = self.dataControl.CallMinData(shcode)
        stockVolumeLastday = self.dataControl.CallStockVolumeLastday(shcode)

        # cl = checklist 축약어
        # [*][0] : 시간 / [*][1] : 거래량 / [*][2] : 종가 / [*][3] : 전날종가대비 지금가격의 % 변화량

        cl1 = (stockMinData[-1][1]*(1.1) > stockMinData[-2][1]) # 해석 : 현  3분봉 거래량이   이전   3분봉보다 1.1배 이상 높음
        cl2 = (stockMinData[-2][1]*(1.1) > stockMinData[-3][1]) # 해석 : 이전 3분봉 거래량이  이전x2  3분봉보다 1.1배 이상 높음

        cl3 = (stockMinData[-1][1] * (4) > stockMinData[-2][1]+stockMinData[-3][1]+stockMinData[-4][1]+stockMinData[-5][1])
        # 해석 : 현 3분봉이 이전 4개 3분봉 거래량 평균보다 거래량이 높음
        cl4 = (stockMinData[-1][1]*(1.5) > stockVolumeLastday/130)    # 해석 : 현 3분봉 거래량이 전날 3분봉 거래량보다 2.0배 이상 높음

        cl5 = (stockMinData[-1][2]*(1.0) > stockMinData[-2][2]) # 해석 : 현  3분봉 종가가     이전   3분봉보다 1.0배 이상 높음
        cl6 = (stockMinData[-2][2]*(1.0) > stockMinData[-3][2]) # 해석 : 이전  3분봉 종가가   이전x2  3분봉보다 1.0배 이상 높음

        # 다양한 buySignal들을 만들어서 응용 코드를 만들 수 있다
        buySignal1 = cl1 & cl2 & cl3 & cl4 & cl5 & cl6
        buySignal2 = cl1 & cl2 & cl3 & cl5 & cl6

        if buySignal1:
            self.BuyStock(shcode, 1)

        if buySignal2:
            self.BuyStock(shcode, 1)


    def BuyStock(self, shcode, quantity):
        """
        한종목
        현재 시장가로 매수, 정액 : 100 만원
        체결 후, Receive된 Data기준으로 평균 가격을 여기 결졍
        """

        # 모의계좌에선 주문가 넣어도 되는데, 실거래에서는 주문가 넣으면 안됨

        print('종목코드 :', shcode[0], '수량 :', quantity)

        self.getCSPAT00600.Query(계좌번호=self.accountNum, 입력비밀번호=self.tradingPwd, 종목번호=shcode[0],
                                 주문수량=quantity, 주문가='', 매매구분='2', 호가유형코드='03',
                                 신용거래코드='000', 대출일='', 주문조건구분='0')
        # ↑오리지널

        # self.getCSPAT00600.Query(계좌번호=self.accountNum, 입력비밀번호=self.tradingPwd, 종목번호='005930',
        #                          주문수량=1, 주문가='', 매매구분='2', 호가유형코드='03',
        #                          신용거래코드='000', 대출일='', 주문조건구분='0')
        # 가짜
        # 주문조건구분 : 0-없음, 1-IOC, 2-FOK => 우린 일단 0-없음
        self.tradingPart1Finish = 1
        self.tradingpart1Start = 1
        print("구매완료")
        # 주문 들어감을 알리는 flag

    def SellStock(self, shcode, quantity):
        """
        현재 지정가로 매도할 경우, 매도 잔량에 대한 Control이 어려우므로
        시장가 매도로 구현하여 잔량 고려하지 않도록 구현
        이 곳에서, 익절 이력을 바로 확인
        매수가 보다 매도가가 큰 경우, profigTakingFlag On -> 알고리즘 종료 시, Off
        """
        self.mainCall = False

        # 매도 주문 전에, 계좌에 남아있는 주문 가능 주식수 확인해야 함

        self.sellCSPAT00600.Query(계좌번호=self.accountNum, 입력비밀번호=self.tradingPwd, 종목번호=shcode,
                                  주문수량=quantity, 주문가='', 매매구분='1', 호가유형코드='03',
                                  신용거래코드='000', 대출일='', 주문조건구분='0')

        self.sellSC1.AdviseRealData()

        while(self.flagSC1 != 1):  # 매도가 조회
            pythoncom.PumpWaitingMessages()
            if (self.flagSC1 == 1):
                self.averageSellPrice = self.resulSC1[0]
                self.flagSC1 = 0
                break

    def StreamCheck(self, shcode):
        """
        횡보인지 아닌지 판단하는 방법
        1분봉 추세를 기준으로 하여, 구매 시점을 시작점으로 잡고 10분 짜리 Window를 가지는
        평균 가격을 대상하며, 이때 평균가격은 종가를 기준으로 계산한다.
        평균가격의 +- 3%이내의 범위에서 현재가격이 형성되어 있고,
        해당 현상이 5분동안 지속 될 경우 횡보로 판단 함
        즉, 판단을 호출하는 시점이 10:30분이라면,
        Step 1. Window : 10:15 ~ 10:25 / 26분봉의 종가
        Step 2. Window : 10:16 ~ 10:26 / 27분봉의 종가
        Step 3. Window : 10:17 ~ 10:27 / 28분봉의 종가
        Step 4. Window : 10:18 ~ 10:28 / 29분봉의 종가
        Step 5. Window : 10:19 ~ 10:29 / 현재 시장가
        """
        streamPrice = []
        tempSum = [0 for i in range(5)]
        avrStream = [0 for i in range(5)]
        count = 0

        self.gett1302.Query(단축코드=shcode, 작업구분='1', 시간='', 건수='15', 연속조회=False)

        while(self.flagt1302 != 1):
            pythoncom.PumpWaitingMessages()
            if (self.flagt1302 == 1):
                self.flagt1302 = 0
                break
        for i in range(len(self.resultt1302)):
            streamPrice.append(self.resultt1302[i][1])

        self.gett1102.Query(종목코드=shcode)

        while(self.flagt1102 != 1):
            pythoncom.PumpWaitingMessages()
            if (self.flagt1102 == 1):
                self.currentPrice = self.resultt1102[1]
                self.flagt1102 = 0
                break

        for i in range(5):
            for j in range(i, len(self.resultt1302)):
                tempSum[i] = tempSum[i] + streamPrice[j]
            avrStream[i] = tempSum[i]/len(self.reuslt1302)
            if (avrStream * 0.97 < self.currentPrice) & (self.currentPrice < avrStream * 1.03):
                count = count + 1

        if count == 5:
            return 1
        else:
            return 0


    def TrailingStockCheck(self):
        """
        TrailingStockCheck 방법은 좀 찾아봐야 // 알고리즘 구현
        HTS/MTS 찾아보고 구현
        """
        pass

    def AlgorithmReporitng(self):
        """
        알고리즘 종료 시, 남겨둘 정보 및 초기화 세팅
        """
        self.profitTakingFlag = 0

    ## Trading은 단일 주식을 대상으로 동작한다. 주식 종목의 최종 갯수는 추후에 확정
    def TradingPart1(self):
        """
        Trading Part 1. 주식 매수
        장 시작후 약 15분 정도는 동작 하지 않음 = 09시 15분 시작
        3분봉은 3분단위로 업데이트 된다고 가정하고, 실제 동작과 다르면 나중에 수정할 예정 (w/ RDY)
        무조건 1분 간격으로 재실행 - 최종 조건을 통과할 경우 List에서 제외
        가장 먼저 조건을 충족하는 한 종목에 대해서 매수
        """

        # 1. sql로 일 거래량 평균 계산
        # select avg(volume) from StockVolume where shcode = "000020"
        # shcode는 "" 으로 감싸야하고, avg() 함수로 쉽게 평균 구할수 있음
        # 2. sql로 가장 최근(전날) 거래량 불러오기
        # select volume from StockVolume where shcode = "000020" order by date desc limit 1
        #
        # routine1 : 1단부터 시작
        # check2 :
        # check3 : 전날 평균거래량보다 괜찮은지(쪼그라드는놈 아닌지 체크) DB.CallStockVolumeLastday(shcode)
        # check4
        #
        ## 주식 종목 선정 후, 구매 직후 실행하는 부분

        schedule.every().day.at("9:15:05").do(Check3Min)
        schedule.every().day.at("9:18:05").do(Check3Min)
        schedule.every().day.at("9:21:05").do(Check3Min)
        schedule.every().day.at("9:24:05").do(Check3Min)
        schedule.every().day.at("9:27:05").do(Check3Min)
        schedule.every().day.at("9:30:05").do(Check3Min)
        schedule.every().day.at("9:33:05").do(Check3Min)
        schedule.every().day.at("9:36:05").do(Check3Min)
        schedule.every().day.at("9:39:05").do(Check3Min)
        schedule.every().day.at("9:42:05").do(Check3Min)
        schedule.every().day.at("9:45:05").do(Check3Min)
        schedule.every().day.at("9:48:05").do(Check3Min)
        schedule.every().day.at("9:51:05").do(Check3Min)
        schedule.every().day.at("9:54:05").do(Check3Min)
        schedule.every().day.at("9:57:05").do(Check3Min)

        schedule.every().day.at("10:00:05").do(Check3Min)
        schedule.every().day.at("10:03:05").do(Check3Min)
        schedule.every().day.at("10:06:05").do(Check3Min)
        schedule.every().day.at("10:09:05").do(Check3Min)
        schedule.every().day.at("10:12:05").do(Check3Min)
        schedule.every().day.at("10:15:05").do(Check3Min)
        schedule.every().day.at("10:18:05").do(Check3Min)
        schedule.every().day.at("10:21:05").do(Check3Min)
        schedule.every().day.at("10:24:05").do(Check3Min)
        schedule.every().day.at("10:27:05").do(Check3Min)
        schedule.every().day.at("10:30:05").do(Check3Min)
        schedule.every().day.at("10:33:05").do(Check3Min)
        schedule.every().day.at("10:36:05").do(Check3Min)
        schedule.every().day.at("10:39:05").do(Check3Min)
        schedule.every().day.at("10:42:05").do(Check3Min)
        schedule.every().day.at("10:45:05").do(Check3Min)
        schedule.every().day.at("10:48:05").do(Check3Min)
        schedule.every().day.at("10:51:05").do(Check3Min)
        schedule.every().day.at("10:54:05").do(Check3Min)
        schedule.every().day.at("10:57:05").do(Check3Min)

        schedule.every().day.at("11:00:05").do(Check3Min)
        schedule.every().day.at("11:03:05").do(Check3Min)
        schedule.every().day.at("11:06:05").do(Check3Min)
        schedule.every().day.at("11:09:05").do(Check3Min)
        schedule.every().day.at("11:12:05").do(Check3Min)
        schedule.every().day.at("11:15:05").do(Check3Min)
        schedule.every().day.at("11:18:05").do(Check3Min)
        schedule.every().day.at("11:21:05").do(Check3Min)
        schedule.every().day.at("11:24:05").do(Check3Min)
        schedule.every().day.at("11:27:05").do(Check3Min)
        schedule.every().day.at("11:30:05").do(Check3Min)
        schedule.every().day.at("11:33:05").do(Check3Min)
        schedule.every().day.at("11:36:05").do(Check3Min)
        schedule.every().day.at("11:39:05").do(Check3Min)
        schedule.every().day.at("11:42:05").do(Check3Min)
        schedule.every().day.at("11:45:05").do(Check3Min)
        schedule.every().day.at("11:48:05").do(Check3Min)
        schedule.every().day.at("11:51:05").do(Check3Min)
        schedule.every().day.at("11:54:05").do(Check3Min)
        schedule.every().day.at("11:57:05").do(Check3Min)


        self.gett1101.Query(단축코드=self.stockName)

        self.averageBuyPrice = 0        # 매수 가격 평균 확정
        self.tradingPart1Finish = 1     # 단타봇의 프로그램 매수 완료


        ## Part1이 최종 완료된 후, Part2를 호출하는 부분
        if (self.tradingpart1Finish == 1):
            QTimer.singleShot(Delay3m, self.ProcessCheck)

        # while self.tradingPart1Finish = 0: 이거 안되네?
        while True:
            schedule.run_pending()
            time.sleep(1)

    def Samplepart1(self):
        self.mainCall = False
        self.tradingPart2Start = 1

        """
        Part 1이 구현되어 있지 않아, 임의로 구현한 부분
        Start----------------------------------------------------------------------------------------------
        """
        print("진입확인")

        self.sampleCSPAT00600.Query(계좌번호=self.accountNum, 입력비밀번호=self.tradingPwd, 종목번호='005930',
                                    주문수량=self.initBuyStock, 주문가='', 매매구분='2',
                                    호가유형코드='03', 신용거래코드='000', 대출일='',
                                    주문조건구분='0')
        self.sampleSC1.AdviseRealData()     # 주문가 단일 지정이라 1회만 호출하지만, 정말 1회로 해결 될지..

        while(self.flagSC1 != 1):  # 매수가 조회
            pythoncom.PumpWaitingMessages()
            if (self.flagSC1 == 1):
                self.averageBuyPrice = self.resulSC1[0]
                self.flagSC1 = 0
                break

        self.stopLossPrice = self.averageBuyPrice * self.stopLossPercentage  # Stop Loss 초기 가격 설정
        self.minProfitPrice = self.averageBuyPrice * self.minProfitPercentage  # 최소 이익 가격 설정

        """
        주식 구매 완료
        Finish-------------------------------------------------------------------------------------------
        """

    def TradingPart2(self,  quantity):
        """
        Trading Part 2. 주식 매도
        """

        self.mainCall = False
        self.tradingPart2Start = 1
        self.upwardCheck1 = False
        self.upwardCheck2 = False
        self.streamCheck1 = False

        ## 3분 대기
        QTest.qWait(Delay3m)

        ## 현재가 조회
        self.gett1102.Query(종목코드=self.stockName)
        while(self.flagt1102 != 1):
            pythoncom.PumpWaitingMessages()
            if (self.flagt1102 == 1):
                self.currentPrice = self.resultt1102[1]
                self.flagt1102 = 0
                break

        ## Alogrithm Run -> 1. StopLoss 가격과 현재가 비교
        if (self.currentPrice <= self.stopLossPrice):
            # 1. 주식 매도
            SellStock(shcode=self.stockName, quantity=quantity)

            # 2. 여유 되면 Report 작성

            # 3. Algorithm 종료 및, 다시 다른 종목 Searching 할 것인지 결정
            self.tradingPart2Finish = 1         # 매도 프로그램 종료 Flag
            return AlgorithmStop                # Alogorithm part2 종료
        else:
            self.upwardCheck1 = True

        ## Algorithm Run -> 2. 현재가 조회 및 3분봉 비교
        if self.upwardCheck1 == True:
            self.gett1102.Query(종목코드=self.stockName)

            while(self.flagt1102 != 1):
                pythoncom.PumpWaitingMessages()
                if (self.flagt1102 == 1):
                    self.currentPrice = self.resultt1102[1]
                    self.flagt1102 = 0
                    break

            self.gett1302.Query(단축코드=self.stockName, 작업구분='2', 시간='', 건수='1', 연속조회=False)

            while(self.flagt1302 != 1):
                pythoncom.PumpWaitingMessages()
                if (self.flagt1302 == 1):
                    self.prior3MinPrice = self.resultt1302[1]
                    self.flagt1302 = 0
                    break

            if(self.currentPrice <= self.prior3MinPrice):
                self.streamCheck1 = True
            else:
                self.upwardCheck2 = True

        ## Algorithm Run -> 3. 현재가와 최소 익절 가격 비교
        if self.upwardCheck2 == True:
            if(self.currentPrice <= self.minProfitPrice):
                # 1. Alogrithm Part 2다시 처음 부터 시작
                return ReStart
            else:
                # 1. 수량의 반절 익절 매도 및 익절 이력 Flag Set
                SellStock(shcode=self.stockName, quantity=quantity/2)
                self.profitTakingFlag = 1
                # 2. StopLoss 재설정 / minprofitprice도 재설정 해야 될 듯 그러나 알고리즘에 없음
                self.stopLossPrice = self.currentPrice * self.stopLossPercentage
                # 3. Algorithm Part 2다시 처음 부터 시작
                return ReStart

        ## Algorithm Run -> 4. 횡보 판단
        if self.streamCheck1 == True:
            streamState = StreamCheck()
            if streamState == 1:
                self.trailingCheck1 = True
            else:
                self.profitCheck1 = True

        ## Algorithm Run -> 5. TrailingStopCheck 방법
        if self.trailingCheck1 == True:
            # 고점 대비 하향세 일 떄 인데, 고점을 알 수 있는 방법?
            return ReStart

        ## Algorithm Run -> 6. 이미 익절 했는지 확인하는 부분
        if self.profitCheck1 == True:
            if self.profitTakingFlag == 1:
                return ReStart
            else:
                SellStock(shcode=self.stockName, quantity=quantity/2)
                self.profitTakingFlag = 1
                # 2. StopLoss 재설정 / minprofitprice도 재설정 해야 될 듯 그러나 알고리즘에 없음
                self.stopLossPrice = self.currentPrice * self.stopLossPercentage
                # 3. Algorithm Part 2다시 처음 부터 시작

        ## 최종 종료할 때만 호출, ReStart 부분에서는 호출하지 않는 부분
        self.tradingPart2Finish = 1  # 단타봇의 프로그램 매도 완료 / 최종 완료

    def Sample(self):
        self.gett1102.Query(종목코드="005930")

        while(self.flagt1102 != 1):
            pythoncom.PumpWaitingMessages()
            if (self.flagt1102 == 1):
                self.currentPrice = self.resultt1102[0][1]
                self.flagt1102 = 0
                break




if __name__ == '__main__':
    ## 실제 알고리즘을 호출하는 부분
    pass
