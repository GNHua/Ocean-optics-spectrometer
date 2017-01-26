import sys
from PyQt4 import QtCore, QtGui, uic

class RunTableModel(QtCore.QAbstractTableModel):
    def __init__(self, runs=[]):
        """
        `runs` are a list of run settings, format [[8,1,1],[9,2,2]].
        """
        super().__init__()
        self._headers = ['Integration (ms)', 'Interval (s)', 'Repeat']
        self._runs = runs
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    def rowCount(self, parent): return len(self._runs)
    def columnCount(self, parent): return 3
    
    def data(self, index, role):
        if not index.isValid(): return None
        if role == QtCore.Qt.DisplayRole:
            return self._runs[index.row()][index.column()]
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        else:
            return None
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        self._runs[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return section+1

class SpinBoxDelegate(QtGui.QItemDelegate):
    def __init__(self):
        super().__init__()
        
    def setEditorData(self, editor, index):
        editor.setValue(index.model()._runs[index.row()][index.column()])
        
    def setModelData(self, editor, model, index):
        model.setData(index, editor.value())
        
    def currentValueChanged(self):
        self.commitData.emit(self.sender())
        
class IntegrationDelegate(SpinBoxDelegate):
    def __init__(self): super().__init__()
    def createEditor(self, parent, option, index):
        spinbox = QtGui.QDoubleSpinBox(parent)
        spinbox.setRange(8, 10000)
        spinbox.setDecimals(1)
        spinbox.valueChanged.connect(self.currentValueChanged)
        return spinbox
        
class IntervalDelegate(SpinBoxDelegate):
    def __init__(self): super().__init__()
    def createEditor(self, parent, option, index):
        spinbox = QtGui.QDoubleSpinBox(parent)
        spinbox.valueChanged.connect(self.currentValueChanged)
        return spinbox
        
class RepeatDelegate(SpinBoxDelegate):
    def __init__(self): super().__init__()
    def createEditor(self, parent, option, index):
        spinbox = QtGui.QSpinBox(parent)
        spinbox.valueChanged.connect(self.currentValueChanged)
        return spinbox

Ui_Dialog, QDialog = uic.loadUiType('ui/run_table_dialog.ui')
class RunTableDialog(QDialog, Ui_Dialog):
    def __init__(self, runs=[]):
        super().__init__()
        self.setupUi(self)

        self.model = RunTableModel(runs=runs)
        self.tableViewRun.setModel(self.model)
        
        self._delegates = [IntegrationDelegate(), IntervalDelegate(), RepeatDelegate()]
        self.tableViewRun.setItemDelegateForColumn(0, self._delegates[0])
        self.tableViewRun.setItemDelegateForColumn(1, self._delegates[1])
        self.tableViewRun.setItemDelegateForColumn(2, self._delegates[2])
        self.tableViewRun.selectionModel().selectionChanged.connect(self.enableInsert)
        
        self.pushButtonAdd.clicked.connect(self.add)
        self.pushButtonInsert.clicked.connect(self.insert)
        self.pushButtonRemove.clicked.connect(self.remove)
        self.pushButtonRemoveAll.clicked.connect(self.removeAll)
        
        self.toolButtonDir.clicked.connect(self.setDir)
        
    def enableInsert(self):
        enabled = False if len(self.tableViewRun.selectedIndexes()) == 0 else True
        self.pushButtonInsert.setEnabled(enabled)
        self.pushButtonRemove.setEnabled(enabled)
        
    def add(self):
        self.insertAt(len(self.model._runs))
    
    def insert(self):
        row = self.tableViewRun.selectedIndexes()[0].row()
        self.insertAt(row)
        
    def insertAt(self, row):
        self.model._runs.insert(row, [8,1,1])
        self.model.layoutChanged.emit()
        
    def remove(self):
        row = self.tableViewRun.selectedIndexes()[0].row()
        del self.model._runs[row]
        self.model.layoutChanged.emit()
        
    def removeAll(self):
        del self.model._runs[:] # delete content, but keep the list
        self.model.layoutChanged.emit()
        
    def setDir(self):
        dir = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', '/', \
                                                     QtGui.QFileDialog.ShowDirsOnly)
        self.lineEditDir.setText(dir)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = RunTableDialog()
    main.show()
    sys.exit(app.exec_())
