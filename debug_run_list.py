import sys
from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType

Ui_Dialog, QDialog = loadUiType('run_list.ui')
class DevListDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = QtGui.QStandardItemModel()
        self.initModel()

        self.pushButtonAdd.clicked.connect(self.add)
        self.pushButtonInsert.clicked.connect(self.insert)
        self.pushButtonRemove.clicked.connect(self.remove)

        self.buttonBox.accepted.connect(self.openDev)
        self.selected_dev = None

    def initModel(self):
        self.model.setColumnCount(3)
        self.model.setHorizontalHeaderLabels(['Integration (ms)', 'Interval (s)', 'Repeat'])
        self.tableViewRun.setModel(self.model)
        
    def add(self):
        integration_item = QtGui.QStandardItem()
        integration_item.setData(8)
        interval_item = QtGui.QStandardItem()
        repeat_item = QtGui.QStandardItem()
        self.model.appendRow([integration_item, interval_item, repeat_item])
        
        # print(self.model.item(0,0).data())
        # print(self.model.item(0,1).data())
        # print(self.model.item(0,2).data())
        
    def insert(self):
        pass
        
    def remove(self):
        pass

    # def refresh(self):
    #     self.model.clear()
    #     self.initModel()

        # for d in sb.list_devices():
        #     serial_item = QtGui.QStandardItem(d.serial)
        #     serial_item.setEditable(False)
        #     serial_item.setTextAlignment(QtCore.Qt.AlignCenter)
        #     model_item = QtGui.QStandardItem(d.model)
        #     model_item.setEditable(False)
        #     model_item.setTextAlignment(QtCore.Qt.AlignCenter)
        #     self.model.appendRow([serial_item, model_item])

    def openDev(self):
        pass
        # select = self.tableViewDev.selectionModel()
        # if select.hasSelection():
        #     # make sure the spectrometer is powered by +5V power supply.
        #     QtGui.QMessageBox.warning(self, 'Message',
        #                               'Make sure power supply is connected!',
        #                               QtGui.QMessageBox.Ok)
        #     # print(self.model.itemData(select.selectedIndexes()[0])[0])
        #     self.selected_dev = self.model.itemData(select.selectedIndexes()[0])[0]

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = DevListDialog()
    main.show()
    sys.exit(app.exec_())
