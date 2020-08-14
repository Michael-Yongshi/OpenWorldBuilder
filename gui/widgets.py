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

                    for indexvp, valuepair in enumerate(foreign_valuepairs):
                        print(f"indexvp {indexvp}, valuepair {valuepair}")
                        foreign_id = valuepair[0]
                        foreign_name = valuepair[1]
                        widget_value.addItem(foreign_name, foreign_id)
                        print(f"added {foreign_name} with {foreign_id}")

                        if recordarray[index] == foreign_id:
                            print(f"record shows value {recordarray[index]}")
                            widget_value.setCurrentIndex(indexvp)

            # print(f"fkfound {fkfound}")

            # no foreign key when in except, so create the appropriate widget to display the value
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
