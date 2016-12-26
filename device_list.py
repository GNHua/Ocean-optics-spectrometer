import sys
from seabreeze.spectrometers import list_devices
from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType

Ui_Dialog, QDialog = loadUiType('device_list.ui')
class DevListDialog(QDialog, Ui_Dialog):
    '''
    A dialog window to select device.
    '''
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = QtGui.QStandardItemModel()
        self.initModel()

        self.pushButtonRefresh = QtGui.QPushButton('&Refresh')
        self.buttonBox.addButton(self.pushButtonRefresh,
                                 QtGui.QDialogButtonBox.ActionRole)
        self.pushButtonRefresh.clicked.connect(self.refresh)

        self.buttonBox.accepted.connect(self.openDev)
        self.selected_dev = None

        self.refresh()

    def initModel(self):
        self.model.setColumnCount(2)
        self.model.setHorizontalHeaderLabels(['Serial Number', 'Model'])
        self.tableViewDev.setModel(self.model)

    def refresh(self):
        self.model.clear()
        self.initModel()

        for d in list_devices():
            serial_item = QtGui.QStandardItem(d.serial)
            serial_item.setEditable(False)
            serial_item.setTextAlignment(QtCore.Qt.AlignCenter)
            model_item = QtGui.QStandardItem(d.model)
            model_item.setEditable(False)
            model_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.appendRow([serial_item, model_item])

    def openDev(self):
        select = self.tableViewDev.selectionModel()
        if select.hasSelection():
            # get the serial number of the selected device
            self.selected_dev = self.model.itemData(select.selectedIndexes()[0])[0]

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = DevListDialog()
    main.show()
    sys.exit(app.exec_())
