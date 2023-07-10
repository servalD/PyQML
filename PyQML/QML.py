

# QmlApp
# QmlDir
# Qrc
# Persist
# Network
# SshDevice
# Version
# Informations
# Debuging

import sys, os, json
import logging
logging.basicConfig(format="%(levelname)-s - %(filename)-s %(lineno)-s in %(funcName)s(): %(message)s", level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, QUrl, pyqtSignal, QThread, pyqtProperty, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStyle
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtQuick import QQuickImageProvider
from PyQt5.QtGui import QPixmap, QImage
import pickle
from threading import Thread as th

from PyQML.ThreadOptimisation import ThreadManager

if __name__ == "__main__":
    from structGen import ComStructGen, toQml
else:
    from .structGen import ComStructGen, toQml

from time import time, sleep

def importSample(name, overwrite=False):
    """ copy qml file sample to the cwd if it's already the case """ 
    """ Currently, samles files should be not modified to ensure no data loose """
    QmlFilePath = os.path.join(os.path.dirname(__file__), "Components", "base", name+".qml")
    if os.path.isfile(QmlFilePath):
        with open(QmlFilePath, "r") as SampleH:
            path=os.path.join("Components", "base")
            if not os.path.exists(path):
                os.makedirs(path)
            dst = os.path.join(path, name+".qml")
            if not os.path.isfile(dst) or overwrite:
                with open(dst, "w") as dstH:
                    dstH.write(SampleH.read())
            else:
                logger.warn(dst+" not overwrited.")
    else:
        logger.warning(QmlFilePath+" is not included in samples lib ")
    

####################################################### qrc and qmldir generation #######################################################################
## list dir tree filtered by extention
def listFileTree(rootPath=None, ext="", excludedFiles=[]):
    """ list all files from a root directory (top dir) to the last (bottom dir) which has the given extention """
    """ rootPath: str or None"""
    """ ext: [str, str, ...] or str """
    if type(ext)!=list:
        ext = [ext]
    ret = []
    if rootPath==None:
        rootPath = "."
    for root, dirs, files in os.walk(rootPath, topdown=False):
        for name in files:
            if name.split(".")[-1] in ext and not name in excludedFiles:
                if root.startswith(".\\"):
                    root = root[2:]
                if not root=="":
                    ret.append(os.path.join(root, name))
                else:
                    if name.startswith(".\\"):
                        name = name[2:]
                    ret.append( name)
    return ret

def QrcWrite(rootPath=None, ext=["qml", "png", "qmldir"], fileName="qml_rc", asPy=True, rmQrcIfPy=True, excludedFiles=[], load=True):
    """generate (filtered by givens ext) a tree file to write the qrc file and convert it to py file
    
    Keyword Arguments:
        rootPath {str} -- [description] (default: {None})
        ext {list} -- [description] (default: {["qml", "png", "qmldir"]})
        fileName {str} -- [description] (default: {"qml_rc"})
        asPy {bool} -- [description] (default: {True})
        rmQrcIfPy {bool} -- [description] (default: {True})
        excludedFiles {list} -- [description] (default: {[]})
    """
    if rootPath:
        qrcPath = os.path.join(rootPath, fileName+".qrc")
    else:
        qrcPath = fileName+".qrc"
    files = listFileTree(rootPath=rootPath, ext=ext, excludedFiles=excludedFiles)
    qrcFile = open( qrcPath, "w")
    qrcBeginsLines = """<RCC>
      <qresource prefix="/">"""
    qrcEndsLines = """
      </qresource>
  </RCC>"""
    qrcFileHeader = """
          <file>filePath</file>"""
    qrcFile.write(qrcBeginsLines)
    for file in files:
        qrcFile.write(qrcFileHeader.replace("filePath", file))
    qrcFile.write(qrcEndsLines)
    qrcFile.close()
    if asPy:
        if rootPath:
            os.system('pyrcc5 -o "'+os.path.join(rootPath, fileName+".py")+'" "'+qrcPath+'"')
        else:
            os.system('pyrcc5 -o "'+fileName+".py"+'" "'+qrcPath+'"')
        if rmQrcIfPy:
            os.remove(qrcPath)
    if load:
        globals()[fileName] = __import__(fileName)

def QmldirWrite(rootPath=None, excludedFiles=[]):
    """ generate the qml tree file to write the qmldir file """
    files = listFileTree(rootPath=rootPath, ext="qml", excludedFiles=excludedFiles)
    if rootPath:
        qmldirFile = open(os.path.join(rootPath, "qmldir"), "w")
    else:
        qmldirFile = open("qmldir", "w")
    for file in files:
        qmldirFile.write(os.path.basename(file).replace(".qml", " "+file)+"\n")
    qmldirFile.close()

#### generate only if it's not a pyinstaller environement (not compiled as .exe in this case) ####
def GenerateQrcQmldir(rootPath=None, includedExtentions="png", excludedFiles=[], QrcFileName="qmlResources", Debbug=False):
    """generate the qml tree file to write the qmldir file
    generate (filtered by included Extentions) a tree file to write the qrc file and convert it to py file
    
    Keyword Arguments:
        rootPath {str} -- [description] (default: {None})
        includedExtentions {str} -- [description] (default: {"png"})
        excludedFiles {list} -- [description] (default: {[]})
        QrcFileName {str} -- [description] (default: {"qmlResources"})
        Debbug {bool} -- [description] (default: {False})
    """
    pyinstallerEXE = sys.argv[0].endswith(".exe")
    if not pyinstallerEXE:
        QmldirWrite(rootPath=rootPath, excludedFiles=excludedFiles)
        if type(includedExtentions)==str:
            includedExtentions = [includedExtentions]
        includedExtentions.extend(["qml", "qmldir"])
        QrcWrite(rootPath=rootPath, ext=includedExtentions, excludedFiles=excludedFiles, fileName=QrcFileName, rmQrcIfPy=Debbug==False, asPy=True, load=True)
    return pyinstallerEXE

####
class QtSPProvider(QQuickImageProvider):
    def __init__(self):
        super(QtSPProvider, self).__init__(QQuickImageProvider.Image)
        self.stdIcons = QApplication.style().standardIcon

    def requestImage(self, p_str, size):
        if "__" in p_str:
            p_str, s = p_str.split("__")
            s=int(s)
        else:
            s=16
        img = self.stdIcons(getattr(QStyle, "SP_"+p_str)).pixmap(s, s).toImage()
        return img, img.size()
####                                                                                          ####

class QmlApp():
    """ Class who wrap PyQt to make the user code more simple """
    initialized = False
    def __init__(self,AppName, width=500, height=400, OrganizationName="", OrganizationDomain="", rootPath=None, **kwargs):
        self.settingsPath = os.path.join(os.getcwd(), "AppSettings.json")
        self.AppName = AppName
        if os.path.isfile(self.settingsPath):
            with open(self.settingsPath, "r") as file:
                self.kwargs = json.load(file)
            self.width = self.kwargs["width"]
            self.height = self.kwargs["height"]
            for kw in kwargs:
                if not kw in self.kwargs:
                    self.kwargs[kw] = kwargs[kw]
        else:
            self.kwargs = kwargs
            self.kwargs["width"] = width
            self.kwargs["height"] = height
        self.OrganizationName = OrganizationName
        self.OrganizationDomain = OrganizationDomain
        if not os.path.isfile(self.AppName.replace(" ", "")+".qml"):
            if rootPath:
                dst = rootPath
            else:
                dst = os.getcwd()
            logger.warn(self.AppName.replace(" ", "")+".qml not existing in "+str(rootPath)+" so it will be created from sample")
            with open(os.path.join(os.path.dirname(__file__), "Sample.qml"), "r") as sampleH:
                with open(os.path.join(dst, self.AppName.replace(" ", "")+".qml"), "w") as dstH:
                    dstH.write(sampleH.read())
        isExe = GenerateQrcQmldir(rootPath=rootPath, QrcFileName="qmlResources")
        
        ###
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.ctx = self.engine.rootContext()
        ######
        self.app.setOrganizationName(self.OrganizationName)
        self.app.setOrganizationDomain(self.OrganizationDomain)
        self.app.setApplicationName(self.AppName)
        self.engine.addImageProvider("QtSP", QtSPProvider())
        if "matplotlib" in globals():
            self.__loadMPL__()
        ### TreadManager
        self.TM = ThreadManager(self.ctx)
        if "addObj" in self.kwargs:
            addObj = self.kwargs.pop("addObj")
            for name, obj in addObj.items():
                self.TM.addObj( name, obj, attachementMode=self.TM.AFFINITY_AUTO)
        ###
        self.pyData = ComStructGen(globals(), "pyData", **self.kwargs)()

        self.ctx.setContextProperty("pyData", self.pyData)
        
        self.engine.load(QUrl('qrc:/'+self.AppName.replace(" ", "")+'.qml'))
        self.win = self.engine.rootObjects()[0]
        self.win.closing.connect( self.closeEvent)
        self.win.show()
        self.initialized = True
        sys.exit(self.app.exec())

    def __loadMPL__(self):
        """ import FigureCanvasQTAgg, FigureCanvasQTAggToolbar and MatplotlibIconProvider to use QFigureToolbar inside qml code """
        from QQuickMpl import FigureCanvasQTAgg, FigureCanvasQTAggToolbar, MatplotlibIconProvider
        qmlRegisterType(FigureCanvasQTAgg, "Backend", 1, 0, "FigureCanvas")
        qmlRegisterType(FigureCanvasQTAggToolbar, "Backend", 1, 0, "FigureToolbar")
        self.mplIcons = MatplotlibIconProvider()
        self.engine.addImageProvider("mplIcons", self.mplIcons)

    def __setitem__(self, key, value):
        if key.startswith("_"):
            if key.count("_")==2:
                _, thread, key = key.split("_")
            else:
                thread, key = key.split("_")
        else:
            thread = None
        
        if not key in self.TM._InterfacesMap:
            if thread:
                if thread=="me":
                    self.TM.addObj( key, value, attachementMode=self.TM.AFFINITY_DEDICATED)
                else:
                    self.TM.addObj( key, value, threadName=thread, attachementMode=self.TM.AFFINITY_DEDICATED)
            else:
                self.TM.addObj( key, value, attachementMode=self.TM.AFFINITY_AUTO)
        else:
            raise Exception(key+" QObject name allready assigned.")
    
    def __getitem__(self, key):
        return self.TM._InterfacesMap[key]

    def closeEvent(self, event):
        """ Save settings (pyData) as json for the persistancy """
        logger.info("dump pyData to json")
        with open(self.settingsPath, "w") as file:
            json.dump(self.pyData.toDict(), file)
        self.TM.close()
        logger.info("App closed")
        

    @pyqtSlot(QVariant)
    def getFig(self, name):
        """ return the mpl figure of the given qml objectName (from QFigureToolbar instance) """
        return self.win.findChild(QObject, name).getFigure()

if __name__ == "__main__":

    py_mainapp = QmlApp("FastApp", width=500, height=400)
    