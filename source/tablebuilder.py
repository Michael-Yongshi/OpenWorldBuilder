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
    TL;DR: child tables with the actual records / data

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
            # id by default is [0,0,1,1] and ordering [0,1,1,1]
            [1,0,1,2],
            [2,0,1,2],
            [3,0,10,2],
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
        column_names = ["name", "province_id", "description"],
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
    TL;DR: Parent tables: one-to-many

    Parent tables are the records that can be referenced from the normal /child tables. 
    This is used to make changes to a group (record in the parent table) recursively for all children, without needing to change it for every child record.
    This can be both for a one-to-many relationship from parent to child as well as a many-to-many (versionized) relationship.

    i.e. a character has a race variable that is the same for other characters with the same race 
    giving them a real one-to-many relationship from this race (parent) table to the character (child) table
    makes it possible to change the description of the race attribute for all the characters in one go.
    """

    tables = []

    # # shown parent tables
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

    # Provinces
    tables.append(Table(
        db = Database(filename=filename),
        name = "provinces",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Countries (versionized)
    tables.append(Table(
        db = Database(filename=filename),
        name = "countries",
        record_name = "Country",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Empires (versionized)
    tables.append(Table(
        db = Database(filename=filename),
        name = "empires",
        column_names = ["name", "description"],
        column_types = ["VARCHAR(255)", "TEXT"],
    ))

    # Research
    tables.append(Table(
        db = Database(filename=filename),
        name = "research",
        column_names = ["name", "description", "source"],
        column_types = ["VARCHAR(255)", "TEXT", "VARCHAR(255)"],
    ))

    return tables

def get_fixed_parent_tables(filename):
    """
    TL;DR: Parent tables: one-to-many fixed parent table

    Technically these are the same as normal parent tables, but these are assumed to be fixed / static
    These don't have to be changed by a regular user. they just have some initial values that can be used to 
    easily filter or make selections of the child tables.

    i.e. the values of genders, which are usually two and normally do not have to be changed.
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

def get_versionized_tables(filename):
    """
    TL;DR: Parent tables: many-to-many on a certain condition

    Versionized tables are cross referencing tables between a child and parent table. But instead of having a normal one-to-many relationship
    this parent and child are linked conditionally or versionized, which means that a many-to-many relationship is established.
    the child table has no foreign key directly to the parent table, but uses a version table to link to a parent on a certain condition
    (usually on time, but not exclusively).
    When referencing this table one can reference the record that is valid at that time (or for another certain condition). This is done by adding the first record
    with a start date and an empty end date. Whenever a new record is recorded for the same two children, the first record gets an end date and the added record a start date
    (with again an empty end date). Along this line you get different 'versions' of the same one-to-many relationship.

    i.e. an empire contains multiple countries in a one-to-many relationship (an empire has multiple countries in it, but a country can only belong to one empire at a time)
    , however in time new countries are conquered and other countries are lost. So depending on the time a country has different allegiances to different empires, 
    making it a many-to-many (versionized) table 
    or
    a character can only be in one place at a time, but over time this changes, making this a versionized many-to-many relationship on condition of time
    """

    tables = []

    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_countries_provinces",
        column_names = ["name", "startversion", "endversion", "country_id", "province_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "INTEGER", "INTEGER REFERENCES countries(id)", "INTEGER REFERENCES provinces(id)", "TEXT"],
    ))

    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_empires_countries",
        column_names = ["name", "startversion", "endversion", "empire_id", "country_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER", "INTEGER", "INTEGER REFERENCES empires(id)", "INTEGER REFERENCES countries(id)", "TEXT"],
    ))

    return tables

def get_xreference_tables(filename):
    """
    TL;DR: child to child: many-to-many

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
        column_names = ["name", "story_id", "character_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER REFERENCES stories(id)", "INTEGER REFERENCES characters(id)", "TEXT"],
    ))

    tables.append(Table(
        db = Database(filename=filename),
        name = "XREF_relationships",

        column_names = ["name", "character1_id", "character2_id", "description"],
        column_types = ["VARCHAR(255)", "INTEGER REFERENCES characters(id)", "INTEGER REFERENCES characters(id)", "TEXT"],
    ))

    return tables


# # Template
# tables.append(Table(
#     db = Database(filename=filename),
#     name = "",
#     column_names = ["", ""],
#     column_types = ["", ""],
# ))