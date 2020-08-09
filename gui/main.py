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

from source.database import (
    Database,
    show_files,
    saveas_file,
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
        self.menu_active = None

        # set menu bar
        bar = self.set_menu_bar()

        self.initUI()

    def initUI(self):
       
        # Some window settings
        self.setWindowTitle('OpenWorldBuilder')
        self.setWindowIcon(QIcon(os.path.join('source','globe-23544_640.ico')))     
        
        # build overview
        nested_widget = self.set_nested_widget()

        self.setCentralWidget(nested_widget)
        self.showMaximized()

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

        return bar

    def set_nested_widget(self):

        # vertical layout for left and right part
        overviewbox = QGridLayout()

        overviewbox.addWidget(self.set_listbox(), 0, 0, 3, 1)
        overviewbox.addWidget(self.set_pagebox(), 0, 1, 3, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

    def set_listbox(self):

        # vertical layout for left and right part
        listbox = QVBoxLayout()

        filenamelabel = QLabel()
        filenamelabel.setText(f"World openend: {self.filename}")
        listbox.addWidget(filenamelabel)

        listwidget = QListWidget()

        if self.db != None:
            dbresult = []
            if self.menu_active == "events":
                dbresult = self.db.get_event_records()

            for record in dbresult:
                listwidget.addItem(QListWidgetItem(record, listwidget))
        
        listbox.addWidget(listwidget)

        listboxframe = QRaisedFrame()
        listboxframe.setLayout(listbox)

        # set the list box to fixed horizontal size to avoid filling up the page when latter is empty
        listboxframe.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        return listboxframe

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
            self.set_database(filename=name)

    def save_database(self):
        pass

    def saveas_database(self):

        name, okPressed = QInputDialog.getText(self, "Save as...", "Name your new savefile")
        if okPressed and name:
            saveas_file(self.filename, name)
                
    def open_database(self):

        # get list of save files /databases
        path, files = show_files()

        # Let user choose out of save files
        name, okPressed = QInputDialog.getItem(self, "Choose", "Choose your world", files, 0, False)

        self.set_database(filename=name)

    def close_database(self):
        
        self.db = None
        self.filename = None
        self.initUI()

    def set_database(self, filename):

        self.db = Database(filename=filename)
        self.filename = filename
        self.initUI()
        print(f"opened database with name: {filename}")

def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
