import json
from htmltable import HtmlTable
import chunker
from formsmanager import FormMgr

class FileToParse(object):
    """
    Base Object for adding files to parse in config
    """
    def __init__(self, name):
        self.name = name
        self.Location = None
        self.FileExample = {}
        self.findFilePatterns = {} # List of Dicts normal = not zipped, zip zipped, {'normal': 'rfsctl-a.log'} || {'zip': 'rfsctl-a.log.*.gz'}  }
        self.findFilePatternsCount = 0
        self.Data = {'Time': {
                         'inLine': None,
                         'TimeStrUnset': True    
                        },
                    'DataPattern': {
                        }
                    }
        self.FileExampleUnconfirmed = {}
        self.FindFilePatternIsGood = False
        self.ToDoList = []
        self.FormMgr = FormMgr()
    def GetNavPane(self,session, FilesToParse, current):
        FileList = []
        """
            input should be self.runningConfig['Tool']['FilesToParse']
            current should be the CurrentNavFile of the config
        """
        for file in FilesToParse:
            FileList.append({file: file})
        navPane = self.FormMgr.GetHtmlTable(["Navigation"], 'nav_ConfMgr')
        
        ChangeFileTb = self.FormMgr.GetHtmlTable([self.FormMgr.GetDropdown(session, "navCurrentFile", FileList, current)], 'nav_ConfMgr_changeFile', 'ConfigMgr')
        ChangeFileTb.AddRow([self.FormMgr.GetButton(session, "View Selected File Config",'nav_ConfMgr_changeFile', 'body', "navCurrentFile")])
        
        
        
        navPane.AddRow([ChangeFileTb])
        FileTestLocationTb = self.FormMgr.GetHtmlTable(["File Test Location"], 'nav_ConfMgr_changeTestLoc', 'ConfigMgr')
        FileTestLocationTb.AddRow([self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, "File Test Location", self.Location), 
                                                              self.FormMgr.GetButton(session, "modify", 'nav_ConfMgr_changeTestLoc', 'nav_ConfMgr_changeTestLoc', "File Test Location")
                                                              ])
                                ])
        navPane.AddRow([FileTestLocationTb])
                        
        NewFileTb = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, "New File Name", None)], 'nav_ConfMgr_newFile', 'ConfigMgr')
        NewFileTb.AddRow([self.FormMgr.GetButton(session, "Add New File",'nav_ConfMgr_newFile', 'body', "New File Name")])
        navPane.AddRow([NewFileTb])
                        
        NewPatternTb = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, "New Pattern Name", None)], 'nav_ConfMgr_newPattern', 'ConfigMgr')
        NewPatternTb.AddRow([self.FormMgr.GetButton(session, "Add New Data Pattern", 'nav_ConfMgr_newPattern', 'DataPattern_base', "New Pattern Name")])
        navPane.AddRow([NewPatternTb])

        SaveConfigTb = self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, "Save Changes", 'nav_ConfMgr_saveConfig', 'nav_ConfMgr_saveConfig', "Save Config")], 'nav_ConfMgr_saveConfig', 'ConfigMgr')
        navPane.AddRow([SaveConfigTb])
        
        
        return navPane.GetFormattedHtml()
        
    def ProcessFormInputs(self, session, returnForm=None):
        print ("")
        forms = self.FormMgr.GetFormInputs()
        print ("FileToParse.ProcessFormInputs forms: %s" %(forms))
        for DataPattern in self.Data['DataPattern']:
            result = self.Data['DataPattern'][DataPattern].ProcessFormInputs(session,returnForm)
            if result is not None:
                if result[0] == 1:
                    """
                        redirect required
                    """
                    if 'config wiz' in result:
                        print ("Existing for redirect for config wiz on %s"%(result[2]['name']))
                        return (1, 'config wiz', result[2]['name'], DataPointConfigWiz(result[2]['PatternObj'], str(self.Location)+ str(self.name)))
                elif result[0] == 2:
                    """
                        AJAX Request, returning relevant html for portion of modified page
                    """
                    return (2,result[1])
            else:
                pass
                    
        if 'add' in forms['ButonList'] and forms['ButonList']['add'] is not None:
            if 'findFilePatterns' in forms['ButonList']['add']:
                print ("Adding a new way to find file")
                #webInsMgr.InstanceList[int(session)].ConfigMgr.configDict[LoadedFile].runningConfig['Tool']['FilesToParse'][CurrentNavFile].AddFindFilePattern()
                self.AddFindFilePattern({'pattern': forms['textBoxes']['findFilePatterns__new__pattern'], 'type': forms['DropdList']['findFilePatterns__new__type']})
        if 'test' in forms['ButonList']:
            if forms['ButonList']['test'] is not None:
                item = forms['ButonList']['test']
                print ("Must test on %s" %(item))
        if 'del' in forms['ButonList'] and forms['ButonList']['del'] is not None:
            item = forms['ButonList']['del']
            if 'DataPattern' in item and not 'tag' in item:
                #Deleting a Data Pattern:
                SplitItem = item.split('__')
                self.RemDataPattern(SplitItem[2])
            elif 'findFilePatterns' in item:
                SplitItem = item.split('__')
                self.RemFindFilePattern(SplitItem[1])
        """
            nav bar options
        """
        if 'View Selected File Config' in forms['ButonList'] and forms['ButonList']['View Selected File Config'] is not None:
            print ("View Selected File Config called, returning 1, %s"%(forms['ButonList']))
            return (1, 'select file', forms['DropdList'][forms['ButonList']['View Selected File Config']])
        if 'Add New File' in forms['ButonList'] and forms['ButonList']['Add New File'] is not None:
            return (1, 'Add New File', forms['textBoxes'][forms['ButonList']['Add New File']])
        if 'Add New Data Pattern' in forms['ButonList'] and forms['ButonList']['Add New Data Pattern'] is not None:
            self.AddDataPattern(forms['textBoxes'][forms['ButonList']['Add New Data Pattern']], None, None)
        if "Save Changes" in forms['ButonList'] and forms['ButonList']['Save Changes'] is not None:
            return (1, 'Save Config')
        if 'modify' in forms['ButonList'] and forms['ButonList']['modify'] is not None:
            self.Location = forms['textBoxes'][forms['ButonList']['modify']]
            
        if returnForm is not None:
            if returnForm in self.FormMgr.divGetHtml:
                self.GetConfigHtmlView(session)
                if returnForm == 'body':
                    self.GetConfigHtmlView(session)
                    return (1, self.FormMgr.divGetHtml[returnForm]())
                return (2, self.FormMgr.divGetHtml[returnForm]())
                    
        
    def GetConfigHtmlView(self,session):
                
        BaseTable = self.FormMgr.GetHtmlTable([self.name], 'body')
        FindFilePattern = self.FormMgr.GetHtmlTable(['File Search Patterns'], 'fsPatterns')
        searchPatternDivId = 'ConfMgr_fileSearchPatternTb'
        FindFilePattern.SetHide(searchPatternDivId)
        FindFilePatternSub = self.FormMgr.GetHtmlTable(['Type','Pattern', 'action'], searchPatternDivId, 'ConfigMgr')
        FindFilePatternSub.IsHidden=True
        for findFileItem in self.findFilePatterns:
            searchPatternActionDivId = 'ConfMgr_searchPattern_%s_ActionTb'%(findFileItem)
            FindFilePatternSub.AddRow([ self.findFilePatterns[findFileItem]['type'],
                                        self.findFilePatterns[findFileItem]['pattern'], 
                                        self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'test',searchPatternActionDivId, searchPatternActionDivId, 'findFilePatterns__%s__test'%(findFileItem)), 
                                                                   self.FormMgr.GetButton(session,'del', searchPatternActionDivId, searchPatternDivId,  'findFilePatterns__%s__del'%(findFileItem))], 
                                                                    searchPatternActionDivId, 'ConfigMgr')
                                    ])
        FindFilePatternSub.AddRow([self.FormMgr.GetHtmlTable([ self.FormMgr.GetDropdown(session, 'findFilePatterns__new__type', ['zip', 'normal'], 'normal'), 
                                                               self.FormMgr.GetTextBox(session,'findFilePatterns__new__pattern', ''), 
                                                               self.FormMgr.GetButton(session,'add', 'ConfMgr_newfileSearchPatternTb', searchPatternDivId, 'findFilePatterns__new__add')
                                                           ], 'ConfMgr_newfileSearchPatternTb', 'ConfigMgr')
                                ])
        FindFilePattern.AddRow([FindFilePatternSub])
        """
        FileExample = self.FormMgr.GetHtmlTable(['File Example found using pattern'])
        for fExamp in self.FileExample:
            FileExample.AddRow([fExamp])
        """
        DataB_Time = self.FormMgr.GetHtmlTable(['Time Configuration'], 'timeCfgRoot')
        
        DataB = self.FormMgr.GetHtmlTable([DataB_Time])
        timeInLineDivId = 'ConfMgr_timeInlineTb'
        
        
        DataB_TimeSub = self.FormMgr.GetHtmlTable(['Parameter', 'Value', 'action'], timeInLineDivId, 'ConfigMgr')
        DataB_TimeSub.AddRow(['Time inLine', 
                              self.FormMgr.GetHtmlTable([self.FormMgr.GetDropdown(session,'Data__Time__inLine', [True,False],self.Data['Time']['inLine']),
                                                         self.FormMgr.GetButton(session,'set', 'Data__Time__configwiz', timeInLineDivId, 'Data__Time__inLine__set')], 'Data__Time__configwiz'),
                                         self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'config wiz', None, None, 'Data__Time__configwiz')], None, '/TimeWiz/%s'%(session), 'POST', False)])
        DataB_Time.AddRow([DataB_TimeSub])

        if not 'pattern' in self.Data['Time']:
            self.Data['Time']['pattern'] = {}
        if self.Data['Time']['pattern'] == {}:
            self.Data['Time']['pattern'] = {'inLine': {'Mo': None, 'Dy': None, 'H': None, 'M': None}}
        #print ("TODOO - Add inline = True Table")
        DataB_TimeSubPattern = self.FormMgr.GetHtmlTable(['Time Config'])
        timeConfigParamTb = 'ConfMgr_timeCfgParamTb'
        DataB_Time.SetHide(timeConfigParamTb)
        DataB_TimeSubPatternSub = self.FormMgr.GetHtmlTable(['param', 'splitConfig', 'action'], timeConfigParamTb, 'ConfigMgr')
        DataB_TimeSubPatternSub.IsHidden=True
        for patternT in self.Data['Time']['pattern']:
             #print ("PatternT: %s" %(patternT))
             timePtrn = self.Data['Time']['pattern'][patternT]
             """
             DataB_TimeSubPatternSub.AddRow(['Yr', self.FormMgr.GetTextBox(session,'Data__Time__pattern__%s__Yr'%(patternT),
                                            self.Data['Time']['pattern'][patternT]['Yr']),
                                            self.FormMgr.GetButton(session,'test', 'Data__Time__pattern__Yr__test')])
             """
             DataB_TimeSubPatternSub.AddRow(['Mon', timePtrn['Mo'],
                                            self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'test','timeCfg_Mo_test', 'timeCfg_Mo_test', 'Data__Time__pattern__Mo__test')], 'timeCfg_Mo_test', 'ConfigMgr')
                                            ])
             DataB_TimeSubPatternSub.AddRow(['Day', timePtrn['Dy'],
                                            self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'test', 'timeCfg_Mo_test', 'timeCfg_Mo_test', 'Data__Time__pattern__Dy__test')], 'timeCfg_Dy_test', 'ConfigMgr')
                                            ])
             DataB_TimeSubPatternSub.AddRow(['Hour', timePtrn['H'],
                                            self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'test', 'timeCfg_H_test', 'timeCfg_H_test', 'Data__Time__pattern__H__test')], 'timeCfg_H_test', 'ConfigMgr')
                                            ])
             DataB_TimeSubPatternSub.AddRow(['Min', timePtrn['M'],
                                            self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session,'test', 'timeCfg_M_test', 'timeCfg_M_test', 'Data__Time__pattern__M__test')], 'timeCfg_M_test', 'ConfigMgr')
                                            ])
             DataB_TimeSubPattern.AddRow([patternT, DataB_TimeSubPatternSub])
             DataB_TimeSubPattern.AddRow([DataB_TimeSubPatternSub])
             DataB_Time.AddRow([DataB_TimeSubPattern])
        
        CfgMgrDpBaseTb = 'DataPattern_base'
        DataB_DataPattern = self.FormMgr.GetHtmlTable(['Pattern', 'Configuration'], CfgMgrDpBaseTb,'ConfigMgr')
        
        for DataPattern in self.Data['DataPattern']:
            #print (DataPattern)
            cfgMgrDpTb = 'dp_%s_tb'%(DataPattern)
            DataPatternTb = self.FormMgr.GetHtmlTable([DataPattern,
                                                 self.FormMgr.GetButton(session,'del',cfgMgrDpTb, CfgMgrDpBaseTb, 'Data__DataPattern__%s__del' %(DataPattern))], cfgMgrDpTb, 'ConfigMgr')
            DataPatternTb.SetHide('dataPattern_'+DataPattern+'_tb')
            DataB_DataPattern.AddRow([DataPatternTb, self.Data['DataPattern'][DataPattern].GetHtmlOut(session)])
            
        DataB.AddRow([DataB_DataPattern])

        BaseTable.AddRow([FindFilePattern])
        BaseTable.AddRow([DataB])
        
        return BaseTable.GetFormattedHtml()
        
    def GetDataPatternForExport(self):
        dataPatternDict = {}
        for Pattern in self.Data['DataPattern']:
            dataPatternDict[str(Pattern)] = self.Data['DataPattern'][str(Pattern)].GetConfigForExport()
        return dataPatternDict
            
    def GetConfigForExport(self):
        return {
                    'findFilePatterns': self.findFilePatterns,
                    'FileExample': self.FileExample,
                    'Data': {'DataPattern': self.GetDataPatternForExport(),
                            'Time': self.Data['Time'],
                            'Location': self.Location
                            }
                }
            
    def LoadConfig(self, config):
        print ("input Config: %s" %(config))
        try:
            self.findFilePatterns = config['findFilePatterns']
            for findFilePatternIndex in self.findFilePatterns:
                self.findFilePatternsCount+=1
        except:
            print ("Error while loading findFilePatterns, review ")
        try:
            self.Location = config['Data']['Location']
        except:
            print ("Error while loading Location, review ")
        try:
            self.FileExample = config['FileExample']
        except:
            print ("Error while loading FileExample, review ")
        self.Data['Time'] = config['Data']['Time']
        for PatternItems in config['Data']['DataPattern']:
            self.Data['DataPattern'][PatternItems]  = DataPattern(PatternItems)
            for TagId in config['Data']['DataPattern'][PatternItems]['tag']:
                self.Data['DataPattern'][PatternItems].AddTag(TagId)
                if 'dataPoints' in config['Data']['DataPattern'][PatternItems]['tag'][TagId]:
                    for DataPoint in config['Data']['DataPattern'][PatternItems]['tag'][TagId]['dataPoints']:
                        self.Data['DataPattern'][PatternItems].AddDataPoint(TagId,DataPoint)
                        self.Data['DataPattern'][PatternItems].pattern['tag'][TagId]['dataPoints'][str(DataPoint)] = config['Data']['DataPattern'][PatternItems]['tag'][TagId]['dataPoints'][DataPoint]
            if 'dataPointTags' in config['Data']['DataPattern'][PatternItems]:
                for ParentDataPoint in config['Data']['DataPattern'][PatternItems]['dataPointTags']:
                    if 'childDataPoints' in config['Data']['DataPattern'][PatternItems]['tag'][TagId]:
                        for ParentDataPoint in config['Data']['DataPattern'][PatternItems]['tag'][TagId]['childDataPoints']:
                            self.Data['DataPattern'][PatternItems].dataPointTags[ParentDataPoint] = TagId
                            for childDataPoint in config['Data']['DataPattern'][PatternItems]['tag'][TagId]['childDataPoints'][ParentDataPoint]['ids']:
                                self.Data['DataPattern'][PatternItems].AddDataPointTag(TagId, ParentDataPoint, childDataPoint)
                                self.Data['DataPattern'][PatternItems].pattern['tag'][TagId]['childDataPoints'][ParentDataPoint]['ids'][str(childDataPoint)] = config['Data']['DataPattern'][PatternItems]['tag'][TagId]['childDataPoints'][ParentDataPoint]['ids'][childDataPoint]
                        
            print ("LoadConfig Tag completed: %s" %(self.Data['DataPattern'][PatternItems].pattern))

    def TestFileFindPattern(self, ToTestPattern):
        if not self.Location == None:
            results = []
            import os
            os.system('mkdir config/testing_area')           
            print ("TestFileFindPattern input pattern: %s" %(ToTestPattern))
            os.system('rm -rf config/testing_area/%s_discovery_test' %(self.name))
            os.system('echo "find %s -name %s" >> config/testing_area/%s_discovery_test'%(self.Location, ToTestPattern, self.name))
            os.system('find %s -name %s >> config/testing_area/%s_discovery_test'%(self.Location, ToTestPattern, self.name))
            with open('config/testing_area/%s_discovery_test' %(self.name), 'r') as findResults:
                ##TOODOO
                for line in findResults:
                    if 'find' in line:
                        continue
                    if not line in self.FileExampleUnconfirmed:
                        self.FileExampleUnconfirmed[line.rstrip()] = self.findFilePatterns[ToTestPattern]
                    results.append((line.rstrip(),self.findFilePatterns[ToTestPattern]))
            return results
        else:
            return 'Location Not Set'
    def ConfirmFindFilePattern(self):
        try:
            for EachPattern in self.findFilePatterns:            
                self.TestFileFindPattern(self.findFilePatterns[EachPattern]['pattern'])
            self.FindFilePatternIsGood = True
            #Add File Example for use in testing other patterns i.e Time.
            if self.FindFilePatternIsGood == True:
                for line in self.FileExampleUnconfirmed:
                    self.FileExample[self.FileExampleUnconfirmed[line]] = line.rstrip()
                    break
        except:
            self.FindFilePatternIsGood = False
        return self.FindFilePatternIsGood
            
    def AddFindFilePattern(self, toAddPattern):
        """toAddPattern Input should be formatted as the following: {"pattern": "message", "type": "normal"} """
        self.findFilePatternsCount+=1
        if type(toAddPattern) == dict:
            self.findFilePatterns[str(self.findFilePatternsCount)] = toAddPattern
            return 'AddFindFilePattern: Passed'
        else:
            return 'Inpput type(%s): Input Pattern should be in a dictionary format {"type[normal|zip]": "pattern"}'%(type(toAddPattern))
    def RemFindFilePattern(self, countToDelPattern):
        self.findFilePatternsCount-=1
        del self.findFilePatterns[str(countToDelPattern)]
        return 'AddFindFilePattern: Passed'
    def AddDataPattern(self, pattern, tag, splitConfig):
        if not pattern == None:
            self.Data['DataPattern'][pattern] = DataPattern(pattern)
    def RemDataPattern(self, pattern):
        if not pattern == None:
            del self.Data['DataPattern'][pattern]
    def SetDataTime(self, IsInLine, pattern):
        if self.Data['Time']['inLine'] == None:
            if IsInLine == True:
                self.Data['Time']['inLine'] = True
                return 'Passed'
            else:
                if pattern is not None:                    
                    self.Data['Time']['pattern'] = pattern
                    self.Data['Time']['inLine'] = False
                    self.Data['Time']['Yr'] = ['unconfigured']
                    self.Data['Time']['Mo'] = ['unconfigured']
                    self.Data['Time']['Dy'] = ['unconfigured']
                    self.Data['Time']['H'] =  ['unconfigured']
                    self.Data['Time']['M'] =  ['unconfigured']
                    self.ToDoList.append(self.Data['Time'])
                    return 'Passed'
                else:
                    return 'PatternNotSet'
        else:
            return 'Time Already Set'
    
    def TestDataTimePattern(self, pattern):
        results = []
        if 'pattern' in self.Data['Time']:
            if self.Data['Time']['pattern'] is not None:
                if self.ConfirmFindFilePattern() == True:
                    import os
                    os.system('rm -rf config/testing_area/%s_time_pattern_test' %(self.name))
                    os.system('echo "TimeTest string: %s" >> config/testing_area/%s_time_pattern_test'%(self.Data['Time']['pattern'], self.name))
                    with open('config/testing_area/%s_time_pattern_test'%(self.name), 'a') as timePattern:
                        for typeF in self.FileExample:
                            if not typeF == 'normal':
                                count = 0
                                import gzip
                                with gzip.open(self.FileExample[typeF], 'r') as ZippedFile:
                                    for PatternFound in ZippedFile:
                                        if count < 10:
                                            results.append(PatternFound)
                                            timePattern.write(PatternFound)
                                            count+=1
                                        else:
                                            break
                            else:
                                count = 0
                                with open(self.FileExample[typeF], 'r') as NonZippedFile:
                                    for PatternFound in NonZippedFile:
                                        if count < 10:
                                            results.append(PatternFound)
                                            timePattern.write(PatternFound)
                                            count+=1
                                        else:
                                            break
            else:
                return 'pattern not set'
        else:
            return 'Use SetDataTime first, no pattern added'
        
        return results

class DataPattern(FileToParse):
    """
    Parameter Object for Data Patterns used in FileToParse in config
    """
    def __init__(self, pattern):
        #self.session = session
        self.pattern =  {'tag': {}}
        self.dataPointTags = {}
        self.name = pattern
        self.TextBoxList = []
        self.ButtonList = []
        self.FormMgr = FormMgr()
    def GetConfigForExport(self):
        self.pattern['dataPointTags'] = self.dataPointTags 
        return self.pattern
    def ProcessFormInputs(self, session, returnForm=None):
        forms = self.FormMgr.GetFormInputs()
        print ("DataPattern %s forms: %s" %(self.name, forms))
        if 'add' in forms['ButonList']:
            if forms['ButonList']['add'] is not None:
                if self.name in forms['ButonList']['add']:
                    print ("Do something")
                    item = forms['ButonList']['add']
                    if 'dataPoints' in item:
                        print ("New item")
                        SplitItem = item.split('__')
                        keyId = 'Data__DataPattern__%s__tag__%s__dataPoints__Id__new'%(SplitItem[2], SplitItem[4])
                        keyPattern = 'Data__DataPattern__%s__tag__%s__dataPoints__pattern__new'%(SplitItem[2], SplitItem[4])
                        'Data__DataPattern__megastore.stats.revmap_misses:__tag__Encoder__dataPoints__add'
                        try:
                            self.AddDataPoint(SplitItem[4], forms['textBoxes'][keyId])
                        except:
                            print ("ID was empty")
                            pass
                        try:
                            self.pattern[SplitItem[3]][SplitItem[4]][SplitItem[5]][forms['textBoxes'][keyId]].append(forms['textBoxes'][keyPattern])
                        except:
                            pass
                    else:
                        SplitItem = item.split('__')
                        if not 'tag' in item:
                            print ("New Data Pattern: Split Item is: %s " %(SplitItem))
                        else:
                            keyId = 'Data__DataPattern__%s__tag__new' %(SplitItem[2])
                            #print ("New Tag: %s" %(InputList[item]))
                            if keyId in forms['textBoxes']:
                                if not forms['textBoxes'][keyId] == '':                                
                                    self.AddTag(forms['textBoxes'][keyId])
                            else:
                                parentDataPoint = forms['DropdList'][next(i for i in forms['DropdList'])]
                                print (parentDataPoint)
                                parentDataPointSplit = parentDataPoint.split('__')
                                self.AddDataPointTag(parentDataPointSplit[1], parentDataPointSplit[3], None)
        if 'test' in forms['ButonList'] and forms['ButonList']['test'] is not None:
            if self.name in forms['ButonList']['test']:
                if 'DataPattern' in item:
                    if 'dataPoints' in item:
                        SplitItem = item.split('__')
                        print ("Split Item: %s" %(SplitItem))
        """
        if 'config wiz' in forms['ButonList'] and forms['ButonList']['config wiz'] is not None:
            if self.name in forms['ButonList']['config wiz']:
                return (1, 'config wiz', {'PatternObj': self, 'name': self.name})
        """
        if 'del' in forms['ButonList'] and forms['ButonList']['del'] is not None:
            if self.name in forms['ButonList']['del']:
                item = forms['ButonList']['del']
                if 'dataPoints' in forms['ButonList']['del']:
                    SplitItem = item.split('__')
                    self.RemDataPoint(SplitItem[4], SplitItem[6])
                elif 'tag' in item:
                    SplitItem = item.split('__')
                    self.RemTag(SplitItem[4])
        if returnForm is not None:
            if returnForm in self.FormMgr.divGetHtml:
                self.GetHtmlOut(session)
                return (2, self.FormMgr.divGetHtml[returnForm]())
                    
    def AddTag(self, tag):
        if not tag in self.pattern['tag']:
            self.pattern['tag'][tag] = {'dataPoints': {}}
    def RemTag(self, tag):
        if tag in self.pattern['tag']:
            del self.pattern['tag'][tag]
        else:
            if tag in self.dataPointTags:
                if self.dataPointTags[tag] in self.pattern['tag']:
                    if tag in self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints']:
                        del self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]

    def AddDataPointTag(self, parentTag, parentDataPoint, childDataPoint):
        """
            input parentDataPoint should be an existing dataPoint: 
                self.pattern['tag'][tag]['dataPoints'][dataPoint]
            childDataPoint = New Data Point
        """
        if not parentDataPoint in self.dataPointTags:
            self.dataPointTags[parentDataPoint] = parentTag
        if not 'childDataPoints' in self.pattern['tag'][parentTag]:
            self.pattern['tag'][parentTag]['childDataPoints'] = {}
        if not parentDataPoint in self.pattern['tag'][parentTag]['childDataPoints']:
            self.pattern['tag'][parentTag]['childDataPoints'][parentDataPoint] = {'ids': {}}
        if not childDataPoint == None:
            self.pattern['tag'][parentTag]['childDataPoints'][parentDataPoint]['ids'][childDataPoint] = []
        
        
    def AddDataPoint(self, tag, dataPoint):
        if tag in self.pattern['tag']:
            print ("Add DataPoint Called: Current Value %s" %(self.pattern['tag'][tag]))
            if not dataPoint in self.pattern['tag'][tag]['dataPoints']:
                self.pattern['tag'][tag]['dataPoints'][dataPoint] = []
                #return self.pattern['tag'][tag]['dataPoints'][dataPoint]
            #print ("Post AddDataPoint %s"%(self.pattern['tag'][tag]))
        else:
            if tag in self.dataPointTags:
                if self.dataPointTags[tag] in self.pattern['tag']:
                    if not dataPoint in self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids']:
                        self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids'][dataPoint] = []
                
    def SetDataPointSplitConfig(self, tag, dataPoint, splitConfig):
        if tag in self.pattern['tag']:
            if dataPoint in self.pattern['tag'][tag]['dataPoints']:
                self.pattern['tag'][tag]['dataPoints'][dataPoint] = splitConfig
        else:
            if tag in self.dataPointTags:
                if self.dataPointTags[tag] in self.pattern['tag']:
                    if dataPoint in self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids']:
                        self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids'][dataPoint] = splitConfig
                
        
    def RemDataPoint(self, tag, dataPoint):
        if tag in self.pattern['tag']:
            print ("Remove DataPoint Called: Current Value %s" %(self.pattern['tag'][tag]))
            if dataPoint in self.pattern['tag'][tag]['dataPoints']:
                del self.pattern['tag'][tag]['dataPoints'][dataPoint]
        else:
            if tag in self.dataPointTags:
                if self.dataPointTags[tag] in self.pattern['tag']:
                    if dataPoint in self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids']:
                        del self.pattern['tag'][self.dataPointTags[tag]]['childDataPoints'][tag]['ids'][dataPoint]
                
    def GetHtmlOut(self,session, InModule=None):
        module = 'ConfigMgr' if InModule == None else InModule
        configWizParent = None if InModule == None else module + '_root'
        
        baseDiv = 'dataPattern_'+self.name+'_tb'
        
        Base = self.FormMgr.GetHtmlTable(['Tag', 'Data Points'], baseDiv, module)
        Base.IsHidden=True if InModule is None else False
        dataPointIdTagList = []
        for tagId in self.pattern['tag']:
            tgDivID = 'dataPattern_'+ self.name + '_tag_' + tagId + '_tgtb'
            tgDpDivID = 'dataPattern_'+ self.name + '_tag_' + tagId + '_dp_tb'
            dataPointsTb = self.FormMgr.GetHtmlTable(['id', 'splitConfig', 'action'], tgDpDivID, module)
            dataPointsTb.IsHidden=True if InModule is None else False
            
            for dataPointId in self.pattern['tag'][tagId]['dataPoints']:
                dataPointIdTagList.append({'pTag__%s__pId__%s'%(tagId, dataPointId): dataPointId})
                dpDivID = 'dataPattern_'+ self.name + '_tag_' + tagId + '_dp_' + dataPointId + '_tb'
                spltCfg = str(self.pattern['tag'][tagId]['dataPoints'][dataPointId])
                dataPointsTb.AddRow([dataPointId,spltCfg,
                                     self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'test', dpDivID, dpDivID, 'Data__DataPattern__%s__tag__%s__dataPoints__%s__test'%(self.name,tagId, dataPointId)), 
                                                                self.FormMgr.GetButton(session, 'del', dpDivID, baseDiv if configWizParent == None else configWizParent, 'Data__DataPattern__%s__tag__%s__dataPoints__%s__del'%(self.name,tagId, dataPointId)), 
                                                                self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'config wiz', None, None, self.name)], None, '/ConfigWiz/%s-%s'%(session, self.name), 'POST', False)
                                                                ], dpDivID, 'ConfigMgr')
                                    ])
            dataPointsTb.AddRow(['', '', 
                                 self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'config wiz', None, None, 'Data__DataPattern__%s__tag__%s__dataPoints__new__config'%(self.name,tagId)),
                                            ], None, '/ConfigWiz/%s-%s'%(session, self.name), 'POST', False)
                                ])
            tagTb = self.FormMgr.GetHtmlTable([tagId, 
                                               self.FormMgr.GetButton(session, 'del', 
                                                                  tgDivID, #Div Forms to process when pressed
                                                                  baseDiv if configWizParent == None else configWizParent, #Div to update when forms are processed.
                                                                  'Data__DataPattern__%s__tag__%s__del'%(self.name,tagId))], tgDivID, module)
            tagTb.SetHide(tgDpDivID)
            Base.AddRow([tagTb,
                        dataPointsTb])
            ###################
            #  DataPointTags  #
            ###################
            if 'childDataPoints' in self.pattern['tag'][tagId]:
                for parentDataPoint in self.pattern['tag'][tagId]['childDataPoints']:
                    dptgDivID = 'dataPattern_'+ self.name + '_tag_' + parentDataPoint + '_tgtb'
                    dpTgDpDivID = 'dataPattern_'+ self.name + '_dptag_' + parentDataPoint + '_dp_tb'
                    TagDataPointsTb = self.FormMgr.GetHtmlTable(['id', 'splitConfig', 'action'], dpTgDpDivID, 'ConfigMgr')
                    TagDataPointsTb.IsHidden = True
                    for Ids in self.pattern['tag'][tagId]['childDataPoints'][parentDataPoint]['ids']:
                        """
                            Add Row to Table 
                        """
                        dpTgDpDpDivID = 'dataPattern_'+ self.name + '_dptag_' + parentDataPoint+ '_dp_' + Ids + '_tb'
                        #dataPointIdTagList.append({'pTag__%s__pId__%s'%(parentDataPoint, Ids): Ids})
                        TagDataPointsTb.AddRow([Ids, 
                                     str(self.pattern['tag'][tagId]['childDataPoints'][parentDataPoint]['ids'][Ids]), 
                                     self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'test', dpTgDpDpDivID, dpTgDpDpDivID, 'Data__DataPattern__%s__dptag__%s__dataPoints__%s__test'%(self.name,parentDataPoint, Ids)), 
                                                self.FormMgr.GetButton(session, 'del', dpTgDpDpDivID, dpTgDpDivID, 'Data__DataPattern__%s__dptag__%s__dataPoints__%s__del'%(self.name,parentDataPoint, Ids)), 
                                                self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'config wiz', None, None, self.name)], None, '/ConfigWiz/%s-%s'%(session, self.name), 'POST', False)], dpTgDpDpDivID, module)])
                    
                    TagDataPointsTb.AddRow(['', '', self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'config wiz', None, None, 'Data__DataPattern__%s__dptag__%s__dataPoints__new__config'%(self.name,parentDataPoint))],
                                                      None, '/ConfigWiz/%s-%s'%(session, self.name), 'POST', False)
                                            ])
    
                    dataPointTagTb = self.FormMgr.GetHtmlTable(['(dataPoint) %s'%(parentDataPoint), 
                                            self.FormMgr.GetButton(session, 'del',dptgDivID, baseDiv if configWizParent == None else configWizParent if configWizParent == None else configWizParent, 'Data__DataPattern__%s__dptag__%s__del'%(self.name,parentDataPoint))],dptgDivID, module)
                    dataPointTagTb.SetHide(dpTgDpDivID)
                    Base.AddRow([dataPointTagTb, 
                                            TagDataPointsTb])
                        
        newTgDivId = 'dataPattern_'+ self.name + '_newtagTb'
        GlobalTagTb = self.FormMgr.GetHtmlTable(['New Tag'])
        GlobalTagTb.AddRow([self.FormMgr.GetTextBox(session, 'Data__DataPattern__%s__tag__new' %(self.name), '')])
        try:
            if len(dataPointIdTagList) > 0:
                DPTagTb = self.FormMgr.GetHtmlTable(['DataPoint Tag'])
                DPTagTb.AddRow([self.FormMgr.GetDropdown(session, 'Data__DataPattern__%s__tag__new__add_dp'%(self.name), dataPointIdTagList, dataPointIdTagList[0])])
        except:
            pass
        try:
            AddTagTable = self.FormMgr.GetHtmlTable([GlobalTagTb, 'or',DPTagTb], newTgDivId, module) if len(dataPointIdTagList) > 0 else self.FormMgr.GetHtmlTable([GlobalTagTb, self.FormMgr.GetButton(session, 'add', newTgDivId, baseDiv if configWizParent == None else configWizParent, 'Data__DataPattern__%s__tag__new__add'%(self.name))], newTgDivId, module)
        except:
            AddTagTable = self.FormMgr.GetHtmlTable([GlobalTagTb, self.FormMgr.GetButton(session, 'add', newTgDivId, baseDiv if configWizParent == None else configWizParent if configWizParent == None else configWizParent if configWizParent == None else configWizParent, 'Data__DataPattern__%s__tag__new__add'%(self.name))], newTgDivId, module)
        try:
            if len(dataPointIdTagList) > 0:
                AddTagTable.AddRow(['', self.FormMgr.GetButton(session, 'add', newTgDivId, baseDiv if configWizParent == None else configWizParent, 'Data__DataPattern__%s__tag__new__add'%(self.name)), ''])
        except:
            pass
        Base.AddRow([AddTagTable,''])
        return Base.GetFormattedHtml()
    
class TimeConfigWiz(object):
    """
        class for managing time config
        input is dict
        {"Time": {"inLine": false, 
        "Example": "TIMESTAMP: 2018-04-03 03:31:00", 
        "pattern": {"TIMESTAMP:": # if inLine == True, text is inLine
            {"H": [{"2": ":"}, 0], 
            "Mo": [{"1": "-"}, 1], 
            "Yr": [{"1": "-"}, 0], 
            "M": [{"2": ":"}, 1], 
            "Dy": [{"1": "-"}, 2]}}}}
    """
    
    def __init__(self, TimeConfig, fileLocation):
        
        self.TimeConfig = TimeConfig
        self.timepattern = (next(p for p in self.TimeConfig['pattern']))
        self.FormMgr=FormMgr()
        self.fileToGrepExamples = []
        with open(fileLocation, 'r') as fileToGrep:
            count = 0
            for line in fileToGrep:
                if self.TimeConfig['inLine'] == True:
                    self.fileToGrepExamples.append(line)
                    count +=1
                else:
                    if str(self.timepattern) in line:
                        self.fileToGrepExamples.append(line)
                        count +=1
                if count > 25:
                    break
                else:
                    pass
        self.currentInd = 0
        self.ChunkerIns = chunker.StringChunker(self.fileToGrepExamples[self.currentInd])
    def GetNavPane(self, session):
        GoBackButton = self.FormMgr.GetButton(session, "Go Back - ConfigMgr", None, None,'/ConfigMgr/%s'%(session))
        navPaneHtml = self.FormMgr.GetHtmlTable(['Navigation'])
        navPaneHtml.AddRow([self.FormMgr.GetHtmlTable([GoBackButton], None, '/ConfigMgr/%s'%(session), 'POST', False)])
        navPaneHtml.AddRow([self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'Go to next line', 'nav_TimeWiz', 'timewizChunkBase', '/TimeWiz/%s'%(session))], 'nav_TimeWiz', 'TimeWiz')])
        return navPaneHtml.GetFormattedHtml()
    def ProcessFormInputs(self, session, returnForm=None):
        forms = self.FormMgr.GetFormInputs() # Returns dict of above line 366
        """
            Handle Nav input
        """
        if 'Go to next line' in forms['ButonList']:
            if not forms['ButonList']['Go to next line'] == None:
                self.TryNextLineExample()
        """
            Handle Splits
        """
        if 'split' in forms['ButonList'] and not forms['ButonList']['split'] == None: #Split called by button input
            #try:
            splitButtonText = str(forms['ButonList']['split'])
            if not forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)] == '': # Check if Split was called but no input given.
                print ("Must Split Message Chunk: %s using string: %s " %(splitButtonText, forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)]))
                splitStr = forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)]
                try:
                    index = self.ChunkIndex[splitButtonText]
                except KeyError:
                    print ("KeyError assigning index @ line 438, attempting int conversion of splitButtonText")
                    index = self.ChunkIndex[int(splitButtonText)]
                print ("Index of current chunk that will be split: %s" %(index))
                self.SplitChunk(splitButtonText, splitStr)
        """
            Handle Add ID requests
        """
        
        if 'Set Pattern' in forms['ButonList'] and not forms['ButonList']['Set Pattern'] == None: #'Set Pattern' called by button input
            chunkDetail = self.GetChunkDetail(forms['ButonList']['Set Pattern'])
            try:
                tag = forms['DropdList'][str('Tag_%s'%(forms['ButonList']['Set Pattern']))] # fix this next 9/3 <--
            except KeyError:
                tag = forms['DropdList'][str('Tag_%s'%(chunkDetail['index']))] # fix this next 9/3 <--
            self.UpdateTimeConfig(tag, [{str(chunkDetail['index']): chunkDetail['chunk']['chain']}])
        if returnForm is not None:
            if returnForm in self.FormMgr.divGetHtml:
                self.GetHtmlOut(session)
                return (2, self.FormMgr.divGetHtml[returnForm]())
        
    def TryNextLineExample(self):
        """
            update line used by config wiz as line 0 could be invalid when initial pattern is not given
        """
        if self.currentInd == 24:
            self.currentInd = 0
        else:
            self.currentInd+=1
        self.ChunkerIns = chunker.StringChunker(self.fileToGrepExamples[self.currentInd])
    def GetChunkDetail(self, msgChunk):
        print ("DataPointConfigWiz__GetChunkDetail called: msgChunk: %s" %(msgChunk))
        msgChunk.split('-')[0]
        return {'index': msgChunk.split('-')[0], 'chunk': self.ChunkerIns.GetChunkDetail(msgChunk)}
    def SplitChunk(self, rootBaseIndex, splitStr):
        try:
            self.ChunkerIns.SplitChunk(splitStr, int(rootBaseIndex), None)
        except ValueError: 
            print ("ValueError converting rootBaseIndex to int, input must be a splitChunkString")
            self.ChunkerIns.SplitChunk(splitStr, self.ChunkerIns.GetChildChunkInd(rootBaseIndex), self.ChunkerIns.GetChildChunkRef(rootBaseIndex))
    def AddTag(self, tag):
        self.DataPatternObj.AddTag(tag)
    def UpdateTimeConfig(self, tag, splitConfig):
        print ("AddIdDataPoint called")
        self.TimeConfig['pattern'][self.timepattern][tag] = splitConfig
    def RemIdDataPoint(self, tag, iD):
        self.DataPatternObj.RemDataPoint(tag,iD)
    def RemTag(self, tag):
        self.DataPatternObj.RemTag(tag)
    def GetChunkIndex(self, msgChunk):
        """
        returns index value of msg chunk.
        """
        return self.ChunkIndex[int(msgChunk)]
    def GetHtmlOut(self, session):
        #Html Out
        self.FormMgr.ChunkIndex = {}
        self.FormMgr.TextBoxList = []
        self.FormMgr.ButtonList = []
        self.FormMgr.DropdownList = []
        self.FormMgr.CheckBoxList = []
        self.ChunkIndex = {}
        Base = self.FormMgr.GetHtmlTable(['Time Config Wizard'])
        timeHtmlTableRoot = self.FormMgr.GetHtmlTable(["Current Time Configuration"])
        tmWizInLineCfg = 'timeWiz_inLineCfg'
        timeHtmlTableConfig = self.FormMgr.GetHtmlTable(["pattern",next(p for p in self.TimeConfig['pattern']), 'inLine', 
                                                                        self.FormMgr.GetCheckBox(session,'isInline', True if self.timepattern =='inLine' else False), 
                                                                        self.FormMgr.GetButton(session, 'update', tmWizInLineCfg, tmWizInLineCfg, 'updateTimeConfig')], tmWizInLineCfg, 'TimeWiz')
        timeWizTimevalue = 'timeWiz_timeValues'
        timeHtmlTableSub = self.FormMgr.GetHtmlTable(['timeValue', 'pattern'], timeWizTimevalue, 'TimeWiz')
        for pattern in self.TimeConfig['pattern']:
                for tConfig in self.TimeConfig['pattern'][pattern]:
                    timeHtmlTableSub.AddRow([tConfig, self.TimeConfig['pattern'][pattern][tConfig]])
        timeHtmlTableRoot.AddRow([timeHtmlTableConfig])
        timeHtmlTableRoot.AddRow([timeHtmlTableSub])
        Base.AddRow([timeHtmlTableRoot])
        TimeWizBase = 'timewizChunkBase'
        ChunkerHtml = self.FormMgr.GetHtmlTable(['Datapoint Configuration Wizard'], TimeWizBase, 'TimeWiz')
        ChunkerDirHtml = self.FormMgr.GetHtmlTable(['Message Chunks'])
    
        chnkIndex = 0
        for item in self.ChunkerIns.Chunkdir:
            chunkDivId = 'chnk%s_splitTb_ChunkRoot'%(chnkIndex)
            ChunkerDirHtml.AddRow([self.FormMgr.GetHtmlTable([self.ChunkerIns.Chunkdir[item], self.GetSplitTextBoxButton(session,self.ChunkerIns.ChunkList[item], chunkDivId)], chunkDivId, 'TimeWiz')
                                ])
            chnkIndex+=1
            
        ChunkerHtml.AddRow([ChunkerDirHtml])
        Base.AddRow([ChunkerHtml])
        return Base.GetFormattedHtml()
    
    def GetSplitTextBoxButton(self, session, chunkRef, parentRef=None):
        if chunkRef.isCluster: # Is a cluster Chunk
            chnkClusterDivId = '%s_cluster'%(chunkRef)
            ClusterSplitTable = self.FormMgr.GetHtmlTable(['Cluster Items'], chnkClusterDivId, 'TimeWiz')
            clustInd = 0
            for clusterItem in chunkRef.clusterList:
                clustDiv = '%s_clusterItem_%s'%(parentRef, clustInd)
                ClusterSplitTable.AddRow([self.FormMgr.GetHtmlTable([clusterItem.string, self.GetSplitTextBoxButton(session,clusterItem, clustDiv)], clustDiv)])
                clustInd+=1
            if chunkRef.parent is not None:
                try:
                    if chunkRef.parent.isCluster:
                        return ClusterSplitTable
                except:
                    pass
                SplitTextBoxButtonTable = self.FormMgr.GetHtmlTable([chunkRef.string, ClusterSplitTable])
                return SplitTextBoxButtonTable
            else:
                return ClusterSplitTable
        else:
            rootchnkDivId = '%s_root_splitTb'%(chunkRef.string if parentRef == None else parentRef)
            SplitTextBoxButtonTable = self.FormMgr.GetHtmlTable(['Split Text', 'Data Point ID'], rootchnkDivId, 'TimeWiz')
            ChunkChain = chunkRef.ChunkChain
            TagList = []
            for Tag in self.TimeConfig['pattern'][self.timepattern]: 
                TagList.append(Tag)
            if chunkRef.parent is not None:
                iDString = str(self.ChunkerIns.GetBaseInd(chunkRef)) + '-' + ChunkChain
                try:
                    self.ChunkIndex[iDString] = str(self.ChunkerIns.Chunkdir[self.ChunkerIns.ChunkList.index(chunkRef.parent)])
                except KeyError:
                    try:
                        self.ChunkIndex[iDString] = str(self.ChunkerIns.ChunkList[self.ChunkerIns.ChunkList.index(chunkRef.parent)].string)
                    except:
                        pass
            else:
                iDString = self.ChunkerIns.ChunkList.index(chunkRef)
                try:
                    self.ChunkIndex[iDString] = str(self.ChunkerIns.Chunkdir[self.ChunkerIns.ChunkList.index(chunkRef)])
                except KeyError:
                    try:
                        self.ChunkIndex[iDString] = str(self.ChunkerIns.ChunkList[self.ChunkerIns.ChunkList.index(chunkRef)].string)
                    except:
                        pass
            chnkRoot = parentRef if parentRef is not None else '%s_ChunkRoot'%(chunkRef.string)
            chnkSplitDivId = '%s_splitTb'%(chunkRef.string) if parentRef == None else '%s_splitTb'%(parentRef)
            chnkSplitIdAddDivId = '%s_splitAddIdTb'%(chunkRef.string if parentRef == None else parentRef)
            #rootChunker = 'chunk_%s'%(chunkRef.string if parentRef == None else parentRef.string)
            SplitTextBoxButton = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, 'SplitTextTb_%s'%(iDString), ''), 
                                            self.FormMgr.GetButton(session, 'split',chnkSplitDivId, chnkRoot, '%s'%(iDString))], chnkSplitDivId, 'TimeWiz')
            IdTextBoxButton= self.FormMgr.GetHtmlTable([HtmlTable([self.FormMgr.GetDropdown(session, 'Tag_%s'%(iDString), TagList, TagList[0] if len(TagList) > 0 else None),
                                                   self.FormMgr.GetButton(session, 'Set Pattern', chnkSplitIdAddDivId, 'timeWiz_timeValues', '%s'%(iDString))])], 
                                        chnkSplitIdAddDivId, 'TimeWiz')
             
            SplitTextBoxButtonTable.AddRow([SplitTextBoxButton, IdTextBoxButton])        
            return SplitTextBoxButtonTable
        
    def ChunkSplit(self, splitStr, ind):
        self.ChunkerIns.SplitChunk(splitStr, ind)
        

class DataPointConfigWiz(object):
    def __init__(self, DataPatternObj, fileLocation):
        """
        # Get String using DataPattern to configure data points.
            #1 Open file using file location
            #2 Grep open file using Data Pattern
            #3 Using a line first found string, Create a StringChunker Instance. 
            #4 Provide capability of specifying a chunk as Data Points with a specific ID orsplit further, 
                #assign ID'd chunks to a Data Point for a particular tag.
        """
        self.reInit(DataPatternObj, fileLocation)
    def reInit(self,DataPatternObj, fileLocation):
        
        self.fileLocation = fileLocation
        self.DataPatternObj = DataPatternObj
        self.fileToGrepExamples = []
        self.FormMgr=FormMgr()
        with open(fileLocation, 'r') as fileToGrep:
            count = 0
            print ("Checking for %s in %s" %(self.DataPatternObj.name, fileLocation))
            for line in fileToGrep:
                if str(self.DataPatternObj.name) in line:
                    self.fileToGrepExamples.append(line)
                    count +=1
                if count > 25:
                    break
                else:
                    pass
        self.currentInd = 0
        self.LocalChunkIndex = {}
        self.ChunkerIns = chunker.StringChunker(self.fileToGrepExamples[self.currentInd])
        
        
        
    def GetNavPane(self, session, PatternList):
        navPaneTab = self.FormMgr.GetHtmlTable(["Navigation"])
        switchDataPatternTab = self.FormMgr.GetHtmlTable([self.FormMgr.GetDropdown(session, "Current Data Pattern", PatternList, str(self.DataPatternObj.name))],'nav_ConfigWiz_switchDp', 'ConfigWiz')
        switchDataPatternTab.AddRow([self.FormMgr.GetButton(session, "Switch To Data Pattern", 'nav_ConfigWiz_switchDp', 'body', "Current Data Pattern")])
        
        newDataPatternTab = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, "New Pattern Name", None)], 'nav_ConfigWiz_newDp', 'ConfigWiz')
        newDataPatternTab.AddRow([self.FormMgr.GetButton(session, "Add New Data Pattern", 'nav_ConfigWiz_newDp', 'body', "New Pattern Name")])
        
        navItems = [self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, "Go Back - ConfigMgr", None, None, '/ConfigMgr')], None, '/ConfigMgr/%s'%(session), 'POST', False),
                    switchDataPatternTab, newDataPatternTab,
                    ]
        for item in navItems:
            navPaneTab.AddRow([item])
        return navPaneTab.GetFormattedHtml()   
    def ProcessFormInputs(self, session, returnForm=None):
        forms = self.FormMgr.GetFormInputs()
        self.DataPatternObj.ProcessFormInputs(session, returnForm)
        if 'Switch To Data Pattern' in forms['ButonList'] and forms['ButonList']['Switch To Data Pattern'] is not None:
            return (3, 'change', forms['DropdList'][forms['ButonList']['Switch To Data Pattern']])
        if 'Add New Data Pattern' in forms['ButonList'] and forms['ButonList']['Add New Data Pattern'] is not None:
            return (3, 'new', forms['textBoxes'][forms['ButonList']['Add New Data Pattern']])
            
        if 'split' in forms['ButonList'] and forms['ButonList']['split'] is not None: #Split called by button input
            #try:
            splitButtonText = str(forms['ButonList']['split'])
            if not forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)] == '' or 'None': # Check if Split was called but no input given.
                print ("Must Split Message Chunk: %s using string: %s " %(splitButtonText, forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)]))
                splitStr = forms['textBoxes']['SplitTextTb_%s'%(splitButtonText)]
                try:
                    index = self.ChunkIndex[splitButtonText]
                except KeyError:
                    print ("KeyError assigning index @ line 438, attempting int conversion of splitButtonText")
                    index = self.ChunkIndex[int(splitButtonText)]
                print ("Index of current chunk that will be split: %s" %(index))
                self.SplitChunk(splitButtonText, splitStr)
            #except: 
                #print ("Key or  Unhandled Exception Error after #Split called by button input line431 ")
        if 'Add ID' in forms['ButonList'] and forms['ButonList']['Add ID'] is not None: #Add ID called by button input
            #try:
            if not forms['textBoxes']['IdTextTb_%s'%(forms['ButonList']['Add ID'])] == '' or None: # Check because Add ID was called if Id is empty
                iD = forms['textBoxes']['IdTextTb_%s'%(forms['ButonList']['Add ID'])]
                chunkDetail = self.GetChunkDetail(forms['ButonList']['Add ID'])
                #chunkDetail {'str': self.ChunkList[ind].string, 'chain': self.ChunkList[ind].ChunkChain}
                print ("Add ID called, need to add ID: %s for chunk: %s with chain config: %s at index: %s" %(iD, chunkDetail['chunk']['str'], chunkDetail['chunk']['chain'], chunkDetail['index']))
                try:
                    tag = forms['DropdList']['Tag_%s'%(forms['ButonList']['Add ID'])] # fix this next 9/3 <--
                except KeyError:
                    tag = forms['DropdList']['Tag_%s'%(chunkDetail['index'])] # fix this next 9/3 <--
                self.AddIdDataPoint(tag, iD, [{str(chunkDetail['index']): chunkDetail['chunk']['chain']}])
        
        DataPattern = ''
        for Button in forms['ButonList']:
            if not forms['ButonList'][str(Button)] == None or '':
                if 'Data__DataPattern' in forms['ButonList'][str(Button)]:
                    if DataPattern == '':
                        DataPattern = '__'.join(forms['ButonList'][str(Button)].split('__')[0:3])
                    #print ("Add a new Tag for Data Pattern: %s" %(DataPattern))
                    if not forms['ButonList'][str(Button)] == None or '':
                        print ("[%s] is not None or '' " %(forms['ButonList'][str(Button)]))
                        print ("Modifying Data Pattern using Top header. I.E Add / Del Tag, add/del a data point inside a tag")
                        TagAndDpSplt= forms['ButonList'][str(Button)].split('__')
                        if 'del' in forms['ButonList'][str(Button)]:
                            print ("Del tag or data point")
                            if 'dataPoints' in forms['ButonList'][str(Button)]: # Deleting a data point
                                # Data__DataPattern__encoded oid__tag__newTag1__dataPoints__Month__del]
                                self.RemIdDataPoint(TagAndDpSplt[4],TagAndDpSplt[6])
                            else: # Deleting tag
                                self.RemTag(TagAndDpSplt[4])
                        elif 'add' in forms['ButonList'][str(Button)]:
                            print ("Add Data Point or tag")
                            if 'dataPoints' in forms['ButonList'][str(Button)]: # Add DataPoint
                                print ("Add Data Point")
                                tag = TagAndDpSplt[4]
                                if not forms['textBoxes'][DataPattern + '__tag__%s__dataPoints__id__new'%(tag)] == None or '':
                                    iD = forms['textBoxes'][DataPattern + '__tag__%s__dataPoints__id__new'%(tag)]
                                    if not forms['textBoxes'][DataPattern + '__tag__%s__dataPoints__pattern__new'%(tag)] == None or '':
                                        SpltCfg = forms['textBoxes'][DataPattern + '__tag__%s__dataPoints__pattern__new'%(tag)]
                                        self.AddIdDataPoint(tag,iD, SpltCfg)
                            else: # add tag
                                print ("Add Tag")
                                if not forms['textBoxes'][DataPattern + '__tag__new'] == None or '':
                                    self.AddTag(forms['textBoxes'][DataPattern + '__tag__new'])
                        else:
                            print ("Unhandled or Test")
        if returnForm is not None:
            if returnForm in self.FormMgr.divGetHtml:
                self.GetHtmlOut(session)
                return (2, self.FormMgr.divGetHtml[returnForm]())
            if returnForm == 'body':
                return (1, self.GetHtmlOut(session))
            
            if returnForm in self.DataPatternObj.FormMgr.divGetHtml:
                #self.DataPatternObj.GetHtmlOut(session, 'ConfigWiz')
                #checkForDataPatternReturn = self.DataPatternObj.ProcessFormInputs(session, returnForm)
                #self.GetHtmlOut(session)   
                return (2, self.GetHtmlOut(session))
                #return (2, checkForDataPatternReturn[1])
    def GetChunkDetail(self, msgChunk):
        print ("DataPointConfigWiz__GetChunkDetail called: msgChunk: %s" %(msgChunk))
        msgChunk.split('-')[0]
        return {'index': msgChunk.split('-')[0], 'chunk': self.ChunkerIns.GetChunkDetail(msgChunk)}
    def SplitChunk(self, rootBaseIndex, splitStr):
        try:
            self.ChunkerIns.SplitChunk(splitStr, int(rootBaseIndex), None)
        except ValueError: 
            print ("ValueError converting rootBaseIndex to int, input must be a splitChunkString")
            self.ChunkerIns.SplitChunk(splitStr, self.ChunkerIns.GetChildChunkInd(rootBaseIndex), self.ChunkerIns.GetChildChunkRef(rootBaseIndex))
    def AddTag(self, tag):
        self.DataPatternObj.AddTag(tag)
    def AddIdDataPoint(self, tag, iD, splitConfig):
        print ("AddIdDataPoint called")
        self.DataPatternObj.AddDataPoint(tag, iD)
        self.DataPatternObj.SetDataPointSplitConfig(tag, iD, splitConfig)
    def RemIdDataPoint(self, tag, iD):
        self.DataPatternObj.RemDataPoint(tag,iD)
    def RemTag(self, tag):
        self.DataPatternObj.RemTag(tag)
        
    def GetChunkIndex(self, msgChunk):
        """
        returns index value of msg chunk.
        """
        #print ("index List : %s" %(self.ChunkIndex))
        return self.ChunkIndex[int(msgChunk)]
    def GetHtmlOut(self, session):
        self.ChunkIndex = {}
        Base = self.FormMgr.GetHtmlTable(['Configuration Wizard'], 'ConfigWiz_root')
        CurrentDataPointHtml = self.DataPatternObj.GetHtmlOut(session, 'ConfigWiz')
        Base.AddRow([CurrentDataPointHtml])
        ChunkerHtml = self.FormMgr.GetHtmlTable(['Datapoint Configuration Wizard'])
        ChunkerDirHtml = self.FormMgr.GetHtmlTable(['Message Chunker'])
    
        chnkIndex = 0
        for item in self.ChunkerIns.Chunkdir:
            msgChunkDivId = 'chunk_%s_DivId_root'%(chnkIndex)
            divToHide = '%s_SplitTextDpIdTb'%(self.ChunkerIns.ChunkList[item].string)
            ChunkSplitTb = self.FormMgr.GetHtmlTable([self.ChunkerIns.Chunkdir[item], self.GetSplitTextBoxButton(session,self.ChunkerIns.ChunkList[item], msgChunkDivId)], msgChunkDivId)
            ChunkSplitTb.SetHide(divToHide)
            ChunkerDirHtml.AddRow([ChunkSplitTb])
            chnkIndex+=1
            
        ChunkerHtml.AddRow([ChunkerDirHtml])
        Base.AddRow([ChunkerHtml])
        return Base.GetFormattedHtml()
    
    def GetSplitTextBoxButton(self, session, chunkRef, parentDiv = None):
        if chunkRef.isCluster: # Is a cluster Chunk

            ClusterSplitTable = self.FormMgr.GetHtmlTable(['Cluster Items'])
            clusterInd = 0
            for clusterItem in chunkRef.clusterList:
                clusterDivId = '%s_clusterDiv_%s'%(parentDiv,clusterInd)
                ClusterSplitSubTb = self.FormMgr.GetHtmlTable([clusterItem.string, self.GetSplitTextBoxButton(session,clusterItem, clusterDivId)], clusterDivId)
                ClusterSplitSubTb.SetHide('%s_SplitTextDpIdTb'%(clusterItem.string))
                ClusterSplitTable.AddRow([ClusterSplitSubTb])
                clusterInd+=1
                
            if chunkRef.parent is not None:
                try:
                    if chunkRef.parent.isCluster:
                        return ClusterSplitTable
                except:
                    pass
                SplitTextBoxButtonTable = self.FormMgr.GetHtmlTable([chunkRef.string, ClusterSplitTable], '%s_SplitTextDpIdTb'%(chunkRef.string))
                SplitTextBoxButtonTable.IsHidden=True
                return SplitTextBoxButtonTable
            else:
                return ClusterSplitTable
        else:
            SplitTextBoxButtonTable = self.FormMgr.GetHtmlTable(['Split Text', 'Data Point ID'], '%s_SplitTextDpIdTb'%(chunkRef.string))
            ChunkChain = chunkRef.ChunkChain
            print (ChunkChain)
            TagList = []
            for Tag in self.DataPatternObj.pattern['tag']: ## TOO DOO NEXT, finish cluster chunk 
                TagList.append(Tag)
                if 'childDataPoints' in self.DataPatternObj.pattern['tag'][Tag]:
                    for parentDataPoint in self.DataPatternObj.pattern['tag'][Tag]['childDataPoints']:
                        TagList.append(parentDataPoint)
            if chunkRef.parent is not None:
                iDString = str(self.ChunkerIns.GetBaseInd(chunkRef)) + '-' + ChunkChain
                try:
                    self.ChunkIndex[iDString] = str(self.ChunkerIns.Chunkdir[self.ChunkerIns.ChunkList.index(chunkRef.parent)])
                except KeyError:
                    try:
                        self.ChunkIndex[iDString] = str(self.ChunkerIns.ChunkList[self.ChunkerIns.ChunkList.index(chunkRef.parent)].string)
                    except:
                        pass
            else:
                iDString = self.ChunkerIns.ChunkList.index(chunkRef)
                try:
                    self.ChunkIndex[iDString] = str(self.ChunkerIns.Chunkdir[self.ChunkerIns.ChunkList.index(chunkRef)])
                except KeyError:
                    try:
                        self.ChunkIndex[iDString] = str(self.ChunkerIns.ChunkList[self.ChunkerIns.ChunkList.index(chunkRef)].string)
                    except:
                        pass
            baseDpDiv = 'dataPattern_'+self.DataPatternObj.name+'_tb'
            baseSplitDivId = parentDiv
            splitTbDivId = '%s_split_Chunk_Tb_'%(parentDiv)
            splitIdTbDivId = '%s_split_Id_Chunk_Tb_'%(parentDiv)
            SplitTextBoxButton = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, 'SplitTextTb_%s'%(iDString), ''), 
                                                            self.FormMgr.GetButton(session, 'split', splitTbDivId, baseSplitDivId, '%s'%(iDString))], splitTbDivId, 'ConfigWiz')
            IdTextBoxButton= self.FormMgr.GetHtmlTable([HtmlTable([self.FormMgr.GetTextBox(session, 'IdTextTb_%s'%(iDString), ''), 
                                                   self.FormMgr.GetDropdown(session, 'Tag_%s'%(iDString), TagList, TagList[0] if len(TagList) > 0 else None),
                                                   self.FormMgr.GetButton(session, 'Add ID', splitIdTbDivId, 'ConfigWiz_root', '%s'%(iDString))])], splitIdTbDivId, 'ConfigWiz')
            SplitTextBoxButtonTable.AddRow([SplitTextBoxButton, IdTextBoxButton])    
            SplitTextBoxButtonTable.IsHidden=True
            return SplitTextBoxButtonTable
        
    def ChunkSplit(self, splitStr, ind):
        self.ChunkerIns.SplitChunk(splitStr, ind)

class Config(object):
    """
    Class for configurations
    """
    def __init__(self, name, config):
        self.name = name
        self.CurrentNavFile = None
        self.config = config
        self.runningConfig = {'Tool': {
                    'FilesToParse': {}
                }
            }
        self.FilesToParse = {}
        self.LoadConfig()
    def GetPatternList(self):
        patternList = []
        print ("NavFile: %s" %(self.CurrentNavFile))
        print ("GetPatternList.fData Patterns : %s" %(self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile].Data['DataPattern']))
        for Pattern in self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile].Data['DataPattern']:
            if not str(Pattern) in patternList:
                patternList.append(str(Pattern))
        return patternList
    def GetTagList(self):
        tagList = []
        for Pattern in self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile]['Data']['DataPattern']:
            if 'tag' in self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile]['Data']['DataPattern'][Pattern]:
                if not self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile]['Data']['DataPattern'][Pattern]['tag'] in tagList:
                    tagList.append(self.runningConfig['Tool']['FilesToParse'][self.CurrentNavFile]['Data']['DataPattern'][Pattern]['tag'])
        return tagList
            
    def GetConfigExport(self):
        
        temp_dict = {}
        for fileToParse in self.runningConfig['Tool']['FilesToParse']:
            temp_dict[fileToParse] = self.runningConfig['Tool']['FilesToParse'][fileToParse].GetConfigForExport()        
        
        return {'Tool': {
                    'FilesToParse': temp_dict
                }
            }
    def LoadConfig(self):
        if self.config is not None:    
            for fileToParse in self.config['Tool']['FilesToParse']:
                 self.AddFileToParse(fileToParse)
                 self.runningConfig['Tool']['FilesToParse'][fileToParse].LoadConfig(self.config['Tool']['FilesToParse'][fileToParse])
                 lastFileToParse = fileToParse
            if lastFileToParse in self.runningConfig['Tool']['FilesToParse']:
                if self.CurrentNavFile == None:
                    self.CurrentNavFile = lastFileToParse
    def AddFileToParse(self, file):
        if not file in self.runningConfig['Tool']['FilesToParse']: 
            self.runningConfig['Tool']['FilesToParse'][file] = FileToParse(file)

class ConfigMgr(object):
    """
    Class for Managing Configurations
    """
    def __init__(self):
        self.configDict = {}
        self.FileListDict = {}
        self.refreshIndex()
        self.LoadedFile = str()
        
    def GetConfigFileList(self):
        self.FileListDict = {}
        self.refreshIndex()
        with open('config_index', 'r') as config_ind:
            ind = 0
            for file in config_ind:
                self.FileListDict[ind] = file.rstrip()
                ind+=1
        return self.FileListDict
    def refreshIndex(self):
        import os
        os.system('rm -f config_index')
        os.system('find cfg/ -type f -maxdepth 1 >> config_index')
    def LoadConfig(self, fileIndex):
        if fileIndex in self.FileListDict:
            with open(self.FileListDict[fileIndex], 'r') as configJs:
                self.LoadedFile = self.FileListDict[fileIndex]
                self.configDict[self.FileListDict[fileIndex]] = Config(self.FileListDict[fileIndex], json.load(configJs))
            return self.FileListDict[fileIndex]
    def SaveConfig(self, fileToSave):
        if fileToSave.split('/cfg')[0] == fileToSave:
            print ("Save Config: input file name: %s"%(fileToSave))
            with open('%s'%(fileToSave), 'w+') as f:
                json.dump(self.configDict[fileToSave].GetConfigExport(), f)
        else:
            with open('%s.json'%(fileToSave), 'w+') as f:
                json.dump(self.configDict[fileToSave].GetConfigExport(), f)
    def NewConfig(self, fileName):
        self.configDict[fileName] = Config(fileName, None)