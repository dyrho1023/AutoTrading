import win32com.client
import pythoncom
import pathlib


class XASessionEvents(object):
    """
    Log In, Log Out 등을 위한 XASessionEvent 처리 부분
    """
    def __init__(self):
        self.parent = None
        self.code = None
        self.msg = None
        self.state = False

    def SetParent(self, parent):            # User Defined Function
        self.parent = parent

    def OnLogin(self, code, msg):           # API Defined Function
        XASessionEvents.logOut = False

        self.code = code
        self.msg = msg
        self.state = True

    def OnLogout(self):                     # API Defined Function
        pass

    def OnDisconnect(self):                 # API Defined Function
        if self.parent is not None:
            self.parent.OnDisconnect()


class XASession:
    """
    XASessionEvent를 사용하기 위한 Class
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.ActiveX = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
        self.id = None

    def login(self, url='demo.ebestsec.co.kr', port=200001, svrtype=0, uid='userid', pwd='password',
              cert='certPassword'):
        result = self.ActiveX.ConnectServer(url, port)

        if not result:
            nErrCode = self.ActiveX.GetLastError()
            strErrMsg = self.ActiveX.GetErrorMessage(nErrCode)

            return (False, nErrCode, strErrMsg)

        self.ActiveX.Login(uid, pwd, cert, svrtype, 0)
        self.id = uid

        while self.ActiveX.state is False:
            pythoncom.PumpWaitingMessages()

        return (True, 0, "OK")

    def logout(self):
        self.ActiveX.Logout()

    def disconnect(self):
        self.ActiveX.DisconnectServer()

    def IsConnected(self):
        return self.ActiveX.IsConnected()


class MyLogInOut(XASession):
    """
    User_Environment.txt 내용 참조하여 Log In & LogOut
    Log In 시에 Server 와 연결
    Log Out 시에 Server 와 연결 해제
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.code = None
        self.msg = None

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

    def MyLogIn(self):
        """
        Log In
        """
        self.login(url=self.url, uid=self.id, pwd=self.pwd, cert=self.cert)
        self.code = self.ActiveX.code
        self.msg = self.ActiveX.msg

        if self.code == "0000":
            self.parent.statusBar.showMessage("Log In 되었습니다.")
        else:
            statusBarMsg = "%s %s" % (self.code, self.msg)
            self.parent.statusBar.showMessage(statusBarMsg)

    def MyLogOut(self):
        """
        Log Out
        """
        self.logout()
        self.disconnect()
        self.parent.statusBar.showMessage("Log Out 되었습니다.")
