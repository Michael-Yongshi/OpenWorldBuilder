import sys
import os

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
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

from gui.widgets import (
    CreateItemDialogEvent,
    CreateItemDialogStory,
    CreateItemDialogTimeline,
    CreateItemDialogLocation,
    CreateItemDialogCharacter,
)

from source.tablebuilder import table_builder
from source.database import (
    Database,
    Table,
    show_files,
    saveas_file,
    check_existance,
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
        self.filename = "Template" # initializing template database
        self.tables = table_builder(self.filename) # list of Table objects by default filled with a new sql database

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
            {
                "name": "Save",
                "shortcut": "Ctrl+S",
                "tooltip": "Save current world",
                "connect": self.save_database
            },
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
        
        # get records from database if there is a table selected
        self.get_records()

        # build overview
        nested_widget = self.set_nested_widget()

        self.setCentralWidget(nested_widget)
        self.showMaximized()

    def set_nested_widget(self):

        # vertical layout for left and right part
        overviewbox = QGridLayout()

        overviewbox.addWidget(self.set_navbox(), 0, 0, 3, 1)
        overviewbox.addWidget(self.set_pagebox(), 0, 1, 3, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

    def set_navbox(self):

        # vertical layout for left and right part
        navbox = QVBoxLayout()

        filenamelabel = QLabel()
        filenamelabel.setText(f"World openend: {self.filename}")
        navbox.addWidget(filenamelabel)

        listwidget = QListWidget()
        print(f"table records {self.table_records}")
        if self.table_records != []:
            for recordarray in self.table_records:
                name = recordarray[1][1]
                listwidgetitem = QListWidgetItem(f"{name}")
                listwidgetitem.setData(1, recordarray)
                listwidget.addItem(listwidgetitem)
            listwidget.itemClicked.connect(self.set_record_from_widget_item)

        for table in self.tables:
            box = QHBoxLayout()

            listbtn = QPushButton()
            listbtn.setText(table.name.title())
            listbtn.clicked.connect(self.closure_nav_selection(table))
            box.addWidget(listbtn, 5)

            newbtn = QPushButton()
            newbtn.setText("+")
            newbtn.clicked.connect(self.closure_new_record(table))
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

        # we will create a formlayout with all the widgets and a seperate array with the widgets in order to manipulate them and pull values

        pagebox = QFormLayout()

        table = self.table_selected
        self.pagewidgets = []

        if table != None:
            print(f"column names {table.readColumnNames()}")
            print(f"column types {table.readColumnTypes()}")

            if self.record_selected != None:
                print(f"record_selected {self.record_selected}")
                
            for c in range(len(table.readColumnNames())):
                
                # create the appropriate widget to display and input values, both added to formlayout and to table.column_widgets
                if table.readColumnTypes()[c][:4].upper() == "TEXT":
                    widget = QLineEdit()

                    if self.record_selected != None:
                        if self.record_selected[c][1] != None:
                            widget.setText(self.record_selected[c][1])

                elif table.readColumnTypes()[c][:4].upper() == "BOOL":
                    widget = QCheckBox()

                    if self.record_selected != None:
                        if self.record_selected[c][1] != None:
                            widget.setChecked(self.record_selected[c][1])

                elif table.readColumnTypes()[c][:7].upper() == "INTEGER":
                    widget = QSpinBox()

                    if self.record_selected != None:
                        if self.record_selected[c][1] != None:
                            widget.setValue(self.record_selected[c][1])

                elif table.readColumnTypes()[c][:4].upper() == "DATE":
                    widget = QDateTimeEdit()

                    if self.record_selected != None:
                        if self.record_selected[c][1] != None:
                            widget.setValue(self.record_selected[c][1])

                else:
                    widget = QLineEdit()
                    widget.setText("Couldn't set widget")

                pagebox.addRow(table.readColumnNames()[c], widget)
                self.pagewidgets.append(widget)

            btn = QPushButton()
            btn.setText("Edit")
            btn.clicked.connect(self.closure_update_record(self.record_selected))
            pagebox.addWidget(btn)

        pageboxframe = QRaisedFrame()
        pageboxframe.setLayout(pagebox)

        # set the page box to expanding horizontal size to make sure it fills up the space, disregarding if it has content or not
        pageboxframe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return pageboxframe

    def new_database(self):
        """Create a new world"""

        if self.filename != "Template":
            confirm = QMessageBox.question(self, 'Are you sure?', f"There is currently a world loaded.\nDo you want to create a new world?", QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.No:
                return

        name, okPressed = QInputDialog.getText(self, "Create", "Name your world:")
        if okPressed and name:

            exists = check_existance(filename=name)

            if exists == False:
                
                old_filename = self.filename
                old_tables = self.tables
                self.filename = name
                try:
                    self.set_owb_tables()
                    if self.tables[0].db.filename == name:
                                    
                        # clean data
                        self.tables = []
                        self.table_selected = None # Table object
                        self.table_records = [] # list of records from table_selected
                        self.record_selected = None

                        print(f"opened database with name: {name}")
                    else:
                        self.filename = old_filename
                        self.tables = old_tables
                        print(f"database filename differs")
                except:
                    self.filename = old_filename
                    self.tables = old_tables
                    print(f"failed to open database")

                self.initUI()
            else:
                QMessageBox.warning(self, "Couldn't create world!", f"database with {name} already exists!", QMessageBox.Ok)

    def open_database(self, filename = ""):

        # if filename is not given
        if filename == "":

            # get list of save files /databases
            path, files = show_files()

            # Let user choose out of save files
            name, okPressed = QInputDialog.getItem(self, "Choose", "Choose your world", files, 0, False)
            if okPressed and name:
                filename = name

        if filename != "":
            
            # clean data
            self.tables = []
            self.table_selected = None # Table object
            self.table_records = [] # list of records from table_selected
            self.record_selected = None

            self.filename = filename
            self.set_owb_tables()
            self.initUI()

    def save_database(self):
        pass

    def saveas_database(self):

        name, okPressed = QInputDialog.getText(self, "Save as...", "Name your new savefile")
        if okPressed and name:
            saveas_file(self.filename, name)
            self.open_database(filename=name)
            # QMessageBox.information(self, "Saved", "Save successful!", QMessageBox.Ok)
    
    def close_database(self):
        
        # clean data
        self.tables = []
        self.table_selected = None # Table object
        self.table_records = [] # list of records from table_selected
        self.record_selected = None

        # create new template database
        self.filename = "Template"
        self.set_owb_tables()
        self.initUI()

    def get_records(self):

        self.table_records = []

        if self.table_selected != None:

            table_records = self.table_selected.readRecords()
            # print(table_records)

            column_names = self.table_selected.readColumnNames()
            # print(f"column names {column_names}")

            self.table_records = []
            for record in table_records:
                # print(f"record {record}")
                recordarray = []
                for c in range(len(column_names)):
                    # print(f"c {c} with column {column_names[c]} and value {record[c]}")
                    valuearray = [column_names[c], record[c]]
                    recordarray.append(valuearray)
                self.table_records.append(recordarray)
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

        self.record_selected = record
        self.initUI()

    def closure_new_record(self, selected):

        def new_record():
                
            self.table_selected = selected

            if self.table_selected == "events":
                dialog = CreateItemDialogEvent()
            elif self.table_selected == "stories":
                dialog = CreateItemDialogStory()
            elif self.table_selected == "timelines":
                dialog = CreateItemDialogTimeline()
            elif self.table_selected == "locations":
                dialog = CreateItemDialogLocation()
            elif self.table_selected == "characters":
                dialog = CreateItemDialogCharacter()
            else:
                return

            if dialog.exec():
                datadict = self.db.create_records(table=self.table_selected, records=[dialog.getQuery()])
                self.record_selected = datadict
                # print(f"created new record in table {self.table_selected} with id {self.record_selected}")

                self.initUI()

        return new_record

    def closure_update_record(self, record):

        def update_record():
            names = self.table_selected.readColumnNames()
            types = self.table_selected.readColumnTypes()
            widgets = self.pagewidgets
            recordarray = []

            for i in range(len(types)):
                if types[i][:4].upper() == "TEXT":
                    recordarray.append([names[i],widgets[i].text()])
                elif types[i][:7].upper() == "INTEGER":
                    recordarray.append([names[i],widgets[i].value()])
                elif types[i][:4].upper() == "DATE":
                    recordarray.append([names[i],widgets[i].value()])
                elif types[i][:4].upper() == "BOOL":
                    recordarray.append([names[i],widgets[i].isChecked()])
            
            self.table_selected.updateRecord(recordarray=recordarray, select=self.record_selected[0][1])
            self.set_record_selection(recordarray)
            self.initUI()

        return update_record

def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
