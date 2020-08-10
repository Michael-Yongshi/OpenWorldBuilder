import sys
import os

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    )

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
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

from source.database import (
    Database,
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

        self.db = None
        self.filename = None
        self.nav_list = [["stories", "Story"],["events", "Event"],["timelines", "TimeLines"], ["locations", "Locations"],["characters", "Characters"]]
        self.nav_selected = None
        self.item_list = []
        self.item_selected = None

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
       
        # Some window settings
        self.setWindowTitle('OpenWorldBuilder')
        self.setWindowIcon(QIcon('globe-23544_640.ico'))     
        
        # get items from database if there is selected
        self.get_items()

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
        if self.item_list != []:
            for itemdict in self.item_list:
                name = itemdict["name"]
                listwidgetitem = QListWidgetItem(f"{name}")
                listwidgetitem.setData(1, itemdict)
                listwidget.addItem(listwidgetitem)
            listwidget.itemClicked.connect(self.set_item_selection)

        for nav_item in self.nav_list:
            box = QHBoxLayout()

            listbtn = QPushButton()
            listbtn.setText(nav_item[1])
            listbtn.clicked.connect(self.closure_nav_selection(nav_item[0]))
            box.addWidget(listbtn, 4)

            newbtn = QPushButton()
            newbtn.setText("+")
            newbtn.clicked.connect(self.closure_new_item(nav_item[0]))
            box.addWidget(newbtn, 1)

            if self.db == None:
                listbtn.setDisabled(True)
                newbtn.setDisabled(True)

            frame = QBorderlessFrame()
            frame.setLayout(box)
            navbox.addWidget(frame)

            if self.nav_selected == nav_item[0]:
                navbox.addWidget(listwidget)

        if self.nav_selected == None:
            navbox.addWidget(listwidget)

        navboxframe = QRaisedFrame()
        navboxframe.setLayout(navbox)

        # set the list box to fixed horizontal size to avoid filling up the page when latter is empty
        navboxframe.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        return navboxframe      

    def set_pagebox(self):

        # vertical layout for left and right part
        pagebox = QVBoxLayout()

        if self.item_selected != None:
            for key in self.item_selected.keys():
                label = QLabel()
                label.setText(str(self.item_selected[key]))
                pagebox.addWidget(label)

            btn = QPushButton()
            btn.setText("Edit")
            btn.clicked.connect(self.closure_update_item(self.item_selected))
            pagebox.addWidget(btn)

        pageboxframe = QRaisedFrame()
        pageboxframe.setLayout(pagebox)

        # set the page box to expanding horizontal size to make sure it fills up the space, disregarding if it has content or not
        pageboxframe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return pageboxframe

    def new_database(self):
        """Create a new world"""

        if self.db != None:
            
            confirm = QMessageBox.question(self, 'Are you sure?', f"There is currently a world loaded.\nDo you want to create a new world?", QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return

        name, okPressed = QInputDialog.getText(self, "Create", "Name your world:")
        if okPressed and name:

            exists = check_existance(filename=name)

            if exists == False:
                self.set_database(filename=name)
            else:
                QMessageBox.warning(self, "Couldn't create world!", f"database with {name} already exists!", QMessageBox.Ok)

    def open_database(self):

        # get list of save files /databases
        path, files = show_files()

        # Let user choose out of save files
        name, okPressed = QInputDialog.getItem(self, "Choose", "Choose your world", files, 0, False)
        if okPressed and name:
            self.set_database(filename=name)

    def save_database(self):
        pass

    def saveas_database(self):

        name, okPressed = QInputDialog.getText(self, "Save as...", "Name your new savefile")
        if okPressed and name:
            saveas_file(self.filename, name)

            # QMessageBox.information(self, "Saved", "Save successful!", QMessageBox.Ok)
    
    def close_database(self):
        
        self.db = None
        self.filename = None
        self.initUI()

    def set_database(self, filename, overwrite=False):

        self.db = Database(filename=filename)
        if self.db.filename == filename:
            self.filename = filename
            # print(f"opened database with name: {filename}")

        self.initUI()

    def get_items(self):

        self.item_list = []

        if self.db != None and self.nav_selected != None:

            item_list = self.db.read_records(self.nav_selected)
            # print(item_list)

            column_names = self.db.read_column_names(table=self.nav_selected)
            # print(f"column names {column_names}")

            self.item_list = []
            for item in item_list:
                # print(f"item {item}")
                itemdict = {}
                for c in range(len(column_names)):
                    # print(f"c {c} with column {column_names[c]} and value {item[c]}")
                    itemdict.update({column_names[c]: item[c]})
                self.item_list += [itemdict]
            # print(self.item_list)

            if self.item_list == []:
                self.item_list = [{"id": 0, "name": "No records found"}]
            elif self.item_list == None:
                self.item_list = [{"id": 0, "name": "table not found"}]
    
    def closure_nav_selection(self, selected):
        
        def nav_selection():
            
            self.nav_selected = selected
            self.initUI()

        return nav_selection

    def set_item_selection(self, item):

        self.item_selected = item.data(1)
        self.initUI()

    def closure_new_item(self, selected):

        def new_item():
                
            self.nav_selected = selected

            if self.nav_selected == "events":
                dialog = CreateItemDialogEvent()
            elif self.nav_selected == "stories":
                dialog = CreateItemDialogStory()
            elif self.nav_selected == "timelines":
                dialog = CreateItemDialogTimeline()
            elif self.nav_selected == "locations":
                dialog = CreateItemDialogLocation()
            elif self.nav_selected == "characters":
                dialog = CreateItemDialogCharacter()
            else:
                return

            if dialog.exec():
                datadict = self.db.create_records(table=self.nav_selected, records=[dialog.getQuery()])
                self.item_selected = datadict
                # print(f"created new item in table {self.nav_selected} with id {self.item_selected}")

                self.initUI()

        return new_item

    def closure_update_item(self, row):

        def update_item():
            
            if self.nav_selected == "stories":
                dialog = CreateItemDialogStory()

                dialog.name.setText(self.item_selected["name"])
                dialog.summary.setText(self.item_selected["summary"])
                dialog.body.setText(self.item_selected["body"])

            elif self.nav_selected == "events":
                dialog = CreateItemDialogEvent()

                dialog.name.setText(self.item_selected["name"])
                dialog.description.setText(self.item_selected["description"])
                dialog.intdate.setText(str(self.item_selected["intdate"]))
                dialog.strdate.setText(self.item_selected["strdate"])
                if self.item_selected["begin"] == 1:
                    dialog.begin.setChecked(True)
                else:
                    dialog.begin.setChecked(False)
                if self.item_selected["end"] == 1:
                    dialog.end.setChecked(True)
                else:
                    dialog.end.setChecked(False)

            elif self.nav_selected == "timelines":
                dialog = CreateItemDialogTimeline()

                dialog.name.setText(self.item_selected["name"])
                
            elif self.nav_selected == "locations":
                dialog = CreateItemDialogLocation()

                dialog.name.setText(self.item_selected["name"])
                
            elif self.nav_selected == "characters":
                dialog = CreateItemDialogCharacter()

                dialog.name.setText(self.item_selected["name"])
                
            else:
                return

            if dialog.exec():
                datadict = self.db.update_record(table=self.nav_selected, values=dialog.getQuery(), row=self.item_selected["id"])
                self.item_selected = datadict
                print(f"updated item in table {self.nav_selected} with id {self.item_selected}")
                self.initUI()

        return update_item


def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
