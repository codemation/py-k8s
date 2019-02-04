from tools import Logger
import time,datetime
from web import form
import web
from htmltable import HtmlTable

def getTimeDateStr():
    import datetime
    now = str(datetime.datetime.now())
    date = str(now.split(' ')[0])
    time_raw = ''.join(now.split(' ')[1].split(':'))
    time = time_raw.split('.')[0]
    timeDateStr = '%s%s' %(date,time)
    return timeDateStr


render2 = web.template.render('template/', base='layout')

class WebInstanceManager(object):
    def __init__(self, basePort):
        self.basePort = basePort
        self.Logger = Logger('9999', 'WebInstanceManager')
        self.MaxInstances = 20
        self.InstanceList = {}
        self.Logger.addLog("Instance Manager: Started")
    def AddInstance(self, WebInstance):
        self.Logger.addLog("AddInstance called")
        if self.MaxInstances < 21:
            self.InstanceList[WebInstance.instance_name] = WebInstance
            return True
        else:
            return False
        self.CleanCache()
    def AddIns(self, session):
        NewInstance = WebInstance(self,session)
        self.AddInstance(NewInstance)
        
    def RestartManager(self):
        self.Logger.addLog("RestartManager called")
        for session in self.InstanceList:
            self.CleanUpSession(int(session))
    def CleanCache(self):
        self.Logger.addLog("CleanCache called")
        import os 
        os.system("sync; echo 1 > /proc/sys/vm/drop_caches")
        self.Logger.addLog ("WebInstanceManager.CleanUpSession clear_cache issued")
    def GetCurrentCount(self):
        self.Logger.addLog("GetCurrentCount called")
        count = 0
        for item in self.InstanceList:
            count+=1
        self.Logger.addLog ("Instance Manager: GetCurrentCalled: Count %d" %(count))
        return count
    def CleanUpSession(self,session):
        self.Logger.addLog("AddInstance called")
        tmp_session_dict = {}
        ses_del = int()
        for ses in self.InstanceList:
            if int(ses) == int(session):
                ses_del = int(ses)
                pass
            else:
                tmp_session_dict[ses] = self.InstanceList[ses]
        
        self.Logger.addLog ("Del: %d" %(int(ses_del)))
        
        try:
            self.InstanceList[ses_del].KeepAlivePythonProcess.kill()
        except:
            pass
        try:
            self.InstanceList[ses_del].subp.kill()
        except:
            pass
        del self.InstanceList[ses_del]

        self.InstanceList = tmp_session_dict
        self.CleanCache()
        
    def GetFreeSessionNumber(self):
        tmp_list = []
        for s in range (0,self.MaxInstances):
            tmp_list.append(s)
        self.Logger.addLog ("Instance Manager: GetFreeSession Called:")
        if self.GetCurrentCount() < self.MaxInstances:
            for item in self.InstanceList:
                tmp_list.remove(item)
            for item in tmp_list:
                return item

        else:
            return False
    def GetAdminTableOutput(self):
        #self.Logger.addLog("AddInstance called")
        TableBase = HtmlTable(['Admin'])
        TableFreeSessionView = HtmlTable(['# Active Sessions', '# Available Sessions for New Connections'])
        SessCount = self.GetCurrentCount()
        TableFreeSessionView.AddRow([SessCount,self.MaxInstances - SessCount])
        TableManageSessions = HtmlTable(['Session Number', 'Last Active Time', 'Action'])
        TableManageServer = HtmlTable(['Restart Manager', 'Restart Server'])
        ManagerActionForm = form.Form(form.Button('RestartMan', type="submit", value='restart_man',id="submit"))
        ServerActionForm = form.Form(form.Button('RestartSer', type="submit", value='restart_ser',id="submit"))
        TableManageServer.AddRow([render2.Admin(ManagerActionForm), render2.Admin(ServerActionForm)])
        SessionTrack = {}
        for session in self.InstanceList:
            ActionForm = form.Form(form.Button('kill: %d'%(session), value=session, id="submit"))
            SessionIns = ActionForm()
            SessionTrack[session] = SessionIns
            TableManageSessions.AddRow([session, self.InstanceList[session].LastAccessTime, render2.Admin(SessionTrack[session])])
        for Table in [TableFreeSessionView, TableManageSessions, TableManageServer]:
            TableBase.AddRow([Table])
            
        return TableBase.GetFormattedHtml()
            
        


class WebInstance(object):
    def __init__(self, WebInsMgrRef, name):
        self.WebInsMgrRef = WebInsMgrRef
        self.Logger = Logger(name, 'WebInstance')
        self.instance_name = name
        self.LastAccessTime = str()
        self.LastEpoch = 0
        self.LongLoad = False
        self.InstanceKeepAliveIns = type(InstanceKeepAlive)
        self.KeepAlivePythonProcess = None
        self.port = int(self.WebInsMgrRef.basePort) + int(self.instance_name)

    def UpdateAccessTime(self):
        self.Logger.addLog("UpdateAccessTime called")
        now = datetime.datetime.now()
        self.LastAccessTime = now.strftime("%Y-%m-%d %H:%M:%S")
        self.LastEpoch = int(time.time())
    def RestartInstance(self):
        self.Logger.addLog("RestartInstance called")
    def StartSession(self, process):
        """
        input process should be in form of subprocess list imput i.e
        ['python', 'file.py', 'args']
        """
        self.Logger.addLog("StartSession called")
        import subprocess
        self.subp = subprocess.Popen(process)
        self.InstanceKeepAliveIns = InstanceKeepAlive(self.instance_name,self.WebInsMgrRef)

class InstanceKeepAlive(object):
    def __init__(self, session, WebInsMgrRef):
        import subprocess
        self.WebInsMgrRef = WebInsMgrRef
        self.Logger = Logger(session, 'InstanceKeepAlive')
        self.session = session
        self.LastTime = self.CheckTime()
        self.port = int(WebInsMgrRef.basePort) + int(self.session)
        self.KeepAlivePython = ['import time,subprocess',
                                'session = %d'%(int(session)),
                                'while True:',
                                '    time.sleep(200)',
                                "    subp = subprocess.Popen(['curl', 'http://10.216.35.20/GetEpoch/%d' %(int(session))])"]
        subprocess.Popen(['rm', '-f', 'session%dkeepalive.py' %(int(self.port))])
        time.sleep(2)
        to_open = 'session%dkeepalive.py' %(self.port)
        pyKeepAlive = open(to_open, 'w')
        for eachLine in self.KeepAlivePython:
            pyKeepAlive.write('%s\n' % (eachLine))
        pyKeepAlive.close()
        self.KeepAlivePythonProcess = subprocess.Popen(['python', 'session%dkeepalive.py' %(self.port)])
        
    def Update(self):
        self.Logger.addLog("Update called")
        self.LastTime = self.CheckTime()
        NewTime = int(time.time())
        self.Logger.addLog(self.LastTime)
        self.Logger.addLog(NewTime)
        if (NewTime - self.LastTime) > 1200:
            if self.WebInsMgrRef.InstanceList[int(self.session)].LongLoad == True:
                return True
            else:
                self.Logger.addLog("Session Inactive after more than 900 seconds, closing %d" %(self.session))
                self.KeepAlivePythonProcess.kill()
                return False
                self.WebInsMgrRef.CleanUpSession(self.session)
        else:
            return True

    def CheckTime(self):
        try:
            return self.WebInsMgrRef.InstanceList[int(self.session)].LastEpoch
        except:
            return 0
class WebSession(object):
    def __init__(self, basePort):
        self.webInsMgr = WebInstanceManager(basePort)