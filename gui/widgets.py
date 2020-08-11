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

class CreateItemDialogStory(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a new Story")

        self.name = QLineEdit(self)
        self.summary = QLineEdit(self)
        self.body = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Summary", self.summary)
        layout.addRow("Body", self.body)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getQuery(self):

        values = []

        values += [self.name.text()]
        values += [self.summary.text()]
        values += [self.body.text()]

        return values

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

        layout.addRow("Name", self.name)
        layout.addRow("Description", self.description)
        layout.addRow("Date integer", self.intdate)
        layout.addRow("Readable date", self.strdate)
        layout.addRow("Beginning", self.begin)
        layout.addRow("Ending", self.end)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getQuery(self):

        values = []

        values += [self.name.text()]
        values += [self.description.text()]
        values += [int(self.intdate.text())]
        values += [self.strdate.text()]
        values += [int(self.begin.isChecked())]
        values += [int(self.end.isChecked())]

        return values

class CreateItemDialogTimeline(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a new Timeline")

        self.name = QLineEdit(self)
        self.format = QLineEdit(self)
        self.description = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Format", self.format)
        layout.addRow("Description", self.description)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getQuery(self):

        values = []

        values += [self.name.text()]
        values += [self.format.text()]
        values += [self.description.text()]

        return values

class CreateItemDialogLocation(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a new Location")

        self.name = QLineEdit(self)
        self.description = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Name", self.name)
        layout.addRow("Description", self.description)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getQuery(self):

        values = []

        values += [self.name.text()]
        values += [self.description.text()]

        return values

class CreateItemDialogCharacter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create a new Character")
        
        self.name = QLineEdit(self)
        self.age = QLineEdit(self)
        self.gender = QLineEdit(self)
        self.nationality = QLineEdit(self)
        self.race = QLineEdit(self)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)

        layout.addRow("Name", self.name)
        layout.addRow("Age", self.age)
        layout.addRow("Gender", self.gender)
        layout.addRow("Nationality", self.nationality)
        layout.addRow("Race", self.race)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)


    def getQuery(self):

        values = []

        values += [self.name.text()]
        values += [self.age.text()]
        values += [self.gender.text()]
        values += [self.nationality.text()]
        values += [self.race.text()]

        return values
