class SystemSetting:
    """
    System_Environment.txt 내용 참조하여 프로그램 기본 설정 기억
    프로그램 시작시에 마지막으로 저장된 설정 호출
    프로그램 종료시에 설정 새롭게 저장
    """
    systemInfo = []
    def LoadSystemSetting(self, parent='None'):
        with open("System_Environment.txt", encoding='utf8') as systemFile:
            for line in systemFile:
                self.systemInfo.append(line.splitlines())
            systemFile.close()

    def SaveSystemSetting(self, parent='None'):
        if parent.checkBox_AutoLogIn.isChecked() is True:
            autoLogIn = '1'
        else:
            autoLogIn = '0'

        if parent.checkBox_AutoUpdate.isChecked() is True:
            autoUpdate = '1'
        else:
            autoUpdate = '0'

        with open("System_Environment.txt", 'w', encoding="utf8") as systemFile:
            systemFile.writelines("0. 자동 로그인 : 0 - No, 1 - Yes\n")
            systemFile.writelines(autoLogIn + '\n')
            systemFile.writelines("1. 자동 업데이트 : 0 - no, 1 - yes\n")
            systemFile.writelines(autoUpdate + '\n')
            systemFile.writelines("2. 기업 리스트 마지막 업데이트\n")
            systemFile.writelines(parent.lastListUpdateTime + '\n')
            systemFile.writelines("3. 기업 거래량 마지막 업데이트\n")
            systemFile.writelines(parent.lastVolumeUpdateTime1 + '\n')
            systemFile.writelines("4. 업종별 기업 마지막 업데이트\n")
            systemFile.writelines(parent.UpCodeUpdateLastDate+'\n')
            systemFile.writelines("5. 재무제표 마지막 업데이트 \n")
            systemFile.writelines(parent.FssUpdateLastDate[0]+','+parent.FssUpdateLastDate[1]+'\n')
            systemFile.writelines("6. 위험 기업 마지막 업데이트 \n")
            systemFile.writelines(parent.RiskCorpUpdateLastDate + '\n')
            systemFile.close()
