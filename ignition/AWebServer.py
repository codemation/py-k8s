"""
    A Basic Web Server

"""

import web
from formsmanager import FormMgr
from htmltable import HtmlTable

urls = ('/', 'index',
        '/getsendform', 'GetSendForm',
        '/getposttest/(.*)', 'GetPostTest')
render = web.template.render('template/', base='WebServerLayout')

def GetHtmlOut(session, formMgr, tableName, table):
    BaseTb = HtmlTable([tableName], tableName + '_base')
    xyTable = HtmlTable(['X', 'Y'], tableName + '_data')
    for xOrY in table:
        xyTable.AddRow([xOrY[0], xOrY[1]])
    xyAddToTable = HtmlTable(['Add To Table'], '%s_addTb'%(tableName))
    testTextBox = GlobalFormMgr.GetTextBox('noSession', 'xAddTb', '')
    testTextBox2 = GlobalFormMgr.GetTextBox('noSession', 'yAddTb', '')
    testButton1 = GlobalFormMgr.GetButton('noSession', 'submit', tableName, tableName+'_base', tableName)
    testButton2 = GlobalFormMgr.GetButton('noSession', 'delete', tableName, tableName+'_base', tableName)
    #RenderedForm = GlobalFormMgr.GetRenderedForm('noSession', [testTextBox,testTextBox2, testButton1, testButton2], tableName,'/getposttest/', 'POST', True)
    InputTable = HtmlTable([testTextBox, testTextBox2,  HtmlTable([testButton1,testButton2])], tableName, '/getposttest/', 'POST')
    xyAddToTable.AddRow([InputTable])
    BaseTb.AddRow([xyTable])
    BaseTb.AddRow([xyAddToTable])
    return BaseTb.GetFormattedHtml()


global ASession
ASession = {'ses': 0,
            'fMgr': FormMgr(),
            'tIndex': {'table1': 0,
                       'table2': 1},
            'tables': [
                {'table1': []},
                {'table2': []}
                ]
            }

global GlobalFormMgr
GlobalFormMgr = ASession['fMgr']

"""
class GetJsFile:
    def GET(self, file):
        web.header('Content-Type', "text/javascript")
        return render
"""

class GetSendForm:
    def GET(self):
        ScriptJs =  """
                    <script>
                        function SendForm(){
                        var inputF = $("#test");
                        var formData = new FormData(inputF);
                        var request = new XMLHttpRequest();
                        var target = $("button").value;
                        request.open("POST", $("button").value);
                        request.send(formData);
                        }
                    </script>
                    """ 
        print (ScriptJs)
        return ScriptJs


class index:
    def GET(self):
        toReturn = []
        for table in ASession['tables']:
            for tName in table:
                toReturn.append(GetHtmlOut(ASession['ses'], ASession['fMgr'],tName, table[tName]))
        return render.WebServer(toReturn)
        
class GetPostTest:
    def GET(self, SomeInput):
        print ("Ajax POST request: %s"%(str(SomeInput)))
        return "Ajax GET request: %s"%(str(SomeInput))
    
    def POST(self, SomeInput):
        
        FormInput = GlobalFormMgr.GetFormInputs()
        if FormInput['ButonList']['submit'] is not None:
            tableName = FormInput['ButonList']['submit']
            #'textBoxes': {'xAddTb': 'data1', 'yAddTb': 'data2'}
            tableToEdit = ASession['tables'][ASession['tIndex'][tableName]]
            tableToEdit[tableName].append((FormInput['textBoxes']['xAddTb'], FormInput['textBoxes']['yAddTb']))
            return GetHtmlOut(ASession['ses'], ASession['fMgr'],tableName, tableToEdit[tableName])
        if FormInput['ButonList']['delete'] is not None:
            tableName = FormInput['ButonList']['delete']
            tableToDelete = ASession['tables'][ASession['tIndex'][tableName]]
            tableToDelete[tableName] = []
            return GetHtmlOut(ASession['ses'], ASession['fMgr'],tableName, tableToDelete[tableName])
        
    
if __name__ == "__main__":
    app = web.application(urls,globals())
    app.run()