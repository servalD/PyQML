from PyQML import *
import os
from time import sleep
os.chdir(os.path.dirname(__file__))


class test():
    def __init__(self):
        QmlData.tic = 1
        QmlData.toc = 5
    
    def Slot_Dre(self, count):
        print("count=", count)
        sleep(1)
        self.tic=count
        return [self.tic, 5]

    def Slot_Drx(self, count, ret):
        print("count=", count)
        sleep(1)
        self.tic=count
        return [self.tic, 5]

test = toQml(test, glob=globals())

app = QmlApp("FastApp", width=500, height=400, addObj={"test": test})
