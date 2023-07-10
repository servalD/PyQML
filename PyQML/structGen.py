import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import QObject, QVariant, pyqtSignal, pyqtProperty, pyqtSlot
import inspect, re, dill, os, sys

print(os.getcwd())
from PyQML.Code import funcLineDeclar, searchAll, privateAttrDeclar, addInheritageDeclar

# Samples code
def getProperty(name, getter=True, setter=True, gCode="", sCode=""):
    getterCode = """
    @pyqtProperty(QVariant, notify=varNameChanged)
    def varName(self):
        #getcode
        return self._varName"""

    setterCode = """
    @varName.setter
    def varName(self, varName):
        if self._varName != varName:
            #setcode
            self._varName = varName
            self.varNameChanged.emit()"""
    ret = ""
    if getter:
        ret+=getterCode.replace("varName", name).replace("#getcode", gCode)
    if setter:
        ret+=setterCode.replace("varName", name).replace("#setcode", sCode)
    return ret

if __name__=="__main__":
    print(getProperty("test", gCode="a=45\
    b=64"))

global SlotCode
SlotCode = """@pyqtSlot(InitVars)
    def varName(self, args):
        self.varNameL.emit(args)
        return None"""
global initVars
initVars = """self._varName = None"""
global newCode
newCode = """def __new__(Cls,*args, **kwargs):
        return super(className, Cls).__new__(Cls,*args, **kwargs)"""
global comClassCode
comClassCode = """class varNameCom(QObject):
    def __init__(self):
        super(QObject, self).__init__()
    def setWorker(self, worker):
        self.worker = worker"""
#

def verifyInterface(code, interface=None):
    if interface==None:
        interface = str(comClassCode)
        code = funcLineDeclar(code, "self.Com.setWorker(self)")# add QObject which stors signals moved on the ui thread
    return code, interface

def toPyqtProperties(code, keyWord="QmlData", interface=None):
    """Convert the given keyWord to self, modify the code to defind pyqtProperty's from sufix name, add setter, getter, notification signal and stored data as "_"+sufixVarName
    
    Keyword Arguments:
        keyWord {str} -- To replace by self in the original code (default: {"QmlData"})
    
    Returns:
        str -- Code result
    """
    if interface!=False:
        code, interface = verifyInterface(code, interface=interface)
        propBase = IPropertyBaseCode
    else:
        propBase = PropertyBaseCode
    properties = []
    # get match objects for each QmlData ocurance
    for match in searchAll(keyWord+r".(?P<property>\w+)", code):
        if not match.group("property") in properties:
            properties.append(match.group("property"))
    properties = list(set(properties))# drop duplicats
    for prop in properties:
        code = funcLineDeclar(code, initVars.replace("varName", prop))# add vars which stors property's values to init
        if interface!=False:
            interface = privateAttrDeclar(interface, PropertyInterfaceCode.replace("varName", prop), "after class")# add signals to the class corp
            interface = privateAttrDeclar(interface, prop+"Changed = pyqtSignal()", "after class")# add signals to the class corp
        code = privateAttrDeclar(code, propBase.replace("varName", prop), "after class")# add signals to the class corp
        code = privateAttrDeclar(code, prop+"Changed = pyqtSignal()", "after class")# add signals to the class corp
        
    code = re.sub(keyWord+r"\.(\w+)", r"self.\1", code)# modify the keyWord to self
    return code, interface



def toPyqtSignals(code, keyWord="Slot", interface=None):
    """Add a signal connected to each methods which have the given keyword in his name and add another signal which is onMethodName and emited sending the method result if return statement.
    
    Arguments:
        code {str} -- Input code to modify
    
    Keyword Arguments:
        keyWord {str} -- Used to find the rights methods to modify (default: {"Slot"})
    
    Returns:
        str -- Code result
    """
    if interface!=False:
        code, interface = verifyInterface(code, interface=interface)
    methods = []
    paramCounts = []
    args = []
    position = []
    # get match objects for each QmlData ocurance
    for match in searchAll(r"(.+)def "+keyWord+r"(?P<name>\w+)\(self(?P<args>.*)\):", code):
        if not match.group("name") in methods:
            position.append(match.start())
            methods.append(match.group("name"))
            paramCounts.append(match.group("args").count(","))
            args.append(match.group("args"))
            if len(args[-1]):
                if args[-1][0]==",":
                    args[-1] = args[-1][1:]
                elif args[-1][0]==" ,":
                    args[-1] = args[-1][2:]
    for j, meth in enumerate(methods):
        # meth = meth[0].upper() + meth[1:]
        inVars = ", ".join(["QVariant" for _ in range(paramCounts[j])])
        virg =", " if inVars!="" else ""
        if interface!=False:
            interface = privateAttrDeclar(interface, SlotCode.replace("varName", meth).replace("keyWord", keyWord).replace("InitVars", inVars).replace("args", args[j]), "after class")# add signals to the class corp
            interface = privateAttrDeclar(interface, meth+"L = pyqtSignal("+inVars+")", "after class")# add signals to the class corp
            interface = privateAttrDeclar(interface, meth+"End = pyqtSignal(QVariant, arguments=['arg'])", "after class")# add signals to the class corp
            interface = funcLineDeclar(interface, "self."+meth+"L.connect(worker."+keyWord+meth+")", "setWorker")# add vars which stors property's values to init
            # interface = funcLineDeclar(interface, "self."+meth+" = worker."+keyWord+meth, "setWorker")# add vars which stors property's values to init

            code = code[:position[j]] + re.sub(r"(.+)(def "+keyWord+r"\w+\({1}.+\):)([\w\W\s\S]+?)(.+)(return )(.+)", r"\1@pyqtSlot("+inVars+virg+r"result=QVariant)\n\1\2\3\4self.Com."+meth+r"End.emit((\6))\n\4\5\6", code[position[j]:], count=1)# only one return suported (func code)
        else:
            code = privateAttrDeclar(code, meth+"End = pyqtSignal(QVariant, arguments=['arg'])", "after class")# add signals to the class corp
            code = code[:position[j]] + re.sub(r"(.+)(def "+keyWord+r"\w+\({1}.+\):)([\w\W\s\S]+?)(.+)(return )(.+)", r"\1@pyqtSlot("+inVars+virg+r"result=QVariant)\n\1\2\3\4self."+meth+r"End.emit((\6))\n\4\5\6", code[position[j]:], count=1)# only one return suported (func code)
    #only one return suported (func code) if no return, all func is shared to modify (anchor to "def" "class" "@" "#"... and end of the script)
    return code, interface

def compileCode(code, objName, glob):
    exec(code, glob)
    return glob[objName]

def toQml(Cls, threaded=True, block=sys.argv[0].endswith(".exe"),glob=globals(), *args, **kwargs):
    """ inerit QObject to the decorated class and add propreties if the of the variable begin by QmlData.myVar = 5 """
    """ should not be already a sub class of QObject!! """
    save=os.path.dirname(sys.argv[0])
    if not block:
        source = dill.source.getsource(Cls)
        # copy data, not the ref # probably
        custom = str(source)
        # get the class name
        className = re.search(r"class (?P<class>.+)\(\w*\):", custom).group("class")
        # inherit of QObject
        custom = addInheritageDeclar(custom, "QObject")
        # add the __new__ func to call __init__ method
        # custom = privateAttrDeclar(custom, newCode.replace("className", className), "after class")# add signals to the class corp
        # print(custom)
        # convert "QmlData.propName" to a pyqtProperty's named propName integrating the notif sign and data storing
        custom, interface = toPyqtProperties(custom, "QmlData", None if threaded else False)
        if interface:
            interface = interface.replace("varName", className)
        # add signals to call the method and another to return the result
        custom, interface = toPyqtSignals(custom, "Slot_", interface)
        if threaded:
            # add interface for threads
            custom = funcLineDeclar(custom, "self.Com = "+className+"Com()")# add QObject which stors signals moved on the ui thread
            # custom = privateAttrDeclar(custom, interface, "after class")
            custom = funcLineDeclar(custom, "super(QObject, self).__init__()")# add to init
            custom = interface+"\n"+custom
        else:
            custom = funcLineDeclar(custom, "super(QObject, self).__init__()")# add to init
        # custom = privateAttrDeclar(custom, "def __call__(self):\n        return self", "after class")
        # print(custom)
        # init the QObject
        if save:
            with open(os.path.join(save, "Gen_pyQML_"+className+".py"), "w") as file:
                file.write(custom)
                # .py file without import statement because it declared on the global scope
        Cls = compileCode(custom, className, glob)

        # ComStructGen(globals(), "I"+className, )
    elif os.path.isfile("Gen_pyQML_"+className):
        with open(os.path.join(save, "Gen_pyQML_"+className+".py"), "r") as file:
            Cls = compileCode(file.read(), className, glob)
        
    return Cls

def ComStructGen( glob, className, *args, **kwargs):
    """ Generate a class inheriting from QObject. Interfacing qml/python by a common property mechanism """
    """ glob should be the current globals dictionary (so just call globals() method) """
    """ className is explicit """
    """ Each args should be a tuple of size 3 like: 
    (varName, 
    defValue (to write in the __init__ declaration eg. label="warning"), 
    raiseNotif (connect the notif to a signal 'changed')) """
    args = list(args)
    if not len(args):
        for key, val in kwargs.items():
            args.append((key, val, True))
    toDictFunc = """\n\n    @pyqtSlot(result=QVariant)
    def toDict(self):
        ret = {"""
    toDictFuncClose = """}
        return ret"""
    toDictData = """'varName': self.varName"""

    initArgsToList = """\n\n    @pyqtSlot(result=list)
    def classAttrs(self):
        return listing
        """

    classCodeStart = """class """+className+"""(QObject):
    changed = pyqtSignal()

    @pyqtSlot(result=QVariant)
    def className(self):
        return '"""+className+"""'
    def __init__(self"""

    classCodeEnd = """, parent=None):
        super("""+className+""", self).__init__(parent)"""

    initVars = """\n        self._varName = varName"""

    raiseNotifCode = """\n        self.varNameChanged.connect(self.changed.emit)"""

    PropertyBaseCode = """\n\n    varNameChanged = pyqtSignal()

    @pyqtProperty(QVariant, notify=varNameChanged)
    def varName(self):
        return self._varName

    @varName.setter
    def varName(self, varName):
        if self._varName != varName:
            self._varName = varName
            self.varNameChanged.emit() """
    
    PropertyAppended = ""
    
    initParamKeyWords = ""
    initParam = ""
    listing = []
    for name, defValue, raiseNotif in args:# iterate each args to write the code
        if defValue==None:# then no keyword
            initParam+= ", "+name
        elif type(defValue)==str and not "'" in defValue:# then add single quotation mark and write it as keyword
            initParamKeyWords+= ", "+name+"="+"'"+defValue+"'"
        elif type(defValue)==str:# should have a single quotation mark eg. given arg "'QObject'" then the code writed: QObject
            initParamKeyWords+= ", "+name+"="+defValue.replace("'", "")
        else:# enithing else 
            initParamKeyWords+= ", "+name+"="+str(defValue)
        classCodeEnd+= initVars.replace( "varName", name)
        if raiseNotif:
            classCodeEnd+= raiseNotifCode.replace( "varName", name)
            toDictFunc+= toDictData.replace( "varName", name) + ", "
        PropertyAppended+= PropertyBaseCode.replace( "varName", name)
        listing.append(name)
    initArgsToList = initArgsToList.replace("listing", str(listing))
    logger.info("Declare generated class '"+className+"'.")
    classCode= classCodeStart + initParam + initParamKeyWords + classCodeEnd + PropertyAppended + toDictFunc + toDictFuncClose + initArgsToList## concat all code parts
    return compileCode(classCode, className, glob)# execut so declare the class in the given globals and then it can be called with the className eg. className='toto'; instance=toto()
    