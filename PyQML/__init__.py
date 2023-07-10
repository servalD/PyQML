from PyQML.QML import QmlApp, GenerateQrcQmldir, importSample, toQml, listFileTree
from PyQML.ThreadOptimisation import ThreadManager
from PyQt5.QtCore import QObject, QVariant, pyqtSignal, pyqtProperty, pyqtSlot
import inspect, re, dill, os, sys
qmlSamples = [os.path.basename(path).replace(".qml", "") for path in listFileTree(os.path.dirname(__file__), 'qml')]
print("availiable qml samples: "+str(qmlSamples))
QmlData = object()
name = "PyQML"