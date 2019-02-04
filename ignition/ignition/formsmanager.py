from web import form
from web import template
from htmltable import HtmlTable

class FormMgr(object):
    """
        Manager object for creating & processing forms  
    """
    def __init__(self):
        self.TextBoxList = []
        self.ButtonList = []
        self.DropdownList = []
        self.CheckBoxList = []
        self.divGetHtml = {}
                
        self.render2 = template.render('template/')
        
    def GetHtmlTable(self, NewHtmlTable, divId=None, action=None, method=None, ajax = True):
        table = HtmlTable(NewHtmlTable, divId, action, method, ajax)
        if divId is not None:
            if ' ' in divId:
                divId = ''.join(divId.split(' '))
                self.divGetHtml[divId] = table.GetFormattedHtml
            else:
                self.divGetHtml[divId] = table.GetFormattedHtml
        return table
    def reset_forms(self):
        self.TextBoxList = []
        self.ButtonList = []
        self.DropdownList = []
        self.CheckBoxList = []
        self.divGetHtml = {}
    
    def GetFormInputs(self):
        """
            returns forms with input values
        """
        forms = {'textBoxes': {},
         'ButonList': {},
         'DropdList': {},
         'CheckList': {}}
        
        def IsNull(v):
           return True if (v is None) or (v is '') or (v is u'') else False

        
        TextBoxListDict = {}
        for TextBoxGroup in [self.TextBoxList]:
            for TextBoxFormName in TextBoxGroup:
                TextBoxListDict[TextBoxFormName.rstrip()] = form.Form(form.Textbox(TextBoxFormName.rstrip()))
                print ("Creating Instance for validation: %s" %(TextBoxFormName))
                textBoxIns = TextBoxListDict[TextBoxFormName.rstrip()]()
                if not textBoxIns.validates():
                    print ("Not Valid")
                else:
                    #print ("Form values: %s" %(textBoxIns.d))
                    for item in textBoxIns.d:
                        if not IsNull(textBoxIns.d[item.rstrip()]):
                            print ("Input Not empty: %s" %(textBoxIns.d[item]))
                            forms['textBoxes'][str(item.rstrip())] = str(textBoxIns.d[item]) if textBoxIns.d[item] is not None else textBoxIns.d[item]
        DropDListDict = {}        
        for DropdListFormName in self.DropdownList:
            DropDListDict[DropdListFormName] = form.Form(form.Dropdown(DropdListFormName,[]))
            tempIns = DropDListDict[DropdListFormName]()
            if not tempIns.validates():
                pass
            else:
                for item in tempIns.d:
                    if not IsNull(tempIns.d[item]):
                        print ("DropDown Input Not empty: %s" %(tempIns.d[item]))
                        forms['DropdList'][item] = str(tempIns.d[item]) if tempIns.d[item] is not None else tempIns.d[item]
        ButonListDict = {}
        for ButonBoxGroup in [self.ButtonList]:
            for ButonListFormName in ButonBoxGroup:
                ButonListDict[ButonListFormName.rstrip()] = form.Form(form.Button(ButonListFormName.rstrip()))
            #for ButonListFormName in ButonListDict:
                tempIns = ButonListDict[ButonListFormName.rstrip()]()
                if not tempIns.validates():
                    pass
                else:
                    for item in tempIns.d:
                        if not IsNull(tempIns.d[item.rstrip()]):
                            print ("Input Not empty: %s" %(tempIns.d[item]))
                            forms['ButonList'][str(item.rstrip())] = str(tempIns.d[item.rstrip()]) if tempIns.d[item.rstrip()] is not None else tempIns.d[item.rstrip()]
        CheckListDict = {}
        for CheckBoxGroup in [self.CheckBoxList]:
            for CheckBoxFormName in CheckBoxGroup:
                CheckListDict[CheckBoxFormName.rstrip()] = form.Form(form.Checkbox(CheckBoxFormName.rstrip()))
            #for ButonListFormName in ButonListDict:
                tempIns = CheckListDict[CheckBoxFormName.rstrip()]()
                if not tempIns.validates():
                    pass
                else:
                    for item in tempIns.d:
                        if not IsNull(tempIns.d[item.rstrip()]):
                            print ("Input Not empty: %s" %(tempIns.d[item]))
                            forms['CheckList'][item.rstrip()] = (tempIns.d[item.rstrip()])
        print (forms)
        return forms
        
        
        
                
    def GetRenderedForm(self,session, Forms, divId, target, PostOrGet, AJAX=False):
        """
        required input
            .GetRenderedForm(session, Forms, divId, target, PostOrGet)
            
        returns a form in raw rendered html
        input Forms should be rendered
        
        target - target of form submission
        divId - used by JS AJAX scripts to check child input 
        PostOrGet - type of HTML Request made when form submission.
        
        """
        if not type(Forms) == list:
            Forms = [Forms]
        if type(Forms == HtmlTable):
            pass
        else:
            for item in Forms:
                if 'web.form' in str(type(item)):
                    Forms[Forms.index(item)] = item.render()
        if AJAX:            
            return self.render2.formMgr(str(session), Forms, divId, str(target), PostOrGet, 0)
        else:
            return self.render2.formMgr(str(session), Forms, divId, str(target), PostOrGet, 1)
        
        
    def GetButton(self, session, name, parentDivId, divToChange, buttonValue):
        """
        required input
            .GetButton(session, name, iD, target_config)
        """

        
        
        ButtonValue = buttonValue.rstrip()
        if not parentDivId == None:
            # ID's parentDivId not have spaces
            if ' ' in parentDivId:
                parentDivId = ''.join(parentDivId.split(' '))
            if ' ' in name:
                ButtonId = ''.join(name.split(' '))
            else:
                ButtonId = name
                
            
            
            if not divToChange == None:
                if ' ' in divToChange:
                    divToChange = ''.join(divToChange.split(' '))
                ActionButton = form.Button("%s" %(name.rstrip()), id="%s"%(ButtonId), onclick="SendForm('%s', '%s', '%s')"%(parentDivId, name, divToChange), value=ButtonValue, target=str(session), style="width:100%")
        else:
            ActionButton = form.Button("%s" %(name.rstrip()), value=ButtonValue, target=str(session), style="width:100%")

        self.ButtonList.append(name.rstrip())
        return ActionButton.render()
    def GetCheckBox(self, session, name, isChecked):
        """
        required input
            .GetCheckBox(session, name, isChecked)
        """
        CheckBox = form.Checkbox(name, value=name+'-%s'%(str(session.rstrip())), checked=isChecked)
        self.CheckBoxList.append(name.rstrip())
        return CheckBox.render()
    def GetTextBox(self, session, name, currentValue):
        """
        required input
            .GetTextBox(session, name, currentValue)
        
        """
        TextBox = form.Textbox("%s" %(name.rstrip()),value=currentValue.rstrip() if type(currentValue) == str else currentValue)
        if not name.rstrip() in self.TextBoxList:
            self.TextBoxList.append(name.rstrip())
        return TextBox.render()
    def GetDropdown(self, session, name, choices, currentValue):
        """
        required input:
            GetDropdown(self, session, name, choices, currentValue):
                
        currentValue - drop down to prepopulate when viewed.
        choices      - a list used by drop-down, list should be tuples of (name,value) or {name, value}.
        """
        choiceList = []
        for item in choices:
            if type(item) == dict:
                print ("FormMGr GetDropdown, item is dict: %s"%(item))
                for name in item:
                    choiceList.append((str(name),str(item[name])))
                    #currentValue = (name,item[name])
            else:
                choiceList.append((str(item),str(item)))
        DropDownV = form.Dropdown(str(name.rstrip()), choiceList, value=str(currentValue))
        self.DropdownList.append(name.rstrip())
        return DropDownV.render()    
