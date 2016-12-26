import os
import sys
import time
import getpass
import numpy as np
# import seabreeze.spectrometers as sb
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
    
from device_list_debug import DevListDialog

Ui_MainWindow, QMainWindow = loadUiType('spectrometer.ui')
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)
        self._is_spec_open = False
        # self.path = os.path.join('C:/Users', getpass.getuser())
        self.path = '/Users/haocan/Developer/Python/spectrometer'
        
        self.connectUi()
        
    def connectUi(self):
        self.actionSave.triggered.connect(self.save)
        self.actionPlot.triggered.connect(self.plot_file)
        self.actionQuit.triggered.connect(self.quit)
        self.actionOpenDev.triggered.connect(self.openSpectrometer)
        self.actionSpectrum.triggered.connect(self.getSpectrum)

    def addmpl(self, fig):
         self.canvas = FigureCanvas(fig)
         self.mplvl.addWidget(self.canvas)
         self.canvas.draw()
         self.toolbar = NavigationToolbar(self.canvas, 
                 self.mplwindow, coordinates=True)
         self.mplvl.addWidget(self.toolbar)
         
    def rmmpl(self):
         self.mplvl.removeWidget(self.canvas)
         self.canvas.close()
         self.mplvl.removeWidget(self.toolbar)
         self.toolbar.close()
         
    def openSpectrometer(self):
        if not self._is_spec_open:
            try:
                devlist = DevListDialog()
                if devlist.exec_() == QtGui.QDialog.Accepted and devlist.selected_dev:
                    print(devlist.selected_dev) ###
                    # self.spec = sb.Spectrometer.from_serial_number(devlist.selected_dev)
                    self._is_spec_open = True
                    self.actionOpenDev.setText('&Close Device')
                    self.actionOpenDev.setToolTip('Close Device')
            except:
                QtGui.QMessageBox.critical(self, 'Message',
                                           "Can't find spectrometer",
                                           QtGui.QMessageBox.Ok)
        else:
            # self.spec.close()
            self._is_spec_open = False
            self.actionOpenDev.setText('&Open Device')
            self.actionOpenDev.setToolTip('Open Device')
        self.actionSpectrum.setEnabled(self._is_spec_open)
        self.actionOpenDev.setChecked(self._is_spec_open)

    # def setIntegrationTime(self):
    #     self.spec.integration_time_micros(self.spinBoxInt.value() * 1000)
        
    def getSpectrum(self):
        # self.spectrum = np.transpose(self.spec.spectrum())
        self.spectrum = np.genfromtxt('test_data.csv', delimiter=',')
        self.saveBackup()
        self.plot(self.spectrum)
        
    def plot(self, data):
        if hasattr(self, 'canvas'):
            self.rmmpl()
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(data[:,0], data[:,1])
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Intensity')
        self.addmpl(fig)
        
    def saveBackup(self):
        if not os.path.exists('./backup'):
            os.makedirs('./backup')
        self.saveCsv(filename=os.path.join('./backup', time.strftime('%Y%m%d_%H%M%S')))
        
    def getSpecSetting(self):
        date = time.strftime("%D")
        fiber = '100 um fiber' if self.radioButton100um.isChecked() else '1000 um fiber'
        slit = 'With slit' if self.checkBoxSlit.isChecked() else 'No slit'
        intTime = 'Integration time: %d ms' % self.spinBoxInt.value()
        return [date, fiber, slit, intTime]
        
    def save(self):
        fn = self.getFileName(0)
        if fn:
            fn = os.path.splitext(fn)[0]
            self.saveCsv(fn)
            self.savePlot(fn)
            
    def plot_file(self):
        fn = self.getFileName(1)
        if fn:
            data = np.genfromtxt(fn, delimiter=',')
            self.plot(data)
    
    def saveCsv(self, filename):
        text = ','.join(self.getSpecSetting())
        np.savetxt(filename+'.csv', self.spectrum, delimiter=',',
                   header=text + '\nwavelength,intensity')
    
    def savePlot(self, filename):
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(self.spectrum[:,0], self.spectrum[:,1])
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Intensity')
        ax.text(0.05, 0.9, '\n'.join(self.getSpecSetting()), 
                ha='left', va='top', transform=ax.transAxes)
        plt.savefig(filename+'.png')
        plt.close('all')
        
    def getFileName(self, mode):
        '''
        Get the name and directory
            mode    0       1
                    save    open
        '''
        title = ['Save data', 'Find']
        acceptmode = [QtGui.QFileDialog.AcceptSave, QtGui.QFileDialog.AcceptOpen]
        
        fd = QtGui.QFileDialog()
        fd.setWindowTitle(title[mode])
        fd.setDirectory(self.path)
        fd.setAcceptMode(acceptmode[mode])
        fd.setDefaultSuffix("csv")
        fd.setNameFilter("csv (*.csv)")

        if fd.exec_() == QtGui.QFileDialog.Accepted:
            filename = str(fd.selectedFiles()[0])
            self.path = os.path.dirname(filename)
            return filename
        else:
            return
            
    def quit(self):
        # if self._is_spec_open:
        #     self.spec.close()
        sys.exit()
        
    def closeEven(self, event):
        self.quit()
        event.accept()
            
if __name__ == '__main__': 
    app = QtGui.QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())