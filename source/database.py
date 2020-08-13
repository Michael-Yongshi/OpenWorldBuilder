import os
import datetime

from pathlib import Path

from shutil import copyfile

import sqlite3
from sqlite3 import Error


# https://stackoverflow.com/questions/2047814/is-it-possible-to-store-python-class-objects-in-sqlite

def get_localpath():
    """set the paths to the users documents folder"""

    local_path = os.path.join("~", "Documents", "OWB")
    path = os.path.expanduser(local_path)

    return path

def show_files(path = ""):
    """Show all files in a folder"""

    if path == "":
        path = get_localpath()

    # Create file list
    filelist = []
    # check if directory already exists, if not cancel opening
    if not os.path.exists(path):
        print(f"couldnt find path: {path}")
        return filelist
        
    # Iterate over sqlite files
    for filename in os.listdir(path):
        if filename.endswith(".sqlite"): 
            name = os.path.splitext(filename)[0]
            filelist.append(name)

    return path, filelist

def saveas_file(srcfile, dstfile, srcpath = "", dstpath = ""):

    srcpath = srcpath if srcpath != "" else get_localpath()
    dstpath = dstpath if dstpath != "" else get_localpath()
    
    src = os.path.join(srcpath, srcfile + ".sqlite")
    dst = os.path.join(dstpath, dstfile + ".sqlite")

    if os.path.exists(src):
        if os.path.exists(dst):
            print(f"error path destination: {dstpath}{dstfile} already exists")

        else:
            print(f"copying file")
            copyfile(srcpath, dst)

def check_existance(filename, path = "", extension = ".sqlite"):

    path = path if path != "" else get_localpath()

    destination = os.path.join(path, filename + extension)
    if os.path.exists(destination):
        print(f"destination: {destination} already exists")
        return True
    else:
        return False

class Database(object):

    def __init__(self, path = "", filename = ""):

        self.connection = None

        if filename == "":
            filename = "test"
        self.filename = filename

        if path == "":
            path = get_localpath()
        self.path = path
        
        try:
            destination = os.path.join(path, filename + ".sqlite")

            # check if directory already exists, if not create it
            if not os.path.exists(path):
                os.makedirs(path)

            self.connection = sqlite3.connect(destination)
            print("Connection to SQLite DB successful")

        except Error as e:

            print(f"The error '{e}' occurred")

    def delete_database(self):

        self.connection.close()

        completepath = os.path.join(self.path, self.filename + ".sqlite")
        os.remove(completepath)

    def execute_query(self, query):
        cursor = self.connection.cursor()

        try:
            print(f"--------------------\n{query}\n")
            cursor.execute(query)
            self.connection.commit()
            print("Success!\n--------------------")

            return cursor

        except Error as e:
            print(f"The error '{e}' occurred")

    def create_table(self, table = "test", variables = ["integer INTEGER","text TEXT"]):

        if table == "test":
            drop_test_table = f"DROP TABLE IF EXISTS test;"
            self.execute_query(drop_test_table)

        "create variables text"
        valuetext = ""
        for variable in variables:
            valuetext += f"{variable},\n"
        valuetext = valuetext[:-2]

        create_table = f"CREATE TABLE IF NOT EXISTS {table}(\nid INTEGER PRIMARY KEY AUTOINCREMENT,\n{valuetext}\n);"
        self.execute_query(create_table)

    def create_records(self, table = "test", records = [[1,'test'], [2, 'test']]):

        columns = self.read_column_names(table)[1:]
        # print(f"columns of table {table} are {columns}")
        column_count = len(columns)
        # print(f"column count = {column_count}")
        
        column_text = ""
        for i in range(column_count):
            column_text += f"{columns[i]},"
        column_text = column_text[:-1]
        # print(column_text)

        # print(records)  
        records_text = ""
        for record in records:

            record_text = ""
            for i in range(column_count):
                if isinstance(record[i], str):
                    record_text += f"'{record[i]}', "
                else:
                    record_text += f"{record[i]}, "
                # print(f"i = {i} with {record_text}")
            record_text = record_text[:-2]
            # print(f"record text = {record_text}")

            records_text += f"({record_text}),"
            # print(records_text)
        records_text = records_text[:-1]
        # print(records_text)

        create_record = f"INSERT INTO {table}\n({column_text})\nVALUES\n{records_text}\n;"
        self.execute_query(create_record)

    def read_table_names(self):

        query = f"SELECT name FROM sqlite_master WHERE type='table';"
        
        cursor = self.execute_query(query=query)
        tables = cursor.fetchall()
        # print(tables)
        # for table in tables:
            # print(table)

        return tables

    def read_column_names(self, table = "test"):

        query = f"SELECT * FROM {table};"
        
        cursor = self.execute_query(query=query)
        description = cursor.description

        # print(description)
        columns = []
        for record in description:
            # print(record[0])
            columns += [record[0]]
        
        # print(columns)
        return columns

    def read_records(self, table = "test", columns="*", where = ""):

        select_records = f"SELECT {columns} from {table}"
        if where != "":
            select_records += f" WHERE {where}"

        cursor = self.execute_query(select_records)    
        records = self.get_records_array(cursor.fetchall())

        return records

    def update_records(self, table = "test", valuepairs = [["integer", 3], ["text",'test']], where=""):

        setvaluepairs = ""
        for valuearray in valuepairs:
            if isinstance(valuearray[1], str):
                setvaluepairs += f"{valuearray[0]} = '{valuearray[1]}',\n"
            else:
                setvaluepairs += f"{valuearray[0]} = {valuearray[1]},\n"
            
        setvaluepairs = setvaluepairs[:-2]
        # print(f"setvaluepairs {setvaluepairs}")

        inpart = ""
        for s in where[1]:

            if isinstance(s, str):
                inpart += f"'{s}', "
            else:
                inpart += f"{s}, "

        inpart = inpart[:-2]
        where = f"{where[0]} IN ({inpart})"
        # print(f"where = {where}")

        update_query = f"UPDATE {table} SET\n{setvaluepairs}\nWHERE\n{where}\n;"
        self.execute_query(update_query)

    def get_records_array(self, sqlrecords):

        recordarrays = []

        for sqlrecord in sqlrecords:
            recordarray = []

            for value in sqlrecord:
                recordarray += [value]

            recordarrays += [recordarray]

        return recordarrays

    def get_max_row(self, table):

        cursor = self.execute_query(f"SELECT COUNT(id) FROM {table}")
        lastrow = cursor.fetchall()[0][0]

        return lastrow

class Table(object):
    def __init__(self, db, name, column_names, column_types, record_name = "", defaults = [], initial_records = [], column_placement = []):
        super().__init__()

        # connect to database
        self.db = db

        # set table and record names
        self.name = name
        if record_name == "":
            self.record_name = self.name[:-1]
        else:
            self.record_name = record_name

        # set column names and types
        self.column_types = column_types
        self.column_names = column_names

        # create table
        self.createTable()

        # set column names and types including the primary key
        self.column_types = ["INTEGER"] + self.column_types
        self.column_names = ["id"] + self.column_names

        self.set_defaults(defaults)
        self.set_column_placement(column_placement)

        # initiate records
        self.initial_records = initial_records
        if self.initial_records != []:
            self.createRecords(records=self.initial_records)

    def set_defaults(self, defaults):
        if defaults != []:
            self.defaults = [-1] + defaults
        else:
            self.defaults = []

            self.defaults += [-1]
            for index, value in enumerate(self.column_types[1:]):
                ctype = value.split(' ', 1)[0].upper()

                if ctype == "INTEGER":
                    default = [0]
                elif ctype == "BOOL":
                    default = [False]
                elif ctype == "DATE":
                    default = [datetime.date.today]
                else:
                    default = [""]

                self.defaults += default

            print(f"defaults set are {self.defaults}")
        
    def set_column_placement(self, column_placement):

        if column_placement != []:
            id_placement = [0,0,1,1]
            self.column_placement = [id_placement] + column_placement

        else:
            self.column_placement = []

            for index, value in enumerate(self.column_names):
                indexconfig = [index,0,1,1]
                self.column_placement += [indexconfig]

            print(f"column_placement set are {self.column_placement}")

    def readColumnCount(self, includepk=True):
        """including private key column"""

        if includepk == True:
            return len(self.column_names)
        else:
            return len(self.column_names) - 1

    def readMaxRow(self):
        
        return self.db.get_max_row(table=self.name)

    def readRecords(self, columns=-1, select=[]):

        if columns != -1:
            column_selection = "id, "
            for c in columns:
                column_selection += f"{self.column_names[c]}, "
            column_selection = column_selection[:-2]
        else:
            column_selection = "*"
        # print(f"columns = {column_selection}")

        # print(f"select {select}")
        if select != []:
            inpart = ""
            for s in select[1]:
                s = self.transform_boolean(s)

                if isinstance(s, str):
                    inpart += f"'{s}', "
                else:
                    inpart += f"{s}, "
            inpart = inpart[:-2]
            where = f"{select[0]} IN ({inpart})"
        else:
            where = ""
        # print(f"where = {where}")

        read_records = self.db.read_records(table=self.name, columns=column_selection, where=where)
        records = []
        # print(read_records)
        for record in read_records:
            valuearray = []
            for value in record:
                valuearray += [value]
            recordobject = Record(self, valuearray)
            records += [recordobject]

        return records

    def createTable(self):

        create_query = []
        for c in range(len(self.column_names)):
            create_query.append(f"{self.column_names[c]} {self.column_types[c]}")

        self.db.create_table(table=self.name, variables=create_query)

    def createRecord(self, values):

        for index, value in enumerate(values):
            values[index] = self.transform_boolean(value)
        # print(values)

        self.db.create_records(table=self.name, records=[values])

        newrows_last = self.db.get_max_row(self.name)

        sqlrecords = self.db.read_records(table=self.name, where=f"id = {newrows_last}")
        recordobject = Record(self, sqlrecords[0])

        return recordobject

    def createRecords(self, records):

        if len(records) == 1:
            records = [self.createRecord(records[0])]
            return records

        else:
            newrows_first = self.db.get_max_row(self.name) + 1

            for rindex, record in enumerate(records):
                for vindex, value in enumerate(record):
                    records[rindex][vindex] = self.transform_boolean(value)
            # print(records)

            self.db.create_records(table=self.name, records=records)

            newrows_last = self.db.get_max_row(self.name)
            whererange = range(newrows_first, newrows_last + 1)
            # print(f"create range = {whererange}")

            wherestring = ""
            for row in whererange:
                wherestring += f"{row}, "
            wherestring = wherestring[:-2]
            records = self.db.read_records(table=self.name, where=f"id IN ({wherestring})")

            recordobjects = []
            for record in records:
                recordobjects += [Record(self, record)]

            return recordobjects

    def updateRecordbyID(self, rowid, valuepairs):

        # get a selectstatement from just the rowid
        select = ["id", [rowid]]

        # get record before updating
        record_before = self.readRecords(select=select)[0]
        # print(f"record before = {record_before}")

        # update the record
        # print(valuepairs)
        self.db.update_records(table=self.name, valuepairs=valuepairs, where=select)

        # get record after updating
        record_after = self.readRecords(select=select)[0]
        # print(f"record after = {record_after}")

        if record_before.primarykey != record_after.primarykey:
            print(f"Update messed up the table!!!")
            return

        record_object = record_after
        if record_before.values != record_after.values:
            print(f"updated record {record_object.recordarray}")
        else:
            print(f"update record was not necessary")

        return record_object

    def updateRecords(self, valuepairs, select):

        table_before = self.readRecords()
        # print(f"table before = {table_before}")

        # print(f"valueparis = {valuepairs}")
        for valuearray in valuepairs:
            valuearray[1] = self.transform_boolean(valuearray[1])
        # print(f"valuepairs = {valuepairs}")

        if isinstance(select, int):
            select = ["id", [select]]
        
        # print(f"select {select}")
        for v in range(len(select[1])):
            select[1][v] = self.transform_boolean(select[1][v])
        # print(f"select {select}")

        self.db.update_records(table=self.name, valuepairs=valuepairs, where=select)
                    
        table_after = self.readRecords()
        # print(f"table after = {table_after}")

        record_objects = []
        for index, record in enumerate(table_after):
            if table_before[index].primarykey != record.primarykey:
                print(f"Update messed up the table!!!")
                return
            if table_before[index].values != record.values:
                record_objects += [table_after[index]]
                for row in record_objects:
                    print(f"updated row {row.recordarray}")
                return record_objects

    def transform_boolean(self, value):
        if value == True:
            value = 1
        elif value == False:
            value = 0
        return value

class Record(object):
    def __init__(self, table, recordarray):
        super().__init__()

        """
        Primarykey: 
        primary key of this record

        Recordarray: 
        array of values
        including the primary key

        Recordpairs: 
        array of column - value pairs
        including the primary key column
        
        Values: 
        array of all values
        excluding the primary key
        
        Valuepairs: 
        array of column - value pairs
        excluding the primary key column

        With Record.get_dict() command you get the record in dictionary format where
        you can search easily based on column name
        """

        self.table = table
        self.primarykey = recordarray[0]

        self.recordarray = recordarray
        self.values = recordarray[1:]
        self.setrecordpairs()
        self.setvaluepairs()

    def setrecordpairs(self):
        self.recordpairs = []
        for index, name in enumerate(self.table.column_names):
            recordpair = [name, self.recordarray[index]]
            self.recordpairs += [recordpair]
        print(f"set recordpairs {self.recordpairs}")

    def setvaluepairs(self):
        self.valuepairs = []
        for index, name in enumerate(self.table.column_names[1:]):
            valuepair = [name, self.recordarray[1:][index]]
            self.valuepairs += [valuepair]
        print(f"set valuepairs {self.valuepairs}")


def print_records(records):
    for record in records:
        print(f"-table: {record.table}, primarykey: {record.primarykey}, recordpairs: {record.recordpairs}")

if __name__ == "__main__":

    database = Database(path="", filename="science")
    database.delete_database()

    newtbl = Table(
        db = Database(path="", filename="science"),
        name = "scientists",
        column_names = ["name", "age", "nobelprizewinner"],
        column_types = ["Text", "Integer", "Bool"],
        initial_records = [
            ["Hawking", 68, True]
        ]
    )
    
    #test functions of table
    print(f"read column names: {newtbl.column_names}")

    values = ["Einstein", 100, False]
    record = newtbl.createRecord(values)
    print(f"create single record")
    print_records([record])

    values = [
        ["Rosenburg", 78, False],
        ["Neil dGrasse Tyson", 57, True],
    ]
    records = newtbl.createRecords(values)
    print(f"create multiple records")
    print_records(records)

    records = newtbl.readRecords()
    print(f"read all records")
    print_records(records)

    selection = ["nobelprizewinner", [True]]
    records = newtbl.readRecords(select=selection)
    print(f"read selection")
    print_records(records)

    valuepairs = [["nobelprizewinner", False]]
    selection = ["nobelprizewinner", [True]]
    records = newtbl.updateRecords(valuepairs=valuepairs, select=selection)
    print(f"update true to false")
    print_records(records)

    valuepairs = [["name", "Neil deGrasse Tyson"], ["age", 40]]
    rowid = 4
    record = newtbl.updateRecordbyID(valuepairs = valuepairs, rowid=rowid)
    print(f"update record 'id = 4'")
    print_records([record])