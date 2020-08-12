import datetime

from source.database import Database, Table

def table_builder(filename):

    tables = []

    # Story
    tables.append(Table(
        db = Database(filename=filename),
        name = "stories",
        record_name = "story",
        column_names = ["name", "summary", "body"],
        column_types = ["Text", "Text", "Text"],
    ))

    # Events
    tables.append(Table(
        db = Database(filename="template"),
        name = "events",
        column_names = ["name", "description", "date", "formatdate", "begin", "end"],
        column_types = ["TEXT", "TEXT", "INTEGER", "TEXT", "BOOL", "BOOL"],
        defaults = ["", "", 0, "", True, True],
    ))

    # Timelines
    tables.append(Table(
        db = Database(filename="template"),
        name = "timelines",
        column_names = ["name", "description"],
        column_types = ["TEXT", "TEXT"],
    ))
    
    # Locations
    tables.append(Table(
        db = Database(filename="template"),
        name = "locations",
        column_names = ["name", "description"],
        column_types = ["TEXT", "TEXT"],
    ))

    # Characters
    tables.append(Table(
        db = Database(filename="template"),
        name = "characters",
        column_names = ["name", "age", "gender", "nationality", "race"],
        column_types = ["TEXT", "Integer", "TEXT", "TEXT", "TEXT"],
    ))


    # # Template
    # tables.append(Table(
    #     db = Database(filename="template"),
    #     name = "",
    #     column_names = ["", ""],
    #     column_types = ["", ""],
    # ))



    # tbl.db.create_table(
    #     table="stories_events",
    #     variables=[
    #         "story_id INTEGER",
    #         "event_id INTEGER",
    #     ]
    # )

    # self.create_table(
    #     table="timeline_events", 
    #     variables=[
    #         "timeline_id INTEGER REFERENCES timelines (id)",
    #         "event_id INTEGER REFERENCES events (id)",
    #         ]
    #     )

    # self.create_table(
    #     table="locations_events", 
    #     variables=[
    #         "location_id INTEGER REFERENCES locations (id)",
    #         "event_id INTEGER REFERENCES events (id)",
    #         ]
    #     )

    # self.create_table(
    #     table="characters_events", 
    #     variables=[
    #         "character_id INTEGER REFERENCES characters (id)",
    #         "event_id INTEGER REFERENCES events (id)",
    #         ]
    #     )

    return tables