import datetime

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QDate,
    QDateTime,
    QVariant,
    )

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
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
    def __init__(self, record, database):
        super().__init__()

        """
        Builds a layout based upon a Table object
        keeps track of the widgets for easy manipulation
        """

        self.database = database
        self.record = record
        self.widgets = []
        self.build_layout()

    def build_layout(self):

        self.build_detailbox()
        self.build_childrenbox()
        self.build_xrefbox()

    def build_detailbox(self):

        box = QGridLayout()
        table = self.record.table
        # print(f"table = {table}")

        recordarray = self.record.recordarray
        # print(f"recordarray = {recordarray}")

        for index, columntype in enumerate(table.column_types):

            # set title for widget
            widget_title = QLabel()
            widget_title.setText(table.column_names[index])

            # check if column is a foreign key, it needs at least 3 text fields between spaces (column name, fk denotion, fk column)
            fkfound = False
            split = columntype.split(' ', 3)
            # print(f"split {split}")
            if len(split) == 3:
                cname = self.record.table.column_names[index]
                creferences = split[1]
                cforeign = split[2]
                
                if creferences.upper() == "REFERENCES":
                    fkfound = True

                    widget_value = QComboBox()
                    foreign_valuepairs = self.record.table.readForeignValues(column=cname)

                    zero_valuepair = [0, f"No {table.column_names[index]}"]
                    valuepairs = [zero_valuepair] + foreign_valuepairs
                    print(f"valuepairs including no choice {valuepairs}")

                    for indexvp, valuepair in enumerate(valuepairs):
                        print(f"indexvp {indexvp}, valuepair {valuepair}")
                        foreign_id = valuepair[0]
                        foreign_name = valuepair[1]
                        widget_value.addItem(foreign_name, foreign_id)
                        widget_tooltip = f"tooltip {foreign_name}"
                        widget_value.setItemData(indexvp, widget_tooltip, Qt.ToolTipRole)
                        print(f"added {foreign_name} with {foreign_id}")

                        if recordarray[index] == foreign_id:
                            # setting the default value and the tooltip for the combobox itself
                            print(f"record shows value {recordarray[index]}")
                            widget_value.setCurrentIndex(indexvp)
                            widget_value.setToolTip(widget_tooltip)

            # if fkfound is true then it was a foreign key and the widget is already made
            if fkfound == False:
                ctype = columntype.split(' ', 1)[0].upper()
                # print(f"ctype = {ctype}")

                if ctype == "INTEGER":
                    widget_value = QSpinBox()
                    widget_value.setMinimum(-1)
                    widget_value.setValue(recordarray[index])

                elif ctype == "BOOL":
                    widget_value = QCheckBox()
                    widget_value.setChecked(recordarray[index])                            

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

                # set focus if widget is "name"
                if table.column_names[index] == "name":
                    widget_value.setFocusPolicy(Qt.StrongFocus)

            # print(f"column placements are {table.column_placement}")
            # print(f"column placements[index] are {table.column_placement[index]}")
            row = table.column_placement[index][0]
            column = table.column_placement[index][1] + 1
            heigth = table.column_placement[index][2]
            width = table.column_placement[index][3]

            # add widget and title to the layout
            box.addWidget(widget_value, row, column, heigth, width)
            box.addWidget(widget_title, row, 0, heigth, 1)

            # add the value widget to the list of widgets for easy access of values
            self.widgets.append(widget_value)

        # finish  window
        frame = QFrame()
        frame.setLayout(box)
        self.addWidget(frame, 0,0,2,8)

    def build_childrenbox(self):
        """
        gather the one to many children of this record,
        so gather the tables that have a foreign key to this table
        and show the foreign records (children) belonging to this record

        i.e. if this record denotes the 'Roman Empire', collect all the countries belonging to it
        """
        box = QVBoxLayout()

        for table in self.database.tables:
            reference_text = f"{self.record.table.name}(id)"
            for ctype in table.column_types:
                ctypesplit = ctype.split("_", 3)
                try:
                    if ctypesplit[2] == reference_text:
                        widget = QLabel()
                        widget.setText(f"child found as {reference_text} in {table}")
                        box.addWidget(widget)

                        # add the value widget to the list of widgets for easy access of values
                        self.childwidgets.append(widget)

                except:
                    pass           

        # finish window
        frame = QFrame()
        frame.setLayout(box)
        self.addWidget(frame, 0,1,1,1)

    def build_xrefbox(self):

        box = QVBoxLayout()


        
        # finish window
        frame = QFrame()
        frame.setLayout(box)
        self.addWidget(frame, 1,1,1,1)

    def processValues(self):
        """
        Returns a Record object, 
        """

        widgets = self.widgets
        table = self.record.table

        recordarray = []
        for index, columntype in enumerate(table.column_types):

            # check if column is a foreign key, it needs at least 3 text fields between spaces (column name, fk denotion, fk column)
            fkfound = False

            split = columntype.split(' ', 3)
            # print(f"split {split}")

            if len(split) == 3:
                cname = self.record.table.column_names[index]
                creferences = split[1]
                cforeign = split[2]
                
                if creferences.upper() == "REFERENCES":
                    fkfound = True
                    currentindex = widgets[index].currentIndex()
                    currentid = widgets[index].itemData(currentindex)
                    print(f"itemindex {currentindex} and itemdata {currentid}")
                    recordarray.append(currentid)

            if fkfound == False:
                ctype = columntype.split(' ', 1)[0].upper()
                # print(f"ctype = {ctype}")

                if ctype == "VARCHAR(255)":
                    string = self.processText(widgets[index].text())
                    recordarray.append(string)
                elif ctype == "TEXT":
                    string = self.processText(widgets[index].toPlainText())
                    recordarray.append(string)
                elif ctype == "INTEGER":
                    recordarray.append(widgets[index].value())
                elif ctype == "DATE":
                    recordarray.append(widgets[index].value())
                elif ctype == "BOOL":
                    recordarray.append(widgets[index].isChecked())

            # print(f"recordarray building {recordarray}")
        # print(f"recordarray processed {recordarray}")
        record = Record(
            table = table,
            recordarray = recordarray,
        )

        return record

    def processText(self, string):
        
        string = f"""{string}"""
        
        # escaping double quotes
        string.replace('"', '\\"')

        # escaping single quotes
        string.replace("'", "\\'")

        return string

class RecordTableDialog(QDialog):
    def __init__(self, mainwindow):
        super().__init__()

        self.mainwindow = mainwindow
        self.setWindowTitle("Create a new Record table")

        self.name = QLineEdit(self)
        self.name.setText("Arcs")
        self.name.setToolTip("Insert a table name, no spaces")

        self.recordname = QLineEdit(self)
        self.recordname.setText("Arc")
        self.recordname.setToolTip("""
        Insert a record name. If left empty the record will have the table name minus the last letter (assuming table names are multiples of the records they represent
        """)

        self.column_names = QLineEdit(self)
        self.column_names.setText("ordering, name, characterid, description")
        self.column_names.setToolTip("Input column names as a list of strings: 'col1, col2, col3, col4'.")

        self.column_types = QLineEdit(self)
        self.column_types.setText("INTEGER, VARCHAR(255), INTEGER REFERENCES characters(id), TEXT")
        self.column_types.setToolTip("Input column types as a list of strings: 'INTEGER, VARCHAR(255), TEXT, BOOL'.\nEnter a foreign key by using 'REFERENCES <table>(<column>)'")

        self.column_placement = QLineEdit(self)
        self.column_placement.setDisabled(True)
        self.column_placement.setToolTip("Not implemented: row, column, height, widt: [[1,0,1,1], [2,0,1,1], [3,0,1,1], [4,0,10,1]].")

        self.defaults = QLineEdit(self)
        self.defaults.setToolTip("""Insert default values: '0, "", "", True'.""")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("Table name", self.name)
        layout.addRow("Record name", self.recordname)
        layout.addRow("Column names", self.column_names)
        layout.addRow("Column types", self.column_types)
        layout.addRow("Column Placements", self.column_placement)
        layout.addRow("Default values", self.defaults)

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def createTable(self):

        table = self.mainwindow.database.create_table(
            name = self.name.text(),
            record_name = self.recordname.text(),
            column_names = self.column_names.text().split(', '),
            column_types = self.column_types.text().split(', '),
            column_placement = self.column_placement.text().split(', '),
            defaults = self.defaults.text().split(', '),
            )

        return table