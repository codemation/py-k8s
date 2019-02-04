"""
    htmlforms
"""

class label:
    """
        name: String visible & describing form.
        label_of: target id which this is labeled of.         
    
        used by forms to describe form input,
        label_of - id this label describes
        
        default: class="control-label col-sm-2", can be modified by input kwargs
        
        **kwargs: 
            class: control-label, 
            size: lg,md,sm
            blk: value out of 12
    """
    def __init__(self, name, targetForm, kw):
        print (kw)
        self.bsClass = self.__getClass(kw)
        self.Id = name if not 'id' in kw else kw['id']
        self.dispname = name
        self.inline = False if not 'inline' in kw else kw['inline']
        self.targetForm = targetForm['p']
        self.childElements = targetForm['c']
        
    def __getClass(self,inKws):
        defClass = 'class="control-label col-sm-2"'
        defClass = 'class="%s"'%(inKws['class']) if 'class' in inKws else defClass
        if "size" in inKws:
            defClass = ' '.join([defClass.split(' ')[1], 'col-%s-%s'%(inKws['size'], inKws['blk'] if 'blk' in inKws else str(2))])
        if "blk" in inKws:
            if not "size" in inKws:
                defClass = 'class="control-label col-sm-%s"'%(inKws['blk'])
        return defClass
    def parentAndChild(self, toAppend):
        toAppend.append(self.targetForm)
        if len(self.childElements) > 0:
            for child in self.childElements:
                toAppend.append(child)
        return toAppend
    def wrapped_html(self, isHidden):
        if isHidden is not True:
            """
            if self.inline is False:
                return ['<label {lblcls} for="{htmlId}">'.format(lblcls=self.bsClass, htmlId=self.Id), 
                        '{form}'.format(form=self.targetForm),
                        '{name}</label>'.format(name=self.dispname)]
            """
            if self.inline is False:
                return self.parentAndChild(['<label {lblcls} for="{htmlId}">'.format(lblcls=self.bsClass, htmlId=self.Id) + 
                        '{name}</label>'.format(name=self.dispname)])
            else:
                print ("label is InLine")
                toReturn = '<label {lblcls} for="{htmlId}">'.format(lblcls=self.bsClass, htmlId=self.Id)
                parAndChild = self.parentAndChild([])
                for pc in parAndChild:
                    toReturn = toReturn + pc
                toReturn = toReturn + '{name}</label>'.format(name=self.dispname)
                return [toReturn]
        else:
            return self.parentAndChild([])

class Input:        
    def __processKw(self,otherProp=None):
        lookFor = ['label', 'class', 'id', 'value', 'disabled', 'name', 'type']
        if otherProp is not None:
            for item in otherProp:
                lookFor.append(item)
        hasValues = []
        for prop in lookFor:
            if prop in self.kw:
                hasValues.append(prop)
        if not 'id' in hasValues:
            hasValues.append('id')
            self.kw['id'] = self.dispname
            self.label['id'] = self.dispname
        return hasValues
    def getProperties(self):
        propToRet = ''
        customLabel = False
        for prop in self.__processKw(self.formSpecial):
            if prop == 'label':
                customLabel = True
            else:
                propToRet = propToRet + '%s="%s" '%(prop, self.kw[prop])
        return propToRet, customLabel
        
    def labelWrap(self, hasCustomLabel, inputText):
        lbl = self.kw['label'] if hasCustomLabel is True else self.label
        return label(self.dispname if not 'name' in lbl else lbl['name'],
                     {'p': inputText, 'c': self.elementChildren},
                     lbl).wrapped_html(self.hideLabel)
    def setInitVars(self, name, kw, label, frmSpec):
        """
            name - sets form name - type str
            kw - kw var inputs to parent form - type {}
            label - type {'default': True, 'class': 'form-check-label'}
            frmSpec - list input [] can be used by form init to set value
        """
        self.dispname = name
        self.kw = kw
        self.label = label
        self.hideLabel = False if not 'lblhidden' in kw else kw['lblhidden']
        self.formSpecial = frmSpec
        self.elementType = 'input' # default type for input objects, other possible is 'select'
        self.elementChildren = [] # elements within input object, to be added when labelWrap() is called.
        
    def html(self):
        toReturn = ['<div class="%s">'%(self.cName)]
        properties, hasCustomLabel = self.getProperties()
        inputText = '<%s type="%s" %s >'%(self.elementType, self.cName if not self.cName == 'button' else 'submit',properties)
        for retItems in self.labelWrap(hasCustomLabel, inputText):
            toReturn.append(retItems)
        if not self.elementType == 'input':
            toReturn.append('</%s>'%(self.elementType))
        toReturn.append('</div>')
        return toReturn
        
class check_box(Input):
    def __init__(self, dispname, **kw):
        """
            see .setInitVars description
        """
        self.cName = 'checkbox'
        self.setInitVars(dispname, kw, {'default': True, 'class': 'form-check-label'}, ["checked", 'oncheck'])
class text_box(Input):
    """
        use type="password" for *** input,
            "email" for email input
    """
    def __init__(self, dispname, **kw):
        self.cName = 'text'
        self.setInitVars(dispname, kw, {'default': True, 'class': 'form-check-label'}, ["type", # Type = Password for *** input
                                                                                    "email"])
class radio(Input):
    def __init__(self, dispname, **kw):
        self.cName = 'radio'
        self.setInitVars(dispname, kw, {'default': True, 'class': 'form-check-label'}, ["checked"])
    
class button(Input):
    """
        style - 
            https://getbootstrap.com/docs/4.0/components/buttons/ for color styles
            color - default btn btn-primary. Other options: secondary, success, danger, warning, info, light
        size - 
            options: lg,md,sm,xs, block(spans entire block)
        label - 
            default: hidden use lblhidden = False to show
        Example:
            aButton= button("b1", value="b1")
            aButton.setActionOnClick('showHide', None,'b1-div')
            print ('\n'.join(aButton.html()))
            Output:
            <div class="button">
                <input type="button" class="btn active" value="b1" onclick="showHideCh(b1-div)" id="b1"  >
            </div>
    """
    def __init__(self, dispname, **kw):
        self.cName = 'button'
        self.disp = dispname
        addBtnCls = kw
        addBtnCls['class'] = 'btn btn-'+ kw['style'] if 'style' in kw else 'btn'
        addBtnCls['class'] = addBtnCls['class'] +' btn-' + kw['size'] if 'size' in kw else addBtnCls['class']
        addBtnCls['class'] = addBtnCls['class'] + ' active' if not 'disabled' in kw else addBtnCls['class'] + ' disabled'
        #Default buttons should appear without label
        addBtnCls['lblhidden'] = True
        # addBtnCls is input with addtion of class=btn or custom values
        self.setInitVars(dispname, addBtnCls, {'default': True, 'class': 'form-check-label'}, ['onclick'])
    def setActionOnClick(self, action, id_of_FormToSubmit, target):
        """
            action: submit(send form data for id) or showHide(collapse / show target id)
        """
        if action is 'submit':
            print ("added submit action")
            self.kw['onclick'] = 'SendForm(%s, %s, %s)'%(id_of_FormToSubmit, self.disp, target)
        elif action == 'showHide':
            self.kw['onclick'] = 'showHideCh(%s)'%(target)
        else:
            pass
class select(Input):
    """
        style:
            https://getbootstrap.com/docs/4.0/components/input-group/#custom-select
            default: form-control, Other options: "custom-select"
        Use: 
            options=[<optionList>] for drop down selections. 
        Example:
            select("select 1", name="b1", options=['1','2','3','4'], label={'blk': 2})
            print ('\n'.join(select("select 1", name="b1", options=['1','2','3','4'], label={'blk': 2}).html()))
            Output:
                <div class="select">
                    <label class="control-label col-sm-2" for="select 1">select 1</label>
                    <select type="select" class="form-control" name="b1" id="select 1"  >
                        <option>1</option>
                        <option>2</option>
                        <option>3</option>
                        <option>4</option>
                    </select>
                </div>
    """
    def __init__(self, dispname, **kw):
        self.cName = 'select'
        
        addSelCls = kw
        addSelCls['class'] = "form-control" if not 'cstm_cls' in kw else kw['cstm_cls']
        
        self.setInitVars(dispname, kw, {'default': True}, None)
        self.elementType = 'select'
        if 'options' in kw:
            for opt in kw['options']:
                self.elementChildren.append('<option>%s</option>'%(opt))                

class htmlelement(object):
    def initParamItems(self, kw):
        self.options = '' if not 'options' in kw else kw['options']
        self.items = kw['items'] if 'items' in kw else []
    def getChildHtml(self, toReturn):
        localRet = toReturn
        for item in self.items:
            itemIns = item.html()
            if itemIns is not None:
                for itemInsItem in itemIns:
                    localRet.append(itemInsItem)
        return localRet
    def printOp(self):
        retOps = ''
        for op in self.options:
            retOps = retOps + ' %s'%(op)
        return retOps
    def add_item(self, item):
        self.items.append(item)

class col(htmlelement):
    """
        colums(vertical) which contain html elements such as form inputs(select, check_box, text_box, button, radio)
        id - position in parent row. 
        input params='' as an argument for addtional class options. Example column('id1', None, blk=2, params="form-group")
    """
    def __init__(self, colId, parentRowRef, **kw):
        self.id = colId
        self.size = 'md' # Default size is medium
        self.blk = '2' if 'blk' not in kw else kw['blk'] # Default blk cnt is 2
        self.initParamItems(kw)
    def html(self):
        toReturn = self.getChildHtml(['<div class="col-%s-%s %s" >'%(self.size, self.blk, self.printOp())])
        toReturn.append('</div>')
        return toReturn
        
class row(htmlelement):
    def __init__(self, rowId, parentItemRef, **kw):
        self.id = rowId
        self.align=None
        self.initParamItems(kw)
    def add_col(self, col):
        self.columns.append(col)
    def ins_col(self, col, index):
        """
            insert column object at specified row index
        """
        tempCol = []
        if len(self.columns) >= index:
            for item in self.columns[:index]:
                tempCol.append(tempCol)
            tempCol.append(col)
            for item in self.columns[index:]:
                tempCol.append(item)
        self.columns = tempCol
    def html(self):
        toReturn = self.getChildHtml(['<div class="row %s %s" >'%(self.align if self.align is not None else '', self.printOp())])
        toReturn.append('</div>')
        return toReturn
    
        
class form(htmlelement):
    """
        a form object is a combination of rows & columns. Each row cotains columns. 
        
        Example:
        In:
            aForm = form('fId1', options=['target="/formHandler"', 'method="POST"'])
        Out:
            <form  target="/formHandler" method="POST">
                
            </form>
    """
    def __init__(self, frmId, **kw):
        self.id = frmId
        self.initParamItems(kw)
    def html(self):
        """
            something
        """
        toReturn = self.getChildHtml(['<form id="%s" %s>'%(self.id, self.printOp())])
        toReturn.append('</form>')
        return toReturn

#aForm = form('fId1', options=['target="/formHandler"', 'method="POST"'])
    
class container(htmlelement):
    """
        basic bootstrap delement required for grid / block system.
        
        kw args:
            fluid=True, will result in container spanning entire row block
        
    """
    def __init__(self, **kw):
        self.fluid = kw['fluid'] if 'fluid' in kw else False
        self.initParamItems(kw)
    def html(self):
        toReturn = self.getChildHtml(['<div class="%s">'%('container' if self.fluid is False else 'container-fluid')]) ## Toodoo - add options
        toReturn.append('</div>')
        return toReturn
"""    
aSideBar = col('sidebar', # Id of sidebar
                None, # No parent Ref
                items=[row('sidebar-r1', None,items=[text_box('a text box', value="")]),
                       row('sidebar-r2', None,items=[button('button b', value="button b")]),
                       row('sidebar-r3', None,items=[button('button c', value="button c")]),
                       row('sidebar-r4', None,items=[button('button d', value="button d")])],
                blk=4)
"""
class sidebar(htmlelement):
    """
        A side bar is a vertical column object and thus should be used inside a row object
    """
    def __init__(self, **kw):
        self.id = kw['id'] if 'id' in kw else 'sidebar-default'
        self.blk = '4' if 'blk' not in kw else kw['blk'] # Default blk cnt is 4
        self.fixed = True
        self.initParamItems(kw)
    def html(self):
        rowItems = []
        for item in self.items:
            rowItems.append(row('%s-%s'%(self.id, self.items.index(item)), None, items=[item]))
        colObj = col('%s'%(self.id), None,items=rowItems, blk=self.blk)
        return colObj.html()
        
#aSideBar = sidebar(items=[text_box('a text box', value=""), button('button a', value="button a"), button('button b', value="button b"), button('button c', value="button c")])
    

class header(htmlelement):
    """
        Large Text appearing in various different size depending on provided size
        headerText - Large Text to Appear 
        size - 1 = <h1>Text</h1> 
               2 = <h2>Text</h2>
               3 = <h3>Text</h3>
    """
    def __init__(self, headerText, size, **kw):
        self.headerText = headerText
        self.size = size
        self.initParamItems(kw)
    def html(self):
        toReturn = ['<div class="page-header">']
        toReturn.append('<h%s>%s</h%s>'%(self.size,self.headerText,self.size))
        toReturn.append('</div>')
        return toReturn

class navbar(htmlelement):
    """
        barType - type options (top / bottom / right / left )
        options:
            fixed-top
            fixed-bottom
        
        <nav class="navbar navbar-inverse navbar-fixed-top">
          <div class="container-fluid">
            <div class="navbar-header">
              <a class="navbar-brand" href="#">WebSiteName</a>
            </div>
            <ul class="nav navbar-nav">
              <li class="active"><a href="#">Home</a></li>
              <li><a href="#">Page 1</a></li>
              <li><a href="#">Page 2</a></li>
              <li><a href="#">Page 3</a></li>
            </ul>
          </div>
        </nav>    
    """
    def __init__(self, iD, barType, **kw):
        self.id = iD
        self.barType = barType
        self.background = 'navbar-inverse'
        self.header = kw['header'] if 'header' in kw else None
        self.initParamItems(kw)
    def _processOptions(self,inOptions):
        if inOptions is None:
            return ''
        else:
            returnOptions = ''
            for opt in inOptions:
                returnOptions = returnOptions + ' navbar-%s '%(opt)
    def html(self):
        toReturn = ['<nav class="navbar %s %s">'%(self.options,self.background),
                        '<div class="container-fluid">']
        if self.header is not None:
            toReturn.append('<div class="navbar-header">')
            toReturn.append(self.header.html())
            toReturn.append('</div>')
        toReturn.append('<ul class="nav navbar-nav">')
        toReturn = self.getChildHtml(toReturn)
        toReturn.append('</ul>')
        toReturn.append('</div>')
        toReturn.append('</nav>')
        return toReturn

## Side Bar
        