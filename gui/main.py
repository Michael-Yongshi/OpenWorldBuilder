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
    CreateItemDialogTime,
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
        self.nav_list = [["stories", "Story"],["events", "Event"],["time", "TimeLines"], ["locations", "Locations"],["characters", "Characters"]]
        self.menu_active = None
        self.items = []

        # set menu bar
        self.set_menu_bar()

        self.initUI()

    def set_menu_bar(self):

        bar = self.menuBar()

        filemenu = bar.addMenu("File")

        newButton = QAction('New', self)
        newButton.setShortcut('Ctrl+N')
        newButton.setStatusTip('Create new world')
        newButton.triggered.connect(self.new_database)
        filemenu.addAction(newButton)

        closeButton = QAction('Open', self)
        closeButton.setShortcut('Ctrl+O')
        closeButton.setStatusTip('Open existing world')
        closeButton.triggered.connect(self.open_database)
        filemenu.addAction(closeButton)

        saveButton = QAction('Save', self)
        saveButton.setShortcut('Ctrl+S')
        saveButton.setStatusTip('Save current world')
        saveButton.triggered.connect(self.save_database)
        filemenu.addAction(saveButton)

        saveButton = QAction('Save As ...', self)
        saveButton.setStatusTip('Save current world')
        saveButton.triggered.connect(self.saveas_database)
        filemenu.addAction(saveButton)

        openButton = QAction('Close', self)
        openButton.setShortcut('Ctrl+C')
        openButton.setStatusTip('Close current world')
        openButton.triggered.connect(self.close_database)
        filemenu.addAction(openButton)

        quitButton = QAction('Quit', self)
        quitButton.setShortcut('Ctrl+Q')
        quitButton.setStatusTip('Quit application')
        quitButton.triggered.connect(self.close)
        filemenu.addAction(quitButton)

    def initUI(self):
       
        # Some window settings
        self.setWindowTitle('OpenWorldBuilder')
        self.setWindowIcon(QIcon(os.path.join('source','globe-23544_640.ico')))     
        
        # get items from database if there is selected
        self.get_items()

        # build overview
        nested_widget = self.set_nested_widget()

        self.setCentralWidget(nested_widget)
        self.showMaximized()

    def get_items(self):

        self.items = []

        if self.db != None:
            # print(selected)

            self.items = self.db.read_records(self.menu_active)

            if self.items == []:
                self.items = ["No records found"]
            elif self.items == None:
                self.items = ["table not found"]

    def set_nested_widget(self):

        # vertical layout for left and right part
        overviewbox = QGridLayout()

        overviewbox.addWidget(self.set_selectbox(), 0, 0, 3, 1)
        overviewbox.addWidget(self.set_pagebox(), 0, 1, 3, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

    def set_selectbox(self):

        # vertical layout for left and right part
        selectbox = QVBoxLayout()

        filenamelabel = QLabel()
        filenamelabel.setText(f"World openend: {self.filename}")
        selectbox.addWidget(filenamelabel)

        listwidget = QListWidget()
        if self.items != []:
            for record in self.items:
                listwidget.addItem(QListWidgetItem(f"{record}", listwidget))

        for nav_item in self.nav_list:
            box = QHBoxLayout()

            listbtn = QPushButton()
            listbtn.setText(nav_item[1])
            listbtn.clicked.connect(self.closure_set_selection(nav_item[0]))
            box.addWidget(listbtn, 4)

            newbtn = QPushButton()
            newbtn.setText("+")
            newbtn.clicked.connect(self.closure_new_item(nav_item[0]))
            box.addWidget(newbtn, 1)

            frame = QBorderlessFrame()
            frame.setLayout(box)
            selectbox.addWidget(frame)

            if self.menu_active == nav_item[0]:
                selectbox.addWidget(listwidget)

        if self.menu_active == None:
            selectbox.addWidget(listwidget)

        selectboxframe = QRaisedFrame()
        selectboxframe.setLayout(selectbox)

        # set the list box to fixed horizontal size to avoid filling up the page when latter is empty
        selectboxframe.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        return selectboxframe      

    def set_pagebox(self):

        # vertical layout for left and right part
        pagebox = QVBoxLayout()

        # pagebox.addWidget(eventbtn)

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
            print(f"opened database with name: {filename}")

        self.initUI()

    def closure_new_item(self, selected):

        def new_item():
            
            if self.db == None:
                return
                
            self.menu_active = selected

            if self.menu_active == "events":
                dialog = CreateItemDialogEvent()
            elif self.menu_active == "stories":
                dialog = CreateItemDialogStory()
            elif self.menu_active == "time":
                dialog = CreateItemDialogTime()
            elif self.menu_active == "locations":
                dialog = CreateItemDialogLocation()
            elif self.menu_active == "characters":
                dialog = CreateItemDialogCharacter()
            else:
                return

            if dialog.exec():
                # QMessageBox.information(self, "New item", f"{dialog.getInputs()}", QMessageBox.Ok)
                self.selected_item = self.db.create_records(table=self.menu_active, records=dialog.getInputs())
                # print(self.selected_item)

                self.initUI()

        return new_item

    def closure_set_selection(self, selected):
        
        def set_selection():
            
            self.menu_active = selected
            self.initUI()

        return set_selection


def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
