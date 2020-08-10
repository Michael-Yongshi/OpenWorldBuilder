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

    def getInputs(self):

        recordstring = f""
        
        recordstring += f"'{self.name.text()}',"
        recordstring += f"'{self.summary.text()}'," 
        recordstring += f"'{self.body.text()}'"

        return [recordstring]

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

    def getInputs(self):

        recordstring = f""

        recordstring += f"'{self.name.text()}',"
        recordstring += f"'{self.description.text()}'," 
        recordstring += f"{int(self.intdate.text())}," 
        recordstring += f"'{self.strdate.text()}',"
        recordstring += f"{int(self.begin.isChecked())},"
        recordstring += f"{int(self.end.isChecked())}"

        return [recordstring]

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

    def getInputs(self):

        recordstring = f""
        
        recordstring += f"'{self.name.text()}',"
        recordstring += f"'{self.format.text()}'," 
        recordstring += f"'{self.description.text()}'"

        return [recordstring]

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

    def getInputs(self):

        recordstring = f""
        
        recordstring += f"'{self.name.text()}',"
        recordstring += f"'{self.description.text()}'"

        return [recordstring]

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

    def getInputs(self):

        recordstring = f""

        recordstring += f"'{self.name.text()}',"
        recordstring += f"'{self.age.text()}'," 
        recordstring += f"'{self.gender.text()}'," 
        recordstring += f"'{self.nationality.text()}'," 
        recordstring += f"'{self.race.text()}'" 

        return [recordstring]