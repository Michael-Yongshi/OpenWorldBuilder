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

        # vertical layout for top and char part
        overviewbox = QGridLayout()
        # overviewbox.addWidget(self.set_topbox(), 0, 0, 1, 3)
        # overviewbox.addWidget(self.set_botbox(), 1, 0, 3, 3)

        overviewboxframe = QBorderlessFrame()
        overviewboxframe.setLayout(overviewbox)

        return overviewboxframe

def run():
    global app
    app = QMainApplication(sys.argv)
    global main
    main = WorldOverview()
    sys.exit(app.exec_())
