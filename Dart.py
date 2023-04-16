import requests
import bs4
import pandas as pd
import zipfile
from io import BytesIO
import os
from datetime import datetime
import sqlite3

# class DartCorpFssGet:
#     """
#     Dart에서 해당 기업('주식 코드')에 대한 재무제표를 받아오는 코드
#     """
#     def Get(stockCode):
#
#         url_api = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'  ##해당주소 + ?
#         key ='a3009a1573c1bf80ec5cf41419e2984134406cfa'
#
#         ## API 요청 인자 변수는 그대로 사용 ##
#         corp_code = DartCorpCodeGet.Get(stockCode).strip()
#         # corp_code = '00126380' # 기업 고유번호 (DART용)
#         bsns_year = '2019'     # 사업연도
#         reprt_code = '11011'   # 1분기보고서 : 11013, 반기보고서 : 11012, 3분기보고서 : 11014, 사업보고서 : 11011
#         fs_div = 'OFS'   ## 연결 재무 제표로 설정 ,   OFS는 개별 재무제표
#
#         dartFssGet_url = url_api+ \
#                         '?crtfc_key={}&corp_code={}&bsns_year={}&reprt_code={}&fs_div={}'.format(key, corp_code,bsns_year, reprt_code, fs_div )
#         print(dartFssGet_url)
#
#         data = requests.get(dartFssGet_url).json()
#
#         print(data)
#
#         now = datetime.datetime.now()
#         searchPeriod = datetime.timedelta(days=365*5)
#         print(searchPeriod)
#
#         beginDate = (now - searchPeriod).strftime('%y%m%d')  #160717 이런식으로 날짜로 변환
#         endDate = now.strftime('%y%m%d')
#
#         page = 20
#
#         report = data['list']
#         print(type(report), report, sep='\n' )
#
#         print(report[0].get('rcept_no'), report[0],report[1] , len(report), sep='\n')
#
#
#         items = ["rcept_no", "bsns_year", "corp_code", "reprt_code", 'account_id', "account_nm", "account_detail", "fs_div",
#                  "fs_nm", "sj_div",
#                  "sj_nm", "thstrm_nm", "thstrm_dt", "thstrm_amount", "thstrm_add_amount", "frmtrm_nm",
#                  "frmtrm_amount", 'frmtrm_q_nm', 'frmtrm_q_amount', "frmtrm_add_amount", "bfefrmtrm_nm", "bfefrmtrm_amount",
#                  "ord"]
#         item_names = ["접수번호", "사업연도", "고유번호", "보고서코드", '계정 ID', "계정명", "계정상세", "개별연결구분", "개별연결명", "재무제표구분",
#                       "재무제표명", "당기명", "당기일자", "당기금액", "당기누적금액", "전기명",
#                       "전기금액", '전기명(분/반기)', '전기금액(분/반기)', "전기누적금액", "전전기명", "전전기금액", "계정과목정렬순서"]
#
#
#         df = pd.DataFrame(columns=item_names)
#
#
#         for j in range(len(items)):
#             tempList = []
#             for i in range(len(report)):
#                 tempList.append(report[i].get(items[j]))
#             df[item_names[j]] = tempList
#
#         print(df)
#         return df
#
#
#
#
#
#
# class DartCorpCodeGet:
#     """
#        Dart에서 API활용할 때, 주식코드가 아닌 기업코드를 입력해야함.
#        이를 위해 주식코드를 입력하여, DART의 기업코드를 받아오는 클래스
#     """
#
#     def Get(stockCode):
#
#         import zipfile
#         import requests
#         import pandas as pd
#         from io import BytesIO
#         import os
#         from xml.etree.ElementTree import parse
#
#         url_api = 'https://opendart.fss.or.kr/api/corpCode.xml'  ##해당주소 + ?
#         key ='a3009a1573c1bf80ec5cf41419e2984134406cfa'
#
#
#         dartcodeInformation_url = url_api+'?crtfc_key={}'.format(key)
#         data = requests.get(dartcodeInformation_url)
#
#         # 압출파일 해제 하는 방법 :
#         # https://ayoteralab.tistory.com/entry/Get-%EB%B0%A9%EC%8B%9D%EC%9D%98-%EC%9B%B9-%EC%84%9C%EB%B9%84%EC%8A%A4Rest-API-%ED%98%B8%EC%B6%9C%ED%95%98%EA%B8%B0-Zip-FILE-binary%ED%8E%B8
#         with zipfile.ZipFile(BytesIO(data.content)) as zipfile:
#             zipfile.extractall()  ## 괄호안은 생성할 파일의 위치, 없으면 코딩 파일과 동일 디렉터리에 생성
#
#
#         # 현재 디렉터리 얻는 방법:
#         # https://codechacha.com/ko/python-examples-get-working-directory/
#         directory = os.path.dirname(os.path.realpath(__file__))
#         directory += r'\corpCode.xml'
#         xmlTree = parse(directory)
#
#         root = xmlTree.getroot()
#         list = root.findall('list')
#
#         # print(list[100].findtext('corp_code'))
#         # print(list[10].findtext('corp_name'))
#         # print(list[10].findtext('stock_code'))
#         # print(list[10].findtext('modify_date'))
#         # print(len(list))
#
#         stockCodeList = []
#         corpCodeList = []
#         corpNameList = []
#         modifyDateList = []
#
#         for i in range(len(list)):
#             if list[i].findtext('stock_code') != ' ':    ## 주식회사만 DataFrame에 담는다. 주식회사가 아닌 경우 space 한칸 입력되어 있음.
#                 stockCodeList.append(list[i].findtext('stock_code'))
#                 corpCodeList.append(list[i].findtext('corp_code'))
#                 corpNameList.append(list[i].findtext('corp_name'))
#                 modifyDateList.append(list[i].findtext('modify_date'))
#
#         dartCorpCodeDataFrame = pd.DataFrame({'종목코드': stockCodeList, 'Dart_고유번호': corpCodeList, '정식명칭': corpNameList, '수정날짜': modifyDateList})
#         dartCorpCodeDataFrame.to_excel('Dart 기업 코드 리스트.xlsx')
#
#         CorpCode = dartCorpCodeDataFrame[dartCorpCodeDataFrame['종목코드'].isin([stockCode])]['Dart_고유번호'].to_string(index = False)
#         print(CorpCode)
#         return str(CorpCode)





class DartCorpListGet():
    """
    Dart에서 취급하는(?) 주식 상장 기업 리스트를 통째로 불러온다.
    해당 리스트는 ETF, 우선주 등을 배제하는데 활용될수 있다.
    """

    def Get():

        import zipfile
        import requests
        import pandas as pd
        from io import BytesIO
        import os
        from xml.etree.ElementTree import parse

        url_api = 'https://opendart.fss.or.kr/api/corpCode.xml'  ##해당주소 + ?
        key ='a3009a1573c1bf80ec5cf41419e2984134406cfa'

        dartcodeInformation_url = url_api+'?crtfc_key={}'.format(key)
        data = requests.get(dartcodeInformation_url)

        # 압출파일 해제 하는 방법 :
        # https://ayoteralab.tistory.com/entry/Get-%EB%B0%A9%EC%8B%9D%EC%9D%98-%EC%9B%B9-%EC%84%9C%EB%B9%84%EC%8A%A4Rest-API-%ED%98%B8%EC%B6%9C%ED%95%98%EA%B8%B0-Zip-FILE-binary%ED%8E%B8
        with zipfile.ZipFile(BytesIO(data.content)) as zipfile:
            zipfile.extractall()  ## 괄호안은 생성할 파일의 위치, 없으면 코딩 파일과 동일 디렉터리에 생성


        # 현재 디렉터리 얻는 방법:
        # https://codechacha.com/ko/python-examples-get-working-directory/
        directory = os.path.dirname(os.path.realpath(__file__))
        directory += r'\corpCode.xml'
        xmlTree = parse(directory)

        root = xmlTree.getroot()
        list = root.findall('list')

        # print(list[100].findtext('corp_code'))
        # print(list[10].findtext('corp_name'))
        # print(list[10].findtext('stock_code'))
        # print(list[10].findtext('modify_date'))
        # print(len(list))

        stockCodeList = []
        corpCodeList = []
        corpNameList = []
        modifyDateList = []

        for i in range(len(list)):
            if list[i].findtext('stock_code') != ' ':    ## 주식회사만 DataFrame에 담는다. 주식회사가 아닌 경우 space 한칸 입력되어 있음.
                stockCodeList.append(list[i].findtext('stock_code'))
                corpCodeList.append(list[i].findtext('corp_code'))
                corpNameList.append(list[i].findtext('corp_name'))
                modifyDateList.append(list[i].findtext('modify_date'))

        dartCorpCodeDataFrame = pd.DataFrame({'종목코드': stockCodeList, 'Dart_고유번호': corpCodeList, '정식명칭': corpNameList, '수정날짜': modifyDateList})
        # dartCorpCodeDataFrame.to_excel('Dart 기업 코드 리스트.xlsx')

        currentDate = datetime.today().strftime("%Y%m%d")

        with sqlite3.connect('Dart.db') as conn:
            dartCorpCodeDataFrame.to_sql('{}_CorpList'.format(currentDate), con=conn, if_exists='replace', index=False)
            dartCorpCodeDataFrame.to_sql('CurrentCorpList', con=conn, if_exists='replace', index=False)

        return dartCorpCodeDataFrame



if __name__ == '__main__':
    dartCorpCodeDataFrame = DartCorpListGet.Get()