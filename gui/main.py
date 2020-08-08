import sys

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    )

from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
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
    
from wamcore.methods_engine import (
    save_warband,
    load_warband,
    show_warbands,
    save_reference,
    load_reference,
    )

from wamcore.class_hierarchy import (
    Warband,
    Squad,
    Character,
    Hero,
    Henchman,
    Rule,
    Treasury,
    Item,
    Skill,
    Ability,
    Magic,
    )

from guidarktheme.widget_template import *

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
        self.initUI()

    def initUI(self):
       
        # Some window settings
        self.setWindowTitle('OpenWorldBuilder')
        self.setWindowIcon(QIcon('globe-23544_640.ico'))     

        # build overview
        nested_widget = self.set_nested_widget()

        self.setCentralWidget(nested_widget)
        self.showMaximized()

    def set_nested_widget(self):

        # vertical layout for left and right part
        overviewbox = QGridLayout()
        overviewbox.addWidget(self.set_navbox(), 0, 0, 1, 1)
        overviewbox.addWidget(self.set_pagebox(), 0, 1, 1, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

    def set_navbox(self):

        # vertical layout for left and right part
        navbox = QVBoxLayout()

        storybtn = QPushButton()
        storybtn.setText("Story")
        navbox.addWidget(storybtn)

        timebtn = QPushButton()
        timebtn.setText("Timelines")
        navbox.addWidget(timebtn)

        localebtn = QPushButton()
        localebtn.setText("Locations")
        navbox.addWidget(localebtn)

        charbtn = QPushButton()
        charbtn.setText("Characters")
        navbox.addWidget(charbtn)

        eventbtn = QPushButton()
        eventbtn.setText("Events")
        navbox.addWidget(eventbtn)

        navboxframe = QBorderlessFrame()
        navboxframe.setLayout(navbox)

        return navboxframe


    def set_pagebox(self):

        # vertical layout for left and right part
        pagebox = QVBoxLayout()

        # pagebox.addWidget(eventbtn)

        pageboxframe = QBorderlessFrame()
        pageboxframe.setLayout(pagebox)

        return pageboxframe

def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
