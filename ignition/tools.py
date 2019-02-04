from dashboard_rev2 import Dashboard
import datetime

class Logger(object):
    def __init__(self, GlobalPID, Module):
        self.Module = Module
        self.pID = GlobalPID
        
    def addLog(self,log):       
        now = str(datetime.datetime.now())
        date = str(now.split(' ')[0])
        time_raw = ''.join(now.split(' ')[1].split(':'))
        time = time_raw.split('.')[0]
        timeDateStr = '%s%s' %(date,time)
        
class PanelMgr(object):
    def __init__(self):
        self.Logger = Logger('9999', 'PanelMgr')
        self.DashBoardExists = False
        self.PanelInstance = type(Dashboard)
        
    def AddPanel(self, Panel):
        self.Logger.addLog("AddPanel called")
        self.PanelInstance = Panel
        self.DashBoardExists = True
        
    def ResetDashboard(self):
        self.PanelInstance.deleteDashboard(self.PanelInstance.title)
        self.DashBoardExists = False
        self.Logger.addLog("ResetDashboard called")

def GetEpoch(Imptime):
    import time
    pattern = '%Y-%m-%d %H:%M:%S'
    print ("Input Time: %s" %(Imptime))
    epoch = int(time.mktime(time.strptime(Imptime.strip(), pattern)))
    print (epoch)
    return epoch*1000

class SendToCarbon(object):
    
    def __init__(self, ToPickle):
        self.Logger = Logger('9999', 'SendToCarbon')
        self.ToPickle = ToPickle
        self.Logger.addLog("Initialized")
    
    def SendToCarbon(self):
        import socket
        import pickle
        import struct
        self.Logger.addLog("SendToCarbon called")
        CARBON_SERVER = '10.216.35.215'
        CARBON_PORT = 2004
        sock = socket.socket()
        sock.connect((CARBON_SERVER, CARBON_PORT))
        for item in self.ToPickle:
            #print (item)
            payload = pickle.dumps(self.ToPickle[item],protocol=2)
            header = struct.pack("!L", len(payload))
            message = header + payload
            sock.sendall(message)
        sock.close()


class GraphData(object):
    """
    Class for Structuring data which will be sent to Graphana.
    path_id is the full identifiable path used, and data is the point which is graphed. 
    """
    def __init__(self):
        self.GraphDataDic = {}
    def AddData(self, path_id, data):
        if not path_id in self.GraphDataDic:
            self.GraphDataDic[path_id] = data


class GraphanaDump(object):
    """
    Graphana DUMP should initialize with a name or add a AddName Method for adjusting value. Will need to be linked with panel creation.
    """
    def __init__(self,Iteration_Length,Case_Number_Loaded):
        self.Logger = Logger('9999', 'GraphanaDump')
        self.Case_Number_Loaded = Case_Number_Loaded #CaseNumber Becoming Serial to allow multiple AVA's & Sysdumps per /case 
        self.Iteration_Length = Iteration_Length
        self.ToPickle = {}
        self.name = 'AltaLog'
        self.ToPickleInd = 0
        self.ToPickle[self.ToPickleInd] = []
        self.AddDataCounter = 0
        self.Logger.addLog("Initialized")
        
    def AddData(self,Imptime, path_id, data):
        self.AddDataCounter+=1
        import time
        pattern = '%Y-%m-%d %H:%M:%S'
        #print (Imptime)
        try:
            epoch = int(time.mktime(time.strptime(Imptime.strip(), pattern)))
            path_name = '%s_%s.%s_Min.%s'%(self.name,self.Case_Number_Loaded,self.Iteration_Length,path_id)
        except ValueError:
            self.Logger.addLog("AddData failed for path_id %s"%(path_id))
            return
        #print (path_name)
        if len(self.ToPickle[self.ToPickleInd]) + len((path_name,(epoch, data))) < 5072:     
            self.ToPickle[self.ToPickleInd].append((path_name,(epoch, data)))
        else:
            self.ToPickleInd+=1
            self.ToPickle[self.ToPickleInd] = []
            self.ToPickle[self.ToPickleInd].append((path_name,(epoch, data)))