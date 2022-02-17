from genericpath import isdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from PyQt5 import QtGui
import sys
import os
from shutil import copyfile
from pathlib import Path
from PyQt5.QtCore import pyqtRemoveInputHook
import json
from datetime import date
from datetime import datetime

class App(QDialog):
    
    def __init__(self):
        super().__init__()
        self.title = ''
        self.left = 100
        self.top = 100
        self.initUI()
        self.path = 'No Path'
        self.obj_list = []
    
    def reject(self):
        print("custom func")
        reply = QMessageBox.question(
                    self,
                    self.tr("Warning!"),
                    'Do you really want to quit?',
                    QMessageBox.Yes,
                    QMessageBox.No,
                )
        if reply == QMessageBox.Yes:
            super().reject()

    def initUI(self):
        # Call the inherited classes __init__ method
        super(App, self).__init__()

        self.root_dir = os.environ.get("_MEIPASS2", os.path.abspath("."))
        self.root_dir = self.root_dir.replace('\\', '/')

        uic.loadUi(f'{self.root_dir}/src/main.ui', self)  # Load the .ui file

        app.setWindowIcon(QtGui.QIcon(f'{self.root_dir}/src/icon.ico'))
        self.setWindowIcon(QtGui.QIcon(f'{self.root_dir}/src/icon.ico'))
        self.title_main = 'Tasker by punishman'
        self.setWindowTitle(self.title_main)

        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint
        )


        self.table = self.findChild(QtWidgets.QTableWidget, 'table')
        self.table.setColumnWidth(0, 115)
        self.table.horizontalHeader().setFixedHeight(30)
        self.table.itemSelectionChanged.connect(self.cell_was_clicked)

        self.addbtn = self.findChild(QtWidgets.QPushButton, 'add')
        self.addbtn.clicked.connect(self.addBtn)

        self.deletebtn = self.findChild(QtWidgets.QPushButton, 'del')
        self.deletebtn.clicked.connect(self.deleteBtn)

        self.savebtn = self.findChild(QtWidgets.QPushButton, 'save')
        self.savebtn.clicked.connect(self.saveBtn)

        self.date = self.findChild(QtWidgets.QLineEdit, 'date')

        self.priority = self.findChild(QtWidgets.QComboBox, 'priority')

        self.labor = self.findChild(QtWidgets.QSpinBox, 'labor')

        self.desc = self.findChild(QtWidgets.QTextEdit, 'desc')

        self.tasks = self.root_dir + '/' + 'tasks.json'

        self.task_data = {
            '17-02-2022':[
                {
                    'desc':'default description',
                    'priority': 'high',
                    'labor': 3
                },
            ],
             '11-02-2022':[
                {
                    'desc':'my awesome description',
                    'priority': 'low',
                    'labor': 12
                },
            ]
        }
        if os.path.isfile(self.tasks):
            self.task_data = json.load(open(self.tasks))
            print('tasks loaded')
        else:
            print('no tasks, lets create a new one')
            f = open(self.tasks, "x")
            f.close()
            f = open(self.tasks, "w")
            json.dump(self.task_data, f)
            f.close()
        
        self.table_repopulate()

        self.table.clearSelection()

        self.show()

    def closeEvent(self, event):
        pass
    
    def table_repopulate(self):
        self.table.setRowCount(len(self.task_data))
        print(len(self.task_data))
        for i in range(len(self.task_data)):
            self.table.setItem(i, 0, QTableWidgetItem(list(self.task_data.keys())[i]))
        
    def clean_inputs(self):
        self.date.setText('')
        self.priority.setCurrentIndex(0)
        self.labor.setValue(0)
        self.desc.setPlainText('')


    def addBtn(self):
        today = date.today()
        self.task_data[str(today)] = [{'desc':'', 'priority':'low', 'labor':0}]
        self.table_repopulate()
        self.clean_inputs()
        self.table.clearSelection()  
        self.save_data()
    
    def deleteBtn(self):
        for index in sorted(self.table.selectionModel().selectedRows()):
            if self.table.selectionModel().hasSelection():
                indexes = [QPersistentModelIndex(
                    index) for index in self.table.selectionModel().selectedRows()]
                for index in indexes:
                    key = self.table.item(index.row(), 0).text()
                    self.task_data.pop(key, None)
                    self.table_repopulate()
                    self.clean_inputs()
                    self.table.clearSelection()
                    self.save_data()
                
    def save_data(self):
        f = open(self.tasks, "w")
        json.dump(self.task_data, f)
        f.close()
    
    def saveBtn(self):
        for index in sorted(self.table.selectionModel().selectedRows()):
            if self.table.selectionModel().hasSelection():
                indexes = [QPersistentModelIndex(
                    index) for index in self.table.selectionModel().selectedRows()]
                for index in indexes:
                    key = self.table.item(index.row(), 0).text()

                    priority = self.priority.currentIndex()
                    if priority == 0:
                        priority = 'low'
                    elif priority == 1:
                        priority = 'medium'
                    elif priority == 2:
                        priority = 'high'

                    labor = int(self.labor.value())
                    desc = self.desc.toPlainText()
                    date = self.date.text()

                    self.task_data[date] = self.task_data[key]
                    del self.task_data[key]

                    self.task_data[date] = [{'desc':desc, 'priority':priority, 'labor':labor}]
                    self.table_repopulate()
                    self.clean_inputs()
                    self.table.clearSelection()
                    self.save_data()
        
    
    def cell_was_clicked(self):
          for index in sorted(self.table.selectionModel().selectedRows()):
            if self.table.selectionModel().hasSelection():
                indexes = [QPersistentModelIndex(
                    index) for index in self.table.selectionModel().selectedRows()]
                for index in indexes:
                    key = self.table.item(index.row(), 0).text()
                   
                    priority = self.task_data[key][0]['priority']
                    if priority == 'low':
                        priority = 0
                    elif priority == 'medium':
                        priority = 1
                    elif priority == 'high':
                        priority = 2

                    labor = int(self.task_data[key][0]['labor'])
                    desc = self.task_data[key][0]['desc']

                    self.date.setText(key)
                    self.priority.setCurrentIndex(priority)
                    self.labor.setValue(labor)
                    self.desc.setPlainText(desc)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    sys.exit(app.exec_())