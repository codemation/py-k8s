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
        
        self.TitleDict = {}
        self.HasTitle = False
        for item in column_list:
            if type(item)==tuple:
                #Item has Title description for hover over message
                self.TitleDict[item[0]] = item[1]
                self.HasTitle = True
        
        if self.HasTitle == False:        
            self.column_list = column_list
        else:
            striped_column_list = []
            for item in column_list:
                if type(item) == tuple:
                    striped_column_list.append(item[0])
                else:
                    striped_column_list.append(item)
            self.column_list = striped_column_list
        #Title is set to give hoverable description of values header.
        self.column_len = len(self.column_list)
        self.row_list = []
        self.row_list.append(self.column_list)
        self.Footer = False
        self.Header = True
        
        self.action = action
        self.method = method
        self.ajax = ajax        
        
        self.has_scroll = False
        self.table_bg = False
        self.table_bg_color = 'bgcolor='
        self.width = 'width="100%%"'
        
        self.Alert = {1: 'bgcolor="f49b42"', #orange
                      2: 'bgcolor="d11f25"', #red
                      3: 'bgcolor="#151c1b"'
                      }
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
            

    def GetHTML(self):
        html_out = []
        if self.has_scroll == True:
            html_out.append('<div class="ex1">') if not self.divId else html_out.append('<div id=%s class="ex1">'%(self.divId))
        else:
            if self.ajax:
                html_out.append('<div>') if not self.divId else html_out.append('<div id="%s" action="%s" method="%s">'%(self.divId,self.action, self.method))
            else:
                html_out.append('<form class="form" action="%s" method="%s">'%(self.action,self.method))

        if self.Footer == True:
            if self.table_bg == True:
                html_out.append('<table %s %s id="Footer">' %(self.table_bg_color))
            else:            
                html_out.append('<table %s id="Footer">')
        elif self.Header == True:
            if self.table_bg == True:
                html_out.append('<table %s id="Header" %s>' %(self.table_bg_color, self.width))
            else:
                html_out.append('<table id="Header" %s>' %(self.width))
        else:
            html_out.append('<table %s %s>' %(self.width,self.table_bg_color)) if self.table_bg else html_out.append('<table %s>' %(self.width))

        for row in self.row_list:
            row_count= 0
            for item in row:
                if type(item) == tuple:
                    ## Item has bg color bgcolor="f49b42"
                    if type(item[0]) == HtmlTable:                        
                        if row_count == 0:
                            tr_string = '<tr %s>' %(self.Alert[int(item[1])])
                            html_out.append(tr_string)
                            row_count+=1
                        td_string = '<td %s>' %(self.Alert[int(item[1])])
                        html_out.append(td_string)
                        GetFromHtmlTable = item.GetHTML()
                        for items in GetFromHtmlTable:
                            html_out.append(items)
                        html_out.append('</td>')
                    else:
                        td_string = '<td %s>%s</td>' %(self.Alert[int(item[1])], str(item[0]))
                        html_out.append(td_string)
                    
                elif type(item) == HtmlTable:
                    if row_count == 0:
                        html_out.append('<tr>')
                        row_count+=1
                    html_out.append('<td>')
                    GetFromHtmlTable = item.GetHTML()
                    for items in GetFromHtmlTable:
                        html_out.append(items)
                    html_out.append('</td>')
                        
                    
                else:
                    if row_count == 0:
                        html_out.append('<tr>')
                        row_count+=1
                    html_out.append('<td %s>%s</td>' %(str(self.Alert[3]), str(item)))
                
            html_out.append('</tr>')
        html_out.append('</table>')
        if self.ajax==True:
            html_out.append('</div>')
        else:
            html_out.append('</form>')
        return html_out