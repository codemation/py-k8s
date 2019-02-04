import web
from web import form
from htmltable import HtmlTable
from websession import WebInstanceManager

urls = ('/', 'Home',
        '/NewSession', 'NewSession',
        '/Admin', 'Admin')
render2 = web.template.render('template/', base='layout')

global WebSes
webInsMgr = WebInstanceManager(9000)

class Clean:
    def GET(self, session):
        try:
            webInsMgr.CleanUpSession(int(session))
            return 'cleanup successful for %s' %(session)
        except:
            return 'CleanUp: could not find session %s to clean %s' %(session)

class Update:
    def GET(self, session):
        try:
            webInsMgr.InstanceList[int(session)].UpdateAccessTime()
        except:
            return 'No Session Found'
        return 'Done'

class GetEpoch:
    def GET(self,session):
        try:
            if webInsMgr.InstanceList[int(session)].InstanceKeepAliveIns.Update():
                return 'passed'
            else:
                webInsMgr.CleanUpSession(self.session)
        except:
            return 'No Session Found'
            
class SetLongLoad:
    def GET(self,session):
        try:
            if not webInsMgr.InstanceList[int(session)].LongLoad == True:
                webInsMgr.InstanceList[int(session)].LongLoad = True
            else:
                webInsMgr.InstanceList[int(session)].LongLoad = False
            return 'Set LongLoad, session (%d)'%(int(session))
        except:
            return 'Set LongLoad, session (%d) not found'%(int(session))
        
class Admin:
    def GET(self):
        return render2.AdminBase(webInsMgr.GetAdminTableOutput())
    def POST(self):
        TableBase = HtmlTable(['Admin'])
        TableFreeSessionView = HtmlTable(['# Active Sessions', '# Available Sessions for New Connections'])
        SessCount = webInsMgr.GetCurrentCount()
        TableFreeSessionView.AddRow([SessCount,webInsMgr.MaxInstances - SessCount])
        TableManageSessions = HtmlTable(['Session Number', 'Last Active Time', 'Action'])
        TableManageServer = HtmlTable(['Restart Manager', 'Restart Server'])
        ManagerActionForm = form.Form(form.Button('RestartMan', type="submit", value='restart_man', id="submit"))
        ServerActionForm = form.Form(form.Button('RestartSer', type="submit", value='restart_ser', id="submit"))
        TableManageServer.AddRow([render2.Admin(ManagerActionForm), render2.Admin(ServerActionForm)])
        SessionTrack = {}
        
        to_clean = []
        
        for session in webInsMgr.InstanceList:
            ActionForm = form.Form(form.Button('kill: %d'%(session), value=session, id="submit"))
            SessionIns = ActionForm()
            SessionTrack[session] = SessionIns
            if SessionTrack[session].validates():
                for item in SessionTrack[session].d:
                    if not SessionTrack[session].d[item] == None:
                        to_clean.append(int(SessionTrack[session].d[item]))
                pass
            else:
                pass
        for clean_up_item in to_clean:
            webInsMgr.CleanUpSession(clean_up_item)
        for session in webInsMgr.InstanceList:                  
            TableManageSessions.AddRow([session, webInsMgr.InstanceList[session].LastAccessTime, render2.Admin(SessionTrack[session])])
            
            
        for Table in [TableFreeSessionView, TableManageSessions, TableManageServer]:
            TableBase.AddRow([Table])
            
        
        
        Manager = ManagerActionForm()
        Server = ServerActionForm()
        if not Manager.validates() or not Server.validates():
            return render2.AdminBase(TableBase.GetFormattedHtml())
        else:
            print (Manager.d)
            print (Server.d)
            
            for item in Manager.d:
                if not Manager.d[item] == None:
                    print ("Restart Manager called")
                    webInsMgr.RestartManager()
                    webInsMgr.CleanCache()
            for item in Server.d:
                if not Server.d[item] == None:
                    import os
                    os.system('echo place-holder for restart of ignition service')
                        
            TableBase = HtmlTable(['Admin'])
            TableFreeSessionView = HtmlTable(['# Active Sessions', '# Available Sessions for New Connections'])
            SessCount = webInsMgr.GetCurrentCount()
            TableFreeSessionView.AddRow([SessCount,webInsMgr.MaxInstances - SessCount])
            TableManageSessions = HtmlTable(['Session Number', 'Last Active Time', 'Action'])
            TableManageServer = HtmlTable(['Restart Manager', 'Restart Server'])
            ManagerActionForm = form.Form(form.Button('RestartMan', type="submit", value='restart_man', id="submit"))
            ServerActionForm = form.Form(form.Button('RestartSer', type="submit", value='restart_ser', id="submit"))
            TableManageServer.AddRow([render2.Admin(ManagerActionForm), render2.Admin(ServerActionForm)])
            SessionTrack = {}
            for session in webInsMgr.InstanceList:
                ActionForm = form.Form(form.Button('kill: %d'%(session), value=session, id="submit"))
                SessionIns = ActionForm()
                SessionTrack[session] = SessionIns
                TableManageSessions.AddRow([session, webInsMgr.InstanceList[session].LastAccessTime, render2.Admin(SessionTrack[session])])
            for Table in [TableFreeSessionView, TableManageSessions, TableManageServer]:
                TableBase.AddRow([Table])
            
            return render2.AdminBase(TableBase.GetFormattedHtml())



class Home:
    def GET(self):
        return render2.ig1(0, '')# Two buttons - Load Configuration / New configuration
    
class NewSession:
    def POST(self):
        session = webInsMgr.GetFreeSessionNumber()
        webInsMgr.AddIns(session)
        webInsMgr.InstanceList[int(session)].StartSession(['python', 'igchild.py', '%d'%(webInsMgr.InstanceList[int(session)].port)])
        return render2.ig1(1, int(webInsMgr.basePort)+int(session))

if __name__ == "__main__":
    app = web.application(urls,globals())
    app.run()
    
    
    
"""
ig1.html

$def with (mode,session)
	$if mode==0:
		<form action="http://10.216.35.20:$session/LoadConfig/$session">
			<input type="submit" value="Load Existing Configuration" id="submit"/>
		</form>
		<form action="http://10.216.35.20:$session/NewConfig/$session">
			<input type="submit" value="Start New Configuration" id="submit"/>
		</form>
"""