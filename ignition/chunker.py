
[{'5': '0__[encoder.__]'}]
    
"""
smString = 'Tue Jul 10 08:05:22 GMT 2018 
ManualUpdate[Jul 10 08:05:20]:0eab1b19-d10d-11e7-bf66-0050569b3638 
Operation-Uuid=fd317238-8417-11e8-aede-0050569b3638 
Group=vserver 
Operation-Cookie=6576496499662783491 
action=End 
source=svm_sql2014:vol_db1_logs 
destination=svm_sql2014_DR:vol_db1_logs  
status=Success 
bytes_transferred=217088 
network_compression_ratio=1.0:1 
transfer_desc=Physical Transfer'
            
            

split = 'Jul  9 11:19:270 localhost rfsd[3179]: [encoder.INFO] (3774) 
        encoded oid 0xc8939d (124345 segs with 1048576000 bytes, 
                      124219 new segs with 1047561667 bytes, 
                      126 escape segs with 1014333 bytes, 
                      63 encode calls, 
                      0 slabs avail for ref, 
                      0 slabs used for ref)'
"""
"""
Configure Wizard is meant to take a Data Pattern example pulled against a file using the file search,  pull & confiugre specific data points and location in string.

"""

class Chunk(object):
    def __init__(self, string, ChunkChain, parent):
        self.ChunkChain = '0'
        self.isCluster = False
        if ChunkChain.split('__') == self.ChunkChain.split('__'): # Chain 0
            pass
        else:
            self.ChunkChain = ChunkChain
        
        if parent is not None:
            self.parent = parent
        else:
            self.parent = None
            
        if not type(string) == str:
            if type(string) == list:
                print ("Chunk is cluster")
                self.isCluster = True
                self.clusterList = []
                for clusterItem in string:
                    self.clusterList.append(Chunk(str(clusterItem), str(self.ChunkChain) +'__cluster__%s' %(str(string.index(clusterItem))),self))
                self.string = '%s'%(ChunkChain[len(ChunkChain)-1]).join(string) + ' (cluster)'
        elif type(string) == str:
            self.string = string
            print ("New Chunk string: %s"%(self.string))
        else:
             self.string = "IGNITION ERROR Creating CHUNK"
    def GetChain(self):
        if self.isCluster: # Chunk Is a Cluster
            chainDict = {}
            for chunk in self.clusterList:
                chainDict[self.clusterList.index(chunk)] =  chunk.GetChain()
            return chainDict
        else:
            return self.ChunkChain
    def GetChunkRef(self):
        if self.isCluster: # Chunk Is a Cluster
            chainDict = {}
            for chunk in self.clusterList:
                chainDict[self.clusterList.index(chunk)] =  chunk.GetChunkRef()
            return chainDict
        else:
            return self
            

class StringChunker(object):
    def __init__(self, string):
        self.BaseString = string
        self.BaseChunks = self.BaseString.split(' ')
        self.ChunkList = []
        self.Chunkdir= {}
        self.ChunkChildDir = {} # Dir Dict to track child chunk refs needed for splitting
        self.ChunkDupCheck = {}
        for chunk in self.BaseChunks:
            if chunk in self.ChunkDupCheck:
                #found duplicate
                self.ChunkDupCheck[chunk]['count']+=1
                NewChunk = Chunk(chunk + '     #DUP %d'%(self.ChunkDupCheck[chunk]['count']), '0', None)
                self.ChunkList.append(NewChunk)
                self.ChunkDupCheck[chunk]['dups'].append(self.ChunkList.index(NewChunk))
                self.Chunkdir[self.ChunkList.index(NewChunk)] = NewChunk.string
            else:
                self.ChunkDupCheck[chunk] = {}
                self.ChunkDupCheck[chunk]['count'] = 0
                self.ChunkDupCheck[chunk]['dups'] = [] 
                NewChunk = Chunk(chunk, '0', None)
                self.ChunkList.append(NewChunk)
                self.Chunkdir[self.ChunkList.index(NewChunk)] = NewChunk.string
    def GetChunkDetail(self, msgChunk):
           
            
        def MsgChunkMapBuild(self,msgChunkSplit):
            splitGuide = msgChunkSplit[1].split('__')
            print ("Initial msgChunkSplit: %s" %(msgChunkSplit))
            print ("Directions: %s" %(splitGuide))
            plan = {str(msgChunkSplit[0]): [],
                    'currentIndex': 0}
            index = 0
            nextStepIsIndex = False
            SplitStringIsNext = True
            lastStep = None
            
            for step in splitGuide:
                if index == 0:
                    index+=1
                    continue # Skip root Chunk Reference
                else:
                    if SplitStringIsNext:
                        if 'cluster' in step: # next index will be 
                        # Last Step resulted in a cluster creation
                            nextStepIsIndex = True
                            SplitStringIsNext = False
                            continue
                        if plan['currentIndex'] == 0:
                            plan[str(msgChunkSplit[0])].append(str(step))
                            continue
                        else:
                            plan[str(msgChunkSplit[0])][plan['currentIndex']][lastStep].append(str(step))
                    if nextStepIsIndex:
                        nextStepIsIndex = False
                        print ("this Step will follow a cluster in step of a cluster and is the index of the cluster")
                        NewDictLevel = {str(step): []}
                        lastStep = step
                        if plan['currentIndex'] == 0:
                            plan[str(msgChunkSplit[0])].append(NewDictLevel)
                            plan['currentIndex'] = plan[str(msgChunkSplit[0])].index(NewDictLevel)
                            #SplitStringIsNext = False
                        else:
                            plan[str(msgChunkSplit[0])].append(NewDictLevel)
                            plan['currentIndex'] = plan[str(msgChunkSplit[0])].index(NewDictLevel)
                        SplitStringIsNext = True
                            
            print ("plan: %s" %(plan))
            print ("GetChain: %s" %(self.ChunkList[int(msgChunkSplit[0])].GetChain()))
            #return {'str': self.ChunkList[int(msgChunkSplit[0])].string, 'chain': plan[str(msgChunkSplit[0])]} Changed 1/29 to test different return values
            return {'str': self.ChunkList[int(msgChunkSplit[0])].string, 'chain': plan[str(msgChunkSplit[0])], 'plan': plan}
        
        
        """msgChunk
         0__[encoder.__]
        """
        
        #msgChunk = '2-0__:__cluster__0'
        msgChunkSplit = msgChunk.split('-')
        print (msgChunkSplit)
        
        
        
        
        if ''.join(msgChunkSplit) == str(msgChunk):
            """
                this handles chunk splits which are not in a cluster, root
            
            """
            #msgChunk = '0__[encoder.__]'
            
            msgChunkSplit = [msgChunkSplit[0], self.ChunkList[int(msgChunkSplit[0])].ChunkChain]
            print (MsgChunkMapBuild(self,msgChunkSplit))
            #print (['', '__'.join(msgChunkSplit)])
            #return MsgChunkMapBuild(['', '__'.join(msgChunkSplit)])
            return MsgChunkMapBuild(self,msgChunkSplit)
        else:
            """
                 2-0__:__cluster__0
            """
            return MsgChunkMapBuild(self,msgChunkSplit)
            
            
            
            
    def GetChunkRef(self, plan):
        #levels = int(plan['currentIndex'])
        for BaseIndex in plan:
            if type(BaseIndex) == list:
                ChunkRefs = self.ChunkList[int(BaseIndex)].GetChunkRef()
                
                for ChunkRef in ChunkRefs:
                    if self.GetChunkDetail(ChunkRef.ChunkChain)['chain'][ChunkRef.ChunkChain.split('-')[0]] == plan:
                        print ("Reference matches input plan")
                        return self
                    #DOOO NEXT
    def GetChildChunkInd(self, inputChainId):
        inputId = inputChainId.split('-')[1]
        if inputId in self.ChunkChildDir:
            return self.ChunkChildDir[inputId]
        else:
            print ("GetChildChunkInd called for input: %s" %(inputId))
            print ("Not Found in %s" %(self.ChunkChildDir))
    def GetChildChunkRef(self, inputChainId):
        inputId = inputChainId.split('-')[1]
        if inputId in self.ChunkChildDir:
            return self.ChunkList[self.ChunkChildDir[inputId]]
    def GetBaseInd(self, chunkRef):
        if chunkRef.parent is not None:
            return self.GetBaseInd(chunkRef.parent)
        else:
            return self.ChunkList.index(chunkRef)
        
    def UpdateChunkDirAndList(self, rootBaseIndex, chunkRef, childRef):            
        if chunkRef.isCluster:
            for childChunkRef in chunkRef.clusterList:
                self.ChunkList.append(childChunkRef)
                self.ChunkChildDir[childChunkRef.ChunkChain] = self.ChunkList.index(childChunkRef)
            if childRef is not None:
                #something
                childRef.parent.clusterList[childRef.parent.clusterList.index(childRef)] = chunkRef
                self.ChunkList[self.ChunkList.index(childRef)] = chunkRef
            else:
                self.ChunkList[int(rootBaseIndex)] = chunkRef
                self.Chunkdir[self.ChunkList.index(chunkRef)] = chunkRef.string
        else:
            if childRef is not None:
                print ("This should probably not happen, FIX THIS LATER")
                childRef.parent.clusterList[childRef.parent.clusterList.index(childRef)] = chunkRef
                self.ChunkList[self.ChunkList.index(childRef)] = chunkRef
                print ("Child Reference changed, may need to remove old reference in ChunkChildDir")
                self.ChunkChildDir[chunkRef.ChunkChain]  = self.ChunkList.index(chunkRef)
            else:
                self.ChunkList[int(rootBaseIndex)] = chunkRef
                self.Chunkdir[self.ChunkList.index(chunkRef)] = chunkRef.string
                
        
    def SplitChunk(self, splitStr, rootBaseIndex, childRef):
        ind = rootBaseIndex
        if '#DUP' in self.ChunkList[ind].string: # Split text before '     #DUP 2' entries
            print ("Chunk Before split: %s" %(self.ChunkList[ind].string))
            dupCount = int(self.ChunkList[ind].string[len(self.ChunkList[ind].string)-1])
            duplocalChunkSplit = ''.join(self.ChunkList[ind].string.split('     #DUP %d'%(dupCount)))
            localChunkSplit = duplocalChunkSplit.split(splitStr)
            print ("Chunk After split: %s" %(localChunkSplit))
            print ("%s after join" %(''.join(localChunkSplit)))
        else:
            print ("Chunk Before split: %s" %(self.ChunkList[ind].string))
            localChunkSplit = self.ChunkList[ind].string.split(splitStr)
            print ("Chunk After split: %s" %(localChunkSplit))
            print ("%s after join" %(''.join(localChunkSplit)))
        """
        else: # Handle Child Splits
            if '#DUP' in self.ChunkList[ind].string:
                print ("Chunk Before split: %s" %(self.ChunkList[ind].string))
                dupCount = int(self.ChunkList[ind].string[len(self.ChunkList[ind].string)-1])
                duplocalChunkSplit = ''.join(self.ChunkList[ind].string.split('     #DUP %d'%(dupCount)))
                localChunkSplit = duplocalChunkSplit.split(splitStr)
                print ("Chunk After split: %s" %(localChunkSplit))
                print ("%s after join" %(''.join(localChunkSplit)))
            else:
                print ("Chunk Before split: %s" %(self.ChunkList[ind].string))
                localChunkSplit = self.ChunkList[ind].string.split(splitStr)
                print ("Chunk After split: %s" %(localChunkSplit))
                print ("%s after join" %(''.join(localChunkSplit)))
        """
        
        #clean '' entries
        for item in localChunkSplit:
            if str(item) == '':
                del localChunkSplit[localChunkSplit.index(item)]
        
        chunkstr = ''.join(localChunkSplit)
        if chunkstr in self.ChunkDupCheck:
            #Split String will be a duplicate
            #print ("Split String is not a duplicate")
            self.ChunkDupCheck[str(chunkstr)]['count']+=1
            NewChunk = Chunk(str(chunkstr) + '     #DUP %d'%(self.ChunkDupCheck[str(chunkstr)]['count']), '%s' %(str(self.ChunkList[ind].ChunkChain)) + '__%s'%(str(splitStr)), None)
            self.UpdateChunkDirAndList(ind, NewChunk,childRef)
            #self.ChunkList[ind] = NewChunk
            #self.Chunkdir[self.ChunkList.index(NewChunk)] = NewChunk.string
        else:
            if len(localChunkSplit) > 1:
                print ("Creating Chunk Cluster")
                if childRef is not None:
                    print ("Creating Cluster with parent: childrefChain: %s" %(str(childRef.ChunkChain)))
                    NewChunk = Chunk(localChunkSplit, '%s' %(str(childRef.ChunkChain)) + '__%s'%(str(splitStr)), childRef.parent)
                else:
                    print ("Creating Cluster WITHOUT a parent")
                    NewChunk = Chunk(localChunkSplit, '%s' %(str(self.ChunkList[ind].ChunkChain)) + '__%s'%(str(splitStr)), None)
            else:
                print ("Re Creating chunk after split")
                if childRef is not None:
                    print ("Re Creating chunk after split with parent")
                    NewChunk = Chunk(str(''.join(localChunkSplit)), '%s' %(str(childRef.ChunkChain)) + '__%s'%(str(splitStr)), childRef.parent)
                else:
                    print ("Re Creating chunk after split WITHOUT a parent")
                    NewChunk = Chunk(str(''.join(localChunkSplit)), '%s' %(str(self.ChunkList[ind].ChunkChain)) + '__%s'%(str(splitStr)), None)
            self.UpdateChunkDirAndList(ind, NewChunk,childRef)
            #print ("#1")
            #self.ChunkList[ind] = NewChunk
            #print ("#2")
           # self.Chunkdir[self.ChunkList.index(NewChunk)] = NewChunk.string

"""
ChunkString = "Jul  9 11:18:17 localhost rfsd[3179]: [encoder.INFO] (3789) encoded oid 0xc8939d (124293 segs with 1048576000 bytes, 124167 new segs with 1047576773 bytes, 126 escape segs with 999227 bytes, 63 encode calls, 0 slabs avail for ref, 0 slabs used for ref)"

ChunkIns = StringChunker(ChunkString)

print (ChunkIns.ChunkList)
"""

class ConfigWiz(object):
    def __init__(self, DataPattern):
        # Get String using DataPattern to configure data points.
            #1 Open file using file location
            #2 Grep open file using Data Pattern
            #3 Using a line first found string, Create a StringChunker Instance. 
            #4 Provide capability of specifying a chunk as Data Points with a specific ID orsplit further, 
                #assign ID'd chunks to a Data Point for a particular tag.
        self.something = None
        
        
class DataPoint(object):
    def __init__(self, item, Id, ChunkChain):
        self.config = {'item': item,
                       'Id': Id,
                       'ChunkChain': ChunkChain}
        try:
            self.valueType = type(int(self.config['item']))
        except:
            try:
                self.valueType = type(str(self.config['item']))
            except:
                try:
                    self.valueType= type(self.config['item'])
                except:
                    pass