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
        column_types = ["VARCHAR(255)", "VARCHAR(255)", "TEXT"],
        column_placement = [
            # row, column, height, width
            # id by default is [0,0,1,1]
            [1,0,1,1],
            [2,0,1,1],
            [3,0,10,1],
        ],
    ))

    # Events
    tables.append(Table(
        db = Database(filename=filename),
        name = "events",
        column_names = ["name", "date", "formatdate", "begin", "end", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "VARCHAR(255)", "BOOL", "BOOL", "TEXT"],
        defaults = ["", 0, "", True, True, ""],
    ))

    # Timelines
    tables.append(Table(
        db = Database(filename=filename),
        name = "timelines",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))
    
    # Locations
    tables.append(Table(
        db = Database(filename=filename),
        name = "locations",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Characters
    tables.append(Table(
        db = Database(filename=filename),
        name = "characters",
        column_names = ["name", "age", "gender", "nationality", "race", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "VARCHAR(255)", "VARCHAR(255)", "INTEGER REFERENCES races(id)", "TEXT"],
    ))

    # Races
    tables.append(Table(
        db = Database(filename=filename),
        name = "races",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # tables.append(Table(
    #     db = Database(filename=filename),
    #     name = "relationships",
    #     column_names = ["name", "character1_id", "character2_id", "type", "description"],
    #     column_types = ["VARCHAR(255)", "INTEGER REFERENCES characters(id)", "INTEGER REFERENCES characters(id)", "VARCHAR(255)", "TEXT"],
    # ))
    
    # Many-to-many tables
    # tables.append(Table(
    #     db = Database(filename=filename),
    #     name = "link_stories_characters",
    #     column_names = ["story_id", "character_id"],
    #     column_types = ["INTEGER REFERENCES stories(id)", "INTEGER REFERENCES characters(id)"],
    # ))



    # # Template
    # tables.append(Table(
    #     db = Database(filename=filename),
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