
from formsmanager import FormMgr

class AppDataMgr(object):
    """
        class for configuring DataPoints, 
        Data Points should be speficied first using ConfigMgr via ConfigWiz, then are defined in an AppDataMgr instnace before saved for use in application.
        
    """
    def __init__(self, ConfMgrIns):
        """
            ConfMgrIns with loaded Configs
        """
        self.ConfMgrIns = ConfMgrIns
        """
            IdTb formatting:
                {'dataType': None, # Will be configured from dataTypes dict, Examples are integer(counter), MB, KB, Percentage
                 'tag': 'tagName', # How the dataPoint is organized 
                 'calc': True/False, # Is the dataPoint derived from calculations made with mined data.
                
                }
        """
        self.IdTb = {}
        
        self.dataTypes = [{'uncfgrd': 'uncfgrd'},
                          {'guage': 'guage'}, # Data can go up / down depending on reported value with maxes and mins
                          {'counter': 'counter'}, # Normally Raw data, could be zeroed, no max. 
                          {'histogram': 'histogram'}, # Tracking if an event occurs at Y Time. 
                          {'bool': 'bool' } # Value is 1 or 0 if a particular condition is True / False i.e Garbage Collection is Running = True 
                          ]
        self.tagList = {}
        self.UpdateTagIdDict()
        self.FormMgr = FormMgr()
        
    def UpdateTagIdDict(self):
        for configObj in self.ConfMgrIns.configDict:
            for file in self.ConfMgrIns.configDict[configObj].runningConfig['Tool']['FilesToParse']:
                fileToParse = self.ConfMgrIns.configDict[configObj].runningConfig['Tool']['FilesToParse'][file]
                for dataPattern in fileToParse.Data['DataPattern']:
                    currPattern = fileToParse.Data['DataPattern'][dataPattern].pattern
                    for tag in currPattern['tag']:
                        if 'childDataPoints' in currPattern['tag'][tag]:
                            for parentDataPoint in currPattern['tag'][tag]['childDataPoints']:
                                for chId in currPattern['tag'][tag]['childDataPoints'][parentDataPoint]['ids']:
                                    dpTag = '%s.%s'%(tag, parentDataPoint)
                                    self.IdTb[chId] = {'dataType': None, 'tag': dpTag, 'calc': False} if not chId in self.IdTb else self.IdTb[chId]
                                    if not dpTag in self.tagList:
                                        self.tagList[dpTag] = []
                                    self.tagList[dpTag].append(chId)
                                        
                                        
                                    
                        for dataPoint in currPattern['tag'][tag]['dataPoints']:
                            #for dpId in currPattern['tag'][tag]['dataPoints'][dataPoint]:
                            print (dataPoint)
                            #if not dpId in self.IdTb:
                            #    self.IdTb[dpId] = {'datatype': None, 'tag': tag, 'calc': False}
                            self.IdTb[dataPoint] = {'dataType': None, 'tag': tag, 'calc': False} if not dataPoint in self.IdTb else self.IdTb[dataPoint]
                            if not tag in self.tagList:
                                self.tagList[tag] = []
                            self.tagList[tag].append(dataPoint)
    def ProcessFormInputs(self, session, returnForm):
        result = self.FormMgr.GetFormInputs()
        print (result)
        if 'New' in result['ButonList']:
            AddOp = self.AddOptions(session, result['ButonList']['New'])
            return (2, AddOp.GetFormattedHtml())
        if 'math' in result['ButonList']:
            MathOp = self.MathOperation(session, str(int(result['ButonList']['math'])))
            return (2, MathOp.GetFormattedHtml())
        if 'conditional' in result['ButonList']:
            """
            if int(result['ButonList']['conditional']) < 1:
                condOp = self.StartIfTable(session, result['ButonList']['conditional'])
            else:
            """
            condOp = self.ConditionalTb(session, result['ButonList']['conditional'])
            return (2,condOp.GetFormattedHtml())
        if 'data point' in result['ButonList']: 
            return (2, self.DataPointTb(session, result['ButonList']['data point']).GetFormattedHtml())
        if 'add' in result['ButonList']:
            AddOp = self.AddOptions(session, str(int(result['ButonList']['add'])))
            return (2, AddOp.GetFormattedHtml())
        if 'done' in result['ButonList']:
            print (self.GetAndVerifyInput(result))

            return (2, self.GetConfigureNewDataPoint(session).GetFormattedHtml())
        else:
            return (2, self.FormMgr.divGetHtml[returnForm]())
        
    def AddOptions(self, session, curOp):
        """
            returns 3 button table: math, conditional, data point
        """
        tbId = 'addOptTb_%s'%(curOp)
        
        addOptsTb = self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'math', tbId+'root', tbId, curOp, True)], tbId+'root', 'AppMgr')
        addOptsTb.AddRow([self.FormMgr.GetButton(session, 'conditional', tbId+'root', tbId, curOp, True)])
        addOptsTb.AddRow([self.FormMgr.GetButton(session, 'data point', tbId+'root', tbId, curOp, True)])
        
        AddOptBase = self.FormMgr.GetHtmlTable([addOptsTb])
        AddOptBase.AddRow([self.FormMgr.GetHtmlTable([''], tbId)])

        return AddOptBase
    def ConditionalTb(self, session, curOp):
        condTb = self.FormMgr.GetHtmlTable([self.Conditional(session, curOp), 
                                            #self.GetDpOrFreeText(session, str(int(curOp)+1)),
                                            self.NextAction(session, str(int(curOp)+1))])
        return condTb
    def DataPointTb(self, session, curOp):
        dpTb = self.FormMgr.GetHtmlTable([self.DataPointsForCalc(session, curOp), self.NextAction(session, str(int(curOp)+1))])
        return dpTb
    
    def Conditional(self, session, curOp):
        """
            Creates Data Point if condtion is met
        """
        cndOps = [{'if': 'if'},
                  {'==': 'equal'}, # Creates Data Point if condtion is met
                  {'>=': 'grtr than or equal'},
                  {'=<': 'less than or equal'},
                  {'or': 'or'},
                  {'not': 'not'},
                  {'then': '(endIf) then'}]
        cndSelect = self.FormMgr.GetDropdown(session, 'cnd_CFG_%s'%(curOp), cndOps, 'if')
        return cndSelect
    
    def GetDpOrFreeText(self, session, curOp):
        freeTextOrDp = self.FormMgr.GetHtmlTable([self.FormMgr.GetTextBox(session, 'fTb_CFG_%s'%(curOp), '')], 'freeTbOrDp_%s'%(curOp))
        freeTextOrDp.AddRow([self.DataPointsForCalc(session, curOp)])
        return freeTextOrDp
        
    def MathOperation(self, session, curOp):
        """
            curOp is used to track form postion for cacluating a new dataPoint.
            0 is processed before 1, then 2, 3 .. 
        """
        mthOps = [{'+' : '+(add)' },
        		   {'-' : '-(sub)' },
        		   {'*' : '*(mul)' },
        		   {'/' : '/(div)' },
        		   {'%%': '%%(mod)'}]
        mthSelect = self.FormMgr.GetDropdown(session, 'mthOp_CFG_%s'%(curOp), mthOps, '+')
        
        freeTextOrDp = self.GetDpOrFreeText(session, str(int(curOp)+1))
        
        tbContents = [mthSelect, freeTextOrDp, self.NextAction(session, str(int(curOp)+2))] if int(curOp) > 0 else [self.DataPointsForCalc(session,curOp), mthSelect, freeTextOrDp, self.NextAction(session, str(int(curOp)+1))]
        
        MthTb = self.FormMgr.GetHtmlTable(tbContents, 'mthTb_%s'%(curOp))
        return MthTb
        
    def DataPointsForCalc(self, session, curOp):
        """# Data Points"""
        dpList = [{'None': None}]
        for dpId in self.IdTb:
            dpList.append({dpId: dpId})
        dpSelect = self.FormMgr.GetDropdown(session, 'dp_CFG_%s'%(curOp), dpList, None)
        return dpSelect
        
    def NextAction(self, session, currentOperation):
        ops = {}
        nextActNm = 'nextActionTb_%s'%(currentOperation)
        for op in ['undo', 'add', 'done']:
            nextAct = nextActNm+'root' if op in ['undo','add'] else 'newCalcDpTb_sub'
            ops[op] = self.FormMgr.GetButton(session, op, nextAct, nextActNm if op in ['undo','add'] else 'newCalcDpTb_root', currentOperation, True if op in ['undo','add'] else False)
        nextATb = self.FormMgr.GetHtmlTable([ops['undo']], nextActNm+'root', 'AppMgr')
        nextATb.AddRow([ops['add']])
        nextATb.AddRow([ops['done']])
        nATb = self.FormMgr.GetHtmlTable([nextATb], None, 'AppMgr')
        nATb.AddRow([self.FormMgr.GetHtmlTable([''], nextActNm, 'AppMgr')])
        return nATb
        
    def GetTagList(self):
        tagList = [{'None': None}]
        for eachTag in self.tagList:
            tagList.append({eachTag: eachTag})
        return tagList
    def GetConfigureNewDataPoint(self, session):
        NewCalcDpTb = self.FormMgr.GetHtmlTable(['Configure a New Data Point using existing data'], 'newCalcDpTb_root')
        NewCalcDpTbSub = self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'New', 'newCalcDpTb_sub'+'root', 'newCalcDpTb_sub', '0',True)], 'newCalcDpTb_sub'+'root', 'AppMgr')
        NewCalcDpTb.AddRow([NewCalcDpTbSub])
        NewCalcDpTb.AddRow([self.FormMgr.GetHtmlTable([''], 'newCalcDpTb_sub', 'AppMgr')])
        return NewCalcDpTb
    def GetAndVerifyInput(self, result):
        """
            Example Input:
                {'DropdList': {'dp_CFG_5': 'Total Enc Segs', 'dp_CFG_3': 'Bytes Encoded', 'dp_CFG_1': 'Total Encoded Segs', 'dp_CFG_8': 'None', 
                               'cnd_CFG_4': 'then', 'cnd_CFG_2': '>=', 'cnd_CFG_0': 'if', 'mthOp_CFG_7': '%%'}, 
                'CheckList': {}, 
                'ButonList': {'done': '9'}, 
                'textBoxes': {'fTb_CFG_8': '1024'}}
        """
        inputs = {}
        
        for InputType in result:
            for inItem in result[InputType]:
                if not result[InputType][inItem] in ['None']:
                    if inItem in ['done']:
                        inputs[inItem] = result[InputType][inItem]
                    else:
                        inItemSplit = inItem.split('_CFG_')    
                        inputs[inItemSplit[1]] = {'type': inItemSplit[0],
                                                  'value': result[InputType][inItem]}
        print ("GetAndVerifyInpus: %s" %(inputs))
        lastOp = None
        ifCheck = False
        ifMap = []
        for i in range(0, int(inputs['done'])):
            curOp = inputs[str(i)]['type']
            if curOp == lastOp:
                return (1, "Unable to determine calculation - two consecutive datapoints without comparison or calculation used")
            lastOp = curOp
            if curOp == 'cnd':
                if str(i) == '0':
                    if not inputs[str(i)]['value'] == 'if':
                        return (1, "Calculations cannot start with a non ('if') statment")
                if inputs[str(i)]['value'] == 'then':
                    if not ifCheck:
                        return (1, "Conditions cannot start with endif(then) statements") # Endif used before if
                    else:
                        ifMap.append({'then': i})
                        ifCheck = False
                elif inputs[str(i)]['value'] == 'if':
                    ifMap.append({'if': i})
                    ifCheck = True
                else: # Non if or then condition
                    pass 
        
        if ifCheck:
            return (1, "If statment never closed with endif")
        
        if len(ifMap) > 0:
            ifWork = False
            
            for ifEntry in ifMap:
                for ifSt in ifEntry:
                    if ifEntry[ifSt] > 0:
                        ifWork = True
                    if ifEntry[ifSt] < int(inputs['done']):
                        ifWork = True
            if not ifWork:
                return (1, "If statement is defined, but no value or calculation followed / preceded")
        def GetReadable(inVal, curStep, maxStep):
            stepStr = ''
            if curStep in inVal:
                if inVal[str(curStep)]['type'] == 'dp':
                    spcChk = ' ' if curStep == '0' else ''
                    stepStr = stepStr + inVal[curStep]['value'] + spcChk
                if inVal[str(curStep)]['type'] == 'mthOp':
                     stepStr = stepStr + ' '+ inVal[str(curStep)]['value'] + ' '
                if inVal[str(curStep)]['type'] == 'cnd':
                    if inVal[str(curStep)]['value'] in ['if','then']:
                        if inVal[str(curStep)]['value'] == 'if':
                            # if stuff
                            stepStr = stepStr + 'if ( '
                        else:
                            # then stuff
                            thenCheck = 'then ' if str(int(curStep)+1) in inVal else ''
                            stepStr = stepStr + ') '+ thenCheck
                    else:
                        stepStr = stepStr + ' '+ inVal[str(curStep)]['value'] + ' '
            else:
                print ("curstep %s is not in input"%(curStep))
            if curStep == maxStep:
                return stepStr
            else:
                return stepStr + GetReadable(inVal, str(int(curStep)+1), maxStep)
            
        print (GetReadable(inputs, '0', inputs['done']))
            
        """
            Example GetAndVerifyInput output:
                {'1': {'type': 'dp', 'value': 'Total Encoded Segs'}, 
                 '0': {'type': 'cnd', 'value': 'if'}, 
                 '3': {'type': 'dp', 'value': 'Bytes Encoded'}, 
                 '2': {'type': 'cnd', 'value': '>='}, 
                 '5': {'type': 'dp', 'value': 'Bytes Encoded'}, 
                 '4': {'type': 'cnd', 'value': 'then'}, 
                 '7': {'type': 'dp', 'value': 'Total Enc Segs'}, 
                 '6': {'type': 'mthOp', 'value': '/'}, 
                 'done': '8'}
                
        """
        return (0, inputs)
    def GetHtmlOut(self, session):
        BaseHtmlTable = self.FormMgr.GetHtmlTable(['AppData Manager'], 'AppDataMgr_root')
        tagList = self.GetTagList()
        
        sortByTagTb = self.FormMgr.GetHtmlTable(['sort by tag name', self.FormMgr.GetDropdown(session, 'sortByTag', tagList, None)], 'sortByTagtb')
        
        BaseHtmlTable.AddRow([sortByTagTb])
        for dpId in self.IdTb:
                        
            subCfgTbDiv = '%s_cfg'%(dpId)
            dpIdCfgTb = self.FormMgr.GetHtmlTable([''], subCfgTbDiv)
            
            
            dataTypeCfgRow = self.FormMgr.GetHtmlTable(['Data Type', self.FormMgr.GetDropdown(session, '%s_dataTypeSelect'%(dpId), self.dataTypes, self.IdTb[dpId]['dataType'])
                                                    ])
            tagCfgRow = self.FormMgr.GetHtmlTable(['tag', self.IdTb[dpId]['tag']])
            calcCfgRow = self.FormMgr.GetHtmlTable(['calculated?', self.IdTb[dpId]['calc']])
            
            dpIdCfgTb.AddRow([tagCfgRow])
            dpIdCfgTb.AddRow([dataTypeCfgRow])
            dpIdCfgTb.AddRow([calcCfgRow])
            dpIdCfgTb.IsHidden=True
            
            dpIdTb = self.FormMgr.GetHtmlTable([dpId, dpIdCfgTb], dpId)
            dpIdTb.SetHide(subCfgTbDiv)
            BaseHtmlTable.AddRow([dpIdTb])
        """
        NewCalcDpTb = self.FormMgr.GetHtmlTable(['Configure a New Data Point using existing data'], 'newCalcDpTb_root')
        NewCalcDpTbSub = self.FormMgr.GetHtmlTable([self.FormMgr.GetButton(session, 'New', 'newCalcDpTb_sub'+'root', 'newCalcDpTb_sub', '0',True)], 'newCalcDpTb_sub'+'root', 'AppMgr')
        NewCalcDpTb.AddRow([NewCalcDpTbSub])
        NewCalcDpTb.AddRow([self.FormMgr.GetHtmlTable([''], 'newCalcDpTb_sub', 'AppMgr')])
        """
        BaseHtmlTable.AddRow([self.GetConfigureNewDataPoint(session)])
        return BaseHtmlTable.GetFormattedHtml()
        
        
        

                                
                            
        
        