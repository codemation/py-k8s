class HtmlTable(object):
    def __init__(self, column_list, divId=None, action=None, method=None, ajax = True):
        """ Header """
        #print ("HtmlTable: init - %s - %s - %s - %s"%(divId, action, method, ajax))
        
        # ID's should not have spaces
        if divId is not None:
            if ' ' in divId:
                self.divId = ''.join(divId.split(' '))
            else:
                self.divId = divId
            
        else:
            self.divId = divId
        self.column_list = column_list

        #Title is set to give hoverable description of values header.
        self.column_len = len(self.column_list)
        self.row_list = []
        self.row_list.append(self.column_list)
        self.Footer = True
        self.Header = False
        
        self.action = action
        self.method = method
        self.ajax = ajax        
        
        self.showHide = False
        self.chDivToHide = None
        self.IsHidden = False
        
        self.has_scroll = False
        self.table_bg = False
        self.table_bg_color = 'bgcolor='
        self.width = None
        
        self.Alert = {1: 'bgcolor="f49b42"', #orange
                      2: 'bgcolor="d11f25"', #red
                      3: 'bgcolor="#151c1b"' # Black
                      }
    def SetWidth(self, percent):
        self.width = 'width="%s%%"'%(str(percent))
    
    def AddRow(self, row_data_list):
        if len(row_data_list) != self.column_len:
            return False
        else:
            self.row_list.append(row_data_list)
    def GetFormattedHtml(self):
        return ('\n'.join(self.GetHTML()))
    
    def AddTableBg(self, input_color):
        if input_color in self.Alert:
            self.table_bg_color = self.Alert[input_color]
            self.table_bg = True
        else:
            try:
                self.table_bg_color+= '"%s"' %(str(input_color))
                self.table_bg = True
            except:
                self.table_bg_color = self.Alert[3]
    def divStrip(self,divId):
        """
            cleans divId to ensure html complient divId is set
        """
        def popUnderScore(inDiv):
            if inDiv[0] == '_':
                splitDiv = inDiv.split('_')
            else:
                return inDiv
            toReturn = ''.join(splitDiv[1:])
            if toReturn[0]=='_':
                return popUnderScore(toReturn)
            else:
                return toReturn
        charsNotAllowed = [' ', ':', '.', '(',')', '[',']', '#', ',', '\n']
        if divId is not None:
            for badChar in charsNotAllowed:
                if badChar in divId:
                    divId = '_'.join(divId.split(badChar))
            return popUnderScore(divId) 
    def SetHide(self,divToHide):
        if not self.showHide:
            self.showHide=True
        self.chDivToHide = self.divStrip(str(divToHide))
    def GetHTML(self):
        html_out = []
        """
        if self.has_scroll == True:
            html_out.append('<div class="ex1">') if not self.divId else html_out.append('<div id=%s class="ex1">'%(self.divId))
        else:
        """
        if self.ajax:
            shwHdStr = 'showHideCh' + '(' + "'%s'"%(self.chDivToHide) + ')'
            divToAppend = '<div"' if not self.showHide else '<div ondblclick="%s"'%(shwHdStr)
            html_out.append(divToAppend+'>') if not self.divId else html_out.append(divToAppend+' id="%s" action="%s" method="%s">'%(self.divId,self.action, self.method))
        else:
            html_out.append('<form class="form" action="%s" method="%s">'%(self.action,self.method))
        """
        if self.Footer == True:
            if self.table_bg == True:
                html_out.append('<table id="Footer" %s>' %(self.table_bg_color, 'style="visibility: collapse;"' if self.IsHidden else ''))
            else:            
                html_out.append('<table class="table" %s>'%('style="visibility: collapse;"' if self.IsHidden else ''))
        elif self.Header == True:
            if self.table_bg == True:
                html_out.append('<table %s id="Header" %s>' %(self.table_bg_color, self.width))
            else:
                html_out.append('<table id="Header" %s %s>' %(self.width, 'style="visibility: collapse;"' if self.IsHidden else ''))
        else:
        """
        html_out.append('<table %s %s>' %(self.width,self.table_bg_color)) if self.table_bg else html_out.append('<table %s>' %(self.width))

        for row in self.row_list:
            row_count= 0
            for item in row:
                print (type(item))
                if type(item) == tuple:
                    ## Item has bg color bgcolor="f49b42"
                    if type(item[0]) == HtmlTable:                        
                        if row_count == 0:
                            tr_string = '<tr %s>' %(self.Alert[int(item[1])])
                            html_out.append(tr_string)
                            row_count+=1
                        td_string = '<td>'
                        html_out.append(td_string)
                        GetFromHtmlTable = item.GetHTML()
                        for items in GetFromHtmlTable:
                            html_out.append(items)
                        html_out.append('</td>')
                    else:
                        print ("Non string item in <td> is type: %s" %(type(item)))
                        td_string = '<td>%s</td>' %(str(item[0]))
                        html_out.append(td_string)
                    
                elif type(item) in [HtmlTable, webdiv]:
                    print ("Non string item in <td> is type: %s" %(type(item)))
                    if row_count == 0:
                        html_out.append('<tr>')
                        row_count+=1
                    html_out.append('<td>')
                    GetFromHtmlTable = item.GetHTML() if type(item) == HtmlTable else item.GetHtml()
                    for items in GetFromHtmlTable:
                        html_out.append(items)
                    html_out.append('</td>')        
                else:
                    print ("Non string item in <td> is type: %s" %(type(item)))
                    if row_count == 0:
                        html_out.append('<tr>')
                        row_count+=1
                    html_out.append('<td>%s</td>' %(str(item)))
                
            html_out.append('</tr>')
        html_out.append('</table>')
        if self.ajax==True:
            html_out.append('</div>')
        else:
            html_out.append('</form>')
        return html_out


class colBs(object):
    """
        an object used to format BootStrap HTML elements within <div class="row"> 
        Use Case: Use if objects should follow a grid stacking upon viewport size changes / smaller screens. 
        data: html object, string
    """
    def __init__(self, data, **kwargs):
        self.data = data
        self.params = kwargs
    def getClassForColumn(self):
        toReturnClass = "col"
        #clsOptions = ['size', 'blkcnt', 'align']
        if 'size' in self.params:
            toReturnClass = toReturnClass + "-%s"%(self.params['size'])
        if 'blkcnt' in self.params:
            toReturnClass = toReturnClass + "-%s"%(self.params['blkcnt'])
        if 'align' in self.params:
            toReturnClass = toReturnClass + ' %s'%(self.params['align'])
        return toReturnClass
    def getStyle(self):
        return ' style="%s"'%(self.params["style"]) if "style" in self.params else ""
        
class webdiv(object):
    """
        object created for managing html div items with bootstrap
    """
    def __init__(self, **kwargs):
        self.row_list= []
        self.initKwargs = {}
        for key,value in kwargs.items():
            self.initKwargs[key] = value
    def AddRow(self, col_list):
        """
            col_list should be a list of [colBs objects, or HtmlTable objects]
            use getCol() to create required objects.
        """
        row_to_add = []
        for col in col_list:
            row_to_add.append(col)
        self.row_list.append(row_to_add)
    def getCol(self, data, **kwargs):
        """
            data: html object(webdiv/HtmlTable) or string
        
            **kwargs: Example Inputs
                blkcnt: bootstrap block count this column should take
                size: sm,md,lg 
                align: special alignment or justification
        """
        return colBs(data, **kwargs)
        
    def GetFormattedHtml(self):
        return ('\n'.join(self.GetHtml()))
    def __getRootDiv(self):
            return '<div class="container">' if not "fluid" in self.initKwargs else '<div class="container-fluid">'
    def GetHtml(self):
        html_out = []
        html_out.append(self.__getRootDiv())
        for row in self.row_list:
            html_out.append('  <div class="row">')
            for col in row:
                if type(col) in [webdiv, HtmlTable]:
                    GetFromHtmlObj = col.GetHTML() if type(col) == HtmlTable else col.GetHtml()
                    for item in GetFromHtmlObj:
                        html_out.append(item)
                else:
                    if type(col) == colBs:
                        if type(col.data) in [webdiv, HtmlTable]:
                            GetFromHtmlObj = col.data.GetHTML() if type(col.data) == HtmlTable else col.data.GetHtml()
                            for item in GetFromHtmlObj:
                                html_out.append(item)
                        else:
                            html_out.append('    <div class="%s"'%(col.getClassForColumn()) + col.getStyle() +'>')
                            html_out.append(col.data)
                        html_out.append('    </div>')
                 
            html_out.append('  </div>') # For each row
        html_out.append('</div>') # Closure for container div
        return html_out
        
wDiv = webdiv(fluid=True)

BaseSub = webdiv(fluid=True)
BaseNav = HtmlTable(["NavTable"])

print (BaseNav.GetFormattedHtml())

BaseNav.AddRow(["A Row 1"])
BaseNav.AddRow(["A Row 2"])
SubNav = HtmlTable(["Row3 Col1", "Row3 Col2"])


wDiv2 = webdiv(fluid=True)
wDiv2.AddRow([wDiv.getCol("nest1", blkcnt=6, size='sm', style="background-color:blue;"),
              wDiv.getCol("nest2", blkcnt=6, size='sm', style="background-color:blue;")])


SubNav.AddRow([wDiv2, wDiv2])

BaseNav.AddRow([SubNav])

BaseSub.AddRow([wDiv.getCol("Base Sub", blkcnt=9, size='sm', style="background-color:red;"), BaseNav])



Base = webdiv(fluid=True)


Base.AddRow([BaseSub])

wDiv.AddRow([wDiv.getCol("Base", blkcnt=12, size='sm', style="background-color:yellow;")])
wDiv.AddRow([wDiv.getCol(Base, blkcnt=12, size='sm', style="background-color:yellow;")])

print (wDiv.GetFormattedHtml())







