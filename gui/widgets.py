from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    )

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
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
    QVBoxLayout,
    QWidget, 
    )

from PyQt5.QtGui import (
    QFont,
    QFontDatabase,
    QIcon,
    )

class CreateItemDialogEvent(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a new Event")
        self.name = QLineEdit(self)
        self.description = QLineEdit(self)
        self.intdate = QLineEdit(self)
        self.strdate = QLineEdit(self)
        self.begin = QCheckBox(self)
        self.end = QCheckBox(self)

        self.begin.setChecked(True)
        self.end.setChecked(True)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)

        layout.addRow("What will the name of this event be?", self.name)
        layout.addRow("How would you describe this event?", self.description)
        layout.addRow("What is the date of this event in days?", self.intdate)
        layout.addRow("What is the date of this event in text?", self.strdate)
        layout.addRow("Is this a starting event?", self.begin)
        layout.addRow("Is this a finished event?", self.end)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        newitem = [f"'{self.name.text()}', '{self.description.text()}', {int(self.intdate.text())}, '{self.strdate.text()}', {int(self.begin.isChecked())}, {int(self.end.isChecked())}"]
        return newitem

class CreateItemDialogStory(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

class CreateItemDialogTimeline(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

class CreateItemDialogLocation(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

class CreateItemDialogCharacter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
