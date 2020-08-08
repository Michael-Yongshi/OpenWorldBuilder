import os
import sqlite3

from sqlite3 import Error


def get_localpath():
    """set the paths to the users documents folder"""

    local_path = os.path.join("~", "Documents", "OWB")
    path = os.path.expanduser(local_path)

    return path

class Database(object):

    def __init__(self, path = "", filename = ""):

        self.connection = None

        if path == "":
            path = get_localpath()
        print(f"database path = {path}")
        
        if filename == "":
            filename = "owb"
        print(f"database filename = {filename}")

        try:
            # check if directory already exists, if not create it
            if not os.path.exists(path):
                os.makedirs(path)

            self.connection = sqlite3.connect(os.path.join(path, filename + ".sqlite"))

            print("Connection to SQLite DB successful")

        except Error as e:

            print(f"The error '{e}' occurred")

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

        for record in records:
            print(record)

    def delete_database(self):
        pass

def create_owb_tables(db):

    # time table as one to many (one time can have many events, but events only one time)
    db.create_table(
        table="time", 
        variables=[
            "date INTEGER",
            "title TEXT",
            ]
        )

    # Event table (start and end are default true, if event is only the start or the end of a persistant event, respectively can be set to false)
    db.create_table(
        table="events", 
        variables=[
            "start BOOL NOT NULL",
            "end BOOL NOT NULL",
            "name TEXT NOT NULL",
            "description TEXT NOT NULL",
            "time_id INTEGER REFERENCES time (id)",
            ]
        )

    db.create_table(
        table="locations", 
        variables=[
            "title TEXT NOT NULL",
            "description TEXT NOT NULL",
            ]
        )

    db.create_table(
        table="locations_events", 
        variables=[
            "location_id INTEGER REFERENCES locations (id)",
            "event_id INTEGER REFERENCES events (id)",
            ]
        )

    db.create_table(
        table="characters", 
        variables=[
            "name TEXT NOT NULL",
            "age INTEGER",
            "gender TEXT",
            "nationality TEXT",
            "race TEXT",
            ]
        )

    db.create_table(
        table="characters_events", 
        variables=[
            "character_id INTEGER REFERENCES characters (id)",
            "event_id INTEGER REFERENCES events (id)",
            ]
        )

def create_test_records(db):

    db.create_records(
        table="time",
        variables="date, title",
        records=[
            "1, '1-1-0001'",
            "2, 'first of january year 1'",
            "3, '1 january 1'",
            ]
    )

    db.create_records(
        table="events",
        variables="start, end, name, description, time_id",
        records=[
            "'true', 'true', 'Creation', 'On the first day god created earth', 1",
            "'true', 'true', 'Dogs', 'On the second day he created dogs', 2",
            "'true', 'true', 'Cats', 'On the second day he also created cats', 2",
            "'true', 'false', 'Armageddon', 'On the third day Armageddon is triggered', 3",
            "'true', 'true', 'Bitcoin doubled', 'Bitcoin doubled in price on this day', 45",
            "'false', 'true', 'Armageddon', 'On the 99 day Armageddon ends', 99",
            "'true', 'true', 'Henk meets Casper', 'Henk found Casper in lost cabin', 2000",
            "'true', 'true', 'Henk travels to China', 'Henk travels to China', 2005",
            "'true', 'false', 'Xi becomes ruler of China', 'Xi becomes ruler of China', 2006",
            ]
    )
    
    db.create_records(
        table="characters",
        variables="name, age, gender, nationality, race",
        records=[
            "'Henk', 24, 'female', 'German', 'Human'",
            "'Ollie', 4, 'male', 'Dutch', 'Labrador'",
            "'Casper', 7846, 'male', 'N/A', 'Ghost'",
            "'Xi', 50, 'male', 'Chinese', 'Panda'",
            ]
    )

    db.create_records(
        table="characters_events",
        variables="character_id, event_id",
        records=[
            "2, 2", # Ollie labrador is created
            "2, 5", # Ollies became wealthy when bitcoin surged
            "1, 7", # Henk meets casper
            "3, 7", # Casper also meets Henk
            "1, 8", # Henk goes to china
            "4, 9", # Xi becomes ruler of China
            ]
    )

    db.create_records(
        table="locations",
        variables="title, description",
        records=[
            "'China', 'Country in the far east ruled by Panda'",
            "'Lost Cabin', 'A lost cabin in the woods'",
            "'Mambo Beach', 'The best beach of Curacao'",
            ]
    )

    db.create_records(
        table="locations_events",
        variables="location_id, event_id",
        records=[
            "2, 7", # Henk meets casper
            "1, 8", # Henk goes to china
            "1, 9", # Xi becomes ruler of China
            ]
    )

def get_test_records(db):

    select_time_events = """
    SELECT
    time.id,
    time.date,
    events.name
    FROM
    events
    INNER JOIN time ON time.id = events.time_id
    """
    time_events = db.execute_read_query(select_time_events)

    for time_event in time_events:
        print(time_event)


if __name__ == "__main__":

    print("")
    db = Database(filename="test")
    print("")

    db.create_table()
    db.create_records()
    db.read_records()

    print("")
    db = Database()
    print("")

    create_owb_tables(db)
    create_test_records(db)
    db.read_records(table="events")
    get_test_records(db)