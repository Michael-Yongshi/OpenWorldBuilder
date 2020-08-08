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

            if os.path.exists(os.path.join(path, filename)):
                print(f"canceling, database already exists")
                return

            self.connection = sqlite3.connect(os.path.join(path, filename + ".sqlite"))

            print("Connection to SQLite DB successful")

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

        # print(columns)
        for record in records:
            print(record)

    def create_owb_tables(self):

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

def create_test_records(db):

    db.create_records(
        table="events",
        variables="intdate, strdate, begin, end, name, description",
        records=[
            "1, '0000-0-1', 1, 1, 'Creation', 'On the first day god created earth'",
            "2, '0000-0-2', 1, 1, 'Dogs', 'On the second day he created dogs'",
            "2, '0000-0-2', 1, 1, 'Cats', 'On the second day he also created cats'",
            "3, '0000-0-3', 1, 0, 'Armageddon', 'On the third day Armageddon is triggered'",
            "45, '0000-0-45', 1, 1, 'Bitcoin doubled', 'Bitcoin doubled in price on this day'",
            "99, '0000-0-99', 0, 1, 'Armageddon', 'On the 99 day Armageddon ends'",
            "2000, '0000-0-2000', 1, 1, 'Henk meets Casper', 'Henk found Casper in lost cabin'",
            "2005, '0000-0-2005', 1, 1, 'Henk travels to China', 'Henk travels to China'",
            "2006, '0000-0-2006', 1, 0, 'Xi becomes ruler of China', 'Xi becomes ruler of China'",
            "NULL, NULL, 1, 1, 'Draft event', 'Draft event'",
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
        variables="name, description",
        records=[
            "'China', 'Country in the far east'",
            "'Lost Cabin', 'A lost cabin in the woods'",
            "'Mambo Beach', 'The best beach of Curacao'",
            "'Global', 'Tag for an event that happens globally",
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
    db.read_records(table="events")
    db.get_event_records()
