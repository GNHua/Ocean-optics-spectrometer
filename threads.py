from PyQt4 import QtCore
import numpy as np
import time, os

class MultiRunThread(QtCore.QThread):
    
    integrationTimeChanged = QtCore.pyqtSignal(float)
    spectrumAcquiredArr = QtCore.pyqtSignal(np.ndarray)
    spectrumAcquiredArrStr = QtCore.pyqtSignal(str, np.ndarray)
    
    def __init__(self, spec, runs, dark, linear, dir, fn):
        super().__init__()
        self.spec = spec
        self.runs = runs
        self.dark = dark
        self.linear = linear
        self.dir = dir
        self.fn = fn
        
    def run(self):
        for i, run in enumerate(self.runs):
            integration_time_ms, interval_s, repeat = run
            self.spec.integration_time_micros(int(integration_time_ms * 1000))
            self.integrationTimeChanged.emit(integration_time_ms)
            for j in range(repeat):
                s = self.spec.spectrum(correct_dark_counts=self.dark, correct_nonlinearity=self.linear).T
                fn = os.path.join(self.dir, self.fn+'_{0:.0f}ms_{1:d}_{2:02d}'.format(integration_time_ms, i, repeat))
                self.spectrumAcquiredArr.emit(s)
                self.spectrumAcquiredArrStr.emit(fn, s)
                time.sleep(interval_s)