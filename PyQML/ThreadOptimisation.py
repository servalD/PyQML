# Autor: serval7391@gmail.com
# Creation date: 25/07/2019

from PyQt5.QtCore import QObject, pyqtSlot, QVariant, QUrl, pyqtSignal, QThread, pyqtProperty, QAbstractListModel
from enum import Enum
from .structGen import ComStructGen
import logging
# logging.basicConfig(format="%(levelname)-s - %(filename)-s %(lineno)-s in %(funcName)s(): %(message)s", level=logging.ERROR)
logger = logging.getLogger(__file__)

## Manage QObjects and QThreads and the access to specified slot (by signal), and pyqtPropertys
class ThreadManager(QObject):
    """Implement a methode to return a QObject interface containing all signals coressponding to each spesified pyqtSlots and pyqtPropertys, for access to it from diferent QThreads
    Manage QObjects in less of QThreads that one by QObject

    Inherite:
        QObject
    """
    ## QObject attachement modes
    AFFINITY_AUTO = 0
    AFFINITY_DEDICATED = 1

    def __init__(self, ctx):
        super(QObject, ThreadManager).__init__(self)
        ## Maximum number of QThread instances. This value is incremented by 1 add() with ATTACHEMENT = DEDICATED
        self._autoTh_count = 1
        ## List of QObjects instances which ones are attached to his _QObjectsMap QObject instance
        ## This is to prevent slots and propertys access violations if _QObjectsMap QObjects instances are not attached to the same QThread
        self._InterfacesMap = {}
        ## QObject names dict
        self._QObjectsMap = {}
        ## QThread names dict
        self._QThreadMap = {}
        ## QThread affinity map of these QObject affinity names
        self._QThreadAffinitys = {}
        ## qml context
        self.ctx = ctx
        self.processAffinitys()

    def _getDefaultsThreadsNames(self):
        return [name for name in self._QThreadMap if "-a " in name]
    ## read only property which return the list of QTheads name dedicated to the automatic mechanism
    defaultsThreadsNames = property(_getDefaultsThreadsNames)

    def __getitem__(self, name):
        if hasattr(self._QObjectsMap[name], "Com"):
            return self._QObjectsMap[name].Com
        else:
            return self._QObjectsMap[name]
    
    def getThreadOf(self, objName):
        """ Return the thread name where is running the give objectName """
        for tname, affinitys in enumerate(self._QThreadAffinitys):
            if objName in affinitys:
                return tname

    ## Find the minimum QObj count of each QThread and assign to it
    def _addAutoAffinity(self, objName):
        """ Move the given object (by name) to the thread which have the minimum QObject affinity's """
        mini = 9999
        threadNames = []
        for _, (name, count) in enumerate({_name: len(self._QThreadAffinitys[_name]) for _name in self.defaultsThreadsNames}.items()):
            if count<mini:
                maxi = count
                threadNames = [name]
            elif count==mini:
                threadNames.append(name)
        self.setAffinity(objName, threadNames[0], attachementMode=self.AFFINITY_DEDICATED)

    def _popAffTo(self, objName, threadName):
        """ pop the oject to the thread affinity. 
        Instanciate a QThread if threadName is not existing"""
        ## remove the object from other threads aff if exist
        trigged = False
        for tname, affinitys in enumerate(self._QThreadAffinitys):
            if objName in affinitys:
                trigged = True
        if trigged:
            self._QThreadAffinitys[threadName].pop(self._QThreadAffinitys[threadName].index(objName))
        ## Instancate a thread if is not in the map
        if not threadName in self._QThreadMap:
            self.addThread(threadName)
            logger.info(threadName+" QThread added.")
        ## set aff
        self._QThreadAffinitys[threadName].append(objName)

    def setAffinity(self, name, threadName=None, attachementMode=AFFINITY_AUTO):
        """ AFFINITY_DEDICATED instanciate a new QThread with the same name as the given name (objectName) or
        move it to the given thread instance """
        if attachementMode==self.AFFINITY_DEDICATED:
            if not threadName:
                threadName = name
            self._popAffTo(name, threadName)
        elif threadName and attachementMode==self.AFFINITY_AUTO:
            if threadName in self.defaultsThreadsNames:
                self._popAffTo(name, threadName)
            else:
                logger.warn(threadName+" auto QThread if not existing so move it to another")
                self._addAutoAffinity(name)
        elif attachementMode==self.AFFINITY_AUTO:
            self._addAutoAffinity(name)

    ## add a QThread to the map at the given name
    def addThread(self, name):
        """ Instanciate a new QThread if this name doesn't exist """
        if not name in self._QThreadMap:
            self._QThreadMap[name] = QThread()
            self._QThreadMap[name].start()
            self._QThreadAffinitys[name] = []
        else:
            logger.warn(name+" already existing.")
    
    ## remove a QThread to the map at the given name
    def removeThread(self, name, affinityTo=AFFINITY_AUTO):
        """ terminate and pop the QThread instance from his map and return all these affinitys """
        if name in self._QThreadMap:
            self._QThreadMap.pop(name).terminate()
            return self._QThreadAffinitys.pop(name)
        else:
            raise Exception("QThread "+name+" is not existing in this ThreadManager instance")

    ## add a QObject to the map at the given name
    def addObj(self, name, QObjectInstance, threadName=None, attachementMode=AFFINITY_DEDICATED, SharedSignals={}, SharedPropertys={}):
        """ Add the given object from his map and his affinity """
        self._QObjectsMap[name] = QObjectInstance
        self.setAffinity(name, threadName, attachementMode)
        self.processAffinitys()
        if hasattr(QObjectInstance, "Com"):
            QObjectInstance.Com.moveToThread(self.thread())
            self.ctx.setContextProperty(name, QObjectInstance.Com)
        else:
            QObjectInstance.moveToThread(self.thread())
    
    def removeObj(self, name):
        """ Remove the given object from his map and his affinity """
        self._QThreadMap[self.getThreadOf(name)].pop(name)
        self._QObjectsMap[name].pop(name)
        
    
    ## Verify if the affinitys has been respected. If it's not the case, the QObject is moved to his thread.
    def processAffinitys(self):
        """ Use QObject.moveToThread(QThread) if affinity is not respected """
        # check if the auto thread count is respected
        autoDiff = len(self.defaultsThreadsNames)-self._autoTh_count
        if autoDiff<0:
            for i in range(len(self.defaultsThreadsNames)-1, self._autoTh_count-1):
                self.addThread("-a "+str(i))
        elif autoDiff>0:
            for i in range(self._autoTh_count-1, len(self.defaultsThreadsNames)-1):
                self.removeThread("-a "+str(i))
        # processAffinitys
        objNamesProcessed = []
        for tname in self._QThreadMap:
            currentThread = self._QThreadMap[tname]
            for oname in self._QThreadAffinitys[tname]:
                if not oname in objNamesProcessed:
                    objNamesProcessed.append(oname)
                if currentThread.currentThreadId() != self._QObjectsMap[oname].thread().currentThreadId():
                    self._QObjectsMap[oname].moveToThread(currentThread)
    def close(self):
        for tname in self._QThreadMap:
            currentThread = self._QThreadMap[tname]
            currentThread.terminate()


