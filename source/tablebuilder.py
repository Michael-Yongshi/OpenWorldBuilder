import datetime

from source.database import Database, Table

def table_builder(filename):

    tables = []
    tables += get_normal_tables(filename)
    print(tables)
    tables += get_parent_tables(filename)
    print(tables)
    tables += get_fixed_parent_tables(filename)
    print(tables)
    tables += get_xreference_tables(filename)
    print(tables)
    tables += get_versionized_tables(filename)

    return tables

def get_normal_tables(filename):
    """
    normal tables or children tables

    i.e. create new characters, locations, events or story parts.
    """

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
        column_names = ["name", "province", "description"],
        column_types = ["VARCHAR(255)", "INTEGER REFERENCES provinces(id)", "TEXT"],
    ))

    # Characters
    tables.append(Table(
        db = Database(filename=filename),
        name = "characters",
        column_names = ["name", "age", "gender", "nationality", "culture", "race", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "INTEGER REFERENCES FIXEDPARENT_genders(id)", "INTEGER REFERENCES countries(id)", "INTEGER REFERENCES cultures(id)", "INTEGER REFERENCES races(id)", "TEXT"],
    ))

    print(tables)

    return tables

def get_parent_tables(filename):
    """
    Parent tables are the parent table in a one to many relationship used as a grouping or collection attribute.
    This is used to make changes to a group (record in the parent table) recursively for all children, without needing to change it for every child record.

    i.e. a character has a race variable that is the same for other characters with the same race.
    giving them a real one-to-many relationship from this race (parent) table to the character (child) table
    makes it possible to change the description of the race attribute for all the characters in one go.
    """

    tables = []

    # # shown parent tables
    # Provinces
    tables.append(Table(
        db = Database(filename=filename),
        name = "provinces",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Cultures
    tables.append(Table(
        db = Database(filename=filename),
        name = "cultures",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Races
    tables.append(Table(
        db = Database(filename=filename),
        name = "races",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Research
    tables.append(Table(
        db = Database(filename=filename),
        name = "research",
        column_names = ["name", "description", "source"],
        column_types = ["VARCHAR(255)", "TEXT", "BLOB"],
    ))

    return tables

def get_fixed_parent_tables(filename):
    """
    Technically these are the same as normal parent tables, but these are assumed to be static
    These don't have to be changed by a regular user. they just have a 

    i.e. the values of genders, which are usually two and do not have to be changed.
    """

    tables = []

    # # not shown fixed parent tables
    tables.append(Table(
        db = Database(filename=filename),
        name = "FIXEDPARENT_genders",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
        initial_records= [
            ["Undetermined", "Undetermined"],
            ["Male", "Male"],
            ["Female", "Female"]
        ]
    ))

    return tables

def get_xreference_tables(filename):
    """
    Many-to-many tables between two or more normal (children) tables, indicating that there are many different possible links in between two different records.
    These are many-to-many links that need to be mapped with an intermediate table containing just 2 foreign keys referencing 2 children tables.

    i.e. a character can be part of many different events, but an event can also have many participating / affected characters. Two link these two children tables
    we record every time a character plays in an event, creating a list of these occurences
    """

    tables = []

    # Stories to characters
    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_stories_characters",
        column_names = ["name", "description", "story_id", "character_id"],
        column_types = ["VARCHAR(255)", "TEXT", "INTEGER REFERENCES stories(id)", "INTEGER REFERENCES characters(id)"],
    ))

    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_relationships",

        column_names = ["name", "description", "character1_id", "character2_id"],
        column_types = ["VARCHAR(255)", "TEXT", "INTEGER REFERENCES characters(id)", "INTEGER REFERENCES characters(id)"],
    ))

    return tables

def get_versionized_tables(filename):
    """
    These are version tables, which contain one-to-many relationship that are registered as a many-to-manyrelationship.
    Then we add for the relationship different version that are only valid on a certain condition (usually on time, but not exclusively).
    When referencing this table on can reference the record that is valid at that time (or for another certain condition). This is done by adding the first record
    with a start date and an empty end date. Whenever a new record is recorded for the same two children, the first record gets an end date and the added record a start date
    (with again an empty end date). Along this line you get different 'versions' of the same one-to-many or many-to-many relationship.

    i.e. an empire contains multiple countries, however in time new countries are conquered and other countries are lost. So depending on the time
    a country has different allegiances to different empires, making it a many-to-many (versionized) table
    or
    a character can only be in one place at a time, but over time this changes, making this a versionized many-to-many relationship on condition of time
    """

    tables = []

    # Countries
    tables.append(Table(
        db = Database(filename=filename),
        name = "countries",
        record_name = "Country",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))
    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_countries_provinces",
        column_names = ["name", "startversion", "endversion", "country_id", "province_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "INTEGER", "INTEGER REFERENCES countries(id)", "INTEGER REFERENCES provinces(id)", "TEXT"],
    ))

    # Empires
    tables.append(Table(
        db = Database(filename=filename),
        name = "empires",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))
    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_empires_countries",
        column_names = ["name", "startversion", "endversion", "empire_id", "country_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "INTEGER", "INTEGER REFERENCES empires(id)", "INTEGER REFERENCES countries(id)", "TEXT"],
    ))

    return tables

# # Template
# tables.append(Table(
#     db = Database(filename=filename),
#     name = "",
#     column_names = ["", ""],
#     column_types = ["", ""],
# ))