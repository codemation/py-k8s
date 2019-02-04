import web
from web import form
from htmltable import HtmlTable
from websession import WebInstanceManager
from configmgr import *
import configmgr
from appdatamgr import AppDataMgr


urls = ('/', 'index',
        '/LoadConfig/(.*)', 'LoadConfig',
        '/NewConfig/(.*)', 'NewConfig',
        '/ConfigMgr/(.*)','ConfigMgr',
        '/ConfigWiz/(.*)', 'ConfigWiz',
        '/AppMgr/(.*)', 'AppMgr',
        '/TimeWiz/(.*)', 'TimeWiz',
        '/FormMgr/(.*)', 'FormMgr',
        '/Admin', 'Admin')
render2 = web.template.render('template/', base='ig_layout')
renderNoLayOut = web.template.render('template/')

global WebSesCh
webInsMgr = WebInstanceManager(10000)


class index:
    def GET(self,session):
        return session

class AppMgr:
    def GET(self, session):
        print("appmgr must be created with ConfigMgr Ins with all loaded Config objects(each file)")
        appDataMgrIns = AppDataMgr(webInsMgr.InstanceList[int(session)].ConfigMgr)
        
        webInsMgr.InstanceList[int(session)].AppDataMgr = appDataMgrIns
        
        return render2.igConfigView(0, [appDataMgrIns.GetHtmlOut(session)], None, session)
    
    def POST(self, session):
        print("appmgr must be created with ConfigMgr Ins with all loaded Config objects(each file)")
        
        appDataMgrIns = AppDataMgr(webInsMgr.InstanceList[int(session)].ConfigMgr)
        return render2.igConfigView(0, [appDataMgrIns.GetHtmlOut(session)], None, session)
        
        
class FormMgr:
    def POST(self, session_module_returnForm):
        """
            module options are: ConfigMgr, TimeWiz, ConfigWiz
        """
        controls = session_module_returnForm.split(' ')
        session = str(controls[0])
        module = str(controls[1])
        returnForm = str(controls[2])
        print (controls)
        print (session)
        print (module)
        print (returnForm)
        
        
        if module == 'AppMgr':
            result = webInsMgr.InstanceList[int(session)].AppDataMgr.ProcessFormInputs(session, returnForm)
            if result[0] == 2:
                return result[1]
        
        if module == 'ConfigMgr':
            LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
            CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
            print ('igchild FormMgr curNavFile: %s'%(CurrentNavFile))
            FileToParseObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile]
            
            print ("igchild is calling ProcessFormInputs")
            print ("FileToParseDropDownList: %s"%(FileToParseObj.FormMgr.DropdownList))
            result = FileToParseObj.ProcessFormInputs(session,returnForm)
            if result[0] == 1:
                if 'select file' in result:
                    webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile = result[2]
                    CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
                if 'Add New File' in result:
                    webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].AddFileToParse(result[2])
                    webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile = result[2]
                    CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
                if 'Save Config' in result:
                    webInsMgr.InstanceList[int(session)].ConfigMgr.SaveConfig(LoadedFile)
                ConfigHtml  = []
                FilesToParse = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']
                nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].GetNavPane(session,FilesToParse,CurrentNavFile)        
                ConfigHtml.append(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].GetConfigHtmlView(session))
                return render2.igConfigView(0,ConfigHtml,nav, session)


            if result[0] == 2:
                return result[1]
        if module == 'TimeWiz':
            result = webInsMgr.InstanceList[int(session)].TimeConfigWiz.ProcessFormInputs(session, returnForm)
            if result[0] == 2:            
                return result[1]
        if 'ConfigWiz' in session_module_returnForm:
            if '-' in session:
                controls = session_module_returnForm.split(' ')
                session = str(controls[0][0])
                module = 'ConfigWiz'
                returnForm = str(controls[-1])
                if module == 'ConfigWiz':
                    result = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.ProcessFormInputs(session, returnForm)
                    if result[0] == 2:            
                        return result[1]
                    if result[0] == 1:
                        pass
                        
            else:
                result = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.ProcessFormInputs(session, returnForm)
                if result[0] == 2:          
                    return result[1]
                if result[0] == 3: # New instance of  DataPointConfigWiz requested for different/ new Pattern
                    print("New instance of  DataPointConfigWiz requested for different/ new Pattern")
                    LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
                    CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
                    name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                    location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                    sessionAndPattern = session + '-' + str(result[2])
                    if result[1] == 'change':
                        print ("change requested")
                        PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][str(result[2])]
                        webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
                        patternList = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetPatternList()
                        nav = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetNavPane(session,patternList)
                        HtmlOut = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(session)
                        return renderNoLayOut.igConfigWiz(0,HtmlOut,sessionAndPattern, nav)
                    if result[1] == 'new':
                        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].AddDataPattern(result[2], None, None)
                        PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][result[2]]
                        webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
                        
                        patternList = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetPatternList()
                        nav = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetNavPane(session,patternList)
                        HtmlOut = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(session)
                        return renderNoLayOut.igConfigWiz(0,HtmlOut,sessionAndPattern, nav)

class ConfigMgr:
    def POST(self, session):
        LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        
        """
        result = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].ProcessFormInputs(session)
        
        if result is not None:
                if result[0] == 1:
                    ###
                        #redirect required
                    ###
                    if 'config wiz' in result:
                        webInsMgr.InstanceList[int(session)].DataPointConfigWiz = result[3]
                        sessionAndPattern = session + '-%s'%(result[2])
                        HtmlOut = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(sessionAndPattern)
                        #nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetDataPointConfigWizNavPane(str(result[2]), session)
                        patternList = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetPatternList()
                        nav = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetNavPane(session,patternList)
                        return render2.igConfigWiz(0,HtmlOut,sessionAndPattern, nav)
                    if 'Data__Time__configwiz' in result:
                        webInsMgr.InstanceList[int(session)].TimeConfigWiz = result[2]
                        HtmlOut = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetHtmlOut(session)
                        nav = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetNavPane(session)
                        return render2.ig_timeWiz(0,HtmlOut,session, nav)
                    if 'select file' in result:
                        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile = result[2]
                        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
                    if 'Add New File' in result:
                        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].AddFileToParse(result[2])
                        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile = result[2]
                        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
                    if 'Save Config' in result:
                        webInsMgr.InstanceList[int(session)].ConfigMgr.SaveConfig(LoadedFile)
        """
                        
                
        ConfigHtml  = []
        FilesToParse = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']
        nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].GetNavPane(session,FilesToParse,CurrentNavFile)        
        ConfigHtml.append(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].GetConfigHtmlView(session))
        return render2.igConfigView(0,ConfigHtml,nav, session)
            
class TimeWiz:
    def GET(self, session):
        LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
        location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
        timeConfig = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['Time']
        webInsMgr.InstanceList[int(session)].TimeConfigWiz = TimeConfigWiz(timeConfig, location+name)
        HtmlOut = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetHtmlOut(session)
        nav = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetNavPane(session)
        return render2.ig_timeWiz(0,HtmlOut,session, nav)
        
    def POST(self, session):
        
        try:        
            webInsMgr.InstanceList[int(session)].TimeConfigWiz.ProcessFormInputs(session)     
            HtmlOut = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetHtmlOut(session)
            nav = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetNavPane(session)
            return render2.ig_timeWiz(0,HtmlOut,session, nav)
        except:
            LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
            CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
            name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
            location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
            timeConfig = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['Time']
            webInsMgr.InstanceList[int(session)].TimeConfigWiz = TimeConfigWiz(timeConfig, location+name)
            HtmlOut = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetHtmlOut(session)
            nav = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetNavPane(session)
            return render2.ig_timeWiz(0,HtmlOut,session, nav)
             
    
class ConfigWiz: # /ConfigMgr/ConfigWiz/0-megastorestats
    def GET(self, sessionAndPattern):
        Splitter = sessionAndPattern.split('-')
        session = Splitter[0]
        
        LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        Pattern = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][Splitter[1]]
        print (CurrentNavFile)
        print (webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location)
        name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
        location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
        webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(Pattern, location+name)
        
        HtmlOut = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(sessionAndPattern)
        patternList = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetPatternList()
        nav = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetNavPane(patternList)
        #nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetDataPointConfigWizNavPane(str(Pattern), session)
        
        return render2.igConfigWiz(0,HtmlOut,sessionAndPattern, nav)
        
    def POST(self, sessionAndPattern):
        Splitter = sessionAndPattern.split('-')
        session = Splitter[0]
        Pattern = Splitter[1]
        LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        
        try:
            if webInsMgr.InstanceList[int(session)].DataPointConfigWiz.DataPatternObj.name == Pattern:
                pass
            else:
                name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][Splitter[1]]
                webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
        except:
            name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
            location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
            PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][Splitter[1]]
            webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
        
        """                
        result = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.ProcessFormInputs(session)
        if result is not None:
            if 'Switch To Data Pattern' in result:
                name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][result[2]]
                webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
            if 'Add New Data Pattern' in result:
                webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].AddDataPattern(result[2], None, None)
                name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][result[2]]
                webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)               
        """
        #nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetDataPointConfigWizNavPane(Pattern, session)
        patternList = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].GetPatternList()
        nav = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetNavPane(session,patternList)
        HtmlOut = webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(sessionAndPattern)
        return render2.igConfigWiz(0,HtmlOut,sessionAndPattern, nav)

class LoadConfig:
    def GET(self, session):
        print ("LoadConfig Session:%s"%(session))
        webInsMgr.AddIns(int(session))
        webInsMgr.InstanceList[int(session)].ConfigMgr = configmgr.ConfigMgr() # Intializeds ConfigMgr within Instance
        #print ("Load Config: %s" %(webInsMgr.InstanceList[int(session)].ConfigMgr.GetConfigFileList()))
        #FileListDict =  
        print ()
        
        FileChoiceFormTable = HtmlTable(['Available Config Files'])
        FileChoiceFormTableSub = HtmlTable(['', 'Config File'])
        fpstring = 'LoadConfig/%s' %(session)
        print ("Fpstring %s" %(fpstring))
        GetConfigFileDict = webInsMgr.InstanceList[int(session)].ConfigMgr.GetConfigFileList()
        for fileIndex in GetConfigFileDict:
            temp_Form = form.Form(form.Button('Load',type="submit" ,value=fileIndex, target=fpstring, id="submit"))
            FileChoiceFormTableSub.AddRow([temp_Form.render(), '%s' %(GetConfigFileDict[fileIndex])])
        
        FileChoiceFormTable.AddRow([FileChoiceFormTableSub])
        
        webInsMgr.InstanceList[int(session)].UpdateAccessTime()
        
        
        return render2.LoadExisting(0,FileChoiceFormTable.GetFormattedHtml(),session)
    def POST(self, session):
        fpstring = 'LoadConfig/%s' %(session)
        print ("POST LoadConfig session: %s" %(session))
        CfgChoice = form.Form(form.Button("Load", type="submit", value="Select File", target=fpstring, id="submit"))
        CfgChoiceIns = CfgChoice()
        
        if not CfgChoiceIns.validates():
            return "session %s inputfailed"
        else:
            
            print ("File Input: session %s - input %s" %(str(session), int(CfgChoiceIns.d['Load'])))
            LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadConfig(int(CfgChoiceIns.d['Load']))
            
            ConfigHtml = []
            filesToParse = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']
            curNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
            for fileToParse in webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']:
                if fileToParse == webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile: 
                    ConfigHtml.append(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][fileToParse].GetConfigHtmlView(session))
            #print ("Files to parse %s "%(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']))
            nav = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][fileToParse].GetNavPane(session,filesToParse,curNavFile)
            
            return render2.igConfigView(0,ConfigHtml,nav, session)
    
class NewConfig:
    def GET(self, session):
        return 'Newconfig %s active' %(session)
    def POST(self, session):
        return


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

if __name__ == "__main__":
    app = web.application(urls,globals())
    app.run()
    