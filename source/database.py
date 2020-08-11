import os
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
        pass

    def execute_query_cursor(self, query, read=False):
        cursor = self.connection.cursor()

        try:
            print(query)
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")

            if read == True:
                return cursor

        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_query(self, query, read=False):
        cursor = self.connection.cursor()

        try:
            print(query)
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")

            if read == True:
                data = cursor.fetchall()
                return data

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

        create_table = f"\nCREATE TABLE IF NOT EXISTS {table}(\nid INTEGER PRIMARY KEY AUTOINCREMENT,\n{valuetext}\n);\n"
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

        create_record = f"\nINSERT INTO {table}\n({column_text})\nVALUES\n{records_text}\n;\n"
        cursor = self.execute_query_cursor(create_record, read = True)

        datadict = {
            "id": cursor.lastrowid
        }

        return datadict

    def read_table_names(self):

        query = f"SELECT name FROM sqlite_master WHERE type='table';"
        
        tables = self.execute_query(query=query, read=True)

        # print(tables)
        # for table in tables:
            # print(table)

        return tables

    def read_column_names(self, table = "test"):

        query = f"SELECT * FROM {table};"
        
        cursor = self.execute_query_cursor(query=query, read=True)
        description = cursor.description

        # print(description)
        columns = []
        for record in description:
            # print(record[0])
            columns += [record[0]]
        
        # print(columns)
        return columns

    def read_records(self, table = "test", columns="*", where = ""):

        select_records = f"\nSELECT {columns} from {table}"
        if where != "":
            select_records += f" WHERE {where}"

        records = self.execute_query(select_records, read=True)
       
        return records

    def update_record(self, table = "test", valuepairs = [["integer", 3], ["text",'test']], where=""):

        # columns = self.read_column_names(table)[1:]
        # # print(f"columns of table {table} are {columns}")
        # column_count = len(columns)
        # # print(f"column count = {column_count}")
        # print(columns)

        setvaluepairs = ""
        for valuepair in valuepairs:
            if isinstance(valuepair[1], str):
                setvaluepairs += f"{valuepair[0]} = '{valuepair[1]}',\n"
            else:
                setvaluepairs += f"{valuepair[0]} = {valuepair[1]},\n"
            
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

        update_record = f"\nUPDATE {table} SET\n{setvaluepairs}\nWHERE\n{where}\n;\n"
        cursor = self.execute_query_cursor(update_record, read = True)

        # if cursor != None:
        #     datadict = {
        #         "id": row
        #     }
        #     # print(datadict)

        #     return datadict

    # def get_event_records(self):

    #     # complete list of events
    #     events_query = """
    #         SELECT
    #         events.id as event_id,
    #         events.name as event_name,
    #         events.description as event_description
    #         events.begin as begin,
    #         events.intdate as intdate,
    #         events.strdate as date,
    #         events.end as end,
    #         FROM
    #         events
    #         """

    #     events_result = self.execute_query(events_query, read=True)

    #     for record in events_result:
    #         # print(record)
    #         pass

    #     # info on related characters and locations for the selected event (selected_event)
    #     events_all_query = """
    #         SELECT
    #         events.id as event_id,
    #         events.name as event_name,
    #         events.description as event_description,
    #         events.begin as begin,
    #         events.end as end,
    #         events.intdate as intdate,
    #         events.strdate as date,
    #         characters.id as character_id,
    #         characters.name as character_name,
    #         characters.age as character_age,
    #         locations.name as location_name,
    #         locations.description as location_description
    #         FROM
    #         events
    #         LEFT JOIN characters_events ON characters_events.event_id = events.id
    #         LEFT JOIN characters ON characters_events.character_id = characters.id
    #         LEFT JOIN locations_events ON locations_events.event_id = events.id
    #         LEFT JOIN locations ON locations_events.location_id = locations.id
    #         """
    #     events_all_result = self.execute_query(events_all_query, read=True)

    #     for record in events_all_result:
    #         # print(record)
    #         pass

    #     return events_result

class Table(object):
    def __init__(self, db, name, column_names, column_types, record_name = "", initial_records = []):
        super().__init__()

        # connect to database
        self.db = db

        # set data
        self.name = name
        if record_name == "":
            self.record_name = self.name[:-1]
        else:
            self.record_name = record_name
        self.column_names = column_names
        self.column_types = column_types

        # create table
        self.createTable()

        # initiate records
        self.initial_records = initial_records
        if self.initial_records != []:
            self.createRecords(records=self.initial_records)

    def createTable(self):

        create_query = []
        for c in range(len(self.column_names)):
            create_query.append(f"{self.column_names[c]} {self.column_types[c]}")

        self.db.create_table(table=self.name, variables=create_query)

    def createRecord(self, values):

        for vindex, value in enumerate(values):
            values[vindex] = self.transform_boolean(value)
        # print(values)

        row = self.db.create_records(table=self.name, records=[values])
        return row

    def createRecords(self, records):

        for rindex, record in enumerate(records):
            for vindex, value in enumerate(record):
                records[rindex][vindex] = self.transform_boolean(value)
        # print(records)

        row = self.db.create_records(table=self.name, records=records)
        return row

    def readColumnNames(self):

        column_names = self.db.read_column_names(table=self.name)
        return column_names

    def readRecords(self, columns=-1, select=[]):

        if columns != -1:
            column_selection = ""
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

        records = self.db.read_records(table=self.name, columns=column_selection, where=where)
        return records

    def updateRecord(self, valuepairs, select):

        # print(f"valueparis = {valuepairs}")
        for valuepair in valuepairs:
            valuepair[1] = self.transform_boolean(valuepair[1])
        # print(f"valuepairs = {valuepairs}")

        if isinstance(select, int):
            select = ["id", [select]]
        
        # print(f"select {select}")
        for v in range(len(select[1])):
            select[1][v] = self.transform_boolean(select[1][v])
        # print(f"select {select}")

        self.db.update_record(table=self.name, valuepairs=valuepairs, where=select)

    def transform_boolean(self, value):
        if value == True:
            value = 1
        elif value == False:
            value = 0
        return value

if __name__ == "__main__":

    newtbl = Table(
        db = Database(path="", filename="science"),
        name = "scientists",
        column_names = ["name", "age", "nobelprizewinner"],
        column_types = ["Text", "Integer", "Bool"],
        initial_records = [
            ["Hawking", 68, True]
        ]
    )
    
    # test functions of table
    print(f"read column names: {newtbl.readColumnNames()}")

    values = ["Einstein", 100, False]
    print(f"create single record: {newtbl.createRecord(values)}")
    records = [
        ["Rosenburg", 78, False],
        ["Neil dGrasse Tyson", 57, True],
    ]
    print(f"create multiple records: {newtbl.createRecords(records)}")

    print(f"read records: {newtbl.readRecords()}")
    columns = [0,2]
    print(f"read with specific columns: {newtbl.readRecords(columns=columns)}")
    selection = ["nobelprizewinner", [True]]
    print(f"read selection: {newtbl.readRecords(select=selection)}")

    valuepairs = [["nobelprizewinner", False]]
    selection = ["nobelprizewinner", [True]]
    print(f"update record: {newtbl.updateRecord(valuepairs=valuepairs, select=selection)}")
    valuepairs = [["name", "Neil deGrasse Tyson"], ["age", 40]]
    selection = 4
    print(f"update typo for id: {newtbl.updateRecord(valuepairs=valuepairs, select=selection)}")