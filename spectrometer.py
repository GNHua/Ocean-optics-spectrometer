import os
import sys
import time
import getpass
import argparse
import numpy as np
from PyQt4 import QtGui, QtCore, uic
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

ui_module_path = os.path.abspath('./ui')
if ui_module_path not in sys.path:
    sys.path.insert(1,ui_module_path)

from run_table_dialog import RunTableDialog

import threads

class MyCanvas:
    def __init__(self):
        self.Fig = Figure()
        self.ax = self.Fig.add_subplot(111)
        self.canvas = FigureCanvas(self.Fig)

    def update(self, data):
        self.ax.cla()
        self.ax.set_xlabel('Wavelength (nm)')
        self.ax.set_ylabel('Intensity')
        if isinstance(data, list):
            ymax = max([max(d[:,1]) for d in data])
            for d in data:
                self.ax.plot(d[:,0], d[:,1])
        else:
            ymax = max(data[:,1])
            self.ax.plot(data[:,0], data[:,1])
        if ymax > 70000:
            self.ax.set_ylim(0, 70000)
        else:
            self.ax.set_ylim(0,)
        self.canvas.draw()

Ui_MainWindow, QMainWindow = uic.loadUiType('ui/spectrometer.ui')
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._is_spec_open = False
        self._runs = []
        self._multirundir = ''
        self._multirunfn = ''
        self.path = os.path.join('/')

        self._mrt = threads.MultiRunThread(None, None, False, False, '', '')
        self.addmpl()

        self.connectUi()

    def connectUi(self):
        self.actionSave.triggered.connect(self.save)
        self.actionPlot.triggered.connect(self.plot_file)
        self.actionQuit.triggered.connect(self.quit)
        self.actionOpenDev.triggered.connect(self.openSpectrometer)
        self.actionSpectrum.triggered.connect(self.getSpectrum)
        self.actionMultiRun.triggered.connect(self.multiRun)
        self.actionSaturationTest.triggered.connect(self.saturationTest)
        self.pushButtonSetInt.clicked.connect(self.setIntegrationTime)
        self._mrt.integrationTimeChanged.connect(self.doubleSpinBoxInt.setValue)
        self._mrt.spectrumAcquiredArr.connect(self.saveBackup)
        self._mrt.spectrumAcquiredArr.connect(self.plot)
        self._mrt.spectrumAcquiredArrStr.connect(self.saveCsv)

    def addmpl(self):
        self._canvas = MyCanvas()
        self.mplvl.addWidget(self._canvas.canvas)
        self._toolbar = NavigationToolbar(self._canvas.canvas, self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self._toolbar)

    def openSpectrometer(self):
        if not self._is_spec_open:
            devtable = DevTableDialog()
            if devtable.exec_() == QtGui.QDialog.Accepted and devtable.selected_dev:
                try:
                    self.spec = sb.Spectrometer.from_serial_number(devtable.selected_dev)
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
        self.actionSaturationTest.setEnabled(self._is_spec_open)

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
        self._mrt.spec = self.spec
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
        self._mrt.spec = None
        self.actionOpenDev.setText('&Open Device')
        self.actionOpenDev.setToolTip('Open Device')

    def setIntegrationTime(self):
        self.spec.integration_time_micros(int(self.doubleSpinBoxInt.value() * 1000))

    def getSpectrum(self):
        correct_dark_counts = self.checkBoxDark.isChecked()
        correct_nonlinearity = self.checkBoxNonlinear.isChecked()
        if self.actionMultiRun.isChecked():
            self._mrt.runs = self._runs
            self._mrt.dark = correct_dark_counts
            self._mrt.linear = correct_nonlinearity
            self._mrt.start()
        else:
            self.spectrum = self.spec.spectrum(correct_dark_counts, correct_nonlinearity).T
            self.saveBackup(self.spectrum)
            self.plot(self.spectrum)

    def plot(self, data):
        '''Get the name and directory'''
        self._canvas.update(data)

    def saveBackup(self, data):
        if not os.path.exists('./backup'):
            os.makedirs('./backup')
        self.saveCsv(filename=os.path.join('./backup', time.strftime('%Y%m%d_%H%M%S')), data=data)

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

    def saveCsv(self, filename, data=None):
        if data is None:
            data = self.spectrum
        text = ','.join(self.getSpecSetting())
        np.savetxt(filename+'.csv', data, delimiter=',',
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

    def multiRun(self):
        # list(self._runs): copy self._runs instead of referring to it.
        dialog = RunTableDialog(runs=list(self._runs))
        dialog.lineEditDir.setText(self._multirundir)
        dialog.lineEditFn.setText(self._multirunfn)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self._runs = list(dialog.model._runs)
            self._multirundir = dialog.lineEditDir.text()
            self._multirunfn = os.path.splitext(dialog.lineEditFn.text())[0]
            self._mrt.dir = self._multirundir
            self._mrt.fn = self._multirunfn
        multirunready = (len(self._runs) > 0) and bool(self._multirundir) and bool(self._multirunfn)
        self.actionMultiRun.setChecked(multirunready)
        self.pushButtonSetInt.setEnabled(not multirunready)
        self.doubleSpinBoxInt.setEnabled(not multirunready)

    def saturationTest(self):
        longExp = self.doubleSpinBoxInt.value()
        shortExp = longExp / 4
        self.spec.integration_time_micros(int(shortExp * 1000))
        shortSpec = np.transpose(self.spec.spectrum(correct_dark_counts=self.checkBoxDark.isChecked(), \
                                                    correct_nonlinearity=self.checkBoxNonlinear.isChecked()))
        shortSpec[:,1] *= 4
        time.sleep(0.1)
        self.spec.integration_time_micros(int(longExp * 1000))
        longSpec = np.transpose(self.spec.spectrum(correct_dark_counts=self.checkBoxDark.isChecked(), \
                                                   correct_nonlinearity=self.checkBoxNonlinear.isChecked()))
        self.plot([shortSpec, longSpec])

    def quit(self):
        if self._is_spec_open:
            self.spec.close()
        sys.exit()

    def closeEvent(self, event):
        self.quit()
        event.accept()


def main(args):
    parser = argparse.ArgumentParser(prog='python spectrometer.py')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Use dummy module to debug')
    args = parser.parse_args(args)
    if args.debug:
        debug_module_path = os.path.abspath('./debug')
        if debug_module_path not in sys.path:
            sys.path.insert(1,debug_module_path)

        import debug_sb as sb
        from debug_device_table_dialog import DevTableDialog
    else:
        import seabreeze.spectrometers as sb
        from device_table_dialog import DevTableDialog

    # make imported module global
    globals()['sb'] = sb
    globals()['DevTableDialog'] = DevTableDialog

    app = QtGui.QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(sys.argv[1:])
