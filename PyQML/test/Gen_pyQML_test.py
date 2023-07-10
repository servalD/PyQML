class test(QObject,):
    
    
    def __call__(self):
        return self
    class Com(QObject):
        
        
        
        
        onDrx = pyqtSignal(QVariant, arguments=['arg'])
        DrxL = pyqtSignal(QVariant, QVariant)
        @pyqtSlot(QVariant, QVariant)
        def Drx(self,  count, ret):
            print("start...")
            self.DrxL.emit( count, ret)
            print("started")
            return None
        onDre = pyqtSignal(QVariant, arguments=['arg'])
        DreL = pyqtSignal(QVariant)
        @pyqtSlot(QVariant)
        def Dre(self,  count):
            print("start...")
            self.DreL.emit( count)
            print("started")
            return None
        tocChanged = pyqtSignal()
        @pyqtProperty(QVariant, notify=tocChanged)
        def toc(self):
            return self.worker._toc

        @toc.setter
        def toc(self, toc):
            if self.worker._toc != toc:
                print("set toc from interface")
                self.worker._toc = toc
                self.tocChanged.emit()
                self.worker.tocChanged.emit()
        ticChanged = pyqtSignal()
        @pyqtProperty(QVariant, notify=ticChanged)
        def tic(self):
            return self.worker._tic

        @tic.setter
        def tic(self, tic):
            if self.worker._tic != tic:
                print("set tic from interface")
                self.worker._tic = tic
                self.ticChanged.emit()
                self.worker.ticChanged.emit()
        def __init__(self):
            super(QObject, self).__init__()
        def setWorker(self, worker):
            self.DrxL.connect(worker.Slot_Drx)
            self.DreL.connect(worker.Slot_Dre)
            self.worker = worker
    Com = Com()
    tocChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify=tocChanged)
    def toc(self):
        return self._toc

    @toc.setter
    def toc(self, toc):
        if self._toc != toc:
            print("set toc from QObject")
            self._toc = toc
            self.tocChanged.emit()
            self.Com.tocChanged.emit()
    ticChanged = pyqtSignal()
    @pyqtProperty(QVariant, notify=ticChanged)
    def tic(self):
        return self._tic

    @tic.setter
    def tic(self, tic):
        if self._tic != tic:
            print("set tic from QObject")
            self._tic = tic
            self.ticChanged.emit()
            self.Com.ticChanged.emit()
    def __init__(self):
        super(QObject, self).__init__()
        self._toc = None
        self._tic = None
        self.Com.setWorker(self)
        self.tic = 1
        self.toc = 5
    
    @pyqtSlot(QVariant, result=QVariant)
    def Slot_Dre(self, count):
        print("count=", count)
        sleep(1)
        self.tic=count
        self.Com.onDre.emit(([self.tic, 5]))
        return [self.tic, 5]

    @pyqtSlot(QVariant, QVariant, result=QVariant)
    def Slot_Drx(self, count, ret):
        print("count=", count)
        sleep(1)
        self.tic=count
        self.Com.onDrx.emit(([self.tic, 5]))
        return [self.tic, 5]
