import sys
import os
from datetime import datetime

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QDate,
    QDateTime,
    )

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDateTimeEdit,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton, 
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget, 
    )

from PyQt5.QtGui import (
    QFont,
    QFontDatabase,
    QIcon,
    )
    
from guidarktheme.widget_template import *
from guidarktheme.decorators import Decorators

from gui.widgets import (
    RecordLayout,
)

from source.tablebuilder import create_database
from source.database import (
    Database,
    Table,
    Record,
    show_files,
    saveas_file,
    check_existance,
    get_localpath,
)

class QMainApplication(QApplication):
    """A Dark styled application."""
    def __init__(self, *__args):
        super().__init__(*__args)
        
        QFontDatabase.addApplicationFont("source/schoensperger.otf")
        self.setStyle("Fusion")
        self.setPalette(QDarkPalette())
        # self.setFont(QFont("schoensperger", 20))
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px solid white; }")
    

class WorldOverview(QMainWindow):
    """The main window that everything runs in"""
    def __init__(self):
        super().__init__()

        # Some window settings
        self.setWindowTitle('OpenWorldBuilder')
        self.setWindowIcon(QIcon('globe-23544_640.ico'))

        # file settings
        self.filename = None
        self.path = get_localpath()
        self.database = None

        # selection settings
        self.table_selected = None # Table object
        self.table_records = [] # list of records from table_selected
        self.record_selected = None

        # set menu bar
        self.set_menu_bar()

        self.initUI()

    def set_menu_bar(self):

        bar = self.menuBar()

        filemenu = bar.addMenu("File")

        buttons = [
            {
                "name": "New",
                "shortcut": "Ctrl+N",
                "tooltip": "Create new world",
                "connect": self.new_database
            },
            {
                "name": "Open",
                "shortcut": "Ctrl+O",
                "tooltip": "Open existing world",
                "connect": self.open_database
            },
            # {
            #     "name": "Save",
            #     "shortcut": "Ctrl+S",
            #     "tooltip": "Save current world",
            #     "connect": self.save_database
            # },
            {
                "name": "SaveAs",
                "shortcut": "",
                "tooltip": "Save current world as ...",
                "connect": self.saveas_database
            },
            {
                "name": "Close",
                "shortcut": "",
                "tooltip": "Close current world",
                "connect": self.close_database
            },
            {
                "name": "Quit",
                "shortcut": "Ctrl+Q",
                "tooltip": "Quit application",
                "connect": self.close
            },
        ]

        for button in buttons:

            btn = QAction(button["name"], self)
            btn.setShortcut(button["shortcut"])
            btn.setStatusTip(button["tooltip"])
            btn.triggered.connect(button["connect"])
            filemenu.addAction(btn)

    def initUI(self):     
        
        # build overview
        nested_widget = self.set_nested_widget()

        self.setCentralWidget(nested_widget)
        self.showMaximized()

        # self.widgets[1].setFocus()

        # build a startup window if filename is empty
        if self.database == None:
            self.open_database(filename="")

    def set_nested_widget(self):

        overviewbox = QGridLayout()

        if self.database != None:
            # get records from database if there is a table selected
            self.get_records()
            
            # vertical layout for left and right part
            overviewbox.addWidget(self.set_navbox(), 0, 0, 3, 1)
            overviewbox.addWidget(self.set_pagebox(), 0, 1, 3, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

    def set_navbox(self):

        # vertical layout for left and right part
        navbox = QVBoxLayout()

        filenamelabel = QLabel()
        filenamelabel.setText(f"World openend: <b>{self.database.filename}</b>")
        navbox.addWidget(filenamelabel)

        listwidget = QListWidget()
        # print(f"table records {self.table_records}")
        if self.table_records != []:
            for record in self.table_records:
                print(record.values)
                name = record.values[1] # take name as first value after primary key
                listwidgetitem = QListWidgetItem(f"{name}")
                listwidgetitem.setData(1, record)
                listwidget.addItem(listwidgetitem)
            listwidget.itemClicked.connect(self.set_record_from_widget_item)

        for table in self.database.tables:
            box = QHBoxLayout()

            listbtn = QPushButton()
            listbtn.setText(table.name.title())
            listbtn.clicked.connect(self.closure_nav_selection(table))
            box.addWidget(listbtn, 5)

            newbtn = QPushButton()
            newbtn.setText("+")
            newbtn.clicked.connect(self.closure_set_new_record_selection(table))
            box.addWidget(newbtn, 1)

            frame = QBorderlessFrame()
            frame.setLayout(box)
            navbox.addWidget(frame)

            if self.table_selected == table:
                navbox.addWidget(listwidget)

        if self.table_selected == None:
            navbox.addWidget(listwidget)

        navboxframe = QRaisedFrame()
        navboxframe.setLayout(navbox)

        # set the list box to fixed horizontal size to avoid filling up the page when latter is empty
        navboxframe.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        return navboxframe      

    def set_pagebox(self):

        pagebox = QVBoxLayout()

        # we will create a gridlayout of the selected record with all the widgets and a seperate array with the widgets in order to manipulate them and pull values
        if self.record_selected != None:
            self.record_layout = RecordLayout(self.record_selected, self.database.tables)
        else:
            self.record_layout = QGridLayout()
        record_frame = QRaisedFrame()
        record_frame.setLayout(self.record_layout)
        pagebox.addWidget(record_frame, 15)

        # adding a new, create or edit button
        buttonbox = QHBoxLayout()
        
        if self.table_selected != None:
            if self.record_selected == None:
                newbtn = QPushButton()
                newbtn.setText("New Record")
                newbtn.clicked.connect(self.closure_set_new_record_selection(self.table_selected))
                buttonbox.addWidget(newbtn, 1)

            elif self.record_selected != None:
                if self.record_selected.primarykey == -1:
                    createbtn = QPushButton()
                    createbtn.setText("Confirm Creation")
                    createbtn.setShortcut("Ctrl+S")
                    createbtn.clicked.connect(self.create_record)
                    buttonbox.addWidget(createbtn, 1)

                else:
                    updatebtn = QPushButton()
                    updatebtn.setText("Confirm Update")
                    updatebtn.setShortcut("Ctrl+S")
                    updatebtn.clicked.connect(self.update_record)
                    buttonbox.addWidget(updatebtn, 1)

                    delbtn = QPushButton()
                    delbtn.setText("Delete")
                    delbtn.clicked.connect(self.delete_record)
                    buttonbox.addWidget(delbtn, 1)
        
        buttonframe = QRaisedFrame()
        buttonframe.setLayout(buttonbox)
        pagebox.addWidget(buttonframe, 1)

        pageboxframe = QRaisedFrame()
        pageboxframe.setLayout(pagebox)

        # set the page box to expanding horizontal size to make sure it fills up the space, disregarding if it has content or not
        pageboxframe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return pageboxframe

    def new_database(self):
        """Create a new world"""

        if self.database != None:
            confirm = QMessageBox.question(self, 'Are you sure?', f"There is currently a world loaded.\nDo you want to create a new world?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.No:
                return

        name, okPressed = QInputDialog.getText(self, "Create", "Name your world:")
        if okPressed and name:

            if check_existance(filename=name) == False:
                self.clean_variables()
                self.database = create_database(filename = name, path="")
                self.initUI()

            else:
                QMessageBox.warning(self, "Couldn't create world!", f"database with {name} already exists!", QMessageBox.Ok)

    def open_database(self, filename="", path=""):

        # if filename is not given
        if filename == "" or filename == False:

            # get list of save files /databases
            path, files = show_files()
            names = ["* New world"] + files

            # Let user choose out of save files
            name, okPressed = QInputDialog.getItem(self, "Choose", "Choose your world", names, 0, False)
            if okPressed and name:
                if name == "* New world":
                    self.new_database()
                    return
                else:
                    filename = name

        if filename != "" and filename != None:
            # print(filename)
            
            # clean data
            self.clean_variables()
            self.database = Database(filename=filename, path=path)
            self.initUI()

    def clean_variables(self):
            # clean data
            self.table_selected = None # Table object
            self.table_records = [] # list of records from table_selected
            self.record_selected = None

    def save_database(self):
        pass

    def saveas_database(self):

        name, okPressed = QInputDialog.getText(self, "Save as...", "Name your new savefile")
        if okPressed and name:
            if check_existance(filename=name) == False:

                # save the database under a different name and then select the new database
                self.database.saveas_database(filename=name, path=self.database.path)
                self.open_database(filename=name, path=self.database.path)

                QMessageBox.information(self, "Saved", "Save successful!", QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Couldn't create world!", f"database with {name} already exists!", QMessageBox.Ok)

    def close_database(self):
        
        # clean data
        self.clean_variables()

        self.initUI()

    def get_records(self):

        self.table_records = []

        if self.table_selected != None:

            self.table_records = self.table_selected.readRecords()
            # print(self.table_records)
    
    def closure_nav_selection(self, selected):
        
        def nav_selection():
            
            self.table_selected = selected
            self.record_selected = None
            self.initUI()

        return nav_selection

    def set_record_from_widget_item(self, widgetitem):

        record = widgetitem.data(1)
        self.set_record_selection(record=record)

    def set_record_selection(self, record):
        # merge with previous method?
        self.record_selected = record
        self.initUI()

    def closure_set_new_record_selection(self, selected):

        def set_new_record_selection():
                
            self.table_selected = selected
            self.record_selected = self.table_selected.create_draft_record()

            self.initUI()

        return set_new_record_selection

    def create_record(self):

        # get a Record object for the new record
        newrecord = self.record_layout.processValues()
        print(f"newrecord including orderer {newrecord.values}")

        # create the new record in database and retrieve the new record from database
        record = newrecord.table.createRecord(values=newrecord.values)
        # print(f"record {newrecord.recordarray}")

        # set the selected record to the new record
        self.set_record_selection(record)

        self.initUI()

    def update_record(self):

        # get a Record object for the new record
        updaterecord = self.record_layout.processValues()

        # update the record in database and retrieve the updated record from database
        record = self.table_selected.updateRecordbyID(rowid=updaterecord.primarykey, valuepairs=updaterecord.valuepairs)

        self.set_record_selection(record)
        self.initUI()

    def delete_record(self):

        pass

def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
