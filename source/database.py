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
            self.create_owb_tables()
            print("Created OWB tables")

        except Error as e:

            print(f"The error '{e}' occurred")

    def delete_database(self):
        pass

    def execute_query(self, query):
        cursor = self.connection.cursor()

        try:
            print(query)
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")

        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None

        try:
            print(query)
            cursor.execute(query)
            description = cursor.description
            result = cursor.fetchall()
            return result

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

    def create_records(self, table = "test", variables = "integer, text", records = ["1,'test'", "2, 'test'"]):

        recordtext = ""
        for record in records:
            recordtext += f"({record}),\n"
        recordtext = recordtext[:-2]

        create_record = f"\nINSERT INTO {table}\n({variables})\nVALUES\n{recordtext}\n;\n"
        self.execute_query(create_record)

    def read_records(self, table = "test", selection = "*"):

        select_records = f"\nSELECT {selection} from {table}"
        records = self.execute_read_query(select_records)
       
        return records

    def create_owb_tables(self):

        self.create_table(
            table="stories",
            variables=[
                "title TEXT",
                "summary TEXT",
                "body TEXT",
            ]
        )

        self.create_table(
            table="stories_events",
            variables=[
                "story_id INTEGER",
                "event_id INTEGER",
            ]
        )

        # Event table (start and end are default true, if event is only the start or the end of a persistant event, respectively can be set to false)
        self.create_table(
            table="events", 
            variables=[
                "intdate INTEGER",
                "strdate TEXT",
                "begin INTEGER NOT NULL",
                "end INTEGER NOT NULL",
                "name TEXT NOT NULL",
                "description TEXT",
                ]
            )

        self.create_table(
            table="locations", 
            variables=[
                "name TEXT NOT NULL",
                "description TEXT",
                ]
            )

        self.create_table(
            table="locations_events", 
            variables=[
                "location_id INTEGER REFERENCES locations (id)",
                "event_id INTEGER REFERENCES events (id)",
                ]
            )

        self.create_table(
            table="characters", 
            variables=[
                "name TEXT NOT NULL",
                "age INTEGER",
                "gender TEXT",
                "nationality TEXT",
                "race TEXT",
                ]
            )

        self.create_table(
            table="characters_events", 
            variables=[
                "character_id INTEGER REFERENCES characters (id)",
                "event_id INTEGER REFERENCES events (id)",
                ]
            )

    def get_event_records(self):

        # complete list of events
        events_query = """
            SELECT
            events.id as event_id,
            events.begin as begin,
            events.intdate as intdate,
            events.strdate as date,
            events.end as end,
            events.name as event_name,
            events.description as event_description
            FROM
            events
            """

        events_result = self.execute_read_query(events_query)

        for record in events_result:
            print(record)

        # info on related characters and locations for the selected event (selected_event)
        events_all_query = """
            SELECT
            events.id as event_id,
            events.begin as begin,
            events.end as end,
            events.intdate as intdate,
            events.strdate as date,
            events.name as event_name,
            events.description as event_description,
            characters.id as character_id,
            characters.name as character_name,
            characters.age as character_age,
            locations.name as location_name,
            locations.description as location_description
            FROM
            events
            LEFT JOIN characters_events ON characters_events.event_id = events.id
            LEFT JOIN characters ON characters_events.character_id = characters.id
            LEFT JOIN locations_events ON locations_events.event_id = events.id
            LEFT JOIN locations ON locations_events.location_id = locations.id
            """
        events_all_result = self.execute_read_query(events_all_query)

        for record in events_all_result:
            print(record)

        return events_result

def create_test_records(db):

    db.create_records(
        table="stories",
        variables="title, summary, body",
        records=[
            "'0-1', 'prologue', 'Ollie was born at Mambo beach in Curacao, but lost his family in some way'",
            "'1-1', 'chapter 1 paragraph one', 'Ollie went swimming with the turtles'",
            "'2-1', 'chapter 2 paragraph one', 'Ollie met Max and played with him at a shipwreck'",
            "'3-1', 'chapter 3 paragraph one', 'Ollie lost Max and wandered in unknown territory'",
            "'4-1', 'chapter 4 paragraph one', 'There was a big tremor in the ocean and Ollie heard Max screaming in the distance'",
            "'4-2', 'chapter 4 paragraph two', 'Max point of view'",
            "'5-1', 'chapter 5 paragraph one', 'Ollie and Max are reunited'",
            "'6-1', 'Epilogue', '3 years later'",
        ]
    )

    db.create_records(
        table="stories_events",
        variables="story_id, event_id",
        records=[
            "1, 1",
            "1, 2",
            "2, 3",
            "3, 4",
            "3, 5",
            "4, 6",
            "5, 7",
            "6, 7",
            "7, 8",
            "8, 4",
            "8, 6",
            "8, 7",
            "8, 8",
        ]
    )

    db.create_records(
        table="events",
        variables="intdate, strdate, begin, end, name, description",
        records=[
            "1, '2002-0-1', 1, 1, 'Born', 'Ollie was born'",
            "50, '2002-2-20', 1, 1, 'Lost', 'Ollie was lost'",
            "240, '2002-10- ', 1, 1, 'Swimming with turtles', 'Ollie left home for the beach to swim with turtles'",
            "245.1, '2002-10-20-12:00', 1, 1, 'Met Max', 'Ollie met max'",
            "245.2, '2002-10-20-15:00', 1, 1, 'Played at shipwreck', 'Played with turtles'",
            "245.3, '2002-10-20-15:30', 1, 1, 'Got lost', 'Got lost'",
            "245.4, '2002-10-20-17:00', 1, 1, 'Tremor', 'Tremor'",
            "245.4, '2002-10-20-17:00', 1, 1, 'Reunited', 'Reunited'",
            ]
    )
    
    db.create_records(
        table="characters",
        variables="name, age, gender, nationality, race",
        records=[
            "'Ollie', 2, 'male', 'Curacaoian', 'Dog'",
            "'Max', 67, 'male', 'Curacaoian', 'Turtle'",
            ]
    )

    db.create_records(
        table="characters_events",
        variables="character_id, event_id",
        records=[
            "1, 1",
            ]
    )

    db.create_records(
        table="locations",
        variables="name, description",
        records=[
            "'China', 'Country in the far east'",
            "'Lost Cabin', 'A lost cabin in the woods'",
            "'Mambo Beach', 'The best beach of Curacao'",
            "'Global', 'Tag for an event that happens globally'",
            ]
    )

    db.create_records(
        table="locations_events",
        variables="location_id, event_id",
        records=[
            "3, 2", # Ollie is created on the beach
            "2, 7", # Henk meets casper
            "1, 8", # Henk goes to china
            "1, 9", # Xi becomes ruler of China
            ]
    )


if __name__ == "__main__":

    # print("")
    # db = Database(filename="test")
    # print("")

    # db.create_table()
    # db.create_records()
    # db.read_records()

    print("")
    db = Database()
    print("")

    db.create_owb_tables()
    create_test_records(db)
    # db.read_records(table="events")
    # db.get_event_records()
