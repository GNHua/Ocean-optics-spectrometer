import os
import sys
import time
import getpass
import numpy as np
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

debug = True
if debug:
    import debug_sb as sb
    from debug_device_list import DevListDialog
    from debug_run_list import RunListDialog
else:
    import seabreeze.spectrometers as sb
    from device_list import DevListDialog

Ui_MainWindow, QMainWindow = loadUiType('spectrometer.ui')
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)
        self._is_spec_open = False
        self._runs = []
        self.path = os.path.join('C:/Users', getpass.getuser())

        self.connectUi()

    def connectUi(self):
        self.actionSave.triggered.connect(self.save)
        self.actionPlot.triggered.connect(self.plot_file)
        self.actionQuit.triggered.connect(self.quit)
        self.actionOpenDev.triggered.connect(self.openSpectrometer)
        self.actionSpectrum.triggered.connect(self.getSpectrum)
        self.actionAbsorbance.triggered.connect(self.calcAbsorbance)
        self.actionMultiRun.triggered.connect(self.multiRun)

        self.pushButtonSetInt.clicked.connect(self.setIntegrationTime)

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
            devlist = DevListDialog()
            if devlist.exec_() == QtGui.QDialog.Accepted and devlist.selected_dev:
                try:
                    self.spec = sb.Spectrometer.from_serial_number(devlist.selected_dev)
                except:
                    QtGui.QMessageBox.critical(self, 'Message',
                                               "Can't find spectrometer",
                                               QtGui.QMessageBox.Ok)
                self.initSpectrometer()
        else:
            self.closeSpectrometer()
        self.actionSpectrum.setEnabled(self._is_spec_open)
        self.actionOpenDev.setChecked(self._is_spec_open)
        self.actionMultiRun.setEnabled(self._is_spec_open)

    def initSpectrometer(self):
        self.initTEC()
        self.spec.integration_time_micros(self.spec.minimum_integration_time_micros)
        self.pushButtonSetInt.setEnabled(True)
        self.doubleSpinBoxInt.setEnabled(True)
        self.doubleSpinBoxInt.setValue(self.spec.minimum_integration_time_micros/1000)
        self.doubleSpinBoxInt.setMinimum(self.spec.minimum_integration_time_micros/1000)
        self.checkBoxDark.setEnabled(self.spec._has_dark_pixels)
        self.checkBoxDark.setChecked(self.spec._has_dark_pixels)
        self.checkBoxNonlinear.setEnabled(self.spec._has_nonlinearity_coeffs)
        self.checkBoxNonlinear.setChecked(self.spec._has_nonlinearity_coeffs)
        self._is_spec_open = True
        self.actionOpenDev.setText('&Close Device')
        self.actionOpenDev.setToolTip('Close Device')

    def initTEC(self):
        # initialize thermoelectric cooling
        self.spec.tec_get_temperature_C()
        time.sleep(0.1)
        self.spec.tec_set_enable(False)
        time.sleep(0.1)
        self.spec.tec_set_temperature_C(-15)
        time.sleep(0.1)
        self.spec.tec_set_enable(True)
        time.sleep(0.1)
        while(self.spec.tec_get_temperature_C() > 10):
            # make sure the spectrometer is powered by +5V power supply.
            QtGui.QMessageBox.warning(self, 'Message',
                                      'Connect Power Supply!\nThen wait for a few seconds.',
                                      QtGui.QMessageBox.Ok)
            time.sleep(2)
            self.initTEC()

    def closeSpectrometer(self):
        self.spec.close()
        self.pushButtonSetInt.setEnabled(False)
        self.doubleSpinBoxInt.setEnabled(False)
        self.checkBoxDark.setChecked(False)
        self.checkBoxDark.setEnabled(False)
        self.checkBoxNonlinear.setChecked(False)
        self.checkBoxNonlinear.setEnabled(False)
        self._is_spec_open = False
        self.actionOpenDev.setText('&Open Device')
        self.actionOpenDev.setToolTip('Open Device')

    def setIntegrationTime(self):
        self.spec.integration_time_micros(int(self.doubleSpinBoxInt.value() * 1000))

    def getSpectrum(self):
        # if self.actionMultiRun.isChecked():
            
        self.spectrum = np.transpose(self.spec.spectrum(correct_dark_counts=self.checkBoxDark.isChecked(), \
                                                        correct_nonlinearity=self.checkBoxNonlinear.isChecked()))
        self.saveBackup()
        self.plot(self.spectrum, mode='spectrum')

    def plot(self, data, mode='spectrum'):
        '''
        Get the name and directory
            mode: 'spectrum', 'absorbance'
        '''
        ylabel = {'spectrum': 'Intensity', 'absorbance': 'Absorbance'}
        if hasattr(self, 'canvas'):
            self.rmmpl()
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(data[:,0], data[:,1])
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel(ylabel[mode])
        ax.set_ylim(0,)
        self.addmpl(fig)

    def saveBackup(self):
        if not os.path.exists('./backup'):
            os.makedirs('./backup')
        self.saveCsv(filename=os.path.join('./backup', time.strftime('%Y%m%d_%H%M%S')))

    def getSpecSetting(self):
        date = time.strftime("%D")
        fiber = '100 um fiber' if self.radioButton100um.isChecked() else '1000 um fiber'
        slit = 'With slit' if self.checkBoxSlit.isChecked() else 'No slit'
        intTime = 'Integration time: %.1f ms' % self.doubleSpinBoxInt.value()
        darkCor = 'on' if self.checkBoxDark.isChecked() else 'off'
        nonlinearCor = 'on' if self.checkBoxNonlinear.isChecked() else 'off'
        return [date, fiber, slit, intTime, \
                'Dark correction '+darkCor, 'Nonlinearity correction '+nonlinearCor]

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
            self.plot(data, mode='spectrum')

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
        
    def calcAbsorbance(self):
        '''
        Select baseline data file and calculate absorbance
        '''
        fn = self.getFileName(1)
        if fn:
            begin_index = 50
            end_index = 998
            noresin = np.genfromtxt(fn, delimiter=',')
            numerator = self.spectrum[begin_index:end_index,1]
            denominator = noresin[begin_index:end_index,1]
            absorbance = -np.log10(numerator/denominator)
            print(absorbance.shape)
            data = np.array([self.spectrum[begin_index:end_index,0], absorbance]).T
            print(data.shape)
            self.plot(data, mode='absorbance')

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
            
    def multiRun(self):
        if len(self._runs) == 0:
            dialog = RunListDialog()
            if dialog.exec_() == QtGui.QDialog.Accepted and len(dialog.model._runs) > 0:
                self._runs = dialog.model._runs
            else:
                self.actionMultiRun.setChecked(False)
        else:
            del self._runs[:]
            self.actionMultiRun.setChecked(False)
            

    def quit(self):
        if self._is_spec_open:
            self.spec.close()
        sys.exit()

    def closeEven(self, event):
        self.quit()
        event.accept()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())
