"""
config = {"Tool":
    {"FilesToParse":
        {"messages":
            {"findFilePatterns":
                {"1": {"pattern": "message", "type": "normal"},
                 "2": {"pattern": "message.*.gz", "type": "zip"}
                 },
            "Data":
                {"DataPattern":
                    {"encoded oid": {"tag": {}},
                     "encoded with oid": {"tag": {}},
                     "decoded oid": {"tag": {}}},
                "Time": {"inLine": true, "pattern": {}}},
                "Location": "/mnt/light/DPEmeaRhlog/sysdump-apalv01-20180822-103145/"},
        "rfsctl-a.log":
            {"findFilePatterns":
                {"1": {"pattern": "rfsctl-a.log", "type": "normal"},
                 "2": {"pattern": "rfsctl-a.log.*.gz", "type": "zip"}},
            "Data": {"DataPattern": {"megastore.stats.revmap_misses:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.num_nonsequential_writes:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.total_wait_flush_latency:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.revmap_hits:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.num_wait_buffer:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.total_wait_for_buffer_latency:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.num_bufs_forced_encode:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_anchor_misses:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.num_overlapping_writes:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.total_write_call_latency:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_bytes:": {"tag": {"Encoder": {}}},
                                     "write_cache.stats.num_bufs_full:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_data_hits:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_calls:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_anchor_hits:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encoders_active:": {"tag": {"Encoder": {}}},
                                     "megastore.stats.encode_data_misses:": {"tag": {"Encoder": {}}}},
                 "Time": {"inLine": false, "Example": "TIMESTAMP: 2018-04-03 03:31:00", "pattern": {"TIMESTAMP:": {"H": [{"2": ":"}, 0], "Mo": [{"1": "-"}, 1], "Yr": [{"1": "-"}, 0], "M": [{"2": ":"}, 1], "Dy": [{"1": "-"}, 2]}}}},
                 "Location": "/mnt/light/DPEmeaRhlog/sysdump-apalv01-20180822-103145/collect_stats/"}}}}
"""
"""
1. Name of class?
        Nave given to file -

2. How to locate files? -
        What to search for? - feeds in findFilePatterns

"""



class logFile(object):
    def __init__(self, ApplicationRef, name, initFindFilePatterns):
        self.ApplicationRef = ApplicationRef
        print ("init")
        self.name = name
        self.workerFuncs = {}
        self.fileList = {}
        self.findFilePatterns = initFindFilePatterns
        self.GenerateFileListFunc = self.GetFileLoadFunction(self.findFilePatterns)
        self.LoadedFiles = {}
        self.locationToSearch = None
        self.isFilesLoaded = False
        self.timeConfig = None
    def UpdateTimeConfig(self, timeConfig):
        self.timeConfig = timeConfig
    def AddFunction(self, name, dataPatternConfig):
        self.workerFuncs[name] = self.GetProcessFunction(name, dataPatternConfig, self.timeConfig)
    def ListWorkFuncs(self):
        for func in self.workerFuncs:
            print ("Function: %s" %(func))
            print (self.workerFuncs[func])
    def UpdateFileList(self, locationToSearch):
        self.fileList = self.GenerateFileListFunc(self,locationToSearch)
# Input DataPatternConfig[dataPattern].append({'tag': tag, 'dpID': dataPointId, 'sc': config[dataPattern]["tag"][tag]["dataPoints"][dataPointId]})
    def GetSubProcessFunction(self, timeConfig, DataPatternConfig):
        def GetCommandsFromSplitConfig(inputConfig):
            def GetSplitListFromSplitConifg(inputConfig, listToAppend):
                LocalListToAppend = listToAppend
                if type(inputConfig)  == list:
                    if len(inputConfig) > 0:
                        for item in inputConfig:
                            if type(item) == dict:
                                GetSplitListFromSplitConifg(item, LocalListToAppend)
                            #if type(item) == list:
                             #   if len(item) > 0:
                              #      splitList.append(GetSplitListFromSplitConifg(item))
                            else:
                                LocalListToAppend.append({'split': item})
                elif type(inputConfig) == dict:
                    for item in inputConfig:
                        LocalListToAppend.append({'index': item})
                        LocalListToAppend.append(GetSplitListFromSplitConifg(inputConfig[item], LocalListToAppend))
                return LocalListToAppend
            #newSc = [{'5': ['.', {'0': ['[', 'cod']}, {'1': []}]}]
            newSc = inputConfig
            newList = []
            newList = GetSplitListFromSplitConifg(newSc, newList)
            newList2 = []
            for item in newList:
                if type(item) == dict:
                    newList2.append(item)
            return newList2
        """
            example of required input splitConfig
            [{'5': ['.', {'0': ['[', 'cod']}, {'1': []}]}]
        """
        DataPattern = next(i for i in DataPatternConfig)
        CommandsToSplitList = []
        for CommandSet in DataPatternConfig[DataPattern]:
            print("ID: %s commands: %s" %(CommandSet['dpID'],GetCommandsFromSplitConfig(CommandSet['sc'])))
            if 'chWrk' in CommandSet:
                """
                    CommandSet has chWrk, for dataSetIDtag
                    {'dptag': dataPointId, 'dpID': childDataPoint, 'sc': childDataPointSc}
                """
                chwrk = []
                for chWrk in CommandSet['chWrk']:
                    chwrk.append({'dpID': chWrk['dpID'], 'split': GetCommandsFromSplitConfig(chWrk['sc'])})
                CommandsToSplitList.append({'tag': CommandSet['tag'], 'dpID': CommandSet['dpID'], 'split': GetCommandsFromSplitConfig(CommandSet['sc']), 'chWrk': chwrk})
            else:
                CommandsToSplitList.append({'tag': CommandSet['tag'], 'dpID': CommandSet['dpID'], 'split': GetCommandsFromSplitConfig(CommandSet['sc'])})
        #print (CommandsToSplitList)
        """
            example of required input timeConfig
        "Time": {"inLine": false,
                 "Example": "TIMESTAMP: 2018-04-03 03:31:00",
                 "pattern": {"TIMESTAMP:": {"H": [{"2": [":", {"0": []}]}],
                                            "Mo": [{"1": "-"}, 1],
                                            "Yr": [{"1": "-"}, 0],
                                            "M": [{"2": [":", {"1": []}]}],
                                            "Dy": [{"1": "-"}, 2]}}}
        """
        timePatterns = timeConfig['Time']['pattern'][next(i for i in timeConfig['Time']['pattern'])]
        TimeCommands = {'inLine': timeConfig['Time']['inLine'],
                        'H': GetCommandsFromSplitConfig(timePatterns['H']),
                        'M': GetCommandsFromSplitConfig(timePatterns['M']),
                        'Mo': GetCommandsFromSplitConfig(timePatterns['Mo']),
                        'Dy': GetCommandsFromSplitConfig(timePatterns['Dy'])
                        #'Yr': GetCommandsFromSplitConfig(timePatterns['Yr'])
                        }

        def ChooseSubProcessFunction():
            """
                Custom Function for parsing Loaded file using splitConfig algy and storing results. Meant to be used with LOW to thread
                Example of Complex Split Config to Parse:
                    5-0__.__cluster__0__[__c__cluster__0
                    [{'5': ['.', {'0': ['[', 'c']}, {'0': []}]}]

                    [{'5': ['[encoder.', ']']}]

                    5 = index position of intial Message Chunk
                        '.' = '.' was used to split.
                        nextDataType {} in list indicates the last split resulted in a cluster
                            '0' the index of the cluster which is used for either an ID or further splitting.
                                '[' was split to remove from Chunk
                                'c' was split
                                    nextDataType {} in list as'last split' resulted in a cluster

                CommandsToSplit = [{'index': '5'}, {'split': '.'}, {'index': '0'}, {'split': '['}, {'split': 'c'}, {'index': '0'}]
            """
            def convertDates(toConvert):
                convertTable = {'jan': 1,'feb': 2,'mar': 3,'apr': 4,'may': 5,'jun': 6,'jul': 7,'aug': 8,'sep': 9,'oct': 10,'nov': 11,'dec': 12}
                try:
                    return convertTable[toConvert[0:3].lower()]
                except:
                    return None
            def checkTimeValue(value):
                try:
                    return int(value)
                except:
                    return convertDates(value)

            def processMsgChunk(lastProcess, splitOrders, msgChunk):
                #print ('processMsgChunk msgChunk: %s'%(msgChunk))
                #print ('splitOrders: %s'%(splitOrders))
                
                order = next(i for i in splitOrders)
                #for order in splitOrders:
                if 'index' in order:
                    """
                        msgChunk should type list as we are picking item from list with index val
                    """
                    if (len(splitOrders) -1) > 0:
                        NewsplitOrders = list(splitOrders[1:])
                        #del NewsplitOrders[NewsplitOrders.index(order)]
                        #print ("len of splitOrders indicates more work after index")
                        return processMsgChunk('index', NewsplitOrders, msgChunk[int(order['index'])])
                    else:
                        return msgChunk[int(order['index'])]
                else:
                    if splitOrders.index(order) < len(splitOrders) -1:
                        """Check if there is another order after this split"""
                        if 'index' in splitOrders[splitOrders.index(order)+1]:
                            """
                                If next process is 'index', this split will result in a cluster and index being required

                                This Order will be a cluster creator as index follows this split, do not join after split

                                still more orders to be performed: return value cluster list
                            """
                            #print("Check if there is another order after this split")
                            NewsplitOrders = list(splitOrders[1:])
                            #del NewsplitOrders[NewsplitOrders.index(order)]
                            return processMsgChunk('split',NewsplitOrders, msgChunk.split(order['split']))

                        else:
                            """
                                still more orders to perform on msgChunk returned: return value string
                            """
                            #print ("still more orders to perform on msgChunk returned: return value string")
                            NewsplitOrders = list(splitOrders[1:])
                            #del NewsplitOrders[NewsplitOrders.index(order)]
                            return processMsgChunk('split', NewsplitOrders, ''.join(msgChunk.split(order['split'])))
                    else:
                        """
                            no more orders to perform on msgChunk
                        
                        #print (order)
                        #print (msgChunk)
                        #print (next(e for i,e in order['split'])
                        #return ''.join(next(e for i,e in order['split'].items()))
                        print ("lastProcess: %s" %(lastProcess))
                        print ('order: %s' %(order))
                        print ('msgChunk: %s' %(msgChunk))
                        """
                        return ''.join(msgChunk.split(order['split']))
            def TimeNotInLineSubProcessFunction(LoadedFile):
                pattern = DataPattern
                TimeOrders = TimeCommands
                storage = {}
                Commands = CommandsToSplitList
                GetTimeNext = True
                month = ''
                day = ''
                hour = ''
                minute = ''
                with open(LoadedFile, 'r') as LoadedFile:
                    for line in LoadedFile:
                        if GetTimeNext or timeConfig['pattern'] in line:
                            """
                                time is needed to store future dataPoints
                            """
                            if timeConfig['pattern'] in line:
                                splitLine = line.split(' ')
    
                                month = checkTimeValue(processMsgChunk('split', TimeOrders['Mo'], splitLine))
                                day = checkTimeValue(processMsgChunk('split', TimeOrders['Dy'], splitLine))
                                hour = checkTimeValue(processMsgChunk('split', TimeOrders['H'], splitLine))
                                minute = checkTimeValue(processMsgChunk('split', TimeOrders['M'], splitLine))
                                if not month in storage:
                                    storage[month] = {}
                                if not day in storage[month]:
                                    storage[month][day] = {}
                                if not hour in storage[month][day]:
                                    storage[month][day][hour] = {}
                                if not minute in storage[month][day][hour]:
                                    storage[month][day][hour][minute] = {}
                                GetTimeNext = False
                        else:
                            if pattern in line:
                                splitLine = line.split(' ')
                                
                                for order in Commands:
                                    ID = order['dpID']
                                    tag = order['tag']
                                    data = processMsgChunk('split', order['split'], splitLine)
                                    if not tag in storage[month][day][hour][minute]:
                                        storage[month][day][hour][minute][tag] = {}
                                    if not ID in storage[month][day][hour][minute][tag]:
                                        storage[month][day][hour][minute][tag][ID] = []
                                    if 'chWrk' in order:
                                        """
                                            dataPoint is Tag for 
                                        """
                                        chWrkList = {}
                                        for chWrk in order['chWrk']:
                                            chID = chWrk['dpID']
                                            chWrkList[chID] = processMsgChunk('split', chWrk['split'], splitLine)
                                        storage[month][day][hour][minute][tag][ID].append({data: chWrkList})
                                    else:
                                        storage[month][day][hour][minute][tag][ID].append(data)
                                        
                                    GetTimeNext = True
                    return {pattern: storage}
            def TimeInLineSubProcessFunction(LoadedFile):
                TimeOrders = TimeCommands
                pattern = DataPattern
                storage = {}
                Commands = CommandsToSplitList
                    
                    
                def Process(LoadedFile):
                    for line in LoadedFile:
                        if pattern in line:
                            splitLine = line.split(' ')
                            month = checkTimeValue(processMsgChunk('split', TimeOrders['Mo'], splitLine))
                            day = checkTimeValue(processMsgChunk('split', TimeOrders['Dy'], splitLine))
                            hour = checkTimeValue(processMsgChunk('split', TimeOrders['H'], splitLine))
                            minute = checkTimeValue(processMsgChunk('split', TimeOrders['M'], splitLine))
                            if not month in storage:
                                storage[month] = {}
                            if not day in storage[month]:
                                storage[month][day] = {}
                            if not hour in storage[month][day]:
                                storage[month][day][hour] = {}
                            if not minute in storage[month][day][hour]:
                                storage[month][day][hour][minute] = {}
                            for order in Commands:
                                ID = order['dpID']
                                tag = order['tag']
                                data = processMsgChunk('split', order['split'], splitLine)
                                if not tag in storage[month][day][hour][minute]:
                                    storage[month][day][hour][minute][tag] = {}
                                if not ID in storage[month][day][hour][minute][tag]:
                                    storage[month][day][hour][minute][tag][ID] = []
                                
                                if 'chWrk' in order:
                                    """
                                        dataPoint is Tag for 
                                    """
                                    
                                    #Work Example
                                    # {'dptag': chWrk['dptag'], 'dpID': chWrk['dpID'], 'split': GetCommandsFromSplitConfig(chWrk['sc'])}
                                    chWrkList = {}
                                    for chWrk in order['chWrk']:
                                        chID = chWrk['dpID']
                                        chWrkList[chID] = processMsgChunk('split', chWrk['split'], splitLine).rstrip()
                                    storage[month][day][hour][minute][tag][ID].append({data.rstrip(): chWrkList})
                                else:
                                    storage[month][day][hour][minute][tag][ID].append(data.rstrip())
                                
                                
                                #print ("Appending tag: %s ID: %s with %s" %(tag, ID, data))
                    return {pattern: storage}
                for FType in LoadedFile:
                    if 'zip' in FType:
                        import gzip
                        with gzip.open(LoadedFile[FType], 'r') as ZipFile:
                            return Process(ZipFile)
                    else:                        
                        with open(LoadedFile[FType], 'r') as NonZipFile:
                            return Process(NonZipFile)

            if not TimeCommands['inLine']:
                return TimeNotInLineSubProcessFunction
            else:
                return TimeInLineSubProcessFunction
        return ChooseSubProcessFunction()

    def GetProcessFunction(self, name, config, timeConfig):

        """
            Get Sub Processes
        """
        from multiwork import LotsOfWork,DataSet
        subProcess = {}
        
        for dataPattern in config:
            DataPatternConfig = {dataPattern: []}
            for tag in config[dataPattern]["tag"]:
                for dataPointId in config[dataPattern]["tag"][tag]["dataPoints"]:
                    #for dataPointId in config[dataPattern]["tag"][tag]["dataPoints"][dataPointId]:
                    print ("dataPointId: %s sc: %s"%(dataPointId, config[dataPattern]["tag"][tag]["dataPoints"][dataPointId]))
                    if 'childDataPoints' in config[dataPattern]['tag'][tag]:
                        if dataPointId in config[dataPattern]['tag'][tag]['childDataPoints']:
                            """
                                dataPointIdValue is used as Tag for subsequent dataPoints
                                
                                patterns = {"encoded oid": {"dataPointTags": {"Total Encoded Segs": "Encoder Stats", "oid": "Encoder Stats"}, "tag": {"Encoder Stats": {"childDataPoints": {"oid": {"ids": {"Total Enc Segs": [{"10": ["("]}]}}}, "dataPoints": {"Total Encoded Segs": [{"10": ["("]}], "Bytes Encoded": [{"13": []}], "oid": [{"9": []}]}}}}, 
                                            "encoded with oid": {"dataPointTags": {}, "tag": {"Encode Info": {"dataPoints": {"Encoded File Name": [{"7": []}], "Encoded File Oid": [{"11": []}]}}}}, 
                                            "decoded oid": {"dataPointTags": {}, "tag": {"Decode Stats": {"dataPoints": {"decoded file": [{"29": []}]}}}}}
                            """
                            childWork = []
                            for childDataPoint in config[dataPattern]["tag"][tag]['childDataPoints'][dataPointId]['ids']:
                                childDataPointSc = config[dataPattern]["tag"][tag]['childDataPoints'][dataPointId]['ids'][childDataPoint]
                                childWork.append({'dptag': dataPointId, 'dpID': childDataPoint, 'sc': childDataPointSc})
                            DataPatternConfig[dataPattern].append({'tag': tag, 'dpID': dataPointId, 'sc': config[dataPattern]["tag"][tag]["dataPoints"][dataPointId], 'chWrk': childWork})
                    else:
                        DataPatternConfig[dataPattern].append({'tag': tag, 'dpID': dataPointId, 'sc': config[dataPattern]["tag"][tag]["dataPoints"][dataPointId]})

                    
            subProcess[dataPattern] = {'func': self.GetSubProcessFunction(timeConfig, 
                                                                          DataPatternConfig),
                                      'store': DataSet(dataPattern)}
            """
                return subprocess will require input Loaded File
            """
        def processingFunction(self):
            """
                processing data pattern configuraitions:
                    "write_cache.stats.total_wait_for_buffer_latency:": {"tag": {"Encoder": {}}}

                    "write_cache.stats.total_wait_for_buffer_latency:" -- Data Pattern used to initally located in log file
                    "tag"{"Encoder":{}} is TAG used to identify DataPoints to be used in Root Application
            """
            SubProcessDict = subProcess
            for dataPattern in config:
                
                jobsToProcess = []
                LoadedFilesRef = self.GetLoadedFilesRef()
                print ("LoadedFilesRef in Processing Function: %s" %(LoadedFilesRef))
                if len(LoadedFilesRef['zip']) > 0:
                    for ZipFile in LoadedFilesRef['zip']: # Per File Create JOB for parsing DataPointID in file.
                        jobsToProcess.append({'zip': ZipFile})
                if len(LoadedFilesRef['norm']) > 0:
                    for norm in LoadedFilesRef['norm']:
                        jobsToProcess.append({'norm': norm})
                FunctionToThread = LotsOfWork(len(jobsToProcess), SubProcessDict[dataPattern]['store'], SubProcessDict[dataPattern]['func'])
                for Job in jobsToProcess:
                    FunctionToThread.AddWork(Job)

            print ("Do config stuff on %s for name: %s" %(config, name))

        return {'func': processingFunction, 'subStore': subProcess}

    def GetFileLoadFunction(self, findFilePatterns):
        def LoadFunction(self, locationToSearch):
            """
            Location required to use patterns and build List of files to load & run Processing functions against:
                            {"findFilePatterns":
                                {"1": {"pattern": "rfsctl-a.log", "type": "normal"},
                                 "2": {"pattern": "rfsctl-a.log.*.gz", "type": "zip"}},
            """
            fileDict = {'zip': [], 'norm': []}
            import os
            os.system('rm -f %s/%s_fileList_zip' %(self.ApplicationRef.moduleDir, self.name))
            os.system('rm -f %s/%s_fileList' %(self.ApplicationRef.moduleDir, self.name))
            for PatternNumber in findFilePatterns:  ## {"1": {"pattern": "rfsctl-a.log", "type": "normal"}
                pattern = findFilePatterns[PatternNumber]["pattern"]
                if findFilePatterns[PatternNumber]["type"] == "zip":
                    os.system('find %s -type f | grep "/%s" >> %s/%s_fileList_zip' %(locationToSearch, pattern, self.ApplicationRef.moduleDir, self.name))
                else:
                    print ("NonZip Pattern to Search: %s in dir %s"%(pattern, locationToSearch))
                    os.system('find %s -name %s >> %s%s_fileList' %(locationToSearch, pattern, self.ApplicationRef.moduleDir, self.name))
            for FileToOpen in ['%s/%s_fileList_zip'%(self.ApplicationRef.moduleDir, self.name), '%s%s_fileList'% (self.ApplicationRef.moduleDir, self.name)]:
                with open(FileToOpen, 'r') as fileList:
                    for file in fileList:
                        if 'zip' in FileToOpen:
                            fileDict['zip'].append(file.rstrip())
                        else:
                            fileDict['norm'].append(file.rstrip())
            print (fileDict)
            return fileDict
        return LoadFunction
    def GetLoadedFilesRef(self):
        
        return self.GetLoadedFiles()
        """
        if not self.isFilesLoaded:
            self.LoadedFiles = self.GetLoadedFiles()
            self.isFilesLoaded = True
            return self.LoadedFiles
        else:
            self.LoadedFiles
        """
    def GetLoadedFiles(self):
        """
            Method to open all possible files that match findFilePatterns to be used by processingFunction's for parsing work.
        """
        #LoadedFiles = {}
        return self.fileList
        """
        for FileType in self.fileList:
            if FileType == 'zip':
                import gzip
                for gzipFile in self.fileList['zip']:
                    try:
                        LoadedFiles[gzipFile] = gzip.open(gzipFile, 'r')
                    except:
                        print ("Maybe %s was not a zipped file" %(gzipFile))
                        pass
            else:
                for nonZipFile in self.fileList['norm']:
                    try:
                        LoadedFiles[nonZipFile] = open(nonZipFile, 'r')
                    except:
                        print ("Maybe %s is a zipped file?" %(nonZipFile))
                        pass
        return LoadedFiles
        """


class application(object):
    def __init__(self):
        self.logFiles = {}
        #self.DataPoints {}  tag": {logFileName: dataPoint} 
        self.moduleDir = 'config2/mod/' 
        # TOODOO: Need to make this a variable that can be modified or changed
    def addLogFile(self, name, initFindFileExamples):
        self.logFiles[name] = logFile(self, name, initFindFileExamples)
    def AddDataPoints(tag, dataPoint):
        print ("Add DataPoints")

app = application()
findFile = {"findFilePatterns": {"1": {"pattern": "messages", "type": "normal"}, "2": {"pattern": "message.*.gz", "type": "zip"}}}
app.addLogFile('messages', findFile["findFilePatterns"])
messagesSearchLocation = "/mnt/light/DPEmeaRhlog/tempSysDumpDir/"

test = app.logFiles['messages']
test.UpdateFileList(messagesSearchLocation)

timeConfig = {"Time": {"inLine": True, 
                       "pattern": {"inLine": {"H": [{"2": [":", {"0": []}]}], 
                                              "Mo": [{"0": []}], 
                                              "Yr": None, 
                                              "M": [{"2": [":", {"1": []}]}], 
                                              "Dy": [{"1": []}]}}}
            }
test.UpdateTimeConfig(timeConfig)

patterns = {"encoded oid": {"dataPointTags": {"Total Encoded Segs": "Encoder Stats", "oid": "Encoder Stats"}, "tag": {"Encoder Stats": {"childDataPoints": {"oid": {"ids": {"Total Enc Segs": [{"10": ["("]}]}}}, "dataPoints": {"Total Encoded Segs": [{"10": ["("]}], "Bytes Encoded": [{"13": []}], "oid": [{"9": []}]}}}}, 
            "encoded with oid": {"dataPointTags": {}, "tag": {"Encode Info": {"dataPoints": {"Encoded File Name": [{"7": []}], "Encoded File Oid": [{"11": []}]}}}}, 
            "decoded oid": {"dataPointTags": {}, "tag": {"Decode Stats": {"dataPoints": {"decoded file": [{"29": []}]}}}}}
for pattern in patterns:
    test.AddFunction(pattern, {pattern: patterns[pattern]})

test.ListWorkFuncs()

test.workerFuncs['encoded oid']['func'](test)
test.workerFuncs['encoded with oid']['func'](test)
test.workerFuncs['decoded oid']['func'](test)

import time

while True:
    count = 0
    doneCount = 0
    for SubStoreId in test.workerFuncs['encoded oid']['subStore']:
        count+=1
        if test.workerFuncs['encoded oid']['subStore'][SubStoreId]['store'].finishedLoading:
            doneCount+=1
        print ("ID: %s running: %s"%(SubStoreId, test.workerFuncs['encoded oid']['subStore'][SubStoreId]['store'].finishedLoading))
    for SubStoreId in test.workerFuncs['encoded with oid']['subStore']:
        count+=1
        if test.workerFuncs['encoded with oid']['subStore'][SubStoreId]['store'].finishedLoading:
            doneCount+=1
        print ("ID: %s running: %s"%(SubStoreId, test.workerFuncs['encoded with oid']['subStore'][SubStoreId]['store'].finishedLoading))
    for SubStoreId in test.workerFuncs['decoded oid']['subStore']:
        count+=1
        if test.workerFuncs['decoded oid']['subStore'][SubStoreId]['store'].finishedLoading:
            doneCount+=1
        print ("ID: %s running: %s"%(SubStoreId, test.workerFuncs['decoded oid']['subStore'][SubStoreId]['store'].finishedLoading))
        
        
    if count == doneCount:
        #print (test.workerFuncs['decoded oid']['subStore'][SubStoreId]['store'].DataSetDict)
        for ssID in test.workerFuncs['encoded oid']['subStore']:
            print (test.workerFuncs['encoded oid']['subStore'][ssID]['store'].DataSetDict)
        break
    else:
        time.sleep(5)

"""
    {'subStore': {'Total Encoded Segs': {'store': <multiwork.DataSet object at 0x7fd46e894c90>, 
                                         'func': <function TimeInLineSubProcessFunction at 0x7fd46e823578>}, 
                  'Bytes Encoded': {'store': <multiwork.DataSet object at 0x7fd46e894ed0>, 
                                    'func': <function TimeInLineSubProcessFunction at 0x7fd46e823a28>}, 
                  'oid': {'store': <multiwork.DataSet object at 0x7fd46e82b150>, 
                          'func': <function TimeInLineSubProcessFunction at 0x7fd46e823ed8>}}, 
    'func': <function processingFunction at 0x7fd46e8e1050>}
"""



"""

test.AddFunction('test13', 'testConfig 13')
test.workerFuncs["write_cache.stats.num_bufs_full:"](test)
"""