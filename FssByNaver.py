import pandas as pd
import sqlite3
import datetime
import numpy as np
from selenium import webdriver
import time
import re
from bs4 import BeautifulSoup


class FssByNAVER_Selenium_Giuphyunhwang:


    def Giuphyunhwang(self, URL, cursor):
        options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
        options.headless = True                         ## 크롬 창 안띄우는 설정
        options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정

        driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
        driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행

        driver.get(URL)
        # driver.get('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930&cn=')
        # time.sleep(0.1)

        driver.find_element_by_id(cursor).click()  ## 기업현황에서 테이블 선택옵션으로 되어 있는 '연간' '분기' 중 1개 클릭
        # time.sleep(0.1)

        driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
                                                                    ## 본문 컨텐츠 클래스 이름 : PageContentContainer

        soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환
        driver.quit()   ## 크롬 드라이버 나가기

        basicSource = soup.find_all('table',class_='gHead01 all-width')

        for i in range(len(basicSource)):                           ## gHead01 all-width의 클래스 이름이 여러 곳에서 쓰이므로
            if basicSource[i].find('caption').text == '주요재무정보': ## '주요재무정보' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
                index=i

        # ffsDataFrame = pd.read_html(str(basicSource[index]))  ## 테이블을 통쨰로 불러오는 방법  : 그런데, 오히려 시간이 더 느림....
        # print(ffsDataFrame)
        # ffsDataFrame[-1].to_excel('{}.xlsx'.format(cursor))
        # print(ffsDataFrame[-1].columns)
        # return ffsDataFrame[-1]

        ### th(재무제표 테이블의 컬럼) 크롤링 하기 ##
        thList=['시점']
        jogunIndexList = [0]  ## 테이블에 날짜가 적혀있는 컬럼의 인덱스만 추출할 리스트 (항목, ,2012/12, 2013/12, 2014/12) => [0,2,3,4]
        for i in range(len(basicSource[index].find('thead').find_all('th'))):

            jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
            if jogun:
                thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])
                jogunIndexList.append(i)

        # print(thList, jogunIndexList)
        del thList[-2:]     ## 2, 3년후에 대한 재무제표 예상치 컬럼 삭제
        del jogunIndexList[-2:]  ## 2, 3년후에 대한 재무제표 예상치 컬럼 삭제
        ### th(재무제표 테이블의 컬럼) 크롤링 하기 ##
        # print(thList, jogunIndexList)



        ### tr(재무제표 테이블의 값이 존재하는 행) 크롤링 하기 ##
        tempList=[]
        ffsDataFrame = pd.DataFrame({thList[0]:thList})
        for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
            tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')


            kanLength = 11                  ## 테이블의 칸(열)의 개수
            if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
                for j in range(kanLength - len(tempList)):
                    tempList.append('0')

            if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
                tempList=tempList[2:]

            for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
                    tempList[j] = tempList[j].strip().replace(',','')

            # del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
            # del tempList[-2:]     ## 2, 3년후에 대한 재무제표 예상치 컬럼 삭제
            tempList.insert(1, 0)

            dataList = []

            for h in jogunIndexList:
                dataList.append(tempList[h])

            ffsSeries = pd.Series(dataList).rename(dataList[0])
            ffsDataFrame = pd.concat([ffsDataFrame, ffsSeries], axis = 1 )
        ### tr(재무제표 테이블의 값이 존재하는 행) 크롤링 하기 ##


        ffsDataFrame= ffsDataFrame.drop(0, axis= 'index').reset_index(drop=True)



        if cursor == 'cns_Tab21':
            ffsDataFrame['시점'] = ffsDataFrame['시점'] + '(Y)'
            # ffsDataFrame['시점'] = ffsDataFrame['시점'].str[0:-2] + 'Year' ## 사업보고서는 2021/Year와 같이 뒤에 Month 대신에 Year을 붙인다.

            # print(ffsDataFrame.columns)

        ffsDataFrame = ffsDataFrame[['시점',  '세전계속사업이익', '당기순이익', '당기순이익(지배)',
       '당기순이익(비지배)', '자산총계', '부채총계', '자본총계', '자본총계(지배)', '자본총계(비지배)', '자본금',
       '영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름', 'CAPEX', 'FCF', '이자발생부채','부채비율', '자본유보율', '발행주식수(보통주)']]

        # print(ffsDataFrame.columns)


        return ffsDataFrame

    def Get(self, code):
        cursorList = ['cns_Tab21' , 'cns_Tab22']  ## ## 기업현황에서 테이블 선택옵션으로 되어 있는 '연간' '분기'를 지칭하는 html 'id'
        URL = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}&cn='.format(code)
        for i in range(len(cursorList)):
            tempDataFrame = self.Giuphyunhwang(URL, cursorList[i])
            if i ==0:
                ffsDataFrame = tempDataFrame.copy()
            else:
                ffsDataFrame = pd.concat([ffsDataFrame, tempDataFrame], axis= 0)  ## 재무분석, 투자지표와 다르게 기업현황은 시점이 '연간'과 '분기'로 나뉘므로

                                                                                  ## 행을 늘리는 방법으로 합친다.
        ffsDataFrame.to_excel('testffdataframe4.xlsx')
        return ffsDataFrame



class FssByNAVER_Selenium_Jaemubunsuk:
    def Jaemubunsuk(self, URL, cursor):
        options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
        options.headless = True                         ## 크롬 창 안띄우는 설정
        options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정

        driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
        driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행

        driver.get(URL)
        # driver.get('https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page=1')

        time.sleep(0.1)

        driver.find_element_by_id(cursor).click()    ##재무분석에서 선택옵션으로 되어 있는 '포괄손익계산서' '재무상태표' '현금흐름표' 중 1개 클릭
        time.sleep(0.1)

        driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
                                                                    ## 본문 컨텐츠 클래스 이름 : PageContentContainer


        soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환

        driver.quit()   ## 크롬 드라이버 나가기

        basicSource = soup.find_all('table',class_='gHead01 all-width data-list')  ## table을 지칭하는 class 이름
        # print(basicSource)

        for i in range(len(basicSource)):                               ## gHead01 all-width의 클래스 이름이 html 상 여러 곳에서 확인되므로
            if basicSource[i].find('caption').text == '재무분석 리스트':  ## '재무분석 리스트' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
                index=i

        ##
        thList=['시점']
        # print(soup.find_all('table',class_='gHead01 all-width')[index].find('thead').find_all('th'))
        for i in range(len(basicSource[index].find('thead').find_all('th'))):
            # print(soup.find_all('table', class_='gHead01 all-width')[index].find('thead').find_all('th')[i].text.strip())
            jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
            if jogun:
                thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])



        tempList=[]
        ffsDataFrame = pd.DataFrame({thList[0]:thList})
        # print('========================', basicSource[index].find('tbody').find_all('tr'), sep='\n')
        # print('========================', basicSource[index].find('tbody').find_all('tr')[0].text.strip().split('\n'), sep='\n')
        for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
            tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')

            kanLength = 11  ## 테이블의 칸(열)의 개수
            if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
                for j in range(kanLength - len(tempList)):
                    tempList.append('0')

            if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
                tempList=tempList[2:]

            for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
                tempList[j]= tempList[j].strip()


            del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
            del tempList[-2:]   ## YoY(전년대비) 항목 지우기


            # print(tempList)

            ffsSeries = pd.Series(tempList).rename(tempList[0])
            ffsDataFrame = pd.merge(ffsDataFrame_Temp, ffsDataFrame, how = 'outer', on='시점' )

        ffsDataFrame= ffsDataFrame.drop(0, axis= 'index').reset_index(drop=True)
        # ffsDataFrame= ffsDataFrame.set_index(ffsDataFrame[thList[0]]).drop(thList[0], axis='columns')

        if cursor == 'rpt_tab3':
            ffsDataFrame = ffsDataFrame.drop(columns = ["법인세비용차감전계속사업이익", "법인세비용"])

        # print(ffsDataFrame)
        return ffsDataFrame
        # ffsDataFrame.to_excel('testffdataframe.xlsx')



    def Get(self, code):
        cursorList = ['rpt_tab1', 'rpt_tab2', 'rpt_tab3']  ## 재무분석에서 선택옵션으로 되어 있는 '포괄손익계산서' '재무상태표' '현금흐름표'를 지칭하는 html 'id'
        URL = 'https://navercomp.wisereport.co.kr/v2/company/c1030001.aspx?cmp_cd={}&cn='.format(code)
        for i in range(len(cursorList)):
            tempDataFrame = self.Jaemubunsuk(URL, cursorList[i])
            if i ==0:
                ffsDataFrame = tempDataFrame.copy()
            else:
                ffsDataFrame = pd.merge(tempDataFrame, ffsDataFrame, how = 'outer', on='시점')

        return ffsDataFrame



class FssByNAVER_Selenium_Tujajipyo:

    def Tujajipyo(self, URL, cursor):
        options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
        options.headless = True                         ## 크롬 창 안띄우는 설정
        options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정

        driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
        driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행

        driver.get(URL)
        # driver.get('https://navercomp.wisereport.co.kr/v2/company/c1040001.aspx?cmp_cd=005930&cn=')
        # time.sleep(0.1)

        driver.find_element_by_id(cursor).click()    ## 투자분석에서 선택옵션으로 되어 있는 '수익성' '성장성' '안정성' '활동성' 중 1개 클릭
        time.sleep(0.3)  ## 최소 0.2는 기다려야 두 개의 표 모두 크롤링됨

        driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
                                                                ## 본문 컨텐츠 클래스 이름 : PageContentContainer
        soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환

        basicSource = soup.find_all('table',class_='gHead01 all-width data-list')  ## table을 지칭하는 class 이름

        driver.quit()  ## 크롬 드라이버 나가기

        ### 투자지표는 테이블 2개를 크롤링하고, 재무분석은 테이블 1개만 크롤링 하므로   ###
        ### 투자지표만 indexList 및 전체 테이블 크롤링을 2회 반복하는 작업을 갖는다.  ###
        ### 그 외는 투자지표와 재무분석의 큰 틀은 거의 동일함.                      ###


        indexList = []                         ## 아래 for문에서 if문('투자지표 리스트'라고 써있는) 을 만족하는 경우가 몇개인지 카운트 및 관리하기 위한 용도
        for i in range(len(basicSource)):                             ## gHead01 all-width의 클래스 이름이 html 상 여러 곳에서 확인되므로
            if basicSource[i].find('caption').text == '투자지표 리스트': ## '재무분석 리스트' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
                index=i
                indexList.append(index)

        for k in range(len(indexList)):       ## basicSource[i].find('caption').text == '투자지표 리스트'을 만족한 횟수만큼 아래의 과정을 반복
            index = indexList[k]

            thList=['시점']
            jogunIndexList = [0]    ## 테이블에 날짜가 적혀있는 컬럼의 인덱스만 추출할 리스트 (항목, ,2012/12, 2013/12, 2014/12) => [0,2,3,4]
            # print(soup.find_all('table',class_='gHead01 all-width')[index].find('thead').find_all('th'))
            for i in range(len(basicSource[index].find('thead').find_all('th'))):
            # print(soup.find_all('table', class_='gHead01 all-width')[index].find('thead').find_all('th')[i].text.strip())

                jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
                if jogun:
                    thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])
                    jogunIndexList.append(i)

            # print(thList, jogunIndexList)

            # for j in range(2, jogunIndexList[0]):
            #     thList.insert(1, None)


            # #
            # tempList=[]
            # ffsDataFrame_Temp = pd.DataFrame({thList[0]:thList})  ## th(테이블의 컬럼이름) 가지고 먼저 dataframe 만들기 -> 나중에 인덱스로 변환 예정
            # # print('========================', basicSource[index].find('tbody').find_all('tr'), sep='\n')
            # # print('========================', basicSource[index].find('tbody').find_all('tr')[0].text.strip().split('\n'), sep='\n')
            # a = pd.read_html(str(basicSource[index]))
            # ffsDataFrame_Temp = a[0].iloc[:,jogunIndexList]
            #
            #
            # if k==0:
            #     ffsDataFrame = ffsDataFrame_Temp.copy()
            # else:
            #     ffsDataFrame = pd.merge(ffsDataFrame_Temp, ffsDataFrame, how = 'outer', on='시점' )
            #
            # print(ffsDataFrame)
            # ffsDataFrame.to_excel('test2.xls')

            tempList = []
            ffsDataFrame_Temp = pd.DataFrame({thList[0]: thList})
            for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
            # for i in jogunIndexList:

                tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')

                kanLength = 11  ## 테이블의 칸(열)의 개수
                if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
                    for j in range(kanLength - len(tempList)):
                        tempList.append('0')

                # kanLength = jogunIndexList[-1] ## 테이블의 칸(열)의 개수
                # if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
                #     for j in range(kanLength - len(tempList)):
                #         tempList.append('')


                if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
                    tempList=tempList[2:]

                for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
                        tempList[j] = tempList[j].strip().replace(',','')


                del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
                # del tempList[-2:]   ## YoY(전년대비) 항목 지우기


                dataList = []

                for h in jogunIndexList:
                    dataList.append(tempList[h])


                ffsSeries = pd.Series(dataList).rename(dataList[0])
                # print(ffsSeries, ffsDataFrame_Temp, sep='\n\n')

                ffsDataFrame_Temp = pd.concat([ffsDataFrame_Temp, ffsSeries], axis = 1)

            ffsDataFrame_Temp= ffsDataFrame_Temp.drop(0, axis= 'index').reset_index(drop=True)
            # ffsDataFrame_Temp= ffsDataFrame_Temp.set_index(ffsDataFrame_Temp[thList[0]]).drop(thList[0], axis='columns')


            if k==0:
                ffsDataFrame = ffsDataFrame_Temp.copy()
            else:
                ffsDataFrame = pd.merge(ffsDataFrame_Temp, ffsDataFrame, how = 'outer', on='시점' )

            # ffsDataFrame['시점'] = ffsDataFrame['시점'] + '(Y)'   ## 사업보고서는 2021/Year와 같이 뒤에 Month 대신에 Year을 붙인다.

        return ffsDataFrame


    def Get(self, code):
        cursorList = ['val_tab1']  ## 투자분석에서 선택옵션으로 되어 있는 '수익성' '성장성' '안정성' '활동성' 중 1개를 지칭하는 html 'id'
        URL = 'https://navercomp.wisereport.co.kr/v2/company/c1040001.aspx?cmp_cd={}&cn='.format(code)
        for i in range(len(cursorList)):

            tempDataFrame = self.Tujajipyo(URL, cursorList[i])

            if i ==0:
                ffsDataFrame = tempDataFrame.copy()
            else:
                ffsDataFrame = pd.merge(tempDataFrame, ffsDataFrame, how = 'outer', on='시점')

        ffsDataFrame['시점'] = ffsDataFrame['시점'] + '(Y)'   ## 사업보고서는 2021/Year와 같이 뒤에 Month 대신에 Year을 붙인다.

        ffsDataFrame = ffsDataFrame[['시점', '매출총이익률', '매출총이익＜당기＞', '매출액＜당기＞_x', '영업이익률', '영업이익＜당기＞','순이익률',
                                     'EPS','BPS', 'CPS', 'SPS', 'PER',  'PBR', 'PCR', 'PSR', 'EV/EBITDA', 'EV＜당기＞',
                                     'EBITDA＜당기＞_x', 'DPS', '현금DPS', '주식DPS', '현금배당수익률', '현금배당성향(%)',
                                    'EBITDA마진율', 'ROE', 'ROA', 'ROIC', 'NOPLAT', 'IC']]

        ffsDataFrame = ffsDataFrame.rename(columns={'매출총이익＜당기＞': '매출총이익', '매출액＜당기＞_x': '매출액',
                                                    '영업이익＜당기＞' : '영업이익',
                                                    'EV＜당기＞': 'EV', 'EBITDA＜당기＞_x' :'EBITDA'})

        # ffsDataFrame.to_excel('testffdataframe2.xlsx')
        return ffsDataFrame



class FssByNaver:
    def Get(self, code):
        try:
            ## 각각의 필요한 클래스를 불러와 합치는 코드 ##
            print('투자지표 불러오는중')
            a = FssByNAVER_Selenium_Tujajipyo().Get(code)

            # b = FssByNAVER_Selenium_Jaemubunsuk().Get(code)
            print('기업현황 불러오는중')
            c = FssByNAVER_Selenium_Giuphyunhwang().Get(code)
            # print(a, c ,sep='\n')

            # a.to_excel('a.xlsx')
            # c.to_excel('c.xlsx')

            ffsDataFrame = pd.merge(a,c, how= 'outer', on='시점')
            # ffsDataFrame.to_excel('test_ffsDataframe3_{}.xlsx'.format(code))
            # ffsDataFrame = pd.concat([a,c], axis = 0)



            ## 재무제표 수치를 string 및 None, '' 값에서 float 타입으로 변경하는 작업
            ffsDataFrame_columns = list(ffsDataFrame.columns)
            ffsDataFrame_columns.remove('시점')


            for i in list(ffsDataFrame_columns): #rename_columns:
                   ffsDataFrame[i] = ffsDataFrame[i].str.strip().replace('', np.nan).replace('N/A', np.nan).fillna(0).astype(float)
            # ffsDataFrame.to_excel('test_ffsDataframe3_{}.xlsx'.format(code))
            ffsDataFrame['종목코드'] = code
            ffsDataFrame['크롤링_시간'] = datetime.datetime.now()



            ### DB에 넣기 ###
            # currentTime = datetime.datetime.today().strftime("%Y-%m-%d")
            with sqlite3.connect('FssData.db') as conn:
                ffsDataFrame.to_sql(code, con=conn, if_exists='replace', index=False)

            ### DB에 넣기 ###

            # ffsDataFrame.to_excel('test_ffsDataframe3_{}.xlsx'.format(code))

            return ffsDataFrame

        except:
            print(code,'는 재무제표가 크롤링되지 않았습니다. \n')

            with open('crawl_fail.txt', encoding='CP949') as f:
                fail_list = []
                for line in f:
                    fail_list.append(line)

                fail_list.append('\n')
                fail_list.append(code)

            with open('crawl_fail.txt', 'w') as f:
                f.writelines(fail_list)

            return None



if __name__ == '__main__':

    # input = '000660'
    # a = FssByNAVER().Get(input)
    # a = FssByNaver().Get('000020')  ##950210 000250 338100
    # a = FssByNaver().Get('328380')
    a = FssByNaver().Get('330590') ## 투자지표의 매출 총이익에서 2019/06가 0이어야하나, 투자지표의 아래 테이블과 합쳐지면서 20 생성됨 => (Y) 적용된 것 중에서 /12가 아닌것은 쓰지 않는다.
    # a = FssByNaver().Get('330990')
    # a = FssByNAVER_Selenium_Tujajipyo().Get('328380')
    # a = FssByNAVER_Selenium_Tujajipyo().Get('000020')
    # a = FssByNAVER_Selenium_Giuphyunhwang().Get('328380')

































########################################## 이전 버젼 #########################################



# import pandas as pd
# import sqlite3
# import datetime
# import numpy as np
# from selenium import webdriver
# import time
# import re
# from bs4 import BeautifulSoup
#
# class FssByNAVER_Selenium_Giuphyunhwang:
#
#
#     def Giuphyunhwang(self, URL, cursor):
#         options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
#         options.headless = True                         ## 크롬 창 안띄우는 설정
#         options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정
#
#         driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
#         driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행
#
#         driver.get(URL)
#         # driver.get('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=005930&cn=')
#         # time.sleep(0.1)
#
#         driver.find_element_by_id(cursor).click()  ## 기업현황에서 테이블 선택옵션으로 되어 있는 '연간' '분기' 중 1개 클릭
#         # time.sleep(0.1)
#
#         driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
#                                                                     ## 본문 컨텐츠 클래스 이름 : PageContentContainer
#
#         soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환
#         driver.quit()   ## 크롬 드라이버 나가기
#
#         basicSource = soup.find_all('table',class_='gHead01 all-width')
#
#         for i in range(len(basicSource)):                           ## gHead01 all-width의 클래스 이름이 여러 곳에서 쓰이므로
#             if basicSource[i].find('caption').text == '주요재무정보': ## '주요재무정보' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
#                 index=i
#
#         # ffsDataFrame = pd.read_html(str(basicSource[index]))  ## 테이블을 통쨰로 불러오는 방법  : 그런데, 오히려 시간이 더 느림....
#         # print(ffsDataFrame)
#         # ffsDataFrame[-1].to_excel('{}.xlsx'.format(cursor))
#         # print(ffsDataFrame[-1].columns)
#         # return ffsDataFrame[-1]
#
#         ### th(재무제표 테이블의 컬럼) 크롤링 하기 ##
#         thList=['시점']
#         for i in range(len(basicSource[index].find('thead').find_all('th'))):
#
#             jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
#             if jogun:
#                 thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])
#         del thList[-2:]     ## ## 2, 3년후에 대한 재무제표 예상치 컬럼 삭제
#         ### th(재무제표 테이블의 컬럼) 크롤링 하기 ##
#
#
#
#         ### tr(재무제표 테이블의 값이 존재하는 행) 크롤링 하기 ##
#         tempList=[]
#         ffsDataFrame = pd.DataFrame({thList[0]:thList})
#         for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
#             tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')
#
#             kanLength = 9                  ## 테이블의 칸(열)의 개수
#             if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
#                 for j in range(kanLength - len(tempList)):
#                     tempList.append('0')
#
#             if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
#                 tempList=tempList[2:]
#
#             for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
#                     tempList[j] = tempList[j].strip().replace(',','')
#
#             # del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
#             del tempList[-2:]     ## 2, 3년후에 대한 재무제표 예상치 컬럼 삭제
#
#             ffsSeries = pd.Series(tempList).rename(tempList[0])
#             ffsDataFrame = pd.concat([ffsDataFrame, ffsSeries], axis = 1 )
#         ### tr(재무제표 테이블의 값이 존재하는 행) 크롤링 하기 ##
#
#
#         ffsDataFrame= ffsDataFrame.drop(0, axis= 'index').reset_index(drop=True)
#
#
#
#         if cursor == 'cns_Tab21':
#             ffsDataFrame['시점'] = ffsDataFrame['시점'].str[0:-2] + 'Year'   ## 사업보고서는 2021/Year와 같이 뒤에 Month 대신에 Year을 붙인다.
#
#         # print(ffsDataFrame.columns)
#
#         ffsDataFrame = ffsDataFrame[['시점',  '세전계속사업이익', '당기순이익', '당기순이익(지배)',
#        '당기순이익(비지배)', '자산총계', '부채총계', '자본총계', '자본총계(지배)', '자본총계(비지배)', '자본금',
#        '영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름', 'CAPEX', 'FCF', '이자발생부채','부채비율', '자본유보율', '발행주식수(보통주)']]
#
#         # print(ffsDataFrame.columns)
#
#
#         return ffsDataFrame
#
#     def Get(self, code):
#         cursorList = ['cns_Tab21' , 'cns_Tab22']  ## ## 기업현황에서 테이블 선택옵션으로 되어 있는 '연간' '분기'를 지칭하는 html 'id'
#         URL = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}&cn='.format(code)
#         for i in range(len(cursorList)):
#             tempDataFrame = self.Giuphyunhwang(URL, cursorList[i])
#             if i ==0:
#                 ffsDataFrame = tempDataFrame.copy()
#             else:
#                 ffsDataFrame = pd.concat([ffsDataFrame, tempDataFrame], axis= 0)  ## 재무분석, 투자지표와 다르게 기업현황은 시점이 '연간'과 '분기'로 나뉘므로
#
#                                                                                   ## 행을 늘리는 방법으로 합친다.
#         # ffsDataFrame.to_excel('testffdataframe4.xlsx')
#         return ffsDataFrame
#
#
#
# class FssByNAVER_Selenium_Jaemubunsuk:
#     def Jaemubunsuk(self, URL, cursor):
#         options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
#         options.headless = True                         ## 크롬 창 안띄우는 설정
#         options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정
#
#         driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
#         driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행
#
#         driver.get(URL)
#         # driver.get('https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page=1')
#
#         time.sleep(0.1)
#
#         driver.find_element_by_id(cursor).click()    ##재무분석에서 선택옵션으로 되어 있는 '포괄손익계산서' '재무상태표' '현금흐름표' 중 1개 클릭
#         time.sleep(0.1)
#
#         driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
#                                                                     ## 본문 컨텐츠 클래스 이름 : PageContentContainer
#
#
#         soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환
#
#         driver.quit()   ## 크롬 드라이버 나가기
#
#         basicSource = soup.find_all('table',class_='gHead01 all-width data-list')  ## table을 지칭하는 class 이름
#         # print(basicSource)
#
#         for i in range(len(basicSource)):                               ## gHead01 all-width의 클래스 이름이 html 상 여러 곳에서 확인되므로
#             if basicSource[i].find('caption').text == '재무분석 리스트':  ## '재무분석 리스트' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
#                 index=i
#
#         ##
#         thList=['시점']
#         # print(soup.find_all('table',class_='gHead01 all-width')[index].find('thead').find_all('th'))
#         for i in range(len(basicSource[index].find('thead').find_all('th'))):
#             # print(soup.find_all('table', class_='gHead01 all-width')[index].find('thead').find_all('th')[i].text.strip())
#             jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
#             if jogun:
#                 thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])
#
#
#
#         tempList=[]
#         ffsDataFrame = pd.DataFrame({thList[0]:thList})
#         # print('========================', basicSource[index].find('tbody').find_all('tr'), sep='\n')
#         # print('========================', basicSource[index].find('tbody').find_all('tr')[0].text.strip().split('\n'), sep='\n')
#         for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
#             tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')
#
#             kanLength = 11  ## 테이블의 칸(열)의 개수
#             if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
#                 for j in range(kanLength - len(tempList)):
#                     tempList.append('')
#
#             if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
#                 tempList=tempList[2:]
#
#             for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
#                 tempList[j]= tempList[j].strip()
#
#
#             del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
#             del tempList[-2:]   ## YoY(전년대비) 항목 지우기
#
#
#             # print(tempList)
#
#             ffsSeries = pd.Series(tempList).rename(tempList[0])
#             ffsDataFrame = pd.merge(ffsDataFrame_Temp, ffsDataFrame, how = 'outer', on='시점' )
#
#         ffsDataFrame= ffsDataFrame.drop(0, axis= 'index').reset_index(drop=True)
#         # ffsDataFrame= ffsDataFrame.set_index(ffsDataFrame[thList[0]]).drop(thList[0], axis='columns')
#
#         if cursor == 'rpt_tab3':
#             ffsDataFrame = ffsDataFrame.drop(columns = ["법인세비용차감전계속사업이익", "법인세비용"])
#
#         # print(ffsDataFrame)
#         return ffsDataFrame
#         # ffsDataFrame.to_excel('testffdataframe.xlsx')
#
#
#
#     def Get(self, code):
#         cursorList = ['rpt_tab1', 'rpt_tab2', 'rpt_tab3']  ## 재무분석에서 선택옵션으로 되어 있는 '포괄손익계산서' '재무상태표' '현금흐름표'를 지칭하는 html 'id'
#         URL = 'https://navercomp.wisereport.co.kr/v2/company/c1030001.aspx?cmp_cd={}&cn='.format(code)
#         for i in range(len(cursorList)):
#             tempDataFrame = self.Jaemubunsuk(URL, cursorList[i])
#             if i ==0:
#                 ffsDataFrame = tempDataFrame.copy()
#             else:
#                 ffsDataFrame = pd.merge(tempDataFrame, ffsDataFrame, how = 'outer', on='시점')
#
#         return ffsDataFrame
#
#
#
# class FssByNAVER_Selenium_Tujajipyo:
#
#     def Tujajipyo(self, URL, cursor):
#         options = webdriver.ChromeOptions()             ## 크롬 창 안띄우는 설정
#         options.headless = True                         ## 크롬 창 안띄우는 설정
#         options.add_argument('window-size=1920x1080')   ## 크롬 창 안띄우는 설정
#
#         driver_dir=r'C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe'    ##크롬 드라이버 위치 설정
#         driver=webdriver.Chrome(driver_dir, options= options)   ## 크롬 드라이버 실행
#
#         driver.get(URL)
#         # driver.get('https://navercomp.wisereport.co.kr/v2/company/c1040001.aspx?cmp_cd=005930&cn=')
#         # time.sleep(0.1)
#
#         driver.find_element_by_id(cursor).click()    ## 투자분석에서 선택옵션으로 되어 있는 '수익성' '성장성' '안정성' '활동성' 중 1개 클릭
#         time.sleep(0.3)  ## 최소 0.2는 기다려야 두 개의 표 모두 크롤링됨
#
#         driver.find_elements_by_class_name('PageContentContainer')  ## selenium은 css 형식을 그대로 따라하므로, 띄어쓰기는 .으로 붙여준다.
#                                                                 ## 본문 컨텐츠 클래스 이름 : PageContentContainer
#         soup = BeautifulSoup(driver.page_source, 'lxml')        ## 여기서부터 selenium -> BeautifulSoup로 전환
#
#         basicSource = soup.find_all('table',class_='gHead01 all-width data-list')  ## table을 지칭하는 class 이름
#
#         driver.quit()  ## 크롬 드라이버 나가기
#
#         ### 투자지표는 테이블 2개를 크롤링하고, 재무분석은 테이블 1개만 크롤링 하므로   ###
#         ### 투자지표만 indexList 및 전체 테이블 크롤링을 2회 반복하는 작업을 갖는다.  ###
#         ### 그 외는 투자지표와 재무분석의 큰 틀은 거의 동일함.                      ###
#
#
#         indexList = []                         ## 아래 for문에서 if문('투자지표 리스트'라고 써있는) 을 만족하는 경우가 몇개인지 카운트 및 관리하기 위한 용도
#         for i in range(len(basicSource)):                             ## gHead01 all-width의 클래스 이름이 html 상 여러 곳에서 확인되므로
#             if basicSource[i].find('caption').text == '투자지표 리스트': ## '재무분석 리스트' 라는 텍스트가 존재하는 곳(테이블)을 찾는 과정
#                 index=i
#                 indexList.append(index)
#
#         for k in range(len(indexList)):       ## basicSource[i].find('caption').text == '투자지표 리스트'을 만족한 횟수만큼 아래의 과정을 반복
#             index = indexList[k]
#
#             thList=['시점']
#             # print(soup.find_all('table',class_='gHead01 all-width')[index].find('thead').find_all('th'))
#             for i in range(len(basicSource[index].find('thead').find_all('th'))):
#             # print(soup.find_all('table', class_='gHead01 all-width')[index].find('thead').find_all('th')[i].text.strip())
#                 jogun = re.search('[0-9]{1,4}\/[0-9]{1,3}', basicSource[index].find('thead').find_all('th')[i].text.strip())
#                 if jogun:
#                     thList.append(basicSource[index].find('thead').find_all('th')[i].text.strip()[jogun.start():jogun.end()])
#
#
#
#             tempList=[]
#             ffsDataFrame_Temp = pd.DataFrame({thList[0]:thList})  ## th(테이블의 컬럼이름) 가지고 먼저 dataframe 만들기 -> 나중에 인덱스로 변환 예정
#             # print('========================', basicSource[index].find('tbody').find_all('tr'), sep='\n')
#             # print('========================', basicSource[index].find('tbody').find_all('tr')[0].text.strip().split('\n'), sep='\n')
#             for i in range(len(basicSource[index].find('tbody').find_all('tr'))):
#                 tempList = basicSource[index].find('tbody').find_all('tr')[i].text.strip().split('\n')
#
#                 kanLength = 11  ## 테이블의 칸(열)의 개수
#                 if len(tempList) < kanLength:  ## 값이 없거나 모자른 경우를 대비하여, list 원소의 개수를 통일시킴 (중간에 빈칸이 있는 경우는 ''로 이미 존재)
#                     for j in range(kanLength - len(tempList)):
#                         tempList.append('0')
#
#                 if tempList[0] == '펼치기':  ##  (+)심볼이 적용된 펼치기 항목은 임의의 빈칸이 2개더 추가되어 있으므로, 삭제한다.
#                     tempList=tempList[2:]
#
#                 for j in range(len(tempList)):  ## \t, \n, space과 같은 난잡한 문자가 섞여있는것을 없앤다.
#                         tempList[j] = tempList[j].strip().replace(',','')
#
#
#                 del tempList[1:3]   ## 중간에 존재하는 의미없는 빈칸 2개 지우기
#                 del tempList[-2:]   ## YoY(전년대비) 항목 지우기
#
#
#                 ffsSeries = pd.Series(tempList).rename(tempList[0])
#                 ffsDataFrame_Temp = pd.concat([ffsDataFrame_Temp, ffsSeries], axis = 1)
#
#             ffsDataFrame_Temp= ffsDataFrame_Temp.drop(0, axis= 'index').reset_index(drop=True)
#             # ffsDataFrame_Temp= ffsDataFrame_Temp.set_index(ffsDataFrame_Temp[thList[0]]).drop(thList[0], axis='columns')
#
#
#             if k==0:
#                 ffsDataFrame = ffsDataFrame_Temp.copy()
#             else:
#                 ffsDataFrame = pd.merge(ffsDataFrame_Temp, ffsDataFrame, how = 'outer', on='시점' )
#
#
#         ffsDataFrame['시점'] = ffsDataFrame['시점'].str[0:-2] + 'Year'   ## 사업보고서는 2021/Year와 같이 뒤에 Month 대신에 Year을 붙인다.
#
#         return ffsDataFrame
#
#
#     def Get(self, code):
#         cursorList = ['val_tab1']  ## 투자분석에서 선택옵션으로 되어 있는 '수익성' '성장성' '안정성' '활동성' 중 1개를 지칭하는 html 'id'
#         URL = 'https://navercomp.wisereport.co.kr/v2/company/c1040001.aspx?cmp_cd={}&cn='.format(code)
#         for i in range(len(cursorList)):
#
#             tempDataFrame = self.Tujajipyo(URL, cursorList[i])
#
#             if i ==0:
#                 ffsDataFrame = tempDataFrame.copy()
#             else:
#                 ffsDataFrame = pd.merge(tempDataFrame, ffsDataFrame, how = 'outer', on='시점')
#
#
#         ffsDataFrame = ffsDataFrame[['시점', '매출총이익률', '매출총이익＜당기＞', '매출액＜당기＞_x', '영업이익률', '영업이익＜당기＞','순이익률',
#                                      'EPS','BPS', 'CPS', 'SPS', 'PER',  'PBR', 'PCR', 'PSR', 'EV/EBITDA', 'EV＜당기＞',
#                                      'EBITDA＜당기＞_x', 'DPS', '현금DPS', '주식DPS', '현금배당수익률', '현금배당성향(%)',
#                                     'EBITDA마진율', 'ROE', 'ROA', 'ROIC', 'NOPLAT', 'IC']]
#
#         ffsDataFrame = ffsDataFrame.rename(columns={'매출총이익＜당기＞': '매출총이익', '매출액＜당기＞_x': '매출액',
#                                                     '영업이익＜당기＞' : '영업이익',
#                                                     'EV＜당기＞': 'EV', 'EBITDA＜당기＞_x' :'EBITDA'})
#
#         # ffsDataFrame.to_excel('testffdataframe2.xlsx')
#         return ffsDataFrame
#
#
#
#
#
# class FssByNaver:
#     def Get(self, code):
#         try:
#             ## 각각의 필요한 클래스를 불러와 합치는 코드 ##
#             print('투자지표 불러오는중')
#             a = FssByNAVER_Selenium_Tujajipyo().Get(code)
#             # b = FssByNAVER_Selenium_Jaemubunsuk().Get(code)
#             print('기업현황 불러오는중')
#             c = FssByNAVER_Selenium_Giuphyunhwang().Get(code)
#             print(a, c ,sep='\n')
#             a.to_excel('a.xlsx')
#             c.to_excel('c.xlsx')
#
#             ffsDataFrame = pd.merge(a,c, how= 'outer', on='시점')
#             # ffsDataFrame = pd.concat([a,c], axis = 0)
#
#
#             ## 중복되는 열을 제거하기 위해, 중복되는 행을 제거하는 drop_duplicates 활용
#             # ffsDataFrame = ffsDataFrame.transpose().drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False).transpose()
#
#
#             ## '중복되는 컬럼명'(ex - 기타) 을 단순히 숫자를 더하는 방법으로 중복을 피함
#             ffsDataFrame_columns = ffsDataFrame.columns
#             rename_columns = []
#             duplicated_idx = ffsDataFrame.columns.duplicated()
#             # duplicated_count = ffsDataFrame.columns.value_counts()  ## for문을 1개라도 줄이고자 해당 방법은 쓰지 않겠음 (대신 숫자가 컬럼명마다 순서대로 적용되지 않음)
#
#             for i in range(len(duplicated_idx)):
#
#                 if duplicated_idx[i]:  ## True이면 (중복이면)
#                     rename_columns.append(ffsDataFrame_columns[i] + '_' + str(i))
#                 else:
#                     rename_columns.append(ffsDataFrame_columns[i])
#             ffsDataFrame.columns = rename_columns
#             ## '중복되는 컬럼명'(ex - 기타) 을 단순히 숫자를 더하는 방법으로 중복을 피함
#
#
#
#
#             ## 재무제표 수치를 string 및 None, '' 값에서 float 타입으로 변경하는 작업
#             rename_columns.remove('시점')
#             # print(rename_columns)
#             for i in rename_columns:
#                 # ffsDataFrame[i] = ffsDataFrame[i].fillna('0')
#                 ffsDataFrame[i] = ffsDataFrame[i].str.strip().replace('', None).replace('', np.nan).replace('N/A', np.nan).replace('N/A', None).fillna(0).astype(float)
#
#             ffsDataFrame['종목코드'] = code
#             ffsDataFrame['크롤링_시간'] = datetime.datetime.now()
#
#
#
#             ### 컬럼명 중복을 테스트해보기 위한 코드 ###
#             # List = pd.Series(ffsDataFrame.columns)
#             # List = List.value_counts()
#             # List.to_excel('test 중복값.xlsx')
#             ### 컬럼명 중복을 테스트해보기 위한 코드 ###
#
#
#             ### DB에 넣기 ###
#             # currentTime = datetime.datetime.today().strftime("%Y-%m-%d")
#             with sqlite3.connect('FssData_test.db') as conn:
#                 ffsDataFrame.to_sql(code, con=conn, if_exists='replace', index=False)
#
#             ### DB에 넣기 ###
#
#             # ffsDataFrame.to_excel('test_ffsDataframe3_{}.xlsx'.format(code))
#
#             return ffsDataFrame
#
#         except:
#             print(code,'는 재무제표가 크롤링되지 않았습니다. \n')
#
#             with open('crawl_fail.txt', encoding='CP949') as f:
#                 fail_list = []
#                 for line in f:
#                     fail_list.append(line)
#
#                 fail_list.append('\n')
#                 fail_list.append(code)
#
#             with open('crawl_fail.txt', 'w') as f:
#                 f.writelines(fail_list)
#
#             return None
#
# if __name__ == '__main__':
#
#     # input = '000660'
#     # a = FssByNAVER().Get(input)
#     # a = FssByNaver().Get('000020')  ##950210 000250 338100
#     a = FssByNaver().Get('328380')
#
#     # currentTime = datetime.datetime.today().strftime("%Y%m%d")
#     #
#     # with sqlite3.connect('Dart.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
#     #     corpDartDataFrame = pd.read_sql('SELECT * FROM currentCorpList', conn, index_col=None)
#     #
#     # with sqlite3.connect('TradingDB.db') as conn:  ## Trading.db로 추후 변경 필요 (Traing.db에 'ETF구분' 항목 추가 필요)
#     #     stockTRDataFrame = pd.read_sql('SELECT * FROM StockList', conn, index_col=None)
#     #
#     # # corpDartList = list(corpDartDataFrame['종목코드'])
#     # # ETFList = list(corporationDataFrame['ETF구분'])
#     #
#     # ## 차례차례 FssByNAVER() 클래스 실행하기
#     # for i in range(0, len(stockTRDataFrame['shcode'])):
#     #
#     #     # if (ETFList[i] == 0) & (corporationList[i].strip()[5] == '0'):  ## ETF가 아니면 실행
#     #     #     a = FssByNAVER().Get(corporationList[i])
#     #
#     #     if corpDartDataFrame['종목코드'].isin([stockTRDataFrame['shcode'].iloc[i]]).sum() == 1:
#     #         a = FssByNaver().Get(stockTRDataFrame['shcode'].iloc[i])
#     #         print(stockTRDataFrame['shcode'].iloc[i], sep='\n')
#
#
#
#
#
#
#
#
#
#
#
#
