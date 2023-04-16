import pandas as pd

class UpdateCheck:
    """
    UpdateCheck.txt 내용 참조하여 업데이트 상태 저장 및 호출
    업데이트 시작시에 마지막으로 업데이트 상태 호출
    업데이트 중단 및 완료시에 업데이트 상태 저장
    """

    def LoadUpdateCheck(self, parent='None'):
        updateInfo = pd.read_excel('UpdateCheck.xlsx')

        return updateInfo


    def SaveUpdateCheck(self, parent='None', upcodeData= None, fssByNaverData = None ):

        updateInfo = self.LoadUpdateCheck()

        if upcodeData:    ## 업종별 기업리스트 업데이트 현황 (T1516)
            updateInfo['UpcodeData'][0] = str(upcodeData)
        else:
            pass

        if fssByNaverData:    ## 업종별 기업리스트 업데이트 현황 (T1516)
            updateInfo['FssByNaverData'][0] = str(fssByNaverData)
        else:
            pass


        # if parent.checkBox_AutoUpdate.isChecked() is True:
        #     autoUpdate = '1'
        # else:
        #     autoUpdate = '0'

        updateInfo.to_excel('UpdateCheck.xlsx', index= False)

if __name__ == '__main__':
    # a= UpdateCheck().SaveUpdateCheck(upcodeData='371')
    # b = UpdateCheck().SaveUpdateCheck(fssByNaverData='3700')
    c= UpdateCheck().SaveUpdateCheck(upcodeData='372', fssByNaverData='3701')