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

        print(f"Database deleted!")

    def execute_query(self, query):
        """
        build a parameterised query:
        for a parameter list of 3 length like below
        -parameters = [1,2,3]
        -placeholders = ', '.join('?' for _ in parameters)
        this results in '?, ?, ?'

        meaning
        for each (_ denotes an unused variable) in parameters, join the strings ('?') with a comma and a space (', ') in order to not have to remove a trailing comma

        then merge with query
        -query= 'SELECT name FROM students WHERE id IN (%s)' % placeholders

        meaning
        this replaces the "%s with our placeholders ('?, ?, ?' in our case)
        """
        cursor = self.connection.cursor()

        try:
            print(f"--------------------\n{query}\n")
            cursor.execute(query)
            self.connection.commit()
            print("Success!\n--------------------")

            return cursor

        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_parameterised_query(self, query, parameters):
        cursor = self.connection.cursor()

        try:
            print(f"--------------------query\n{query}\n")
            print(f"--------------------parameters\n{parameters}\n")
            cursor.execute(query, parameters)
            self.connection.commit()
            print("Success!\n--------------------")

            return cursor

        except Error as e:
            print(f"The error '{e}' occurred")

    def read_table_names(self):

        query = f"SELECT name FROM sqlite_master WHERE type='table';"
        
        cursor = self.execute_query(query=query)
        tables = cursor.fetchall()
        # print(tables)
        # for table in tables:
            # print(table)

        return tables

    def read_column_names(self, table):

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

    def read_records(self, table, columns=[], where = []):

        if columns == []:
            column_line = "*"

        else:
            column_line = ', '.join(columns)
        
        parameters = tuple()
        
        # where can be collected as [[column name, [values]], [column name2, [values2]]]
        # print(f"where {where}")
        if where == []:
            whereline = ""

        else:
            whereline = "WHERE "
            for statement in where:
                parameters += tuple(statement[1])
                # print(f"statement {statement}")
                # print(f"statement0 {statement[0]}")
                # print(f"statement1 {statement[1]}")
                whereline += f"{statement[0]}"
                whereline += " IN ("
                whereline += ', '.join('?' for _ in statement[1])
                whereline += ') AND '
            whereline = whereline[:-5]
            # print(f"whereline {whereline}")
        # print(f"parameters = {parameters}")

        query = f"SELECT {column_line} from {table} {whereline}"

        cursor = self.execute_parameterised_query(query, parameters)
        records = self.get_records_array(cursor.fetchall())

        return records

    def create_table(self, table, variables = ["integer INTEGER","text TEXT"]):
        """
        collects input of table name and column information
        builds a single query and 
        forwards to execute_query
        """
        
        # transform variables to string format
        valuetext = ',\n'.join(variables)

        # create variables text
        query = f"CREATE TABLE IF NOT EXISTS {table} (\n{valuetext}\n);"
        self.execute_query(query)

    def create_records(self, table, column_names = ["integer", "text"], valuepairs = [[1,'test'], [2, 'test']]):
        
        # print(f"create records database with table {table}, columns {column_names} and valuepairs {valuepairs}")

        # transform column names to a string
        column_text = ', '.join(column_names)

        # create placeholders
        placeholders = ""
        parameters = ()
        for valuepair in valuepairs:
            valuepair_parameters = tuple(valuepair)
            parameters += valuepair_parameters
            valuepair_placeholders = '(' + ','.join('?' for value in valuepair) + '),\n'
            placeholders += valuepair_placeholders
        placeholders = placeholders[:-2]
        # print(f"placeholders = {placeholders}")
        # print(f"parameters = {parameters}")

        query = f"INSERT INTO {table}\n({column_text})\nVALUES\n{placeholders}\n;"
        self.execute_parameterised_query(query, parameters)

    def update_records(self, table, valuepairs = [["integer", 3], ["text",'test']], where=[["integer", 5]]):

        parameters = tuple()

        # create set_placeholders
        set_placeholders = ""
        for valuepair in valuepairs:
            parameters += tuple([valuepair[1]])
            set_placeholders += valuepair[0] + ' = ?, '
        set_placeholders = set_placeholders[:-2]
        # print(f"set_placeholders = {set_placeholders}")
        # print(f"parameters = {parameters}")

        # create where_placeholders
        where_placeholders = ""
        for statement in where:
            parameters += tuple(statement[1])
            where_placeholders += statement[0] + ' = ? AND '
        where_placeholders = where_placeholders[:-5]
        # print(f"where_placeholders = {where_placeholders}")
        # print(f"parameters = {parameters}")

        query = f"UPDATE {table} SET\n{set_placeholders}\nWHERE\n{where_placeholders}\n;"
        self.execute_parameterised_query(query, parameters)

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

    def get_max_columncontent(self, table, column):

        query = f"SELECT MAX({column}) FROM {table}"

        cursor = self.execute_query(query)
        max_columncontent = cursor.fetchall()
        if max_columncontent[0][0] == None:
            max_columncontent = [(0,)]

        return max_columncontent[0][0]

    def transform_boolean(self, value):
        if value == True:
            value = 1
        elif value == False:
            value = 0
        return value

class Table(object):
    def __init__(self, db, name, column_names, column_types, record_name = "", defaults = [], initial_records = [], column_placement = []):
        super().__init__()

        # set table and record names
        self.name = name
        if record_name == "":
            self.record_name = self.name[:-1]
        else:
            self.record_name = record_name

        # set column names and types including the primary key and ordering column
        self.column_names = ["id", "ordering"] + column_names
        self.column_types = ["INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER"] + column_types

        self.set_defaults(defaults)
        self.set_column_placement(column_placement)

        # set connection to database
        self.db = db

        #### check if table exists, then only open the table, check integrity
        # create tables in database
        self.createTable()

        # initiate records
        if initial_records != []:
            self.createRecords(records=initial_records)

    def move_to_database(self, db):

        # copy table records
        tablerecords = self.readRecords()

        # connect to new database
        self.db = db

        # create tables in new database
        self.createTable()

        # copy records in new database
        tablevalues = []
        for record in tablerecords:
            values = []

            for value in record.values:
                values += [value]

            # print(f"values {values}")
            tablevalues += [values]

        # print(f"tablevalues {tablevalues}")
        self.createRecords(tablevalues)

    def set_defaults(self, defaults):
        if defaults != []:
            self.defaults = [-1, 0] + defaults
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

            # print(f"defaults set are {self.defaults}")
        
    def set_column_placement(self, column_placement):

        if column_placement != []:
            id_placement = [0,0,1,1]
            ordering_placement = [0,1,1,1]
            self.column_placement = [id_placement] + [ordering_placement] + column_placement

        else:
            self.column_placement = []

            for index, value in enumerate(self.column_names):
                indexconfig = [index,0,1,1]
                self.column_placement += [indexconfig]

            # print(f"column_placement set are {self.column_placement}")

    def readColumnCount(self, includepk=True):
        """including private key column"""

        if includepk == True:
            return len(self.column_names)
        else:
            return len(self.column_names) - 1

    def readMaxRow(self):
        
        return self.db.get_max_row(table=self.name)

    def readRecords(self, columns=[], where=[]):

        columns = self.column_names

        # only do something with where if its given
        if where != []:
            if isinstance(where, int):
                where = [["id", [where]]]
            else:
                for statement in where:
                    # if column is a number, get the column name
                    if isinstance(statement[0], int):
                        statement[0] = self.column_names[statement[0]]

        # print(f"where = {where}")

        sqlrecords = self.db.read_records(table=self.name, columns=columns, where=where)

        records = []
        # print(sqlrecords)
        for record in sqlrecords:
            valuearray = []
            for value in record:
                valuearray += [value]
            recordobject = Record(self, valuearray)
            records += [recordobject]

        return records

    def readForeignValues(self, column):
        """
        collects foreign values for a foreign key of this table
        checks if the given column is a foreign key
        checks what table and column this foreign key is pointing to
        checks the table and retrieves the column values
        creates recordarrays of these values
        returns the recordarrays
        """

        columnindex = self.column_names.index(column)
        split = self.column_types[columnindex].split(' ', 3)
        if len(split) != 3:
            return
        
        if split[1].upper() != "REFERENCES":
            return
        
        ftable = split[2].split('(',1)[0]
        print(f"foreign table {ftable}")

        # fcolumn = split[2].split('(',1)[1][:-1]
        # print(f"foreign column {fcolumn}")

        fcolumn_names = self.db.read_column_names(table=ftable)
        print(f"fcolumn names {fcolumn_names}")

        sqltable = self.db.read_records(table=ftable, columns = [])
        print(f"all table records {sqltable}")

        # by default just assuming we are pointing to primary key in first column and third column contains something meaningfull
        fcolumns = [fcolumn_names[0], fcolumn_names[2]]
        sqlcolumns = self.db.read_records(table=ftable, columns = fcolumns)

        print(f"all table records with foreign key column {sqlcolumns}")

        return sqlcolumns

    def createTable(self):
        """
        gathers the table name and the column info and then forwards them to
        create_table method of the Database object
        """
        # columns = [f"id INTEGER PRIMARY KEY AUTOINCREMENT", f"ordering INTEGER"]
        columns = []

        # get column info without primary key
        column_names = self.column_names
        column_types = self.column_types

        # enumerate over column names without id column
        for index, column_name in enumerate(column_names):
            columns.append(f"{column_name} {column_types[index]}")
        # print(columns)

        # print(f"query create table {columns}")
        self.db.create_table(table=self.name, variables=columns)

    def createRecord(self, values):
        """
        collects an array of values for a single record
        package it in an array of 1 record and then
        forwards it to the create_records method of Database

        It returns the last row as a Record object
        """

        # print(values)
        maxordering = self.db.get_max_columncontent(table=self.name, column="ordering") + 1
        # print(maxordering)
        valuepairs = [[maxordering] + values]
        # print(valuepairs)

        self.db.create_records(table=self.name, column_names=self.column_names[1:], valuepairs=valuepairs)
        self.defaults[1] = self.db.get_max_columncontent(table=self.name, column="ordering") + 1

        newrows_last = self.db.get_max_row(self.name)
        print(newrows_last)
        where = [["id",[newrows_last]]]

        sqlrecords = self.db.read_records(table=self.name, where=where)
        print(f"Record created: {sqlrecords}")
        recordobject = Record(self, sqlrecords[0])

        return recordobject

    def createRecords(self, records):

        if len(records) == 1:
            records = [self.createRecord(records[0])]
            return records

        else:
            # print(records)
            maxordering = self.db.get_max_columncontent(table=self.name, column="ordering") + 1
            # print(maxordering)
            for index, record in enumerate(records):
                records[index] = [maxordering] + record
                maxordering += 1
            # print(records)

            newrows_first = self.db.get_max_row(self.name) + 1
            
            self.db.create_records(table=self.name, column_names=self.column_names[1:], valuepairs=records)
            self.defaults[1] = self.db.get_max_columncontent(table=self.name, column="ordering") + 1
            
            newrows_last = self.db.get_max_row(self.name)

            wherevalues = list(range(newrows_first, newrows_last + 1))
            # print(f"wherevalues = {wherevalues}")
            where = [["id",wherevalues]]

            sqlrecords = self.db.read_records(table=self.name, where=where)
            print(f"Records created: {sqlrecords}")

            recordobjects = []
            for record in sqlrecords:
                recordobjects += [Record(self, record)]

            return recordobjects

    def updateRecordbyID(self, rowid, valuepairs):

        # get a wherestatement from just the rowid
        where = [["id",[rowid]]]

        # get record before updating
        record_before = self.readRecords(where=where)[0]
        # print(f"record before = {record_before}")

        # update the record
        # print(valuepairs)
        self.db.update_records(table=self.name, valuepairs=valuepairs, where=where)

        # get record after updating
        record_after = self.readRecords(where=where)[0]
        # print(f"record after = {record_after}")

        if record_before.primarykey != record_after.primarykey:
            # print(f"Update messed up the table!!!")
            return

        record_object = record_after
        if record_before.values != record_after.values:
            print(f"updated record {record_object.recordarray}")
        else:
            print(f"update record was not necessary")

        return record_object

    def updateRecords(self, valuepairs, where):

        table_before = self.readRecords()
        # print(f"table before = {table_before}")

        # # print(f"valueparis = {valuepairs}")
        # for valuearray in valuepairs:
        #     valuearray[1] = self.transform_boolean(valuearray[1])
        # # print(f"valuepairs = {valuepairs}")

        if isinstance(where, int):
            where = [["id", [where]]]
        else:
            if where != []:
                for statement in where:
                    # if column is a number, get the column name
                    if isinstance(statement[0], int):
                        statement[0] = self.column_names[statement[0]]

        # print(f"where {where}, valuepairs {valuepairs}")
        self.db.update_records(table=self.name, valuepairs=valuepairs, where=where)
                    
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

    # def transform_boolean(self, value):
    #     if value == True:
    #         value = 1
    #     elif value == False:
    #         value = 0
    #     return value

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
        print(self.table.column_names)
        print(self.recordarray)
        for index, name in enumerate(self.table.column_names):
            
            recordpair = [name, self.recordarray[index]]
            self.recordpairs += [recordpair]
        # print(f"set recordpairs {self.recordpairs}")

    def setvaluepairs(self):
        self.valuepairs = []
        for index, name in enumerate(self.table.column_names[1:]):
            valuepair = [name, self.recordarray[1:][index]]
            self.valuepairs += [valuepair]
        # print(f"set valuepairs {self.valuepairs}")


def print_records(records):
    for record in records:
        print(f"-table: {record.table}, primarykey: {record.primarykey}, recordpairs: {record.recordpairs}")

if __name__ == "__main__":

    # string = """ "I am Inevitable" said Thanos' maid."""
    # # string.replace('"', '\\"')
    # # string.replace("'", "\\'")
    # print(string)

    # l = [1,2,3]
    # placeholder= '?' # For SQLite. See DBAPI paramstyle.
    # placeholders= ', '.join(placeholder for _ in l)
    # query= f'SELECT name FROM students WHERE id IN ({placeholders})'
    # print(query)

    db = Database(path="", filename="science")
    db.delete_database()

    charbl = Table(
        db = Database(path="", filename="science"),
        name = "scientists",
        column_names = ["name", "age", "nobelprizewinner"],
        column_types = ["Text", "Integer", "Bool"],
        initial_records = [
            ["Hawking", 68, True],
            ["Edison's child said \"Apple!\"", 20, True],
        ]
    )
    
    #test functions of table
    print(f"read column names: {charbl.column_names}")

    values = ["Einstein", 100, False]
    record = charbl.createRecord(values)
    print(f"create single record")
    print_records([record])

    values = [
        ["Rosenburg", 78, False],
        ["Neil dGrasse Tyson", 57, True],
    ]
    records = charbl.createRecords(values)
    print(f"create multiple records")
    print_records(records)

    columns = ["name", "age"]
    records = charbl.readRecords(columns=columns)
    print(f"read only name and age columns for all records")
    print_records(records)

    # columns = ["name", "age"]
    # records = charbl.readRecords(columns=columns)
    # print(f"read only name and age columns for all records")
    # print_records(records)

    where = [["nobelprizewinner", [True]]]
    records = charbl.readRecords(where=where)
    print(f"read where")
    print_records(records)

    valuepairs = [["nobelprizewinner", False]]
    where = [["nobelprizewinner", [True]], ["name", ["Hawking"]]]
    records = charbl.updateRecords(valuepairs=valuepairs, where=where)
    print(f"update true to false")
    print_records(records)

    valuepairs = [["name", "Neil de'Grasse Tyson"], ["age", 40]]
    rowid = 5
    record = charbl.updateRecordbyID(valuepairs = valuepairs, rowid=rowid)
    print(f"update record 'id = 5'")
    print_records([record])

    records = charbl.readRecords()
    print(f"read all records")
    print_records(records)

    reltbl = Table(
        db = Database(path="", filename="science"),
        name = "relationships",
        column_names = ["charid1", "charid2", "description"],
        column_types = ["INTEGER REFERENCES scientists(id)", "INTEGER REFERENCES scientists(id)", "TEXT"],
    )

    values = [1, 2, "hawking and edison"]
    record = reltbl.createRecord(values)
    print(f"create single record")
    print_records([record])

    records = reltbl.readRecords()
    print(f"read all records")
    print_records(records)

    records = reltbl.readForeignValues('charid1')
