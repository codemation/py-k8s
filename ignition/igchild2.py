"""
    igchild2
"""
from web import application,input
from websession import WebInstanceManager
from configmgr2 import *
import configmgr2 as configmgr
from appdatamgr import AppDataMgr
from htmlpage import page
from htmlform import form,row,col,dropdown,button,container,text,header,rowOfCol,select,table,tr,textbox,navbar

urls = ('/', 'index',
        '/LoadConfig/(.*)', 'LoadConfig',
        '/NewConfig/(.*)', 'NewConfig',
        '/ConfigMgr/(.*)','ConfigMgr',
        '/ConfigWiz/(.*)', 'ConfigWiz',
        '/AppMgr/(.*)', 'AppMgr',
        '/TimeWiz/(.*)', 'TimeWiz',
        '/FormMgr/(.*)', 'FormMgr',
        '/Admin', 'Admin')
"""
    initializes Instance manager for variable control.
"""
webInsMgr = WebInstanceManager(10000)

#Step 1 - Load config #
global LoadConfigPg
LoadConfigPg = page("Loadconfig")
#LoadConfigPg.head.add_script('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>')
#LoadConfigPg.head.add_script('<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"></script>')
#LoadConfigPg.head.add_script('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>')
#LoadConfigPg.head.add_link('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">')
#LoadConfigPg.save()
global render
render = LoadConfigPg.htmlrender
from web import input as webinput

class FormMgr:
    def getinput(self):
        d = {}
        for k,v in webinput().items():
            if not v in [u'', None, '']:
                d[k] = v
        return d
    def getLoaded(self, ses_mod_retForm):
        session, module, retForm = ses_mod_retForm.split(' ')
        postInput = self.getinput()
        LoadedFile = webInsMgr.InstanceList[int(session)].LoadedFile
        curNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        return session, module, retForm, postInput, LoadedFile, curNavFile
    
    def get_process_mod(self, session, retForm,postInput, inMod, **kw):
        extra = kw['extra'] if 'extra' in kw else []
        extraF = []
        for f in extra:
            if f in inMod.__dict__:
                extraF.append(inMod.__dict__[f])
                
        def getinput():
            d = {}
            for k,v in webinput().items():
                if not v in [u'', None, '']:
                    d[k] = v
            return d
        def process_mod():
            postInput = getinput
            extraFuncs = extraF
            inp = postInput()
            inMod.setWebInput(inp)
            for k,v in inp.items():
                try:
                    vInt = int(v)
                except:
                    vInt = None
                    pass
                if v in inMod.idstr or vInt in inMod.idstr:
                    v = vInt if not v in inMod.idstr else v
                    print ("v = '%s' in postInput: "%(v))
                    inMod.idstr[v]()
                    inMod.html(session)
                    for f in extraFuncs:
                        f()
                    return '\n'.join(inMod.idstr[retForm]())
            else:
                return '\n'.join(inMod.idstr[retForm]())
        return process_mod
    def process_input(self,ses_mod_retForm):
        session, module, retForm, postInput, LoadedFile, curNavFile = self.getLoaded(ses_mod_retForm)
        if module == 'ConfigMgr':
            return self.get_process_mod(session, retForm, postInput, 
                                        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile])()
        if module == 'TimeWiz':
            return self.get_process_mod(session, retForm, postInput, 
                                        webInsMgr.InstanceList[int(session)].TimeConfigWiz,
                                        extra=['updateTimeConfig'])()
    """
    def process_TimeWiz(self, ses_mod_retForm):
        self.process_input(ses_mod_retForm)
        webInsMgr.InstanceList[int(session)].TimeConfigWiz.setWebInput(postInput)
        
        
        
        webInsMgr.InstanceList[int(session)].updateTimeConfig()

    def process_ConfigMgr(self, ses_mod_retForm):
        session, module, retForm, postInput, LoadedFile, curNavFile = self.getLoaded(ses_mod_retForm)
        file = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile]
        print (file.Data['Time'])
        webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile].setWebInput(postInput)
        for k,v in postInput.items():
            v = u'%s'%(v)
            if v in file.idstr:
                print (v)
                webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile].idstr[v]()
                webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile].GetConfigHtmlView(session)
                return '\n'.join(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile].idstr[retForm]())
        else:
            return '\n'.join(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][curNavFile].idstr[retForm]())
        """
    def POST(self, ses_mod_retForm):
        print ("Input session_module_returnForm: %s"%(ses_mod_retForm))
        print ("webinput: %s"%(webinput()))
        return self.process_input(ses_mod_retForm)
        

class TimeWiz:
    def setAndUpdateTimeconfig(self, session):
        def updateTimeConfig():
            LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
            CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
            if 'TimeConfigWiz' in webInsMgr.InstanceList[int(session)].__dict__:
                webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['Time'] = webInsMgr.InstanceList[int(session)].TimeConfigWiz.TimeConfig
            else:
                print ("TimeConfigWiz not found in session, creating.")
                name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                timeConfig = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['Time']
                webInsMgr.InstanceList[int(session)].TimeConfigWiz = TimeConfigWiz(timeConfig, location+name)
        updateTimeConfig()
        webInsMgr.InstanceList[int(session)].TimeConfigWiz.updateTimeConfig = updateTimeConfig
            
    def POST(self, session):
        self.setAndUpdateTimeconfig(session)
        HtmlOut = webInsMgr.InstanceList[int(session)].TimeConfigWiz.html(session)
        #nav = webInsMgr.InstanceList[int(session)].TimeConfigWiz.GetNavPane(session)
        return render(HtmlOut)

        
        
        
class ConfigWiz:
    def POST(self, session_Pattern):
        Splitter = session_Pattern.split('-')
        session = Splitter[0]
        pattern = Splitter[1]
        LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadedFile
        CurrentNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
        try:
            if webInsMgr.InstanceList[int(session)].DataPointConfigWiz.DataPatternObj.name == pattern:
                pass
            else:
                name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
                location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
                PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][pattern]
                webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
        except:
            name = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].name
            location = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Location
            PatternObj = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].Data['DataPattern'][pattern]
            webInsMgr.InstanceList[int(session)].DataPointConfigWiz = DataPointConfigWiz(PatternObj, location+name)
        return webInsMgr.InstanceList[int(session)].DataPointConfigWiz.GetHtmlOut(session)
            
        
class LoadConfig:
    def GET(self, session):
        # Add Session
        webInsMgr.AddIns(int(session))
        # Create Config Manager
        webInsMgr.InstanceList[int(session)].ConfigMgr = configmgr.ConfigMgr()
        choices = webInsMgr.InstanceList[int(session)].ConfigMgr.GetConfigFileList()
        choiceList = []
        ind = 0
        for cfgId in choices:
            choiceList.append(button("{%s}"%(choices[cfgId]), name="LoadFile", value="%s-%s"%(cfgId,choices[cfgId]), id="%s-id-%d"%(choices[cfgId],ind)))
            ind+=1
        chDrpdwn = dropdown("Load Configurations", id="LoadConfigurations", items=choiceList)
        
        choiceForm = form("LoadForm", items=[row(items=[chDrpdwn], align="center")], options=['target="LoadConfig/%s"'%(session), 'method="POST"'])
        print (LoadConfigPg.head.scripts)
        return render(container(items=[choiceForm]))
    def getinput(self):
        d = {}
        for k,v in webinput().items():
            if not v in [u'', None, '']:
                d[k] = v
        return d
            
            
    def POST(self, session):
        postInput = self.getinput()
        if 'LoadFile' in postInput:
            fileToLoad = int(postInput['LoadFile'].split('-')[0])
            webInsMgr.InstanceList[int(session)].LoadedFile = webInsMgr.InstanceList[int(session)].ConfigMgr.LoadConfig(fileToLoad)
            LoadedFile = webInsMgr.InstanceList[int(session)].LoadedFile
            filesToParse = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse']
            curNavFile = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile
            file = None
            for f in filesToParse:
                if f == webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].CurrentNavFile:
                    file = f
        print ("findFilePatterns: - %s"%(webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][file].findFilePatterns))
        getConfigView = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][file].html(session)
        getconfigNav  = webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][file].GetNavPane(session, filesToParse)
        root = container(items=[row(items=[getconfigNav]), getConfigView])
        return render(root)
        
        

if __name__ == "__main__":
    app = application(urls,globals())
    app.run()
        
