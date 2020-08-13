import datetime

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
    QDateEdit,
    QDateTimeEdit,
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
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget, 
    )

from PyQt5.QtGui import (
    QFont,
    QFontDatabase,
    QIcon,
    )

from source.database import (
    Database,
    Table,
    Record,
)

class RecordLayout(QGridLayout):
    def __init__(self, record):
        super().__init__()

        """
        Builds a layout based upon a Table object
        keeps track of the widgets for easy manipulation
        """

        self.record = record
        self.widgets = []
        self.build_layout()

    def build_layout(self):

        table = self.record.table
        # print(f"table = {table}")
        recordarray = self.record.recordarray
        # print(f"recordarray = {recordarray}")

        for index, columntype in enumerate(table.column_types):

            ctype = columntype.split(' ', 1)[0].upper()
            # print(f"ctype = {ctype}")

            # create the appropriate widget to display the value
            if ctype == "BOOL":
                widget_value = QCheckBox()
                widget_value.setChecked(recordarray[index])                            

            elif ctype == "INTEGER":
                widget_value = QSpinBox()
                widget_value.setMinimum(-1)
                widget_value.setValue(recordarray[index])

            elif ctype == "VARCHAR(255)":
                widget_value = QLineEdit()
                widget_value.setText(recordarray[index])
            
            elif ctype == "TEXT":
                widget_value = QTextEdit()
                widget_value.adjustSize()
                widget_value.insertPlainText(recordarray[index])
                # widget_value.insertHtml(recordarray[index])

            # elif ctype == "DATE":
            #     widget_value = QDateEdit()
            #     date = QDate()
            #     sqldate = recordarray[index]
            #     datestring = datetime.date()
            #     date.fromString(recordarray[index], 'yyyy-MM-dd')
            #     widget_value.setDate(date)

            # elif ctype == "DATETIME" or ctype == "TIMESTAMP":
            #     widget_value = QDateTimeEdit()
            #     date = QDateTime()
            #     sqldate = recordarray[index]
            #     datestring = datetime.datetime()
            #     date.fromString(recordarray[index], 'yyyy-MM-dd')
            #     widget_value.setDate(date)

            else:
                try:
                    # assumed text
                    widget_value = QLineEdit()
                    widget_value.setText(recordarray[index])
                except:
                    widget_value = QLineEdit()
                    widget_value.setText("Error setting widget")

            # set title for widget
            widget_title = QLabel()
            widget_title.setText(table.column_names[index])

            # print(f"column placements are {table.column_placement}")
            # print(f"column placements[index] are {table.column_placement[index]}")

            row = table.column_placement[index][0]
            column = table.column_placement[index][1] + 1
            heigth = table.column_placement[index][2]
            width = table.column_placement[index][3]

            # add widget and title to the layout
            self.addWidget(widget_value, row, column, heigth, width)
            self.addWidget(widget_title, row, 0, heigth, 1)

            # add the value widget to the list of widgets for easy access of values
            self.widgets.append(widget_value)

    def processValues(self):
        """
        Returns a Record object, 
        """

        widgets = self.widgets
        table = self.record.table

        recordarray = []
        for index, columntype in enumerate(table.column_types):
            ctype = columntype.split(' ', 1)[0].upper()
            print(f"ctype = {ctype}")

            if ctype == "VARCHAR(255)":
                recordarray.append(widgets[index].text())
            elif ctype == "TEXT":
                recordarray.append(widgets[index].toPlainText())
            elif ctype == "INTEGER":
                recordarray.append(widgets[index].value())
            elif ctype == "DATE":
                recordarray.append(widgets[index].value())
            elif ctype == "BOOL":
                recordarray.append(widgets[index].isChecked())
            print(f"recordarray building {recordarray}")
        print(f"recordarray processed {recordarray}")
        record = Record(
            table = table,
            recordarray = recordarray,
        )

        return record

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
