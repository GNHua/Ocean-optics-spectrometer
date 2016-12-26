import sys
# import seabreeze.spectrometers as sb
from PyQt4 import QtCore, QtGui
from PyQt4.uic import loadUiType
    
Ui_Dialog, QDialog = loadUiType('device_list.ui')
class DevListDialog(QDialog, Ui_Dialog):
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
        
        serial_item = QtGui.QStandardItem('QEPB0079')
        serial_item.setEditable(False)
        serial_item.setTextAlignment(QtCore.Qt.AlignCenter)
        model_item = QtGui.QStandardItem('QE65000')
        model_item.setEditable(False)
        model_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.model.appendRow([serial_item, model_item])
        
        serial_item = QtGui.QStandardItem('QEPB0080')
        serial_item.setEditable(False)
        serial_item.setTextAlignment(QtCore.Qt.AlignCenter)
        model_item = QtGui.QStandardItem('QE65001')
        model_item.setEditable(False)
        model_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.model.appendRow([serial_item, model_item])
        
        # for d in sb.list_devices():
        #     serial_item = QtGui.QStandardItem(d.serial)
        #     serial_item.setEditable(False)
        #     serial_item.setTextAlignment(QtCore.Qt.AlignCenter)
        #     model_item = QtGui.QStandardItem(d.model)
        #     model_item.setEditable(False)
        #     model_item.setTextAlignment(QtCore.Qt.AlignCenter)
        #     self.model.appendRow([serial_item, model_item])
        
    def openDev(self):
        select = self.tableViewDev.selectionModel()
        if select.hasSelection():
            # print(self.model.itemData(select.selectedIndexes()[0])[0])
            self.selected_dev = self.model.itemData(select.selectedIndexes()[0])[0]
        
if __name__ == '__main__': 
    app = QtGui.QApplication(sys.argv)
    main = DevListDialog()
    main.show()
    sys.exit(app.exec_())